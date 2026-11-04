"""
iCREATE Automation Engine - Playwright Global Scraper Examples
For Shopee, Lazada, TikTok Shop - PH Market

Install:
pip install playwright beautifulsoup4 lxml httpx fake-useragent
playwright install chromium
"""

import asyncio
from src.pyautoforge.scraper import GlobalScraper, ScrapeConfig
from src.pyautoforge.scraper.providers import ShopeeScraper, LazadaScraper

async def example_1_smart_fallback():
    """Smart mode - HTTP first, auto fallback to Playwright if Cloudflare/blocked"""
    scraper = GlobalScraper(ScrapeConfig(geo="PH", strategy="smart"))
    result = await scraper.scrape("https://shopee.ph/search?keyword=iphone%2015")
    print(f"Smart: {result.url} | Status {result.status} | Title: {result.extracted.get('title','')[:100]}")
    print(f"Used strategy: {result.metadata.get('strategy')}")

async def example_2_browser_direct():
    """Direct browser mode - for JS heavy sites"""
    scraper = GlobalScraper(ScrapeConfig(geo="PH", strategy="browser", screenshot=False, timeout=45))
    result = await scraper.scrape("https://www.lazada.com.ph/tag/iphone/")
    print(f"Browser: {result.status} | HTML len {len(result.html)}")
    print(f"Title: {result.extracted.get('title')}")
    print(f"Prices found: {result.extracted.get('detected_prices')[:5]}")

async def example_3_shopee_provider():
    """Using pre-built Shopee provider"""
    scraper = ShopeeScraper(geo="PH")
    result = await scraper.scrape("https://shopee.ph/search?keyword=airpods")
    print(f"Shopee: {result.extracted}")

async def example_4_bulk_with_playwright():
    """Bulk scraping with browser - concurrency 3 only for browser to save RAM"""
    urls = [
        "https://shopee.ph/search?keyword=iphone",
        "https://www.lazada.com.ph/tag/iphone/",
        "https://www.tiktok.com/discover/tiktok-shop-iphone"
    ]
    scraper = GlobalScraper(ScrapeConfig(geo="PH", strategy="browser"))
    results = await scraper.scrape_bulk(urls, concurrency=2)
    for r in results:
        print(f"{r.url} -> {r.status} | success={r.success} | {r.duration:.1f}s")

if __name__ == "__main__":
    # asyncio.run(example_1_smart_fallback())
    asyncio.run(example_2_browser_direct())
