#!/usr/bin/env python3
"""
JARVIS Automated Setup - ProtonVPN & Download Management
Executes all setup tasks automatically

Tags: #JARVIS #AUTOMATION #SETUP @JARVIS @LUMINA @DOIT
"""

import subprocess
import sys
import os
from pathlib import Path
from typing import Tuple, Optional
import logging
logger = logging.getLogger("jarvis_automated_setup")



def run_command(command: str, host: Optional[str] = None, timeout: int = 300) -> Tuple[str, int]:
    """Run command locally or via SSH"""
    if host:
        ssh_cmd = ["ssh", host, command]
    else:
        if sys.platform == "win32":
            ssh_cmd = ["powershell", "-Command", command]
        else:
            ssh_cmd = command.split()

    try:
        result = subprocess.run(
            ssh_cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        return result.stdout, result.returncode
    except Exception as e:
        return str(e), 1


def install_protonvpn(host: Optional[str] = None) -> Tuple[bool, str]:
    """Install ProtonVPN via winget"""
    print(f"📦 Installing ProtonVPN on {host or 'local'}...")

    if host:
        cmd = "winget install --id=ProtonTechnologies.ProtonVPN -e --accept-package-agreements --accept-source-agreements"
    else:
        cmd = "winget install --id=ProtonTechnologies.ProtonVPN -e --accept-package-agreements --accept-source-agreements"

    stdout, code = run_command(cmd, host=host, timeout=600)

    if code == 0:
        return True, "ProtonVPN installed successfully"
    else:
        return False, f"Installation failed: {stdout}"


def setup_protonvpn(host: Optional[str] = None) -> Tuple[bool, str]:
    try:
        """Run ProtonVPN setup script"""
        print(f"⚙️  Configuring ProtonVPN on {host or 'local'}...")

        if host:
            cmd = "cd 'D:\\Dropbox\\my_projects\\.lumina'; powershell -ExecutionPolicy Bypass -File 'scripts\\startup\\SETUP_PROTONVPN.ps1'"
        else:
            script_path = Path(__file__).parent.parent / "startup" / "SETUP_PROTONVPN.ps1"
            cmd = f"powershell -ExecutionPolicy Bypass -File '{script_path}'"

        stdout, code = run_command(cmd, host=host, timeout=300)

        if code == 0:
            return True, "ProtonVPN configured successfully"
        else:
            return False, f"Configuration failed: {stdout}"


    except Exception as e:
        logger.error(f"Error in setup_protonvpn: {e}", exc_info=True)
        raise
def setup_downloads_local() -> Tuple[bool, str]:
    try:
        """Set up local download management on FALC"""
        print("📥 Setting up download management on FALC (local)...")

        script_path = Path(__file__).parent.parent / "startup" / "DOWNLOAD_MODELS_LOCAL_FALC.ps1"
        cmd = f"powershell -ExecutionPolicy Bypass -File '{script_path}'"

        stdout, code = run_command(cmd, timeout=600)

        if code == 0:
            return True, "Download management configured"
        else:
            return False, f"Setup failed: {stdout}"


    except Exception as e:
        logger.error(f"Error in setup_downloads_local: {e}", exc_info=True)
        raise
def check_manus_monitoring() -> Tuple[bool, str]:
    try:
        """Check if @manus desktop monitoring is active"""
        print("👁️  Checking @manus desktop monitoring...")

        # Search for manus-related files
        scripts_dir = Path(__file__).parent
        manus_files = list(scripts_dir.glob("*manus*.py"))

        if manus_files:
            print(f"  Found @manus files: {[f.name for f in manus_files]}")
            return True, f"@manus monitoring found: {manus_files[0].name}"
        else:
            return False, "@manus monitoring not found"


    except Exception as e:
        logger.error(f"Error in check_manus_monitoring: {e}", exc_info=True)
        raise
def main():
    """Main automation"""
    print("=" * 80)
    print("JARVIS Automated Setup")
    print("=" * 80)
    print()

    results = []

    # Step 1: Check @manus monitoring
    print("Step 1: Checking @manus desktop monitoring...")
    manus_ok, manus_msg = check_manus_monitoring()
    print(f"  {'✅' if manus_ok else '⚠️ '} {manus_msg}")
    results.append(("@manus Monitoring", manus_ok, manus_msg))
    print()

    # Step 2: Install ProtonVPN on FALC (local)
    print("Step 2: Installing ProtonVPN on FALC (local)...")
    install_ok, install_msg = install_protonvpn(host=None)
    print(f"  {'✅' if install_ok else '❌'} {install_msg}")
    results.append(("ProtonVPN FALC Install", install_ok, install_msg))
    print()

    # Step 3: Setup ProtonVPN on FALC
    if install_ok:
        setup_ok, setup_msg = setup_protonvpn(host=None)
        print(f"  {'✅' if setup_ok else '❌'} {setup_msg}")
        results.append(("ProtonVPN FALC Setup", setup_ok, setup_msg))
    print()

    # Step 4: Install ProtonVPN on KAIJU (remote)
    print("Step 3: Installing ProtonVPN on KAIJU (remote)...")
    install_kaiju_ok, install_kaiju_msg = install_protonvpn(host="<NAS_IP>")
    print(f"  {'✅' if install_kaiju_ok else '❌'} {install_kaiju_msg}")
    results.append(("ProtonVPN KAIJU Install", install_kaiju_ok, install_kaiju_msg))
    print()

    # Step 5: Setup ProtonVPN on KAIJU
    if install_kaiju_ok:
        setup_kaiju_ok, setup_kaiju_msg = setup_protonvpn(host="<NAS_IP>")
        print(f"  {'✅' if setup_kaiju_ok else '❌'} {setup_kaiju_msg}")
        results.append(("ProtonVPN KAIJU Setup", setup_kaiju_ok, setup_kaiju_msg))
    print()

    # Step 6: Setup local download management
    print("Step 4: Setting up download management on FALC...")
    download_ok, download_msg = setup_downloads_local()
    print(f"  {'✅' if download_ok else '❌'} {download_msg}")
    results.append(("Download Management", download_ok, download_msg))
    print()

    # Summary
    print("=" * 80)
    print("Setup Summary")
    print("=" * 80)
    for name, success, msg in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}: {msg}")
    print()

    all_ok = all(success for _, success, _ in results)
    if all_ok:
        print("✅ All setup tasks completed successfully!")
    else:
        print("⚠️  Some tasks need attention. Check output above.")
    print()


if __name__ == "__main__":


    main()