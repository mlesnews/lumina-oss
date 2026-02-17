#!/usr/bin/env python3
"""Test N8N API Key"""
import sys
import requests
from pathlib import Path

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from azure_service_bus_integration import AzureKeyVaultClient

vault = AzureKeyVaultClient(vault_url="https://jarvis-lumina.vault.azure.net/")
api_key = vault.get_secret("n8n-api-token")

n8n_url = "http://<NAS_PRIMARY_IP>:5678"

print("Testing N8N API Key...")
print(f"API Key length: {len(api_key)}")
print(f"API Key preview: {api_key[:20]}...")

# Test GET workflows
headers = {
    "X-N8N-API-KEY": api_key,
    "Content-Type": "application/json"
}

print("\n1. Testing GET /api/v1/workflows...")
r = requests.get(f"{n8n_url}/api/v1/workflows", headers=headers, timeout=5, verify=False)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.text[:300]}")

print("\n2. Testing GET /rest/workflows...")
r2 = requests.get(f"{n8n_url}/rest/workflows", headers=headers, timeout=5, verify=False)
print(f"   Status: {r2.status_code}")
print(f"   Response: {r2.text[:300]}")

print("\n3. Testing POST /api/v1/workflows/import (empty)...")
r3 = requests.post(
    f"{n8n_url}/api/v1/workflows/import",
    json={"workflow": {"name": "test"}},
    headers=headers,
    timeout=5,
    verify=False
)
print(f"   Status: {r3.status_code}")
print(f"   Response: {r3.text[:300]}")
