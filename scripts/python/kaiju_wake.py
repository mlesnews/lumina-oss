#!/usr/bin/env python3
"""
KAIJU Wake Script — ensures Docker Desktop is running on KAIJU.

Called by health monitor watchdog when Iron Legion goes down.
Creates an RDP session to trigger auto-logon + Docker Desktop auto-start.

COMPUSEC: Password retrieved from Azure Key Vault, piped via stdin to xfreerdp3.
"""
import subprocess
import sys
import time

KAIJU_IP = "<NAS_IP>"
KAIJU_USER = "mlesn"
VAULT_NAME = "jarvis-lumina"
SECRET_NAME = "kaiju-windows-password"
SSH_KEY = "/root/.ssh/id_rsa_kaiju"


def ssh_cmd(cmd: str, timeout: int = 15) -> tuple[int, str]:
    """Run a command on KAIJU via SSH. Returns (returncode, stdout)."""
    r = subprocess.run(
        ["ssh", "-i", SSH_KEY, "-o", "ConnectTimeout=5", "-o", "StrictHostKeyChecking=no",
         f"{KAIJU_USER}@{KAIJU_IP}", cmd],
        capture_output=True, text=True, timeout=timeout,
    )
    return r.returncode, (r.stdout + r.stderr).strip()


def check_docker() -> bool:
    """Check if Docker is responding on KAIJU."""
    rc, out = ssh_cmd('docker info --format "{{.ServerVersion}}" 2>&1')
    return rc == 0 and "." in out and "error" not in out.lower()


def check_user_session() -> bool:
    """Check if there's a logged-in user session on KAIJU."""
    rc, out = ssh_cmd("query user 2>&1")
    return rc == 0 and "mlesn" in out.lower()


def get_vault_secret() -> str:
    """Retrieve password from Azure Key Vault. Never displayed."""
    r = subprocess.run(
        ["az", "keyvault", "secret", "show",
         "--vault-name", VAULT_NAME, "--name", SECRET_NAME,
         "--query", "value", "-o", "tsv"],
        capture_output=True, text=True, timeout=15,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Vault retrieval failed: {r.stderr[:100]}")
    return r.stdout.strip().replace("\r", "")


def create_rdp_session(password: str) -> bool:
    """Create headless RDP session to trigger desktop + Docker auto-start."""
    r = subprocess.run(
        ["xfreerdp3", f"/v:{KAIJU_IP}", f"/u:{KAIJU_USER}",
         "/from-stdin", "/cert:ignore", "+auto-reconnect", "/dynamic-resolution"],
        input=password, capture_output=True, text=True, timeout=30,
    )
    return True  # xfreerdp3 may exit non-zero but still create session


def wake():
    """Main wake sequence."""
    # Step 1: Check if Docker is already running
    if check_docker():
        print("KAIJU Docker already running — no action needed")
        return 0

    print("KAIJU Docker is DOWN — initiating wake sequence")

    # Step 2: Check for user session
    if check_user_session():
        print("  User session exists but Docker not responding")
        print("  Attempting Docker Desktop restart via SSH...")
        ssh_cmd('Start-Process "C:\\Program Files\\Docker\\Docker\\Docker Desktop.exe"', timeout=10)
        time.sleep(30)
        if check_docker():
            print("  Docker recovered after Desktop restart")
            return 0

    # Step 3: Create RDP session (triggers auto-logon)
    print("  Creating RDP session for auto-logon...")
    password = get_vault_secret()
    create_rdp_session(password)
    del password

    # Step 4: Wait for Docker Desktop to initialize
    print("  Waiting for Docker Desktop to start...")
    for attempt in range(1, 7):
        time.sleep(15)
        if check_docker():
            print(f"  Docker UP after {attempt * 15}s")
            return 0
        print(f"  Attempt {attempt}/6 — not yet ready")

    print("  FAILED: Docker did not start within 90 seconds")
    return 1


if __name__ == "__main__":
    sys.exit(wake())
