#!/usr/bin/env python3
"""
WSL Kali Linux Access Utility

Detects and accesses hardened Kali Linux installation on Falcon laptop.
Tests access methods and verifies Perl installation.

Tags: #WSL #KALI_LINUX #HARDENED #PERL #ACCESS @JARVIS @LUMINA
"""

import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

DEFAULT_WSL_DISTRO = os.getenv("SYPHON_WSL_DISTRO", "kali-linux")

try:
    from lumina_core.logging import get_logger
    logger = get_logger("WSLKaliAccess")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("WSLKaliAccess")


def _decode_wsl_list_output(output: bytes) -> str:
    """Decode WSL list output (handles UTF-16LE from PowerShell)"""
    try:
        return output.decode("utf-16-le")
    except UnicodeDecodeError:
        return output.decode("utf-8", errors="ignore")


def check_wsl_distributions() -> List[Dict[str, Any]]:
    """Check available WSL distributions"""
    try:
        result = subprocess.run(
            ['wsl', '--list', '--verbose'],
            capture_output=True,
            timeout=10,
            text=False
        )

        distributions = []
        if result.returncode == 0:
            decoded = _decode_wsl_list_output(result.stdout)
            lines = decoded.strip().split('\n')
            # Skip header line
            for line in lines[1:]:
                if line.strip():
                    # Handle lines with asterisk (default distribution)
                    line_clean = line.replace('*', '').strip()
                    parts = line_clean.split()
                    if len(parts) >= 1:
                        name = parts[0].strip()
                        state = parts[1] if len(parts) > 1 else "Unknown"
                        version = parts[2] if len(parts) > 2 else "Unknown"
                        distributions.append({
                            "name": name,
                            "state": state,
                            "version": version
                        })

        return distributions
    except Exception as e:
        logger.error("Failed to check WSL distributions", exc_info=True)
        return []


def check_kali_wsl() -> Optional[Dict[str, Any]]:
    """Check if preferred WSL distribution is available"""
    distributions = check_wsl_distributions()

    for distro in distributions:
        name_lower = distro["name"].lower()
        if DEFAULT_WSL_DISTRO.lower() in name_lower:
            return distro

    return None


def test_kali_access(distribution_name: str = DEFAULT_WSL_DISTRO) -> Dict[str, Any]:
    """Test access to preferred WSL distribution"""
    result = {
        "accessible": False,
        "method": "unknown",
        "perl_available": False,
        "perl_version": None,
        "error": None
    }

    # Try WSL access
    try:
        # Test basic access
        test_cmd = subprocess.run(
            ['wsl', '-d', distribution_name, 'uname', '-a'],
            capture_output=True,
            timeout=10,
            text=True
        )

        if test_cmd.returncode == 0:
            result["accessible"] = True
            result["method"] = "wsl"
            result["system_info"] = test_cmd.stdout.strip()

            # Check Perl
            perl_cmd = subprocess.run(
                ['wsl', '-d', distribution_name, 'perl', '-v'],
                capture_output=True,
                timeout=10,
                text=True
            )

            if perl_cmd.returncode == 0:
                result["perl_available"] = True
                # Extract version
                version_line = perl_cmd.stdout.split('\n')[0]
                result["perl_version"] = version_line
            else:
                result["error"] = f"Perl not found: {perl_cmd.stderr}"
        else:
            result["error"] = f"WSL access failed: {test_cmd.stderr}"

    except FileNotFoundError:
        result["error"] = "WSL command not found"
    except subprocess.TimeoutExpired:
        result["error"] = "WSL access timed out"
    except Exception as e:
        result["error"] = f"Access test failed: {e}"

    return result


def find_kali_installation() -> Dict[str, Any]:
    """Find Kali Linux installation using various methods"""
    result = {
        "found": False,
        "method": None,
        "details": {}
    }

    # Method 1: Check WSL distributions
    logger.info("Checking WSL distributions...")
    kali_wsl = check_kali_wsl()
    if kali_wsl:
        result["found"] = True
        result["method"] = "wsl"
        result["details"] = kali_wsl
        logger.info(f"✅ Found Kali Linux in WSL: {kali_wsl['name']}")
        return result

    # Method 2: Try common WSL distribution names
    logger.info("Trying common WSL distribution names...")
    common_names = [DEFAULT_WSL_DISTRO, "kali-linux", "kali", "Kali-Linux", "Kali"]
    for name in common_names:
        test_result = test_kali_access(name)
        if test_result["accessible"]:
            result["found"] = True
            result["method"] = "wsl"
            result["details"] = {
                "name": name,
                "access": test_result
            }
            logger.info(f"✅ Found Kali Linux accessible as: {name}")
            return result

    # Method 3: Check for VM (would need VM tools)
    logger.info("Kali Linux not found in WSL. May be in VM or native installation.")
    logger.info("Please provide access method (WSL name, SSH, VM, etc.)")

    return result


