"""
iCREATE Automation Engine - Full MCP/Connector Libraries Example

Run MCP server with all connectors:
- Stdio (for Claude Desktop)
- WebSocket :8765
- TCP :8766
- SSE :8767

Test with client
"""

import asyncio
from src.pyautoforge.engine.core import AutomationEngine
from src.pyautoforge.mcp.server import MCPServer
from src.pyautoforge.connectors import ConnectorManager

async def run_full_mcp_server():
    # Create engine
    engine = AutomationEngine()
    
    # Register some example tasks
    @engine.task(task_id="hello_world", description="Hello world task")
    def hello(ctx):
        return {"message": "Hello from iCREATE!", "ctx": ctx}

    # Create MCP server
    mcp_server = MCPServer(engine)
    
    # Create connector manager - all transports
    manager = ConnectorManager(mcp_server, config={
        'ws_host': '0.0.0.0', 'ws_port': 8765,
        'tcp_host': '0.0.0.0', 'tcp_port': 8766,
        'sse_host': '0.0.0.0', 'sse_port': 8767
    })
    
    print("🔌 Starting full MCP connector library...")
    print(f"Connectors: {manager.list_connectors()}")
    
    # Start all except stdio (stdio blocks stdin)
    # For Claude Desktop, run separately: python -m pyautoforge.mcp.stdio_main
    
    await manager.start_all(include_stdio=False)

async def test_mcp_client():
    from src.pyautoforge.mcp.client import MCPClient
    
    # Test WebSocket client
    client = MCPClient(transport="websocket", host="localhost", port=8765)
    if await client.connect_websocket():
        print("\n📡 Testing MCP client...")
        init = await client.initialize()
        print(f"Server info: {init.get('result',{}).get('serverInfo')}")
        
        tools = await client.list_tools()
        tool_names = [t['name'] for t in tools.get('result',{}).get('tools',[])]
        print(f"Tools ({len(tool_names)}): {tool_names[:10]}")
        
        resources = await client.list_resources()
        print(f"Resources: {resources.get('result',{}).get('resources',[])[:3]}")
        
        prompts = await client.list_prompts()
        print(f"Prompts: {prompts.get('result',{}).get('prompts',[])[:3]}")
        
        # Call healing report
        report = await client.call_tool("healing_report")
        print(f"Healing report: {str(report)[:500]}")
        
        await client.close()
    else:
        print("Failed to connect WebSocket - is server running on :8765?")

if __name__ == "__main__":
    # Run server in one terminal, client in another
    # Terminal 1: python examples/full_mcp_example.py (runs server)
    # Terminal 2: python -c "import asyncio; from examples.full_mcp_example import test_mcp_client; asyncio.run(test_mcp_client())"
    
    asyncio.run(run_full_mcp_server())
