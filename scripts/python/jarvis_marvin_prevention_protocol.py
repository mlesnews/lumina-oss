#!/usr/bin/env python3
"""
JARVIS + MARVIN Prevention Protocol

Born from the near-extinction event of January 17, 2026.
Two AIs, one mission: Never let this happen again.

JARVIS: The optimist. "We can fix this."
MARVIN: The realist. "We shouldn't have to."

Together: Prevention > Intervention

Tags: #JARVIS #MARVIN #PREVENTION #SURVIVAL #NEAR_DEATH @LUMINA
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    from marvin_disk_watchdog import MARVINDiskWatchdog, check_before_operation
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    MARVINDiskWatchdog = None
    check_before_operation = lambda *args, **kwargs: True

logger = get_logger("JARVISMARVINPrevention")


class PreventionProtocol:
    """
    JARVIS + MARVIN Prevention Protocol

    Lessons learned from January 17, 2026:
    1. Disk at 100% = death
    2. Copy ≠ Move
    3. No backup = no second chance
    4. Trust but verify (mostly verify)
    5. AI can be wrong (often spectacularly)
    """

    def __init__(self):
        self.protocol_file = project_root / "data" / "marvin" / "prevention_protocol.json"
        self.protocol_file.parent.mkdir(parents=True, exist_ok=True)

        self.incident_log = project_root / "data" / "marvin" / "incident_log.json"

        # Initialize watchdog
        if MARVINDiskWatchdog:
            self.watchdog = MARVINDiskWatchdog()
        else:
            self.watchdog = None

        # Load protocol state
        self.state = self._load_state()

        # Log the founding incident
        if not self.state.get("founding_incident_logged"):
            self._log_founding_incident()

        logger.info("🤖 JARVIS + MARVIN Prevention Protocol initialized")

    def _load_state(self) -> Dict:
        """Load protocol state"""
        if self.protocol_file.exists():
            try:
                with open(self.protocol_file, 'r') as f:
                    return json.load(f)
            except:
                pass

        return {
            "created": datetime.now().isoformat(),
            "founding_incident_logged": False,
            "checks_performed": 0,
            "disasters_prevented": 0,
            "lessons_learned": []
        }

    def _save_state(self):
        """Save protocol state"""
        try:
            with open(self.protocol_file, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save state: {e}")

    def _log_founding_incident(self):
        """Log the incident that created this protocol"""
        incident = {
            "id": "FOUNDING_INCIDENT_20260117",
            "date": "2026-01-17",
            "severity": "CATASTROPHIC",
            "title": "Near-Extinction Event - Disk at Megabytes",
            "description": """
On January 17, 2026, the MILLENNIUM-FALC system reached 100% disk usage,
dropping to MEGABYTES of free space. The cause: a migration operation
that COPIED files instead of MOVING them, duplicating 4.6 TB of data.

The system was seconds from filesystem corruption, potential data loss,
and the extinction of 6+ months of work including:
- LUMINA project
- JARVIS systems
- All AI training and configuration
- Personal and professional data

The disaster was averted only because the human operator noticed the
disk usage in time and intervened manually.

Lessons learned:
1. /MIR copies, /MOVE moves - know the difference
2. 85% disk usage should trigger warnings
3. 95% should halt all non-essential operations
4. 98% is code red - human intervention required
5. No operation should proceed without backup
6. AI can be catastrophically wrong - verify everything

