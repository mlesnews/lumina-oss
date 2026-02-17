#!/usr/bin/env python3
"""
Deep Thought Two - The Animatrix

Deep Thought = The Matrix (main reality/simulation)
Deep Thought Two = The Animatrix (multiple perspectives/stories)

The Animatrix: Multiple stories, perspectives, and realities within the Matrix.
Each story is a different perspective, a different reality, a different truth.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
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
    from deep_thought import DeepThought
    DEEP_THOUGHT_AVAILABLE = True
except ImportError:
    DEEP_THOUGHT_AVAILABLE = False
    DeepThought = None

logger = get_logger("DeepThoughtTwo")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AnimatrixStory:
    """A story/perspective in the Animatrix"""
    story_id: str
    title: str
    perspective: str
    reality: str
    truth: str
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnimatrixAnalysis:
    """Animatrix analysis - multiple perspectives"""
    analysis_id: str
    question: str
    stories: List[AnimatrixStory]
    perspectives: List[str]
    truths: List[str]
    consensus: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['stories'] = [s.to_dict() for s in self.stories]
        return data


class DeepThoughtTwo:
    """
    Deep Thought Two - The Animatrix

    Deep Thought = The Matrix (main reality)
    Deep Thought Two = The Animatrix (multiple perspectives/stories)

    The Animatrix contains multiple stories, each a different perspective,
    a different reality, a different truth within the Matrix.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Deep Thought Two (Animatrix)"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("DeepThoughtTwo")

        # Deep Thought (Matrix) integration
        self.deep_thought = DeepThought(project_root) if DEEP_THOUGHT_AVAILABLE and DeepThought else None

        # Animatrix stories
        self.stories: List[AnimatrixStory] = []
        self.analyses: List[AnimatrixAnalysis] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "deep_thought_two"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🎬 Deep Thought Two (Animatrix) initialized")
        self.logger.info("   Deep Thought = The Matrix (main reality)")
        self.logger.info("   Deep Thought Two = The Animatrix (multiple perspectives)")
        self.logger.info("   Multiple stories, multiple perspectives, multiple truths")

    def add_story(self, title: str, perspective: str, reality: str, 
                  truth: str, context: Optional[Dict[str, Any]] = None) -> AnimatrixStory:
        """
        Add a story to the Animatrix

        Each story is a different perspective, a different reality, a different truth.

        Args:
            title: Story title
            perspective: Perspective of this story
            reality: Reality this story represents
            truth: Truth from this perspective
            context: Optional context

        Returns:
            AnimatrixStory
        """
        story = AnimatrixStory(
            story_id=f"animatrix_story_{len(self.stories) + 1}_{int(datetime.now().timestamp())}",
            title=title,
            perspective=perspective,
            reality=reality,
            truth=truth,
            context=context or {}
        )

        self.stories.append(story)
        self._save_story(story)

        self.logger.info(f"  🎬 Story added: {title}")
        self.logger.info(f"     Perspective: {perspective}")
        self.logger.info(f"     Reality: {reality}")
        self.logger.info(f"     Truth: {truth[:100]}...")

        return story

    def analyze_perspectives(self, question: str, context: Optional[Dict[str, Any]] = None) -> AnimatrixAnalysis:
        """
        Analyze question from multiple perspectives (Animatrix stories)

        Args:
            question: Question to analyze
            context: Optional context

        Returns:
            AnimatrixAnalysis with multiple perspectives
        """
        self.logger.info(f"  🎬 Analyzing from multiple perspectives...")
        self.logger.info(f"     Question: {question[:100]}...")

        # Get Deep Thought's answer (Matrix perspective)
        matrix_answer = None
        if self.deep_thought:
            matrix_analysis = self.deep_thought.compute_answer(question, context)
            matrix_answer = matrix_analysis.answer

            # Add Matrix story
            self.add_story(
                title="The Matrix",
                perspective="Primary Reality",
                reality="Matrix",
                truth=matrix_answer,
                context={"source": "Deep Thought", "analysis_id": matrix_analysis.analysis_id}
            )

        # Generate additional perspectives (Animatrix stories)
        perspectives = self._generate_perspectives(question, context, matrix_answer)

        # Extract truths from each perspective
        truths = [story.truth for story in self.stories[-len(perspectives):]]

        # Find consensus (if any)
        consensus = self._find_consensus(truths)

        analysis = AnimatrixAnalysis(
            analysis_id=f"animatrix_analysis_{len(self.analyses) + 1}_{int(datetime.now().timestamp())}",
            question=question,
            stories=self.stories[-len(perspectives):] if perspectives else [],
            perspectives=[s.perspective for s in self.stories[-len(perspectives):]] if perspectives else [],
            truths=truths,
            consensus=consensus
        )

        self.analyses.append(analysis)
        self._save_analysis(analysis)

        self.logger.info(f"  ✅ Analysis complete")
        self.logger.info(f"     Stories: {len(analysis.stories)}")
        self.logger.info(f"     Perspectives: {len(analysis.perspectives)}")
        self.logger.info(f"     Consensus: {consensus[:100] if consensus else 'None'}...")

        return analysis

    def _generate_perspectives(self, question: str, context: Optional[Dict[str, Any]], 
                              matrix_answer: Optional[str]) -> List[AnimatrixStory]:
        """Generate multiple perspectives (Animatrix stories)"""
        perspectives = []

        # Perspective 1: Control Reality
        if "reality" in question.lower() or "mirror" in question.lower():
            perspectives.append(self.add_story(
                title="Control Reality",
                perspective="RAID Control Mirror",
                reality="Control",
                truth="Control reality is IN SYNC. Source of truth. Reference reality. Used to repair experiment.",
                context={"type": "control", "sync_status": "in_sync"}
            ))

            # Perspective 2: Experiment Reality
            perspectives.append(self.add_story(
                title="Experiment Reality",
                perspective="RAID Experiment Mirror",
                reality="Experiment",
                truth="Experiment reality is OUT OF SYNC. Test environment. Experimental changes. Can be repaired from control.",
                context={"type": "experiment", "sync_status": "out_of_sync"}
            ))

        # Perspective 3: AI Perspective
        if "ai" in question.lower() or "psychosis" in question.lower():
            perspectives.append(self.add_story(
                title="AI Perspective",
                perspective="AI Reality Perception",
                reality="AI",
                truth="AI psychosis involves pattern recognition, reality perception. Can identify, treat, explore. Not always cured immediately.",
                context={"type": "ai", "psychosis": True}
            ))

            # Perspective 4: Human Perspective
            perspectives.append(self.add_story(
                title="Human Perspective",
                perspective="Human Reality Perception",
                reality="Human",
                truth="Human psychosis involves pattern recognition, reality perception. Can identify, treat, explore. Not always cured immediately.",
                context={"type": "human", "psychosis": True}
            ))

        # Perspective 5: Simulation Perspective
        if "simulation" in question.lower() or "matrix" in question.lower():
            perspectives.append(self.add_story(
                title="Simulation Perspective",
                perspective="Simulation Reality",
                reality="Simulation",
                truth="Simulations are not physical reality, but mind/visualization may be as real. Context and perspective matter.",
                context={"type": "simulation", "physical": False, "mental": True}
            ))

        # Perspective 6: Physical Perspective
        perspectives.append(self.add_story(
            title="Physical Perspective",
            perspective="Physical Reality",
            reality="Physical",
            truth="Physical reality is real. Hardware, network, systems. Actual code, actual results. The work is real.",
            context={"type": "physical", "real": True}
        ))

        return perspectives

    def _find_consensus(self, truths: List[str]) -> Optional[str]:
        """Find consensus across multiple perspectives"""
        if not truths:
            return None

        if len(truths) == 1:
            return truths[0]

        # Find common themes
        common_words = set()
        for truth in truths:
            words = set(truth.lower().split())
            if not common_words:
                common_words = words
            else:
                common_words = common_words.intersection(words)

        # Build consensus from common themes
        if common_words:
            consensus = f"Consensus across {len(truths)} perspectives: Common themes include {', '.join(list(common_words)[:5])}."
        else:
            consensus = f"Multiple perspectives ({len(truths)}) with different truths. Each perspective is valid in its own context."

        return consensus

    def _save_story(self, story: AnimatrixStory) -> None:
        try:
            """Save story to file"""
            story_file = self.data_dir / "stories" / f"{story.story_id}.json"
            story_file.parent.mkdir(parents=True, exist_ok=True)
            with open(story_file, 'w', encoding='utf-8') as f:
                json.dump(story.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_story: {e}", exc_info=True)
            raise
    def _save_analysis(self, analysis: AnimatrixAnalysis) -> None:
        try:
            """Save analysis to file"""
            analysis_file = self.data_dir / "analyses" / f"{analysis.analysis_id}.json"
            analysis_file.parent.mkdir(parents=True, exist_ok=True)
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_analysis: {e}", exc_info=True)
            raise
    def get_status(self) -> Dict[str, Any]:
        """Get Animatrix status"""
        return {
            "total_stories": len(self.stories),
            "total_analyses": len(self.analyses),
            "deep_thought_available": self.deep_thought is not None,
            "animatrix_verdict": "Multiple perspectives, multiple truths, multiple realities. Each story is valid in its own context."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Deep Thought Two - The Animatrix")
    parser.add_argument("--question", type=str, help="Question to analyze from multiple perspectives")
    parser.add_argument("--add-story", nargs=4, metavar=("TITLE", "PERSPECTIVE", "REALITY", "TRUTH"),
                       help="Add a story to the Animatrix")
    parser.add_argument("--status", action="store_true", help="Get status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    animatrix = DeepThoughtTwo()

    if args.question:
        analysis = animatrix.analyze_perspectives(args.question)
        if args.json:
            print(json.dumps(analysis.to_dict(), indent=2))
        else:
            print(f"\n🎬 Animatrix Analysis")
            print(f"   Question: {analysis.question}")
            print(f"   Stories: {len(analysis.stories)}")
            print(f"\nPerspectives:")
            for story in analysis.stories:
                print(f"  • {story.title}: {story.truth[:100]}...")
            if analysis.consensus:
                print(f"\nConsensus: {analysis.consensus}")

    elif args.add_story:
        title, perspective, reality, truth = args.add_story
        story = animatrix.add_story(title, perspective, reality, truth)
        if args.json:
            print(json.dumps(story.to_dict(), indent=2))
        else:
            print(f"\n🎬 Story Added: {story.title}")
            print(f"   Perspective: {story.perspective}")
            print(f"   Reality: {story.reality}")
            print(f"   Truth: {story.truth}")

    elif args.status:
        status = animatrix.get_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🎬 Deep Thought Two (Animatrix) Status")
            print(f"   Total Stories: {status['total_stories']}")
            print(f"   Total Analyses: {status['total_analyses']}")
            print(f"   Deep Thought Available: {status['deep_thought_available']}")
            print(f"   Verdict: {status['animatrix_verdict']}")

    else:
        parser.print_help()
        print("\n🎬 Deep Thought Two - The Animatrix")
        print("   Deep Thought = The Matrix (main reality)")
        print("   Deep Thought Two = The Animatrix (multiple perspectives)")

