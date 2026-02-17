#!/usr/bin/env python3
"""Dump FULL Kilo Code configuration."""

import json
import os
import sqlite3

db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
row = cursor.fetchone()
settings = json.loads(row[0])

print("=== FULL listApiConfigMeta ===")
for config in settings.get("listApiConfigMeta", []):
    print(json.dumps(config, indent=2))
    print("---")

print("\n=== ALL OLLAMA-RELATED KEYS ===")
for key, value in settings.items():
    if "ollama" in key.lower():
        print(f"{key}: {value}")

print("\n=== API PROVIDER ===")
print(f"apiProvider: {settings.get('apiProvider')}")
print(f"currentApiConfigName: {settings.get('currentApiConfigName')}")

conn.close()
