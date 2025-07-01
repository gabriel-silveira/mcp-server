# MCP Server - FastAPI Application

Este documento fornece instruções detalhadas para implantar a aplicação MCP Server em uma instância EC2 da AWS, utilizando Gunicorn como servidor WSGI e Nginx como proxy reverso.

## Pré-requisitos

- Conta AWS com permissões para criar instâncias EC2
- Chave SSH para acessar a instância EC2
- Domínio (opcional, mas recomendado para produção)

## 1. Configuração da Instância EC2

### 1.1. Iniciar uma nova instância EC2

1. Acesse o Console de Gerenciamento da AWS
2. Navegue até o serviço EC2
3. Clique em "Lançar instância"

### 1.2. Configurações da instância

- **Nome da instância**: `mcp-server`
- **Sistema operacional**: Ubuntu 24.04 LTS
- **Tipo de instância**: t3.micro (gratuito na camada gratuita) ou maior, dependendo da carga esperada
- **Par de chaves**: Selecione ou cione um par de chaves SSH existente
- **Configurações de rede**:
  - Habilitar proteção contra parada acidental
  - Configurar grupo de segurança para permitir tráfego nas portas:
    - SSH (22)
    - HTTP (80)
    - HTTPS (443)

## 2. Acesso Inicial à Instância

Conecte-se à sua instância via SSH:

```bash
ssh -i /caminho/para/sua-chave.pem ubuntu@seu-endereco-ip
```

## 3. Configuração do Ambiente

### 3.1. Atualizar o sistema

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2. Instalar dependências do sistema

```bash
sudo apt install -y python3-pip python3-venv nginx git
```

## 4. Implantação da Aplicação

### 4.1. Clonar o repositório

```bash
mkdir mcp && cd mcp
git clone https://github.com/gabriel-silveira/mcp-server.git .
```

### 4.2. Configurar ambiente virtual

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4.3. Instalar dependências

```bash
pip install --upgrade pip
pip install uv
uv pip install -e ".[dev]"

# Verificar se o Gunicorn foi instalado corretamente
which gunicorn || pip install gunicorn
```

### 4.4. Configurar variáveis de ambiente

```bash
nano .env
```

Edite o arquivo `.env` com as configurações necessárias para o ambiente de produção.
```bash
ARCADE_API_KEY="your_arcade_api_key"
OPENAI_API_KEY="your_openai_api_key"
```

### 4.5. Testar a aplicação

```bash
uvicorn main:app --host 0.0.0.0 --port 2906
```

Pressione Ctrl+C para encerrar o servidor de teste.

## 5. Configuração do Gunicorn

### 5.1. Criar arquivo de serviço do systemd

```bash
sudo nano /etc/systemd/system/mcp.service
```

Adicione o seguinte conteúdo:

```ini
[Unit]
Description=MCP Server
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/home/ubuntu/mcp
Environment="PATH=/home/ubuntu/mcp/venv/bin"
ExecStart=/home/ubuntu/mcp/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:2906 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 5.2. Iniciar e habilitar o serviço

```bash
sudo systemctl daemon-reload
sudo systemctl start mcp
sudo systemctl enable mcp
```

### 5.3. Verificar status do serviço

```bash
sudo systemctl status mcp
```

## 6. Configuração do Nginx

### 6.1. Criar arquivo de configuração

```bash
sudo nano /etc/nginx/sites-available/mcp
```

Adicione o seguinte conteúdo:

```nginx
server {
    listen 80;
    # Configurar para responder ao domínio E ao endereço IP
    server_name seu-dominio.com www.seu-dominio.com seu-endereco-ip;
    # Alternativamente, para responder a qualquer solicitação: server_name _;

    location / {
        proxy_pass http://127.0.0.1:2906;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Configurações adicionais de segurança
    client_max_body_size 20M;
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
```

### 6.2. Habilitar o site e testar a configuração

```bash
# Remover o site padrão do Nginx para evitar conflitos
sudo rm -f /etc/nginx/sites-enabled/default

# Habilitar o site MCP
sudo ln -s /etc/nginx/sites-available/mcp /etc/nginx/sites-enabled/

# Testar a configuração
sudo nginx -t
```

Se o teste for bem-sucedido, reinicie o Nginx:

```bash
sudo systemctl restart nginx
```

### 6.3. Verificar o funcionamento

```bash
# Verificar se o serviço está rodando na porta 2906
curl http://localhost:2906

# Verificar se o Nginx está encaminhando corretamente
curl http://localhost
```

## 7. Configurar HTTPS com Let's Encrypt (Opcional, mas altamente recomendado)

### 7.1. Instalar o Certbot

```bash
sudo apt install -y certbot python3-certbot-nginx
```

### 7.2. Obter certificado SSL

```bash
sudo certbot --nginx -d seu-dominio.com -d www.seu-dominio.com
```

Siga as instruções para configurar o HTTPS.

### 7.3. Configurar renovação automática

O Certbot já configura um cron job para renovação automática. Você pode testar com:

```bash
sudo certbot renew --dry-run
```

## 8. Manutenção

### 8.1. Verificar logs da aplicação

```bash
sudo journalctl -u mcp -f
```

### 8.2. Verificar logs do Nginx

```bash
sudo tail -f /var/log/nginx/error.log
sudo tail -f /var/log/nginx/access.log
```

### 8.3. Atualizar a aplicação

```bash
cd /home/ubuntu/mcp
git pull
source venv/bin/activate
uv pip install -e ".[dev]"
sudo systemctl restart mcp
```

## 9. Solução de Problemas

### 9.1. Verificar se a aplicação está rodando

```bash
curl http://localhost:2906
```

### 9.2. Verificar portas em uso

```bash
sudo ss -tulpn | grep LISTEN
```

### 9.3. Verificar erros do systemd

```bash
sudo systemctl status mcp
sudo journalctl -u mcp -n 50 --no-pager
```

## 10. Segurança Adicional (Recomendado para Produção)

1. Configurar firewall (UFW):
   ```bash
   sudo ufw allow OpenSSH
   sudo ufw allow 'Nginx Full'
   sudo ufw enable
   ```

2. Configurar atualizações automáticas de segurança:
   ```bash
   sudo apt install -y unattended-upgrades
   sudo dpkg-reconfigure -plow unattended-upgrades
   ```

3. Configurar fail2ban para proteção contra força bruta:
   ```bash
   sudo apt install -y fail2ban
   sudo systemctl enable fail2ban
   sudo systemctl start fail2ban
   ```

## Conclusão

Sua aplicação MCP Server agora está em execução em uma instância EC2 da AWS, com Gunicorn como servidor de aplicação e Nginx como proxy reverso. A aplicação está configurada para inicializar automaticamente com o sistema e inclui configurações básicas de segurança.

Para acessar sua aplicação, abra um navegador e acesse `http://seu-endereco-ip` ou seu domínio configurado.
