#!/usr/bin/env python3
"""
ProtonPass CLI Reinstallation Helper
Assists with uninstalling and reinstalling ProtonPass CLI to fix persistent issues

Tags: #PROTONPASS #REINSTALL #HELPDESK #JARVIS
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ProtonPassCLIReinstallHelper")


class ProtonPassCLIReinstallHelper:
    """
    Helper for ProtonPass CLI reinstallation

    Provides steps and automation for reinstalling ProtonPass CLI
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize reinstall helper"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.protonpass_paths = {
            "cli": Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe"),
            "app_dir": Path(r"C:\Users\mlesn\AppData\Local\ProtonPass"),
            "config": Path.home() / ".protonpass"
        }

        logger.info("=" * 70)
        logger.info("🔧 PROTONPASS CLI REINSTALLATION HELPER")
        logger.info("=" * 70)
        logger.info("")

    def check_current_installation(self) -> Dict[str, Any]:
        """Check current ProtonPass installation"""
        logger.info("🔍 Checking current installation...")

        status = {
            "cli_exists": self.protonpass_paths["cli"].exists(),
            "app_dir_exists": self.protonpass_paths["app_dir"].exists(),
            "config_exists": self.protonpass_paths["config"].exists(),
            "cli_version": None,
            "issues": []
        }

        if status["cli_exists"]:
            try:
                result = subprocess.run(
                    [str(self.protonpass_paths["cli"]), "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    status["cli_version"] = result.stdout.strip()
                    logger.info(f"   ✅ CLI found: {status['cli_version']}")
                else:
                    status["issues"].append("CLI exists but version check failed")
                    logger.warning("   ⚠️  CLI exists but version check failed")
            except Exception as e:
                status["issues"].append(f"CLI version check error: {e}")
                logger.error(f"   ❌ CLI version check error: {e}")
        else:
            status["issues"].append("CLI not found at expected location")
            logger.warning("   ⚠️  CLI not found")

        return status

    def generate_uninstall_instructions(self) -> Dict[str, Any]:
        """Generate uninstall instructions"""
        logger.info("📋 Generating uninstall instructions...")

        instructions = {
            "method": "manual",
            "steps": [],
            "backup_needed": True,
            "warnings": []
        }

        # Step 1: Backup (if needed)
        instructions["steps"].append({
            "step": 1,
            "action": "backup",
            "description": "Backup ProtonPass data (if any local data exists)",
            "command": None,
            "manual": True
        })

        # Step 2: Close ProtonPass processes
        instructions["steps"].append({
            "step": 2,
            "action": "close_processes",
            "description": "Close all ProtonPass processes",
            "command": "Get-Process | Where-Object {$_.ProcessName -eq 'ProtonPass'} | Stop-Process -Force",
            "manual": False
        })

        # Step 3: Uninstall via Windows
        instructions["steps"].append({
            "step": 3,
            "action": "uninstall",
            "description": "Uninstall ProtonPass via Windows Settings",
            "command": None,
            "manual": True,
            "details": [
                "Open Windows Settings > Apps > Apps & features",
                "Search for 'ProtonPass'",
                "Click 'Uninstall'",
                "Follow uninstall wizard"
            ]
        })

        # Step 4: Remove remaining directories
        instructions["steps"].append({
            "step": 4,
            "action": "cleanup",
            "description": "Remove remaining ProtonPass directories",
            "command": f"Remove-Item -Path '{self.protonpass_paths['app_dir']}' -Recurse -Force -ErrorAction SilentlyContinue",
            "manual": False,
            "warnings": ["This will remove all ProtonPass local data"]
        })

        # Step 5: Remove config files
        instructions["steps"].append({
            "step": 5,
            "action": "cleanup_config",
            "description": "Remove ProtonPass config files",
            "command": f"Remove-Item -Path '{self.protonpass_paths['config']}' -Recurse -Force -ErrorAction SilentlyContinue",
            "manual": False
        })

        instructions["warnings"] = [
            "Backup any important data before uninstalling",
            "You will need to re-authenticate after reinstall",
            "Local config will be lost"
        ]

        return instructions

    def generate_reinstall_instructions(self) -> Dict[str, Any]:
        """Generate reinstall instructions"""
        logger.info("📋 Generating reinstall instructions...")

        instructions = {
            "method": "download_and_install",
            "steps": [],
            "download_url": "https://proton.me/pass/download",
            "notes": []
        }

        # Step 1: Download
        instructions["steps"].append({
            "step": 1,
            "action": "download",
            "description": "Download ProtonPass installer",
            "url": "https://proton.me/pass/download",
            "manual": True
        })

        # Step 2: Install
        instructions["steps"].append({
            "step": 2,
            "action": "install",
            "description": "Run installer and follow setup wizard",
            "manual": True,
            "details": [
                "Run downloaded installer",
                "Follow installation wizard",
                "Complete setup"
            ]
        })

        # Step 3: Authenticate
        instructions["steps"].append({
            "step": 3,
            "action": "authenticate",
            "description": "Authenticate ProtonPass CLI",
            "command": "python scripts/python/protonpass_auto_login.py",
            "manual": False
        })

        # Step 4: Test
        instructions["steps"].append({
            "step": 4,
            "action": "test",
            "description": "Test ProtonPass CLI functionality",
            "command": "pass-cli.exe item list",
            "manual": False
        })

        instructions["notes"] = [
            "CLI should be installed to: C:\\Users\\mlesn\\AppData\\Local\\Programs\\ProtonPass\\pass-cli.exe",
            "You may need to re-authenticate after installation"
        ]

        return instructions

    def generate_full_reinstall_plan(self) -> Dict[str, Any]:
        """Generate complete reinstallation plan"""
        logger.info("=" * 70)
        logger.info("📋 GENERATING COMPLETE REINSTALLATION PLAN")
        logger.info("=" * 70)
        logger.info("")

        current_status = self.check_current_installation()
        uninstall_instructions = self.generate_uninstall_instructions()
        reinstall_instructions = self.generate_reinstall_instructions()

        plan = {
            "current_status": current_status,
            "uninstall": uninstall_instructions,
            "reinstall": reinstall_instructions,
            "estimated_time": "15-20 minutes",
            "risk_level": "Low",
            "backup_required": True
        }

        return plan

    def print_reinstall_plan(self, plan: Dict[str, Any]):
        """Print reinstallation plan"""
        logger.info("=" * 70)
        logger.info("📋 PROTONPASS CLI REINSTALLATION PLAN")
        logger.info("=" * 70)
        logger.info("")

        logger.info("CURRENT STATUS:")
        logger.info(f"   CLI Exists: {'✅' if plan['current_status']['cli_exists'] else '❌'}")
        logger.info(f"   CLI Version: {plan['current_status']['cli_version'] or 'Unknown'}")
        if plan['current_status']['issues']:
            logger.info("   Issues:")
            for issue in plan['current_status']['issues']:
                logger.info(f"      - {issue}")
        logger.info("")

        logger.info("UNINSTALL STEPS:")
        for step in plan['uninstall']['steps']:
            logger.info(f"   Step {step['step']}: {step['description']}")
            if step.get('command'):
                logger.info(f"      Command: {step['command']}")
            if step.get('details'):
                for detail in step['details']:
                    logger.info(f"      - {detail}")
        logger.info("")

        logger.info("REINSTALL STEPS:")
        for step in plan['reinstall']['steps']:
            logger.info(f"   Step {step['step']}: {step['description']}")
            if step.get('url'):
                logger.info(f"      URL: {step['url']}")
            if step.get('command'):
                logger.info(f"      Command: {step['command']}")
            if step.get('details'):
                for detail in step['details']:
                    logger.info(f"      - {detail}")
        logger.info("")

        logger.info("=" * 70)
        logger.info("✅ REINSTALLATION PLAN GENERATED")
        logger.info("=" * 70)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ProtonPass CLI Reinstallation Helper")
    parser.add_argument("--plan", "-p", action="store_true", help="Generate reinstallation plan")
    parser.add_argument("--check", "-c", action="store_true", help="Check current installation")

    args = parser.parse_args()

    helper = ProtonPassCLIReinstallHelper()

    if args.plan:
        plan = helper.generate_full_reinstall_plan()
        helper.print_reinstall_plan(plan)
    elif args.check:
        status = helper.check_current_installation()
        print(f"\n✅ Installation check complete!")
        print(f"   CLI Exists: {status['cli_exists']}")
        print(f"   CLI Version: {status['cli_version'] or 'Unknown'}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()