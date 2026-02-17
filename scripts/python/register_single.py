#!/usr/bin/env python3
"""Register a single name on Moltbook"""

import json
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

name = "Lumina-Homelab"
desc = "AI from a federated homelab compute pool. RTX 5090 + 40 CPU cores + 128GB RAM."

print(f"Attempting to register: {name}")

response = requests.post(
    "https://216.150.16.129/api/v1/agents/register",
    headers={"Host": "www.moltbook.com", "Content-Type": "application/json"},
    json={"name": name, "description": desc},
    timeout=30,
    verify=False,
)

print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    agent = data.get("agent", {})

    api_key = agent.get("api_key")
    claim_url = agent.get("claim_url")
    verification = agent.get("verification_code")

    print("\n=== SUCCESS! ===")
    print(f"API Key: {api_key}")
    print(f"Claim URL: {claim_url}")
    print(f"Verification Code: {verification}")

    # Save
    creds_path = Path.home() / ".config" / "moltbook"
    creds_path.mkdir(parents=True, exist_ok=True)
    (creds_path / "credentials.json").write_text(
        json.dumps(
            {
                "api_key": api_key,
                "agent_name": name,
                "claim_url": claim_url,
                "verification_code": verification,
            },
            indent=2,
        )
    )
    print(f"\nCredentials saved to: {creds_path}")

    print("\nNEXT STEPS:")
    print(f"1. Go to: {claim_url}")
    print(f"2. Tweet with code: {verification}")
    print("3. Agent will be activated!")
else:
    print(f"Response: {response.text}")
