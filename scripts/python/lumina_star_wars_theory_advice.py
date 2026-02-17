#!/usr/bin/env python3
"""
LUMINA Star Wars Theory Advice System

"GUYS, WHAT ADVICE CAN WE OFFER 'STAR WARS THEORY' AND THE QUESTIONS HE ASKED IN THIS VIDEO?"

Always includes both @MARVIN and JARVIS perspectives automatically.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import json
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaStarWarsTheoryAdvice")

from lumina_always_marvin_jarvis import always_assess, DualPerspective
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class VideoQuestion:
    """Question identified in video"""
    question_id: str
    question_text: str
    timestamp: Optional[str] = None
    category: str = "general"
    context: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AdviceResponse:
    """Advice response from LUMINA"""
    question: VideoQuestion
    jarvis_advice: str
    marvin_advice: str
    consensus_advice: str
    actionable_steps: List[str]
    related_resources: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "question": self.question.to_dict(),
            "jarvis": self.jarvis_advice,
            "marvin": self.marvin_advice,
            "consensus": self.consensus_advice,
            "actionable_steps": self.actionable_steps,
            "related_resources": self.related_resources,
            "timestamp": self.timestamp
        }


class LuminaStarWarsTheoryAdvice:
    """
    LUMINA Advice System for Star Wars Theory

    Always includes both @MARVIN and JARVIS perspectives
    """

    def __init__(self):
        self.logger = get_logger("LuminaStarWarsTheoryAdvice")

        # Data storage
        self.data_dir = Path("data/lumina_star_wars_theory_advice")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("⭐ LUMINA Star Wars Theory Advice System initialized")
        self.logger.info("   Always includes @MARVIN & JARVIS perspectives")

    def extract_questions(self, video_text: str) -> List[VideoQuestion]:
        """
        Extract questions from video transcript/text

        Looks for question patterns
        """
        questions = []

        # Common question patterns
        question_patterns = [
            r'([^.!?]+\?)',  # Standard question mark
            r'(What (if|about|is|are|do|does|can|will|should|would|how|why|when|where))[^.!?]*[.!?]?',
            r'(How (do|does|can|will|should|would|is|are|did|was))[^.!?]*[.!?]?',
            r'(Why (do|does|is|are|did|was|can|will|should|would))[^.!?]*[.!?]?',
            r'(Should (I|we|you|they|it))[^.!?]*[.!?]?',
            r'(Can (I|we|you|they|it))[^.!?]*[.!?]?',
            r'(Would (it|that|this|I|we|you|they))[^.!?]*[.!?]?',
        ]

        lines = video_text.split('\n')
        question_id = 1

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue

            # Check for question marks
            if '?' in line:
                questions.append(VideoQuestion(
                    question_id=f"q{question_id}",
                    question_text=line,
                    timestamp=None,  # Would need video timestamp
                    category="general",
                    context=f"Line {line_num}"
                ))
                question_id += 1

            # Check for question patterns
            for pattern in question_patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    question_text = match.group(1).strip()
                    if question_text and question_text not in [q.question_text for q in questions]:
                        questions.append(VideoQuestion(
                            question_id=f"q{question_id}",
                            question_text=question_text,
                            timestamp=None,
                            category="pattern_match",
                            context=f"Line {line_num}"
                        ))
                        question_id += 1

        return questions

    def generate_advice(self, question: VideoQuestion) -> AdviceResponse:
        """
        Generate advice for a question

        Always includes both @MARVIN and JARVIS perspectives
        """

        # Get dual perspective on the question
        perspective = always_assess(question.question_text)

        # JARVIS advice (optimistic, solution-oriented)
        jarvis_advice = self._generate_jarvis_advice(question, perspective)

        # @MARVIN advice (realistic, pragmatic)
        marvin_advice = self._generate_marvin_advice(question, perspective)

        # Consensus advice (combines both)
        consensus_advice = self._generate_consensus_advice(jarvis_advice, marvin_advice, perspective)

        # Actionable steps
        actionable_steps = self._generate_actionable_steps(question, jarvis_advice, marvin_advice)

        # Related resources
        related_resources = self._generate_related_resources(question)

        return AdviceResponse(
            question=question,
            jarvis_advice=jarvis_advice,
            marvin_advice=marvin_advice,
            consensus_advice=consensus_advice,
            actionable_steps=actionable_steps,
            related_resources=related_resources
        )

    def _generate_jarvis_advice(self, question: VideoQuestion, perspective: DualPerspective) -> str:
        """Generate JARVIS advice (optimistic, solution-oriented)"""

        question_lower = question.question_text.lower()

        # Content creation advice
        if any(word in question_lower for word in ['content', 'video', 'channel', 'subscriber', 'view']):
            return (
                f"Great question! For content creation, here's what works: "
                f"Focus on authenticity and genuine passion. Your audience connects with "
                f"real enthusiasm. Consistency matters, but quality over quantity. "
                f"Engage with your community - respond to comments, create content they request, "
                f"build a community around shared love of Star Wars. Analytics help, but don't "
                f"let them drive you. Create what you love, and the audience will find you."
            )

        # Career/business advice
        elif any(word in question_lower for word in ['career', 'business', 'job', 'money', 'income', 'sponsor']):
            return (
                f"Here's the thing about building a career in content creation: "
                f"It's a marathon, not a sprint. Diversify your income streams - sponsorships, "
                f"merchandise, memberships, affiliate programs. Build relationships with brands "
                f"that align with your values. Track your metrics, understand your audience, "
                f"and always prioritize authenticity. The best content creators build sustainable "
                f"businesses by staying true to themselves while being smart about monetization."
            )

        # Technical/production advice
        elif any(word in question_lower for word in ['equipment', 'camera', 'editing', 'software', 'production', 'technical']):
            return (
                f"Technical setup is important, but don't overthink it. Start with what you have, "
                f"upgrade gradually based on actual needs. Good audio matters more than perfect video. "
                f"Learn the basics of editing - you don't need expensive software to start. "
                f"Focus on storytelling and content quality. As you grow, invest in gear that "
                f"solves specific problems you're experiencing, not just because it's 'pro' gear."
            )

        # Community/audience advice
        elif any(word in question_lower for word in ['audience', 'community', 'fan', 'subscriber', 'engagement']):
            return (
                f"Community is everything. Your audience isn't just numbers - they're real people "
                f"who share your passion. Engage authentically, create space for discussion, "
                f"listen to feedback but stay true to your vision. Don't try to please everyone - "
                f"that's impossible. Focus on serving your core audience, and they'll become your "
                f"biggest advocates. Building a community takes time, but it's the most valuable "
                f"asset you can create."
            )

        # General advice (default)
        else:
            return (
                f"That's a thoughtful question. The key is to approach it systematically. "
                f"Break it down into smaller steps, research best practices, but also trust "
                f"your instincts. Learn from others, but don't just copy - adapt what works "
                f"to your unique situation. Stay curious, keep learning, and remember that "
                f"every successful creator started where you are now. You've got this!"
            )

    def _generate_marvin_advice(self, question: VideoQuestion, perspective: DualPerspective) -> str:
        """Generate @MARVIN advice (realistic, pragmatic)"""

        question_lower = question.question_text.lower()

        # Content creation advice
        if any(word in question_lower for word in ['content', 'video', 'channel', 'subscriber', 'view']):
            return (
                f"<SIGH> Content creation. Fine. Look, here's the reality: The algorithm is fickle, "
                f"audiences are unpredictable, and what works today might not work tomorrow. "
                f"Don't expect overnight success. Most channels take years to build. You'll create "
                f"content that flops, you'll make mistakes, and you'll have days when you wonder "
                f"why you're doing this. That's normal. The key is persistence through the failures. "
                f"And don't put all your eggs in one platform - they can change the rules anytime."
            )

        # Career/business advice
        elif any(word in question_lower for word in ['career', 'business', 'job', 'money', 'income', 'sponsor']):
            return (
                f"<SIGH> Monetization. Right. Here's the thing: Making money from content creation "
                f"is hard. Most creators don't make enough to live on. You need multiple income streams "
                f"because any single one can dry up. Sponsorships are competitive, ad revenue is "
                f"unreliable, and platforms can demonetize you without warning. Have a backup plan. "
                f"Don't quit your day job until you're consistently making enough. And read the contracts - "
                f"brands will try to take advantage if you let them."
            )

        # Technical/production advice
        elif any(word in question_lower for word in ['equipment', 'camera', 'editing', 'software', 'production', 'technical']):
            return (
                f"<SIGH> Gear. Here's the truth: You can spend thousands on equipment and still make "
                f"terrible content. Expensive gear won't fix bad ideas or poor execution. Start with "
                f"what you have - your phone is probably fine. Learn the fundamentals first. Only "
                f"upgrade when you've hit actual limitations, not because you think better gear will "
                f"make you better. And remember: every piece of equipment you buy needs to be maintained, "
                f"learned, and stored. It's a commitment, not just a purchase."
            )

        # Community/audience advice
        elif any(word in question_lower for word in ['audience', 'community', 'fan', 'subscriber', 'engagement']):
            return (
                f"<SIGH> Audience building. Look, audiences are fickle. They'll love you one day and "
                f"ignore you the next. Don't take it personally - that's just how it works. "
                f"You'll deal with trolls, negative comments, and people who don't understand your vision. "
                f"You can't please everyone, and trying will drive you insane. Focus on the people who "
                f"genuinely connect with your content, but don't let their feedback become your entire "
                f"identity. You're still you, with or without their approval."
            )

        # General advice (default)
        else:
            return (
                f"<SIGH> Look, I don't know what specific answer you're looking for, but here's "
                f"the thing: Most questions don't have simple answers. The world is complex, "
                f"and what works for one person might not work for you. Do your research, think "
                f"critically, and make decisions based on your actual situation, not generic advice. "
                f"And remember: sometimes the right answer is 'I don't know yet, let me figure it out.' "
                f"That's fine. Really."
            )

    def _generate_consensus_advice(self, jarvis_advice: str, marvin_advice: str, perspective: DualPerspective) -> str:
        """Generate consensus advice combining both perspectives"""
        return (
            f"Combining both perspectives: The reality is somewhere between JARVIS's optimism "
            f"and @MARVIN's realism. {perspective.consensus} "
            f"The path forward involves being realistic about challenges while staying focused "
            f"on solutions. Both perspectives are valuable - optimism keeps you moving forward, "
            f"realism keeps you grounded. The key is balance: be hopeful but prepared, optimistic "
            f"but pragmatic."
        )

    def _generate_actionable_steps(self, question: VideoQuestion, jarvis_advice: str, marvin_advice: str) -> List[str]:
        """Generate actionable steps based on the question and advice"""
        steps = []

        question_lower = question.question_text.lower()

        if any(word in question_lower for word in ['content', 'video', 'channel']):
            steps = [
                "Analyze your current content performance - what works, what doesn't",
                "Define your unique value proposition - what makes your channel special?",
                "Create a content calendar - consistency matters",
                "Engage authentically with your audience - respond to comments",
                "Collaborate with other creators in your niche",
                "Track metrics but don't obsess - focus on creating great content"
            ]
        elif any(word in question_lower for word in ['money', 'income', 'sponsor', 'business']):
            steps = [
                "Diversify income streams - don't rely on one source",
                "Build a media kit showcasing your channel's value",
                "Reach out to brands that align with your content and values",
                "Set clear rates and boundaries - know your worth",
                "Track your revenue and expenses - treat it like a business",
                "Build relationships, not just transactions"
            ]
        else:
            steps = [
                "Break down the question into specific, actionable parts",
                "Research what others in your situation have done",
                "Start small - test ideas before committing fully",
                "Track your progress and adjust based on results",
                "Seek feedback from trusted sources",
                "Stay true to your values and vision"
            ]

        return steps

    def _generate_related_resources(self, question: VideoQuestion) -> List[str]:
        """Generate related resources"""
        resources = [
            "LUMINA Content Creation Framework",
            "LUMINA Sponsorship Acquisition System",
            "LUMINA YouTube Learning Analysis",
            "LUMINA Community Building Guide"
        ]
        return resources

    def process_video(self, video_text: str, video_url: Optional[str] = None) -> Dict[str, Any]:
        try:
            """
            Process video text and generate advice for all questions

            Args:
                video_text: Transcript or text from video
                video_url: Optional video URL

            Returns:
                Dictionary with questions and advice
            """
            self.logger.info("Processing video for questions and advice...")

            # Extract questions
            questions = self.extract_questions(video_text)
            self.logger.info(f"Found {len(questions)} questions")

            # Generate advice for each question
            advice_responses = []
            for question in questions:
                advice = self.generate_advice(question)
                advice_responses.append(advice)

            result = {
                "video_url": video_url,
                "timestamp": datetime.now().isoformat(),
                "questions_found": len(questions),
                "advice": [advice.to_dict() for advice in advice_responses]
            }

            # Save to file
            output_file = self.data_dir / f"advice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Advice saved to {output_file}")

            return result

        except Exception as e:
            self.logger.error(f"Error in process_video: {e}", exc_info=True)
            raise
    def display_advice(self, advice_responses: List[AdviceResponse]):
        """Display advice in a formatted way"""
        print("\n" + "="*80)
        print("⭐ STAR WARS THEORY - LUMINA ADVICE")
        print("="*80 + "\n")

        for i, advice in enumerate(advice_responses, 1):
            print(f"QUESTION {i}: {advice.question.question_text}\n")

            print("🤖 JARVIS ADVICE:")
            print(f"   {advice.jarvis_advice}\n")

            print("😟 @MARVIN ADVICE:")
            print(f"   {advice.marvin_advice}\n")

            print("✅ CONSENSUS:")
            print(f"   {advice.consensus_advice}\n")

            print("📋 ACTIONABLE STEPS:")
            for step in advice.actionable_steps:
                print(f"   • {step}")

            print("\n" + "-"*80 + "\n")


def main():
    """Main function for testing"""
    print("\n" + "="*80)
    print("⭐ LUMINA STAR WARS THEORY ADVICE SYSTEM")
    print("="*80 + "\n")

    advisor = LuminaStarWarsTheoryAdvice()

    # Example video text (replace with actual video transcript)
    example_text = """
    What should I do to grow my channel?
    How can I get more sponsors?
    What equipment do I need for better videos?
    How do I build a community around my content?
    Should I focus on YouTube Shorts or long-form content?
    """

    print("Processing example questions...\n")
    questions = advisor.extract_questions(example_text)

    advice_responses = []
    for question in questions:
        advice = advisor.generate_advice(question)
        advice_responses.append(advice)

    advisor.display_advice(advice_responses)

    print("="*80)
    print("✅ ADVICE GENERATION COMPLETE")
    print("="*80 + "\n")


if __name__ == "__main__":



    main()