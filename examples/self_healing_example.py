"""
iCREATE Automation Engine - Self-Healing Example
"""
import asyncio
from src.pyautoforge.self_healing import SelfHealingEngine, SelectorHealer
from src.pyautoforge.scraper.global_scraper import GlobalScraper, ScrapeConfig
from bs4 import BeautifulSoup

async def test_selector_healing():
    healer = SelfHealingEngine()
    
    # Simulate Shopee page where class changed from ._2ShlId to .aAcVaW
    html_old = '<div class="_2ShlId">₱1,299</div>'
    html_new = '<div class="aAcVaW new-price">₱1,299</div>'  # Shopee changed class!
    
    soup = BeautifulSoup(html_new, "html.parser")
    
    # Without healing: would fail
    # With healing: auto-detects fallback
    result = healer.heal_selector_failure(soup, "shopee_price")
    print(f"Healed result: {result}")
    print(f"Report: {healer.get_health_report()}")

async def test_task_healing():
    healer = SelfHealingEngine()
    
    async def flaky_task():
        import random
        if random.random() < 0.7:
            raise Exception("Random network error")
        return {"success": True, "data": "ok"}
    
    result = await healer.heal_task("test_task", flaky_task)
    print(f"Task healing result: {result}")

async def test_full_scraper_healing():
    scraper = GlobalScraper(ScrapeConfig(geo="PH", strategy="smart"))
    # Scraper now has built-in healer
    print(f"Scraper has healer: {scraper.healer is not None}")
    print(f"Healing stats: {scraper.healer.get_health_report() if scraper.healer else 'No healer'}")

if __name__ == "__main__":
    asyncio.run(test_selector_healing())
    asyncio.run(test_task_healing())
