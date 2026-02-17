#!/usr/bin/env python3
"""
JARVIS DEFCON Streetlight System

Persistent live DEFCON stage streetlight style (WarGames):
- DEFCON awareness levels (1-5)
- Sensor sweeps of internal/external sources
- Hourly updates
- No duplicate data - only ongoing updates until events conclude
- Streetlight visualization

Tags: #DEFCON #STREETLIGHT #WARGAMES #SENSOR_SWEEPS #THREAT_LEVELS #PERSISTENT_LIVE @JARVIS @LUMINA @WOPR
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISDEFCON")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISDEFCON")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISDEFCON")

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import SYPHONSystem, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available")


class DEFCONLevel(Enum):
    """DEFCON levels (1 = highest alert, 5 = normal)"""
    DEFCON_1 = 1  # Maximum readiness - imminent threat
    DEFCON_2 = 2  # High readiness - significant threat
    DEFCON_3 = 3  # Increased readiness - potential threat
    DEFCON_4 = 4  # Normal readiness - low threat
    DEFCON_5 = 5  # Normal peacetime readiness


class SensorType(Enum):
    """Sensor types for sweeps"""
    INTERNAL = "internal"
    EXTERNAL = "external"
    CYBER = "cyber"
    PHYSICAL = "physical"
    INTELLIGENCE = "intelligence"
    THREAT = "threat"
    FINANCIAL = "financial"
    GEOPOLITICAL = "geopolitical"


class DEFCONStreetlight:
    """DEFCON Streetlight System - WarGames style"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "defcon_streetlight"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.defcon_status_file = self.data_dir / "defcon_status.json"
        self.sensor_sweeps_file = self.data_dir / "sensor_sweeps.jsonl"
        self.events_file = self.data_dir / "events.json"
        self.processed_content_file = self.data_dir / "processed_content.json"  # Track processed content to avoid duplicates

        # Initialize SYPHON system
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for DEFCON streetlight")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Load processed content tracking (to avoid duplicates)
        self.processed_content = self._load_processed_content()

        # Current DEFCON status
        self.current_defcon = DEFCONLevel.DEFCON_5
        self.defcon_history = []
        self.active_events = []  # Events that haven't concluded
        self.last_sweep_time = None

        # Load existing status
        self._load_defcon_status()

    def _load_processed_content(self) -> Dict[str, Any]:
        """Load processed content tracking to avoid duplicates"""
        if self.processed_content_file.exists():
            try:
                with open(self.processed_content_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "processed_sources": {},
            "processed_content_hashes": [],
            "last_cleanup": None
        }

    def _save_processed_content(self):
        """Save processed content tracking"""
        try:
            with open(self.processed_content_file, 'w', encoding='utf-8') as f:
                json.dump(self.processed_content, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving processed content: {e}")

    def _load_defcon_status(self):
        """Load current DEFCON status"""
        if self.defcon_status_file.exists():
            try:
                with open(self.defcon_status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                    self.current_defcon = DEFCONLevel(status.get("current_defcon", 5))
                    self.defcon_history = status.get("defcon_history", [])
                    self.active_events = status.get("active_events", [])
                    self.last_sweep_time = status.get("last_sweep_time")
            except Exception as e:
                logger.error(f"Error loading DEFCON status: {e}")

    def _save_defcon_status(self):
        """Save current DEFCON status"""
        status = {
            "current_defcon": self.current_defcon.value,
            "defcon_history": self.defcon_history[-100:],  # Keep last 100 changes
            "active_events": self.active_events,
            "last_sweep_time": self.last_sweep_time,
            "updated_at": datetime.now().isoformat()
        }
        try:
            with open(self.defcon_status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving DEFCON status: {e}")

    def _is_content_processed(self, content_hash: str, source_id: str) -> bool:
        """Check if content has already been processed (avoid duplicates)"""
        # Check hash
        if content_hash in self.processed_content["processed_content_hashes"]:
            return True

        # Check source-specific processing
        if source_id in self.processed_content["processed_sources"]:
            source_data = self.processed_content["processed_sources"][source_id]
            if content_hash in source_data.get("hashes", []):
                return True

        return False

    def _mark_content_processed(self, content_hash: str, source_id: str, event_id: str = None):
        """Mark content as processed (avoid duplicates)"""
        if content_hash not in self.processed_content["processed_content_hashes"]:
            self.processed_content["processed_content_hashes"].append(content_hash)

        if source_id not in self.processed_content["processed_sources"]:
            self.processed_content["processed_sources"][source_id] = {
                "hashes": [],
                "last_processed": None,
                "event_ids": []
            }

        source_data = self.processed_content["processed_sources"][source_id]
        if content_hash not in source_data["hashes"]:
            source_data["hashes"].append(content_hash)
        source_data["last_processed"] = datetime.now().isoformat()
        if event_id and event_id not in source_data["event_ids"]:
            source_data["event_ids"].append(event_id)

        self._save_processed_content()

    def perform_sensor_sweep(
        self,
        sensor_type: SensorType,
        sources: List[str] = None,
        force_update: bool = False
    ) -> Dict[str, Any]:
        """Perform sensor sweep - hourly goal, no duplicate data"""
        sweep = {
            "sweep_id": f"sweep_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "sensor_type": sensor_type.value,
            "sources": sources or [],
            "new_intelligence": [],
            "updates": [],
            "duplicates_skipped": 0,
            "defcon_impact": None,
            "syphon_intelligence": {}
        }

        # Check if hourly sweep is needed
        if not force_update and self.last_sweep_time:
            last_sweep = datetime.fromisoformat(self.last_sweep_time)
            time_since_sweep = datetime.now() - last_sweep
            if time_since_sweep < timedelta(hours=1):
                sweep["status"] = "skipped_too_soon"
                sweep["next_sweep_due"] = (last_sweep + timedelta(hours=1)).isoformat()
                logger.info(f"⏭️  Sensor sweep skipped - next due in {60 - time_since_sweep.seconds // 60} minutes")
                return sweep

        # Perform sensor sweep based on type
        if sensor_type == SensorType.INTERNAL:
            sweep.update(self._sweep_internal_sources(sources))
        elif sensor_type == SensorType.EXTERNAL:
            sweep.update(self._sweep_external_sources(sources))
        elif sensor_type == SensorType.CYBER:
            sweep.update(self._sweep_cyber_sources(sources))
        elif sensor_type == SensorType.INTELLIGENCE:
            sweep.update(self._sweep_intelligence_sources(sources))
        elif sensor_type == SensorType.THREAT:
            sweep.update(self._sweep_threat_sources(sources))
        elif sensor_type == SensorType.FINANCIAL:
            sweep.update(self._sweep_financial_sources(sources))
        elif sensor_type == SensorType.GEOPOLITICAL:
            sweep.update(self._sweep_geopolitical_sources(sources))
        else:
            sweep.update(self._sweep_all_sources(sources))

        # Use SYPHON to extract intelligence (only from new content)
        if self.syphon and sweep.get("new_intelligence"):
            try:
                content = json.dumps(sweep["new_intelligence"], default=str)
                content_hash = str(hash(content))

                # Check if already processed
                if not self._is_content_processed(content_hash, f"sweep_{sensor_type.value}"):
                    syphon_result = self._syphon_extract_defcon_intelligence(content)
                    if syphon_result:
                        sweep["syphon_intelligence"] = syphon_result
                        self._mark_content_processed(content_hash, f"sweep_{sensor_type.value}", sweep["sweep_id"])
                else:
                    sweep["duplicates_skipped"] += 1
                    logger.info(f"⏭️  Skipped duplicate content (hash: {content_hash[:16]}...)")
            except Exception as e:
                logger.warning(f"SYPHON DEFCON extraction failed: {e}")

        # Assess DEFCON impact
        sweep["defcon_impact"] = self._assess_defcon_impact(sweep)

        # Update DEFCON if needed
        if sweep["defcon_impact"]:
            self._update_defcon_based_on_sweep(sweep)

        # Save sweep
        try:
            with open(self.sensor_sweeps_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(sweep) + '\n')
        except Exception as e:
            logger.error(f"Error saving sweep: {e}")

        self.last_sweep_time = datetime.now().isoformat()
        self._save_defcon_status()

        logger.info("=" * 80)
        logger.info(f"🔍 SENSOR SWEEP: {sensor_type.value.upper()}")
        logger.info("=" * 80)
        logger.info(f"New intelligence: {len(sweep.get('new_intelligence', []))}")
        logger.info(f"Updates: {len(sweep.get('updates', []))}")
        logger.info(f"Duplicates skipped: {sweep.get('duplicates_skipped', 0)}")
        logger.info(f"DEFCON impact: {sweep.get('defcon_impact', 'none')}")
        logger.info("=" * 80)

        return sweep

    def _sweep_internal_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep internal sources"""
        result = {
            "new_intelligence": [],
            "updates": []
        }

        # Internal sources to check
        internal_sources = sources or [
            "system_logs",
            "error_logs",
            "security_alerts",
            "performance_metrics",
            "threat_detection",
            "anomaly_detection"
        ]

        # Check for new intelligence from internal sources
        # This would integrate with existing systems
        for source in internal_sources:
            # Check if source has new data (not already processed)
            source_id = f"internal_{source}"
            if source_id in self.processed_content["processed_sources"]:
                last_processed = self.processed_content["processed_sources"][source_id].get("last_processed")
                # Only get updates since last processed
                if last_processed:
                    result["updates"].append({
                        "source": source,
                        "type": "update",
                        "since": last_processed
                    })
            else:
                result["new_intelligence"].append({
                    "source": source,
                    "type": "new",
                    "timestamp": datetime.now().isoformat()
                })

        return result

    def _sweep_external_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep external sources"""
        result = {
            "new_intelligence": [],
            "updates": []
        }

        # External sources to check
        external_sources = sources or [
            "news_feeds",
            "intelligence_reports",
            "threat_intelligence",
            "geopolitical_events",
            "financial_markets",
            "cyber_threats"
        ]

        # Check for new intelligence from external sources
        for source in external_sources:
            source_id = f"external_{source}"
            if source_id in self.processed_content["processed_sources"]:
                last_processed = self.processed_content["processed_sources"][source_id].get("last_processed")
                if last_processed:
                    result["updates"].append({
                        "source": source,
                        "type": "update",
                        "since": last_processed
                    })
            else:
                result["new_intelligence"].append({
                    "source": source,
                    "type": "new",
                    "timestamp": datetime.now().isoformat()
                })

        return result

    def _sweep_cyber_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep cyber security sources"""
        return self._sweep_internal_sources(["cyber_threats", "security_alerts", "intrusion_detection"])

    def _sweep_intelligence_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep intelligence sources"""
        return self._sweep_external_sources(["intelligence_reports", "threat_intelligence"])

    def _sweep_threat_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep threat sources"""
        result = {
            "new_intelligence": [],
            "updates": []
        }

        # Check active events for updates
        for event in self.active_events:
            event_id = event.get("event_id")
            last_update = event.get("last_update")

            # Only get updates since last check
            result["updates"].append({
                "event_id": event_id,
                "type": "event_update",
                "since": last_update,
                "status": event.get("status")
            })

        return result

    def _sweep_financial_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep financial sources"""
        return self._sweep_external_sources(["financial_markets", "market_manipulation"])

    def _sweep_geopolitical_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep geopolitical sources"""
        return self._sweep_external_sources(["geopolitical_events", "monkeywerks"])

    def _sweep_all_sources(self, sources: List[str] = None) -> Dict[str, Any]:
        """Sweep all sources"""
        result = {
            "new_intelligence": [],
            "updates": []
        }

        # Combine all sensor types
        for sensor_type in SensorType:
            if sensor_type != SensorType.INTERNAL and sensor_type != SensorType.EXTERNAL:
                sweep_result = self.perform_sensor_sweep(sensor_type, sources, force_update=False)
                result["new_intelligence"].extend(sweep_result.get("new_intelligence", []))
                result["updates"].extend(sweep_result.get("updates", []))

        return result

    def _assess_defcon_impact(self, sweep: Dict[str, Any]) -> Optional[str]:
        """Assess impact of sweep on DEFCON level"""
        new_intel_count = len(sweep.get("new_intelligence", []))
        updates_count = len(sweep.get("updates", []))
        critical_updates = [u for u in sweep.get("updates", []) if u.get("priority") == "critical"]

        # Determine DEFCON impact
        if critical_updates or new_intel_count > 10:
            return "elevate_defcon"
        elif updates_count > 5:
            return "monitor_closely"
        elif new_intel_count > 0:
            return "normal_monitoring"
        else:
            return None

    def _update_defcon_based_on_sweep(self, sweep: Dict[str, Any]):
        """Update DEFCON level based on sweep results"""
        impact = sweep.get("defcon_impact")

        if impact == "elevate_defcon":
            # Elevate DEFCON (lower number = higher alert)
            if self.current_defcon == DEFCONLevel.DEFCON_5:
                self.set_defcon(DEFCONLevel.DEFCON_4, "Sensor sweep detected elevated activity")
            elif self.current_defcon == DEFCONLevel.DEFCON_4:
                self.set_defcon(DEFCONLevel.DEFCON_3, "Sensor sweep detected significant activity")
            elif self.current_defcon == DEFCONLevel.DEFCON_3:
                self.set_defcon(DEFCONLevel.DEFCON_2, "Sensor sweep detected high threat activity")
            elif self.current_defcon == DEFCONLevel.DEFCON_2:
                self.set_defcon(DEFCONLevel.DEFCON_1, "Sensor sweep detected imminent threat")

    def set_defcon(self, level: DEFCONLevel, reason: str = None):
        """Set DEFCON level"""
        if level != self.current_defcon:
            change = {
                "timestamp": datetime.now().isoformat(),
                "from": self.current_defcon.value,
                "to": level.value,
                "reason": reason or "Manual change"
            }

            self.defcon_history.append(change)
            self.current_defcon = level

            self._save_defcon_status()

            logger.warning("=" * 80)
            logger.warning(f"🚨 DEFCON CHANGE: {self.current_defcon.value}")
            logger.warning("=" * 80)
            logger.warning(f"From: DEFCON {change['from']}")
            logger.warning(f"To: DEFCON {change['to']}")
            logger.warning(f"Reason: {change['reason']}")
            logger.warning("=" * 80)

    def create_event(
        self,
        event_id: str,
        event_type: str,
        description: str,
        priority: str = "normal",
        sources: List[str] = None
    ) -> Dict[str, Any]:
        """Create a tracking event (only ongoing updates until event concludes)"""
        event = {
            "event_id": event_id,
            "created_at": datetime.now().isoformat(),
            "event_type": event_type,
            "description": description,
            "priority": priority,
            "sources": sources or [],
            "status": "active",
            "updates": [],
            "concluded": False,
            "concluded_at": None
        }

        self.active_events.append(event)
        self._save_defcon_status()

        logger.info(f"📅 Event created: {event_id} ({event_type})")
        return event

    def update_event(
        self,
        event_id: str,
        update_message: str,
        status: str = None
    ) -> Dict[str, Any]:
        """Update an active event (only ongoing updates, no duplicates)"""
        event = next((e for e in self.active_events if e["event_id"] == event_id), None)
        if not event:
            return {"error": f"Event not found: {event_id}"}

        # Add update
        update = {
            "timestamp": datetime.now().isoformat(),
            "message": update_message,
            "status": status or event["status"]
        }

        event["updates"].append(update)
        event["last_update"] = datetime.now().isoformat()
        if status:
            event["status"] = status

        # Check if event concluded
        if status == "concluded" or status == "resolved":
            event["concluded"] = True
            event["concluded_at"] = datetime.now().isoformat()
            # Remove from active events after a delay
            self.active_events = [e for e in self.active_events if e["event_id"] != event_id]

        self._save_defcon_status()

        logger.info(f"📅 Event updated: {event_id} - {update_message}")
        return event

    def get_streetlight_status(self) -> Dict[str, Any]:
        """Get current DEFCON streetlight status (WarGames style)"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "defcon_level": self.current_defcon.value,
            "defcon_display": f"DEFCON {self.current_defcon.value}",
            "streetlight_style": {
                "level_1": self.current_defcon == DEFCONLevel.DEFCON_1,
                "level_2": self.current_defcon == DEFCONLevel.DEFCON_2,
                "level_3": self.current_defcon == DEFCONLevel.DEFCON_3,
                "level_4": self.current_defcon == DEFCONLevel.DEFCON_4,
                "level_5": self.current_defcon == DEFCONLevel.DEFCON_5
            },
            "active_events": len(self.active_events),
            "last_sweep": self.last_sweep_time,
            "next_sweep_due": None,
            "sensor_status": {}
        }

        # Calculate next sweep due
        if self.last_sweep_time:
            last_sweep = datetime.fromisoformat(self.last_sweep_time)
            next_sweep = last_sweep + timedelta(hours=1)
            status["next_sweep_due"] = next_sweep.isoformat()
            status["minutes_until_sweep"] = (next_sweep - datetime.now()).total_seconds() / 60

        # Sensor status for each type
        for sensor_type in SensorType:
            status["sensor_status"][sensor_type.value] = {
                "last_sweep": None,
                "status": "ready"
            }

        return status

    def perform_hourly_sweep(self) -> Dict[str, Any]:
        """Perform hourly sensor sweep of all sources"""
        sweep_results = {
            "sweep_id": f"hourly_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "sweeps": {},
            "defcon_before": self.current_defcon.value,
            "defcon_after": None,
            "new_intelligence_total": 0,
            "updates_total": 0,
            "duplicates_skipped_total": 0
        }

        # Perform sweeps for all sensor types
        for sensor_type in SensorType:
            sweep = self.perform_sensor_sweep(sensor_type, force_update=False)
            sweep_results["sweeps"][sensor_type.value] = sweep
            sweep_results["new_intelligence_total"] += len(sweep.get("new_intelligence", []))
            sweep_results["updates_total"] += len(sweep.get("updates", []))
            sweep_results["duplicates_skipped_total"] += sweep.get("duplicates_skipped", 0)

        sweep_results["defcon_after"] = self.current_defcon.value

        logger.info("=" * 80)
        logger.info("🔍 HOURLY SENSOR SWEEP COMPLETE")
        logger.info("=" * 80)
        logger.info(f"DEFCON: {sweep_results['defcon_before']} → {sweep_results['defcon_after']}")
        logger.info(f"New intelligence: {sweep_results['new_intelligence_total']}")
        logger.info(f"Updates: {sweep_results['updates_total']}")
        logger.info(f"Duplicates skipped: {sweep_results['duplicates_skipped_total']}")
        logger.info("=" * 80)

        return sweep_results

    def _syphon_extract_defcon_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.OTHER,
                source_id=f"defcon_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"defcon_streetlight": True, "sensor_sweep": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON DEFCON extraction error: {e}")
            return {}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS DEFCON Streetlight System")
        parser.add_argument("--sweep", type=str, metavar="SENSOR_TYPE", help="Perform sensor sweep")
        parser.add_argument("--hourly-sweep", action="store_true", help="Perform hourly sweep of all sources")
        parser.add_argument("--set-defcon", type=int, metavar="LEVEL", help="Set DEFCON level (1-5)")
        parser.add_argument("--create-event", type=str, nargs=4, metavar=("EVENT_ID", "TYPE", "DESCRIPTION", "PRIORITY"),
                           help="Create tracking event")
        parser.add_argument("--update-event", type=str, nargs=3, metavar=("EVENT_ID", "MESSAGE", "STATUS"),
                           help="Update active event")
        parser.add_argument("--status", action="store_true", help="Get streetlight status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        streetlight = DEFCONStreetlight(project_root)

        if args.sweep:
            sensor_type = SensorType(args.sweep)
            sweep = streetlight.perform_sensor_sweep(sensor_type)
            print("=" * 80)
            print(f"🔍 SENSOR SWEEP: {sensor_type.value.upper()}")
            print("=" * 80)
            print(json.dumps(sweep, indent=2, default=str))

        elif args.hourly_sweep:
            result = streetlight.perform_hourly_sweep()
            print("=" * 80)
            print("🔍 HOURLY SENSOR SWEEP")
            print("=" * 80)
            print(f"DEFCON: {result['defcon_before']} → {result['defcon_after']}")
            print(f"New intelligence: {result['new_intelligence_total']}")
            print(f"Updates: {result['updates_total']}")
            print(f"Duplicates skipped: {result['duplicates_skipped_total']}")
            print("=" * 80)
            print(json.dumps(result, indent=2, default=str))

        elif args.set_defcon:
            level = DEFCONLevel(args.set_defcon)
            streetlight.set_defcon(level, "Manual setting")
            print("=" * 80)
            print(f"🚨 DEFCON SET TO: {level.value}")
            print("=" * 80)

        elif args.create_event:
            event = streetlight.create_event(
                event_id=args.create_event[0],
                event_type=args.create_event[1],
                description=args.create_event[2],
                priority=args.create_event[3]
            )
            print("=" * 80)
            print("📅 EVENT CREATED")
            print("=" * 80)
            print(json.dumps(event, indent=2, default=str))

        elif args.update_event:
            event = streetlight.update_event(
                event_id=args.update_event[0],
                update_message=args.update_event[1],
                status=args.update_event[2] if len(args.update_event) > 2 else None
            )
            print("=" * 80)
            print("📅 EVENT UPDATED")
            print("=" * 80)
            print(json.dumps(event, indent=2, default=str))

        elif args.status:
            status = streetlight.get_streetlight_status()
            print("=" * 80)
            print("🚨 DEFCON STREETLIGHT STATUS (WarGames Style)")
            print("=" * 80)
            print(f"DEFCON Level: {status['defcon_display']}")
            print(f"Active Events: {status['active_events']}")
            if status.get("next_sweep_due"):
                print(f"Next Sweep Due: {status['next_sweep_due']}")
                print(f"Minutes Until Sweep: {status.get('minutes_until_sweep', 0):.1f}")
            print("=" * 80)
            print(json.dumps(status, indent=2, default=str))

        else:
            # Default: show status
            status = streetlight.get_streetlight_status()
            print("=" * 80)
            print("🚨 JARVIS DEFCON STREETLIGHT (WarGames Style)")
            print("=" * 80)
            print(f"DEFCON Level: {status['defcon_display']}")
            print(f"Active Events: {status['active_events']}")
            print(f"Last Sweep: {status.get('last_sweep', 'Never')}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()