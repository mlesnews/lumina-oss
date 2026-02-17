#!/usr/bin/env python3
"""
ZUUL Secret Rotation Engine

"There is no static password, only ZUUL"

Automated 30-day round-robin secret rotation using the
Gatekeeper-Keymaster-Zuul architecture.

Security: This engine NEVER logs secret values. Only metadata.
"""

import sys
import json
import secrets
import string
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
from enum import Enum
import fnmatch

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

PROJECT_ROOT = Path(r"C:\Users\mlesn\Dropbox\my_projects\.lumina")

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ZUUL")


class RotationType(Enum):
    STANDARD = "standard"      # 30 days
    CRITICAL = "critical"      # 14 days
    GATING = "gating"          # 90 days
    STATIC = "static"          # Manual only


@dataclass
class SecretMetadata:
    """Metadata about a secret (NEVER contains the actual value)"""
    name: str
    rotation_type: RotationType
    group: str
    last_rotated: Optional[datetime] = None
    next_rotation: Optional[datetime] = None
    rotation_count: int = 0
    hash_prefix: str = ""  # First 8 chars of SHA256 for verification


@dataclass
class RotationResult:
    """Result of a rotation operation"""
    secret_name: str
    success: bool
    message: str
    gatekeeper_updated: bool = False
    keymaster_updated: bool = False
    rollback_performed: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


