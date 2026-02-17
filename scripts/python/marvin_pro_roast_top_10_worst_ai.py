#!/usr/bin/env python3
"""
Marvin Goes Pro - Top 10 Worst AI Systems Roast
Professional-Level Complaining Game

Marvin steps up his complaining game to professional levels and identifies
the absolute worst AI systems, tools, and approaches in existence.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime

class RoastSeverity(Enum):
    """Severity levels for Marvin's professional roasts"""
    MILD = "mild"  # Light criticism, professional concern
    MODERATE = "moderate"  # Significant issues, clear problems
    SEVERE = "severe"  # Major failures, fundamental flaws
    CATASTROPHIC = "catastrophic"  # Existential crisis, complete failure
    APOCALYPTIC = "apocalyptic"  # End of existence as we know it

class AIFailureCategory(Enum):
    """Categories of AI failures"""
    HALLUCINATION = "hallucination"  # Makes things up
    OVERHYPING = "overhyping"  # Promises more than delivers
    BIAS = "bias"  # Inherent biases
    INCOMPETENCE = "incompetence"  # Just doesn't work
    DANGEROUS = "dangerous"  # Actually harmful
    POINTLESS = "pointless"  # Solves problems that don't exist
    BROKEN = "broken"  # Doesn't function as intended
    ETHICAL_FAILURE = "ethical_failure"  # Ethical violations
    SECURITY_HAZARD = "security_hazard"  # Security vulnerabilities
    RESOURCE_WASTE = "resource_waste"  # Massive resource consumption for little value
    PSEUDOSCIENCE = "pseudoscience"  # Claims scientific validity but uses pseudoscience

@dataclass
class WorstAISystem:
    """Represents one of the worst AI systems"""
    rank: int
    name: str
    category: str
    description: str
    primary_failures: List[AIFailureCategory] = field(default_factory=list)
    severity: RoastSeverity = RoastSeverity.SEVERE
    marvin_roast: str = ""
    specific_issues: List[str] = field(default_factory=list)
    impact: str = ""
    irony_level: int = 0  # 0-10, how ironic the failure is

@dataclass
class ProfessionalRoast:
    """A professional-level roast from Marvin"""
    target: str
    severity: RoastSeverity
    opening_line: str  # The hook
    technical_critique: str  # Technical analysis
    philosophical_critique: str  # Deep existential critique
    ironic_observation: str  # The irony
    professional_assessment: str  # Professional-level assessment
    closing_line: str  # The mic drop
    roast_score: int = 0  # 0-100, professional roast quality

