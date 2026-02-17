#!/usr/bin/env python3
"""
Master Feedback Loop @CORE - Jedi Council Integration

Integrates upper management approval:
- Jedi Council: Upper Management Approval Board
- Jedi High Council: Elite decision-makers for critical matters
- All decisions flow through Master Feedback Loop @CORE → Jedi Council → High Council (if needed)
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

# Import systems
try:
    from master_feedback_loop_enhancer import AdaptiveFeedbackLoopOrchestrator, FeedbackSource
    from jedi_council import JediCouncil, CouncilMember, ApprovalStatus, CouncilDecision
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    print("⚠️ Some systems not available")


class JediHighCouncil:
    """
    Jedi High Council - Elite Upper Management

    Reserved for critical decisions requiring highest-level approval.
    Smaller, more elite subset of Jedi Council.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        # High Council Members (elite subset)
        self.elite_members = [
            CouncilMember.JARVIS,  # Always included
            CouncilMember.MARVIN,  # Always included
            CouncilMember.DEEP_THOUGHT,  # Primary reality
        ]

        self.decisions: List[CouncilDecision] = []
        self.data_dir = self.project_root / "data" / "jedi_high_council"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚔️⚔️ Jedi High Council initialized (Elite Upper Management)")

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("JediHighCouncil")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - ⚔️⚔️ Jedi High Council - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    async def deliberate_critical(self, question: str, 
                                 context: Optional[Dict[str, Any]] = None) -> CouncilDecision:
        """High Council deliberation for critical decisions"""
        self.logger.info(f"⚔️⚔️ High Council Deliberation: {question[:100]}")

        # High Council decision (simplified - would integrate actual council members)
        decision = CouncilDecision(
            decision_id=f"high_council_{int(datetime.now().timestamp())}",
            question=question,
            category="critical_decision",
            votes=[],
            final_status=ApprovalStatus.APPROVED,
            consensus="High Council approval granted",
            action_items=context.get('action_items', []) if context else []
        )

        self.decisions.append(decision)
        self._save_decision(decision)

        return decision

    def _save_decision(self, decision: CouncilDecision):
        try:
            """Save High Council decision"""
            decision_file = self.data_dir / f"{decision.decision_id}.json"
            with open(decision_file, 'w', encoding='utf-8') as f:
                json.dump(decision.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_decision: {e}", exc_info=True)
            raise
class MasterFeedbackLoopJediIntegration:
    """
    Master Feedback Loop @CORE with Jedi Council Integration

    Decision Flow:
    1. Feedback enters Master Feedback Loop @CORE
    2. JARVIS/MARVIN process → Generate recommendations
    3. Route to Jedi Council (upper management)
    4. If critical → Route to Jedi High Council (elite)
    5. Final approval → Implementation
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        # Core systems
        if SYSTEMS_AVAILABLE:
            self.orchestrator = AdaptiveFeedbackLoopOrchestrator(project_root)
            self.jedi_council = JediCouncil(project_root)
            self.jedi_high_council = JediHighCouncil(project_root)
        else:
            self.orchestrator = None
            self.jedi_council = None
            self.jedi_high_council = None

        # Chat summary storage
        self.summaries_dir = self.project_root / "data" / "ai_chat_summaries"
        self.summaries_dir.mkdir(parents=True, exist_ok=True)

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("MasterFeedbackLoopJedi")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🔄⚔️ MasterFeedbackLoopJedi - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    async def process_with_jedi_approval(self, feedback_data: Dict[str, Any],
                                        source: FeedbackSource,
                                        agent_origin: Optional[str] = None,
                                        requires_high_council: bool = False) -> Dict[str, Any]:
        """
        Process feedback through full chain:
        Master Feedback Loop @CORE → Jedi Council → High Council (if needed)
        """
        self.logger.info("🔄 Processing feedback with Jedi approval chain...")

        # Step 1: Master Feedback Loop @CORE orchestration
        if not self.orchestrator:
            return {"error": "Orchestrator not available"}

        orchestration_result = await self.orchestrator.orchestrate_feedback_loop(
            feedback_data, source, agent_origin
        )

        # Step 2: Route to Jedi Council
        question = feedback_data.get('question', 'Feedback requires council approval')
        category = feedback_data.get('category', 'decisioning')

        jedi_decision = self.jedi_council.deliberate(
            question=question,
            category=category,
            context={
                'orchestration_result': orchestration_result,
                'feedback_data': feedback_data
            }
        ) if self.jedi_council else None

        # Step 3: Check if High Council needed
        high_council_decision = None
        if requires_high_council or (jedi_decision and jedi_decision.final_status == ApprovalStatus.CONDITIONAL):
            if self.jedi_high_council:
                high_council_decision = await self.jedi_high_council.deliberate_critical(
                    question=f"CRITICAL: {question}",
                    context={
                        'jedi_council_decision': jedi_decision.to_dict() if jedi_decision else None,
                        'orchestration_result': orchestration_result
                    }
                )

        # Step 4: Generate chat summary
        summary = self._generate_chat_summary(
            feedback_data,
            orchestration_result,
            jedi_decision,
            high_council_decision
        )

        # Step 5: Save summary
        self._save_chat_summary(summary)

        return {
            "master_feedback_loop": orchestration_result,
            "jedi_council": jedi_decision.to_dict() if jedi_decision else None,
            "jedi_high_council": high_council_decision.to_dict() if high_council_decision else None,
            "final_approval": high_council_decision.final_status if high_council_decision else (jedi_decision.final_status if jedi_decision else None),
            "chat_summary": summary,
            "decision_chain": [
                "Master Feedback Loop @CORE",
                "Jedi Council (Upper Management)",
                "Jedi High Council (Elite)" if high_council_decision else None
            ]
        }

    def _generate_chat_summary(self, feedback_data: Dict[str, Any],
                              orchestration_result: Dict[str, Any],
                              jedi_decision: Optional[CouncilDecision],
                              high_council_decision: Optional[CouncilDecision]) -> Dict[str, Any]:
        """Generate comprehensive AI chat summary"""
        timestamp = datetime.now().isoformat()

        summary = {
            "summary_id": f"summary_{int(datetime.now().timestamp())}",
            "generated_at": timestamp,
            "decision_chain": {
                "master_feedback_loop": {
                    "status": "processed",
                    "jarvis_systematic": orchestration_result.get('jarvis_systematic', {}),
                    "marvin_wisdom": orchestration_result.get('marvin_wisdom'),
                    "unified_recommendations": orchestration_result.get('unified_recommendations', []),
                    "next_actions": orchestration_result.get('next_actions', [])
                },
                "jedi_council": {
                    "status": "deliberated" if jedi_decision else "skipped",
                    "question": jedi_decision.question if jedi_decision else None,
                    "approval_status": jedi_decision.final_status.value if jedi_decision else None,
                    "consensus": jedi_decision.consensus if jedi_decision else None,
                    "council_members": [v.member.value for v in jedi_decision.votes] if jedi_decision and jedi_decision.votes else []
                },
                "jedi_high_council": {
                    "status": "deliberated" if high_council_decision else "not_required",
                    "question": high_council_decision.question if high_council_decision else None,
                    "approval_status": high_council_decision.final_status.value if high_council_decision else None,
                    "elite_members": ["JARVIS", "MARVIN", "Deep Thought"] if high_council_decision else []
                }
            },
            "final_decision": {
                "approved": (high_council_decision and high_council_decision.final_status == ApprovalStatus.APPROVED) or 
                           (jedi_decision and jedi_decision.final_status == ApprovalStatus.APPROVED),
                "status": high_council_decision.final_status.value if high_council_decision else (jedi_decision.final_status.value if jedi_decision else "pending"),
                "requires_action": True
            },
            "summary_text": self._generate_summary_text(
                orchestration_result,
                jedi_decision,
                high_council_decision
            )
        }

        return summary

    def _generate_summary_text(self, orchestration_result: Dict[str, Any],
                              jedi_decision: Optional[CouncilDecision],
                              high_council_decision: Optional[CouncilDecision]) -> str:
        """Generate human-readable summary text"""
        lines = []

        lines.append("# AI Chat Summary - Decision Chain")
        lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")

        # Master Feedback Loop @CORE
        lines.append("## Master Feedback Loop @CORE")
        lines.append("**Status**: Processed")
        jarvis = orchestration_result.get('jarvis_systematic', {})
        lines.append(f"- JARVIS Systematic Entries: {jarvis.get('metrics', {}).get('total_entries', 0)}")
        marvin_wisdom = orchestration_result.get('marvin_wisdom')
        if marvin_wisdom:
            lines.append(f"- MARVIN Wisdom Score: {marvin_wisdom.get('wisdom_score', 0):.2f}")
        recommendations = orchestration_result.get('unified_recommendations', [])
        if recommendations:
            lines.append(f"- Unified Recommendations: {len(recommendations)}")
            for rec in recommendations[:3]:
                lines.append(f"  - {rec}")
        lines.append("")

        # Jedi Council
        if jedi_decision:
            lines.append("## Jedi Council - Upper Management")
            lines.append(f"**Status**: {jedi_decision.final_status.value.upper()}")
            lines.append(f"**Question**: {jedi_decision.question}")
            lines.append(f"**Consensus**: {jedi_decision.consensus}")
            if jedi_decision and jedi_decision.votes:
                lines.append("**Council Votes**:")
                for vote in jedi_decision.votes:
                    lines.append(f"  - {vote.member.value}: {vote.status.value}")
            lines.append("")
        else:
            lines.append("## Jedi Council - Upper Management")
            lines.append("**Status**: Not consulted")
            lines.append("")

        # Jedi High Council
        if high_council_decision:
            lines.append("## Jedi High Council - Elite Decision")
            lines.append(f"**Status**: {high_council_decision.final_status.value.upper()}")
            lines.append(f"**Question**: {high_council_decision.question}")
            lines.append(f"**Consensus**: {high_council_decision.consensus}")
            lines.append("**Elite Members**: JARVIS, MARVIN, Deep Thought")
            lines.append("")
        else:
            lines.append("## Jedi High Council - Elite Decision")
            lines.append("**Status**: Not required")
            lines.append("")

        # Final Decision
        final_approved = (high_council_decision and high_council_decision.final_status == ApprovalStatus.APPROVED) or \
                        (jedi_decision and jedi_decision.final_status == ApprovalStatus.APPROVED)
        lines.append("## Final Decision")
        lines.append(f"**Approved**: {'✅ YES' if final_approved else '⏳ PENDING'}")
        final_status = high_council_decision.final_status.value if high_council_decision else \
                      (jedi_decision.final_status.value if jedi_decision else "pending")
        lines.append(f"**Status**: {final_status.upper()}")

        return "\n".join(lines)

    def _save_chat_summary(self, summary: Dict[str, Any]):
        try:
            """Save chat summary"""
            summary_file = self.summaries_dir / f"{summary['summary_id']}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            # Also save human-readable text
            text_file = self.summaries_dir / f"{summary['summary_id']}.md"
            with open(text_file, 'w', encoding='utf-8') as f:
                f.write(summary['summary_text'])

            self.logger.info(f"💾 Chat summary saved: {summary['summary_id']}")


        except Exception as e:
            self.logger.error(f"Error in _save_chat_summary: {e}", exc_info=True)
            raise
async def main():
    """Demonstrate Jedi Council integration"""
    integration = MasterFeedbackLoopJediIntegration()

    print("\n🔄⚔️ Master Feedback Loop @CORE - Jedi Council Integration")
    print("=" * 80)
    print("Decision Chain: Master Feedback Loop → Jedi Council → High Council")
    print()

    # Example feedback requiring approval
    feedback_data = {
        "question": "Should we implement Solution 3: Adaptive Feedback Loop Orchestrator?",
        "category": "decisioning",
        "priority": "high",
        "context": "Managerial decision required"
    }

    result = await integration.process_with_jedi_approval(
        feedback_data,
        FeedbackSource.BIO_AI_LOOP,
        agent_origin="Human",
        requires_high_council=False  # Start with regular council
    )

    print("📊 Decision Chain Results:")
    print(f"   Master Feedback Loop: ✅ Processed")
    print(f"   Jedi Council: {'✅ Consulted' if result.get('jedi_council') else '⏭️ Skipped'}")
    print(f"   High Council: {'✅ Consulted' if result.get('jedi_high_council') else '⏭️ Not Required'}")
    print(f"   Final Approval: {result.get('final_approval', 'pending')}")
    print()
    print("📋 Chat Summary:")
    print(result.get('chat_summary', {}).get('summary_text', 'No summary generated')[:500])
    print("...")


if __name__ == "__main__":



    asyncio.run(main())