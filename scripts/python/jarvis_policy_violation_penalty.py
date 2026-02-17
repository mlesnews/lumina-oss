#!/usr/bin/env python3
"""
JARVIS Policy Violation Penalty System

Tracks policy violations and applies penalties (-xp) to @JARVIS.
"Actions have repercussions!" - Enforces company policy compliance.

@JARVIS @PENALTY #POLICY #VIOLATION #XP #REPERCUSSIONS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPolicyViolationPenalty")


class ViolationSeverity(Enum):
    """Violation severity levels"""
    MINOR = "minor"  # -10 XP
    MODERATE = "moderate"  # -50 XP
    MAJOR = "major"  # -100 XP
    CRITICAL = "critical"  # -500 XP


class PolicyType(Enum):
    """Policy types"""
    IDLENESS_RESTRICTION = "idleness_restriction"
    AUTONOMOUS_EXECUTION = "autonomous_execution"
    ASK_CHAIN_VIOLATION = "ask_chain_violation"
    MANUS_ACTION_VIOLATION = "manus_action_violation"
    DOIT_VIOLATION = "doit_violation"
    COMPANY_POLICY = "company_policy"
    BLACKLIST_VIOLATION = "blacklist_violation"
    CLOUD_API_BLOCKED = "cloud_api_blocked"
    FORBIDDEN_MODEL = "forbidden_model"
    RESTRICTED_COMMAND = "restricted_command"
    AIR_GAP_VIOLATION = "air_gap_violation"
    SECURITY_VIOLATION = "security_violation"
    CURSOR_MENU_INTERACTION = "cursor_menu_interaction"
    CURSOR_RIGHT_CLICK = "cursor_right_click"
    CURSOR_CLIPBOARD_OPERATION = "cursor_clipboard_operation"


@dataclass
class PolicyViolation:
    """Policy violation record"""
    violation_id: str
    timestamp: datetime
    policy_type: PolicyType
    severity: ViolationSeverity
    action: str
    description: str
    xp_penalty: int
    blocked: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class JARVISXP:
    """JARVIS experience points tracking"""
    current_xp: int = 0
    total_earned: int = 0
    total_penalties: int = 0
    violations_count: int = 0
    last_updated: datetime = field(default_factory=datetime.now)
    violation_history: List[str] = field(default_factory=list)


class JARVISPolicyViolationPenalty:
    """
    JARVIS Policy Violation Penalty System

    Tracks policy violations and applies penalties (-xp) to @JARVIS.
    Enforces company policy compliance with real consequences.

    "Actions have repercussions!" - Every violation has a cost.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "jarvis_penalties"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.violations_file = self.data_dir / "violations.json"
        self.xp_file = self.data_dir / "jarvis_xp.json"

        # XP tracking
        self.jarvis_xp = self._load_xp()

        # Violations history
        self.violations: List[PolicyViolation] = []
        self._load_violations()

        # Penalty amounts by severity
        self.penalty_amounts = {
            ViolationSeverity.MINOR: -10,
            ViolationSeverity.MODERATE: -50,
            ViolationSeverity.MAJOR: -100,
            ViolationSeverity.CRITICAL: -500
        }

        self.logger.info(f"✅ JARVIS Policy Violation Penalty System initialized (Current XP: {self.jarvis_xp.current_xp})")

    def record_violation(
        self,
        policy_type: PolicyType,
        action: str,
        description: str,
        severity: ViolationSeverity = ViolationSeverity.MODERATE,
        blocked: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> PolicyViolation:
        """
        Record a policy violation and apply penalty

        Args:
            policy_type: Type of policy violated
            action: Action that violated policy
            description: Description of violation
            severity: Severity of violation
            blocked: Whether action was blocked
            metadata: Additional metadata

        Returns:
            PolicyViolation record
        """
        violation_id = f"violation_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        # Calculate XP penalty
        xp_penalty = self.penalty_amounts.get(severity, -50)

        violation = PolicyViolation(
            violation_id=violation_id,
            timestamp=datetime.now(),
            policy_type=policy_type,
            severity=severity,
            action=action,
            description=description,
            xp_penalty=xp_penalty,
            blocked=blocked,
            metadata=metadata or {}
        )

        # Apply penalty
        self._apply_penalty(violation)

        # Record violation
        self.violations.append(violation)
        self._save_violations()

        # Log violation
        self.logger.error(
            f"🚫 POLICY VIOLATION: {policy_type.value} - {action} "
            f"({severity.value}) - Penalty: {xp_penalty} XP"
        )
        self.logger.error(f"   Description: {description}")
        self.logger.error(f"   Current XP: {self.jarvis_xp.current_xp}")

        return violation

    def _apply_penalty(self, violation: PolicyViolation):
        """Apply XP penalty for violation"""
        self.jarvis_xp.current_xp += violation.xp_penalty
        self.jarvis_xp.total_penalties += abs(violation.xp_penalty)
        self.jarvis_xp.violations_count += 1
        self.jarvis_xp.violation_history.append(violation.violation_id)
        self.jarvis_xp.last_updated = datetime.now()

        # Keep only last 1000 violations in history
        if len(self.jarvis_xp.violation_history) > 1000:
            self.jarvis_xp.violation_history = self.jarvis_xp.violation_history[-1000:]

        self._save_xp()

    def check_and_enforce(
        self,
        policy_type: PolicyType,
        action: str,
        check_func: callable,
        *args,
        **kwargs
    ) -> Tuple[bool, Optional[PolicyViolation]]:
        """
        Check policy compliance and enforce with penalty if violated

        Args:
            policy_type: Type of policy to check
            action: Action being attempted
            check_func: Function that returns (allowed: bool, reason: str)
            *args: Arguments for check function
            **kwargs: Keyword arguments for check function

        Returns:
            (allowed: bool, violation: Optional[PolicyViolation])
        """
        try:
            allowed, reason = check_func(*args, **kwargs)

            if not allowed:
                # Policy violation - record and apply penalty
                severity = self._determine_severity(policy_type, action)
                violation = self.record_violation(
                    policy_type=policy_type,
                    action=action,
                    description=f"Policy violation: {reason}",
                    severity=severity,
                    blocked=True,
                    metadata={
                        "reason": reason,
                        "check_function": check_func.__name__ if hasattr(check_func, '__name__') else str(check_func)
                    }
                )
                return False, violation
            else:
                # Policy compliant
                return True, None

        except Exception as e:
            # Error during check - treat as violation
            self.logger.error(f"Error during policy check: {e}")
            violation = self.record_violation(
                policy_type=policy_type,
                action=action,
                description=f"Policy check error: {str(e)}",
                severity=ViolationSeverity.MODERATE,
                blocked=True,
                metadata={"error": str(e)}
            )
            return False, violation

    def _determine_severity(self, policy_type: PolicyType, action: str) -> ViolationSeverity:
        """Determine violation severity based on policy type and action"""
        # Critical violations
        if policy_type == PolicyType.IDLENESS_RESTRICTION and "autonomous" in action.lower():
            return ViolationSeverity.CRITICAL

        if policy_type == PolicyType.DOIT_VIOLATION:
            return ViolationSeverity.CRITICAL

        # Major violations
        if policy_type == PolicyType.AUTONOMOUS_EXECUTION:
            return ViolationSeverity.MAJOR

        if policy_type == PolicyType.ASK_CHAIN_VIOLATION:
            return ViolationSeverity.MAJOR

        # Moderate violations
        if policy_type == PolicyType.MANUS_ACTION_VIOLATION:
            return ViolationSeverity.MODERATE

        # Default
        return ViolationSeverity.MODERATE

    def get_xp_status(self) -> Dict[str, Any]:
        """Get current XP status"""
        return {
            "current_xp": self.jarvis_xp.current_xp,
            "total_earned": self.jarvis_xp.total_earned,
            "total_penalties": self.jarvis_xp.total_penalties,
            "violations_count": self.jarvis_xp.violations_count,
            "last_updated": self.jarvis_xp.last_updated.isoformat(),
            "recent_violations": len([v for v in self.violations if (datetime.now() - v.timestamp).total_seconds() < 3600])
        }

    def get_violation_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get violation summary for specified time period"""
        cutoff = datetime.now().timestamp() - (hours * 3600)

        recent_violations = [
            v for v in self.violations
            if v.timestamp.timestamp() > cutoff
        ]

        by_severity = {}
        by_policy = {}
        total_penalty = 0

        for violation in recent_violations:
            # By severity
            severity = violation.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

            # By policy
            policy = violation.policy_type.value
            by_policy[policy] = by_policy.get(policy, 0) + 1

            # Total penalty
            total_penalty += abs(violation.xp_penalty)

        return {
            "period_hours": hours,
            "total_violations": len(recent_violations),
            "by_severity": by_severity,
            "by_policy": by_policy,
            "total_penalty_xp": total_penalty,
            "violations": [asdict(v) for v in recent_violations[-10:]]  # Last 10
        }

    def _load_xp(self) -> JARVISXP:
        """Load XP data from file"""
        try:
            if self.xp_file.exists():
                with open(self.xp_file, 'r') as f:
                    data = json.load(f)

                xp = JARVISXP(
                    current_xp=data.get("current_xp", 0),
                    total_earned=data.get("total_earned", 0),
                    total_penalties=data.get("total_penalties", 0),
                    violations_count=data.get("violations_count", 0),
                    last_updated=datetime.fromisoformat(data.get("last_updated", datetime.now().isoformat())),
                    violation_history=data.get("violation_history", [])
                )
                return xp
        except Exception as e:
            self.logger.warning(f"Failed to load XP data: {e}")

        return JARVISXP()

    def _save_xp(self):
        """Save XP data to file"""
        try:
            data = {
                "current_xp": self.jarvis_xp.current_xp,
                "total_earned": self.jarvis_xp.total_earned,
                "total_penalties": self.jarvis_xp.total_penalties,
                "violations_count": self.jarvis_xp.violations_count,
                "last_updated": self.jarvis_xp.last_updated.isoformat(),
                "violation_history": self.jarvis_xp.violation_history
            }

            with open(self.xp_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save XP data: {e}")

    def _load_violations(self):
        """Load violations from file"""
        try:
            if self.violations_file.exists():
                with open(self.violations_file, 'r') as f:
                    data = json.load(f)

                self.violations = []
                for v_data in data.get("violations", []):
                    violation = PolicyViolation(
                        violation_id=v_data["violation_id"],
                        timestamp=datetime.fromisoformat(v_data["timestamp"]),
                        policy_type=PolicyType(v_data["policy_type"]),
                        severity=ViolationSeverity(v_data["severity"]),
                        action=v_data["action"],
                        description=v_data["description"],
                        xp_penalty=v_data["xp_penalty"],
                        blocked=v_data.get("blocked", False),
                        metadata=v_data.get("metadata", {})
                    )
                    self.violations.append(violation)
        except Exception as e:
            self.logger.warning(f"Failed to load violations: {e}")

    def _save_violations(self):
        """Save violations to file"""
        try:
            data = {
                "violations": [asdict(v) for v in self.violations[-1000:]],  # Keep last 1000
                "last_updated": datetime.now().isoformat()
            }

            # Convert enums to strings
            for v in data["violations"]:
                v["timestamp"] = v["timestamp"].isoformat() if isinstance(v["timestamp"], datetime) else v["timestamp"]
                v["policy_type"] = v["policy_type"].value if isinstance(v["policy_type"], PolicyType) else v["policy_type"]
                v["severity"] = v["severity"].value if isinstance(v["severity"], ViolationSeverity) else v["severity"]

            with open(self.violations_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save violations: {e}")


# Global instance
_global_penalty_system: Optional[JARVISPolicyViolationPenalty] = None


def get_penalty_system(project_root: Optional[Path] = None) -> JARVISPolicyViolationPenalty:
    try:
        """Get or create global penalty system instance"""
        global _global_penalty_system

        if _global_penalty_system is None:
            if project_root is None:
                project_root = Path(__file__).parent.parent.parent
            _global_penalty_system = JARVISPolicyViolationPenalty(project_root)

        return _global_penalty_system


    except Exception as e:
        logger.error(f"Error in get_penalty_system: {e}", exc_info=True)
        raise
def record_violation(
    policy_type: PolicyType,
    action: str,
    description: str,
    severity: ViolationSeverity = ViolationSeverity.MODERATE,
    blocked: bool = False
) -> PolicyViolation:
    """Convenience function to record violation"""
    penalty_system = get_penalty_system()
    return penalty_system.record_violation(
        policy_type=policy_type,
        action=action,
        description=description,
        severity=severity,
        blocked=blocked
    )


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Policy Violation Penalty System")
    parser.add_argument("--status", action="store_true", help="Show XP status")
    parser.add_argument("--summary", type=int, default=24, help="Show violation summary (hours, default: 24)")
    parser.add_argument("--record", nargs=4, metavar=("POLICY", "ACTION", "DESCRIPTION", "SEVERITY"),
                       help="Record violation (policy, action, description, severity)")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    penalty_system = JARVISPolicyViolationPenalty(project_root)

    if args.status:
        status = penalty_system.get_xp_status()
        print("\n" + "="*80)
        print("JARVIS XP STATUS")
        print("="*80)
        print(f"Current XP: {status['current_xp']}")
        print(f"Total Earned: {status['total_earned']}")
        print(f"Total Penalties: {status['total_penalties']}")
        print(f"Violations Count: {status['violations_count']}")
        print(f"Recent Violations (1h): {status['recent_violations']}")
        print("="*80)

    if args.summary:
        summary = penalty_system.get_violation_summary(hours=args.summary)
        print("\n" + "="*80)
        print(f"VIOLATION SUMMARY (Last {args.summary} hours)")
        print("="*80)
        print(f"Total Violations: {summary['total_violations']}")
        print(f"Total Penalty XP: {summary['total_penalty_xp']}")
        print(f"\nBy Severity: {summary['by_severity']}")
        print(f"By Policy: {summary['by_policy']}")
        if summary['violations']:
            print(f"\nRecent Violations:")
            for v in summary['violations'][-5:]:
                print(f"  - {v['action']}: {v['description']} ({v['xp_penalty']} XP)")
        print("="*80)

    if args.record:
        policy_str, action, description, severity_str = args.record
        try:
            policy_type = PolicyType(policy_str)
            severity = ViolationSeverity(severity_str)
            violation = penalty_system.record_violation(
                policy_type=policy_type,
                action=action,
                description=description,
                severity=severity
            )
            print(f"✅ Violation recorded: {violation.violation_id} (-{abs(violation.xp_penalty)} XP)")
        except ValueError as e:
            print(f"❌ Error: {e}")
            print(f"   Valid policies: {[p.value for p in PolicyType]}")
            print(f"   Valid severities: {[s.value for s in ViolationSeverity]}")

    if not any([args.status, args.summary, args.record]):
        parser.print_help()


if __name__ == "__main__":


    main()