import uvicorn
from fastapi import FastAPI
from src.routes.auth_routes import auth_router
from src.routes.mcp_routes import mcp_router

# Cria a aplicação FastAPI
app = FastAPI(
    title="MCP Server",
    description="Servidor MCP de Ferramentas do Arcade",
    version="1.0.0",
)

app.include_router(auth_router)
app.include_router(mcp_router)