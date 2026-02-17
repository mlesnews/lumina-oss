#!/usr/bin/env python3
"""
Tape Library Team Decision Engine

Handles all data lifecycle management decisions so JARVIS doesn't have to worry.
Implements the Tape Library Team philosophy: Data deletion is extremely dangerous.

Core Principles:
- Larger data = higher temperature = greater weight = longer recreation time
- Always prefer archive over delete when possible
- Calculate recovery time: recreation from scratch vs restore from backup
- Multiple backup locations for critical data
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
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

logger = get_logger("TapeLibraryTeamDecisionEngine")


@dataclass
class DataAssessment:
    """Assessment of data for lifecycle decision"""
    data_path: str
    data_size_bytes: int
    data_age_days: int
    data_type: str
    criticality: str  # critical, important, routine, low_priority
    backup_available: bool
    backup_locations: List[str]
    recreation_time_hours: Optional[float] = None
    restore_time_hours: Optional[float] = None
    unique_data: bool = True
    retention_required: bool = True
    archive_options: List[str] = field(default_factory=list)


@dataclass
class LifecycleDecision:
    """Decision from Tape Library Team"""
    decision_id: str
    timestamp: str
    data_path: str
    decision: str  # archive, delete, keep, escalate
    reasoning: str
    risk_assessment: Dict[str, Any]
    recommended_action: Dict[str, Any]
    approval_required: bool
    recovery_plan: Optional[Dict[str, Any]] = None


class TapeLibraryTeamDecisionEngine:
    """
    Tape Library Team Decision Engine

    Handles all data lifecycle management decisions.
    Core philosophy: Data deletion is extremely dangerous.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Tape Library Team Decision Engine"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("TapeLibraryTeamDecisionEngine")

        # Load team configuration
        team_config = self.project_root / "config" / "helpdesk" / "tape_library_team.json"
        if team_config.exists():
            with open(team_config, 'r', encoding='utf-8') as f:
                self.team_config = json.load(f)
        else:
            self.team_config = {}

        # Decision history
        self.decisions: List[LifecycleDecision] = []

        # Data directory
        self.data_dir = self.project_root / "data" / "tape_library_team"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ Tape Library Team Decision Engine initialized")
        self.logger.info("   Philosophy: Data deletion is extremely dangerous")
        self.logger.info("   Specialization: Archive, backup, restore, retention")

    def assess_data(self, data_path: Path,
                        data_size_bytes: Optional[int] = None,
                        backup_locations: Optional[List[str]] = None) -> DataAssessment:
        try:
            """
            Assess data for lifecycle decision

            Args:
                data_path: Path to data to assess
                data_size_bytes: Size of data in bytes (if known)
                backup_locations: List of backup locations (if known)

            Returns:
                DataAssessment
            """
            self.logger.info(f"Assessing data: {data_path}")

            # Get file/directory stats
            if data_path.exists():
                if data_path.is_file():
                    stat = data_path.stat()
                    data_size_bytes = stat.st_size
                    data_age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
                else:
                    # Directory - estimate size (this is expensive, might want to cache)
                    data_size_bytes = data_size_bytes or self._estimate_dir_size(data_path)
                    # Use modification time of directory
                    stat = data_path.stat()
                    data_age_days = (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).days
            else:
                data_size_bytes = data_size_bytes or 0
                data_age_days = 0

            # Determine data type
            data_type = self._determine_data_type(data_path)

            # Assess criticality
            criticality = self._assess_criticality(data_path, data_size_bytes, data_type)

            # Check for backups
            backup_available = backup_locations is not None and len(backup_locations) > 0
            if not backup_locations:
                backup_locations = self._find_backup_locations(data_path)
                backup_available = len(backup_locations) > 0

            # Calculate recreation vs restore time
            recreation_time = self._estimate_recreation_time(data_path, data_size_bytes, data_type)
            restore_time = self._estimate_restore_time(data_size_bytes, backup_available)

            # Determine if unique data
            unique_data = self._is_unique_data(data_path)

            # Retention requirements
            retention_required = self._assess_retention_requirement(data_path, data_type, criticality)

            # Archive options
            archive_options = self._identify_archive_options(data_size_bytes, criticality)

            assessment = DataAssessment(
                data_path=str(data_path),
                data_size_bytes=data_size_bytes,
                data_age_days=data_age_days,
                data_type=data_type,
                criticality=criticality,
                backup_available=backup_available,
                backup_locations=backup_locations,
                recreation_time_hours=recreation_time,
                restore_time_hours=restore_time,
                unique_data=unique_data,
                retention_required=retention_required,
                archive_options=archive_options
            )

            self.logger.info(f"  Criticality: {criticality}")
            self.logger.info(f"  Size: {data_size_bytes / (1024**3):.2f} GB")
            self.logger.info(f"  Backup available: {backup_available}")
            self.logger.info(f"  Recreation time: {recreation_time:.2f} hours")
            self.logger.info(f"  Restore time: {restore_time:.2f} hours")

            return assessment

        except Exception as e:
            self.logger.error(f"Error in assess_data: {e}", exc_info=True)
            raise
    def make_deletion_decision(self, assessment: DataAssessment, 
                              reason: Optional[str] = None) -> LifecycleDecision:
        """
        Make decision on data deletion

        Core principle: Data deletion is extremely dangerous.
        Always prefer archive over delete when possible.

        Args:
            assessment: DataAssessment
            reason: Reason for deletion request

        Returns:
            LifecycleDecision
        """
        self.logger.info("=" * 70)
        self.logger.info("TAPE LIBRARY TEAM DELETION DECISION")
        self.logger.info("=" * 70)
        self.logger.info(f"Data: {assessment.data_path}")
        self.logger.info(f"Size: {assessment.data_size_bytes / (1024**3):.2f} GB")
        self.logger.info(f"Reason: {reason or 'Not provided'}")
        self.logger.info("")

        decision_id = f"deletion-decision-{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Risk assessment
        risk_assessment = {
            "data_loss_risk": "high" if assessment.unique_data else "medium",
            "recreation_cost": "high" if assessment.recreation_time_hours and assessment.recreation_time_hours > 24 else "medium",
            "irreversibility": "high",
            "backup_coverage": "good" if assessment.backup_available else "poor",
            "size_factor": "high" if assessment.data_size_bytes > 100 * 1024**3 else "medium"  # > 100 GB
        }

        # Decision logic (Tape Library Team philosophy)
        decision = "escalate"
        reasoning = ""
        recommended_action = {}
        approval_required = True

        # Core principle: Larger data = higher risk
        size_gb = assessment.data_size_bytes / (1024**3)

        if size_gb > 1000:  # > 1 TB
            decision = "escalate"
            reasoning = f"Data size ({size_gb:.2f} GB) exceeds 1 TB threshold. Requires JARVIS approval."
            recommended_action = {
                "action": "escalate_to_jarvis",
                "steps": [
                    "1. Escalate to JARVIS for approval",
                    "2. Provide full assessment and risk analysis",
                    "3. Await decision before proceeding"
                ]
            }
        elif not assessment.backup_available and assessment.unique_data:
            decision = "escalate"
            reasoning = "No backup available and data appears unique. Deletion would result in permanent data loss."
            recommended_action = {
                "action": "create_backup_then_reassess",
                "steps": [
                    "1. Create backup before considering deletion",
                    "2. Reassess after backup creation",
                    "3. Consider archive instead of deletion"
                ]
            }
        elif assessment.recreation_time_hours and assessment.restore_time_hours:
            if assessment.recreation_time_hours > assessment.restore_time_hours * 10:
                decision = "archive"
                reasoning = f"Recreation time ({assessment.recreation_time_hours:.2f} hours) is much longer than restore time ({assessment.restore_time_hours:.2f} hours). Archive instead of delete."
                recommended_action = {
                    "action": "archive",
                    "archive_location": assessment.archive_options[0] if assessment.archive_options else "nas",
                    "steps": [
                        "1. Archive data to primary location",
                        "2. Create backup to secondary location",
                        "3. Verify archive integrity",
                        "4. Then delete original (if space critical)"
                    ]
                }
            else:
                decision = "archive"
                reasoning = "Recovery time analysis suggests archiving is safer than deletion."
                recommended_action = {
                    "action": "archive",
                    "archive_location": assessment.archive_options[0] if assessment.archive_options else "nas"
                }
        elif assessment.criticality in ["critical", "important"]:
            decision = "archive"
            reasoning = f"Data criticality ({assessment.criticality}) requires preservation. Archive instead of delete."
            recommended_action = {
                "action": "archive",
                "archive_location": assessment.archive_options[0] if assessment.archive_options else "nas"
            }
        elif assessment.retention_required:
            decision = "archive"
            reasoning = "Retention requirements mandate preservation. Archive instead of delete."
            recommended_action = {
                "action": "archive",
                "archive_location": assessment.archive_options[0] if assessment.archive_options else "nas"
            }
        else:
            # Small, non-critical, backed up data - might be safe to delete
            decision = "archive"  # Still prefer archive
            reasoning = "Even for non-critical data, archive is safer than delete. Prefer archive when possible."
            recommended_action = {
                "action": "archive",
                "archive_location": assessment.archive_options[0] if assessment.archive_options else "nas",
                "note": "Consider deletion only if archive space is unavailable"
            }

        # Recovery plan
        recovery_plan = {
            "backup_locations": assessment.backup_locations,
            "restore_time_hours": assessment.restore_time_hours,
            "recreation_time_hours": assessment.recreation_time_hours,
            "restore_procedures": [
                "1. Locate backup/archive",
                f"2. Estimated restore time: {assessment.restore_time_hours:.2f} hours",
                "3. Verify restore integrity",
                "4. Validate data completeness"
            ]
        }

        lifecycle_decision = LifecycleDecision(
            decision_id=decision_id,
            timestamp=datetime.now().isoformat(),
            data_path=assessment.data_path,
            decision=decision,
            reasoning=reasoning,
            risk_assessment=risk_assessment,
            recommended_action=recommended_action,
            approval_required=approval_required,
            recovery_plan=recovery_plan
        )

        self.decisions.append(lifecycle_decision)
        self._save_decision(lifecycle_decision)

        self.logger.info("")
        self.logger.info("DECISION:")
        self.logger.info(f"  Action: {decision.upper()}")
        self.logger.info(f"  Reasoning: {reasoning}")
        self.logger.info(f"  Approval Required: {approval_required}")
        self.logger.info("")

        return lifecycle_decision

    def _estimate_dir_size(self, path: Path) -> int:
        """Estimate directory size (cached if possible)"""
        # This is expensive - in production, would want caching
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except (OSError, PermissionError):
                        continue
        except (OSError, PermissionError):
            pass
        return total

    def _determine_data_type(self, path: Path) -> str:
        """Determine data type"""
        path_str = str(path).lower()
        if "snapshot" in path_str:
            return "snapshot"
        elif "backup" in path_str:
            return "backup"
        elif "log" in path_str:
            return "log"
        elif "cache" in path_str:
            return "cache"
        elif "temp" in path_str or "tmp" in path_str:
            return "temporary"
        elif path.suffix in [".json", ".yaml", ".yml", ".toml"]:
            return "config_data"
        else:
            return "general"

    def _assess_criticality(self, path: Path, size_bytes: int, data_type: str) -> str:
        """Assess data criticality"""
        path_str = str(path).lower()

        # Critical indicators
        if any(x in path_str for x in ["config", "production", "database", "critical"]):
            return "critical"

        # Important indicators
        if any(x in path_str for x in ["data", "archive", "backup", "important"]):
            return "important"

        # Low priority
        if data_type in ["cache", "temporary", "log"]:
            return "low_priority"

        # Size-based
        size_gb = size_bytes / (1024**3)
        if size_gb > 100:
            return "important"  # Large data is important

        return "routine"

    def _find_backup_locations(self, path: Path) -> List[str]:
        """Find backup locations for data"""
        # This would check actual backup systems
        # For now, return empty list
        return []

    def _estimate_recreation_time(self, path: Path, size_bytes: int, data_type: str) -> float:
        """Estimate time to recreate data from scratch (hours)"""
        # Simplified estimation
        size_gb = size_bytes / (1024**3)

        # Base time per GB varies by data type
        base_time_per_gb = {
            "snapshot": 0.1,  # Fast to recreate (just copy)
            "backup": 0.1,
            "log": 0.5,  # Moderate (logs regenerate over time)
            "cache": 0.2,
            "temporary": 0.1,
            "config_data": 2.0,  # Slow (might need manual recreation)
            "general": 1.0
        }

        time_per_gb = base_time_per_gb.get(data_type, 1.0)

        # Larger data = longer time (non-linear)
        if size_gb > 100:
            time_per_gb *= 1.5  # Slower for large datasets
        if size_gb > 1000:
            time_per_gb *= 2.0  # Much slower for very large datasets

        return size_gb * time_per_gb

    def _estimate_restore_time(self, size_bytes: int, backup_available: bool) -> float:
        """Estimate time to restore from backup (hours)"""
        if not backup_available:
            return float('inf')  # Cannot restore

        size_gb = size_bytes / (1024**3)

        # Restore is generally faster than recreation (just copy)
        # Assume 100 MB/s restore speed (network/disk dependent)
        restore_speed_gb_per_hour = 360  # 100 MB/s = 360 GB/hour

        base_time = size_gb / restore_speed_gb_per_hour

        # Add overhead
        overhead_hours = 0.5  # 30 minutes for verification, etc.

        return base_time + overhead_hours

    def _is_unique_data(self, path: Path) -> bool:
        """Determine if data is unique (not a copy)"""
        # Simplified - would need more sophisticated analysis
        path_str = str(path).lower()

        # Recursive snapshots are not unique
        if "snapshot" in path_str and path_str.count("snapshot") > 1:
            return False

        # Caches are generally not unique
        if "cache" in path_str:
            return False

        # Assume unique by default
        return True

    def _assess_retention_requirement(self, path: Path, data_type: str, criticality: str) -> bool:
        """Assess if retention is required"""
        # Critical/important data should be retained
        if criticality in ["critical", "important"]:
            return True

        # Config data should be retained
        if data_type == "config_data":
            return True

        # Caches/temps generally don't need retention
        if data_type in ["cache", "temporary"]:
            return False

        return True

    def _identify_archive_options(self, size_bytes: int, criticality: str) -> List[str]:
        """Identify available archive options"""
        size_gb = size_bytes / (1024**3)

        options = []

        # NAS for primary archive
        if size_gb < 10000:  # < 10 TB
            options.append("nas")

        # External drive for secondary backup
        if size_gb < 5000:  # < 5 TB
            options.append("external_drive")

        # Tape library for very large or long-term
        if size_gb > 100 or criticality == "critical":
            options.append("tape_library")

        return options

    def _save_decision(self, decision: LifecycleDecision):
        try:
            """Save decision to disk"""
            decision_file = self.data_dir / f"{decision.decision_id}.json"
            with open(decision_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(decision), f, indent=2, ensure_ascii=False)


        except Exception as e:
            self.logger.error(f"Error in _save_decision: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Tape Library Team Decision Engine - Data lifecycle management"
        )
        parser.add_argument(
            "--data-path",
            type=str,
            required=True,
            help="Path to data to assess"
        )
        parser.add_argument(
            "--reason",
            type=str,
            help="Reason for deletion/archive request"
        )

        args = parser.parse_args()

        engine = TapeLibraryTeamDecisionEngine()

        data_path = Path(args.data_path)

        # Assess data
        assessment = engine.assess_data(data_path)

        # Make decision
        decision = engine.make_deletion_decision(assessment, reason=args.reason)

        print("\n" + "=" * 70)
        print("TAPE LIBRARY TEAM DECISION")
        print("=" * 70)
        print(f"Decision: {decision.decision.upper()}")
        print(f"Reasoning: {decision.reasoning}")
        print(f"Approval Required: {decision.approval_required}")
        print("=" * 70)

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())