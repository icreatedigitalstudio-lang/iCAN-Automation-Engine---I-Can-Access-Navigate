"""
iCREATE Automation Engine - Official MCP SDK Example
Using Anthropic's official python-sdk (pip install mcp)

GitHub: https://github.com/modelcontextprotocol/python-sdk
Docs: https://modelcontextprotocol.io

Official SDK gives you native Claude Desktop compatibility
"""

import asyncio

# Example 1: Official SDK server (Claude Desktop native)
async def example_official_stdio():
    """
    This is what Claude Desktop runs - stdio transport
    Config in claude_desktop_config.json:
    {
      "mcpServers": {
        "icreate": {
          "command": "python",
          "args": ["-m", "pyautoforge.mcp.official_server"],
          "env": {"OLLAMA_BASE_URL": "http://localhost:11434"}
        }
      }
    }
    """
    try:
        from src.pyautoforge.mcp.official_server import run_official_stdio
        from src.pyautoforge.engine.core import AutomationEngine
        
        engine = AutomationEngine()
        # Register tasks
        @engine.task(task_id="hello", description="Hello task")
        def hello(ctx):
            return {"message": "Hello from official MCP SDK!"}
        
        print("Starting official MCP SDK stdio server - for Claude Desktop...")
        print("This will appear to hang - waiting for client on stdin (expected)")
        await run_official_stdio(engine=engine)
    except ImportError as e:
        print(f"Official MCP SDK not installed: {e}")
        print("Install: pip install mcp")

# Example 2: Custom MCP server (our existing) - supports more transports
async def example_custom_full():
    """
    Our custom server supports: stdio + websocket :8765 + tcp :8766 + sse :8767
    Official SDK only supports: stdio + sse (via Starlette)
    """
    from src.pyautoforge.engine.core import AutomationEngine
    from src.pyautoforge.mcp.server import MCPServer
    from src.pyautoforge.connectors import ConnectorManager
    
    engine = AutomationEngine()
    mcp_server = MCPServer(engine)
    manager = ConnectorManager(mcp_server, config={'ws_port': 8765, 'tcp_port': 8766, 'sse_port': 8767})
    
    print(f"Starting custom MCP with all transports: {manager.list_connectors()}")
    await manager.start_all()

# Example 3: Using official SDK client
async def example_official_client():
    """
    Client using official SDK to connect to any MCP server
    """
    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
        
        # Connect to filesystem server
        server_params = StdioServerParameters(
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        )
        
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                print(f"Tools from filesystem server: {tools}")
                resources = await session.list_resources()
                print(f"Resources: {resources}")
    except ImportError as e:
        print(f"Official SDK not installed: {e}")
    except Exception as e:
        print(f"Client example failed (need npx): {e}")

# Example 4: List all official reference servers
def example_list_servers():
    from src.pyautoforge.mcp.github_servers import list_official_servers
    data = list_official_servers()
    print("\nOfficial Reference Servers:")
    for name, info in data['reference'].items():
        print(f"  - {name}: {info['description']} | {info['command']}")
    
    print("\nArchived Servers:")
    for name, info in data['archived'].items():
        print(f"  - {name}: {info['description']}")
    
    print("\nSDKs:")
    for name, info in data['sdks'].items():
        print(f"  - {name} ({info['language']}): {info.get('install','')} | {info['repo']}")

if __name__ == "__main__":
    example_list_servers()
    # asyncio.run(example_official_stdio()) # For Claude Desktop
    # asyncio.run(example_custom_full()) # For full platform
    # asyncio.run(example_official_client())
