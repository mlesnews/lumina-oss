#!/usr/bin/env python3
"""
#AUTOPIN|UNPIN #AUTOARCHIVE System

Automatic pin/unpin and auto-archive for AI agent chat sessions.

Criteria:
- Line count > 100K → Auto-unpin + Auto-archive
- Age > 24 hours → Auto-unpin
- 3+ crashes → Auto-unpin + Auto-archive
- High memory → Auto-unpin
- Completed → Auto-unpin + Auto-archive

Tags: #AUTOPIN #UNPIN #AUTOARCHIVE #AI #AGENT #CHAT #AUTOMATION
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger(__name__)


class AutoPinUnpinAutoArchive:
    """#AUTOPIN|UNPIN #AUTOARCHIVE System"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.config = {
            "auto_unpin_line_count": 100000,
            "auto_unpin_age_hours": 24,
            "auto_unpin_crashes": 3,
            "auto_archive_age_days": 7,
            "auto_syphon_before_archive": True
        }

        logger.info("=" * 80)
        logger.info("#AUTOPIN|UNPIN #AUTOARCHIVE SYSTEM INITIALIZED")
        logger.info("=" * 80)

    def evaluate_session(self, session_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """@v3: Evaluate session with judicial approval"""
        # Try to use V3 judicial approval if available
        try:
            from v3_pin_decision_system import V3PinDecisionSystem
            v3_system = V3PinDecisionSystem()

            file_path = session_metrics.get("file_path", "unknown")
            reason = f"Auto-pin evaluation: line_count={session_metrics.get('line_count', 0)}, "
            reason += f"crashes={session_metrics.get('crashes', 0)}, age_hours={session_metrics.get('age_hours', 0)}"

            # Use V3 for unpin decision
            unpin_decision = v3_system.should_unpin_file(file_path, reason, session_metrics)

            # Use V3 for archive decision
            archive_decision = v3_system.should_archive_file(file_path, reason, session_metrics)

            return {
                "should_unpin": unpin_decision["should_unpin"],
                "should_archive": archive_decision["should_archive"],
                "should_syphon": archive_decision["should_archive"],  # Syphon before archive
                "reason": f"V3 Approved: {unpin_decision['rationale']}",
                "priority": "HIGH" if unpin_decision["status"] == "approved" else "NORMAL",
                "v3_ticket_id": unpin_decision.get("ticket_id"),
                "v3_status": unpin_decision["status"]
            }
        except ImportError:
            # Fallback to original logic if V3 not available
            pass

        # Original decision logic (fallback)
        decision = {
            "should_unpin": False,
            "should_archive": False,
            "should_syphon": False,
            "reason": "",
            "priority": "NORMAL"
        }

        # Check line count
        line_count = session_metrics.get("line_count", 0)
        if line_count >= self.config["auto_unpin_line_count"]:
            decision["should_unpin"] = True
            decision["should_archive"] = True
            decision["should_syphon"] = True
            decision["reason"] = f"Line count {line_count} >= {self.config['auto_unpin_line_count']}"
            decision["priority"] = "HIGH"

        # Check crashes
        crashes = session_metrics.get("crashes", 0)
        if crashes >= self.config["auto_unpin_crashes"]:
            decision["should_unpin"] = True
            decision["should_archive"] = True
            decision["should_syphon"] = True
            decision["reason"] = f"Crashes {crashes} >= {self.config['auto_unpin_crashes']}"
            decision["priority"] = "CRITICAL"

        # Check age
        age_hours = session_metrics.get("age_hours", 0)
        if age_hours >= self.config["auto_unpin_age_hours"]:
            decision["should_unpin"] = True
            decision["reason"] = f"Age {age_hours}h >= {self.config['auto_unpin_age_hours']}h"

        # Check archive age
        age_days = session_metrics.get("age_days", 0)
        if age_days >= self.config["auto_archive_age_days"]:
            decision["should_archive"] = True
            decision["should_syphon"] = True
            decision["reason"] = f"Age {age_days}d >= {self.config['auto_archive_age_days']}d"

        # Check completion
        if session_metrics.get("completed", False):
            decision["should_unpin"] = True
            decision["should_archive"] = True
            decision["should_syphon"] = True
            decision["reason"] = "Session completed"

        return decision

    def execute_decision(self, decision: Dict[str, Any], session_id: str) -> Dict[str, Any]:
        """@HK-47: Execute decision efficiently"""
        results = {
            "unpinned": False,
            "archived": False,
            "syphoned": False,
            "timestamp": datetime.now().isoformat()
        }

        if decision["should_syphon"] and self.config["auto_syphon_before_archive"]:
            # SYPHON session
            results["syphoned"] = self._syphon_session(session_id)

        if decision["should_unpin"]:
            # Auto-unpin (log action - actual unpin handled by IDE)
            logger.info(f"🔓 AUTO-UNPIN: {session_id} - {decision['reason']}")
            results["unpinned"] = True

        if decision["should_archive"]:
            # Auto-archive
            results["archived"] = self._archive_session(session_id)

        return results

    def _syphon_session(self, session_id: str) -> bool:
        """SYPHON session before archive"""
        try:
            # Import and run SYPHON
            from syphon_current_session_urgent import session_data
            output_dir = self.project_root / "data" / "syphon" / "chat_sessions"
            output_dir.mkdir(parents=True, exist_ok=True)

            output_file = output_dir / f"{session_id}_auto_syphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2)

            logger.info(f"✅ AUTO-SYPHON: {session_id} → {output_file.name}")
            return True
        except Exception as e:
            logger.error(f"❌ SYPHON failed: {e}")
            return False

    def _archive_session(self, session_id: str) -> bool:
        """Archive session"""
        try:
            archive_dir = self.project_root / "data" / "archived_sessions"
            archive_dir.mkdir(parents=True, exist_ok=True)

            archive_file = archive_dir / f"{session_id}_archived_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            archive_data = {
                "session_id": session_id,
                "archived_at": datetime.now().isoformat(),
                "reason": "AUTO-ARCHIVE",
                "status": "archived"
            }

            with open(archive_file, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2)

            logger.info(f"✅ AUTO-ARCHIVE: {session_id} → {archive_file.name}")
            return True
        except Exception as e:
            logger.error(f"❌ ARCHIVE failed: {e}")
            return False


