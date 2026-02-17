#!/usr/bin/env python3
"""
Test WebSocket CDP Connection
"""

import sys
import json
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    print("❌ websocket library not available")
    print("   Install with: pip install websocket-client")
    sys.exit(1)

import requests

print("Testing WebSocket CDP Connection...")
print("=" * 70)

# Get CDP sessions
cdp_endpoint = "http://localhost:9222"
response = requests.get(f"{cdp_endpoint}/json", timeout=10)
sessions = response.json()

# Find ProtonPass session
protonpass_session = None
for session in sessions:
    title = (session.get("title", "") or "").lower()
    if "proton pass" in title or "proton" in title:
        protonpass_session = session
        break

if not protonpass_session:
    print("❌ ProtonPass session not found")
    sys.exit(1)

print(f"✅ Found session: {protonpass_session.get('title', 'Unknown')}")
ws_url = protonpass_session.get("webSocketDebuggerUrl")
print(f"   WebSocket URL: {ws_url}")
print("")

# Connect via WebSocket
print("Connecting via WebSocket...")
try:
    ws = websocket.create_connection(ws_url, timeout=10)
    print("✅ WebSocket connected")
    print("")

    # Send Runtime.evaluate command
    command_id = 12345
    payload = {
        "id": command_id,
        "method": "Runtime.evaluate",
        "params": {
            "expression": "return 'Hello from WebSocket CDP';",
            "returnByValue": True
        }
    }

    print(f"Sending command: {json.dumps(payload, indent=2)}")
    ws.send(json.dumps(payload))
    print("")

    # Wait for response
    print("Waiting for response...")
    timeout = time.time() + 10
    while time.time() < timeout:
        response_text = ws.recv()
        response_data = json.loads(response_text)
        print(f"Received: {json.dumps(response_data, indent=2)}")

        if response_data.get("id") == command_id:
            print("✅ Got matching response!")
            if "result" in response_data:
                result = response_data["result"]
                if "value" in result:
                    print(f"   Value: {result['value']}")
            break
        elif "method" in response_data:
            print(f"   (Event: {response_data.get('method')})")
            continue

    ws.close()
    print("")
    print("✅ WebSocket test complete")

except Exception as e:
    print(f"❌ WebSocket error: {e}")
    import traceback
    traceback.print_exc()
