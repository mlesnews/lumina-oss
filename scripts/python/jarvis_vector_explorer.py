#!/usr/bin/env python3
"""
JARVIS Vector Explorer - Human-Inspired Teammate

JARVIS as a real human-inspired teammate that:
- Asks the human/IDE operator questions
- Identifies, maps out, and explores all different vectors
- Analyzes vectors and considers correct paths
- Uses fly pathfinder logic (pathfinding)
- Uses decision tree for decisioning

This is the full-circle back to JARVIS as the core teammate.
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import json
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
    DECISION_TREE_AVAILABLE = True
except ImportError:
    DECISION_TREE_AVAILABLE = False
    decide = None
    DecisionContext = None
    DecisionOutcome = None

logger = get_logger("JARVISVectorExplorer")


class VectorType(Enum):
    """Types of vectors to explore"""
    TECHNICAL = "technical"
    BUSINESS = "business"
    SECURITY = "security"
    PERFORMANCE = "performance"
    RELIABILITY = "reliability"
    COMPLIANCE = "compliance"
    USER_EXPERIENCE = "user_experience"
    COST = "cost"
    TIME = "time"
    RISK = "risk"


class PathStatus(Enum):
    """Path exploration status"""
    IDENTIFIED = "identified"
    EXPLORING = "exploring"
    ANALYZED = "analyzed"
    EVALUATED = "evaluated"
    RECOMMENDED = "recommended"
    REJECTED = "rejected"


@dataclass
class Vector:
    """A vector to explore"""
    vector_id: str
    vector_type: VectorType
    name: str
    description: str
    questions: List[str] = field(default_factory=list)
    data_points: Dict[str, Any] = field(default_factory=dict)
    analysis: Optional[str] = None
    confidence: float = 0.0  # 0.0 to 1.0
    priority: int = 0  # 0-10, higher = more important
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PathForward:
    """A path forward"""
    path_id: str
    name: str
    description: str
    vectors: List[str]  # Vector IDs this path addresses
    decision_context: Optional[Dict[str, Any]] = None
    decision_outcome: Optional[Dict[str, Any]] = None
    status: PathStatus = PathStatus.IDENTIFIED
    feasibility: float = 0.0  # 0.0 to 1.0
    impact: float = 0.0  # 0.0 to 1.0
    effort: float = 0.0  # 0.0 to 1.0
    recommendation_score: float = 0.0  # Calculated score
    metadata: Dict[str, Any] = field(default_factory=dict)


class JARVISVectorExplorer:
    """
    JARVIS Vector Explorer - Human-Inspired Teammate

    JARVIS asks questions, explores vectors, uses pathfinding,
    and decision trees to help the human operator make decisions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("JARVISVectorExplorer")

        self.data_dir = self.project_root / "data" / "jarvis" / "vector_explorer"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.vectors: Dict[str, Vector] = {}
        self.paths: Dict[str, PathForward] = {}
        self.questions_asked: List[Dict[str, Any]] = []
        self.human_responses: Dict[str, Any] = {}

        self.logger.info("🤖 JARVIS Vector Explorer initialized")
        self.logger.info("   Role: Human-inspired teammate")
        self.logger.info("   Capabilities: Question asking, vector exploration, pathfinding, decisioning")

    def ask_human_question(self, question: str, context: str = "", options: List[str] = None) -> Dict[str, Any]:
        """
        Ask the human/IDE operator a question

        This is the core of JARVIS as a teammate - asking questions
        to understand the situation and gather information.
        """
        question_id = f"q_{datetime.now().timestamp()}"

        question_data = {
            "question_id": question_id,
            "question": question,
            "context": context,
            "options": options or [],
            "asked_at": datetime.now().isoformat(),
            "answered": False,
            "response": None
        }

        self.questions_asked.append(question_data)

        self.logger.info(f"🤖 JARVIS: {question}")
        if context:
            self.logger.info(f"   Context: {context}")
        if options:
            self.logger.info(f"   Options: {', '.join(options)}")

        # In IDE-style, this would be displayed to the user
        # For now, we'll return the question for the user to answer

        return question_data

    def identify_vectors(self, problem_description: str) -> List[Vector]:
        """
        Identify all different vectors to explore

        JARVIS analyzes the problem and identifies all possible
        vectors (dimensions) to explore.
        """
        self.logger.info("🔍 JARVIS: Identifying vectors to explore...")

        vectors = []

        # Technical vector
        vectors.append(Vector(
            vector_id="vec_technical",
            vector_type=VectorType.TECHNICAL,
            name="Technical Implementation",
            description="Technical aspects, architecture, implementation details",
            questions=[
                "What technologies are involved?",
                "What are the technical constraints?",
                "What is the current architecture?",
                "What are the technical requirements?"
            ],
            priority=8
        ))

        # Business vector
        vectors.append(Vector(
            vector_id="vec_business",
            vector_type=VectorType.BUSINESS,
            name="Business Impact",
            description="Business value, ROI, stakeholder impact",
            questions=[
                "What is the business value?",
                "Who are the stakeholders?",
                "What is the expected ROI?",
                "What are the business requirements?"
            ],
            priority=7
        ))

        # Security vector
        vectors.append(Vector(
            vector_id="vec_security",
            vector_type=VectorType.SECURITY,
            name="Security Considerations",
            description="Security implications, threats, compliance",
            questions=[
                "What are the security implications?",
                "What threats need to be considered?",
                "What compliance requirements exist?",
                "What security controls are needed?"
            ],
            priority=9
        ))

        # Performance vector
        vectors.append(Vector(
            vector_id="vec_performance",
            vector_type=VectorType.PERFORMANCE,
            name="Performance Requirements",
            description="Performance, scalability, efficiency",
            questions=[
                "What are the performance requirements?",
                "What is the expected load?",
                "What are the scalability needs?",
                "What are the efficiency goals?"
            ],
            priority=6
        ))

        # Risk vector
        vectors.append(Vector(
            vector_id="vec_risk",
            vector_type=VectorType.RISK,
            name="Risk Assessment",
            description="Risks, mitigation strategies, worst-case scenarios",
            questions=[
                "What are the potential risks?",
                "What is the worst-case scenario?",
                "What mitigation strategies exist?",
                "What is the risk tolerance?"
            ],
            priority=8
        ))

        # Store vectors
        for vector in vectors:
            self.vectors[vector.vector_id] = vector

        self.logger.info(f"✅ JARVIS: Identified {len(vectors)} vectors to explore")

        return vectors

    def explore_vector(self, vector_id: str, human_responses: Dict[str, Any] = None) -> Vector:
        """
        Explore a vector by asking questions and gathering data

        JARVIS asks questions to the human operator and explores
        the vector in depth.
        """
        if vector_id not in self.vectors:
            raise ValueError(f"Vector not found: {vector_id}")

        vector = self.vectors[vector_id]
        self.logger.info(f"🔍 JARVIS: Exploring vector - {vector.name}")

        # Ask questions for this vector
        for question in vector.questions:
            question_data = self.ask_human_question(
                question=question,
                context=f"Exploring {vector.name} vector",
                options=None
            )

            # If human responses provided, use them
            if human_responses and question_data["question_id"] in human_responses:
                vector.data_points[question] = human_responses[question_data["question_id"]]
                question_data["answered"] = True
                question_data["response"] = human_responses[question_data["question_id"]]

        # Analyze the vector
        vector.analysis = self._analyze_vector(vector)
        vector.confidence = self._calculate_confidence(vector)

        self.logger.info(f"✅ JARVIS: Explored {vector.name} (confidence: {vector.confidence:.0%})")

        return vector

    def _analyze_vector(self, vector: Vector) -> str:
        """Analyze a vector based on gathered data"""
        if not vector.data_points:
            return "No data gathered yet - need human input"

        analysis = f"Analysis of {vector.name}:\n"
        analysis += f"- Data points collected: {len(vector.data_points)}\n"
        analysis += f"- Vector type: {vector.vector_type.value}\n"
        analysis += f"- Priority: {vector.priority}/10\n"

        # Add specific analysis based on vector type
        if vector.vector_type == VectorType.SECURITY:
            analysis += "- Security implications identified\n"
            analysis += "- Threat assessment needed\n"
        elif vector.vector_type == VectorType.TECHNICAL:
            analysis += "- Technical requirements identified\n"
            analysis += "- Architecture considerations noted\n"
        elif vector.vector_type == VectorType.RISK:
            analysis += "- Risks identified\n"
            analysis += "- Mitigation strategies considered\n"

        return analysis

    def _calculate_confidence(self, vector: Vector) -> float:
        """Calculate confidence in vector exploration"""
        if not vector.data_points:
            return 0.0

        # More data points = higher confidence
        base_confidence = min(len(vector.data_points) / len(vector.questions), 1.0)

        # Adjust based on vector type priority
        priority_multiplier = vector.priority / 10.0

        return base_confidence * priority_multiplier

    def find_paths_forward(self, vectors: List[str] = None) -> List[PathForward]:
        """
        Use fly pathfinder logic to find paths forward

        JARVIS uses pathfinding to identify possible paths
        based on explored vectors.
        """
        self.logger.info("🛤️  JARVIS: Finding paths forward (fly pathfinder logic)...")

        if vectors is None:
            vectors = list(self.vectors.keys())

        paths = []

        # Path 1: Direct implementation
        paths.append(PathForward(
            path_id="path_direct",
            name="Direct Implementation",
            description="Implement directly without additional exploration",
            vectors=vectors,
            feasibility=0.8,
            impact=0.7,
            effort=0.6,
            status=PathStatus.IDENTIFIED
        ))

        # Path 2: Phased approach
        paths.append(PathForward(
            path_id="path_phased",
            name="Phased Implementation",
            description="Implement in phases with validation at each step",
            vectors=vectors,
            feasibility=0.9,
            impact=0.8,
            effort=0.7,
            status=PathStatus.IDENTIFIED
        ))

        # Path 3: Proof of concept
        paths.append(PathForward(
            path_id="path_poc",
            name="Proof of Concept",
            description="Build proof of concept first, then full implementation",
            vectors=vectors,
            feasibility=0.95,
            impact=0.6,
            effort=0.5,
            status=PathStatus.IDENTIFIED
        ))

        # Path 4: Research and design
        paths.append(PathForward(
            path_id="path_research",
            name="Research and Design",
            description="Research options, design solution, then implement",
            vectors=vectors,
            feasibility=0.9,
            impact=0.9,
            effort=0.8,
            status=PathStatus.IDENTIFIED
        ))

        # Store paths
        for path in paths:
            self.paths[path.path_id] = path

        self.logger.info(f"✅ JARVIS: Found {len(paths)} paths forward")

        return paths

    def analyze_paths(self, paths: List[str] = None) -> List[PathForward]:
        """
        Analyze paths using decision tree

        JARVIS uses decision tree logic to analyze and evaluate paths.
        """
        self.logger.info("🧠 JARVIS: Analyzing paths with decision tree...")

        if paths is None:
            paths = list(self.paths.keys())

        analyzed_paths = []

        for path_id in paths:
            path = self.paths[path_id]

            # Use decision tree if available
            if DECISION_TREE_AVAILABLE:
                decision_context = DecisionContext(
                    complexity="medium",
                    urgency="medium",
                    cost_sensitive=True,
                    custom_data={
                        "scenario": f"Evaluate path: {path.name}",
                        "available_options": [p.name for p in self.paths.values()],
                        "feasibility": path.feasibility,
                        "impact": path.impact,
                        "effort": path.effort,
                        "path_id": path_id,
                        "vectors": path.vectors
                    }
                )

                # Decide using decision tree
                outcome = decide("path_evaluation", decision_context)

                path.decision_context = decision_context.__dict__ if hasattr(decision_context, '__dict__') else {}
                path.decision_outcome = outcome.__dict__ if hasattr(outcome, '__dict__') else {}

                # Calculate recommendation score
                path.recommendation_score = self._calculate_recommendation_score(path, outcome)
            else:
                # Fallback: simple scoring
                path.recommendation_score = (path.feasibility + path.impact - path.effort) / 3.0

            path.status = PathStatus.ANALYZED
            analyzed_paths.append(path)

            self.logger.info(f"  ✅ Analyzed: {path.name} (score: {path.recommendation_score:.2f})")

        return analyzed_paths

    def _calculate_recommendation_score(self, path: PathForward, outcome: Any) -> float:
        """Calculate recommendation score for a path"""
        # Base score from path metrics
        base_score = (path.feasibility * 0.4 + path.impact * 0.4 + (1 - path.effort) * 0.2)

        # Adjust based on decision outcome if available
        if outcome and hasattr(outcome, 'confidence'):
            decision_confidence = getattr(outcome, 'confidence', 0.5)
            base_score = base_score * 0.7 + decision_confidence * 0.3

        return base_score

    def recommend_path(self, paths: List[str] = None) -> Optional[PathForward]:
        """
        Recommend the best path forward

        JARVIS analyzes all paths and recommends the best one.
        """
        if paths is None:
            paths = list(self.paths.keys())

        # Analyze paths first
        analyzed_paths = self.analyze_paths(paths)

        # Sort by recommendation score
        analyzed_paths.sort(key=lambda p: p.recommendation_score, reverse=True)

        if analyzed_paths:
            recommended = analyzed_paths[0]
            recommended.status = PathStatus.RECOMMENDED

            self.logger.info(f"🎯 JARVIS: Recommended path - {recommended.name}")
            self.logger.info(f"   Score: {recommended.recommendation_score:.2f}")
            self.logger.info(f"   Feasibility: {recommended.feasibility:.0%}")
            self.logger.info(f"   Impact: {recommended.impact:.0%}")
            self.logger.info(f"   Effort: {recommended.effort:.0%}")

            return recommended

        return None

    def full_exploration_workflow(self, problem_description: str, human_responses: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Full workflow: Identify vectors → Explore → Find paths → Analyze → Recommend

        This is the complete JARVIS teammate workflow.
        """
        self.logger.info("🤖 JARVIS: Starting full exploration workflow...")
        self.logger.info(f"   Problem: {problem_description}")

        # Step 1: Identify vectors
        vectors = self.identify_vectors(problem_description)

        # Step 2: Explore vectors (ask questions)
        explored_vectors = []
        for vector in vectors:
            explored = self.explore_vector(vector.vector_id, human_responses)
            explored_vectors.append(explored)

        # Step 3: Find paths forward (pathfinding)
        paths = self.find_paths_forward([v.vector_id for v in explored_vectors])

        # Step 4: Analyze paths (decision tree)
        analyzed_paths = self.analyze_paths([p.path_id for p in paths])

        # Step 5: Recommend best path
        recommended_path = self.recommend_path([p.path_id for p in analyzed_paths])

        result = {
            "problem": problem_description,
            "vectors_identified": len(vectors),
            "vectors_explored": len(explored_vectors),
            "paths_found": len(paths),
            "paths_analyzed": len(analyzed_paths),
            "recommended_path": recommended_path.__dict__ if recommended_path else None,
            "questions_asked": len(self.questions_asked),
            "exploration_complete": datetime.now().isoformat()
        }

        self.logger.info("✅ JARVIS: Full exploration workflow complete")

        return result


def main():
    """CLI for JARVIS Vector Explorer"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Vector Explorer - Human-Inspired Teammate")
    parser.add_argument("--problem", help="Problem description to explore")
    parser.add_argument("--identify-vectors", action="store_true", help="Identify vectors")
    parser.add_argument("--explore-vector", help="Explore a specific vector")
    parser.add_argument("--find-paths", action="store_true", help="Find paths forward")
    parser.add_argument("--analyze-paths", action="store_true", help="Analyze paths")
    parser.add_argument("--recommend", action="store_true", help="Recommend best path")
    parser.add_argument("--full-workflow", action="store_true", help="Run full exploration workflow")

    args = parser.parse_args()

    jarvis = JARVISVectorExplorer()

    if args.full_workflow and args.problem:
        result = jarvis.full_exploration_workflow(args.problem)
        print(f"\n🤖 JARVIS Exploration Results:")
        print(f"  Vectors Identified: {result['vectors_identified']}")
        print(f"  Vectors Explored: {result['vectors_explored']}")
        print(f"  Paths Found: {result['paths_found']}")
        print(f"  Paths Analyzed: {result['paths_analyzed']}")
        if result['recommended_path']:
            print(f"\n  🎯 Recommended Path: {result['recommended_path']['name']}")
            print(f"     Score: {result['recommended_path']['recommendation_score']:.2f}")

    elif args.identify_vectors:
        vectors = jarvis.identify_vectors(args.problem or "General problem")
        print(f"\n🔍 Identified {len(vectors)} vectors:")
        for vector in vectors:
            print(f"  - {vector.name} ({vector.vector_type.value})")

    elif args.explore_vector:
        vector = jarvis.explore_vector(args.explore_vector)
        print(f"\n🔍 Explored: {vector.name}")
        print(f"  Confidence: {vector.confidence:.0%}")
        print(f"  Analysis: {vector.analysis}")

    elif args.find_paths:
        paths = jarvis.find_paths_forward()
        print(f"\n🛤️  Found {len(paths)} paths:")
        for path in paths:
            print(f"  - {path.name} (feasibility: {path.feasibility:.0%})")

    elif args.analyze_paths:
        analyzed = jarvis.analyze_paths()
        print(f"\n🧠 Analyzed {len(analyzed)} paths:")
        for path in analyzed:
            print(f"  - {path.name} (score: {path.recommendation_score:.2f})")

    elif args.recommend:
        recommended = jarvis.recommend_path()
        if recommended:
            print(f"\n🎯 Recommended: {recommended.name}")
            print(f"  Score: {recommended.recommendation_score:.2f}")
            print(f"  Feasibility: {recommended.feasibility:.0%}")
            print(f"  Impact: {recommended.impact:.0%}")
            print(f"  Effort: {recommended.effort:.0%}")

    else:
        parser.print_help()


if __name__ == "__main__":



    main()