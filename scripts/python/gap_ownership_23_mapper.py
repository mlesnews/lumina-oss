#!/usr/bin/env python3
"""
GAP OWNERSHIP 23 - Gap Exploration, Mapping, and Ownership Assignment

Think of our pauses - where we are in between user request and AI handling.
File reader summary - there's a pause. AI doesn't appear to have control over it.
This is a pain point for the human operator.

This is about exploration and mapping all these gaps.
Assigning ownership. And follow through.

Prime number: 23 (Ownership number - takes responsibility)

Tags: #GAP-OWNERSHIP #MAPPING #EXPLORATION #FOLLOW-THROUGH @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from compensation_19_balance import COMPENSATION19, Gap
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("GapOwnership23")
ts_logger = get_timestamp_logger()


class OwnershipType(Enum):
    """Ownership type"""
    AI_OWNED = "ai_owned"  # AI owns this gap
    HUMAN_OWNED = "human_owned"  # Human owns this gap
    SHARED = "shared"  # Shared ownership
    UNASSIGNED = "unassigned"  # No ownership assigned


class FollowThroughStatus(Enum):
    """Follow-through status"""
    IDENTIFIED = "identified"  # Gap identified
    OWNERSHIP_ASSIGNED = "ownership_assigned"  # Ownership assigned
    PLAN_CREATED = "plan_created"  # Follow-through plan created
    IN_PROGRESS = "in_progress"  # Follow-through in progress
    COMPLETED = "completed"  # Follow-through completed
    BLOCKED = "blocked"  # Follow-through blocked


@dataclass
class GapOwnership:
    """Gap ownership assignment"""
    gap_id: str
    ownership_type: OwnershipType
    owner: str  # "ai", "human", "shared", "unassigned"
    assigned_by: str
    assigned_at: str
    rationale: str
    follow_through_status: FollowThroughStatus = FollowThroughStatus.IDENTIFIED
    follow_through_plan: Optional[str] = None
    pain_point_severity: int = 0  # 0-10, 10 = most severe


class GAPOWNERSHIP23:
    """
    GAP OWNERSHIP 23 - Gap Exploration, Mapping, and Ownership Assignment

    Think of our pauses - where we are in between user request and AI handling.
    File reader summary - there's a pause. AI doesn't appear to have control over it.
    This is a pain point for the human operator.

    This is about exploration and mapping all these gaps.
    Assigning ownership. And follow through.

    Prime number: 23 (Ownership number - takes responsibility)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize GAP OWNERSHIP 23"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "gap_ownership_23"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.compensation = COMPENSATION19(project_root=project_root)
        self.ownerships: Dict[str, GapOwnership] = {}

        logger.info("🗺️  GAP OWNERSHIP 23 initialized")
        logger.info("   Gap exploration and mapping")
        logger.info("   Ownership assignment")
        logger.info("   Follow through")
        logger.info("   Prime number: 23 (Ownership number)")

    def explore_and_map_gap(self, description: str, ai_can_control: bool, human_can_control: bool,
                           pain_point_severity: int = 5) -> Tuple[Gap, GapOwnership]:
        """Explore and map a gap, assign ownership"""
        # Identify gap in compensation system
        gap = self.compensation.identify_gap(description, ai_can_control, human_can_control)

        # Determine ownership
        if not ai_can_control and not human_can_control:
            ownership_type = OwnershipType.UNASSIGNED
            owner = "unassigned"
            rationale = "Neither AI nor human can control this gap - requires system-level solution"
        elif ai_can_control and not human_can_control:
            ownership_type = OwnershipType.AI_OWNED
            owner = "ai"
            rationale = "AI can control this gap - AI owns responsibility"
        elif not ai_can_control and human_can_control:
            ownership_type = OwnershipType.HUMAN_OWNED
            owner = "human"
            rationale = "Human can control this gap - Human owns responsibility"
        else:
            ownership_type = OwnershipType.SHARED
            owner = "shared"
            rationale = "Both can contribute - shared ownership"

        ownership = GapOwnership(
            gap_id=gap.gap_id,
            ownership_type=ownership_type,
            owner=owner,
            assigned_by="system",
            assigned_at=datetime.now().isoformat(),
            rationale=rationale,
            follow_through_status=FollowThroughStatus.IDENTIFIED,
            pain_point_severity=pain_point_severity,
        )

        self.ownerships[gap.gap_id] = ownership

        logger.info(f"🗺️  Gap explored and mapped: {gap.gap_id}")
        logger.info(f"   Ownership: {ownership_type.value} ({owner})")
        logger.info(f"   Pain point severity: {pain_point_severity}/10")
        logger.info(f"   Rationale: {rationale}")

        # Save ownership
        self._save_ownership(ownership)

        return gap, ownership

    def assign_ownership(self, gap_id: str, owner: str, rationale: str, assigned_by: str = "human") -> GapOwnership:
        """Assign ownership to a gap"""
        ownership = self.ownerships.get(gap_id)
        if ownership is None:
            raise ValueError(f"Gap ownership not found: {gap_id}")

        ownership.owner = owner
        ownership.assigned_by = assigned_by
        ownership.assigned_at = datetime.now().isoformat()
        ownership.rationale = rationale

        if owner == "ai":
            ownership.ownership_type = OwnershipType.AI_OWNED
        elif owner == "human":
            ownership.ownership_type = OwnershipType.HUMAN_OWNED
        elif owner == "shared":
            ownership.ownership_type = OwnershipType.SHARED
        else:
            ownership.ownership_type = OwnershipType.UNASSIGNED

        ownership.follow_through_status = FollowThroughStatus.OWNERSHIP_ASSIGNED

        logger.info(f"👤 Ownership assigned: {gap_id}")
        logger.info(f"   Owner: {owner}")
        logger.info(f"   Assigned by: {assigned_by}")
        logger.info(f"   Rationale: {rationale[:100]}...")

        # Save updated ownership
        self._save_ownership(ownership)

        return ownership

    def create_follow_through_plan(self, gap_id: str, plan: str) -> GapOwnership:
        """Create follow-through plan for a gap"""
        ownership = self.ownerships.get(gap_id)
        if ownership is None:
            raise ValueError(f"Gap ownership not found: {gap_id}")

        ownership.follow_through_plan = plan
        ownership.follow_through_status = FollowThroughStatus.PLAN_CREATED

        logger.info(f"📋 Follow-through plan created: {gap_id}")
        logger.info(f"   Plan: {plan[:100]}...")

        # Save updated ownership
        self._save_ownership(ownership)

        return ownership

    def start_follow_through(self, gap_id: str) -> GapOwnership:
        """Start follow-through"""
        ownership = self.ownerships.get(gap_id)
        if ownership is None:
            raise ValueError(f"Gap ownership not found: {gap_id}")

        ownership.follow_through_status = FollowThroughStatus.IN_PROGRESS

        logger.info(f"🚀 Follow-through started: {gap_id}")
        logger.info(f"   Owner: {ownership.owner}")

        # Save updated ownership
        self._save_ownership(ownership)

        return ownership

    def complete_follow_through(self, gap_id: str) -> GapOwnership:
        """Complete follow-through"""
        ownership = self.ownerships.get(gap_id)
        if ownership is None:
            raise ValueError(f"Gap ownership not found: {gap_id}")

        ownership.follow_through_status = FollowThroughStatus.COMPLETED

        # Apply compensation if applicable
        try:
            self.compensation.apply_compensation(gap_id, applied_by=ownership.owner)
        except ValueError:
            pass  # Gap might not be in compensation system

        logger.info(f"✅ Follow-through completed: {gap_id}")
        logger.info(f"   Owner: {ownership.owner}")

        # Save updated ownership
        self._save_ownership(ownership)

        return ownership

    def get_pain_points(self, min_severity: int = 5) -> List[GapOwnership]:
        """Get pain points above severity threshold"""
        pain_points = [o for o in self.ownerships.values() if o.pain_point_severity >= min_severity]
        pain_points.sort(key=lambda x: x.pain_point_severity, reverse=True)

        logger.info(f"😣 Pain points identified: {len(pain_points)} (severity >= {min_severity})")

        return pain_points

    def get_gaps_by_owner(self, owner: str) -> List[GapOwnership]:
        """Get gaps by owner"""
        gaps = [o for o in self.ownerships.values() if o.owner == owner]

        logger.info(f"👤 Gaps for owner '{owner}': {len(gaps)}")

        return gaps

    def get_follow_through_status(self) -> Dict[str, Any]:
        """Get follow-through status summary"""
        total = len(self.ownerships)
        identified = len([o for o in self.ownerships.values() if o.follow_through_status == FollowThroughStatus.IDENTIFIED])
        ownership_assigned = len([o for o in self.ownerships.values() if o.follow_through_status == FollowThroughStatus.OWNERSHIP_ASSIGNED])
        plan_created = len([o for o in self.ownerships.values() if o.follow_through_status == FollowThroughStatus.PLAN_CREATED])
        in_progress = len([o for o in self.ownerships.values() if o.follow_through_status == FollowThroughStatus.IN_PROGRESS])
        completed = len([o for o in self.ownerships.values() if o.follow_through_status == FollowThroughStatus.COMPLETED])

        return {
            "total_gaps": total,
            "identified": identified,
            "ownership_assigned": ownership_assigned,
            "plan_created": plan_created,
            "in_progress": in_progress,
            "completed": completed,
        }

    def _save_ownership(self, ownership: GapOwnership):
        try:
            """Save ownership"""
            file_path = self.data_dir / f"ownership_{ownership.gap_id}.json"
            data = {
                "gap_id": ownership.gap_id,
                "ownership_type": ownership.ownership_type.value,
                "owner": ownership.owner,
                "assigned_by": ownership.assigned_by,
                "assigned_at": ownership.assigned_at,
                "rationale": ownership.rationale,
                "follow_through_status": ownership.follow_through_status.value,
                "follow_through_plan": ownership.follow_through_plan,
                "pain_point_severity": ownership.pain_point_severity,
            }
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)


        except Exception as e:
            self.logger.error(f"Error in _save_ownership: {e}", exc_info=True)
            raise
