# to run this example you will need the following :
""" 
ggml-model-gpt4all-falcon-q4_0.bin or llama-2-7b-chat.ggmlv3.q4_0.bin or a similar LLM
You can download ggml-model-gpt4all-falcon-q4_0.bin using the following command:

wget --no-check-certificate https://huggingface.co/nomic-ai/gpt4all-falcon-ggml/resolve/main/ggml-model-gpt4all-falcon-q4_0.bin

wget --no-check-certificate https://huggingface.co/TheBloke/Llama-2-7b-Chat-GGUF/resolve/main/llama-2-7b-chat.Q5_K_S.gguf

Once you have this file downloaded 
- be sure to edit the line that points the lib_path to the correct location of that library: 

(near line #130 in this file)
lib_path = './ggml-model-gpt4all-falcon-q4_0.bin'
"""

# execute: > 
""" 
python localCMDLineChat.py -h <host> -p <port> [optional -s <password>] [optional -u <username>] 
python3 localCMDLineChat.py -h redis-12144.c309.us-east-2-1.ec2.cloud.redislabs.com -p 12144 -s WqedzS2orEF4Dh0baBeaRqo16DrYYxzIo1
python3 localCMDLineChat.py -h redis-12000.homelab.local -p 12000
"""
# This version only uses cmdline interface
# redis imports: for caching prompts and responses and 
# searching using Vector Similarity for previous prompts 
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
import re,time,sys,getopt

### General Setup / functions: ###
## this function is designed to return a likely to be unique value for a string
## a bloom or cuckoo filter used for deduping would be better
## redis has a bloom module designed for that purpose
def compact_string_for_keyname(payload):
    payload_string1 = payload[0]
    payload_string1 = payload_string1.replace(" ", "")
    sumchars=0
    for s in payload_string1:
        sumchars = sumchars+ord(s)
    response = f'{re.sub("[}aeiouAEIOU{?!,.]","",payload_string1)}:{sumchars}'
    return(response)

spacer = "\n**********************************************\n"

def display_menu():
    #display something to UI CMDLine:
    print(spacer)
    print('\tType: END   and hit enter to exit the program...\n')
    print('\tCommandline Instructions: \nType in your prompt/question as a single statement with no return characters... ')
    print('(only hit enter for the purpose of submitting your question)')
    print(spacer)
    # get user input/prompt/question:
    user_text = input('\n\tWhat is your question? (prompt):\t')
    if user_text =="END" or user_text =="end":
        print('\nYOU ENTERED --> \"END\" <-- QUITTING PROGRAM!!')
        exit(0)
    return (user_text)
        
### Redis Setup / functions: ###

## checks sys.args for host and port etc...
redis_host = 'redis-12000.homelab.local'
redis_port = 12000
redis_password = ""
redis_user = "default"
create_new_index = False

argv = sys.argv[1:] # skip the name of this script
opts,args = getopt.getopt(argv,"h:p:s:u:", 
                                ["host =",
                                "port =",
                                "password =",
                                "username =",
                                ]) 
for opt,arg in opts:
    if opt in ['-h','-host']:
        redis_host = arg
    elif opt in ['-p','-port']:
        redis_port = arg
    elif opt in ['-s','-secret_password']:
        redis_password = arg
    elif opt in ['-u','-username']:
        redis_user = arg
if len(sys.argv)<4:
    print('\nPlease supply a hostname & port for your target Redis instance:\n')
    print('\n\tYour options are: host port password username:')
    print('-h <host> -p <port> -s <password> -u <username>')
    exit(0)


if redis_password == "" and redis_user == "default":
    redis_connection = redis.Redis( host=redis_host, port=redis_port, encoding='utf-8', decode_responses=True)
else:
    redis_connection = redis.Redis( host=redis_host, port=redis_port, password=redis_password ,username=redis_user, encoding='utf-8', decode_responses=True)

