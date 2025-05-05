import datetime
import logging
import os
import httpx
import json
import asyncio
import websockets
from google.adk.runners import Runner
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
from google.adk.models.lite_llm import LiteLlm
from google.genai import types
from scraper.paperscraper import PaperScraper
from uuid import uuid4
from dotenv import load_dotenv
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from typing import Dict, Optional, Union
from db.chroma import DBClient
from backend.schemas import Request

load_dotenv()

APP_NAME = 'Papers with code agent'
USER_ID = 'user1'
SESSION_ID = str(uuid4())

BASE_URL = 'http://localhost:8000'

session_service = InMemorySessionService()

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID
)

initial_state = None

session = session_service.create_session(
    app_name=APP_NAME,
    user_id=USER_ID,
    session_id=SESSION_ID,
    state=initial_state
)

GET = {
    "get_trending_papers": {
        "path": "/papers/get/trending",
        "description": "Get the trending papers from the database."
    },
    "get_lattest_papers": {
        "path": "/papers/get/lattest",
        "description": "Get the lattest papers from the database."
    }
}

POST = {
    "post_trending_papers": {
        "path": "/papers/post/trending",
        "description": "Post the lattest papers to the database."
    },
    "post_lattest_papers": {
        "path": "/papers/post/lattest",
        "description": "Post lattest papers to the lattest database"
    }
}

async def connect_to_agent(prompt):
    url = 'ws://localhost:8000/agent_ws'
    async with websockets.connect(url) as agent_ws:
        await agent_ws.send(prompt)
        return await agent_ws.recv()

async def call_get_fastapi_endpoint(endpoint:str, query:str, n_results:int) -> Dict[str, Union[str, Dict[str, str]]]:
    '''
    Calls FastAPI endpoints to either get papers.

    Args:
        endpoint (str): Which endpoint to perform operations. Options are:
            - "get_trending_papers": Retrieves trending papers from the database
            - "get_lattest_papers": Retrieves latest papers from the database  
        query (str): Query to chromadb
        n_results (int): Number of results to retrieve

    Returns:
        Dict containing:
            - 'data': The API response data
            - 'endpoint_called': Details about the called endpoint
            - 'error': Error message if request failed

    Examples:
        # To get trending papers:
        call_get_fastapi_endpoint("get_trending_papers", "machine learning", 10)
    '''
    
    if endpoint not in GET: 
        return {'error': 'invalid action'}

    path = GET[endpoint].get('path')
    response = httpx.get(BASE_URL + path, params = Request(query = query, n_results = n_results).model_dump(), timeout = 600)
    try:
        return {'data': response.json().get('papers'), 'endpoint_called': 'get'}
    except:
        return {'data': 'invalid response'}

async def call_post_fastapi_endpoint(endpoint:str):
    '''
    Calls FastAPI endpoints to either post papers to the latest papers db or the trending.

    Args:
        action (str): The endpoint action to perform. Options are:
            - "post_trending_papers": Scrapes and stores trending papers in trending database
            - "post_lattest_papers": Scrapes and stores latest papers in latest database
            
    Returns:
        Dict containing:
            - 'data': The API response data
            - 'endpoint_called': Details about the called endpoint
            - 'error': Error message if request failed
    
    Examples:
        # To post trending papers to database:
        call_post_fastapi_endpoint("post_trending_papers", None)
    '''
    if endpoint not in POST:
        return {'error': 'invalid action'}
    
    path = POST[endpoint].get('path')

    response = httpx.post(BASE_URL + path, timeout = 600)

    try:
        return {'status': response.json().get('papers'), 'endpoint_called': 'post'}
    except:
        return {'status': 'invalid response'}

post_tool = FunctionTool(func = call_post_fastapi_endpoint)
get_tool = FunctionTool(func = call_get_fastapi_endpoint)

api_interpreter = Agent(
    model = LiteLlm(model = 'openrouter/meta-llama/llama-3-8b-instruct'),
    name = 'api_interpreter',
    description = 'Agent that will interpret if the user wants to post data to db or get',
    instruction = 'You are a helpful agent that can interpret if the user wants to post data to db or get',
    tools = [post_tool, get_tool]
)

researcher = Agent(
    model = 'gemini-2.0-flash-exp',
    name = 'ml_researcher',
    description = 'Agent that can chat about the papers stored in the database',
    instruction = 'You are a machine learning researcher that can chat about papers stored in the database',
    tools = []
)

router = Agent(
    model = LiteLlm(model= 'openrouter/mistralai/mistral-7b-instruct'),
    name = 'router',
    description = 'Agent to route the request to the correct action, api manipulation or chat about the data',
    instruction = '''
        You are an agent that has the role of calling other agents to perform the task prompted by the user.
        1. the first agent is the api_interpreter, he will manipulate the database api whenver prompted.       
        api_interpreter goal:
            Use api_interpreter whenever the user refers to populate the database in specific paperwithcode page(or get papers from the site it might look similar to get from the db but might mean to post to the db),
            if the user doesnt provide the specific topic and isnt clear if it is a query populate the db
            if intended to post at the latest database the endpoint parameter should be 'post_lattest_papers' and trending 'post_trending_papers'
            (e.g., 'i want the papers from latest', 'post papers from trending') -> whenever something similar happers this is a post method call
            get papers from the api that manages the database
            if intended to get at the latest database the endpoint parameter should be 'get_lattest_papers' and trending 'get_trending_papers',
            query should be the topic that the user is interested in and n_results should be the number of papers that the user wants to get
            (e.g., 'i want the 3 latest from reinforcment learning', 'i want the 6 trending papers about computer vision')
        2. the second agent is the researcher, he will chat about the papers stored in the database
        researcher goal:
            use the websocket so the user chats about the paper he got from a query
            IMPORTANT: When using the researcher agent, always include the phrase "researcher: chat about paper" in your response

        and use the researcher agent whenever the user makes a question about a paper to answer the user questions
        do not perform any other actions
    ''',
    sub_agents = [api_interpreter, researcher]
)

runner = Runner(
        agent = router,
        app_name = APP_NAME,
        session_service = session_service   
)


async def run(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = 'No final response captured'
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            final_response = event.content.parts[0].text
            if 'researcher' in final_response.lower() or 'chat about paper' in final_response.lower():
                websocket_response = await connect_to_agent(final_response)
                yield websocket_response
            else:
                yield final_response
            print("Agent Response: ", final_response)
    
    if final_response == 'No final response captured':
        yield final_response
