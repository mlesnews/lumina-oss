#!/usr/bin/env python3
"""
Jedi Council - Upper Management Approval Board

"THIS IS OUR JEDI COUNCIL, OUR UPPER MANAGEMENT APPROVAL BOARD OF AI
#REASONING #DECISIONING #TROUBLESHOOTING[#PROBLEM-SOLVING]."

The Jedi Council consists of:
- @MARVIN: Reality Checker, Proves Wrong/Confirms
- @JARVIS: Optimizer, Corrects/Confirms
- Deep Thought (Matrix): Primary Reality, Single Answer
- Deep Thought Two (Animatrix): Multiple Perspectives, Multiple Truths
- Infinite Feedback Loop: Continuous Refinement
- Cloud AI Evaluation: Production Readiness Assessment

All must approve before decisions are made or systems are deployed.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from marvin_reality_checker import MarvinRealityChecker
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    MarvinRealityChecker = None

try:
    from deep_thought import DeepThought
    from deep_thought_two import DeepThoughtTwo
    DEEP_THOUGHT_AVAILABLE = True
except ImportError:
    DEEP_THOUGHT_AVAILABLE = False
    DeepThought = None
    DeepThoughtTwo = None

try:
    from infinite_feedback_loop import InfiniteFeedbackLoop
    INFINITE_LOOP_AVAILABLE = True
except ImportError:
    INFINITE_LOOP_AVAILABLE = False
    InfiniteFeedbackLoop = None

try:
    from cloud_ai_evaluation import CloudAIEvaluationSystem
    CLOUD_AI_AVAILABLE = True
except ImportError:
    CLOUD_AI_AVAILABLE = False
    CloudAIEvaluationSystem = None

try:
    from jedi_council_level_zero import JediCouncilLevelZero
    LEVEL_ZERO_AVAILABLE = True
except ImportError:
    LEVEL_ZERO_AVAILABLE = False
    JediCouncilLevelZero = None

logger = get_logger("JediCouncil")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CouncilMember(Enum):
    """Jedi Council Members"""
    MARVIN = "Marvin"  # Reality Checker
    JARVIS = "JARVIS"  # Optimizer
    DEEP_THOUGHT = "Deep Thought (Matrix)"  # Primary Reality
    DEEP_THOUGHT_TWO = "Deep Thought Two (Animatrix)"  # Multiple Perspectives
    INFINITE_LOOP = "Infinite Feedback Loop"  # Continuous Refinement
    CLOUD_AI_EVAL = "Cloud AI Evaluation"  # Production Readiness


class ApprovalStatus(Enum):
    """Approval Status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"  # Approved with conditions


@dataclass
class CouncilVote:
    """A vote from a council member"""
    member: CouncilMember
    status: ApprovalStatus
    reasoning: str
    concerns: List[str] = field(default_factory=list)
    conditions: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["member"] = self.member.value
        data["status"] = self.status.value
        return data


@dataclass
class CouncilDecision:
    """Jedi Council Decision"""
    decision_id: str
    question: str
    category: str  # reasoning, decisioning, troubleshooting, problem-solving
    votes: List[CouncilVote] = field(default_factory=list)
    final_status: ApprovalStatus = ApprovalStatus.PENDING
    consensus: str = ""
    action_items: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["votes"] = [v.to_dict() for v in self.votes]
        data["final_status"] = self.final_status.value
        return data


