#!/usr/bin/env python3
"""
Workflow Scope Selector
<COMPANY_NAME> LLC

Selects optimal scope for operations:
- Local scope
- Worktree scope
- Cloud scope
- Workspace scope
- Non-workspace scope

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from workflow_scope_context_analyzer import OperationContext

logger = get_logger("WorkflowScopeSelector")


class Scope(Enum):
    """Operation scopes"""
    LOCAL = "local"
    WORKTREE = "worktree"
    CLOUD = "cloud"
    WORKSPACE = "workspace"
    NON_WORKSPACE = "non_workspace"


@dataclass
class ScopeSelection:
    """Scope selection result"""
    scope: Scope
    reason: str
    confidence: float
    fallback_scope: Optional[Scope] = None
    fallback_reason: Optional[str] = None


class WorkflowScopeSelector:
    """Select optimal scope for operation"""

    def __init__(self):
        """Initialize scope selector"""
        self.logger = logger
        self.logger.info("✅ Workflow Scope Selector initialized")

    def select(self, context: OperationContext) -> ScopeSelection:
        """
        Select scope based on context

        Priority order:
        1. Explicitly requested scope
        2. Workspace (if required and available)
        3. Worktree (if git required and available)
        4. Cloud (if required and available)
        5. Non-workspace (if simple operation)
        6. Local (default fallback)
        """
        self.logger.info("🔍 Selecting optimal scope...")

        # Check for explicitly requested scope
        if context.requested_scope:
            try:
                scope = Scope(context.requested_scope)
                self.logger.info(f"✅ Using requested scope: {scope.value}")
                return ScopeSelection(
                    scope=scope,
                    reason=f"Explicitly requested: {context.requested_scope}",
                    confidence=1.0
                )
            except ValueError:
                self.logger.warning(f"Invalid requested scope: {context.requested_scope}")

        # Priority 1: Workspace (if required and available)
        if context.requires_workspace and context.has_workspace:
            self.logger.info("✅ Selected: WORKSPACE (required and available)")
            return ScopeSelection(
                scope=Scope.WORKSPACE,
                reason="Workspace required for multi-file/project operations",
                confidence=0.95,
                fallback_scope=Scope.NON_WORKSPACE,
                fallback_reason="Fallback to non-workspace if workspace unavailable"
            )

        # Priority 2: Worktree (if git required and available)
        if context.requires_git and context.has_worktree:
            self.logger.info("✅ Selected: WORKTREE (git required and available)")
            return ScopeSelection(
                scope=Scope.WORKTREE,
                reason="Worktree required for git operations",
                confidence=0.90,
                fallback_scope=Scope.LOCAL,
                fallback_reason="Fallback to local if worktree unavailable"
            )

        # Priority 3: Cloud (if required and available)
        if context.requires_cloud and context.resource_availability.cloud_available:
            self.logger.info("✅ Selected: CLOUD (required and available)")
            return ScopeSelection(
                scope=Scope.CLOUD,
                reason="Cloud required for collaboration/remote operations",
                confidence=0.85,
                fallback_scope=Scope.LOCAL,
                fallback_reason="Fallback to local if cloud unavailable"
            )

        # Priority 4: Non-workspace (if simple operation and workspace not required)
        if context.is_simple_operation and not context.requires_workspace:
            self.logger.info("✅ Selected: NON-WORKSPACE (simple operation)")
            return ScopeSelection(
                scope=Scope.NON_WORKSPACE,
                reason="Simple operation, workspace not required",
                confidence=0.80,
                fallback_scope=Scope.LOCAL,
                fallback_reason="Fallback to local if non-workspace unavailable"
            )

        # Priority 5: Workspace (if available, even if not strictly required)
        if context.has_workspace and not context.is_simple_operation:
            self.logger.info("✅ Selected: WORKSPACE (available, operation benefits from it)")
            return ScopeSelection(
                scope=Scope.WORKSPACE,
                reason="Workspace available and operation benefits from full context",
                confidence=0.75,
                fallback_scope=Scope.NON_WORKSPACE,
                fallback_reason="Fallback to non-workspace if workspace unavailable"
            )

        # Priority 6: Worktree (if available, even if not strictly required)
        if context.has_worktree and context.git_status.has_git:
            self.logger.info("✅ Selected: WORKTREE (available, git operations possible)")
            return ScopeSelection(
                scope=Scope.WORKTREE,
                reason="Worktree available and git operations possible",
                confidence=0.70,
                fallback_scope=Scope.LOCAL,
                fallback_reason="Fallback to local if worktree unavailable"
            )

        # Default: Local
        self.logger.info("✅ Selected: LOCAL (default fallback)")
        return ScopeSelection(
            scope=Scope.LOCAL,
            reason="Default fallback - local operations",
            confidence=0.60
        )

    def validate(self, scope: Scope, context: OperationContext) -> tuple[bool, Optional[str]]:
        """Validate scope selection"""

        # Check if scope is available
        if scope == Scope.WORKSPACE and not context.has_workspace:
            return False, "Workspace not available"

        if scope == Scope.WORKTREE and not context.has_worktree:
            return False, "Worktree not available"

        if scope == Scope.CLOUD and not context.resource_availability.cloud_available:
            return False, "Cloud not available"

        # Check if scope matches requirements
        if context.requires_workspace and scope not in [Scope.WORKSPACE]:
            return False, f"Scope {scope.value} does not meet workspace requirement"

        if context.requires_git and scope not in [Scope.WORKTREE, Scope.WORKSPACE]:
            return False, f"Scope {scope.value} does not meet git requirement"

        if context.requires_cloud and scope != Scope.CLOUD:
            return False, f"Scope {scope.value} does not meet cloud requirement"

        # Check invalid combinations
        if scope == Scope.NON_WORKSPACE and context.requires_workspace:
            return False, "Non-workspace cannot meet workspace requirement"

        if scope == Scope.LOCAL and context.requires_cloud:
            return False, "Local cannot meet cloud requirement"

        return True, None


if __name__ == "__main__":
    import argparse
    from workflow_scope_context_analyzer import WorkflowScopeContextAnalyzer

    parser = argparse.ArgumentParser(description="Workflow Scope Selector")
    parser.add_argument("request", help="User request/operation description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Analyze context
    analyzer = WorkflowScopeContextAnalyzer()
    context = analyzer.analyze(args.request)

    # Select scope
    selector = WorkflowScopeSelector()
    selection = selector.select(context)

    # Validate
    is_valid, error = selector.validate(selection.scope, context)

    if args.json:
        import json
        result = {
            "scope": selection.scope.value,
            "reason": selection.reason,
            "confidence": selection.confidence,
            "valid": is_valid,
            "error": error
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\n🎯 Scope Selection:")
        print(f"   Scope: {selection.scope.value}")
        print(f"   Reason: {selection.reason}")
        print(f"   Confidence: {selection.confidence:.2f}")
        print(f"   Valid: {is_valid}")
        if error:
            print(f"   Error: {error}")

