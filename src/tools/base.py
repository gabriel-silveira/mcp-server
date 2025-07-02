from typing import Dict, Any
from pydantic import BaseModel
from langchain_arcade import ToolManager
from src.config import ARCADE_API_KEY

class ToolCallParams(BaseModel):
    name: str
    arguments: Dict[str, Any]

# Base tool manager
manager = ToolManager(
    api_key=ARCADE_API_KEY,
)

# Base tools dictionary
tools: Dict[str, Any] = {}
