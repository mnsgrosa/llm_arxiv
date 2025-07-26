from typing import Dict, Any, List
from ..scraper.paperscraper import PaperScraper
from ..db.chroma import DBClient

class PaperToolsCore:
    """Core business logic for paper tools - shared between MCP and LangChain"""
    
    def __init__(self):
        self.titles_db = DBClient('/tmp/chroma/titles')
        self.abstracts_db = DBClient('/tmp/chroma/abstracts')
        self.topics_db = DBClient('/tmp/chroma/topics')
    
    def scrape_arxiv_papers(self, topic: str, max_results: int = 10) -> Dict[str, Any]:
        """Core scraping logic"""
        try:
            scraper = PaperScraper(topic=topic, max_results=max_results)
            data = scraper.get_arxiv_papers_data()
            
            self.titles_db.add_context(**data['titles'])
            self.abstracts_db.add_context(**data['abstracts'])
            self.topics_db.add_context(**data['topic'])
            
            return data
        except Exception as e:
            return {'error': str(e)}

    def search_stored_papers(self, topic: str, max_results: int = 10) -> Dict[str, Any]:
        """Core search logic"""
        try:
            topic_results = self.topics_db.query(query=topic, n_results=1)
            
            if not topic_results or not topic_results.get('documents'):
                return {'error': 'No matching topics found in database', 'titles': [], 'abstracts': []}
            
            similar_topic = topic_results['documents'][0]
            
            titles_results = self.titles_db.query(query=similar_topic, n_results=max_results)
            abstracts_results = self.abstracts_db.query(query=similar_topic, n_results=max_results)
            
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

    def get_or_scrape_papers(self, topic: str, max_results: int = 10) -> Dict[str, Any]:
        """Core get-or-scrape logic"""
        try:
            stored_papers = self.search_stored_papers(topic, max_results)
            
            if stored_papers.get('error') or not stored_papers.get('titles'):
                scrape_result = self.scrape_arxiv_papers(topic, max_results)
                if scrape_result and 'error' not in scrape_result:
                    stored_papers = self.search_stored_papers(topic, max_results)
                    stored_papers['scraped'] = True
                else:
                    return {'error': f'Both database search and scraping failed. Scrape error: {scrape_result}'}
            else:
                stored_papers['scraped'] = False
                
            return stored_papers
        except Exception as e:
            return {'error': f'Unexpected error: {str(e)}'}

    def list_available_topics(self, limit: int = 20) -> List[str]:
        """Core topics listing logic"""
        try:
            all_topics = self.topics_db.get_all(limit=limit)
            return all_topics.get('documents', [])
        except Exception as e:
            return ['error']