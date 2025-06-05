from langgraph.prebuilt import create_react_agent
from src.llm import bound_model
from src.tools import tools
from src.memory import memory

graph = create_react_agent(
  model=bound_model,
  tools=tools,
  checkpointer=memory
)
