import asyncio
import gradio as gr
from agent import initialize_agent
from typing import List, Tuple, Dict, Any

agent = None

async def chat_fn(message: str, history: List[List[str]]) -> gr.ChatMessage:
    '''Gradio chat function'''
    if not message.strip():
        return gr.ChatMessage(role = 'assistant', content = 'No message')
    
    try:
        if agent is None:
            await initialize_agent()
        
        response = await agent.chat(message)
        
        message = gr.ChatMessage(role = 'assistant', content = response)

        return message
    
    except Exception as e:
        error_response = f'Error: {str(e)}'
        history.append([message, error_response])
        return gr.ChatMessage(role = 'assistant', content = error_response)
    

async def main():
    global agent
    agent = await initialize_agent()
    interface = gr.ChatInterface(
        fn = chat_fn,
        type ='messages'
    )
    
    interface.launch(      
        share = True           
    )

if __name__ == '__main__':
    asyncio.run(main())