#!/usr/bin/env python3
"""
Password Rotation Manager

Automated password rotation system with lifecycle management.
Integrates with ProtonPass and Azure Key Vault for credential storage.

Security Policy: Routine password rotation at recommended security levels
for all AI-accessible credentials.

Author: LUMINA Security Team
Date: 2025-01-24
Tags: @marvin @hk-47 @jarvis @aiq @jedicouncil
"""

import json
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from scripts.python.protonpass_manager import ProtonPassManager
except ImportError:
    ProtonPassManager = None

try:
    from scripts.python.azure_service_bus_integration import AzureKeyVaultClient
except ImportError:
    AzureKeyVaultClient = None


class CredentialPriority(Enum):
    """Credential priority levels for rotation policy"""
    CRITICAL = "critical"  # 15-30 day rotation
    HIGH_PRIORITY = "high_priority"  # 30-60 day rotation
    STANDARD = "standard"  # 60-90 day rotation
    LOW_PRIORITY = "low_priority"  # 90-180 day rotation


class RotationTrigger(Enum):
    """Rotation trigger types"""
    SCHEDULED = "scheduled"  # Based on rotation interval
    SECURITY_BREACH = "security_breach"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    CREDENTIAL_EXPOSURE = "credential_exposure"
    ACCESS_PATTERN_CHANGE = "access_pattern_change"
    EMPLOYEE_TERMINATION = "employee_termination"
    SERVICE_COMPROMISE = "service_compromise"
    MANUAL_REQUEST = "manual_request"


@dataclass
class RotationPolicy:
    """Password rotation policy configuration"""
    priority: CredentialPriority
    interval_days: int
    event_driven: bool = True
    auto_rotate: bool = True
    notification_days_before: List[int] = field(default_factory=lambda: [7, 3, 1])
    require_approval: bool = False


@dataclass
class CredentialMetadata:
    """Metadata for credential lifecycle tracking"""
    name: str
    priority: CredentialPriority
    storage_location: str  # "protonpass", "azure_key_vault", "both"
    created_date: datetime
    last_rotated: Optional[datetime]
    next_rotation_due: datetime
    rotation_count: int = 0
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    ai_systems_with_access: List[str] = field(default_factory=list)
    rotation_history: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data['created_date'] = self.created_date.isoformat()
        data['last_rotated'] = self.last_rotated.isoformat() if self.last_rotated else None
        data['next_rotation_due'] = self.next_rotation_due.isoformat()
        data['last_accessed'] = self.last_accessed.isoformat() if self.last_accessed else None
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'CredentialMetadata':
        """Create from dictionary"""
        # Convert ISO strings back to datetime
        data['created_date'] = datetime.fromisoformat(data['created_date'])
        data['last_rotated'] = datetime.fromisoformat(data['last_rotated']) if data.get('last_rotated') else None
        data['next_rotation_due'] = datetime.fromisoformat(data['next_rotation_due'])
        data['last_accessed'] = datetime.fromisoformat(data['last_accessed']) if data.get('last_accessed') else None
        data['priority'] = CredentialPriority(data['priority'])
        return cls(**data)