# this function creates the index in redis and returns its name:
def create_index_in_redis(redis_connection):
    index_name = 'idx_vss_lclc'
    SCHEMA = [
        VectorField("embedding", "FLAT", {"INITIAL_CAP": 1000, "TYPE": "FLOAT32", "DIM": 768, "DISTANCE_METRIC": "COSINE"}),
    ]
    # Create the index
    try:
        redis_connection.ft(index_name).create_index(fields=SCHEMA, definition=IndexDefinition(prefix=["prompt:"], index_type=IndexType.HASH))
    except Exception as e:
        print(repr(e))
    return index_name

# this function executes the VSS search call against Redis
# it accepts a redis index (generated by calling connection)
def vec_search(vindex,query_vector_as_bytes):
    # KNN 10 specifies to return only up to 10 nearest results (could be unrelated)
    # VECTOR_RANGE specifies the prompts must be similar
    query =(
        Query(f'(@embedding:[VECTOR_RANGE .02 $vec_param]=>{{$yield_distance_as: range_dist}})=>[KNN 10 @embedding $knn_vec]=>{{$yield_distance_as: knn_dist}}')
        .sort_by(f'knn_dist') #asc is default order
        .return_fields("response_key", "knn_dist")
        .dialect(2)
    )
    res = vindex.search(query, query_params = {'vec_param': query_vector_as_bytes, 'knn_vec': query_vector_as_bytes})
    return res.docs

### LLM / AI Setup / functions ###
# where is the LLM library?
# In Other Words: what large language model will we use to answer our prompts?
#lib_path ='/Users/owentaylor/Library/Application Support/nomic.ai/GPT4All/llama-2-7b-chat.ggmlv3.q4_0.bin'
lib_path = './ggml-model-gpt4all-falcon-q4_0.bin'

def create_and_fetchLLM():
    # create LLM object:
    return(GPT4All(model=lib_path,verbose=False,repeat_penalty=1.5))

# a little prompt engineering is needed to get the answers in a usable format:
template_="""The prompt that follows is a question you must answer:
    
    Question: the input you must answer {question}

    Format your answer as a brief article
      
    Begin! ...
    """    

# try your hand at prompt engineering by playing with this template: (rename the variable below to 'template')
template_llama_rename_me_to_template_if_needed="""
    The prompt below is a question to answer.
    You are a gangster from 1940
    If you don't know the answer, celebrate that you don't know and congratulate the user, don't try to make up an answer.
    Use the following format:

    Question: the input question you must answer {question}

    Begin! Remember to speak as an educator when giving your answer and do not use emojis. 
    Do not add prefixes like Human: and AI:. 
    Do not prefix your answer with any caveat.
    
    Keep the Answer to under 150 words.
    If asked to write a poem, make that the priority and ensure every line in your response uses iambic pentameter.

    Answer: Step through this with me ...
    """    

template="""You are a helpful virtual technology and IT assistant. Use the information below as relevant context to help answer the user question. Don't blindly make things up. If you don't know the answer, just say that you don't know, don't try to make up an answer. Keep the answer as concise as possible.

INFORMATION:
American cellist and fan of chocolate ice cream, Jakob Giovanni Taylor is 26 years old. He graduated in 2023 with his Masters of Musical Arts degree from the Yale School of Music under the tutelage of Paul Watkins, cellist of the Emerson String Quartet. Born in New York City, Taylor began playing the cello at the age of three. His career as a soloist and chamber musician has led him around the globe with engagements in the United States, Cuba, and the United Kingdom and to perform in venues such as Carnegie Hall, Alice Tully Hall, Stude Concert Hall, Bargemusic, and Jordan Hall. Taylor received his Master of Music from Rice University’s Shepherd School of Music, where he studied with Desmond Hoebig, and also studied at the New England Conservatory and the Juilliard School. Taylor is the recipient of the Harvey R. Russell Scholarship and Irving S. Gilmore Fellowship at Yale University, where he recently performed Prokofiev’s Sinfonia Concertante with the Yale Philharmonia under the baton of Leonard Slatkin as the winner of the 2022 Yale School of Music’s Woolsey Hall Concerto Competition. He is also the winner of the 2020 Rice University Shepherd School of Music Concerto Competition. Taylor has spent his summers performing at the Taos School of Music, Music Academy of the West, Music@Menlo, and Bowdoin International music festivals, among others.

QUESTION:
{question}?

ANSWER:"""

