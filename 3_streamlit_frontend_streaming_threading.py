import streamlit as st
from langgraph_backend import chatmodel
from langchain_core.messages import HumanMessage
import uuid

#********* Utility Function ****************#
def genetrate_thread_id():
    return uuid.uuid4()

def reset_chat():
    st.session_state['thread_id']=genetrate_thread_id()
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history']=[]


def add_thread(thread_id):
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)

def load_conversation(thread_id):
    state = chatmodel.get_state(config={'configurable': {'thread_id': thread_id}})
    # Check if messages key exists in state values, return empty list if not
    return state.values.get('messages', [])

#**********************Session Setup ******************#
if 'message_history' not in st.session_state: # session state is dictiornary which does not get reset after every enter press, saves the memory
    st.session_state['message_history']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id']=genetrate_thread_id()

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]
add_thread(st.session_state['thread_id'])

CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


# message_history=[] # it get reset in every iteration
user_input=st.chat_input('Type here') # input box

#“Print all previous messages again”
for message in st.session_state['message_history']: 
    with st.chat_message(message['role']):
        st.text(message['content'])

#******************* SideBar UI ***************************/
st.sidebar.title('Langgraph Chatbot')
if st.sidebar.button('New Chat'):
    reset_chat()
st.sidebar.title('My Conversation')

for thread_id in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread_id)):
        st.session_state['thread_id'] = thread_id
        messages = load_conversation(thread_id)
        temp_messages = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role='user'
            else:
                role='assistant'
            temp_messages.append({'role': role, 'content': msg.content})

            st.session_state['message_history'] = temp_messages




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
