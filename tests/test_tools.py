import pytest
from unittest.mock import patch, MagicMock
from pydantic import BaseModel
from src.tools.base import handle_tool_call, ToolCallParams, find_tool_by_name
from src.schemas.mcp_schemas import MCPErrorCode

class MockArgsSchema(BaseModel):
    url: str
    formats: list[str] = ["markdown"]
    timeout: int = 30000
    tags: list[str] = []  # Novo campo para testar array padrão
    categories: list[str] = []  # Mais um campo array

class MockTool:
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.args_schema = MockArgsSchema

    async def arun(self, arguments):
        if self.should_fail:
            raise Exception("Tool execution failed")
        return {
            "markdown": "Test content",
            "html": "<p>Test content</p>"
        }

@pytest.fixture(autouse=True)
def mock_tools(monkeypatch):
    tools_dict = {}
    tools_dict["scrapeurl"] = MockTool("scrapeurl")
    
    # Mock the find_tool_by_name function
    def mock_find_tool_by_name(name):
        return tools_dict.get(name.lower())
    
    # Mock the manager.requires_auth method
    mock_manager = MagicMock()
    mock_manager.requires_auth.return_value = False
    
    monkeypatch.setattr("src.tools.base.find_tool_by_name", mock_find_tool_by_name)
    monkeypatch.setattr("src.tools.base.manager", mock_manager)
    return tools_dict

@pytest.mark.asyncio
async def test_handle_nonexistent_tool_not_found():
    """Test tool not found error"""
    result = await handle_tool_call(1, "nonexistent_tool", {})
    data = result.body.decode()
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"error"' in data
    assert str(MCPErrorCode.METHOD_NOT_FOUND.value) in data
    assert "Tool nonexistent_tool not found" in data

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_with_none_result(mock_tools, monkeypatch):
    """Test tool execution with None result"""
    async def mock_arun(arguments):
        return None
    
    tools_dict = {}
    tool = MockTool("scrapeurl")
    tool.arun = mock_arun
    tools_dict["scrapeurl"] = tool
    
    # Mock the find_tool_by_name function
    def mock_find_tool_by_name(name):
        return tools_dict.get(name.lower())
    
    # Mock the manager object
    mock_manager = MagicMock()
    mock_manager.requires_auth.return_value = False
    
    monkeypatch.setattr("src.tools.base.find_tool_by_name", mock_find_tool_by_name)
    monkeypatch.setattr("src.tools.base.manager", mock_manager)
    
    result = await handle_tool_call(1, "scrapeurl", {"url": "https://example.com"})
    data = result.body.decode()
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"content"' in data
    assert '""' in data  # Empty string content

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_with_string_result(mock_tools, monkeypatch):
    """Test tool execution with string result"""
    async def mock_arun(arguments):
        return "Direct string result"
    
    tools_dict = {}
    tool = MockTool("scrapeurl")
    tool.arun = mock_arun
    tools_dict["scrapeurl"] = tool
    
    # Mock the find_tool_by_name function
    def mock_find_tool_by_name(name):
        return tools_dict.get(name.lower())
    
    # Mock the manager object
    mock_manager = MagicMock()
    mock_manager.requires_auth.return_value = False
    
    monkeypatch.setattr("src.tools.base.find_tool_by_name", mock_find_tool_by_name)
    monkeypatch.setattr("src.tools.base.manager", mock_manager)
    
    result = await handle_tool_call(1, "scrapeurl", {"url": "https://example.com"})
    data = result.body.decode()
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"content"' in data
    assert "Direct string result" in data

@pytest.mark.asyncio
async def test_handle_scrapeurl_tool_with_dict_result(mock_tools, monkeypatch):
    """Test tool execution with dictionary result"""
    async def mock_arun(arguments):
        return {"other_key": "Other content"}
    
    tools_dict = {}
    tool = MockTool("scrapeurl")
    tool.arun = mock_arun
    tools_dict["scrapeurl"] = tool
    
    # Mock the find_tool_by_name function
    def mock_find_tool_by_name(name):
        return tools_dict.get(name.lower())
    
    # Mock the manager object
    mock_manager = MagicMock()
    mock_manager.requires_auth.return_value = False
    
    monkeypatch.setattr("src.tools.base.find_tool_by_name", mock_find_tool_by_name)
    monkeypatch.setattr("src.tools.base.manager", mock_manager)
    
    result = await handle_tool_call(1, "scrapeurl", {"url": "https://example.com"})
    data = result.body.decode()
    assert '"id":1' in data
    assert '"jsonrpc":"2.0"' in data
    assert '"content"' in data
    assert "{'other_key': 'Other content'}" in data
