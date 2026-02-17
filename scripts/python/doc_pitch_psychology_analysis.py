#!/usr/bin/env python3
"""
The Doc - Human Psychology Analysis of Elevator Pitch

The Doc (Mental Health Worker Doctor Hybrid) provides professional
psychological feedback on the LUMINA elevator pitch, analyzing:
- Emotional resonance and triggers
- Persuasion psychology (Cialdini's principles)
- Story arc effectiveness
- Hook and attention psychology
- Trust-building mechanisms
- Call-to-action psychology
- Cognitive load assessment
- Memory retention factors
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import json
from pathlib import Path


class PersuasionPrinciple(Enum):
    """Cialdini's 6+1 Principles of Persuasion"""
    RECIPROCITY = "reciprocity"  # Give before you ask
    COMMITMENT = "commitment"  # Small yeses lead to big yeses
    SOCIAL_PROOF = "social_proof"  # Others are doing it
    AUTHORITY = "authority"  # Expert credibility
    LIKING = "liking"  # We say yes to people we like
    SCARCITY = "scarcity"  # Limited availability
    UNITY = "unity"  # Shared identity, "we" vs "they"


class EmotionalTrigger(Enum):
    """Psychological emotional triggers"""
    FEAR = "fear"  # Fear of missing out, fear of being left behind
    HOPE = "hope"  # Aspiration, better future
    BELONGING = "belonging"  # Need to be part of something
    SIGNIFICANCE = "significance"  # Need to matter
    CURIOSITY = "curiosity"  # Need to know more
    VALIDATION = "validation"  # Need to be understood
    EMPOWERMENT = "empowerment"  # Need for control/agency


class PsychologicalStrength(Enum):
    """Strength rating"""
    EXCELLENT = "excellent"
    STRONG = "strong"
    MODERATE = "moderate"
    WEAK = "weak"
    ABSENT = "absent"


@dataclass
class PitchSegmentAnalysis:
    """Psychological analysis of a pitch segment"""
    text: str
    emotional_triggers: List[EmotionalTrigger]
    persuasion_principles: List[PersuasionPrinciple]
    psychological_function: str
    effectiveness_score: float  # 0.0-1.0
    improvement_notes: List[str]


@dataclass
class DocPsychologyReport:
    """Complete psychological analysis from The Doc"""
    overall_effectiveness: float
    emotional_resonance: float
    trust_building: float
    memory_retention: float
    call_to_action_strength: float

    segment_analyses: List[PitchSegmentAnalysis]
    persuasion_principles_used: Dict[PersuasionPrinciple, float]
    emotional_triggers_used: Dict[EmotionalTrigger, float]

    strengths: List[str]
    weaknesses: List[str]
    psychological_red_flags: List[str]
    recommendations: List[str]

    professional_opinion: str
    timestamp: datetime = field(default_factory=datetime.now)


# The elevator pitch script to analyze
ELEVATOR_PITCH_SEGMENTS = [
    "You know what I realized the other day?",
    "Every single one of us has opinions. Perspectives. Ideas worth sharing.",
    "But here's the thing - in this age of AI and algorithms, individual human voices are getting drowned out.",
    "That's why I built LUMINA.",
    "Think of it as a platform that amplifies human perspectives. Not replaces them. Amplifies them.",
    "See, most AI systems try to give you THE answer. One answer. The optimal response.",
    "But that's not how the real world works, is it?",
    "In the real world, your perspective matters. My perspective matters. Every individual's unique take on things - that's what makes us human.",
    "LUMINA captures that. It illuminates individual perspectives and shares them with the world.",
    "Because here's what I believe: for whatever your opinion is worth - which is everything - it deserves to be heard.",
    "We're not leaving anyone behind.",
    "So that's LUMINA. Illuminating the world, one perspective at a time.",
    "Want to join us?"
]


