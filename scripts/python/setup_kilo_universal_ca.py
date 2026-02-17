#!/usr/bin/env python3
"""
Setup Kilo Code as Universal CA

Configures Kilo Code with:
- Custom modes from Continue, Cline, Roo
- MCP servers for extended functionality
- Context providers
- Embeddings for codebase awareness
- Voice integration

Usage:
    python setup_kilo_universal_ca.py              # Full setup
    python setup_kilo_universal_ca.py --modes      # Setup modes only
    python setup_kilo_universal_ca.py --mcp        # Setup MCP only
    python setup_kilo_universal_ca.py --embeddings # Index codebase
    python setup_kilo_universal_ca.py --verify     # Verify setup

Tags: @PEAK @KILO_CODE @UNIVERSAL_CA #automation
"""

import argparse
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
KILOCODE_DIR = PROJECT_ROOT / ".kilocode"

# Kilo Code paths
CURSOR_STATE_DB = Path(os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\state.vscdb"))
CURSOR_MCP_CONFIG = Path(os.path.expandvars(r"%APPDATA%\Cursor\User\globalStorage\kilocode.kilo-code\settings\mcp_settings.json"))


def print_header(title: str):
    """Print section header"""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def setup_modes():
    """Configure custom modes in Kilo Code"""
    print_header("SETTING UP CUSTOM MODES")
    
    # Load unified modes config
    modes_file = CONFIG_DIR / "kilo_unified_ca_modes.json"
    if not modes_file.exists():
        print(f"ERROR: Modes config not found: {modes_file}")
        return False
    
    with open(modes_file) as f:
        modes_config = json.load(f)
    
    print(f"Loaded {len(modes_config['modes'])} custom modes")
    
    # Get Kilo Code settings
    if not CURSOR_STATE_DB.exists():
        print(f"ERROR: Kilo Code database not found: {CURSOR_STATE_DB}")
        return False
    
    conn = sqlite3.connect(CURSOR_STATE_DB)
    cur = conn.cursor()
    
    cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
    row = cur.fetchone()
    
    if not row:
        print("ERROR: Kilo Code settings not found")
        conn.close()
        return False
    
    settings = json.loads(row[0])
    
    # Add custom modes
    if "customModes" not in settings:
        settings["customModes"] = []
    
    existing_slugs = {m.get("slug") for m in settings["customModes"]}
    
    modes_added = 0
    for slug, mode_data in modes_config["modes"].items():
        if slug not in existing_slugs:
            custom_mode = {
                "slug": mode_data["slug"],
                "name": mode_data["name"],
                "roleDefinition": mode_data["role_definition"],
                "groups": mode_data.get("tools", ["read", "edit", "browser", "commands", "mcp"]),
            }
            settings["customModes"].append(custom_mode)
            modes_added += 1
            print(f"  Added mode: {mode_data['name']} (/{slug})")
        else:
            print(f"  Mode exists: {mode_data['name']} (/{slug})")
    
    # Save settings
    cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?",
               (json.dumps(settings), "kilocode.kilo-code"))
    conn.commit()
    conn.close()
    
    print(f"\nAdded {modes_added} new modes")
    print("Reload Cursor to apply (Ctrl+Shift+P -> Developer: Reload Window)")
    
    return True


def setup_mcp():
    """Configure MCP servers"""
    print_header("SETTING UP MCP SERVERS")
    
    # Copy project-level MCP config
    project_mcp = KILOCODE_DIR / "mcp.json"
    if project_mcp.exists():
        print(f"Project MCP config exists: {project_mcp}")
        
        with open(project_mcp) as f:
            mcp_config = json.load(f)
        
        print(f"Configured servers:")
        for name, server in mcp_config.get("mcpServers", {}).items():
            print(f"  - {name}: {server.get('description', 'No description')}")
    else:
        print(f"ERROR: Project MCP config not found: {project_mcp}")
        return False
    
    # Also update global MCP config
    global_mcp_dir = CURSOR_MCP_CONFIG.parent
    global_mcp_dir.mkdir(parents=True, exist_ok=True)
    
    if CURSOR_MCP_CONFIG.exists():
        with open(CURSOR_MCP_CONFIG) as f:
            global_mcp = json.load(f)
    else:
        global_mcp = {"mcpServers": {}}
    
    # Merge project MCP into global
    for name, server in mcp_config.get("mcpServers", {}).items():
        if name not in global_mcp.get("mcpServers", {}):
            global_mcp.setdefault("mcpServers", {})[name] = server
            print(f"  Added to global: {name}")
    
    with open(CURSOR_MCP_CONFIG, "w") as f:
        json.dump(global_mcp, f, indent=2)
    
    print(f"\nMCP config saved to: {CURSOR_MCP_CONFIG}")
    
    return True


