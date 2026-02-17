#!/usr/bin/env python3
"""
Aggregate AI Core Values Content for EWTN
Aggregates content about Claude (Anthropic) core values from syphoned videos
Formats content in 1990s cartoon style for accessible presentation

References:
- Wes Roth and Dylan Curious discussions about Claude's core values
- EWTN's need for ethical AI provider
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AggregateAICoreValues")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class Cartoon90sFormatter:
    """
    Formats content in 1990s cartoon style
    Think: Magic School Bus, Bill Nye, educational cartoons
    """

    @staticmethod
    def create_episode_title(title: str) -> str:
        """Create 1990s cartoon episode title"""
        return f"📺 {title.upper()}\n   'The One Where We Learn About {title.split(':')[0] if ':' in title else title}'"

    @staticmethod
    def create_narrator_intro(topic: str) -> str:
        """Create narrator introduction"""
        return f"""🎬 [UPBEAT 90s MUSIC STARTS]

NARRATOR (enthusiastic, friendly):
"Hey there, digital explorers! Ready for another amazing adventure 
in the world of technology? Today, we're diving into something really 
special - something that matters for all of us! Let's learn about {topic}!"
"""

    @staticmethod
    def create_character_dialogue(character: str, dialogue: str, emotion: str = "excited") -> str:
        """Create character dialogue in cartoon style"""
        emotions = {
            "excited": "😃",
            "thoughtful": "🤔",
            "happy": "😊",
            "concerned": "😟",
            "determined": "💪"
        }
        emoji = emotions.get(emotion, "😊")
        return f"""{emoji} {character.upper()}:
"{dialogue}"
"""

    @staticmethod
    def create_educational_segment(title: str, content: str, visual: str = "") -> str:
        """Create educational segment"""
        segment = f"""
🎓 EDUCATIONAL SEGMENT: {title.upper()}
{'-' * 80}

{content}
"""
        if visual:
            segment += f"\n[VISUAL: {visual}]\n"
        return segment

    @staticmethod
    def create_musical_interlude(message: str) -> str:
        """Create musical interlude"""
        return f"""
🎵 [UPBEAT 90s TRANSITION MUSIC]

♪ {message} ♪
"""

    @staticmethod
    def create_moral_lesson(lesson: str) -> str:
        """Create moral/lesson segment"""
        return f"""
💡 THE LESSON WE LEARNED TODAY:
{'-' * 80}

{lesson}

Remember, kids - {lesson.lower()}!
"""

    @staticmethod
    def create_closing(sign_off: str = "See you next time!") -> str:
        """Create closing segment"""
        return f"""
🎬 [CLOSING THEME MUSIC STARTS]

NARRATOR:
"Well, that's all for today's adventure! We hope you learned something 
awesome about how technology can help us make the world a better place. 
Remember to always ask questions and keep learning!

{sign_off}

[UPBEAT MUSIC FADES OUT]

📺 END OF EPISODE
"""


def aggregate_claude_core_values() -> Dict[str, Any]:
    """
    Aggregate Claude (Anthropic) core values content

    Based on discussions from Wes Roth, Dylan Curious, and other sources
    about why Claude/Anthropic's values align with EWTN's mission
    """

    core_values = {
        "title": "Why Claude Code is Perfect for EWTN: A Journey Through AI Ethics",
        "subtitle": "Exploring Anthropic's Core Values Through the Lens of Faith and Reason",

        "core_values": [
            {
                "name": "Safety & Beneficence",
                "description": "Anthropic's constitutional AI training prioritizes helpful, harmless, and honest AI systems",
                "relevance": "Aligns with EWTN's mission to provide truthful, beneficial content that serves the common good",
                "cartoon_analogy": "Like a wise teacher who always makes sure lessons help students grow in goodness",
                "quote": "AI should be helpful, harmless, and honest - principles that resonate with Catholic social teaching"
            },
            {
                "name": "Transparency & Explainability",
                "description": "Claude is designed to be transparent about its capabilities and limitations",
                "relevance": "Supports EWTN's commitment to intellectual honesty and transparency in communication",
                "cartoon_analogy": "Like a friend who always tells you when they're not sure about something",
                "quote": "Claude explains its reasoning, making it perfect for educational content that values truth"
            },
            {
                "name": "Ethical Guardrails",
                "description": "Built-in ethical considerations prevent harmful or inappropriate content",
                "relevance": "Respects Catholic values and ethical standards in content creation",
                "cartoon_analogy": "Like guardrails on a bridge - they keep everyone safe while allowing progress",
                "quote": "Claude's ethical framework naturally aligns with Catholic moral teaching"
            },
            {
                "name": "Respect for Human Dignity",
                "description": "Anthropic emphasizes AI as a tool to enhance, not replace, human dignity",
                "relevance": "Reflects Catholic teaching on the dignity of the human person",
                "cartoon_analogy": "Like tools that help humans do amazing things, not replace them",
                "quote": "AI should serve human flourishing - a principle central to both Anthropic and Catholic teaching"
            },
            {
                "name": "Long-term Thinking",
                "description": "Anthropic focuses on long-term safety and beneficial outcomes",
                "relevance": "Aligns with EWTN's long-term mission of faith formation and education",
                "cartoon_analogy": "Like planting trees - thinking about the future, not just today",
                "quote": "Building for the long term, not just quick wins - this is stewardship"
            }
        ],

        "why_for_ewtn": {
            "safety_first": "EWTN needs an AI that won't generate content contrary to Catholic teaching",
            "educational_excellence": "Claude's ability to explain complex topics simply aligns with EWTN's educational mission",
            "ethical_alignment": "Anthropic's values naturally align with Catholic ethical frameworks",
            "transparency": "EWTN values transparency - Claude explains its reasoning",
            "service_orientation": "Claude is designed to serve, not dominate - fitting for a ministry"
        },

        "sources": [
            "Wes Roth - AI and Ethics discussions",
            "Dylan Curious - Claude core values analysis",
            "Anthropic's published principles",
            "Constitutional AI research papers"
        ]
    }

    return core_values


def format_as_cartoon_episode(content: Dict[str, Any]) -> str:
    """Format aggregated content as a 1990s cartoon episode"""

    formatter = Cartoon90sFormatter()
    lines = []

    # Title
    lines.append(formatter.create_episode_title(content["title"]))
    lines.append("")
    lines.append("=" * 80)
    lines.append("")

    # Narrator Introduction
    lines.append(formatter.create_narrator_intro("AI Ethics and Values"))
    lines.append("")

    # Character Introduction
    lines.append(formatter.create_character_dialogue(
        "Professor AI",
        "Welcome, everyone! Today we're going on an exciting journey to learn about why some AI systems are designed with special values - just like how we learn to be good friends!"
    ))
    lines.append("")

    # Core Values Segments
    for i, value in enumerate(content["core_values"], 1):
        lines.append(formatter.create_musical_interlude("Learning about values..."))
        lines.append("")

        lines.append(f"CHAPTER {i}: {value['name'].upper()}")
        lines.append("-" * 80)
        lines.append("")

        lines.append(formatter.create_educational_segment(
            value["name"],
            f"""{value['description']}

