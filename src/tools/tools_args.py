from src.utils import create_error_response, MCPErrorCode
import json
from typing import Dict, Any

async def _clean_microsoft_createandsendemail_args(arguments: Dict[str, Any], schema: Dict[str, Any], request_id: int, correlation_id: str) -> Dict[str, Any]:
    """Clean and validate email tool arguments."""
    clean_args = {}
    
    for k, v in arguments.items():
        if v is None:
            continue
            
        if k == 'to_recipients' and isinstance(v, str):
            if v.startswith('[') and v.endswith(']'):
                try:
                    parsed_value = json.loads(v)
                    if parsed_value is not None:
                        clean_args[k] = parsed_value
                except json.JSONDecodeError:
                    return create_error_response(request_id, MCPErrorCode.INVALID_PARAMS, f"Invalid array format for to_recipients")
            else:
                clean_args[k] = [v]
        else:
            clean_args[k] = v
    
    return clean_args

def _clean_scrape_args(arguments: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate scrape tool arguments."""
    clean_args = {k: v for k, v in arguments.items() if v is not None}
    
    # Set scrape-specific defaults
    for prop, details in schema.get('properties', {}).items():
        if prop not in clean_args:
            if prop == 'formats':
                clean_args[prop] = ['markdown']
            elif prop == 'timeout':
                clean_args[prop] = 30000
            elif details.get('type') == 'array':
                clean_args[prop] = []
            elif details.get('type') == 'boolean':
                clean_args[prop] = False
            elif details.get('type') == 'integer':
                clean_args[prop] = 0
    
    return clean_args

def _clean_default_args(arguments: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """Clean and validate default tool arguments."""
    clean_args = {k: v for k, v in arguments.items() if v is not None}
    
    # Set generic defaults
    for prop, details in schema.get('properties', {}).items():
        if prop not in clean_args:
            if details.get('type') == 'array':
                clean_args[prop] = []
            elif details.get('type') == 'boolean':
                clean_args[prop] = False
            elif details.get('type') == 'integer':
                clean_args[prop] = 0
    
    return clean_args


async def _clean_arguments(tool, arguments: Dict[str, Any], tool_name: str, request_id: int, correlation_id: str):
    # Clean and validate arguments based on tool type
    if hasattr(tool, 'args_schema'):
        schema = tool.args_schema.model_json_schema()
        
        # Nota: Aqui ainda estamos usando os nomes antigos para compatibilidade com as funções de limpeza
        # Se necessário, você pode atualizar essas condições para usar os nomes originais
        if tool_name == 'microsoft_createandsendemail':
            arguments = await _clean_microsoft_createandsendemail_args(arguments, schema, request_id, correlation_id)
            if isinstance(arguments, JSONResponse):  # If error response
                return arguments
        elif tool_name == 'Web_ScrapeUrl':
            arguments = _clean_scrape_args(arguments, schema)
        else:
            arguments = _clean_default_args(arguments, schema)

        return arguments