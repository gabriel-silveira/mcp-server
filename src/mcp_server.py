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
    toolkits=["Google"]
)

# MCP endpoint
@app.post("/mcp")
@app.get("/mcp")
async def mcp_endpoint(request: Request):
    if request.method == "GET":
        return JSONResponse(content={
            "name": "Arcade Tools MCP Server",
            "version": "1.0.0",
            "capabilities": {
                "tools": {
                    "web_scrape": {
                        "name": "web_scrape",
                        "description": "Scrape content from a URL",
                        "parameters": {
                            "url": "string"
                        }
                    },
                    "google_search": {
                        "name": "google_search",
                        "description": "Search on Google",
                        "parameters": {
                            "query": "string"
                        }
                    }
                }
            }
        })
    
    data = await request.json()
    method = data.get("method")
    
    if method == "initialize":
        return JSONResponse(content={
            "name": "Arcade Tools MCP Server",
            "version": "1.0.0",
            "capabilities": {
                "tools": True
            }
        })
    
    elif method == "listTools":
        return JSONResponse(content={
            "tools": [
                {
                    "name": "web_scrape",
                    "description": "Scrape content from a URL",
                    "parameters": {
                        "url": "string"
                    }
                },
                {
                    "name": "google_search",
                    "description": "Search on Google",
                    "parameters": {
                        "query": "string"
                    }
                }
            ]
        })
    
    elif method == "invokeTool":
        tool_name = data.get("tool")
        params = data.get("parameters", {})
        
        if tool_name == "web_scrape":
            result = await tools[0].arun({"url": params.get("url")})
            return JSONResponse(content={"result": result})
        
        elif tool_name == "google_search":
            result = await tools[1].arun({"query": params.get("query")})
            return JSONResponse(content={"result": result})
        
        else:
            return JSONResponse(content={"error": f"Tool {tool_name} not found"}, status_code=404)
    
    return JSONResponse(content={"error": f"Method {method} not supported"}, status_code=400)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2906)
