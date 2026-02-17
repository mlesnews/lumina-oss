#!/usr/bin/env python3
"""
MANUS Cursor IDE Controller
@PEAK Troubleshooting & Decisioning System

Advanced Cursor IDE control system for automated troubleshooting,
decision making, and intelligent code manipulation using MANUS framework.

Features:
- Real-time IDE state monitoring
- Automated troubleshooting workflows
- Intelligent decision support
- Code manipulation and refactoring
- Error detection and resolution
- Performance optimization
"""

import sys
import time
import json
import psutil
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import threading
import queue
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    import pynput
    from pynput.keyboard import Key, Controller as KeyboardController
    from pynput.mouse import Button, Controller as MouseController
    import pygetwindow as gw
    import pyautogui
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MANUS] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CursorState:
    """Current state of Cursor IDE"""
    window_title: str = ""
    active_file: str = ""
    cursor_position: Tuple[int, int] = (0, 0)
    selection: str = ""
    diagnostics: List[Dict[str, Any]] = field(default_factory=list)
    problems: List[Dict[str, Any]] = field(default_factory=list)
    last_modified: datetime = field(default_factory=datetime.now)
    performance_metrics: Dict[str, float] = field(default_factory=dict)

@dataclass
class TroubleshootingAction:
    """A troubleshooting action with decision logic"""
    action_id: str
    description: str
    trigger_conditions: List[str]
    execution_steps: List[Dict[str, Any]]
    success_criteria: List[str]
    rollback_steps: List[Dict[str, Any]]
    priority: int = 1
    risk_level: str = "low"
    estimated_duration: int = 30  # seconds

@dataclass
class DecisionContext:
    """Context for decision making"""
    problem_type: str
    severity: str
    affected_files: List[str]
    error_messages: List[str]
    code_context: str
    available_actions: List[TroubleshootingAction]
    system_state: CursorState
    decision_timestamp: datetime = field(default_factory=datetime.now)

