from langchain_arcade import ArcadeToolManager
from src.config import ARCADE_API_KEY

manager = ArcadeToolManager(api_key=ARCADE_API_KEY)

# Get tools from the ArcadeToolManager
# ScrapeUrl tool from the Web toolkit
# Google toolkit
tools = manager.get_tools(
  tools=["Web.ScrapeUrl"],
  toolkits=["Google"],
)