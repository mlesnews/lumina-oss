#!/usr/bin/env python3
"""
Homelab Holocron - SYPHON Integration

Homelab Holocron contains all specifics of Lumina homelab:
- Inventory of hardware and software
- All features and functionality
- Key mapping where applicable

Uses SYPHON and WOPR workflows to constantly improve and learn.
SYPHON extracts from all sources (internal/external) as often as possible
using dynamic scaling timing module.

Tags: #HOMELAB #HOLOCRON #SYPHON #WOPR #DYNAMIC_SCALING @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

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

logger = get_logger("HomelabHolocronSYPHON")

# SYPHON Integration
try:
    from syphon_system import SYPHONSystem, DataSourceType, SyphonData
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("⚠️  SYPHON system not available")

# Software Inventory Integration
try:
    from software_inventory_system import SoftwareInventorySystem, DeviceType
    INVENTORY_AVAILABLE = True
except ImportError:
    INVENTORY_AVAILABLE = False
    logger.warning("⚠️  Software inventory system not available")

# Dynamic Scaling Timing
try:
    from voice_pause_detection import DynamicVoicePauseDetection
    TIMING_AVAILABLE = True
except ImportError:
    TIMING_AVAILABLE = False
    logger.warning("⚠️  Dynamic timing module not available")


@dataclass
class HomelabHolocronEntry:
    """Entry in the homelab Holocron"""
    entry_id: str
    device_id: Optional[str] = None
    device_name: str = ""
    device_type: str = ""
    feature_id: Optional[str] = None
    feature_name: str = ""
    feature_description: str = ""
    functionality: List[str] = field(default_factory=list)
    key_mappings: Dict[str, str] = field(default_factory=dict)
    syphon_source: str = ""
    syphon_timestamp: str = ""
    extracted_intelligence: Dict[str, Any] = field(default_factory=dict)
    wopr_processed: bool = False
    last_updated: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["last_updated"] = self.last_updated.isoformat()
        return data


class HomelabHolocronSYPHON:
    """
    Homelab Holocron with SYPHON Integration

    Contains all specifics of Lumina homelab:
    - Inventory of hardware and software
    - All features and functionality
    - Key mapping where applicable

    Uses SYPHON to extract from all sources (internal/external)
    with dynamic scaling timing.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "holocron" / "homelab"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.holocron_file = self.data_dir / "homelab_holocron.json"
        self.syphon_log = self.data_dir / "syphon_log.jsonl"

        # Initialize systems
        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root=project_root)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON initialization failed: {e}")

        self.inventory = None
        if INVENTORY_AVAILABLE:
            try:
                self.inventory = SoftwareInventorySystem(project_root=project_root)
                logger.info("✅ Software inventory system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Inventory initialization failed: {e}")

        # Dynamic scaling timing for SYPHON frequency
        self.timing = None
        if TIMING_AVAILABLE:
            try:
                self.timing = DynamicVoicePauseDetection(
                    project_root=project_root,
                    initial_pause_seconds=60.0,  # Start with 60s between syphons
                    min_pause_seconds=10.0,  # Minimum 10s
                    max_pause_seconds=300.0  # Maximum 5 minutes
                )
                logger.info("✅ Dynamic timing module initialized")
            except Exception as e:
                logger.warning(f"⚠️  Timing module initialization failed: {e}")

        # Holocron entries
        self.entries: Dict[str, HomelabHolocronEntry] = {}

        # SYPHON daemon state
        self.syphon_daemon_running = False
        self.syphon_daemon_thread: Optional[threading.Thread] = None

        # Load existing holocron
        self._load_holocron()

        # Workflow tracker integration - track all SYPHON operations
        try:
            from workflow_tracker_integration import get_workflow_tracker, track_interaction
            self.workflow_tracker = get_workflow_tracker(project_root=project_root, auto_start=True)
            self.track_interaction = track_interaction
        except ImportError:
            self.workflow_tracker = None
            self.track_interaction = None

        logger.info("=" * 80)
        logger.info("🏠 HOMELAB HOLOCRON - SYPHON INTEGRATION")
        logger.info("=" * 80)
        logger.info("   Contains: Hardware/Software inventory, features, functionality")
        logger.info("   SYPHON: Extracts from all sources (internal/external)")
        logger.info("   Timing: Dynamic scaling (10s - 5min intervals)")
        logger.info(f"   Entries: {len(self.entries)}")
        logger.info("=" * 80)

    def _load_holocron(self):
        """Load holocron entries"""
        if self.holocron_file.exists():
            try:
                with open(self.holocron_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for entry_data in data.get("entries", []):
                    entry = self._dict_to_entry(entry_data)
                    self.entries[entry.entry_id] = entry

                logger.info(f"✅ Loaded {len(self.entries)} holocron entries")
            except Exception as e:
                logger.error(f"❌ Error loading holocron: {e}")

    def _save_holocron(self):
        """Save holocron entries"""
        try:
            data = {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "entries": [entry.to_dict() for entry in self.entries.values()]
            }

            with open(self.holocron_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved holocron ({len(self.entries)} entries)")
        except Exception as e:
            logger.error(f"❌ Error saving holocron: {e}")

    def _dict_to_entry(self, data: Dict[str, Any]) -> HomelabHolocronEntry:
        """Convert dict to HomelabHolocronEntry"""
        entry = HomelabHolocronEntry(
            entry_id=data["entry_id"],
            device_id=data.get("device_id"),
            device_name=data.get("device_name", ""),
            device_type=data.get("device_type", ""),
            feature_id=data.get("feature_id"),
            feature_name=data.get("feature_name", ""),
            feature_description=data.get("feature_description", ""),
            functionality=data.get("functionality", []),
            key_mappings=data.get("key_mappings", {}),
            syphon_source=data.get("syphon_source", ""),
            syphon_timestamp=data.get("syphon_timestamp", ""),
            extracted_intelligence=data.get("extracted_intelligence", {}),
            wopr_processed=data.get("wopr_processed", False)
        )

        if "last_updated" in data:
            entry.last_updated = datetime.fromisoformat(data["last_updated"])

        return entry

    def syphon_from_source(
        self,
        source_type: DataSourceType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[HomelabHolocronEntry]:
        """
        SYPHON intelligence from a source

        Extracts device/feature information and creates holocron entries.
        """
        # Track SYPHON operation in workflow tracker
        if self.track_interaction:
            try:
                self.track_interaction(
                    interaction_type="syphon_operation",
                    from_context="conversation",
                    to_context=f"syphon_{source_type.value}",
                    metadata={"source_type": source_type.value}
                )
            except Exception:
                pass  # Don't break SYPHON if tracker fails

        if not self.syphon:
            logger.warning("⚠️  SYPHON not available")
            return []

        entries = []

        try:
            # Use SYPHON to extract intelligence
            if source_type == DataSourceType.EMAIL:
                # Extract from email
                syphon_data = self.syphon.syphon_email(
                    email_id=metadata.get("email_id", f"email_{int(time.time())}"),
                    subject=metadata.get("subject", ""),
                    body=content,
                    from_address=metadata.get("from", ""),
                    to_address=metadata.get("to", ""),
                    metadata=metadata
                )
            elif source_type == DataSourceType.SMS:
                # Extract from SMS
                syphon_data = self.syphon.syphon_sms(
                    sms_id=metadata.get("sms_id", f"sms_{int(time.time())}"),
                    message=content,  # Fixed: use 'message' parameter
                    from_number=metadata.get("from", ""),
                    to_number=metadata.get("to", ""),
                    metadata=metadata
                )
            else:
                # Generic extraction - create syphon data manually
                # Extract intelligence using SYPHON's extraction methods
                actionable_items = self.syphon._extract_actionable_items(content)
                tasks = self.syphon._extract_tasks(content, "")
                decisions = self.syphon._extract_decisions(content)
                intelligence = self.syphon._extract_intelligence(content, "")

                syphon_data = SyphonData(
                    data_id=f"{source_type.value}_{int(time.time())}",
                    source_type=source_type,
                    source_id=metadata.get("source_id", f"source_{int(time.time())}"),
                    content=content,
                    metadata=metadata or {},
                    extracted_at=datetime.now(),
                    actionable_items=actionable_items,
                    tasks=tasks,
                    decisions=decisions,
                    intelligence=intelligence
                )

                # Add to SYPHON's extracted data
                self.syphon.extracted_data.append(syphon_data)
                self.syphon._save_extracted_data()

            # Process extracted intelligence for device/feature info
            entries = self._process_syphon_intelligence(syphon_data, source_type)

            # Save entries
            for entry in entries:
                self.entries[entry.entry_id] = entry

            self._save_holocron()

            # Log SYPHON event
            self._log_syphon(syphon_data, entries)

            logger.info(f"📚 SYPHON extracted {len(entries)} holocron entries from {source_type.value}")

        except Exception as e:
            logger.error(f"❌ Error syphoning from {source_type.value}: {e}")

        return entries

    def _process_syphon_intelligence(
        self,
        syphon_data: SyphonData,
        source_type: DataSourceType
    ) -> List[HomelabHolocronEntry]:
        """Process SYPHON intelligence and create holocron entries"""
        entries = []

        # Extract device mentions from intelligence
        intelligence = syphon_data.intelligence
        content = syphon_data.content

        # Look for device/feature patterns in content and intelligence
        device_patterns = [
            r"(?:device|equipment|hardware|system|server|nas|router|switch)\s+([A-Za-z0-9\s\-_]+)",
            r"([A-Za-z0-9\s\-_]+)\s+(?:has|supports|can|does)\s+([A-Za-z0-9\s\-_.,;:!?]+)",
        ]

        import re
        for pattern in device_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                device_name = match.group(1).strip()
                if len(device_name) > 2:
                    entry_id = f"holocron_{int(time.time())}_{len(entries)}"
                    entry = HomelabHolocronEntry(
                        entry_id=entry_id,
                        device_name=device_name,
                        syphon_source=source_type.value,
                        syphon_timestamp=syphon_data.extracted_at.isoformat(),
                        extracted_intelligence={
                            "actionable_items": syphon_data.actionable_items,
                            "tasks": syphon_data.tasks,
                            "decisions": syphon_data.decisions,
                            "intelligence": syphon_data.intelligence
                        }
                    )
                    entries.append(entry)

        # Process actionable items for features
        for item in syphon_data.actionable_items:
            # Look for feature mentions
            if any(kw in item.lower() for kw in ["feature", "functionality", "option", "setting"]):
                entry_id = f"holocron_{int(time.time())}_{len(entries)}"
                entry = HomelabHolocronEntry(
                    entry_id=entry_id,
                    feature_name=item[:100],  # First 100 chars
                    feature_description=item,
                    syphon_source=source_type.value,
                    syphon_timestamp=syphon_data.extracted_at.isoformat(),
                    extracted_intelligence={"actionable_item": item}
                )
                entries.append(entry)

        return entries

    def start_syphon_daemon(self):
        """Start SYPHON daemon with dynamic scaling timing"""
        if self.syphon_daemon_running:
            logger.warning("⚠️  SYPHON daemon already running")
            return

        self.syphon_daemon_running = True
        self.syphon_daemon_thread = threading.Thread(target=self._syphon_daemon_loop, daemon=True)
        self.syphon_daemon_thread.start()
        logger.info("🔄 SYPHON daemon started (dynamic scaling timing)")

    def stop_syphon_daemon(self):
        """Stop SYPHON daemon"""
        self.syphon_daemon_running = False
        if self.syphon_daemon_thread:
            self.syphon_daemon_thread.join(timeout=5.0)
        logger.info("⏹️  SYPHON daemon stopped")

    def _syphon_daemon_loop(self):
        """SYPHON daemon loop with dynamic scaling timing"""
        logger.info("🔄 SYPHON daemon loop started")

        while self.syphon_daemon_running:
            try:
                # Get dynamic timing interval
                if self.timing:
                    interval = self.timing.get_current_pause_seconds()
                else:
                    interval = 60.0  # Default 60 seconds

                # SYPHON from all sources
                self._syphon_all_sources()

                # Wait for next interval (dynamic scaling)
                time.sleep(interval)

            except Exception as e:
                logger.error(f"❌ Error in SYPHON daemon loop: {e}")
                time.sleep(10)  # Short wait on error

    def _syphon_all_sources(self):
        """SYPHON from all available sources"""
        # This would integrate with actual SYPHON sources
        # For now, log that we would syphon
        logger.debug(f"📚 SYPHON cycle: Would extract from all sources")

        # In production, this would:
        # 1. Check email sources
        # 2. Check SMS sources
        # 3. Check internal documentation
        # 4. Check external sources
        # 5. Process all through SYPHON
        # 6. Create holocron entries

    def _log_syphon(self, syphon_data: SyphonData, entries: List[HomelabHolocronEntry]):
        """Log SYPHON event"""
        try:
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "syphon_data_id": syphon_data.data_id,
                "source_type": syphon_data.source_type.value,
                "entries_created": len(entries),
                "entry_ids": [e.entry_id for e in entries]
            }

            with open(self.syphon_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error logging SYPHON: {e}")

    def get_holocron_table(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get holocron table grouped by device type"""
        table = {}

        for entry in self.entries.values():
            device_type = entry.device_type or "other"
            if device_type not in table:
                table[device_type] = []

            table[device_type].append({
                "entry_id": entry.entry_id,
                "device_name": entry.device_name,
                "feature_name": entry.feature_name,
                "functionality_count": len(entry.functionality),
                "syphon_source": entry.syphon_source,
                "last_updated": entry.last_updated.isoformat()
            })

        return table


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Homelab Holocron SYPHON")
    parser.add_argument("--start-daemon", action="store_true", help="Start SYPHON daemon")
    parser.add_argument("--stop-daemon", action="store_true", help="Stop SYPHON daemon")
    parser.add_argument("--table", action="store_true", help="Show holocron table")

    args = parser.parse_args()

    holocron = HomelabHolocronSYPHON()

    if args.start_daemon:
        holocron.start_syphon_daemon()
        print("✅ SYPHON daemon started")
        print("   Press Ctrl+C to stop")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            holocron.stop_syphon_daemon()

    if args.stop_daemon:
        holocron.stop_syphon_daemon()
        print("✅ SYPHON daemon stopped")

    if args.table:
        table = holocron.get_holocron_table()
        print("\n" + "=" * 80)
        print("🏠 HOMELAB HOLOCRON TABLE (Grouped by Device Type)")
        print("=" * 80)
        for device_type, entries in table.items():
            print(f"\n{device_type.upper()}:")
            for entry in entries:
                print(f"  - {entry['device_name']} / {entry['feature_name']}")
                print(f"    Source: {entry['syphon_source']}")
                print(f"    Functionality: {entry['functionality_count']} items")


if __name__ == "__main__":


    main()