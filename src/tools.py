from langchain_arcade import ArcadeToolManager
from config import ARCADE_API_KEY

manager = ArcadeToolManager(api_key=ARCADE_API_KEY)

# Get tools from the ArcadeToolManager
# ScrapeUrl tool from the Web toolkit
# Google toolkit
tools = manager.init_tools(
  tools=["Web.ScrapeUrl"],
  toolkits=["Google"])