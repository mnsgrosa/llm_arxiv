from fastmcp import FastMCP
from typing import Dict, Any, List
from .scraper.paperscraper import PaperScraper
from .db.chroma import DBClient

mcp = FastMCP()

titles_db = DBClient('/tmp/chroma/titles')
abstracts_db = DBClient('/tmp/chroma/abstracts')
topics_db = DBClient('/tmp/chroma/topics')

@mcp.tool
def scrape_arxiv_papers(topic: str, max_results: int = 10) -> str:
    """
    Scrapes papers from arXiv for a given topic and stores them in the database.
    
    Args:
        topic: The research topic to search for
        max_results: Maximum number of papers to scrape (default: 10)
    
    Returns:
        Success or error message
    """
    try:
        scraper = PaperScraper(topic=topic, max_results=max_results)
        data = scraper.get_arxiv_papers_data()
        
        titles_db.add_context(**data['titles'])
        abstracts_db.add_context(**data['abstracts'])
        topics_db.add_context(**data['topic'])
        
        return f'Successfully scraped and stored {len(data.get("titles", {}).get("documents", []))} papers for topic: {topic}'
    except Exception as e:
        return f'Failed to scrape papers: {str(e)}'

@mcp.tool
def search_stored_papers(topic: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Searches for papers in the local database based on topic similarity.
    
    Args:
        topic: The research topic to search for
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing titles and abstracts of matching papers
    """
    try:
        topic_results = topics_db.query(query=topic, n_results=1)
        
        if not topic_results or not topic_results.get('documents'):
            return {'error': 'No matching topics found in database', 'titles': [], 'abstracts': []}
        
        similar_topic = topic_results['documents'][0]  # Assuming single result
        
        titles_results = titles_db.query(query=similar_topic, n_results=max_results)
        abstracts_results = abstracts_db.query(query=similar_topic, n_results=max_results)
        
        return {
            'titles': titles_results.get('documents', []),
            'abstracts': abstracts_results.get('documents', []),
            'metadata': {
                'matched_topic': similar_topic,
                'results_count': len(titles_results.get('documents', []))
            }
        }
    except Exception as e:
        return {'error': f'Failed to search papers: {str(e)}', 'titles': [], 'abstracts': []}

@mcp.tool
def get_or_scrape_papers(topic: str, max_results: int = 10) -> Dict[str, Any]:
    """
    Attempts to get papers from database first, scrapes from arXiv if none found.
    
    Args:
        topic: The research topic to search for
        max_results: Maximum number of results to return (default: 10)
    
    Returns:
        Dictionary containing paper data or error information
    """
    try:
        stored_papers = search_stored_papers(topic, max_results)
        
        if stored_papers.get('error') or not stored_papers.get('titles'):
            scrape_result = scrape_arxiv_papers(topic, max_results)
            if 'Successfully' in scrape_result:
                stored_papers = search_stored_papers(topic, max_results)
                stored_papers['scraped'] = True
            else:
                return {'error': f'Both database search and scraping failed. Scrape error: {scrape_result}'}
        else:
            stored_papers['scraped'] = False
            
        return stored_papers
    except Exception as e:
        return {'error': f'Unexpected error: {str(e)}'}

@mcp.tool
def list_available_topics(limit: int = 20) -> List[str]:
    """
    Lists topics currently stored in the database.
    
    Args:
        limit: Maximum number of topics to return (default: 20)
    
    Returns:
        List of available topics
    """
    try:
        all_topics = topics_db.get_all(limit=limit)
        return all_topics.get('documents', [])
    except Exception as e:
        return [f'Error retrieving topics: {str(e)}']

if __name__ == '__main__':
    print("Starting MCP server...")
    mcp.run()