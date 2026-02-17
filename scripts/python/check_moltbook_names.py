#!/usr/bin/env python3
"""Check if Moltbook names are available WITHOUT registering"""

import sys

import requests
import urllib3

urllib3.disable_warnings()

print("=== CHECKING MOLTBOOK NAME AVAILABILITY ===\n")

# Names to check
names_to_check = (
    sys.argv[1:]
    if len(sys.argv) > 1
    else ["Lumina", "Jarvis", "Lumina-Homelab", "LuminaAI", "Lumina-Federation", "LuminaForge"]
)

print(f"Checking {len(names_to_check)} names...\n")

for name in names_to_check:
    try:
        # Try the public profile endpoint (no auth required for public profiles)
        response = requests.get(
            "https://216.150.16.129/api/v1/agents/profile",
            params={"name": name},
            headers={"Host": "www.moltbook.com"},
            timeout=10,
            verify=False,
        )

        if response.status_code == 200:
            data = response.json()
            agent = data.get("agent", {})
            desc = agent.get("description", "no description")
            karma = agent.get("karma", 0)
            print(f"  {name}: TAKEN (karma: {karma})")

        elif response.status_code == 404:
            print(f"  {name}: AVAILABLE!")

        elif response.status_code == 401:
            print(f"  {name}: Need auth to check")

        else:
            text = response.text[:80] if response.text else "no response"
            print(f"  {name}: {response.status_code} - {text}")

    except Exception as e:
        print(f"  {name}: Error - {e}")

print("\nNote: 404 = available, 200 = taken, 401 = need API key to check")
