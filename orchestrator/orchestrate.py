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
        texts = PaperScraper(page = selected_page).create_data()
        return texts
    except Exception as e:
        raise Exception(f'Failed to get {selected_page}:{e}')

@task(log_prints = True)
def transform_titles(titles:List[Dict[str, str]]):
    try:
        transformed = []
        for title in titles:
            transformed.append(Title(**title))
        return transformed
    except Exception as e:
        raise Exception(f'Failed to transform titles due to:{e}')

@task(log_prints = True)
def transform_abstracts(abstracts: List[Dict[str, str]]):
    try:
        transformed = []
        for abstract in abstracts:
            transformed.append(Abstract(**abstract))
        return transformed
    except Exception as e:
        raise Exception(f'Failed to transform abstract due to:{e}')

@task(log_prints = True)
def post_titles(titles:List[Title]):
    try:
        with httpx.Client() as client:
            response = client.post('http://localhost:8000/papers/post/titles', data = titles.model_dump())
        return Completed(message = 'Succesfully posted the titles of each papers')
    except Exception as e:
        raise Exception(f'Failed to post titles due to:{e}')

@task(log_prints = True)
def post_abstracts(abstracts: List[Abstract]):
    try:
        with httpx.Client() as client:
            response = client.post('http://localhost:8000/papers/post/abstract', data = abstracts.model_dump())
        return Completed(message = 'Succesfully posted the abstract of each paper')
    except Exception as e:
        raise Exception(f'Failed to post abstracts due to:{e}')


@flow(log_prints = True)
def main_flow():
    latest = scrape_papers(selected_page = 'latest')
    trending = scrape_papers(selected_page = 'trending')

    titles = latest['titles'] + trending['titles']
    abstracts = latest['abstracts'] + trending['abstracts']
    
    titles = transform_titles(titles = titles)
    abstracts = transform_abstracts(abstracts = abstracts)

    post_titles(titles = titles)
    post_abstracts(abstracts = abstracts)