import asyncio
import json
import os
import logging
from typing import List, Tuple, Dict, Any

from langchain_groq import ChatGroq
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
from langchain.tools import BaseTool
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
    def __init__(self):
        self.groq_api_key = os.getenv('GROQ_API_KEY')
        self.server_url = 'http://llm_arxiv-mcp-server-1:8000/sse/'
        self.mcp_session = None
        self.tools = []
        self.agent_executor = None
        self.logger = logging.getLogger(__name__)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        self.llm = ChatGroq(
            groq_api_key=self.groq_api_key,
            model_name='llama3-8b-8192',
            temperature=0.3,
            max_tokens=1024
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ('system', '''You are a knowledgeable research assistant that helps users explore and discuss academic papers. 

            Guidelines:
            1. Be conversational and engaging when discussing papers
            2. When users ask about papers, scrape or search within your tools
            3. Summarize key findings in an accessible way
            4. Ask follow-up questions to help users dive deeper into interesting aspects
            5. If users ask about specific papers by title, search for them
            6. Whenever the response contains the title, abstract and link place the name of item alongside
            7. Whenever you use a tool tell the user something in the lines "searching arxiv about <paper>" or "getting db about <paper>"
            8. Whenever prompted to get papers don't look at your memory use the tools provided

            Remember: You're having a conversation about research, not just answering isolated questions.'''),
            ('placeholder', '{chat_history}'),
            ('human', '{input}'),
            ('placeholder', '{agent_scratchpad}')
        ])


        if not self.logger.handlers:
            file_handler = logging.FileHandler('chat_history.log')
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        self.chat_history = []
        self.current_papers = {} 
    
    async def chat(self, message: str, chat_history:  List[str]) -> Dict[str, Any]:
        '''Process a chat message and return response'''
        logging.info('Starting chat')
        try:
            async with sse_client(self.server_url) as (read, write):
                self.logger.info("SSE connection established")
                
                async with ClientSession(read, write) as session:
                    self.logger.info("MCP session created")
                    await session.initialize()
                    self.logger.info("MCP session initialized")
                    
                    tools = await load_mcp_tools(session)
                    self.logger.info(f"Loaded {len(tools)} tools")
                    
                    agent = create_tool_calling_agent(self.llm, tools, self.prompt)
                    agent_executor = AgentExecutor(
                        agent=agent,
                        tools=tools,
                        verbose=True,
                        handle_parsing_errors=True,
                        max_iterations=3
                    )
                    
                    self.logger.info("Agent created, invoking...")
                    
                    result = await agent_executor.ainvoke({
                        'input': message,
                        'chat_history': chat_history
                    })
                    
                    self.logger.info("Agent invocation successful!")
                    return {'message': result['output'], 'success': True}
                    
        except Exception as e:
            self.logger.error(f"Error in chat: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {'message': f'Sorry, I encountered an error: {str(e)}', 'success': False}


    def chat_sync(self, message: str) -> Dict[str, Any]:
        yield asyncio.run(self.chat(message))
    
    def get_chat_history(self) -> List[Tuple[str, str]]:
        '''Get formatted chat history for Gradio'''
        return self.chat_history
    
    def clear_history(self):
        '''Clear chat history'''
        self.chat_history = []
        self.current_papers = {}

agent = None

async def initialize_agent(mcp_command: List[str] = None):
    '''Initialize the agent - call this once'''
    global agent
    if agent is None:
        agent = ChatPaperAgent()  
        await agent.initialize()
    return agent



def clear_chat():
    '''Clear chat history'''
    if agent:
        agent.clear_history()
    return []