# This file is now just a proxy to maintain backward compatibility
# All functionality has been moved to the tools/ package
from src.tools import handle_tool_call, tools, ToolCallParams

__all__ = ['handle_tool_call', 'tools', 'ToolCallParams']