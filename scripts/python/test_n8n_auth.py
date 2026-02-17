#!/usr/bin/env python3
"""Test N8N authentication with vault credentials"""
import sys
import requests
from pathlib import Path
from requests.auth import HTTPBasicAuth

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
pwd = vault.get_secret('n8n-password')

urls = [
    "http://<NAS_PRIMARY_IP>:5678",
    "http://<NAS_PRIMARY_IP>:5000"
]

for url in urls:
    print(f"\nTesting {url}...")
    for user in ["mlesn", "admin", "n8n"]:
        auth = HTTPBasicAuth(user, pwd)
        try:
            r = requests.get(f"{url}/api/v1/workflows", auth=auth, timeout=3, verify=False)
            print(f"  {user}: {r.status_code}")
            if r.status_code == 200:
                print(f"  ✅ SUCCESS with {user}!")
                break
        except Exception as e:
            print(f"  {user}: Error - {e}")
