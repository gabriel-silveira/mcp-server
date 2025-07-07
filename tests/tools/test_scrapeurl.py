"""Tests for the ScrapeUrl tool."""
import pytest
from unittest.mock import patch, MagicMock
from src.tools.base import handle_tool_call
from src.schemas.mcp_schemas import MCPErrorCode
from tests.conftest import MockTool

@pytest.fixture(autouse=True)
def mock_tools(mock_tool, monkeypatch):
    """Mock the find_tool_by_name function and manager for testing."""
    tool = mock_tool()
    def mock_find_tool_by_name(name):
        return tool if name.lower() == "scrapeurl" else None
    
    # Mock the manager object
    mock_manager = MagicMock()
    mock_manager.requires_auth.return_value = False
    
    monkeypatch.setattr("src.tools.base.find_tool_by_name", mock_find_tool_by_name)
    monkeypatch.setattr("src.tools.base.manager", mock_manager)

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_success(mock_tools):
    """Test successful tool execution."""
    result = await handle_tool_call(1, "scrapeurl", {"url": "https://example.com"})
    data = result.body.decode()
    
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"content"' in data
    assert "Test content" in data

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_not_found():
    """Test tool not found error."""
    with patch("src.tools.base.find_tool_by_name", return_value=None):
        result = await handle_tool_call(1, "nonexistent", {})
        data = result.body.decode()
        
        assert '"id":1' in data
        assert '"jsonrpc":"2.0"' in data
        assert '"error"' in data
        assert str(MCPErrorCode.METHOD_NOT_FOUND.value) in data

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_failure(mock_tools, monkeypatch):
    """Test tool execution failure."""
    failing_tool = MockTool("scrapeurl", should_fail=True)
    def mock_find_tool_by_name(name):
        return failing_tool if name.lower() == "scrapeurl" else None
    
    # Mock the manager object
    mock_manager = MagicMock()
    mock_manager.requires_auth.return_value = False
    
    monkeypatch.setattr("src.tools.base.find_tool_by_name", mock_find_tool_by_name)
    monkeypatch.setattr("src.tools.base.manager", mock_manager)
    result = await handle_tool_call(1, "scrapeurl", {"url": "https://example.com"})
    data = result.body.decode()
    
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"error"' in data
    assert str(MCPErrorCode.INTERNAL_ERROR.value) in data
    assert "Tool execution failed" in data

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_with_default_args(mock_tools):
    """Test tool execution with default arguments."""
    result = await handle_tool_call(1, "scrapeurl", {
        "url": "https://example.com",
        "formats": None,
        "tags": None,
        "categories": None
    })
    data = result.body.decode()
    
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"content"' in data
    assert "Test content" in data
