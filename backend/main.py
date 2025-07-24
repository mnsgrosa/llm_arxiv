from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse
from schemas import Title, Abstract, Getter
from db.chroma import DBClient
from backend.schemas import Request
from uuid import uuid4
import json

app = FastAPI()
scraper = PaperScraper()
db_titles = DBClient('/tmp/chroma/titles')
db_abstracts = DBClient('/tmp/chroma/abstracts')

@app.post('/papers/post/titles')
def add_trending_papers(titles:List[Title]):
    try:
        for title in titles:
            db_titles.add_context(ids=[title.ids], documents=[title.documents], metadatas=[title.metadatas])
        return {'message': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/titles')
def get_trending_papers(title: Getter):
    try:
        titles = db_titles.query(title.query, title.n_results)
        return {'papers': titles}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/papers/post/abstracts')
def add_latest_papers(abstracts: List[Abstract]):
    try:
        for abstract in abstracts:
            db_abstracts.add_context(ids=[abstract.ids], documents=[abstract.documents], metadatas=[abstract.metadatas])
        return {'message': 'success'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/abstracts')
def get_latest_papers(abstract: Getter):
    try:
        abstracts = db_abstracts.query(abstract.query, abstract.n_results)
        return {'papers': abstracts}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))