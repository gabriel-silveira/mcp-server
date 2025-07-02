import json
import time
from typing import Dict, Any
from uuid import uuid4
from fastapi.responses import JSONResponse

from src.utils import create_error_response, create_success_response, MCPErrorCode
from src.logs import tools_logger
from .base import tools
from .args import get_firecrawl_scrape_args, get_gmail_sendemail_args

async def handle_tool_call(request_id: int, tool_name: str, arguments: Dict[str, Any]) -> JSONResponse:
    """Handle tool execution requests"""
    correlation_id = str(uuid4())
    start_time = time.time()
    
    tools_logger.info(f"[{correlation_id}] Tool '{tool_name}' called with arguments: {json.dumps(arguments, indent=2)}")
    
    if tool_name not in tools:
        return create_error_response(request_id, MCPErrorCode.METHOD_NOT_FOUND, f"Tool {tool_name} not found")
    
    try:
        tool = tools[tool_name]
        
        # Get tool-specific arguments
        if tool_name == 'scrapeurl':
            arguments = get_firecrawl_scrape_args(arguments)
        elif tool_name == 'gmail_sendemail':
            arguments = get_gmail_sendemail_args(arguments)
        
        # Log final arguments before execution
        tools_logger.info(f"[{correlation_id}] Executing tool with arguments: {json.dumps(arguments, indent=2)}")
        
        result = await tool.arun(arguments)
        execution_time = time.time() - start_time
        
        tools_logger.info(
            f"[{correlation_id}] Tool '{tool_name}' completed in {execution_time:.2f}s with result: "
            f"{json.dumps(result, indent=2) if result else 'None'}"
        )
        
        # Format result
        markdown_content = (
            "" if result is None
            else result if isinstance(result, str)
            else result["markdown"] if isinstance(result, dict) and "markdown" in result
            else str(result)
        )
        
        return create_success_response(request_id, {
            "content": [{"type": "text", "text": markdown_content}]
        })
        
    except Exception as e:
        tools_logger.error(f"[{correlation_id}] Error executing tool: {str(e)}")
        return create_error_response(request_id, MCPErrorCode.INTERNAL_ERROR, str(e))