def install_perl_in_kali(distribution_name: str = "kali-linux") -> Dict[str, Any]:
    """Install Perl in Kali Linux WSL"""
    result = {
        "success": False,
        "method": None,
        "error": None
    }

    try:
        # Check if Perl already installed
        check_cmd = subprocess.run(
            ['wsl', '-d', distribution_name, 'perl', '-v'],
            capture_output=True,
            timeout=10,
            text=True
        )

        if check_cmd.returncode == 0:
            result["success"] = True
            result["method"] = "already_installed"
            result["version"] = check_cmd.stdout.split('\n')[0]
            logger.info("✅ Perl already installed in Kali Linux")
            return result

        # Install Perl
        logger.info(f"Installing Perl in {distribution_name}...")
        install_cmd = subprocess.run(
            ['wsl', '-d', distribution_name, 'sudo', 'apt-get', 'update'],
            capture_output=True,
            timeout=60,
            text=True
        )

        if install_cmd.returncode != 0:
            result["error"] = f"apt-get update failed: {install_cmd.stderr}"
            return result

        install_perl = subprocess.run(
            ['wsl', '-d', distribution_name, 'sudo', 'apt-get', 'install', '-y', 'perl'],
            capture_output=True,
            timeout=120,
            text=True
        )

        if install_perl.returncode == 0:
            result["success"] = True
            result["method"] = "installed"
            logger.info("✅ Perl installed successfully in Kali Linux")
        else:
            result["error"] = f"Perl installation failed: {install_perl.stderr}"

    except Exception as e:
        result["error"] = f"Installation failed: {e}"
        logger.error("Failed to install Perl", exc_info=True)

    return result


def main():
    """Main entry point"""
    print("="*80)
    print("🔍 WSL KALI LINUX ACCESS UTILITY")
    print("="*80)
    print()

    # Check WSL distributions
    print("Checking WSL distributions...")
    distributions = check_wsl_distributions()
    print(f"Found {len(distributions)} WSL distribution(s):")
    for distro in distributions:
        print(f"  - {distro['name']}: {distro['state']} (WSL{distro['version']})")
    print()

    # Find Kali Linux
    print("Searching for Kali Linux installation...")
    kali_found = find_kali_installation()

    if kali_found["found"]:
        print(f"✅ Kali Linux found via: {kali_found['method']}")
        if "details" in kali_found and "access" in kali_found["details"]:
            access = kali_found["details"]["access"]
            print(f"   Accessible: {access['accessible']}")
            print(f"   Perl Available: {access['perl_available']}")
            if access.get("perl_version"):
                print(f"   Perl Version: {access['perl_version']}")
        print()

        # Install Perl if needed
        if kali_found["method"] == "wsl":
            distro_name = kali_found["details"].get("name", "kali-linux")
            if not kali_found["details"].get("access", {}).get("perl_available"):
                print("Installing Perl in Kali Linux...")
                install_result = install_perl_in_kali(distro_name)
                if install_result["success"]:
                    print("✅ Perl installation complete")
                else:
                    print(f"❌ Perl installation failed: {install_result.get('error')}")
    else:
        print("⚠️  Kali Linux not found in WSL")
        print()
        print("Possible locations:")
        print("  1. Native installation (dual-boot)")
        print("  2. VM (Hyper-V, VirtualBox, etc.)")
        print("  3. Network-accessible system")
        print("  4. Not yet installed as WSL distribution")
        print()
        print("Next steps:")
        print("  1. If native/VM: Provide access method (SSH, RDP, etc.)")
        print("  2. If not installed: Install Kali Linux WSL")
        print("  3. If on network: Provide SSH connection details")

    print()
    print("="*80)
    print("✅ WSL KALI LINUX ACCESS CHECK COMPLETE")
    print("="*80)


if __name__ == "__main__":


    main()