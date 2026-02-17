#!/usr/bin/env python3
"""
JARVIS Grammarly Lighting Fix
Fix lights brightening after using Grammarly

@JARVIS @GRAMMARLY @LIGHTING @FIX
"""

import sys
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISGrammarlyFix")


class GrammarlyLightingFix:
    """
    Fix lights brightening after Grammarly usage

    Grammarly may trigger:
    - Screen brightness changes
    - Focus/attention mode lighting
    - Notification lighting
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Grammarly lighting fix"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        from src.cfservices.services.jarvis_core.integrations.armoury_crate import create_armoury_crate_integration
        self.armoury_crate = create_armoury_crate_integration()

        logger.info("✅ Grammarly Lighting Fix initialized")

    async def fix_grammarly_lighting(self) -> Dict[str, Any]:
        """Fix lighting after Grammarly usage"""
        logger.info("=" * 70)
        logger.info("🔧 GRAMMARLY LIGHTING FIX")
        logger.info("   Fixing lights that brighten after Grammarly")
        logger.info("=" * 70)
        logger.info("")

        results = {}

        # Step 1: Disable all lighting
        logger.info("STEP 1: Disabling all external lighting...")
        lighting_result = await self.armoury_crate.process_request({
            "action": "disable_all_lighting"
        })
        results["lighting_disable"] = lighting_result

        # Step 2: Check for Grammarly processes
        logger.info("\nSTEP 2: Checking Grammarly processes...")
        import subprocess
        grammarly_check = subprocess.run(
            ["powershell", "-Command", "Get-Process -Name 'Grammarly*' -ErrorAction SilentlyContinue | Select-Object ProcessName, Id"],
            capture_output=True,
            text=True
        )

        if grammarly_check.returncode == 0 and grammarly_check.stdout.strip():
            logger.info(f"  Found Grammarly processes: {grammarly_check.stdout.strip()}")
            results["grammarly_processes"] = grammarly_check.stdout.strip()
        else:
            logger.info("  No Grammarly processes found")
            results["grammarly_processes"] = "None"

        # Step 3: Check Grammarly CLI mode
        logger.info("\nSTEP 3: Checking for Grammarly CLI mode...")
        grammarly_cli_info = self._check_grammarly_cli()
        results["grammarly_cli"] = grammarly_cli_info
        logger.info(f"  {grammarly_cli_info.get('message', 'Unknown')}")

        logger.info("")
        logger.info("=" * 70)
        logger.info("✅ GRAMMARLY LIGHTING FIX COMPLETE")
        logger.info("=" * 70)

        return results

    def _check_grammarly_cli(self) -> Dict[str, Any]:
        """Check for Grammarly CLI mode"""
        import subprocess

        # Check if Grammarly CLI is installed
        cli_check = subprocess.run(
            ["powershell", "-Command", "Get-Command grammarly -ErrorAction SilentlyContinue"],
            capture_output=True,
            text=True
        )

        if cli_check.returncode == 0:
            return {
                "available": True,
                "message": "Grammarly CLI is available",
                "path": cli_check.stdout.strip()
            }

        # Check npm/pip installations
        try:
            npm_check = subprocess.run(
                ["npm", "list", "-g", "@grammarly/cli", "--depth=0"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if npm_check.returncode == 0 and "@grammarly/cli" in npm_check.stdout:
                return {
                    "available": True,
                    "message": "Grammarly CLI available via npm",
                    "method": "npm"
                }
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass

        return {
            "available": False,
            "message": "Grammarly CLI not found. Install via: npm install -g @grammarly/cli",
            "installation": "npm install -g @grammarly/cli"
        }


async def main():
    """Main execution"""
    print("=" * 70)
    print("🔧 JARVIS GRAMMARLY LIGHTING FIX")
    print("=" * 70)
    print()

    fixer = GrammarlyLightingFix()
    results = await fixer.fix_grammarly_lighting()

    print()
    print("=" * 70)
    print("✅ FIX COMPLETE")
    print("=" * 70)
    print(f"Lighting: {'✅' if results.get('lighting_disable', {}).get('success') else '❌'}")
    print(f"Grammarly CLI: {results.get('grammarly_cli', {}).get('message', 'Unknown')}")
    print("=" * 70)


if __name__ == "__main__":


    asyncio.run(main())