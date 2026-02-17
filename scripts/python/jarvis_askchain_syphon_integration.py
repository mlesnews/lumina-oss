#!/usr/bin/env python3
"""
JARVIS @ASKChain SYPHON Integration

Integrates SYPHON-enhanced troubleshooting into @askchain execution.

@ASKCHAIN @SYPHON #TROUBLESHOOTING #INTEGRATION
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAskChainSyphonIntegration")

# Import SYPHON-enhanced troubleshooting
try:
    from jarvis_syphon_enhanced_troubleshooting import JARVISSyphonEnhancedTroubleshooting
    SYPHON_TROUBLESHOOTING_AVAILABLE = True
except ImportError:
    SYPHON_TROUBLESHOOTING_AVAILABLE = False
    JARVISSyphonEnhancedTroubleshooting = None
    logger.warning("⚠️  SYPHON-enhanced troubleshooting not available")

# Import askchain executor
try:
    from jarvis_execute_ask_chains import JARVISAskChainExecutor
    ASKCHAIN_EXECUTOR_AVAILABLE = True
except ImportError:
    ASKCHAIN_EXECUTOR_AVAILABLE = False
    JARVISAskChainExecutor = None
    logger.warning("⚠️  AskChain executor not available")


class JARVISAskChainSyphonIntegration:
    """
    Integration layer between @askchain execution and SYPHON troubleshooting.

    Provides:
    - Pre-execution troubleshooting
    - Pattern recognition for failures
    - Intelligence extraction from failures
    - Automatic retry with proven fixes
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize SYPHON troubleshooter
        self.syphon_troubleshooter = None
        if SYPHON_TROUBLESHOOTING_AVAILABLE:
            try:
                self.syphon_troubleshooter = JARVISSyphonEnhancedTroubleshooting(project_root)
                logger.info("✅ SYPHON-enhanced troubleshooting initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON troubleshooting initialization failed: {e}")

        # Initialize askchain executor
        self.executor = None
        if ASKCHAIN_EXECUTOR_AVAILABLE:
            try:
                self.executor = JARVISAskChainExecutor(project_root)
                logger.info("✅ AskChain executor initialized")
            except Exception as e:
                logger.warning(f"⚠️  AskChain executor initialization failed: {e}")

    def troubleshoot_task_pre_execution(self, task: Any) -> Dict[str, Any]:
        """
        Troubleshoot task before execution.

        Args:
            task: ChainedTask to troubleshoot

        Returns:
            Troubleshooting result
        """
        if not self.syphon_troubleshooter:
            return {"available": False}

        try:
            error_data = {
                "error_id": f"pre_check_{task.task_id}",
                "error_type": "pre_execution_check",
                "message": f"Pre-execution check for task: {task.task_id}",
                "task_id": task.task_id,
                "ask_text": task.ask_text,
                "dependencies": getattr(task, 'dependencies', []),
                "category": getattr(task, 'category', 'unknown'),
                "priority": getattr(task, 'priority', 'medium')
            }

            result = self.syphon_troubleshooter.troubleshoot_with_syphon(
                error_data,
                mode="pre",
                level="standard"
            )

            return {
                "available": True,
                "should_proceed": result.simulation_success_rate > 0.75,
                "simulation_success_rate": result.simulation_success_rate,
                "patterns_detected": len(result.patterns_detected),
                "intent": result.intent_extracted,
                "building_blocks": result.building_blocks,
                "troubleshooting_result": result.to_dict()
            }
        except Exception as e:
            logger.error(f"❌ Pre-execution troubleshooting failed: {e}")
            return {"available": False, "error": str(e)}

    def troubleshoot_task_failure(self, task: Any, error: Exception) -> Dict[str, Any]:
        """
        Troubleshoot task failure and extract intelligence.

        Args:
            task: Failed ChainedTask
            error: Exception that occurred

        Returns:
            Intelligence extraction result
        """
        if not self.syphon_troubleshooter:
            return {"available": False}

        try:
            error_data = {
                "error_id": f"failure_{task.task_id}",
                "error_type": "task_execution_failure",
                "message": str(error),
                "task_id": task.task_id,
                "ask_text": task.ask_text,
                "task_status": getattr(task, 'status', 'unknown'),
                "error_message": getattr(task, 'error_message', None),
                "dependencies": getattr(task, 'dependencies', [])
            }

            result = self.syphon_troubleshooter.troubleshoot_with_syphon(
                error_data,
                mode="on_error",
                level="standard"
            )

            return {
                "available": True,
                "patterns_detected": len(result.patterns_detected),
                "actionable_intelligence": result.actionable_intelligence,
                "proven_patterns": result.proven_patterns,
                "fix_suggestions": self._extract_fix_suggestions(result),
                "troubleshooting_result": result.to_dict()
            }
        except Exception as e:
            logger.error(f"❌ Failure troubleshooting failed: {e}")
            return {"available": False, "error": str(e)}

    def _extract_fix_suggestions(self, troubleshooting_result: Any) -> List[Dict[str, Any]]:
        """Extract fix suggestions from troubleshooting result"""
        suggestions = []

        # Extract from proven patterns
        for pattern in troubleshooting_result.proven_patterns:
            if pattern.get("success_rate", 0) > 0.75:
                suggestions.append({
                    "pattern": pattern.get("pattern_id"),
                    "fix_strategy": pattern.get("fix_strategy"),
                    "success_rate": pattern.get("success_rate"),
                    "recommended": True
                })

        # Extract from actionable intelligence
        for item in troubleshooting_result.actionable_intelligence:
            if "fix" in item.lower() or "retry" in item.lower():
                suggestions.append({
                    "suggestion": item,
                    "source": "actionable_intelligence"
                })

        return suggestions

    def should_retry_task(self, task: Any, error: Exception, intelligence: Dict[str, Any]) -> bool:
        """
        Determine if task should be retried based on intelligence.

        Args:
            task: Failed task
            error: Exception
            intelligence: Intelligence from troubleshooting

        Returns:
            True if should retry
        """
        if not intelligence.get("available"):
            return False

        # Check for proven patterns with high success rate
        proven_patterns = intelligence.get("proven_patterns", [])
        for pattern in proven_patterns:
            if pattern.get("success_rate", 0) > 0.75:
                fix_strategy = pattern.get("fix_strategy", "")
                if fix_strategy in ["retry", "retry_with_delay", "retry_after_fix"]:
                    return True

        return False

    def get_retry_strategy(self, task: Any, intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get retry strategy based on intelligence.

        Args:
            task: Task to retry
            intelligence: Intelligence from troubleshooting

        Returns:
            Retry strategy
        """
        strategy = {
            "should_retry": False,
            "delay_seconds": 0,
            "fixes_to_apply": [],
            "max_retries": 1
        }

        if not intelligence.get("available"):
            return strategy

        # Find best proven pattern
        proven_patterns = intelligence.get("proven_patterns", [])
        best_pattern = None
        best_rate = 0.0

        for pattern in proven_patterns:
            rate = pattern.get("success_rate", 0.0)
            if rate > best_rate and rate > 0.75:
                best_rate = rate
                best_pattern = pattern

        if best_pattern:
            strategy["should_retry"] = True
            fix_strategy = best_pattern.get("fix_strategy", "")

            if "delay" in fix_strategy:
                strategy["delay_seconds"] = 5

            if "fix" in fix_strategy:
                strategy["fixes_to_apply"] = best_pattern.get("building_blocks", [])

            strategy["max_retries"] = 1  # Only retry once with proven fix

        return strategy


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS @ASKChain SYPHON Integration")
    parser.add_argument("--test", action="store_true", help="Test integration")

    args = parser.parse_args()

    integration = JARVISAskChainSyphonIntegration()

    if args.test:
        print("✅ SYPHON-enhanced troubleshooting available:", integration.syphon_troubleshooter is not None)
        print("✅ AskChain executor available:", integration.executor is not None)

    return 0


if __name__ == "__main__":


    exit(main())