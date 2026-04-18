import streamlit as st
from langgraph_backend import chatmodel
from langchain_core.messages import HumanMessage
import uuid

# =========================================================
# Utility Functions
# =========================================================

def genetrate_thread_id():
    """
    Generates a unique thread ID using UUID.

    Note:
    - Returns a UUID object (not string). This may affect display/serialization.
    - Typo in function name ('genetrate') reduces readability.
    """
    return uuid.uuid4()


def reset_chat():
    """
    Resets the current chat session:
    - Creates a new thread_id
    - Adds it to thread list
    - Clears UI message history

    Design Note:
    - Old conversation is not explicitly persisted here; relies on backend.
    """
    st.session_state['thread_id'] = genetrate_thread_id()
    add_thread(st.session_state['thread_id'])
    st.session_state['message_history'] = []


def add_thread(thread_id):
    """
    Adds a thread_id to session state if not already present.

    Performance Note:
    - Uses list → O(n) lookup. Acceptable for small scale.
    """
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id)


def load_conversation(thread_id):
    """
    Loads conversation state from LangGraph backend.

    Assumptions:
    - state.values exists
    - 'messages' key exists inside values

    Risk:
    - Tight coupling with backend schema
    """
    state = chatmodel.get_state(config={'configurable': {'thread_id': thread_id}})
    return state.values.get('messages', [])


# =========================================================
# Session Setup
# =========================================================

# Initialize message history (persists across reruns)
if 'message_history' not in st.session_state:
    st.session_state['message_history'] = []

# Initialize thread_id
if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = genetrate_thread_id()

# Initialize thread list
if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads'] = []

if 'thread_labels' not in st.session_state:
    st.session_state['thread_labels'] = {}

# Ensure current thread is tracked
add_thread(st.session_state['thread_id'])

# Config passed to LangGraph
# ⚠️ NOTE: This becomes stale if thread_id changes later
CONFIG = {'configurable': {'thread_id': st.session_state['thread_id']}}


# =========================================================
# Chat Input
# =========================================================

user_input = st.chat_input('Type here')  # Input box for user


# =========================================================
# Render Previous Messages
# =========================================================

#Re-renders full chat history on every Streamlit rerun.

#Note:
#- Streamlit reruns script top-to-bottom on every interaction
#- session_state preserves memory across runs

for message in st.session_state['message_history']:
    with st.chat_message(message['role']):
        st.text(message['content'])


# =========================================================
# Sidebar UI
# =========================================================

st.sidebar.title('Langgraph Chatbot')

# Button to start new chat
if st.sidebar.button('New Chat'):
    reset_chat()

st.sidebar.title('My Conversation')

# Display all threads
for thread_id in st.session_state['chat_threads']:
    
    label = st.session_state['thread_labels'].get(thread_id, str(thread_id))
    
    if st.sidebar.button(label):

        # Switch active thread
        st.session_state['thread_id'] = thread_id

        # Load messages from backend
        messages = load_conversation(thread_id)

        temp_messages = []

        # Convert backend messages → UI format
        for msg in messages:
            if isinstance(msg, HumanMessage):
                role = 'user'
            else:
                # ⚠️ Assumes all non-human messages are assistant
                role = 'assistant'

            temp_messages.append({'role': role, 'content': msg.content})

            # ⚠️ ISSUE:
            # This assignment is inside loop → repeated updates
            st.session_state['message_history'] = temp_messages


# =========================================================
# Handle User Input
# =========================================================

if user_input:

    thread_id = st.session_state['thread_id']

    # Generate label only once per thread
    if thread_id not in st.session_state['thread_labels']:
        label = user_input.strip().replace("\n", " ")
        label = label[:30] + "..." if len(label) > 30 else label
        st.session_state['thread_labels'][thread_id] = label

    # Store user message first (important for UI consistency)
    st.session_state['message_history'].append({
        'role': 'user',
        'content': user_input
    })

    # Render user message immediately
    with st.chat_message('user'):
        st.text(user_input)

    # =====================================================
    # Assistant Response (Streaming)
    # =====================================================

    with st.chat_message('Assistant'):  # ⚠️ Should be 'assistant'
        ai_message = st.write_stream(
            message_chunk.content 
            for message_chunk, metadata in chatmodel.stream(
                {'messages': [HumanMessage(content=user_input)]},
                config=CONFIG,
                stream_mode='messages'
            )
        )

    # Store assistant response
    st.session_state['message_history'].append({
        'role': 'Assistant',  # ⚠️ Inconsistent casing
        'content': ai_message
    })
