#!/usr/bin/env python3
"""Test function with authentication key"""
import requests

endpoint = "https://jarvis-lumina-functions.azurewebsites.net/api/renderironlegion"
function_key = "49NWp1OfkqX262TkUYTruGMkV3iQpfOmaQAeSZxVvbVYAzFupr5HKw=="

payload = {
    "state": "armor",
    "animation_frame": 0,
    "transformation_progress": 1.0,
    "size": 180
}

url = f"{endpoint}?code={function_key}"

print(f"🧪 Testing: {endpoint}")
print(f"   With function key authentication")
try:
    r = requests.post(url, json=payload, timeout=15)
    print(f"   Status: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ SUCCESS! Image: {len(data.get('image', ''))} bytes")
        print("   🎉 REMOTE COMPUTE IS ACTIVE!")
        print(f"\n   Endpoint: {endpoint}")
        print(f"   Function Key: {function_key[:20]}...")
    else:
        print(f"   Response: {r.text[:300]}")
except Exception as e:
    print(f"   ❌ Error: {e}")
