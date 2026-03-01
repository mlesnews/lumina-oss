# Lumina AIOS

**AI-native workflow primitives for any platform.**

Lumina AIOS is a Python framework that gives developers production-tested building blocks for AI-powered automation: circuit breakers, health monitoring, multi-tier memory, quality gates, cost tracking, and secret detection. Zero dependencies. Runs anywhere Python runs.

Built by [Cedarbrook Financial Services LLC](https://github.com/mlesnews) — veteran-owned, AI-first.

```bash
pip install lumina-aios
```

## What's Inside

### Core (`lumina.aios`)
| Module | What it does |
|--------|-------------|
| `kernel` | Intent processor — classify, route, execute, return structured results |
| `memory` | Multi-tier memory with TTL, eviction, and priority (CRITICAL through TEMPORARY) |
| `process` | Molecule model — trigger + action + stopper + exit lifecycle for any workflow |
| `health` | Weighted N-dimension health scoring with thresholds and trend detection |

### Safety (`lumina.safety`)
| Module | What it does |
|--------|-------------|
| `circuit_breaker` | 5-level state machine (GREEN-YELLOW-ORANGE-RED-BLACK), fail-closed by default |
| `budget_guard` | API cost monitor — OPERATIONAL/WARNING/HALT based on MTD burn rate |
| `secret_scanner` | Regex-based detection for API keys, tokens, private keys, JWTs |

### Workflow (`lumina.workflow`)
| Module | What it does |
|--------|-------------|
| `decisioning` | Context scoring + threshold gate — PROCEED or ASK |
| `troubleshooting` | `@troubleshoot` decorator with symptom collection and resolution tracking |
| `gatekeeper` | Spectrum quality gate (RED-ORANGE-CYAN-BLUE-GREY-GREEN) |
| `verifier` | Triple-verification — N independent checks, require consensus |

### Intel (`lumina.intel`)
| Module | What it does |
|--------|-------------|
| `context_matrix` | Multi-source knowledge aggregation with pattern extraction |
| `pattern_db` | JSON-backed pattern storage with efficacy tracking |

### Integrations (`lumina.integrations`)
| Module | What it does |
|--------|-------------|
| `wakatime` | WakaTime API client for coding statistics |
| `ticket_system` | JSON-backed ticket lifecycle management |

### Powertools (`lumina.powertools`)
| Module | What it does |
|--------|-------------|
| `statusline` | HUD status rendering — build compact, color-coded status bars |
| `hook_protocol` | Hook I/O parsing — stdin/stdout protocol for Claude Code hooks |
| `cost_analyzer` | Token usage analysis — parse JSONL cost logs, breakdown by model |

### Claude Code Hooks (`claude_code_hooks/`)
Drop-in hooks for [Claude Code](https://docs.anthropic.com/en/docs/claude-code):
| Hook | Type | What it does |
|------|------|-------------|
| `compusec_guard.py` | PreToolUse | Blocks secret exposure in CLI args and tool output |
| `cost_tracker.py` | PostToolUse | Logs token usage and USD cost to JSONL |
| `trace_track.py` | PreToolUse | Enforces MEMORY.md rules as active guardrails |
| `api_watchdog.py` | Stop | Detects API crashes, classifies errors, alerts on threshold |

## Quick Start

```python
from lumina.aios import HealthAggregator

# Create a health monitor with weighted dimensions
health = HealthAggregator(dimensions={
    "api_latency": 0.3,
    "error_rate": 0.3,
    "throughput": 0.2,
    "memory": 0.2,
})

health.score("api_latency", 0.85, "p99=120ms")
health.score("error_rate", 0.95, "0.5% errors")
health.score("throughput", 0.70, "850 req/s")
health.score("memory", 0.60, "75% utilization")

report = health.evaluate()
print(f"System: {report.score_pct:.1f}% [{report.label}]")
# System: 79.5% [DEGRADED]
print(report.recommendation)
# Focus on: memory (below 50%).
```

```python
from lumina.safety import CircuitBreaker, Level

# Safety circuit breaker with custom thresholds
cb = CircuitBreaker(thresholds={
    Level.YELLOW: {"error_rate": 0.05},
    Level.ORANGE: {"error_rate": 0.10},
    Level.RED: {"error_rate": 0.20},
})

level, reason = cb.check({"error_rate": 0.15})
print(f"{level.name}: {reason}")  # ORANGE: error_rate=0.1500 >= 0.1000
print(f"Can proceed: {cb.can_proceed()}")  # False
```

```python
from lumina.aios import Molecule, MoleculeRunner

# Define a workflow as a molecule
mol = Molecule(
    name="deploy_check",
    trigger=lambda ctx: ctx.get("branch") == "main",
    action=lambda ctx: f"Deploying {ctx['service']}",
    stopper=lambda ctx: ctx.get("frozen", False),
)

runner = MoleculeRunner()
result = runner.run(mol, {"branch": "main", "service": "api-v2"})
print(f"{result.state.name}: {result.output}")
# COMPLETED: Deploying api-v2
```

## Architecture

```
                    ┌──────────────────────┐
                    │     AIOS Kernel       │
                    │  Intent → Priority →  │
                    │  Handler → Result     │
                    └──────────┬───────────┘
                               │
              ┌────────────────┼────────────────┐
              │                │                 │
    ┌─────────▼──────┐ ┌──────▼───────┐ ┌──────▼───────┐
    │    Safety       │ │   Workflow    │ │    Intel      │
    │ Circuit Breaker │ │  Decisioning  │ │ Context Matrix│
    │ Budget Guard    │ │  Gatekeeper   │ │  Pattern DB   │
    │ Secret Scanner  │ │  Verifier     │ │               │
    └────────────────┘ └──────────────┘ └──────────────┘
              │                │                 │
              └────────────────┼────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │    Memory Manager     │
                    │ CRITICAL → TEMPORARY  │
                    │   TTL + Eviction      │
                    └──────────────────────┘
```

These are operating system primitives — they just happen to be written in Python instead of C:
- **Molecules** = processes (trigger - execute - exit)
- **Health Aggregator** = system monitor
- **Circuit Breaker** = safety kernel
- **Decisioning** = interrupt handler
- **Context Matrix** = I/O bus
- **Memory Manager** = memory management
- **Gatekeeper** = access control

## Why "AI Operating System"?

We're not building a kernel. We're building a layer.

Like Docker gave us containers on any OS, Lumina gives AI workflows on any OS. Like SteamOS didn't replace Linux — it's a layer that makes gaming primary — Lumina AIOS is a layer that makes AI workflows primary.

Every module is extracted from a production system that's been running 24/7. The trading system is the reference implementation; the framework is the product.

## Development

```bash
git clone https://github.com/mlesnews/lumina-oss.git
cd lumina-oss
pip install -e ".[dev]"
pytest tests/ -v
```

**67 tests, 0 dependencies, Python 3.10+.**

## Project Structure

```
lumina-oss/
├── lumina/                  # pip package
│   ├── aios/                # AI OS kernel, memory, process, health
│   ├── safety/              # Circuit breaker, budget guard, secret scanner
│   ├── workflow/            # Decisioning, troubleshooting, gatekeeper, verifier
│   ├── intel/               # Context matrix, pattern DB
│   ├── integrations/        # WakaTime, ticket system
│   └── powertools/          # Statusline, hook protocol, cost analyzer
├── claude_code_hooks/       # Drop-in hooks for Claude Code
├── examples/                # Runnable demos
├── docs/                    # Architecture and guides
└── tests/                   # Test suite
```

## License

MIT License — see [LICENSE](LICENSE)

## Premium

Advanced trading, strategy optimization, and financial intelligence: [Lumina Premium](https://github.com/mlesnews/lumina-premium) (private).
