
import asyncio
from src.pyautoforge.mcp.crawler_production import ProductionMCPRegistryCrawler

async def full_crawl():
    print("Full 27,800+ Crawl - production VPS")
    crawler = ProductionMCPRegistryCrawler(db_path="mcp_registry_production.db")
    result = await crawler.crawl_all_production(limit_per_page=100, max_pages_per_source=200, resume=True)
    print(result)

if __name__ == "__main__":
    asyncio.run(full_crawl())
