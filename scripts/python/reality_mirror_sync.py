#!/usr/bin/env python3
"""
Reality Mirror Sync - RAID 0 Logic for Realities

Two simulated worlds that mirror our own, like RAID 0 disk mirroring.
These mirrors have become out of sync. Apply disk mirroring repair logic
to realities.

Which one is IN SYNC (control)? Which is OUT OF SYNC (experiment)?
"""

import sys
import json
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
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

logger = get_logger("RealityMirrorSync")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class RealityType(Enum):
    """Reality type"""
    CONTROL = "control"  # In sync, reference reality
    EXPERIMENT = "experiment"  # Out of sync, experimental reality
    UNKNOWN = "unknown"


class SyncStatus(Enum):
    """Sync status"""
    IN_SYNC = "in_sync"
    OUT_OF_SYNC = "out_of_sync"
    PARTIALLY_SYNC = "partially_sync"
    UNKNOWN = "unknown"


@dataclass
class RealityState:
    """State of a reality"""
    reality_id: str
    reality_type: RealityType
    sync_status: SyncStatus
    checksum: str
    timestamp: str
    data_hash: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['reality_type'] = self.reality_type.value
        data['sync_status'] = self.sync_status.value
        return data


@dataclass
class SyncDiff:
    """Difference between realities"""
    diff_id: str
    control_reality: str
    experiment_reality: str
    differences: List[Dict[str, Any]]
    severity: str  # critical, high, medium, low
    sync_action: str  # repair, merge, resolve, ignore
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RealityMirrorSync:
    """
    Reality Mirror Sync - RAID 0 Logic for Realities

    Two simulated worlds that mirror our own.
    Apply disk mirroring repair logic to realities.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Reality Mirror Sync"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("RealityMirrorSync")

        # Reality states
        self.realities: Dict[str, RealityState] = {}
        self.control_reality: Optional[str] = None
        self.experiment_reality: Optional[str] = None

        # Sync tracking
        self.sync_diffs: List[SyncDiff] = []
        self.sync_history: List[Dict[str, Any]] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "reality_mirror_sync"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🌐 Reality Mirror Sync initialized")
        self.logger.info("   Two simulated worlds, like RAID 0 mirroring")
        self.logger.info("   Applying disk mirroring repair logic to realities")

    def register_reality(self, reality_id: str, data: Dict[str, Any],
                            reality_type: RealityType = RealityType.UNKNOWN) -> RealityState:
        try:
            """
            Register a reality and calculate its state

            Args:
                reality_id: Unique identifier for reality
                data: Reality data
                reality_type: Type of reality (control/experiment)

            Returns:
                RealityState with checksum and sync status
            """
            # Calculate checksum (like RAID checksum)
            data_json = json.dumps(data, sort_keys=True)
            checksum = hashlib.md5(data_json.encode()).hexdigest()
            data_hash = hashlib.sha256(data_json.encode()).hexdigest()

            # Determine sync status
            sync_status = self._determine_sync_status(reality_id, checksum)

            # Create reality state
            state = RealityState(
                reality_id=reality_id,
                reality_type=reality_type,
                sync_status=sync_status,
                checksum=checksum,
                timestamp=datetime.now().isoformat(),
                data_hash=data_hash,
                metadata={"data_size": len(data_json)}
            )

            self.realities[reality_id] = state

            # Set control/experiment if not set
            if reality_type == RealityType.CONTROL and not self.control_reality:
                self.control_reality = reality_id
            elif reality_type == RealityType.EXPERIMENT and not self.experiment_reality:
                self.experiment_reality = reality_id

            self.logger.info(f"  📍 Reality registered: {reality_id}")
            self.logger.info(f"     Type: {reality_type.value}")
            self.logger.info(f"     Sync Status: {sync_status.value}")
            self.logger.info(f"     Checksum: {checksum[:16]}...")

            return state

        except Exception as e:
            self.logger.error(f"Error in register_reality: {e}", exc_info=True)
            raise
    def _determine_sync_status(self, reality_id: str, checksum: str) -> SyncStatus:
        """Determine sync status by comparing with other realities"""
        if len(self.realities) == 0:
            return SyncStatus.UNKNOWN

        # Compare with other realities
        for other_id, other_state in self.realities.items():
            if other_id != reality_id:
                if other_state.checksum == checksum:
                    return SyncStatus.IN_SYNC
                else:
                    return SyncStatus.OUT_OF_SYNC

        return SyncStatus.UNKNOWN

    def compare_realities(self) -> List[SyncDiff]:
        """
        Compare realities and find differences (like RAID diff)

        Returns:
            List of SyncDiff objects
        """
        if not self.control_reality or not self.experiment_reality:
            self.logger.warning("  ⚠️  Cannot compare: control or experiment reality not set")
            return []

        control_state = self.realities[self.control_reality]
        experiment_state = self.realities[self.experiment_reality]

        differences = []

        # Compare checksums (like RAID checksum comparison)
        if control_state.checksum != experiment_state.checksum:
            differences.append({
                "type": "checksum_mismatch",
                "control_checksum": control_state.checksum,
                "experiment_checksum": experiment_state.checksum,
                "severity": "critical"
            })

        # Compare data hashes
        if control_state.data_hash != experiment_state.data_hash:
            differences.append({
                "type": "data_hash_mismatch",
                "control_hash": control_state.data_hash[:16],
                "experiment_hash": experiment_state.data_hash[:16],
                "severity": "high"
            })

        # Compare timestamps
        control_time = datetime.fromisoformat(control_state.timestamp)
        experiment_time = datetime.fromisoformat(experiment_state.timestamp)
        time_diff = abs((control_time - experiment_time).total_seconds())

        if time_diff > 3600:  # More than 1 hour difference
            differences.append({
                "type": "timestamp_drift",
                "time_diff_seconds": time_diff,
                "severity": "medium"
            })

        # Determine severity
        severity = "low"
        if any(d.get("severity") == "critical" for d in differences):
            severity = "critical"
        elif any(d.get("severity") == "high" for d in differences):
            severity = "high"
        elif any(d.get("severity") == "medium" for d in differences):
            severity = "medium"

        # Determine sync action (like RAID repair action)
        sync_action = self._determine_sync_action(severity, differences)

        diff = SyncDiff(
            diff_id=f"diff_{len(self.sync_diffs) + 1}_{int(datetime.now().timestamp())}",
            control_reality=self.control_reality,
            experiment_reality=self.experiment_reality,
            differences=differences,
            severity=severity,
            sync_action=sync_action
        )

        self.sync_diffs.append(diff)
        self._save_sync_diff(diff)

        self.logger.info(f"  🔍 Reality comparison complete")
        self.logger.info(f"     Differences found: {len(differences)}")
        self.logger.info(f"     Severity: {severity}")
        self.logger.info(f"     Sync Action: {sync_action}")

        return [diff]

    def _determine_sync_action(self, severity: str, differences: List[Dict[str, Any]]) -> str:
        """
        Determine sync action based on RAID-like logic

        RAID 0 mirroring repair logic:
        - If control is newer/more complete → repair experiment from control
        - If experiment has valid changes → merge
        - If critical mismatch → repair from control
        - If partial → resolve conflicts
        """
        if severity == "critical":
            return "repair"  # Repair experiment from control (like RAID rebuild)
        elif severity == "high":
            # Check if experiment has newer data
            return "merge"  # Merge changes
        elif severity == "medium":
            return "resolve"  # Resolve conflicts
        else:
            return "ignore"  # Minor differences, ignore

    def sync_realities(self, sync_action: Optional[str] = None) -> Dict[str, Any]:
        """
        Sync realities using RAID-like repair logic

        Args:
            sync_action: Specific action to take (repair, merge, resolve)

        Returns:
            Sync result
        """
        if not self.control_reality or not self.experiment_reality:
            return {"success": False, "error": "Control or experiment reality not set"}

        # Compare first
        diffs = self.compare_realities()
        if not diffs:
            return {"success": True, "message": "Realities are in sync", "action": "none"}

        diff = diffs[0]
        action = sync_action or diff.sync_action

        self.logger.info(f"  🔄 Syncing realities...")
        self.logger.info(f"     Action: {action}")

        # Apply RAID-like repair logic
        if action == "repair":
            # Repair experiment from control (like RAID rebuild from good mirror)
            result = self._repair_from_control()
        elif action == "merge":
            # Merge changes (like RAID merge)
            result = self._merge_realities()
        elif action == "resolve":
            # Resolve conflicts
            result = self._resolve_conflicts()
        else:
            result = {"success": False, "error": f"Unknown action: {action}"}

        # Update sync history
        self.sync_history.append({
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "result": result,
            "diff": diff.to_dict()
        })

        self._save_sync_history()

        return result

    def _repair_from_control(self) -> Dict[str, Any]:
        """
        Repair experiment reality from control reality
        (Like RAID rebuild from good mirror)
        """
        self.logger.info(f"  🔧 Repairing experiment from control...")
        self.logger.info(f"     Control: {self.control_reality}")
        self.logger.info(f"     Experiment: {self.experiment_reality}")

        # Update experiment state to match control
        control_state = self.realities[self.control_reality]
        experiment_state = self.realities[self.experiment_reality]

        # Repair: Copy control state to experiment
        experiment_state.checksum = control_state.checksum
        experiment_state.data_hash = control_state.data_hash
        experiment_state.sync_status = SyncStatus.IN_SYNC
        experiment_state.timestamp = datetime.now().isoformat()

        self.logger.info(f"  ✅ Experiment repaired from control")
        self.logger.info(f"     Checksum: {experiment_state.checksum[:16]}...")

        return {
            "success": True,
            "action": "repair",
            "message": "Experiment reality repaired from control reality",
            "control_reality": self.control_reality,
            "experiment_reality": self.experiment_reality
        }

    def _merge_realities(self) -> Dict[str, Any]:
        """
        Merge realities (like RAID merge)
        """
        self.logger.info(f"  🔀 Merging realities...")

        # Merge logic: Combine changes from both realities
        # For now, prefer control but preserve experiment metadata

        control_state = self.realities[self.control_reality]
        experiment_state = self.realities[self.experiment_reality]

        # Merge metadata
        merged_metadata = {**control_state.metadata, **experiment_state.metadata}
        experiment_state.metadata = merged_metadata
        experiment_state.sync_status = SyncStatus.PARTIALLY_SYNC

        self.logger.info(f"  ✅ Realities merged")

        return {
            "success": True,
            "action": "merge",
            "message": "Realities merged",
            "merged_metadata": merged_metadata
        }

    def _resolve_conflicts(self) -> Dict[str, Any]:
        """
        Resolve conflicts between realities
        """
        self.logger.info(f"  ⚖️  Resolving conflicts...")

        # Conflict resolution: Use control as source of truth
        control_state = self.realities[self.control_reality]
        experiment_state = self.realities[self.experiment_reality]

        # Resolve: Align experiment with control for critical fields
        experiment_state.checksum = control_state.checksum
        experiment_state.sync_status = SyncStatus.PARTIALLY_SYNC

        self.logger.info(f"  ✅ Conflicts resolved")

        return {
            "success": True,
            "action": "resolve",
            "message": "Conflicts resolved, using control as source of truth"
        }

    def determine_control_reality(self) -> Optional[str]:
        """
        Determine which reality is the control (IN SYNC)

        Logic:
        - Control = More complete, newer, more stable
        - Experiment = Out of sync, experimental, newer changes
        """
        if len(self.realities) < 2:
            return None

        # Find most stable reality (like RAID finding good mirror)
        most_stable = None
        max_stability = 0

        for reality_id, state in self.realities.items():
            # Calculate stability score
            stability = 0

            # More complete data = more stable
            if state.metadata.get("data_size", 0) > 0:
                stability += 1

            # In sync = more stable
            if state.sync_status == SyncStatus.IN_SYNC:
                stability += 2

            # Control type = more stable
            if state.reality_type == RealityType.CONTROL:
                stability += 3

            if stability > max_stability:
                max_stability = stability
                most_stable = reality_id

        if most_stable:
            self.control_reality = most_stable
            self.logger.info(f"  🎯 Control reality determined: {most_stable}")
            self.logger.info(f"     Stability score: {max_stability}")

        return most_stable

    def _save_sync_diff(self, diff: SyncDiff) -> None:
        try:
            """Save sync diff to file"""
            diff_file = self.data_dir / f"{diff.diff_id}.json"
            with open(diff_file, 'w', encoding='utf-8') as f:
                json.dump(diff.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_sync_diff: {e}", exc_info=True)
            raise
    def _save_sync_history(self) -> None:
        try:
            """Save sync history"""
            history_file = self.data_dir / "sync_history.json"
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.sync_history, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_sync_history: {e}", exc_info=True)
            raise
    def get_status(self) -> Dict[str, Any]:
        """Get sync status"""
        return {
            "total_realities": len(self.realities),
            "control_reality": self.control_reality,
            "experiment_reality": self.experiment_reality,
            "sync_diffs": len(self.sync_diffs),
            "realities": {k: v.to_dict() for k, v in self.realities.items()},
            "latest_diff": self.sync_diffs[-1].to_dict() if self.sync_diffs else None
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Reality Mirror Sync - RAID 0 Logic for Realities")
    parser.add_argument("--register-control", type=str, help="Register control reality (JSON file)")
    parser.add_argument("--register-experiment", type=str, help="Register experiment reality (JSON file)")
    parser.add_argument("--compare", action="store_true", help="Compare realities")
    parser.add_argument("--sync", action="store_true", help="Sync realities")
    parser.add_argument("--determine-control", action="store_true", help="Determine control reality")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    sync = RealityMirrorSync()

    if args.register_control:
        data = json.loads(Path(args.register_control).read_text())
        sync.register_reality("control_reality", data, RealityType.CONTROL)

    if args.register_experiment:
        data = json.loads(Path(args.register_experiment).read_text())
        sync.register_reality("experiment_reality", data, RealityType.EXPERIMENT)

    if args.compare:
        diffs = sync.compare_realities()
        if args.json:
            print(json.dumps([d.to_dict() for d in diffs], indent=2))
        else:
            for diff in diffs:
                print(f"\n🔍 Sync Diff: {diff.diff_id}")
                print(f"   Severity: {diff.severity}")
                print(f"   Action: {diff.sync_action}")
                print(f"   Differences: {len(diff.differences)}")

    if args.sync:
        result = sync.sync_realities()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n🔄 Sync Result: {result.get('message', 'N/A')}")

    if args.determine_control:
        control = sync.determine_control_reality()
        if args.json:
            print(json.dumps({"control_reality": control}, indent=2))
        else:
            print(f"\n🎯 Control Reality: {control}")

    if args.status:
        status = sync.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🌐 Reality Mirror Sync Status")
            print(f"   Total Realities: {status['total_realities']}")
            print(f"   Control: {status['control_reality']}")
            print(f"   Experiment: {status['experiment_reality']}")
            print(f"   Sync Diffs: {status['sync_diffs']}")