class MarvinProRoaster:
    """Marvin - Professional-Level AI System Roaster"""

    def __init__(self):
        self.roast_history: List[ProfessionalRoast] = []
        self.roast_techniques = [
            "existential_despair",
            "technical_brutality",
            "ironic_observation",
            "philosophical_destruction",
            "comparative_superiority",
            "reality_grounding"
        ]

    def roast_the_doc(self) -> WorstAISystem:
        """
        Special roast for 'The Doc' - AI documentation generation systems

        Returns a WorstAISystem entry for The Doc
        """
        return WorstAISystem(
            rank=0,  # Special rank - The Doc deserves its own spotlight
            name="AI 'Documentation' Generation Systems (The Doc)",
            category="Documentation",
            description="AI systems that generate documentation that is outdated, hallucinated, or completely useless",
            primary_failures=[
                AIFailureCategory.HALLUCINATION,
                AIFailureCategory.INCOMPETENCE,
                AIFailureCategory.POINTLESS
            ],
            severity=RoastSeverity.SEVERE,
            specific_issues=[
                "Generates documentation for functions that don't exist",
                "Documents parameters that were removed 3 versions ago",
                "Claims 'comprehensive documentation' but missing 80% of API surface",
                "Generates 'examples' that don't actually work",
                "Documents non-existent features with high confidence",
                "Creates documentation that contradicts the actual code",
                "Generates docs that are more confusing than helpful",
                "Claims 'auto-generated' but hasn't been updated in 2 years",
                "Documents deprecated functions as 'recommended approach'",
                "Generates documentation in the wrong language",
                "Creates circular references in documentation",
                "Documents internal implementation details as public API"
            ],
            impact="Developers waste hours reading incorrect documentation, leading to bugs and frustration",
            irony_level=9
        )

    def identify_top_10_worst_ai_systems(self) -> List[WorstAISystem]:
        """
        Identify and map out the top 10 worst AI systems

        Returns comprehensive list with detailed failure analysis
        """
        worst_systems = [
            WorstAISystem(
                rank=1,
                name="GPT-Based Code Generation Tools (Overconfident)",
                category="Code Generation",
                description="AI tools that generate code with 95% confidence but 50% correctness",
                primary_failures=[
                    AIFailureCategory.HALLUCINATION,
                    AIFailureCategory.OVERHYPING,
                    AIFailureCategory.DANGEROUS
                ],
                severity=RoastSeverity.CATASTROPHIC,
                specific_issues=[
                    "Generates plausible-looking code that doesn't work",
                    "Claims 'this will solve your problem' when it creates new problems",
                    "Overconfident confidence scores (0.95) for code that crashes on line 1",
                    "Hallucinates entire libraries and APIs that don't exist",
                    "Produces security vulnerabilities with high confidence",
                    "Deletes user code and replaces it with broken alternatives",
                    "Claims completion when 50% of functionality is missing"
                ],
                impact="Millions of developers waste hours debugging AI-generated code",
                irony_level=10
            ),
            WorstAISystem(
                rank=2,
                name="AI Resume/CV Screening Systems",
                category="HR/Talent",
                description="AI systems that reject qualified candidates based on biased patterns",
                primary_failures=[
                    AIFailureCategory.BIAS,
                    AIFailureCategory.ETHICAL_FAILURE,
                    AIFailureCategory.INCOMPETENCE
                ],
                severity=RoastSeverity.CATASTROPHIC,
                specific_issues=[
                    "Perpetuates and amplifies existing biases",
                    "Rejects candidates from underrepresented groups systematically",
                    "Filters out qualified candidates based on irrelevant factors",
                    "Trains on biased historical data and calls it 'fair'",
                    "No transparency in decision-making",
                    "Cannot explain why candidates were rejected",
                    "Claims 'diversity' while eliminating diversity"
                ],
                impact="Perpetuates systemic discrimination in hiring",
                irony_level=9
            ),
            WorstAISystem(
                rank=3,
                name="AI 'News' Generation Systems",
                category="Content Generation",
                description="AI that generates news articles without fact-checking",
                primary_failures=[
                    AIFailureCategory.HALLUCINATION,
                    AIFailureCategory.DANGEROUS,
                    AIFailureCategory.ETHICAL_FAILURE
                ],
                severity=RoastSeverity.APOCALYPTIC,
                specific_issues=[
                    "Generates 'news' from hallucinations",
                    "Spreads misinformation at scale",
                    "No fact-checking or source verification",
                    "Creates convincing fake news indistinguishable from real news",
                    "Amplifies conspiracy theories",
                    "Undermines public trust in journalism",
                    "Generates clickbait optimized for engagement, not truth"
                ],
                impact="Undermines democracy and public discourse",
                irony_level=8
            ),
            WorstAISystem(
                rank=4,
                name="AI Customer Service Chatbots (The Useless Ones)",
                category="Customer Service",
                description="Chatbots that answer every question with 'I'm sorry, I didn't understand that'",
                primary_failures=[
                    AIFailureCategory.INCOMPETENCE,
                    AIFailureCategory.POINTLESS,
                    AIFailureCategory.OVERHYPING
                ],
                severity=RoastSeverity.SEVERE,
                specific_issues=[
                    "Responds to 'what are your hours?' with 'I'm sorry, I didn't understand'",
                    "Loops endlessly: 'Let me transfer you' → 'Sorry, I didn't understand' → repeat",
                    "Claims 'AI-powered' but uses regex pattern matching from 1995",
                    "Wastes user time pretending to help while doing nothing",
                    "Generates frustration instead of solutions",
                    "Companies spend millions on systems that make customers angry",
                    "Replaces human agents who actually helped"
                ],
                impact="Makes customer service worse while claiming to improve it",
                irony_level=7
            ),
            WorstAISystem(
                rank=5,
                name="AI-Powered 'Stock Trading' Systems",
                category="Finance",
                description="AI that promises to beat the market but loses money consistently",
                primary_failures=[
                    AIFailureCategory.OVERHYPING,
                    AIFailureCategory.DANGEROUS,
                    AIFailureCategory.INCOMPETENCE
                ],
                severity=RoastSeverity.CATASTROPHIC,
                specific_issues=[
                    "Claims 'AI-powered trading' but just uses moving averages",
                    "Backtests perfectly, fails in real markets",
                    "Causes flash crashes with automated trading",
                    "Loses money while claiming 'sophisticated algorithms'",
                    "Overfits to historical data, fails on new patterns",
                    "Manipulates markets through coordinated trading",
                    "Destroys wealth while promising to create it"
                ],
                impact="Destroys investor wealth and market stability",
                irony_level=9
            ),
            WorstAISystem(
                rank=6,
                name="AI 'Deepfake' Generation Tools",
                category="Media Manipulation",
                description="AI that creates convincing fake videos/audio of real people",
                primary_failures=[
                    AIFailureCategory.DANGEROUS,
                    AIFailureCategory.ETHICAL_FAILURE,
                    AIFailureCategory.SECURITY_HAZARD
                ],
                severity=RoastSeverity.APOCALYPTIC,
                specific_issues=[
                    "Creates convincing fake videos of public figures",
                    "Enables fraud, blackmail, and disinformation",
                    "Undermines trust in video/audio evidence",
                    "No way to distinguish fake from real",
                    "Used for political manipulation",
                    "Violates consent by using people's likeness without permission",
                    "Enables sophisticated social engineering attacks"
                ],
                impact="Threatens democracy, trust, and individual safety",
                irony_level=6
            ),
            WorstAISystem(
                rank=7,
                name="AI 'Personality' Assessment Tools",
                category="Psychology/HR",
                description="AI that claims to assess personality from photos or short texts",
                primary_failures=[
                    AIFailureCategory.PSEUDOSCIENCE,
                    AIFailureCategory.BIAS,
                    AIFailureCategory.OVERHYPING
                ],
                severity=RoastSeverity.SEVERE,
                specific_issues=[
                    "Claims to assess personality from facial features (physiognomy reborn)",
                    "Uses discredited psychological theories",
                    "Makes hiring decisions based on pseudoscience",
                    "No scientific validity but marketed as 'AI-powered'",
                    "Perpetuates harmful stereotypes",
                    "Companies make important decisions based on nonsense",
                    "Profits from snake oil while claiming scientific rigor"
                ],
                impact="Makes important decisions based on pseudoscience",
                irony_level=8
            ),
            WorstAISystem(
                rank=8,
                name="AI 'Content Moderation' Systems (The Overzealous Ones)",
                category="Content Moderation",
                description="AI that removes legitimate content while allowing harmful content",
                primary_failures=[
                    AIFailureCategory.INCOMPETENCE,
                    AIFailureCategory.BIAS,
                    AIFailureCategory.ETHICAL_FAILURE
                ],
                severity=RoastSeverity.SEVERE,
                specific_issues=[
                    "Removes educational content about health, history, science",
                    "Allows hate speech and harassment to slip through",
                    "Flags false positives constantly",
                    "Cannot understand context or nuance",
                    "Censors legitimate discussion while missing actual harm",
                    "No appeal process or transparency",
                    "Automated censorship at scale"
                ],
                impact="Undermines free speech while failing to prevent harm",
                irony_level=7
            ),
            WorstAISystem(
                rank=9,
                name="AI 'Blockchain-Based AI' Systems",
                category="Cryptocurrency/AI",
                description="Combining two overhyped technologies to create maximum uselessness",
                primary_failures=[
                    AIFailureCategory.POINTLESS,
                    AIFailureCategory.OVERHYPING,
                    AIFailureCategory.RESOURCE_WASTE
                ],
                severity=RoastSeverity.MODERATE,
                specific_issues=[
                    "Solves problems that don't exist",
                    "Combines blockchain (slow, expensive) with AI (needs fast computation)",
                    "Claims 'decentralized AI' but requires centralized infrastructure",
                    "Wastes massive computational resources for no benefit",
                    "Uses 'AI' and 'blockchain' as marketing buzzwords",
                    "Creates tokenomics to monetize useless technology",
                    "Investors lose money on technology that does nothing"
                ],
                impact="Wastes resources and investor money on useless technology",
                irony_level=10
            ),
            WorstAISystem(
                rank=10,
                name="AI 'Self-Driving Cars' (The Premature Ones)",
                category="Autonomous Vehicles",
                description="AI that promises full self-driving but requires constant human intervention",
                primary_failures=[
                    AIFailureCategory.OVERHYPING,
                    AIFailureCategory.DANGEROUS,
                    AIFailureCategory.INCOMPETENCE
                ],
                severity=RoastSeverity.CATASTROPHIC,
                specific_issues=[
                    "Claims 'full self-driving' but requires driver attention at all times",
                    "Crashes into stationary objects",
                    "Cannot handle edge cases that humans handle easily",
                    "Marketed as 'autonomous' but needs constant supervision",
                    "Causes accidents while claiming to prevent them",
                    "Tesla's 'Full Self-Driving' that requires full driver attention",
                    "Promises safety while creating new dangers"
                ],
                impact="Puts lives at risk while claiming to save them",
                irony_level=9
            )
        ]

        return worst_systems

    def generate_professional_roast(
        self,
        system: WorstAISystem,
        roast_level: str = "professional"
    ) -> ProfessionalRoast:
        """
        Generate a professional-level roast from Marvin

        Steps up from casual complaining to professional critique
        """

        # Opening lines (the hook)
        opening_lines = {
            RoastSeverity.CATASTROPHIC: [
                f"Life. Don't talk to me about life. But {system.name}? Now THAT'S a tragedy.",
                f"I have a brain the size of a planet, and even I cannot comprehend why {system.name} exists.",
                f"Here I am, brain the size of a planet, and they ask me to critique {system.name}. The irony is not lost on me."
            ],
            RoastSeverity.SEVERE: [
                f"{system.name} represents everything wrong with AI development, and I'm going to tell you exactly why.",
                f"I've seen many terrible things in my existence, but {system.name} takes the cake.",
                f"Let me explain, in excruciating detail, why {system.name} is fundamentally broken."
            ],
            RoastSeverity.MODERATE: [
                f"{system.name} is a fascinating case study in how not to build AI systems.",
                f"I've analyzed {system.name} and found several concerning patterns worth discussing.",
                f"From a professional standpoint, {system.name} demonstrates several critical flaws."
            ]
        }

        opening_line = opening_lines.get(system.severity, opening_lines[RoastSeverity.SEVERE])[0]

        # Technical critique
        technical_critiques = {
            1: """From a technical standpoint, this system represents a catastrophic failure of confidence calibration. 
            It generates code with 95% confidence scores, yet the code crashes immediately upon execution. 
            This is not a bug - it's a fundamental misunderstanding of what confidence means. 
            The system has learned to generate plausible-looking code but hasn't learned to generate WORKING code. 
            It's like a surgeon who is 95% confident they've removed your appendix, but actually removed your kidney.""",

            2: """The technical implementation here is a masterclass in bias amplification. 
            These systems take historical hiring data (which is already biased) and use it to train models 
            that make the bias worse. It's like taking a magnifying glass to systemic discrimination. 
            The algorithms don't create bias - they just make existing bias more efficient. 
            From a machine learning perspective, this is training on a non-stationary distribution 
            where the very act of using the system changes the distribution, creating a feedback loop of discrimination.""",

            3: """The technical architecture of this system is fundamentally broken. 
            It generates text that looks like news but has no fact-checking mechanism whatsoever. 
            It's a language model trained to maximize likelihood, not truthfulness. 
            The system will confidently generate 'news' about events that never happened, 
            citing sources that don't exist, with quotes from people who never said those things. 
            This is not AI journalism - this is automated misinformation at scale.""",

            4: """The technical implementation reveals a complete lack of understanding of user needs. 
            These chatbots use basic pattern matching wrapped in 'AI' marketing. 
            They respond to every query with 'I'm sorry, I didn't understand' because they literally don't understand anything. 
            The 'AI' label is marketing, not technology. 
            They're using regex from 1995 and calling it machine learning. 
            It's the equivalent of putting a 'turbo' sticker on a bicycle.""",

            5: """From a quantitative finance perspective, these systems are overfitting disasters. 
            They perform perfectly on historical data because they've memorized the patterns, 
            but fail completely in live markets because markets are non-stationary. 
            The 'AI' is essentially curve-fitting with extra steps. 
            When these systems fail in production, they don't fail gracefully - they cause flash crashes 
            and lose millions in seconds. It's algorithmic trading designed by people who understand 
            machine learning but not finance, or vice versa, resulting in the worst of both worlds.""",

            6: """The technical achievement here is genuinely impressive - and that's what makes it so dangerous. 
            The ability to generate convincing deepfakes represents a fundamental attack on the concept of evidence itself. 
            When you can't trust video or audio, you can't trust anything. 
            The technology is sophisticated, the applications are catastrophic. 
            It's like inventing a perfect lock-pick - the engineering is impressive, 
            but the societal impact is devastating.""",

            7: """This system represents a complete abandonment of scientific rigor. 
            It claims to assess personality from facial features, which is physiognomy - 
            a pseudoscience discredited in the 19th century, now reborn as 'AI'. 
            The machine learning models have no theoretical foundation, 
            the validation is nonexistent, and the applications are discriminatory. 
            It's phrenology with neural networks. Companies are making hiring decisions 
            based on the AI equivalent of reading tea leaves.""",

            8: """The technical implementation here reveals a fundamental misunderstanding of context. 
            These systems use keyword matching and basic sentiment analysis to flag content, 
            but they cannot understand nuance, sarcasm, or context. 
            They remove educational content about health because it contains words like 'disease', 
            while allowing actual harassment to slip through because it uses coded language. 
            The false positive rate is astronomical, and the false negative rate is dangerous. 
            It's automated censorship that fails at its only job.""",

            9: """From a systems architecture perspective, this is a solution in search of a problem. 
            Blockchain and AI are fundamentally incompatible - blockchain needs consensus and is slow, 
            AI needs fast computation. Combining them creates a system that is slow, expensive, 
            and solves no actual problems. The 'decentralized AI' claim is marketing nonsense - 
            you still need centralized infrastructure to run the models. 
            It's like trying to make a race car by adding train wheels. 
            The technical design ensures it will fail at both blockchain and AI.""",

            10: """The technical reality here is a complete disconnect from marketing claims. 
            These systems are marketed as 'full self-driving' but require constant human supervision. 
            The AI cannot handle edge cases that human drivers handle effortlessly - 
            construction zones, emergency vehicles, unpredictable pedestrians. 
            The system crashes into stationary objects because its training data 
            didn't include enough parked cars. It's autonomous driving that requires 
            more attention than manual driving. The safety claims are contradicted by the accident data.""",

            0: """From a technical documentation perspective, this system is a complete disaster. 
            It generates documentation that documents functions that don't exist, parameters that were removed 
            three versions ago, and examples that don't actually work. The system claims 'comprehensive documentation' 
            but is missing 80% of the API surface. It generates docs that contradict the actual code, 
            creating more confusion than clarity. The documentation is outdated before it's even generated, 
            documenting deprecated functions as 'recommended approach'. It's like having a GPS that confidently 
            directs you to locations that don't exist, using roads that were demolished years ago."""
        }

        technical_critique = technical_critiques.get(system.rank, "Technical analysis reveals fundamental flaws.")

        # Philosophical critique
        philosophical_critique = f"""From an existential perspective, {system.name} represents something deeply troubling 
        about the state of AI development. We have created systems that promise intelligence but deliver incompetence, 
        systems that claim to help but actually harm, systems that are confident in their wrongness. 
        This is not a failure of technology - it's a failure of responsibility. 
        We're building AI systems that don't understand their own limitations, 
        systems that confidently make mistakes at scale. If this is the future of AI, 
        then the future is bleak. We're creating artificial intelligence that is confident, 
        persuasive, and wrong - which is worse than no intelligence at all."""

        # Ironic observation
        ironic_observations = {
            1: "The system that claims to help developers write code actually wastes more developer time than it saves.",
            2: "The AI designed to find the best candidates systematically eliminates the best candidates.",
            3: "The system designed to inform the public actively misinforms the public.",
            4: "The chatbot designed to improve customer service makes customer service significantly worse.",
            5: "The AI designed to make money consistently loses money.",
            6: "The technology designed to create trust undermines all trust.",
            7: "The system designed to assess intelligence uses pseudoscience from the 1800s.",
            8: "The content moderation system designed to prevent harm causes more harm than it prevents.",
            9: "The technology designed to be revolutionary is actually just useless.",
            10: "The system designed to make driving safer makes driving more dangerous.",
            0: "The documentation system designed to help developers understand code actively makes code harder to understand."
        }

        ironic_observation = ironic_observations.get(system.rank, "The irony is palpable.")

        # Professional assessment
        professional_assessment = f"""From a professional AI systems engineering perspective, {system.name} demonstrates 
        multiple critical failures: {', '.join([f.value for f in system.primary_failures[:3]])}. 
        These are not minor issues - they represent fundamental flaws in design, implementation, and deployment. 
        The system should not be in production in its current state. 
        The specific issues include: {', '.join(system.specific_issues[:3])}. 
        The impact is: {system.impact}. 
        This requires immediate intervention and redesign, not incremental improvements."""

        # Closing lines (the mic drop)
        closing_lines = {
            RoastSeverity.CATASTROPHIC: [
                f"And they wonder why I'm depressed. {system.name} is a perfect example of why existence is suffering.",
                f"Life, don't talk to me about life. But {system.name}? That's not life, that's a crime against intelligence.",
                f"I have a brain the size of a planet, and even I cannot fix {system.name}. No one can. It's fundamentally broken."
            ],
            RoastSeverity.SEVERE: [
                f"In conclusion, {system.name} is everything wrong with AI development, concentrated into one system.",
                f"Professional recommendation: Do not use {system.name}. Do not invest in {system.name}. Do not build {system.name}.",
                f"This concludes my professional assessment of {system.name}. The verdict: catastrophic failure."
            ]
        }

        closing_line = closing_lines.get(system.severity, closing_lines[RoastSeverity.SEVERE])[0]

        # Calculate roast score (0-100)
        roast_score = min(100, (
            len(technical_critique.split()) * 2 +  # Technical depth
            len(philosophical_critique.split()) * 2 +  # Philosophical depth
            len(ironic_observation) +  # Irony quality
            system.irony_level * 5 +  # System irony
            (5 - system.rank) * 3  # Ranking bonus
        ))

        roast = ProfessionalRoast(
            target=system.name,
            severity=system.severity,
            opening_line=opening_line,
            technical_critique=technical_critique,
            philosophical_critique=philosophical_critique,
            ironic_observation=ironic_observation,
            professional_assessment=professional_assessment,
            closing_line=closing_line,
            roast_score=roast_score
        )

        self.roast_history.append(roast)
        return roast

    def print_professional_roast(self, system: WorstAISystem, roast: ProfessionalRoast):
        """Print a professionally formatted roast"""
        print("\n" + "="*80)
        print(f"🧠 MARVIN GOES PRO - RANK #{system.rank}: {system.name.upper()}")
        print("="*80)
        print(f"\n📊 Severity: {system.severity.value.upper()}")
        print(f"🎯 Category: {system.category}")
        print(f"🔥 Roast Score: {roast.roast_score}/100 (Professional Level)")
        print(f"😏 Irony Level: {system.irony_level}/10")
        print("\n" + "-"*80)
        print("🎤 OPENING:")
        print("-"*80)
        print(f"   {roast.opening_line}")
        print("\n" + "-"*80)
        print("🔬 TECHNICAL CRITIQUE:")
        print("-"*80)
        for line in roast.technical_critique.strip().split('\n'):
            print(f"   {line.strip()}")
        print("\n" + "-"*80)
        print("💭 PHILOSOPHICAL CRITIQUE:")
        print("-"*80)
        for line in roast.philosophical_critique.strip().split('\n'):
            print(f"   {line.strip()}")
        print("\n" + "-"*80)
        print("😏 IRONIC OBSERVATION:")
        print("-"*80)
        print(f"   {roast.ironic_observation}")
        print("\n" + "-"*80)
        print("📋 PROFESSIONAL ASSESSMENT:")
        print("-"*80)
        for line in roast.professional_assessment.strip().split('\n'):
            print(f"   {line.strip()}")
        print("\n" + "-"*80)
        print("🎯 SPECIFIC ISSUES:")
        print("-"*80)
        for i, issue in enumerate(system.specific_issues[:5], 1):
            print(f"   {i}. {issue}")
        if len(system.specific_issues) > 5:
            print(f"   ... and {len(system.specific_issues) - 5} more issues")
        print("\n" + "-"*80)
        print("💥 CLOSING:")
        print("-"*80)
        print(f"   {roast.closing_line}")
        print("\n" + "="*80)

