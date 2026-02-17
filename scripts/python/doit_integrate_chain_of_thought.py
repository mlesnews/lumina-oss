#!/usr/bin/env python3
"""
Integrate Chain-of-Thought into @DOIT Enhanced

Integrates the chain-of-thought reasoning system into the existing
@DOIT Enhanced framework to address workflow processing weaknesses.

Tags: #DOIT #CHAIN_OF_THOUGHT #INTEGRATION #WORKFLOW @JARVIS @LUMINA
"""

import sys
from pathlib import Path

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("DOITIntegrateCOT")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DOITIntegrateCOT")

# Import both systems
try:
    from doit_enhanced import DOITEnhanced
    DOIT_ENHANCED_AVAILABLE = True
except ImportError:
    DOIT_ENHANCED_AVAILABLE = False
    logger.warning("⚠️  DOIT Enhanced not available")

try:
    from doit_chain_of_thought_enhanced import DOITChainOfThoughtEnhanced
    COT_AVAILABLE = True
except ImportError:
    COT_AVAILABLE = False
    logger.warning("⚠️  Chain-of-Thought Enhanced not available")


class DOITIntegrated:
    """
    Integrated @DOIT with Chain-of-Thought

    Combines:
    - @DOIT Enhanced (5W1H, Root Cause Analysis)
    - Chain-of-Thought Enhanced (Reasoning, Workflow Management)
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)

        # Initialize both systems
        self.doit_enhanced = DOITEnhanced(project_root) if DOIT_ENHANCED_AVAILABLE else None
        self.cot_enhanced = DOITChainOfThoughtEnhanced(project_root) if COT_AVAILABLE else None

        logger.info("="*80)
        logger.info("🔗 @DOIT INTEGRATED (Enhanced + Chain-of-Thought)")
        logger.info("="*80)
        logger.info(f"   DOIT Enhanced: {'✅' if DOIT_ENHANCED_AVAILABLE else '❌'}")
        logger.info(f"   Chain-of-Thought: {'✅' if COT_AVAILABLE else '❌'}")
        logger.info("")

    def doit(
        self,
        task_description: str,
        context: dict = None,
        use_chain_of_thought: bool = True
    ) -> dict:
        """
        Execute @DOIT with integrated chain-of-thought

        Args:
            task_description: Task to execute
            context: Additional context
            use_chain_of_thought: Use chain-of-thought reasoning

        Returns:
            Complete execution result
        """
        logger.info("🚀 @DOIT INTEGRATED EXECUTION")
        logger.info(f"   Task: {task_description}")
        logger.info("")

        # Use chain-of-thought if available and requested
        if use_chain_of_thought and self.cot_enhanced:
            logger.info("   Using Chain-of-Thought Enhanced workflow")
            result = self.cot_enhanced.process_ask(
                task_description,
                context=context
            )
        elif self.doit_enhanced:
            logger.info("   Using DOIT Enhanced workflow")
            result = self.doit_enhanced.doit(
                task_description,
                context=context
            )
        else:
            logger.error("❌ No @DOIT system available")
            return {
                "success": False,
                "error": "No @DOIT system available"
            }

        return result


def main():
    try:
        """Main entry point"""
        project_root = Path(__file__).parent.parent.parent

        doit = DOITIntegrated(project_root)

        # Example execution
        result = doit.doit(
            "@ask Fix the WSL unresponsive issue and complete all unfinished @asks",
            use_chain_of_thought=True
        )

        return 0 if result.get("success") else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())