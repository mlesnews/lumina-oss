#!/usr/bin/env python3
"""
Deep Terminal Fix - Additional Autonomous Fixes for Exit Code 4294967295

This script applies additional fixes that may resolve the terminal issue,
including trace logging, alternative configurations, and registry checks.

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


class DeepTerminalFixer:
    """Deep terminal fixer with additional automated fixes."""

    def __init__(self):
        self.user_profile = Path(os.environ.get("USERPROFILE", ""))
        self.appdata_roaming = self.user_profile / "AppData" / "Roaming"
        self.fixes_applied: List[Dict[str, Any]] = []
        self.additional_fixes: List[Dict[str, Any]] = []

    def run_deep_fixes(self) -> Dict[str, Any]:
        """Run deep fixes for terminal issues."""
        logger.info("="*80)
        logger.info("DEEP TERMINAL FIX - EXIT CODE 4294967295")
        logger.info("="*80)
        logger.info("Applying additional automated fixes...")
        logger.info("")

        # 1. Enable trace logging for diagnostics
        self.enable_trace_logging()

        # 2. Try alternative terminal configurations
        self.configure_alternative_terminal_profiles()

        # 3. Check and fix registry settings if possible
        self.check_registry_settings()

        # 4. Test with different shell configurations
        self.test_alternative_shells()

        # 5. Generate report
        report = {
            "fixes_applied": self.fixes_applied,
            "additional_fixes": self.additional_fixes,
            "recommendations": self.generate_recommendations()
        }

        return report

    def enable_trace_logging(self):
        """Enable trace logging for terminal diagnostics."""
        logger.info("🔧 ENABLING TRACE LOGGING...")

        settings_files = [
            (self.appdata_roaming / "Cursor" / "User" / "settings.json", "Cursor"),
        ]

        for settings_file, editor_name in settings_files:
            if not settings_file.exists():
                continue

            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                changes = []

                # Enable trace logging
                if settings.get("terminal.integrated.trace") != True:
                    settings["terminal.integrated.trace"] = True
                    changes.append("trace enabled")

                if settings.get("terminal.integrated.logLevel") != "trace":
                    settings["terminal.integrated.logLevel"] = "trace"
                    changes.append("logLevel set to trace")

                if changes:
                    with open(settings_file, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=2, ensure_ascii=False)

                    logger.info(f"  ✅ Enabled trace logging for {editor_name}")
                    self.fixes_applied.append({
                        "fix": f"{editor_name} Trace Logging",
                        "status": "enabled",
                        "changes": changes
                    })
                else:
                    logger.info(f"  ✓ Trace logging already enabled for {editor_name}")

            except Exception as e:
                logger.error(f"  ❌ Error enabling trace logging: {e}")

    def configure_alternative_terminal_profiles(self):
        """Configure alternative terminal profiles as fallback."""
        logger.info("🔧 CONFIGURING ALTERNATIVE TERMINAL PROFILES...")

        settings_file = self.appdata_roaming / "Cursor" / "User" / "settings.json"

        if not settings_file.exists():
            return

        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)

            # Ensure we have both PowerShell and CMD profiles
            if "terminal.integrated.profiles.windows" not in settings:
                settings["terminal.integrated.profiles.windows"] = {}

            profiles = settings["terminal.integrated.profiles.windows"]

            changes = []

            # Add/update PowerShell profile
            if "PowerShell" not in profiles or profiles["PowerShell"].get("source") != "PowerShell":
                profiles["PowerShell"] = {
                    "source": "PowerShell",
                    "icon": "terminal-powershell"
                }
                changes.append("PowerShell profile configured")

            # Add/update CMD profile with explicit path
            if "Command Prompt" not in profiles:
                profiles["Command Prompt"] = {
                    "path": [
                        "${env:windir}\\System32\\cmd.exe"
                    ],
                    "args": [],
                    "icon": "terminal-cmd"
                }
                changes.append("CMD profile configured")

            # Add Git Bash if available
            git_bash_paths = [
                r"C:\Program Files\Git\bin\bash.exe",
                r"C:\Program Files (x86)\Git\bin\bash.exe",
            ]

            for git_bash_path in git_bash_paths:
                if os.path.exists(git_bash_path):
                    if "Git Bash" not in profiles:
                        profiles["Git Bash"] = {
                            "path": git_bash_path,
                            "icon": "terminal-bash"
                        }
                        changes.append("Git Bash profile added")
                    break

            # Set CMD as fallback default if PowerShell fails
            if "terminal.integrated.defaultProfile.windows" not in settings:
                settings["terminal.integrated.defaultProfile.windows"] = "Command Prompt"
                changes.append("Default profile set to CMD (fallback)")

            if changes:
                with open(settings_file, 'w', encoding='utf-8') as f:
                    json.dump(settings, f, indent=2, ensure_ascii=False)

                logger.info(f"  ✅ Configured alternative profiles: {', '.join(changes)}")
                self.fixes_applied.append({
                    "fix": "Alternative Terminal Profiles",
                    "status": "configured",
                    "changes": changes
                })
            else:
                logger.info("  ✓ Alternative profiles already configured")

        except Exception as e:
            logger.error(f"  ❌ Error configuring profiles: {e}")

    def check_registry_settings(self):
        """Check and fix registry settings if possible."""
        logger.info("🔧 CHECKING REGISTRY SETTINGS...")

        try:
            # Check for legacy console mode in registry
            # HKEY_CURRENT_USER\Console - UseLegacyConsole
            try:
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Console", 0, winreg.KEY_READ) as key:
                    try:
                        legacy_console = winreg.QueryValueEx(key, "UseLegacyConsole")[0]
                        if legacy_console == 1:
                            logger.info("  ⚠️  Legacy console mode is enabled in registry")
                            logger.info("      This may cause terminal issues")
                            self.additional_fixes.append({
                                "issue": "Legacy Console Mode",
                                "status": "detected",
                                "fix": "Set UseLegacyConsole to 0 in HKEY_CURRENT_USER\\Console",
                                "manual_required": True
                            })
                        else:
                            logger.info("  ✓ Legacy console mode is disabled")
                    except FileNotFoundError:
                        logger.info("  ✓ Legacy console mode not set (default is disabled)")
            except Exception as e:
                logger.warning(f"  ⚠️  Could not check registry: {e}")

        except Exception as e:
            logger.error(f"  ❌ Error checking registry: {e}")

    def test_alternative_shells(self):
        """Test alternative shell configurations."""
        logger.info("🔧 TESTING ALTERNATIVE SHELL CONFIGURATIONS...")

        shells = [
            ("PowerShell", r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe", ["-NoProfile", "-Command", "Write-Host 'Test'"]),
            ("CMD", r"C:\Windows\System32\cmd.exe", ["/c", "echo Test"]),
        ]

        # Check for PowerShell 7+
        pwsh_paths = [
            r"C:\Program Files\PowerShell\7\pwsh.exe",
            r"C:\Program Files (x86)\PowerShell\7\pwsh.exe",
        ]

        for pwsh_path in pwsh_paths:
            if os.path.exists(pwsh_path):
                shells.append(("PowerShell 7+", pwsh_path, ["-NoProfile", "-Command", "Write-Host 'Test'"]))
                break

        results = []
        for shell_name, shell_path, args in shells:
            try:
                result = subprocess.run(
                    [shell_path] + args,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    logger.info(f"  ✅ {shell_name} working: {shell_path}")
                    results.append({
                        "shell": shell_name,
                        "path": shell_path,
                        "status": "working"
                    })
                else:
                    logger.warning(f"  ⚠️  {shell_name} failed (exit: {result.returncode})")
                    results.append({
                        "shell": shell_name,
                        "path": shell_path,
                        "status": "failed",
                        "exit_code": result.returncode
                    })
            except Exception as e:
                logger.warning(f"  ⚠️  {shell_name} error: {e}")
                results.append({
                    "shell": shell_name,
                    "status": "error",
                    "error": str(e)
                })

        self.fixes_applied.append({
            "fix": "Alternative Shell Tests",
            "status": "completed",
            "results": results
        })

    def generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on findings."""
        recommendations = []

        # Check if trace logging is enabled
        recommendations.append({
            "priority": "HIGH",
            "action": "Check Output Panel for Terminal Errors",
            "instructions": "In Cursor: View → Output → Select 'Log (Window)' from dropdown → Look for terminal errors"
        })

        # Check compatibility mode
        recommendations.append({
            "priority": "CRITICAL",
            "action": "Check Compatibility Mode",
            "instructions": "Right-click Cursor.exe → Properties → Compatibility → Uncheck compatibility mode → Restart Cursor"
        })

        # Try CMD instead of PowerShell
        recommendations.append({
            "priority": "MEDIUM",
            "action": "Try Command Prompt Instead",
            "instructions": "In Cursor: Ctrl+Shift+P → 'Terminal: Select Default Profile' → Choose 'Command Prompt'"
        })

        # Check anti-virus
        recommendations.append({
            "priority": "HIGH",
            "action": "Check Anti-Virus Exclusions",
            "instructions": "Add Cursor terminal DLL files to anti-virus exclusions (see troubleshooting guide)"
        })

        return recommendations

    def save_report(self, report: Dict[str, Any], output_path: Optional[Path] = None):
        try:
            """Save fix report."""
            if output_path is None:
                output_path = project_root / "data" / "diagnostics" / "deep_terminal_fix_report.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"\n📄 Deep fix report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point."""
    fixer = DeepTerminalFixer()
    report = fixer.run_deep_fixes()
    report_path = fixer.save_report(report)

    logger.info("")
    logger.info("="*80)
    logger.info("DEEP FIX SUMMARY")
    logger.info("="*80)
    logger.info(f"✅ Fixes Applied: {len(fixer.fixes_applied)}")
    logger.info(f"⚠️  Additional Issues: {len(fixer.additional_fixes)}")
    logger.info(f"📋 Recommendations: {len(report.get('recommendations', []))}")
    logger.info("")
    logger.info("🔍 NEXT STEPS:")
    logger.info("   1. Check Output Panel → Log (Window) for detailed terminal errors")
    logger.info("   2. Try opening terminal again (Ctrl+`)")
    logger.info("   3. If still failing, check compatibility mode (CRITICAL)")
    logger.info("="*80)

    return 0


if __name__ == "__main__":


    sys.exit(main())