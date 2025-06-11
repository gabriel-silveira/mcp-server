from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langchain_arcade import ArcadeToolManager
from config import ARCADE_API_KEY

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import RedirectResponse

# Cria a aplicação FastAPI
app = FastAPI()

# Initialize tool manager
from langchain_arcade import ToolManager
manager = ToolManager(
    api_key=ARCADE_API_KEY,
)

# Initialize tools
raw_tools = manager.init_tools(
    tools=["Web.ScrapeUrl"],
)

# Map tools by name for easier access
tools = {}
for tool in raw_tools:
    if isinstance(tool.name, str):
        name = tool.name.lower().replace('web_', '')
        tools[name] = tool

@app.get("/auth/google")
async def google_auth():
    """Endpoint para iniciar a autenticação do Google"""
    auth_url = manager.get_auth_url("google")
    return {"auth_url": auth_url}

@app.get("/auth/google/callback")
async def google_callback(code: str):
    """Endpoint para receber o callback do Google após a autenticação"""
    try:
        # Troca o código de autorização por um token
        manager.exchange_code("google", code)
        
        # Inicializa as ferramentas do Google
        google_tools = manager.init_tools(toolkits=["Google"])
        
        # Adiciona as ferramentas do Google ao dicionário
        for tool in google_tools:
            if isinstance(tool.name, str):
                name = tool.name.lower().replace('google_', '')
                tools[name] = tool
        
        return {"message": "Autenticado com sucesso! Você já pode usar as ferramentas do Google."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

server_name = "OAPV Tools MCP Server"
server_version = "1.0.0"

# MCP endpoint
@app.post("/mcp")
@app.get("/mcp")
async def mcp_endpoint(request: Request):
    if request.method == "GET":
        return JSONResponse(content={
            "id": 0,
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "logging": {},
                    "prompts": {},
                    "resources": {},
                    "tools": {}
                },
                "serverInfo": {
                    "name": server_name,
                    "version": server_version
                }
            }
        })
    
    data = await request.json()
    method = data.get("method")
    request_id = data.get("id", 0)
    
    if method == "initialize":
        return JSONResponse(content={
            "id": request_id,
            "jsonrpc": "2.0",
            "result": {
                "protocolVersion": "2025-03-26",
                "capabilities": {
                    "logging": {},
                    "prompts": {},
                    "resources": {},
                    "tools": {}
                },
                "serverInfo": {
                    "name": server_name,
                    "version": server_version
                }
            }
        })
    
    elif method == "notifications/initialized":
        return JSONResponse(
            content={
                "id": request_id,
                "jsonrpc": "2.0",
                "result": None
            },
            status_code=202
        )
    
    elif method == "tools/list":
        return JSONResponse(content={
            "id": request_id,
            "jsonrpc": "2.0",
            "result": {
                "tools": [
                    {
                        "name": tool_name,
                        "description": tool.description,
                        "inputSchema": tool.args_schema.model_json_schema() if hasattr(tool, 'args_schema') else {
                            "type": "object",
                            "properties": {},
                            "required": []
                        }
                    }
                    for tool_name, tool in tools.items()
                ]
            }
        })
    
    elif method == "tools/call":
        tool_name = data.get("params", {}).get("name")
        arguments = data.get("params", {}).get("arguments", {})
        
        if tool_name not in tools:
            return JSONResponse(content={
                "id": request_id,
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Tool {tool_name} not found"
                }
            }, status_code=404)
        
        try:
            tool = tools[tool_name]
            
            # Remove argumentos null e preenche valores padrão
            if hasattr(tool, 'args_schema'):
                schema = tool.args_schema.model_json_schema()
                clean_args = {}
                
                # Copia apenas argumentos não-nulos
                for key, value in arguments.items():
                    if value is not None:
                        clean_args[key] = value
                
                # Preenche valores padrão para argumentos ausentes
                for prop, details in schema.get('properties', {}).items():
                    if prop not in clean_args:
                        if details.get('type') == 'array':
                            clean_args[prop] = ['markdown'] if prop == 'formats' else []
                        elif details.get('type') == 'boolean':
                            clean_args[prop] = False
                        elif details.get('type') == 'integer':
                            clean_args[prop] = 30000 if prop == 'timeout' else 0
                
                arguments = clean_args
            
            result = await tool.arun(arguments)
            
            # Se result for None, criar estrutura padrão
            if result is None:
                result = {
                    "markdown": "",
                    "metadata": {}
                }
            # Se result for string, converter para formato estruturado
            elif isinstance(result, str):
                result = {
                    "markdown": result,
                    "metadata": {}
                }
            
            return JSONResponse(content={
                "id": request_id,
                "jsonrpc": "2.0",
                "result": {
                    "structuredContent": result
                }
            })
        except Exception as e:
            return JSONResponse(content={
                "id": request_id,
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }, status_code=500)
        
        else:
            return JSONResponse(content={
                "id": request_id,
                "jsonrpc": "2.0",
                "error": {
                    "code": -32601,
                    "message": f"Tool {tool_name} not found"
                }
            }, status_code=404)
    
    return JSONResponse(content={
        "id": request_id,
        "jsonrpc": "2.0",
        "error": {
            "code": -32601,
            "message": f"Method {method} not supported"
        }
    }, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2906)
