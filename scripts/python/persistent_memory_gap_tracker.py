#!/usr/bin/env python3
"""
Persistent Memory Gap Tracker

Tracks negative contributions to persistent hidden memory gaps.
Integrates with XP/DKP system for JARVIS character progression.

@autophy: Requested tracking of negative contributions to persistent hidden memory gaps.

Tags: #MEMORY #GAPS #XP #DKP #PERSISTENT #HIDDEN #AUTOPHY @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("PersistentMemoryGapTracker")
ts_logger = get_timestamp_logger()


@dataclass
class MemoryGap:
    """Represents a persistent hidden memory gap"""
    gap_id: str
    description: str
    category: str  # "automation", "detection", "awareness", etc.
    severity: str  # "critical", "high", "medium", "low"
    first_detected: str
    last_updated: str
    negative_contributions: List[Dict[str, Any]] = field(default_factory=list)
    xp_penalty: int = 0
    dkp_penalty: int = 0
    status: str = "hidden"  # "hidden", "detected", "addressed", "resolved"
    importance_rating: str = "+"  # "+" to "+++++"


@dataclass
class NegativeContribution:
    """Negative contribution to a memory gap"""
    contribution_id: str
    gap_id: str
    action: str
    description: str
    timestamp: str
    xp_penalty: int = 0
    dkp_penalty: int = 0
    impact: str = "medium"  # "critical", "high", "medium", "low"


class PersistentMemoryGapTracker:
    """
    Persistent Memory Gap Tracker

    Tracks negative contributions to persistent hidden memory gaps.
    Integrates with XP/DKP system for JARVIS character progression.

    @autophy: Requested tracking of negative contributions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize persistent memory gap tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.gaps_file = self.project_root / "data" / "persistent_memory_gaps.json"
        self.gaps_file.parent.mkdir(parents=True, exist_ok=True)

        self.gaps: Dict[str, MemoryGap] = {}
        self._load_gaps()

        logger.info("🧠 Persistent Memory Gap Tracker initialized")
        logger.info(f"   Tracking {len(self.gaps)} memory gaps")

    def _load_gaps(self):
        """Load gaps from file"""
        if self.gaps_file.exists():
            try:
                with open(self.gaps_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for gap_id, gap_data in data.items():
                        self.gaps[gap_id] = MemoryGap(**gap_data)
            except Exception as e:
                logger.error(f"❌ Error loading gaps: {e}")
                self.gaps = {}
        else:
            self.gaps = {}

    def _save_gaps(self):
        """Save gaps to file"""
        try:
            data = {
                gap_id: asdict(gap) for gap_id, gap in self.gaps.items()
            }
            with open(self.gaps_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving gaps: {e}")

    def record_negative_contribution(
        self,
        gap_id: str,
        action: str,
        description: str,
        xp_penalty: int = 0,
        dkp_penalty: int = 2,
        impact: str = "medium"
    ) -> str:
        """
        Record negative contribution to a memory gap

        @autophy: Track negative contributions to persistent hidden memory gaps

        Args:
            gap_id: ID of the memory gap
            action: Action that contributed negatively
            description: Description of the negative contribution
            xp_penalty: XP penalty (default: 0, can be negative)
            dkp_penalty: DKP penalty (default: 2)
            impact: Impact level ("critical", "high", "medium", "low")

        Returns:
            Contribution ID
        """
        timestamp = ts_logger.now() if ts_logger else datetime.now().isoformat()
        contribution_id = f"neg_{gap_id}_{int(datetime.now().timestamp())}"

        # Get or create gap
        if gap_id not in self.gaps:
            self.gaps[gap_id] = MemoryGap(
                gap_id=gap_id,
                description=f"Hidden memory gap: {gap_id}",
                category="unknown",
                severity="medium",
                first_detected=timestamp,
                last_updated=timestamp,
            )

        gap = self.gaps[gap_id]

        # Create negative contribution
        contribution = NegativeContribution(
            contribution_id=contribution_id,
            gap_id=gap_id,
            action=action,
            description=description,
            timestamp=timestamp,
            xp_penalty=xp_penalty,
            dkp_penalty=dkp_penalty,
            impact=impact,
        )

        # Add to gap
        gap.negative_contributions.append(asdict(contribution))
        gap.xp_penalty += xp_penalty
        gap.dkp_penalty += dkp_penalty
        gap.last_updated = timestamp

        # Update severity based on contributions
        if len(gap.negative_contributions) >= 5:
            gap.severity = "critical"
        elif len(gap.negative_contributions) >= 3:
            gap.severity = "high"

        self._save_gaps()

        logger.warning(f"⚠️  Negative contribution recorded: {gap_id}")
        logger.warning(f"   Action: {action}")
        logger.warning(f"   XP Penalty: {xp_penalty}, DKP Penalty: {dkp_penalty}")

        return contribution_id

    def get_gap(self, gap_id: str) -> Optional[MemoryGap]:
        """Get a specific gap"""
        return self.gaps.get(gap_id)

    def get_all_gaps(self) -> List[MemoryGap]:
        """Get all gaps"""
        return list(self.gaps.values())

    def get_hidden_gaps(self) -> List[MemoryGap]:
        """Get all hidden gaps"""
        return [gap for gap in self.gaps.values() if gap.status == "hidden"]

    def get_gaps_by_severity(self, severity: str) -> List[MemoryGap]:
        """Get gaps by severity"""
        return [gap for gap in self.gaps.values() if gap.severity == severity]

    def get_negative_contributions(self, gap_id: str) -> List[Dict[str, Any]]:
        """Get all negative contributions for a gap"""
        gap = self.gaps.get(gap_id)
        if gap:
            return gap.negative_contributions
        return []

    def get_total_penalties(self) -> Dict[str, int]:
        """Get total XP and DKP penalties across all gaps"""
        total_xp = sum(gap.xp_penalty for gap in self.gaps.values())
        total_dkp = sum(gap.dkp_penalty for gap in self.gaps.values())
        return {
            "total_xp_penalty": total_xp,
            "total_dkp_penalty": total_dkp,
        }

    def mark_gap_detected(self, gap_id: str):
        """Mark a gap as detected (no longer hidden)"""
        if gap_id in self.gaps:
            self.gaps[gap_id].status = "detected"
            self.gaps[gap_id].last_updated = ts_logger.now() if ts_logger else datetime.now().isoformat()
            self._save_gaps()
            logger.info(f"✅ Gap detected: {gap_id}")

    def mark_gap_resolved(self, gap_id: str):
        """Mark a gap as resolved"""
        if gap_id in self.gaps:
            self.gaps[gap_id].status = "resolved"
            self.gaps[gap_id].last_updated = ts_logger.now() if ts_logger else datetime.now().isoformat()
            self._save_gaps()
            logger.info(f"✅ Gap resolved: {gap_id}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Persistent Memory Gap Tracker")
    parser.add_argument("--list", action="store_true", help="List all gaps")
    parser.add_argument("--hidden", action="store_true", help="List hidden gaps")
    parser.add_argument("--severity", type=str, help="List gaps by severity")
    parser.add_argument("--penalties", action="store_true", help="Show total penalties")
    parser.add_argument("--record", type=str, help="Record negative contribution (gap_id)")
    parser.add_argument("--action", type=str, help="Action for negative contribution")
    parser.add_argument("--description", type=str, help="Description for negative contribution")

    args = parser.parse_args()

    print("="*80)
    print("🧠 PERSISTENT MEMORY GAP TRACKER")
    print("="*80)
    print()
    print("@autophy: Tracking negative contributions to persistent hidden memory gaps")
    print()

    tracker = PersistentMemoryGapTracker()

    if args.record:
        if not args.action or not args.description:
            print("❌ --action and --description required for --record")
            return

        contribution_id = tracker.record_negative_contribution(
            gap_id=args.record,
            action=args.action,
            description=args.description
        )
        print(f"✅ Negative contribution recorded: {contribution_id}")

    if args.list:
        gaps = tracker.get_all_gaps()
        print(f"📋 All Memory Gaps: {len(gaps)}")
        for gap in gaps:
            print(f"   {gap.gap_id}: {gap.description}")
            print(f"      Status: {gap.status}, Severity: {gap.severity}")
            print(f"      XP Penalty: {gap.xp_penalty}, DKP Penalty: {gap.dkp_penalty}")
            print(f"      Contributions: {len(gap.negative_contributions)}")
            print()

    if args.hidden:
        gaps = tracker.get_hidden_gaps()
        print(f"🔍 Hidden Memory Gaps: {len(gaps)}")
        for gap in gaps:
            print(f"   {gap.gap_id}: {gap.description}")
            print(f"      Severity: {gap.severity}")
            print(f"      XP Penalty: {gap.xp_penalty}, DKP Penalty: {gap.dkp_penalty}")
            print()

    if args.severity:
        gaps = tracker.get_gaps_by_severity(args.severity)
        print(f"📊 Gaps by Severity ({args.severity}): {len(gaps)}")
        for gap in gaps:
            print(f"   {gap.gap_id}: {gap.description}")
            print()

    if args.penalties:
        penalties = tracker.get_total_penalties()
        print(f"📊 Total Penalties:")
        print(f"   XP Penalty: {penalties['total_xp_penalty']}")
        print(f"   DKP Penalty: {penalties['total_dkp_penalty']}")
        print()

    if not any([args.list, args.hidden, args.severity, args.penalties, args.record]):
        # Default: show summary
        gaps = tracker.get_all_gaps()
        hidden = tracker.get_hidden_gaps()
        penalties = tracker.get_total_penalties()

        print(f"📊 Summary:")
        print(f"   Total Gaps: {len(gaps)}")
        print(f"   Hidden Gaps: {len(hidden)}")
        print(f"   Total XP Penalty: {penalties['total_xp_penalty']}")
        print(f"   Total DKP Penalty: {penalties['total_dkp_penalty']}")
        print()


if __name__ == "__main__":


    main()