from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
import jwt
import json

from ..auth.jwt_handler import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
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

@auth_router.post("/oauth/token", response_model=Token)
async def token_exchange(request: Request = None):
    """
    Endpoint para trocar um token externo (ex: Supabase) por um token JWT do MCP
    """
    # Log do IP da requisição
    auth_logger.info(f"Solicitação de troca de token recebida | IP: {request.client.host if request else 'desconhecido'}")
    
    # Log dos headers da requisição
    headers_log = {k: v for k, v in request.headers.items() if k.lower() not in ['authorization']}
    auth_logger.debug(f"Headers da requisição: {headers_log}")
    
    # Verificar o Content-Type e processar o corpo da requisição adequadamente
    content_type = request.headers.get('content-type', '')
    auth_logger.debug(f"Content-Type: {content_type}")
    
    try:
        # Processar o corpo da requisição com base no Content-Type
        if 'application/x-www-form-urlencoded' in content_type:
            form_data = await request.form()
            auth_logger.debug(f"Form data recebido: {dict(form_data)}")
            
            # Converter form_data para um dicionário
            credentials_dict = dict(form_data)
        else:  # Assume JSON como padrão
            body = await request.json()
            auth_logger.debug(f"JSON recebido: {body}")
            credentials_dict = body
            
        # Criar objeto UserCredentials a partir dos dados recebidos
        credentials = UserCredentials(**credentials_dict)
        auth_logger.debug(f"Credenciais processadas: {credentials.dict()}")
        
        # Log do client_id
        auth_logger.info(f"Client ID: {credentials.client_id}")
    except Exception as e:
        auth_logger.error(f"Erro ao processar o corpo da requisição: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Erro ao processar o corpo da requisição: {str(e)}"
        )
    try:
        # Verificar todos os campos obrigatórios
        missing_fields = []
        if not credentials.subject_token:
            missing_fields.append("subject_token")
        
        # Se houver campos faltando, logar e retornar erro
        if missing_fields:
            auth_logger.error(f"Campos obrigatórios faltando: {missing_fields} | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Campos obrigatórios faltando: {missing_fields}",
            )
            
        # Verificar formato do token
        if not credentials.subject_token:
            auth_logger.error(f"Token vazio na solicitação de troca | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Log do token recebido (apenas primeiros caracteres por segurança)
        auth_logger.debug(f"Token recebido para troca: {credentials.subject_token[:10]}... | Resource: {credentials.resource}")
        
        # Log de valores esperados vs recebidos
        auth_logger.debug(f"Grant type esperado: 'urn:ietf:params:oauth:grant-type:token-exchange', recebido: '{credentials.grant_type}'")
        auth_logger.debug(f"Subject token type esperado: 'urn:ietf:params:oauth:token-type:access_token', recebido: '{credentials.subject_token_type}'")
        auth_logger.debug(f"Client ID esperado: 'next_app', recebido: '{credentials.client_id}'")
        auth_logger.debug(f"Resource recebido: '{credentials.resource}'")
        
        # Verificar valores específicos esperados
        if credentials.grant_type != "urn:ietf:params:oauth:grant-type:token-exchange":
            auth_logger.warning(f"Grant type inválido: '{credentials.grant_type}'")
            # Não retornamos erro para permitir compatibilidade
        
        # Em um cenário real, você verificaria o token com o provedor externo
        # e extrairia informações como o ID do usuário, email, etc.
        auth_logger.debug("Iniciando processamento do token Supabase...")
        
        # Dados a serem incluídos no token
        auth_logger.debug("Preparando dados para inclusão no token JWT...")
        
        token_data = {
            "sub": "user_from_external_token",
            "roles": ["user", "admin", "tools_access"],
            # Você pode adicionar mais dados aqui conforme necessário
        }
        
        # Criação do token com expiração
        auth_logger.debug(f"Criando token JWT com dados: {token_data} e expiração de {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
        try:
            # Garantir que ACCESS_TOKEN_EXPIRE_MINUTES seja um número válido
            expire_minutes = 30  # Valor padrão de 30 minutos
            if ACCESS_TOKEN_EXPIRE_MINUTES is not None:
                try:
                    expire_minutes = int(ACCESS_TOKEN_EXPIRE_MINUTES)
                except (TypeError, ValueError):
                    auth_logger.warning(f"ACCESS_TOKEN_EXPIRE_MINUTES inválido: {ACCESS_TOKEN_EXPIRE_MINUTES}, usando valor padrão de 30 minutos")
            
            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=expire_minutes)
            )
            auth_logger.debug(f"Token JWT criado com sucesso, primeiros caracteres: {access_token[:15]}...")
        except Exception as e:
            auth_logger.error(f"Erro ao criar token JWT: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao gerar token de acesso",
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
    except ValueError as e:
        auth_logger.error(f"Erro de validação de dados: {str(e)} | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id if hasattr(credentials, 'client_id') else 'desconhecido'}")
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Erro de validação de dados: {str(e)}",
        )
    except json.JSONDecodeError as e:
        auth_logger.error(f"Erro ao decodificar JSON: {str(e)} | IP: {request.client.host if request else 'desconhecido'}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"JSON inválido: {str(e)}",
        )
    except Exception as e:
        auth_logger.error(f"Erro inesperado na troca de token: {str(e)} | IP: {request.client.host if request else 'desconhecido'} | Client ID: {credentials.client_id if hasattr(credentials, 'client_id') else 'desconhecido'}")
        auth_logger.exception("Detalhes do erro:")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro inesperado: {str(e)}",
        )

@auth_router.get("/oauth/callback")
async def oauth_callback(request: Request = None):
    """
    Endpoint para receber a callback do OAuth
    """
    return f"Callback received {request.query_params}"
    