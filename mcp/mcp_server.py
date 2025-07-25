from fastmcp import FastMCP
from mcp_tools import TOOLS

mcp = FastMCP()

@mcp.tool
def get_arxiv_files_mcp(topic: str, max_results: int = 10) -> str:
    return get_arxiv_files(topic, max_results)

@mcp.tool  
def get_stored_data_mcp(topic: str):
    return get_stored_data(topic)

if __name__ == '__main__':
    print("Starting MCP server...")
    mcp.run()