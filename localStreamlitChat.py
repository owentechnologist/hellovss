# to run execute: > streamlit run localStreamlitChat.py 
# UI framework for humans:
import streamlit as st

st.title('Is This Thing On?')
# get input:
text_input = st.text_input('What is your question? (prompt)')

# pass the user text to the LLM Chain and print out the response: 
if text_input:
    llm_response = llmChain.run(text_input)
    st.write(llm_response)
#    st.write(text_input)
    

