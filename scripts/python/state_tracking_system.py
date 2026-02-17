#!/usr/bin/env python3
"""
State Tracking System - Past, Present, Future
<COMPANY_NAME> LLC

Tracks:
- Where we've been (history)
- Where we are (current state)
- Where we're going (future direction)

"If we're not measuring, we don't know where we've been, where we are, or where we're going."
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from measurement_gatekeeper import get_measurement_gatekeeper
    GATEKEEPER_AVAILABLE = True
except ImportError:
    GATEKEEPER_AVAILABLE = False

logger = get_logger("StateTrackingSystem")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class StateDimension(Enum):
    """State dimensions"""
    PAST = "past"  # Where we've been
    PRESENT = "present"  # Where we are
    FUTURE = "future"  # Where we're going


@dataclass
class StateSnapshot:
    """State snapshot at a point in time"""
    snapshot_id: str
    timestamp: datetime
    dimension: StateDimension

    # State data
    component: str
    state_data: Dict[str, Any]

    # Context
    context: Dict[str, Any] = field(default_factory=dict)

    # Relationships
    previous_snapshot_id: Optional[str] = None
    next_snapshot_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        data['dimension'] = self.dimension.value
        return data


@dataclass
class StateTrajectory:
    """State trajectory (past -> present -> future)"""
    component: str
    trajectory_id: str

    # Past states
    past_snapshots: List[StateSnapshot] = field(default_factory=list)

    # Present state
    present_snapshot: Optional[StateSnapshot] = None

    # Future projections
    future_projections: List[StateSnapshot] = field(default_factory=list)

    # Analysis
    trend: str = "stable"  # increasing, decreasing, stable, volatile
    velocity: float = 0.0  # Rate of change
    acceleration: float = 0.0  # Rate of change of change

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['past_snapshots'] = [s.to_dict() for s in self.past_snapshots]
        if self.present_snapshot:
            data['present_snapshot'] = self.present_snapshot.to_dict()
        data['future_projections'] = [s.to_dict() for s in self.future_projections]
        return data


class StateTrackingSystem:
    """
    State Tracking System

    Tracks past, present, and future states to know:
    - Where we've been
    - Where we are
    - Where we're going
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize State Tracking System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("StateTrackingSystem")

        # Data directories
        self.data_dir = self.project_root / "data" / "state_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # State storage
        self.state_snapshots: Dict[str, StateSnapshot] = {}
        self.state_trajectories: Dict[str, StateTrajectory] = {}

        # Current states
        self.current_states: Dict[str, Dict[str, Any]] = {}

        # Measurement integration
        self.gatekeeper = None
        if GATEKEEPER_AVAILABLE:
            try:
                self.gatekeeper = get_measurement_gatekeeper()
            except Exception:
                pass

        self.logger.info("✅ State Tracking System initialized")
        self.logger.info("   Tracking: Past, Present, Future")

    def record_state(self, component: str, state_data: Dict[str, Any],
                    dimension: StateDimension = StateDimension.PRESENT,
                    context: Optional[Dict[str, Any]] = None) -> str:
        """
        Record a state snapshot

        Returns snapshot_id
        """
        snapshot_id = f"{component}_{int(time.time() * 1000)}"

        # Get previous snapshot for this component
        previous_snapshot_id = None
        if component in self.state_trajectories:
            trajectory = self.state_trajectories[component]
            if trajectory.present_snapshot:
                previous_snapshot_id = trajectory.present_snapshot.snapshot_id

        # Create snapshot
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            timestamp=datetime.now(),
            dimension=dimension,
            component=component,
            state_data=state_data,
            context=context or {},
            previous_snapshot_id=previous_snapshot_id
        )

        # Store snapshot
        self.state_snapshots[snapshot_id] = snapshot

        # Update trajectory
        if component not in self.state_trajectories:
            self.state_trajectories[component] = StateTrajectory(
                component=component,
                trajectory_id=f"trajectory_{component}_{int(time.time())}"
            )

        trajectory = self.state_trajectories[component]

        # Move current present to past
        if trajectory.present_snapshot:
            trajectory.past_snapshots.append(trajectory.present_snapshot)
            # Keep only last 1000 past snapshots
            if len(trajectory.past_snapshots) > 1000:
                trajectory.past_snapshots = trajectory.past_snapshots[-1000:]

        # Set new present
        trajectory.present_snapshot = snapshot

        # Update current state
        self.current_states[component] = state_data

        # Analyze trajectory
        self._analyze_trajectory(component)

        # Log state
        self.logger.info(f"📊 STATE: {component} [{dimension.value}]")
        self.logger.debug(f"   Snapshot ID: {snapshot_id}")

        # Save snapshot
        self._save_snapshot(snapshot)

        return snapshot_id

    def project_future(self, component: str, 
                      projection_data: Dict[str, Any],
                      projection_time: Optional[datetime] = None) -> str:
        """
        Project future state

        Returns projection_id
        """
        if projection_time is None:
            projection_time = datetime.now() + timedelta(hours=1)

        projection_id = f"{component}_future_{int(time.time() * 1000)}"

        # Create future projection
        projection = StateSnapshot(
            snapshot_id=projection_id,
            timestamp=projection_time,
            dimension=StateDimension.FUTURE,
            component=component,
            state_data=projection_data,
            context={'projection': True}
        )

        # Add to trajectory
        if component in self.state_trajectories:
            trajectory = self.state_trajectories[component]
            trajectory.future_projections.append(projection)
            # Keep only last 100 future projections
            if len(trajectory.future_projections) > 100:
                trajectory.future_projections = trajectory.future_projections[-100:]

        self.logger.info(f"🔮 FUTURE: {component} projected to {projection_time.isoformat()}")

        return projection_id

    def get_where_we_been(self, component: str, limit: int = 100) -> List[StateSnapshot]:
        """Get where we've been (past states)"""
        if component not in self.state_trajectories:
            return []

        trajectory = self.state_trajectories[component]
        return trajectory.past_snapshots[-limit:]

    def get_where_we_are(self, component: str) -> Optional[Dict[str, Any]]:
        """Get where we are (current state)"""
        if component not in self.state_trajectories:
            return None

        trajectory = self.state_trajectories[component]
        if trajectory.present_snapshot:
            return trajectory.present_snapshot.state_data

        return self.current_states.get(component)

    def get_where_we_going(self, component: str) -> List[StateSnapshot]:
        """Get where we're going (future projections)"""
        if component not in self.state_trajectories:
            return []

        trajectory = self.state_trajectories[component]
        return trajectory.future_projections

    def get_trajectory(self, component: str) -> Optional[StateTrajectory]:
        """Get complete trajectory (past, present, future)"""
        return self.state_trajectories.get(component)

    def _analyze_trajectory(self, component: str) -> None:
        """Analyze trajectory to determine trend, velocity, acceleration"""
        if component not in self.state_trajectories:
            return

        trajectory = self.state_trajectories[component]

        # Need at least 2 past snapshots for analysis
        if len(trajectory.past_snapshots) < 2:
            trajectory.trend = "stable"
            trajectory.velocity = 0.0
            trajectory.acceleration = 0.0
            return

        # Analyze numeric values in state data
        # This is a simplified analysis - can be extended
        try:
            # Get numeric values from recent snapshots
            recent_snapshots = trajectory.past_snapshots[-10:]  # Last 10
            if trajectory.present_snapshot:
                recent_snapshots.append(trajectory.present_snapshot)

            # Calculate velocity (rate of change)
            if len(recent_snapshots) >= 2:
                # Simple velocity calculation based on timestamp
                time_delta = (recent_snapshots[-1].timestamp - recent_snapshots[0].timestamp).total_seconds()
                if time_delta > 0:
                    trajectory.velocity = len(recent_snapshots) / time_delta
                else:
                    trajectory.velocity = 0.0

            # Determine trend
            if trajectory.velocity > 0.1:
                trajectory.trend = "increasing"
            elif trajectory.velocity < -0.1:
                trajectory.trend = "decreasing"
            else:
                trajectory.trend = "stable"
        except Exception as e:
            self.logger.debug(f"Trajectory analysis error: {e}")
            trajectory.trend = "stable"

    def _save_snapshot(self, snapshot: StateSnapshot) -> None:
        """Save snapshot to disk"""
        try:
            date_str = datetime.now().strftime('%Y%m%d')
            snapshot_file = self.data_dir / f"snapshots_{date_str}.jsonl"

            with open(snapshot_file, 'a', encoding='utf-8') as f:
                json.dump(snapshot.to_dict(), f, ensure_ascii=False, default=str)
                f.write('\n')
        except Exception as e:
            self.logger.error(f"Failed to save snapshot: {e}")

    def get_comprehensive_state(self, component: str) -> Dict[str, Any]:
        """Get comprehensive state (past, present, future)"""
        trajectory = self.get_trajectory(component)

        if not trajectory:
            return {
                'component': component,
                'past': [],
                'present': None,
                'future': [],
                'trend': 'unknown',
                'velocity': 0.0
            }

        return {
            'component': component,
            'past': [s.to_dict() for s in trajectory.past_snapshots[-10:]],
            'present': trajectory.present_snapshot.to_dict() if trajectory.present_snapshot else None,
            'future': [s.to_dict() for s in trajectory.future_projections],
            'trend': trajectory.trend,
            'velocity': trajectory.velocity,
            'acceleration': trajectory.acceleration
        }


