import datetime
import logging
import os
import httpx
import json
from google.adk.runners import Runner
from google.adk.events import Event
from google.adk.sessions import InMemorySessionService
from google.adk.tools import FunctionTool
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

def call_get_fastapi_endpoint(endpoint:str, query:str, n_results:int) -> Dict[str, Union[str, Dict[str, str]]]:
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
        return {'data': response.json().get('papers')}
    except:
        return {'error': 'invalid response'}

def call_post_fastapi_endpoint(endpoint:str):
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
        return {'status': response.json().get('papers')}
    except:
        return {'error': 'invalid response'}

post_tool = FunctionTool(func = call_post_fastapi_endpoint)
get_tool = FunctionTool(func = call_get_fastapi_endpoint)

agent = Agent(
        name="endpoint_scraper_agent",
        model="gemini-2.0-flash-exp",
        description=(
            "Agent to manipulate my endpoint and return the papers stored at the chroma db"
        ),
        instruction=(
            "You are a helpful data scientist researcher agent that can scrape papers from PapersWithCode and store them in a chroma db."
        ),
        tools=[post_tool, get_tool]
    )

runner = Runner(
            agent = agent,
            app_name = APP_NAME,
            session_service = session_service
)


def run(query):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response: ", final_response)
            return final_response
