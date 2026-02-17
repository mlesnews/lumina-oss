#!/usr/bin/env python3
"""
Tape Library Pathfinder - Qui-Gon Jinn Logic

When work is stopped/waiting (e.g., after ESCALATE decision), the Pathfinder
searches for the next breadcrumb to continue the workflow automatically.

Pathfinder logic:
1. Analyze current state (what's blocking)
2. Search for solutions/next steps
3. Find available paths forward
4. Bridge the gap automatically
5. Lead to the next breadcrumb
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TapeLibraryPathfinder")


@dataclass
class PathfindingState:
    """Current state for pathfinding"""
    workflow_id: str
    current_step: str
    blocking_reason: str
    decision_made: str
    approval_status: str
    waiting_for: List[str]
    available_actions: List[str] = field(default_factory=list)
    next_breadcrumbs: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class PathfindingResult:
    """Pathfinding result"""
    pathfinder_id: str
    timestamp: str
    paths_found: List[Dict[str, Any]]
    recommended_path: Dict[str, Any]
    actions_to_take: List[str]
    breadcrumbs: List[Dict[str, Any]]
    can_proceed: bool
    blocking_conditions: List[str] = field(default_factory=list)


class TapeLibraryPathfinder:
    """
    Tape Library Pathfinder - Qui-Gon Jinn Logic

    Finds paths forward when work is blocked or waiting.
    Searches for next breadcrumbs to continue automation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Pathfinder"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("TapeLibraryPathfinder")

        # Data directories
        self.workflows_dir = self.project_root / "data" / "tape_library_team" / "workflows"
        self.pathfinder_dir = self.project_root / "data" / "tape_library_team" / "pathfinder"
        self.pathfinder_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Tape Library Pathfinder initialized (Qui-Gon Jinn logic)")

    def find_paths_forward(self, workflow_result_file: Path) -> PathfindingResult:
        try:
            """
            Find paths forward from current workflow state

            Args:
                workflow_result_file: Path to workflow result JSON file

            Returns:
                PathfindingResult with paths forward
            """
            self.logger.info("=" * 70)
            self.logger.info("PATHFINDER: Searching for paths forward...")
            self.logger.info("=" * 70)

            # Load workflow result
            with open(workflow_result_file, 'r', encoding='utf-8') as f:
                workflow_result = json.load(f)

            # Analyze current state
            state = self._analyze_state(workflow_result)

            self.logger.info(f"Current Step: {state.current_step}")
            self.logger.info(f"Blocking Reason: {state.blocking_reason}")
            self.logger.info(f"Waiting For: {', '.join(state.waiting_for)}")
            self.logger.info("")

            # Find paths forward
            paths = self._find_paths(state, workflow_result)

            # Identify recommended path
            recommended = self._recommend_path(paths, state)

            # Generate breadcrumbs
            breadcrumbs = self._generate_breadcrumbs(recommended, state)

            # Determine if we can proceed
            can_proceed = self._can_proceed(recommended, state)

            # Create result
            result = PathfindingResult(
                pathfinder_id=f"pathfinder-{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now().isoformat(),
                paths_found=paths,
                recommended_path=recommended,
                actions_to_take=recommended.get("actions", []),
                breadcrumbs=breadcrumbs,
                can_proceed=can_proceed,
                blocking_conditions=state.waiting_for if not can_proceed else []
            )

            # Save result
            self._save_pathfinding_result(result, workflow_result_file)

            self.logger.info("=" * 70)
            self.logger.info("PATHFINDER RESULTS")
            self.logger.info("=" * 70)
            self.logger.info(f"Paths Found: {len(paths)}")
            self.logger.info(f"Recommended: {recommended.get('name', 'None')}")
            self.logger.info(f"Can Proceed: {can_proceed}")
            self.logger.info(f"Breadcrumbs: {len(breadcrumbs)}")
            self.logger.info("")

            if breadcrumbs:
                self.logger.info("NEXT BREADCRUMBS:")
                for i, crumb in enumerate(breadcrumbs, 1):
                    self.logger.info(f"  {i}. {crumb.get('action', 'Unknown')}")
                    self.logger.info(f"     {crumb.get('description', '')}")
                    self.logger.info("")

            return result

        except Exception as e:
            self.logger.error(f"Error in find_paths_forward: {e}", exc_info=True)
            raise
    def _analyze_state(self, workflow_result: Dict[str, Any]) -> PathfindingState:
        """Analyze current workflow state"""
        decision = workflow_result.get("step_6_decision_making", {})
        escalation = workflow_result.get("step_4_escalation_determination", {})

        current_step = "decision_making"
        blocking_reason = "Awaiting approval/decision"
        decision_made = decision.get("decision", "unknown")
        approval_status = decision.get("approval_status", "pending")

        waiting_for = []
        if approval_status == "pending":
            approval_authorities = escalation.get("approval_authorities", [])
            waiting_for = approval_authorities.copy()

        available_actions = []
        if decision_made == "escalate":
            available_actions = [
                "Prepare escalation package",
                "Document approval requirements",
                "Identify alternative paths",
                "Search for similar past decisions",
                "Prepare fallback options"
            ]
        elif decision_made == "archive":
            available_actions = [
                "Identify archive location",
                "Prepare archive operation",
                "Verify backup availability",
                "Create archive plan"
            ]
        elif decision_made == "delete":
            available_actions = [
                "Verify backup exists",
                "Prepare deletion operation",
                "Create recovery plan",
                "Document deletion rationale"
            ]

        return PathfindingState(
            workflow_id=workflow_result.get("workflow_id", "unknown"),
            current_step=current_step,
            blocking_reason=blocking_reason,
            decision_made=decision_made,
            approval_status=approval_status,
            waiting_for=waiting_for,
            available_actions=available_actions
        )

    def _find_paths(self, state: PathfindingState, 
                   workflow_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find available paths forward"""
        paths = []

        decision = workflow_result.get("step_6_decision_making", {})
        escalation = workflow_result.get("step_4_escalation_determination", {})
        prevention = workflow_result.get("step_5_prevention_strategies", {})

        # Path 1: Proceed with approval
        if state.approval_status == "pending":
            paths.append({
                "path_id": "path_approval",
                "name": "Proceed with Approval Process",
                "description": "Continue with escalation/approval workflow",
                "actions": [
                    "Prepare escalation package with all workflow results",
                    "Submit to approval authorities",
                    "Monitor approval status",
                    "Execute once approved"
                ],
                "prerequisites": state.waiting_for,
                "risk": "low",
                "can_proceed": False  # Blocked on approval
            })

        # Path 2: Execute prevention strategies (can do while waiting)
        immediate_prevention = prevention.get("immediate_prevention", [])
        if immediate_prevention:
            paths.append({
                "path_id": "path_prevention",
                "name": "Execute Immediate Prevention Strategies",
                "description": "Implement prevention strategies while waiting for approval",
                "actions": immediate_prevention.copy(),
                "prerequisites": [],
                "risk": "low",
                "can_proceed": True  # Can proceed without approval
            })

        # Path 3: Prepare implementation (can do while waiting)
        if state.decision_made in ["archive", "delete"]:
            paths.append({
                "path_id": "path_prepare",
                "name": "Prepare Implementation",
                "description": "Prepare implementation details while waiting for approval",
                "actions": [
                    "Create detailed implementation plan",
                    "Identify required resources",
                    "Prepare rollback procedures",
                    "Create testing plan",
                    "Document execution steps"
                ],
                "prerequisites": [],
                "risk": "low",
                "can_proceed": True  # Can proceed without approval
            })

        # Path 4: Search for similar past decisions
        paths.append({
            "path_id": "path_precedent",
            "name": "Search for Precedents",
            "description": "Search for similar past decisions/workflows",
            "actions": [
                "Search workflow history for similar cases",
                "Review past escalation patterns",
                "Identify patterns in approvals",
                "Learn from past decisions"
            ],
            "prerequisites": [],
            "risk": "none",
            "can_proceed": True  # Can proceed without approval
        })

        # Path 5: Alternative analysis (if decision is escalate)
        if state.decision_made == "escalate":
            paths.append({
                "path_id": "path_alternative",
                "name": "Analyze Alternatives",
                "description": "Deep dive into alternative options",
                "actions": [
                    "Analyze all decision alternatives in detail",
                    "Create comparison matrix",
                    "Evaluate risk/benefit of each option",
                    "Prepare alternative recommendations"
                ],
                "prerequisites": [],
                "risk": "none",
                "can_proceed": True  # Can proceed without approval
            })

        return paths

    def _recommend_path(self, paths: List[Dict[str, Any]], 
                       state: PathfindingState) -> Dict[str, Any]:
        """Recommend best path forward"""
        # Prioritize paths that can proceed (not blocked)
        can_proceed_paths = [p for p in paths if p.get("can_proceed", False)]

        if can_proceed_paths:
            # Prefer prevention strategies (immediate value)
            prevention_path = next((p for p in can_proceed_paths if p["path_id"] == "path_prevention"), None)
            if prevention_path:
                return prevention_path

            # Then preparation (readiness value)
            prepare_path = next((p for p in can_proceed_paths if p["path_id"] == "path_prepare"), None)
            if prepare_path:
                return prepare_path

            # Then precedent search (learning value)
            precedent_path = next((p for p in can_proceed_paths if p["path_id"] == "path_precedent"), None)
            if precedent_path:
                return precedent_path

            # Return first available
            return can_proceed_paths[0]
        else:
            # All paths blocked - recommend approval path
            approval_path = next((p for p in paths if p["path_id"] == "path_approval"), None)
            if approval_path:
                return approval_path

            # Fallback
            return paths[0] if paths else {}

    def _generate_breadcrumbs(self, recommended_path: Dict[str, Any],
                             state: PathfindingState) -> List[Dict[str, Any]]:
        """Generate breadcrumbs (next steps)"""
        breadcrumbs = []

        actions = recommended_path.get("actions", [])

        for i, action in enumerate(actions, 1):
            breadcrumb = {
                "breadcrumb_id": f"crumb_{i}",
                "order": i,
                "action": action,
                "description": f"Step {i}: {action}",
                "can_execute": recommended_path.get("can_proceed", False),
                "estimated_time": "varies",
                "dependencies": []
            }
            breadcrumbs.append(breadcrumb)

        return breadcrumbs

    def _can_proceed(self, recommended_path: Dict[str, Any],
                    state: PathfindingState) -> bool:
        """Determine if we can proceed with recommended path"""
        # Can proceed if path says it can proceed (regardless of waiting_for)
        # Some paths (like prevention) can be done while waiting
        return recommended_path.get("can_proceed", False)

    def _save_pathfinding_result(self, result: PathfindingResult,
                                     workflow_file: Path):
        """Save pathfinding result"""
        try:
            result_file = self.pathfinder_dir / f"{result.pathfinder_id}.json"

            result_dict = asdict(result)

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result_dict, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Pathfinding result saved to: {result_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_pathfinding_result: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Tape Library Pathfinder - Find paths forward when work is blocked"
        )
        parser.add_argument(
            "--workflow-file",
            type=str,
            required=True,
            help="Path to workflow result JSON file"
        )

        args = parser.parse_args()

        pathfinder = TapeLibraryPathfinder()

        workflow_file = Path(args.workflow_file)

        result = pathfinder.find_paths_forward(workflow_file)

        print("\n" + "=" * 70)
        print("PATHFINDER RESULTS")
        print("=" * 70)
        print(f"Paths Found: {len(result.paths_found)}")
        print(f"Recommended Path: {result.recommended_path.get('name', 'None')}")
        print(f"Can Proceed: {result.can_proceed}")
        print(f"Breadcrumbs: {len(result.breadcrumbs)}")
        print("")

        if result.breadcrumbs:
            print("NEXT BREADCRUMBS:")
            for crumb in result.breadcrumbs:
                print(f"  • {crumb.get('action', 'Unknown')}")

        print("=" * 70)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())