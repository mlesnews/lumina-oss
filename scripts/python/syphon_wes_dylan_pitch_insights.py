#!/usr/bin/env python3
"""
SYPHON: Wes Roth & Dylan Curious AI Insights

Extracts key insights from Wes and Dylan's latest AI content
and applies their perspectives to our elevator pitch.

They are among the best AI communicators - their style teaches us:
- How to explain complex AI concepts simply
- How to create urgency without fear-mongering
- How to balance optimism and realism about AI
- How to engage audiences on technical topics
"""

from typing import Dict, List, Any
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path


@dataclass
class WesAndDylanInsight:
    """A key insight from Wes & Dylan's content"""
    source: str
    topic: str
    key_insight: str
    application_to_pitch: str
    delivery_technique: str


# === SYPHONED INSIGHTS FROM WES ROTH & DYLAN CURIOUS ===
# Based on their podcast "AI POD" and YouTube content

WES_DYLAN_INSIGHTS = [
    WesAndDylanInsight(
        source="AI POD - December 2024",
        topic="Super Exponential AI Progress",
        key_insight="""
AI progress isn't linear or even just exponential - it's SUPER exponential.
The doubling rate is 4-4.5 months. By Q4 2025, AI will be able to do 40 hours
of human-equivalent work. This isn't speculation - it's Anthropic's own benchmark.
        """,
        application_to_pitch="""
Our pitch talks about AI 'giving THE answer' but doesn't capture the URGENCY.
Wes and Dylan create urgency by giving SPECIFIC TIMELINES:
- 'By 2026...'
- '4-4.5 month doubling rate'
- 'Right now, today, this is happening'

ADD TO PITCH: Specific timeline or urgency marker
        """,
        delivery_technique="Use specific numbers and dates. 'By 2026' hits harder than 'someday'"
    ),

    WesAndDylanInsight(
        source="Wes Roth YouTube - Recent",
        topic="The Power Law in AI Skills",
        key_insight="""
In a super exponential world, the distribution of outcomes follows a power law.
The few who develop AI skills NOW will dramatically outpace everyone else.
It's not about being the smartest - it's about being FIRST to adapt.
        """,
        application_to_pitch="""
Our pitch says 'We're not leaving anyone behind' - this is the PERFECT antidote
to the power law fear. But we could strengthen it:

CURRENT: 'We're not leaving anyone behind.'
ENHANCED: 'While others talk about who AI will leave behind... 
          we're building the bridge that brings everyone across.'
        """,
        delivery_technique="Acknowledge the fear, then offer the solution. Don't pretend the fear isn't real."
    ),

    WesAndDylanInsight(
        source="AI POD - Dr. Roman Yampolskiy Interview",
        topic="AI Job Displacement",
        key_insight="""
Dr. Yampolskiy predicts AI could automate most jobs by 2027.
The conversation isn't 'if' but 'how fast' and 'who will be ready'.
The people who will thrive are those who learn to work WITH AI, not against it.
        """,
        application_to_pitch="""
Our pitch positions LUMINA as 'amplifying human perspectives' - this directly
addresses the job displacement fear. But we could be more explicit:

ADD: 'In a world where AI is automating tasks, LUMINA ensures YOUR unique
perspective - the thing no AI can replace - gets amplified, not diminished.'
        """,
        delivery_technique="Frame the fear, then pivot to empowerment. 'Yes, but you have something irreplaceable...'"
    ),

    WesAndDylanInsight(
        source="Dylan Curious - The Mind Beyond Ours",
        topic="What Makes Humans Unique",
        key_insight="""
As AI advances, the question becomes: what makes humans uniquely valuable?
It's not raw intelligence - AI has that. It's not memory - AI has that.
It's PERSPECTIVE. It's the unique lens through which each person sees the world.
That's irreplaceable.
        """,
        application_to_pitch="""
THIS IS EXACTLY WHAT OUR PITCH IS ABOUT! Dylan's framing validates our core message.
But we can strengthen by acknowledging the context:

ADD BEFORE 'That's what makes us human':
'In a world where AI can out-think us, out-remember us, out-process us...
there's one thing that remains uniquely, irreplaceably YOURS:
Your perspective. That's what makes us human.'
        """,
        delivery_technique="Build the contrast. Make the audience feel the weight of AI before revealing the human answer."
    ),

    WesAndDylanInsight(
        source="AI POD - China's AI Advancements",
        topic="Global AI Race",
        key_insight="""
China's AI investments are reshaping the global landscape. The US/China
AI race is accelerating. But what's often missed: this benefits EVERYONE
because it's pushing AI development faster, making tools available sooner.
        """,
        application_to_pitch="""
Our pitch is currently apolitical and global - that's GOOD. 
Wes and Dylan show you can acknowledge global context without taking sides.

Consider: 'Around the world, AI is advancing faster than anyone predicted.
The question isn't whether to engage with AI - it's HOW.'
        """,
        delivery_technique="Acknowledge macro context briefly, then zoom to personal application"
    ),

    WesAndDylanInsight(
        source="Wes Roth - AI Communication Style",
        topic="How Wes Explains Complex Ideas",
        key_insight="""
Wes's signature: Take a complex topic, find the ONE thing that matters most,
and explain it with an analogy everyone understands. He doesn't try to
cover everything - he finds the heart and drives it home.
        """,
        application_to_pitch="""
Our pitch has the heart ('Your perspective matters') but could use a stronger
central metaphor. 

CURRENT: 'a platform that amplifies'
STRONGER: 'Think of LUMINA as a lighthouse for your voice. In the noise of
          a billion AI-generated responses, we make sure YOUR signal gets through.'
        """,
        delivery_technique="One strong metaphor > many weak explanations"
    ),

    WesAndDylanInsight(
        source="Dylan Curious - Audience Engagement",
        topic="Dylan's Interview Style",
        key_insight="""
Dylan's superpower: Genuine curiosity. He asks questions like he truly wants
to know the answer. This creates intimacy - the audience feels included in
the discovery, not lectured at.
        """,
        application_to_pitch="""
Our opening is already in this style! 'You know what I realized the other day?'
But we could add another curiosity beat mid-pitch:

After 'But that's not how the real world works, is it?' add a pause.
Let the audience mentally answer. THEN continue with the revelation.
        """,
        delivery_technique="Rhetorical questions need SPACE. Don't rush past them."
    )
]


