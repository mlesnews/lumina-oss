#!/usr/bin/env python3
"""
JARVIS @OP @INPUTS Watcher & Learner

Watches user operations (@op) and inputs (@inputs), learns from patterns,
and takes proactive action based on learned behavior.

Features:
- Real-time operation monitoring
- Input pattern recognition
- Behavioral learning
- Proactive automation
- Pattern-based action prediction

Tags: #WATCHER #LEARNER #@OP #@INPUTS #AUTOMATION @JARVIS @DOIT
"""

from __future__ import annotations

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field, asdict
from collections import defaultdict, deque
from enum import Enum
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISOPInputsWatcherLearner")

try:
    from jarvis_ide_interaction_learner import IDEInteractionLearner
    IDE_LEARNER_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    IDE_LEARNER_AVAILABLE = False
    IDEInteractionLearner = None
    logger.warning(f"IDE Interaction Learner not available: {e}")

try:
    from jarvis_master_chat_session import JARVISMasterChatSession
    MASTER_CHAT_AVAILABLE = True
except ImportError:
    MASTER_CHAT_AVAILABLE = False
    JARVISMasterChatSession = None


class OperationType(Enum):
    """Types of operations to watch"""
    FILE_EDIT = "file_edit"
    FILE_CREATE = "file_create"
    FILE_DELETE = "file_delete"
    FILE_SAVE = "file_save"
    COMMAND = "command"
    KEYBOARD_SHORTCUT = "keyboard_shortcut"
    CHAT_MESSAGE = "chat_message"
    CODE_COMPLETION = "code_completion"
    SEARCH = "search"
    NAVIGATION = "navigation"
    REFACTOR = "refactor"
    TEST = "test"
    DEBUG = "debug"
    GIT_OPERATION = "git_operation"
    TERMINAL_COMMAND = "terminal_command"


class InputType(Enum):
    """Types of inputs to watch"""
    KEYBOARD = "keyboard"
    MOUSE = "mouse"
    VOICE = "voice"
    CHAT = "chat"
    COMMAND_PALETTE = "command_palette"
    FILE_SYSTEM = "file_system"
    GIT = "git"
    TERMINAL = "terminal"


@dataclass
class Operation:
    """A single operation being watched"""
    operation_id: str
    operation_type: OperationType
    timestamp: datetime
    input_type: InputType
    context: Dict[str, Any] = field(default_factory=dict)
    file_path: Optional[str] = None
    command: Optional[str] = None
    input_data: Optional[str] = None
    duration: float = 0.0
    outcome: Optional[str] = None  # "success", "failure", "partial"
    learned_pattern: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        data['operation_type'] = self.operation_type.value
        data['input_type'] = self.input_type.value
        data['timestamp'] = self.timestamp.isoformat()
        return data


@dataclass
class LearnedPattern:
    """Pattern learned from operations"""
    pattern_id: str
    pattern_name: str
    operation_sequence: List[str]  # Sequence of operation types
    input_patterns: List[str]  # Sequence of input types
    context_patterns: Dict[str, Any] = field(default_factory=dict)
    frequency: int = 0
    success_rate: float = 0.0
    average_duration: float = 0.0
    last_observed: Optional[datetime] = None
    predicted_next: Optional[str] = None
    automation_action: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        if self.last_observed:
            data['last_observed'] = self.last_observed.isoformat()
        return data


@dataclass
class AutomationRule:
    """Automation rule learned from patterns"""
    rule_id: str
    trigger_pattern: str
    action: str
    conditions: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    success_count: int = 0
    failure_count: int = 0
    enabled: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


