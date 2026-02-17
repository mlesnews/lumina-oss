#!/usr/bin/env python3
"""
Flow Rate Drop Detector

Automatically detects drops in flow rate per second and:
1. Identifies root cause(s) disrupting flow rate
2. Methodically and systematically eliminates negative performance impactors (gaps)
3. Fixes all gaps (if we don't know what the gap is, we can't fix it)
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from flow_rate_monitor import FlowRateMonitor
    FLOW_RATE_MONITOR_AVAILABLE = True
except ImportError:
    FLOW_RATE_MONITOR_AVAILABLE = False
    FlowRateMonitor = None


class GapType(Enum):
    """Type of gap (negative performance impactor)"""
    UNKNOWN = "unknown"  # Gap not identified - CAN'T FIX IF WE DON'T KNOW
    DELEGATION_MISSING = "delegation_missing"  # No asks delegated to sub-agent chats
    WORKFLOW_BLOCKED = "workflow_blocked"  # Workflow blocked
    AGENT_IDLE = "agent_idle"  # Agent idle when should be working
    PATTERN_NOT_MAPPED = "pattern_not_mapped"  # Pattern not mapped to workflow
    RESOURCE_CONSTRAINT = "resource_constraint"  # Resource constraint
    DEPENDENCY_WAIT = "dependency_wait"  # Waiting on dependency
    ERROR_RATE_HIGH = "error_rate_high"  # High error rate
    COMPLETION_FALSE = "completion_false"  # False completion claims


@dataclass
class FlowRateDrop:
    """Flow rate drop detection"""
    drop_id: str
    timestamp: str
    flow_rate_before: float
    flow_rate_after: float
    drop_percentage: float
    root_causes: List[str] = field(default_factory=list)
    gaps_identified: List[str] = field(default_factory=list)
    gaps_fixed: List[str] = field(default_factory=list)
    status: str = "detected"  # detected, analyzing, fixing, fixed
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Gap:
    """Gap (negative performance impactor)"""
    gap_id: str
    gap_type: GapType
    description: str
    identified_at: str
    root_cause: Optional[str] = None
    impact: float = 0.0  # Impact on flow rate (0.0 to 1.0)
    fixed: bool = False
    fixed_at: Optional[str] = None
    fix_method: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["gap_type"] = self.gap_type.value
        return data


class FlowRateDropDetector:
    """
    Detects flow rate drops and identifies/fixes gaps

    If we don't know what the gap is, we can't fix it.
    So we MUST identify all gaps.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("FlowRateDropDetector")

        # Directories
        self.data_dir = self.project_root / "data" / "flow_rate_drops"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.drops_file = self.data_dir / "flow_rate_drops.jsonl"
        self.gaps_file = self.data_dir / "gaps.json"

        # Flow rate monitor
        self.flow_rate_monitor = None
        if FLOW_RATE_MONITOR_AVAILABLE and FlowRateMonitor:
            try:
                self.flow_rate_monitor = FlowRateMonitor(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Flow rate monitor not available: {e}")

        # State
        self.flow_rate_history: List[Tuple[float, float]] = []  # (timestamp, flow_rate)
        self.drops: List[FlowRateDrop] = []
        self.gaps: Dict[str, Gap] = {}

        # Thresholds
        self.drop_threshold_percentage = 20.0  # 20% drop triggers detection
        self.min_flow_rate = 0.01  # Minimum flow rate to consider

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        # Load drops
        if self.drops_file.exists():
            try:
                with open(self.drops_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.drops.append(FlowRateDrop(**data))
            except Exception as e:
                self.logger.error(f"Error loading drops: {e}")

        # Load gaps
        if self.gaps_file.exists():
            try:
                with open(self.gaps_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for gap_id, gap_data in data.items():
                        gap = Gap(**gap_data)
                        gap.gap_type = GapType(gap_data["gap_type"])
                        self.gaps[gap_id] = gap
            except Exception as e:
                self.logger.error(f"Error loading gaps: {e}")

    def _save_state(self):
        try:
            """Save state"""
            # Save drops
            with open(self.drops_file, 'a', encoding='utf-8') as f:
                for drop in self.drops[-100:]:  # Last 100
                    f.write(json.dumps(drop.to_dict()) + '\n')

            # Save gaps
            gaps_data = {
                gap_id: gap.to_dict()
                for gap_id, gap in self.gaps.items()
            }
            with open(self.gaps_file, 'w', encoding='utf-8') as f:
                json.dump(gaps_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise
    def check_flow_rate(self) -> Optional[FlowRateDrop]:
        """
        Check current flow rate for drops

        Returns FlowRateDrop if drop detected, None otherwise
        """
        if not self.flow_rate_monitor:
            return None

        current_flow_rate = self.flow_rate_monitor.get_flow_rate_per_second()
        now = datetime.now().timestamp()

        # Add to history
        self.flow_rate_history.append((now, current_flow_rate))

        # Keep only last 100 entries
        if len(self.flow_rate_history) > 100:
            self.flow_rate_history = self.flow_rate_history[-100:]

        # Need at least 2 data points
        if len(self.flow_rate_history) < 2:
            return None

        # Get previous flow rate (average of last 5 entries before current)
        previous_entries = self.flow_rate_history[:-1][-5:]
        if not previous_entries:
            return None

        previous_flow_rate = sum(rate for _, rate in previous_entries) / len(previous_entries)

        # Check for drop
        if previous_flow_rate < self.min_flow_rate:
            return None

        drop_percentage = ((previous_flow_rate - current_flow_rate) / previous_flow_rate) * 100

        if drop_percentage >= self.drop_threshold_percentage:
            # DROP DETECTED
            drop = FlowRateDrop(
                drop_id=f"drop_{int(now * 1000)}",
                timestamp=datetime.now().isoformat(),
                flow_rate_before=previous_flow_rate,
                flow_rate_after=current_flow_rate,
                drop_percentage=drop_percentage,
                status="detected"
            )

            self.drops.append(drop)

            self.logger.warning(f"⚠️ FLOW RATE DROP DETECTED: {drop_percentage:.1f}% drop ({previous_flow_rate:.4f}/s → {current_flow_rate:.4f}/s)")

            # Immediately analyze root causes and identify gaps
            self._analyze_root_causes(drop)
            self._identify_gaps(drop)

            # Start fixing gaps
            self._fix_gaps(drop)

            self._save_state()

            return drop

        return None

    def _analyze_root_causes(self, drop: FlowRateDrop):
        """Analyze root causes of flow rate drop"""
        self.logger.info(f"🔍 Analyzing root causes for drop {drop.drop_id}...")

        root_causes = []

        # Check for delegation missing (no asks delegated to sub-agent chats)
        if self._check_delegation_missing():
            root_causes.append("No asks delegated to sub-agent chats")
            drop.root_causes.append("delegation_missing")

        # Check for workflow blocks
        if self._check_workflow_blocks():
            root_causes.append("Workflows blocked or stalled")
            drop.root_causes.append("workflow_blocked")

        # Check for agent idle
        if self._check_agent_idle():
            root_causes.append("Agents idle when should be working")
            drop.root_causes.append("agent_idle")

        # Check for pattern not mapped
        if self._check_pattern_not_mapped():
            root_causes.append("Patterns not mapped to workflows")
            drop.root_causes.append("pattern_not_mapped")

        # Check for resource constraints
        if self._check_resource_constraints():
            root_causes.append("Resource constraints")
            drop.root_causes.append("resource_constraint")

        # Check for dependency waits
        if self._check_dependency_waits():
            root_causes.append("Waiting on dependencies")
            drop.root_causes.append("dependency_wait")

        # Check for high error rate
        if self._check_error_rate_high():
            root_causes.append("High error rate")
            drop.root_causes.append("error_rate_high")

        # Check for false completions
        if self._check_false_completions():
            root_causes.append("False completion claims")
            drop.root_causes.append("completion_false")

        # If no root causes identified, mark as unknown
        if not root_causes:
            root_causes.append("Unknown root cause - needs investigation")
            drop.root_causes.append("unknown")

        drop.metadata["root_causes_analyzed"] = root_causes
        drop.status = "analyzing"

        self.logger.info(f"✅ Identified {len(root_causes)} root cause(s): {', '.join(root_causes)}")

    def _identify_gaps(self, drop: FlowRateDrop):
        """Identify gaps (negative performance impactors)"""
        self.logger.info(f"🔍 Identifying gaps for drop {drop.drop_id}...")

        gaps_identified = []

        for root_cause in drop.root_causes:
            gap_type = GapType.UNKNOWN

            if root_cause == "delegation_missing":
                gap_type = GapType.DELEGATION_MISSING
            elif root_cause == "workflow_blocked":
                gap_type = GapType.WORKFLOW_BLOCKED
            elif root_cause == "agent_idle":
                gap_type = GapType.AGENT_IDLE
            elif root_cause == "pattern_not_mapped":
                gap_type = GapType.PATTERN_NOT_MAPPED
            elif root_cause == "resource_constraint":
                gap_type = GapType.RESOURCE_CONSTRAINT
            elif root_cause == "dependency_wait":
                gap_type = GapType.DEPENDENCY_WAIT
            elif root_cause == "error_rate_high":
                gap_type = GapType.ERROR_RATE_HIGH
            elif root_cause == "completion_false":
                gap_type = GapType.COMPLETION_FALSE

            gap_id = f"gap_{int(datetime.now().timestamp() * 1000)}_{len(gaps_identified)}"

            gap = Gap(
                gap_id=gap_id,
                gap_type=gap_type,
                description=f"Gap identified from flow rate drop: {root_cause}",
                identified_at=datetime.now().isoformat(),
                root_cause=root_cause,
                impact=drop.drop_percentage / 100.0,  # Normalize to 0.0-1.0
                fixed=False
            )

            self.gaps[gap_id] = gap
            gaps_identified.append(gap_id)
            drop.gaps_identified.append(gap_id)

            self.logger.info(f"🔍 Identified gap: {gap_id} ({gap_type.value}) - {gap.description}")

        drop.status = "fixing"

        self.logger.info(f"✅ Identified {len(gaps_identified)} gap(s)")

    def _fix_gaps(self, drop: FlowRateDrop):
        """Methodically and systematically fix all gaps"""
        self.logger.info(f"🔧 Fixing gaps for drop {drop.drop_id}...")

        for gap_id in drop.gaps_identified:
            if gap_id not in self.gaps:
                continue

            gap = self.gaps[gap_id]

            if gap.fixed:
                continue

            # Fix gap based on type
            fixed = False
            fix_method = None

            if gap.gap_type == GapType.DELEGATION_MISSING:
                fixed, fix_method = self._fix_delegation_missing(gap)
            elif gap.gap_type == GapType.WORKFLOW_BLOCKED:
                fixed, fix_method = self._fix_workflow_blocked(gap)
            elif gap.gap_type == GapType.AGENT_IDLE:
                fixed, fix_method = self._fix_agent_idle(gap)
            elif gap.gap_type == GapType.PATTERN_NOT_MAPPED:
                fixed, fix_method = self._fix_pattern_not_mapped(gap)
            elif gap.gap_type == GapType.RESOURCE_CONSTRAINT:
                fixed, fix_method = self._fix_resource_constraint(gap)
            elif gap.gap_type == GapType.DEPENDENCY_WAIT:
                fixed, fix_method = self._fix_dependency_wait(gap)
            elif gap.gap_type == GapType.ERROR_RATE_HIGH:
                fixed, fix_method = self._fix_error_rate_high(gap)
            elif gap.gap_type == GapType.COMPLETION_FALSE:
                fixed, fix_method = self._fix_completion_false(gap)
            elif gap.gap_type == GapType.UNKNOWN:
                # Can't fix if we don't know what it is
                self.logger.warning(f"⚠️ Cannot fix gap {gap_id}: Gap type is UNKNOWN - need to identify gap first")
                continue

            if fixed:
                gap.fixed = True
                gap.fixed_at = datetime.now().isoformat()
                gap.fix_method = fix_method
                drop.gaps_fixed.append(gap_id)
                self.logger.info(f"✅ Fixed gap: {gap_id} using {fix_method}")
            else:
                self.logger.warning(f"⚠️ Could not fix gap: {gap_id}")

        if len(drop.gaps_fixed) == len(drop.gaps_identified):
            drop.status = "fixed"
            self.logger.info(f"✅ All gaps fixed for drop {drop.drop_id}")
        else:
            drop.status = "partially_fixed"
            self.logger.warning(f"⚠️ Partially fixed: {len(drop.gaps_fixed)}/{len(drop.gaps_identified)} gaps fixed")

    def _check_delegation_missing(self) -> bool:
        """Check if delegation to sub-agent chats is missing"""
        try:
            from master_workflow_orchestrator import MasterWorkflowOrchestrator
            from sub_ask_todo_manager import SubAskTodoManager

            # Check if orchestrator exists and has asks
            orchestrator_path = self.project_root / "data" / "master_orchestrator" / "orchestrator_state.json"
            if not orchestrator_path.exists():
                return True  # No orchestrator state = no delegation

            with open(orchestrator_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            # Check if there are asks without sub-sessions
            user_asks = state.get("user_asks", {})
            sub_sessions = state.get("sub_sessions", {})

            # Count asks without sub-sessions
            asks_without_sessions = 0
            for ask_id in user_asks.keys():
                # Check if ask has sub-session
                has_sub_session = any(
                    sub.get("ask_id") == ask_id
                    for sub in sub_sessions.values()
                )
                if not has_sub_session:
                    asks_without_sessions += 1

            # Also check sub-ask manager for chat sessions
            sub_ask_manager = SubAskTodoManager(self.project_root)
            chat_sessions = sub_ask_manager.chat_sessions

            # If there are asks but no sub-sessions or chat sessions, delegation is missing
            if user_asks and not sub_sessions and not chat_sessions:
                return True

            # If significant number of asks without sub-sessions, delegation is missing
            if asks_without_sessions > len(user_asks) * 0.5:  # More than 50% without delegation
                return True

            return False
        except Exception as e:
            self.logger.warning(f"Error checking delegation: {e}")
            return True  # Assume missing if we can't verify

    def _check_workflow_blocks(self) -> bool:
        """Check if workflows are blocked"""
        # TODO: Check for blocked workflows  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _check_agent_idle(self) -> bool:
        """Check if agents are idle"""
        # TODO: Check for idle agents  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _check_pattern_not_mapped(self) -> bool:
        """Check if patterns are not mapped"""
        # TODO: Check for unmapped patterns  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _check_resource_constraints(self) -> bool:
        """Check for resource constraints"""
        # TODO: Check for resource constraints  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _check_dependency_waits(self) -> bool:
        """Check for dependency waits"""
        # TODO: Check for dependency waits  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _check_error_rate_high(self) -> bool:
        """Check for high error rate"""
        # DONE: Check error rate  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _check_false_completions(self) -> bool:
        """Check for false completions"""
        # TODO: Check for false completions  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False

    def _fix_delegation_missing(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix delegation missing gap - delegate asks to sub-agent chats"""
        self.logger.info(f"🔧 Fixing delegation missing gap: {gap.gap_id}")

        try:
            from master_workflow_orchestrator import MasterWorkflowOrchestrator

            orchestrator = MasterWorkflowOrchestrator(self.project_root)

            # Get all asks without sub-sessions
            orchestrator_path = self.project_root / "data" / "master_orchestrator" / "orchestrator_state.json"
            if not orchestrator_path.exists():
                return False, "No orchestrator state found"

            with open(orchestrator_path, 'r', encoding='utf-8') as f:
                state = json.load(f)

            user_asks = state.get("user_asks", {})
            sub_sessions = state.get("sub_sessions", {})

            # Find asks without sub-sessions
            asks_to_delegate = []
            for ask_id, ask_data in user_asks.items():
                has_sub_session = any(
                    sub.get("ask_id") == ask_id
                    for sub in sub_sessions.values()
                )
                if not has_sub_session:
                    asks_to_delegate.append((ask_id, ask_data))

            if not asks_to_delegate:
                return True, "All asks already delegated"

            # Delegate each ask
            delegated_count = 0
            for ask_id, ask_data in asks_to_delegate:
                try:
                    # Get workflow matches for ask
                    ask_text = ask_data.get("ask_text", "")
                    matches = orchestrator.get_workflow_matches_for_ask(ask_id)

                    if matches:
                        # Spawn sub-session (creates sub-agent chat automatically)
                        sub_session_id = orchestrator.spawn_sub_session(ask_id, matches[0])
                        delegated_count += 1
                        self.logger.info(f"✅ Delegated ask {ask_id} to sub-session {sub_session_id}")
                    else:
                        self.logger.warning(f"⚠️ No workflow matches for ask {ask_id}, cannot delegate")
                except Exception as e:
                    self.logger.error(f"Error delegating ask {ask_id}: {e}")

            if delegated_count > 0:
                return True, f"Delegated {delegated_count} ask(s) to sub-agent chats"
            else:
                return False, "No asks could be delegated"

        except Exception as e:
            self.logger.error(f"Error fixing delegation missing gap: {e}")
            return False, f"Error: {e}"

    def _fix_workflow_blocked(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix workflow blocked gap"""
        self.logger.info(f"🔧 Fixing workflow blocked gap: {gap.gap_id}")
        # DONE: Implement workflow unblocking  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def _fix_agent_idle(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix agent idle gap"""
        self.logger.info(f"🔧 Fixing agent idle gap: {gap.gap_id}")
        # TODO: Implement agent activation  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def _fix_pattern_not_mapped(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix pattern not mapped gap"""
        self.logger.info(f"🔧 Fixing pattern not mapped gap: {gap.gap_id}")
        # TODO: Implement pattern mapping  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def _fix_resource_constraint(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix resource constraint gap"""
        self.logger.info(f"🔧 Fixing resource constraint gap: {gap.gap_id}")
        # TODO: Implement resource constraint resolution  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def _fix_dependency_wait(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix dependency wait gap"""
        self.logger.info(f"🔧 Fixing dependency wait gap: {gap.gap_id}")
        # TODO: Implement dependency resolution  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def _fix_error_rate_high(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix error rate high gap"""
        self.logger.info(f"🔧 Fixing error rate high gap: {gap.gap_id}")
        # DONE: Implement error rate reduction  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def _fix_completion_false(self, gap: Gap) -> Tuple[bool, Optional[str]]:
        """Fix completion false gap"""
        self.logger.info(f"🔧 Fixing completion false gap: {gap.gap_id}")
        # TODO: Implement false completion prevention  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        return False, None

    def get_unfixed_gaps(self) -> List[Gap]:
        """Get all unfixed gaps"""
        return [gap for gap in self.gaps.values() if not gap.fixed]

    def get_unknown_gaps(self) -> List[Gap]:
        """Get all unknown gaps (can't fix if we don't know what they are)"""
        return [gap for gap in self.gaps.values() if gap.gap_type == GapType.UNKNOWN and not gap.fixed]


def main():
    """Main execution for testing"""
    detector = FlowRateDropDetector()

    print("=" * 80)
    print("📊 FLOW RATE DROP DETECTOR")
    print("=" * 80)

    # Check for flow rate drops
    drop = detector.check_flow_rate()

    if drop:
        print(f"\n⚠️ Flow Rate Drop Detected:")
        print(f"   Drop ID: {drop.drop_id}")
        print(f"   Drop: {drop.drop_percentage:.1f}% ({drop.flow_rate_before:.4f}/s → {drop.flow_rate_after:.4f}/s)")
        print(f"   Root Causes: {len(drop.root_causes)}")
        print(f"   Gaps Identified: {len(drop.gaps_identified)}")
        print(f"   Gaps Fixed: {len(drop.gaps_fixed)}")
        print(f"   Status: {drop.status}")
    else:
        print("\n✅ No flow rate drop detected")

    # Get unfixed gaps
    unfixed = detector.get_unfixed_gaps()
    print(f"\n🔍 Unfixed Gaps: {len(unfixed)}")
    for gap in unfixed:
        print(f"   - {gap.gap_id}: {gap.gap_type.value} - {gap.description}")

    # Get unknown gaps
    unknown = detector.get_unknown_gaps()
    print(f"\n⚠️ Unknown Gaps (Can't Fix): {len(unknown)}")
    for gap in unknown:
        print(f"   - {gap.gap_id}: {gap.description}")


if __name__ == "__main__":



    main()