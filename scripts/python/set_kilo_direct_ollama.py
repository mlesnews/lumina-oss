#!/usr/bin/env python3
"""Set Kilo Code to use direct Ollama (bypass router for testing)."""

import json
import os
import sqlite3

db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT value FROM ItemTable WHERE key = 'kilocode.kilo-code';")
row = cursor.fetchone()
settings = json.loads(row[0])

print(f"Current ollamaBaseUrl: {settings.get('ollamaBaseUrl')}")

# Change to direct Ollama
settings["ollamaBaseUrl"] = "http://localhost:11434"
print("Setting ollamaBaseUrl to: http://localhost:11434")

cursor.execute(
    "UPDATE ItemTable SET value = ? WHERE key = 'kilocode.kilo-code';", (json.dumps(settings),)
)
conn.commit()
conn.close()
print("\nDone! Reload Cursor (Ctrl+Shift+P -> Developer: Reload Window)")
