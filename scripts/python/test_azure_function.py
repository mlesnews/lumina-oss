#!/usr/bin/env python3
"""Test Azure Function endpoint"""
import requests
import json

endpoint = "https://jarvis-lumina-functions.azurewebsites.net/api/RenderIronLegion"

test_payload = {
    "state": "armor",
    "animation_frame": 0,
    "transformation_progress": 1.0,
    "size": 180
}

print(f"🧪 Testing endpoint: {endpoint}")
try:
    response = requests.post(endpoint, json=test_payload, timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        print("   ✅ Function is deployed and responding!")
        data = response.json()
        print(f"   Image size: {len(data.get('image', ''))} bytes (base64)")
    elif response.status_code == 404:
        print("   ❌ Function not found - needs deployment")
    elif response.status_code == 401:
        print("   ⚠️  Authentication required")
    else:
        print(f"   Response: {response.text[:200]}")
except requests.exceptions.ConnectionError as e:
    print(f"   ❌ Connection failed: Function not deployed or endpoint incorrect")
except Exception as e:
    print(f"   ❌ Error: {e}")