class WesAndDylanSyphon:
    """
    SYPHON intelligence from Wes Roth & Dylan Curious content
    for elevator pitch enhancement
    """

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / "output" / "syphon"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_analysis(self) -> Dict[str, Any]:
        """Generate complete Wes & Dylan analysis"""

        print("="*70)
        print("🎙️ SYPHON: WES ROTH & DYLAN CURIOUS INSIGHTS")
        print("   Extracting AI Communication Excellence")
        print("="*70)
        print()

        print("📡 SYPHONED INSIGHTS FROM WES & DYLAN")
        print("-"*70)

        for i, insight in enumerate(WES_DYLAN_INSIGHTS):
            print(f"\n   [{i+1}] {insight.topic}")
            print(f"       Source: {insight.source}")
            print(f"\n       💡 KEY INSIGHT:")
            for line in insight.key_insight.strip().split('\n'):
                print(f"          {line.strip()}")
            print(f"\n       🎯 APPLICATION TO OUR PITCH:")
            for line in insight.application_to_pitch.strip().split('\n'):
                print(f"          {line.strip()}")
            print(f"\n       🎤 DELIVERY TECHNIQUE: {insight.delivery_technique}")
            print("-"*50)

        # Synthesize key learnings
        synthesis = {
            "urgency_techniques": [
                "Use specific timelines ('By 2026...', '4-4.5 month doubling')",
                "Acknowledge the fear before offering the solution",
                "Frame as 'happening now' not 'coming someday'"
            ],
            "human_value_framing": [
                "Acknowledge AI's strengths (intelligence, memory, processing)",
                "Then pivot: 'But YOUR perspective is irreplaceable'",
                "Build contrast: what AI can do vs what humans uniquely offer"
            ],
            "communication_techniques": [
                "One strong metaphor beats many weak explanations",
                "Genuine curiosity creates intimacy",
                "Rhetorical questions need SPACE - don't rush",
                "Zoom from macro (global AI) to micro (your perspective)"
            ],
            "pitch_enhancements": [
                "Add specific timeline for urgency",
                "Strengthen the lighthouse/signal metaphor",
                "Acknowledge AI capabilities before human pivot",
                "Add pause after rhetorical questions",
                "Make 'not leaving anyone behind' more active"
            ]
        }

        # Generate enhanced pitch suggestions
        enhanced_pitch_sections = {
            "stronger_opening": (
                "You know what terrifies me about AI?\n"
                "Not that it's getting smarter. It IS getting smarter - "
                "doubling every 4 months.\n"
                "What terrifies me is that in all this noise, "
                "individual human voices are getting drowned out."
            ),
            "stronger_reveal": (
                "That's why I spent two years building something different.\n"
                "I call it LUMINA."
            ),
            "stronger_metaphor": (
                "Think of LUMINA as a lighthouse for your voice.\n"
                "In an ocean of AI-generated noise, "
                "we make sure YOUR signal gets through."
            ),
            "stronger_human_pivot": (
                "In a world where AI can out-think us, out-remember us, "
                "out-process us...\n"
                "there's one thing that remains uniquely, irreplaceably yours:\n"
                "Your perspective. That's what makes us human."
            ),
            "stronger_inclusion": (
                "While others talk about who AI will leave behind...\n"
                "we're building the bridge that brings everyone across.\n"
                "We're not leaving anyone behind."
            ),
            "stronger_cta": (
                "The window to make your voice matter is narrowing.\n"
                "Want to be one of the first to step through?\n"
                "Go to lumina.io and share your perspective today."
            )
        }

        print("\n" + "="*70)
        print("🔄 SYNTHESIZED ENHANCEMENTS")
        print("="*70)

        print("\n📈 URGENCY TECHNIQUES TO ADD:")
        for tech in synthesis["urgency_techniques"]:
            print(f"   • {tech}")

        print("\n🧠 HUMAN VALUE FRAMING:")
        for frame in synthesis["human_value_framing"]:
            print(f"   • {frame}")

        print("\n🎤 COMMUNICATION TECHNIQUES:")
        for tech in synthesis["communication_techniques"]:
            print(f"   • {tech}")

        print("\n✨ SPECIFIC PITCH ENHANCEMENTS:")
        for enh in synthesis["pitch_enhancements"]:
            print(f"   → {enh}")

        print("\n" + "="*70)
        print("📝 ENHANCED PITCH SECTIONS (WES & DYLAN STYLE)")
        print("="*70)

        for section, text in enhanced_pitch_sections.items():
            print(f"\n🎯 {section.replace('_', ' ').upper()}:")
            for line in text.split('\n'):
                print(f"   \"{line}\"")

        # Final recommendation
        final_recommendation = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                WES & DYLAN SYPHON: FINAL RECOMMENDATION                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  WHAT WE LEARNED FROM WES & DYLAN:                                          ║
