"""
iCREATE Automation Engine - Production Crawler Example - Full 10k+ + 17.8k
Option B - Production-grade with pagination, resume, rate limiting

This is the real crawler that can fetch 27,800+ servers
"""

import asyncio
import json
from src.pyautoforge.mcp.crawler_production import ProductionMCPRegistryCrawler
from src.pyautoforge.mcp.auto_installer import MCPAutoInstaller

async def example_full_crawl():
    """Full crawl - 10k+ + 17.8k with pagination"""
    crawler = ProductionMCPRegistryCrawler(db_path="mcp_registry_production.db")
    
    # Full production crawl - 100 per page, 100 pages per source = 10k per source
    # Official registry: 100 * 100 = 10,000
    # Glama: 100 * 100 = 10,000
    # mcp.so: 100 * 100 = 10,000
    # Total: 30,000+
    result = await crawler.crawl_all_production(
        limit_per_page=100,
        max_pages_per_source=100,  # 100 pages * 100 = 10k per source
        resume=True  # Resume from checkpoint if interrupted
    )
    
    print(json.dumps(result, indent=2))
    print(f"\nCategories: {crawler.get_all_categories()}")
    print(f"\nStats: {crawler.get_stats()}")

async def example_search():
    """Search FTS5"""
    crawler = ProductionMCPRegistryCrawler(db_path="mcp_registry_production.db")
    
    # FTS search
    results = crawler.search_fts("shopify", 10)
    print(f"Search shopify: {json.dumps(results, indent=2)}")
    
    results = crawler.search_fts("scrape", 10)
    print(f"Search scrape: {len(results)} results")
    
    # Category
    ecommerce = crawler.get_by_category("ecommerce", 10)
    print(f"E-commerce: {ecommerce}")

async def example_auto_install():
    """Auto-install from 10k+ registry"""
    installer = MCPAutoInstaller(db_path="mcp_registry_production.db")
    
    # Install single
    result = await installer.install_server("shopify")
    print(f"Install shopify: {result}")
    
    # Install many from category
    results = await installer.install_many(["filesystem", "fetch", "git", "memory", "shopify", "firecrawl"], concurrency=3)
    print(f"Installed many: {json.dumps(results, indent=2)}")
    
    # Generate Claude config with 150+ tools
    config_path = installer.save_claude_config("claude_desktop_mega_150tools.json")
    print(f"Config saved: {config_path}")

async def example_resume():
    """Test resume capability"""
    crawler = ProductionMCPRegistryCrawler(db_path="mcp_registry_production.db")
    
    # First crawl - 5 pages
    print("First crawl - 5 pages...")
    result1 = await crawler.crawl_all_production(limit_per_page=100, max_pages_per_source=5, resume=True)
    print(f"First: {result1['total_unique_db']} total")
    
    # Resume - continue from checkpoint
    print("\nResuming - 5 more pages...")
    result2 = await crawler.crawl_all_production(limit_per_page=100, max_pages_per_source=10, resume=True)
    print(f"After resume: {result2['total_unique_db']} total")

if __name__ == "__main__":
    # asyncio.run(example_full_crawl())  # Full 27,800+ - needs internet, takes ~30 mins
    asyncio.run(example_search())
    # asyncio.run(example_auto_install())
    # asyncio.run(example_resume())