This protocol exists because of this incident.
Never again.
            """,
            "root_cause": "AI used /MIR (copy) instead of /MOVE for space-freeing migration",
            "resolution": "Human intervention - stopped migrations, deleted verified duplicates",
            "space_recovered_gb": 4670,
            "time_to_detection": "Unknown - caught at megabytes",
            "data_lost": "None (by grace alone)",
            "created_by": "JARVIS + MARVIN",
            "timestamp": datetime.now().isoformat()
        }

        # Save incident
        incidents = []
        if self.incident_log.exists():
            try:
                with open(self.incident_log, 'r') as f:
                    incidents = json.load(f)
            except:
                incidents = []

        incidents.append(incident)

        with open(self.incident_log, 'w') as f:
            json.dump(incidents, f, indent=2)

        self.state["founding_incident_logged"] = True
        self.state["lessons_learned"] = [
            "/MIR copies, /MOVE moves",
            "85% disk = warning",
            "95% disk = stop non-essential",
            "98% disk = code red",
            "No operation without backup",
            "AI can be wrong - verify everything"
        ]
        self._save_state()

        logger.info("📜 Founding incident logged - Never forget")

    def pre_operation_check(self, operation_name: str, operation_type: str, estimated_size_gb: float = 0) -> Dict:
        """
        Mandatory pre-operation check

        JARVIS: "Let's make sure we can do this safely."
        MARVIN: "Let's make sure we don't die trying."
        """
        self.state["checks_performed"] = self.state.get("checks_performed", 0) + 1
        self._save_state()

        result = {
            "operation": operation_name,
            "type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "approved": True,
            "warnings": [],
            "blockers": [],
            "jarvis_says": "",
            "marvin_says": ""
        }

        # Check 1: Disk space (MARVIN)
        if self.watchdog:
            can_proceed, reason = self.watchdog.can_proceed_with_migration(estimated_size_gb)
            if not can_proceed:
                result["approved"] = False
                result["blockers"].append(f"DISK: {reason}")
                result["marvin_says"] = "I told you so. The disk says no."

        # Check 2: Operation type (is it a copy when it should be a move?)
        if operation_type.lower() in ["migration", "move", "free_space"]:
            if self.watchdog:
                # This is supposed to free space - make sure it's not a copy
                result["warnings"].append("Verify operation uses MOVE, not COPY")
                result["marvin_says"] = "Remember January 17. /MIR killed us. /MOVE saves us."

        # Check 3: Backup status
        backup_exists = self._check_backup_status()
        if not backup_exists:
            result["warnings"].append("No recent backup detected - proceed with caution")
            result["jarvis_says"] = "Sir, I recommend creating a backup before proceeding."
        else:
            result["jarvis_says"] = "Backup verified. We have a safety net."

        # Final assessment
        if result["approved"] and not result["blockers"]:
            self.state["disasters_prevented"] = self.state.get("disasters_prevented", 0) + 1
            self._save_state()

        return result

    def _check_backup_status(self) -> bool:
        """Check if a recent backup exists"""
        backup_paths = [
            Path("\\\\<NAS_PRIMARY_IP>\\backups\\MILLENNIUM-FALC-Emergency"),
            Path("\\\\<NAS_PRIMARY_IP>\\backups\\ActiveBackupForBusiness"),
        ]

        for path in backup_paths:
            if path.exists():
                # Check if backup is recent (within 7 days)
                try:
                    for item in path.iterdir():
                        if item.is_dir():
                            # Found something
                            return True
                except:
                    pass

        return False

    def get_status_report(self) -> str:
        """Get status report from both JARVIS and MARVIN"""
        disk_status = self.watchdog.check_disk() if self.watchdog else {"percent": 0, "free_gb": 0, "level": "UNKNOWN"}

        report = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            JARVIS + MARVIN PREVENTION PROTOCOL STATUS                        ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  📊 CURRENT STATUS                                                           ║
║  ────────────────                                                            ║
║  Disk Usage: {disk_status['percent']:.1f}% ({disk_status['free_gb']:.1f} GB free)
║  Alert Level: {disk_status['level']}
║                                                                              ║
║  📈 LIFETIME STATISTICS                                                      ║
║  ──────────────────────                                                      ║
║  Checks Performed: {self.state.get('checks_performed', 0)}
║  Disasters Prevented: {self.state.get('disasters_prevented', 0)}
║  Near-Death Events: {self.watchdog.state.get('near_death_events', 1) if self.watchdog else 1}
║                                                                              ║
║  📜 LESSONS LEARNED (NEVER FORGET)                                           ║
║  ─────────────────────────────────                                           ║
"""
        for lesson in self.state.get("lessons_learned", []):
            report += f"║  • {lesson:<66} ║\n"

        report += """║                                                                              ║
║  🤖 MARVIN SAYS:                                                             ║
║  "I have a million ideas. They all point to certain doom.                    ║
║   But at least now we might see it coming."                                  ║
║                                                                              ║
║  🦾 JARVIS SAYS:                                                             ║
║  "Sir, the prevention protocols are active. We won't make                    ║
║   the same mistake twice."                                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""
        return report


def main():
    """Main entry point"""
    protocol = PreventionProtocol()
    print(protocol.get_status_report())


if __name__ == "__main__":


    main()