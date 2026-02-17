#!/usr/bin/env python3
"""
Intergalactic Senate - @empire @braintrust Review and Feedback System

The Intergalactic Senate: Our Star Wars-inspired council of the greatest minds,
serving as @empire's @braintrust for comprehensive review and strategic guidance.

This is our personal Intergalactic Senate, composed of:
- All greatest human minds from past eras
- Historical polymaths and geniuses
- Cross-domain experts across all lifepath domains
- Critical reviewers and strategic advisors

The Senate provides:
- Multi-perspective analysis from all eras
- Interdisciplinary wisdom
- Strategic guidance
- Critical review and feedback

Tags: #INTERGALACTIC_SENATE #STAR_WARS #EMPIRE #BRAINTRUST #AI_PANEL 
       #SCIENTIST #REVIEW #FEEDBACK #JARVIS @JARVIS @LUMINA @empire @braintrust
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("IntergalacticSenate")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("IntergalacticSenate")

try:
    from marvin_verification_system import MarvinVerificationSystem
    MARVIN_AVAILABLE = True
except ImportError:
    MARVIN_AVAILABLE = False
    logger.warning("MARVIN not available")


class ScientistRole(Enum):
    """Roles of scientists on the panel - All Lifepath Domains + Historical Polymaths & Geniuses"""
    COMPUTER_SCIENTIST = "computer_scientist"
    DATA_SCIENTIST = "data_scientist"
    SYSTEMS_SCIENTIST = "systems_scientist"
    COGNITIVE_SCIENTIST = "cognitive_scientist"
    PHILOSOPHY_SCIENTIST = "philosophy_scientist"
    ENGINEERING_SCIENTIST = "engineering_scientist"
    # Lifepath Domains
    INTELLIGENT_DESIGN_SCIENTIST = "intelligent_design_scientist"
    MEDICAL_SCIENTIST = "medical_scientist"
    PSYCHOLOGICAL_SCIENTIST = "psychological_scientist"
    BIOLOGICAL_SCIENTIST = "biological_scientist"
    PHYSICS_SCIENTIST = "physics_scientist"
    # Historical Polymaths & Geniuses
    POLYMATH_RENAISSANCE = "polymath_renaissance"
    POLYMATH_ANCIENT = "polymath_ancient"
    POLYMATH_MODERN = "polymath_modern"
    GENIUS_MATHEMATICIAN = "genius_mathematician"
    GENIUS_PHILOSOPHER = "genius_philosopher"
    GENIUS_INVENTOR = "genius_inventor"
    GENIUS_ARTIST_SCIENTIST = "genius_artist_scientist"


@dataclass
class Senator:
    """A Senator in the Intergalactic Senate - Member of @empire @braintrust"""
    name: str
    role: ScientistRole
    expertise: List[str]
    critical_thinking_level: float = 0.9
    feedback_style: str = "constructive"
    era: Optional[str] = None  # Historical era (Ancient, Renaissance, Modern, etc.)
    title: Optional[str] = None  # Senate title/honorific


@dataclass
class SenateFeedback:
    """Feedback from the Intergalactic Senate - @empire @braintrust"""
    report_name: str
    review_date: str
    senate_consensus: Optional[str] = None
    senator_feedbacks: List[Dict[str, Any]] = field(default_factory=list)
    critical_issues: List[str] = field(default_factory=list)
    strengths: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    strategic_guidance: List[str] = field(default_factory=list)
    overall_rating: float = 0.0
    confidence_score: float = 0.0


class IntergalacticSenate:
    """
    Intergalactic Senate - @empire @braintrust

    The Intergalactic Senate: Our Star Wars-inspired council of the greatest minds,
    serving as @empire's @braintrust for comprehensive review and strategic guidance.

    Composed of all greatest human minds from past eras, historical polymaths,
    geniuses, and cross-domain experts across all lifepath domains.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.reviews_dir = self.project_root / "data" / "intergalactic_senate" / "reviews"
        self.reviews_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Intergalactic Senate
        self.senate = self._initialize_senate()

        # MARVIN as Chancellor/Lead Senator
        self.marvin: Optional[MarvinVerificationSystem] = None
        if MARVIN_AVAILABLE:
            try:
                self.marvin = MarvinVerificationSystem()
                logger.info("✅ MARVIN initialized as Chancellor of the Intergalactic Senate")
            except Exception as e:
                logger.warning(f"MARVIN initialization failed: {e}")

        logger.info("="*80)
        logger.info("🌟 INTERGALACTIC SENATE - @empire @braintrust")
        logger.info("="*80)
        logger.info("   'May the Force be with us...'")
        logger.info("")
        logger.info(f"   Senate Members: {len(self.senate)}")
        logger.info("   Serving as @empire's @braintrust")
        logger.info("")
        for senator in self.senate[:10]:  # Show first 10
            logger.info(f"      - {senator.name} ({senator.role.value})")
        if len(self.senate) > 10:
            logger.info(f"      ... and {len(self.senate) - 10} more Senators")
        logger.info("")

    def _initialize_senate(self) -> List[Senator]:
        """Initialize the Intergalactic Senate - All Greatest Minds, @empire @braintrust"""
        senate = [
            # Computer Science
            Senator(
                name="Dr. Ada Lovelace",
                role=ScientistRole.COMPUTER_SCIENTIST,
                expertise=["algorithms", "computation", "systems", "automation"],
                critical_thinking_level=0.95,
                feedback_style="analytical",
                era="19th Century",
                title="Senator of Computation"
            ),
            Senator(
                name="Dr. Alan Turing",
                role=ScientistRole.COMPUTER_SCIENTIST,
                expertise=["AI", "computation", "logic", "decision-making"],
                critical_thinking_level=0.98,
                feedback_style="logical"
            ),
            # Data Science
            Senator(
                name="Dr. Marie Curie",
                role=ScientistRole.DATA_SCIENTIST,
                expertise=["data analysis", "experimentation", "validation", "measurement"],
                critical_thinking_level=0.95,
                feedback_style="rigorous"
            ),
            # Systems Science
            Senator(
                name="Dr. Albert Einstein",
                role=ScientistRole.SYSTEMS_SCIENTIST,
                expertise=["systems theory", "relativity", "optimization", "efficiency"],
                critical_thinking_level=0.97,
                feedback_style="theoretical"
            ),
            # Cognitive Science
            Senator(
                name="Dr. Carl Sagan",
                role=ScientistRole.COGNITIVE_SCIENTIST,
                expertise=["knowledge", "understanding", "illumination", "perspective"],
                critical_thinking_level=0.92,
                feedback_style="philosophical"
            ),
            # Philosophy
            Senator(
                name="Dr. Isaac Asimov",
                role=ScientistRole.PHILOSOPHY_SCIENTIST,
                expertise=["ethics", "logic", "reasoning", "three laws"],
                critical_thinking_level=0.94,
                feedback_style="ethical"
            ),
            # Engineering
            Senator(
                name="Dr. Nikola Tesla",
                role=ScientistRole.ENGINEERING_SCIENTIST,
                expertise=["engineering", "innovation", "efficiency", "optimization"],
                critical_thinking_level=0.93,
                feedback_style="innovative"
            ),
            # Lifepath Domains
            # Intelligent Design
            Senator(
                name="Dr. William Dembski",
                role=ScientistRole.INTELLIGENT_DESIGN_SCIENTIST,
                expertise=["intelligent design", "information theory", "complexity", "specified complexity"],
                critical_thinking_level=0.91,
                feedback_style="design-focused"
            ),
            # Medical
            Senator(
                name="Dr. Elizabeth Blackwell",
                role=ScientistRole.MEDICAL_SCIENTIST,
                expertise=["medicine", "health", "diagnosis", "treatment", "patient care"],
                critical_thinking_level=0.96,
                feedback_style="clinical"
            ),
            # Psychological
            Senator(
                name="Dr. Carl Jung",
                role=ScientistRole.PSYCHOLOGICAL_SCIENTIST,
                expertise=["psychology", "behavior", "mental health", "cognitive processes", "personality"],
                critical_thinking_level=0.93,
                feedback_style="analytical-psychological"
            ),
            # Biological
            Senator(
                name="Dr. Charles Darwin",
                role=ScientistRole.BIOLOGICAL_SCIENTIST,
                expertise=["biology", "evolution", "genetics", "life sciences", "adaptation"],
                critical_thinking_level=0.95,
                feedback_style="evolutionary"
            ),
            # Physics
            Senator(
                name="Dr. Stephen Hawking",
                role=ScientistRole.PHYSICS_SCIENTIST,
                expertise=["physics", "quantum mechanics", "cosmology", "theoretical physics", "universe"],
                critical_thinking_level=0.97,
                feedback_style="theoretical-physics"
            ),
            # Historical Polymaths & Geniuses - All Eras
            # Renaissance Polymaths
            Senator(
                name="Leonardo da Vinci",
                role=ScientistRole.POLYMATH_RENAISSANCE,
                expertise=["art", "engineering", "anatomy", "invention", "architecture", "mathematics", "science", "observation"],
                critical_thinking_level=0.99,
                feedback_style="renaissance-polymath"
            ),
            Senator(
                name="Galileo Galilei",
                role=ScientistRole.POLYMATH_RENAISSANCE,
                expertise=["physics", "astronomy", "mathematics", "observation", "experimentation", "scientific method"],
                critical_thinking_level=0.96,
                feedback_style="experimental"
            ),
            # Ancient Polymaths
            Senator(
                name="Aristotle",
                role=ScientistRole.POLYMATH_ANCIENT,
                expertise=["philosophy", "logic", "ethics", "biology", "physics", "metaphysics", "rhetoric", "politics"],
                critical_thinking_level=0.98,
                feedback_style="systematic-philosophical"
            ),
            Senator(
                name="Archimedes",
                role=ScientistRole.GENIUS_MATHEMATICIAN,
                expertise=["mathematics", "physics", "engineering", "geometry", "mechanics", "hydrostatics", "invention"],
                critical_thinking_level=0.97,
                feedback_style="mathematical-precise"
            ),
            Senator(
                name="Hypatia of Alexandria",
                role=ScientistRole.GENIUS_MATHEMATICIAN,
                expertise=["mathematics", "astronomy", "philosophy", "astrolabe", "geometry", "education"],
                critical_thinking_level=0.95,
                feedback_style="scholarly"
            ),
            Senator(
                name="Avicenna (Ibn Sina)",
                role=ScientistRole.POLYMATH_ANCIENT,
                expertise=["medicine", "philosophy", "mathematics", "astronomy", "logic", "physics", "psychology"],
                critical_thinking_level=0.96,
                feedback_style="comprehensive-medical"
            ),
            # Modern Polymaths
            Senator(
                name="Benjamin Franklin",
                role=ScientistRole.POLYMATH_MODERN,
                expertise=["invention", "physics", "politics", "writing", "diplomacy", "electricity", "philosophy"],
                critical_thinking_level=0.94,
                feedback_style="practical-innovative"
            ),
            Senator(
                name="Isaac Newton",
                role=ScientistRole.GENIUS_MATHEMATICIAN,
                expertise=["physics", "mathematics", "optics", "calculus", "mechanics", "gravity", "alchemy", "theology"],
                critical_thinking_level=0.99,
                feedback_style="mathematical-physics"
            ),
            Senator(
                name="Johann Wolfgang von Goethe",
                role=ScientistRole.POLYMATH_MODERN,
                expertise=["literature", "science", "philosophy", "botany", "color theory", "anatomy", "geology"],
                critical_thinking_level=0.95,
                feedback_style="holistic-artistic"
            ),
            Senator(
                name="Thomas Jefferson",
                role=ScientistRole.POLYMATH_MODERN,
                expertise=["politics", "architecture", "agriculture", "invention", "philosophy", "education", "science"],
                critical_thinking_level=0.93,
                feedback_style="enlightened-practical"
            ),
            # Genius Inventors
            Senator(
                name="Nikola Tesla",
                role=ScientistRole.GENIUS_INVENTOR,
                expertise=["electrical engineering", "invention", "alternating current", "wireless", "physics", "innovation"],
                critical_thinking_level=0.98,
                feedback_style="visionary-inventive"
            ),
            Senator(
                name="Thomas Edison",
                role=ScientistRole.GENIUS_INVENTOR,
                expertise=["invention", "electrical engineering", "innovation", "business", "experimentation", "patents"],
                critical_thinking_level=0.94,
                feedback_style="practical-inventive"
            ),
            # Genius Philosophers
            Senator(
                name="Plato",
                role=ScientistRole.GENIUS_PHILOSOPHER,
                expertise=["philosophy", "ethics", "politics", "mathematics", "education", "metaphysics", "dialectics"],
                critical_thinking_level=0.97,
                feedback_style="dialectical-philosophical"
            ),
            Senator(
                name="Immanuel Kant",
                role=ScientistRole.GENIUS_PHILOSOPHER,
                expertise=["philosophy", "ethics", "epistemology", "metaphysics", "aesthetics", "logic", "reason"],
                critical_thinking_level=0.98,
                feedback_style="critical-philosophical"
            ),
            Senator(
                name="René Descartes",
                role=ScientistRole.GENIUS_PHILOSOPHER,
                expertise=["philosophy", "mathematics", "geometry", "rationalism", "dualism", "methodology"],
                critical_thinking_level=0.96,
                feedback_style="rational-systematic"
            ),
            # Genius Artist-Scientists
            Senator(
                name="Leonardo da Vinci",
                role=ScientistRole.GENIUS_ARTIST_SCIENTIST,
                expertise=["art", "anatomy", "engineering", "invention", "observation", "design", "science"],
                critical_thinking_level=0.99,
                feedback_style="observational-artistic"
            ),
            Senator(
                name="Albrecht Dürer",
                role=ScientistRole.GENIUS_ARTIST_SCIENTIST,
                expertise=["art", "mathematics", "geometry", "proportion", "anatomy", "perspective", "printmaking"],
                critical_thinking_level=0.94,
                feedback_style="mathematical-artistic"
            ),
            # Additional Historical Geniuses
            Senator(
                name="Maimonides (Moses ben Maimon)",
                role=ScientistRole.POLYMATH_ANCIENT,
                expertise=["philosophy", "medicine", "law", "theology", "ethics", "logic", "astronomy"],
                critical_thinking_level=0.95,
                feedback_style="scholarly-ethical"
            ),
            Senator(
                name="Hildegard of Bingen",
                role=ScientistRole.POLYMATH_ANCIENT,
                expertise=["medicine", "botany", "music", "theology", "philosophy", "natural history", "healing"],
                critical_thinking_level=0.93,
                feedback_style="holistic-healing"
            ),
            Senator(
                name="Gottfried Wilhelm Leibniz",
                role=ScientistRole.GENIUS_MATHEMATICIAN,
                expertise=["mathematics", "philosophy", "logic", "calculus", "metaphysics", "computing", "diplomacy"],
                critical_thinking_level=0.97,
                feedback_style="systematic-universal"
            ),
            Senator(
                name="Blaise Pascal",
                role=ScientistRole.GENIUS_MATHEMATICIAN,
                expertise=["mathematics", "physics", "philosophy", "probability", "geometry", "theology", "invention"],
                critical_thinking_level=0.96,
                feedback_style="mathematical-philosophical"
            ),
            Senator(
                name="Marie Curie",
                role=ScientistRole.POLYMATH_MODERN,
                expertise=["physics", "chemistry", "radioactivity", "experimentation", "medicine", "research"],
                critical_thinking_level=0.98,
                feedback_style="rigorous-experimental"
            ),
            Senator(
                name="Richard Feynman",
                role=ScientistRole.GENIUS_MATHEMATICIAN,
                expertise=["physics", "quantum mechanics", "mathematics", "teaching", "explanation", "curiosity"],
                critical_thinking_level=0.97,
                feedback_style="curious-explanatory"
            ),
            Senator(
                name="Albert Einstein",
                role=ScientistRole.PHYSICS_SCIENTIST,
                expertise=["physics", "relativity", "quantum mechanics", "philosophy", "mathematics", "cosmology"],
                critical_thinking_level=0.99,
                feedback_style="theoretical-revolutionary"
            )
        ]

        return senate

    def review_reports(self, report_paths: List[Path]) -> Dict[str, Any]:
        try:
            """Review multiple reports with the Intergalactic Senate - @empire @braintrust"""
            logger.info("🌟 Intergalactic Senate convening...")
            logger.info("   @empire @braintrust review session")
            logger.info("")

            all_feedback = {
                "review_date": datetime.now().isoformat(),
                "senate_members": [s.name for s in self.senate],
                "reports_reviewed": len(report_paths),
                "reviews": []
            }

            for report_path in report_paths:
                logger.info(f"   📄 Senate reviewing: {report_path.name}...")
                feedback = self.review_report(report_path)
                all_feedback["reviews"].append(feedback)
                logger.info(f"      Senate Rating: {feedback.overall_rating:.2f}/1.0")
                logger.info("")

            # Generate Senate consensus
            consensus = self._generate_senate_consensus(all_feedback["reviews"])
            all_feedback["senate_consensus"] = consensus

            # Save reviews
            reviews_file = self.reviews_dir / f"senate_reviews_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(reviews_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "reviews": [self._feedback_to_dict(f) for f in all_feedback["reviews"]],
                    "senate_consensus": consensus,
                    "review_date": all_feedback["review_date"],
                    "empire": "@empire",
                    "braintrust": "@braintrust"
                }, f, indent=2, ensure_ascii=False)

            logger.info("="*80)
            logger.info("✅ INTERGALACTIC SENATE REVIEW COMPLETE")
            logger.info("="*80)
            logger.info(f"   Reports Reviewed: {len(report_paths)}")
            logger.info(f"   Senate Consensus: {consensus.get('summary', 'N/A')}")
            logger.info(f"   Reviews: {reviews_file}")
            logger.info("   @empire @braintrust session complete")
            logger.info("")

            return all_feedback

        except Exception as e:
            self.logger.error(f"Error in review_reports: {e}", exc_info=True)
            raise
    def review_report(self, report_path: Path) -> SenateFeedback:
        """Review a single report with AI panel"""
        if not report_path.exists():
            logger.warning(f"Report not found: {report_path}")
            return SenateFeedback(
                report_name=report_path.name,
                review_date=datetime.now().isoformat(),
                overall_rating=0.0
            )

        # Load report
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                if report_path.suffix == '.json':
                    report_content = json.load(f)
                    report_text = json.dumps(report_content, indent=2)
                else:
                    report_text = f.read()
        except Exception as e:
            logger.error(f"Error reading report: {e}")
            return SenateFeedback(
                report_name=report_path.name,
                review_date=datetime.now().isoformat(),
                overall_rating=0.0
            )

        # Get feedback from each Senator
        feedback = SenateFeedback(
            report_name=report_path.name,
            review_date=datetime.now().isoformat()
        )

        for senator in self.senate:
            senator_feedback = self._get_senator_feedback(senator, report_text, report_path.name)
            feedback.senator_feedbacks.append(senator_feedback)

        # Aggregate feedback
        feedback.critical_issues = self._aggregate_critical_issues(feedback.senator_feedbacks)
        feedback.strengths = self._aggregate_strengths(feedback.senator_feedbacks)
        feedback.recommendations = self._aggregate_recommendations(feedback.senator_feedbacks)
        feedback.strategic_guidance = self._generate_strategic_guidance(feedback.senator_feedbacks)
        feedback.overall_rating = self._calculate_overall_rating(feedback.senator_feedbacks)
        feedback.confidence_score = self._calculate_confidence(feedback.senator_feedbacks)

        # MARVIN's final review as Chancellor (if available)
        if self.marvin:
            marvin_feedback = self._get_marvin_feedback(report_text, report_path.name)
            feedback.senator_feedbacks.append(marvin_feedback)
            feedback.senate_consensus = marvin_feedback.get("assessment", "No consensus")

        return feedback

    def _get_senator_feedback(self, senator: Senator, report_text: str, report_name: str) -> Dict[str, Any]:
        """Get feedback from a specific Senator - @empire @braintrust"""
        # Simulate Senator review based on their expertise and style
        feedback = {
            "senator": senator.name,
            "role": senator.role.value,
            "expertise": senator.expertise,
            "feedback_style": senator.feedback_style,
            "era": senator.era,
            "title": senator.title,
            "assessment": "",
            "strengths": [],
            "issues": [],
            "recommendations": [],
            "strategic_guidance": [],
            "rating": 0.0
        }

        # Analyze report based on Senator's expertise
        if "systems" in senator.expertise:
            if "system" in report_text.lower() or "architecture" in report_text.lower():
                feedback["strengths"].append("Good systems thinking")
                feedback["rating"] += 0.2
            else:
                feedback["issues"].append("Could benefit from more systems perspective")

        if "validation" in senator.expertise or "experimentation" in senator.expertise:
            if "validation" in report_text.lower() or "verify" in report_text.lower():
                feedback["strengths"].append("Includes validation")
                feedback["rating"] += 0.2
            else:
                feedback["issues"].append("Missing validation approach")

        if "optimization" in scientist.expertise:
            if "optimize" in report_text.lower() or "efficiency" in report_text.lower():
                feedback["strengths"].append("Considers optimization")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could include optimization considerations")

        if "knowledge" in senator.expertise or "understanding" in senator.expertise:
            if "knowledge" in report_text.lower() or "understanding" in report_text.lower():
                feedback["strengths"].append("Addresses knowledge/understanding")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could better address knowledge application")

        if "logic" in scientist.expertise or "reasoning" in scientist.expertise:
            if "logic" in report_text.lower() or "reasoning" in report_text.lower():
                feedback["strengths"].append("Uses logical reasoning")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could strengthen logical reasoning")

        # Lifepath Domain Analysis
        if "intelligent design" in senator.expertise or "design" in senator.expertise:
            if "design" in report_text.lower() or "architecture" in report_text.lower() or "structure" in report_text.lower():
                feedback["strengths"].append("Good design thinking")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could benefit from design perspective")

        if "medicine" in scientist.expertise or "health" in scientist.expertise:
            if "health" in report_text.lower() or "medical" in report_text.lower() or "wellness" in report_text.lower():
                feedback["strengths"].append("Considers health/medical aspects")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could consider health/medical implications")

        if "psychology" in senator.expertise or "behavior" in senator.expertise:
            if "psychology" in report_text.lower() or "behavior" in report_text.lower() or "mental" in report_text.lower():
                feedback["strengths"].append("Addresses psychological aspects")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could consider psychological factors")

        if "biology" in scientist.expertise or "evolution" in scientist.expertise:
            if "biology" in report_text.lower() or "evolution" in report_text.lower() or "genetic" in report_text.lower():
                feedback["strengths"].append("Considers biological factors")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could consider biological perspectives")

        if "physics" in senator.expertise or "quantum" in senator.expertise:
            if "physics" in report_text.lower() or "quantum" in report_text.lower() or "energy" in report_text.lower():
                feedback["strengths"].append("Applies physics principles")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could apply physics principles")

        # Polymath & Genius Analysis
        if "polymath" in scientist.role.value or scientist.role in [ScientistRole.POLYMATH_RENAISSANCE, ScientistRole.POLYMATH_ANCIENT, ScientistRole.POLYMATH_MODERN]:
            # Polymaths look for interdisciplinary connections
            if len([w for w in ["art", "science", "philosophy", "mathematics", "engineering"] if w in report_text.lower()]) >= 2:
                feedback["strengths"].append("Shows interdisciplinary thinking")
                feedback["rating"] += 0.2
            else:
                feedback["issues"].append("Could benefit from interdisciplinary perspective")

        if "mathematics" in senator.expertise or "geometry" in senator.expertise:
            if "math" in report_text.lower() or "mathematical" in report_text.lower() or "quantitative" in report_text.lower():
                feedback["strengths"].append("Uses mathematical rigor")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could apply mathematical rigor")

        if "philosophy" in scientist.expertise or "ethics" in scientist.expertise:
            if "philosophy" in report_text.lower() or "ethical" in report_text.lower() or "moral" in report_text.lower():
                feedback["strengths"].append("Addresses philosophical/ethical dimensions")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could consider philosophical/ethical implications")

        if "art" in senator.expertise or "aesthetics" in senator.expertise:
            if "art" in report_text.lower() or "aesthetic" in report_text.lower() or "beauty" in report_text.lower():
                feedback["strengths"].append("Considers aesthetic dimensions")
                feedback["rating"] += 0.1
            else:
                feedback["issues"].append("Could consider aesthetic aspects")

        if "invention" in scientist.expertise or "innovation" in scientist.expertise:
            if "invent" in report_text.lower() or "innovate" in report_text.lower() or "novel" in report_text.lower():
                feedback["strengths"].append("Shows innovation")
                feedback["rating"] += 0.15
            else:
                feedback["issues"].append("Could show more innovation")

        # Base rating
        feedback["rating"] = min(1.0, feedback["rating"] + 0.5)  # Base 0.5, max 1.0

        # Generate assessment based on style
        if feedback["rating"] >= 0.8:
            feedback["assessment"] = f"Strong work. Senator {senator.name} finds this report well-structured and comprehensive."
        elif feedback["rating"] >= 0.6:
            feedback["assessment"] = f"Good work with room for improvement. Senator {senator.name} sees potential but notes some gaps."
        else:
            feedback["assessment"] = f"Needs significant improvement. Senator {senator.name} identifies several critical issues."

        # Add strategic guidance for @empire @braintrust
        if feedback["rating"] >= 0.7:
            feedback["strategic_guidance"].append(f"Senator {senator.name} recommends proceeding with strategic considerations")
        else:
            feedback["strategic_guidance"].append(f"Senator {senator.name} recommends addressing issues before strategic deployment")

        # Add recommendations
        if feedback["issues"]:
            feedback["recommendations"].append(f"Address the {len(feedback['issues'])} issues identified")

        return feedback

    def _get_marvin_feedback(self, report_text: str, report_name: str) -> Dict[str, Any]:
        """Get MARVIN's feedback as lead scientist"""
        if not self.marvin:
            return {"senator": "MARVIN", "title": "Chancellor", "assessment": "MARVIN not available"}

        try:
            verification_result = self.marvin.verify_work(
                work_content=report_text,
                work_type="report_review",
                context={"report_name": report_name}
            )

            return {
                "scientist": "MARVIN",
                "role": "lead_scientist",
                "assessment": verification_result.philosophical_insights[0] if verification_result.philosophical_insights else "Life is meaningless, but this report is... acceptable.",
                "strengths": [issue.get("description", "") for issue in verification_result.issues_found if issue.get("severity") == "low"],
                "issues": [issue.get("description", "") for issue in verification_result.issues_found if issue.get("severity") in ["high", "critical"]],
                "recommendations": verification_result.recommendations,
                "rating": verification_result.confidence_score,
                "confidence": verification_result.confidence_score
            }
        except Exception as e:
            logger.error(f"MARVIN feedback error: {e}")
            return {"scientist": "MARVIN", "assessment": f"Error: {e}"}

    def _aggregate_critical_issues(self, feedbacks: List[Dict[str, Any]]) -> List[str]:
        """Aggregate critical issues from all feedback"""
        all_issues = []
        for feedback in feedbacks:
            all_issues.extend(feedback.get("issues", []))

        # Count frequency
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        # Return most common issues
        sorted_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)
        return [issue for issue, count in sorted_issues[:5]]

    def _aggregate_strengths(self, feedbacks: List[Dict[str, Any]]) -> List[str]:
        """Aggregate strengths from all feedback"""
        all_strengths = []
        for feedback in feedbacks:
            all_strengths.extend(feedback.get("strengths", []))

        # Return unique strengths
        return list(set(all_strengths))[:10]

    def _aggregate_recommendations(self, feedbacks: List[Dict[str, Any]]) -> List[str]:
        """Aggregate recommendations from all feedback"""
        all_recommendations = []
        for feedback in feedbacks:
            all_recommendations.extend(feedback.get("recommendations", []))

        # Return unique recommendations
        return list(set(all_recommendations))[:10]

    def _calculate_overall_rating(self, feedbacks: List[Dict[str, Any]]) -> float:
        """Calculate overall rating from all feedback"""
        if not feedbacks:
            return 0.0

        ratings = [f.get("rating", 0.0) for f in feedbacks if f.get("rating")]
        if not ratings:
            return 0.0

        return sum(ratings) / len(ratings)

    def _calculate_confidence(self, feedbacks: List[Dict[str, Any]]) -> float:
        """Calculate confidence score from feedback consistency"""
        if not feedbacks:
            return 0.0

        ratings = [f.get("rating", 0.0) for f in feedbacks if f.get("rating")]
        if not ratings:
            return 0.0

        # Confidence based on rating consistency (lower variance = higher confidence)
        mean_rating = sum(ratings) / len(ratings)
        variance = sum((r - mean_rating) ** 2 for r in ratings) / len(ratings)
        confidence = 1.0 - min(1.0, variance)  # Lower variance = higher confidence

        return confidence

    def _generate_senate_consensus(self, reviews: List[SenateFeedback]) -> Dict[str, Any]:
        """Generate Senate consensus from all reviews - @empire @braintrust"""
        if not reviews:
            return {"summary": "No reviews available"}

        avg_rating = sum(r.overall_rating for r in reviews) / len(reviews)
        all_critical_issues = []
        all_strengths = []
        all_recommendations = []
        all_strategic_guidance = []

        for review in reviews:
            all_critical_issues.extend(review.critical_issues)
            all_strengths.extend(review.strengths)
            all_recommendations.extend(review.recommendations)
            all_strategic_guidance.extend(review.strategic_guidance)

        consensus = {
            "summary": f"Intergalactic Senate consensus: Average rating {avg_rating:.2f}/1.0",
            "average_rating": avg_rating,
            "top_critical_issues": list(set(all_critical_issues))[:5],
            "top_strengths": list(set(all_strengths))[:5],
            "top_recommendations": list(set(all_recommendations))[:5],
            "strategic_guidance": list(set(all_strategic_guidance))[:5],
            "senate_size": len(self.senate),
            "reviews_count": len(reviews),
            "empire": "@empire",
            "braintrust": "@braintrust"
        }

        return consensus

    def _generate_strategic_guidance(self, feedbacks: List[Dict[str, Any]]) -> List[str]:
        """Generate strategic guidance from all Senator feedbacks - @empire @braintrust"""
        all_guidance = []
        for feedback in feedbacks:
            all_guidance.extend(feedback.get("strategic_guidance", []))

        # Return unique strategic guidance
        return list(set(all_guidance))[:10]

    def _feedback_to_dict(self, feedback: SenateFeedback) -> Dict[str, Any]:
        """Convert feedback to dictionary - @empire @braintrust"""
        return {
            "report_name": feedback.report_name,
            "review_date": feedback.review_date,
            "senate_consensus": feedback.senate_consensus,
            "senator_feedbacks": feedback.senator_feedbacks,
            "critical_issues": feedback.critical_issues,
            "strengths": feedback.strengths,
            "recommendations": feedback.recommendations,
            "strategic_guidance": feedback.strategic_guidance,
            "overall_rating": feedback.overall_rating,
            "confidence_score": feedback.confidence_score,
            "empire": "@empire",
            "braintrust": "@braintrust"
        }


