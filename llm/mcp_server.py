from fastmcp import FastMCP
from shared_paper_tools import PaperToolsCore
from typing import Dict, List, Any

mcp = FastMCP()
paper_tools = PaperToolsCore()

@mcp.tool()
async def scrape_arxiv_papers(topic: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Scrapes papers from arXiv for a given topic and stores them in the database and return a string with the papers or error message
    
    Args:
        topic[str]: The research topic to search for
        max_results[int]: Maximum number of papers to scrape (default: 10)
    
    Returns:
        Success or error message
    """
    return  paper_tools.scrape_arxiv_papers(topic, max_results)

@mcp.tool()
async def search_stored_papers(topic: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Searches for papers in the local database based on topic similarity.
    
    Args:
        topic[str]: The research topic to search for
        max_results[int]: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing titles and abstracts of matching papers
    """
    return  paper_tools.search_stored_papers(topic, max_results)

@mcp.tool()
async def get_or_scrape_papers(topic: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Attempts to get papers from database first, scrapes from arXiv if none found.
    
    Args:
        topic[str]: The research topic to search for
        max_results[int]: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing paper data or error information
    """
    return  paper_tools.get_or_scrape_papers(topic, max_results)

@mcp.tool()
async def list_available_topics(limit: int = 20) -> List[str]:
    """
    Lists topics currently stored in the database.
    
    Args:
        limit[int]: Maximum number of topics to return (default: 20)
    
    Returns:
        List of available topics
    """
    return  paper_tools.list_available_topics(limit)

if __name__ == '__main__':
    print("Starting MCP server...")
    mcp.run(transport = 'sse',
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )