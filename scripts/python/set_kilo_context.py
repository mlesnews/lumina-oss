#!/usr/bin/env python3
"""Set Kilo Code Ollama context window."""

import json
import os
import sqlite3
import sys

ctx_size = int(sys.argv[1]) if len(sys.argv) > 1 else 8192

db = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db)
cur = conn.cursor()
cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
s = json.loads(cur.fetchone()[0])
old = s.get("ollamaNumCtx", 4096)
print(f"Before: ollamaNumCtx = {old}")
s["ollamaNumCtx"] = ctx_size
cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?", (json.dumps(s), "kilocode.kilo-code"))
conn.commit()
print(f"After:  ollamaNumCtx = {ctx_size}")
conn.close()
