#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# Autoboost Daemon — Auto-toggle /fast mode based on tok/s
#
# Monitors the cost log for sustained high throughput and
# automatically toggles fast mode by injecting /fast into
# the active terminal.
#
# Usage:
#   ./autoboost.sh start   # Start daemon (background)
#   ./autoboost.sh stop    # Stop daemon
#   ./autoboost.sh status  # Check if running
#
# Config: Edit constants below
# Requires: cost_tracker.py hook writing to COST_LOG
# ──────────────────────────────────────────────────────────────
set -euo pipefail

COST_LOG="${HOME}/logs/claude-costs/cost_log.jsonl"
STATE_FILE="${HOME}/.claude/fast_mode_state.json"
PID_FILE="/tmp/lumina_autoboost.pid"
LOG_FILE="${HOME}/logs/autoboost.log"

# Thresholds
POLL_INTERVAL=10        # seconds between checks
HIGH_TPS_THRESHOLD=60   # tok/s above this = heavy
CONSECUTIVE_NEEDED=3    # consecutive heavy entries before toggle
IDLE_THRESHOLD=30       # seconds of 0 tok/s before disabling
COOLDOWN=60             # seconds between toggle attempts

log() {
    echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" >> "$LOG_FILE" 2>/dev/null
}

get_fast_mode() {
    if [ -f "$STATE_FILE" ]; then
        python3 -c "import json; print(json.load(open('$STATE_FILE')).get('fast_mode', False))" 2>/dev/null || echo "False"
    else
        echo "False"
    fi
}

get_recent_tps() {
    # Return last N tok_per_sec values from cost log
    if [ ! -f "$COST_LOG" ]; then
        echo "0"
        return
    fi
    tail -n "$CONSECUTIVE_NEEDED" "$COST_LOG" 2>/dev/null | \
        python3 -c "
import sys, json
tps = []
for line in sys.stdin:
    try:
        e = json.loads(line.strip())
        t = e.get('tok_per_sec', 0)
        if t > 0:
            tps.append(t)
    except:
        pass
print(' '.join(str(t) for t in tps[-$CONSECUTIVE_NEEDED:]))
" 2>/dev/null || echo "0"
}

inject_fast() {
    # Platform-specific: inject /fast into terminal
    # Override this function for your platform
    log "Would inject /fast (override inject_fast for your platform)"
}

daemon_loop() {
    log "Autoboost daemon started (PID $$)"
    echo $$ > "$PID_FILE"
    local last_toggle=0

    while true; do
        sleep "$POLL_INTERVAL"

        now=$(date +%s)
        elapsed=$((now - last_toggle))
        if [ "$elapsed" -lt "$COOLDOWN" ]; then
            continue
        fi

        fast_mode=$(get_fast_mode)
        tps_values=$(get_recent_tps)

        if [ -z "$tps_values" ] || [ "$tps_values" = "0" ]; then
            # No data or idle
            if [ "$fast_mode" = "True" ]; then
                log "Idle detected, would disable fast mode"
                # inject_fast  # Uncomment to auto-disable
            fi
            continue
        fi

        # Check if all recent values are above threshold
        all_high=true
        for tps in $tps_values; do
            if python3 -c "exit(0 if $tps >= $HIGH_TPS_THRESHOLD else 1)" 2>/dev/null; then
                :
            else
                all_high=false
                break
            fi
        done

        if $all_high && [ "$fast_mode" = "False" ]; then
            log "Heavy load detected (all $tps_values >= $HIGH_TPS_THRESHOLD), recommending /fast"
            inject_fast
            last_toggle=$now
        fi
    done
}

case "${1:-status}" in
    start)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "Autoboost already running (PID $(cat "$PID_FILE"))"
            exit 0
        fi
        mkdir -p "$(dirname "$LOG_FILE")"
        daemon_loop &
        echo "Autoboost daemon started (PID $!)"
        ;;
    stop)
        if [ -f "$PID_FILE" ]; then
            pid=$(cat "$PID_FILE")
            kill "$pid" 2>/dev/null && echo "Stopped autoboost (PID $pid)" || echo "Not running"
            rm -f "$PID_FILE"
        else
            echo "No PID file found"
        fi
        ;;
    status)
        if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
            echo "Running (PID $(cat "$PID_FILE"))"
            echo "Fast mode: $(get_fast_mode)"
        else
            echo "Not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|status}"
        exit 1
        ;;
esac
