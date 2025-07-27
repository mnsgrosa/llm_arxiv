import asyncio
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
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent

from mcp import ClientSession
from mcp.client.sse import sse_client

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
    def __init__(self, mcp_command: List[str] = None):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.server_url = 'http://localhost:8000/sse'
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
        try:
            async with sse_client(self.server_url) as (read, write):
                async with ClientSession(read, write) as session:
                    self.mcp_session = session
                    await session.initialize()
                    
                    self.tools = await load_mcp_tools(session)
                    
                    llm = ChatGroq(
                        groq_api_key=self.groq_api_key,
                        model_name='llama3-8b-8192',
                        temperature=0.3,
                        max_tokens=1024
                    )
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
                        8. Whenever the response contains the title and abstract place the name of item alongside

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
                    
        except Exception as e:
            print(f"Failed to connect to MCP server at {self.server_url}: {e}")
            raise
    
    async def chat(self, message: str) -> str:
        '''Process a chat message and return response'''
        if not self.agent_executor:
            return 'Agent not initialized. Please restart the interface.'
        
        try:
            context_message = message
            if self.current_papers:
                paper_titles = list(self.current_papers.keys())[:3]  
                context_message += f"\n\n[Context: We've recently discussed these papers: {', '.join(paper_titles)}]"
            
            result = await self.agent_executor.ainvoke({
                'input': context_message,
                'chat_history': self.memory.chat_memory.messages
            })
            
            response = result['output']

            self.chat_history.append((message, response))
            
            return response
            
        except Exception as e:
            return f'Sorry, I encountered an error: {str(e)}'
    
    def _extract_papers_from_response(self, response: str):
        '''Extract paper titles from agent response to maintain context'''
        if not response:
            return {}

        response_words = response.split(' ')
        titles = [title.strip('title:') if 'title' in title else None for title in response_words]
        abstracts = [abstract.strip('abstract:') if 'abstract' in abstract else None for abstract in response_words]
        
        return {'titles': titles, 'abstracts': abstracts}
        
    def get_chat_history(self) -> List[Tuple[str, str]]:
        '''Get formatted chat history for Gradio'''
        return self.chat_history
    
    def clear_history(self):
        '''Clear chat history'''
        self.chat_history = []
        self.current_papers = {}
        self.memory.clear()

agent = None

async def initialize_agent(mcp_command: List[str] = None):
    '''Initialize the agent - call this once'''
    global agent
    if agent is None:
        default_command = ["python", "-m", "your_mcp_server"]
        if mcp_command:
            command = mcp_command
        else:
            env_command = os.getenv('MCP_SERVER_COMMAND')
            command = env_command.split() if env_command else default_command
        
        agent = ChatPaperAgent(mcp_command=command)  
        await agent.initialize()
    return agent



def clear_chat():
    '''Clear chat history'''
    if agent:
        agent.clear_history()
    return []