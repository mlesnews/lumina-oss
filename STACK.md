# Stack Guide

What you need to build a system like Lumina. This is a bill-of-materials organized by function, not a shopping list — swap any component for your preferred alternative.

## Philosophy

Three layers, clean separation:

| Layer | Contains | Visibility |
|-------|----------|------------|
| **Public** | Framework + patterns + templates | Open source (this repo) |
| **Private** | Strategies + real configs + domain logic | Your private repo |
| **Personal** | Secrets + credentials + keys | Vault only, never in git |

Nothing sensitive lives in the public layer. The framework is generic; the value is in YOUR private configuration.

## Core Infrastructure

### Compute Nodes
| Role | What to use | Notes |
|------|-------------|-------|
| Primary GPU node | Any NVIDIA GPU with 16GB+ VRAM | RTX 3090/4090/5090, runs local LLM inference |
| CPU inference | Any multi-core x86_64 | Microsoft BitNet for 1-bit models, no GPU needed |
| NAS / storage | Synology, TrueNAS, or any NAS | File storage, backups, lightweight services |
| Edge (optional) | Raspberry Pi, mini PC | Sensors, monitoring, lightweight tasks |

### Networking
| Component | Options | Purpose |
|-----------|---------|---------|
| Router/firewall | pfSense, OPNsense, Unifi | Network segmentation, IDS/IPS |
| DNS | Pi-hole, AdGuard Home | Ad blocking, local DNS resolution |
| VPN | WireGuard, Tailscale | Remote access to homelab |

## AI / LLM Stack