# Singleton instance
_state_tracker_instance: Optional[StateTrackingSystem] = None


def get_state_tracker() -> StateTrackingSystem:
    """Get singleton state tracker instance"""
    global _state_tracker_instance
    if _state_tracker_instance is None:
        _state_tracker_instance = StateTrackingSystem()
    return _state_tracker_instance


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="State Tracking System")
    parser.add_argument("--record", type=str, nargs=2, metavar=("COMPONENT", "STATE_JSON"),
                       help="Record state for component")
    parser.add_argument("--past", type=str, help="Get past states for component")
    parser.add_argument("--present", type=str, help="Get present state for component")
    parser.add_argument("--future", type=str, help="Get future projections for component")
    parser.add_argument("--trajectory", type=str, help="Get complete trajectory for component")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    tracker = get_state_tracker()

    if args.record:
        component, state_json = args.record
        state_data = json.loads(state_json)
        snapshot_id = tracker.record_state(component, state_data)
        print(f"✅ Recorded state: {snapshot_id}")

    elif args.past:
        past = tracker.get_where_we_been(args.past)
        if args.json:
            print(json.dumps([s.to_dict() for s in past], indent=2))
        else:
            print(f"\n📊 Past States: {args.past}")
            print(f"   Records: {len(past)}")
            for snapshot in past[-5:]:
                print(f"   {snapshot.timestamp}: {snapshot.state_data}")

    elif args.present:
        present = tracker.get_where_we_are(args.present)
        if args.json:
            print(json.dumps(present, indent=2))
        else:
            print(f"\n📊 Present State: {args.present}")
            print(json.dumps(present, indent=2))

    elif args.future:
        future = tracker.get_where_we_going(args.future)
        if args.json:
            print(json.dumps([s.to_dict() for s in future], indent=2))
        else:
            print(f"\n🔮 Future Projections: {args.future}")
            print(f"   Projections: {len(future)}")
            for projection in future:
                print(f"   {projection.timestamp}: {projection.state_data}")

    elif args.trajectory:
        trajectory = tracker.get_trajectory(args.trajectory)
        if args.json:
            print(json.dumps(trajectory.to_dict() if trajectory else {}, indent=2))
        else:
            if trajectory:
                print(f"\n📊 Trajectory: {args.trajectory}")
                print(f"   Past: {len(trajectory.past_snapshots)}")
                print(f"   Present: {'Yes' if trajectory.present_snapshot else 'No'}")
                print(f"   Future: {len(trajectory.future_projections)}")
                print(f"   Trend: {trajectory.trend}")
                print(f"   Velocity: {trajectory.velocity:.2f}")
            else:
                print(f"No trajectory found for {args.trajectory}")

    else:
        parser.print_help()
        print("\n📊 State Tracking System")
        print("   Tracking: Past, Present, Future")

