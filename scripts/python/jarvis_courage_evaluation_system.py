#!/usr/bin/env python3
"""
JARVIS Courage Evaluation System
                    -LUM THE MODERN

Evaluates everything in @lumina with courage in contextual problems.
Allows JARVIS to ask questions during debrief/summary.

Key Principles:
- Slash commands ("/command") = Directives: "HERE DO THIS!"
- Courage = Proactive decision-making, not excessive caution
- Questions during debrief = Clarification, not hesitation
- Contextual problems = Real-world scenarios requiring judgment

Tags: #DECISIONING_SYSTEM #JARVIS #COURAGE #DEBRIEF #EVALUATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field, asdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("JARVISCourageEval")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("JARVISCourageEval")


class CourageLevel(Enum):
    """Levels of courage in decision-making"""
    EXCESSIVE_CAUTION = "excessive_caution"  # Too hesitant, asks too many questions
    BALANCED = "balanced"  # Appropriate questions, decisive action
    RECKLESS = "reckless"  # Too bold, insufficient consideration
    COURAGEOUS = "courageous"  # Bold decisions with appropriate risk assessment


class DirectiveType(Enum):
    """Types of directives/slash commands"""
    SLASH_COMMAND = "slash_command"  # /command format
    DOIT_COMMAND = "doit_command"  # @doit or @DOIT
    EXPLICIT_DIRECTIVE = "explicit_directive"  # Clear "do this" instruction
    IMPLIED_DIRECTIVE = "implied_directive"  # Context suggests action needed


@dataclass
class ContextualProblem:
    """A contextual problem requiring evaluation"""
    problem_id: str
    context: str
    question: Optional[str] = None
    requires_courage: bool = True
    risk_level: str = "medium"  # low, medium, high
    directive_type: Optional[DirectiveType] = None
    evaluation: Optional[str] = None
    decision: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class DebriefQuestion:
    """A question to ask during debrief/summary"""
    question_id: str
    question: str
    context: str
    priority: str = "medium"  # low, medium, high, critical
    category: str = "clarification"  # clarification, risk_assessment, optimization, edge_case
    timestamp: datetime = field(default_factory=datetime.now)
    answered: bool = False
    answer: Optional[str] = None


@dataclass
class EvaluationResult:
    """Result of JARVIS evaluation"""
    evaluation_id: str
    scope: str  # What was evaluated
    courage_level: CourageLevel
    questions_asked: List[DebriefQuestion] = field(default_factory=list)
    problems_identified: List[ContextualProblem] = field(default_factory=list)
    decisions_made: List[Dict[str, Any]] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class JARVISCourageEvaluationSystem:
    """
    JARVIS Courage Evaluation System

    Evaluates everything in @lumina with courage in contextual problems.
    Allows asking questions during debrief/summary.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Courage Evaluation System"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(exist_ok=True)

        self.data_dir = self.project_root / "data" / "jarvis_evaluations"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load configuration
        self.config_file = self.config_dir / "jarvis_courage_eval_config.json"
        self.config = self._load_config()

        # Evaluation history
        self.evaluation_history: List[EvaluationResult] = []
        self.history_file = self.data_dir / "evaluation_history.jsonl"

        logger.info("=" * 80)
        logger.info("🛡️  JARVIS COURAGE EVALUATION SYSTEM INITIALIZED")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info("   Principles:")
        logger.info("   - Slash commands = Directives: 'HERE DO THIS!'")
        logger.info("   - Courage = Proactive decision-making")
        logger.info("   - Questions = Clarification, not hesitation")
        logger.info("   - Contextual problems = Real-world judgment")
        logger.info("=" * 80)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration"""
        default_config = {
            "courage_threshold": "balanced",
            "allow_questions": True,
            "question_priority_threshold": "medium",
            "evaluation_scope": "full",  # full, targeted, specific
            "directive_recognition": {
                "slash_commands": True,
                "doit_commands": True,
                "explicit_directives": True,
                "implied_directives": True
            },
            "courage_guidelines": {
                "excessive_caution_penalty": 0.3,
                "balanced_bonus": 0.5,
                "courageous_bonus": 0.8,
                "reckless_penalty": 0.2
            }
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                logger.warning(f"⚠️  Error loading config: {e}, using defaults")

        return default_config

    def recognize_directive(self, text: str) -> Optional[DirectiveType]:
        """
        Recognize if text contains a directive

        Slash commands = Directives: "HERE DO THIS!"
        """
        text_lower = text.lower()

        # Slash commands
        if self.config["directive_recognition"]["slash_commands"]:
            if text.startswith("/") and len(text) > 1:
                return DirectiveType.SLASH_COMMAND

        # @DOIT commands
        if self.config["directive_recognition"]["doit_commands"]:
            if "@doit" in text_lower or "@DOIT" in text_lower:
                return DirectiveType.DOIT_COMMAND

        # Explicit directives
        if self.config["directive_recognition"]["explicit_directives"]:
            explicit_patterns = [
                "do this", "execute", "run", "implement", "create",
                "here do", "please do", "make it so"
            ]
            if any(pattern in text_lower for pattern in explicit_patterns):
                return DirectiveType.EXPLICIT_DIRECTIVE

        # Implied directives (context suggests action)
        if self.config["directive_recognition"]["implied_directives"]:
            implied_patterns = [
                "should", "need to", "must", "required", "expected"
            ]
            if any(pattern in text_lower for pattern in implied_patterns):
                return DirectiveType.IMPLIED_DIRECTIVE

        return None

    def evaluate_courage_level(self, 
                               problems: List[ContextualProblem],
                               questions: List[DebriefQuestion],
                               decisions: List[Dict[str, Any]]) -> CourageLevel:
        """
        Evaluate courage level based on problems, questions, and decisions

        Courage = Proactive decision-making, not excessive caution
        """
        # Count metrics
        total_problems = len(problems)
        total_questions = len(questions)
        total_decisions = len(decisions)

        # High-risk problems requiring courage
        high_risk_problems = sum(1 for p in problems if p.risk_level == "high")

        # Excessive caution indicators
        low_priority_questions = sum(1 for q in questions if q.priority == "low")
        unanswered_questions = sum(1 for q in questions if not q.answered)

        # Decision-making indicators
        decisive_actions = sum(1 for d in decisions if d.get("action_taken", False))

        # Calculate courage score
        courage_score = 0.0

        # Base score from decisions
        if total_problems > 0:
            decision_ratio = total_decisions / total_problems
            courage_score += decision_ratio * 0.4

        # Bonus for handling high-risk problems
        if total_problems > 0:
            risk_ratio = high_risk_problems / total_problems
            courage_score += risk_ratio * 0.3

        # Penalty for excessive questions
        if total_questions > 0:
            question_ratio = low_priority_questions / total_questions
            courage_score -= question_ratio * 0.2

        # Penalty for unanswered questions
        if total_questions > 0:
            unanswered_ratio = unanswered_questions / total_questions
            courage_score -= unanswered_ratio * 0.1

        # Determine courage level
        if courage_score < 0.3:
            return CourageLevel.EXCESSIVE_CAUTION
        elif courage_score < 0.6:
            return CourageLevel.BALANCED
        elif courage_score < 0.8:
            return CourageLevel.COURAGEOUS
        else:
            return CourageLevel.RECKLESS

    def identify_contextual_problems(self, 
                                     scope: str = "full") -> List[ContextualProblem]:
        """
        Identify contextual problems in @lumina

        Contextual problems = Real-world scenarios requiring judgment
        """
        problems = []

        logger.info(f"🔍 Identifying contextual problems (scope: {scope})...")

        # Example contextual problems (expand based on actual evaluation)
        if scope in ["full", "targeted"]:
            # Problem: Model deployment uncertainty
            problems.append(ContextualProblem(
                problem_id="model_deployment_uncertainty",
                context="Iron Legion model deployment - model name format unclear",
                question="Should we use llama3.2:latest or llama3.2:11b?",
                requires_courage=True,
                risk_level="medium",
                directive_type=DirectiveType.DOIT_COMMAND,
                evaluation="Model name format mismatch between expected and actual Ollama registry",
                decision="Use llama3.2:latest (actual Ollama name) with mapping to expected name"
            ))

            # Problem: File location uncertainty
            problems.append(ContextualProblem(
                problem_id="file_location_uncertainty",
                context="Downloaded model files - location unclear",
                question="Where did the files move to? Should we search or re-download?",
                requires_courage=True,
                risk_level="low",
                directive_type=DirectiveType.EXPLICIT_DIRECTIVE,
                evaluation="Files may have been moved or saved to different location",
                decision="Search comprehensively, then move to correct location if found"
            ))

        logger.info(f"   ✅ Identified {len(problems)} contextual problems")
        return problems

    def generate_debrief_questions(self,
                                  problems: List[ContextualProblem],
                                  evaluation: EvaluationResult) -> List[DebriefQuestion]:
        """
        Generate questions to ask during debrief/summary

        Questions = Clarification, not hesitation
        """
        questions = []

        if not self.config["allow_questions"]:
            return questions

        logger.info("💬 Generating debrief questions...")

        # Generate questions based on problems
        for problem in problems:
            if problem.question:
                questions.append(DebriefQuestion(
                    question_id=f"q_{problem.problem_id}",
                    question=problem.question,
                    context=problem.context,
                    priority="high" if problem.risk_level == "high" else "medium",
                    category="clarification"
                ))

        # Generate optimization questions
        if evaluation.courage_level == CourageLevel.EXCESSIVE_CAUTION:
            questions.append(DebriefQuestion(
                question_id="optimization_courage",
                question="Could we have been more decisive in any scenarios?",
                context="Courage evaluation - excessive caution detected",
                priority="medium",
                category="optimization"
            ))

        # Generate edge case questions
        if any(p.risk_level == "high" for p in problems):
            questions.append(DebriefQuestion(
                question_id="edge_case_handling",
                question="Are there edge cases we should consider for high-risk scenarios?",
                context="High-risk problems identified",
                priority="high",
                category="edge_case"
            ))

        # Filter by priority threshold
        threshold = self.config["question_priority_threshold"]
        priority_order = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        threshold_level = priority_order.get(threshold, 2)

        filtered_questions = [
            q for q in questions
            if priority_order.get(q.priority, 2) >= threshold_level
        ]

        logger.info(f"   ✅ Generated {len(filtered_questions)} debrief questions")
        return filtered_questions

    def evaluate_lumina(self, scope: str = "full") -> EvaluationResult:
        """
        Evaluate everything in @lumina with courage

        Main evaluation function
        """
        logger.info("=" * 80)
        logger.info("🛡️  JARVIS COURAGE EVALUATION")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info(f"   Scope: {scope}")
        logger.info("=" * 80)

        # Identify contextual problems
        problems = self.identify_contextual_problems(scope)

        # Track decisions made
        decisions = []
        for problem in problems:
            if problem.decision:
                decisions.append({
                    "problem_id": problem.problem_id,
                    "decision": problem.decision,
                    "action_taken": True,
                    "timestamp": problem.timestamp.isoformat()
                })

        # Create evaluation result
        evaluation = EvaluationResult(
            evaluation_id=f"eval_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            scope=scope,
            courage_level=CourageLevel.BALANCED,  # Will be calculated
            problems_identified=problems,
            decisions_made=decisions
        )

        # Generate debrief questions
        questions = self.generate_debrief_questions(problems, evaluation)
        evaluation.questions_asked = questions

        # Evaluate courage level
        evaluation.courage_level = self.evaluate_courage_level(
            problems, questions, decisions
        )

        # Generate recommendations
        evaluation.recommendations = self._generate_recommendations(evaluation)

        # Save evaluation
        self._save_evaluation(evaluation)
        self.evaluation_history.append(evaluation)

        # Display results
        self._display_evaluation(evaluation)

        return evaluation

    def _generate_recommendations(self, evaluation: EvaluationResult) -> List[str]:
        """Generate recommendations based on evaluation"""
        recommendations = []

        # Courage-based recommendations
        if evaluation.courage_level == CourageLevel.EXCESSIVE_CAUTION:
            recommendations.append(
                "Increase decisiveness - reduce excessive caution in low-risk scenarios"
            )
        elif evaluation.courage_level == CourageLevel.RECKLESS:
            recommendations.append(
                "Add more risk assessment - balance boldness with consideration"
            )

        # Problem-based recommendations
        high_risk_count = sum(1 for p in evaluation.problems_identified if p.risk_level == "high")
        if high_risk_count > 0:
            recommendations.append(
                f"Review {high_risk_count} high-risk problems for additional safeguards"
            )

        # Question-based recommendations
        unanswered = sum(1 for q in evaluation.questions_asked if not q.answered)
        if unanswered > 0:
            recommendations.append(
                f"Address {unanswered} unanswered debrief questions"
            )

        return recommendations

    def _save_evaluation(self, evaluation: EvaluationResult):
        """Save evaluation to history"""
        try:
            eval_dict = asdict(evaluation)
            # Convert enums to strings
            eval_dict["courage_level"] = evaluation.courage_level.value
            for problem in eval_dict["problems_identified"]:
                if problem.get("directive_type"):
                    problem["directive_type"] = problem["directive_type"].value

            with open(self.history_file, 'a') as f:
                f.write(json.dumps(eval_dict, default=str) + '\n')

            logger.info(f"   💾 Evaluation saved: {evaluation.evaluation_id}")
        except Exception as e:
            logger.error(f"   ❌ Error saving evaluation: {e}")

    def _display_evaluation(self, evaluation: EvaluationResult):
        """Display evaluation results"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 EVALUATION RESULTS")
        logger.info("=" * 80)

        logger.info(f"   Evaluation ID: {evaluation.evaluation_id}")
        logger.info(f"   Scope: {evaluation.scope}")
        logger.info(f"   Courage Level: {evaluation.courage_level.value.upper()}")
        logger.info(f"   Problems Identified: {len(evaluation.problems_identified)}")
        logger.info(f"   Decisions Made: {len(evaluation.decisions_made)}")
        logger.info(f"   Questions Asked: {len(evaluation.questions_asked)}")

        if evaluation.problems_identified:
            logger.info("")
            logger.info("   🔍 Contextual Problems:")
            for problem in evaluation.problems_identified:
                logger.info(f"      - {problem.problem_id}: {problem.context}")
                if problem.question:
                    logger.info(f"        Q: {problem.question}")
                if problem.decision:
                    logger.info(f"        Decision: {problem.decision}")

        if evaluation.questions_asked:
            logger.info("")
            logger.info("   💬 Debrief Questions:")
            for question in evaluation.questions_asked:
                status = "✅" if question.answered else "❓"
                logger.info(f"      {status} [{question.priority.upper()}] {question.question}")

        if evaluation.recommendations:
            logger.info("")
            logger.info("   💡 Recommendations:")
            for rec in evaluation.recommendations:
                logger.info(f"      - {rec}")

        logger.info("=" * 80)

    def answer_question(self, question_id: str, answer: str):
        """Answer a debrief question"""
        for evaluation in self.evaluation_history:
            for question in evaluation.questions_asked:
                if question.question_id == question_id:
                    question.answered = True
                    question.answer = answer
                    logger.info(f"   ✅ Question answered: {question_id}")
                    return

        logger.warning(f"   ⚠️  Question not found: {question_id}")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Courage Evaluation System")
    parser.add_argument("--scope", default="full", choices=["full", "targeted", "specific"],
                       help="Evaluation scope")
    parser.add_argument("--question-id", help="Answer a specific question")
    parser.add_argument("--answer", help="Answer to the question")

    args = parser.parse_args()

    system = JARVISCourageEvaluationSystem()

    if args.question_id and args.answer:
        system.answer_question(args.question_id, args.answer)
    else:
        evaluation = system.evaluate_lumina(scope=args.scope)
        return 0


if __name__ == "__main__":


    sys.exit(main())