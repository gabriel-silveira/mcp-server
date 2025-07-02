from .base import manager, tools

def initialize_web_tools():
    """Initialize web-based tools like ScrapeUrl"""
    raw_tools = manager.init_tools(
        tools=["Web.ScrapeUrl"],
    )
    
    for tool in raw_tools:
        if isinstance(tool.name, str):
            name = tool.name.lower().replace('web_', '')
            tools[name] = tool