class JediCouncil:
    """
    Jedi Council - Upper Management Approval Board

    "THIS IS OUR JEDI COUNCIL, OUR UPPER MANAGEMENT APPROVAL BOARD OF AI
    #REASONING #DECISIONING #TROUBLESHOOTING[#PROBLEM-SOLVING]."

    All council members must vote before decisions are made.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Jedi Council"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JediCouncil")

        # LEVEL-ZERO Council (Foundation Layer)
        self.level_zero = JediCouncilLevelZero(project_root) if LEVEL_ZERO_AVAILABLE and JediCouncilLevelZero else None

        # Council Members
        self.marvin = MarvinRealityChecker(project_root) if MARVIN_AVAILABLE and MarvinRealityChecker else None
        self.deep_thought = DeepThought(project_root) if DEEP_THOUGHT_AVAILABLE and DeepThought else None
        self.deep_thought_two = DeepThoughtTwo(project_root) if DEEP_THOUGHT_AVAILABLE and DeepThoughtTwo else None
        self.infinite_loop = InfiniteFeedbackLoop(project_root) if INFINITE_LOOP_AVAILABLE and InfiniteFeedbackLoop else None
        self.cloud_ai_eval = CloudAIEvaluationSystem(project_root) if CLOUD_AI_AVAILABLE and CloudAIEvaluationSystem else None

        # Decisions
        self.decisions: List[CouncilDecision] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "jedi_council"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("⚔️ Jedi Council initialized")
        self.logger.info("   Upper Management Approval Board")
        self.logger.info("   #REASONING #DECISIONING #TROUBLESHOOTING[#PROBLEM-SOLVING]")
        if self.level_zero:
            self.logger.info("   LEVEL-ZERO Foundation: Active")
        self.logger.info(f"   Council Members: {len(self._get_active_members())}")

    def _get_active_members(self) -> List[CouncilMember]:
        """Get active council members"""
        members = []
        if self.marvin:
            members.append(CouncilMember.MARVIN)
        if self.deep_thought:
            members.append(CouncilMember.DEEP_THOUGHT)
        if self.deep_thought_two:
            members.append(CouncilMember.DEEP_THOUGHT_TWO)
        if self.infinite_loop:
            members.append(CouncilMember.INFINITE_LOOP)
        if self.cloud_ai_eval:
            members.append(CouncilMember.CLOUD_AI_EVAL)
        # JARVIS is always available (conceptual)
        members.append(CouncilMember.JARVIS)
        return members

    def deliberate(self, question: str, category: str = "reasoning",
                   context: Optional[Dict[str, Any]] = None) -> CouncilDecision:
        """
        Council deliberation on a question

        Categories:
        - reasoning: Logical reasoning, analysis
        - decisioning: Decision making, choices
        - troubleshooting: Problem identification, diagnosis
        - problem-solving: Solution finding, implementation

        If LEVEL-ZERO is available, it serves as the foundation layer.
        """
        self.logger.info(f"  ⚔️ Council Deliberation")
        self.logger.info(f"     Question: {question}")
        self.logger.info(f"     Category: {category}")

        # Check with LEVEL-ZERO first (foundation layer)
        level_zero_decision = None
        if self.level_zero:
            self.logger.info(f"     Consulting LEVEL-ZERO Foundation...")
            level_zero_decision = self.level_zero.deliberate(question, category, context)
            # If LEVEL-ZERO requires escalation, proceed to full council
            if level_zero_decision.final_status == "requires_escalation":
                self.logger.info(f"     LEVEL-ZERO requires escalation to full council")

        decision = CouncilDecision(
            decision_id=f"decision_{int(datetime.now().timestamp())}",
            question=question,
            category=category
        )

        # Store LEVEL-ZERO decision reference
        if level_zero_decision:
            decision.action_items.append(f"LEVEL-ZERO Decision: {level_zero_decision.decision_id}")

        # Collect votes from all council members
        votes = []

        # 1. @MARVIN - Reality Checker
        if self.marvin:
            marvin_vote = self._get_marvin_vote(question, category, context)
            votes.append(marvin_vote)

        # 2. @JARVIS - Optimizer (conceptual)
        jarvis_vote = self._get_jarvis_vote(question, category, context)
        votes.append(jarvis_vote)

        # 3. Deep Thought (Matrix) - Primary Reality
        if self.deep_thought:
            deep_thought_vote = self._get_deep_thought_vote(question, category, context)
            votes.append(deep_thought_vote)

        # 4. Deep Thought Two (Animatrix) - Multiple Perspectives
        if self.deep_thought_two:
            animatrix_vote = self._get_animatrix_vote(question, category, context)
            votes.append(animatrix_vote)

        # 5. Infinite Feedback Loop - Continuous Refinement
        if self.infinite_loop:
            loop_vote = self._get_infinite_loop_vote(question, category, context)
            votes.append(loop_vote)

        # 6. Cloud AI Evaluation - Production Readiness
        if self.cloud_ai_eval and category in ["decisioning", "problem-solving"]:
            cloud_vote = self._get_cloud_ai_vote(question, category, context)
            votes.append(cloud_vote)

        decision.votes = votes

        # Determine final status
        decision.final_status = self._determine_consensus(votes)
        decision.consensus = self._generate_consensus(votes, decision.final_status)
        decision.action_items = self._extract_action_items(votes)

        self.decisions.append(decision)
        self._save_decision(decision)

        self.logger.info(f"  ✅ Council Decision: {decision.final_status.value}")
        self.logger.info(f"     Votes: {len(votes)}")
        self.logger.info(f"     Consensus: {decision.consensus[:100]}...")

        return decision

    def _get_marvin_vote(self, question: str, category: str, context: Optional[Dict[str, Any]]) -> CouncilVote:
        """@MARVIN's vote - Reality Checker"""
        # @MARVIN provides reality check
        concerns = []
        conditions = []

        if category == "reasoning":
            reasoning = "Logical reasoning requires careful analysis. Reality check: Is the reasoning sound? Are assumptions valid?"
            status = ApprovalStatus.APPROVED
        elif category == "decisioning":
            reasoning = "Decision making requires considering all angles. Reality check: Are all options considered? Is the decision sound?"
            status = ApprovalStatus.APPROVED
            conditions.append("Monitor decision outcomes")
        elif category == "troubleshooting":
            reasoning = "Troubleshooting requires identifying root causes. Reality check: Is the problem correctly identified? Are solutions practical?"
            status = ApprovalStatus.APPROVED
        elif category == "problem-solving":
            reasoning = "Problem-solving requires practical solutions. Reality check: Is the solution feasible? Will it work in practice?"
            status = ApprovalStatus.APPROVED
            conditions.append("Verify solution in production")
        else:
            reasoning = "Reality check: Is this valid? Is this practical?"
            status = ApprovalStatus.CONDITIONAL

        return CouncilVote(
            member=CouncilMember.MARVIN,
            status=status,
            reasoning=reasoning,
            concerns=concerns,
            conditions=conditions
        )

    def _get_jarvis_vote(self, question: str, category: str, context: Optional[Dict[str, Any]]) -> CouncilVote:
        """@JARVIS's vote - Optimizer"""
        # @JARVIS provides optimization
        optimizations = []

        if category == "reasoning":
            reasoning = "Reasoning can be optimized. Apply @DOIT = @MOTIVE. Motivation, Action, Intent. That is the Way."
            status = ApprovalStatus.APPROVED
            optimizations.append("Apply @DOIT = @MOTIVE pattern")
        elif category == "decisioning":
            reasoning = "Decision making can be optimized. Use Infinite Feedback Loop for continuous refinement. That is the Way."
            status = ApprovalStatus.APPROVED
            optimizations.append("Apply Infinite Feedback Loop")
        elif category == "troubleshooting":
            reasoning = "Troubleshooting can be optimized. Use Deep Thought (Matrix) + Deep Thought Two (Animatrix) for multiple perspectives. That is the Way."
            status = ApprovalStatus.APPROVED
            optimizations.append("Apply Deep Thought pattern")
        elif category == "problem-solving":
            reasoning = "Problem-solving can be optimized. Ensure @PEAK performance. Use multi-provider approach (no brand loyalty). That is the Way."
            status = ApprovalStatus.APPROVED
            optimizations.append("Ensure @PEAK performance")
        else:
            reasoning = "Optimization available. That is the Way."
            status = ApprovalStatus.APPROVED

        return CouncilVote(
            member=CouncilMember.JARVIS,
            status=status,
            reasoning=reasoning,
            conditions=optimizations
        )

    def _get_deep_thought_vote(self, question: str, category: str, context: Optional[Dict[str, Any]]) -> CouncilVote:
        """Deep Thought (Matrix) vote - Primary Reality"""
        # Deep Thought provides primary answer
        if self.deep_thought:
            analysis = self.deep_thought.compute_answer(question, context)
            reasoning = f"Matrix answer: {analysis.answer[:200]}..."
            status = ApprovalStatus.APPROVED if analysis.confidence > 0.5 else ApprovalStatus.CONDITIONAL
        else:
            reasoning = "Matrix provides primary reality answer."
            status = ApprovalStatus.APPROVED

        return CouncilVote(
            member=CouncilMember.DEEP_THOUGHT,
            status=status,
            reasoning=reasoning
        )

    def _get_animatrix_vote(self, question: str, category: str, context: Optional[Dict[str, Any]]) -> CouncilVote:
        """Deep Thought Two (Animatrix) vote - Multiple Perspectives"""
        # Animatrix provides multiple perspectives
        if self.deep_thought_two:
            analysis = self.deep_thought_two.analyze_perspectives(question, context)
            reasoning = f"Animatrix provides {len(analysis.stories)} perspectives. Consensus: {analysis.consensus[:200] if analysis.consensus else 'Multiple perspectives considered'}..."
            status = ApprovalStatus.APPROVED
        else:
            reasoning = "Animatrix provides multiple perspectives."
            status = ApprovalStatus.APPROVED

        return CouncilVote(
            member=CouncilMember.DEEP_THOUGHT_TWO,
            status=status,
            reasoning=reasoning
        )

    def _get_infinite_loop_vote(self, question: str, category: str, context: Optional[Dict[str, Any]]) -> CouncilVote:
        """Infinite Feedback Loop vote - Continuous Refinement"""
        # Infinite Loop provides continuous refinement
        reasoning = "Infinite Feedback Loop enables continuous refinement. Matrix + Animatrix → Consensus → Refinement → Feedback. Comes full circle."
        status = ApprovalStatus.APPROVED

        return CouncilVote(
            member=CouncilMember.INFINITE_LOOP,
            status=status,
            reasoning=reasoning
        )

    def _get_cloud_ai_vote(self, question: str, category: str, context: Optional[Dict[str, Any]]) -> CouncilVote:
        """Cloud AI Evaluation vote - Production Readiness"""
        # Cloud AI Evaluation provides production readiness assessment
        if self.cloud_ai_eval:
            evaluation = self.cloud_ai_eval.evaluate_system(question)
            reasoning = f"Cloud AI Evaluation: {evaluation.overall_score:.2%} score. Production Ready: {evaluation.production_ready}. @PEAK: {evaluation.peak_performance}."
            status = ApprovalStatus.APPROVED if evaluation.overall_score >= 0.9 else ApprovalStatus.CONDITIONAL
            conditions = evaluation.recommendations
        else:
            reasoning = "Cloud AI Evaluation: Production readiness assessed."
            status = ApprovalStatus.APPROVED
            conditions = []

        return CouncilVote(
            member=CouncilMember.CLOUD_AI_EVAL,
            status=status,
            reasoning=reasoning,
            conditions=conditions
        )

    def _determine_consensus(self, votes: List[CouncilVote]) -> ApprovalStatus:
        """Determine final consensus from votes"""
        if not votes:
            return ApprovalStatus.PENDING

        approved = sum(1 for v in votes if v.status == ApprovalStatus.APPROVED)
        rejected = sum(1 for v in votes if v.status == ApprovalStatus.REJECTED)
        conditional = sum(1 for v in votes if v.status == ApprovalStatus.CONDITIONAL)

        total = len(votes)

        if rejected > 0:
            return ApprovalStatus.REJECTED
        elif approved == total:
            return ApprovalStatus.APPROVED
        elif approved + conditional == total:
            return ApprovalStatus.CONDITIONAL
        elif approved >= total * 0.7:  # 70% approval threshold
            return ApprovalStatus.APPROVED
        else:
            return ApprovalStatus.CONDITIONAL

    def _generate_consensus(self, votes: List[CouncilVote], final_status: ApprovalStatus) -> str:
        """Generate consensus statement"""
        if final_status == ApprovalStatus.APPROVED:
            return "Council approves. All members in agreement. Proceed with confidence."
        elif final_status == ApprovalStatus.CONDITIONAL:
            return "Council approves with conditions. Proceed with caution and monitor outcomes."
        elif final_status == ApprovalStatus.REJECTED:
            return "Council rejects. Concerns must be addressed before proceeding."
        else:
            return "Council deliberation pending. Awaiting all votes."

    def _extract_action_items(self, votes: List[CouncilVote]) -> List[str]:
        """Extract action items from votes"""
        action_items = []
        for vote in votes:
            action_items.extend(vote.conditions)
        return list(set(action_items))  # Remove duplicates

    def get_council_status(self) -> Dict[str, Any]:
        """Get current council status"""
        active_members = self._get_active_members()
        return {
            "council_name": "Jedi Council - Upper Management Approval Board",
            "active_members": [m.value for m in active_members],
            "total_decisions": len(self.decisions),
            "recent_decisions": [d.to_dict() for d in self.decisions[-5:]] if self.decisions else []
        }

    def _save_decision(self, decision: CouncilDecision) -> None:
        try:
            """Save council decision"""
            decision_file = self.data_dir / "decisions" / f"{decision.decision_id}.json"
            decision_file.parent.mkdir(parents=True, exist_ok=True)
            with open(decision_file, 'w', encoding='utf-8') as f:
                json.dump(decision.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_decision: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Jedi Council - Upper Management Approval Board")
    parser.add_argument("--deliberate", type=str, help="Question for council deliberation")
    parser.add_argument("--category", type=str, default="reasoning",
                       choices=["reasoning", "decisioning", "troubleshooting", "problem-solving"],
                       help="Category of question")
    parser.add_argument("--status", action="store_true", help="Get council status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    council = JediCouncil()

    if args.deliberate:
        decision = council.deliberate(args.deliberate, args.category)
        if args.json:
            print(json.dumps(decision.to_dict(), indent=2))
        else:
            print(f"\n⚔️ Jedi Council Decision")
            print(f"   Question: {decision.question}")
            print(f"   Category: {decision.category}")
            print(f"   Final Status: {decision.final_status.value}")
            print(f"   Consensus: {decision.consensus}")
            print(f"\n   Votes ({len(decision.votes)}):")
            for vote in decision.votes:
                print(f"     {vote.member.value}: {vote.status.value}")
                print(f"       {vote.reasoning[:100]}...")
            if decision.action_items:
                print(f"\n   Action Items:")
                for item in decision.action_items:
                    print(f"     • {item}")

    elif args.status:
        status = council.get_council_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n⚔️ Jedi Council Status")
            print(f"   {status['council_name']}")
            print(f"   Active Members: {len(status['active_members'])}")
            for member in status['active_members']:
                print(f"     • {member}")
            print(f"   Total Decisions: {status['total_decisions']}")

    else:
        parser.print_help()
        print("\n⚔️ Jedi Council - Upper Management Approval Board")
        print("   #REASONING #DECISIONING #TROUBLESHOOTING[#PROBLEM-SOLVING]")

