#!/usr/bin/env python3
"""
Use Local LLM to evaluate and recommend Cursor IDE recycle
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from cursor_intelligent_warm_recycle import CursorIntelligentWarmRecycle, RecycleReason

print('='*60)
print('🔄 Cursor Intelligent Warm Recycle - LLM Decision')
print('='*60)
print()

# Initialize
recycler = CursorIntelligentWarmRecycle()

# Check current state
print('📊 Current Cursor State:')
decision = recycler.should_recycle()
print(f'   Should Recycle: {decision.should_recycle}')
print(f'   Reason: {decision.reason.value}')
print(f'   Urgency: {decision.urgency}')
print()

# Get process info
processes = recycler.find_cursor_processes()
total_memory = sum(p.memory_mb for p in processes)
avg_cpu = sum(p.cpu_percent for p in processes) / max(1, len(processes))

print(f'📋 Cursor Processes: {len(processes)} found')
print(f'   Total Memory: {total_memory:.1f}MB')
print(f'   Avg CPU: {avg_cpu:.1f}%')
print()

for p in processes[:5]:  # Show first 5
    print(f'   - PID {p.pid}: Status={p.status}')
    print(f'     Memory: {p.memory_mb:.1f}MB, CPU: {p.cpu_percent:.1f}%, Threads: {p.threads}')
print()

# Consult Local LLM via Ollama API (ULTRON cluster - qwen2.5:72b)
print('🤖 Consulting ULTRON LLM (Ollama qwen2.5:72b)...')
print()

try:
    import requests
    import json as json_lib

    prompt = f"""You are an expert system administrator. Based on the following metrics, should the Cursor IDE be warm recycled (gracefully restarted)?

Current State:
- Process Count: {len(processes)}
- Total Memory Usage: {total_memory:.1f}MB (threshold: 2048MB)
- Average CPU: {avg_cpu:.1f}% (threshold: 80%)
- Automated Decision: {decision.should_recycle}
- Reason: {decision.reason.value}
- Urgency: {decision.urgency}

Respond with a JSON object:
{{"recommend_recycle": true/false, "reason": "brief explanation", "urgency": "low/medium/high"}}
"""

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            'model': 'qwen2.5:72b',
            'prompt': prompt,
            'stream': False,
            'options': {'temperature': 0.3}
        },
        timeout=120
    )

    if response.status_code == 200:
        result = response.json()
        llm_response = result.get('response', 'No response')
        print('📝 LLM Analysis:')
        print(llm_response)
        print()
    else:
        print(f'   ⚠️  Ollama API error: {response.status_code}')
        print('   Using rule-based decision instead.')

except requests.exceptions.ConnectionError:
    print('   ⚠️  Ollama not running. Using rule-based decision.')
except Exception as e:
    print(f'   ⚠️  LLM error: {e}')
    print('   Using rule-based decision instead.')

# Final recommendation
print('='*60)
if decision.should_recycle:
    print('⚠️  RECOMMENDATION: Recycle Cursor IDE')
    print(f'   Reason: {decision.reason.value}')
    print(f'   Urgency: {decision.urgency}')
    print()
    print('   To execute:')
    print('   python scripts/python/cursor_intelligent_warm_recycle.py --recycle')
else:
    print('✅ RECOMMENDATION: No recycle needed')
    print('   Cursor is operating within healthy parameters.')
print('='*60)
