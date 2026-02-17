#!/usr/bin/env python3
"""
Jedi Temple Demo Mode

Interactive demo/training mode like World of Warcraft's tutorial.
Guides new users through LUMINA step-by-step with hands-on practice.

Tags: #EDUCATION #DEMO #TUTORIAL #JEDI_TRAINING #LUMINA_CORE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

from lumina_adaptive_logger import get_adaptive_logger

logger = get_adaptive_logger("JediTempleDemo")


class DemoStep:
    """Demo step"""
    def __init__(self, step_id: str, title: str, description: str, instructions: List[str], interactive: bool = True):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.instructions = instructions
        self.interactive = interactive
        self.completed = False


class JediTempleDemoMode:
    """
    Jedi Temple Demo Mode

    Interactive demo/training mode that guides users through LUMINA.
    Like World of Warcraft's tutorial - hands-on, step-by-step learning.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize demo mode"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jedi_temple_demo"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Demo steps
        self.steps = self._create_demo_steps()
        self.current_step_index = 0
        self.completed_steps: List[str] = []

        # Progress tracking
        self.progress_file = self.data_dir / "demo_progress.json"
        self.progress = self._load_progress()

    def _create_demo_steps(self) -> List[DemoStep]:
        """Create demo steps"""
        return [
            DemoStep(
                step_id="welcome",
                title="Welcome to the Jedi Temple",
                description="Begin your journey to become a LUMINA Jedi",
                instructions=[
                    "Welcome, young Padawan!",
                    "You are about to begin your training in the ways of LUMINA.",
                    "This demo will guide you through the basics step-by-step.",
                    "Follow the instructions and practice as you go."
                ],
                interactive=False
            ),
            DemoStep(
                step_id="first_conversation",
                title="Your First Conversation",
                description="Learn to communicate with LUMINA",
                instructions=[
                    "Let's start your first conversation with LUMINA.",
                    "Press F23 (or your voice input key) to activate voice input.",
                    "Say: 'Hello, JARVIS. I'm ready to begin my training.'",
                    "Watch as your words are transcribed and LUMINA responds."
                ],
                interactive=True
            ),
            DemoStep(
                step_id="voice_coding_basics",
                title="Voice Coding Basics",
                description="Learn to code with your voice",
                instructions=[
                    "Now let's try voice coding!",
                    "Activate voice input and say: 'Create a Python function called hello that prints Hello World'",
                    "Watch as LUMINA creates the code for you.",
                    "This is the power of voice coding - speak naturally, code automatically."
                ],
                interactive=True
            ),
            DemoStep(
                step_id="workflows_intro",
                title="Understanding Workflows",
                description="Learn about LUMINA workflows",
                instructions=[
                    "LUMINA uses workflows to automate tasks.",
                    "Workflows are like recipes - they tell LUMINA what to do.",
                    "Try saying: 'Show me my workflows'",
                    "Explore the workflow system and see how automation works."
                ],
                interactive=True
            ),
            DemoStep(
                step_id="decisioning",
                title="Using #DECISIONING",
                description="Learn about automatic decision-making",
                instructions=[
                    "LUMINA can make decisions automatically using #DECISIONING.",
                    "When you see 'Keep All' or 'Accept Changes', LUMINA can auto-accept.",
                    "This saves you time and keeps your workflow smooth.",
                    "Try making a change and watch LUMINA automatically accept it."
                ],
                interactive=True
            ),
            DemoStep(
                step_id="completion",
                title="Demo Complete!",
                description="You've completed the demo - ready for full training",
                instructions=[
                    "Congratulations! You've completed the demo.",
                    "You now understand the basics of LUMINA.",
                    "Ready to begin your full Jedi Temple Training?",
                    "Continue to the full training program to become a LUMINA Jedi Master!"
                ],
                interactive=False
            )
        ]

    def _load_progress(self) -> Dict[str, Any]:
        """Load demo progress"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load progress: {e}")

        return {
            "current_step": 0,
            "completed_steps": [],
            "started_at": datetime.now().isoformat()
        }

    def _save_progress(self):
        """Save demo progress"""
        try:
            self.progress["current_step"] = self.current_step_index
            self.progress["completed_steps"] = self.completed_steps
            self.progress["last_updated"] = datetime.now().isoformat()

            with open(self.progress_file, 'w', encoding='utf-8') as f:
                json.dump(self.progress, f, indent=2)
        except Exception as e:
            logger.warning(f"   ⚠️  Failed to save progress: {e}")

    def start_demo(self) -> Dict[str, Any]:
        """Start demo mode"""
        logger.info("   🎮 Starting Jedi Temple Demo Mode...")

        self.current_step_index = 0
        self.completed_steps = []

        current_step = self.steps[self.current_step_index]

        return {
            "demo_started": True,
            "current_step": {
                "id": current_step.step_id,
                "title": current_step.title,
                "description": current_step.description,
                "instructions": current_step.instructions,
                "interactive": current_step.interactive
            },
            "total_steps": len(self.steps),
            "progress": 0.0
        }

    def get_current_step(self) -> Optional[Dict[str, Any]]:
        """Get current step"""
        if self.current_step_index >= len(self.steps):
            return None

        step = self.steps[self.current_step_index]

        return {
            "id": step.step_id,
            "title": step.title,
            "description": step.description,
            "instructions": step.instructions,
            "interactive": step.interactive,
            "step_number": self.current_step_index + 1,
            "total_steps": len(self.steps),
            "progress": (self.current_step_index / len(self.steps)) * 100
        }

    def complete_current_step(self) -> Dict[str, Any]:
        """Complete current step and advance"""
        if self.current_step_index >= len(self.steps):
            return {"error": "Demo already complete"}

        step = self.steps[self.current_step_index]
        step.completed = True
        self.completed_steps.append(step.step_id)

        # Advance to next step
        self.current_step_index += 1
        self._save_progress()

        if self.current_step_index >= len(self.steps):
            # Demo complete
            return {
                "demo_complete": True,
                "completed_steps": self.completed_steps,
                "total_steps": len(self.steps)
            }

        # Return next step
        next_step = self.steps[self.current_step_index]
        return {
            "step_completed": step.step_id,
            "next_step": {
                "id": next_step.step_id,
                "title": next_step.title,
                "description": next_step.description,
                "instructions": next_step.instructions,
                "interactive": next_step.interactive
            },
            "progress": (self.current_step_index / len(self.steps)) * 100
        }

    def get_progress(self) -> Dict[str, Any]:
        """Get demo progress"""
        return {
            "current_step": self.current_step_index + 1,
            "total_steps": len(self.steps),
            "completed_steps": len(self.completed_steps),
            "progress_percentage": (len(self.completed_steps) / len(self.steps)) * 100,
            "completed_step_ids": self.completed_steps
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Jedi Temple Demo Mode")
        parser.add_argument("--start", action="store_true", help="Start demo")
        parser.add_argument("--step", action="store_true", help="Get current step")
        parser.add_argument("--complete", action="store_true", help="Complete current step")
        parser.add_argument("--progress", action="store_true", help="Show progress")

        args = parser.parse_args()

        demo = JediTempleDemoMode()

        if args.start:
            result = demo.start_demo()
            print(json.dumps(result, indent=2))
        elif args.step:
            step = demo.get_current_step()
            print(json.dumps(step, indent=2))
        elif args.complete:
            result = demo.complete_current_step()
            print(json.dumps(result, indent=2))
        elif args.progress:
            progress = demo.get_progress()
            print(json.dumps(progress, indent=2))

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())