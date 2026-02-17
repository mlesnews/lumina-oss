#!/usr/bin/env python3
"""
JARVIS Comprehensive Terminal Fix
Comprehensive investigation and fix for all terminal startup sources.

Tags: #CURSOR #TERMINAL #STARTUP #FIX @AUTO
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISComprehensiveTerminalFix")


class ComprehensiveTerminalFix:
    """
    Comprehensive investigation and fix for all terminal startup sources.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.cursor_dir = project_root / ".cursor"

        self.logger.info("✅ Comprehensive Terminal Fix initialized")

    def investigate_all_sources(self) -> Dict[str, Any]:
        """Investigate all possible terminal startup sources"""
        self.logger.info("="*80)
        self.logger.info("INVESTIGATING ALL TERMINAL STARTUP SOURCES")
        self.logger.info("="*80)

        findings = {
            "tasks_json": [],
            "settings_json": [],
            "extensions": [],
            "workspace_settings": [],
            "user_settings": []
        }

        # Check tasks.json
        tasks_file = self.cursor_dir / "tasks.json"
        if tasks_file.exists():
            try:
                with open(tasks_file, 'r', encoding='utf-8') as f:
                    tasks = json.load(f)
                    for task in tasks.get("tasks", []):
                        if task.get("runOptions", {}).get("runOn") == "folderOpen":
                            findings["tasks_json"].append({
                                "label": task.get("label"),
                                "command": task.get("command"),
                                "runOn": "folderOpen"
                            })
            except Exception as e:
                self.logger.error(f"❌ Failed to read tasks.json: {e}")

        # Check settings.json for terminal-related settings
        settings_file = self.cursor_dir / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    # Check for terminal auto-start settings
                    for key, value in settings.items():
                        if "terminal" in key.lower() and ("auto" in key.lower() or "start" in key.lower()):
                            findings["settings_json"].append({
                                "key": key,
                                "value": value
                            })
            except Exception as e:
                self.logger.error(f"❌ Failed to read settings.json: {e}")

        # Check extensions.json
        extensions_file = self.cursor_dir / "extensions.json"
        if extensions_file.exists():
            try:
                with open(extensions_file, 'r', encoding='utf-8') as f:
                    extensions = json.load(f)
                    # Note: Extensions themselves don't auto-start terminals, but they might have settings
                    findings["extensions"] = extensions.get("recommendations", [])
            except Exception as e:
                self.logger.error(f"❌ Failed to read extensions.json: {e}")

        # Summary
        total_findings = sum(len(v) for v in findings.values())
        self.logger.info(f"📋 Found {total_findings} potential terminal startup sources:")
        self.logger.info(f"   - tasks.json: {len(findings['tasks_json'])}")
        self.logger.info(f"   - settings.json: {len(findings['settings_json'])}")
        self.logger.info(f"   - extensions: {len(findings['extensions'])}")

        return findings

    def fix_all_sources(self) -> Dict[str, Any]:
        """Fix all identified terminal startup sources"""
        self.logger.info("="*80)
        self.logger.info("FIXING ALL TERMINAL STARTUP SOURCES")
        self.logger.info("="*80)

        findings = self.investigate_all_sources()
        fixes_applied = []

        # Fix tasks.json
        if findings["tasks_json"]:
            from jarvis_cursor_terminal_manager import CursorTerminalManager
            manager = CursorTerminalManager(self.project_root)
            if manager.disable_auto_start():
                fixes_applied.append("tasks.json auto-start disabled")

        # Fix settings.json (if any terminal auto-start settings found)
        if findings["settings_json"]:
            settings_file = self.cursor_dir / "settings.json"
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                modified = False
                for finding in findings["settings_json"]:
                    key = finding["key"]
                    # Disable auto-start settings
                    if settings.get(key) is True:
                        settings[key] = False
                        modified = True
                        fixes_applied.append(f"Disabled {key} in settings.json")

                if modified:
                    # Backup
                    backup_file = settings_file.with_suffix('.json.backup')
                    with open(backup_file, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=2)

                    # Write updated
                    with open(settings_file, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=2)

                    self.logger.info("✅ Updated settings.json")
            except Exception as e:
                self.logger.error(f"❌ Failed to update settings.json: {e}")

        return {
            "success": len(fixes_applied) > 0,
            "findings": findings,
            "fixes_applied": fixes_applied
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Comprehensive terminal startup fix")
        parser.add_argument("--investigate", action="store_true", help="Investigate all sources")
        parser.add_argument("--fix", action="store_true", help="Fix all sources")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        fixer = ComprehensiveTerminalFix(project_root)

        if args.investigate:
            findings = fixer.investigate_all_sources()
            print(json.dumps(findings, indent=2, default=str))
        elif args.fix:
            result = fixer.fix_all_sources()
            print(json.dumps(result, indent=2, default=str))
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()