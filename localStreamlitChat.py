# to run execute: > streamlit run localStreamlitChat.py 
# UI framework for humans:
import streamlit as st
from langchain.llms import GPT4All
from langchain.chains import LLMChain
from langchain.prompts.prompt import PromptTemplate
#from langchain.agents import Tool, AgentExecutor, AgentOutputParser, LLMSingleActionAgent
#from langchain.prompts import BaseChatPromptTemplate
#from langchain.schema import AgentAction, AgentFinish, HumanMessage

# where is the LLM library of 'weights'?
lib_path = '/Users/owentaylor/Library/Application Support/nomic.ai/GPT4All/llama-2-7b-chat.ggmlv3.q4_0.bin'

# create LLM object:
llm=GPT4All(model=lib_path,verbose=False)

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
    If asked to write a poem, make that the priority and respond in a rhyming fashion.

    Answer: Step through this with me
    """    

text_input=PromptTemplate(template=template,input_variables=['question'])


# bring prompt and LLM chain together:
#try:
llmChain = LLMChain(prompt=text_input,llm=llm)
#except:

#display something:
st.title('Is This Thing On?')
# get input:
text_input = st.text_input('What is your question? (prompt)')

# pass the user text to the LLM Chain and print out the response: 
if text_input:
    llm_response = llmChain.run(text_input)
    st.write(llm_response)
#    st.write(text_input)
    

