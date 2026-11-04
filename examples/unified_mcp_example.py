"""
iCREATE Automation Engine - Unified MCP Server Example
ONE server with ALL tools: iCREATE (22) + Official Reference (32) = 54 tools

Reference servers integrated from GitHub modelcontextprotocol/servers:
- Filesystem (7 tools): read_file, write_file, list_directory, etc
- Fetch (1): fetch web content
- Git (7): git_status, git_log, git_diff, git_show, etc
- Memory Graph (9): create_entities, create_relations, read_graph, search_nodes, etc
- SQLite (5): list_tables, describe_table, read_query, write_query, etc
- Time (2): get_current_time, convert_time
- Sequential Thinking (1): sequentialthinking for complex problem breakdown

Total: 54 tools in ONE MCP server
"""

import asyncio
from src.pyautoforge.engine.core import AutomationEngine
from src.pyautoforge.mcp.unified_server import UnifiedMCPServer
from src.pyautoforge.connectors import ConnectorManager

async def run_unified_server():
    engine = AutomationEngine()
    
    @engine.task(task_id="hello", description="Hello task")
    def hello(ctx):
        return {"message": "Hello from Unified MCP!"}

    # Unified server with all reference tools
    unified_server = UnifiedMCPServer(
        engine=engine,
        allowed_dirs=["/tmp", ".", "./data"],
        repo_path=".",
        memory_db="memory_graph.db",
        sqlite_db="healed_selectors.db"
    )

    print(f"Unified MCP Info: {unified_server.get_info()}")

    # Connector manager with unified server
    manager = ConnectorManager(unified_server, config={
        'ws_port': 8765,
        'tcp_port': 8766,
        'sse_port': 8767
    })

    print(f"Starting Unified MCP with {manager.list_connectors()}")
    print(f"Total tools: {unified_server.get_info()['total_tools']}")
    print("Tools: filesystem (7) + fetch (1) + git (7) + memory (9) + sqlite (5) + time (2) + sequential (1) + icreate (22) = 54")

    await manager.start_all()

async def test_unified_tools():
    from src.pyautoforge.mcp.unified_server import UnifiedMCPServer
    
    server = UnifiedMCPServer()
    
    # Test filesystem
    result = await server.handle_tool_call("list_directory", {"path": "."})
    print(f"list_directory: {str(result)[:500]}")
    
    # Test time
    result = await server.handle_tool_call("get_current_time", {"timezone": "Asia/Manila"})
    print(f"get_current_time: {result}")
    
    # Test memory graph
    result = await server.handle_tool_call("read_graph", {})
    print(f"read_graph: {str(result)[:500]}")
    
    # Test sqlite
    result = await server.handle_tool_call("list_tables", {"db_path": "healed_selectors.db"})
    print(f"list_tables: {result}")
    
    # Test iCREATE
    result = await server.handle_tool_call("healing_report", {})
    print(f"healing_report: {str(result)[:500]}")

if __name__ == "__main__":
    # asyncio.run(test_unified_tools())
    asyncio.run(run_unified_server())
