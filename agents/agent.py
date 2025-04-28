import logging
import os
from scraper.paperscraper import PaperScraper
from uuid import uuid4
from dotenv import load_dotenv
from smolagents import tool, CodeAgent, InferenceClientModel, HfApiModel, LiteLLMModel
from typing import List
from db.chroma import DBClient

load_dotenv()

@tool
def add_trending_papers() -> str:
    '''
    Add trending papers to the database.
    '''
    scrapper = PaperScraper()
    trending_papers = scrapper.returnable_text(page = 'trending')
    db = DBClient(persist_dir = '/tmp/chroma/trending')
    for paper in trending_papers:
        db.add_context(str(uuid4()), paper)
    return 'Done'

@tool
def get_related_trending_papers(query: str, n_results: int = 5) -> str:
    '''
    Get related trending papers based on a search query.

    Args:
        query: The search query to find related papers
        n_results: The number of desired results to return

    Returns:
        A string containing the related trending papers
    '''
    db = DBClient(persist_dir = '/tmp/chroma/trending')
    return db.query(query, n_results)

@tool
def add_lattest_papers_to_db() -> str:
    '''
    Add lattest papers to the database.
    '''
    scrapper = PaperScraper()
    lattest_papers = scrapper.returnable_text(page = 'lattest')
    db = DBClient(persist_dir = '/tmp/chroma/lattest')
    for paper in lattest_papers:
        db.add_context(str(uuid4()), paper)
    return 'Done'

@tool
def get_related_lattest_papers(query: str, n_results: int = 5) -> str:
    '''
    Get related latest papers based on a search query.

    Args:
        query: The search query to find related papers
        n_results: The number of desired results to return

    Returns:
        A string containing the related latest papers
    '''
    db = DBClient(persist_dir = '/tmp/chroma/lattest')
    return db.query(query, n_results)

class LLMAgent:
    def __init__(self):
        key = os.getenv('HF_TOKEN')
        self.model = HfApiModel(
            model_id='meta-llama/Llama-3.3-70B-Instruct',
            api_key=key
        )

        self.agent = CodeAgent(
            tools = [add_trending_papers, get_related_trending_papers, add_lattest_papers_to_db, get_related_lattest_papers],
            model = self.model
        )

    def run(self, prompt: str) -> str:
        return self.agent.run(prompt)