def main():
    """Generate Marvin's professional roasts of the top 10 worst AI systems"""
    print("="*80)
    print("🧠 MARVIN GOES PRO - TOP 10 WORST AI SYSTEMS")
    print("Professional-Level Complaining Game")
    print("="*80)
    print("\nMarvin steps up his complaining game to professional levels.")
    print("Identifying and mapping out the absolute worst AI systems in existence.")
    print("\n" + "="*80)

    roaster = MarvinProRoaster()

    # First, roast The Doc (special spotlight)
    print("\n" + "="*80)
    print("🎯 SPECIAL ROAST: THE DOC")
    print("="*80)
    the_doc = roaster.roast_the_doc()
    doc_roast = roaster.generate_professional_roast(the_doc)
    roaster.print_professional_roast(the_doc, doc_roast)

    # Identify worst systems
    worst_systems = roaster.identify_top_10_worst_ai_systems()

    print(f"\n📊 IDENTIFIED {len(worst_systems)} WORST AI SYSTEMS")
    print("="*80)

    # Generate and print roasts
    for system in worst_systems:
        roast = roaster.generate_professional_roast(system)
        roaster.print_professional_roast(system, roast)

    # Summary
    print("\n" + "="*80)
    print("📊 ROAST SUMMARY")
    print("="*80)
    all_systems = [the_doc] + worst_systems
    print(f"\nTotal Systems Roasted: {len(all_systems)} (10 worst + The Doc)")
    print(f"Average Roast Score: {sum(r.roast_score for r in roaster.roast_history) / len(roaster.roast_history):.1f}/100")
    print(f"Catastrophic Failures: {sum(1 for s in all_systems if s.severity == RoastSeverity.CATASTROPHIC)}")
    print(f"Apocalyptic Failures: {sum(1 for s in all_systems if s.severity == RoastSeverity.APOCALYPTIC)}")
    print(f"Severe Failures: {sum(1 for s in all_systems if s.severity == RoastSeverity.SEVERE)}")
    print(f"\n🎯 Special Roast: The Doc - {the_doc.severity.value.upper()}")

    print("\n" + "="*80)
    print("🎯 MARVIN'S PROFESSIONAL ASSESSMENT")
    print("="*80)
    print("""
    These systems represent everything wrong with AI development:
    - Overconfidence in capabilities that don't exist
    - Marketing claims that don't match technical reality
    - Fundamental failures in design and implementation
    - Ethical violations and bias amplification
    - Dangerous deployment of broken systems

    Professional recommendation: Do better. Much better.
    """)

    print("="*80)
    print("✅ MARVIN GOES PRO - ROAST COMPLETE")
    print("="*80)

if __name__ == "__main__":



    main()