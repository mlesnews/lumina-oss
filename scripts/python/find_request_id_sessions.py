#!/usr/bin/env python3
"""
Find sessions containing specific request IDs
"""

import json
import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Load analysis
analysis_file = project_root / "data" / "syphon" / "cursor_agent_chat" / "cursor_agent_chat_analysis_20260109_032821.json"

if not analysis_file.exists():
    print(f"❌ Analysis file not found: {analysis_file}")
    sys.exit(1)

with open(analysis_file, "r", encoding="utf-8") as f:
    data = json.load(f)

# Request IDs to find
req_ids = [
    "40f54051-33f7-474c-851d-ad85cbb29218",
    "1847f13b-6d51-4ffd-949f-9ba946974e94"
]

print("=" * 80)
print("🔍 FINDING SESSIONS WITH REQUEST IDs")
print("=" * 80)
print()

# Find sessions with these request IDs
sessions_with_ids = []
for session in data.get("session_intelligence", []):
    session_req_ids = session.get("request_ids", [])
    for req_id in req_ids:
        if req_id in session_req_ids:
            sessions_with_ids.append({
                "session_id": session.get("session_id"),
                "request_id": req_id,
                "file_path": session.get("file_path"),
                "agents": session.get("agents", []),
                "errors": len(session.get("errors", [])),
                "completions": len(session.get("completions", []))
            })

if sessions_with_ids:
    print(f"✅ Found {len(sessions_with_ids)} sessions with requested IDs:")
    print()
    for item in sessions_with_ids:
        print(f"   Request ID: {item['request_id']}")
        print(f"   Session: {item['session_id']}")
        print(f"   File: {item['file_path']}")
        print(f"   Agents: {', '.join(item['agents'][:5])}")
        print(f"   Errors: {item['errors']}")
        print(f"   Completions: {item['completions']}")
        print()
else:
    print("⚠️  No sessions found with these request IDs in session intelligence")
    print("   (They are in the aggregated list but may not be in individual sessions)")
    print()

# Check aggregated list
print("=" * 80)
print("📊 REQUEST ID STATUS IN AGGREGATED DATA")
print("=" * 80)
print()

aggregated_ids = data.get("aggregated", {}).get("request_ids", [])
for req_id in req_ids:
    if req_id in aggregated_ids:
        print(f"   ✅ {req_id} - FOUND in aggregated request IDs")
    else:
        print(f"   ❌ {req_id} - NOT FOUND")

print()
print("=" * 80)
