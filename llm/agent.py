from langchain.tools import BaseTool
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import httpx
import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

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

class MCPToolManager:
    '''
    Manager class to handle multiple MCP tools and LangChain integration
    '''

    def __init__(self, mcp_server_url: str = 'http://localhost:8000'):
        self.mcp_server_url = mcp_server_url
        self.tools: List[MCPTool] = []

        async def discover_tools(self) -> List[Dict[str, Any]]:
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
                You are a helpful AI assistant with access to MCP (Model Context Protocol) tools.
                Use the available tools to help answer questions and tasks.
                always explain what tools you're using and why
                '''

            prompt = ChatPromptTemplate.from_messages([
                ('system', system_prompt),
                ('human', '{input}'),
                ('placeholder', '{agent_scratchpad}')
            ])

            agent = create_openai_functions_agent(llm, self.tools, prompt)

            return AgentExecutor(
                agent = agent,
                tools = self.tools,
                verbose = True,
                handle_parsing_errors = True
            )

async def main():
    mcp_manager = MCPToolManager('http://localhost:8000')

    await mcp_manager.setup_tools()

    llm = ChatOpenAI(
        model= 'gpt-4',
        temperature = 0,
        api_key = ...
    )

    AgentExecutor = mcp_manager.create_agent(llm)

    result = await agent_executor.ainvoke({
        'input': ...
    })

    print(result['output'])

if __name__ == '__main__':
    asyncio.run(main())