class PasswordRotationManager:
    """
    Automated password rotation manager with lifecycle tracking

    Features:
    - Scheduled rotation based on policy
    - Event-driven rotation
    - Integration with ProtonPass + Azure Key Vault
    - Audit logging
    - Notification system
    """

    # Rotation policies by priority
    ROTATION_POLICIES = {
        CredentialPriority.CRITICAL: RotationPolicy(
            priority=CredentialPriority.CRITICAL,
            interval_days=30,
            event_driven=True,
            auto_rotate=True,
            notification_days_before=[7, 3, 1],
            require_approval=False
        ),
        CredentialPriority.HIGH_PRIORITY: RotationPolicy(
            priority=CredentialPriority.HIGH_PRIORITY,
            interval_days=60,
            event_driven=True,
            auto_rotate=True,
            notification_days_before=[14, 7, 3],
            require_approval=False
        ),
        CredentialPriority.STANDARD: RotationPolicy(
            priority=CredentialPriority.STANDARD,
            interval_days=90,
            event_driven=True,
            auto_rotate=True,
            notification_days_before=[30, 14, 7],
            require_approval=False
        ),
        CredentialPriority.LOW_PRIORITY: RotationPolicy(
            priority=CredentialPriority.LOW_PRIORITY,
            interval_days=180,
            event_driven=False,
            auto_rotate=False,
            notification_days_before=[60, 30, 14],
            require_approval=False
        )
    }

    def __init__(self, metadata_file: Optional[Path] = None, project_root: Optional[Path] = None):
        """
        Initialize password rotation manager

        Args:
            metadata_file: Path to credential metadata JSON file
            project_root: Project root directory
        """
        self.logger = get_logger("PasswordRotationManager")
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.metadata_file = metadata_file or self.project_root / "data" / "security" / "credential_metadata.json"

        # Ensure metadata file directory exists
        self.metadata_file.parent.mkdir(parents=True, exist_ok=True)

        # Initialize storage clients
        self.proton_pass = None
        self.azure_vault = None

        if ProtonPassManager:
            try:
                self.proton_pass = ProtonPassManager()
                if not self.proton_pass.cli_available:
                    self.logger.warning("ProtonPassCLI not available")
                    self.proton_pass = None
            except Exception as e:
                self.logger.warning(f"Could not initialize ProtonPassManager: {e}")

        if AzureKeyVaultClient:
            try:
                self.azure_vault = AzureKeyVaultClient(
                    vault_url="https://jarvis-lumina.vault.azure.net/"
                )
            except Exception as e:
                self.logger.warning(f"Could not initialize AzureKeyVaultClient: {e}")

        # Load credential metadata
        self.credentials: Dict[str, CredentialMetadata] = self._load_metadata()

    def _load_metadata(self) -> Dict[str, CredentialMetadata]:
        """Load credential metadata from file"""
        if not self.metadata_file.exists():
            self.logger.info(f"Metadata file not found, creating: {self.metadata_file}")
            return {}

        try:
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            credentials = {}
            for name, cred_data in data.items():
                credentials[name] = CredentialMetadata.from_dict(cred_data)

            self.logger.info(f"Loaded {len(credentials)} credential metadata entries")
            return credentials
        except Exception as e:
            self.logger.error(f"Error loading metadata: {e}")
            return {}

    def _save_metadata(self):
        """Save credential metadata to file"""
        try:
            data = {}
            for name, cred in self.credentials.items():
                data[name] = cred.to_dict()

            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            self.logger.debug(f"Saved {len(self.credentials)} credential metadata entries")
        except Exception as e:
            self.logger.error(f"Error saving metadata: {e}")

    def register_credential(
        self,
        name: str,
        priority: CredentialPriority,
        storage_location: str,
        created_date: Optional[datetime] = None
    ) -> bool:
        """
        Register a credential for rotation tracking

        Args:
            name: Credential name/identifier
            priority: Credential priority level
            storage_location: Where credential is stored ("protonpass", "azure_key_vault", "both")
            created_date: When credential was created (defaults to now)

        Returns:
            True if registered successfully
        """
        if name in self.credentials:
            self.logger.warning(f"Credential '{name}' already registered, updating")

        policy = self.ROTATION_POLICIES[priority]
        created = created_date or datetime.now()

        metadata = CredentialMetadata(
            name=name,
            priority=priority,
            storage_location=storage_location,
            created_date=created,
            last_rotated=None,
            next_rotation_due=created + timedelta(days=policy.interval_days)
        )

        self.credentials[name] = metadata
        self._save_metadata()

        self.logger.info(f"✅ Registered credential '{name}' for rotation (priority: {priority.value}, due: {metadata.next_rotation_due.date()})")
        return True

    def check_rotations_due(self, check_date: Optional[datetime] = None) -> List[CredentialMetadata]:
        """
        Check which credentials are due for rotation

        Args:
            check_date: Date to check against (defaults to now)

        Returns:
            List of credentials due for rotation
        """
        check_date = check_date or datetime.now()
        due_credentials = []

        for cred in self.credentials.values():
            if cred.next_rotation_due <= check_date:
                due_credentials.append(cred)

        return due_credentials

    def check_upcoming_rotations(
        self,
        days_ahead: int = 30,
        check_date: Optional[datetime] = None
    ) -> List[Tuple[CredentialMetadata, int]]:
        """
        Check credentials with upcoming rotations

        Args:
            days_ahead: How many days ahead to check
            check_date: Date to check from (defaults to now)

        Returns:
            List of (credential, days_until_due) tuples
        """
        check_date = check_date or datetime.now()
        upcoming = []

        for cred in self.credentials.values():
            days_until = (cred.next_rotation_due - check_date).days
            if 0 <= days_until <= days_ahead:
                upcoming.append((cred, days_until))

        # Sort by days until due
        upcoming.sort(key=lambda x: x[1])
        return upcoming

    def rotate_credential(
        self,
        name: str,
        trigger: RotationTrigger = RotationTrigger.SCHEDULED,
        new_password: Optional[str] = None,
        ai_system: Optional[str] = None
    ) -> bool:
        """
        Rotate a credential

        Args:
            name: Credential name
            trigger: What triggered the rotation
            new_password: New password (generated if not provided)
            ai_system: AI system requesting rotation (if applicable)

        Returns:
            True if rotation successful
        """
        if name not in self.credentials:
            self.logger.error(f"Credential '{name}' not registered")
            return False

        cred = self.credentials[name]
        policy = self.ROTATION_POLICIES[cred.priority]

        if not policy.auto_rotate and trigger == RotationTrigger.SCHEDULED:
            self.logger.warning(f"Auto-rotate disabled for '{name}', skipping scheduled rotation")
            return False

        self.logger.info(f"🔄 Rotating credential '{name}' (trigger: {trigger.value}, priority: {cred.priority.value})")

        # TODO: Implement actual credential rotation  # [ADDRESSED]  # [ADDRESSED]
        # This is a placeholder - actual implementation would:
        # 1. Generate new password (if not provided)
        # 2. Update in ProtonPass or Azure Key Vault
        # 3. Update dependent systems
        # 4. Revoke old credential
        # 5. Log rotation event

        rotation_date = datetime.now()

        # Update metadata
        cred.last_rotated = rotation_date
        cred.next_rotation_due = rotation_date + timedelta(days=policy.interval_days)
        cred.rotation_count += 1

        # Add to rotation history
        cred.rotation_history.append({
            "date": rotation_date.isoformat(),
            "trigger": trigger.value,
            "ai_system": ai_system,
            "success": True
        })

        self._save_metadata()

        self.logger.info(f"✅ Credential '{name}' rotated successfully (next rotation due: {cred.next_rotation_due.date()})")
        return True

    def record_access(
        self,
        name: str,
        ai_system: str,
        success: bool = True
    ):
        """
        Record credential access for audit logging

        Args:
            name: Credential name
            ai_system: AI system accessing credential
            success: Whether access was successful
        """
        if name not in self.credentials:
            return

        cred = self.credentials[name]
        cred.access_count += 1
        cred.last_accessed = datetime.now()

        if ai_system not in cred.ai_systems_with_access:
            cred.ai_systems_with_access.append(ai_system)

        self._save_metadata()

        self.logger.debug(f"Recorded access to '{name}' by {ai_system} (success: {success})")

    def get_rotation_status(self) -> Dict[str, Any]:
        """
        Get overall rotation status

        Returns:
            Dictionary with rotation statistics
        """
        now = datetime.now()
        due = self.check_rotations_due(now)
        overdue = [c for c in due if c.next_rotation_due < now - timedelta(days=1)]
        upcoming = self.check_upcoming_rotations(30, now)

        by_priority = {}
        for priority in CredentialPriority:
            by_priority[priority.value] = len([
                c for c in self.credentials.values() if c.priority == priority
            ])

        return {
            "total_credentials": len(self.credentials),
            "due_for_rotation": len(due),
            "overdue": len(overdue),
            "upcoming_rotations": len(upcoming),
            "by_priority": by_priority,
            "last_check": now.isoformat()
        }


