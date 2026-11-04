"""
iCREATE Automation Engine - One-Click Installer Example
From dashboard -> one click -> executable tool in mega server
"""

import asyncio
import json
from src.pyautoforge.mcp.dynamic_loader import DynamicMCPLoader
from src.pyautoforge.mcp.mega_unified_server import MegaUnifiedMCPServer
from src.pyautoforge.connectors import ConnectorManager

async def example_one_click():
    """One-click install from 10k+ registry"""
    loader = DynamicMCPLoader()
    
    # One-click install shopify from 27,800
    print("One-click installing shopify from 10k+ registry...")
    result = await loader.install_and_load("shopify")
    print(json.dumps(result, indent=2))
    
    # Install many
    print("\nInstalling many: filesystem, fetch, firecrawl...")
    results = await loader.install_many(["filesystem", "fetch", "firecrawl"], concurrency=3)
    print(json.dumps(results, indent=2))
    
    # List loaded - now 150+ + dynamic tools
    print("\nLoaded servers:")
    print(json.dumps(loader.list_loaded(), indent=2))
    
    # Call tool from dynamically loaded server
    print("\nCalling tool from dynamic server...")
    result = await loader.call_tool("firecrawl_scrape", {"url": "https://example.com"})
    print(json.dumps(result, indent=2))

async def example_mega_with_dynamic():
    """Mega unified + dynamic loader = 150+ + dynamic"""
    from src.pyautoforge.engine.core import AutomationEngine
    
    engine = AutomationEngine()
    
    @engine.task(task_id="hello", description="Hello")
    def hello(ctx):
        return {"message": "Hello from mega + dynamic!"}
    
    # Mega server
    mega = MegaUnifiedMCPServer(engine=engine)
    print(f"Mega base tools: {len(mega.list_tools()['tools'])}")  # 150+
    
    # Dynamic loader
    loader = DynamicMCPLoader()
    await loader.install_and_load("shopify")
    await loader.install_and_load("firecrawl")
    
    print(f"Dynamic loaded: {loader.list_loaded()['total_tools']} tools")
    print(f"Total with dynamic: {len(mega.list_tools()['tools']) + loader.list_loaded()['total_tools']}")
    
    # Start both
    manager = ConnectorManager(mega, config={'ws_port': 8765})
    await manager.start_all()

async def example_api_server():
    """FastAPI for dashboard one-click install"""
    import uvicorn
    from src.pyautoforge.mcp.dynamic_loader import app
    
    print("Starting Dynamic Loader API on :8768")
    print("Dashboard can POST /install with {name: 'shopify'}")
    print("One-click install -> executable tool")
    uvicorn.run(app, host="0.0.0.0", port=8768)

if __name__ == "__main__":
    asyncio.run(example_one_click())
    # asyncio.run(example_mega_with_dynamic())
    # asyncio.run(example_api_server())
