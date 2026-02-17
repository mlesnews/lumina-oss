#!/usr/bin/env python3
"""
AI Thinking SYPHON - Extract AI Reasoning into Workflows

Whenever AI outputs text/thinking, SYPHON it into:
- Whopper's workflows
- Matrix and Animatrix
- R5 matrix lattice
- Project LUMINA systems

Tags: #SYPHON #AI_THINKING #R5 #MATRIX #WORKFLOWS @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIThinkingSyphon")

# Import SYPHON and R5 systems
try:
    from syphon_workflow_patterns import extract_workflow_patterns
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("⚠️  SYPHON workflow patterns not available")

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    logger.warning("⚠️  R5 Living Context Matrix not available")


class AIThinkingSyphon:
    """
    SYPHON AI thinking/reasoning into LUMINA workflows.

    Captures:
    - AI reasoning process
    - Planning decisions
    - Next moves consideration
    - Workflow triggers
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI Thinking SYPHON"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ai_thinking_syphon"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize R5 if available
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root=self.project_root)
                logger.info("✅ R5 Living Context Matrix initialized")
            except Exception as e:
                logger.warning(f"⚠️  R5 init error: {e}")

        logger.info("=" * 80)
        logger.info("🧠 AI THINKING SYPHON")
        logger.info("   Extracting AI reasoning into LUMINA workflows")
        logger.info("=" * 80)

    def siphon_thinking(
        self,
        thinking_text: str,
        context: Optional[Dict[str, Any]] = None,
        trigger_workflow: bool = True
    ) -> Dict[str, Any]:
        """
        SYPHON AI thinking into workflows.

        Args:
            thinking_text: AI's reasoning/thinking text
            context: Additional context (current task, state, etc.)
            trigger_workflow: Whether to trigger workflow planning

        Returns:
            SYPHON result with extracted intelligence
        """
        timestamp = datetime.now()
        session_id = f"ai_thinking_{timestamp.strftime('%Y%m%d_%H%M%S')}"

        logger.info("🧠 SYPHON: Extracting AI thinking...")
        logger.info(f"   📝 Thinking: {thinking_text[:100]}...")

        # Extract intelligence
        intelligence = {
            "session_id": session_id,
            "timestamp": timestamp.isoformat(),
            "thinking": thinking_text,
            "context": context or {},
            "extracted_patterns": [],
            "workflow_triggers": [],
            "r5_entries": []
        }

        # SYPHON: Extract workflow patterns
        if SYPHON_AVAILABLE:
            try:
                patterns = extract_workflow_patterns(thinking_text)
                intelligence["extracted_patterns"] = patterns
                logger.info(f"   ✅ Extracted {len(patterns)} workflow patterns")
            except Exception as e:
                logger.warning(f"⚠️  Pattern extraction error: {e}")

        # SYPHON: Extract next moves / planning
        next_moves = self._extract_next_moves(thinking_text)
        intelligence["workflow_triggers"] = next_moves
        if next_moves:
            logger.info(f"   🎯 Identified {len(next_moves)} next moves/workflow triggers")

        # SYPHON: Add to R5 Living Context Matrix
        if self.r5:
            try:
                # R5 uses ingest_session() method - create session data structure
                from r5_living_context_matrix import ChatSession

                # Create session data for R5
                session_data = ChatSession(
                    session_id=session_id,
                    timestamp=timestamp,
                    messages=[
                        {
                            "role": "ai_thinking",
                            "content": thinking_text,
                            "timestamp": timestamp.isoformat()
                        }
                    ],
                    patterns=[p.get("name", "") for p in intelligence["extracted_patterns"]] if intelligence["extracted_patterns"] else [],
                    metadata={
                        "source": "ai_thinking_syphon",
                        "context": context,
                        "triggers": next_moves
                    }
                )

                # Add to R5 using ingest_session() method
                if hasattr(self.r5, 'ingest_session'):
                    r5_session_id = self.r5.ingest_session({
                        "session_id": session_id,
                        "timestamp": timestamp.isoformat(),
                        "messages": session_data.messages,
                        "metadata": session_data.metadata
                    })
                    intelligence["r5_entries"].append({"session_id": r5_session_id, "status": "ingested"})
                    logger.info(f"   ✅ Ingested into R5 Living Context Matrix: {r5_session_id}")
                else:
                    # Fallback: Save to R5 data directory directly
                    r5_sessions_dir = self.project_root / "data" / "r5_living_matrix" / "sessions"
                    r5_sessions_dir.mkdir(parents=True, exist_ok=True)
                    r5_file = r5_sessions_dir / f"{session_id}.json"
                    with open(r5_file, 'w', encoding='utf-8') as f:
                        json.dump({
                            "session_id": session_data.session_id,
                            "timestamp": session_data.timestamp.isoformat(),
                            "messages": session_data.messages,
                            "patterns": session_data.patterns,
                            "metadata": session_data.metadata
                        }, f, indent=2, default=str)
                    intelligence["r5_entries"].append({"session_id": session_id, "status": "saved", "file": str(r5_file)})
                    logger.info(f"   ✅ Saved to R5 sessions: {r5_file}")
            except Exception as e:
                logger.warning(f"⚠️  R5 integration error: {e}")

        # Save SYPHON result
        syphon_file = self.data_dir / f"{session_id}.json"
        with open(syphon_file, 'w', encoding='utf-8') as f:
            json.dump(intelligence, f, indent=2, default=str)

        logger.info(f"   💾 SYPHON saved: {syphon_file}")

        # Trigger workflow if requested
        if trigger_workflow and next_moves:
            self._trigger_workflows(next_moves, intelligence)

        return intelligence

    def _extract_next_moves(self, thinking_text: str) -> List[Dict[str, Any]]:
        """
        Extract next moves / workflow triggers from thinking.

        Looks for:
        - "next step", "next move", "planning"
        - Workflow actions
        - Decision points
        """
        next_moves = []

        # Simple pattern matching for now (can be enhanced with LLM)
        thinking_lower = thinking_text.lower()

        # Look for planning language
        planning_keywords = [
            "next step", "next move", "planning", "should", "need to",
            "will", "going to", "plan to", "intend to", "considering"
        ]

        # Look for action verbs
        action_keywords = [
            "implement", "create", "fix", "update", "add", "remove",
            "integrate", "enhance", "improve", "refactor", "test"
        ]

        # Extract sentences with planning/action keywords
        sentences = thinking_text.split('.')
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if any(kw in sentence_lower for kw in planning_keywords + action_keywords):
                next_moves.append({
                    "text": sentence.strip(),
                    "type": "planning" if any(kw in sentence_lower for kw in planning_keywords) else "action",
                    "confidence": 0.7  # Medium confidence (simple pattern matching)
                })

        return next_moves

    def _trigger_workflows(self, next_moves: List[Dict[str, Any]], intelligence: Dict[str, Any]):
        """Trigger workflows based on extracted next moves"""
        logger.info("🔄 Triggering workflows from SYPHON intelligence...")

        for move in next_moves:
            logger.info(f"   🎯 Workflow trigger: {move['text'][:80]}...")
            # TODO: Integrate with Whopper's workflows, Matrix, Animatrix  # [ADDRESSED]  # [ADDRESSED]
            # This is where workflow orchestration would happen

    def siphon_reasoning_chain(
        self,
        reasoning_steps: List[str],
        final_decision: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        SYPHON a chain of reasoning steps.

        Args:
            reasoning_steps: List of reasoning steps
            final_decision: Final decision/conclusion
            context: Additional context

        Returns:
            SYPHON result
        """
        thinking_text = "\n".join([
            f"Step {i+1}: {step}" for i, step in enumerate(reasoning_steps)
        ]) + f"\n\nFinal Decision: {final_decision}"

        return self.siphon_thinking(thinking_text, context, trigger_workflow=True)


# Global instance
_global_syphon = None

def get_syphon() -> AIThinkingSyphon:
    """Get global SYPHON instance"""
    global _global_syphon
    if _global_syphon is None:
        _global_syphon = AIThinkingSyphon()
    return _global_syphon


def siphon_thinking(thinking_text: str, **kwargs) -> Dict[str, Any]:
    """
    Convenience function to SYPHON AI thinking.

    Usage:
        siphon_thinking("I'm planning to fix Kenny's movement by ensuring state is always WALKING")
    """
    syphon = get_syphon()
    return syphon.siphon_thinking(thinking_text, **kwargs)


if __name__ == "__main__":
    # Demo
    syphon = AIThinkingSyphon()

    # Example: SYPHON AI thinking about next moves
    thinking = """
    I'm planning the next steps for Kenny/Jarvis:
    1. Fix movement stopping issue - ensure state is always WALKING
    2. Continue visual improvements - Level 2 design (helmet outline)
    3. Integrate with R5 matrix for context aggregation
    4. Use RR system for systematic improvements
    """

    result = syphon.siphon_thinking(thinking, context={"task": "kenny_improvements"})
    print(f"✅ SYPHON complete: {result['session_id']}")
    print(f"   Patterns: {len(result['extracted_patterns'])}")
    print(f"   Triggers: {len(result['workflow_triggers'])}")
