"""
iCREATE Automation Engine - Full Global Monitor Example
With Captcha + Proxy + Sheets + Telegram

pip install playwright gspread google-auth httpx
playwright install chromium
"""

import asyncio
from src.pyautoforge.integrations.monitor import GlobalPriceMonitor
from src.pyautoforge.scraper.proxy_manager import ProxyConfig
from src.pyautoforge.scraper.captcha import CaptchaConfig
from src.pyautoforge.integrations.google_sheets import GoogleSheetsExporter
from src.pyautoforge.integrations.telegram import TelegramNotifier

# 1. Configure
proxy_cfg = ProxyConfig(
    provider="custom",
    custom_list=[
        # "http://user:pass@1.2.3.4:8000",
    ],
    country="PH"
)

captcha_cfg = CaptchaConfig(
    provider="capsolver",
    api_key="YOUR_CAPSOLVER_API_KEY"  # Get from capsolver.com
)

sheets = GoogleSheetsExporter(
    creds_path="service_account.json",  # From Google Cloud Console
    sheet_id="YOUR_SHEET_ID"
)

telegram = TelegramNotifier(
    bot_token="123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
    chat_id="-1001234567890"  # Your channel ID
)

monitor = GlobalPriceMonitor(
    proxy_config=proxy_cfg if proxy_cfg.custom_list else None,
    captcha_config=captcha_cfg if captcha_cfg.api_key else None,
    sheets_exporter=sheets,
    telegram_notifier=telegram
)

# 2. URLs to monitor - PH e-commerce
urls_to_monitor = [
    "https://shopee.ph/search?keyword=iphone%2015%20pro",
    "https://www.lazada.com.ph/tag/iphone-15-pro/",
    "https://www.tiktok.com/discover/tiktok-shop-iphone-15",
]

async def main():
    print("🚀 iCREATE Global Price Monitor Starting...")
    results = await monitor.monitor_urls(
        urls=urls_to_monitor,
        geo="PH",
        strategy="smart"  # Will auto fallback to browser for Shopee/Lazada
    )
    
    print(f"\n📊 Results: {len(results)} products")
    for r in results:
        print(f"- {r['title'][:60]} | {r['price']} | {r['competitor']} | {r['url'][:50]}")

if __name__ == "__main__":
    asyncio.run(main())
