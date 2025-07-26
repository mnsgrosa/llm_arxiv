import asyncio
import gradio as gr
import json
import os
from typing import List, Tuple, Dict, Any
from datetime import datetime

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.tools import ToolException

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from dotenv import load_dotenv
load_dotenv()

class MCPTool(BaseTool):
    '''MCP Tool wrapper for LangChain'''
    
    def __init__(self, name: str, description: str, mcp_session: ClientSession):
        super().__init__(name=name, description=description)
        self.mcp_session = mcp_session
    
    def _run(self, **kwargs) -> str:
        return asyncio.run(self._arun(**kwargs))
    
    async def _arun(self, **kwargs) -> str:
        try:
            result = await self.mcp_session.call_tool(self.name, kwargs)
            return json.dumps(result.content, indent=2)
        except Exception as e:
            raise ToolException(f'MCP tool error: {str(e)}')

class ChatPaperAgent:
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.mcp_session = None
        self.tools = []
        self.agent_executor = None
        self.memory = ConversationBufferWindowMemory(
            memory_key = 'chat_history',
            return_messages = True,
            k=10  
        )
        self.chat_history = []
        self.current_papers = {} 
        
    async def initialize(self):
        '''Initialize MCP connection and create the conversational agent'''
        server_params = StdioServerParameters(
            command = 'python -m llm_arxiv.mcp.mcp_server',
            env = None
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.mcp_session = session
                await session.initialize()
                
                tools_result = await session.list_tools()
                for tool_info in tools_result.tools:
                    mcp_tool = MCPTool(
                        name = tool_info.name,
                        description = tool_info.description,
                        mcp_session = session
                    )
                    self.tools.append(mcp_tool)
                
                llm = ChatGroq(
                    groq_api_key=self.groq_api_key,
                    model_name='llama3-8b-8192',
                    temperature=0.3,  # Slightly higher for more conversational responses
                    max_tokens=1024
                )
                
                # Create conversational prompt
                prompt = ChatPromptTemplate.from_messages([
                    ('system', '''You are a knowledgeable research assistant that helps users explore and discuss academic papers. 

                    Available tools:
                    - scrape_arxiv_papers: Get new papers from arXiv on a topic
                    - search_stored_papers: Search papers already in the database  
                    - get_or_scrape_papers: Smart search (tries database first, then arXiv)
                    - list_available_topics: Show what topics are in the database

                    Guidelines:
                    1. Be conversational and engaging when discussing papers
                    2. When users ask about papers, first check if you have relevant ones, then search/scrape if needed
                    3. Summarize key findings in an accessible way
                    4. Ask follow-up questions to help users dive deeper into interesting aspects
                    5. Remember previous papers discussed in this conversation
                    6. If users ask about specific papers by title, search for them
                    7. Offer to find related papers when appropriate

                    Remember: You're having a conversation about research, not just answering isolated questions.'''),
                    ('placeholder', '{chat_history}'),
                    ('human', '{input}'),
                    ('placeholder', '{agent_scratchpad}')
                ])

                agent = create_tool_calling_agent(llm, self.tools, prompt)
                self.agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    memory=self.memory
                )
    
    async def chat(self, message: str) -> str:
        '''Process a chat message and return response'''
        if not self.agent_executor:
            return 'Agent not initialized. Please restart the interface.'
        
        try:
            context_message = message
            if self.current_papers:
                paper_titles = list(self.current_papers.keys())[:3]  # Mention last 3 papers
                context_message += f"\n\n[Context: We've recently discussed these papers: {', '.join(paper_titles)}]"
            
            result = await self.agent_executor.ainvoke({
                'input': context_message,
                'chat_history': self.memory.chat_memory.messages
            })
            
            response = result['output']
            
            self._extract_papers_from_response(response)

            self.chat_history.append((message, response))
            
            return response
            
        except Exception as e:
            return f'Sorry, I encountered an error: {str(e)}'
    
    def _extract_papers_from_response(self, response: str):
        '''Extract paper titles from agent response to maintain context'''
        if 'title' in response.lower() or 'paper' in response.lower():
            # This is a simplified version - in practice you'd parse the JSON response
            # from your MCP tools to extract actual paper data
            pass
    
    def get_chat_history(self) -> List[Tuple[str, str]]:
        '''Get formatted chat history for Gradio'''
        return self.chat_history
    
    def clear_history(self):
        '''Clear chat history'''
        self.chat_history = []
        self.current_papers = {}
        self.memory.clear()

agent = None

async def initialize_agent():
    '''Initialize the agent - call this once'''
    global agent
    if agent is None:
        agent = ChatPaperAgent()  
        await agent.initialize()
    return agent

def chat_fn(message: str, history: List[List[str]]) -> Tuple[str, List[List[str]]]:
    '''Gradio chat function'''
    if not message.strip():
        return '', history
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        if agent is None:
            loop.run_until_complete(initialize_agent())
        
        response = loop.run_until_complete(agent.chat(message))
        
        history.append([message, response])
        
        return '', history
    
    except Exception as e:
        error_response = f'Error: {str(e)}'
        history.append([message, error_response])
        return '', history
    
    finally:
        loop.close()

def clear_chat():
    '''Clear chat history'''
    if agent:
        agent.clear_history()
    return []