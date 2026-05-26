# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- **`lumina.memory_score.score_freshness`** — replaced a hardcoded reference date (`2026-03-14`) and 30-day-month approximation with `datetime.date.today()` and real calendar arithmetic, so freshness scores reflect actual age instead of drifting after the reference date. Regression test added.
- **STATUS.md** — refreshed header (date + current version), cut the unreleased queue into a shipped v0.2.0 section, and corrected the upstream workspace reference (`mlesnews/lumina` → `mlesnews/lumina-premium`) to match `README.md` and `SECURITY.md`.
- **SECURITY.md** — added `0.2.x` to the Supported Versions table (was still listing only `0.1.x`).
- **Doc drift** (1ebbb50): `lumina/__init__.py` `__version__` bumped 0.1.0 → 0.2.0 to match `pyproject.toml`; PR template test count 67+ → 100; `docs/CLAUDE_CODE_HOOKS.md` hook count 4 → 10 with all 10 hooks listed.

## [0.2.0] - 2026-05-14

### Added
- **`lumina.memory_score`** — 10-dimension MEMORY.md grader built on this framework's own `HealthAggregator` (eats its own cooking). Public API: `score_memory_file`, `score_memory_directory`, `MemoryScorer`. CLI entrypoint via `python -m lumina.memory_score`. Renders text, Markdown, or JSON. Dimensions: structure, completeness, conciseness, freshness, modularity, cross_referencing, actionability, coverage, platform_compliance, meta_awareness.
- **`docs/MEMORY_SCORE.md`** — full documentation of the scorer (CLI, programmatic API, the 10 dimensions, grading scale, architecture).
- **`examples/memory_scorer/demo.py`** — runnable programmatic example covering single-file, directory, custom weights, and all three output formats.
- **`/braintrust`** Claude Code command — polymath lifeline panel for cross-domain advisory.
- **`/convergence`** Claude Code command — AI measurement / distance-from-buzzwords assessment.
- **AI Convergence Measurement** essay in `docs/`.
- **SECURITY.md** — vulnerability disclosure policy.
- **`STATUS.md`** — current-state snapshot and v0.2.0 roadmap.

### Changed
- **README / STATUS / CONTRIBUTING** — test count updated from "67+" to reflect the current 100 tests.
- **CI** — Dependabot bumps: `pytest >=9.0.3`, `actions/checkout@v6`, `actions/setup-python@v6`.

### Fixed
- **CI portability** (#7) — removed a hardcoded developer cwd from the test suite so it runs in any CI runner / contributor environment.
- **Iron Curtain self-scan** — excluded `test_secret_scanner.py` (which intentionally contains synthetic secret patterns) from the pre-commit scanner.

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

[0.2.0]: https://github.com/mlesnews/lumina-oss/releases/tag/v0.2.0
[0.1.0]: https://github.com/mlesnews/lumina-oss/releases/tag/v0.1.0
