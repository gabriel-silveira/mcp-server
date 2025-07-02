from .base import manager, tools

def initialize_gmail_tools():
    """Initialize Gmail tools with proper authentication"""
    # TODO: Add Gmail authentication logic here
    raw_tools = manager.init_tools(
        toolkits=["Gmail"],
    )
    
    for tool in raw_tools:
        if isinstance(tool.name, str):
            name = tool.name.lower()
            tools[name] = tool
