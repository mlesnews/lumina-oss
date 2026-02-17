#!/usr/bin/env python3
"""
Save "Teach a Man to Fish" Discussion

Saves the discussion about:
- "Give a man a fish, he eats for a day, teach a man to fish and he eats for a lifetime"
- Empowerment over dependency
- Teaching over giving
- Sustainability over temporary solutions

To:
1. @HOLOCRON (public)
2. @SECRET @HOLOCRON (blackbox, privacy respected)
3. THE CAPTAIN'S LOG (in respect to Star Trek TOS)

Tags: #TEACH #FISH #EMPOWERMENT #COLLABORATION #EXPLORATION #BEKIND #SUSTAINABILITY #KNOWLEDGE #DEEPBLACK
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from save_to_holocron_and_journal import save_discussion_to_all

# The "Teach a Man to Fish" discussion content
discussion_content = {
    "title": "Teach a Man to Fish",
    "timestamp": "2026-01-10",
    "proverb": "Give a man a fish, he eats for a day, teach a man to fish and he eats for a lifetime.",
    "wisdom": {
        "principle": {
            "teaching_vs_giving": {
                "giving": "Temporary solution, dependency, short-term",
                "teaching": "Empowerment, independence, lifetime solution"
            },
            "empowerment": "Enable others to do for themselves",
            "independence": "Foster self-sufficiency",
            "sustainability": "Create lasting solutions",
            "knowledge_transfer": "Share the how, not just the what"
        },
        "application": {
            "collaboration": "Don't just collaborate, teach others to collaborate",
            "exploration": "Don't just explore, teach others to explore",
            "knowledge": "Don't just share knowledge, teach how to learn"
        }
    },
    "framework": {
        "teaching_principles": [
            "Empowerment - Enable others to do for themselves",
            "Independence - Foster self-sufficiency",
            "Sustainability - Create lasting solutions",
            "Knowledge Transfer - Share the how, not just the what",
            "Collaboration - Teach collaboration, enable collaboration"
        ],
        "universal_application": {
            "for_all_persons": "All persons deserve empowerment, teaching, knowledge transfer, independence, sustainability",
            "teaching_is_kindness": "Teaching is the ultimate kindness - empowering others is kind"
        }
    },
    "connection": {
        "to_collaborate": "Teach collaboration - don't just collaborate, teach others to collaborate, enable universal collaboration, empower all persons to collaborate",
        "to_exploration": "Teach exploration - don't just explore, teach others to explore, enable exploration, empower all persons to explore",
        "to_bekind": "Teaching is kindness - empowering others is kind, enabling independence is kind, creating sustainability is kind, teaching is the ultimate kindness"
    },
    "deepblack": {
        "insight": "Teaching is empowerment. Empowerment is collaboration. Collaboration is exploration. Exploration is human nature. All are connected. All are one."
    },
    "tags": [
        "#TEACH",
        "#FISH",
        "#EMPOWERMENT",
        "#COLLABORATION",
        "#EXPLORATION",
        "#BEKIND",
        "#SUSTAINABILITY",
        "#KNOWLEDGE",
        "#DEEPBLACK",
        "#MOONSHOT",
        "#MOON",
        "#TOTHEMOON",
        "+WORDS-WORTH-SAVING"
    ],
    "significance": "This represents the profound wisdom of teaching vs. giving. Empowerment over dependency. Teaching over giving. Sustainability over temporary solutions. Teaching is the ultimate kindness. All persons deserve empowerment, teaching, knowledge transfer, independence, sustainability."
}

if __name__ == "__main__":
    results = save_discussion_to_all(
        discussion_title="Teach a Man to Fish",
        discussion_content=discussion_content
    )

    print("=" * 80)
    print("🎓 TEACH A MAN TO FISH DISCUSSION SAVED")
    print("=" * 80)
    print(f"   @HOLOCRON: {results['holocron_id']}")
    print(f"   @SECRET @HOLOCRON: {results['secret_holocron_id']}")
    print(f"     (blackbox, privacy respected, theme: DO BETTER)")
    print(f"   THE CAPTAIN'S LOG: {results['captains_log_id']} (Star Trek TOS)")
    print("=" * 80)
    print()
    print("   Give a man a fish, he eats for a day")
    print("   Teach a man to fish, he eats for a lifetime")
    print("")
    print("   Empowerment over dependency")
    print("   Teaching over giving")
    print("   Sustainability over temporary solutions")
    print("   Teaching is the ultimate kindness")
    print("=" * 80)
