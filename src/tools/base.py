from fastapi.responses import JSONResponse
from langchain_arcade import ToolManager
from typing import Dict, Any
from pydantic import BaseModel
from uuid import uuid4
import json, time

from src.utils import create_error_response, create_success_response, MCPErrorCode
from src.logs import tools_logger
from src.config import ARCADE_API_KEY
from src.tools.tools_args import _clean_arguments
from src.agent.graph import get_graph_with_tool
from src.tools.youtube_tools import Youtube_BlogPost
# from src.tools.verx_rh_tools import VerxRH_GetDBCatalog, VerxRH_RunQuery


# Request/Response models
class ToolCallParams(BaseModel):
    name: str
    arguments: Dict[str, Any]


# Initialize tool manager
tools_manager = ToolManager(
    api_key=ARCADE_API_KEY,
)


# Initialize tools
raw_tools = tools_manager.init_tools(
    toolkits=[
        "Web",
        "Search",
        "Google",
        "Microsoft",
        "Github",
        "Slack",
        "Linkedin",
        "X",
        "Confluence",
        "Jira",
        "Trello",
        "Notion",
        "Dropbox",
        "Reddit",
    ],
)

raw_tools.append(Youtube_BlogPost)


# raw_tools.append(VerxRH_GetDBCatalog)
# raw_tools.append(VerxRH_RunQuery)

# As ferramentas personalizadas estão em raw_tools, mas precisamos garantir
# que sejam executadas corretamente mesmo sem estarem no tools_manager


# Função auxiliar para encontrar uma ferramenta pelo nome
def find_tool_by_name(name: str):
    """Find a tool by its name in raw_tools."""
    for tool in raw_tools:
        if tool.name == name:
            return tool
    return None


def _create_auth_response(request_id: int, tool_name: str, url: str) -> JSONResponse:
    """Create authentication response for tools requiring authentication."""

    tools_logger.info(f"Creating authentication response for tool: {tool_name}")

    return JSONResponse(
        content={
            "error": {
                "code": -32003,
                "data": {
                    "id": f"ar_{uuid4().hex[:24]}",
                    "type": "url",
                    "url": url,
                    "message": {
                        "text": "Autorização necessária. Por favor, clique no link para autorizar."
                    }
                },
                "message": "interaction_required"
            },
            "id": request_id,
            "jsonrpc": "2.0"
        },
        status_code=200
    )


def _format_result(result: Any) -> str:
    """Format tool execution result to markdown content."""
    if isinstance(result, dict) and "markdown" in result:
        return result["markdown"]
    elif isinstance(result, str):
        return result
    else:
        return str(result) if result is not None else ""


async def handle_tool_call(request_id: int, tool_name: str, arguments: Dict[str, Any]) -> JSONResponse:
    """Handle tool execution requests"""
    thread_id = str(uuid4())
    start_time = time.time()

    # TODO: the user_id should be related to the logged user...
    user_id = "gabrielsilveira.web@gmail.com"
    
    tools_logger.info(f"[{thread_id}] Tool '{tool_name}' called with arguments: {json.dumps(arguments, indent=2)}")

    tool = find_tool_by_name(tool_name)
    if not tool:
        return create_error_response(request_id, MCPErrorCode.METHOD_NOT_FOUND, f"Tool {tool_name} not found")

    tools_logger.info(f"Tool found: {tool}")

    cleaned_arguments = await _clean_arguments(tool, arguments, tool_name, request_id, thread_id)

    tools_logger.info(f"[{thread_id}] Cleaned arguments for tool '{tool_name}': {json.dumps(cleaned_arguments, indent=2)}")

    try:
        # Verifica se é uma ferramenta personalizada (adicionada manualmente a raw_tools)
        is_custom_tool = tool_name in ["Youtube_BlogPost", "VerxRH_GetDBCatalog", "VerxRH_RunQuery"]
        
        # Verifica se a ferramenta requer autorização
        if not is_custom_tool and tools_manager.requires_auth(tool_name):
            tools_logger.info(f"Auth is required for tool: {tool_name}")

            auth_response = tools_manager.authorize(tool_name, user_id)

            tools_logger.info(f"Auth response ID: {auth_response.id}")
            tools_logger.info(f"Auth response Status: {auth_response.status}")
            tools_logger.info(f"Complete auth response: {auth_response}")
        
            if auth_response.status != "completed":
                return _create_auth_response(request_id, tool_name, auth_response.url)

            # executa a ferramenta (autorizada)
            graph_with_tool = get_graph_with_tool(tool_name)

            # Define as mensagens com o input do usuário
            inputs = {
                "messages": [
                    {
                        "role": "user",
                        "content": f"Execute a ferramenta {tool_name} com os seguintes argumentos: {str(cleaned_arguments)}",
                    }
                ],
            }

            tools_logger.info(f"Message: {inputs}")
            
            # Configuração com IDs de encadeamento e usuário para fins de autorização
            config = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
            
            # Executa o grafo e transmite as saídas.
            for chunk in graph_with_tool.stream(inputs, config=config, stream_mode="values"):
                tools_logger.info(f"Chunk: {chunk}")

            return create_success_response(request_id, {
                "content": [{"type": "text", "text": chunk["messages"][-1].content}]
            })
        else:
            # Executa a ferramenta (sem autorização)
            # Para ferramentas personalizadas, execute usando o método invoke conforme documentação
            if is_custom_tool:
                tools_logger.info(f"Executando ferramenta personalizada: {tool_name}")
                
                # Tratamento específico para cada ferramenta personalizada
                if tool_name == "VerxRH_RunQuery":
                    # VerxRH_RunQuery espera um argumento 'sql'
                    sql = cleaned_arguments.get("sql", "")
                    result = tool.invoke({"sql": sql})
                elif tool_name == "VerxRH_GetDBCatalog":
                    # VerxRH_GetDBCatalog não espera argumentos
                    result = tool.invoke({})
                else:
                    # Para outras ferramentas personalizadas
                    result = tool.invoke(cleaned_arguments)
            else:
                # Para ferramentas do Arcade, use o método arun
                result = await tool.arun(cleaned_arguments)

            tools_logger.info(f"Tool result: {result}")
            
            tools_logger.info(
                f"[{thread_id}] Tool '{tool_name}' completed in {time.time() - start_time:.2f}s with result: "
                f"{json.dumps(result, indent=2) if result else 'None'}"
            )
            
            # Formata o resultado e retorna a resposta de sucesso
            markdown_content = _format_result(result)

            return create_success_response(request_id, {
                "content": [{"type": "text", "text": markdown_content}]
            })
    except Exception as e:
        tools_logger.error(f"[{thread_id}] Error executing tool '{tool_name}': {str(e)}")

        return create_error_response(request_id, MCPErrorCode.INTERNAL_ERROR, str(e))