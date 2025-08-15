"""Configuration module to load environment variables."""
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

# Import os after loading .env to ensure variables are available
import os

# API Keys
ARCADE_API_KEY = os.getenv('ARCADE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MARIADB_URI = os.getenv('MARIADB_URI')

# JWT Authentication
SECRET_KEY = os.getenv('JWT_SECRET_KEY', "chave_secreta_muito_segura")  # Use uma chave gerada com openssl rand -hex 32
ALGORITHM = os.getenv('JWT_ALGORITHM', "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', "30"))
AUTH_REQUIRED = os.getenv('MCP_AUTH_REQUIRED', "true").lower() == "true"

server_name = "OAPV Tools MCP Server"
server_version = "1.0.0"