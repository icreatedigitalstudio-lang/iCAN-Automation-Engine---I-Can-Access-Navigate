"""
iCREATE Automation Engine - AI Vision Self-Healing Example
Auto-generates selectors when layout completely changes

pip install openai beautifulsoup4 lxml httpx
Set OPENAI_API_KEY env var
"""

import asyncio
import os
from src.pyautoforge.self_healing.ai_healer import AIHealer, AIHealingConfig
from src.pyautoforge.self_healing.healing_engine import SelfHealingEngine

async def example_1_ai_heal_price():
    # Config with OpenAI
    config = AIHealingConfig(
        provider="openai",
        api_key=os.getenv("OPENAI_API_KEY", ""),
        model="gpt-4o-mini",
        auto_update_db=True
    )
    
    healer = AIHealer(config, db_path="healed_selectors.db")
    
    # Simulated new Shopee HTML where they changed everything
    html_new = """
    <html><body>
        <div class="new-shopee-layout-2025">
            <div class="product-header">
                <span class="x-product-name-new">iPhone 15 Pro Max 256GB</span>
                <div class="price-wrapper-v3">
                    <span class="current-price-new-style">₱75,990</span>
                </div>
            </div>
        </div>
    </body></html>
    """
    
    print("🤖 AI Healing: Old selector ._2ShlId broke, new layout detected...")
    result = await healer.heal_with_llm(
        html=html_new,
        url="https://shopee.ph/search?keyword=iphone",
        field_name="shopee_price",
        old_selector="._2ShlId",
        screenshot_b64=None  # Add screenshot base64 for vision mode
    )
    
    print(f"Result: {result}")
    
    # Check DB
    healed = healer.get_healed_selector("shopee.ph", "shopee_price")
    print(f"Saved in DB: {healed}")
    
    all_healed = healer.get_all_healed("shopee.ph")
    print(f"All healed for shopee.ph: {all_healed}")

async def example_2_full_engine_ai():
    engine = SelfHealingEngine()
    # Enable AI healer with API key
    if os.getenv("OPENAI_API_KEY"):
        engine.ai_healer = AIHealer(
            AIHealingConfig(provider="openai", api_key=os.getenv("OPENAI_API_KEY"), model="gpt-4o-mini"),
            db_path="healed_selectors.db"
        )
        print("AI Healer enabled")
    
    # Simulate healing
    html = "<div class='price-new'>₱1,299</div>"
    result = await engine.heal_selector_failure_ai(html, "https://shopee.ph/test", "price", "._2ShlId")
    print(f"Engine AI healing: {result}")
    print(f"Health report: {engine.get_health_report()}")

if __name__ == "__main__":
    # asyncio.run(example_1_ai_heal_price())
    asyncio.run(example_2_full_engine_ai())