### Local Inference (Tier 1 — Free, Private)
| Tool | License | Purpose |
|------|---------|---------|
| [llama.cpp](https://github.com/ggerganov/llama.cpp) | MIT | GPU inference server — runs any GGUF model |
| [BitNet](https://github.com/microsoft/BitNet) | MIT | CPU-only 1-bit inference — runs on anything |
| [LiteLLM](https://github.com/BerriAI/litellm) | MIT | OpenAI-compatible proxy — routes to any backend |
| [Ollama](https://ollama.ai) | MIT | Easy model management — good for NAS deployment |
| [Open WebUI](https://github.com/open-webui/open-webui) | MIT | Chat UI for local models |

### Cloud AI (Tier 2 — Free Tiers)
| Service | Free tier | Purpose |
|---------|-----------|---------|
| Google Gemini | Generous free tier | Large context (1M tokens), fast |
| Groq | Free tier available | Ultra-fast inference (Llama 3.3 70B) |
| Cerebras | Free tier available | Fast inference, various models |
| Mistral AI | Free tier available | European AI, Codestral for code |
| Cohere | Free tier available | RAG-optimized models |

### Premium AI (Tier 3 — Paid, Last Resort)
| Service | Use case |
|---------|----------|
| Cloud LLM provider | Complex reasoning, audit trail tasks |
| Cloud speech services | High-quality TTS/STT |

## Databases

| Database | License | Use case |
|----------|---------|----------|
| [MariaDB](https://mariadb.org) | GPLv2 | Relational data, audit trails, device catalogs |
| [Redis](https://redis.io) | BSD-3 | Caching, event bus, state management |
| [PostgreSQL](https://postgresql.org) | PostgreSQL License | Financial data, complex queries |
| [ChromaDB](https://www.trychroma.com) | Apache 2.0 | Vector embeddings, RAG, semantic search |
| [SQLite](https://sqlite.org) | Public domain | Embedded/lightweight, trade history |

## Automation & Orchestration

| Tool | License | Purpose |
|------|---------|---------|
| [Docker](https://docker.com) + Compose | Apache 2.0 | Container runtime for all services |
| [n8n](https://n8n.io) | Sustainable Use | Visual workflow automation |
| [Nginx](https://nginx.org) | BSD-2 | Reverse proxy, load balancing |
| [Traefik](https://traefik.io) | MIT | Modern reverse proxy with auto-HTTPS |
| [Portainer](https://portainer.io) | Zlib | Docker management UI |
| [Watchtower](https://containrrr.dev/watchtower/) | Apache 2.0 | Auto-update containers |

## Monitoring & Observability

| Tool | License | Purpose |
|------|---------|---------|
| [Prometheus](https://prometheus.io) | Apache 2.0 | Metrics collection |
| [Grafana](https://grafana.com) | AGPLv3 | Dashboards and visualization |
| [Loki](https://grafana.com/oss/loki/) | AGPLv3 | Log aggregation |
| [Netdata](https://netdata.cloud) | GPLv3 | Real-time system monitoring |
| [Uptime Kuma](https://github.com/louislam/uptime-kuma) | MIT | Service uptime monitoring |

## Security

| Tool | License | Purpose |
|------|---------|---------|
| Cloud secret vault | Varies | Centralized secret management |
| [Vaultwarden](https://github.com/dani-garcia/vaultwarden) | AGPLv3 | Self-hosted password manager |
| [Cowrie](https://github.com/cowrie/cowrie) | BSD-3 | SSH honeypot — intrusion detection |
| [TruffleHog](https://github.com/trufflesecurity/trufflehog) | AGPLv3 | Git secret scanning in CI |

## Communication

| Channel | Options | Purpose |
|---------|---------|---------|
| Chat bot | Telegram Bot API, Discord.py, Slack SDK | Mobile interface to your AI |
| SMS gateway | Vonage, Twilio | Remote alerts when internet is down |
| Voice | Whisper (STT) + Edge TTS / Piper (TTS) | Voice interface |

## Development Tools

| Tool | License | Purpose |
|------|---------|---------|
| [Claude Code](https://docs.anthropic.com/en/docs/claude-code) | Proprietary | AI coding assistant (runs these slash commands) |
| [aider](https://aider.chat) | Apache 2.0 | AI pair programming — delegates routine coding |
| [Playwright](https://playwright.dev) | Apache 2.0 | Browser automation |
| [WakaTime](https://wakatime.com) | BSD-3 (client) | Developer time tracking |

## Financial (Domain-Specific)

These are categories — swap for your domain's equivalents:

| Function | What it does |
|----------|-------------|
| Trading bot API | Executes trades based on signals |
| Bank account linking | Transaction sync, balance tracking |
| Brokerage connection | Portfolio sync, investment tracking |
| Market data feed | Price data, fear/greed indices |
| Charting platform | Technical analysis, signal generation |
| Accounting engine | Double-entry bookkeeping, tax lots |

## MCP Servers (Claude Code Integration)

[Model Context Protocol](https://modelcontextprotocol.io/) servers extend Claude Code with tools:

| Server | Purpose |
|--------|---------|
| `server-filesystem` | File operations |
| `server-git` | Git operations |
| `server-sqlite` | Database queries |
| MariaDB MCP server | Relational DB queries |
| `server-brave-search` | Web search |
| `server-puppeteer` | Web automation |
| `server-github` | GitHub operations |

## Cost Profile

| Tier | Monthly cost | Coverage |
|------|-------------|----------|
| Hardware (amortized) | ~$50-100/mo | GPU node + NAS over 3 years |
| Cloud AI (free tiers) | $0 | 90%+ of inference needs |
| Premium AI (when needed) | $50-200/mo | Complex reasoning, 5-10% of tasks |
| Cloud infrastructure | $10-50/mo | Secret vault, serverless functions |
| **Total** | **$100-350/mo** | Full AI-powered homelab |

Previous approach (all cloud): $500-1,000+/mo. Local-first saves 60-80%.

## Getting Started

1. **Start with compute** — one machine with a GPU (even a used RTX 3090)
2. **Add LiteLLM** — proxy that makes everything look like OpenAI
3. **Add this framework** — `pip install lumina-aios` for safety rails and workflow primitives
4. **Add a chat interface** — Telegram bot or Open WebUI
5. **Add monitoring** — Uptime Kuma + Netdata (30 minutes to set up)
6. **Grow from there** — NAS, more models, automation, domain-specific integrations
