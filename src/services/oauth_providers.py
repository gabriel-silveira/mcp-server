import base64
import hashlib
import secrets

def generate_code_verifier(length=64):
    """
    Gera um code_verifier aleatório para o fluxo PKCE OAuth 2.0.
    
    Args:
        length (int): Comprimento do code_verifier. Padrão é 64 caracteres.
        
    Returns:
        str: O code_verifier gerado.
    """
    # Gera uma string aleatória usando a biblioteca secrets
    code_verifier = secrets.token_urlsafe(length)
    # Garante que o tamanho seja exatamente o especificado
    return code_verifier[:length]

def generate_code_challenge(code_verifier):
    """
    Gera um code_challenge a partir de um code_verifier usando o método S256.
    
    Args:
        code_verifier (str): O code_verifier a partir do qual gerar o code_challenge.
        
    Returns:
        str: O code_challenge gerado.
    """
    # Converte o code_verifier para bytes
    verifier_bytes = code_verifier.encode('ascii')
    # Calcula o hash SHA-256
    sha256_hash = hashlib.sha256(verifier_bytes).digest()
    # Codifica em base64url (base64 com caracteres URL-safe)
    code_challenge = base64.urlsafe_b64encode(sha256_hash).decode('ascii')
    # Remove o padding (=) conforme especificado pelo RFC 7636
    return code_challenge.rstrip('=')

# Configurações dos provedores OAuth
OAUTH_PROVIDERS = {
    "microsoft": {
        "auth_url": "https://login.microsoftonline.com/af6dc112-fd52-4fd9-9170-7560e2c71636/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/af6dc112-fd52-4fd9-9170-7560e2c71636/oauth2/v2.0/token",
        "client_id": "26549cea-bdd6-4d23-bec5-abdddb8d6072",
        "client_secret": "Ck48Q~JkIJnKLPcEhXVsRVnUBiQQGYhZbBBUgbLi", # Segredo do cliente para troca de código por token
        "redirect_uri": "http://localhost:2906/auth/callback",
        "scopes": ["offline_access", "Mail.Send"],
        # Este código deve ser gerado dinamicamente para cada solicitação
        "code_challenge": "",
        "code_challenge_method": "S256"
    },
    # Adicione outros provedores conforme necessário
    # "google": { ... },
    # "github": { ... },
}
