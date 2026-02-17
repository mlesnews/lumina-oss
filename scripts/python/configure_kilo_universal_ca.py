#!/usr/bin/env python3
"""
Configure Kilo Code as Universal CA

Sets up Kilo Code with:
- Global Compute Pool endpoint
- 32K context window
- All features enabled
- Auto-approval settings

Tags: @PEAK @KILO_CODE @UNIVERSAL_CA #automation
"""
import sqlite3
import json
import os
from pathlib import Path

def configure_kilo_code():
    """Configure Kilo Code as the Universal CA"""
    print("=== CONFIGURING KILO CODE AS UNIVERSAL CA ===\n")
    
    # Kilo Code settings path
    db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
    
    if not Path(db_path).exists():
        print("Kilo Code database not found at:", db_path)
        return False
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Get current settings
    cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
    row = cur.fetchone()
    
    if not row:
        print("Kilo Code settings not found in database")
        conn.close()
        return False
    
    settings = json.loads(row[0])
    
    # Configure for Universal CA with Global Compute Pool
    print("Applying Universal CA settings...")
    
    # Core settings
    settings["ollamaBaseUrl"] = "http://localhost:8080"  # Global Compute Pool
    settings["ollamaNumCtx"] = 32768  # 32K context window
    
    # Enable features
    settings["autoApprovalEnabled"] = True
    settings["diffEnabled"] = True
    
    # Set allowed commands for auto-approval
    if "allowedCommands" not in settings:
        settings["allowedCommands"] = []
    
    allowed = settings["allowedCommands"]
    for cmd in ["git", "npm", "npx", "python", "node", "pip", "yarn", "pnpm", "cargo", "go"]:
        if cmd not in allowed:
            allowed.append(cmd)
    
    # Update database
    cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?", 
               (json.dumps(settings), "kilocode.kilo-code"))
    conn.commit()
    conn.close()
    
    # Print summary
    print("\nKilo Code configured as Universal CA!")
    print("-" * 50)
    print(f"  Endpoint:      {settings.get('ollamaBaseUrl')}")
    print(f"  Context:       {settings.get('ollamaNumCtx')} tokens")
    print(f"  Model:         {settings.get('ollamaModelId', 'default')}")
    print(f"  Auto-approval: {settings.get('autoApprovalEnabled')}")
    print(f"  Diff enabled:  {settings.get('diffEnabled')}")
    print(f"  Allowed cmds:  {len(settings.get('allowedCommands', []))} commands")
    print("-" * 50)
    print("\nReload Cursor to apply changes (Ctrl+Shift+P -> Developer: Reload Window)")
    
    return True


def show_current_config():
    """Show current Kilo Code configuration"""
    db_path = os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb")
    
    if not Path(db_path).exists():
        print("Kilo Code database not found")
        return
    
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
    row = cur.fetchone()
    
    if row:
        settings = json.loads(row[0])
        print("Current Kilo Code Configuration:")
        print("-" * 50)
        
        keys = ["ollamaBaseUrl", "ollamaModelId", "ollamaNumCtx", 
                "autoApprovalEnabled", "diffEnabled", "allowedCommands"]
        
        for key in keys:
            val = settings.get(key)
            if isinstance(val, list):
                val = f"[{len(val)} items]"
            print(f"  {key}: {val}")
    
    conn.close()


if __name__ == "__main__":
    import sys
    
    if "--show" in sys.argv:
        show_current_config()
    else:
        configure_kilo_code()