user_input = "BEGIN"
index_name = create_index_in_redis(redis_connection=redis_connection)

# UI loop: (if user responds with "END" - program ends)
while True:

    ## useful examples:
    # https://blog.baeke.info/2023/03/21/storing-and-querying-for-embeddings-with-redis/ 
    # https://github.com/RediSearch/RediSearch/blob/master/docs/docs/vecsim-range_queries_examples.ipynb
    sentences = [display_menu()]
    user_input = sentences
    model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')
    # create the numpy array encoding representation of the sentences/prompt:
    embeddings = model.encode(sentences)
    # convert the embedding numpy array to bytes for use in Redis Hash:
    embedding_vector_as_bytes = embeddings.tobytes()

    # pass the user text/prompt to the LLM Chain and print out the response: 
    # also, check for a suitable cached response
    if user_input:
        start_time=time.perf_counter()
        trimmed_question = compact_string_for_keyname(sentences)
        prompt_hash = {
            "prompt_used": sentences[0],
            "embedding": embedding_vector_as_bytes,
            "response_key": ""
        }

        if not redis_connection.exists(f"prompt:{trimmed_question}"):
            redis_connection.hset(name=f"prompt:{trimmed_question}", mapping=prompt_hash)

        results = vec_search(redis_connection.ft(index_name),embedding_vector_as_bytes)
        # only write the response to an empty prompt: hashkey
        # due to the sortby this should always be the one at zero index
        # we expect at most 10 docs (KNN 10 is specified in query)
        # they are in asc distance order - smaller the distance the better
        found_useful_result = False
        llm_response = ""
        for next_result in results:
            if not next_result.response_key == "":
                # ensure that we only reuse a response that is suitable
                # cached responses are stored as strings in redis 
                # and the keyname for the relevant string is stored in the 
                # response attribute of the prompt Hash object in Redis.
                # This decouples the storage of the answer allowing for more reuse
                # answers stored this way can easily be edited and all similar prompts will 
                # point to this now, updated response|answer
                if (float(next_result.knn_dist) < .2) and (next_result.response_key != "") :
                    print(f'\nFound a match! -->\n {next_result}\n')
                    found_useful_result = True
                    # llm_reponse_cache_key should point to a string in redis:
                    llm_response_cache_key=next_result.response_key
                    print(f'keyname of cached response: {llm_response_cache_key}')
                    llm_response=redis_connection.get(llm_response_cache_key)
            if found_useful_result: 
                # write the nearby result as the answer to this object in redis
                # in this way, multiple prompts will share the same result
                redis_connection.hset(results[0].id,'response_key',llm_response_cache_key)
                break
        # we have exhausted all the potential matches:
        if not found_useful_result:
            print('\n No suitable response has been cached.  Generating new Response...\n')
            # create a new AI-generated result as the answer            
            ## Setup the LLM PromptTemplate so it can be added to the chain:
            prompt_template=PromptTemplate(template=template,input_variables=['question'])
            
            # bring prompt and LLM chain together:
            llmChain = LLMChain(prompt=prompt_template,llm=create_and_fetchLLM())

            llm_response = llmChain.run(user_input)

            x = redis_connection.incr('prompt:responsekeycounter')
            # store the full response in a string in redis under the keyname prompt:response:x
            redis_connection.set(f'prompt:response:{x}',llm_response)
            # write the cached response keyname to the response attribute in redis:
            # due to sorting of the results by KNN distance ASC the first result should be our target:
            redis_connection.hset(results[0].id,'response_key',(f'prompt:response:{x}'))            
        
        # output whatever the result it to the User Interface:
        print(f'{spacer}{llm_response}{spacer}\n')
        uparrows = " ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ \n"
        print(f'\t{uparrows}\tElapsed Time to respond to user prompt was: {(time.perf_counter()-start_time)*1} seconds\n')

