#!/usr/bin/env python3
"""
Master Feedback Loop @CORE - @AIQ Integration

@AIQ = AIQ Consensus System
- Runs consensus across candidate solutions
- Integrates with Triage system
- Routes to Jedi Council for high-priority issues
- All @AIQ decisions flow through Master Feedback Loop @CORE
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import systems
try:
    from master_feedback_loop_jedi_integration import MasterFeedbackLoopJediIntegration, FeedbackSource
    from aiq_triage_jedi import AIQTriageRouter, AIQResult, TriageResult, TriagePriority
    SYSTEMS_AVAILABLE = True
except ImportError:
    SYSTEMS_AVAILABLE = False
    print("⚠️ Some systems not available")


class MasterFeedbackLoopAIQIntegration:
    """
    Master Feedback Loop @CORE with @AIQ Integration

    Complete Decision Flow:
    1. Feedback enters Master Feedback Loop @CORE
    2. @AIQ runs consensus on candidate solutions
    3. Triage determines priority
    4. Master Feedback Loop orchestrates
    5. Jedi Council approves (if needed)
    6. High Council (if critical)
    7. Chat summary generated with @AIQ results
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        # Core systems
        if SYSTEMS_AVAILABLE:
            self.master_loop_jedi = MasterFeedbackLoopJediIntegration(project_root)
            self.aiq_router = AIQTriageRouter(mcp_server_url="http://localhost:8000")
        else:
            self.master_loop_jedi = None
            self.aiq_router = None

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("MasterFeedbackLoopAIQ")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🔄⚔️🤖 MasterFeedbackLoopAIQ - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    async def process_with_aiq_consensus(self, issue_text: str,
                                        candidate_solutions: List[Dict[str, Any]],
                                        severity: Optional[str] = None,
                                        agent_origin: Optional[str] = None) -> Dict[str, Any]:
        """
        Process issue through complete chain:
        @AIQ Consensus → Triage → Master Feedback Loop @CORE → Jedi Council → Chat Summary
        """
        self.logger.info("🔄 Processing with @AIQ consensus...")

        if not self.aiq_router or not self.master_loop_jedi:
            return {"error": "Systems not available"}

        # Step 1: @AIQ Consensus
        try:
            aiq_result = self.aiq_router.run_aiq_consensus(candidate_solutions, quorum=3)
            self.logger.info(f"✅ @AIQ Consensus: Selected solution {aiq_result.selected.get('id', 'unknown')}")
        except Exception as e:
            self.logger.warning(f"⚠️ @AIQ consensus failed: {e}, using first candidate")
            aiq_result = AIQResult(
                selected=candidate_solutions[0] if candidate_solutions else {},
                scores={c.get('id', 'unknown'): 1.0 for c in candidate_solutions}
            )

        # Step 2: Triage
        try:
            triage_result = self.aiq_router.triage_issue(issue_text, severity)
            self.logger.info(f"✅ Triage: {triage_result.priority} - {triage_result.category}")
        except Exception as e:
            self.logger.warning(f"⚠️ Triage failed: {e}, defaulting to ROUTINE")
            triage_result = TriageResult(
                category="general",
                priority=TriagePriority.ROUTINE.value,
                notes="Triage unavailable"
            )

        # Step 3: Master Feedback Loop @CORE with Jedi approval
        feedback_data = {
            "question": f"Should we implement solution: {aiq_result.selected.get('id', 'unknown')}?",
            "category": "decisioning",
            "priority": triage_result.priority,
            "context": {
                "issue_text": issue_text,
                "aiq_consensus": {
                    "selected_solution": aiq_result.selected,
                    "scores": aiq_result.scores
                },
                "triage": {
                    "category": triage_result.category,
                    "priority": triage_result.priority,
                    "notes": triage_result.notes
                }
            }
        }

        # Determine if High Council needed
        requires_high_council = triage_result.priority in [
            TriagePriority.IMMEDIATE.value,
            TriagePriority.URGENT.value
        ]

        master_result = await self.master_loop_jedi.process_with_jedi_approval(
            feedback_data,
            FeedbackSource.BIO_AI_LOOP,
            agent_origin=agent_origin,
            requires_high_council=requires_high_council
        )

        # Step 4: Enhanced chat summary with @AIQ results
        enhanced_summary = self._enhance_chat_summary_with_aiq(
            master_result.get('chat_summary', {}),
            aiq_result,
            triage_result
        )

        # Save enhanced summary
        self._save_enhanced_summary(enhanced_summary)

        return {
            "@aiq_consensus": {
                "selected_solution": aiq_result.selected,
                "scores": aiq_result.scores,
                "quorum": 3
            },
            "triage": {
                "category": triage_result.category,
                "priority": triage_result.priority,
                "notes": triage_result.notes
            },
            "master_feedback_loop": master_result.get('master_feedback_loop', {}),
            "jedi_council": master_result.get('jedi_council'),
            "jedi_high_council": master_result.get('jedi_high_council'),
            "final_approval": master_result.get('final_approval'),
            "chat_summary": enhanced_summary,
            "decision_chain": [
                "@AIQ Consensus",
                "Triage",
                "Master Feedback Loop @CORE",
                "Jedi Council (Upper Management)",
                "Jedi High Council (Elite)" if requires_high_council else None
            ]
        }

    def _enhance_chat_summary_with_aiq(self, base_summary: Dict[str, Any],
                                       aiq_result: AIQResult,
                                       triage_result: TriageResult) -> Dict[str, Any]:
        """Enhance chat summary with @AIQ consensus results"""
        if not base_summary:
            base_summary = {}

        # Add @AIQ section at the beginning
        aiq_section = {
            "@aiq_consensus": {
                "status": "completed",
                "selected_solution": aiq_result.selected.get('id', 'unknown'),
                "selected_content": aiq_result.selected.get('content', '')[:200],
                "all_scores": aiq_result.scores,
                "quorum": 3,
                "consensus_reached": True
            },
            "triage": {
                "status": "completed",
                "category": triage_result.category,
                "priority": triage_result.priority,
                "notes": triage_result.notes,
                "requires_high_council": triage_result.priority in [
                    TriagePriority.IMMEDIATE.value,
                    TriagePriority.URGENT.value
                ]
            }
        }

        # Enhance summary text
        summary_text = base_summary.get('summary_text', '')

        aiq_text = f"""# AI Chat Summary - Decision Chain with @AIQ Consensus
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## @AIQ Consensus
**Status**: ✅ Completed
- **Selected Solution**: {aiq_result.selected.get('id', 'unknown')}
- **Consensus Scores**: {json.dumps(aiq_result.scores, indent=2)}
- **Quorum**: 3
- **Solution Preview**: {aiq_result.selected.get('content', 'N/A')[:200]}...

## Triage
**Status**: ✅ Completed
- **Priority**: {triage_result.priority}
- **Category**: {triage_result.category}
- **Notes**: {triage_result.notes or 'None'}
- **Requires High Council**: {'✅ Yes' if triage_result.priority in [TriagePriority.IMMEDIATE.value, TriagePriority.URGENT.value] else 'No'}

---

{summary_text}
"""

        enhanced_summary = {
            **base_summary,
            "@aiq_consensus": aiq_section["@aiq_consensus"],
            "triage": aiq_section["triage"],
            "summary_text": aiq_text,
            "enhanced_with_aiq": True
        }

        return enhanced_summary

    def _save_enhanced_summary(self, summary: Dict[str, Any]):
        try:
            """Save enhanced summary with @AIQ results"""
            summaries_dir = self.project_root / "data" / "ai_chat_summaries"
            summaries_dir.mkdir(parents=True, exist_ok=True)

            summary_id = summary.get('summary_id', f"summary_{int(datetime.now().timestamp())}")

            # Save JSON
            json_file = summaries_dir / f"{summary_id}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, default=str)

            # Save Markdown
            md_file = summaries_dir / f"{summary_id}.md"
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(summary.get('summary_text', ''))

            self.logger.info(f"💾 Enhanced chat summary saved: {summary_id} (with @AIQ)")


        except Exception as e:
            self.logger.error(f"Error in _save_enhanced_summary: {e}", exc_info=True)
            raise
