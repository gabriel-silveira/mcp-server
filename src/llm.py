from langchain_openai import ChatOpenAI
from src.config import OPENAI_API_KEY
from src.tools import tools

model = ChatOpenAI(model="gpt-4o", api_key=OPENAI_API_KEY)

bound_model = model.bind_tools(tools)