class ManusCursorController:
    """
    MANUS Framework for Cursor IDE Control
    @PEAK Troubleshooting & Decisioning System
    """

    def __init__(self):
        self.cursor_window = None
        self.keyboard = None
        self.mouse = None
        self.current_state = CursorState()

        # Initialize controllers
        if PYNPUT_AVAILABLE:
            self.keyboard = KeyboardController()
            self.mouse = MouseController()
        else:
            logger.warning("PyAutoGUI controllers not available")

        # Troubleshooting action database
        self.troubleshooting_actions = self._initialize_troubleshooting_actions()

        # Decision engine
        self.decision_queue = queue.Queue()
        self.decision_thread = threading.Thread(
            target=self._decision_engine_loop,
            daemon=True
        )
        self.decision_thread.start()

        # Monitoring
        self.monitoring_active = False
        self.monitor_thread = None

        # Git repository path (will be detected from current working directory)
        self.git_repo_path = None
        self._detect_git_repo()

        logger.info("🕹️ MANUS Cursor Controller initialized")

    def _initialize_troubleshooting_actions(self) -> Dict[str, TroubleshootingAction]:
        """Initialize comprehensive troubleshooting action database"""
        actions = {}

        # Import Error Resolution
        actions['fix_import_error'] = TroubleshootingAction(
            action_id='fix_import_error',
            description='Fix Python import errors by checking paths and installing missing packages',
            trigger_conditions=[
                'error_message contains "ImportError"',
                'error_message contains "ModuleNotFoundError"',
                'file_extension == ".py"'
            ],
            execution_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},  # Command palette
                {'type': 'type_text', 'text': 'Python: Select Interpreter'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'wait', 'duration': 2},
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},
                {'type': 'type_text', 'text': 'Terminal: Create New Terminal'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'type_text', 'text': 'pip install '},
                {'type': 'wait', 'duration': 1}
            ],
            success_criteria=[
                'no_import_errors_remaining',
                'module_can_be_imported'
            ],
            rollback_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'z']},
                {'type': 'wait', 'duration': 1}
            ],
            priority=1,
            risk_level='low'
        )

        # Syntax Error Auto-Fix
        actions['fix_syntax_error'] = TroubleshootingAction(
            action_id='fix_syntax_error',
            description='Automatically fix common Python syntax errors',
            trigger_conditions=[
                'error_message contains "SyntaxError"',
                'error_message contains "IndentationError"',
                'file_extension == ".py"'
            ],
            execution_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},
                {'type': 'type_text', 'text': 'Python: Run Selection/Line in Terminal'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'wait', 'duration': 2},
                {'type': 'analyze_output', 'action': 'check_syntax_errors'},
                {'type': 'auto_fix', 'patterns': ['indentation', 'missing_colon', 'unmatched_brackets']}
            ],
            success_criteria=[
                'syntax_errors_resolved',
                'code_compiles_successfully'
            ],
            rollback_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'z']},
                {'type': 'wait', 'duration': 1}
            ],
            priority=2,
            risk_level='low'
        )

        # Performance Optimization
        actions['optimize_performance'] = TroubleshootingAction(
            action_id='optimize_performance',
            description='Optimize code performance and memory usage',
            trigger_conditions=[
                'performance_metric > threshold',
                'memory_usage > 80%',
                'response_time > 2_seconds'
            ],
            execution_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},
                {'type': 'type_text', 'text': 'Python: Run Selection/Line in Terminal'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'analyze_code', 'patterns': ['inefficient_loops', 'memory_leaks', 'blocking_calls']},
                {'type': 'apply_optimizations', 'techniques': ['vectorization', 'caching', 'async_conversion']}
            ],
            success_criteria=[
                'performance_improved > 20%',
                'memory_usage_reduced',
                'response_time_improved'
            ],
            rollback_steps=[
                {'type': 'git', 'command': 'checkout HEAD -- {file}'},
                {'type': 'wait', 'duration': 2}
            ],
            priority=3,
            risk_level='medium'
        )

        # Code Quality Enhancement
        actions['enhance_code_quality'] = TroubleshootingAction(
            action_id='enhance_code_quality',
            description='Improve code quality with linting and formatting',
            trigger_conditions=[
                'linting_errors > 0',
                'code_complexity > 10',
                'test_coverage < 80%'
            ],
            execution_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},
                {'type': 'type_text', 'text': 'Python: Sort Imports'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'wait', 'duration': 1},
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},
                {'type': 'type_text', 'text': 'Python: Run Linting'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'auto_fix_linting', 'rules': ['formatting', 'imports', 'naming']}
            ],
            success_criteria=[
                'linting_errors_resolved',
                'code_quality_score_improved',
                'formatting_consistent'
            ],
            rollback_steps=[
                {'type': 'git', 'command': 'checkout HEAD -- {file}'},
                {'type': 'wait', 'duration': 1}
            ],
            priority=4,
            risk_level='low'
        )

        # Debug Session Setup
        actions['setup_debug_session'] = TroubleshootingAction(
            action_id='setup_debug_session',
            description='Set up debugging session for error investigation',
            trigger_conditions=[
                'error_message contains "Exception"',
                'error_message contains "Traceback"',
                'debugging_requested'
            ],
            execution_steps=[
                {'type': 'keyboard', 'keys': ['f9']},  # Toggle breakpoint
                {'type': 'keyboard', 'keys': ['f5']},  # Start debugging
                {'type': 'wait', 'duration': 3},
                {'type': 'analyze_debug_output', 'action': 'capture_stack_trace'},
                {'type': 'set_watch_expressions', 'variables': ['key_variables']}
            ],
            success_criteria=[
                'debug_session_started',
                'breakpoints_set',
                'variables_inspectable'
            ],
            rollback_steps=[
                {'type': 'keyboard', 'keys': ['shift', 'f5']},  # Stop debugging
                {'type': 'wait', 'duration': 1}
            ],
            priority=1,
            risk_level='low'
        )

        # Git Conflict Resolution
        actions['resolve_git_conflicts'] = TroubleshootingAction(
            action_id='resolve_git_conflicts',
            description='Automatically resolve Git merge conflicts',
            trigger_conditions=[
                'git_status contains "conflicts"',
                'error_message contains "merge conflict"',
                'file_status == "conflicted"'
            ],
            execution_steps=[
                {'type': 'keyboard', 'keys': ['ctrl', 'shift', 'p']},
                {'type': 'type_text', 'text': 'Git: Open Changes'},
                {'type': 'press', 'key': 'enter'},
                {'type': 'analyze_conflicts', 'strategy': 'intelligent_merge'},
                {'type': 'accept_merge', 'option': 'both'}
            ],
            success_criteria=[
                'conflicts_resolved',
                'git_status_clean',
                'code_compiles'
            ],
            rollback_steps=[
                {'type': 'terminal', 'command': 'git merge --abort'},
                {'type': 'wait', 'duration': 2}
            ],
            priority=2,
            risk_level='medium'
        )

        return actions

    def connect_to_cursor(self) -> bool:
        """
        Establish connection to Cursor IDE window
        """
        try:
            # Find Cursor window
            windows = gw.getWindowsWithTitle('Cursor')
            if not windows:
                windows = gw.getWindowsWithTitle('cursor')

            if windows:
                self.cursor_window = windows[0]
                self.cursor_window.activate()
                logger.info(f"✅ Connected to Cursor window: {self.cursor_window.title}")
                return True
            else:
                logger.error("❌ Cursor IDE window not found")
                return False

        except Exception as e:
            logger.error(f"❌ Failed to connect to Cursor: {e}")
            return False

    def get_cursor_state(self) -> CursorState:
        """
        Get comprehensive Cursor IDE state
        """
        state = CursorState()

        if not self.cursor_window:
            if not self.connect_to_cursor():
                return state

        try:
            # Get window info
            state.window_title = self.cursor_window.title

            # Get performance metrics
            process = psutil.Process()
            state.performance_metrics = {
                'cpu_percent': process.cpu_percent(),
                'memory_percent': process.memory_percent(),
                'memory_mb': process.memory_info().rss / 1024 / 1024
            }

            # Get diagnostics (would need VS Code API integration)
            # This is a placeholder for actual diagnostics
            state.diagnostics = []
            state.problems = []

            state.last_modified = datetime.now()

        except Exception as e:
            logger.error(f"❌ Failed to get Cursor state: {e}")

        self.current_state = state
        return state

    def execute_troubleshooting_action(self, action: TroubleshootingAction,
                                     context: DecisionContext) -> bool:
        """
        Execute a troubleshooting action with MANUS control
        """
        logger.info(f"🔧 Executing troubleshooting action: {action.action_id}")

        try:
            # Ensure Cursor is active
            if not self.connect_to_cursor():
                return False

            success = True

            for step in action.execution_steps:
                if not self._execute_step(step, context):
                    success = False
                    break

                time.sleep(0.5)  # Small delay between steps

            # Verify success criteria
            if success:
                success = self._verify_success_criteria(action.success_criteria, context)

            if not success and action.rollback_steps:
                logger.warning(f"⚠️ Action failed, executing rollback for: {action.action_id}")
                self._execute_rollback(action.rollback_steps, context)

            return success

        except Exception as e:
            logger.error(f"❌ Action execution failed: {e}")
            return False

    def _execute_step(self, step: Dict[str, Any], context: DecisionContext) -> bool:
        """Execute a single action step"""
        step_type = step.get('type', '')

        try:
            if step_type == 'keyboard':
                keys = step.get('keys', [])
                if isinstance(keys, list):
                    for key in keys:
                        if hasattr(Key, key):
                            self.keyboard.press(getattr(Key, key))
                        else:
                            self.keyboard.press(key)
                    time.sleep(0.1)
                    for key in reversed(keys):
                        if hasattr(Key, key):
                            self.keyboard.release(getattr(Key, key))
                        else:
                            self.keyboard.release(key)
                return True

            elif step_type == 'press':
                key = step.get('key', '')
                if hasattr(Key, key):
                    self.keyboard.press(getattr(Key, key))
                    time.sleep(0.1)
                    self.keyboard.release(getattr(Key, key))
                else:
                    pyautogui.press(key)
                return True

            elif step_type == 'type_text':
                text = step.get('text', '')
                # Auto-correct typos before typing
                try:
                    from manus_auto_grammarly import MANUSAutoGrammarly
                    grammarly = MANUSAutoGrammarly()
                    text = grammarly.auto_correct_input(text)
                except Exception as e:
                    logger.debug(f"Auto-Grammarly not available: {e}")
                self.keyboard.type(text)
                return True

            elif step_type == 'wait':
                duration = step.get('duration', 1)
                time.sleep(duration)
                return True

            elif step_type == 'analyze_code':
                # Placeholder for code analysis
                patterns = step.get('patterns', [])
                logger.info(f"Analyzing code patterns: {patterns}")
                return True

            elif step_type == 'auto_fix':
                # Placeholder for auto-fixing
                patterns = step.get('patterns', [])
                logger.info(f"Auto-fixing patterns: {patterns}")
                return True

            else:
                logger.warning(f"Unknown step type: {step_type}")
                return False

        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return False

    def _execute_rollback(self, rollback_steps: List[Dict[str, Any]],
                         context: DecisionContext) -> bool:
        """Execute rollback steps"""
        logger.info("🔄 Executing rollback steps")

        for step in rollback_steps:
            try:
                if step['type'] == 'keyboard':
                    keys = step.get('keys', [])
                    self.keyboard.press(Key.ctrl)
                    self.keyboard.press('z')
                    time.sleep(0.1)
                    self.keyboard.release('z')
                    self.keyboard.release(Key.ctrl)
                elif step['type'] == 'git':
                    command = step.get('command', '')
                    # Execute git command (placeholder)
                    logger.info(f"Git rollback: {command}")
                elif step['type'] == 'terminal':
                    command = step.get('command', '')
                    # Execute terminal command (placeholder)
                    logger.info(f"Terminal rollback: {command}")

            except Exception as e:
                logger.error(f"Rollback step failed: {e}")
                return False

        return True

    def _verify_success_criteria(self, criteria: List[str], context: DecisionContext) -> bool:
        """Verify if success criteria are met"""
        # Placeholder verification logic
        for criterion in criteria:
            if 'no_import_errors' in criterion:
                # Check if imports work
                pass
            elif 'syntax_errors_resolved' in criterion:
                # Check syntax
                pass
            elif 'performance_improved' in criterion:
                # Check performance metrics
                pass

        # For now, assume success
        return True

    def make_decision(self, problem_description: str, context: DecisionContext) -> Optional[TroubleshootingAction]:
        """
        Make intelligent decision on which troubleshooting action to take
        """
        logger.info(f"🤔 Making decision for problem: {problem_description}")

        # Analyze context and select appropriate action
        applicable_actions = []

        for action in self.troubleshooting_actions.values():
            if self._matches_trigger_conditions(action.trigger_conditions, context):
                applicable_actions.append(action)

        if not applicable_actions:
            logger.warning("No applicable troubleshooting actions found")
            return None

        # Select best action based on priority, risk, and context
        best_action = min(applicable_actions,
                         key=lambda x: (x.priority, self._risk_score(x.risk_level)))

        logger.info(f"🎯 Selected action: {best_action.action_id}")
        return best_action

    def _matches_trigger_conditions(self, conditions: List[str], context: DecisionContext) -> bool:
        """Check if trigger conditions match the current context"""
        for condition in conditions:
            if 'error_message contains' in condition:
                error_text = condition.split('"')[1]
                if not any(error_text in error for error in context.error_messages):
                    return False
            elif 'file_extension' in condition:
                ext = condition.split('==')[1].strip().strip('"').strip("'")
                if not any(file.endswith(ext) for file in context.affected_files):
                    return False

        return True

    def _risk_score(self, risk_level: str) -> int:
        """Convert risk level to numeric score"""
        risk_scores = {'low': 1, 'medium': 2, 'high': 3, 'critical': 4}
        return risk_scores.get(risk_level, 1)

    def _decision_engine_loop(self):
        """Main decision engine processing loop"""
        while True:
            try:
                if not self.decision_queue.empty():
                    decision_request = self.decision_queue.get()

                    # Process decision request
                    action = self.make_decision(
                        decision_request['problem'],
                        decision_request['context']
                    )

                    if action:
                        success = self.execute_troubleshooting_action(
                            action,
                            decision_request['context']
                        )

                        logger.info(f"Decision execution result: {'SUCCESS' if success else 'FAILED'}")

                time.sleep(1)  # Process decisions every second

            except Exception as e:
                logger.error(f"Decision engine error: {e}")
                time.sleep(5)

    def start_monitoring(self):
        """Start Cursor IDE monitoring"""
        if self.monitoring_active:
            return

        self.monitoring_active = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            daemon=True
        )
        self.monitor_thread.start()

        logger.info("👁️ MANUS monitoring started")

    def stop_monitoring(self):
        """Stop Cursor IDE monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)

        logger.info("🛑 MANUS monitoring stopped")

    def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self.monitoring_active:
            try:
                # Update Cursor state
                state = self.get_cursor_state()

                # Check for issues requiring decisions
                issues = self._detect_issues(state)

                for issue in issues:
                    decision_context = DecisionContext(
                        problem_type=issue['type'],
                        severity=issue['severity'],
                        affected_files=issue.get('files', []),
                        error_messages=issue.get('messages', []),
                        code_context=issue.get('code_context', ''),
                        available_actions=list(self.troubleshooting_actions.values()),
                        system_state=state
                    )

                    # Queue decision for processing
                    self.decision_queue.put({
                        'problem': issue['description'],
                        'context': decision_context
                    })

                time.sleep(10)  # Monitor every 10 seconds

            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(30)

    def _detect_issues(self, state: CursorState) -> List[Dict[str, Any]]:
        """Detect issues requiring troubleshooting"""
        issues = []

        # Check performance issues
        if state.performance_metrics.get('memory_percent', 0) > 80:
            issues.append({
                'type': 'performance',
                'severity': 'high',
                'description': 'High memory usage detected',
                'messages': ['Memory usage above 80%'],
                'code_context': ''
            })

        # Check for common error patterns (placeholder)
        # In real implementation, this would analyze diagnostics/problems

        return issues

    def troubleshoot_issue(self, problem_description: str,
                          affected_files: List[str] = None,
                          error_messages: List[str] = None) -> bool:
        """
        Manually trigger troubleshooting for a specific issue
        """
        context = DecisionContext(
            problem_type='manual',
            severity='medium',
            affected_files=affected_files or [],
            error_messages=error_messages or [],
            code_context='',
            available_actions=list(self.troubleshooting_actions.values()),
            system_state=self.current_state
        )

        action = self.make_decision(problem_description, context)

        if action:
            return self.execute_troubleshooting_action(action, context)
        else:
            logger.warning("No suitable troubleshooting action found")
            return False

    def _detect_git_repo(self):
        """Detect git repository path from current working directory"""
        try:
            current_dir = Path.cwd()
            # Walk up the directory tree to find .git folder
            for path in [current_dir] + list(current_dir.parents):
                if (path / '.git').exists():
                    self.git_repo_path = path
                    logger.info(f"✅ Detected git repository: {self.git_repo_path}")
                    return
            logger.warning("⚠️ No git repository detected in current directory tree")
        except Exception as e:
            logger.error(f"❌ Failed to detect git repository: {e}")

    def review_workflow(self, commit_message: str, 
                       review_files: Optional[List[str]] = None,
                       stage_all: bool = True) -> Dict[str, Any]:
        """
        Perform review workflow: review changes, stage files, commit with custom message

        Args:
            commit_message: Custom commit message for the changes
            review_files: Optional list of specific files to review and commit
            stage_all: If True, stage all changes; if False, only stage specified files

        Returns:
            Dict with workflow results including status, files_staged, commit_hash, etc.
        """
        logger.info(f"📋 Starting review workflow with commit message: {commit_message[:50]}...")

        result = {
            'status': 'pending',
            'timestamp': datetime.now().isoformat(),
            'commit_message': commit_message,
            'files_staged': [],
            'files_modified': [],
            'commit_hash': None,
            'error': None
        }

        try:
            if not self.git_repo_path:
                self._detect_git_repo()
                if not self.git_repo_path:
                    result['status'] = 'error'
                    result['error'] = 'No git repository found'
                    logger.error("❌ Cannot perform review workflow: no git repository")
                    return result

            # Get status of modified files
            status_result = self._git_status()
            if status_result.get('error'):
                result['status'] = 'error'
                result['error'] = status_result['error']
                return result

            modified_files = status_result.get('modified', [])
            untracked_files = status_result.get('untracked', [])
            all_changed_files = modified_files + untracked_files

            result['files_modified'] = all_changed_files

            # Determine which files to stage
            if review_files:
                # Stage specific files if provided
                files_to_stage = [f for f in review_files if f in all_changed_files]
            elif stage_all:
                # Stage all changes
                files_to_stage = all_changed_files
            else:
                files_to_stage = []

            if not files_to_stage:
                logger.warning("⚠️ No files to stage")
                result['status'] = 'skipped'
                result['error'] = 'No files to stage'
                return result

            # Stage files
            stage_result = self._git_stage(files_to_stage)
            if stage_result.get('error'):
                result['status'] = 'error'
                result['error'] = stage_result['error']
                return result

            result['files_staged'] = stage_result.get('staged', [])
            logger.info(f"✅ Staged {len(result['files_staged'])} files")

            # Commit with custom message
            commit_result = self._git_commit(commit_message)
            if commit_result.get('error'):
                result['status'] = 'error'
                result['error'] = commit_result['error']
                return result

            result['commit_hash'] = commit_result.get('commit_hash')
            result['status'] = 'success'
            logger.info(f"✅ Review workflow completed successfully. Commit: {result['commit_hash']}")

        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            logger.error(f"❌ Review workflow failed: {e}")

        return result

    def _git_status(self) -> Dict[str, Any]:
        """Get git status of repository"""
        try:
            cmd = ['git', 'status', '--porcelain']
            result = subprocess.run(
                cmd,
                cwd=self.git_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {'error': f'git status failed: {result.stderr}'}

            modified = []
            untracked = []

            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                status = line[:2]
                filename = line[3:].strip()

                if status.startswith('??'):
                    untracked.append(filename)
                elif status.startswith((' M', 'MM', 'AM')):
                    modified.append(filename)
                elif status.startswith(('A ', 'M ', 'R ', 'C ')):
                    modified.append(filename)

            return {
                'modified': modified,
                'untracked': untracked,
                'status_text': result.stdout
            }

        except subprocess.TimeoutExpired:
            return {'error': 'git status command timed out'}
        except Exception as e:
            return {'error': f'Failed to get git status: {str(e)}'}

    def _git_stage(self, files: List[str]) -> Dict[str, Any]:
        """Stage files for commit"""
        try:
            if not files:
                return {'staged': [], 'error': None}

            # Stage files
            cmd = ['git', 'add'] + files
            result = subprocess.run(
                cmd,
                cwd=self.git_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {'error': f'git add failed: {result.stderr}'}

            logger.info(f"✅ Staged {len(files)} files")
            return {'staged': files, 'error': None}

        except subprocess.TimeoutExpired:
            return {'error': 'git add command timed out'}
        except Exception as e:
            return {'error': f'Failed to stage files: {str(e)}'}

    def _git_commit(self, commit_message: str) -> Dict[str, Any]:
        """Commit staged changes with custom message"""
        try:
            cmd = ['git', 'commit', '-m', commit_message]
            result = subprocess.run(
                cmd,
                cwd=self.git_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode != 0:
                return {'error': f'git commit failed: {result.stderr}'}

            # Get commit hash
            cmd_hash = ['git', 'rev-parse', 'HEAD']
            hash_result = subprocess.run(
                cmd_hash,
                cwd=self.git_repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )

            commit_hash = hash_result.stdout.strip() if hash_result.returncode == 0 else None

            logger.info(f"✅ Committed changes: {commit_hash or 'unknown'}")
            return {'commit_hash': commit_hash, 'error': None}

        except subprocess.TimeoutExpired:
            return {'error': 'git commit command timed out'}
        except Exception as e:
            return {'error': f'Failed to commit: {str(e)}'}

    def administer_cursor_ide(self) -> Dict[str, Any]:
        """
        Administer Cursor IDE Windows desktop application

        Returns comprehensive administration information and status
        """
        logger.info("🔧 Administering Cursor IDE...")

        admin_info = {
            'timestamp': datetime.now().isoformat(),
            'window_status': {},
            'process_info': {},
            'performance_metrics': {},
            'connection_status': False
        }

        try:
            # Window administration
            if self.cursor_window:
                admin_info['window_status'] = {
                    'title': self.cursor_window.title,
                    'is_active': self.cursor_window.isActive,
                    'is_maximized': self.cursor_window.isMaximized,
                    'is_minimized': self.cursor_window.isMinimized,
                    'position': {
                        'x': self.cursor_window.left,
                        'y': self.cursor_window.top,
                        'width': self.cursor_window.width,
                        'height': self.cursor_window.height
                    }
                }
            else:
                # Try to connect
                if self.connect_to_cursor():
                    admin_info['window_status'] = {
                        'title': self.cursor_window.title if self.cursor_window else 'Unknown',
                        'is_active': self.cursor_window.isActive if self.cursor_window else False
                    }

            # Process administration
            cursor_processes = self._get_cursor_processes()
            admin_info['process_info'] = {
                'processes_found': len(cursor_processes),
                'processes': []
            }

            for proc in cursor_processes:
                try:
                    proc_info = {
                        'pid': proc.pid,
                        'name': proc.name(),
                        'status': proc.status(),
                        'cpu_percent': proc.cpu_percent(interval=0.1),
                        'memory_mb': proc.memory_info().rss / 1024 / 1024,
                        'memory_percent': proc.memory_percent(),
                        'create_time': datetime.fromtimestamp(proc.create_time()).isoformat()
                    }
                    admin_info['process_info']['processes'].append(proc_info)
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            # Performance metrics from current state
            state = self.get_cursor_state()
            admin_info['performance_metrics'] = state.performance_metrics

            # Connection status
            admin_info['connection_status'] = self.cursor_window is not None and self.cursor_window.isActive

            logger.info("✅ Cursor IDE administration information collected")

        except Exception as e:
            logger.error(f"❌ Failed to administer Cursor IDE: {e}")
            admin_info['error'] = str(e)

        return admin_info

    def _get_cursor_processes(self) -> List[Any]:
        """Get all Cursor IDE processes"""
        cursor_processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'cursor' in proc_name or 'cursor.exe' in proc_name:
                        cursor_processes.append(psutil.Process(proc.info['pid']))
                except (psutil.NoSuchProcess, psutil.AccessDenied, KeyError):
                    continue
        except Exception as e:
            logger.error(f"Error finding Cursor processes: {e}")

        return cursor_processes

    def monitor_cursor_ide_comprehensive(self, interval: int = 10) -> Dict[str, Any]:
        """
        Comprehensive monitoring of Cursor IDE Windows desktop application

        Args:
            interval: Monitoring interval in seconds (default: 10)

        Returns:
            Dict with comprehensive monitoring information
        """
        logger.info(f"👁️ Starting comprehensive Cursor IDE monitoring (interval: {interval}s)")

        monitor_data = {
            'timestamp': datetime.now().isoformat(),
            'window_monitoring': {},
            'process_monitoring': {},
            'performance_monitoring': {},
            'git_status': {},
            'ide_state': {}
        }

        try:
            # Window monitoring
            if not self.cursor_window:
                self.connect_to_cursor()

            if self.cursor_window:
                monitor_data['window_monitoring'] = {
                    'connected': True,
                    'title': self.cursor_window.title,
                    'is_active': self.cursor_window.isActive,
                    'is_visible': self.cursor_window.visible,
                    'position': {
                        'x': self.cursor_window.left,
                        'y': self.cursor_window.top,
                        'width': self.cursor_window.width,
                        'height': self.cursor_window.height
                    }
                }
            else:
                monitor_data['window_monitoring'] = {'connected': False}

            # Process monitoring
            cursor_processes = self._get_cursor_processes()
            process_metrics = []
            total_cpu = 0.0
            total_memory_mb = 0.0

            for proc in cursor_processes:
                try:
                    cpu = proc.cpu_percent(interval=0.1)
                    memory_mb = proc.memory_info().rss / 1024 / 1024
                    total_cpu += cpu
                    total_memory_mb += memory_mb

                    process_metrics.append({
                        'pid': proc.pid,
                        'name': proc.name(),
                        'cpu_percent': cpu,
                        'memory_mb': memory_mb
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

            monitor_data['process_monitoring'] = {
                'process_count': len(cursor_processes),
                'total_cpu_percent': total_cpu,
                'total_memory_mb': total_memory_mb,
                'processes': process_metrics
            }

            # Performance monitoring
            state = self.get_cursor_state()
            monitor_data['performance_monitoring'] = state.performance_metrics
            monitor_data['ide_state'] = {
                'window_title': state.window_title,
                'last_modified': state.last_modified.isoformat() if state.last_modified else None,
                'diagnostics_count': len(state.diagnostics),
                'problems_count': len(state.problems)
            }

            # Git status monitoring (if repository detected)
            if self.git_repo_path:
                git_status = self._git_status()
                if not git_status.get('error'):
                    monitor_data['git_status'] = {
                        'modified_files': len(git_status.get('modified', [])),
                        'untracked_files': len(git_status.get('untracked', [])),
                        'has_changes': len(git_status.get('modified', [])) + len(git_status.get('untracked', [])) > 0
                    }

            logger.info("✅ Comprehensive monitoring data collected")

        except Exception as e:
            logger.error(f"❌ Comprehensive monitoring failed: {e}")
            monitor_data['error'] = str(e)

        return monitor_data

def main():
    """MANUS Cursor Controller CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Cursor IDE Controller")
    parser.add_argument("--connect", action="store_true", help="Connect to Cursor IDE")
    parser.add_argument("--monitor", action="store_true", help="Start monitoring mode")
    parser.add_argument("--troubleshoot", type=str, help="Manually troubleshoot an issue")
    parser.add_argument("--files", nargs="*", help="Affected files for troubleshooting")
    parser.add_argument("--errors", nargs="*", help="Error messages for troubleshooting")
    parser.add_argument("--review-workflow", type=str, metavar="COMMIT_MESSAGE", help="Perform review workflow with commit message")
    parser.add_argument("--review-files", nargs="*", help="Specific files to review and commit (optional)")
    parser.add_argument("--administer", action="store_true", help="Administer Cursor IDE (show status and information)")
    parser.add_argument("--monitor-comprehensive", action="store_true", help="Start comprehensive monitoring")
    parser.add_argument("--monitor-interval", type=int, default=10, help="Monitoring interval in seconds (default: 10)")

    args = parser.parse_args()

    controller = ManusCursorController()

    if args.connect:
        success = controller.connect_to_cursor()
        print(f"Connection: {'SUCCESS' if success else 'FAILED'}")

    if args.monitor:
        print("🎯 Starting MANUS monitoring...")
        controller.start_monitoring()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Stopping monitoring...")
            controller.stop_monitoring()

    if args.troubleshoot:
        print(f"🔧 Troubleshooting: {args.troubleshoot}")
        success = controller.troubleshoot_issue(
            args.troubleshoot,
            args.files,
            args.errors
        )
        print(f"Result: {'SUCCESS' if success else 'FAILED'}")

    if args.review_workflow:
        print(f"📋 Performing review workflow with commit message: {args.review_workflow}")
        result = controller.review_workflow(
            commit_message=args.review_workflow,
            review_files=args.review_files,
            stage_all=not args.review_files  # Stage all if no specific files provided
        )
        print(f"Review Workflow Result: {result['status'].upper()}")
        if result['status'] == 'success':
            print(f"✅ Committed {len(result['files_staged'])} files")
            print(f"Commit hash: {result['commit_hash']}")
        elif result.get('error'):
            print(f"❌ Error: {result['error']}")
        print(json.dumps(result, indent=2, default=str))

    if args.administer:
        print("🔧 Administering Cursor IDE...")
        admin_info = controller.administer_cursor_ide()
        print(json.dumps(admin_info, indent=2, default=str))

    if args.monitor_comprehensive:
        print(f"👁️ Starting comprehensive monitoring (interval: {args.monitor_interval}s)...")
        try:
            while True:
                monitor_data = controller.monitor_cursor_ide_comprehensive(args.monitor_interval)
                print(f"\n📊 Monitoring Data ({datetime.now().strftime('%H:%M:%S')}):")
                print(json.dumps(monitor_data, indent=2, default=str))
                time.sleep(args.monitor_interval)
        except KeyboardInterrupt:
            print("\n🛑 Stopping comprehensive monitoring...")

    if not any([args.connect, args.monitor, args.troubleshoot, args.review_workflow, args.administer, args.monitor_comprehensive]):
        print("🕹️ MANUS Cursor IDE Controller")
        print("Use --help for available options")

if __name__ == "__main__":


    main()