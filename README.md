# Lumina AI Framework

Lumina is an AI-augmented automation platform providing workflow orchestration, intelligent agent routing, and extensible service architecture.

## Components

- **lumina_core/** — Workflow engine, gatekeeper, JARVIS extensions
- **aios/** — AI Operating System kernel, intent processor
- **services/** — AI gateway, cluster router, voice actor, compute pool
- **skills/** — Pluggable skill modules (container-debug, ollama, n8n, security-scanner)
- **vscode-extensions/** — IDE integrations for VSCode and Cursor
- **config/** — Configuration templates and agent definitions
- **scripts/** — Automation utilities and framework tools

## Quick Start

```bash
pip install -r requirements.txt
```

## Architecture

Lumina uses a hierarchical agent system with:
- **JARVIS** — Master orchestrator and supervisor
- **Gatekeeper (Zuul)** — Quality gates and spectrum enforcement
- **AIOS Kernel** — Async intent processing and execution engine
- **Skill Registry** — Pluggable capabilities loaded at runtime

## License

MIT License — see [LICENSE](LICENSE)

## Premium Features

Advanced trading, strategy optimization, and financial intelligence features are available in [Lumina Premium](https://github.com/mlesnews/lumina-premium) (private).