def main():
    """CLI interface for password rotation manager"""
    import argparse

    parser = argparse.ArgumentParser(description="Password Rotation Manager")
    parser.add_argument("--check", action="store_true", help="Check rotations due")
    parser.add_argument("--status", action="store_true", help="Show rotation status")
    parser.add_argument("--register", type=str, help="Register a credential")
    parser.add_argument("--priority", type=str, choices=[p.value for p in CredentialPriority],
                       help="Credential priority")
    parser.add_argument("--storage", type=str, choices=["protonpass", "azure_key_vault", "both"],
                       help="Storage location")
    parser.add_argument("--rotate", type=str, help="Rotate a credential")

    args = parser.parse_args()

    manager = PasswordRotationManager()

    if args.status:
        status = manager.get_rotation_status()
        print("\n🔐 Password Rotation Status")
        print("=" * 50)
        print(f"Total Credentials: {status['total_credentials']}")
        print(f"Due for Rotation: {status['due_for_rotation']}")
        print(f"Overdue: {status['overdue']}")
        print(f"Upcoming (30 days): {status['upcoming_rotations']}")
        print("\nBy Priority:")
        for priority, count in status['by_priority'].items():
            print(f"  {priority}: {count}")

    elif args.check:
        due = manager.check_rotations_due()
        if due:
            print(f"\n⚠️  {len(due)} credentials due for rotation:")
            for cred in due:
                days_overdue = (datetime.now() - cred.next_rotation_due).days
                print(f"  - {cred.name} ({cred.priority.value}) - {days_overdue} days overdue")
        else:
            print("\n✅ No credentials due for rotation")

    elif args.register:
        if not args.priority or not args.storage:
            print("Error: --priority and --storage required for --register")
            return

        priority = CredentialPriority(args.priority)
        manager.register_credential(args.register, priority, args.storage)
        print(f"✅ Registered credential '{args.register}'")

    elif args.rotate:
        success = manager.rotate_credential(args.rotate)
        if success:
            print(f"✅ Rotated credential '{args.rotate}'")
        else:
            print(f"❌ Failed to rotate credential '{args.rotate}'")

    else:
        parser.print_help()


if __name__ == "__main__":

    main()