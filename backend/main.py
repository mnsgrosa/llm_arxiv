from fastapi import FastAPI, HTTPException,Request, WebSocket
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse, StreamingResponse
from scraper.paperscraper import PaperScraper
from db.chroma import DBClient
from backend.schemas import Request
from uuid import uuid4
import json
import asyncio

app = FastAPI()
scraper = PaperScraper()
db_trending = DBClient('/tmp/chroma/trending')
db_lattest = DBClient('/tmp/chroma/lattest')

message_queue = asyncio.Queue()
agent_queue = asyncio.Queue()

@app.post('/papers/post/trending')
async def add_trending_papers():
    try:
        trending = scraper.returnable_text(page = 'trending')
        for paper in trending:
            db_trending.add_context(str(uuid4()), paper)
        return {'message': 'Trending papers added successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/trending')
async def get_trending_papers(query: str, n_results: int):
    try:
        trending = db_trending.query(query, n_results)
        return {'papers': trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post('/papers/post/lattest')
async def add_latest_papers():
    try:
        lattest = scraper.returnable_text(page = 'lattest')
        for paper in lattest:
            db_lattest.add_context(str(uuid4()), paper)
        return {'message': 'Latest papers added successfully'}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get('/papers/get/lattest')
async def get_latest_papers(query: str, n_results: int):
    try:
        lattest = db_lattest.query(query, n_results)
        return {'papers': lattest}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket('/chat')
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()

    async def forward_agent_messages():
        while True:
            response = await agent_queue.get()
            await websocket.send_text(response)
            agent_queue.task_done()


    forward_task = asyncio.create_task(forward_agent_messages())

    try:
        while True:
           message = await websocket.receive_text()
           if message == 'exit':
               break
           await message_queue.put(message)
    except Exception as e:
        await websocket.send_text(f"Error: {str(e)}")
    finally:
        forward_task.cancel()
        try:
            await forward_task
        except asyncio.CancelledError:
            pass

@app.websocket('/agent_ws')
async def websocket_agent(websocket: WebSocket):
    await websocket.accept()

    async def forward_client_messages():
        while True:
            message = await message_queue.get()
            await websocket.send_text(message)
            message_queue.task_done()

    forward_task = asyncio.create_task(forward_client_messages())

    try:
        while True:
            response = await websocket.receive_text()
            await agent_queue.put(response)
    except Exception as e:
        print(f"Agent WebSocket error: {e}")
    finally:
        forward_task.cancel()
        try:
            await forward_task
        except asyncio.CancelledError:
            pass

    

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8501)
