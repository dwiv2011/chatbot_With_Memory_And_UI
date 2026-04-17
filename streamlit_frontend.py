import streamlit as st
from langgraph_backend import chatmodel
from langchain_core.messages import HumanMessage

# st.session_state -> dict -> 
CONFIG = {'configurable': {'thread_id': 'thread-1'}}
if 'message_history' not in st.session_state: # session state is dictiornary whoch does not get reset after every enter press
    st.session_state['message_history']=[]

# message_history=[] # it get reset in every iteration
user_input=st.chat_input('Type here')

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


if user_input:
    #first add the message to history,
    #why because streamlit does not store the previous messages
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
        st.text(user_input)

    response= chatmodel.invoke({'messages':[HumanMessage(content=user_input)]}, config=CONFIG)
    ai_message=response['messages'][-1].content
    st.session_state['message_history'].append({'role':'assistant','content':ai_message})
    with st.chat_message('Assistant'):
        st.text(ai_message)
