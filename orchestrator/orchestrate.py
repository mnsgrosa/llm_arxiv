from prefect import flow, task
from prefect.states import Completed, Failed
from typing import List, Dict
from scraper.paperscraper import PaperScraper
from backend.schemas import Title, Abstract
from uuid import uuid4
import httpx

@task(log_prints = True)
def scrape_papers(selected_page:str) -> Dict[str, str]:
    try:
        texts = PaperScraper(page = selected_page).returnable_text()
        return texts
    except Exception as e:
        return Failed(message = f'Failed to get {selected_page}:{e}')

@task(log_prints = True)
def post_titles(scraper:List[Dict[str, str]]):
    try:
        with httpx.Client() as client:
            response = client.post()
    except Exception as e:
        return Failed(message = f'Failed to post titles:{e}')

@flow(log_prints = True)
def main_flow():
    lattest = scrape_papers(selected_page = 'latest').submit()
    trending = scrape_papers(selected_page = 'trending').submit()

