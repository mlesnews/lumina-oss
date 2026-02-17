#!/usr/bin/env python3
"""
Comprehensive Terminal Exit Code 4294967295 Diagnostic Script

This script checks ALL troubleshooting steps for VS Code/Cursor terminal issues.
Run this to get a complete diagnostic report.

Author: LUMINA Project
Date: 2026-01-11
"""

import os
import sys
import json
import subprocess
import platform
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
    logging.basicConfig(level=logging.INFO)


class TerminalDiagnostic:
    """Comprehensive terminal diagnostic checker."""

    def __init__(self):
        self.results: Dict[str, Any] = {
            "system_info": {},
            "shell_checks": {},
            "settings_checks": {},
            "compatibility_checks": {},
            "process_checks": {},
            "recommendations": []
        }
        self.user_profile = Path(os.environ.get("USERPROFILE", ""))
        self.appdata_roaming = self.user_profile / "AppData" / "Roaming"

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all diagnostic checks."""
        logger.info("Starting comprehensive terminal diagnostic...")

        self.check_system_info()
        self.check_shell_availability()
        self.check_vscode_settings()
        self.check_compatibility_mode()
        self.check_processes()
        self.check_environment_variables()
        self.generate_recommendations()

        return self.results

    def check_system_info(self):
        """Check system information."""
        logger.info("Checking system information...")

        self.results["system_info"] = {
            "os": platform.system(),
            "os_version": platform.version(),
            "os_release": platform.release(),
            "architecture": platform.machine(),
            "python_version": platform.python_version(),
            "user_profile": str(self.user_profile),
            "appdata_roaming": str(self.appdata_roaming)
        }

    def check_shell_availability(self):
        """Check if shells are available."""
        logger.info("Checking shell availability...")

        shells = {
            "PowerShell 5.1": r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
            "CMD": r"C:\Windows\System32\cmd.exe",
            "PowerShell 7+": None  # Will check via command
        }

        shell_results = {}

        for name, path in shells.items():
            if path:
                exists = os.path.exists(path)
                shell_results[name] = {
                    "exists": exists,
                    "path": path
                }

                if exists:
                    # Try to get version info
                    try:
                        if "PowerShell" in name:
                            result = subprocess.run(
                                [path, "-Command", "$PSVersionTable.PSVersion"],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            shell_results[name]["version_check"] = result.returncode == 0
                        else:
                            result = subprocess.run(
                                [path, "/c", "echo test"],
                                capture_output=True,
                                text=True,
                                timeout=5
                            )
                            shell_results[name]["version_check"] = result.returncode == 0
                    except Exception as e:
                        shell_results[name]["version_check_error"] = str(e)
            else:
                # Check for PowerShell 7+
                try:
                    result = subprocess.run(
                        ["pwsh", "--version"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    shell_results[name] = {
                        "exists": result.returncode == 0,
                        "version": result.stdout.strip() if result.returncode == 0 else None
                    }
                except FileNotFoundError:
                    shell_results[name] = {"exists": False}
                except Exception as e:
                    shell_results[name] = {"exists": False, "error": str(e)}

        self.results["shell_checks"] = shell_results

    def check_vscode_settings(self):
        """Check VS Code/Cursor settings."""
        logger.info("Checking VS Code/Cursor settings...")

        settings_files = [
            self.appdata_roaming / "Code" / "User" / "settings.json",
            self.appdata_roaming / "Cursor" / "User" / "settings.json",
        ]

        settings_results = {}

        for settings_file in settings_files:
            if settings_file.exists():
                try:
                    with open(settings_file, 'r', encoding='utf-8') as f:
                        settings = json.load(f)

                    terminal_settings = {
                        k: v for k, v in settings.items()
                        if 'terminal' in k.lower()
                    }

                    settings_results[str(settings_file)] = {
                        "exists": True,
                        "terminal_settings": terminal_settings,
                        "all_settings_count": len(settings)
                    }
                except json.JSONDecodeError as e:
                    settings_results[str(settings_file)] = {
                        "exists": True,
                        "error": f"Invalid JSON: {e}",
                        "corrupted": True
                    }
                except Exception as e:
                    settings_results[str(settings_file)] = {
                        "exists": True,
                        "error": str(e)
                    }
            else:
                settings_results[str(settings_file)] = {"exists": False}

        self.results["settings_checks"] = settings_results

    def check_compatibility_mode(self):
        try:
            """Check for compatibility mode (requires manual check note)."""
            logger.info("Checking compatibility mode...")

            # Common VS Code/Cursor paths
            possible_paths = [
                self.user_profile / "AppData" / "Local" / "Programs" / "Cursor" / "Cursor.exe",
                self.user_profile / "AppData" / "Local" / "Programs" / "Microsoft VS Code" / "Code.exe",
                Path(r"C:\Program Files\Microsoft VS Code\Code.exe"),
                Path(r"C:\Program Files\Cursor\Cursor.exe"),
            ]

            compatibility_results = {}

            for exe_path in possible_paths:
                if exe_path.exists():
                    compatibility_results[str(exe_path)] = {
                        "exists": True,
                        "note": "Compatibility mode must be checked manually: Right-click → Properties → Compatibility tab",
                        "size": exe_path.stat().st_size,
                        "modified": exe_path.stat().st_mtime
                    }

            if not compatibility_results:
                compatibility_results["note"] = "No VS Code/Cursor executables found in common locations"

            self.results["compatibility_checks"] = compatibility_results

        except Exception as e:
            self.logger.error(f"Error in check_compatibility_mode: {e}", exc_info=True)
            raise
    def check_processes(self):
        """Check for running processes."""
        logger.info("Checking running processes...")

        process_names = ["code", "cursor", "powershell", "pwsh", "cmd", "conhost"]

        try:
            result = subprocess.run(
                ["tasklist", "/FO", "CSV"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[1:]  # Skip header
                found_processes = []

                for line in lines:
                    if any(name in line.lower() for name in process_names):
                        # Parse CSV (simple split, assuming no commas in process names)
                        parts = line.split(',')
                        if len(parts) >= 2:
                            process_name = parts[0].strip('"')
                            pid = parts[1].strip('"')
                            found_processes.append({
                                "name": process_name,
                                "pid": pid
                            })

                self.results["process_checks"] = {
                    "found_processes": found_processes,
                    "count": len(found_processes)
                }
            else:
                self.results["process_checks"] = {
                    "error": "Failed to get process list",
                    "returncode": result.returncode
                }
        except Exception as e:
            self.results["process_checks"] = {"error": str(e)}

    def check_environment_variables(self):
        try:
            """Check environment variables."""
            logger.info("Checking environment variables...")

            env_vars = {
                "PATH": os.environ.get("PATH", ""),
                "PSModulePath": os.environ.get("PSModulePath", ""),
                "USERPROFILE": os.environ.get("USERPROFILE", ""),
                "APPDATA": os.environ.get("APPDATA", ""),
            }

            # Check PATH for invalid entries
            path_entries = env_vars["PATH"].split(os.pathsep)
            invalid_paths = []

            for path_entry in path_entries:
                if path_entry and not os.path.exists(path_entry):
                    invalid_paths.append(path_entry)

            self.results["environment_checks"] = {
                "env_vars": {k: v for k, v in env_vars.items() if k != "PATH"},
                "path_entry_count": len(path_entries),
                "invalid_path_entries": invalid_paths,
                "invalid_path_count": len(invalid_paths)
            }

        except Exception as e:
            self.logger.error(f"Error in check_environment_variables: {e}", exc_info=True)
            raise
    def generate_recommendations(self):
        """Generate recommendations based on findings."""
        logger.info("Generating recommendations...")

        recommendations = []

        # Check shell availability
        shell_checks = self.results.get("shell_checks", {})
        if not shell_checks.get("PowerShell 5.1", {}).get("exists"):
            recommendations.append({
                "priority": "HIGH",
                "issue": "PowerShell 5.1 not found",
                "fix": "Reinstall PowerShell or use Command Prompt as default terminal"
            })

        # Check settings
        settings_checks = self.results.get("settings_checks", {})
        for settings_file, settings_info in settings_checks.items():
            if settings_info.get("corrupted"):
                recommendations.append({
                    "priority": "HIGH",
                    "issue": f"Corrupted settings file: {settings_file}",
                    "fix": "Fix JSON syntax errors in settings.json"
                })

        # Check environment
        env_checks = self.results.get("environment_checks", {})
        if env_checks.get("invalid_path_count", 0) > 0:
            recommendations.append({
                "priority": "MEDIUM",
                "issue": f"Found {env_checks['invalid_path_count']} invalid PATH entries",
                "fix": "Clean up PATH environment variable"
            })

        # General recommendations
        recommendations.extend([
            {
                "priority": "HIGH",
                "issue": "Compatibility mode may be enabled",
                "fix": "Right-click VS Code/Cursor executable → Properties → Compatibility → Uncheck compatibility mode"
            },
            {
                "priority": "HIGH",
                "issue": "Anti-virus may be blocking terminal",
                "fix": "Add terminal DLL files to anti-virus exclusions (see troubleshooting guide)"
            },
            {
                "priority": "MEDIUM",
                "issue": "Legacy console mode may be enabled",
                "fix": "Open cmd.exe → Right-click title bar → Properties → Options → Uncheck 'Use legacy console'"
            },
            {
                "priority": "LOW",
                "issue": "Try Command Prompt instead of PowerShell",
                "fix": "Change default terminal profile to Command Prompt in VS Code settings"
            }
        ])

        self.results["recommendations"] = recommendations

    def print_report(self):
        """Print diagnostic report."""
        print("\n" + "="*80)
        print("TERMINAL EXIT CODE 4294967295 - COMPREHENSIVE DIAGNOSTIC REPORT")
        print("="*80 + "\n")

        # System Info
        print("SYSTEM INFORMATION:")
        print("-" * 80)
        for key, value in self.results["system_info"].items():
            print(f"  {key}: {value}")
        print()

        # Shell Checks
        print("SHELL AVAILABILITY:")
        print("-" * 80)
        for shell_name, shell_info in self.results["shell_checks"].items():
            status = "✓ AVAILABLE" if shell_info.get("exists") else "✗ NOT FOUND"
            print(f"  {shell_name}: {status}")
            if shell_info.get("path"):
                print(f"    Path: {shell_info['path']}")
        print()

        # Settings Checks
        print("VS CODE/CURSOR SETTINGS:")
        print("-" * 80)
        for settings_file, settings_info in self.results["settings_checks"].items():
            if settings_info.get("exists"):
                print(f"  ✓ Found: {settings_file}")
                terminal_settings = settings_info.get("terminal_settings", {})
                if terminal_settings:
                    print(f"    Terminal settings found: {len(terminal_settings)}")
                    for key in list(terminal_settings.keys())[:5]:  # Show first 5
                        print(f"      - {key}")
                else:
                    print("    No terminal-specific settings found")
            else:
                print(f"  ✗ Not found: {settings_file}")
        print()

        # Compatibility Checks
        print("COMPATIBILITY MODE CHECK:")
        print("-" * 80)
        for exe_path, exe_info in self.results["compatibility_checks"].items():
            if exe_info.get("exists"):
                print(f"  ✓ Found executable: {exe_path}")
                print(f"    {exe_info.get('note', '')}")
        print()

        # Process Checks
        print("RUNNING PROCESSES:")
        print("-" * 80)
        process_checks = self.results.get("process_checks", {})
        if "found_processes" in process_checks:
            processes = process_checks["found_processes"]
            print(f"  Found {len(processes)} relevant processes:")
            for proc in processes[:10]:  # Show first 10
                print(f"    - {proc['name']} (PID: {proc['pid']})")
        else:
            print(f"  Error: {process_checks.get('error', 'Unknown error')}")
        print()

        # Environment Checks
        print("ENVIRONMENT VARIABLES:")
        print("-" * 80)
        env_checks = self.results.get("environment_checks", {})
        invalid_count = env_checks.get("invalid_path_count", 0)
        if invalid_count > 0:
            print(f"  ⚠ Found {invalid_count} invalid PATH entries:")
            for invalid_path in env_checks.get("invalid_path_entries", [])[:10]:
                print(f"    - {invalid_path}")
        else:
            print("  ✓ No invalid PATH entries found")
        print()

        # Recommendations
        print("RECOMMENDATIONS:")
        print("-" * 80)
        recommendations = self.results.get("recommendations", [])

        # Group by priority
        high_priority = [r for r in recommendations if r["priority"] == "HIGH"]
        medium_priority = [r for r in recommendations if r["priority"] == "MEDIUM"]
        low_priority = [r for r in recommendations if r["priority"] == "LOW"]

        if high_priority:
            print("\n  🔴 HIGH PRIORITY:")
            for i, rec in enumerate(high_priority, 1):
                print(f"\n    {i}. {rec['issue']}")
                print(f"       Fix: {rec['fix']}")

        if medium_priority:
            print("\n  🟡 MEDIUM PRIORITY:")
            for i, rec in enumerate(medium_priority, 1):
                print(f"\n    {i}. {rec['issue']}")
                print(f"       Fix: {rec['fix']}")

        if low_priority:
            print("\n  🟢 LOW PRIORITY:")
            for i, rec in enumerate(low_priority, 1):
                print(f"\n    {i}. {rec['issue']}")
                print(f"       Fix: {rec['fix']}")

        print("\n" + "="*80)
        print("For detailed troubleshooting guide, see:")
        print("docs/troubleshooting/VS_CODE_TERMINAL_EXIT_4294967295.md")
        print("="*80 + "\n")

    def save_report(self, output_path: Optional[Path] = None):
        try:
            """Save diagnostic report to JSON file."""
            if output_path is None:
                output_path = project_root / "data" / "diagnostics" / "terminal_diagnostic_report.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.results, f, indent=2, default=str)

            logger.info(f"Diagnostic report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point."""
    diagnostic = TerminalDiagnostic()
    diagnostic.run_all_checks()
    diagnostic.print_report()

    # Save report
    report_path = diagnostic.save_report()
    print(f"\nFull diagnostic report saved to: {report_path}")

    return 0


if __name__ == "__main__":


    sys.exit(main())