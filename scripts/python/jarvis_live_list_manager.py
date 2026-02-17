#!/usr/bin/env python3
"""
JARVIS Live List Manager

Maintains active/live blacklist, whitelist, and greylist with real-time monitoring
and dynamic updates. Integrates with penalty system and MANUS control.

@JARVIS @PENALTY #BLACKLIST #WHITELIST #GREYLIST #LIVE #MONITORING
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
import logging
import hashlib

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISLiveListManager")

# Import penalty system
try:
    from jarvis_policy_violation_penalty import get_penalty_system, PolicyType, ViolationSeverity
    PENALTY_AVAILABLE = True
except ImportError:
    PENALTY_AVAILABLE = False
    get_penalty_system = None
    PolicyType = None
    ViolationSeverity = None
    logger.warning("⚠️  Penalty system not available")


class ListType(Enum):
    """List types"""
    BLACKLIST = "blacklist"
    WHITELIST = "whitelist"
    GREYLIST = "greylist"


class EntryStatus(Enum):
    """Entry status"""
    ACTIVE = "active"
    PENDING = "pending"
    EXPIRED = "expired"
    DISABLED = "disabled"


@dataclass
class ListEntry:
    """List entry"""
    entry_id: str
    list_type: ListType
    value: str
    category: str
    description: str
    status: EntryStatus
    created_at: datetime
    expires_at: Optional[datetime] = None
    created_by: str = "system"
    metadata: Dict[str, Any] = field(default_factory=dict)
    violation_count: int = 0
    last_violation: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['list_type'] = self.list_type.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        if self.expires_at:
            data['expires_at'] = self.expires_at.isoformat()
        if self.last_violation:
            data['last_violation'] = self.last_violation.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ListEntry':
        """Create from dictionary"""
        data['list_type'] = ListType(data['list_type'])
        data['status'] = EntryStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('expires_at'):
            data['expires_at'] = datetime.fromisoformat(data['expires_at'])
        else:
            data['expires_at'] = None
        if data.get('last_violation'):
            data['last_violation'] = datetime.fromisoformat(data['last_violation'])
        else:
            data['last_violation'] = None
        return cls(**data)

    def is_active(self) -> bool:
        """Check if entry is active"""
        if self.status != EntryStatus.ACTIVE:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        return True


class JARVISLiveListManager:
    """
    JARVIS Live List Manager

    Maintains active/live blacklist, whitelist, and greylist with:
    - Real-time monitoring
    - Dynamic updates
    - Automatic expiration
    - Violation tracking
    - Penalty integration
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "jarvis_live_lists"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.lists_file = self.data_dir / "live_lists.json"
        self.history_file = self.data_dir / "list_history.json"

        # Lists storage
        self.blacklist: Dict[str, ListEntry] = {}
        self.whitelist: Dict[str, ListEntry] = {}
        self.greylist: Dict[str, ListEntry] = {}

        # Greylist approval callbacks
        self.greylist_callbacks: Dict[str, Callable] = {}

        # Load existing lists
        self._load_lists()

        # Initialize penalty system
        self.penalty_system = None
        if PENALTY_AVAILABLE:
            try:
                self.penalty_system = get_penalty_system(project_root)
                self.logger.info("✅ Penalty system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Penalty system initialization failed: {e}")

        # Start monitoring thread
        self.monitoring_active = False
        self.monitor_thread = None
        self.start_monitoring()

        self.logger.info(f"✅ JARVIS Live List Manager initialized")
        self.logger.info(f"   Blacklist: {len([e for e in self.blacklist.values() if e.is_active()])} active entries")
        self.logger.info(f"   Whitelist: {len([e for e in self.whitelist.values() if e.is_active()])} active entries")
        self.logger.info(f"   Greylist: {len([e for e in self.greylist.values() if e.is_active()])} active entries")

    def _load_lists(self):
        """Load lists from storage"""
        try:
            if self.lists_file.exists():
                with open(self.lists_file, 'r') as f:
                    content = f.read().strip()
                    if not content:
                        return  # Empty file
                    data = json.loads(content)

                # Load blacklist
                for entry_data in data.get('blacklist', []):
                    try:
                        entry = ListEntry.from_dict(entry_data)
                        self.blacklist[entry.entry_id] = entry
                    except Exception as e:
                        self.logger.warning(f"⚠️  Failed to load blacklist entry: {e}")

                # Load whitelist
                for entry_data in data.get('whitelist', []):
                    try:
                        entry = ListEntry.from_dict(entry_data)
                        self.whitelist[entry.entry_id] = entry
                    except Exception as e:
                        self.logger.warning(f"⚠️  Failed to load whitelist entry: {e}")

                # Load greylist
                for entry_data in data.get('greylist', []):
                    try:
                        entry = ListEntry.from_dict(entry_data)
                        self.greylist[entry.entry_id] = entry
                    except Exception as e:
                        self.logger.warning(f"⚠️  Failed to load greylist entry: {e}")

                self.logger.info(f"✅ Loaded lists from storage")
        except json.JSONDecodeError as e:
            self.logger.warning(f"⚠️  Invalid JSON in lists file: {e} - creating new file")
            # Backup corrupted file
            if self.lists_file.exists():
                backup_file = self.lists_file.with_suffix('.json.bak')
                self.lists_file.rename(backup_file)
                self.logger.info(f"   Backed up corrupted file to: {backup_file}")
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load lists: {e}")

    def _save_lists(self):
        """Save lists to storage"""
        try:
            data = {
                'blacklist': [entry.to_dict() for entry in self.blacklist.values()],
                'whitelist': [entry.to_dict() for entry in self.whitelist.values()],
                'greylist': [entry.to_dict() for entry in self.greylist.values()],
                'last_updated': datetime.now().isoformat()
            }

            with open(self.lists_file, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.debug("✅ Lists saved to storage")
        except Exception as e:
            self.logger.error(f"❌ Failed to save lists: {e}")

    def _generate_entry_id(self, value: str, category: str) -> str:
        """Generate unique entry ID"""
        hash_input = f"{value}:{category}:{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:16]

    def add_entry(
        self,
        list_type: ListType,
        value: str,
        category: str,
        description: str,
        expires_in_hours: Optional[int] = None,
        created_by: str = "system",
        metadata: Optional[Dict[str, Any]] = None
    ) -> ListEntry:
        """
        Add entry to list

        Args:
            list_type: BLACKLIST, WHITELIST, or GREYLIST
            value: Value to add (e.g., "openai", "rm", "cursor_menu")
            category: Category (e.g., "cloud_api", "command", "ide_interaction")
            description: Description of why it's listed
            expires_in_hours: Optional expiration time
            created_by: Who created the entry
            metadata: Additional metadata
        """
        entry_id = self._generate_entry_id(value, category)

        expires_at = None
        if expires_in_hours:
            expires_at = datetime.now() + timedelta(hours=expires_in_hours)

        entry = ListEntry(
            entry_id=entry_id,
            list_type=list_type,
            value=value,
            category=category,
            description=description,
            status=EntryStatus.ACTIVE,
            created_at=datetime.now(),
            expires_at=expires_at,
            created_by=created_by,
            metadata=metadata or {}
        )

        # Add to appropriate list
        if list_type == ListType.BLACKLIST:
            self.blacklist[entry_id] = entry
        elif list_type == ListType.WHITELIST:
            self.whitelist[entry_id] = entry
        elif list_type == ListType.GREYLIST:
            self.greylist[entry_id] = entry

        self._save_lists()
        self.logger.info(f"✅ Added {list_type.value} entry: {value} ({category})")

        return entry

    def remove_entry(self, entry_id: str, list_type: Optional[ListType] = None) -> bool:
        """Remove entry from list"""
        removed = False

        if list_type:
            lists_to_check = {
                ListType.BLACKLIST: self.blacklist,
                ListType.WHITELIST: self.whitelist,
                ListType.GREYLIST: self.greylist
            }
            if entry_id in lists_to_check[list_type]:
                del lists_to_check[list_type][entry_id]
                removed = True
        else:
            # Check all lists
            for lst in [self.blacklist, self.whitelist, self.greylist]:
                if entry_id in lst:
                    del lst[entry_id]
                    removed = True
                    break

        if removed:
            self._save_lists()
            self.logger.info(f"✅ Removed entry: {entry_id}")

        return removed

    def check_value(
        self,
        value: str,
        category: Optional[str] = None,
        auto_approve_greylist: bool = False
    ) -> tuple[bool, Optional[str], Optional[ListEntry]]:
        """
        Check if value is allowed

        Returns:
            (allowed: bool, reason: str, entry: Optional[ListEntry])
        """
        # Check whitelist first (highest priority)
        for entry in self.whitelist.values():
            if entry.is_active() and entry.value.lower() == value.lower():
                if not category or entry.category == category:
                    return True, f"Whitelisted: {entry.description}", entry

        # Check blacklist (blocks everything)
        for entry in self.blacklist.values():
            if entry.is_active() and entry.value.lower() == value.lower():
                if not category or entry.category == category:
                    # Record violation
                    entry.violation_count += 1
                    entry.last_violation = datetime.now()
                    self._save_lists()

                    # Apply penalty
                    if self.penalty_system:
                        self.penalty_system.record_violation(
                            policy_type=PolicyType.BLACKLIST_VIOLATION,
                            action=f"attempted_{category}",
                            description=f"Blacklisted value '{value}': {entry.description}",
                            severity=ViolationSeverity.MAJOR,
                            blocked=True,
                            metadata={
                                "value": value,
                                "category": category,
                                "entry_id": entry.entry_id
                            }
                        )

                    return False, f"Blacklisted: {entry.description}", entry

        # Check greylist (requires approval)
        for entry in self.greylist.values():
            if entry.is_active() and entry.value.lower() == value.lower():
                if not category or entry.category == category:
                    if auto_approve_greylist:
                        return True, f"Greylist auto-approved: {entry.description}", entry
                    else:
                        # Check if callback exists for approval
                        callback = self.greylist_callbacks.get(entry.entry_id)
                        if callback and callback(entry):
                            return True, f"Greylist approved: {entry.description}", entry
                        else:
                            return False, f"Greylist requires approval: {entry.description}", entry

        # Not in any list - default allow
        return True, "Not in any list", None

    def register_greylist_callback(self, entry_id: str, callback: Callable[[ListEntry], bool]):
        """Register callback for greylist approval"""
        self.greylist_callbacks[entry_id] = callback
        self.logger.info(f"✅ Registered greylist callback for: {entry_id}")

    def start_monitoring(self):
        """Start live monitoring thread"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()
        self.logger.info("✅ Live monitoring started")

    def stop_monitoring(self):
        """Stop live monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        self.logger.info("🛑 Live monitoring stopped")

    def _monitoring_loop(self):
        """Live monitoring loop"""
        while self.monitoring_active:
            try:
                # Clean up expired entries
                self._cleanup_expired()

                # Update entry statuses
                self._update_statuses()

                # Save lists periodically
                self._save_lists()

                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"❌ Monitoring error: {e}")
                time.sleep(60)

    def _cleanup_expired(self):
        """Remove expired entries"""
        for lst in [self.blacklist, self.whitelist, self.greylist]:
            expired_ids = [
                entry_id for entry_id, entry in lst.items()
                if entry.expires_at and datetime.now() > entry.expires_at
            ]
            for entry_id in expired_ids:
                entry = lst[entry_id]
                entry.status = EntryStatus.EXPIRED
                self.logger.info(f"⏰ Entry expired: {entry.value} ({entry.category})")
                # Optionally remove expired entries
                # del lst[entry_id]

    def _update_statuses(self):
        """Update entry statuses"""
        for lst in [self.blacklist, self.whitelist, self.greylist]:
            for entry in lst.values():
                if entry.expires_at and datetime.now() > entry.expires_at:
                    entry.status = EntryStatus.EXPIRED

    def get_statistics(self) -> Dict[str, Any]:
        """Get list statistics"""
        return {
            'blacklist': {
                'total': len(self.blacklist),
                'active': len([e for e in self.blacklist.values() if e.is_active()]),
                'expired': len([e for e in self.blacklist.values() if e.status == EntryStatus.EXPIRED])
            },
            'whitelist': {
                'total': len(self.whitelist),
                'active': len([e for e in self.whitelist.values() if e.is_active()]),
                'expired': len([e for e in self.whitelist.values() if e.status == EntryStatus.EXPIRED])
            },
            'greylist': {
                'total': len(self.greylist),
                'active': len([e for e in self.greylist.values() if e.is_active()]),
                'expired': len([e for e in self.greylist.values() if e.status == EntryStatus.EXPIRED])
            }
        }

    def get_entries(
        self,
        list_type: Optional[ListType] = None,
        category: Optional[str] = None,
        active_only: bool = True
    ) -> List[ListEntry]:
        """Get entries matching criteria"""
        entries = []

        lists_to_check = []
        if list_type:
            lists_to_check = {
                ListType.BLACKLIST: self.blacklist,
                ListType.WHITELIST: self.whitelist,
                ListType.GREYLIST: self.greylist
            }[list_type]
        else:
            lists_to_check = {**self.blacklist, **self.whitelist, **self.greylist}

        for entry in lists_to_check.values():
            if active_only and not entry.is_active():
                continue
            if category and entry.category != category:
                continue
            entries.append(entry)

        return entries


