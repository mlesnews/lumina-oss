#!/usr/bin/env python3
"""Quick script to check available models"""
import requests
import json

endpoints = [
    "http://localhost:11434",
    "http://<NAS_PRIMARY_IP>:11434",
    "http://<NAS_IP>:3001",
    "http://<NAS_IP>:3004",
    "http://<NAS_IP>:3005"
]

for endpoint in endpoints:
    try:
        r = requests.get(f"{endpoint}/api/tags", timeout=5)
        if r.status_code == 200:
            data = r.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            print(f"{endpoint}: {models}")
        else:
            print(f"{endpoint}: HTTP {r.status_code}")
    except Exception as e:
        print(f"{endpoint}: Error - {e}")
