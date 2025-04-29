import logging
import os
import httpx
from scraper.paperscraper import PaperScraper
from uuid import uuid4
from dotenv import load_dotenv
from smolagents import tool, CodeAgent, LiteLLMModel
from typing import Dict, Optional, Union
from db.chroma import DBClient
from backend.schemas import Request

load_dotenv()

BASE_URL = 'http://localhost:8000'

endpoints = {
    "post_trending_papers": {
        "method": "POST",
        "path": "/papers/post/trending",
        "description": "Post the lattest papers to the database."
    },
    "get_trending_papers": {
        "method": "GET",
        "path": "/papers/get/trending",
        "description": "Get the trending papers from trending database."
    },
    "post_lattest_papers": {
        "method": "POST",
        "path": "/papers/post/lattest",
        "description": "Post lattest papers to the lattest database"
    },
    "get_lattest_papers": {
        "method": "GET",
        "path": "/papers/get/lattest",
        "description": "Get the lattest papers from lattest database"
    }
}

@tool
def call_fastapi_endpoint(action:str, params:Optional[Dict[str, str]]) -> Dict[str, Union[str, Dict[str, str]]]:
    '''
    Calls FastAPI endpoints to either post papers to databases or retrieve papers based on queries.

    Args:
        action (str): The endpoint action to perform. Options are:
            - "post_trending_papers": Scrapes and stores trending papers in trending database
            - "post_lattest_papers": Scrapes and stores latest papers in latest database
            - "get_trending_papers": Retrieves papers from trending database based on query
            - "get_lattest_papers": Retrieves papers from latest database based on query
        
        params (Optional[Dict[str, Union[str, int]]]): Parameters for GET requests:
            - For get_*_papers actions: Must include:
                - "query": str - The search query for papers
                - "n_results": int - Number of papers to retrieve
            - For post_*_papers actions: No parameters needed
    
    Returns:
        Dict containing:
            - 'data': The API response data
            - 'endpoint_called': Details about the called endpoint
            - 'error': Error message if request failed
    
    Examples:
        # To post trending papers to database:
        call_fastapi_endpoint("post_trending_papers", None)
        
        # To search in trending database:
        call_fastapi_endpoint("get_trending_papers", {"query": "machine learning", "n_r
    '''
    if action not in endpoints:
        return {'error': 'invalid action'}
    
    endpoint = endpoints[action]
    method = endpoint['method']
    path = endpoint['path']

    if method == 'GET':
        response = httpx.get(BASE_URL + path, params = Request(params).model_dump(), timeout = 600)
    elif method == 'POST':
        response = httpx.post(BASE_URL + path, timeout = 600)
    else:
        return {'error': 'invalid method'}

    try:
        return {'data': response.json(),
                'endpoint_called':{
                    'action': action,
                    'method': method,
                }
            }
    except:
        return {'error': 'invalid response'}

class LLMAgent:
    def __init__(self):
        self.model = LiteLLMModel(model_id="gemini/gemini-2.0-flash-lite",
                             api_key=os.getenv("GEMINI_TOKEN")
                )

        self.agent = CodeAgent(
            tools=[call_fastapi_endpoint],
            model=self.model
        )

    def run(self, prompt: str) -> str:
        return self.agent.run(prompt)