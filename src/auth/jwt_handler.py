from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Importa as configurações do JWT
from src.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, AUTH_REQUIRED

security = HTTPBearer()

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

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """
    Verifica se o token JWT é válido
    """
    try:
        # Extrai o token do cabeçalho de autorização
        token = credentials.credentials
        
        # Decodifica e verifica o token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # O PyJWT já verifica a expiração automaticamente durante o decode
        # Não precisamos verificar manualmente, mas podemos adicionar logs
        exp_time = datetime.fromtimestamp(payload.get("exp"))
        now = datetime.utcnow()
        
        from ..logs import auth_logger
        auth_logger.debug(f"Token válido. Expira em {exp_time.isoformat()}, agora é {now.isoformat()}, tempo restante: {(exp_time - now).total_seconds()} segundos")
        
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
