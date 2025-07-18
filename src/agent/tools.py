from langchain_arcade import ToolManager
from src.config import ARCADE_API_KEY

# Initialize tool manager
tools_manager = ToolManager(
  api_key=ARCADE_API_KEY,
)

def initialize_tools(tool_name: str):
  """Initialize tools"""
  return tools_manager.init_tools(
    tools=[tool_name],
  )