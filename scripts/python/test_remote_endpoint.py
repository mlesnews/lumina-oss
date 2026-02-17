#!/usr/bin/env python3
"""Test remote endpoint"""
import requests

endpoint = "https://jarvis-lumina-functions.azurewebsites.net/api/renderironlegion"
payload = {
    "state": "armor",
    "animation_frame": 0,
    "transformation_progress": 1.0,
    "size": 180
}

print(f"🧪 Testing: {endpoint}")
try:
    r = requests.post(endpoint, json=payload, timeout=15)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ SUCCESS! Image: {len(data.get('image', ''))} bytes")
        print("   🎉 REMOTE COMPUTE IS ACTIVE!")
    else:
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")
