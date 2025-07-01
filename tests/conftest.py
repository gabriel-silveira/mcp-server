"""Shared test fixtures and configuration."""
import pytest
from unittest.mock import MagicMock
from pydantic import BaseModel

class TestArgsSchema(BaseModel):
    """Base schema for testing tools."""
    url: str
    formats: list[str] = ["markdown"]
    timeout: int = 30000
    tags: list[str] = []
    categories: list[str] = []

class MockTool:
    """Base mock tool for testing."""
    def __init__(self, name: str, should_fail: bool = False):
        self.name = name
        self.should_fail = should_fail
        self.args_schema = TestArgsSchema

    async def arun(self, arguments):
        if self.should_fail:
            raise Exception("Tool execution failed")
        return {
            "markdown": "Test content",
            "html": "<p>Test content</p>"
        }

@pytest.fixture
def mock_tool():
    """Fixture that returns a mock tool instance."""
    return lambda name="scrapeurl", should_fail=False: MockTool(name, should_fail)
