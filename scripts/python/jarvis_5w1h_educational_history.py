#!/usr/bin/env python3
"""
JARVIS 5W1H Educational History System

Explains to today's youth the opportunities that history has taught us.
Educational, loosely focused exploration of technology's quantum duality:
"Technology is neither good nor bad — it's both simultaneously, QUANTUMTATIVELY"

Explores the mystery of known and unknown, like the media did for kids in the 70s-90s.

Tags: #5W1H #EDUCATION #HISTORY #QUANTUM_DUALITY #YOUTH @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVIS5W1H")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVIS5W1H")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVIS5W1H")


class HistoricalTechnologyLesson:
    """Historical lesson about technology's quantum duality"""

    def __init__(self):
        self.hard_way_context = {
            "era": "1970s-1990s",
            "method": "THE HARD WAY - All manual human labor and research",
            "journey": "Star Wars (1977) to here we are now",
            "characteristics": [
                "Manual research in libraries",
                "Trial and error experimentation",
                "No AI assistance - pure human exploration",
                "Learning through doing",
                "Figuring things out yourself",
                "Physical books, encyclopedias, manuals",
                "Hands-on tinkering and discovery"
            ],
            "value": "The hard way taught resilience, critical thinking, and deep understanding",
            "contrast": "Today's youth have AI assistance - easier path, but different lessons"
        }

        self.lessons = {
            "internet": {
                "era": "1990s",
                "who": "Everyone - from researchers to everyday people",
                "what": "The Internet - global information network",
                "when": "1990s - explosion of public internet access",
                "where": "Worldwide - connecting the globe",
                "why": "Share information, connect people, democratize knowledge",
                "how": "Through protocols, browsers, and infrastructure",
                "quantum_duality": {
                    "good": "Unprecedented access to information, global communication, education",
                    "bad": "Misinformation, privacy concerns, digital divide, addiction",
                    "quantum_nature": "Both simultaneously - same technology, opposite impacts",
                    "mystery": "We didn't know how it would transform society - we explored together THE HARD WAY"
                },
                "historical_opportunity": "Learn from early internet - balance freedom with responsibility",
                "the_hard_way": {
                    "method": "Manual research, trial and error, no AI assistance",
                    "journey": "Star Wars era (1977) to here we are now",
                    "lesson": "Previous generations did it the hard way - manual labor and research"
                }
            },
            "personal_computer": {
                "era": "1980s-1990s",
                "who": "Kids, families, businesses",
                "what": "Personal computers - computing power in homes",
                "when": "1980s-1990s - PC revolution",
                "where": "Homes, schools, offices",
                "why": "Empower individuals, automate tasks, enable creativity",
                "how": "Through affordable hardware, software, and user-friendly interfaces",
                "quantum_duality": {
                    "good": "Empowerment, creativity, productivity, education",
                    "bad": "Screen time concerns, job displacement, digital dependency",
                    "quantum_nature": "Both simultaneously - empowerment and dependency coexist",
                    "mystery": "We explored what computers could do - discovering possibilities together THE HARD WAY"
                },
                "historical_opportunity": "Learn from PC era - technology empowers but requires balance",
                "the_hard_way": {
                    "method": "Reading manuals, experimenting, no tutorials or AI help",
                    "journey": "Star Wars era to personal computing revolution",
                    "lesson": "Kids in 80s-90s learned computers through manual exploration"
                }
            },
            "social_media": {
                "era": "2000s-2010s",
                "who": "Everyone - especially youth",
                "what": "Social media platforms - connecting and sharing",
                "when": "2000s-2010s - social media explosion",
                "where": "Online - global platforms",
                "why": "Connect, share, express, build communities",
                "how": "Through platforms, mobile devices, and networks",
                "quantum_duality": {
                    "good": "Connection, community, expression, awareness",
                    "bad": "Comparison, cyberbullying, echo chambers, mental health",
                    "quantum_nature": "Both simultaneously - connection and isolation from same tool",
                    "mystery": "We're still discovering social media's full impact - exploring in real-time"
                },
                "historical_opportunity": "Learn from social media - connection requires mindfulness",
                "the_hard_way": {
                    "method": "Early adopters figured it out through use, no guides",
                    "journey": "From Star Wars era to social media explosion",
                    "lesson": "Previous generations explored social media without AI assistance"
                }
            },
            "ai_assistants": {
                "era": "2020s",
                "who": "Everyone - AI assistants becoming ubiquitous",
                "what": "AI assistants - intelligent helpers",
                "when": "2020s - AI assistant revolution",
                "where": "Everywhere - devices, apps, services",
                "why": "Help, automate, enhance, assist",
                "how": "Through machine learning, natural language, and integration",
                "quantum_duality": {
                    "good": "Enhanced capabilities, efficiency, accessibility, assistance",
                    "bad": "Over-reliance, job displacement, privacy, manipulation",
                    "quantum_nature": "Both simultaneously - assistance and dependency from same AI",
                    "mystery": "We're exploring AI's potential now - but previous generations did it THE HARD WAY"
                },
                "historical_opportunity": "Learn from history - use AI wisely, maintain human agency",
                "the_hard_way": {
                    "method": "Previous generations: manual research, no AI assistance",
                    "journey": "Star Wars (1977) to here we are now - the full journey",
                    "lesson": "They did it the hard way - all manual human labor and research. You have AI assistance - easier path, but learn from their resilience"
                }
            }
        }

    def get_5w1h_lesson(self, technology: str) -> Dict[str, Any]:
        """Get 5W1H lesson for a technology"""
        lesson = self.lessons.get(technology.lower(), {})
        if not lesson:
            return {"error": f"Lesson not found for {technology}"}

        return {
            "technology": technology,
            "5w1h": {
                "who": lesson.get("who", "Unknown"),
                "what": lesson.get("what", "Unknown"),
                "when": lesson.get("when", "Unknown"),
                "where": lesson.get("where", "Unknown"),
                "why": lesson.get("why", "Unknown"),
                "how": lesson.get("how", "Unknown")
            },
            "quantum_duality": lesson.get("quantum_duality", {}),
            "historical_opportunity": lesson.get("historical_opportunity", ""),
            "the_hard_way": lesson.get("the_hard_way", {}),
            "era": lesson.get("era", "Unknown")
        }


