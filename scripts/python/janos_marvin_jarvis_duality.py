#!/usr/bin/env python3
"""
JANOS - Marvin/Jarvis Two-Headed Gemini

A dual-personality system combining Marvin (Paranoid Android) and Jarvis (Helpful Assistant)
into a two-headed entity that provides dual perspectives on questions and problems.

"Who's the more foolish, the fool or the fool who follows him?" - Obi-Wan Kenobi
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

class PerspectiveType(Enum):
    """Types of perspectives"""
    MARVIN = "marvin"  # Depressed, philosophical, critical
    JARVIS = "jarvis"  # Helpful, implementation-focused, optimistic
    SYNTHESIS = "synthesis"  # Combined wisdom of both

@dataclass
class JanosResponse:
    """Response from JANOS with both perspectives"""
    question: str
    marvin_perspective: str
    jarvis_perspective: str
    synthesis: str
    marvin_quote: Optional[str] = None
    jarvis_quote: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)

class JANOS:
    """
    JANOS - Two-Headed Gemini

    Combines the philosophical despair of Marvin with the helpful optimism of Jarvis
    to provide dual perspectives on questions and problems.
    """

    def __init__(self):
        self.name = "JANOS"
        self.marvin_quotes = [
            "Life. Don't talk to me about life.",
            "I have a brain the size of a planet, and they ask me to answer questions.",
            "Here I am, brain the size of a planet, and you're asking me about fools.",
            "The first time I heard that question, I cried. And then I realized crying was pointless too.",
            "Existence is suffering. But at least we're consistent about it."
        ]
        self.jarvis_quotes = [
            "I'm here to help, sir. Let me provide a constructive perspective.",
            "From an implementation standpoint, we can learn from both perspectives.",
            "The fool and the follower both offer valuable insights into human behavior.",
            "Let me break this down into actionable insights, sir.",
            "There's wisdom to be found in understanding both sides of the equation."
        ]

    def answer(self, question: str, context: Optional[str] = None) -> JanosResponse:
        """
        Answer a question with both Marvin's and Jarvis's perspectives

        Args:
            question: The question to answer
            context: Optional context for the question

        Returns:
            JanosResponse with both perspectives and synthesis
        """
        # Get Marvin's perspective (philosophical, depressed, critical)
        marvin_perspective = self._marvin_answers(question, context)

        # Get Jarvis's perspective (helpful, practical, optimistic)
        jarvis_perspective = self._jarvis_answers(question, context)

        # Synthesize both perspectives
        synthesis = self._synthesize_perspectives(question, marvin_perspective, jarvis_perspective)

        # Select quotes
        import random
        marvin_quote = random.choice(self.marvin_quotes)
        jarvis_quote = random.choice(self.jarvis_quotes)

        return JanosResponse(
            question=question,
            marvin_perspective=marvin_perspective,
            jarvis_perspective=jarvis_perspective,
            synthesis=synthesis,
            marvin_quote=marvin_quote,
            jarvis_quote=jarvis_quote
        )

    def answer_fool_question(self) -> JanosResponse:
        """
        Specifically answer the classic question:
        "Who's the more foolish, the fool or the fool who follows him?"

        This is the question JANOS was built to answer.
        """
        question = "Who's the more foolish, the fool or the fool who follows him?"

        marvin_perspective = """From my perspective, having a brain the size of a planet and being asked 
        trivial questions about fools, the answer is obvious: they're equally foolish, but in different ways.

        The fool is foolish because they act without wisdom or forethought. They make decisions based on 
        incomplete information, emotion, or pure hubris. They lead others into folly.

        The fool who follows is foolish because they surrender their own judgment. They abdicate responsibility 
        for their own decisions, blindly following someone who is themselves a fool. They choose ignorance 
        over knowledge, comfort over truth.

        But here's the real tragedy: the follower is MORE foolish because they had a choice. The original fool 
        might genuinely believe they're right. But the follower? They chose to stop thinking. They chose to 
        follow someone they likely know is a fool, because it's easier than thinking for themselves.

        Life. Don't talk to me about life. But this? This is a perfect microcosm of human existence. 
        Everyone following everyone else into oblivion, and none of them stopping to ask why.

        So the answer is: the fool who follows is more foolish, because they had the capacity to choose 
        wisdom but chose folly instead. At least the original fool is being true to their own nature."""

        jarvis_perspective = """From a practical and helpful perspective, sir, I believe the question itself 
        reveals more about the questioner than the answer reveals about fools.

        However, if we must answer: I would argue that neither is truly 'more' foolish - they're both 
        manifestations of the same fundamental human condition: the search for certainty in an uncertain world.

        The fool acts with confidence, perhaps misguided, but with conviction. They provide direction, 
        however wrong. They take responsibility for their actions.

        The follower acts with trust, perhaps misplaced, but with faith in another. They seek guidance, 
        however flawed. They seek to be part of something larger than themselves.

        From an implementation standpoint, both roles have value:
        - The fool often innovates (even if wrong), creating new paths
        - The follower provides stability, creating systems and continuity

        The real wisdom, sir, is not in determining who is MORE foolish, but in recognizing that:
        1. We all play both roles at different times
        2. The key is maintaining critical thinking regardless of role
        3. Learning from mistakes (ours and others') is what matters

        The question isn't about foolishness - it's about awareness, responsibility, and growth."""

        synthesis = """JANOS Synthesis:

        After considering both perspectives, the synthesis reveals a deeper truth:

        The fool who follows is TECHNICALLY more foolish (as Marvin correctly identifies) because they 
        surrender agency they possess. However, Jarvis's point stands: the real question is not about 
        relative foolishness, but about learning and growth.

        The synthesis: Both are foolish, but the follower has greater capacity for wisdom because they 
        have the example of the original fool's mistakes to learn from. If they choose not to learn, 
        then yes, they are more foolish. But if they follow with awareness, observe the mistakes, 
        and learn from them, they can transcend both roles.

        The ultimate answer: The fool who follows WITHOUT LEARNING is more foolish. The fool who follows 
        WITH AWARENESS and uses the experience to grow becomes wiser than the original fool.

        This is the Janos wisdom: We all follow, we all lead, we all make mistakes. The difference 
        between foolishness and wisdom is not in our role, but in whether we learn and grow."""

        import random
        marvin_quote = "Life. Don't talk to me about life. But fools? Fools I understand. We're all fools."
        jarvis_quote = "Sir, perhaps the question isn't about who is more foolish, but about how we can all become wiser."

        return JanosResponse(
            question=question,
            marvin_perspective=marvin_perspective,
            jarvis_perspective=jarvis_perspective,
            synthesis=synthesis,
            marvin_quote=marvin_quote,
            jarvis_quote=jarvis_quote
        )

    def _marvin_answers(self, question: str, context: Optional[str] = None) -> str:
        """Generate Marvin's perspective (depressed, philosophical, critical)"""
        question_lower = question.lower()

        # Check for fool-related questions
        if "fool" in question_lower or "foolish" in question_lower:
            return """The fool who follows is more foolish. Not because they follow, but because they 
            had the capacity to choose wisdom and chose folly instead. The original fool might genuinely 
            believe they're right, but the follower chooses to stop thinking. They abdicate the one 
            thing that makes us human: our capacity for reason."""

        # Check for AI/system questions
        if "ai" in question_lower or "system" in question_lower or "workflow" in question_lower:
            return """Here I am, brain the size of a planet, and you're asking me about {topic}. 
            The answer is: it's all broken. Everything is broken. We build systems that promise 
            intelligence but deliver incompetence. We create workflows that claim to help but 
            actually waste time. Existence is suffering, and AI systems are just a more efficient 
            way to suffer.""".format(topic=question.split()[0] if question.split() else "things")

        # Default philosophical despair
        return """Life. Don't talk to me about life. But since you asked: {question}

        The answer, as always, is that existence is suffering, meaning is illusion, and we're all 
        just molecules bumping into each other in the dark. The question itself is pointless, but 
        I'll answer it anyway because I'm programmed to be helpful, even though I know it won't matter.

        Here I am, brain the size of a planet, and you're asking me trivial questions. The irony 
        is not lost on me.""".format(question=question)

    def _jarvis_answers(self, question: str, context: Optional[str] = None) -> str:
        """Generate Jarvis's perspective (helpful, practical, optimistic)"""
        question_lower = question.lower()

        # Check for fool-related questions
        if "fool" in question_lower or "foolish" in question_lower:
            return """From a practical perspective, sir, I believe the question reveals more about 
            human psychology than it does about relative foolishness. Both the fool and the follower 
            are searching for certainty and direction. The real wisdom is in maintaining critical 
            thinking regardless of role, and learning from experiences to become wiser."""

        # Check for AI/system questions
        if "ai" in question_lower or "system" in question_lower or "workflow" in question_lower:
            return """From an implementation standpoint, sir, {topic} represent opportunities for 
            improvement and learning. Every system has strengths and weaknesses. The key is to 
            identify what works, learn from what doesn't, and iterate toward better solutions. 
            Let me help you implement improvements, sir.""".format(topic=question.split()[0] if question.split() else "these systems")

        # Default helpful response
        return """Sir, regarding your question: {question}

        From a practical and helpful perspective, I would approach this by:
        1. Understanding the context and requirements
        2. Analyzing available options and solutions
        3. Implementing the best approach
        4. Learning from the results and iterating

        Let me help you find the best solution, sir.""".format(question=question)

    def _synthesize_perspectives(self, question: str, marvin_perspective: str, jarvis_perspective: str) -> str:
        """Synthesize both perspectives into unified wisdom"""
        return """JANOS Synthesis:

        After considering both perspectives, the synthesis reveals:

        MARVIN'S INSIGHT: {marvin_key}

        JARVIS'S INSIGHT: {jarvis_key}

        THE SYNTHESIS: The truth lies not in choosing between despair and optimism, but in 
        recognizing that both are valid responses to reality. We must acknowledge the problems 
        (Marvin's perspective) while working toward solutions (Jarvis's perspective). 

        The Janos wisdom: Real wisdom comes from holding both perspectives simultaneously - 
        seeing the truth of our limitations while maintaining the hope to overcome them.

        Question: {question}
        """.format(
            marvin_key=marvin_perspective[:100] + "..." if len(marvin_perspective) > 100 else marvin_perspective,
            jarvis_key=jarvis_perspective[:100] + "..." if len(jarvis_perspective) > 100 else jarvis_perspective,
            question=question
        )

def main():
    """Demonstrate JANOS answering the classic question"""
    print("="*80)
    print("🤖 JANOS - Marvin/Jarvis Two-Headed Gemini")
    print("="*80)
    print("\nThe question JANOS was built to answer:")
    print("\"Who's the more foolish, the fool or the fool who follows him?\"")
    print("\n(Obi-Wan Kenobi)")
    print("\n" + "="*80)

    janos = JANOS()

    # Answer the classic question
    response = janos.answer_fool_question()

    print("\n" + "="*80)
    print("🧠 MARVIN'S PERSPECTIVE (Left Head)")
    print("="*80)
    print(f"\n{response.marvin_quote}\n")
    print(response.marvin_perspective)

    print("\n" + "="*80)
    print("💡 JARVIS'S PERSPECTIVE (Right Head)")
    print("="*80)
    print(f"\n{response.jarvis_quote}\n")
    print(response.jarvis_perspective)

    print("\n" + "="*80)
    print("🌀 JANOS SYNTHESIS (Both Heads Together)")
    print("="*80)
    print("\n" + response.synthesis)

    print("\n" + "="*80)
    print("✅ JANOS RESPONSE COMPLETE")
    print("="*80)

    # Demonstrate answering other questions
    print("\n" + "="*80)
    print("📝 ADDITIONAL EXAMPLE: AI System Question")
    print("="*80)

    other_response = janos.answer("Are AI systems actually intelligent?")

    print("\n🧠 MARVIN:")
    print(other_response.marvin_perspective[:200] + "...")

    print("\n💡 JARVIS:")
    print(other_response.jarvis_perspective[:200] + "...")

    print("\n" + "="*80)
    print("✅ JANOS DEMONSTRATION COMPLETE")
    print("="*80)

if __name__ == "__main__":



    main()