# Claude Code Hooks Guide

## Overview

Claude Code hooks are scripts that run automatically before or after tool calls. They intercept tool inputs/outputs and can approve (exit 0) or block (exit 2) actions.

Lumina AIOS ships four production-tested hooks:

| Hook | Type | Purpose |
|------|------|---------|
| `compusec_guard.py` | PreToolUse | Block secret exposure |
| `cost_tracker.py` | PostToolUse | Track token usage and cost |
| `trace_track.py` | PreToolUse | Enforce rules from MEMORY.md |
| `api_watchdog.py` | Stop | Detect API crashes and alert |

## Installation

```bash
# Copy hooks
mkdir -p ~/.claude/hooks
cp claude_code_hooks/*.py ~/.claude/hooks/

# Add to settings
cat >> ~/.claude/settings.json << 'EOF'
{
  "hooks": {
    "PreToolUse": [
      {"command": "python3 ~/.claude/hooks/compusec_guard.py"},
      {"command": "python3 ~/.claude/hooks/trace_track.py"}
    ],
    "PostToolUse": [
      {"command": "python3 ~/.claude/hooks/cost_tracker.py"}
    ],
    "Stop": [
      {"command": "python3 ~/.claude/hooks/api_watchdog.py"}
    ]
  }
}
EOF
```

## Hook Details

### compusec_guard.py (Secret Leak Prevention)

**What it blocks:**
- Passwords/tokens in CLI arguments (`--password=abc123`)
- Vault secrets piped to display commands (`az keyvault show | cat`)
- Direct echo of secret variables (`echo $API_KEY`)
- Clipboard reads without safe pipe targets
- Writing secrets to temp files

**What it allows:**
- Vault secrets piped to assignment (`$(az keyvault ...)`)
- Length checks on secrets (`az keyvault ... | wc -c`)
- Clipboard to vault pipeline (`Get-Clipboard | az keyvault set`)

**Fail mode:** Closed (blocks on error).

### cost_tracker.py (Token Cost Logger)

**Output:** `~/logs/claude-costs/cost_log.jsonl`

Each line:
```json
{
  "timestamp": "2026-02-26T12:00:00Z",
  "tool": "Bash",
  "model": "claude-opus-4-6",
  "tokens_input": 1500,
  "tokens_output": 200,
  "cache_read": 0,
  "cache_create": 0,
  "cost_usd": 0.037500,
  "session_id": "abc123"
}
```

**Token source:** Reads real usage from Claude Code transcript JSONL. Falls back to character estimation if transcript unavailable.

**Budget alert:** Prints warning to stderr when daily spend exceeds 80% of budget.

### trace_track.py (Rule Enforcer)

Reads rules from your MEMORY.md `## CRITICAL RULES` section and blocks violations.

**Built-in rules:**
- `NO_ENV_SECRETS`: Block writing secrets to .env files
- `VAULT_ONLY`: No hardcoded tokens in docker-compose files

**Adding custom rules:** Edit the `GUARDRAIL_RULES` list in the script.

**Audit trail:** `~/logs/trace-track/audit.jsonl`

**Fail mode:** Open (allows on error — compusec_guard handles fail-closed).

### api_watchdog.py (Crash Detector)

**Classifications:**
- `clean_exit`: Normal session end
- `api_500`: Anthropic server error
- `timeout`: Request timed out
- `rate_limit`: 429 response
- `overloaded`: 529 response
- `unknown_error`: Unclassified error

**Alert:** Sends Telegram message when 3+ failures occur in 30 minutes. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` environment variables.

**Log:** `~/logs/claude-api-watchdog/api_errors.jsonl`

## Hook Protocol

Hooks receive JSON on stdin:
```json
{
  "tool_name": "Bash",
  "tool_input": {"command": "echo hello"},
  "tool_output": "",
  "model": "claude-opus-4-6",
  "session_id": "...",
  "transcript_path": "..."
}
```

Exit codes:
- `0`: Approve the tool call
- `2`: Block the tool call (message on stderr shown to user)
