import httpx
import json
import logging
from uuid import uuid4
from bs4 import BeautifulSoup

class PaperScraper:
    def __init__(self, topic:str, max_results:int = 10):
        self.base_url = 'https://export.arxiv.org/api/query?search_query=all:'
        self.topic = topic
        self.max_results = max_results
        self.data = {}

    def get_arxiv_papers_data(self):
        get_topic_url = self.base_url + self.topic + f'&start=0&max_results={self.max_results}'
        with httpx.Client() as client:
            data = client.get(get_topic_url).text
        soup = BeautifulSoup(data, 'xml')
        titles = soup.find_all('title')
        summaries = soup.find_all('summary')
        links = soup.find_all('link')

        self.papers_title_list = []
        self.papers_abstract_list = []
        topic_id = uuid4()

        for i in range(len(summaries)):
            paper_id = uuid4()
            title_id = uuid4()
            abstract_id = uuid4()

            self.papers_title_list.append({
                    'ids': title_id,
                    'documents':titles[i],
                    'metadatas':{
                        'paper_url':links[i],
                        'document_type': 'title',
                        'title': titles[i],
                        'paper_id': paper_id,
                        'topic': topic_id
                        }
                    }
                )

            self.papers_abstract_list.append({
                    'ids': abstract_id,
                    'documents':summaries[i],
                    'metadatas':{
                        'paper_url':links[i],
                        'document_type': 'abstract',
                        'abstract': summaries[i],
                        'paper_id': paper_id,
                        'topic':topic_id
                        }
                    }
                )
        
        topics = {
            'ids': topic_id,
            'documents': self.topic,
        }

        self.data = {'titles': self.papers_title_list, 'abstracts': self.papers_abstract_list, 'topic':topics}
        return self.data