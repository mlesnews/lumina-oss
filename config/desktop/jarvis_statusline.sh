#!/bin/bash
# ── JARVIS Statusline — Iron Man HUD for Claude Code CLI ──
# Reads stdin JSON from Claude Code, enriches with live Lumina state.
# Must be FAST (<100ms) — file reads only, no network calls.

set -euo pipefail

# Read Claude Code's JSON input
INPUT=$(cat)

# ── Extract Claude Code state ────────────────────────────
MODEL=$(echo "$INPUT" | jq -r '.model.display_name // "Claude"')
CWD=$(echo "$INPUT" | jq -r '.workspace.current_dir // "~"')
REMAINING=$(echo "$INPUT" | jq -r '.context_window.remaining_percentage // "?"')
REMAINING_INT=$(echo "$REMAINING" | cut -d. -f1 2>/dev/null || echo "0")

# Compact path (last 2 segments)
COMPACT_PATH=$(echo "$CWD" | awk -F/ '{if(NF>2) print $(NF-1)"/"$NF; else print $0}')

# ── JARVIS Mode ──────────────────────────────────────────
JARVIS_MODE="OFF"
[ -f "$HOME/.claude/jarvis_mode.txt" ] && JARVIS_MODE=$(head -1 "$HOME/.claude/jarvis_mode.txt" | tr -d '[:space:]')

# ── FPCON (from OSINT) ───────────────────────────────────
OSINT_FILE="$HOME/lumina/docker/cluster-ui/data/trading/osint/last_assessment.json"
FPCON="—"
THREAT_PCT="0"
if [ -f "$OSINT_FILE" ]; then
    FPCON=$(jq -r '.threat_level_name // "—"' "$OSINT_FILE" 2>/dev/null || echo "—")
    THREAT_PCT=$(jq -r '(.composite_threat_score // 0) * 100 | floor' "$OSINT_FILE" 2>/dev/null || echo "0")
fi

# ── Circuit Breaker ──────────────────────────────────────
CB_FILE="$HOME/lumina/docker/cluster-ui/data/trading/state/circuit_breaker.json"
CB="GREEN"
if [ -f "$CB_FILE" ]; then
    CB_RAW=$(jq -r '.level // "operational"' "$CB_FILE" 2>/dev/null || echo "operational")
    case "$CB_RAW" in
        operational) CB="GREEN" ;;
        caution) CB="YELLOW" ;;
        restricted) CB="ORANGE" ;;
        halted) CB="RED" ;;
        emergency) CB="BLACK" ;;
        *) CB="GREEN" ;;
    esac
fi

# ── Emergency Stop ───────────────────────────────────────
ESTOP=""
[ -f "$HOME/lumina/docker/cluster-ui/data/trading/EMERGENCY_STOP" ] && ESTOP=" ⛔"

# ── Active Process Count ─────────────────────────────────
PROC_COUNT=$(ps aux 2>/dev/null | grep -cE "(run_trading|run_intel|bitnet_api|ironman_animated|ollama serve)" || echo "0")

# ── Context Window Color ─────────────────────────────────
CTX_COLOR=""
CTX_RESET=""
if [ "$REMAINING_INT" -gt 50 ] 2>/dev/null; then
    CTX_COLOR="\033[92m"  # Green
elif [ "$REMAINING_INT" -gt 20 ] 2>/dev/null; then
    CTX_COLOR="\033[93m"  # Yellow
else
    CTX_COLOR="\033[91m"  # Red
fi
CTX_RESET="\033[0m"

# ── FPCON Color ──────────────────────────────────────────
FPCON_COLOR="\033[96m"  # Cyan default
case "$FPCON" in
    DELTA)   FPCON_COLOR="\033[91m\033[1m" ;;
    CHARLIE) FPCON_COLOR="\033[91m" ;;
    BRAVO)   FPCON_COLOR="\033[93m" ;;
    ALPHA)   FPCON_COLOR="\033[92m" ;;
    NORMAL)  FPCON_COLOR="\033[96m" ;;
esac

# ── Circuit Breaker Color ────────────────────────────────
CB_COLOR="\033[92m"  # Green default
case "$CB" in
    GREEN)  CB_COLOR="\033[92m" ;;
    YELLOW) CB_COLOR="\033[93m" ;;
    ORANGE) CB_COLOR="\033[93m" ;;
    RED)    CB_COLOR="\033[91m" ;;
    BLACK)  CB_COLOR="\033[91m\033[1m" ;;
esac

# ── JARVIS Mode Color ───────────────────────────────────
JM_COLOR="\033[92m"
[ "$JARVIS_MODE" = "OFF" ] && JM_COLOR="\033[90m"

# ── Render ───────────────────────────────────────────────
DIM="\033[2m"
BOLD="\033[1m"
CYAN="\033[96m"
RST="\033[0m"

printf "${CYAN}◉${RST} ${BOLD}JARVIS${RST}:${JM_COLOR}${JARVIS_MODE}${RST}"
printf " ${DIM}│${RST} ${FPCON_COLOR}FPCON:${FPCON}${RST}"
printf " ${DIM}│${RST} ${CB_COLOR}CB:${CB}${RST}"
printf " ${DIM}│${RST} ${DIM}⚙${RST}${PROC_COUNT}"
printf " ${DIM}│${RST} ${DIM}${COMPACT_PATH}${RST}"
printf " ${DIM}│${RST} CTX:${CTX_COLOR}${REMAINING_INT}%%${RST}"
printf " ${DIM}│${RST} ${DIM}${MODEL}${RST}"
printf "${ESTOP}"
printf "\n"
