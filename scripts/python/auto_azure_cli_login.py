#!/usr/bin/env python3
"""
Auto Azure CLI Login for Cursor Startup

This script automatically ensures Azure CLI is logged in when Cursor starts.
It checks login status first and only runs `az login` if needed.

Features:
- Checks if already logged in (no unnecessary prompts)
- Silent operation (minimal output)
- Handles errors gracefully
- Can be run from VSCode tasks or PowerShell profile

Tags: #AZURE #CURSOR #STARTUP #AUTHENTICATION
"""

import sys
import subprocess
import json
import platform

# Suppress output by default (can be overridden with --verbose)
VERBOSE = "--verbose" in sys.argv or "-v" in sys.argv


def log(message: str, level: str = "INFO"):
    """Log message if verbose mode is enabled"""
    if VERBOSE:
        print(f"[{level}] {message}", file=sys.stderr)


def check_azure_cli_installed() -> bool:
    """Check if Azure CLI is installed"""
    try:
        # On Windows, use shell=True to find .cmd/.bat files
        # On other platforms, az should be in PATH
        if platform.system() == "Windows":
            result = subprocess.run(
                ["az", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False,
                shell=True
            )
        else:
            result = subprocess.run(
                ["az", "--version"],
                capture_output=True,
                text=True,
                timeout=5,
                check=False
            )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def check_azure_cli_logged_in() -> bool:
    """Check if Azure CLI is already logged in"""
    try:
        # On Windows, use shell=True to find .cmd/.bat files
        if platform.system() == "Windows":
            result = subprocess.run(
                ["az", "account", "show"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
                shell=True
            )
        else:
            result = subprocess.run(
                ["az", "account", "show"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

        if result.returncode == 0:
            try:
                account_info = json.loads(result.stdout)
                account_name = account_info.get('name', 'Unknown')
                log(f"✅ Azure CLI is already logged in: {account_name}")
                return True
            except json.JSONDecodeError:
                log("⚠️  Could not parse Azure CLI account info", "WARN")
                return False
        else:
            log("⚠️  Azure CLI is not logged in")
            return False
    except subprocess.TimeoutExpired:
        log("⚠️  Azure CLI check timed out", "WARN")
        return False
    except Exception as e:
        log(f"⚠️  Error checking Azure CLI login: {e}", "WARN")
        return False


def run_azure_login(use_device_code: bool = False) -> bool:
    """Run Azure CLI login"""
    try:
        log("🔐 Attempting Azure CLI login...")

        cmd = ["az", "login"]
        if use_device_code:
            cmd.append("--use-device-code")
            log("Using device code authentication (non-interactive)")

        # Run login (this will be interactive or use device code)
        # On Windows, use shell=True to find .cmd/.bat files
        if platform.system() == "Windows":
            result = subprocess.run(
                cmd,
                timeout=300,  # 5 minutes timeout for login
                text=True,
                check=False,
                shell=True
            )
        else:
            result = subprocess.run(
                cmd,
                timeout=300,  # 5 minutes timeout for login
                text=True,
                check=False
            )

        if result.returncode == 0:
            log("✅ Azure CLI login successful")
            return True
        else:
            log(f"❌ Azure CLI login failed (exit code: {result.returncode})", "ERROR")
            return False
    except subprocess.TimeoutExpired:
        log("❌ Azure CLI login timed out", "ERROR")
        return False
    except KeyboardInterrupt:
        log("⚠️  Azure CLI login cancelled by user", "WARN")
        return False
    except Exception as e:
        log(f"❌ Error during Azure CLI login: {e}", "ERROR")
        return False


def main():
    """Main function"""
    # Check if Azure CLI is installed
    if not check_azure_cli_installed():
        if VERBOSE:
            print("⚠️  Azure CLI is not installed. Please install it first.", file=sys.stderr)
            print("   Download from: https://aka.ms/installazurecliwindows", file=sys.stderr)
        return 1

    # Check if already logged in
    if check_azure_cli_logged_in():
        if VERBOSE:
            print("✅ Azure CLI is already authenticated", file=sys.stderr)
        return 0

    # Not logged in - attempt login
    use_device_code = "--device-code" in sys.argv or "-d" in sys.argv

    if VERBOSE:
        print("🔐 Azure CLI is not logged in. Attempting login...", file=sys.stderr)

    success = run_azure_login(use_device_code=use_device_code)

    if success:
        if VERBOSE:
            print("✅ Azure CLI login completed successfully", file=sys.stderr)
        return 0
    else:
        if VERBOSE:
            print("❌ Azure CLI login failed. You may need to run 'az login' manually.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)  # Standard exit code for Ctrl+C
    except Exception as e:
        if VERBOSE:
            print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)