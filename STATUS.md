# STATUS

**Last updated:** 2026-06-08
**Current version:** v0.2.0 (2026-05-14)
**Status:** Active development

## What's actually in the public repo today

### Core (`lumina.aios`)
- **Kernel** — intent processor: classify, route, execute, return
- **Memory Manager** — multi-tier memory (CRITICAL → TEMPORARY) with TTL and eviction
- **Process** — molecule model: trigger + action + stopper + exit lifecycle
- **Health Aggregator** — weighted N-dimension health scoring with trend detection

### Safety (`lumina.safety`)
- **Circuit Breaker** — 5-level state machine (GREEN → BLACK)
- **Budget Guard** — API cost monitor with OPERATIONAL / WARNING / HALT
- **Secret Scanner** — regex detection for API keys, tokens, private keys, JWTs

### Workflow (`lumina.workflow`)
- **Decisioning Engine** — context scoring with threshold gates
- **Troubleshooting Decorator** — symptom collection + resolution tracking
- **Gatekeeper** — spectrum quality gate (RED → GREEN)
- **Verifier** — triple-verification with N independent checks + consensus

### Intel (`lumina.intel`)
- **Context Matrix** — multi-source knowledge aggregation
- **Pattern DB** — JSON-backed pattern storage with efficacy tracking

### Integrations (`lumina.integrations`)
- **WakaTime** — coding statistics API client
- **Ticket System** — JSON-backed ticket lifecycle management

### Powertools (`lumina.powertools`)
- **Statusline Renderer** — compact, color-coded HUD status bars
- **Hook Protocol** — stdin/stdout I/O parsing for Claude Code hooks
- **Cost Analyzer** — token usage analysis from JSONL cost logs

### Memory Score (`lumina.memory_score`) — added since v0.1.0
- **10-dimension MEMORY.md grader** — eats its own cooking (built on this framework's own HealthAggregator)
- CLI entrypoint, parser, scorer, constants, dimension definitions

### Claude Code Hooks (10 drop-ins)
compusec_guard · cost_tracker · trace_track · api_watchdog · secrets_redactor · fast_mode_tracker · precompact_snapshot · session_compiler · wakatime_heartbeat · autoboost_daemon

### Claude Code Commands
brainstorm · redact · snapshot · save · `/braintrust` (polymath panel, added since v0.1.0) · `/convergence` (AI measurement, added since v0.1.0)

### Documentation
README · CHANGELOG · CONTRIBUTING · SECURITY · CODE_OF_CONDUCT · STACK · LICENSE (MIT) · AI Convergence Measurement essay

## Tests + quality

- **101 tests** (pytest, Python 3.10–3.13 matrix)
- Zero runtime dependencies (stdlib + dev tools only)
- CI: GitHub Actions matrix on push/PR
- Secret scanning in CI (TruffleHog + Iron Curtain custom patterns)
- Dependabot for actions + pip dev-deps

## Unreleased

_No changes yet._

## v0.2.0 — 2026-05-14

Since v0.1.0:
- `lumina.memory_score` module + CLI
- `/braintrust` polymath panel command
- `/convergence` AI-measurement command + essay
- SECURITY.md
- CI portability fix (PR #7): test paths no longer hardcoded to a developer cwd
- Dependabot bumps: pytest ≥9.0.3, actions/checkout@v6, actions/setup-python@v6
- Test count grew from 67 to 100

## Cadence + provenance

This project is the curated public extract of an internal Lumina workspace at `mlesnews/lumina-premium`. Public commits batch every 2–6 weeks when an internal piece reaches generic + reusable + dependency-free shape. Silent periods in the public commit log reflect upstream consolidation cycles, not abandonment.

## What is NOT in this public repo

Prior versions of this file claimed HUD/LCARS, Life-Domain scanner, Apple Watch hooks, event bus, LLM routing, ChromaDB RAG, and multi-agent governance. **Those modules live in the internal workspace.** They are not part of `lumina-oss`. If/when they reach extractable shape, they will land here with a corresponding CHANGELOG entry. Until then, this STATUS reflects only what is currently in the public tree.

## Contact

See [README.md](README.md) and [CONTRIBUTING.md](CONTRIBUTING.md) for fork-based contribution workflow.