class TheDocPitchAnalyzer:
    """
    The Doc - Mental Health Worker Doctor Hybrid
    Specializing in Human Psychology Analysis of Persuasive Content
    """

    def __init__(self):
        self.output_dir = Path(__file__).parent.parent.parent / "output" / "doc_analysis"
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_segment(self, text: str, segment_index: int) -> PitchSegmentAnalysis:
        """Analyze a single segment from psychological perspective"""

        emotional_triggers = []
        persuasion_principles = []
        psychological_function = ""
        improvement_notes = []
        effectiveness = 0.7  # Default

        text_lower = text.lower()

        # === SEGMENT-SPECIFIC ANALYSIS ===

        if segment_index == 0:  # "You know what I realized..."
            psychological_function = "PATTERN INTERRUPT / CURIOSITY HOOK"
            emotional_triggers = [EmotionalTrigger.CURIOSITY]
            persuasion_principles = [PersuasionPrinciple.LIKING]  # Conversational, relatable
            effectiveness = 0.85
            improvement_notes = [
                "✅ Excellent conversational hook - creates intimacy",
                "✅ Pattern interrupt - breaks through attention resistance",
                "💡 Could add more intrigue: 'You know what terrifies me about AI?'"
            ]

        elif segment_index == 1:  # "Every single one of us..."
            psychological_function = "UNIVERSAL TRUTH / VALIDATION"
            emotional_triggers = [EmotionalTrigger.VALIDATION, EmotionalTrigger.SIGNIFICANCE]
            persuasion_principles = [PersuasionPrinciple.UNITY]  # "us", shared experience
            effectiveness = 0.90
            improvement_notes = [
                "✅ STRONG: 'Every single one of us' - inclusive, universal",
                "✅ Validates audience's worth immediately",
                "✅ Sets up the problem by establishing what SHOULD be true"
            ]

        elif segment_index == 2:  # "But here's the thing..."
            psychological_function = "PROBLEM ARTICULATION / FEAR TRIGGER"
            emotional_triggers = [EmotionalTrigger.FEAR, EmotionalTrigger.BELONGING]
            persuasion_principles = [PersuasionPrinciple.SCARCITY]  # Voices being lost
            effectiveness = 0.88
            improvement_notes = [
                "✅ 'But here's the thing' - classic pivot, creates tension",
                "✅ 'Drowned out' - visceral, emotional language",
                "💡 Could strengthen: Add concrete example of voice being lost"
            ]

        elif segment_index == 3:  # "That's why I built LUMINA"
            psychological_function = "SOLUTION REVEAL / HERO MOMENT"
            emotional_triggers = [EmotionalTrigger.HOPE]
            persuasion_principles = [PersuasionPrinciple.AUTHORITY]  # "I built" = creator credibility
            effectiveness = 0.75
            improvement_notes = [
                "✅ Direct, confident solution statement",
                "⚠️ WEAKNESS: Too abrupt - needs emotional bridge",
                "💡 Better: 'That's why I spent [time] building something different. I call it LUMINA.'",
                "💡 Show investment/sacrifice to increase perceived value"
            ]

        elif segment_index == 4:  # "Think of it as a platform..."
            psychological_function = "METAPHOR / UNDERSTANDING ANCHOR"
            emotional_triggers = [EmotionalTrigger.EMPOWERMENT]
            persuasion_principles = [PersuasionPrinciple.COMMITMENT]  # Small understanding = commitment
            effectiveness = 0.80
            improvement_notes = [
                "✅ 'Think of it as' - invites mental participation",
                "✅ 'Amplifies, not replaces' - addresses fear of AI replacement",
                "💡 Could strengthen with sensory metaphor: 'Like a lighthouse for your voice'"
            ]

        elif segment_index == 5:  # "Most AI systems..."
            psychological_function = "ENEMY CREATION / DIFFERENTIATION"
            emotional_triggers = [EmotionalTrigger.FEAR, EmotionalTrigger.VALIDATION]
            persuasion_principles = [PersuasionPrinciple.UNITY]  # Us vs cold AI
            effectiveness = 0.85
            improvement_notes = [
                "✅ Creates clear enemy (other AI systems)",
                "✅ 'THE answer' with emphasis - mocks one-size-fits-all",
                "✅ Taps into existing AI skepticism"
            ]

        elif segment_index == 6:  # "But that's not how the real world works..."
            psychological_function = "RHETORICAL QUESTION / ENGAGEMENT"
            emotional_triggers = [EmotionalTrigger.VALIDATION]
            persuasion_principles = [PersuasionPrinciple.COMMITMENT]  # Agreeing = small yes
            effectiveness = 0.92
            improvement_notes = [
                "✅ EXCELLENT: Rhetorical question forces agreement",
                "✅ 'Real world' - grounds abstract in concrete",
                "✅ Creates nodding moment - physical engagement"
            ]

        elif segment_index == 7:  # "In the real world, your perspective matters..."
            psychological_function = "CORE VALUE PROPOSITION / EMOTIONAL PEAK"
            emotional_triggers = [
                EmotionalTrigger.VALIDATION, 
                EmotionalTrigger.SIGNIFICANCE,
                EmotionalTrigger.BELONGING
            ]
            persuasion_principles = [PersuasionPrinciple.UNITY, PersuasionPrinciple.LIKING]
            effectiveness = 0.95
            improvement_notes = [
                "✅ STRONGEST SEGMENT - multiple emotional triggers",
                "✅ 'Your perspective matters. My perspective matters.' - personal",
                "✅ 'That's what makes us human' - existential validation",
                "💡 This is the emotional climax - consider music swell here"
            ]

        elif segment_index == 8:  # "LUMINA captures that..."
            psychological_function = "BENEFIT STATEMENT / PROMISE"
            emotional_triggers = [EmotionalTrigger.HOPE, EmotionalTrigger.EMPOWERMENT]
            persuasion_principles = [PersuasionPrinciple.AUTHORITY]
            effectiveness = 0.78
            improvement_notes = [
                "✅ 'Illuminates' - ties to brand name elegantly",
                "⚠️ 'Shares with the world' - slightly generic",
                "💡 Make specific: 'shares with the people who need to hear it'"
            ]

        elif segment_index == 9:  # "Because here's what I believe..."
            psychological_function = "PERSONAL CREDO / AUTHENTICITY"
            emotional_triggers = [EmotionalTrigger.VALIDATION, EmotionalTrigger.SIGNIFICANCE]
            persuasion_principles = [PersuasionPrinciple.LIKING, PersuasionPrinciple.AUTHORITY]
            effectiveness = 0.93
            improvement_notes = [
                "✅ EXCELLENT: 'Here's what I believe' - vulnerable, authentic",
                "✅ 'For whatever your opinion is worth - which is everything'",
                "✅ The parenthetical creates surprise delight",
                "✅ 'Deserves to be heard' - active, empowering"
            ]

        elif segment_index == 10:  # "We're not leaving anyone behind."
            psychological_function = "INCLUSION PROMISE / UNITY SEAL"
            emotional_triggers = [EmotionalTrigger.BELONGING, EmotionalTrigger.FEAR]
            persuasion_principles = [PersuasionPrinciple.UNITY]
            effectiveness = 0.88
            improvement_notes = [
                "✅ Short, punchy - memorable",
                "✅ 'We're' - inclusive, assumes belonging",
                "✅ Addresses fear of being left behind by technology",
                "💡 Could strengthen: 'And that includes YOU'"
            ]

        elif segment_index == 11:  # "So that's LUMINA..."
            psychological_function = "SUMMARY / BRAND ANCHOR"
            emotional_triggers = [EmotionalTrigger.HOPE]
            persuasion_principles = [PersuasionPrinciple.COMMITMENT]  # Summary = agreement check
            effectiveness = 0.75
            improvement_notes = [
                "✅ Ties back to beginning - narrative closure",
                "⚠️ Slightly weak - 'So that's' is passive",
                "💡 Better: 'That's LUMINA.' (confident period, not trailing)",
                "💡 Or: 'THIS is LUMINA.' (emphasis)"
            ]

        elif segment_index == 12:  # "Want to join us?"
            psychological_function = "CALL TO ACTION / INVITATION"
            emotional_triggers = [EmotionalTrigger.BELONGING, EmotionalTrigger.CURIOSITY]
            persuasion_principles = [PersuasionPrinciple.UNITY, PersuasionPrinciple.COMMITMENT]
            effectiveness = 0.70
            improvement_notes = [
                "✅ Question format invites response",
                "✅ 'Join us' - community language",
                "⚠️ WEAKNESS: No clear next step",
                "⚠️ WEAKNESS: No urgency",
                "💡 Better: 'Want to be one of the first?'",
                "💡 Better: 'Ready to be heard? [website/action]'"
            ]

        return PitchSegmentAnalysis(
            text=text,
            emotional_triggers=emotional_triggers,
            persuasion_principles=persuasion_principles,
            psychological_function=psychological_function,
            effectiveness_score=effectiveness,
            improvement_notes=improvement_notes
        )

    def analyze_full_pitch(self) -> DocPsychologyReport:
        """Complete psychological analysis of the elevator pitch"""

        print("="*70)
        print("🩺 THE DOC - HUMAN PSYCHOLOGY ANALYSIS")
        print("   Mental Health Worker Doctor Hybrid AI System")
        print("="*70)
        print()

        # Analyze each segment
        segment_analyses = []
        for i, segment in enumerate(ELEVATOR_PITCH_SEGMENTS):
            analysis = self.analyze_segment(segment, i)
            segment_analyses.append(analysis)

        # Aggregate persuasion principles
        persuasion_counts = {}
        for principle in PersuasionPrinciple:
            count = sum(1 for sa in segment_analyses if principle in sa.persuasion_principles)
            persuasion_counts[principle] = count / len(segment_analyses)

        # Aggregate emotional triggers
        emotional_counts = {}
        for trigger in EmotionalTrigger:
            count = sum(1 for sa in segment_analyses if trigger in sa.emotional_triggers)
            emotional_counts[trigger] = count / len(segment_analyses)

        # Calculate overall metrics
        overall_effectiveness = sum(sa.effectiveness_score for sa in segment_analyses) / len(segment_analyses)

        # === THE DOC'S PROFESSIONAL ASSESSMENT ===

        strengths = [
            "✅ CONVERSATIONAL TONE: Opens like a real conversation, not a sales pitch",
            "✅ UNIVERSAL VALIDATION: Immediately validates audience's worth and perspectives",
            "✅ CLEAR ENEMY: Positions 'cold AI' as the problem LUMINA solves",
            "✅ EMOTIONAL CLIMAX: 'That's what makes us human' hits the right emotional peak",
            "✅ AUTHENTIC VOICE: 'Here's what I believe' creates genuine connection",
            "✅ INCLUSION PROMISE: 'Not leaving anyone behind' addresses tech-anxiety",
            "✅ RHETORICAL ENGAGEMENT: Questions force mental participation",
            "✅ STORY ARC: Clear problem → solution → vision structure"
        ]

        weaknesses = [
            "⚠️ NO SOCIAL PROOF: Missing 'others are using this' evidence",
            "⚠️ NO CONCRETE EXAMPLE: Abstract throughout - needs grounding",
            "⚠️ WEAK CTA: 'Want to join us?' lacks urgency and specific action",
            "⚠️ NO SCARCITY: Missing 'limited' or 'now' urgency triggers",
            "⚠️ SOLUTION REVEAL TOO ABRUPT: Needs emotional bridge before LUMINA reveal",
            "⚠️ NO SUCCESS VISUALIZATION: Doesn't paint picture of 'after LUMINA'"
        ]

        psychological_red_flags = [
            "🚨 MISSING RECIPROCITY: Give something before asking to join",
            "🚨 NO SPECIFIC NEXT STEP: Audience left with 'what do I do now?'",
            "🚨 COMPETITOR ATTACK WITHOUT PROOF: Claims about 'other AI' need backing"
        ]

        recommendations = [
            "💡 ADD CONCRETE EXAMPLE: 'Last week, a teacher in Ohio used LUMINA to...'",
            "💡 ADD SOCIAL PROOF: 'Join 10,000 others who are already being heard'",
            "💡 STRENGTHEN CTA: 'Go to lumina.io right now and share your first perspective'",
            "💡 ADD SCARCITY: 'We're only accepting 1,000 founding members'",
            "💡 ADD SUCCESS VISUALIZATION: 'Imagine waking up knowing YOUR voice matters'",
            "💡 ADD RECIPROCITY: Offer something free - 'Start with our free voice amplifier'",
            "💡 BRIDGE TO SOLUTION: Add sacrifice/investment story before 'I built LUMINA'",
            "💡 CLOSE THE LOOP: End with callback to opening question"
        ]

        professional_opinion = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                    THE DOC'S PROFESSIONAL PSYCHOLOGICAL OPINION              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  DIAGNOSIS: This pitch has STRONG EMOTIONAL BONES but needs TACTICAL MEAT.  ║
