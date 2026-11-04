"""
iCREATE Automation Engine - ConnectionManager Example
Centralized singleton for ALL service connections
"""

import asyncio
from src.pyautoforge.core.connections import connection_manager

async def example_1_basic():
    print("ConnectionManager Basic Example")
    redis = await connection_manager.get_redis()
    print(f"Redis: {redis is not None}")
    pg = await connection_manager.get_postgres()
    print(f"Postgres: {pg is not None}")
    ollama = connection_manager.get_ollama_client()
    print(f"Ollama client: {ollama is not None}")
    http = connection_manager.get_http_client()
    print(f"HTTP client: {http is not None}")
    proxy = connection_manager.get_proxy_manager()
    print(f"Proxy: {proxy is not None}")
    healed = connection_manager.get_healed_db()
    brain = connection_manager.get_brain_db()
    print(f"Healed DB: {healed is not None}, Brain DB: {brain is not None}")

async def example_2_health_check():
    print("\nHealth Check All Services")
    health = await connection_manager.health_check_all(force=True)
    import json
    print(json.dumps(health, indent=2))

if __name__ == "__main__":
    asyncio.run(example_1_basic())
    asyncio.run(example_2_health_check())
