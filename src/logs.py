import logging

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s\n'
)
mcp_logger = logging.getLogger('mcp_server')
auth_logger = logging.getLogger('auth')
tools_logger = logging.getLogger('tools')
agent_logger = logging.getLogger('agent')