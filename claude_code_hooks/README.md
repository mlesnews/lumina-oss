# Claude Code Hooks Collection

Drop-in hooks for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) that add safety, cost tracking, session continuity, and developer productivity to your AI coding sessions.

## Hooks

| Hook | Type | What it does |
|------|------|-------------|
| `compusec_guard.py` | PreToolUse | Blocks commands that would expose secrets in CLI args or tool output |
| `trace_track.py` | PreToolUse | Reads rules from MEMORY.md and enforces them as active guardrails |
| `cost_tracker.py` | PostToolUse | Logs every tool call with token usage and estimated USD cost to JSONL |
| `secrets_redactor.py` | PostToolUse | Scans tool output for leaked secrets (API keys, JWTs, private keys) |
| `wakatime_heartbeat.py` | PostToolUse | Sends WakaTime coding heartbeats for AI-assisted development tracking |
| `fast_mode_tracker.py` | UserPromptSubmit | Tracks /fast toggle state, recommends boost on heavy throughput |
| `precompact_snapshot.py` | PreCompact | Saves git state + session context before context compaction |
| `api_watchdog.py` | Stop | Detects API errors, classifies crash types, alerts on failures |
| `session_compiler.py` | Stop | Compiles memory files into recovery batons for session continuity |
| `autoboost.sh` | Daemon | Auto-toggles /fast mode based on sustained tok/s throughput |

## Quick Start

```bash
# Copy all hooks
mkdir -p ~/.claude/hooks
cp claude_code_hooks/*.py ~/.claude/hooks/
cp claude_code_hooks/autoboost.sh ~/.claude/hooks/
chmod +x ~/.claude/hooks/autoboost.sh

# Copy and customize settings template
# Then merge relevant sections into ~/.claude/settings.json
cat claude_code_hooks/settings_template.json
```

## Installation

### 1. Copy hooks

```bash
cp claude_code_hooks/*.py ~/.claude/hooks/
```

### 2. Register in settings.json

Add to `~/.claude/settings.json` (see `settings_template.json` for full example):

```json
{
  "hooks": {
    "PreToolUse": [
      {"matcher": "Bash|Edit|Write", "command": "python3 ~/.claude/hooks/compusec_guard.py"},
      {"matcher": "Bash|Edit|Write", "command": "python3 ~/.claude/hooks/trace_track.py"}
    ],
    "PostToolUse": [
      {"command": "python3 ~/.claude/hooks/cost_tracker.py"},
      {"matcher": "Bash|Read|Grep", "command": "python3 ~/.claude/hooks/secrets_redactor.py"}
    ],
    "UserPromptSubmit": [
      {"command": "python3 ~/.claude/hooks/fast_mode_tracker.py"}
    ],
    "PreCompact": [
      {"command": "python3 ~/.claude/hooks/precompact_snapshot.py"}
    ],
    "Stop": [
      {"command": "python3 ~/.claude/hooks/api_watchdog.py"},
      {"command": "python3 ~/.claude/hooks/session_compiler.py"}
    ]
  }
}
```

### 3. Start the autoboost daemon (optional)

```bash
~/.claude/hooks/autoboost.sh start
```

## Hook Details

### compusec_guard.py (PreToolUse)
Blocks dangerous commands that would leak secrets. Edit `DANGEROUS_PATTERNS` and `SAFE_PATTERNS` to customize.

### trace_track.py (PreToolUse)
Reads your `MEMORY.md` `## CRITICAL RULES` section and blocks tool calls that violate them. Your rules become active guardrails.

### cost_tracker.py (PostToolUse)
- **Log**: `~/logs/claude-costs/cost_log.jsonl`
- **Budget**: Edit `DAILY_BUDGET` (default: $0.67/day = $20/month)
- **Pricing**: Edit `PRICING` dict for your model tier
- Reads real token counts from transcript when available, falls back to estimation

### secrets_redactor.py (PostToolUse)
Last line of defense. Scans tool output for 20+ secret patterns (GitHub PATs, AWS keys, JWTs, private keys, DB connection strings). Logs findings to `~/logs/security/secrets_audit.jsonl`.

### wakatime_heartbeat.py (PostToolUse)
Sends heartbeats to WakaTime for coding activity tracking. Requires WakaTime CLI (`~/.wakatime/wakatime-cli`).

### fast_mode_tracker.py (UserPromptSubmit)
- **State**: `~/.claude/fast_mode_state.json`
- Detects `/fast` command and toggles state
- Monitors tok/s from cost log and recommends boost when sustained heavy load (50+ tok/s for 3+ entries)

### precompact_snapshot.py (PreCompact)
Saves git branch, status, recent commits, and session ID before context compaction. Snapshots at `~/.claude/snapshots/` (keeps last 10).

### api_watchdog.py (Stop)
- **Alert threshold**: 3 failures in 30 minutes
- **Telegram**: Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` env vars for alerts

### session_compiler.py (Stop)
Compiles all `~/.claude/projects/*/memory/*.md` files into a single JSON baton. Saves to `~/.claude/session_batons/` (keeps last 10). Enables session continuity across restarts.

### autoboost.sh (Daemon)
Background daemon that monitors cost log throughput and auto-toggles `/fast` mode. Configure thresholds at the top of the script.

## Hook Protocol

All hooks follow the same protocol:

```
stdin  → JSON (tool_name, tool_input, tool_output, session_id, model, etc.)
stdout → JSON messages (systemMessage, result, etc.)
stderr → Human-readable warnings (shown in Claude Code)
exit 0 → Allow the operation
exit 2 → Block the operation (PreToolUse only)
```

Use `lumina.powertools.HookIO` for a reusable implementation:

```python
from lumina.powertools import HookIO

io = HookIO.from_stdin()
if "rm -rf /" in io.command:
    io.block("Absolutely not.")
io.allow()
```

## Requirements

- Python 3.10+
- No pip dependencies (stdlib only)
- WakaTime CLI (optional, for `wakatime_heartbeat.py`)
