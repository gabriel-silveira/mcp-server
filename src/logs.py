import logging

# Configuração do logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
mcp_logger = logging.getLogger('mcp_server')
auth_logger = logging.getLogger('auth')
tools_logger = logging.getLogger('tools')