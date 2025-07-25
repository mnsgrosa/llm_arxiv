from fastmcp import FastMCPClient
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

async def main():
    client = FastMCPClient('http://localhost:8000')
    llm = ChatGoogleGenerativeAI(model = 'gemini-pro')

    tools = await client.get_tools()