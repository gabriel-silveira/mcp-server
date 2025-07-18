from langgraph.checkpoint.memory import MemorySaver
from src.agent.workflow import get_workflow
from src.agent.tools import initialize_tools
from src.logs import agent_logger


def get_graph_with_tool(tool_name: str):
  """Obtém o grafo compilado"""

  try:
    agent_logger.info(f"Obtendo grafo para ferramenta: {tool_name}")

    agent_logger.info(f"Inicializando ferramentas...")
    langchain_tools = initialize_tools(tool_name)
    agent_logger.info(f"Ferramentas inicializadas: {langchain_tools}")

    agent_logger.info(f"Obtendo workflow...")
    workflow = get_workflow(langchain_tools)
    agent_logger.info(f"Workflow obtido: {workflow}")

    # Cria uma instância do nosso "salvador de memória"
    memory = MemorySaver()

    agent_logger.info(f"Compilando grafo...")
    # Compila o workflow em um grafo executável.
    # O checkpointer garante que o estado seja salvo a cada passo.
    graph = workflow.compile(checkpointer=memory)

    agent_logger.info(f"Grafo compilado com sucesso")

    return graph
  except Exception as e:
    agent_logger.error(f"Erro ao obter grafo para ferramenta {tool_name}: {str(e)}")
    raise e