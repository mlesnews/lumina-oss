#!/usr/bin/env python3
"""Fix Kilo Code Ollama URL and verify."""

import json
import os
import sqlite3

db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
row = cursor.fetchone()
settings = json.loads(row[0])

old_url = settings.get("ollamaBaseUrl", "NOT SET")
print(f"BEFORE: ollamaBaseUrl = {old_url}")

# Fix it
settings["ollamaBaseUrl"] = "http://localhost:11434"

cursor.execute(
    "UPDATE ItemTable SET value = ? WHERE key = ?", (json.dumps(settings), "kilocode.kilo-code")
)
conn.commit()

# Verify by re-reading
cursor.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
row = cursor.fetchone()
settings = json.loads(row[0])
new_url = settings.get("ollamaBaseUrl", "NOT SET")
print(f"AFTER:  ollamaBaseUrl = {new_url}")

if new_url == "http://localhost:11434":
    print("\n✅ Successfully fixed! Reload Cursor now.")
else:
    print(f"\n❌ Fix failed - got {new_url}")

conn.close()
