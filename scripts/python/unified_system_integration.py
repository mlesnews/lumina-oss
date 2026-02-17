#!/usr/bin/env python3
"""
Unified System Integration Layer
<COMPANY_NAME> LLC

Connects all systems:
- Workflow Scope & Mode Selection
- IDE Queue Processing
- @auto Mode System
- Existing systems (JARVIS, workflows, etc.)

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UnifiedSystemIntegration")


class UnifiedSystemIntegration:
    """Unified integration layer for all systems"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified integration"""
        if project_root is None:
            project_root = Path.cwd()

        self.project_root = Path(project_root)
        self.logger = logger

        # Initialize all systems
        self._initialize_systems()

        self.logger.info("✅ Unified System Integration initialized")

    def _initialize_systems(self):
        """Initialize all integrated systems"""

        # Workflow Scope & Mode
        try:
            from workflow_scope_mode_orchestrator import WorkflowScopeModeOrchestrator
            self.scope_mode_orchestrator = WorkflowScopeModeOrchestrator(self.project_root)
            self.logger.info("   ✅ Workflow Scope & Mode Orchestrator")
        except Exception as e:
            self.scope_mode_orchestrator = None
            self.logger.debug(f"   Scope/Mode not available: {e}")

        # IDE Queue Processing
        try:
            from ide_queue_monitor import IDEQueueMonitor
            self.queue_monitor = IDEQueueMonitor(self.project_root)
            self.logger.info("   ✅ IDE Queue Monitor")
        except Exception as e:
            self.queue_monitor = None
            self.logger.debug(f"   Queue Monitor not available: {e}")

        # @auto Mode
        try:
            from auto_mode_integrated import AutoModeIntegrated
            self.auto_mode = AutoModeIntegrated()
            self.logger.info("   ✅ @auto Mode Integrated")
        except Exception as e:
            self.auto_mode = None
            self.logger.debug(f"   @auto Mode not available: {e}")

    def process_request(self, request: str, use_auto_mode: bool = False) -> Dict[str, Any]:
        try:
            """Process request through unified system"""

            result = {
                "request": request,
                "scope_mode": None,
                "auto_mode": None,
                "queue_processing": None
            }

            # 1. Determine scope/mode
            if self.scope_mode_orchestrator:
                scope_mode_result = self.scope_mode_orchestrator.orchestrate(request)
                result["scope_mode"] = {
                    "scope": scope_mode_result.scope.value,
                    "mode": scope_mode_result.mode.value,
                    "confidence": scope_mode_result.confidence
                }

            # 2. @auto mode if requested
            if use_auto_mode and self.auto_mode:
                auto_result = self.auto_mode.execute(request)
                result["auto_mode"] = {
                    "response": auto_result.final_response,
                    "confidence": auto_result.confidence
                }

            # 3. Queue processing (background)
            if self.queue_monitor:
                queue_results = self.queue_monitor.monitor_all_queues()
                result["queue_processing"] = {
                    queue_type.value: len(events) for queue_type, events in queue_results.items()
                }

            return result


        except Exception as e:
            self.logger.error(f"Error in process_request: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Unified System Integration")
    parser.add_argument("request", help="User request")
    parser.add_argument("--auto", action="store_true", help="Use @auto mode")

    args = parser.parse_args()

    integration = UnifiedSystemIntegration()
    result = integration.process_request(args.request, use_auto_mode=args.auto)

    import json
    print(json.dumps(result, indent=2, default=str))

