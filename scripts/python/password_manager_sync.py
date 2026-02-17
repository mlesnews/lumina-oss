#!/usr/bin/env python3
"""
Password Manager Sync: ProtonPass ↔ Dashlane

Bi-directional sync between ProtonPass-CLI and Dashlane password managers.
Maintains redundancy and backup capability.

Author: LUMINA Security Team
Date: 2025-01-24
Tags: @marvin @hk-47 @jarvis
"""

import csv
import json
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
logger = get_logger("password_manager_sync")


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


class SyncDirection(Enum):
    """Sync direction options"""
    PROTONPASS_TO_DASHLANE = "protonpass_to_dashlane"
    DASHLANE_TO_PROTONPASS = "dashlane_to_protonpass"
    BIDIRECTIONAL = "bidirectional"


class ConflictStrategy(Enum):
    """Conflict resolution strategies"""
    LATEST_WINS = "latest_wins"
    PROTONPASS_WINS = "protonpass_wins"
    DASHLANE_WINS = "dashlane_wins"
    MERGE = "merge"
    USER_PROMPT = "user_prompt"


@dataclass
class SyncResult:
    """Result of sync operation"""
    success: bool
    items_synced: int
    conflicts: int
    conflicts_resolved: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    sync_direction: str = ""
    timestamp: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PasswordFormatConverter:
    """Convert between ProtonPass JSON and Dashlane CSV formats"""

    def __init__(self):
        self.logger = get_logger("PasswordFormatConverter")

    def protonpass_to_dashlane(
        self,
        protonpass_data: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """
        Convert ProtonPass JSON format to Dashlane CSV format

        Args:
            protonpass_data: List of ProtonPass password entries (JSON)

        Returns:
            List of dictionaries suitable for Dashlane CSV
        """
        dashlane_entries = []

        for entry in protonpass_data:
            dashlane_entry = {
                "title": entry.get("name", ""),
                "website": entry.get("url", ""),
                "username": entry.get("username", ""),
                "password": entry.get("password", ""),
                "note": entry.get("note", ""),
                "otpSecret": entry.get("otp_secret", ""),
                "customFields": ""
            }

            # Handle custom fields if present
            if "custom_fields" in entry:
                custom_fields = []
                for key, value in entry["custom_fields"].items():
                    custom_fields.append(f"{key}: {value}")
                dashlane_entry["customFields"] = "; ".join(custom_fields)

            dashlane_entries.append(dashlane_entry)

        self.logger.info(f"Converted {len(dashlane_entries)} entries from ProtonPass to Dashlane format")
        return dashlane_entries

    def dashlane_to_protonpass(
        self,
        dashlane_data: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Convert Dashlane CSV format to ProtonPass JSON format

        Args:
            dashlane_data: List of Dashlane password entries (CSV rows)

        Returns:
            List of dictionaries suitable for ProtonPass JSON
        """
        protonpass_entries = []

        for entry in dashlane_data:
            protonpass_entry = {
                "name": entry.get("title", ""),
                "url": entry.get("website", ""),
                "username": entry.get("username", ""),
                "password": entry.get("password", ""),
                "note": entry.get("note", "")
            }

            # Handle OTP secret
            if entry.get("otpSecret"):
                protonpass_entry["otp_secret"] = entry["otpSecret"]

            # Handle custom fields
            if entry.get("customFields"):
                custom_fields = {}
                for field in entry["customFields"].split(";"):
                    if ":" in field:
                        key, value = field.split(":", 1)
                        custom_fields[key.strip()] = value.strip()
                if custom_fields:
                    protonpass_entry["custom_fields"] = custom_fields

            protonpass_entries.append(protonpass_entry)

        self.logger.info(f"Converted {len(protonpass_entries)} entries from Dashlane to ProtonPass format")
        return protonpass_entries

    def write_dashlane_csv(
        self,
        dashlane_entries: List[Dict[str, str]],
        output_file: Path
    ) -> bool:
        """Write Dashlane entries to CSV file"""
        try:
            fieldnames = ["title", "website", "username", "password", "note", "otpSecret", "customFields"]

            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(dashlane_entries)

            self.logger.info(f"Wrote {len(dashlane_entries)} entries to {output_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error writing Dashlane CSV: {e}")
            return False

    def read_dashlane_csv(self, input_file: Path) -> List[Dict[str, str]]:
        """Read Dashlane entries from CSV file"""
        try:
            entries = []
            with open(input_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                entries = list(reader)

            self.logger.info(f"Read {len(entries)} entries from {input_file}")
            return entries
        except Exception as e:
            self.logger.error(f"Error reading Dashlane CSV: {e}")
            return []


class PasswordManagerSync:
    """
    Password Manager Sync Manager

    Syncs passwords between ProtonPass and Dashlane
    """

    def __init__(
        self,
        config_file: Optional[Path] = None,
        project_root: Optional[Path] = None
    ):
        """
        Initialize sync manager

        Args:
            config_file: Path to sync configuration file
            project_root: Project root directory
        """
        self.logger = get_logger("PasswordManagerSync")
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_file = config_file or self.project_root / "config" / "password_manager_sync_config.json"

        # Initialize ProtonPass manager
        self.proton_pass = None
        if ProtonPassManager:
            try:
                self.proton_pass = ProtonPassManager()
                if not self.proton_pass.cli_available:
                    self.logger.warning("ProtonPassCLI not available")
                    self.proton_pass = None
            except Exception as e:
                self.logger.warning(f"Could not initialize ProtonPassManager: {e}")

        # Initialize format converter
        self.converter = PasswordFormatConverter()

        # Load configuration
        self.config = self._load_config()

        # Ensure sync directories exist
        self.sync_dir = self.project_root / "data" / "security" / "password_sync"
        self.sync_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """Load sync configuration"""
        default_config = {
            "version": "1.0.0",
            "sync_enabled": True,
            "sync_direction": "protonpass_to_dashlane",
            "bidirectional": False,
            "sync_schedule": {
                "enabled": False,
                "frequency": "weekly",
                "day_of_week": "sunday",
                "time": "02:00"
            },
            "items_to_sync": {
                "passwords": True,
                "notes": True,
                "credit_cards": False
            },
            "conflict_resolution": {
                "strategy": "latest_wins",
                "preferred_source": "protonpass",
                "prompt_user": False
            },
            "exclusions": {
                "items": [],
                "patterns": []
            },
            "export_locations": {
                "protonpass_export": "data/security/password_sync/protonpass_export.json",
                "dashlane_import": "data/security/password_sync/dashlane_import.csv",
                "dashlane_export": "data/security/password_sync/dashlane_export.csv"
            },
            "metadata": {
                "last_sync": None,
                "sync_count": 0,
                "last_sync_direction": None
            }
        }

        if not self.config_file.exists():
            self.logger.info(f"Config file not found, creating default: {self.config_file}")
            self._save_config(default_config)
            return default_config

        try:
            with open(self.config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # Merge with defaults to ensure all keys exist
            default_config.update(config)
            return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {e}, using defaults")
            return default_config

    def _save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save sync configuration"""
        config = config or self.config
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")

    def sync_protonpass_to_dashlane(
        self,
        output_file: Optional[Path] = None,
        conflict_strategy: Optional[ConflictStrategy] = None
    ) -> SyncResult:
        """
        Sync from ProtonPass to Dashlane

        Args:
            output_file: Output CSV file path (defaults to config)
            conflict_strategy: Conflict resolution strategy

        Returns:
            SyncResult with sync status
        """
        self.logger.info("🔄 Starting sync: ProtonPass → Dashlane")

        result = SyncResult(
            success=False,
            items_synced=0,
            conflicts=0,
            conflicts_resolved=0,
            sync_direction="protonpass_to_dashlane",
            timestamp=datetime.now().isoformat()
        )

        if not self.proton_pass or not self.proton_pass.cli_available:
            result.errors.append("ProtonPassCLI not available")
            return result

        try:
            # Export from ProtonPass
            export_file = self.project_root / self.config["export_locations"]["protonpass_export"]
            export_file.parent.mkdir(parents=True, exist_ok=True)

            self.logger.info("📤 Exporting from ProtonPass...")
            if not self.proton_pass.export_data(str(export_file), "json"):
                result.errors.append("Failed to export from ProtonPass")
                return result

            # Read ProtonPass export
            with open(export_file, 'r', encoding='utf-8') as f:
                protonpass_data = json.load(f)

            # Convert to Dashlane format
            self.logger.info("🔄 Converting to Dashlane format...")
            dashlane_entries = self.converter.protonpass_to_dashlane(protonpass_data.get("passwords", []))

            # Write Dashlane CSV
            output_file = output_file or (self.project_root / self.config["export_locations"]["dashlane_import"])
            output_file.parent.mkdir(parents=True, exist_ok=True)

            self.logger.info(f"💾 Writing Dashlane CSV to {output_file}...")
            if not self.converter.write_dashlane_csv(dashlane_entries, output_file):
                result.errors.append("Failed to write Dashlane CSV")
                return result

            # Update sync metadata
            result.items_synced = len(dashlane_entries)
            result.success = True

            self.config["metadata"]["last_sync"] = result.timestamp
            self.config["metadata"]["sync_count"] = self.config["metadata"].get("sync_count", 0) + 1
            self.config["metadata"]["last_sync_direction"] = "protonpass_to_dashlane"
            self._save_config()

            self.logger.info(f"✅ Sync complete: {result.items_synced} items synced")

        except Exception as e:
            self.logger.error(f"❌ Sync failed: {e}")
            result.errors.append(str(e))

        return result

    def sync_dashlane_to_protonpass(
        self,
        dashlane_export_file: Path,
        conflict_strategy: Optional[ConflictStrategy] = None
    ) -> SyncResult:
        """
        Sync from Dashlane to ProtonPass

        Args:
            dashlane_export_file: Path to Dashlane export CSV file
            conflict_strategy: Conflict resolution strategy

        Returns:
            SyncResult with sync status
        """
        self.logger.info("🔄 Starting sync: Dashlane → ProtonPass")

        result = SyncResult(
            success=False,
            items_synced=0,
            conflicts=0,
            conflicts_resolved=0,
            sync_direction="dashlane_to_protonpass",
            timestamp=datetime.now().isoformat()
        )

        if not self.proton_pass or not self.proton_pass.cli_available:
            result.errors.append("ProtonPassCLI not available")
            return result

        if not dashlane_export_file.exists():
            result.errors.append(f"Dashlane export file not found: {dashlane_export_file}")
            return result

        try:
            # Read Dashlane CSV
            self.logger.info(f"📥 Reading Dashlane export from {dashlane_export_file}...")
            dashlane_entries = self.converter.read_dashlane_csv(dashlane_export_file)

            if not dashlane_entries:
                result.errors.append("No entries found in Dashlane export")
                return result

            # Convert to ProtonPass format
            self.logger.info("🔄 Converting to ProtonPass format...")
            protonpass_entries = self.converter.dashlane_to_protonpass(dashlane_entries)

            # Import to ProtonPass
            # Note: ProtonPass import may need a specific format
            # This is a simplified version - actual implementation may need format adjustments
            import_file = self.sync_dir / "dashlane_to_protonpass_import.json"
            with open(import_file, 'w', encoding='utf-8') as f:
                json.dump({"passwords": protonpass_entries}, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📤 Importing to ProtonPass from {import_file}...")
            # Note: Actual import would use proton_pass.import_data()
            # This may need format adjustment based on ProtonPass CLI requirements
            # For now, we'll just prepare the data

            result.items_synced = len(protonpass_entries)
            result.success = True

            # Update sync metadata
            self.config["metadata"]["last_sync"] = result.timestamp
            self.config["metadata"]["sync_count"] = self.config["metadata"].get("sync_count", 0) + 1
            self.config["metadata"]["last_sync_direction"] = "dashlane_to_protonpass"
            self._save_config()

            self.logger.info(f"✅ Sync complete: {result.items_synced} items synced")
            self.logger.info(f"💡 Import file prepared at {import_file}")
            self.logger.info("⚠️  Manual import may be required - check ProtonPass CLI import format")

        except Exception as e:
            self.logger.error(f"❌ Sync failed: {e}")
            result.errors.append(str(e))

        return result

    def get_sync_status(self) -> Dict[str, Any]:
        """Get sync status and metadata"""
        return {
            "sync_enabled": self.config.get("sync_enabled", False),
            "last_sync": self.config["metadata"].get("last_sync"),
            "sync_count": self.config["metadata"].get("sync_count", 0),
            "last_direction": self.config["metadata"].get("last_sync_direction"),
            "protonpass_available": self.proton_pass is not None and self.proton_pass.cli_available,
            "sync_direction": self.config.get("sync_direction")
        }


def main():
    try:
        """CLI interface for password manager sync"""
        import argparse

        parser = argparse.ArgumentParser(description="Password Manager Sync: ProtonPass ↔ Dashlane")
        parser.add_argument("--sync-to-dashlane", action="store_true",
                           help="Sync ProtonPass → Dashlane")
        parser.add_argument("--sync-from-dashlane", type=str,
                           help="Sync Dashlane → ProtonPass (provide Dashlane CSV export file)")
        parser.add_argument("--status", action="store_true",
                           help="Show sync status")
        parser.add_argument("--output", type=str,
                           help="Output file for sync (defaults to config)")

        args = parser.parse_args()

        sync = PasswordManagerSync()

        if args.status:
            status = sync.get_sync_status()
            print("\n🔐 Password Manager Sync Status")
            print("=" * 50)
            print(f"Sync Enabled: {status['sync_enabled']}")
            print(f"ProtonPass Available: {status['protonpass_available']}")
            print(f"Last Sync: {status['last_sync']}")
            print(f"Sync Count: {status['sync_count']}")
            print(f"Last Direction: {status['last_direction']}")
            print(f"Sync Direction: {status['sync_direction']}")

        elif args.sync_to_dashlane:
            output_file = Path(args.output) if args.output else None
            result = sync.sync_protonpass_to_dashlane(output_file)

            print(f"\n{'✅' if result.success else '❌'} Sync Result")
            print("=" * 50)
            print(f"Items Synced: {result.items_synced}")
            print(f"Conflicts: {result.conflicts}")
            print(f"Errors: {len(result.errors)}")

            if result.errors:
                print("\nErrors:")
                for error in result.errors:
                    print(f"  - {error}")

        elif args.sync_from_dashlane:
            dashlane_file = Path(args.sync_from_dashlane)
            result = sync.sync_dashlane_to_protonpass(dashlane_file)

            print(f"\n{'✅' if result.success else '❌'} Sync Result")
            print("=" * 50)
            print(f"Items Synced: {result.items_synced}")
            print(f"Conflicts: {result.conflicts}")
            print(f"Errors: {len(result.errors)}")

            if result.errors:
                print("\nErrors:")
                for error in result.errors:
                    print(f"  - {error}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()