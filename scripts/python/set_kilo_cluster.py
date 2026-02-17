#!/usr/bin/env python3
"""Configure Kilo Code to use the cluster router."""

import json
import os
import sqlite3

db = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
s = json.loads(cur.fetchone()[0])

print(f"BEFORE: ollamaBaseUrl = {s.get('ollamaBaseUrl')}")

# Set to cluster router
s["ollamaBaseUrl"] = "http://localhost:8080"
s["ollamaNumCtx"] = 8192  # Reasonable context size

cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?", (json.dumps(s), "kilocode.kilo-code"))
conn.commit()

print("AFTER:  ollamaBaseUrl = http://localhost:8080")
print("        ollamaNumCtx = 8192")
print("\n✅ Kilo Code now points to cluster router!")
print("   Reload Cursor to apply.")

conn.close()
