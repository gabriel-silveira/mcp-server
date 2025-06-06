from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from langchain_arcade import ArcadeToolManager
from config import ARCADE_API_KEY

# Cria a aplicação FastAPI
app = FastAPI()

# Initialize Arcade tool manager
manager = ArcadeToolManager(api_key=ARCADE_API_KEY)

# Initialize tools
tools = manager.init_tools(
    tools=["Web.ScrapeUrl"],
    toolkits=["Google"],
)

server_name = "Arcade Tools MCP Server"
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
                        "name": "web_scrape",
                        "description": "Scrape content from a URL",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "url": {
                                    "type": "string",
                                    "description": "URL to scrape content from"
                                }
                            },
                            "required": ["url"]
                        }
                    },
                    {
                        "name": "google_search",
                        "description": "Search on Google",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Search query"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        })
    
    elif method == "tools/call":
        tool_name = data.get("params", {}).get("name")
        arguments = data.get("params", {}).get("arguments", {})
        
        if tool_name == "web_scrape":
            result = await tools[0].arun({"url": arguments.get("url")})
            return JSONResponse(content={
                "id": request_id,
                "jsonrpc": "2.0",
                "result": {
                    "output": result
                }
            })
        
        elif tool_name == "google_search":
            result = await tools[1].arun({"query": arguments.get("query")})
            return JSONResponse(content={
                "id": request_id,
                "jsonrpc": "2.0",
                "result": {
                    "output": result
                }
            })
        
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