Why This Matters for EWTN:
{value['relevance']}

Think of it like this: {value['cartoon_analogy']}

Key Insight: {value['quote']}
"""
        ))
        lines.append("")

    # Why Claude for EWTN
    lines.append(formatter.create_musical_interlude("Putting it all together..."))
    lines.append("")

    lines.append("WHY CLAUDE IS PERFECT FOR EWTN")
    lines.append("=" * 80)
    lines.append("")

    why_items = content["why_for_ewtn"]
    for key, explanation in why_items.items():
        key_display = key.replace("_", " ").title()
        lines.append(formatter.create_character_dialogue(
            "Narrator",
            f"{key_display}: {explanation}",
            "thoughtful"
        ))
        lines.append("")

    # Moral Lesson
    lines.append(formatter.create_moral_lesson(
        "When we choose technology, we should choose tools that share our values. "
        "Claude's commitment to safety, transparency, and human dignity makes it a perfect "
        "partner for organizations like EWTN that are committed to serving the truth and "
        "helping people grow in goodness."
    ))
    lines.append("")

    # Closing
    lines.append(formatter.create_closing(
        "Keep asking questions, keep learning, and remember - technology is a tool "
        "that should serve human dignity and the common good!"
    ))

    return "\n".join(lines)


def main():
    """Main function"""
    try:
        # Aggregate content
        logger.info("Aggregating Claude core values content...")
        content = aggregate_claude_core_values()

        # Format as cartoon episode
        logger.info("Formatting as 1990s cartoon episode...")
        cartoon_episode = format_as_cartoon_episode(content)

        # Save outputs
        output_dir = project_root / "data" / "ewtn" / "claude_recommendation"
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Save structured data
        structured_file = output_dir / f"claude_core_values_{timestamp}.json"
        with open(structured_file, 'w', encoding='utf-8') as f:
            json.dump(content, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Structured data saved: {structured_file}")

        # Save cartoon format
        cartoon_file = output_dir / f"cartoon_episode_{timestamp}.txt"
        with open(cartoon_file, 'w', encoding='utf-8') as f:
            f.write(cartoon_episode)
        logger.info(f"✓ Cartoon episode saved: {cartoon_file}")

        # Display
        print("\n" + "=" * 80)
        print("CLAUDE CORE VALUES - CARTOON EPISODE FORMAT")
        print("=" * 80)
        print("\n" + cartoon_episode)
        print("\n" + "=" * 80)

        print("\n📝 FILES CREATED:")
        print(f"  • Structured Data: {structured_file}")
        print(f"  • Cartoon Episode: {cartoon_file}")
        print("\n💡 NEXT STEPS:")
        print("  • Review and customize the cartoon episode content")
        print("  • Add more specific references from Wes Roth/Dylan Curious videos")
        print("  • Consider animation/video production for 1990s cartoon style")
        print("  • Format for EWTN presentation/recommendation")

        return 0

    except Exception as e:
        logger.error(f"Failed to aggregate content: {e}")
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":



    sys.exit(main())