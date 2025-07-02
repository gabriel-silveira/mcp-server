from .base import tools, ToolCallParams
from .web_tools import initialize_web_tools
from .gmail_tools import initialize_gmail_tools
from .handlers import handle_tool_call

# Initialize all tools
initialize_web_tools()
initialize_gmail_tools()

__all__ = ['tools', 'ToolCallParams', 'handle_tool_call']
