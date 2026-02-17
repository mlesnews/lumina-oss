#!/usr/bin/env python3
"""
Autonomous Terminal Fix Script - Exit Code 4294967295

This script autonomously fixes all fixable terminal issues without human intervention.
It makes decisions about what can be fixed programmatically and what requires manual steps.

Author: LUMINA Project
Date: 2026-01-11
"""

import os
import sys
import json
import subprocess
import platform
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

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


class AutonomousTerminalFixer:
    """Autonomous terminal fixer that makes decisions and fixes issues."""

    def __init__(self):
        self.user_profile = Path(os.environ.get("USERPROFILE", ""))
        self.appdata_roaming = self.user_profile / "AppData" / "Roaming"
        self.appdata_local = self.user_profile / "AppData" / "Local"
        self.fixes_applied: List[Dict[str, Any]] = []
        self.fixes_failed: List[Dict[str, Any]] = []
        self.manual_actions_required: List[Dict[str, Any]] = []
        self.decisions_made: List[Dict[str, Any]] = []

    def run_autonomous_fixes(self) -> Dict[str, Any]:
        """Run all autonomous fixes and make decisions."""
        logger.info("="*80)
        logger.info("AUTONOMOUS TERMINAL FIX - EXIT CODE 4294967295")
        logger.info("="*80)
        logger.info("Running all automated fixes without human intervention...")
        logger.info("")

        # 1. Fix PATH environment variable
        self.fix_path_environment()

        # 2. Optimize terminal settings
        self.optimize_terminal_settings()

        # 3. Test terminal configurations
        self.test_terminal_configurations()

        # 4. Check for fixable compatibility issues
        self.check_compatibility_issues()

        # 5. Generate decision report
        report = self.generate_decision_report()

        return report

    def fix_path_environment(self):
        """Fix invalid PATH entries programmatically."""
        logger.info("🔧 FIXING PATH ENVIRONMENT VARIABLE...")

        try:
            # Get current PATH
            current_path = os.environ.get("PATH", "")
            path_entries = [e.strip() for e in current_path.split(os.pathsep) if e.strip()]

            # Identify invalid entries
            valid_entries = []
            invalid_entries = []

            for entry in path_entries:
                if os.path.exists(entry):
                    valid_entries.append(entry)
                else:
                    invalid_entries.append(entry)

            if not invalid_entries:
                logger.info("  ✓ PATH is clean - no invalid entries found")
                self.fixes_applied.append({
                    "fix": "PATH Environment Variable",
                    "status": "no_action_needed",
                    "details": "No invalid entries found"
                })
                return

            logger.info(f"  ⚠️  Found {len(invalid_entries)} invalid PATH entries:")
            for entry in invalid_entries:
                logger.info(f"      - {entry}")

            # Decision: Try to fix via registry (requires admin, but worth trying)
            decision = {
                "issue": "Invalid PATH entries",
                "decision": "Attempt to fix via PowerShell registry command",
                "reason": "Can be fixed programmatically if user has admin rights or user-level PATH access"
            }
            self.decisions_made.append(decision)

            # Build new PATH
            new_path = os.pathsep.join(valid_entries)

            # Try to fix user-level PATH
            try:
                # Use PowerShell to update user PATH
                ps_command = f"""
                $currentPath = [Environment]::GetEnvironmentVariable('PATH', 'User')
                $entries = $currentPath -split ';' | Where-Object {{ $_.Trim() -ne '' }}
                $validEntries = $entries | Where-Object {{ Test-Path $_ }}
                $newPath = $validEntries -join ';'
                [Environment]::SetEnvironmentVariable('PATH', $newPath, 'User')
                Write-Output 'PATH updated successfully'
                """

                result = subprocess.run(
                    ["powershell", "-Command", ps_command],
                    capture_output=True,
                    text=True,
                    timeout=10
                )

                if result.returncode == 0:
                    logger.info("  ✅ Successfully fixed PATH environment variable")
                    self.fixes_applied.append({
                        "fix": "PATH Environment Variable",
                        "status": "fixed",
                        "invalid_entries_removed": invalid_entries,
                        "method": "PowerShell registry update"
                    })
                else:
                    logger.warning(f"  ⚠️  Could not fix PATH automatically: {result.stderr}")
                    self.fixes_failed.append({
                        "fix": "PATH Environment Variable",
                        "status": "failed",
                        "reason": "PowerShell command failed (may need admin rights)",
                        "error": result.stderr,
                        "manual_fix": "Edit PATH in System Properties → Environment Variables"
                    })
            except Exception as e:
                logger.warning(f"  ⚠️  Exception fixing PATH: {e}")
                self.fixes_failed.append({
                    "fix": "PATH Environment Variable",
                    "status": "failed",
                    "reason": str(e),
                    "manual_fix": "Edit PATH in System Properties → Environment Variables"
                })

        except Exception as e:
            logger.error(f"  ❌ Error checking PATH: {e}")
            self.fixes_failed.append({
                "fix": "PATH Environment Variable",
                "status": "error",
                "error": str(e)
            })

    def optimize_terminal_settings(self):
        """Optimize terminal settings in Cursor/VS Code."""
        logger.info("🔧 OPTIMIZING TERMINAL SETTINGS...")

        settings_files = [
            (self.appdata_roaming / "Cursor" / "User" / "settings.json", "Cursor"),
            (self.appdata_roaming / "Code" / "User" / "settings.json", "VS Code"),
        ]

        optimal_settings = {
            "terminal.integrated.defaultProfile.windows": "PowerShell",
            "terminal.integrated.profiles.windows": {
                "PowerShell": {
                    "source": "PowerShell",
                    "icon": "terminal-powershell"
                },
                "Command Prompt": {
                    "path": [
                        "${env:windir}\\System32\\cmd.exe"
                    ],
                    "args": [],
                    "icon": "terminal-cmd"
                }
            },
            "terminal.integrated.windowsEnableConpty": True,
            "terminal.integrated.shellIntegration.enabled": True,
            "terminal.integrated.trace": False,  # Only enable if debugging
            "terminal.integrated.logLevel": "info"
        }

        for settings_file, editor_name in settings_files:
            if not settings_file.exists():
                logger.info(f"  ⚠️  {editor_name} settings file not found: {settings_file}")
                continue

            try:
                # Read current settings
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)

                changes_made = []
                needs_update = False

                # Check and update terminal settings
                for key, value in optimal_settings.items():
                    if key not in settings or settings[key] != value:
                        settings[key] = value
                        changes_made.append(key)
                        needs_update = True

                if needs_update:
                    # Backup original
                    backup_file = settings_file.with_suffix('.json.backup')
                    if not backup_file.exists():
                        with open(backup_file, 'w', encoding='utf-8') as f:
                            json.dump(settings, f, indent=2)
                        logger.info(f"  📋 Created backup: {backup_file.name}")

                    # Write updated settings
                    with open(settings_file, 'w', encoding='utf-8') as f:
                        json.dump(settings, f, indent=2, ensure_ascii=False)

                    logger.info(f"  ✅ Optimized {editor_name} terminal settings")
                    logger.info(f"      Updated {len(changes_made)} settings: {', '.join(changes_made[:3])}...")

                    self.fixes_applied.append({
                        "fix": f"{editor_name} Terminal Settings",
                        "status": "optimized",
                        "settings_updated": changes_made,
                        "backup_created": str(backup_file)
                    })
                else:
                    logger.info(f"  ✓ {editor_name} terminal settings already optimal")
                    self.fixes_applied.append({
                        "fix": f"{editor_name} Terminal Settings",
                        "status": "already_optimal"
                    })

            except json.JSONDecodeError as e:
                logger.error(f"  ❌ {editor_name} settings file is corrupted: {e}")
                self.fixes_failed.append({
                    "fix": f"{editor_name} Terminal Settings",
                    "status": "error",
                    "reason": "Corrupted JSON",
                    "error": str(e),
                    "manual_fix": f"Fix JSON syntax in {settings_file}"
                })
            except Exception as e:
                logger.error(f"  ❌ Error optimizing {editor_name} settings: {e}")
                self.fixes_failed.append({
                    "fix": f"{editor_name} Terminal Settings",
                    "status": "error",
                    "error": str(e)
                })

    def test_terminal_configurations(self):
        """Test terminal configurations to verify they work."""
        logger.info("🔧 TESTING TERMINAL CONFIGURATIONS...")

        shells_to_test = [
            ("PowerShell", "powershell.exe", "-Command", "Write-Host 'Test'"),
            ("CMD", "cmd.exe", "/c", "echo Test"),
        ]

        test_results = []

        for shell_name, shell_exe, arg_flag, test_command in shells_to_test:
            try:
                shell_path = None

                # Find shell path
                if shell_exe == "powershell.exe":
                    shell_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
                elif shell_exe == "cmd.exe":
                    shell_path = r"C:\Windows\System32\cmd.exe"

                if not shell_path or not os.path.exists(shell_path):
                    logger.warning(f"  ⚠️  {shell_name} not found at expected path")
                    test_results.append({
                        "shell": shell_name,
                        "status": "not_found"
                    })
                    continue

                # Test shell
                result = subprocess.run(
                    [shell_path, arg_flag, test_command],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    logger.info(f"  ✅ {shell_name} test passed")
                    test_results.append({
                        "shell": shell_name,
                        "status": "working",
                        "path": shell_path
                    })
                else:
                    logger.warning(f"  ⚠️  {shell_name} test failed (exit code: {result.returncode})")
                    test_results.append({
                        "shell": shell_name,
                        "status": "failed",
                        "exit_code": result.returncode,
                        "error": result.stderr
                    })

            except subprocess.TimeoutExpired:
                logger.warning(f"  ⚠️  {shell_name} test timed out")
                test_results.append({
                    "shell": shell_name,
                    "status": "timeout"
                })
            except Exception as e:
                logger.error(f"  ❌ Error testing {shell_name}: {e}")
                test_results.append({
                    "shell": shell_name,
                    "status": "error",
                    "error": str(e)
                })

        self.fixes_applied.append({
            "fix": "Terminal Configuration Tests",
            "status": "completed",
            "test_results": test_results
        })

    def check_compatibility_issues(self):
        try:
            """Check for compatibility mode issues (can detect, but requires manual fix)."""
            logger.info("🔧 CHECKING COMPATIBILITY MODE ISSUES...")

            # Common executable paths
            executables = [
                self.appdata_local / "Programs" / "Cursor" / "Cursor.exe",
                Path(r"C:\Program Files\Cursor\Cursor.exe"),
                self.appdata_local / "Programs" / "Microsoft VS Code" / "Code.exe",
                Path(r"C:\Program Files\Microsoft VS Code\Code.exe"),
            ]

            found_executables = []
            for exe_path in executables:
                if exe_path.exists():
                    found_executables.append(exe_path)
                    logger.info(f"  ✓ Found: {exe_path}")

            # Decision: Cannot programmatically check/fix compatibility mode
            # But we can provide clear instructions
            decision = {
                "issue": "Compatibility Mode Check",
                "decision": "Cannot be fixed programmatically - requires GUI interaction",
                "reason": "Windows compatibility mode settings are stored in registry with specific permissions",
                "action": "Manual check required"
            }
            self.decisions_made.append(decision)

            if found_executables:
                logger.info("  ⚠️  Compatibility mode must be checked manually:")
                for exe_path in found_executables:
                    logger.info(f"      Right-click: {exe_path}")
                    logger.info(f"      Properties → Compatibility → Uncheck compatibility mode")

                self.manual_actions_required.append({
                    "action": "Check Compatibility Mode",
                    "priority": "HIGH",
                    "executables": [str(e) for e in found_executables],
                    "instructions": "Right-click each executable → Properties → Compatibility → Uncheck compatibility mode"
                })

        except Exception as e:
            self.logger.error(f"Error in check_compatibility_issues: {e}", exc_info=True)
            raise
    def generate_decision_report(self) -> Dict[str, Any]:
        """Generate comprehensive decision and fix report."""
        logger.info("")
        logger.info("="*80)
        logger.info("AUTONOMOUS FIX DECISION REPORT")
        logger.info("="*80)

        report = {
            "summary": {
                "fixes_applied": len(self.fixes_applied),
                "fixes_failed": len(self.fixes_failed),
                "manual_actions_required": len(self.manual_actions_required),
                "decisions_made": len(self.decisions_made)
            },
            "fixes_applied": self.fixes_applied,
            "fixes_failed": self.fixes_failed,
            "manual_actions_required": self.manual_actions_required,
            "decisions_made": self.decisions_made
        }

        # Print summary
        logger.info(f"\n📊 SUMMARY:")
        logger.info(f"   ✅ Fixes Applied: {report['summary']['fixes_applied']}")
        logger.info(f"   ❌ Fixes Failed: {report['summary']['fixes_failed']}")
        logger.info(f"   ⚠️  Manual Actions Required: {report['summary']['manual_actions_required']}")
        logger.info(f"   🤔 Decisions Made: {report['summary']['decisions_made']}")

        # Print fixes applied
        if self.fixes_applied:
            logger.info(f"\n✅ FIXES APPLIED:")
            for fix in self.fixes_applied:
                logger.info(f"   - {fix.get('fix', 'Unknown')}: {fix.get('status', 'Unknown')}")

        # Print fixes failed
        if self.fixes_failed:
            logger.info(f"\n❌ FIXES FAILED:")
            for fix in self.fixes_failed:
                logger.info(f"   - {fix.get('fix', 'Unknown')}: {fix.get('reason', 'Unknown error')}")

        # Print manual actions
        if self.manual_actions_required:
            logger.info(f"\n⚠️  MANUAL ACTIONS REQUIRED (Cannot be automated):")
            for action in self.manual_actions_required:
                logger.info(f"   [{action.get('priority', 'UNKNOWN')}] {action.get('action', 'Unknown')}")
                if 'instructions' in action:
                    logger.info(f"      → {action['instructions']}")

        # Print decisions
        if self.decisions_made:
            logger.info(f"\n🤔 DECISIONS MADE:")
            for decision in self.decisions_made:
                logger.info(f"   Issue: {decision.get('issue', 'Unknown')}")
                logger.info(f"   Decision: {decision.get('decision', 'Unknown')}")
                logger.info(f"   Reason: {decision.get('reason', 'N/A')}")
                logger.info("")

        logger.info("="*80)

        return report

    def save_report(self, report: Dict[str, Any], output_path: Optional[Path] = None):
        try:
            """Save fix report to JSON file."""
            if output_path is None:
                output_path = project_root / "data" / "diagnostics" / "autonomous_terminal_fix_report.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"\n📄 Full report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point."""
    fixer = AutonomousTerminalFixer()
    report = fixer.run_autonomous_fixes()
    report_path = fixer.save_report(report)

    # Return exit code based on results
    if report['summary']['fixes_failed'] > 0 or report['summary']['manual_actions_required'] > 0:
        return 1  # Some issues remain
    return 0  # All automated fixes successful


if __name__ == "__main__":


    sys.exit(main())