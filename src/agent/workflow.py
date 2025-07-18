
from langchain_core.tools import StructuredTool
from langgraph.prebuilt import ToolNode
from langgraph.graph import END, START, MessagesState, StateGraph

from src.agent.nodes import authorize_node, should_continue_node
from src.agent.nodes import get_agent_node
from src.logs import agent_logger


def get_workflow(langchain_tools: list[StructuredTool]):
  """Obtém o workflow (nós e arestas)"""

  agent_logger.info(f"Obtendo nó de ferramentas...")
  tool_node = ToolNode(langchain_tools)
  agent_logger.info(f"Nó de ferramentas obtido: {tool_node}")

  agent_logger.info(f"Obtendo nó do agente...")
  agent_node = get_agent_node(langchain_tools)
  agent_logger.info(f"Nó do agente obtido: {agent_node}")

  # Cria um novo grafo de fluxo de trabalho.
  # Ele sabe que vai gerenciar um estado do tipo MessagesState.
  workflow = StateGraph(MessagesState)

  # Adiciona o nó "agent": quando ativado, ele chama a função call_agent.
  workflow.add_node("agent", agent_node)
  # Adiciona o nó "tools": responsável por executar ferramentas.
  workflow.add_node("tools", tool_node)
  # Adiciona o nó "authorization": para lidar com a autorização.
  workflow.add_node("authorization", authorize_node)

  # Define a primeira aresta: do ponto inicial, vá para o nó "agent".
  workflow.add_edge(START, "agent")

  # Após o nó "agent", chame a função should_continue para decidir o próximo passo.
  workflow.add_conditional_edges(
    "agent",
    should_continue_node, # A função que toma a decisão
    ["authorization", "tools", END], # Os destinos possíveis
  )

  # Se o fluxo for para "authorization", o próximo passo deve ser "tools".
  workflow.add_edge("authorization", "tools")

  # Após executar as ferramentas, volte para o agente.
  workflow.add_edge("tools", "agent")

  return workflow