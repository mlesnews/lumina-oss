# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-03-01

### Added
- **AIOS Kernel** — intent processor with classify, route, execute, return lifecycle
- **Memory Manager** — multi-tier memory (CRITICAL through TEMPORARY) with TTL and eviction
- **Molecule Process Model** — trigger + action + stopper + exit lifecycle for workflows
- **Health Aggregator** — weighted N-dimension health scoring with trend detection
- **Circuit Breaker** — 5-level state machine (GREEN-YELLOW-ORANGE-RED-BLACK)
- **Budget Guard** — API cost monitor with OPERATIONAL/WARNING/HALT states
- **Secret Scanner** — regex-based detection for API keys, tokens, private keys, JWTs
- **Decisioning Engine** — context scoring with threshold gates
- **Troubleshooting Decorator** — symptom collection and resolution tracking
- **Gatekeeper** — spectrum quality gate (RED-ORANGE-CYAN-BLUE-GREY-GREEN)
- **Verifier** — triple-verification with N independent checks and consensus
- **Context Matrix** — multi-source knowledge aggregation
- **Pattern DB** — JSON-backed pattern storage with efficacy tracking
- **WakaTime Integration** — coding statistics API client
- **Ticket System** — JSON-backed ticket lifecycle management
- **Statusline Renderer** — compact, color-coded HUD status bars
- **Hook Protocol** — stdin/stdout I/O parsing for Claude Code hooks
- **Cost Analyzer** — token usage analysis from JSONL cost logs
- **Claude Code Hooks** — 10 drop-in hooks (compusec guard, cost tracker, trace track, API watchdog, secrets redactor, fast mode tracker, precompact snapshot, session compiler, WakaTime heartbeat, autoboost daemon)
- **Claude Code Command Templates** — portable slash commands (brainstorm, redact, snapshot, save)
- CI/CD with pytest matrix (Python 3.10-3.13)
- Secret scanning (TruffleHog + Iron Curtain custom patterns)
- Issue templates, PR template, Dependabot
- SECURITY.md, CONTRIBUTING.md
- 67+ tests, zero dependencies

[0.1.0]: https://github.com/mlesnews/lumina-oss/releases/tag/v0.1.0
