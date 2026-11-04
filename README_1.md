# iCREATE Automation Engine v3.2 One-Click — by iCREATE Digital Studio, Lipa City, Batangas, Philippines

Enterprise-grade, self-hosted, offline-capable automation engine for PH e-commerce monitoring (Shopee/Lazada/TikTok Shop) + global scraping + 27,800+ MCP registry.

## Brand
- **Product:** iCREATE Automation Engine
- **Company:** iCREATE Digital Studio
- **Location:** Lipa City, Batangas, Philippines
- **Package:** `icreate-automation-engine` — CLI `icreate`
- **Version:** v3.2 One-Click — 150+ tools in ONE MCP server + 27,800+ registry + one-click installer

## Features
- DAG engine @engine.task(), retry, circuit breaker, rate limiter
- Global scraper smart/http/browser, Playwright stealth PH geo en-PH 14.5995,120.9842
- 7-layer self-healing: SelectorHealer, TaskHealer, Proxy, AIHealer, VisionHealer
- Ollama offline qwen2.5-coder:7b + llava:7b + nomic-embed-text, Memory RAG 0.1s reuse
- Auto-Train nightly 2 AM PH, healing_examples.jsonl push GitHub
- MCP: Official Registry 2,993 active (2,731 hosted + 248 packages) + Glama 96,262 + mcp.so 19,700 = 27,800+ total
- Mega Unified 150+ tools (54 base + 100+ curated) ONE server + Dynamic Loader one-click installer :8768
- Production: Docker non-root, docker-compose Redis/Postgres/Prometheus/Grafana/Ollama, k8s HPA 3-20 pods, 12-Factor

## Quickstart
```bash
pip install icreate-automation-engine
icreate --help
```

## GitHub Actions
- CI: ruff, mypy strict, pytest, 150+ tools verify
- CD: Docker Buildx multi-arch -> ghcr.io/icreate-studio/automation-engine -> Deploy Lipa City VPS + K8s
- Crawler: daily 2 AM PH 27,800+ registry
- Auto-Train: daily 2 AM PH heal export
- Release: tag v* -> GitHub Release
