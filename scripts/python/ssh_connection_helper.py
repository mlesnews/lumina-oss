#!/usr/bin/env python3
"""
SSH Connection Helper
Provides a unified way to connect to NAS using SSH keys (preferred) or password (fallback)
#JARVIS #SSH #NAS #AUTHENTICATION #INFOSEC
"""

import os
import sys
import logging
from pathlib import Path
import paramiko
from typing import Optional, Tuple
from datetime import datetime

# Determine project root and log directory
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
log_dir = project_root / "data" / "logs"
log_dir.mkdir(parents=True, exist_ok=True)

# Setup logging for security events
logger = logging.getLogger("SSHConnection")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.WARNING)  # Log warnings and above

# Configure paramiko logging to file with timestamps (not console)
# This prevents duplicate terminal output and ensures timestamps
# Only configure once to avoid duplicate handlers
_paramiko_logger_configured = False

def _configure_paramiko_logging():
    """Configure paramiko logging to file with timestamps, suppress console output"""
    global _paramiko_logger_configured
    if _paramiko_logger_configured:
        return

    paramiko_logger = logging.getLogger("paramiko")
    paramiko_logger.setLevel(logging.INFO)  # Capture INFO and above

    # Check if we already have a file handler
    has_file_handler = any(
        isinstance(h, logging.FileHandler) and 
        getattr(h, 'baseFilename', '').endswith('ssh_connections.log')
        for h in paramiko_logger.handlers
    )

    if not has_file_handler:
        # Remove any existing console handlers to avoid duplicate output
        paramiko_logger.handlers = [
            h for h in paramiko_logger.handlers 
            if not isinstance(h, logging.StreamHandler)
        ]

        # Create file handler for paramiko logs
        ssh_log_file = log_dir / "ssh_connections.log"
        file_handler = logging.FileHandler(ssh_log_file, encoding='utf-8')
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        paramiko_logger.addHandler(file_handler)

    # Suppress console output from paramiko
    # Only log to file, not to stderr/stdout
    paramiko_logger.propagate = False

    _paramiko_logger_configured = True

# Configure on import
_configure_paramiko_logging()

def get_ssh_key_path() -> Optional[Path]:
    try:
        """Get the path to the LUMINA NAS SSH key."""
        ssh_dir = Path.home() / ".ssh"
        key_name = "id_ed25519_lumina_nas"
        private_key_path = ssh_dir / key_name

        if private_key_path.exists():
            # SECURITY CHECK: Verify key permissions are secure
            if sys.platform != 'win32':
                import stat
                key_stat = private_key_path.stat()
                # Check if permissions are too permissive (should be 600 = rw-------)
                mode = key_stat.st_mode
                if (mode & stat.S_IRGRP) or (mode & stat.S_IWGRP) or \
                   (mode & stat.S_IROTH) or (mode & stat.S_IWOTH):
                    logger.warning(
                        f"⚠️  SSH key {private_key_path} has insecure permissions. "
                        f"Should be 600 (rw-------), but has group/other access. "
                        f"Fixing permissions..."
                    )
                    private_key_path.chmod(0o600)
            return private_key_path
        return None

    except Exception as e:
        logger.error(f"Error in get_ssh_key_path: {e}", exc_info=True)
        raise
def load_ssh_key(key_path: Path) -> Optional[paramiko.PKey]:
    """Load SSH private key from file."""
    try:
        # Try ed25519 first (what we generate)
        return paramiko.Ed25519Key.from_private_key_file(str(key_path))
    except Exception:
        try:
            # Fallback to RSA
            return paramiko.RSAKey.from_private_key_file(str(key_path))
        except Exception:
            return None

def connect_to_nas(
    nas_ip: str,
    username: str,
    password: Optional[str] = None,
    timeout: int = 10
) -> paramiko.SSHClient:
    """
    Connect to NAS using SSH key (preferred) or password (fallback).

    Args:
        nas_ip: NAS IP address
        username: SSH username
        password: SSH password (used as fallback if key auth fails)
        timeout: Connection timeout in seconds

    Returns:
        Connected SSHClient instance

    Raises:
        paramiko.AuthenticationException: If both key and password auth fail
        paramiko.SSHException: If connection fails
    """
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Try SSH key first (instant, no failed attempts)
    key_path = get_ssh_key_path()
    if key_path:
        ssh_key = load_ssh_key(key_path)
        if ssh_key:
            try:
                ssh.connect(
                    nas_ip,
                    port=22,
                    username=username,
                    pkey=ssh_key,
                    timeout=timeout,
                    allow_agent=False,
                    look_for_keys=False
                )
                logger.info(f"✅ SSH key authentication successful for {username}@{nas_ip}")
                return ssh  # Success with key!
            except paramiko.AuthenticationException as e:
                # Key auth failed, fall back to password
                logger.warning(
                    f"⚠️  SSH key authentication failed for {username}@{nas_ip}, "
                    f"falling back to password authentication. "
                    f"Reason: {str(e)[:100]}"
                )
                # SECURITY ALERT: Password fallback should be rare
                # This indicates either:
                # 1. Key was removed/rotated
                # 2. Key permissions changed
                # 3. Key is invalid
                # 4. Potential security issue
                pass

    # Fallback to password authentication
    if password:
        logger.warning(
            f"🔐 Using password authentication for {username}@{nas_ip} "
            f"(SSH key not available or failed). "
            f"This should be investigated by @INFOSEC @DROIDS."
        )
        ssh.connect(
            nas_ip,
            port=22,
            username=username,
            password=password,
            timeout=timeout,
            allow_agent=False,
            look_for_keys=False
        )
        return ssh

    # No key and no password - can't connect
    raise paramiko.AuthenticationException("No SSH key found and no password provided")
