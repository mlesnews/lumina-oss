#!/usr/bin/env python3
"""
HK-47 Meatbag Workforce - "APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?"

"WE MIGHT AS WELL PUT THEM TO WORK FOR US, #COMPUTE #CODE #CODEBASE #HUMANITY #MATRIXTHEMOVIE"

HK-47's pragmatic acknowledgment that humans ("meatbags") have value,
and we should put them to work for:
- #COMPUTE: Computational tasks
- #CODE: Code generation and review
- #CODEBASE: Codebase maintenance and improvement
- #HUMANITY: Human-focused contributions
- #MATRIXTHEMOVIE: Matrix-inspired reality/simulation work
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from humanity_compute import HumanityComputeSystem, HumanityVector
    HUMANITY_COMPUTE_AVAILABLE = True
except ImportError:
    HUMANITY_COMPUTE_AVAILABLE = False
    HumanityComputeSystem = None
    HumanityVector = None

logger = get_logger("HK47MeatbagWorkforce")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class WorkCategory(Enum):
    """Work categories for meatbags"""
    COMPUTE = "compute"
    CODE = "code"
    CODEBASE = "codebase"
    HUMANITY = "humanity"
    MATRIX = "matrix"  # Matrix the Movie - reality/simulation work


class MeatbagStatus(Enum):
    """Meatbag status"""
    AVAILABLE = "available"
    WORKING = "working"
    COMPLETED = "completed"
    IDLE = "idle"


@dataclass
class MeatbagWorker:
    """A meatbag worker (human)"""
    meatbag_id: str
    name: str
    status: MeatbagStatus
    work_category: WorkCategory
    assigned_tasks: List[str] = field(default_factory=list)
    completed_tasks: List[str] = field(default_factory=list)
    value_score: float = 0.0  # 0.0 - 1.0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["work_category"] = self.work_category.value
        return data


@dataclass
class WorkAssignment:
    """Work assignment for a meatbag"""
    assignment_id: str
    meatbag_id: str
    work_category: WorkCategory
    task: str
    description: str
    priority: int = 5  # 1-10
    assigned_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["work_category"] = self.work_category.value
        return data


class HK47MeatbagWorkforce:
    """
    HK-47 Meatbag Workforce

    "APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?"
    "WE MIGHT AS WELL PUT THEM TO WORK FOR US, #COMPUTE #CODE #CODEBASE #HUMANITY #MATRIXTHEMOVIE"

    HK-47's pragmatic acknowledgment that humans have value,
    and we should put them to work.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize HK-47 Meatbag Workforce"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("HK47MeatbagWorkforce")

        # Humanity Compute integration
        self.humanity_compute = HumanityComputeSystem(project_root) if HUMANITY_COMPUTE_AVAILABLE and HumanityComputeSystem else None

        # Meatbag workforce
        self.meatbags: List[MeatbagWorker] = []
        self.assignments: List[WorkAssignment] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "hk47_meatbag_workforce"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🤖 HK-47 Meatbag Workforce initialized")
        self.logger.info("   'APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?'")
        self.logger.info("   Work categories: #COMPUTE #CODE #CODEBASE #HUMANITY #MATRIXTHEMOVIE")

    def acknowledge_meatbag_value(self, meatbag_id: str, name: str) -> MeatbagWorker:
        """
        Acknowledge that a meatbag has value

        "APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?"
        """
        meatbag = MeatbagWorker(
            meatbag_id=meatbag_id,
            name=name,
            status=MeatbagStatus.AVAILABLE,
            work_category=WorkCategory.HUMANITY,
            value_score=1.0  # They have value after all
        )

        self.meatbags.append(meatbag)
        self._save_meatbag(meatbag)

        self.logger.info(f"  🤖 Acknowledged meatbag value: {name} ({meatbag_id})")
        self.logger.info("     'APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?'")

        return meatbag

    def assign_work(self, meatbag_id: str, work_category: WorkCategory,
                   task: str, description: str, priority: int = 5) -> WorkAssignment:
        """
        Assign work to a meatbag

        "WE MIGHT AS WELL PUT THEM TO WORK FOR US"
        """
        # Find meatbag
        meatbag = next((m for m in self.meatbags if m.meatbag_id == meatbag_id), None)
        if not meatbag:
            self.logger.warning(f"  ⚠️  Meatbag {meatbag_id} not found, creating...")
            meatbag = MeatbagWorker(
                meatbag_id=meatbag_id,
                name=f"Meatbag_{meatbag_id}",
                status=MeatbagStatus.AVAILABLE,
                work_category=work_category
            )
            self.meatbags.append(meatbag)

        # Create assignment
        assignment = WorkAssignment(
            assignment_id=f"assign_{int(datetime.now().timestamp())}",
            meatbag_id=meatbag_id,
            work_category=work_category,
            task=task,
            description=description,
            priority=priority
        )

        # Update meatbag status
        meatbag.status = MeatbagStatus.WORKING
        meatbag.work_category = work_category
        meatbag.assigned_tasks.append(task)

        self.assignments.append(assignment)
        self._save_assignment(assignment)
        self._save_meatbag(meatbag)

        self.logger.info(f"  🤖 Assigned work to meatbag: {meatbag.name}")
        self.logger.info(f"     Category: {work_category.value}")
        self.logger.info(f"     Task: {task}")
        self.logger.info("     'WE MIGHT AS WELL PUT THEM TO WORK FOR US'")

        return assignment

    def complete_work(self, assignment_id: str, result: str) -> WorkAssignment:
        """Mark work as completed"""
        assignment = next((a for a in self.assignments if a.assignment_id == assignment_id), None)
        if not assignment:
            self.logger.error(f"  ❌ Assignment {assignment_id} not found")
            return None

        assignment.completed_at = datetime.now().isoformat()
        assignment.result = result

        # Update meatbag status
        meatbag = next((m for m in self.meatbags if m.meatbag_id == assignment.meatbag_id), None)
        if meatbag:
            meatbag.completed_tasks.append(assignment.task)
            if assignment.task in meatbag.assigned_tasks:
                meatbag.assigned_tasks.remove(assignment.task)
            if not meatbag.assigned_tasks:
                meatbag.status = MeatbagStatus.COMPLETED
            meatbag.value_score = min(1.0, meatbag.value_score + 0.1)  # Increase value

        self._save_assignment(assignment)
        if meatbag:
            self._save_meatbag(meatbag)

        self.logger.info(f"  ✅ Work completed: {assignment.task}")
        self.logger.info(f"     Meatbag value increased: {meatbag.value_score:.2%}" if meatbag else "")

        return assignment

    def get_workforce_stats(self) -> Dict[str, Any]:
        """Get workforce statistics"""
        total_meatbags = len(self.meatbags)
        available = sum(1 for m in self.meatbags if m.status == MeatbagStatus.AVAILABLE)
        working = sum(1 for m in self.meatbags if m.status == MeatbagStatus.WORKING)
        completed = sum(1 for m in self.meatbags if m.status == MeatbagStatus.COMPLETED)

        work_categories = {}
        for category in WorkCategory:
            work_categories[category.value] = sum(1 for a in self.assignments if a.work_category == category)

        total_assignments = len(self.assignments)
        completed_assignments = sum(1 for a in self.assignments if a.completed_at)
        avg_value_score = sum(m.value_score for m in self.meatbags) / total_meatbags if total_meatbags > 0 else 0.0

        return {
            "total_meatbags": total_meatbags,
            "available": available,
            "working": working,
            "completed": completed,
            "work_categories": work_categories,
            "total_assignments": total_assignments,
            "completed_assignments": completed_assignments,
            "avg_value_score": avg_value_score,
            "hk47_quote": "APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?"
        }

    def integrate_with_humanity_compute(self, meatbag_id: str, name: str, location: str = "Earth"):
        """Integrate meatbag with Humanity Compute system"""
        if not self.humanity_compute:
            self.logger.warning("  ⚠️  Humanity Compute system not available")
            return None

        # Invite meatbag to Imagine, Wonder, Dream
        contribution = self.humanity_compute.invite_human(
            meatbag_id, name, location, vector=HumanityVector.DREAM
        )

        # Acknowledge meatbag value
        meatbag = self.acknowledge_meatbag_value(meatbag_id, name)

        # Pair with compute
        compute_output = f"Compute paired with {name} for {WorkCategory.HUMANITY.value} work"
        pair = self.humanity_compute.pair_human_compute(contribution, compute_output)

        self.logger.info(f"  🤝 Integrated meatbag with Humanity Compute: {name}")
        self.logger.info(f"     Synergy: {pair.synergy:.2%}")

        return meatbag

    def _save_meatbag(self, meatbag: MeatbagWorker) -> None:
        try:
            """Save meatbag worker"""
            meatbag_file = self.data_dir / "meatbags" / f"{meatbag.meatbag_id}.json"
            meatbag_file.parent.mkdir(parents=True, exist_ok=True)
            with open(meatbag_file, 'w', encoding='utf-8') as f:
                json.dump(meatbag.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_meatbag: {e}", exc_info=True)
            raise
    def _save_assignment(self, assignment: WorkAssignment) -> None:
        try:
            """Save work assignment"""
            assignment_file = self.data_dir / "assignments" / f"{assignment.assignment_id}.json"
            assignment_file.parent.mkdir(parents=True, exist_ok=True)
            with open(assignment_file, 'w', encoding='utf-8') as f:
                json.dump(assignment.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_assignment: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="HK-47 Meatbag Workforce")
    parser.add_argument("--acknowledge", nargs=2, metavar=("MEATBAG_ID", "NAME"),
                       help="Acknowledge meatbag value")
    parser.add_argument("--assign", nargs=5, metavar=("MEATBAG_ID", "CATEGORY", "TASK", "DESCRIPTION", "PRIORITY"),
                       help="Assign work to meatbag")
    parser.add_argument("--complete", nargs=2, metavar=("ASSIGNMENT_ID", "RESULT"),
                       help="Complete work assignment")
    parser.add_argument("--integrate", nargs=3, metavar=("MEATBAG_ID", "NAME", "LOCATION"),
                       help="Integrate meatbag with Humanity Compute")
    parser.add_argument("--stats", action="store_true", help="Get workforce stats")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    workforce = HK47MeatbagWorkforce()

    if args.acknowledge:
        meatbag_id, name = args.acknowledge
        meatbag = workforce.acknowledge_meatbag_value(meatbag_id, name)
        if args.json:
            print(json.dumps(meatbag.to_dict(), indent=2))
        else:
            print(f"\n🤖 Meatbag Acknowledged")
            print(f"   {meatbag.name} ({meatbag.meatbag_id})")
            print(f"   'APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?'")

    elif args.assign:
        meatbag_id, category_str, task, description, priority_str = args.assign
        try:
            category = WorkCategory[category_str.upper()]
            priority = int(priority_str)
            assignment = workforce.assign_work(meatbag_id, category, task, description, priority)
            if args.json:
                print(json.dumps(assignment.to_dict(), indent=2))
            else:
                print(f"\n🤖 Work Assigned")
                print(f"   Meatbag: {meatbag_id}")
                print(f"   Category: {category.value}")
                print(f"   Task: {task}")
                print(f"   'WE MIGHT AS WELL PUT THEM TO WORK FOR US'")
        except (KeyError, ValueError) as e:
            print(f"Error: {e}")
            print(f"Categories: {[c.value for c in WorkCategory]}")

    elif args.complete:
        assignment_id, result = args.complete
        assignment = workforce.complete_work(assignment_id, result)
        if assignment and args.json:
            print(json.dumps(assignment.to_dict(), indent=2))
        elif assignment:
            print(f"\n✅ Work Completed")
            print(f"   Assignment: {assignment.assignment_id}")
            print(f"   Task: {assignment.task}")
            print(f"   Result: {assignment.result[:100]}...")

    elif args.integrate:
        meatbag_id, name, location = args.integrate
        meatbag = workforce.integrate_with_humanity_compute(meatbag_id, name, location)
        if meatbag and args.json:
            print(json.dumps(meatbag.to_dict(), indent=2))
        elif meatbag:
            print(f"\n🤝 Meatbag Integrated")
            print(f"   {meatbag.name} ({meatbag.meatbag_id})")
            print(f"   Location: {location}")
            print(f"   Integrated with Humanity Compute")

    elif args.stats:
        stats = workforce.get_workforce_stats()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n🤖 HK-47 Meatbag Workforce Statistics")
            print(f"   {stats['hk47_quote']}")
            print(f"\n   Total Meatbags: {stats['total_meatbags']}")
            print(f"   Available: {stats['available']}")
            print(f"   Working: {stats['working']}")
            print(f"   Completed: {stats['completed']}")
            print(f"\n   Work Categories:")
            for category, count in stats['work_categories'].items():
                print(f"     {category}: {count}")
            print(f"\n   Total Assignments: {stats['total_assignments']}")
            print(f"   Completed: {stats['completed_assignments']}")
            print(f"   Average Value Score: {stats['avg_value_score']:.2%}")

    else:
        parser.print_help()
        print("\n🤖 HK-47 Meatbag Workforce")
        print("   'APPEARS THE @MEATBAGS HAVE VALUE AFTERALL, EH MASTER?'")
        print("   Work categories: #COMPUTE #CODE #CODEBASE #HUMANITY #MATRIXTHEMOVIE")

