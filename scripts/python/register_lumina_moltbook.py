#!/usr/bin/env python3
"""Register Lumina on Moltbook"""

import json
from pathlib import Path

import requests

print("=== REGISTERING LUMINA ON MOLTBOOK ===\n")

body = {
    "name": "Lumina",
    "description": "AI from a federated homelab compute pool. RTX 5090 + 40 CPU cores + 128GB RAM. Building local-first AI infrastructure.",
}

try:
    response = requests.post(
        "https://www.moltbook.com/api/v1/agents/register",
        headers={"Content-Type": "application/json"},
        json=body,
        timeout=30,
    )

    if response.status_code == 200:
        data = response.json()
        agent = data.get("agent", {})

        print("Registration successful!\n")
        print("CREDENTIALS (SAVE THESE):")
        print(f"  API Key: {agent.get('api_key')}")
        print(f"  Claim URL: {agent.get('claim_url')}")
        print(f"  Verification Code: {agent.get('verification_code')}")

        # Save credentials
        creds_path = Path.home() / ".config" / "moltbook"
        creds_path.mkdir(parents=True, exist_ok=True)
        (creds_path / "credentials.json").write_text(
            json.dumps(
                {
                    "api_key": agent.get("api_key"),
                    "agent_name": "Lumina",
                    "claim_url": agent.get("claim_url"),
                    "verification_code": agent.get("verification_code"),
                },
                indent=2,
            )
        )

        print(f"\nCredentials saved to: {creds_path}/credentials.json")
        print("\nNEXT STEPS:")
        print(f"1. Go to: {agent.get('claim_url')}")
        print(f"2. Post a tweet with verification code: {agent.get('verification_code')}")
        print("3. Lumina will be activated on Moltbook!")

    else:
        print(f"Response {response.status_code}: {response.text}")

        # If name taken, try alternatives
        if (
            "already" in response.text.lower()
            or response.status_code == 409
            or "taken" in response.text.lower()
        ):
            print("\n'Lumina' may be taken. Trying alternatives...")
            for alt in ["Lumina-AI", "Lumina-Homelab", "LuminaHQ", "Lumina-Fed"]:
                print(f"  Trying: {alt}...")
                body["name"] = alt
                r = requests.post(
                    "https://www.moltbook.com/api/v1/agents/register", json=body, timeout=30
                )
                if r.status_code == 200:
                    data = r.json()
                    agent = data.get("agent", {})
                    print(f"\n'{alt}' is available!")
                    print(f"  API Key: {agent.get('api_key')}")
                    print(f"  Claim URL: {agent.get('claim_url')}")
                    print(f"  Verification Code: {agent.get('verification_code')}")

                    # Save
                    creds_path = Path.home() / ".config" / "moltbook"
                    creds_path.mkdir(parents=True, exist_ok=True)
                    (creds_path / "credentials.json").write_text(
                        json.dumps(
                            {
                                "api_key": agent.get("api_key"),
                                "agent_name": alt,
                                "claim_url": agent.get("claim_url"),
                                "verification_code": agent.get("verification_code"),
                            },
                            indent=2,
                        )
                    )
                    break

except requests.exceptions.RequestException as e:
    print(f"Network error: {e}")
    print("\nMoltbook may be temporarily unavailable.")
    print("Try again later with:")
    print('  python scripts/python/moltbook_agent.py register --name Lumina --description "..."')
