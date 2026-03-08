# /convergence — AI Capability Measurement

Track your AI's actual performance: boons (wins), banes (failures), and OEM ceiling (architectural limits).

See [AI Convergence Measurement](../docs/AI_CONVERGENCE_MEASUREMENT.md) for the full framework.

## Instructions

**Action:** $ARGUMENTS (if empty, show current session stats)

### Variation Detection

Parse the first word of $ARGUMENTS:

- **`boon [description]`** — Record a success (playbook hit, autonomous completion)
- **`bane [description]`** — Record a failure (auth spiral, hallucination, blind navigation)
- **`score`** — Calculate and display current hit rate + OEM ceiling
- **`trend`** — Show hit rate trend over recent sessions (if history exists)
- **(no argument)** — Summarize this session's boons and banes so far

### Recording a Boon

When the user says `/convergence boon [description]`:

```
✓ BOON recorded: [description]
  Type: [playbook_hit | autonomous_completion | pattern_reuse]
  Session total: X boons / Y banes (Z% hit rate)
```

### Recording a Bane

When the user says `/convergence bane [description]`:

```
✗ BANE recorded: [description]
  Type: [auth_spiral | blind_navigation | hallucination_loop | oem_limitation]
  Session total: X boons / Y banes (Z% hit rate)

  [If type is oem_limitation]: This is an architectural limit — mitigate, don't try to fix.
```

### Showing Score

```
@CONVERGENCE SCORE
==================
Session: [date]
Boons: X | Banes: Y | Hit Rate: Z%
OEM Ceiling: N% (irreducible floor)

Distance from Buzzwords:
  AGI: [your domain-specific hit rate — not general intelligence]
  Autonomous: [autonomous completions vs human interventions]
  Self-improving: [trend direction — improving, flat, or degrading]
```

## Behavioral Rules

- **Be honest** — the entire point is accurate measurement, not flattery
- **Classify OEM limitations separately** — these aren't failures, they're architecture. Track them but don't count against hit rate.
- **The trend matters more than any single score** — always show direction when history exists
- **No judgment on low scores** — measuring is the capability. A 50% hit rate that's accurately tracked is more valuable than a claimed 95% nobody verified.

## Storage

Store boon/bane records wherever works for your project:
- JSON file in your project (e.g., `data/convergence.json`)
- Database table
- Even just session notes

The format doesn't matter. The discipline of recording does.
