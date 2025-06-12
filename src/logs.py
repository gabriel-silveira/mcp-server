import logging

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
mcp_logger = logging.getLogger('mcp_server')
tools_logger = logging.getLogger('tools')