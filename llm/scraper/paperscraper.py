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
        try:
            get_topic_url = self.base_url + self.topic + f'&start=0&max_results={self.max_results}'
            with httpx.Client() as client:
                data = client.get(get_topic_url).text
            soup = BeautifulSoup(data, 'xml')
            entries = soup.find_all('entry')
            
            papers = []

            for entry in entries:
                paper_info = {
                    'title': entry.find('title').text.strip() if entry.find('title') else None,
                    'summary': entry.find('summary').text.strip() if entry.find('summary') else None,
                    'url': None
                }
                
                links = entry.find_all('link')
                for link in links:
                    if (link.get('title') == 'pdf' and link.get('type') == 'application/pdf') or (link.get('rel') == 'alternate' and link.get('type') == 'text/html'):
                        paper_info['url'] = link['href']
                
                papers.append(paper_info)

            self.papers_title_list = []
            self.papers_abstract_list = []
            self.papers_link_list = []

            topic_id = uuid4().hex

            for paper in papers:
                paper_id = uuid4().hex
                title_id = uuid4().hex
                abstract_id = uuid4().hex
                link_id = uuid4().hex

                self.papers_link_list.append({
                    'ids':link_id,
                    'documents':paper.get('url', ''),
                    'metadatas':{
                        'paper_url':paper.get('url', ''),
                        'document_type': 'link',
                        'title':paper.get('title', ''),
                        'paper_id': paper_id,
                        'topic': topic_id,
                        }
                    }
                )

                self.papers_title_list.append({
                        'ids': title_id,
                        'documents':paper.get('title', ''),
                        'metadatas':{
                            'paper_url':paper.get('url', ''),
                            'document_type': 'title',
                            'title': paper.get('title', ''),
                            'paper_id': paper_id,
                            'topic': topic_id,
                            }
                        }
                    )

                self.papers_abstract_list.append({
                        'ids': abstract_id,
                        'documents':paper.get('summary', ''),
                        'metadatas':{
                            'paper_url':paper.get('url', ''),
                            'document_type': 'abstract',
                            'abstract': paper.get('summary', ''),
                            'paper_id': paper_id,
                            'topic':topic_id,
                            }
                        }
                    )
            
            topics = {
                'ids': topic_id,
                'documents': self.topic,
            }

            self.data = {'titles': self.papers_title_list, 'abstracts': self.papers_abstract_list, 'links':self.papers_link_list, 'topic':topics}
            return self.data
        except Exception as e:
            return {}