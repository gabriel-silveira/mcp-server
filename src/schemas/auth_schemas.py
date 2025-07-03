from pydantic import BaseModel
from typing import Optional, List

class Token(BaseModel):
    """
    Modelo para o token de acesso
    """
    access_token: str
    token_type: str

class TokenData(BaseModel):
    """
    Modelo para os dados do token
    """
    username: Optional[str] = None
    roles: Optional[List[str]] = None

class UserCredentials(BaseModel):
    """
    Modelo para credenciais de usuário na troca de tokens
    """
    subject_token: str
    client_id: Optional[str] = None
    grant_type: Optional[str] = None
    resource: Optional[str] = None
    subject_token_type: Optional[str] = None
