from src.utils import create_error_response
from src.tools.base import handle_tool_call, tools, ToolCallParams
from src.logs import tools_logger
from src.schemas.mcp_schemas import MCPErrorCode
from src.config import server_name, server_version

def get_server_info():
    """Get server information and capabilities"""
    return {
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
    }

def get_initialize_response(request_id: int):
    """Get initialization response"""
    return {
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
    }

def get_initialized_notification_response(request_id: int):
    """Get initialized notification response"""
    return {
        "id": request_id,
        "jsonrpc": "2.0",
        "result": None
    }

def get_tools_list_response(request_id: int):
    """Get list of available tools"""
    # Log básico da solicitação
    tools_logger.info(f"Solicitação de listagem de ferramentas (request_id: {request_id})")
    
    return {
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
    }

async def handle_tool_request(request_id: int, params: dict):
    """Handle tool execution request"""
    try:
        params = ToolCallParams(**params or {})
        return await handle_tool_call(request_id, params.name, params.arguments)
    except Exception as e:
        tools_logger.error(f"Error processing tool call: {str(e)}")
        return create_error_response(request_id, MCPErrorCode.INTERNAL_ERROR, str(e))
