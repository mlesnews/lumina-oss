#!/usr/bin/env python3
"""
Workflow Scope & Mode Orchestrator
<COMPANY_NAME> LLC

Orchestrates scope and mode selection for operations:
- Analyzes context
- Selects optimal scope
- Selects optimal mode
- Validates combinations
- Executes with selected scope/mode

@JARVIS @MARVIN @SYPHON
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from workflow_scope_context_analyzer import WorkflowScopeContextAnalyzer, OperationContext
from workflow_scope_selector import WorkflowScopeSelector, Scope, ScopeSelection
from workflow_mode_selector import WorkflowModeSelector, Mode, ModeSelection

logger = get_logger("WorkflowScopeModeOrchestrator")


@dataclass
class OrchestrationResult:
    """Complete orchestration result"""
    scope: Scope
    mode: Mode
    scope_reason: str
    mode_reason: str
    confidence: float
    valid: bool
    error: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "scope": self.scope.value,
            "mode": self.mode.value,
            "scope_reason": self.scope_reason,
            "mode_reason": self.mode_reason,
            "confidence": self.confidence,
            "valid": self.valid,
            "error": self.error,
            "context": self.context
        }


class WorkflowScopeModeOrchestrator:
    """Orchestrate scope and mode selection"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize orchestrator"""
        self.project_root = project_root or Path.cwd()
        self.logger = logger

        # Initialize components
        self.context_analyzer = WorkflowScopeContextAnalyzer(self.project_root)
        self.scope_selector = WorkflowScopeSelector()
        self.mode_selector = WorkflowModeSelector()

        self.logger.info("✅ Workflow Scope & Mode Orchestrator initialized")

    def orchestrate(self, request: str, current_state: Optional[Dict[str, Any]] = None) -> OrchestrationResult:
        """
        Orchestrate scope and mode selection

        Args:
            request: User request/operation description
            current_state: Current system state (optional)

        Returns:
            OrchestrationResult with selected scope and mode
        """
        self.logger.info(f"🎯 Orchestrating scope/mode selection for: {request[:100]}...")

        # Step 1: Analyze context
        context = self.context_analyzer.analyze(request, current_state)
        self.logger.info(f"   Context analyzed: {context.task_type.value}, complexity: {context.complexity.value}")

        # Step 2: Select scope
        scope_selection = self.scope_selector.select(context)
        self.logger.info(f"   Scope selected: {scope_selection.scope.value} (confidence: {scope_selection.confidence:.2f})")

        # Step 3: Select mode
        mode_selection = self.mode_selector.select(context, scope_selection.scope)
        self.logger.info(f"   Mode selected: {mode_selection.mode.value} (confidence: {mode_selection.confidence:.2f})")

        # Step 4: Validate combination
        is_valid, error = self.mode_selector.validate(mode_selection.mode, scope_selection.scope, context)

        # Calculate overall confidence
        confidence = (scope_selection.confidence + mode_selection.confidence) / 2

        # Build result
        result = OrchestrationResult(
            scope=scope_selection.scope,
            mode=mode_selection.mode,
            scope_reason=scope_selection.reason,
            mode_reason=mode_selection.reason,
            confidence=confidence,
            valid=is_valid,
            error=error,
            context={
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
        )

        if is_valid:
            self.logger.info(f"✅ Orchestration complete: {scope_selection.scope.value} + {mode_selection.mode.value} (confidence: {confidence:.2f})")
        else:
            self.logger.warning(f"⚠️  Orchestration complete but invalid: {error}")

        return result

    def get_recommendation(self, request: str, current_state: Optional[Dict[str, Any]] = None) -> str:
        """
        Get human-readable recommendation

        Args:
            request: User request/operation description
            current_state: Current system state (optional)

        Returns:
            Human-readable recommendation string
        """
        result = self.orchestrate(request, current_state)

        recommendation = f"""
🎯 Scope & Mode Recommendation

Request: {request[:100]}{'...' if len(request) > 100 else ''}

Selected:
  Scope: {result.scope.value}
  Mode: {result.mode.value}

Reasoning:
  Scope: {result.scope_reason}
  Mode: {result.mode_reason}

Confidence: {result.confidence:.2f}
Valid: {result.valid}
"""

        if result.error:
            recommendation += f"\n⚠️  Warning: {result.error}\n"

        if result.context:
            recommendation += f"\nContext:\n"
            for key, value in result.context.items():
                recommendation += f"  {key}: {value}\n"

        return recommendation


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Workflow Scope & Mode Orchestrator")
    parser.add_argument("request", help="User request/operation description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--recommendation", action="store_true", help="Output human-readable recommendation")

    args = parser.parse_args()

    orchestrator = WorkflowScopeModeOrchestrator()

    if args.recommendation:
        recommendation = orchestrator.get_recommendation(args.request)
        print(recommendation)
    else:
        result = orchestrator.orchestrate(args.request)

        if args.json:
            print(json.dumps(result.to_dict(), indent=2))
        else:
            print(f"\n🎯 Orchestration Result:")
            print(f"   Scope: {result.scope.value}")
            print(f"   Mode: {result.mode.value}")
            print(f"   Scope Reason: {result.scope_reason}")
            print(f"   Mode Reason: {result.mode_reason}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Valid: {result.valid}")
            if result.error:
                print(f"   Error: {result.error}")