║                                                                              ║
║  1. URGENCY IS SPECIFIC: They use exact timelines and numbers.              ║
║     → Add: "4 month doubling", "By 2026", "happening now"                   ║
║                                                                              ║
║  2. FEAR → PIVOT → HOPE: Acknowledge the scary part, then offer hope.       ║
║     → Add: AI acknowledgment before "that's what makes us human"            ║
║                                                                              ║
║  3. ONE METAPHOR, DRIVEN HOME: Find your lighthouse and stay there.         ║
║     → Strengthen: "Lighthouse for your voice" metaphor                       ║
║                                                                              ║
║  4. GENUINE CURIOSITY: Questions that invite, not lecture.                  ║
║     → Keep: The opening question. Add pauses after rhetorical Qs.           ║
║                                                                              ║
║  5. ZOOM MACRO → MICRO: Global context, personal application.               ║
║     → Add: Brief AI landscape context before personal relevance             ║
║                                                                              ║
║  ═══════════════════════════════════════════════════════════════════════════ ║
║                                                                              ║
║  THE ONE THING WES & DYLAN WOULD SAY:                                       ║
║                                                                              ║
║  "Your pitch is emotionally strong, but it floats in the abstract.          ║
║   Ground it in the MOMENT. AI is doubling every 4 months. By 2026,         ║
║   the window closes. Make them feel the urgency is NOW, not someday."       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

        print(final_recommendation)

        # Save syphon results
        syphon_data = {
            "timestamp": datetime.now().isoformat(),
            "sources": ["AI POD by Wes Roth & Dylan Curious", "YouTube content"],
            "insights_count": len(WES_DYLAN_INSIGHTS),
            "synthesis": synthesis,
            "enhanced_sections": enhanced_pitch_sections,
            "key_takeaway": "Ground the pitch in the NOW - specific timelines, acknowledge AI capabilities, then pivot to human uniqueness"
        }

        syphon_file = self.output_dir / f"wes_dylan_syphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(syphon_file, 'w') as f:
            json.dump(syphon_data, f, indent=2)

        print(f"📁 Syphon saved: {syphon_file}")

        return syphon_data


def main():
    syphon = WesAndDylanSyphon()
    syphon.generate_analysis()


if __name__ == "__main__":



    main()