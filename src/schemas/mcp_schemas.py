from pydantic import BaseModel
from typing import Optional, Dict, Any
from enum import Enum

class MCPRequest(BaseModel):
    jsonrpc: str = "2.0"
    method: str
    params: Optional[Dict[str, Any]] = None
    id: Optional[int] = 0

# Error codes enum
class MCPErrorCode(Enum):
    METHOD_NOT_FOUND = -32601
    INTERNAL_ERROR = -32603
    INVALID_REQUEST = -32600