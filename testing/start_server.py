import subprocess
import threading
import time
import sys

def run_mcp_server():
    """Run MCP server in thread"""
    subprocess.run([sys.executable, "mcp_server.py"])

def run_http_server():
    """Run HTTP server in thread"""  
    subprocess.run([sys.executable, "http_server.py"])

if __name__ == '__main__':
    print("Starting both MCP and HTTP servers...")
    mcp_thread = threading.Thread(target=run_mcp_server, daemon=True)
    mcp_thread.start()
    
    time.sleep(10)
    
    try:
        run_http_server()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
