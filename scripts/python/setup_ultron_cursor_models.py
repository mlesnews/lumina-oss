#!/usr/bin/env python3
"""
Setup ULTRON models in Cursor IDE

This script helps configure ULTRON cluster models in Cursor IDE's chat model dropdown.
Since Cursor IDE may require manual configuration through the Settings UI,
this script provides instructions and can verify the configuration.
"""

import json
import os
from pathlib import Path
import sys
import logging
logger = logging.getLogger("setup_ultron_cursor_models")


def get_cursor_settings_path():
    try:
        """Get Cursor settings.json path"""
        # Try workspace settings first
        workspace_root = Path(__file__).parent.parent.parent
        workspace_settings = workspace_root / ".cursor" / "settings.json"

        # Also check user settings
        home = Path.home()
        if sys.platform == "win32":
            cursor_user_settings = home / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
        elif sys.platform == "darwin":
            cursor_user_settings = home / "Library" / "Application Support" / "Cursor" / "User" / "settings.json"
        else:
            cursor_user_settings = home / ".config" / "Cursor" / "User" / "settings.json"

        return workspace_settings, cursor_user_settings

    except Exception as e:
        logger.error(f"Error in get_cursor_settings_path: {e}", exc_info=True)
        raise
def load_settings(path):
    """Load settings.json if it exists"""
    if path.exists():
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading {path}: {e}")
            return None
    return None

def save_settings(path, settings):
    """Save settings.json"""
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"❌ Error saving {path}: {e}")
        return False

def ensure_ultron_models(settings):
    """Ensure ULTRON models are in settings"""
    if not settings:
        settings = {}

    # ULTRON models configuration
    ultron_models = {
        "cursor.model": {
            "customModels": [
                {
                    "title": "ULTRON Cluster (Qwen2.5 72B)",
                    "provider": "ollama",
                    "model": "qwen2.5:72b",
                    "apiBase": "http://localhost:11434",
                    "contextLength": 32768,
                    "description": "ULTRON Cluster - Local Qwen2.5 72B + KAIJU Iron Legion hybrid cluster"
                },
                {
                    "title": "ULTRON Router (Smart Routing)",
                    "provider": "ollama",
                    "model": "qwen2.5:72b",
                    "apiBase": "http://<NAS_PRIMARY_IP>:3008",
                    "contextLength": 32768,
                    "description": "ULTRON Router - Smart routing between local laptop and KAIJU NAS"
                },
                {
                    "title": "KAIJU Iron Legion",
                    "provider": "ollama",
                    "model": "llama3",
                    "apiBase": "http://<NAS_PRIMARY_IP>:11434",
                    "contextLength": 8192,
                    "description": "KAIJU NAS Iron Legion - 7 models available"
                }
            ]
        },
        "ollama.endpoint": "http://localhost:11434",
        "ollama.defaultModel": "qwen2.5:72b"
    }

    # Merge settings
    for key, value in ultron_models.items():
        if key not in settings:
            settings[key] = value
        elif key == "cursor.model":
            # Merge customModels array
            if "customModels" not in settings[key]:
                settings[key]["customModels"] = []

            existing_names = {m.get("title") or m.get("name") for m in settings[key]["customModels"]}

            for model in value["customModels"]:
                model_name = model.get("title") or model.get("name")
                if model_name not in existing_names:
                    settings[key]["customModels"].append(model)
                    print(f"✅ Added model: {model_name}")

    return settings

def print_manual_instructions():
    """Print manual setup instructions"""
    print("\n" + "="*70)
    print("📋 MANUAL SETUP INSTRUCTIONS FOR CURSOR IDE")
    print("="*70)
    print("\nIf models don't appear automatically, follow these steps:\n")
    print("1. Open Cursor Settings:")
    print("   - Press Ctrl+, (or Cmd+, on Mac)")
    print("   - Or: File → Preferences → Settings\n")
    print("2. Search for 'model' or 'ollama'\n")
    print("3. Configure Ollama:")
    print("   - Set 'Ollama Endpoint': http://localhost:11434")
    print("   - Set 'Default Model': qwen2.5:72b\n")
    print("4. Add Custom Models (if option available):")
    print("   - Look for 'Custom Models' or 'Add Model' option")
    print("   - Add each ULTRON model manually\n")
    print("5. Restart Cursor IDE\n")
    print("="*70)
    print("\nULTRON Models to Add:\n")
    print("Model 1:")
    print("  Name: ULTRON Cluster (Qwen2.5 72B)")
    print("  Provider: ollama")
    print("  Model: qwen2.5:72b")
    print("  Endpoint: http://localhost:11434\n")
    print("Model 2:")
    print("  Name: ULTRON Router (Smart Routing)")
    print("  Provider: ollama")
    print("  Model: qwen2.5:72b")
    print("  Endpoint: http://<NAS_PRIMARY_IP>:3008\n")
    print("Model 3:")
    print("  Name: KAIJU Iron Legion")
    print("  Provider: ollama")
    print("  Model: llama3")
    print("  Endpoint: http://<NAS_PRIMARY_IP>:11434\n")
    print("="*70)

def main():
    print("🤖 ULTRON Cursor Model Setup")
    print("="*70)
    print()

    workspace_settings_path, user_settings_path = get_cursor_settings_path()

    # Try workspace settings first
    print(f"📁 Checking workspace settings: {workspace_settings_path}")
    workspace_settings = load_settings(workspace_settings_path)

    if workspace_settings:
        print("✅ Workspace settings found")
        workspace_settings = ensure_ultron_models(workspace_settings)
        if save_settings(workspace_settings_path, workspace_settings):
            print("✅ Workspace settings updated")
        else:
            print("⚠️  Could not update workspace settings")
    else:
        print("⚠️  Workspace settings not found, creating...")
        new_settings = ensure_ultron_models({})
        if save_settings(workspace_settings_path, new_settings):
            print("✅ Created workspace settings with ULTRON models")
        else:
            print("❌ Could not create workspace settings")

    print()
    print("💡 TIP: Restart Cursor IDE for changes to take effect")
    print()

    # Print manual instructions
    print_manual_instructions()

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Restart Cursor IDE")
    print("2. Open Chat panel (Ctrl+L)")
    print("3. Click model dropdown")
    print("4. Look for ULTRON models")

if __name__ == "__main__":


    main()