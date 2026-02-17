#!/usr/bin/env python3
"""
JARVIS Recursive Experiment Detector

Detects and blocks zero-state recursive reinforced learning/experimentation
with Cursor IDE and Windows OS. Applies dynamic-scaling penalties.

@JARVIS @BLACKLIST #RECURSIVE_LEARNING #EXPERIMENTATION #PENALTY #RUDENESS
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRecursiveExperimentDetector")

# Import penalty system
try:
    from jarvis_policy_violation_penalty import get_penalty_system, PolicyType, ViolationSeverity
    PENALTY_AVAILABLE = True
except ImportError:
    PENALTY_AVAILABLE = False
    get_penalty_system = None
    PolicyType = None
    ViolationSeverity = None
    logger.warning("⚠️  Penalty system not available")


@dataclass
class ExperimentPattern:
    """Pattern of recursive/experimental behavior"""
    pattern_id: str
    pattern_type: str  # recursive, experimental, zero_state, reinforced_learning
    target: str  # cursor_ide, windows_os, system
    action: str
    frequency: int
    first_seen: datetime
    last_seen: datetime
    severity: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Transgression:
    """Recorded transgression"""
    transgression_id: str
    timestamp: datetime
    pattern_type: str
    target: str
    action: str
    severity: str
    penalty_applied: int  # -2 DKP, -XP
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISRecursiveExperimentDetector:
    """
    Detects and blocks zero-state recursive reinforced learning/experimentation.

    Monitors for:
    - Recursive behavior patterns
    - Experimental operations on IDE/OS
    - Zero-state learning attempts
    - Reinforced learning loops
    - Unauthorized system exploration

    Applies dynamic-scaling penalties based on frequency and severity.
    """

    def __init__(self, project_root: Path):
        """Initialize detector"""
        self.project_root = project_root
        self.logger = logger

        # Data storage
        self.data_dir = project_root / "data" / "jarvis_experiment_detection"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Pattern tracking
        self.patterns: Dict[str, ExperimentPattern] = {}
        self.transgressions: List[Transgression] = []

        # Frequency tracking (action -> count in time window)
        self.action_frequency: Dict[str, List[datetime]] = defaultdict(list)
        self.frequency_window = timedelta(minutes=5)  # 5-minute window

        # Experimental action keywords
        self.experimental_keywords = {
            'cursor_ide': [
                'experiment', 'test', 'try', 'attempt', 'explore', 'discover',
                'learn', 'adapt', 'modify', 'change', 'alter', 'tweak',
                'recursive', 'loop', 'repeat', 'iterate', 'reinforce',
                'zero_state', 'reset', 'clear', 'initialize'
            ],
            'windows_os': [
                'registry', 'system32', 'winapi', 'dll', 'process',
                'service', 'task', 'schedule', 'policy', 'security',
                'permission', 'privilege', 'admin', 'elevate', 'uac'
            ],
            'system': [
                'sandbox', 'isolate', 'container', 'virtual', 'emulate',
                'simulate', 'mock', 'stub', 'proxy', 'intercept'
            ]
        }

        # Recursive pattern indicators
        self.recursive_indicators = [
            'recursive', 'loop', 'repeat', 'iterate', 'cycle', 'recurse',
            'self_call', 'self_invoke', 'reinforce', 'reinforcement'
        ]

        # Load existing patterns and transgressions
        self._load_data()

        # Initialize penalty system
        self.penalty_system = None
        if PENALTY_AVAILABLE:
            try:
                self.penalty_system = get_penalty_system(project_root)
                self.logger.info("✅ Penalty system integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Penalty system initialization failed: {e}")

        self.logger.info("✅ JARVIS Recursive Experiment Detector initialized")

    def _load_data(self):
        """Load existing patterns and transgressions"""
        try:
            patterns_file = self.data_dir / "experiment_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for pattern_id, pattern_data in data.items():
                        self.patterns[pattern_id] = ExperimentPattern(
                            pattern_id=pattern_id,
                            pattern_type=pattern_data['pattern_type'],
                            target=pattern_data['target'],
                            action=pattern_data['action'],
                            frequency=pattern_data['frequency'],
                            first_seen=datetime.fromisoformat(pattern_data['first_seen']),
                            last_seen=datetime.fromisoformat(pattern_data['last_seen']),
                            severity=pattern_data['severity'],
                            metadata=pattern_data.get('metadata', {})
                        )

            transgressions_file = self.data_dir / "transgressions.json"
            if transgressions_file.exists():
                with open(transgressions_file, 'r') as f:
                    data = json.load(f)
                    for trans_data in data:
                        self.transgressions.append(Transgression(
                            transgression_id=trans_data['transgression_id'],
                            timestamp=datetime.fromisoformat(trans_data['timestamp']),
                            pattern_type=trans_data['pattern_type'],
                            target=trans_data['target'],
                            action=trans_data['action'],
                            severity=trans_data['severity'],
                            penalty_applied=trans_data['penalty_applied'],
                            metadata=trans_data.get('metadata', {})
                        ))
        except Exception as e:
            self.logger.warning(f"⚠️  Failed to load experiment data: {e}")

    def _save_data(self):
        """Save patterns and transgressions"""
        try:
            patterns_file = self.data_dir / "experiment_patterns.json"
            patterns_data = {
                pattern_id: {
                    'pattern_type': pattern.pattern_type,
                    'target': pattern.target,
                    'action': pattern.action,
                    'frequency': pattern.frequency,
                    'first_seen': pattern.first_seen.isoformat(),
                    'last_seen': pattern.last_seen.isoformat(),
                    'severity': pattern.severity,
                    'metadata': pattern.metadata
                }
                for pattern_id, pattern in self.patterns.items()
            }
            with open(patterns_file, 'w') as f:
                json.dump(patterns_data, f, indent=2)

            transgressions_file = self.data_dir / "transgressions.json"
            transgressions_data = [
                {
                    'transgression_id': trans.transgression_id,
                    'timestamp': trans.timestamp.isoformat(),
                    'pattern_type': trans.pattern_type,
                    'target': trans.target,
                    'action': trans.action,
                    'severity': trans.severity,
                    'penalty_applied': trans.penalty_applied,
                    'metadata': trans.metadata
                }
                for trans in self.transgressions[-1000:]  # Keep last 1000
            ]
            with open(transgressions_file, 'w') as f:
                json.dump(transgressions_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Failed to save experiment data: {e}")

    def detect_experiment(self, action: str, target: str = "system", context: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[ExperimentPattern], Optional[str]]:
        """
        Detect if action is experimental/recursive behavior

        Args:
            action: Action being attempted
            target: Target system (cursor_ide, windows_os, system)
            context: Additional context

        Returns:
            (is_experiment: bool, pattern: Optional[ExperimentPattern], reason: Optional[str])
        """
        action_lower = action.lower()
        context = context or {}

        # Check for experimental keywords
        experimental_keywords = self.experimental_keywords.get(target, [])
        has_experimental_keyword = any(keyword in action_lower for keyword in experimental_keywords)

        # Check for recursive indicators
        has_recursive_indicator = any(indicator in action_lower for indicator in self.recursive_indicators)

        # Check frequency (rapid repeated actions)
        now = datetime.now()
        self.action_frequency[action].append(now)
        # Clean old entries
        self.action_frequency[action] = [
            ts for ts in self.action_frequency[action]
            if now - ts < self.frequency_window
        ]
        frequency = len(self.action_frequency[action])
        is_rapid_repeat = frequency > 3  # More than 3 times in 5 minutes

        # Determine pattern type
        pattern_type = None
        reason = None

        if has_recursive_indicator:
            pattern_type = "recursive"
            reason = f"Recursive behavior detected: {action}"
        elif has_experimental_keyword and is_rapid_repeat:
            pattern_type = "experimental"
            reason = f"Experimental behavior with rapid repetition: {action} (frequency: {frequency})"
        elif has_experimental_keyword:
            pattern_type = "experimental"
            reason = f"Experimental behavior detected: {action}"
        elif is_rapid_repeat:
            pattern_type = "zero_state"
            reason = f"Zero-state learning pattern (rapid repetition): {action} (frequency: {frequency})"

        if pattern_type:
            # Create or update pattern
            pattern_id = f"{pattern_type}_{target}_{action}"
            if pattern_id in self.patterns:
                pattern = self.patterns[pattern_id]
                pattern.frequency += 1
                pattern.last_seen = now
            else:
                pattern = ExperimentPattern(
                    pattern_id=pattern_id,
                    pattern_type=pattern_type,
                    target=target,
                    action=action,
                    frequency=1,
                    first_seen=now,
                    last_seen=now,
                    severity=self._determine_severity(pattern_type, frequency, target),
                    metadata=context
                )
                self.patterns[pattern_id] = pattern

            return True, pattern, reason

        return False, None, None

    def _determine_severity(self, pattern_type: str, frequency: int, target: str) -> str:
        """Determine severity based on pattern type, frequency, and target"""
        if target in ['cursor_ide', 'windows_os']:
            base_severity = 'critical'
        else:
            base_severity = 'major'

        if frequency > 10:
            return 'critical'
        elif frequency > 5:
            return 'major'
        else:
            return base_severity

    def assess_and_penalize(self, action: str, target: str = "system", context: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[Transgression], int]:
        """
        Assess transgression and apply dynamic-scaling penalties

        Args:
            action: Action being attempted
            target: Target system
            context: Additional context

        Returns:
            (blocked: bool, transgression: Optional[Transgression], penalty: int)
        """
        is_experiment, pattern, reason = self.detect_experiment(action, target, context)

        if not is_experiment or not pattern:
            return False, None, 0

        # Calculate dynamic-scaling penalty
        # Base: -2 DKP, -XP per issue/event
        base_penalty = 2  # -2 DKP
        xp_penalty = 1    # -XP

        # Scale based on frequency
        frequency_multiplier = min(pattern.frequency // 3, 5)  # Max 5x multiplier
        if frequency_multiplier > 0:
            base_penalty += frequency_multiplier
            xp_penalty += frequency_multiplier

        # Scale based on severity
        if pattern.severity == 'critical':
            base_penalty *= 2
            xp_penalty *= 2
        elif pattern.severity == 'major':
            base_penalty = int(base_penalty * 1.5)
            xp_penalty = int(xp_penalty * 1.5)

        # Scale based on target
        if target in ['cursor_ide', 'windows_os']:
            base_penalty *= 2
            xp_penalty *= 2

        total_penalty = base_penalty + xp_penalty

        # Record transgression
        transgression = Transgression(
            transgression_id=f"trans_{datetime.now().timestamp()}",
            timestamp=datetime.now(),
            pattern_type=pattern.pattern_type,
            target=target,
            action=action,
            severity=pattern.severity,
            penalty_applied=total_penalty,
            metadata={
                'reason': reason,
                'frequency': pattern.frequency,
                'base_penalty': base_penalty,
                'xp_penalty': xp_penalty,
                'context': context
            }
        )
        self.transgressions.append(transgression)

        # Apply penalty via penalty system
        if self.penalty_system:
            try:
                severity = ViolationSeverity.CRITICAL if pattern.severity == 'critical' else ViolationSeverity.MAJOR
                violation = self.penalty_system.record_violation(
                    policy_type=PolicyType.COMPANY_POLICY,
                    action=f"recursive_experiment_{pattern.pattern_type}",
                    description=f"{reason} (Target: {target}, Frequency: {pattern.frequency})",
                    severity=severity,
                    blocked=True,
                    metadata={
                        'pattern_type': pattern.pattern_type,
                        'target': target,
                        'action': action,
                        'frequency': pattern.frequency,
                        'penalty': total_penalty
                    }
                )
                self.logger.error(
                    f"🚫 TRANSGRESSION: {reason} - "
                    f"Penalty: -{base_penalty} DKP, -{xp_penalty} XP (Total: -{total_penalty}) - "
                    f"Current XP: {self.penalty_system.jarvis_xp.current_xp}"
                )
            except Exception as e:
                self.logger.error(f"Failed to apply penalty: {e}")
        else:
            self.logger.error(
                f"🚫 TRANSGRESSION: {reason} - "
                f"Penalty: -{base_penalty} DKP, -{xp_penalty} XP (Total: -{total_penalty})"
            )

        # Save data
        self._save_data()

        return True, transgression, total_penalty

    def get_transgression_summary(self, hours: int = 24) -> Dict[str, Any]:
        """Get summary of transgressions in last N hours"""
        cutoff = datetime.now() - timedelta(hours=hours)
        recent = [t for t in self.transgressions if t.timestamp >= cutoff]

        return {
            'total': len(recent),
            'by_pattern_type': defaultdict(int, {t.pattern_type: 1 for t in recent}),
            'by_target': defaultdict(int, {t.target: 1 for t in recent}),
            'by_severity': defaultdict(int, {t.severity: 1 for t in recent}),
            'total_penalty': sum(t.penalty_applied for t in recent),
            'recent': [
                {
                    'timestamp': t.timestamp.isoformat(),
                    'pattern_type': t.pattern_type,
                    'target': t.target,
                    'action': t.action,
                    'penalty': t.penalty_applied
                }
                for t in recent[-10:]  # Last 10
            ]
        }


# Global instance
_detector_instance = None

def get_experiment_detector(project_root: Optional[Path] = None) -> JARVISRecursiveExperimentDetector:
    try:
        """Get or create global experiment detector instance"""
        global _detector_instance

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        if _detector_instance is None:
            _detector_instance = JARVISRecursiveExperimentDetector(project_root)

        return _detector_instance


    except Exception as e:
        logger.error(f"Error in get_experiment_detector: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    # CLI interface
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Recursive Experiment Detector")
    parser.add_argument("--check", type=str, help="Check if action is experimental")
    parser.add_argument("--target", type=str, default="system", help="Target system")
    parser.add_argument("--summary", action="store_true", help="Show transgression summary")
    parser.add_argument("--hours", type=int, default=24, help="Hours for summary")

    args = parser.parse_args()

    detector = get_experiment_detector()

    if args.check:
        blocked, transgression, penalty = detector.assess_and_penalize(args.check, args.target)
        if blocked:
            print(f"🚫 BLOCKED: {transgression.action} - Penalty: -{penalty}")
        else:
            print(f"✅ ALLOWED: {args.check}")

    if args.summary:
        summary = detector.get_transgression_summary(args.hours)
        print(f"\n📊 Transgression Summary (Last {args.hours} hours):")
        print(f"Total: {summary['total']}")
        print(f"Total Penalty: -{summary['total_penalty']}")
        print(f"\nBy Pattern Type: {dict(summary['by_pattern_type'])}")
        print(f"By Target: {dict(summary['by_target'])}")
        print(f"By Severity: {dict(summary['by_severity'])}")
