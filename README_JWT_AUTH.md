# Documentação da Autenticação JWT entre Next.js e MCP Server

Este documento descreve a implementação da autenticação baseada em JWT (JSON Web Token) para proteger a comunicação entre a aplicação Next.js e o servidor MCP (implementado em FastAPI).

## Visão Geral

A autenticação JWT implementada fornece:
- Troca segura de tokens entre a aplicação Next.js e o servidor MCP
- Validação de tokens em rotas protegidas
- Gerenciamento automático de ciclo de vida dos tokens
- Configuração flexível através de variáveis de ambiente

## Componentes Principais

### Servidor MCP (FastAPI)

1. **Módulo de Autenticação JWT** (`src/auth/jwt_handler.py`)
   - Criação e verificação de tokens JWT
   - Dependência para proteção de rotas

2. **Rotas de Autenticação** (`src/routes/auth_routes.py`)
   - Endpoint `/token`: Autenticação direta com credenciais
   - Endpoint `/token_exchange`: Troca de token externo (Supabase) por token JWT do MCP

3. **Configuração** (`src/config.py`)
   - Variáveis de ambiente para configuração JWT
   - Controle de ativação da autenticação

### Aplicação Next.js

1. **Proxy de Requisições** (`src/app/api/oap_mcp/proxy-request.ts`)
   - Gerenciamento de tokens JWT
   - Troca automática de token Supabase por token JWT do MCP
   - Armazenamento seguro do token em cookie

## Fluxo de Autenticação

1. O cliente faz uma requisição para a API Next.js (`/api/oap_mcp`)
2. O proxy verifica se há um token JWT válido no cookie
3. Se não houver token válido:
   - Obtém o token Supabase da sessão do usuário
   - Troca o token Supabase por um token JWT do MCP via `/token_exchange`
   - Armazena o token JWT em cookie seguro
4. O proxy adiciona o token JWT no cabeçalho `Authorization` da requisição para o MCP
5. O servidor MCP valida o token JWT antes de processar a requisição
6. A resposta é retornada ao cliente

## Configuração

### Variáveis de Ambiente do Servidor MCP

```
JWT_SECRET_KEY=chave_secreta_muito_segura  # Use openssl rand -hex 32 para gerar
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MCP_AUTH_REQUIRED=true
```

### Variáveis de Ambiente do Next.js

```
NEXT_PUBLIC_MCP_AUTH_REQUIRED=true
MCP_SERVER_URL=http://localhost:8000
```

## Segurança

- Tokens JWT são assinados com algoritmo HS256
- Tokens têm tempo de expiração configurável (padrão: 30 minutos)
- Cookies são configurados com flags de segurança (httpOnly, secure, sameSite)
- Autenticação pode ser ativada/desativada via variável de ambiente

## Considerações para Produção

1. **Gerar uma chave secreta forte**:
   ```
   openssl rand -hex 32
   ```

2. **Configurar tempos de expiração adequados**:
   - Tokens JWT: 15-30 minutos
   - Cookies: Mesmo tempo que os tokens JWT

3. **Habilitar HTTPS** em ambos os serviços

4. **Implementar renovação automática de tokens** para melhor experiência do usuário
