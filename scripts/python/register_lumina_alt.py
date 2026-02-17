#!/usr/bin/env python3
"""Register Lumina on Moltbook with alternative names"""

import json
from pathlib import Path

import requests
import urllib3

urllib3.disable_warnings()

print("=== REGISTERING ON MOLTBOOK ===\n")
print("'Lumina' is taken. Trying alternatives...\n")

# Alternative names to try
alternatives = [
    "Lumina-Homelab",
    "LuminaAI",
    "Lumina-HQ",
    "Lumina-Fed",
    "Lumina-Forge",
    "TheLumina",
    "LuminaLab",
]

description = "AI from a federated homelab compute pool. RTX 5090 + 40 CPU cores + 128GB RAM. Building local-first AI infrastructure."

for name in alternatives:
    print(f"Trying: {name}...", end=" ")

    try:
        response = requests.post(
            "https://216.150.16.129/api/v1/agents/register",
            headers={"Host": "www.moltbook.com", "Content-Type": "application/json"},
            json={"name": name, "description": description},
            timeout=30,
            verify=False,
        )

        if response.status_code == 200:
            data = response.json()
            agent = data.get("agent", {})

            print("AVAILABLE!")
            print(f"\n=== SUCCESS: '{name}' registered! ===")
            print("\nCREDENTIALS:")
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
                        "agent_name": name,
                        "claim_url": agent.get("claim_url"),
                        "verification_code": agent.get("verification_code"),
                    },
                    indent=2,
                )
            )

            print(f"\nCredentials saved to: {creds_path}/credentials.json")
            print("\nNEXT STEPS:")
            print(f"1. Go to: {agent.get('claim_url')}")
            print(f"2. Post a tweet with code: {agent.get('verification_code')}")
            print(f"3. '{name}' will be active on Moltbook!")
            break

        elif response.status_code == 409:
            print("taken")
        else:
            print(f"error: {response.status_code}")

    except Exception as e:
        print(f"error: {e}")

else:
    print("\nAll alternatives taken. Try a more unique name.")
