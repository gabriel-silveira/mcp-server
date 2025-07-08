from fastapi.responses import JSONResponse
from langchain_arcade import ToolManager
from typing import Dict, Any
import json
import time
from pydantic import BaseModel
from uuid import uuid4

from src.services.oauth_service import get_microsoft_auth_url, get_google_auth_url

from src.utils import create_error_response, create_success_response, MCPErrorCode
from src.logs import tools_logger
from src.config import ARCADE_API_KEY
from src.tools.tools_args import _clean_microsoft_createandsendemail_args, _clean_scrape_args, _clean_default_args

# Request/Response models
class ToolCallParams(BaseModel):
    name: str
    arguments: Dict[str, Any]

# Initialize tool manager
manager = ToolManager(
    api_key=ARCADE_API_KEY,
)

# Initialize tools
raw_tools = manager.init_tools(
    toolkits=[
        "Web",
        "Search",
        "Google",
        "Microsoft",
        "Github",
        "Slack",
        "Linkedin",
        "X",
        "Confluence",
        "Jira",
        "Trello",
        "Notion",
        "Dropbox",
        "Reddit",
    ],
)

# Função auxiliar para encontrar uma ferramenta pelo nome
def find_tool_by_name(name: str):
    """Find a tool by its name in raw_tools."""
    for tool in raw_tools:
        if tool.name == name:
            return tool
    return None

def _create_auth_response(request_id: int, tool_name: str, url: str) -> JSONResponse:
    """Create authentication response for tools requiring authentication."""

    tools_logger.info(f"Creating authentication response for tool: {tool_name}")

    return JSONResponse(
        content={
            "error": {
                "code": -32003,
                "data": {
                    "id": f"ar_{uuid4().hex[:24]}",
                    "type": "url",
                    "url": url,
                    "message": {
                        "text": "Autorização necessária. Por favor, clique no link para autorizar."
                    }
                },
                "message": "interaction_required"
            },
            "id": request_id,
            "jsonrpc": "2.0"
        },
        status_code=200
    )


def _format_result(result: Any) -> str:
    """Format tool execution result to markdown content."""
    if isinstance(result, dict) and "markdown" in result:
        return result["markdown"]
    elif isinstance(result, str):
        return result
    else:
        return str(result) if result is not None else ""


async def handle_tool_call(request_id: int, tool_name: str, arguments: Dict[str, Any]) -> JSONResponse:
    """Handle tool execution requests"""
    correlation_id = str(uuid4())
    start_time = time.time()
    
    tools_logger.info(f"[{correlation_id}] Tool '{tool_name}' called with arguments: {json.dumps(arguments, indent=2)}")

    tool = find_tool_by_name(tool_name)
    if not tool:
        return create_error_response(request_id, MCPErrorCode.METHOD_NOT_FOUND, f"Tool {tool_name} not found")

    tools_logger.info(f"Tool found: {tool}")

    try:
        # Clean and validate arguments based on tool type
        if hasattr(tool, 'args_schema'):
            schema = tool.args_schema.model_json_schema()
            
            # Nota: Aqui ainda estamos usando os nomes antigos para compatibilidade com as funções de limpeza
            # Se necessário, você pode atualizar essas condições para usar os nomes originais
            if tool_name == 'microsoft_createandsendemail':
                arguments = await _clean_microsoft_createandsendemail_args(arguments, schema, request_id, correlation_id)
                if isinstance(arguments, JSONResponse):  # If error response
                    return arguments
            elif tool_name == 'Web_ScrapeUrl':
                arguments = _clean_scrape_args(arguments, schema)
            else:
                arguments = _clean_default_args(arguments, schema)
        
        tools_logger.info(f"[{correlation_id}] Final cleaned arguments for tool '{tool_name}': {json.dumps(arguments, indent=2)}")
        
        if manager.requires_auth(tool_name):
            auth_response = manager.authorize(tool_name, "user_123")
        
            if auth_response.status != "completed":
                # Solicite ao usuário que visite a URL para autorização
                tools_logger.info(f"Visit the following URL to authorize: {auth_response.url}")
                return _create_auth_response(request_id, tool_name, auth_response.url)

        result = await tool.arun(arguments)
        execution_time = time.time() - start_time

        tools_logger.info(f"Tool result: {result}")
        
        tools_logger.info(
            f"[{correlation_id}] Tool '{tool_name}' completed in {execution_time:.2f}s with result: "
            f"{json.dumps(result, indent=2) if result else 'None'}"
        )
        
        # Format result and return success response
        markdown_content = _format_result(result)
        return create_success_response(request_id, {
            "content": [{"type": "text", "text": markdown_content}]
        })
    except Exception as e:
        tools_logger.error(f"[{correlation_id}] Error executing tool '{tool_name}': {str(e)}")
        
        # Handle authentication errors
        #error_str = str(e)
        #if 'Interrupt' in error_str and 'user_id is required' in error_str:
        #    return _create_auth_response(request_id, tool_name)
            
        return create_error_response(request_id, MCPErrorCode.INTERNAL_ERROR, str(e))