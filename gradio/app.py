import asyncio
import gradio as gr
from ..llm.agent import chat_fn, initialize_agent

agent = None

async def main():
    global agent
    agent = await initialize_agent()

    gr.ChatInterface(
        fn = chat_fn,
        type = 'message'
    ).launc()

if __name__ == '__main__':
    asyncio.run(main())