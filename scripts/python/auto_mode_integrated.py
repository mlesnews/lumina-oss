#!/usr/bin/env python3
"""
@auto Mode Integrated System
<COMPANY_NAME> LLC

Complete @auto mode system integration:
- Decision tree
- Model selector
- Multi-agent orchestrator
- End-to-end execution

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

from auto_mode_decision_tree import AutoModeDecisionTree
from auto_mode_model_selector import AutoModeModelSelector
from auto_mode_agent_orchestrator import AutoModeAgentOrchestrator

logger = get_logger("AutoModeIntegrated")


@dataclass
class AutoModeResult:
    """Complete @auto mode result"""
    decision: Any
    model_selection: Any
    agent_result: Any
    final_response: str
    confidence: float


class AutoModeIntegrated:
    """Complete @auto mode integrated system"""

    def __init__(self):
        self.logger = logger
        self.decision_tree = AutoModeDecisionTree()
        self.model_selector = AutoModeModelSelector()
        self.agent_orchestrator = AutoModeAgentOrchestrator()
        self.logger.info("✅ Auto Mode Integrated System initialized")

    def execute(self, request: str, context: Optional[Dict[str, Any]] = None) -> AutoModeResult:
        """Execute complete @auto mode flow"""

        # 1. Decision tree
        decision = self.decision_tree.decide(request, context)

        # 2. Model selection
        model_selection = self.model_selector.select(decision, decision._analysis if hasattr(decision, '_analysis') else None)

        # 3. Agent orchestration
        agent_result = self.agent_orchestrator.orchestrate(request, decision)

        # 4. Final response
        final_response = agent_result.aggregated_response

        # Calculate overall confidence
        confidence = (decision.confidence + model_selection.confidence + agent_result.confidence) / 3

        return AutoModeResult(
            decision=decision,
            model_selection=model_selection,
            agent_result=agent_result,
            final_response=final_response,
            confidence=confidence
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="@auto Mode Integrated System")
    parser.add_argument("request", help="User request")

    args = parser.parse_args()

    auto_mode = AutoModeIntegrated()
    result = auto_mode.execute(args.request)

    print(f"\n🎯 @auto Mode Result:")
    print(f"   Response: {result.final_response}")
    print(f"   Confidence: {result.confidence:.2f}")

