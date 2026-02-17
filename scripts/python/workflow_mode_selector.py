#!/usr/bin/env python3
"""
Workflow Mode Selector
<COMPANY_NAME> LLC

Selects optimal mode for operations:
- @flow mode (workflow orchestration)
- @auto[#automatic] (auto-execute)
- @auto[#autonomous] (self-directed)
- @auto[#automation] (automated workflows)

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
from workflow_scope_selector import Scope

logger = get_logger("WorkflowModeSelector")


class Mode(Enum):
    """Operation modes"""
    FLOW = "flow"
    AUTO_AUTOMATIC = "auto_automatic"
    AUTO_AUTONOMOUS = "auto_autonomous"
    AUTO_AUTOMATION = "auto_automation"
    MANUAL = "manual"


@dataclass
class ModeSelection:
    """Mode selection result"""
    mode: Mode
    reason: str
    confidence: float
    fallback_mode: Optional[Mode] = None
    fallback_reason: Optional[str] = None


class WorkflowModeSelector:
    """Select optimal mode for operation"""

    def __init__(self):
        """Initialize mode selector"""
        self.logger = logger
        self.logger.info("✅ Workflow Mode Selector initialized")

    def select(self, context: OperationContext, scope: Scope) -> ModeSelection:
        """
        Select mode based on context and scope

        Priority order:
        1. Explicitly requested mode
        2. @flow (if complex workflow)
        3. @auto[#automatic] (if simple task and can auto-execute)
        4. @auto[#autonomous] (if requires independence)
        5. @auto[#automation] (if recurring)
        6. Manual (default)
        """
        self.logger.info("🔍 Selecting optimal mode...")

        # Check for explicitly requested mode
        if context.requested_mode:
            try:
                mode = Mode(context.requested_mode)
                self.logger.info(f"✅ Using requested mode: {mode.value}")
                return ModeSelection(
                    mode=mode,
                    reason=f"Explicitly requested: {context.requested_mode}",
                    confidence=1.0
                )
            except ValueError:
                self.logger.warning(f"Invalid requested mode: {context.requested_mode}")

        # Priority 1: @flow (if complex workflow)
        if context.is_complex_workflow:
            self.logger.info("✅ Selected: @flow (complex workflow)")
            return ModeSelection(
                mode=Mode.FLOW,
                reason="Complex workflow requires orchestration",
                confidence=0.95,
                fallback_mode=Mode.MANUAL,
                fallback_reason="Fallback to manual if flow unavailable"
            )

        # Priority 2: @auto[#automatic] (if simple task and can auto-execute)
        if context.is_simple_task and context.can_auto_execute:
            self.logger.info("✅ Selected: @auto[#automatic] (simple auto-execute)")
            return ModeSelection(
                mode=Mode.AUTO_AUTOMATIC,
                reason="Simple task can be auto-executed",
                confidence=0.90,
                fallback_mode=Mode.MANUAL,
                fallback_reason="Fallback to manual if auto-execute unavailable"
            )

        # Priority 3: @auto[#autonomous] (if requires independence)
        if context.requires_independence:
            self.logger.info("✅ Selected: @auto[#autonomous] (requires independence)")
            return ModeSelection(
                mode=Mode.AUTO_AUTONOMOUS,
                reason="Task requires independent decision-making",
                confidence=0.85,
                fallback_mode=Mode.MANUAL,
                fallback_reason="Fallback to manual if autonomous unavailable"
            )

        # Priority 4: @auto[#automation] (if recurring)
        if context.is_recurring:
            self.logger.info("✅ Selected: @auto[#automation] (recurring task)")
            return ModeSelection(
                mode=Mode.AUTO_AUTOMATION,
                reason="Recurring task should be automated",
                confidence=0.80,
                fallback_mode=Mode.MANUAL,
                fallback_reason="Fallback to manual if automation unavailable"
            )

        # Default: Manual
        self.logger.info("✅ Selected: MANUAL (default)")
        return ModeSelection(
            mode=Mode.MANUAL,
            reason="Default mode - manual execution",
            confidence=0.70
        )

    def validate(self, mode: Mode, scope: Scope, context: OperationContext) -> tuple[bool, Optional[str]]:
        """Validate mode selection and scope combination"""

        # Check invalid combinations
        invalid_combinations = [
            (Scope.CLOUD, Mode.AUTO_AUTONOMOUS, "Cloud + autonomous is privacy risk"),
            (Scope.NON_WORKSPACE, Mode.FLOW, "Non-workspace + flow is too complex"),
            (Scope.LOCAL, Mode.AUTO_AUTOMATION, "Local + automation should use workspace"),
        ]

        for invalid_scope, invalid_mode, reason in invalid_combinations:
            if scope == invalid_scope and mode == invalid_mode:
                return False, reason

        # Check if mode matches requirements
        if context.is_complex_workflow and mode not in [Mode.FLOW]:
            return False, f"Mode {mode.value} does not meet complex workflow requirement"

        if context.is_simple_task and context.can_auto_execute and mode not in [Mode.AUTO_AUTOMATIC, Mode.MANUAL]:
            return False, f"Mode {mode.value} does not meet simple auto-execute requirement"

        if context.requires_independence and mode not in [Mode.AUTO_AUTONOMOUS, Mode.MANUAL]:
            return False, f"Mode {mode.value} does not meet independence requirement"

        if context.is_recurring and mode not in [Mode.AUTO_AUTOMATION, Mode.MANUAL]:
            return False, f"Mode {mode.value} does not meet recurring requirement"

        return True, None


if __name__ == "__main__":
    import argparse
    from workflow_scope_context_analyzer import WorkflowScopeContextAnalyzer
    from workflow_scope_selector import WorkflowScopeSelector

    parser = argparse.ArgumentParser(description="Workflow Mode Selector")
    parser.add_argument("request", help="User request/operation description")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    # Analyze context
    analyzer = WorkflowScopeContextAnalyzer()
    context = analyzer.analyze(args.request)

    # Select scope
    scope_selector = WorkflowScopeSelector()
    scope_selection = scope_selector.select(context)

    # Select mode
    mode_selector = WorkflowModeSelector()
    mode_selection = mode_selector.select(context, scope_selection.scope)

    # Validate
    is_valid, error = mode_selector.validate(mode_selection.mode, scope_selection.scope, context)

    if args.json:
        import json
        result = {
            "mode": mode_selection.mode.value,
            "reason": mode_selection.reason,
            "confidence": mode_selection.confidence,
            "scope": scope_selection.scope.value,
            "valid": is_valid,
            "error": error
        }
        print(json.dumps(result, indent=2))
    else:
        print(f"\n🎯 Mode Selection:")
        print(f"   Mode: {mode_selection.mode.value}")
        print(f"   Reason: {mode_selection.reason}")
        print(f"   Confidence: {mode_selection.confidence:.2f}")
        print(f"   Scope: {scope_selection.scope.value}")
        print(f"   Valid: {is_valid}")
        if error:
            print(f"   Error: {error}")

