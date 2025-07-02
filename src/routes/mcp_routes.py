from fastapi import APIRouter
from fastapi import Request
from fastapi.responses import JSONResponse
from src.utils import create_error_response
from src.logs import mcp_logger
from src.schemas.mcp_schemas import MCPRequest, MCPErrorCode
from src.services import tools_service

async def get_mcp_info():
    """Handle GET /mcp requests - Returns server information"""
    return JSONResponse(content=tools_service.get_server_info())

async def handle_mcp_request(request: Request):
    """Handle POST /mcp requests - Process MCP method calls"""
    try:
        data = await request.json()
        mcp_request = MCPRequest(**data)
        method = mcp_request.method
        request_id = mcp_request.id or 0
    except ValueError as e:
        mcp_logger.error(f"Invalid request format: {str(e)}")
        return create_error_response(0, MCPErrorCode.INVALID_REQUEST, str(e))
    
    if method == "initialize":
        return JSONResponse(content=tools_service.get_initialize_response(request_id))
    
    elif method == "notifications/initialized":
        return JSONResponse(
            content=tools_service.get_initialized_notification_response(request_id),
            status_code=202
        )
    
    elif method == "tools/list":
        return JSONResponse(content=tools_service.get_tools_list_response(request_id))
    
    elif method == "tools/call":
        return await tools_service.handle_tool_request(request_id, mcp_request.params)
    
    return create_error_response(
        request_id,
        MCPErrorCode.METHOD_NOT_FOUND,
        f"Method {method} not supported"
    )

mcp_router = APIRouter()

mcp_router.get("/mcp")(get_mcp_info)
mcp_router.post("/mcp")(handle_mcp_request)