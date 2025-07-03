from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import os
import jwt

from ..auth.jwt_handler import create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..schemas.auth_schemas import Token, UserCredentials
from ..logs import auth_logger

# Criação do router de autenticação
auth_router = APIRouter(tags=["Authentication"])

# OAuth2 para autenticação com senha
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@auth_router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), request: Request = None):
    auth_logger.info(f"Tentativa de login para usuário: {form_data.username} | IP: {request.client.host if request else 'desconhecido'}")
    """
    Endpoint para obter um token JWT usando credenciais OAuth2
    """
    # Aqui você implementaria a validação de usuário e senha
    # Por enquanto, vamos apenas verificar se o usuário é "admin" e a senha é "password"
    if form_data.username != "admin" or form_data.password != "password":
        auth_logger.warning(f"Falha na autenticação para usuário: {form_data.username} | IP: {request.client.host if request else 'desconhecido'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Dados a serem incluídos no token
    token_data = {
        "sub": form_data.username,
        "roles": ["admin"]  # Exemplo de roles
    }
    
    # Criação do token com expiração
    access_token = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    
    auth_logger.info(f"Login bem-sucedido para usuário: {form_data.username} | IP: {request.client.host if request else 'desconhecido'}")
    return {"access_token": access_token, "token_type": "bearer"}

@auth_router.post("/token_exchange", response_model=Token)
async def token_exchange(credentials: UserCredentials, request: Request = None):
    auth_logger.info(f"Solicitação de troca de token recebida | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
    """
    Endpoint para trocar um token externo (ex: Supabase) por um token JWT do MCP
    """
    try:
        # Aqui você implementaria a validação do token externo
        # Por enquanto, vamos apenas verificar se o token não está vazio
        if not credentials.subject_token:
            auth_logger.error(f"Token vazio na solicitação de troca | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        auth_logger.debug(f"Token recebido para troca: {credentials.subject_token[:10]}... | Resource: {credentials.resource}")
        
        # Em um cenário real, você verificaria o token com o provedor externo
        # e extrairia informações como o ID do usuário, email, etc.
        
        # Dados a serem incluídos no token
        token_data = {
            "sub": "user_from_external_token",
            "roles": ["user", "admin", "tools_access"],
            # Você pode adicionar mais dados aqui conforme necessário
        }
        
        # Criação do token com expiração
        access_token = create_access_token(
            data=token_data,
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        auth_logger.info(f"Token trocado com sucesso | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
        return {"access_token": access_token, "token_type": "bearer"}
    
    except jwt.PyJWTError as e:
        auth_logger.error(f"Erro JWT na validação do token externo: {str(e)} | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não foi possível validar o token externo",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        auth_logger.error(f"Erro inesperado na troca de token: {str(e)} | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Erro interno ao processar a troca de token",
        )