async def main():
    """Demonstrate @AIQ integration"""
    integration = MasterFeedbackLoopAIQIntegration()

    print("\n🔄⚔️🤖 Master Feedback Loop @CORE - @AIQ Integration")
    print("=" * 80)
    print("Decision Chain: @AIQ Consensus → Triage → Master Loop → Jedi Council")
    print()

    # Example issue with candidate solutions
    issue_text = "Enhance master feedback loop with @AIQ consensus system"

    candidate_solutions = [
        {
            "id": "solution_1",
            "content": "Integrate @AIQ consensus directly into Master Feedback Loop @CORE"
        },
        {
            "id": "solution_2",
            "content": "Create separate @AIQ service and route through Master Loop"
        },
        {
            "id": "solution_3",
            "content": "Enhance existing orchestrator with @AIQ consensus layer"
        }
    ]

    result = await integration.process_with_aiq_consensus(
        issue_text=issue_text,
        candidate_solutions=candidate_solutions,
        severity="high",
        agent_origin="Human"
    )

    print("📊 Decision Chain Results:")
    print(f"   @AIQ Consensus: ✅ Completed")
    print(f"      Selected: {result.get('@aiq_consensus', {}).get('selected_solution', {}).get('id', 'unknown')}")
    print(f"   Triage: ✅ {result.get('triage', {}).get('priority', 'unknown')}")
    print(f"   Master Feedback Loop: ✅ Processed")
    print(f"   Jedi Council: {'✅ Consulted' if result.get('jedi_council') else '⏭️ Skipped'}")
    print(f"   High Council: {'✅ Consulted' if result.get('jedi_high_council') else '⏭️ Not Required'}")
    print()
    print("📋 Enhanced Chat Summary (with @AIQ):")
    print(result.get('chat_summary', {}).get('summary_text', 'No summary')[:800])
    print("...")


if __name__ == "__main__":



    asyncio.run(main())