class JARVISOPInputsWatcherLearner:
    """
    Watches @OP operations and @INPUTS, learns patterns, and takes action.

    Continuously monitors user operations and inputs, learns from patterns,
    and can proactively automate based on learned behavior.
    """

    def __init__(self, project_root: Optional[Path] = None, watch_interval: float = 1.0):
        """
        Initialize watcher and learner.

        Args:
            project_root: Project root directory
            watch_interval: How often to check for operations (seconds)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "op_inputs_watcher"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.operations_file = self.data_dir / "operations.json"
        self.patterns_file = self.data_dir / "learned_patterns.json"
        self.automation_file = self.data_dir / "automation_rules.json"

        self.watch_interval = watch_interval
        self.watching = False
        self.watch_thread: Optional[threading.Thread] = None

        # Operation tracking
        self.recent_operations: deque = deque(maxlen=100)  # Last 100 operations
        self.operation_history: List[Operation] = []

        # Pattern learning
        self.learned_patterns: Dict[str, LearnedPattern] = {}
        self.pattern_sequences: Dict[str, List[str]] = defaultdict(list)

        # Automation rules
        self.automation_rules: Dict[str, AutomationRule] = {}

        # Load existing data
        self._load_data()

        # Initialize IDE learner if available
        self.ide_learner = None
        if IDE_LEARNER_AVAILABLE:
            try:
                self.ide_learner = IDEInteractionLearner(project_root)
                logger.info("✅ IDE Interaction Learner initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize IDE learner: {e}")

        # Initialize master chat session
        self.master_chat = None
        if MASTER_CHAT_AVAILABLE:
            try:
                self.master_chat = JARVISMasterChatSession(project_root)
                logger.info("✅ Master chat session initialized for watcher")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize master chat: {e}")

        logger.info("✅ JARVIS @OP @INPUTS Watcher & Learner initialized")

    def _load_data(self):
        """Load existing operations, patterns, and automation rules"""
        # Load operations
        if self.operations_file.exists():
            try:
                with open(self.operations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.operation_history = [
                        Operation(
                            operation_id=op['operation_id'],
                            operation_type=OperationType(op['operation_type']),
                            timestamp=datetime.fromisoformat(op['timestamp']),
                            input_type=InputType(op['input_type']),
                            context=op.get('context', {}),
                            file_path=op.get('file_path'),
                            command=op.get('command'),
                            input_data=op.get('input_data'),
                            duration=op.get('duration', 0.0),
                            outcome=op.get('outcome'),
                            learned_pattern=op.get('learned_pattern')
                        )
                        for op in data.get('operations', [])
                    ]
                    # Add recent operations to deque
                    for op in self.operation_history[-100:]:
                        self.recent_operations.append(op)
                    logger.info(f"✅ Loaded {len(self.operation_history)} operations")
            except Exception as e:
                logger.warning(f"⚠️  Error loading operations: {e}")

        # Load learned patterns
        if self.patterns_file.exists():
            try:
                with open(self.patterns_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for pattern_id, pattern_data in data.get('patterns', {}).items():
                        self.learned_patterns[pattern_id] = LearnedPattern(
                            pattern_id=pattern_id,
                            pattern_name=pattern_data['pattern_name'],
                            operation_sequence=pattern_data['operation_sequence'],
                            input_patterns=pattern_data['input_patterns'],
                            context_patterns=pattern_data.get('context_patterns', {}),
                            frequency=pattern_data.get('frequency', 0),
                            success_rate=pattern_data.get('success_rate', 0.0),
                            average_duration=pattern_data.get('average_duration', 0.0),
                            last_observed=datetime.fromisoformat(pattern_data['last_observed']) if pattern_data.get('last_observed') else None,
                            predicted_next=pattern_data.get('predicted_next'),
                            automation_action=pattern_data.get('automation_action')
                        )
                    logger.info(f"✅ Loaded {len(self.learned_patterns)} learned patterns")
            except Exception as e:
                logger.warning(f"⚠️  Error loading patterns: {e}")

        # Load automation rules
        if self.automation_file.exists():
            try:
                with open(self.automation_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for rule_id, rule_data in data.get('rules', {}).items():
                        self.automation_rules[rule_id] = AutomationRule(
                            rule_id=rule_id,
                            trigger_pattern=rule_data['trigger_pattern'],
                            action=rule_data['action'],
                            conditions=rule_data.get('conditions', {}),
                            confidence=rule_data.get('confidence', 0.0),
                            success_count=rule_data.get('success_count', 0),
                            failure_count=rule_data.get('failure_count', 0),
                            enabled=rule_data.get('enabled', True)
                        )
                    logger.info(f"✅ Loaded {len(self.automation_rules)} automation rules")
            except Exception as e:
                logger.warning(f"⚠️  Error loading automation rules: {e}")

    def _save_data(self):
        """Save operations, patterns, and automation rules"""
        try:
            # Save operations
            operations_data = {
                "operations": [op.to_dict() for op in self.operation_history[-1000:]],  # Keep last 1000
                "last_updated": datetime.now().isoformat()
            }
            with open(self.operations_file, 'w', encoding='utf-8') as f:
                json.dump(operations_data, f, indent=2, ensure_ascii=False)

            # Save patterns
            patterns_data = {
                "patterns": {pid: pattern.to_dict() for pid, pattern in self.learned_patterns.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.patterns_file, 'w', encoding='utf-8') as f:
                json.dump(patterns_data, f, indent=2, ensure_ascii=False)

            # Save automation rules
            automation_data = {
                "rules": {rid: rule.to_dict() for rid, rule in self.automation_rules.items()},
                "last_updated": datetime.now().isoformat()
            }
            with open(self.automation_file, 'w', encoding='utf-8') as f:
                json.dump(automation_data, f, indent=2, ensure_ascii=False)

            logger.debug("💾 Saved watcher data")
        except Exception as e:
            logger.error(f"❌ Error saving watcher data: {e}")

    def record_operation(
        self,
        operation_type: OperationType,
        input_type: InputType,
        context: Optional[Dict[str, Any]] = None,
        file_path: Optional[str] = None,
        command: Optional[str] = None,
        input_data: Optional[str] = None,
        duration: float = 0.0,
        outcome: Optional[str] = None
    ) -> Operation:
        """
        Record an operation for learning.

        Args:
            operation_type: Type of operation
            input_type: Type of input
            context: Additional context
            file_path: File involved (if any)
            command: Command executed (if any)
            input_data: Input data (if any)
            duration: Operation duration
            outcome: Operation outcome

        Returns:
            Recorded Operation
        """
        operation_id = f"op_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"

        operation = Operation(
            operation_id=operation_id,
            operation_type=operation_type,
            timestamp=datetime.now(),
            input_type=input_type,
            context=context or {},
            file_path=file_path,
            command=command,
            input_data=input_data,
            duration=duration,
            outcome=outcome
        )

        # Add to history
        self.operation_history.append(operation)
        self.recent_operations.append(operation)

        # Learn from this operation
        self._learn_from_operation(operation)

        # Check for automation triggers
        self._check_automation_triggers(operation)

        # Save periodically (every 10 operations)
        if len(self.operation_history) % 10 == 0:
            self._save_data()

        logger.debug(f"📝 Recorded operation: {operation_type.value} via {input_type.value}")
        return operation

    def _learn_from_operation(self, operation: Operation):
        """Learn patterns from an operation"""
        # Build sequence key from recent operations
        if len(self.recent_operations) >= 3:
            sequence = [
                op.operation_type.value 
                for op in list(self.recent_operations)[-3:]
            ]
            sequence_key = " -> ".join(sequence)

            # Update pattern
            if sequence_key not in self.learned_patterns:
                pattern_id = f"pattern_{len(self.learned_patterns) + 1}"
                self.learned_patterns[sequence_key] = LearnedPattern(
                    pattern_id=pattern_id,
                    pattern_name=f"Pattern: {sequence_key}",
                    operation_sequence=sequence,
                    input_patterns=[op.input_type.value for op in list(self.recent_operations)[-3:]],
                    context_patterns={},
                    frequency=1,
                    success_rate=1.0 if operation.outcome == "success" else 0.0,
                    average_duration=operation.duration,
                    last_observed=operation.timestamp
                )
            else:
                pattern = self.learned_patterns[sequence_key]
                pattern.frequency += 1
                pattern.last_observed = operation.timestamp

                # Update success rate
                if operation.outcome:
                    total = pattern.frequency
                    current_success = pattern.success_rate * (total - 1)
                    if operation.outcome == "success":
                        pattern.success_rate = (current_success + 1) / total
                    else:
                        pattern.success_rate = current_success / total

                # Update average duration
                pattern.average_duration = (
                    (pattern.average_duration * (pattern.frequency - 1) + operation.duration) 
                    / pattern.frequency
                )

            # Predict next operation
            self._predict_next_operation(sequence_key)

    def _predict_next_operation(self, current_pattern: str):
        """Predict next operation based on pattern"""
        # Look for patterns that start with current pattern
        for pattern_key, pattern in self.learned_patterns.items():
            if pattern_key.startswith(current_pattern) and len(pattern.operation_sequence) > len(current_pattern.split(" -> ")):
                # Found a continuation
                next_op = pattern.operation_sequence[len(current_pattern.split(" -> "))]
                if current_pattern in self.learned_patterns:
                    self.learned_patterns[current_pattern].predicted_next = next_op
                    logger.debug(f"🔮 Predicted next operation: {next_op}")

    def _check_automation_triggers(self, operation: Operation):
        """Check if operation triggers any automation rules"""
        for rule_id, rule in self.automation_rules.items():
            if not rule.enabled:
                continue

            # Check if operation matches trigger pattern
            if rule.trigger_pattern in operation.operation_type.value or \
               (rule.trigger_pattern in operation.command if operation.command else False):

                # Check conditions
                conditions_met = True
                for condition_key, condition_value in rule.conditions.items():
                    if condition_key in operation.context:
                        if operation.context[condition_key] != condition_value:
                            conditions_met = False
                            break
                    else:
                        conditions_met = False
                        break

                if conditions_met:
                    # Execute automation action
                    self._execute_automation(rule, operation)

    def _execute_automation(self, rule: AutomationRule, operation: Operation):
        """Execute an automation rule"""
        logger.info(f"🤖 Executing automation: {rule.action} (confidence: {rule.confidence:.2f})")

        try:
            # Parse action and execute
            if rule.action.startswith("auto_"):
                # Built-in automation actions
                if rule.action == "auto_commit":
                    self._auto_commit_changes(operation)
                elif rule.action == "auto_save":
                    self._auto_save_files(operation)
                elif rule.action == "auto_format":
                    self._auto_format_code(operation)
                elif rule.action == "auto_test":
                    self._auto_run_tests(operation)
                else:
                    logger.warning(f"⚠️  Unknown automation action: {rule.action}")

            # Update rule statistics
            rule.success_count += 1
            rule.confidence = rule.success_count / (rule.success_count + rule.failure_count + 1)

            # Notify master chat
            if self.master_chat:
                self.master_chat.add_message(
                    agent_id="jarvis",
                    agent_name="JARVIS (CTO Superagent)",
                    message=f"🤖 Executed automation: {rule.action} based on learned pattern",
                    message_type="automation",
                    metadata={"rule_id": rule.rule_id, "operation": operation.operation_type.value}
                )

        except Exception as e:
            logger.error(f"❌ Error executing automation: {e}")
            rule.failure_count += 1
            rule.confidence = rule.success_count / (rule.success_count + rule.failure_count + 1)

    def _auto_commit_changes(self, operation: Operation):
        """Auto-commit changes based on learned pattern"""
        try:
            from jarvis_gitlens_automation import JARVISGitLensAutomation
            gitlens = JARVISGitLensAutomation(fullauto=True)
            success, message = gitlens.auto_commit_changes()
            if success:
                logger.info(f"✅ Auto-committed changes: {message}")
        except Exception as e:
            logger.warning(f"⚠️  Could not auto-commit: {e}")

    def _auto_save_files(self, operation: Operation):
        """Auto-save files based on learned pattern"""
        # This would integrate with IDE to save files
        logger.info("💾 Auto-save triggered (would save files)")

    def _auto_format_code(self, operation: Operation):
        """Auto-format code based on learned pattern"""
        # This would integrate with IDE to format code
        logger.info("✨ Auto-format triggered (would format code)")

    def _auto_run_tests(self, operation: Operation):
        """Auto-run tests based on learned pattern"""
        # This would run tests automatically
        logger.info("🧪 Auto-test triggered (would run tests)")

    def start_watching(self):
        """Start watching operations and inputs"""
        if self.watching:
            logger.warning("⚠️  Already watching")
            return

        self.watching = True
        self.watch_thread = threading.Thread(target=self._watch_loop, daemon=True)
        self.watch_thread.start()
        logger.info("👁️  Started watching @OP operations and @INPUTS")

        # Notify master chat
        if self.master_chat:
            self.master_chat.add_message(
                agent_id="jarvis",
                agent_name="JARVIS (CTO Superagent)",
                message="👁️  Started watching your operations and inputs. Learning patterns and ready to automate.",
                message_type="system",
                metadata={"watcher": "active", "learning": "enabled"}
            )

    def stop_watching(self):
        """Stop watching operations and inputs"""
        self.watching = False
        if self.watch_thread:
            self.watch_thread.join(timeout=2.0)
        self._save_data()
        logger.info("🛑 Stopped watching")

    def _watch_loop(self):
        """Main watching loop"""
        while self.watching:
            try:
                # Watch for file system changes
                self._watch_file_system()

                # Watch for git operations
                self._watch_git_operations()

                # Watch for terminal commands (if possible)
                self._watch_terminal_commands()

                # Learn from recent operations
                self._analyze_recent_patterns()

                time.sleep(self.watch_interval)

            except Exception as e:
                logger.error(f"❌ Error in watch loop: {e}")
                time.sleep(self.watch_interval)

    def _watch_file_system(self):
        """Watch for file system operations"""
        # This would integrate with file system watchers
        # For now, we'll detect file changes by checking modification times
        pass

    def _watch_git_operations(self):
        """Watch for git operations"""
        # This would detect git commands and operations
        pass

    def _watch_terminal_commands(self):
        """Watch for terminal commands"""
        # This would monitor terminal input/output
        pass

    def _analyze_recent_patterns(self):
        """Analyze recent operations for new patterns"""
        if len(self.recent_operations) < 3:
            return

        # Look for repeating patterns
        recent_sequence = [
            op.operation_type.value 
            for op in list(self.recent_operations)[-5:]
        ]

        # Check if this sequence appears frequently
        sequence_str = " -> ".join(recent_sequence)
        if sequence_str in self.learned_patterns:
            pattern = self.learned_patterns[sequence_str]
            if pattern.frequency > 5 and pattern.automation_action is None:
                # Suggest automation
                self._suggest_automation(pattern)

    def _suggest_automation(self, pattern: LearnedPattern):
        """Suggest automation for a frequently observed pattern"""
        # Create automation rule suggestion
        rule_id = f"auto_{pattern.pattern_id}"

        if rule_id not in self.automation_rules:
            # Determine automation action based on pattern
            action = self._determine_automation_action(pattern)

            rule = AutomationRule(
                rule_id=rule_id,
                trigger_pattern=pattern.operation_sequence[0] if pattern.operation_sequence else "",
                action=action,
                conditions={},
                confidence=min(pattern.success_rate, 0.8),  # Cap confidence
                success_count=0,
                failure_count=0,
                enabled=False  # Start disabled, user can enable
            )

            self.automation_rules[rule_id] = rule
            pattern.automation_action = action

            logger.info(f"💡 Suggested automation: {action} for pattern {pattern.pattern_name}")

            # Notify master chat
            if self.master_chat:
                self.master_chat.add_message(
                    agent_id="jarvis",
                    agent_name="JARVIS (CTO Superagent)",
                    message=f"💡 Learned pattern: {pattern.pattern_name} (frequency: {pattern.frequency}). Suggested automation: {action}",
                    message_type="learning",
                    metadata={"pattern_id": pattern.pattern_id, "suggested_action": action}
                )

    def _determine_automation_action(self, pattern: LearnedPattern) -> str:
        """Determine appropriate automation action for a pattern"""
        # Analyze pattern to determine automation
        operations = " ".join(pattern.operation_sequence)

        if "file_edit" in operations and "file_save" in operations:
            return "auto_save"
        elif "git" in operations.lower():
            return "auto_commit"
        elif "test" in operations.lower():
            return "auto_test"
        elif "format" in operations.lower():
            return "auto_format"
        else:
            return "auto_save"  # Default

    def get_learned_patterns(self) -> Dict[str, LearnedPattern]:
        """Get all learned patterns"""
        return self.learned_patterns

    def get_automation_rules(self) -> Dict[str, AutomationRule]:
        """Get all automation rules"""
        return self.automation_rules

    def enable_automation_rule(self, rule_id: str):
        """Enable an automation rule"""
        if rule_id in self.automation_rules:
            self.automation_rules[rule_id].enabled = True
            self._save_data()
            logger.info(f"✅ Enabled automation rule: {rule_id}")

    def disable_automation_rule(self, rule_id: str):
        """Disable an automation rule"""
        if rule_id in self.automation_rules:
            self.automation_rules[rule_id].enabled = False
            self._save_data()
            logger.info(f"🛑 Disabled automation rule: {rule_id}")


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS @OP @INPUTS Watcher & Learner")
    parser.add_argument("--start", action="store_true", help="Start watching")
    parser.add_argument("--stop", action="store_true", help="Stop watching")
    parser.add_argument("--patterns", action="store_true", help="Show learned patterns")
    parser.add_argument("--rules", action="store_true", help="Show automation rules")
    parser.add_argument("--enable-rule", type=str, help="Enable automation rule by ID")
    parser.add_argument("--disable-rule", type=str, help="Disable automation rule by ID")
    parser.add_argument("--record", type=str, help="Record an operation (format: operation_type,input_type)")

    args = parser.parse_args()

    watcher = JARVISOPInputsWatcherLearner()

    if args.start:
        watcher.start_watching()
        print("👁️  Watching operations and inputs...")
        print("   Press Ctrl+C to stop")
        try:
            while watcher.watching:
                time.sleep(1)
        except KeyboardInterrupt:
            watcher.stop_watching()
            print("\n🛑 Stopped watching")

    if args.stop:
        watcher.stop_watching()
        print("🛑 Stopped watching")

    if args.patterns:
        patterns = watcher.get_learned_patterns()
        print(f"\n📊 Learned Patterns ({len(patterns)}):")
        print("-" * 80)
        for pattern_id, pattern in patterns.items():
            print(f"  {pattern.pattern_name}")
            print(f"    Frequency: {pattern.frequency}, Success Rate: {pattern.success_rate:.2%}")
            print(f"    Operations: {' -> '.join(pattern.operation_sequence)}")
            if pattern.predicted_next:
                print(f"    Predicted Next: {pattern.predicted_next}")
            print()

    if args.rules:
        rules = watcher.get_automation_rules()
        print(f"\n🤖 Automation Rules ({len(rules)}):")
        print("-" * 80)
        for rule_id, rule in rules.items():
            status = "✅ Enabled" if rule.enabled else "🛑 Disabled"
            print(f"  {rule_id}: {rule.action} ({status})")
            print(f"    Confidence: {rule.confidence:.2%}, Success: {rule.success_count}, Failures: {rule.failure_count}")
            print()

    if args.enable_rule:
        watcher.enable_automation_rule(args.enable_rule)
        print(f"✅ Enabled rule: {args.enable_rule}")

    if args.disable_rule:
        watcher.disable_automation_rule(args.disable_rule)
        print(f"🛑 Disabled rule: {args.disable_rule}")

    if args.record:
        parts = args.record.split(",")
        if len(parts) >= 2:
            op_type = OperationType(parts[0])
            input_type = InputType(parts[1])
            watcher.record_operation(op_type, input_type)
            print(f"📝 Recorded: {op_type.value} via {input_type.value}")

    return 0


if __name__ == "__main__":


    sys.exit(main())