# Global instance
_global_manager: Optional[JARVISLiveListManager] = None


def get_live_list_manager(project_root: Optional[Path] = None) -> JARVISLiveListManager:
    try:
        """Get or create global live list manager instance"""
        global _global_manager

        if _global_manager is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_manager = JARVISLiveListManager(project_root)

        return _global_manager


    except Exception as e:
        logger.error(f"Error in get_live_list_manager: {e}", exc_info=True)
        raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Live List Manager")
    parser.add_argument("--add-blacklist", nargs=3, metavar=("VALUE", "CATEGORY", "DESCRIPTION"), help="Add to blacklist")
    parser.add_argument("--add-whitelist", nargs=3, metavar=("VALUE", "CATEGORY", "DESCRIPTION"), help="Add to whitelist")
    parser.add_argument("--add-greylist", nargs=3, metavar=("VALUE", "CATEGORY", "DESCRIPTION"), help="Add to greylist")
    parser.add_argument("--check", nargs=2, metavar=("VALUE", "CATEGORY"), help="Check value")
    parser.add_argument("--list", choices=["blacklist", "whitelist", "greylist", "all"], help="List entries")
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--remove", type=str, help="Remove entry by ID")
    parser.add_argument("--expires", type=int, help="Expiration in hours (for add commands)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    manager = JARVISLiveListManager(project_root)

    if args.add_blacklist:
        value, category, description = args.add_blacklist
        entry = manager.add_entry(
            ListType.BLACKLIST,
            value,
            category,
            description,
            expires_in_hours=args.expires
        )
        print(f"✅ Added to blacklist: {entry.entry_id}")

    if args.add_whitelist:
        value, category, description = args.add_whitelist
        entry = manager.add_entry(
            ListType.WHITELIST,
            value,
            category,
            description,
            expires_in_hours=args.expires
        )
        print(f"✅ Added to whitelist: {entry.entry_id}")

    if args.add_greylist:
        value, category, description = args.add_greylist
        entry = manager.add_entry(
            ListType.GREYLIST,
            value,
            category,
            description,
            expires_in_hours=args.expires
        )
        print(f"✅ Added to greylist: {entry.entry_id}")

    if args.check:
        value, category = args.check
        allowed, reason, entry = manager.check_value(value, category)
        print(f"{'✅ ALLOWED' if allowed else '🚫 BLOCKED'}: {value}")
        print(f"   Reason: {reason}")
        if entry:
            print(f"   Entry ID: {entry.entry_id}")

    if args.list:
        if args.list == "all":
            list_types = [ListType.BLACKLIST, ListType.WHITELIST, ListType.GREYLIST]
        else:
            list_types = [ListType[args.list.upper()]]

        for list_type in list_types:
            entries = manager.get_entries(list_type, active_only=True)
            print(f"\n{list_type.value.upper()} ({len(entries)} active):")
            for entry in entries[:20]:  # Show first 20
                print(f"   {entry.value} ({entry.category}) - {entry.description}")
            if len(entries) > 20:
                print(f"   ... and {len(entries) - 20} more")

    if args.stats:
        stats = manager.get_statistics()
        print("\n" + "="*80)
        print("JARVIS LIVE LIST STATISTICS")
        print("="*80)
        for list_name, list_stats in stats.items():
            print(f"\n{list_name.upper()}:")
            print(f"   Total: {list_stats['total']}")
            print(f"   Active: {list_stats['active']}")
            print(f"   Expired: {list_stats['expired']}")
        print("="*80)

    if args.remove:
        removed = manager.remove_entry(args.remove)
        print(f"{'✅ Removed' if removed else '❌ Not found'}: {args.remove}")

    if not any([args.add_blacklist, args.add_whitelist, args.add_greylist, args.check, args.list, args.stats, args.remove]):
        parser.print_help()


if __name__ == "__main__":


    main()