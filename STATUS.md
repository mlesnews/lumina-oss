# STATUS

**Last updated:** 2026-05-11
**Current version:** v0.2.0 (in progress)
**Status:** Active development

## What's working today

- **HUD** — LCARS dashboard framework, color system, data adapters, federation support
- **Health** — Life domain scanner, anomaly detection, Apple Watch integration hooks

## In progress (v0.2.0 → v0.3.0)

- **Bus** — event-driven IPC for agent communication
- **LLM Routing** — multi-model orchestration with capacity scaling
- **Knowledge** — ChromaDB RAG pipeline with structured ingestion
- **Governance** — multi-agent advisory council and trust registry

## Recent activity

- 2026-05-11 — dependency refresh: pytest >=9.0.3, GitHub Actions checkout@v6, setup-python@v6
- 2026-05-11 — CI portability fix in flight (PR #7) — removing hardcoded test paths
- 2026-04-13 — initial public release of HUD and Health modules

## Cadence

This project ships from a private upstream (`mlesnews/lumina`). Public commits batch every 2–6 weeks when a generic framework piece reaches extractable shape. Silent periods in the commit log are **not** abandonment — they reflect upstream consolidation cycles, not project state.

## Contact

See [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for fork-based contribution workflow.
