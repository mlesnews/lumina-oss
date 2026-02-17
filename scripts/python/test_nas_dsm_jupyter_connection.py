#!/usr/bin/env python3
import json
import socket
import sys
from pathlib import Path

import requests

# Load Configuration
CONFIG_PATH = Path("../../config/nas_dsm_jupyter_config.json")


def load_config():
    if not CONFIG_PATH.exists():
        print(f"❌ Configuration file not found at {CONFIG_PATH}")
        sys.exit(1)

    with open(CONFIG_PATH) as f:
        return json.load(f)


def check_socket(host, port, timeout=5):
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (OSError, socket.timeout):
        return False


def check_jupyter_api(host, port, token):
    url = f"http://{host}:{port}/api/status"
    headers = {"Authorization": f"token {token}"}
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Status Code: {response.status_code}"
    except requests.RequestException as e:
        return False, str(e)


def main():
    print("🔍 Testing NAS-DSM Jupyter Connection...")
    config = load_config()

    host = config.get("nas_host")
    port = config.get("jupyter_port")
    token = config.get("jupyter_token")

    # 1. Check TCP Socket
    print(f"   👉 Connecting to {host}:{port}...")
    if check_socket(host, port):
        print("   ✅ TCP Connection Successful")
    else:
        print("   ❌ TCP Connection Failed")
        sys.exit(1)

    # 2. Check Jupyter API
    print("   👉 Verifying Jupyter API...")
    success, details = check_jupyter_api(host, port, token)
    if success:
        print("   ✅ Jupyter API Accessible")
        print(f"   ℹ️  Server Status: {details}")
    else:
        print(f"   ❌ Jupyter API Failed: {details}")
        sys.exit(1)

    print("\n✅ NAS-DSM Jupyter Server is Ready for Jedi Archives.")


if __name__ == "__main__":
    main()
