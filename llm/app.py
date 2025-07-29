import asyncio
import streamlit as st
from agent import ChatPaperAgent

@st.cache_resource
def get_agent():
    return ChatPaperAgent()

agent = get_agent()

if 'messages' not in st.session_state:
    st.session_state['messages'] = []

for message in st.session_state.messages:
    with st.chat_message(message['role']):
        st.markdown(message['content'])

if prompt:= st.chat_input('Chat with arxiv mcp'):
    if 'scrape' in prompt:
        chat_history = []
    st.session_state.messages.append({'role': 'user', 'content': prompt})
    with st.chat_message('user'):
        st.markdown(prompt)

    with st.chat_message('assistant'):
        with st.spinner('Thinking...', show_time=True):
            chat_history = []
            for msg in st.session_state.messages[:-1]:
                if msg["role"] == "user":
                    chat_history.append(msg["content"])
                else:
                    chat_history.append(msg["content"])
            response = asyncio.run(
                    agent.chat(prompt, chat_history)
            )

            if response['success']:
                st.markdown(response['message'])
                st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response['message']
                    })
            else:
                st.error(f"Error: {response['message']}")
