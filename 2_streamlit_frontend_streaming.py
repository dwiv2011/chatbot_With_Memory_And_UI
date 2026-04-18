import streamlit as st
from langgraph_backend import chatmodel
from langchain_core.messages import HumanMessage

# st.session_state -> dict -> 
CONFIG = {'configurable': {'thread_id': 'thread-1'}}
if 'message_history' not in st.session_state: # session state is dictiornary which does not get reset after every enter press, saves the memory
    st.session_state['message_history']=[]

# message_history=[] # it get reset in every iteration
user_input=st.chat_input('Type here') # input box

for message in st.session_state['message_history']: #“Print all previous messages again”
    with st.chat_message(message['role']):
        st.text(message['content'])


if user_input:
    #first add the message to history,
    #why because streamlit does not store the previous messages
    st.session_state['message_history'].append({'role':'user','content':user_input})
    with st.chat_message('user'): #“Everything inside this block belongs to the assistant’s chat bubble”
        st.text(user_input)

    with st.chat_message('Assistant'):
        ai_message=st.write_stream( #stream the response chunk by chunk
            message_chunk.content for message_chunk,metadata in chatmodel.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages' # Means the model returns output as message chunks

            )
        )
    st.session_state['message_history'].append({'role':'Assistant','content':ai_message})
