
# PRIVATE REPO PROTECTION - iCREATE v4.0 Concept Protection Guide

## BAKIT PRIVATE PWEDE PA RIN FREE?

**Hindi mo need i-public para free!**

| Repo Type | GitHub Actions Free Minutes | Kaya ba v4.0 mo? |
|-----------|----------------------------|------------------|
| **PRIVATE (Free account)** | **2000 mins/month FREE** | **YES - 1410 mins/month lang gamit mo** |
| PUBLIC (Free account) | Unlimited FREE | YES unlimited pero kita code mo |

**Computation mo GitHub Actions Only Mode:**
- ci.yml 5-10 mins x 30 pushes = 150-300 mins/month
- crawler.yml 30 mins x 30 days = 900 mins/month
- dashboard.yml 2 mins x 30 pushes = 60 mins/month
- auto-train.yml 2 mins x 30 days = 60 mins/month
- cd.yml 10 mins x 30 pushes = 300 mins/month
- battle-test.yml 5 mins x 24 hours x 30 days = 3600 mins/month pero OPTIONAL lang to, pwede daily lang 5 mins x 30 = 150 mins/month
- **Total: ~1410 mins/month (without hourly battle-test) = PASOK SA 2000 MINS PRIVATE FREE**
- **With hourly battle-test: 1410 + 3600 = 5010 mins/month = need public OR Pro $4/mo 3000 mins OR self-hosted runner FREE unlimited**

**RECOMMENDATION: PRIVATE + daily battle-test lang muna, hindi hourly, para pasok sa 2000 mins FREE at protected concept**

## PAANO PROTECT CONCEPT - PRIVATE REPO SETUP

### 1. Gawin PRIVATE Repo (Free)

```bash
# Sa GitHub, create repo as PRIVATE
# Push mo private
git init
git add .
git commit -m "v4.0 Universal Platform 27,800+ - PRIVATE - Production Validated"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/automation-engine.git
git push -u origin main
```

### 2. .gitignore - Huwag i-push sensitive files

```gitignore
# Sensitive - NEVER push
.env
*.db
*.db-shm
*.db-wal
crawler_v4_checkpoint.json
crawler_checkpoints/
healed_selectors.db
brain_memory.db
sector_knowledge.db
training_data/
*.key
*.pem
secrets/

# Build artifacts
__pycache__/
*.pyc
.mypy_cache/
.ruff_cache/
dist/
build/
*.egg-info/

# OS
.DS_Store
Thumbs.db

# Keep these for GitHub Actions (needed for crawler)
!crawler_v4_27800.db
!icreate_v4_universal_platform_report.json
```

**Pero para sa GitHub Actions Only Mode, need mo i-commit:**
- crawler_v4_checkpoint.json (OK lang - public counts lang, hindi sensitive logic)
- icreate_v4_universal_platform_report.json (OK lang - stats lang)
- Wag mo i-commit: .env, *.db with credentials, healing db with client data

### 3. LICENSE - Proprietary, Not MIT

Create LICENSE file:

```
Proprietary License - iCREATE Digital Studio

Copyright (c) 2024 iCREATE Digital Studio - iCREATE Automation Engine v4.0 Universal Autonomous Automation Platform

All rights reserved. This software and its concept, architecture (6 layers, 10 specialists, Dynamic Agent Factory, Sector Intelligence Engine, 27,800+ one-click installer, 7-layer self-healing, AI Vision Healing, Memory RAG, Ollama Brain) is proprietary and confidential.

No part of this software, including but not limited to:
- Universal Autonomous Automation Platform architecture
- 27,800+ registry crawler with cursor pagination FTS5 dedup hash
- One-click installer DynamicMCPLoader stdio handshake
- 7-layer self-healing + AI Vision + Auto-Train + Memory RAG
- 10 specialists + Central Brain L4 + Dynamic Agent Factory
- Multi-employer isolation + Multi-tenant isolation
- 68/68 tasks 100% workforce benchmark

may be reproduced, distributed, or transmitted in any form or by any means without prior written permission of iCREATE Digital Studio.

For licensing inquiries: iCREATE Digital Studio

This is NOT open source. Unauthorized copying is strictly prohibited.
```

