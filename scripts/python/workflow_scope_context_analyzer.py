#!/usr/bin/env python3
"""
Workflow Scope Context Analyzer
<COMPANY_NAME> LLC

Analyzes operation context to determine optimal scope and mode selection:
- Task type classification
- File structure analysis
- Git status analysis
- Resource availability checking
- User intent detection

@JARVIS @MARVIN @SYPHON
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("WorkflowScopeContextAnalyzer")


class TaskType(Enum):
    """Task type classification"""
    SINGLE_FILE = "single_file"
    MULTI_FILE = "multi_file"
    PROJECT_LEVEL = "project_level"
    GIT_OPERATION = "git_operation"
    WORKFLOW = "workflow"
    QUICK_EDIT = "quick_edit"
    COMPLEX_REFACTORING = "complex_refactoring"
    UNKNOWN = "unknown"


class OperationComplexity(Enum):
    """Operation complexity"""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"
    VERY_COMPLEX = "very_complex"


@dataclass
class FileStructure:
    """File structure analysis"""
    has_workspace: bool = False
    has_worktree: bool = False
    workspace_path: Optional[Path] = None
    worktree_path: Optional[Path] = None
    open_files: List[Path] = field(default_factory=list)
    file_count: int = 0
    is_single_file: bool = False
    is_multi_file: bool = False
    has_git: bool = False
    git_root: Optional[Path] = None


@dataclass
class GitStatus:
    """Git status analysis"""
    has_git: bool = False
    is_worktree: bool = False
    worktree_count: int = 0
    current_branch: Optional[str] = None
    has_uncommitted_changes: bool = False
    modified_files: List[str] = field(default_factory=list)
    untracked_files: List[str] = field(default_factory=list)


@dataclass
class ResourceAvailability:
    """Resource availability"""
    local_available: bool = True
    worktree_available: bool = False
    cloud_available: bool = False
    workspace_available: bool = False
    network_available: bool = True


@dataclass
class OperationContext:
    """Complete operation context"""
    # Task classification
    task_type: TaskType = TaskType.UNKNOWN
    complexity: OperationComplexity = OperationComplexity.MEDIUM

    # File structure
    file_structure: FileStructure = field(default_factory=FileStructure)

    # Git status
    git_status: GitStatus = field(default_factory=GitStatus)

    # Resource availability
    resource_availability: ResourceAvailability = field(default_factory=ResourceAvailability)

    # User intent
    user_intent: str = ""
    requested_scope: Optional[str] = None
    requested_mode: Optional[str] = None

    # Derived flags
    has_workspace: bool = False
    has_worktree: bool = False
    requires_workspace: bool = False
    requires_git: bool = False
    requires_cloud: bool = False
    is_complex_workflow: bool = False
    is_simple_task: bool = False
    can_auto_execute: bool = False
    requires_independence: bool = False
    is_recurring: bool = False
    is_simple_operation: bool = False

    # Metadata
    analyzed_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0


class WorkflowScopeContextAnalyzer:
    """Analyze context for scope/mode selection"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize analyzer"""
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = Path(project_root)
        self.logger = logger

        self.logger.info("✅ Workflow Scope Context Analyzer initialized")

    def analyze(self, request: str, current_state: Optional[Dict[str, Any]] = None) -> OperationContext:
        """
        Analyze operation context

        Args:
            request: User request/operation description
            current_state: Current system state (optional)

        Returns:
            OperationContext with complete analysis
        """
        self.logger.info(f"🔍 Analyzing context for: {request[:100]}...")

        # Analyze file structure
        file_structure = self._analyze_file_structure()

        # Analyze git status
        git_status = self._analyze_git_status()

        # Check resource availability
        resource_availability = self._check_resources()

        # Classify task type
        task_type = self._classify_task_type(request, file_structure, git_status)

        # Assess complexity
        complexity = self._assess_complexity(request, task_type)

        # Detect user intent
        user_intent = self._detect_intent(request)

        # Extract requested scope/mode
        requested_scope, requested_mode = self._extract_requested_scope_mode(request)

        # Build context
        context = OperationContext(
            task_type=task_type,
            complexity=complexity,
            file_structure=file_structure,
            git_status=git_status,
            resource_availability=resource_availability,
            user_intent=user_intent,
            requested_scope=requested_scope,
            requested_mode=requested_mode,
            has_workspace=file_structure.has_workspace,
            has_worktree=file_structure.has_worktree or git_status.is_worktree,
            requires_workspace=self._requires_workspace(request, task_type, file_structure),
            requires_git=self._requires_git(request, task_type, git_status),
            requires_cloud=self._requires_cloud(request, resource_availability),
            is_complex_workflow=self._is_complex_workflow(request, task_type, complexity),
            is_simple_task=self._is_simple_task(request, task_type, complexity),
            can_auto_execute=self._can_auto_execute(request, task_type, complexity),
            requires_independence=self._requires_independence(request, task_type),
            is_recurring=self._is_recurring(request, current_state),
            is_simple_operation=self._is_simple_operation(request, task_type, complexity)
        )

        # Calculate confidence
        context.confidence = self._calculate_confidence(context)

        self.logger.info(f"✅ Context analyzed: {task_type.value}, complexity: {complexity.value}, confidence: {context.confidence:.2f}")

        return context

    def _analyze_file_structure(self) -> FileStructure:
        """Analyze file structure"""
        structure = FileStructure()

        # Check for workspace indicators
        workspace_indicators = [
            self.project_root / ".cursor",
            self.project_root / ".vscode",
            self.project_root / "workspace",
        ]

        structure.has_workspace = any(indicator.exists() for indicator in workspace_indicators)
        if structure.has_workspace:
            structure.workspace_path = self.project_root

        # Check for worktree
        worktree_indicators = [
            self.project_root.parent / ".git" / "worktrees",
            Path.home() / ".cursor" / "worktrees",
        ]

        for indicator in worktree_indicators:
            if indicator.exists():
                structure.has_worktree = True
                structure.worktree_path = indicator
                break

        # Check for git
        git_path = self.project_root / ".git"
        if git_path.exists():
            structure.has_git = True
            structure.git_root = self.project_root
        else:
            # Check parent directories
            for parent in self.project_root.parents:
                git_path = parent / ".git"
                if git_path.exists():
                    structure.has_git = True
                    structure.git_root = parent
                    break

        # Count files (simplified - just check if directory has many files)
        if self.project_root.is_dir():
            try:
                file_count = sum(1 for _ in self.project_root.rglob("*") if _.is_file())
                structure.file_count = file_count
                structure.is_single_file = file_count == 1
                structure.is_multi_file = file_count > 1
            except Exception:
                pass

        return structure

    def _analyze_git_status(self) -> GitStatus:
        """Analyze git status"""
        status = GitStatus()

        # Check if git is available
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                status.has_git = True

                # Check if worktree - linked worktrees have .git as a file (gitdir pointer)
                # not a directory. Regular repos have .git as a directory.
                git_path = self.project_root / ".git"
                if git_path.exists() and git_path.is_file():
                    # This is a linked worktree - .git is a file containing gitdir pointer
                    status.is_worktree = True
                else:
                    # Regular repository - .git is a directory
                    status.is_worktree = False

                # Get current branch
                result = subprocess.run(
                    ["git", "branch", "--show-current"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    status.current_branch = result.stdout.strip()

                # Check for uncommitted changes
                result = subprocess.run(
                    ["git", "status", "--porcelain"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    if lines and lines[0]:
                        status.has_uncommitted_changes = True
                        for line in lines:
                            if line.startswith(' M') or line.startswith('M '):
                                status.modified_files.append(line[3:].strip())
                            elif line.startswith('??'):
                                status.untracked_files.append(line[3:].strip())

                # Count worktrees
                result = subprocess.run(
                    ["git", "worktree", "list"],
                    cwd=self.project_root,
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    status.worktree_count = len(result.stdout.strip().split('\n'))

        except Exception as e:
            self.logger.debug(f"Git analysis error: {e}")

        return status

    def _check_resources(self) -> ResourceAvailability:
        """Check resource availability"""
        resources = ResourceAvailability()

        # Local is always available
        resources.local_available = True

        # Check for workspace
        workspace_indicators = [
            self.project_root / ".cursor",
            self.project_root / ".vscode",
        ]
        resources.workspace_available = any(indicator.exists() for indicator in workspace_indicators)

        # Check for worktree
        worktree_indicators = [
            self.project_root.parent / ".git" / "worktrees",
            Path.home() / ".cursor" / "worktrees",
        ]
        resources.worktree_available = any(indicator.exists() for indicator in worktree_indicators)

        # Check network (simplified)
        try:
            result = subprocess.run(
                ["ping", "-n", "1", "8.8.8.8"],
                capture_output=True,
                timeout=2
            )
            resources.network_available = result.returncode == 0
            resources.cloud_available = resources.network_available
        except Exception:
            resources.network_available = False
            resources.cloud_available = False

        return resources

    def _classify_task_type(self, request: str, file_structure: FileStructure, git_status: GitStatus) -> TaskType:
        """Classify task type"""
        request_lower = request.lower()

        # Git operations
        git_keywords = ["git", "commit", "branch", "merge", "push", "pull", "rebase", "stash"]
        if any(keyword in request_lower for keyword in git_keywords):
            return TaskType.GIT_OPERATION

        # Workflow operations
        workflow_keywords = ["workflow", "pipeline", "process", "steps", "sequence"]
        if any(keyword in request_lower for keyword in workflow_keywords):
            return TaskType.WORKFLOW

        # Complex refactoring
        refactoring_keywords = ["refactor", "restructure", "reorganize", "migrate", "convert"]
        if any(keyword in request_lower for keyword in refactoring_keywords):
            return TaskType.COMPLEX_REFACTORING

        # Project-level operations
        project_keywords = ["project", "workspace", "all files", "entire", "whole"]
        if any(keyword in request_lower for keyword in project_keywords):
            return TaskType.PROJECT_LEVEL

        # Multi-file operations
        multi_file_keywords = ["multiple", "several", "all", "batch", "bulk"]
        if any(keyword in request_lower for keyword in multi_file_keywords):
            return TaskType.MULTI_FILE

        # Quick edits
        quick_keywords = ["quick", "simple", "fix", "update", "change"]
        if any(keyword in request_lower for keyword in quick_keywords) and file_structure.is_single_file:
            return TaskType.QUICK_EDIT

        # Default based on file structure
        if file_structure.is_single_file:
            return TaskType.SINGLE_FILE
        elif file_structure.is_multi_file:
            return TaskType.MULTI_FILE
        else:
            return TaskType.UNKNOWN

    def _assess_complexity(self, request: str, task_type: TaskType) -> OperationComplexity:
        """Assess operation complexity"""
        request_lower = request.lower()

        # Very complex indicators
        very_complex_keywords = ["refactor", "migrate", "restructure", "reorganize", "complex", "multiple steps"]
        if any(keyword in request_lower for keyword in very_complex_keywords):
            return OperationComplexity.VERY_COMPLEX

        # Complex indicators
        complex_keywords = ["workflow", "pipeline", "process", "multiple", "batch"]
        if any(keyword in request_lower for keyword in complex_keywords):
            return OperationComplexity.COMPLEX

        # Simple indicators
        simple_keywords = ["quick", "simple", "fix", "update", "change", "edit"]
        if any(keyword in request_lower for keyword in simple_keywords):
            return OperationComplexity.SIMPLE

        # Default based on task type
        if task_type in [TaskType.QUICK_EDIT, TaskType.SINGLE_FILE]:
            return OperationComplexity.SIMPLE
        elif task_type in [TaskType.COMPLEX_REFACTORING, TaskType.WORKFLOW]:
            return OperationComplexity.COMPLEX
        else:
            return OperationComplexity.MEDIUM

    def _detect_intent(self, request: str) -> str:
        """Detect user intent"""
        request_lower = request.lower()

        intents = []

        if "fix" in request_lower or "error" in request_lower:
            intents.append("fix")
        if "create" in request_lower or "new" in request_lower:
            intents.append("create")
        if "update" in request_lower or "modify" in request_lower:
            intents.append("update")
        if "delete" in request_lower or "remove" in request_lower:
            intents.append("delete")
        if "analyze" in request_lower or "check" in request_lower:
            intents.append("analyze")
        if "optimize" in request_lower or "improve" in request_lower:
            intents.append("optimize")

        return ", ".join(intents) if intents else "general"

    def _extract_requested_scope_mode(self, request: str) -> tuple[Optional[str], Optional[str]]:
        """Extract requested scope and mode from request"""
        request_lower = request.lower()

        scope = None
        mode = None

        # Extract scope
        if "@local" in request_lower or "#local" in request_lower:
            scope = "local"
        elif "@worktree" in request_lower or "#worktree" in request_lower:
            scope = "worktree"
        elif "@cloud" in request_lower or "#cloud" in request_lower:
            scope = "cloud"
        elif "@workspace" in request_lower or "#workspace" in request_lower:
            scope = "workspace"
        elif "@non-workspace" in request_lower or "#non-workspace" in request_lower:
            scope = "non-workspace"

        # Extract mode
        if "@flow" in request_lower or "#flow" in request_lower:
            mode = "flow"
        elif "@auto" in request_lower or "#auto" in request_lower:
            if "#automatic" in request_lower:
                mode = "auto_automatic"
            elif "#autonomous" in request_lower:
                mode = "auto_autonomous"
            elif "#automation" in request_lower:
                mode = "auto_automation"
            else:
                mode = "auto"  # Generic auto

        return scope, mode

    def _requires_workspace(self, request: str, task_type: TaskType, file_structure: FileStructure) -> bool:
        """Determine if workspace is required"""
        if task_type in [TaskType.PROJECT_LEVEL, TaskType.COMPLEX_REFACTORING, TaskType.MULTI_FILE]:
            return True

        if task_type == TaskType.WORKFLOW:
            return True

        request_lower = request.lower()
        if any(keyword in request_lower for keyword in ["workspace", "project", "all files", "entire"]):
            return True

        return False

    def _requires_git(self, request: str, task_type: TaskType, git_status: GitStatus) -> bool:
        """Determine if git is required"""
        if task_type == TaskType.GIT_OPERATION:
            return True

        request_lower = request.lower()
        git_keywords = ["git", "commit", "branch", "merge", "push", "pull"]
        if any(keyword in request_lower for keyword in git_keywords):
            return True

        return False

    def _requires_cloud(self, request: str, resource_availability: ResourceAvailability) -> bool:
        """Determine if cloud is required"""
        request_lower = request.lower()

        cloud_keywords = ["cloud", "remote", "sync", "collaborate", "share"]
        if any(keyword in request_lower for keyword in cloud_keywords):
            return True

        # If network not available, can't use cloud
        if not resource_availability.network_available:
            return False

        return False

    def _is_complex_workflow(self, request: str, task_type: TaskType, complexity: OperationComplexity) -> bool:
        """Determine if this is a complex workflow"""
        if task_type == TaskType.WORKFLOW:
            return True

        if complexity in [OperationComplexity.COMPLEX, OperationComplexity.VERY_COMPLEX]:
            return True

        request_lower = request.lower()
        if "workflow" in request_lower or "pipeline" in request_lower or "steps" in request_lower:
            return True

        return False

    def _is_simple_task(self, request: str, task_type: TaskType, complexity: OperationComplexity) -> bool:
        """Determine if this is a simple task"""
        if task_type in [TaskType.QUICK_EDIT, TaskType.SINGLE_FILE]:
            return True

        if complexity == OperationComplexity.SIMPLE:
            return True

        return False

    def _can_auto_execute(self, request: str, task_type: TaskType, complexity: OperationComplexity) -> bool:
        """Determine if task can be auto-executed"""
        if complexity == OperationComplexity.SIMPLE and task_type in [TaskType.QUICK_EDIT, TaskType.SINGLE_FILE]:
            return True

        request_lower = request.lower()
        if "auto" in request_lower or "automatic" in request_lower:
            return True

        return False

    def _requires_independence(self, request: str, task_type: TaskType) -> bool:
        """Determine if task requires independence"""
        request_lower = request.lower()

        independent_keywords = ["autonomous", "independent", "self", "learn", "adapt"]
        if any(keyword in request_lower for keyword in independent_keywords):
            return True

        return False

    def _is_recurring(self, request: str, current_state: Optional[Dict[str, Any]]) -> bool:
        """Determine if task is recurring"""
        request_lower = request.lower()

        recurring_keywords = ["schedule", "recurring", "periodic", "cron", "automated"]
        if any(keyword in request_lower for keyword in recurring_keywords):
            return True

        # Check current state for recurring patterns
        if current_state and current_state.get("is_recurring", False):
            return True

        return False

    def _is_simple_operation(self, request: str, task_type: TaskType, complexity: OperationComplexity) -> bool:
        """Determine if this is a simple operation"""
        return self._is_simple_task(request, task_type, complexity) and not self._requires_workspace(request, task_type, FileStructure())

    def _calculate_confidence(self, context: OperationContext) -> float:
        """Calculate confidence score"""
        confidence = 0.5  # Base confidence

        # Increase confidence based on clear indicators
        if context.task_type != TaskType.UNKNOWN:
            confidence += 0.2

        if context.complexity != OperationComplexity.MEDIUM:
            confidence += 0.1

        if context.requested_scope or context.requested_mode:
            confidence += 0.1

        if context.has_workspace or context.has_worktree:
            confidence += 0.1

        # Cap at 1.0
        return min(confidence, 1.0)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Scope Context Analyzer")
    parser.add_argument("request", help="User request/operation description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    analyzer = WorkflowScopeContextAnalyzer()
    context = analyzer.analyze(args.request)

    if args.json:
        # Convert to dict for JSON output
        context_dict = {
            "task_type": context.task_type.value,
            "complexity": context.complexity.value,
            "has_workspace": context.has_workspace,
            "has_worktree": context.has_worktree,
            "requires_workspace": context.requires_workspace,
            "requires_git": context.requires_git,
            "requires_cloud": context.requires_cloud,
            "is_complex_workflow": context.is_complex_workflow,
            "is_simple_task": context.is_simple_task,
            "can_auto_execute": context.can_auto_execute,
            "confidence": context.confidence
        }
        print(json.dumps(context_dict, indent=2))
    else:
        print(f"\n📊 Context Analysis Results:")
        print(f"   Task Type: {context.task_type.value}")
        print(f"   Complexity: {context.complexity.value}")
        print(f"   Has Workspace: {context.has_workspace}")
        print(f"   Has Worktree: {context.has_worktree}")
        print(f"   Requires Workspace: {context.requires_workspace}")
        print(f"   Requires Git: {context.requires_git}")
        print(f"   Requires Cloud: {context.requires_cloud}")
        print(f"   Is Complex Workflow: {context.is_complex_workflow}")
        print(f"   Is Simple Task: {context.is_simple_task}")
        print(f"   Can Auto-Execute: {context.can_auto_execute}")
        print(f"   Confidence: {context.confidence:.2f}")

