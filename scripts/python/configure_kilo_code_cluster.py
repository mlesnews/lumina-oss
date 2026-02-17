#!/usr/bin/env python3
"""
Configure Kilo Code with Unified Cluster + Iron Legion Standalone

Sets up:
1. ULTRON Cluster (localhost:8080) - Unified ULTRON + Iron Legion
2. ULTRON Direct (localhost:11434) - Direct to laptop Ollama
3. Iron Legion (<NAS_IP>:11434) - Direct to Kaiju for testing

Tags: @PEAK @CLUSTER @KILO_CODE #configuration
"""

import json
import os
import shutil
import sqlite3
import uuid
from datetime import datetime

db_path = os.path.expandvars(r"$APPDATA\Cursor\User\globalStorage\state.vscdb")

# Backup first
backup_path = db_path + f".backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
print(f"Creating backup: {backup_path}")
shutil.copy2(db_path, backup_path)

print(f"Opening database: {db_path}")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get current settings
cursor.execute("SELECT value FROM ItemTable WHERE key = 'kilocode.kilo-code';")
row = cursor.fetchone()

if not row:
    print("ERROR: Kilo Code settings not found!")
    conn.close()
    exit(1)

settings = json.loads(row[0])

print("\n=== Current API Configurations ===")
for config in settings.get("listApiConfigMeta", []):
    print(f"  • {config['name']} ({config['apiProvider']}) - {config.get('modelId', 'N/A')}")

# Define the new configurations
new_configs = [
    {
        "name": "ULTRON Cluster",
        "id": str(uuid.uuid4())[:11].replace("-", ""),
        "apiProvider": "ollama",
        "modelId": "qwen2.5:7b",
        "baseUrl": "http://localhost:8080",
        "description": "Unified cluster: ULTRON + Iron Legion with load balancing",
    },
    {
        "name": "ULTRON Direct",
        "id": str(uuid.uuid4())[:11].replace("-", ""),
        "apiProvider": "ollama",
        "modelId": "qwen2.5:7b",
        "baseUrl": "http://localhost:11434",
        "description": "Direct to laptop Ollama (ULTRON)",
    },
    {
        "name": "Iron Legion",
        "id": str(uuid.uuid4())[:11].replace("-", ""),
        "apiProvider": "ollama",
        "modelId": "qwen2.5:7b",
        "baseUrl": "http://<NAS_IP>:11434",
        "description": "Direct to Kaiju desktop (Iron Legion) for testing",
    },
]

# Check which configs already exist
existing_names = {c["name"] for c in settings.get("listApiConfigMeta", [])}

# Add new configs
added = []
for config in new_configs:
    if config["name"] not in existing_names:
        # Add to listApiConfigMeta
        meta_entry = {
            "name": config["name"],
            "id": config["id"],
            "apiProvider": config["apiProvider"],
            "modelId": config["modelId"],
        }
        if "listApiConfigMeta" not in settings:
            settings["listApiConfigMeta"] = []
        settings["listApiConfigMeta"].append(meta_entry)
        added.append(config["name"])
        print(f"  ✓ Added: {config['name']}")
    else:
        print(f"  • Already exists: {config['name']}")

# Set the default to ULTRON Cluster if it was added
if "ULTRON Cluster" in added:
    settings["currentApiConfigName"] = "ULTRON Cluster"
    settings["ollamaBaseUrl"] = "http://localhost:8080"
    print("\n✓ Set default to: ULTRON Cluster (localhost:8080)")
elif "ULTRON Direct" in existing_names or "ULTRON" in existing_names:
    # Keep existing ULTRON config but ensure URL is correct
    settings["ollamaBaseUrl"] = "http://localhost:11434"
    print("\n✓ Keeping ULTRON Direct as default (localhost:11434)")

# Increase context window
if settings.get("ollamaNumCtx", 4096) < 32768:
    settings["ollamaNumCtx"] = 32768
    print("✓ Context window set to: 32768")

# Write back
cursor.execute(
    "UPDATE ItemTable SET value = ? WHERE key = 'kilocode.kilo-code';", (json.dumps(settings),)
)
conn.commit()

print("\n=== Final API Configurations ===")
for config in settings.get("listApiConfigMeta", []):
    marker = "→" if config["name"] == settings.get("currentApiConfigName") else " "
    print(f"  {marker} {config['name']} ({config['apiProvider']}) - {config.get('modelId', 'N/A')}")

conn.close()

print("""
╔══════════════════════════════════════════════════════════════════╗
║  KILO CODE CLUSTER CONFIGURATION COMPLETE                        ║
╠══════════════════════════════════════════════════════════════════╣
║                                                                  ║
║  API Providers configured:                                       ║
║                                                                  ║
║  1. ULTRON Cluster (localhost:8080)                              ║
║     → Unified: ULTRON + Iron Legion with load balancing          ║
║     → Requires: cluster_router.py running                        ║
║                                                                  ║
║  2. ULTRON Direct (localhost:11434)                              ║
║     → Direct to laptop Ollama                                    ║
║     → Use for: local-only testing                                ║
║                                                                  ║
║  3. Iron Legion (<NAS_IP>:11434)                              ║
║     → Direct to Kaiju desktop                                    ║
║     → Use for: Kaiju-specific testing                            ║
║                                                                  ║
╠══════════════════════════════════════════════════════════════════╣
║  NEXT STEPS:                                                     ║
║                                                                  ║
║  1. Start the cluster router:                                    ║
║     .\\services\\cluster_router\\start_cluster_router.ps1          ║
║                                                                  ║
║  2. Reload Cursor:                                               ║
║     Ctrl+Shift+P → Developer: Reload Window                      ║
║                                                                  ║
║  3. Switch providers in Kilo Code:                               ║
║     Click gear → API Provider → Select desired config            ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
""")
