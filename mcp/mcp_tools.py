from fastmcp import FastMCP
from typing import Dict, Any
from scraper.paperscraper import PaperScraper
from db.chroma import DBClient

titles_db = DBClient('/tmp/chroma/titles')
abstracts_db = DBClient('/tmp/chroma/abstracts')
topics_db = DBClient('/tmp/chroma/topics')

def get_arxiv_files(topic:str, max_results:int = 10) -> str:
    '''
    Queries the topic provided by user and the number of results desired that the prompt tells you to scrape
    ARGS:
    topic [str]: The main focus of the query
    max_results [int]: If the user didnt specify leave as 10
    '''
    try:
        scraper = PaperScraper(topic = topic, max_results = max_results)
        data = scraper.get_arxiv_papers_data()
        titles_db.add_context(**data['titles'])
        abstracts_db.add_context(**data['abstracts'])
        topics_db.add_context(**data['topic'])
        return 'Successfully added papers to the database.'
    except Exception as e:
        return f'Failed to add papers to the database due to:{e}'

def get_stored_data(topic: str):
    '''
    This function takes a topic that the user is interested at, infer from the user prompt.
    than, you will get a similar topic from the db and use it to querie to title db and topic db
    ARGS:
    topic [str]: The main focus of the query
    '''
    try:
        topic_queried = topics_db.query(query = topic, n_results = 1)
        titles_queried = titles_db.get(topic = topic_queried)
        abstracts_queried = abstracts_db.get(topic = topic_queried)
        return {
            'titles': titles_queried, 'abstracts': abstracts_queried
        }
    except Exception as e:
        return {}


TOOLS = {
    'get_arxiv_files': get_arxiv_files,
    'get_stored_data': get_stored_data
}