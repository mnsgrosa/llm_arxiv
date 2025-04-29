import streamlit as st
from agents.agent import LLMAgent


if 'response' not in st.session_state:
    st.session_state.response = {}

if 'trending' not in st.session_state:
    st.session_state.trending = []

if 'lattest' not in st.session_state:
    st.session_state.lattest = []

if 'get_trending' not in st.session_state:
    st.session_state.get_trending = []

if 'get_lattest' not in st.session_state:
    st.session_state.get_lattest = []

agent = LLMAgent()

st.set_page_config(page_title="LLM Papers with Code", page_icon=":books:", layout = 'wide')
st.title("Agentic queries for papers with Code")

st.markdown('''# How to use the agentic paper scraper
1. Enter your prompt asking to add the papers wheter they are trending or lattest to the database.
2. The agent will get if you want to add trending or lattest papers to the database.
3. Click the submit prompt button.
4. The streamlit will show all the papers that were added.
5. After you've added the papers to the choosen database you can query the topic and how many papers you want to get.
6. The agent will query the database and return the papers.
'''
)

with st.form('input_prompt'):
    prompt = st.text_input('Input your prompt')
    submit = st.form_submit_button('Submit prompt')

if submit:
    try:
        response = agent.run(prompt)
        st.write(f'Latest response from the prompt {response}')
    except Exception as e:
        st.error(f'Error retrieving the response: {e}')

if st.session_state.response:
    data = response.get('data')
    endpoint = response.get('endpoint_called')
    if endpoint['method'] == 'POST':
        if endpoint['action'] == 'post_trending_papers':
            st.session_state.trending = data.get('message')
            st.write('Trending papers added successfully')
            st.write(st.session_state.trending)
        elif endpoint['action'] == 'post_lattest_papers':
            st.session_state.lattest = data.get('message')
            st.write('Lattest papers added successfully')
            st.write(st.session_state.lattest)
    if endpoint['method'] == 'GET':
        if endpoint['action'] == 'get_trending_papers':
            st.session_state.get_trending = data.get('papers')
            st.write('Trending papers retrieved successfully')
            st.write(st.session_state.get_trending)
        elif endpoint['action'] == 'get_lattest_papers':
            st.session_state.get_lattest = data.get('papers')
            st.write('Lattest papers retrieved successfully')
            st.write(st.session_state.get_lattest)