#!/usr/bin/env python3
"""
Test NEO Browser CDP Support
Check if NEO browser supports Chrome DevTools Protocol
#JARVIS #NEO #CDP #TEST
"""

import sys
from pathlib import Path
import time
import subprocess
import requests
import os

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

neo_exe = Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "Application" / "neo.exe"

def test_cdp():
    """Test if NEO browser supports CDP"""
    print("=" * 70)
    print("Testing NEO Browser CDP Support")
    print("=" * 70)

    if not neo_exe.exists():
        print(f"❌ NEO browser not found at: {neo_exe}")
        return False

    print(f"✅ NEO browser found: {neo_exe}")

    # Test different ports
    ports = [9222, 9223, 9224, 9225, 9226]

    for port in ports:
        print(f"\n🔍 Testing port {port}...")

        # Launch browser with remote debugging
        args = [
            str(neo_exe),
            f"--remote-debugging-port={port}",
            "--disable-web-security",
            "--no-sandbox"
        ]

        try:
            print(f"   Launching NEO with --remote-debugging-port={port}...")
            process = subprocess.Popen(
                args,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            # Wait for browser to start
            time.sleep(5)

            # Try to connect to CDP endpoint
            cdp_url = f"http://localhost:{port}/json"
            print(f"   Checking CDP endpoint: {cdp_url}")

            try:
                response = requests.get(cdp_url, timeout=5)
                if response.status_code == 200:
                    sessions = response.json()
                    print(f"   ✅ CDP AVAILABLE on port {port}!")
                    print(f"   Found {len(sessions)} session(s)")
                    if sessions:
                        print(f"   First session: {sessions[0].get('title', 'N/A')}")
                        print(f"   WebSocket URL: {sessions[0].get('webSocketDebuggerUrl', 'N/A')}")
                    process.terminate()
                    return True
                else:
                    print(f"   ❌ HTTP {response.status_code}")
            except requests.exceptions.ConnectionError:
                print(f"   ❌ Connection refused - CDP not available on port {port}")
            except Exception as e:
                print(f"   ❌ Error: {e}")

            # Clean up
            process.terminate()
            time.sleep(2)

        except Exception as e:
            print(f"   ❌ Launch error: {e}")

    print("\n" + "=" * 70)
    print("❌ CDP NOT AVAILABLE on any tested port")
    print("=" * 70)
    print("\nPossible reasons:")
    print("1. NEO browser doesn't support CDP")
    print("2. NEO uses a different protocol")
    print("3. NEO requires different flags")
    print("4. NEO has CDP disabled")
    print("\nRecommendation: Use Windows API automation instead")

    return False

if __name__ == "__main__":
    test_cdp()
