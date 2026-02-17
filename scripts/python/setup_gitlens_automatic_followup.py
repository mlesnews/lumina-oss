#!/usr/bin/env python3
"""
Setup Automatic GitLens Follow-up Handling

Configures automatic handling of all GitLens follow-up requirements.
This script sets up the automation to run automatically.

Tags: #GITLENS #AUTOMATION #SETUP #FULLAUTO @JARVIS @DOIT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SetupGitLensAutomaticFollowup")


def setup_automatic_followup():
    """Set up automatic GitLens follow-up handling"""
    project_root = Path(__file__).parent.parent.parent

    print("\n" + "="*80)
    print("⚙️  SETTING UP AUTOMATIC GITLENS FOLLOW-UP HANDLING")
    print("="*80 + "\n")

    # 1. Create VS Code task for automatic handling
    print("📝 Step 1: Creating VS Code task...")
    vscode_dir = project_root / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    tasks_file = vscode_dir / "tasks.json"
    tasks = {"version": "2.0.0", "tasks": []}

    if tasks_file.exists():
        try:
            with open(tasks_file, 'r', encoding='utf-8') as f:
                tasks = json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Error reading tasks.json: {e}")

    # Check if task already exists
    task_label = "JARVIS: Auto-Handle GitLens Follow-ups"
    existing_task = next(
        (t for t in tasks.get("tasks", []) if t.get("label") == task_label),
        None
    )

    if not existing_task:
        gitlens_task = {
            "label": task_label,
            "type": "shell",
            "command": "python",
            "args": [
                "${workspaceFolder}/scripts/python/jarvis_gitlens_followup_automation.py",
                "--handle"
            ],
            "problemMatcher": [],
            "presentation": {
                "reveal": "silent",
                "panel": "shared",
                "close": True
            },
            "runOptions": {
                "runOn": "folderOpen"
            },
            "group": {
                "kind": "build",
                "isDefault": False
            }
        }

        tasks.setdefault("tasks", []).append(gitlens_task)

        try:
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)
            print(f"   ✅ Added task to {tasks_file}")
        except Exception as e:
            print(f"   ❌ Error writing tasks.json: {e}")
    else:
        print(f"   ℹ️  Task already exists in {tasks_file}")

    # 2. Create settings entry for automatic handling
    print("\n📝 Step 2: Configuring settings...")
    settings_file = vscode_dir / "settings.json"
    settings = {}

    if settings_file.exists():
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Error reading settings.json: {e}")

    # Add GitLens automation settings
    gitlens_auto_settings = {
        "gitlens.followup.automation.enabled": True,
        "gitlens.followup.automation.fullauto": True,
        "gitlens.followup.automation.interval": 60,
        "gitlens.followup.automation.script": "scripts/python/jarvis_gitlens_followup_automation.py"
    }

    updated = False
    for key, value in gitlens_auto_settings.items():
        if key not in settings or settings[key] != value:
            settings[key] = value
            updated = True

    if updated:
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            print(f"   ✅ Updated settings in {settings_file}")
        except Exception as e:
            print(f"   ❌ Error writing settings.json: {e}")
    else:
        print(f"   ℹ️  Settings already configured")

    # 3. Create configuration file
    print("\n📝 Step 3: Creating configuration file...")
    config_dir = project_root / "config"
    config_dir.mkdir(exist_ok=True)

    config_file = config_dir / "gitlens_automatic_followup_config.json"
    config = {
        "enabled": True,
        "fullauto": True,
        "interval_seconds": 60,
        "auto_commit": True,
        "auto_push": True,
        "auto_pull": True,
        "auto_resolve_conflicts": True,
        "setup_date": datetime.now().isoformat(),
        "script": "scripts/python/jarvis_gitlens_followup_automation.py"
    }

    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        print(f"   ✅ Created configuration: {config_file}")
    except Exception as e:
        print(f"   ❌ Error creating config: {e}")

    # 4. Test the automation
    print("\n🧪 Step 4: Testing automation...")
    try:
        from jarvis_gitlens_followup_automation import JARVISGitLensFollowupAutomation

        automation = JARVISGitLensFollowupAutomation(fullauto=True)
        status = automation.get_status()

        if status["components"]["gitlens_automation"]:
            print("   ✅ GitLens automation component: OK")
        else:
            print("   ⚠️  GitLens automation component: Not available")

        if status["components"]["alert_handler"]:
            print("   ✅ Alert handler component: OK")
        else:
            print("   ⚠️  Alert handler component: Not available")

        print(f"   ✅ Fullauto mode: {'ENABLED' if status['fullauto'] else 'DISABLED'}")

    except Exception as e:
        print(f"   ⚠️  Could not test automation: {e}")

    # Summary
    print("\n" + "="*80)
    print("✅ AUTOMATIC GITLENS FOLLOW-UP HANDLING SETUP COMPLETE")
    print("="*80)
    print("\n📋 Summary:")
    print("   • VS Code task created: Runs on folder open")
    print("   • Settings configured: Fullauto mode enabled")
    print("   • Configuration file created")
    print("\n🚀 Usage:")
    print("   • Automatic: Follow-ups handled automatically when workspace opens")
    print("   • Manual: Run 'python scripts/python/jarvis_gitlens_followup_automation.py --handle'")
    print("   • Continuous: Run 'python scripts/python/jarvis_gitlens_followup_automation.py --monitor'")
    print("\n💡 To disable fullauto mode:")
    print("   python scripts/python/jarvis_gitlens_followup_automation.py --handle --no-fullauto")
    print()


if __name__ == "__main__":
    setup_automatic_followup()
