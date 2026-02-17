#!/usr/bin/env python3
"""
Check for environment issues caused by not using venv
Diagnoses Python environment problems and suggests fixes
"""

import sys
import os
from pathlib import Path
import logging
logger = logging.getLogger("check_environment_issues")


def check_environment():
    try:
        """Check current Python environment"""
        issues = []
        warnings = []
        info = []

        # Check Python executable
        python_exe = sys.executable
        info.append(f"Python executable: {python_exe}")

        # Check if using venv
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )

        if not in_venv:
            issues.append("❌ NOT using virtual environment (venv)")
            issues.append(f"   Current: {python_exe}")
            issues.append("   Should be: venv\\Scripts\\python.exe (Windows) or venv/bin/python (Unix)")
        else:
            info.append(f"✅ Using virtual environment: {sys.prefix}")

        # Check if venv exists
        project_root = Path(__file__).parent.parent.parent
        venv_paths = [
            project_root / "venv",
            project_root / ".venv",
            project_root / "env"
        ]

        venv_found = None
        for venv_path in venv_paths:
            if venv_path.exists():
                python_in_venv = venv_path / "Scripts" / "python.exe" if os.name == 'nt' else venv_path / "bin" / "python"
                if python_in_venv.exists():
                    venv_found = venv_path
                    break

        if not venv_found:
            warnings.append("⚠️  No venv found in project root")
            warnings.append("   Create with: python -m venv venv")
        else:
            info.append(f"✅ Venv found: {venv_found}")
            if not in_venv:
                warnings.append(f"⚠️  Venv exists but not activated: {venv_found}")

        # Check sys.path for issues
        site_packages_in_path = any('site-packages' in p for p in sys.path)
        if not site_packages_in_path and in_venv:
            warnings.append("⚠️  site-packages not in sys.path (venv may be incomplete)")

        # Check for common environment issues
        if os.name == 'nt':
            # Windows-specific checks
            if 'AppData\\Local\\Programs\\Python' in python_exe and not in_venv:
                warnings.append("⚠️  Using system Python - should use venv")

        return {
            "issues": issues,
            "warnings": warnings,
            "info": info,
            "in_venv": in_venv,
            "venv_found": str(venv_found) if venv_found else None
        }

    except Exception as e:
        logger.error(f"Error in check_environment: {e}", exc_info=True)
        raise
def main():
    """Main entry point"""
    print("=" * 80)
    print("🔍 ENVIRONMENT DIAGNOSTICS")
    print("=" * 80)
    print()

    result = check_environment()

    # Print info
    if result["info"]:
        print("📋 Information:")
        for item in result["info"]:
            print(f"   {item}")
        print()

    # Print warnings
    if result["warnings"]:
        print("⚠️  Warnings:")
        for item in result["warnings"]:
            print(f"   {item}")
        print()

    # Print issues
    if result["issues"]:
        print("❌ Issues Found:")
        for item in result["issues"]:
            print(f"   {item}")
        print()

    # Recommendations
    print("💡 Recommendations:")
    if not result["in_venv"]:
        if result["venv_found"]:
            print("   1. Activate venv:")
            if os.name == 'nt':
                print(f"      . {result['venv_found']}\\Scripts\\Activate.ps1")
            else:
                print(f"      source {result['venv_found']}/bin/activate")
        else:
            print("   1. Create venv:")
            print("      python -m venv venv")
            print("   2. Activate venv:")
            if os.name == 'nt':
                print("      . venv\\Scripts\\Activate.ps1")
            else:
                print("      source venv/bin/activate")
        print("   3. Install dependencies:")
        print("      pip install -r requirements.txt")
    else:
        print("   ✅ Environment looks good!")

    print()
    print("=" * 80)

    # Return exit code
    return 0 if not result["issues"] else 1

if __name__ == "__main__":


    sys.exit(main())