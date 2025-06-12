import time
from typing import Optional, Dict, Any
from langgraph.errors import NodeInterrupt
from src.agent import graph

config = {
  "configurable": {
    "thread_id": "1",
    "user_id": "gabriel@gabrielsilveira.com.br"
  }
}

user_input = {
  "messages": [
    #("user", "Faça um pequeno resumo dos 5 últimos e-mails não lidos na minha caixa de entrada.")
    ("user", "Faça um resumo da página inicial de arcade.dev")
  ]
}


def wait_for_auth(last_state: Optional[Dict[str, Any]] = None) -> bool:
    """Tenta executar o fluxo e retorna True se autenticado com sucesso."""
    try:
        # Se temos um estado anterior, tentamos continuar de onde paramos
        stream_kwargs = {"stream_mode": "values"}
        if last_state:
            stream_kwargs["state"] = last_state

        for chunk in graph.stream(user_input, config, **stream_kwargs):
            if "__interrupt__" in chunk:
                return False
            elif "messages" in chunk:
                last_message = chunk["messages"][-1]
                if hasattr(last_message, "content") and last_message.content:
                    print(f"\n💬 Assistant: {last_message.content}")
                if hasattr(last_message, "additional_kwargs") and "tool_calls" in last_message.additional_kwargs:
                    for tool_call in last_message.additional_kwargs["tool_calls"]:
                        print(f"\n🔧 Using tool: {tool_call['function']['name']}")
                        print(f"   with args: {tool_call['function']['arguments']}")
            else:
                print(chunk)
        return True
    except NodeInterrupt as exc:
        return False

def run_with_auth():
    last_state = None
    auth_link_shown = False

    while True:
        # Tenta executar o fluxo
        success = wait_for_auth(last_state)
        if success:
            break

        # Se chegou aqui, precisa de autenticação
        if not auth_link_shown:
            print("\n🔐 Aguardando autenticação...")
            print("Por favor, clique no link abaixo para autorizar:")
            try:
                # Tenta uma vez para pegar o link de autenticação
                next(graph.stream(user_input, config, stream_mode="values"))
            except NodeInterrupt as exc:
                print(f"\n{exc}")
            auth_link_shown = True

        # Aguarda um pouco antes de tentar novamente
        print("\r⏳ Aguardando autenticação...", end="")
        time.sleep(2)

if __name__ == "__main__":
    run_with_auth()
