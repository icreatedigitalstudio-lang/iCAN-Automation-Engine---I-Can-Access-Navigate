"""
iCREATE Automation Engine - Ollama Brain with Memory + RAG Example
Long-term memory, remembers all heals, RAG reuse for faster healing

Setup:
ollama serve
ollama pull qwen2.5-coder:7b
ollama pull nomic-embed-text

pip install httpx beautifulsoup4 lxml
"""

import asyncio
import os
from src.pyautoforge.brain.memory_brain import MemoryBrain
from src.pyautoforge.brain.ollama_brain import OllamaConfig
from src.pyautoforge.brain.memory import MemoryConfig

async def example_1_memory_rag():
    print("🧠 Memory Brain with RAG Demo")
    
    brain = MemoryBrain(
        ollama_config=OllamaConfig(model="qwen2.5-coder:7b"),
        memory_config=MemoryConfig(db_path="brain_memory.db")
    )
    
    # Simulate first heal - Shopee changes layout
    html_v1 = """
    <html><body>
        <div class="new-layout-v1">
            <span class="price-new-v1">₱1,299</span>
        </div>
    </body></html>
    """
    
    print("\n1. First heal - no memory yet, will call Ollama...")
    result1 = await brain.heal_with_memory(
        html=html_v1,
        url="https://shopee.ph/test",
        field_name="shopee_price",
        old_selector="._2ShlId",
        error="selector not found"
    )
    print(f"First heal result: {result1}")
    
    # Simulate second heal - similar layout, should reuse from memory (fast, no LLM call)
    html_v2 = """
    <html><body>
        <div class="new-layout-v1-similar">
            <span class="price-new-v1">₱1,499</span>
        </div>
    </body></html>
    """
    
    print("\n2. Second heal - similar case, should reuse from memory (RAG)...")
    result2 = await brain.heal_with_memory(
        html=html_v2,
        url="https://shopee.ph/test2",
        field_name="shopee_price",
        old_selector="._2ShlId",
        error="selector not found"
    )
    print(f"Second heal result (should be memory reuse): {result2}")
    
    # Stats
    stats = await brain.get_brain_stats()
    print(f"\n📊 Brain stats: {stats}")

async def example_2_search_memory():
    from src.pyautoforge.brain.memory import BrainMemory
    
    mem = BrainMemory(MemoryConfig(db_path="brain_memory.db"))
    
    print("\n🔍 Searching memory for shopee price heals...")
    results = await mem.search_memories("shopee price healing", domain="shopee.ph", top_k=5)
    for r in results:
        print(f"- {r['memory_id']} | sim {r['similarity']:.2f} | {r['content']}")
    
    print(f"\n📊 Memory stats: {mem.get_stats()}")

async def example_3_memory_brain_flow():
    """
    Full flow: failure -> remember -> search -> heal -> remember success
    """
    brain = MemoryBrain()
    
    domain = "shopee.ph"
    field = "shopee_price"
    
    # Remember a failure
    await brain.remember_failure(domain, field, "selector ._2ShlId not found, page changed", "<div>₱1,299</div>")
    print("Remembered failure")
    
    # Later, search similar failures to avoid same mistake
    similar_failures = await brain.memory.search_memories("shopee price failure", domain=domain, memory_type="failure", top_k=3)
    print(f"Similar past failures: {len(similar_failures)}")
    
    # Heal
    html = "<div class='price-new'>₱1,299</div>"
    result = await brain.heal_with_memory(html, f"https://{domain}/test", field, "._2ShlId", "not found")
    print(f"Healed: {result}")
    
    # Remember success
    if result:
        await brain.remember_success(domain, field, result['healed_selector'])
        print("Remembered success")

if __name__ == "__main__":
    asyncio.run(example_1_memory_rag())
    # asyncio.run(example_2_search_memory())
    # asyncio.run(example_3_memory_brain_flow())
