from fastapi import FastAPI, HTTPException
from schemas import ToolCallRequest, ToolCallResponse, ToolsResponse
from typing import List, Dict, Any
import uvicorn
import inspect
from mcp.mcp_tools import TOOLS

app = FastAPI(title = 'ArXiv Paper HTTP API')

def extract_tool_schema(func) -> Dict[str, Any]:
    '''
    Extract schema information from signature and docstring
    '''
    sig = inspect.signature(func)
    doc = inspect.getdoc(func) or ''

    properties = {}
    required = []

    mapper = {
        str: 'string',
        int: 'integer',
        float: 'float',
        bool: 'boolean',
        list: 'array',
        dict: 'object'
    }

    for param_name, param in sig.parameters.items():
        if param_name == 'self':
            continue

        if param.annotation != inspect.Parameter.empty:
            param_type = mapper[param.annotation]

        properties[param_name] = {'type': param_type}

        if 'ARGS:' in doc:
            args_section = doc.split('ARGS:')[1]
            for line in args_section.split('\n'):
                if param_name in line and '[' in line and ']' in line:
                    desc_part = line.split(']:')
                    if len(desc_part) > 1:
                        properties[param_name]['description'] = desc_part[1].strip()
            
            if param.default == inspect.Parameter.empty:
                required.append(param_name)
            
    return {
        'type': 'object',
        'properties': properties,
        'required': required
    }

@app.get('/tools', response = ToolsResponse)
async def get_tools():
    tools = []

    tool_registry = getattr(mcp, '_tools', {})

    for tool_name, tool_func in tool_registry.items():
        schema = extract_tool_schema(tool_func)
        description = inspect.getdoc(tool_func) or f'MCP tool: {tool_name}'

        if 'ARGS:' in description:
            description = description.split('ARGS:')[0].strip()
        else:
            description = description.split('\n')[0].strip()

        tools.append(ToolInfo(
            name = tool_name,
            description = description,
            inputSchema = schema
        ))

    return ToolsResponse(tools = tools)

@app.post('/call_tool', response = ToolCallResponse)
async def call_tool(request: ToolCallRequest):
    try:
        tool_registry = getattr(mcp, '_tools', {})

        if request.tool not in tool_registry:
            raise HTTPException(
                status_code = 404,
                detail = f'Tool {request.tool} not found from {list(tool_registry.keys())}'
            )

        tool_func = tool_registry[request.tool]

        result = tool_func(**request.arguments)

        if asyncio.iscoroutine(result):
            result = await result

        return ToolCallResponse(content = result, isError = False)

    except Exception as e:
        return ToolCallResponse(
            content=f"Error executing tool '{request.tool}': {str(e)}", 
            isError=True
        )

if __name__ == '__main__':
    uvicorn.run(app, host = '0.0.0.0', port = 9001, log_level = 'info')