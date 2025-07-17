FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Instalar pacotes essenciais e UV
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir uv

# Copiar arquivos necessários para o build
COPY README.md pyproject.toml uv.lock ./

# Instalar dependências usando UV (sem modo editable para evitar problemas)
RUN uv pip install --system --no-cache-dir -e .

# Copiar o restante do código da aplicação
COPY . .

# Expose the port the app runs on
EXPOSE 2906

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "2906"]