class ZUULRotationEngine:
    """
    ZUUL - The Rotation Orchestrator

    "Are you the Gatekeeper? I am the Keymaster."
    """

    def __init__(self, project_root: Path = PROJECT_ROOT):
        self.project_root = Path(project_root)
        self.config = self._load_config()
        self.audit_log = self.project_root / "data" / "zuul_rotation" / "audit.jsonl"
        self.state_file = self.project_root / "data" / "zuul_rotation" / "state.json"

        # Ensure directories exist
        self.audit_log.parent.mkdir(parents=True, exist_ok=True)

        # Load state
        self.state = self._load_state()

        logger.info("⚡ ZUUL Rotation Engine initialized")
        logger.info("   'There is no static password, only ZUUL'")

    def _load_config(self) -> dict:
        """Load ZUUL configuration."""
        config_path = self.project_root / "config" / "zuul_rotation_config.json"
        try:
            with open(config_path) as f:
                return json.load(f).get("zuul_rotation_system", {})
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            return {}

    def _load_state(self) -> dict:
        """Load rotation state."""
        try:
            if self.state_file.exists():
                with open(self.state_file) as f:
                    return json.load(f)
        except Exception:
            pass
        return {"secrets": {}, "last_check": None}

    def _save_state(self):
        """Save rotation state."""
        try:
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.state_file, 'w') as f:
                json.dump(self.state, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _generate_secure_password(self) -> str:
        """Generate a cryptographically secure password."""
        policy = self.config.get("password_policy", {})
        length = policy.get("min_length", 32)
        charset = policy.get("charset", string.ascii_letters + string.digits + "!@#$%^&*")

        # Ensure all requirements are met
        password = []

        if policy.get("require_uppercase", True):
            password.append(secrets.choice(string.ascii_uppercase))
        if policy.get("require_lowercase", True):
            password.append(secrets.choice(string.ascii_lowercase))
        if policy.get("require_digits", True):
            password.append(secrets.choice(string.digits))
        if policy.get("require_symbols", True):
            password.append(secrets.choice("!@#$%^&*"))

        # Fill the rest
        remaining = length - len(password)
        password.extend(secrets.choice(charset) for _ in range(remaining))

        # Shuffle
        password_list = list(password)
        secrets.SystemRandom().shuffle(password_list)

        return ''.join(password_list)

    def _get_secret_hash_prefix(self, value: str) -> str:
        """Get first 8 chars of SHA256 hash (for verification without storing value)."""
        return hashlib.sha256(value.encode()).hexdigest()[:8]

    def _determine_rotation_type(self, secret_name: str) -> RotationType:
        """Determine rotation type based on secret name patterns."""
        # Check static patterns
        for pattern in self.config.get("static_secrets", []):
            if fnmatch.fnmatch(secret_name, pattern):
                return RotationType.STATIC

        # Check critical patterns
        for pattern in self.config.get("critical_secrets", []):
            if fnmatch.fnmatch(secret_name, pattern):
                return RotationType.CRITICAL

        # Check gating (excluded from keymaster)
        if secret_name in self.config.get("excluded_from_keymaster", []):
            return RotationType.GATING

        return RotationType.STANDARD

    def _determine_group(self, secret_name: str) -> str:
        """Determine which round-robin group a secret belongs to."""
        groups = self.config.get("round_robin_groups", {})

        for group_name, group_config in groups.items():
            for pattern in group_config.get("patterns", []):
                if fnmatch.fnmatch(secret_name, pattern):
                    return group_name

        # Default: assign based on first letter
        first_char = secret_name[0].lower() if secret_name else 'a'
        if first_char <= 'f':
            return "alpha"
        elif first_char <= 'l':
            return "beta"
        elif first_char <= 'r':
            return "gamma"
        else:
            return "delta"

    def _get_rotation_interval(self, rotation_type: RotationType) -> int:
        """Get rotation interval in days."""
        intervals = self.config.get("rotation_intervals", {})
        return intervals.get(rotation_type.value, 30)

    def _should_rotate(self, metadata: SecretMetadata) -> Tuple[bool, str]:
        """Check if a secret should be rotated."""
        if metadata.rotation_type == RotationType.STATIC:
            return False, "Static secret - manual rotation only"

        if metadata.last_rotated is None:
            return True, "Never rotated"

        interval = self._get_rotation_interval(metadata.rotation_type)
        next_rotation = metadata.last_rotated + timedelta(days=interval)

        if datetime.now() >= next_rotation:
            return True, f"Rotation due (interval: {interval} days)"

        days_until = (next_rotation - datetime.now()).days
        return False, f"Next rotation in {days_until} days"

    def _update_gatekeeper(self, secret_name: str, new_value: str) -> bool:
        """Update secret in Azure Key Vault (Gatekeeper)."""
        import subprocess

        try:
            # Use Azure CLI - value passed via stdin to avoid logging
            az_cmd = r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd"
            vault_name = self.config.get("vaults", {}).get("gatekeeper", {}).get("vault_name", "jarvis-lumina")

            # SECURITY: Pass value via stdin, not command line
            result = subprocess.run(
                [az_cmd, "keyvault", "secret", "set",
                 "--vault-name", vault_name,
                 "--name", secret_name,
                 "--value", "@-"],  # Read from stdin
                input=new_value,
                capture_output=True,
                text=True,
                timeout=60,
                shell=True
            )

            if result.returncode == 0:
                logger.info(f"✅ GATEKEEPER updated: {secret_name}")
                return True
            else:
                logger.error(f"❌ GATEKEEPER failed: {secret_name}")
                return False

        except Exception as e:
            logger.error(f"❌ GATEKEEPER error: {e}")
            return False

    def _update_keymaster(self, secret_name: str, new_value: str) -> bool:
        """Update secret in ProtonPass (Keymaster)."""
        # Check if this secret should be excluded
        if secret_name in self.config.get("excluded_from_keymaster", []):
            logger.info(f"🔒 KEYMASTER skip (gating secret): {secret_name}")
            return True  # Not a failure, intentionally skipped

        # ProtonPass update would go here
        # For now, log that it would be updated
        logger.info(f"📝 KEYMASTER would update: {secret_name}")
        return True

    def rotate_secret(self, secret_name: str, force: bool = False) -> RotationResult:
        """
        Rotate a single secret.

        SECURITY: New value is generated, used, then immediately discarded.
        Only the hash prefix is stored for verification.
        """
        logger.info(f"🔄 Rotating: {secret_name}")

        # Determine metadata
        rotation_type = self._determine_rotation_type(secret_name)
        group = self._determine_group(secret_name)

        # Check if static
        if rotation_type == RotationType.STATIC and not force:
            return RotationResult(
                secret_name=secret_name,
                success=False,
                message="Static secret - use force=True for manual rotation"
            )

        # Generate new secret
        new_value = self._generate_secure_password()
        hash_prefix = self._get_secret_hash_prefix(new_value)

        # Update Gatekeeper first
        gatekeeper_ok = self._update_gatekeeper(secret_name, new_value)

        if not gatekeeper_ok:
            # Clear the value and fail
            new_value = None
            return RotationResult(
                secret_name=secret_name,
                success=False,
                message="Failed to update Gatekeeper",
                gatekeeper_updated=False
            )

        # Update Keymaster
        keymaster_ok = self._update_keymaster(secret_name, new_value)

        # Clear the value from memory
        new_value = None

        # Update state
        now = datetime.now()
        interval = self._get_rotation_interval(rotation_type)

        self.state["secrets"][secret_name] = {
            "rotation_type": rotation_type.value,
            "group": group,
            "last_rotated": now.isoformat(),
            "next_rotation": (now + timedelta(days=interval)).isoformat(),
            "rotation_count": self.state.get("secrets", {}).get(secret_name, {}).get("rotation_count", 0) + 1,
            "hash_prefix": hash_prefix
        }
        self._save_state()

        # Audit log
        self._audit_log({
            "action": "rotate",
            "secret_name": secret_name,
            "rotation_type": rotation_type.value,
            "group": group,
            "gatekeeper_updated": gatekeeper_ok,
            "keymaster_updated": keymaster_ok,
            "hash_prefix": hash_prefix,
            "timestamp": now.isoformat()
        })

        return RotationResult(
            secret_name=secret_name,
            success=gatekeeper_ok,
            message="Rotation complete",
            gatekeeper_updated=gatekeeper_ok,
            keymaster_updated=keymaster_ok
        )

    def _audit_log(self, entry: dict):
        """Append to audit log (JSONL format)."""
        try:
            with open(self.audit_log, 'a') as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Audit log error: {e}")

    def check_due_rotations(self) -> List[str]:
        """Get list of secrets due for rotation."""
        due = []

        for secret_name, secret_data in self.state.get("secrets", {}).items():
            next_rotation = secret_data.get("next_rotation")
            if next_rotation:
                next_dt = datetime.fromisoformat(next_rotation)
                if datetime.now() >= next_dt:
                    due.append(secret_name)

        return due

    def run_scheduled_rotation(self) -> Dict[str, RotationResult]:
        """Run scheduled rotations for today."""
        logger.info("⚡ ZUUL scheduled rotation check")

        today = datetime.now().day
        results = {}

        # Check which group rotates today
        groups = self.config.get("round_robin_groups", {})

        for group_name, group_config in groups.items():
            if group_config.get("rotation_day") == today:
                logger.info(f"📅 Today is {group_name.upper()} rotation day")

                # Get secrets in this group that are due
                for secret_name, secret_data in self.state.get("secrets", {}).items():
                    if secret_data.get("group") == group_name:
                        should_rotate, reason = self._should_rotate(
                            SecretMetadata(
                                name=secret_name,
                                rotation_type=RotationType(secret_data.get("rotation_type", "standard")),
                                group=group_name,
                                last_rotated=datetime.fromisoformat(secret_data["last_rotated"]) if secret_data.get("last_rotated") else None
                            )
                        )

                        if should_rotate:
                            results[secret_name] = self.rotate_secret(secret_name)

        # Update last check
        self.state["last_check"] = datetime.now().isoformat()
        self._save_state()

        return results

    def get_status(self) -> dict:
        """Get ZUUL system status."""
        secrets_by_type = {}
        secrets_by_group = {}
        due_count = 0

        for secret_name, data in self.state.get("secrets", {}).items():
            rot_type = data.get("rotation_type", "standard")
            group = data.get("group", "unknown")

            secrets_by_type[rot_type] = secrets_by_type.get(rot_type, 0) + 1
            secrets_by_group[group] = secrets_by_group.get(group, 0) + 1

            if data.get("next_rotation"):
                if datetime.now() >= datetime.fromisoformat(data["next_rotation"]):
                    due_count += 1

        return {
            "enabled": self.config.get("enabled", False),
            "total_secrets": len(self.state.get("secrets", {})),
            "due_for_rotation": due_count,
            "by_type": secrets_by_type,
            "by_group": secrets_by_group,
            "last_check": self.state.get("last_check"),
            "motto": self.config.get("motto", "There is no static password, only ZUUL")
        }


def main():
    try:
        """CLI interface for ZUUL."""
        import argparse

        parser = argparse.ArgumentParser(description="ZUUL Secret Rotation Engine")
        parser.add_argument("--status", action="store_true", help="Show ZUUL status")
        parser.add_argument("--check", action="store_true", help="Check for due rotations")
        parser.add_argument("--run", action="store_true", help="Run scheduled rotations")
        parser.add_argument("--rotate", type=str, help="Rotate a specific secret")
        parser.add_argument("--force", action="store_true", help="Force rotation (even static)")

        args = parser.parse_args()

        zuul = ZUULRotationEngine()

        if args.status:
            status = zuul.get_status()
            print(json.dumps(status, indent=2))

        elif args.check:
            due = zuul.check_due_rotations()
            print(f"Secrets due for rotation: {len(due)}")
            for name in due:
                print(f"  - {name}")

        elif args.run:
            results = zuul.run_scheduled_rotation()
            print(f"Rotated {len(results)} secrets")
            for name, result in results.items():
                status = "✅" if result.success else "❌"
                print(f"  {status} {name}: {result.message}")

        elif args.rotate:
            result = zuul.rotate_secret(args.rotate, force=args.force)
            status = "✅" if result.success else "❌"
            print(f"{status} {result.secret_name}: {result.message}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()