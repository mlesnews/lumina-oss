#!/usr/bin/env python3
"""
Final Terminal Fix - Attempt Programmatic Compatibility Mode Fix

This script attempts to fix compatibility mode programmatically via registry,
and applies a CMD fallback configuration as immediate workaround.

Author: LUMINA Project
Date: 2026-01-11
"""

import os
import sys
import json
import subprocess
import winreg
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')


class FinalTerminalFixer:
    """Final terminal fixer with compatibility mode attempt."""

    def __init__(self):
        self.user_profile = Path(os.environ.get("USERPROFILE", ""))
        self.appdata_roaming = self.user_profile / "AppData" / "Roaming"
        self.appdata_local = self.user_profile / "AppData" / "Local"
        self.fixes_applied: List[Dict[str, Any]] = []

    def run_final_fixes(self) -> Dict[str, Any]:
        """Run final fixes including compatibility mode attempt."""
        logger.info("="*80)
        logger.info("FINAL TERMINAL FIX - COMPATIBILITY MODE & FALLBACK")
        logger.info("="*80)
        logger.info("")

        # 1. Set CMD as default (immediate workaround)
        self.set_cmd_as_default()

        # 2. Attempt to fix compatibility mode via registry
        self.attempt_compatibility_mode_fix()

        # 3. Create emergency terminal configuration
        self.create_emergency_config()

        report = {
            "fixes_applied": self.fixes_applied,
            "status": "complete"
        }

        return report

    def set_cmd_as_default(self):
        """Set CMD as default terminal (more reliable than PowerShell)."""
        logger.info("🔧 SETTING CMD AS DEFAULT TERMINAL (WORKAROUND)...")

        settings_file = self.appdata_roaming / "Cursor" / "User" / "settings.json"

        if not settings_file.exists():
            logger.warning("  ⚠️  Cursor settings file not found")
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Set CMD as default
            current_default = settings.get("terminal.integrated.defaultProfile.windows", "")

            if current_default != "Command Prompt":
                settings["terminal.integrated.defaultProfile.windows"] = "Command Prompt"

                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)

                logger.info("  ✅ Set Command Prompt as default terminal")
                logger.info("      This is more reliable than PowerShell for this issue")
                self.fixes_applied.append({
                    "fix": "Default Terminal Profile",
                    "status": "changed_to_cmd",
                    "reason": "CMD is more reliable than PowerShell for exit code 4294967295"
                })
            else:
                logger.info("  ✓ CMD already set as default")

        except Exception as e:
            logger.error(f"  ❌ Error setting CMD as default: {e}")

    def attempt_compatibility_mode_fix(self):
        """Attempt to fix compatibility mode programmatically."""
        logger.info("🔧 ATTEMPTING COMPATIBILITY MODE FIX...")

        executables = [
            Path(r"C:\Program Files\Cursor\Cursor.exe"),
            self.appdata_local / "Programs" / "Microsoft VS Code" / "Code.exe",
        ]

        for exe_path in executables:
            if not exe_path.exists():
                continue

            logger.info(f"  Checking: {exe_path}")

            try:
                # Try to read compatibility flags from registry
                # HKEY_CURRENT_USER\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers
                reg_path = r"Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"

                try:
                    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ | winreg.KEY_WRITE) as key:
                        try:
                            # Check if compatibility flags exist
                            flags, _ = winreg.QueryValueEx(key, str(exe_path))

                            if flags:
                                logger.info(f"    ⚠️  Compatibility flags found: {flags}")

                                # Try to remove compatibility flags
                                try:
                                    winreg.DeleteValue(key, str(exe_path))
                                    logger.info(f"    ✅ Removed compatibility flags for {exe_path.name}")
                                    self.fixes_applied.append({
                                        "fix": f"Compatibility Mode - {exe_path.name}",
                                        "status": "removed",
                                        "executable": str(exe_path)
                                    })
                                except Exception as e:
                                    logger.warning(f"    ⚠️  Could not remove flags: {e}")
                                    logger.info(f"    → Manual removal required: Registry key {reg_path}")

                        except FileNotFoundError:
                            logger.info(f"    ✓ No compatibility flags found (good!)")
                        except Exception as e:
                            logger.warning(f"    ⚠️  Error reading flags: {e}")

                except PermissionError:
                    logger.warning(f"    ⚠️  Permission denied - may need admin rights")
                    logger.info(f"    → Manual fix required: Right-click {exe_path} → Properties → Compatibility")
                except FileNotFoundError:
                    logger.info(f"    ✓ Registry key doesn't exist (no compatibility mode set)")
                except Exception as e:
                    logger.warning(f"    ⚠️  Error accessing registry: {e}")

            except Exception as e:
                logger.error(f"  ❌ Error checking {exe_path}: {e}")

    def create_emergency_config(self):
        """Create emergency terminal configuration."""
        logger.info("🔧 CREATING EMERGENCY TERMINAL CONFIGURATION...")

        settings_file = self.appdata_roaming / "Cursor" / "User" / "settings.json"

        if not settings_file.exists():
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Ensure minimal, reliable terminal configuration
            emergency_config = {
                "terminal.integrated.defaultProfile.windows": "Command Prompt",
                "terminal.integrated.profiles.windows": {
                    "Command Prompt": {
                        "path": [
                            "${env:windir}\\System32\\cmd.exe"
                        ],
                        "args": [],
                        "icon": "terminal-cmd"
                    }
                },
                "terminal.integrated.windowsEnableConpty": True,
                "terminal.integrated.shellIntegration.enabled": False,  # Disable if causing issues
                "terminal.integrated.trace": True,
                "terminal.integrated.logLevel": "trace"
            }

            changes = []
            for key, value in emergency_config.items():
                if settings.get(key) != value:
                    settings[key] = value
                    changes.append(key)

            if changes:
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)

                logger.info(f"  ✅ Applied emergency configuration ({len(changes)} changes)")
                self.fixes_applied.append({
                    "fix": "Emergency Terminal Configuration",
                    "status": "applied",
                    "changes": changes
                })
            else:
                logger.info("  ✓ Emergency configuration already applied")

        except Exception as e:
            logger.error(f"  ❌ Error creating emergency config: {e}")

    def save_report(self, report: Dict[str, Any], output_path: Optional[Path] = None):
        try:
            """Save fix report."""
            if output_path is None:
                output_path = project_root / "data" / "diagnostics" / "final_terminal_fix_report.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"\n📄 Final fix report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point."""
    fixer = FinalTerminalFixer()
    report = fixer.run_final_fixes()
    report_path = fixer.save_report(report)

    logger.info("")
    logger.info("="*80)
    logger.info("FINAL FIX SUMMARY")
    logger.info("="*80)
    logger.info(f"✅ Fixes Applied: {len(fixer.fixes_applied)}")
    logger.info("")
    logger.info("🎯 IMMEDIATE ACTIONS:")
    logger.info("   1. RESTART CURSOR (required for changes to take effect)")
    logger.info("   2. Try opening terminal (Ctrl+`)")
    logger.info("   3. If CMD works, PowerShell issue is confirmed")
    logger.info("   4. Check Output Panel → Log (Window) for errors")
    logger.info("")
    logger.info("⚠️  IF STILL FAILING:")
    logger.info("   → Compatibility mode MUST be checked manually")
    logger.info("   → Right-click Cursor.exe → Properties → Compatibility")
    logger.info("   → Uncheck compatibility mode → Restart")
    logger.info("="*80)

    return 0


if __name__ == "__main__":


    sys.exit(main())