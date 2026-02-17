#!/usr/bin/env python3
"""
Fix Kilo Code Ollama URL in Cursor state database.

Problem: ollamaBaseUrl is set to http://localhost:8080 but Ollama runs on 11434.
Solution: Update the database to use the correct port.

Tags: @PEAK @TROUBLESHOOTING #fix
"""

import json
import os
import shutil
import sqlite3
from datetime import datetime

db_path = os.path.expandvars(r"$APPDATA\Cursor\User\globalStorage\state.vscdb")

# Backup first
backup_path = db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"Creating backup: {backup_path}")
shutil.copy2(db_path, backup_path)

print(f"Opening database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current Kilo Code settings
cursor.execute("SELECT value FROM ItemTable WHERE key = 'kilocode.kilo-code';")
row = cursor.fetchone()

if not row:
    print("ERROR: Kilo Code settings not found!")
    conn.close()
    exit(1)

settings = json.loads(row[0])

print("\n=== Current Settings ===")
print(f"ollamaBaseUrl: {settings.get('ollamaBaseUrl', 'NOT SET')}")
print(f"ollamaModelId: {settings.get('ollamaModelId', 'NOT SET')}")
print(f"apiProvider: {settings.get('apiProvider', 'NOT SET')}")

# Fix the URL
old_url = settings.get("ollamaBaseUrl", "")
new_url = "http://localhost:11434"

if old_url == new_url:
    print(f"\n✅ URL is already correct: {new_url}")
else:
    print(f"\n🔧 Fixing URL: {old_url} → {new_url}")
    settings["ollamaBaseUrl"] = new_url

    # Also update the API config list if it exists
    if "listApiConfigMeta" in settings:
        for config in settings["listApiConfigMeta"]:
            if config.get("apiProvider") == "ollama":
                print(f"   Also found in listApiConfigMeta: {config.get('name')}")

    # Update ollamaNumCtx to a better value (32768 instead of default 4096)
    old_ctx = settings.get("ollamaNumCtx", 4096)
    if old_ctx < 32768:
        print(f"🔧 Increasing context window: {old_ctx} → 32768")
        settings["ollamaNumCtx"] = 32768

    # Write back
    cursor.execute(
        "UPDATE ItemTable SET value = ? WHERE key = 'kilocode.kilo-code';", (json.dumps(settings),)
    )
    conn.commit()
    print("\n✅ Settings updated!")

print("\n=== Updated Settings ===")
print(f"ollamaBaseUrl: {settings.get('ollamaBaseUrl')}")
print(f"ollamaNumCtx: {settings.get('ollamaNumCtx')}")

conn.close()

print("\n⚠️  IMPORTANT: Restart Cursor for changes to take effect!")
print("   Or run: Developer: Reload Window")