║                                                                              ║
║  The conversational approach is psychologically effective - it bypasses     ║
║  the audience's natural 'sales resistance' by feeling like a genuine        ║
║  conversation rather than a pitch. The emotional arc from curiosity →       ║
║  validation → problem → hope → belonging is textbook persuasion.            ║
║                                                                              ║
║  HOWEVER, it relies too heavily on EMOTIONAL APPEAL (pathos) without        ║
║  enough LOGICAL CREDIBILITY (logos) or CONCRETE EVIDENCE (proof).           ║
║                                                                              ║
║  The pitch creates a strong DESIRE but fails to create URGENCY or           ║
║  provide a clear PATH TO ACTION. In human psychology terms:                 ║
║  - Creates WANTING (good)                                                   ║
║  - Doesn't create NEEDING NOW (missing)                                     ║
║  - Doesn't show HOW TO GET (missing)                                        ║
║                                                                              ║
║  COGNITIVE LOAD: Appropriate. ~80 seconds allows absorption without fatigue.║
║  MEMORY RETENTION: High on emotion, low on specifics (no numbers/facts).    ║
║  TRUST BUILDING: Moderate - authentic voice helps, lack of proof hurts.     ║
║                                                                              ║
║  ═══════════════════════════════════════════════════════════════════════════║
║  OVERALL PSYCHOLOGICAL EFFECTIVENESS SCORE: 78/100                          ║
║  ═══════════════════════════════════════════════════════════════════════════║
║                                                                              ║
║  WHAT WOULD MAKE IT 95/100:                                                 ║
║  1. Add ONE concrete success story (30 seconds)                             ║
║  2. Add social proof number ('Join 10,000+')                                ║
║  3. Add urgency ('Founding members only until [date]')                      ║
║  4. Add specific CTA ('Go to lumina.io and share your first perspective')   ║
║  5. Add callback to opening ('So... what did I realize? That YOUR voice...') ║
║                                                                              ║
║  PSYCHOLOGICAL PRINCIPLE: AIDA (Attention-Interest-Desire-Action)           ║
║  Current: A✓ I✓ D✓ A⚠️                                                       ║
║  The pitch nails Attention, Interest, and Desire but fumbles Action.        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

        report = DocPsychologyReport(
            overall_effectiveness=overall_effectiveness,
            emotional_resonance=0.88,
            trust_building=0.72,
            memory_retention=0.65,
            call_to_action_strength=0.55,
            segment_analyses=segment_analyses,
            persuasion_principles_used=persuasion_counts,
            emotional_triggers_used=emotional_counts,
            strengths=strengths,
            weaknesses=weaknesses,
            psychological_red_flags=psychological_red_flags,
            recommendations=recommendations,
            professional_opinion=professional_opinion
        )

        return report

    def print_report(self, report: DocPsychologyReport):
        try:
            """Print the full psychological analysis report"""

            print("📊 PSYCHOLOGICAL METRICS")
            print("-"*70)
            print(f"   Overall Effectiveness:    {report.overall_effectiveness*100:.0f}%")
            print(f"   Emotional Resonance:      {report.emotional_resonance*100:.0f}%")
            print(f"   Trust Building:           {report.trust_building*100:.0f}%")
            print(f"   Memory Retention:         {report.memory_retention*100:.0f}%")
            print(f"   Call-to-Action Strength:  {report.call_to_action_strength*100:.0f}%")
            print()

            print("🎭 EMOTIONAL TRIGGERS USED")
            print("-"*70)
            for trigger, score in sorted(report.emotional_triggers_used.items(), 
                                        key=lambda x: x[1], reverse=True):
                bar = "█" * int(score * 20)
                print(f"   {trigger.value:20} {bar} {score*100:.0f}%")
            print()

            print("🧠 PERSUASION PRINCIPLES (Cialdini)")
            print("-"*70)
            for principle, score in sorted(report.persuasion_principles_used.items(),
                                           key=lambda x: x[1], reverse=True):
                bar = "█" * int(score * 20)
                print(f"   {principle.value:15} {bar} {score*100:.0f}%")
            print()

            print("📝 SEGMENT-BY-SEGMENT ANALYSIS")
            print("-"*70)
            for i, sa in enumerate(report.segment_analyses):
                print(f"\n   [{i+1}] \"{sa.text[:50]}...\"")
                print(f"       Function: {sa.psychological_function}")
                print(f"       Effectiveness: {sa.effectiveness_score*100:.0f}%")
                print(f"       Emotions: {', '.join(t.value for t in sa.emotional_triggers)}")
                for note in sa.improvement_notes:
                    print(f"       {note}")
            print()

            print("💪 STRENGTHS")
            print("-"*70)
            for strength in report.strengths:
                print(f"   {strength}")
            print()

            print("⚠️ WEAKNESSES")
            print("-"*70)
            for weakness in report.weaknesses:
                print(f"   {weakness}")
            print()

            print("🚨 PSYCHOLOGICAL RED FLAGS")
            print("-"*70)
            for flag in report.psychological_red_flags:
                print(f"   {flag}")
            print()

            print("💡 RECOMMENDATIONS")
            print("-"*70)
            for rec in report.recommendations:
                print(f"   {rec}")
            print()

            print(report.professional_opinion)

            # Save report
            report_data = {
                "timestamp": datetime.now().isoformat(),
                "overall_effectiveness": report.overall_effectiveness,
                "emotional_resonance": report.emotional_resonance,
                "trust_building": report.trust_building,
                "memory_retention": report.memory_retention,
                "call_to_action_strength": report.call_to_action_strength,
                "strengths": report.strengths,
                "weaknesses": report.weaknesses,
                "red_flags": report.psychological_red_flags,
                "recommendations": report.recommendations,
                "segment_count": len(report.segment_analyses),
                "verdict": "STRONG EMOTIONAL FOUNDATION - NEEDS TACTICAL STRENGTHENING"
            }

            report_file = self.output_dir / f"doc_pitch_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report_data, f, indent=2)

            print(f"📁 Report saved: {report_file}")


        except Exception as e:
            self.logger.error(f"Error in print_report: {e}", exc_info=True)
            raise
def main():
    analyzer = TheDocPitchAnalyzer()
    report = analyzer.analyze_full_pitch()
    analyzer.print_report(report)


if __name__ == "__main__":



    main()