from langgraph.graph import END, MessagesState
from langchain_core.tools import StructuredTool
from src.agent.llm import get_llm_with_tools
from src.agent.tools import tools_manager


def get_agent_node(langchain_tools: list[StructuredTool]):
    # Função para invocar o modelo de linguagem e obter uma resposta
    def agent_node(state: MessagesState):
        messages = state["messages"]

        llm_with_tools = get_llm_with_tools(langchain_tools)

        response = llm_with_tools.invoke(messages)

        # Retorna o histórico atualizado de mensagens
        return {"messages": [response]}

    return agent_node


# Essa função irá inspecionar a resposta do agente e retornar uma string: "authorization", "tools", ou "END".
def should_continue_node(state: MessagesState):
    # Pega a última mensagem e verifica se o agente decidiu usar uma ferramenta
    if state["messages"][-1].tool_calls:
        for tool_call in state["messages"][-1].tool_calls:
            # verifica se a ferramenta precisa de autorização
            if tools_manager.requires_auth(tool_call["name"]):
                return "authorization"
        return "tools"  # Prossiga para a execução da ferramenta se nenhuma autorização for necessária
    return END  # Termine o fluxo de trabalho se nenhuma ferramenta estiver presente



# Função para lidar com a autorização para ferramentas que exigem isso
def authorize_node(state: MessagesState, config: dict):
    # Pega o ID do usuário
    user_id = config["configurable"].get("user_id")

    for tool_call in state["messages"][-1].tool_calls:
        # Pega o nome da ferramenta
        tool_name = tool_call["name"]

        # Verifica se a ferramenta precisa de autorização
        if not tools_manager.requires_auth(tool_name):
            continue

        auth_response = tools_manager.authorize(tool_name, user_id)

        if auth_response.status != "completed":
            # Solicite ao usuário que visite a URL para autorização
            print(f"Visit the following URL to authorize: {auth_response.url}")

            # Aguarde o usuário concluir a autorização
            # e depois verifique o status da autorização novamente
            tools_manager.wait_for_auth(auth_response.id)

            if not tools_manager.is_authorized(auth_response.id):
                # Interrompe a execução se a autorização falhar
                raise ValueError("Authorization failed")

    return {"messages": []}