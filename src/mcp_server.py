from fastapi import FastAPI
import logging
from src.routes import google_auth, google_callback, mcp_endpoint

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp_server')

# Cria a aplicação FastAPI
app = FastAPI()

# Registra as rotas
app.get("/auth/google")(google_auth)
app.get("/auth/google/callback")(google_callback)
app.post("/mcp")(mcp_endpoint)
app.get("/mcp")(mcp_endpoint)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=2906)
