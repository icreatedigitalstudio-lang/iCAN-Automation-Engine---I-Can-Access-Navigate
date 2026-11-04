"""
iCREATE Automation Engine - Ollama as Brain Example
Local, offline, free - perfect for Lipa production

Setup:
1. Install Ollama: https://ollama.com/install
   curl -fsSL https://ollama.com/install.sh | sh

2. Pull models:
   ollama pull qwen2.5-coder:7b      # Best for selector generation (4GB)
   ollama pull llama3.1:8b            # General brain
   ollama pull llava:7b               # Vision for screenshot healing (4.5GB)
   ollama pull nomic-embed-text       # Embeddings (270MB)

3. Run Ollama:
   ollama serve  # Runs on http://localhost:11434

4. Test:
   python examples/ollama_brain_example.py
"""

import asyncio
import os
from src.pyautoforge.brain.ollama_brain import OllamaBrain, OllamaConfig
from src.pyautoforge.brain.brain_engine import BrainEngine, BrainConfig

async def example_1_check_ollama():
    brain = OllamaBrain(OllamaConfig(model="qwen2.5-coder:7b"))
    available = await brain.is_available()
    print(f"Ollama available: {available}")
    if available:
        models = await brain.list_models()
        print(f"Models installed: {models}")
    else:
        print("❌ Ollama not running. Run: ollama serve")

async def example_2_generate_selector():
    brain = OllamaBrain(OllamaConfig(model="qwen2.5-coder:7b"))
    
    # Simulate Shopee new layout
    html = """
    <html><body>
        <div class="new-shopee-2025-layout">
            <div class="product-info">
                <span class="x-product-title-new-v3">iPhone 15 Pro Max 256GB Titan</span>
                <div class="price-container-new">
                    <span class="current-price-x">₱75,990</span>
                    <span class="original-price">₱85,990</span>
                </div>
                <div class="sold-count">1.2k sold</div>
            </div>
        </div>
    </body></html>
    """
    
    print("🧠 Ollama Brain healing broken selector ._2ShlId...")
    result = await brain.generate_selector(html, "shopee_price", "._2ShlId", "https://shopee.ph/test")
    print(f"Result: {result}")

    result_title = await brain.generate_selector(html, "shopee_title", "[data-sqe='name']", "https://shopee.ph/test")
    print(f"Title Result: {result_title}")

async def example_3_brain_engine_auto():
    # Unified brain - auto chooses Ollama first, then OpenAI, then rules
    brain_engine = BrainEngine(BrainConfig(
        primary="auto",  # Try Ollama first, then OpenAI, then rules
        ollama_model="qwen2.5-coder:7b",
        openai_api_key=os.getenv("OPENAI_API_KEY",""),
        offline_mode=False
    ))
    
    html = "<div class='price-new-2025'>₱1,299</div>"
    result = await brain_engine.heal_selector(html, "https://shopee.ph/test", "price", "._2ShlId")
    print(f"Brain Engine healed: {result}")
    
    stats = await brain_engine.get_full_stats()
    print(f"Stats: {stats}")

async def example_4_offline_mode():
    # Pure offline - no cloud, only Ollama + rules - perfect for Lipa without internet
    brain_engine = BrainEngine(BrainConfig(
        primary="ollama",
        ollama_model="qwen2.5-coder:7b",
        offline_mode=True  # No OpenAI calls
    ))
    
    print("🔒 Offline mode - only local Ollama + rules")
    html = "<div class='new-price'>₱2,500</div>"
    result = await brain_engine.heal_selector(html, "https://shopee.ph/test", "price", ".old-price")
    print(f"Offline healed: {result}")

if __name__ == "__main__":
    # asyncio.run(example_1_check_ollama())
    # asyncio.run(example_2_generate_selector())
    asyncio.run(example_3_brain_engine_auto())
