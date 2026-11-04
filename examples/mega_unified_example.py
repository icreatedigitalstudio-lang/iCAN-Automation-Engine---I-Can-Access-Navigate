"""
iCREATE Automation Engine - Mega Unified - Option B - 10k+ + 17.8k
100+ tools automation engine
"""

import asyncio
import json
from src.pyautoforge.engine.core import AutomationEngine
from src.pyautoforge.mcp.mega_unified_server import MegaUnifiedMCPServer
from src.pyautoforge.mcp.registry_crawler import MCPRegistryCrawler
from src.pyautoforge.connectors import ConnectorManager

async def run_mega():
    engine = AutomationEngine()
    
    @engine.task(task_id="hello", description="Hello from mega")
    def hello(ctx):
        return {"message": "Hello from Mega Unified 150+ tools!"}

    # Crawler - fetch 10k+ and 17.8k
    crawler = MCPRegistryCrawler()
    print("Crawling 10k+ registry + 17.8k mcp.so...")
    result = await crawler.crawl_all(limit_per_source=100)
    print(f"Crawl result: {json.dumps(result, indent=2)}")
    print(f"Categories: {crawler.get_all_categories()}")

    # Mega server
    mega_server = MegaUnifiedMCPServer(engine=engine, allowed_dirs=["/tmp", ".", "./data"])
    info = mega_server.get_mega_info()
    print(f"\nMega Unified Info: {json.dumps(info, indent=2)}")

    # Start
    manager = ConnectorManager(mega_server, config={'ws_port': 8765, 'tcp_port': 8766, 'sse_port': 8767})
    print(f"Starting Mega Unified with {len(mega_server.list_tools()['tools'])} tools")
    await manager.start_all()

async def test_search():
    crawler = MCPRegistryCrawler()
    crawler.load_curated()
    
    print(f"All categories: {crawler.get_all_categories()}")
    print(f"\nE-commerce: {crawler.get_by_category('ecommerce', 10)}")
    print(f"\nScraping: {crawler.get_by_category('scraping', 5)}")
    print(f"\nSearch 'shopify': {crawler.search('shopify', 3)}")
    print(f"\nSearch 'scrape': {crawler.search('scrape', 5)}")

if __name__ == "__main__":
    # asyncio.run(test_search())
    asyncio.run(run_mega())
