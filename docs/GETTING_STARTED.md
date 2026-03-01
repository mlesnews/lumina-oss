# Getting Started with Lumina AIOS

## Install

```bash
pip install lumina-aios
```

Or from source:

```bash
git clone https://github.com/mlesnews/lumina-oss.git
cd lumina-oss
pip install -e .
```

## 5-Minute Tour

### 1. Health Monitoring

Monitor any system across weighted dimensions:

```python
from lumina.aios import HealthAggregator

health = HealthAggregator(dimensions={
    "api": 0.4,
    "database": 0.3,
    "cache": 0.3,
})

health.score("api", 0.95, "p99=80ms, 0.1% errors")
health.score("database", 0.70, "slow queries detected")
health.score("cache", 0.85, "92% hit rate")

report = health.evaluate()
print(f"{report.score_pct:.1f}% [{report.label}]")
print(report.recommendation)
```

### 2. Circuit Breaker

Protect systems with automatic safety levels:

```python
from lumina.safety import CircuitBreaker, Level

cb = CircuitBreaker(thresholds={
    Level.YELLOW: {"latency_ms": 200},
    Level.RED: {"latency_ms": 1000},
})

# Check metrics every cycle
level, reason = cb.check({"latency_ms": 500})
if not cb.can_proceed():
    print(f"HALTED: {reason}")
```

### 3. Workflow Molecules

Define any repeatable workflow:

```python
from lumina.aios import Molecule, MoleculeRunner

backup_mol = Molecule(
    name="nightly_backup",
    trigger=lambda ctx: ctx.get("hour") == 3,
    action=lambda ctx: f"Backed up {ctx['db_name']}",
    stopper=lambda ctx: ctx.get("disk_full", False),
)

runner = MoleculeRunner()
result = runner.run(backup_mol, {"hour": 3, "db_name": "production"})
print(result.output)  # "Backed up production"
```

### 4. Secret Scanning

Detect leaked credentials in code or text:

```python
from lumina.safety import SecretScanner

scanner = SecretScanner()
findings = scanner.scan(open("config.yaml").read())
if findings:
    for f in findings:
        print(f"LEAK: {f['pattern_name']} — {f['match']}")
```

### 5. Claude Code Hooks

Copy hooks to your Claude Code installation:

```bash
mkdir -p ~/.claude/hooks
cp claude_code_hooks/compusec_guard.py ~/.claude/hooks/
cp claude_code_hooks/cost_tracker.py ~/.claude/hooks/
```

Add to `~/.claude/settings.json` (merge into existing `hooks` section):

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/compusec_guard.py",
            "timeout": 10
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python3 ~/.claude/hooks/cost_tracker.py",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

See `claude_code_hooks/settings_template.json` for the full configuration with all hooks.

## Next Steps

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design
- [CLAUDE_CODE_HOOKS.md](CLAUDE_CODE_HOOKS.md) — full hook guide
- `examples/` — runnable demos
