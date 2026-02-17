#!/usr/bin/env python3
"""Check Kilo Code configuration"""

import json
import os
import sqlite3

db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Get Kilo Code settings
cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
row = cur.fetchone()

if row:
    settings = json.loads(row[0])

    print("=" * 60)
    print("  KILO CODE CONFIGURATION")
    print("=" * 60)

    print("\n[Model Settings]")
    print(f"  Ollama Model: {settings.get('ollamaModelId', 'not set')}")
    print(f"  Base URL: {settings.get('ollamaBaseUrl', 'not set')}")
    print(f"  Context Window: {settings.get('ollamaNumCtx', 'not set')}")

    # Check API configs
    configs = settings.get("listApiConfigMeta", [])
    print(f"\n[API Configurations] ({len(configs)} total)")
    for c in configs:
        name = c.get("name", "?")
        provider = c.get("apiProvider", "?")
        model = c.get("modelId", "?")
        is_active = " (ACTIVE)" if c.get("id") == settings.get("apiConfigId") else ""
        print(f"  - {name}: {provider} / {model}{is_active}")

    # Check features
    print("\n[Features]")
    print(f"  Auto-approve enabled: {settings.get('autoApprovalEnabled', False)}")
    print(f"  Diff enabled: {settings.get('diffEnabled', True)}")
    print(f"  Fuzzy match threshold: {settings.get('fuzzyMatchThreshold', 'default')}")
    print(f"  Directory context: {settings.get('directoryContextAddedContext', 'default')}")

    # Check allowed/denied commands
    allowed = settings.get("allowedCommands", [])
    denied = settings.get("deniedCommands", [])
    print("\n[Command Permissions]")
    print(f"  Allowed commands: {len(allowed)}")
    print(f"  Denied commands: {len(denied)}")

    # Check custom modes
    modes = settings.get("customModes", [])
    print(f"\n[Custom Modes] ({len(modes)} total)")
    for m in modes:
        print(f"  - {m.get('name', '?')}: {m.get('description', '')[:40]}")

    # Check MCP settings
    print("\n[MCP Integration]")
    print(f"  MCP settings exist: {'mcpSettings' in str(settings)}")

    # Output raw settings keys for reference
    print("\n[All Settings Keys]")
    for key in sorted(settings.keys()):
        val = settings[key]
        if isinstance(val, (list, dict)):
            print(f"  {key}: ({type(val).__name__}, {len(val)} items)")
        else:
            print(f"  {key}: {str(val)[:50]}")

else:
    print("Kilo Code settings not found in database")

conn.close()
