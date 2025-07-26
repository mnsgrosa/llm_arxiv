from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_groq import ChatGroq
import httpx
import asyncio
import os
from dotenv import load_dotenv
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

def create_groq_llm(model: str = 'llama3-8b-8192') -> ChatGroq:
    '''
    Creates the free llm with groq api key
    '''
    load_dotenv()
    api_key = os.getenv('GROQ_API_KEY')

    return ChatGroq(
        model = model,
        temperature = 0.1,
        groq_api_key = api_key,
        max_tokens = 4096
    )

class MCPTool(BaseTool):
    '''
    Custom LangChain tool to interface with FastMCP server
    '''

    name: str = 'mcp_tool'
    description: str = 'Execute MCP server operations'
    mcp_server_url: str = Field(default = 'http://localhost:8000')
    tool_name: str = Field(...)

    def __init__(self, mcp_server_url: str, tool_name: str, description: str = None, **kwargs):
        super().__init__(
            name = f'mcp_{tool_name}',
            description = description or f'Execute {tool_name} operation via MCP server',
            mcp_server_url = mcp_server_url,
            tool_name = tool_name,
            **kwargs
        )
    
    def _run(self, **kwargs) -> str:
        '''
        Synchronous execution - runs async code in event loop
        '''
        try:
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(self._arun(**kwargs))
        except RuntimeError:
            return asyncio.run(self._arun(**kwargs))

    async def _arun(self, **kwargs) ->str:
        '''
        Execute MCP tool asynchronously
        '''
        async with httpx.AsyncClient() as client:
            try:
                payload = {
                    'tool': self.tool_name,
                    'arguments': kwargs
                }

                response = await client.post(
                    f'{self.mcp_server_url}/call_tool',
                    json = payload,
                    timeout = 30
                )
                response.raise_for_status()

                result = response.json()

                if 'content' in result:
                    if isinstance(result['content'], list):
                        return '\n'.join([item.get('text', str(item)) for item in result['content']])
                    return str(result['content'])
                
                return str(result)

            except httpx.RequestError as e:
                return f'Error calling MCP server: {str(e)}'
            except Exception as e:
                return f'Unexpected error: {e}'

class MCPChat:
    '''
    Manager class to handle multiple MCP tools and LangChain integration
    '''
    def __init__(self, mcp_server_url: str = 'http://localhost:8000'):
        self.mcp_server_url = mcp_server_url
        self.tools: List[MCPTool] = []
        self.agent_executor = None
        self.conversation_history = []

        self.memory = ConversationBufferWindowMemory(
            k = memory_k,
            memory_key = 'chat_history',
            return_messages = True
        )

        async def discover_tools(self) -> List[Dict[str, Any]]:
            '''
            Gets the tools exposed by the fastapi backend
            '''
            async with httpx.AsyncClient() as client:
                try:
                    response = await client.get(f'{self.mcp_server_url}/tools')
                    response.raise_for_status()
                    return response.json().get('tools', [])
                except Exception as e:
                    print(f'Error discovering MCP tools: {e}')
                    return []
        
        async def setup_tools(self) -> List[MCPTool]:
            '''
            Setup Langchain tools from MCP server capabilities
            '''
            discover_tools = await self.discover_tools()

            for tool_info in discover_tools:
                tool = MCPTool(
                    mcp_server_url = self.mcp_server_url,
                    tool_name = tool_info['name'],
                    description = tool_info.get('description', f"MCP: tool:{tool_info['name']}")
                )
                self.tools.append(tool)
            
            return self.tools

        def create_agent(self, llm, system_prompt: str = None) -> AgentExecutor:
            '''
            Create a LangChain agent with MCP tools
            '''

            if not self.tools:
                raise ValueError('No MCP tools available. Run setup_tools() first')

            if system_prompt is None:
                system_prompt = '''
                You are a helpful AI research assistant with access to MCP tools for paper scraping and ChromaDB operations.
                
                Available capabilities:
                - Scrape academic papers from various sources
                - Store and retrieve information from ChromaDB vector database
                - Maintain context across our conversation
                
                Always:
                - Explain what tools you're using and why
                - Reference previous parts of our conversation when relevant
                - Ask clarifying questions if needed
                - Provide detailed explanations of your findings
                '''

            prompt = ChatPromptTemplate.from_messages([
                ('system', system_prompt),
                ('human', '{input}'),
                ('placeholder', '{chat_history}'),
                ('placeholder', '{agent_scratchpad}')
            ])

            agent = create_openai_functions_agent(llm, self.tools, prompt)

            self.agent_executor = AgentExecutor(
                agent = agent,
                tools = self.tools,
                memory = self.memory,
                verbose = True,
                handle_parsing_errors = True,
                max_iterations = 5,
                return_intermediate_steps = True
            )
            return self.agent_executor

    async def chat(self, user_input: str) -> Dict[str, Any]:
        '''
        Send message to interact with the model
        '''
        if not self.agent_executor:
            raise ValueError('Agent not initialized. Run create_agent() first.')
        
        try:
            self.conversation_history({'role':'user', 'content':user_input})
            result = await self.agent_executor.ainvoke({
                'input': user_input
            })

            self.conversation_history.append({'role':'assistant', 'content':result['output']})
            return {
                'response': result['output'],
                'intermediate_steps': result.get('intermediate_steps', []),
                'conversation_length': len(self.conversation_history)
            }
        except Exception as e:
            error_msg = f"Error during conversation: {e}"
            self.conversation_history.append({"role": "system", "content": error_msg})
            return {'response': error_msg, 'intermediate_steps': [], 'error': True}

    def get_conversation_history(self) -> List[Dict[str, str]]:
        '''
        Get the full conversation history
        '''
        return self.conversation_history.copy()

    def clear_conversation(self):
        '''
        Clear conversation history and memory
        '''
        self.conversation_history.clear()
        self.memory.clear()
        print("Conversation history cleared.")

    def save_conversation(self, filename: str):
        '''
        Save conversation to a file
        '''
        import json
        with open(filename, 'w') as f:
            json.dump(self.conversation_history, f, indent=2)
        print(f"Conversation saved to {filename}")

async def main():
    '''
    Example of usage of MCP agent
    '''
    mcp_manager = MCPToolManager('http://localhost:8000')
    
    print("Discovering MCP tools...")
    await mcp_manager.setup_tools()
    print(f"Found {len(mcp_manager.tools)} MCP tools")
    
    try:
        llm = create_groq_llm()
        print("✅ Groq LLM initialized successfully")
    except ValueError as e:
        print(f"❌ Error initializing Groq LLM: {e}")
        print("Get your free API key at: https://console.groq.com/")
        return
    
    agent_executor = mcp_manager.create_agent(llm)
    
    test_query = "What MCP tools are available and what can they do?"
    
    print(f"\n🤖 Query: {test_query}")
    print("=" * 60)
    
    try:
        result = await agent_executor.ainvoke({
            'input': test_query
        })
        print(f"\n📝 Response:\n{result['output']}")
    except Exception as e:
        print(f"❌ Error during execution: {e}")

if __name__ == '__main__':
    asyncio.run(main())