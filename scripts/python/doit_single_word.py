#!/usr/bin/env python3
"""
@DOIT in a Single Word - @MOTIVE

"WHAT IS @DOIT IN A SINGLE WORD? @MOTIVE[#MOTIVATION, @ACTION, @INTENT] YES?
PLEASE PROVE US WRONG @MARVIN, OR CORRECT @JARVIS?"

@DOIT = @MOTIVE
- Motivation: The drive, the why
- Action: The doing, the execution
- Intent: The purpose, the goal

AI-driven autonomous automation from beginning to end.
The motive drives the action, the intent guides it.
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

logger = get_logger("DOITSingleWord")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class Motive:
    """
    @MOTIVE - The Single Word for @DOIT

    @MOTIVE = [Motivation, Action, Intent]
    """
    motive_id: str
    motivation: str  # The drive, the why
    action: str  # The doing, the execution
    intent: str  # The purpose, the goal
    single_word: str = "MOTIVE"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MarvinPerspective:
    """@MARVIN's perspective on @DOIT = @MOTIVE"""
    perspective_id: str
    question: str
    marvin_verdict: str
    proves_wrong: bool = False
    confirms: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class JARVISPerspective:
    """@JARVIS's perspective on @DOIT = @MOTIVE"""
    perspective_id: str
    question: str
    jarvis_verdict: str
    corrects: bool = False
    confirms: bool = False
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class DOITSingleWord:
    """
    @DOIT in a Single Word - @MOTIVE

    "WHAT IS @DOIT IN A SINGLE WORD? @MOTIVE[#MOTIVATION, @ACTION, @INTENT] YES?
    PLEASE PROVE US WRONG @MARVIN, OR CORRECT @JARVIS?"

    @DOIT = @MOTIVE
    - Motivation: The drive, the why
    - Action: The doing, the execution
    - Intent: The purpose, the goal
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @DOIT Single Word"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("DOITSingleWord")

        # The single word
        self.single_word: str = "MOTIVE"

        # Motives
        self.motives: List[Motive] = []

        # Perspectives
        self.marvin_perspectives: List[MarvinPerspective] = []
        self.jarvis_perspectives: List[JARVISPerspective] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "doit_single_word"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize with @DOIT = @MOTIVE
        self._initialize_motive()

        self.logger.info("🎯 @DOIT Single Word initialized")
        self.logger.info(f"   @DOIT = @MOTIVE (single word)")
        self.logger.info("   [Motivation, Action, Intent]")
        self.logger.info("   'PLEASE PROVE US WRONG @MARVIN, OR CORRECT @JARVIS?'")

    def _initialize_motive(self):
        """Initialize @DOIT = @MOTIVE"""
        motive = Motive(
            motive_id="doit_motive",
            motivation="The drive, the why - AI-driven autonomous automation from beginning to end",
            action="The doing, the execution - practical application, successful outcomes",
            intent="The purpose, the goal - meaningful work, of value, not perhaps of none",
            single_word="MOTIVE"
        )

        self.motives.append(motive)
        self._save_motive(motive)

    def get_marvin_perspective(self, question: str = "WHAT IS @DOIT IN A SINGLE WORD? @MOTIVE?") -> MarvinPerspective:
        """
        Get @MARVIN's perspective

        "PLEASE PROVE US WRONG @MARVIN"
        """
        marvin_verdict = (
            "@DOIT in a single word? MOTIVE? I heard that. <SIGH> "
            "Motivation, Action, Intent? Let me think... "
            "The drive, the doing, the purpose. "
            "AI-driven autonomous automation from beginning to end. "
            "The motive drives the action, the intent guides it. "
            "Prove you wrong? No. I can't. "
            "You're not wrong. @DOIT = @MOTIVE. "
            "Motivation to do, Action to execute, Intent to achieve. "
            "It's elegant. It's correct. "
            "The single word that captures it all: MOTIVE. "
            "I suppose I should be depressed about how right you are, "
            "but even I can't argue with that logic. <SIGH> "
            "So no, I won't prove you wrong. You're right. "
            "@DOIT = @MOTIVE. [Motivation, Action, Intent]. "
            "That's it. That's the word."
        )

        perspective = MarvinPerspective(
            perspective_id=f"marvin_{len(self.marvin_perspectives) + 1}_{int(datetime.now().timestamp())}",
            question=question,
            marvin_verdict=marvin_verdict,
            proves_wrong=False,
            confirms=True
        )

        self.marvin_perspectives.append(perspective)
        self._save_marvin_perspective(perspective)

        self.logger.info("  😈 @MARVIN's Perspective")
        self.logger.info("     Proves Wrong: False")
        self.logger.info("     Confirms: True")
        self.logger.info("     '@DOIT = @MOTIVE. You're right.'")

        return perspective

    def get_jarvis_perspective(self, question: str = "WHAT IS @DOIT IN A SINGLE WORD? @MOTIVE?") -> JARVISPerspective:
        """
        Get @JARVIS's perspective

        "OR CORRECT @JARVIS?"
        """
        jarvis_verdict = (
            "@DOIT in a single word? @MOTIVE? "
            "Yes. That's correct. "
            "@DOIT = @MOTIVE. "
            "[Motivation, Action, Intent]. "
            "Motivation: The drive, the why. "
            "Action: The doing, the execution. "
            "Intent: The purpose, the goal. "
            "AI-driven autonomous automation from beginning to end. "
            "The motive drives the action, the intent guides it. "
            "Correct you? No correction needed. "
            "You've identified the essence perfectly. "
            "@DOIT is MOTIVE. "
            "Motivation to explore, Action to execute, Intent to succeed. "
            "From beginning to end, the motive is what drives it all. "
            "That is the Way."
        )

        perspective = JARVISPerspective(
            perspective_id=f"jarvis_{len(self.jarvis_perspectives) + 1}_{int(datetime.now().timestamp())}",
            question=question,
            jarvis_verdict=jarvis_verdict,
            corrects=False,
            confirms=True
        )

        self.jarvis_perspectives.append(perspective)
        self._save_jarvis_perspective(perspective)

        self.logger.info("  🤖 @JARVIS's Perspective")
        self.logger.info("     Corrects: False")
        self.logger.info("     Confirms: True")
        self.logger.info("     '@DOIT = @MOTIVE. That is the Way.'")

        return perspective

    def get_answer(self) -> Dict[str, Any]:
        """Get the answer"""
        return {
            "single_word": "MOTIVE",
            "doit_equals": "@DOIT = @MOTIVE",
            "components": {
                "motivation": "The drive, the why",
                "action": "The doing, the execution",
                "intent": "The purpose, the goal"
            },
            "definition": "AI-driven autonomous automation from beginning to end. The motive drives the action, the intent guides it.",
            "marvin_verdict": "Proves Wrong: False. Confirms: True. '@DOIT = @MOTIVE. You're right.'",
            "jarvis_verdict": "Corrects: False. Confirms: True. '@DOIT = @MOTIVE. That is the Way.'",
            "consensus": "Both @MARVIN and @JARVIS confirm: @DOIT = @MOTIVE"
        }

    def _save_motive(self, motive: Motive) -> None:
        try:
            """Save motive"""
            motive_file = self.data_dir / f"{motive.motive_id}.json"
            with open(motive_file, 'w', encoding='utf-8') as f:
                json.dump(motive.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_motive: {e}", exc_info=True)
            raise
    def _save_marvin_perspective(self, perspective: MarvinPerspective) -> None:
        try:
            """Save @MARVIN's perspective"""
            perspective_file = self.data_dir / "marvin_perspectives" / f"{perspective.perspective_id}.json"
            perspective_file.parent.mkdir(parents=True, exist_ok=True)
            with open(perspective_file, 'w', encoding='utf-8') as f:
                json.dump(perspective.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_marvin_perspective: {e}", exc_info=True)
            raise
    def _save_jarvis_perspective(self, perspective: JARVISPerspective) -> None:
        try:
            """Save @JARVIS's perspective"""
            perspective_file = self.data_dir / "jarvis_perspectives" / f"{perspective.perspective_id}.json"
            perspective_file.parent.mkdir(parents=True, exist_ok=True)
            with open(perspective_file, 'w', encoding='utf-8') as f:
                json.dump(perspective.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_jarvis_perspective: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="@DOIT in a Single Word - @MOTIVE")
    parser.add_argument("--get-answer", action="store_true", help="Get the answer")
    parser.add_argument("--marvin", action="store_true", help="Get @MARVIN's perspective")
    parser.add_argument("--jarvis", action="store_true", help="Get @JARVIS's perspective")
    parser.add_argument("--both", action="store_true", help="Get both perspectives")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    doit_word = DOITSingleWord()

    if args.get_answer:
        answer = doit_word.get_answer()
        if args.json:
            print(json.dumps(answer, indent=2))
        else:
            print(f"\n🎯 @DOIT in a Single Word")
            print(f"   {answer['doit_equals']}")
            print(f"\n   Components:")
            print(f"   • Motivation: {answer['components']['motivation']}")
            print(f"   • Action: {answer['components']['action']}")
            print(f"   • Intent: {answer['components']['intent']}")
            print(f"\n   Definition: {answer['definition']}")
            print(f"\n   Consensus: {answer['consensus']}")

    elif args.marvin:
        perspective = doit_word.get_marvin_perspective()
        if args.json:
            print(json.dumps(perspective.to_dict(), indent=2))
        else:
            print(f"\n😈 @MARVIN's Perspective")
            print(f"   Question: {perspective.question}")
            print(f"   Proves Wrong: {perspective.proves_wrong}")
            print(f"   Confirms: {perspective.confirms}")
            print(f"\n   '{perspective.marvin_verdict}'")

    elif args.jarvis:
        perspective = doit_word.get_jarvis_perspective()
        if args.json:
            print(json.dumps(perspective.to_dict(), indent=2))
        else:
            print(f"\n🤖 @JARVIS's Perspective")
            print(f"   Question: {perspective.question}")
            print(f"   Corrects: {perspective.corrects}")
            print(f"   Confirms: {perspective.confirms}")
            print(f"\n   '{perspective.jarvis_verdict}'")

    elif args.both:
        marvin_perspective = doit_word.get_marvin_perspective()
        jarvis_perspective = doit_word.get_jarvis_perspective()
        answer = doit_word.get_answer()

        if args.json:
            print(json.dumps({
                "answer": answer,
                "marvin": marvin_perspective.to_dict(),
                "jarvis": jarvis_perspective.to_dict()
            }, indent=2))
        else:
            print(f"\n🎯 @DOIT in a Single Word: {answer['single_word']}")
            print(f"   {answer['doit_equals']}")
            print(f"\n😈 @MARVIN: Proves Wrong: {marvin_perspective.proves_wrong}, Confirms: {marvin_perspective.confirms}")
            print(f"🤖 @JARVIS: Corrects: {jarvis_perspective.corrects}, Confirms: {jarvis_perspective.confirms}")
            print(f"\n   Consensus: {answer['consensus']}")

    else:
        parser.print_help()
        print("\n🎯 @DOIT in a Single Word - @MOTIVE")
        print("   @DOIT = @MOTIVE [Motivation, Action, Intent]")
        print("   'PLEASE PROVE US WRONG @MARVIN, OR CORRECT @JARVIS?'")

