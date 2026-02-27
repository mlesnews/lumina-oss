# Lumina AIOS Architecture

## Design Philosophy

Lumina AIOS is an AI-native runtime framework — not an operating system kernel. It provides OS-like primitives (processes, memory, health monitoring, safety) implemented in Python for AI workflow orchestration.

The analogy: SteamOS didn't replace Linux. It's a layer that makes gaming primary. Lumina AIOS is a layer on top of any OS that makes AI workflows primary.

## Core Abstractions

### Molecules (Process Model)

The fundamental unit of work. Every workflow is a molecule with four phases:

```
Trigger → Stopper Check → Action → Exit Handler
```

- **Trigger**: Condition that starts execution (returns bool)
- **Stopper**: Safety check that can halt before action runs
- **Action**: The actual work
- **Exit Handler**: Cleanup and result packaging

Molecules are composable — a MoleculeRunner evaluates multiple molecules against the same context.

### Memory Manager

Multi-tier knowledge storage with explicit priority:

```
CRITICAL (5) → Never auto-evicted
HIGH (4)     → Evicted only under extreme pressure
MEDIUM (3)   → Standard working memory
LOW (2)      → Evicted when space needed
TEMPORARY (1)→ Short-lived, first to evict
```

Features: TTL-based expiration, LRU eviction within tiers, thread-safe.

### Health Aggregator

N-dimensional weighted health scoring:

```
Score = Σ (dimension_score × dimension_weight) × 100
```

Each dimension is scored 0.0-1.0 independently by pluggable scorer functions. Weights must sum to 1.0. Thresholds map score ranges to labels.

### Circuit Breaker

5-level fail-closed state machine:

```
GREEN → YELLOW → ORANGE → RED → BLACK
  ↑                                 ↑
normal                        emergency
```

- Defaults to YELLOW on startup (fail-closed)
- Checks metrics against thresholds from BLACK down to YELLOW
- State persisted to JSON file for crash recovery
- `can_proceed()` / `is_halted()` for quick status checks

### Quality Gatekeeper

Spectrum-based audit with color precedence:

```
RED (5) > ORANGE (4) > CYAN (3) > BLUE (2) > GREY (1) > GREEN (0)
```

Pluggable checks return finding lists. The overall status is the highest severity found.

### Decisioning Engine

Context-score threshold gate:

```
if context_score >= threshold:
    PROCEED (autonomous)
else:
    ASK (needs human)
```

Accumulates context entries with weights, computes relevance scores via keyword overlap, and decides whether the system has enough information to act autonomously.

## Agent Multiplier Architecture

The framework is designed for a 1:10:100 agent hierarchy:

```
1 Orchestrator (Opus)
├── 10 Specialist Agents (Haiku/Sonnet)
│   ├── 10 Sub-agents each
│   └── ...
└── Total: ~100 workers, most on free/local inference
```

Each agent gets the same primitives: circuit breakers for safety, health scoring for monitoring, molecules for workflow, memory for state.

## Data Flow

```
External Input
     │
     ▼
┌─────────┐     ┌──────────┐     ┌──────────┐
│  Kernel  │────▶│ Decision │────▶│ Molecule │
│ (Route)  │     │ (Gate)   │     │ (Execute)│
└─────────┘     └──────────┘     └──────────┘
     │                                  │
     ▼                                  ▼
┌─────────┐     ┌──────────┐     ┌──────────┐
│ Context  │     │ Circuit  │     │ Health   │
│ Matrix   │     │ Breaker  │     │ Aggreg.  │
│ (Intel)  │     │ (Safety) │     │ (Monitor)│
└─────────┘     └──────────┘     └──────────┘
     │                                  │
     └──────────────┬───────────────────┘
                    ▼
              ┌──────────┐
              │  Memory  │
              │ Manager  │
              └──────────┘
```

## Extension Points

1. **Custom Molecules**: Define trigger/action/stopper/exit for any workflow
2. **Health Dimensions**: Add weighted dimensions to HealthAggregator
3. **Circuit Breaker Thresholds**: Custom metrics and levels
4. **Gatekeeper Checks**: Register check functions at any color level
5. **Pattern DB**: Store and track efficacy of reusable patterns
6. **Context Matrix Sources**: Ingest from any source (sessions, APIs, files)

## Zero-Dependency Design

Every module uses Python stdlib only. No pip install required beyond the package itself. This ensures:
- Runs anywhere Python 3.10+ runs
- No supply chain risk
- No version conflicts
- Deploys in seconds
