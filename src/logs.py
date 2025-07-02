import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# MCP Server: logger to be used while processing MCP requests
mcp_logger = logging.getLogger('mcp_server')

# Tools logger: to be used while processing tool calls
tools_logger = logging.getLogger('tools')