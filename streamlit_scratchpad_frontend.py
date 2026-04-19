import streamlit as st

# Chat input (accepts both text + optional file)
user_input = st.chat_input(
    "Type Here",
    accept_file=True,
    file_type=["jpg", "jpeg"]
)

# When user sends something
if user_input:
    # Show user message
    with st.chat_message("user"):
        st.write(user_input)["text"]

    # Show same message as bot response
    with st.chat_message("assistant"):
        st.write(user_input)