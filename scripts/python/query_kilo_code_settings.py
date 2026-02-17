#!/usr/bin/env python3
"""Query Kilo Code settings from Cursor state database."""

import json
import os
import sqlite3

db_path = os.path.expandvars(r"$APPDATA\Cursor\User\globalStorage\state.vscdb")

print(f"Opening database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print(f"Tables: {[t[0] for t in tables]}")

# Look for Kilo Code related keys
print("\n=== Kilo Code related keys ===")
cursor.execute("SELECT key FROM ItemTable WHERE key LIKE '%kilo%' OR key LIKE '%kilocode%';")
keys = cursor.fetchall()
for (key,) in keys:
    print(f"  {key}")

# Get the actual provider settings
print("\n=== Looking for provider/API settings ===")
provider_keys = [
    "kilocode.kilo-code",
    "kilo-code.apiProvider",
    "kilo-code.apiConfiguration",
    "kilocode.kilo-code.apiProvider",
]

for pk in provider_keys:
    cursor.execute("SELECT value FROM ItemTable WHERE key = ?;", (pk,))
    row = cursor.fetchone()
    if row:
        print(f"\nKey: {pk}")
        try:
            val = json.loads(row[0])
            print(json.dumps(val, indent=2)[:2000])
        except (json.JSONDecodeError, TypeError):
            print(f"Raw value (first 500 chars): {str(row[0])[:500]}")

# Try to find any API-related settings
print("\n=== Searching for API/provider patterns ===")
cursor.execute(
    "SELECT key, substr(value, 1, 500) FROM ItemTable WHERE value LIKE '%apiProvider%' OR value LIKE '%ollama%' OR value LIKE '%11434%' LIMIT 20;"
)
for key, val in cursor.fetchall():
    print(f"\nKey: {key}")
    print(f"Preview: {val}")

# Get the full kilocode.kilo-code value
print("\n=== Full Kilo Code settings ===")
cursor.execute("SELECT value FROM ItemTable WHERE key = 'kilocode.kilo-code';")
row = cursor.fetchone()
if row:
    try:
        val = json.loads(row[0])
        # Look for API-related keys
        api_keys = [
            k
            for k in val.keys()
            if any(
                x in k.lower() for x in ["api", "provider", "model", "config", "url", "endpoint"]
            )
        ]
        print(f"API-related keys found: {api_keys}")
        for k in api_keys:
            print(f"\n{k}: {json.dumps(val[k], indent=2)[:1000]}")

        # Print all keys
        print(f"\nAll keys in settings: {list(val.keys())}")
    except Exception as e:
        print(f"Error: {e}")

# Check for roo_cline_config which might have the API config
print("\n=== Looking for roo/cline config patterns ===")
cursor.execute(
    "SELECT key, substr(value, 1, 1000) FROM ItemTable WHERE key LIKE '%roo%' OR key LIKE '%cline%' LIMIT 10;"
)
for key, val in cursor.fetchall():
    print(f"\nKey: {key}")
    print(f"Preview: {val[:500]}")

conn.close()
print("\nDone.")
