from typing import Any
from fastapi.responses import JSONResponse
from src.schemas.mcp_schemas import MCPErrorCode

def create_error_response(request_id: int, code: MCPErrorCode, message: str) -> JSONResponse:
    """Helper function to create error responses"""
    return JSONResponse(
        content={
            "id": request_id,
            "jsonrpc": "2.0",
            "error": {
                "code": code.value,
                "message": message
            }
        },
        status_code=400 if code == MCPErrorCode.METHOD_NOT_FOUND else 500
    )

def create_success_response(request_id: int, result: Any) -> JSONResponse:
    """Helper function to create success responses"""
    return JSONResponse(
        content={
            "id": request_id,
            "jsonrpc": "2.0",
            "result": result
        }
    )
