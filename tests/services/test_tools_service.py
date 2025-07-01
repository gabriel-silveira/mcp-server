import pytest
from unittest.mock import patch, MagicMock
from src.services import tools_service
from src.config import server_name, server_version
from src.schemas.mcp_schemas import MCPErrorCode

def test_get_server_info():
    """Test server info response"""
    response = tools_service.get_server_info()
    
    assert response["id"] == 0
    assert response["jsonrpc"] == "2.0"
    assert response["result"]["protocolVersion"] == "2025-03-26"
    assert response["result"]["serverInfo"]["name"] == server_name
    assert response["result"]["serverInfo"]["version"] == server_version
    assert "capabilities" in response["result"]

def test_get_initialize_response():
    """Test initialize response"""
    request_id = 123
    response = tools_service.get_initialize_response(request_id)
    
    assert response["id"] == request_id
    assert response["jsonrpc"] == "2.0"
    assert response["result"]["protocolVersion"] == "2025-03-26"
    assert response["result"]["serverInfo"]["name"] == server_name
    assert response["result"]["serverInfo"]["version"] == server_version
    assert "capabilities" in response["result"]

def test_get_initialized_notification_response():
    """Test initialized notification response"""
    request_id = 456
    response = tools_service.get_initialized_notification_response(request_id)
    
    assert response["id"] == request_id
    assert response["jsonrpc"] == "2.0"
    assert response["result"] is None

def test_get_tools_list_response():
    """Test tools list response"""
    request_id = 789
    mock_tool = MagicMock()
    mock_tool.description = "Test tool"
    mock_tool.args_schema.model_json_schema.return_value = {
        "type": "object",
        "properties": {"url": {"type": "string"}},
        "required": ["url"]
    }
    
    with patch("src.services.tools_service.tools", {"test_tool": mock_tool}):
        response = tools_service.get_tools_list_response(request_id)
    
    assert response["id"] == request_id
    assert response["jsonrpc"] == "2.0"
    assert "tools" in response["result"]
    assert len(response["result"]["tools"]) == 1
    
    tool_info = response["result"]["tools"][0]
    assert tool_info["name"] == "test_tool"
    assert tool_info["description"] == "Test tool"
    assert tool_info["inputSchema"]["type"] == "object"
    assert "url" in tool_info["inputSchema"]["properties"]

def test_get_tools_list_response_no_schema():
    """Test tools list response with tool without schema"""
    request_id = 789
    mock_tool = MagicMock()
    mock_tool.description = "Test tool"
    # Remove args_schema attribute
    del mock_tool.args_schema
    
    with patch("src.services.tools_service.tools", {"test_tool": mock_tool}):
        response = tools_service.get_tools_list_response(request_id)
    
    assert response["id"] == request_id
    assert response["jsonrpc"] == "2.0"
    tool_info = response["result"]["tools"][0]
    assert tool_info["inputSchema"] == {
        "type": "object",
        "properties": {},
        "required": []
    }

@pytest.mark.asyncio
async def test_handle_tool_request_success():
    """Test successful tool request handling"""
    request_id = 101
    params = {
        "name": "test_tool",
        "arguments": {"url": "https://example.com"}
    }
    
    mock_response = MagicMock()
    with patch("src.services.tools_service.handle_tool_call", return_value=mock_response) as mock_handle:
        response = await tools_service.handle_tool_request(request_id, params)
        
        mock_handle.assert_called_once_with(request_id, "test_tool", {"url": "https://example.com"})
        assert response == mock_response

@pytest.mark.asyncio
async def test_handle_tool_request_validation_error():
    """Test tool request with invalid parameters"""
    request_id = 102
    params = {
        "invalid_field": "test"  # Missing required fields
    }
    
    response = await tools_service.handle_tool_request(request_id, params)
    data = response.body.decode()
    
    assert '"id":102' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"error"' in data
    assert str(MCPErrorCode.INTERNAL_ERROR.value) in data

@pytest.mark.asyncio
async def test_handle_tool_request_execution_error():
    """Test tool request with execution error"""
    request_id = 103
    params = {
        "name": "test_tool",
        "arguments": {"url": "https://example.com"}
    }
    
    with patch("src.services.tools_service.handle_tool_call", side_effect=Exception("Test error")):
        response = await tools_service.handle_tool_request(request_id, params)
        data = response.body.decode()
        
        assert '"id":103' in data
        assert '"jsonrpc":"2.0"' in data
        assert '"error"' in data
        assert str(MCPErrorCode.INTERNAL_ERROR.value) in data
        assert "Test error" in data
