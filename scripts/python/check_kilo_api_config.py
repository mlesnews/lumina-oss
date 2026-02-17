#!/usr/bin/env python3
"""Check Kilo Code API configuration."""

import json
import os
import sqlite3

db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT value FROM ItemTable WHERE key = 'kilocode.kilo-code';")
row = cursor.fetchone()
settings = json.loads(row[0])

print("=== ACTIVE SELECTION ===")
print(f"currentApiConfigName: {settings.get('currentApiConfigName')}")
print(f"apiProvider: {settings.get('apiProvider')}")
print(f"ollamaBaseUrl: {settings.get('ollamaBaseUrl')}")
print(f"ollamaModelId: {settings.get('ollamaModelId')}")
print(f"apiModelId: {settings.get('apiModelId')}")

print("\n=== ALL API CONFIGS ===")
for c in settings.get("listApiConfigMeta", []):
    current = " <-- ACTIVE" if c["name"] == settings.get("currentApiConfigName") else ""
    print(f"\n{c['name']}{current}")
    print(f"  id: {c.get('id')}")
    print(f"  apiProvider: {c.get('apiProvider')}")
    print(f"  modelId: {c.get('modelId')}")

# Check if there's a secret config
print("\n=== CHECKING SECRET CONFIG ===")
cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%roo_cline_config_api_config%';")
secret_keys = cursor.fetchall()
for (key,) in secret_keys:
    print(f"Found secret key: {key}")

conn.close()
