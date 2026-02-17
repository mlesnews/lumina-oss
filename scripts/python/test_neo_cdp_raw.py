#!/usr/bin/env python3
"""
Test Neo CDP Raw Commands
Test CDP commands directly to see what's happening
"""

import sys
import json
import requests
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

print("Testing Neo CDP Raw Commands...")
print("=" * 70)

# Connect to CDP
cdp_endpoint = "http://localhost:9222"
response = requests.get(f"{cdp_endpoint}/json", timeout=10)
if response.status_code != 200:
    print(f"❌ Failed to get CDP sessions: {response.status_code}")
    sys.exit(1)

sessions = response.json()
if not sessions:
    print("❌ No CDP sessions found")
    sys.exit(1)

# Get first session
session = sessions[0]
session_id = session["id"]
print(f"✅ Found session: {session.get('title', 'Unknown')}")
print(f"   ID: {session_id}")
print(f"   URL: {session.get('url', 'Unknown')}")
print("")

# Send CDP command directly
cdp_url = f"{cdp_endpoint}/json/runtime/evaluate"
payload = {
    "expression": "return 'Hello from CDP';",
    "returnByValue": True
}

print("Sending CDP command directly...")
print(f"   URL: {cdp_url}")
print(f"   Payload: {json.dumps(payload, indent=2)}")
print("")

# Try WebSocket if available
ws_url = session.get("webSocketDebuggerUrl")
if ws_url:
    print(f"WebSocket URL: {ws_url}")
    print("   (Would need websocket library to test)")
    print("")

# Try HTTP POST to session
session_url = f"{cdp_endpoint}/json/runtime/evaluate"
print(f"Trying HTTP POST to: {session_url}")
try:
    response = requests.post(
        session_url,
        json=payload,
        params={"sessionId": session_id},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:500]}")
except Exception as e:
    print(f"   Error: {e}")

print("")
print("=" * 70)
print("Checking Neo automation engine's cdp_command method...")

from neo_browser_automation_engine import NEOBrowserAutomationEngine
neo = NEOBrowserAutomationEngine(project_root)
if neo._connect_cdp():
    print("✅ Connected via engine")
    result = neo.cdp_command("Runtime.evaluate", {
        "expression": "return 'Test';",
        "returnByValue": True
    })
    print(f"   cdp_command result: {result}")
    print(f"   Type: {type(result)}")
    if isinstance(result, dict):
        print(f"   Keys: {list(result.keys())}")
