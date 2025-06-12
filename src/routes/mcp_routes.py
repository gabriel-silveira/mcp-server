from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils import create_error_response
from src.tools import handle_tool_call, tools, ToolCallParams
from src.logs import mcp_logger
from src.schemas.mcp_schemas import MCPRequest, MCPErrorCode
from src.config import server_name, server_version

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
    
    try:
        data = await request.json()
        mcp_request = MCPRequest(**data)
        method = mcp_request.method
        request_id = mcp_request.id or 0
    except ValueError as e:
        mcp_logger.error(f"Invalid request format: {str(e)}")
        return create_error_response(0, MCPErrorCode.INVALID_REQUEST, str(e))
    
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
        try:
            params = ToolCallParams(**mcp_request.params or {})
            return await handle_tool_call(request_id, params.name, params.arguments)
        except Exception as e:
            mcp_logger.error(f"Error processing tool call: {str(e)}")
            return create_error_response(request_id, MCPErrorCode.INTERNAL_ERROR, str(e))
    
    if method not in ["initialize", "notifications/initialized", "tools/list", "tools/call"]:
        return create_error_response(
            request_id,
            MCPErrorCode.METHOD_NOT_FOUND,
            f"Method {method} not supported"
        )

mcp_router = APIRouter()

mcp_router.post("/mcp")(mcp_endpoint)
mcp_router.get("/mcp")(mcp_endpoint)