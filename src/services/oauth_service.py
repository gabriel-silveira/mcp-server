"""
Serviço para gerenciar autenticação OAuth com diferentes provedores.
Fornece funções para gerar URLs de autenticação e gerenciar tokens.
"""
from uuid import uuid4
from typing import Dict, Optional, Any
from urllib.parse import quote

# Configurações dos provedores OAuth
OAUTH_PROVIDERS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "client_id": "616965216235-j00hdhfapqu1kgkkdm3btghldkjmcior.apps.googleusercontent.com",
        "redirect_uri": "http://localhost:2906/oauth/callback",
        "scopes": ["https://www.googleapis.com/auth/userinfo.email", "https://www.googleapis.com/auth/userinfo.profile"],
    },
    "microsoft": {
        "auth_url": "https://login.microsoftonline.com/common/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/common/oauth2/v2.0/token",
        "client_id": "e079991b-92b0-4f3f-8238-d2d6b7155a59",
        "redirect_uri": "http://localhost:2906/oauth/callback",
        "scopes": ["offline_access", "Mail.Send"],
        # Este valor deve ser gerado dinamicamente para cada solicitação
        "code_challenge": "Ts60Nq-COBuxYIDFBCzff6q2H42i2jSj6Dznm9yFiPA",
        "code_challenge_method": "S256"
    },
    # Adicione outros provedores conforme necessário
    # "google": { ... },
    # "github": { ... },
}

def get_auth_url(
    provider: str,
    additional_scopes: Optional[list] = None, 
    additional_params: Optional[Dict[str, Any]] = None
) -> Dict[str, str]:
    """
    Gera uma URL de autenticação OAuth para o provedor especificado.
    
    Args:
        provider: Nome do provedor OAuth (ex: "microsoft", "google")
        additional_scopes: Escopos adicionais a serem solicitados
        additional_params: Parâmetros adicionais para a URL de autenticação
        
    Returns:
        Dict contendo:
            - url: URL de autenticação completa
            - state: Valor state gerado para esta solicitação
            - provider: Nome do provedor
    """
    if provider not in OAUTH_PROVIDERS:
        raise ValueError(f"Provedor OAuth não suportado: {provider}")
    
    provider_config = OAUTH_PROVIDERS[provider]
    
    # Gerar um state único para o fluxo OAuth
    state = str(uuid4())
    
    # Combinar escopos padrão com escopos adicionais
    scopes = provider_config["scopes"]
    if additional_scopes:
        scopes.extend(additional_scopes)
    
    # Codificar escopos para URL (separados por espaço)
    encoded_scopes = quote(" ".join(scopes))
    
    # Construir URL base com parâmetros obrigatórios
    auth_url = (
        f"{provider_config['auth_url']}"
        f"?client_id={provider_config['client_id']}"
        f"&response_type=code"
        f"&redirect_uri={quote(provider_config['redirect_uri'])}"
        f"&response_mode=query"
        f"&scope={encoded_scopes}"
        f"&state={state}"
    )
    
    # Adicionar parâmetros específicos do provedor
    if provider == "microsoft":
        auth_url += (
            f"&code_challenge={provider_config['code_challenge']}"
            f"&code_challenge_method={provider_config['code_challenge_method']}"
        )
    
    # Adicionar parâmetros adicionais, se fornecidos
    if additional_params:
        for key, value in additional_params.items():
            auth_url += f"&{key}={quote(str(value))}"
    
    return {
        "url": auth_url,
        "state": state,
        "provider": provider
    }

def get_google_auth_url(additional_scopes: Optional[list] = None) -> Dict[str, str]:
    """
    Gera uma URL de autenticação OAuth específica para Google.
    
    Args:
        additional_scopes: Escopos adicionais a serem solicitados além dos padrão
        
    Returns:
        Dict contendo URL de autenticação e state
    """
    return get_auth_url("google", additional_scopes)

def get_microsoft_auth_url(additional_scopes: Optional[list] = None) -> Dict[str, str]:
    """
    Gera uma URL de autenticação OAuth específica para Microsoft.
    
    Args:
        additional_scopes: Escopos adicionais a serem solicitados além dos padrão
        
    Returns:
        Dict contendo URL de autenticação e state
    """
    return get_auth_url("microsoft", additional_scopes)

# Funções auxiliares para outros provedores podem ser adicionadas aqui
# def get_google_auth_url(...): ...
# def get_github_auth_url(...): ...

# Funções para troca de código de autorização por tokens
def exchange_code_for_token(provider: str, code: str) -> Dict[str, Any]:
    """
    Troca um código de autorização por tokens de acesso e atualização.
    
    Args:
        provider: Nome do provedor OAuth
        code: Código de autorização recebido
        
    Returns:
        Dict contendo tokens e informações relacionadas
    """
    # Implementação a ser adicionada
    pass
