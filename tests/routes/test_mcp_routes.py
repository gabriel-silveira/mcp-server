import pytest
from fastapi.testclient import TestClient
from src.app import app
from src.config import server_name, server_version

client = TestClient(app)

def test_mcp_get_endpoint():
    response = client.get("/mcp")
    assert response.status_code == 200
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 0
    assert data["result"]["protocolVersion"] == "2025-03-26"
    assert data["result"]["serverInfo"]["name"] == server_name
    assert data["result"]["serverInfo"]["version"] == server_version

@pytest.mark.parametrize("method", [
    "initialize",
    "notifications/initialized",
    "tools/list",
])
def test_valid_methods(method):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
    }
    response = client.post("/mcp", json=payload)
    assert response.status_code in [200, 202]
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    
    if method == "initialize":
        assert data["result"]["protocolVersion"] == "2025-03-26"
        assert data["result"]["serverInfo"]["name"] == server_name
    elif method == "notifications/initialized":
        assert response.status_code == 202
        assert data["result"] is None
    elif method == "tools/list":
        assert "tools" in data["result"]
        assert isinstance(data["result"]["tools"], list)

def test_invalid_method():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "invalid_method",
    }
    response = client.post("/mcp", json=payload)
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "error" in data
    assert data["error"]["code"] == -32601

def test_invalid_request_format():
    payload = {
        "invalid": "format"
    }
    response = client.post("/mcp", json=payload)
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 0
    assert "error" in data
    assert data["error"]["code"] == -32600

@pytest.mark.asyncio
async def test_tool_call():
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "firecrawl_scrape",
            "arguments": {
                "url": "https://example.com",
                "formats": ["markdown"]
            }
        }
    }
    response = client.post("/mcp", json=payload)
    data = response.json()
    assert data["jsonrpc"] == "2.0"
    assert data["id"] == 1
    assert "result" in data or "error" in data  # Both are valid responses depending on tool execution
