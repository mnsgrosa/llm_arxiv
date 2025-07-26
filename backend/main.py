from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import inspect
from .schemas import ToolsResponse, ToolCallResponse, ToolCallRequest, ToolInfo
from ..mcp.mcp_server import scrape_arxiv_papers, search_stored_papers, get_or_scrape_papers, list_available_topics

app = FastAPI(title="ArXiv Paper HTTP API", version="1.0.0")

def handle_tool_execution(func, **kwargs):
    """Generic handler for tool execution with consistent error handling"""
    try:
        result = func(**kwargs)
        
        if isinstance(result, dict) and 'error' in result:
            return StandardResponse(
                data=None, 
                error=result['error'], 
                success=False
            )
        
        return StandardResponse(data=result, success=True)
        
    except Exception as e:
        return StandardResponse(
            data=None, 
            error=str(e), 
            success=False
        )

@app.get("/tools", response_model=ToolsResponse)
async def get_tools():
    '''
    Get list of available tools with their schemas
    '''
    tools = [
        ToolInfo(
            name="scrape_arxiv_papers",
            description="Scrapes papers from arXiv for a given topic and stores them in the database",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The research topic to search for"},
                    "max_results": {"type": "integer", "description": "Maximum number of papers to scrape", "default": 10}
                },
                "required": ["topic"]
            }
        ),
        ToolInfo(
            name="search_stored_papers", 
            description="Searches for papers in the local database based on topic similarity",
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The research topic to search for"},
                    "max_results": {"type": "integer", "description": "Maximum number of results to return", "default": 10}
                },
                "required": ["topic"]
            }
        ),
        ToolInfo(
            name="get_or_scrape_papers",
            description="Attempts to get papers from database first, scrapes from arXiv if none found", 
            inputSchema={
                "type": "object",
                "properties": {
                    "topic": {"type": "string", "description": "The research topic to search for"},
                    "max_results": {"type": "integer", "description": "Maximum number of results to return", "default": 10}
                },
                "required": ["topic"]
            }
        ),
        ToolInfo(
            name="list_available_topics",
            description="Lists topics currently stored in the database",
            inputSchema={
                "type": "object", 
                "properties": {
                    "limit": {"type": "integer", "description": "Maximum number of topics to return", "default": 20}
                },
                "required": []
            }
        )
    ]
    
    return ToolsResponse(tools=tools)


@app.post('/scrape', response_model=StandardResponse)
async def scrape_papers(request: ScrapeRequest):
    '''
    Scrape arXiv papers for a given topic
    '''
    return handle_tool_execution(
        scrape_arxiv_papers,
        topic=request.topic,
        max_results=request.max_results
    )

@app.post('/search', response_model=StandardResponse) 
async def search_papers(request: SearchRequest):
    '''
    Search stored papers by topic similarity
    '''
    return handle_tool_execution(
        search_stored_papers,
        topic=request.topic,
        max_results=request.max_results
    )

@app.post('/get_or_scrape', response_model=StandardResponse)
async def get_or_scrape(request: GetOrScrapeRequest):
    '''
    Get papers from database or scrape if not found
    '''
    return handle_tool_execution(
        get_or_scrape_papers,
        topic=request.topic,
        max_results=request.max_results
    )


@app.post('/topics', response_model=StandardResponse)
async def list_topics(request: ListTopicsRequest):
    '''
    List available topics in the database
    '''
    return handle_tool_execution(
        list_available_topics,
        limit=request.limit
    )

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "arxiv-paper-http-server"}

if __name__ == '__main__':
    print("Starting HTTP API server...")
    print("Available endpoints:")
    print("- GET /tools")
    print("- POST /call_tool") 
    print("- GET /health")
    uvicorn.run(app, host = '0.0.0.0', port = 9001, log_level = 'info')