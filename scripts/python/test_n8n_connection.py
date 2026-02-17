#!/usr/bin/env python3
"""Test N8N connection"""
import sys
import time
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
pwd = vault.get_secret("n8n-password")

print("Testing N8N connection...")
for i in range(12):
    try:
        r = requests.get(
            "http://<NAS_PRIMARY_IP>:5678",
            auth=HTTPBasicAuth("mlesn", pwd),
            timeout=5,
            verify=False
        )
        print(f"✅ N8N is accessible! Status: {r.status_code}")
        break
    except Exception as e:
        print(f"Attempt {i+1}/12: {e}")
        if i < 11:
            time.sleep(5)
        else:
            print("❌ N8N not accessible after 60 seconds")