def main():
    try:
        """Main execution - Intergalactic Senate Review - @empire @braintrust"""
        import argparse

        parser = argparse.ArgumentParser(description="Intergalactic Senate Review - @empire @braintrust")
        parser.add_argument("--reports", nargs="+", help="Report files to review")
        parser.add_argument("--today", action="store_true", help="Review today's reports")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        senate = IntergalacticSenate(project_root)

        if args.today:
            # Review today's reports
            today_reports = [
                project_root / "docs" / "system" / "ILLUMINATION_ASSESSMENT_RESULTS.md",
                project_root / "docs" / "system" / "SYPHON_10000_YEAR_SIMULATION_RESULTS.md",
                project_root / "docs" / "system" / "THE_BEEF_DELIVERED.md",
                project_root / "docs" / "system" / "WHO_MOVED_THE_CHEESE.md",
                project_root / "docs" / "system" / "PERSPECTIVE_VALIDATION_SYSTEM.md",
                project_root / "docs" / "system" / "BLIND_TESTING_METHODOLOGY.md"
            ]
            # Filter to existing files
            existing_reports = [r for r in today_reports if r.exists()]
            results = senate.review_reports(existing_reports)
        elif args.reports:
            report_paths = [Path(r) for r in args.reports]
            results = senate.review_reports(report_paths)
        else:
            parser.print_help()
            return 1

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())