### 4. GitHub Pages from PRIVATE Repo - Protected pa rin

- Private repo mo, pero GitHub Pages site public accessible (dashboard lang kita, hindi source code)
- Settings -> Pages -> Source: GitHub Actions
- Site live at https://YOUR_USERNAME.github.io/automation-engine/ - dashboard lang kita, hindi yung buong engine code
- Source code mo PRIVATE pa rin, hindi nila makikita

### 5. GHCR Package - PRIVATE

- ghcr.io/icreate-studio/automation-engine:latest
- Settings -> Packages -> Change visibility to PRIVATE
- Only you can pull with GITHUB_TOKEN

### 6. Secrets - Never in code

- GitHub Settings -> Secrets and variables -> Actions -> New repository secret
- VPS_HOST, VPS_USER, SSH_KEY, OPENAI_API_KEY, etc
- Never hardcode sa code, use os.getenv()

## ANO PWEDENG KOPYAHIN KUNG PUBLIC? ANO HINDI?

**Kung naka-PUBLIC (risk):**
- Kita nila buong concept: 6 layers, 10 specialists, Dynamic Agent Factory, Sector Intelligence Engine, 27,800+ crawler, one-click installer, 7-layer healing, etc
- Pwede nila i-fork at i-rebrand

**Pero kahit public, mahirap kopyahin execution mo:**
- Curated 46 top 100+ tools mo - need nila i-research ulit
- 68/68 tasks 100% workforce benchmark with controls - need nila i-validate ulit
- 89/89 production validation - need nila i-battle test 1 month
- 27,800+ deduped registry - need nila i-crawl ulit 30 mins daily
- Brand iCREATE Digital Studio + client relationships + pricing

**Kung PRIVATE (recommended):**
- Hindi nila kita code at concept
- 2000 mins/month FREE pa rin, pasok 1410 mins/month
- Dashboard sa GitHub Pages public pero source private
- GHCR private

## FINAL RECOMMENDATION - PRIVATE + FREE + PROTECTED

1. **Repo PRIVATE** - 2000 mins/month FREE, pasok 1410 mins/month (daily crawler + daily battle-test, hindi hourly)
2. **.gitignore** - Wag i-push .env, *.db sensitive, healing db with client data
3. **LICENSE Proprietary** - Not MIT, bawal kopyahin
4. **GitHub Pages from private repo** - Dashboard public pero source private (OK lang)
5. **GHCR private** - Package private
6. **Secrets sa GitHub Secrets** - Never sa code
7. **Optional upgrade later:** Pro $4/mo = 3000 mins/month OR Oracle Always Free self-hosted runner = unlimited mins FREE + private pa rin

## COST

- **PRIVATE + GitHub Actions Only Mode + GitHub Pages = 100% FREE + PROTECTED CONCEPT**
- **2000 mins/month free = enough for daily crawler 30 mins x 30 = 900 mins + ci/cd/dashboard/auto-train ~510 mins = 1410 mins**
- **No need public para free**

## DEPLOYMENT PRIVATE MODE

```bash
# Private repo
git init
git add .
git commit -m "v4.0 PRIVATE - Production Validated 89/89 100% + Workforce 68/68 100% - Protected Concept"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/automation-engine.git
git push -u origin main

# Settings -> Pages -> Source: GitHub Actions -> live at https://YOUR_USERNAME.github.io/automation-engine/ (dashboard public, source private)
# Actions tab -> 6 workflows running PRIVATE + FREE
# No secrets needed
```

**Brand: iCREATE Digital Studio - iCREATE Automation Engine v4.0 Universal Autonomous Automation Platform 27,800+ Connectors One-Click Installer - Global Standards Production Validated - Proprietary - Protected Concept**

Deploy: PRIVATE repo + GitHub Actions Only Mode FREE + GitHub Pages dashboard public source private + GHCR private = protected concept + free deployment
