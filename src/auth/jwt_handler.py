from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Importa as configurações do JWT
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_REQUIRED

# Configurando HTTPBearer com auto_error=False para não gerar erro automaticamente
security = HTTPBearer(auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """
    Cria um token JWT com os dados fornecidos
    """
    to_encode = data.copy()
    
    # Define o tempo de expiração
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Adiciona a expiração aos dados do token como timestamp (segundos desde a época)
    # PyJWT espera um timestamp numérico, não um objeto datetime
    to_encode.update({"exp": int(expire.timestamp())})
    
    # Gera o token JWT
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """
    Verifica se o token JWT é válido ou permite acesso quando AUTH_REQUIRED=False
    """
    # Bypass de autenticação quando não é obrigatória
    if not AUTH_REQUIRED:
        return {}
    
    # Quando a autenticação é obrigatória mas não há credenciais
    # Com auto_error=False, credentials será None quando não houver token
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token não fornecido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Validação do token
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