def main():
    try:
        """Main entry point - @DOIT"""
        project_root = Path(__file__).parent.parent.parent
        system = AutoPinUnpinAutoArchive(project_root)

        # Current session metrics (from user report)
        current_metrics = {
            "session_id": "current_cursor_session",
            "line_count": 100000,  # ~100K lines
            "crashes": 3,  # 3 crashes in 5 minutes
            "age_hours": 0.1,  # Recent
            "age_days": 0,
            "completed": False,
            "memory_usage": "HIGH"
        }

        # @AIQ: Evaluate
        decision = system.evaluate_session(current_metrics)

        # @HK-47: Execute
        results = system.execute_decision(decision, current_metrics["session_id"])

        print("=" * 80)
        print("#AUTOPIN|UNPIN #AUTOARCHIVE DECISION")
        print("=" * 80)
        print()
        print(f"  Session: {current_metrics['session_id']}")
        print(f"  Line Count: {current_metrics['line_count']:,}")
        print(f"  Crashes: {current_metrics['crashes']}")
        print()
        print("  Decision:")
        print(f"    Unpin: {decision['should_unpin']} - {decision['reason']}")
        print(f"    Archive: {decision['should_archive']}")
        print(f"    SYPHON: {decision['should_syphon']}")
        print(f"    Priority: {decision['priority']}")
        print()
        print("  Results:")
        print(f"    Unpinned: {results['unpinned']}")
        print(f"    Archived: {results['archived']}")
        print(f"    Syphoned: {results['syphoned']}")
        print()
        print("=" * 80)

        return results


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()