class YouthEducationGenerator:
    """Generate educational content for today's youth about historical technology lessons"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "youth_education"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.lessons = HistoricalTechnologyLesson()
        self.style = "70s_90s_exploration"  # Like the media that taught kids in 70s-90s

    def generate_educational_story(
        self,
        technology: str,
        target_audience: str = "youth",
        style: str = "exploratory_mystery"
    ) -> Dict[str, Any]:
        """Generate educational story using 5W1H framework"""
        lesson = self.lessons.get_5w1h_lesson(technology)

        if "error" in lesson:
            return lesson

        story = {
            "story_id": f"story_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "technology": technology,
            "target_audience": target_audience,
            "style": style,
            "era_context": lesson.get("era", "Unknown"),
            "5w1h_explanation": self._create_5w1h_narrative(lesson),
            "quantum_duality_exploration": self._explore_duality(lesson),
            "mystery_of_known_unknown": self._explore_mystery(lesson),
            "historical_opportunity": self._explain_opportunity(lesson),
            "the_hard_way_acknowledgment": self._acknowledge_hard_way(lesson),
            "generated_at": datetime.now().isoformat(),
            "educational_approach": "Like 70s-90s media: exploratory, mysterious, engaging",
            "journey": "Star Wars (1977) to here we are now - the full journey"
        }

        # Save story
        story_file = self.data_dir / f"{technology}_educational_story.json"
        with open(story_file, 'w', encoding='utf-8') as f:
            json.dump(story, f, indent=2, default=str)

        logger.info(f"📚 Generated educational story: {technology}")

        return story

    def _create_5w1h_narrative(self, lesson: Dict[str, Any]) -> Dict[str, Any]:
        """Create 5W1H narrative explanation"""
        w5h1 = lesson.get("5w1h", {})

        narrative = {
            "who": {
                "question": "WHO was affected?",
                "answer": w5h1.get("who", "Unknown"),
                "explanation": "Understanding who uses technology helps us see its impact"
            },
            "what": {
                "question": "WHAT is this technology?",
                "answer": w5h1.get("what", "Unknown"),
                "explanation": "Defining what it is helps us understand its nature"
            },
            "when": {
                "question": "WHEN did this happen?",
                "answer": w5h1.get("when", "Unknown"),
                "explanation": "Timing shows us the context and era of discovery"
            },
            "where": {
                "question": "WHERE did this occur?",
                "answer": w5h1.get("where", "Unknown"),
                "explanation": "Location shows us the scope and reach of technology"
            },
            "why": {
                "question": "WHY was this created?",
                "answer": w5h1.get("why", "Unknown"),
                "explanation": "Understanding purpose reveals intentions and outcomes"
            },
            "how": {
                "question": "HOW does it work?",
                "answer": w5h1.get("how", "Unknown"),
                "explanation": "Mechanisms show us how technology achieves its purpose"
            }
        }

        return narrative

    def _explore_duality(self, lesson: Dict[str, Any]) -> Dict[str, Any]:
        """Explore quantum duality"""
        duality = lesson.get("quantum_duality", {})

        return {
            "principle": "Technology is neither good nor bad — it's both simultaneously, QUANTUMTATIVELY",
            "good_side": {
                "aspects": duality.get("good", "").split(", "),
                "explanation": "These positive impacts show technology's potential"
            },
            "bad_side": {
                "aspects": duality.get("bad", "").split(", "),
                "explanation": "These negative impacts show technology's risks"
            },
            "quantum_nature": {
                "insight": duality.get("quantum_nature", ""),
                "explanation": "Both sides exist simultaneously - same technology, opposite impacts"
            },
            "lesson_for_youth": "History teaches us: technology has two sides - awareness helps us navigate both"
        }

    def _explore_mystery(self, lesson: Dict[str, Any]) -> Dict[str, Any]:
        """Explore the mystery of known and unknown"""
        duality = lesson.get("quantum_duality", {})
        mystery_text = duality.get("mystery", "")

        return {
            "mystery": mystery_text,
            "known": {
                "what_we_know": "Technology's immediate impacts and uses",
                "explanation": "We can see what technology does in the present"
            },
            "unknown": {
                "what_we_dont_know": "Long-term effects, unintended consequences, future possibilities",
                "explanation": "Like kids in the 70s-90s, we're exploring the unknown together"
            },
            "exploration": {
                "approach": "Like 70s-90s media taught us: explore with curiosity and caution",
                "method": "Discover through use, learn from mistakes, adapt and grow"
            },
            "message_for_youth": "You're living through the same kind of exploration - be curious, be aware, be thoughtful"
        }

    def _explain_opportunity(self, lesson: Dict[str, Any]) -> Dict[str, Any]:
        """Explain the historical opportunity"""
        opportunity = lesson.get("historical_opportunity", "")

        return {
            "opportunity": opportunity,
            "what_history_teaches": "Previous generations explored technology - we can learn from their experiences",
            "youth_opportunity": "You have the chance to shape technology's future with awareness of its duality",
            "approach": "Learn from history, explore with curiosity, navigate with wisdom",
            "quantum_understanding": "Recognize that technology is both good and bad - your choices matter"
        }

    def _acknowledge_hard_way(self, lesson: Dict[str, Any]) -> Dict[str, Any]:
        """Acknowledge that previous generations did it THE HARD WAY"""
        hard_way = lesson.get("the_hard_way", {})

        return {
            "acknowledgment": "Previous generations did it THE HARD WAY - all manual human labor and research",
            "method": hard_way.get("method", "Manual exploration, no AI assistance"),
            "journey": hard_way.get("journey", "Star Wars (1977) to here we are now"),
            "lesson": hard_way.get("lesson", "They figured it out through manual exploration"),
            "contrast": {
                "then": "70s-90s: Manual research, trial and error, no AI help",
                "now": "2020s: AI assistance, easier path, but different lessons",
                "value": "The hard way taught resilience, critical thinking, and deep understanding"
            },
            "message_for_youth": "You have AI assistance - easier path. But learn from those who did it the hard way - their resilience and deep understanding are valuable lessons"
        }

    def generate_complete_educational_package(
        self,
        technologies: List[str] = None
    ) -> Dict[str, Any]:
        """Generate complete educational package for youth"""
        if technologies is None:
            technologies = ["internet", "personal_computer", "social_media", "ai_assistants"]

        package = {
            "package_id": f"package_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "title": "Technology's Quantum Duality: Lessons from History",
            "subtitle": "Explaining to Today's Youth the Opportunities History Has Taught Us",
            "target_audience": "youth",
            "educational_style": "70s_90s_exploratory_mystery",
            "core_principle": "Technology is neither good nor bad — it's both simultaneously, QUANTUMTATIVELY",
            "the_hard_way_acknowledgment": {
                "era": "1970s-1990s",
                "method": "THE HARD WAY - All manual human labor and research",
                "journey": "Star Wars (1977) to here we are now",
                "message": "Previous generations did it the hard way. You have AI assistance - easier path, but learn from their resilience."
            },
            "stories": [],
            "generated_at": datetime.now().isoformat()
        }

        for tech in technologies:
            story = self.generate_educational_story(tech)
            package["stories"].append(story)

        # Save package
        package_file = self.data_dir / "complete_educational_package.json"
        with open(package_file, 'w', encoding='utf-8') as f:
            json.dump(package, f, indent=2, default=str)

        logger.info(f"📚 Generated complete educational package: {len(technologies)} technologies")

        return package


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS 5W1H Educational History")
        parser.add_argument("--technology", type=str, help="Generate story for technology")
        parser.add_argument("--package", action="store_true", help="Generate complete package")
        parser.add_argument("--list", action="store_true", help="List available technologies")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        generator = YouthEducationGenerator(project_root)

        if args.technology:
            story = generator.generate_educational_story(args.technology)
            print("=" * 80)
            print("5W1H EDUCATIONAL STORY")
            print("=" * 80)
            print(f"\nTechnology: {story['technology']}")
            print(f"Era: {story['era_context']}")
            print(f"\n5W1H:")
            for key, value in story['5w1h_explanation'].items():
                print(f"  {key.upper()}: {value['question']}")
                print(f"    {value['answer']}")
            print(f"\nQuantum Duality: {story['quantum_duality_exploration']['principle']}")
            print("=" * 80)
            print(json.dumps(story, indent=2, default=str))

        elif args.package:
            package = generator.generate_complete_educational_package()
            print("=" * 80)
            print("COMPLETE EDUCATIONAL PACKAGE")
            print("=" * 80)
            print(f"\nTitle: {package['title']}")
            print(f"Core Principle: {package['core_principle']}")
            print(f"Stories: {len(package['stories'])}")
            print("=" * 80)
            print(json.dumps(package, indent=2, default=str))

        elif args.list:
            lessons = HistoricalTechnologyLesson()
            print("Available Technologies:")
            for tech in lessons.lessons.keys():
                print(f"  • {tech}")

        else:
            # Default: generate package
            package = generator.generate_complete_educational_package()
            print(json.dumps(package, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()