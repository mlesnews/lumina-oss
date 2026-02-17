#!/usr/bin/env python3
"""
Build Lumina Complete VSIX Extension

Builds and packages the Lumina Complete VSIX extension with all services.

Tags: #BUILD #VSIX #EXTENSION @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BuildLuminaVSIX")


def build_vsix():
    """Build the Lumina Complete VSIX extension"""
    extension_dir = project_root / "vscode-extensions" / "lumina-complete"

    if not extension_dir.exists():
        logger.error(f"Extension directory not found: {extension_dir}")
        return False

    logger.info("Building Lumina Complete VSIX extension...")

    # Install dependencies
    logger.info("Installing dependencies...")
    try:
        subprocess.run(["npm", "install"], cwd=extension_dir, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

    # Compile TypeScript
    logger.info("Compiling TypeScript...")
    try:
        subprocess.run(["npm", "run", "compile"], cwd=extension_dir, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to compile: {e}")
        return False

    # Package VSIX
    logger.info("Packaging VSIX...")
    try:
        result = subprocess.run(
            ["npm", "run", "package"],
            cwd=extension_dir,
            check=True,
            capture_output=True,
            text=True
        )

        # Find the generated VSIX file
        vsix_files = list(extension_dir.glob("*.vsix"))
        if vsix_files:
            vsix_file = vsix_files[0]
            logger.info(f"✅ VSIX package created: {vsix_file}")

            # Copy to project root
            target = project_root / f"lumina-complete-{datetime.now().strftime('%Y%m%d')}.vsix"
            import shutil
            shutil.copy2(vsix_file, target)
            logger.info(f"✅ VSIX copied to: {target}")

            return True
        else:
            logger.error("VSIX file not found after packaging")
            return False

    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to package VSIX: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False


def main():
    """Main execution"""
    print("=" * 80)
    print("🔨 BUILDING LUMINA COMPLETE VSIX EXTENSION")
    print("=" * 80)
    print()

    if build_vsix():
        print("✅ Build successful!")
        print()
        print("To install the extension:")
        print("  code --install-extension lumina-complete-YYYYMMDD.vsix")
    else:
        print("❌ Build failed!")
        sys.exit(1)


if __name__ == "__main__":


    main()