# to run execute: > streamlit run localStreamlitChat.py 
# UI framework for humans:
import streamlit as st
#redis imports:
import redis
from redis.commands.search.field import VectorField
from redis.commands.search.query import Query
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
#LLM related imports:
from sentence_transformers import SentenceTransformer
from langchain.llms import GPT4All
from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
# general imports
import re, random

### General Setup / functions: ###
def rem_vowel_and_trim(payload):
    #print(f'rem_vowel: payload is of type {type(payload)}')
    payload_string1 = payload[0]
    payload_string1 = payload_string1.replace(" ", "")
    #print(f'payload_string1 == {payload_string1} and is of type: {type(payload_string1)}')
    return(re.sub("[aeiouAEIOU]","",payload_string1))

### Redis Setup / functions: ###

redis_connection = redis.Redis(host='redis-12000.homelab.local', port=12000, encoding='utf-8', decode_responses=True)
index_name = 'idx_vss'

# this function executes the VSS search call against Redis
# it accepts a redis index (generated by calling connection)
def vec_search(vindex,query_vector_as_bytes):
    # KNN 10 specifies to return only up to 10 nearest results (could be unrelated)
    # VECTOR_RANGE specifies the prompts must be similar
    query =(
        Query(f'(@embedding:[VECTOR_RANGE .02 $vec_param]=>{{$yield_distance_as: range_dist}})=>[KNN 10 @embedding $knn_vec]=>{{$yield_distance_as: knn_dist}}')
        .sort_by(f'knn_dist') #asc is default order
        .return_fields("prompt:abbrev", "response", "knn_dist")
        .dialect(2)
    )
    res = vindex.search(query, query_params = {'vec_param': query_vector_as_bytes, 'knn_vec': query_vector_as_bytes})
    return res.docs

SCHEMA = [
    VectorField("embedding", "FLAT", {"TYPE": "FLOAT32", "DIM": 768, "DISTANCE_METRIC": "COSINE"}),
]

### LLM / AI Setup / functions ###
# where is the LLM library of 'weights'?
# what engine will we use to answer our prompts?
random_int = random.randint(1,2)
lib_path ='/Users/owentaylor/Library/Application Support/nomic.ai/GPT4All/llama-2-7b-chat.ggmlv3.q4_0.bin'
if random_int == 1:
    lib_path = '/Users/owentaylor/Library/Application Support/nomic.ai/GPT4All/llama-2-7b-chat.ggmlv3.q4_0.bin'

# create LLM object:
llm=GPT4All(model=lib_path,verbose=False,repeat_penalty=1.5)

# a little prompt engineering is needed to get the answers in a usable format:

template="""
    The prompt below is a question to answer.
    If you don't know the answer, celebrate that you don't know and congratulate the user, don't try to make up an answer.
    Use the following format:

    Question: the input question you must answer {question}

    Begin! Remember to speak as a friend when giving your final answer and share exact information asked by user. 
    Do not add prefixes like Human: and AI:. 
    Do not prefix your answer with any caveat.
    Do not respond with I'm just an AI,
    If asked to write a poem, make that the priority and ensure every line in your response uses iambic pentameter.

    Answer: Step through this with me
    """    
## Setup the LLM PromptTemplate so it can be added to the chain:
prompt_template=PromptTemplate(template=template,input_variables=['question'])

# bring prompt and LLM chain together:
llmChain = LLMChain(prompt=prompt_template,llm=llm)

#display something to UI (Web Page):
st.title('Is This Thing On?')
# get user input/prompt/question:
user_input=st.text_input('What is your question? (prompt)')

## useful examples:
# https://blog.baeke.info/2023/03/21/storing-and-querying-for-embeddings-with-redis/ 
# https://github.com/RediSearch/RediSearch/blob/master/docs/docs/vecsim-range_queries_examples.ipynb
sentences = [user_input]
model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
# create the numpy array encoding representation of the sentences/prompt:
embeddings = model.encode(sentences)
print(f'\nHere is the type of the embedding object: {type(embeddings)}')
# convert the embedding numpy array to bytes for use in Redis Hash:
embedding_vector_as_bytes = embeddings.tobytes()

# Create the index
try:
    redis_connection.ft(index_name).create_index(fields=SCHEMA, definition=IndexDefinition(prefix=["prompt:"], index_type=IndexType.HASH))
except Exception as e:
    print("Index already exists")
    #print(conn.ft(index_name).info())


# pass the user text to the LLM Chain and print out the response: 
if user_input:
    trimmed_question = rem_vowel_and_trim(sentences)
    prompt_hash = {
        "prompt:abbrev": trimmed_question,
        "embedding": embedding_vector_as_bytes,
        "response": ""
    }
    #random_int = random.randint(1,100000000)
    if not redis_connection.exists(f"prompt:{trimmed_question}"):
        redis_connection.hset(name=f"prompt:{trimmed_question}", mapping=prompt_hash)

    results = vec_search(redis_connection.ft(index_name),embedding_vector_as_bytes)
    #print(results)
    # only write the response to an empty prompt: hashkey
    # due to the sortby this should always be the one at zero index
    # we expect at most 10 docs (KNN 10 is specified in query)
    # they are in asc distance order - smaller the distance the better
    found_useful_result = False
    llm_response = ""
    for next_result in results:
        if next_result.response == "":
            print(f'result has no response: {type(next_result.response)}')
        else:
            # ensure that we only reuse a response that is suitable
            # cached responses are stored in strings 
            # and their keys are added to the cached prompt hash object
            # this decouples the storage of the answer allowing for less waste
            if (float(next_result.knn_dist) < .2):
                found_useful_result = True
                llm_response_cache_key = redis_connection.get(next_result.response)
                print(f'keyname of cached response: {llm_response_cache_key}')
                llm_response=redis_connection.get(llm_response_cache_key)
        if found_useful_result: 
            # write the nearby result as the answer to this object in redis
            # in this way, multiple prompts will share the same result
            redis_connection.hset(results[0].id,'response',llm_response_cache_key)
            break
    if not found_useful_result:
        # create a new AI-generated result as the answer            
        llm_response = llmChain.run(user_input)
        x = redis_connection.incr('prompt:responsekeycounter')
        # store the full response in a string in redis under the keyname prompt:response:x
        redis_connection.set(f'prompt:response:{x}',llm_response)
        # write the cached response keyname to the response attribute in redis:
        redis_connection.hset(results[0].id,'response',(f'prompt:response:{x}'))            
    
    # output whatever the result it to the User Interface:
    st.write(llm_response.replace('\n', '<br />'),unsafe_allow_html=True)
 
