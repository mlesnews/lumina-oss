#!/usr/bin/env python3
"""
Add SSH Key to GitHub via API
Requires a GitHub Personal Access Token with 'admin:public_key' scope
"""

import sys
import requests
from pathlib import Path
from typing import Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def add_ssh_key_to_github(token: str, title: Optional[str] = None) -> bool:
    """
    Add SSH public key to GitHub account via API

    Args:
        token: GitHub Personal Access Token with 'admin:public_key' scope
        title: Optional title for the SSH key (default: Windows Development Machine)

    Returns:
        True if successful, False otherwise
    """
    # Read SSH public key
    ssh_key_path = Path.home() / ".ssh" / "id_ed25519.pub"

    if not ssh_key_path.exists():
        print(f"[ERROR] SSH public key not found at: {ssh_key_path}")
        return False

    with open(ssh_key_path, 'r', encoding='utf-8') as f:
        key_content = f.read().strip()

    # Validate key format
    if not key_content.startswith(('ssh-rsa', 'ssh-ed25519', 'ecdsa-sha2')):
        print(f"[ERROR] Invalid SSH key format")
        return False

    # Prepare API request
    url = "https://api.github.com/user/keys"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    data = {
        "title": title or "Windows Development Machine",
        "key": key_content
    }

    try:
        print(f"[INFO] Adding SSH key to GitHub...")
        print(f"[INFO] Title: {data['title']}")

        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 201:
            key_info = response.json()
            print(f"[SUCCESS] SSH key added successfully!")
            print(f"  Key ID: {key_info.get('id')}")
            print(f"  Title: {key_info.get('title')}")
            print(f"  Created: {key_info.get('created_at')}")
            return True
        elif response.status_code == 401:
            print(f"[ERROR] Authentication failed. Check your token.")
            return False
        elif response.status_code == 422:
            error_data = response.json()
            if 'errors' in error_data:
                for error in error_data['errors']:
                    if error.get('message') == 'key is already in use':
                        print(f"[INFO] This SSH key is already added to your GitHub account")
                        return True
            print(f"[ERROR] Validation failed: {error_data}")
            return False
        else:
            print(f"[ERROR] Failed to add key. Status: {response.status_code}")
            print(f"Response: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
        return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Add SSH key to GitHub via API")
    parser.add_argument(
        "--token",
        type=str,
        help="GitHub Personal Access Token (with 'admin:public_key' scope)"
    )
    parser.add_argument(
        "--title",
        type=str,
        default="Windows Development Machine",
        help="Title for the SSH key"
    )

    args = parser.parse_args()

    if not args.token:
        print("[INFO] GitHub Personal Access Token required")
        print("\nTo create a token:")
        print("1. Go to: https://github.com/settings/tokens")
        print("2. Click 'Generate new token (classic)'")
        print("3. Select scope: 'admin:public_key'")
        print("4. Copy the token and run:")
        print("   python add_ssh_key_to_github.py --token YOUR_TOKEN")
        print("\nOr provide it interactively:")
        token = input("GitHub Personal Access Token: ").strip()
        if not token:
            print("[ERROR] Token required")
            sys.exit(1)
        args.token = token

    success = add_ssh_key_to_github(args.token, args.title)
    sys.exit(0 if success else 1)


if __name__ == "__main__":



    main()