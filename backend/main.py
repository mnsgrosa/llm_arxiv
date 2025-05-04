from fastapi import FastAPI, HTTPException
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse
from scraper.paperscraper import PaperScraper
from db.chroma import DBClient
from backend.schemas import Request
from uuid import uuid4
import json

app = FastAPI()
scraper = PaperScraper()
db_trending = DBClient('/tmp/chroma/trending')
db_lattest = DBClient('/tmp/chroma/lattest')

@app.post('/papers/post/trending')
def add_trending_papers():
    try:
        trending = scraper.returnable_text(page = 'trending')
        for paper in trending:
            db_trending.add_context(str(uuid4()), paper)
        return {'message': 'Trending papers added successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/trending')
def get_trending_papers(query: str, n_results: int):
    try:
        trending = db_trending.query(query, n_results)
        return {'papers': trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/papers/post/lattest')
def add_latest_papers():
    try:
        lattest = scraper.returnable_text(page = 'lattest')
        for paper in lattest:
            db_lattest.add_context(str(uuid4()), paper)
        return {'message': 'Latest papers added successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/lattest')
def get_latest_papers(query: str, n_results: int):
    try:
        lattest = db_lattest.query(query, n_results)
        return {'papers': lattest}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8501)
