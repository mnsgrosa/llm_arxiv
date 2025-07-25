import httpx
import json
import logging
from bs4 import BeautifulSoup

class PaperScraper:
    def __init__(self, page = 'latest'):
        self.base_url = 'https://www.paperswithcode.com'
        self.selected_page = page
        self.latest = '/latest'
        self.data = {}

    def get_papers_soup(self, page: str = 'latest'):
        with httpx.Client() as client:
            if page == 'latest':
                response = client.get(self.base_url + self.latest)
            elif page == 'trending':
                response = client.get(self.base_url)
            else:
                logging.error(f'Invalid page: {page}')
                return
            try:
                soup = BeautifulSoup(response.text, 'html.parser')
                self.paper_titles = soup.find_all('a', href=lambda href: href and '/paper/' in href)
                return self.paper_titles
            except Exception as e:
                logging.error(f'Error getting the papers: {e}')
                return

    def get_papers_link(self):
        self.papers_link = [self.base_url + title['href'] for title in self.paper_titles]
        return self.papers_link

    def get_papers_abstract(self):
        self.papers_abstract = []
        for link in self.papers_link:
            with httpx.Client() as client:
                try:
                    response = client.get(link, timeout = 1000)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    abstract_div = soup.find('div', class_='paper-abstract')
                    p_tag = abstract_div.find('p')
                    abstract_text = p_tag.text.strip()
                    self.papers_abstract.append(abstract_text)
                except Exception as e:
                    logging.error(f'Error getting the abstract for {link}: {e}')
                    self.papers_abstract.append(None)
        return self.papers_abstract

    def get_papers_github(self):
        self.papers_github = []
        for link in self.papers_link:
            with httpx.Client() as client:
                try:
                    response = client.get(link, timeout = 1000)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    github_links = soup.find('a', href=lambda href: href and 'github.com' in href)
                    self.papers_github.append(github_links)
                except Exception as e:
                    logging.error(f'Error getting the github link for {link}: {e}')
                    self.papers_github.append(None)
        return self.papers_github

    def create_data(self):
        self.get_papers_soup(self.selected_page)
        self.get_papers_link()
        self.get_papers_abstract()
        self.get_papers_github()
        self.papers_title_list = []
        self.papers_abstract_list = []

        print(f"Lengths: titles={len(self.paper_titles)}, abstracts={len(self.papers_abstract)}, github={len(self.papers_github)}")
        
        for i in range(len(self.paper_titles)):
            title_id = uuid4()
            abstract_id = uuid4()
            paper_id = uuid4()

            self.papers_title_list.append({
                'ids': title_id,
                'documents':self.papers_title[i],
                'metadatas':{
                    'paper_url':self.papers_link[i],
                    'github_url': self.papers_github[i],
                    'document_type': 'title',
                    'title': self.papers_title[i],
                    'paper_id': paper_id
                    }
                }
            )

            self.papers_abstract_list.append({
                'ids': abstract_id,
                'documents':self.papers_abstract[i],
                'metadatas':{
                    'paper_url':self.papers_link[i],
                    'github_url': self.papers_github[i],
                    'document_type': 'abstract',
                    'abstract': self.papers_abstract[i],
                    'paper_id': paper_id
                    }
                }
            )

        self.data = {'titles': self.papers_title_list, 'abstracts': self.papers_abstract_list}

        return self.data