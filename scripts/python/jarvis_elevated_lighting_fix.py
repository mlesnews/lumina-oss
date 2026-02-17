#!/usr/bin/env python3
"""
JARVIS Elevated Lighting Fix

Requests admin privileges and attempts all methods that require elevation.

@JARVIS @ELEVATED @LIGHTING @FIX @ADMIN
"""

import sys
import subprocess
import ctypes
from pathlib import Path
import logging
logger = logging.getLogger("jarvis_elevated_lighting_fix")


project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def is_admin():
    """Check if running as admin"""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


def run_as_admin():
    try:
        """Rerun script with admin privileges"""
        if is_admin():
            return True
        else:
            # Re-run the program with admin rights
            script_path = Path(__file__).resolve()
            ctypes.windll.shell32.ShellExecuteW(
                None, "runas", sys.executable, str(script_path), None, 1
            )
            return False


    except Exception as e:
        logger.error(f"Error in run_as_admin: {e}", exc_info=True)
        raise
def main():
    """Main execution"""
    if not is_admin():
        print("=" * 70)
        print("🔧 ELEVATED LIGHTING FIX")
        print("=" * 70)
        print("   ⚠️  Admin privileges required")
        print("   🔄 Requesting admin privileges...")
        print("=" * 70)
        print()

        if run_as_admin():
            # This shouldn't be reached, but just in case
            pass
        else:
            print("   ✅ Admin request sent. Please approve the UAC prompt.")
            return
    else:
        # We have admin privileges, run the fix
        print("=" * 70)
        print("🔧 ELEVATED LIGHTING FIX")
        print("   ✅ Running with admin privileges")
        print("=" * 70)
        print()

        # Import and run the installer
        from scripts.python.jarvis_automated_lighting_fix_installer import AutomatedLightingFixInstaller

        installer = AutomatedLightingFixInstaller(project_root)

        # Run only the methods that require admin
        print("   🔧 Running admin-required methods...")
        print()

        # Method 1: Scheduled Task
        result1 = installer.method_1_create_scheduled_task()
        print()

        # Method 2: Disable Services
        result2 = installer.method_2_disable_services_permanently()
        print()

        # Method 3: Service Recovery
        result3 = installer.method_3_set_service_recovery()
        print()

        # Summary
        print("=" * 70)
        print("📊 ELEVATED METHODS SUMMARY")
        print("=" * 70)
        print(f"   ✅ Scheduled Task: {'SUCCESS' if result1.get('success') else 'FAILED'}")
        print(f"   ✅ Disable Services: {'SUCCESS' if result2.get('success') else 'FAILED'}")
        print(f"   ✅ Service Recovery: {'SUCCESS' if result3.get('success') else 'FAILED'}")
        print()
        print("=" * 70)
        print("✅ ELEVATED FIX COMPLETE")
        print("=" * 70)
        print()


if __name__ == "__main__":


    main()