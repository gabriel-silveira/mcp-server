import uvicorn
from fastapi import FastAPI
# from src.routes.auth_routes import auth_router
from src.routes.mcp_routes import mcp_router

# Cria a aplicação FastAPI
app = FastAPI()

# app.include_router(auth_router)
app.include_router(mcp_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=2906)