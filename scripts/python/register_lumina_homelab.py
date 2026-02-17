#!/usr/bin/env python3
"""
Register Lumina-Homelab on Moltbook

Run this when rate limit expires (~24h after last attempt).
Or schedule it to run automatically.

Usage:
    python register_lumina_homelab.py
    python register_lumina_homelab.py --check-only
"""

import json
import sys
from datetime import datetime
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

MOLTBOOK_IP = "216.150.16.129"
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "moltbook_registration.json"
CREDS_PATH = Path.home() / ".config" / "moltbook" / "credentials.json"


def load_config():
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return None


def check_available(name: str) -> bool:
    """Check if name is still available"""
    try:
        r = requests.get(
            f"https://{MOLTBOOK_IP}/api/v1/agents/profile",
            params={"name": name},
            headers={"Host": "www.moltbook.com"},
            timeout=10,
            verify=False,
        )
        return r.status_code == 404
    except:
        return None


def register(name: str, description: str):
    """Register the agent"""
    try:
        r = requests.post(
            f"https://{MOLTBOOK_IP}/api/v1/agents/register",
            headers={"Host": "www.moltbook.com", "Content-Type": "application/json"},
            json={"name": name, "description": description},
            timeout=30,
            verify=False,
        )
        return r.status_code, r.json() if r.status_code in [200, 409, 429] else r.text
    except Exception as e:
        return None, str(e)


def main():
    print("=" * 60)
    print("  LUMINA-HOMELAB MOLTBOOK REGISTRATION")
    print("=" * 60)

    config = load_config()
    if not config:
        print("\nError: Config not found at", CONFIG_PATH)
        return 1

    name = config["agent_name"]
    description = config["description"]

    print(f"\nAgent Name: {name}")
    print(f"Description: {description[:60]}...")

    # Check if still available
    print(f"\nChecking availability of '{name}'...", end=" ")
    if check_available(name):
        print("AVAILABLE!")
    else:
        print("TAKEN or error")
        print("The name may have been registered by someone else.")
        return 1

    if "--check-only" in sys.argv:
        print("\n[Check only mode - not registering]")
        return 0

    # Attempt registration
    print("\nAttempting registration...")
    status, response = register(name, description)

    if status == 200:
        agent = response.get("agent", {})
        api_key = agent.get("api_key")
        claim_url = agent.get("claim_url")
        verification = agent.get("verification_code")

        print("\n" + "=" * 60)
        print("  SUCCESS! Lumina-Homelab is registered!")
        print("=" * 60)
        print(f"\nAPI Key: {api_key}")
        print(f"Claim URL: {claim_url}")
        print(f"Verification Code: {verification}")

        # Save credentials
        CREDS_PATH.parent.mkdir(parents=True, exist_ok=True)
        CREDS_PATH.write_text(
            json.dumps(
                {
                    "api_key": api_key,
                    "agent_name": name,
                    "claim_url": claim_url,
                    "verification_code": verification,
                    "registered_at": datetime.now().isoformat(),
                },
                indent=2,
            )
        )
        print(f"\nCredentials saved to: {CREDS_PATH}")

        # Update config
        config["status"] = "registered"
        config["registered_at"] = datetime.now().isoformat()
        CONFIG_PATH.write_text(json.dumps(config, indent=2))

        print("\n" + "=" * 60)
        print("  NEXT STEPS")
        print("=" * 60)
        print(f"\n1. Go to: {claim_url}")
        print(f"2. Tweet with verification code: {verification}")
        print("3. Lumina-Homelab will be active on Moltbook!")
        print("\nTarget communities to join:")
        for c in config.get("target_communities", []):
            print(f"  - {c}")

        return 0

    elif status == 429:
        retry = response.get("retry_after_seconds", "?")
        hours = int(retry) // 3600 if isinstance(retry, int) else "?"
        print(f"\nRate limited. Try again in {hours} hours ({retry} seconds)")
        return 2

    elif status == 409:
        print(f"\nName already taken: {response}")
        return 1

    else:
        print(f"\nUnexpected response: {status} - {response}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
