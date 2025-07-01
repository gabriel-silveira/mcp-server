# Testes do MCP Server

Este documento descreve como executar os testes do MCP Server e quais ferramentas são necessárias.

## Pré-requisitos

Os seguintes pacotes são necessários para executar os testes:

- `pytest`: Framework de testes
- `pytest-cov`: Plugin para análise de cobertura de código
- `pytest-asyncio`: Plugin para testes assíncronos
- `httpx`: Cliente HTTP para testes do FastAPI

Todos estes pacotes já estão configurados nas dependências de desenvolvimento do projeto. Para instalá-los, execute:

```bash
uv pip install -e ".[dev]"
```

## Executando os Testes

### Testes Básicos

Para executar todos os testes:

```bash
pytest
```

Para executar testes com mais detalhes:

```bash
pytest -v
```

### Testes com Cobertura

Para executar os testes e ver a cobertura básica:

```bash
pytest --cov=src tests/
```

Para ver um relatório detalhado com as linhas que faltam cobertura:

```bash
pytest --cov-report term-missing --cov=src tests/
```

Para gerar um relatório HTML da cobertura:

```bash
pytest --cov-report html --cov=src tests/
```

O relatório HTML será gerado no diretório `htmlcov/`. Abra o arquivo `htmlcov/index.html` no navegador para ver uma visualização detalhada da cobertura de cada arquivo.
