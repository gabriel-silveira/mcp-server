from langchain_openai import ChatOpenAI
from langchain_core.tools import StructuredTool


def get_llm_with_tools(langchain_tools: list[StructuredTool], model: str = "gpt-4o"):
  # Create a language model instance and bind it with the tools
  llm = ChatOpenAI(model=model)
  llm_with_tools = llm.bind_tools(langchain_tools)
  return llm_with_tools