def setup_embeddings():
    """Index codebase for semantic search"""
    print_header("INDEXING CODEBASE FOR EMBEDDINGS")
    
    # Check dependencies
    try:
        import sentence_transformers
        print("sentence-transformers: OK")
    except ImportError:
        print("Installing sentence-transformers...")
        subprocess.run([sys.executable, "-m", "pip", "install", "sentence-transformers", "faiss-cpu"], check=True)
    
    # Run indexing
    embeddings_script = SCRIPT_DIR / "embeddings_mcp_server.py"
    if embeddings_script.exists():
        print("\nIndexing codebase (this may take a few minutes)...")
        result = subprocess.run(
            [sys.executable, str(embeddings_script), "--index"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print(f"WARNING: {result.stderr}")
    else:
        print(f"ERROR: Embeddings script not found: {embeddings_script}")
        return False
    
    return True


def setup_voice():
    """Configure voice integration"""
    print_header("SETTING UP VOICE INTEGRATION")
    
    voice_config = CONFIG_DIR / "kilo_voice_system.json"
    if voice_config.exists():
        print(f"Voice config exists: {voice_config}")
        
        with open(voice_config) as f:
            config = json.load(f)
        
        print(f"  PTT Hotkey: {config.get('push_to_talk_key')}")
        print(f"  Whisper Model: {config.get('whisper_model')}")
        print(f"  TTS Enabled: {config.get('elevenlabs_enabled')}")
    else:
        print("Creating default voice config...")
        # Will be created by kilo_voice_system.py on first run
    
    print("\nTo start voice: python scripts/python/kilo_voice_system.py --ptt")
    
    return True


def configure_kilo_settings():
    """Configure Kilo Code base settings"""
    print_header("CONFIGURING KILO CODE SETTINGS")
    
    if not CURSOR_STATE_DB.exists():
        print(f"ERROR: Kilo Code database not found")
        return False
    
    conn = sqlite3.connect(CURSOR_STATE_DB)
    cur = conn.cursor()
    
    cur.execute("SELECT value FROM ItemTable WHERE key = ?", ("kilocode.kilo-code",))
    row = cur.fetchone()
    
    if not row:
        print("ERROR: Kilo Code settings not found")
        conn.close()
        return False
    
    settings = json.loads(row[0])
    
    # Configure for Universal CA
    settings["ollamaBaseUrl"] = "http://localhost:8080"  # Global Compute Pool
    settings["ollamaNumCtx"] = 32768  # 32K context
    settings["autoApprovalEnabled"] = True
    settings["diffEnabled"] = True
    
    # Add allowed commands
    if "allowedCommands" not in settings:
        settings["allowedCommands"] = []
    
    safe_commands = ["git", "npm", "npx", "python", "node", "pip", "yarn", "pnpm", "cargo", "go"]
    for cmd in safe_commands:
        if cmd not in settings["allowedCommands"]:
            settings["allowedCommands"].append(cmd)
    
    cur.execute("UPDATE ItemTable SET value = ? WHERE key = ?",
               (json.dumps(settings), "kilocode.kilo-code"))
    conn.commit()
    conn.close()
    
    print("Kilo Code settings configured:")
    print(f"  Endpoint: {settings.get('ollamaBaseUrl')}")
    print(f"  Context: {settings.get('ollamaNumCtx')} tokens")
    print(f"  Auto-approval: {settings.get('autoApprovalEnabled')}")
    
    return True


def verify_setup():
    """Verify Universal CA setup"""
    print_header("VERIFYING UNIVERSAL CA SETUP")
    
    checks = []
    
    # Check modes config
    modes_file = CONFIG_DIR / "kilo_unified_ca_modes.json"
    checks.append(("Modes config", modes_file.exists()))
    
    # Check MCP config
    mcp_file = KILOCODE_DIR / "mcp.json"
    checks.append(("Project MCP config", mcp_file.exists()))
    
    # Check voice config
    voice_file = CONFIG_DIR / "kilo_voice_system.json"
    checks.append(("Voice config", voice_file.exists()))
    
    # Check embeddings index
    embeddings_file = PROJECT_ROOT / "data" / "embeddings" / "codebase_index.json"
    checks.append(("Embeddings index", embeddings_file.exists()))
    
    # Check Kilo Code database
    checks.append(("Kilo Code database", CURSOR_STATE_DB.exists()))
    
    # Print results
    print("\nSetup Status:")
    all_ok = True
    for name, status in checks:
        icon = "OK" if status else "MISSING"
        print(f"  [{icon}] {name}")
        if not status:
            all_ok = False
    
    if all_ok:
        print("\n All checks passed! Universal CA is ready.")
    else:
        print("\n Some components missing. Run full setup.")
    
    return all_ok


def show_usage():
    """Show usage information"""
    print_header("KILO CODE UNIVERSAL CA - USAGE")
    
    print("""
MODES (use slash commands or keyboard shortcuts):
  /code       - Full access coding mode (Ctrl+Shift+1)
  /ask        - Read-only Q&A mode (Ctrl+Shift+2)
  /architect  - System design mode (Ctrl+Shift+3)
  /debug      - Troubleshooting mode (Ctrl+Shift+4)
  /orchestrator - Task orchestration mode (Ctrl+Shift+5)
  /codebase   - Codebase-aware mode with embeddings (Ctrl+Shift+6)
  /plan       - Plan & Act mode (Ctrl+Shift+7)
  /yolo       - Auto-approve mode (Ctrl+Shift+8)
  /jarvis     - Full JARVIS mode with voice (Ctrl+Shift+9)
  /security   - Security review mode (Ctrl+Shift+0)

CONTEXT PROVIDERS (type @ in chat):
  @File       - Include specific file
  @Folder     - Include folder contents
  @Codebase   - Semantic search (requires embeddings)
  @Git Diff   - Include git changes
  @Terminal   - Include terminal output
  @Problems   - Include linter errors

VOICE COMMANDS:
  Start voice: python scripts/python/kilo_voice_system.py --ptt
  Hold Ctrl+Shift+K to speak, release to send

MCP TOOLS:
  Embeddings search, voice output, helpdesk integration,
  filesystem, git, web search, browser automation
""")


def main():
    parser = argparse.ArgumentParser(description="Setup Kilo Code as Universal CA")
    parser.add_argument("--modes", action="store_true", help="Setup custom modes only")
    parser.add_argument("--mcp", action="store_true", help="Setup MCP servers only")
    parser.add_argument("--embeddings", action="store_true", help="Index codebase only")
    parser.add_argument("--voice", action="store_true", help="Setup voice only")
    parser.add_argument("--verify", action="store_true", help="Verify setup")
    parser.add_argument("--usage", action="store_true", help="Show usage info")
    
    args = parser.parse_args()
    
    print("""
╔══════════════════════════════════════════════════════════════╗
║          KILO CODE UNIVERSAL CA SETUP                        ║
║                                                              ║
║  Incorporating features from:                                ║
║    - Continue (context providers, embeddings)                ║
║    - Cline (plan & act, YOLO mode, checkpoints)              ║
║    - Roo (modes, orchestration, boomerang tasks)             ║
║    - Jarvis (voice, helpdesk, orchestration)                 ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
    
    if args.verify:
        verify_setup()
    elif args.usage:
        show_usage()
    elif args.modes:
        setup_modes()
    elif args.mcp:
        setup_mcp()
    elif args.embeddings:
        setup_embeddings()
    elif args.voice:
        setup_voice()
    else:
        # Full setup
        configure_kilo_settings()
        setup_modes()
        setup_mcp()
        setup_voice()
        # setup_embeddings()  # Commented out - run separately as it takes time
        
        print_header("SETUP COMPLETE")
        print("""
Next steps:
1. Reload Cursor: Ctrl+Shift+P -> Developer: Reload Window
2. Start voice: python scripts/python/kilo_voice_system.py --ptt
3. Index codebase: python scripts/python/setup_kilo_universal_ca.py --embeddings
4. Use modes: Type /code, /ask, /architect, etc. in Kilo chat
        """)
        
        verify_setup()


if __name__ == "__main__":
    main()