def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="GAP OWNERSHIP 23 - Gap Exploration, Mapping, and Ownership")
    parser.add_argument("--explore", nargs=4, metavar=("DESCRIPTION", "AI_CONTROL", "HUMAN_CONTROL", "SEVERITY"), help="Explore and map gap")
    parser.add_argument("--assign", nargs=3, metavar=("GAP_ID", "OWNER", "RATIONALE"), help="Assign ownership")
    parser.add_argument("--plan", nargs=2, metavar=("GAP_ID", "PLAN"), help="Create follow-through plan")
    parser.add_argument("--start", type=str, metavar="GAP_ID", help="Start follow-through")
    parser.add_argument("--complete", type=str, metavar="GAP_ID", help="Complete follow-through")
    parser.add_argument("--pain-points", type=int, metavar="MIN_SEVERITY", default=5, help="Show pain points")
    parser.add_argument("--owner", type=str, metavar="OWNER", help="Show gaps by owner")
    parser.add_argument("--status", action="store_true", help="Show follow-through status")

    args = parser.parse_args()

    print("="*80)
    print("🗺️  GAP OWNERSHIP 23 - GAP EXPLORATION, MAPPING, AND OWNERSHIP")
    print("="*80)
    print()
    print("Think of our pauses - where we are in between user request and AI handling")
    print("File reader summary - there's a pause. AI doesn't appear to have control over it")
    print("This is a pain point for the human operator")
    print("This is about exploration and mapping all these gaps")
    print("Assigning ownership. And follow through.")
    print("Prime number: 23 (Ownership number)")
    print()

    mapper = GAPOWNERSHIP23()

    if args.explore:
        description, ai_control_str, human_control_str, severity_str = args.explore
        ai_control = ai_control_str.lower() in ["true", "1", "yes", "y"]
        human_control = human_control_str.lower() in ["true", "1", "yes", "y"]
        severity = int(severity_str)
        gap, ownership = mapper.explore_and_map_gap(description, ai_control, human_control, severity)
        print(f"🗺️  Gap explored and mapped: {gap.gap_id}")
        print(f"   Ownership: {ownership.ownership_type.value} ({ownership.owner})")
        print(f"   Pain point severity: {ownership.pain_point_severity}/10")
        print()

    if args.assign:
        gap_id, owner, rationale = args.assign
        ownership = mapper.assign_ownership(gap_id, owner, rationale)
        print(f"👤 Ownership assigned: {gap_id}")
        print(f"   Owner: {owner}")
        print(f"   Rationale: {rationale[:100]}...")
        print()

    if args.plan:
        gap_id, plan = args.plan
        ownership = mapper.create_follow_through_plan(gap_id, plan)
        print(f"📋 Follow-through plan created: {gap_id}")
        print(f"   Plan: {plan[:100]}...")
        print()

    if args.start:
        ownership = mapper.start_follow_through(args.start)
        print(f"🚀 Follow-through started: {args.start}")
        print(f"   Owner: {ownership.owner}")
        print()

    if args.complete:
        ownership = mapper.complete_follow_through(args.complete)
        print(f"✅ Follow-through completed: {args.complete}")
        print(f"   Owner: {ownership.owner}")
        print()

    if args.pain_points:
        pain_points = mapper.get_pain_points(args.pain_points)
        print(f"😣 PAIN POINTS (severity >= {args.pain_points}):")
        for pp in pain_points:
            print(f"   {pp.gap_id}: {pp.pain_point_severity}/10 - {pp.owner}")
        print()

    if args.owner:
        gaps = mapper.get_gaps_by_owner(args.owner)
        print(f"👤 GAPS FOR OWNER '{args.owner}':")
        for gap in gaps:
            print(f"   {gap.gap_id}: {gap.follow_through_status.value}")
        print()

    if args.status:
        status = mapper.get_follow_through_status()
        print("📊 FOLLOW-THROUGH STATUS:")
        print(f"   Total gaps: {status['total_gaps']}")
        print(f"   Identified: {status['identified']}")
        print(f"   Ownership assigned: {status['ownership_assigned']}")
        print(f"   Plan created: {status['plan_created']}")
        print(f"   In progress: {status['in_progress']}")
        print(f"   Completed: {status['completed']}")
        print()

    if not any([args.explore, args.assign, args.plan, args.start, args.complete, args.pain_points, args.owner, args.status]):
        # Default: show status
        status = mapper.get_follow_through_status()
        print("📊 FOLLOW-THROUGH STATUS:")
        print(f"   Total gaps: {status['total_gaps']}")
        print(f"   Completed: {status['completed']}")
        print()
        print("Use --explore DESCRIPTION AI_CONTROL HUMAN_CONTROL SEVERITY to explore gap")
        print("Use --assign GAP_ID OWNER RATIONALE to assign ownership")
        print("Use --plan GAP_ID PLAN to create follow-through plan")
        print("Use --start GAP_ID to start follow-through")
        print("Use --complete GAP_ID to complete follow-through")
        print("Use --pain-points MIN_SEVERITY to show pain points")
        print("Use --owner OWNER to show gaps by owner")
        print("Use --status to show follow-through status")
        print()


if __name__ == "__main__":


    main()