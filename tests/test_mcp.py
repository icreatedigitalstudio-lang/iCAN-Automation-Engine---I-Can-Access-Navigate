
import pytest
from src.pyautoforge.mcp.mega_unified_server import MegaUnifiedMCPServer
from src.pyautoforge.mcp.registry_crawler import CURATED_TOP_100

def test_mega_tools():
    server = MegaUnifiedMCPServer()
    tools = server.list_tools()
    assert len(tools["tools"]) >= 50

def test_curated():
    assert len(CURATED_TOP_100) >= 40
