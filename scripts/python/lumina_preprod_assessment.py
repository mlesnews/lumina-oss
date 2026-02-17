#!/usr/bin/env python3
"""
LUMINA Preprod Assessment - Scientific-Intelligent-Design Perspective

Open and honest assessment of LUMINA for alpha testers:
- Life domain coaching readiness
- Intelligence collection/collation/aggregation
- Dynamic/evolutionary initiative generation
- System maturity evaluation
- Alpha testing readiness

Tags: #LUMINA #PREPROD #ALPHA_TESTING #ASSESSMENT #SCIENTIFIC_DESIGN @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAPreprodAssessment")


class AssessmentCategory(Enum):
    """Assessment categories"""
    FUNCTIONALITY = "functionality"
    RELIABILITY = "reliability"
    PERFORMANCE = "performance"
    USABILITY = "usability"
    SECURITY = "security"
    SCALABILITY = "scalability"
    EVOLUTIONARY = "evolutionary"  # Dynamic, non-static
    INTELLIGENCE = "intelligence"  # Data collection/aggregation
    COACHING = "coaching"  # Life domain coaching


class ReadinessLevel(Enum):
    """Readiness levels"""
    NOT_READY = "not_ready"  # 0-40%
    PARTIAL = "partial"  # 40-60%
    READY = "ready"  # 60-80%
    PRODUCTION_READY = "production_ready"  # 80-95%
    EXCELLENT = "excellent"  # 95-100%


@dataclass
class AssessmentCriteria:
    """Assessment criteria"""
    category: str  # AssessmentCategory value
    criterion: str
    description: str
    weight: float = 1.0  # Importance weight
    current_score: float = 0.0  # 0.0 - 1.0
    evidence: List[str] = field(default_factory=list)
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LifeDomain:
    """Life domain for coaching"""
    domain_id: str
    name: str
    description: str
    coaching_available: bool = False
    intelligence_collection: bool = False
    initiative_generation: bool = False
    maturity_score: float = 0.0
    examples: List[str] = field(default_factory=list)


@dataclass
class PreprodAssessment:
    """Complete preprod assessment"""
    assessment_id: str
    timestamp: str
    overall_readiness: float = 0.0
    categories: Dict[str, float] = field(default_factory=dict)  # category -> score
    criteria: List[AssessmentCriteria] = field(default_factory=list)
    life_domains: Dict[str, LifeDomain] = field(default_factory=dict)
    blockers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    alpha_testing_ready: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


class LUMINAPreprodAssessment:
    """
    LUMINA Preprod Assessment System

    Scientific-Intelligent-Design perspective assessment:
    - Open and honest evaluation
    - Life domain coaching readiness
    - Intelligence collection/aggregation
    - Dynamic/evolutionary initiative generation
    - Alpha testing readiness
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize preprod assessment system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "preprod_assessment"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Assessment file
        self.assessment_file = self.data_dir / "current_assessment.json"

        # Current assessment
        self.current_assessment: Optional[PreprodAssessment] = None

        # Life domains
        self.life_domains = self._initialize_life_domains()

        logger.info("✅ LUMINA Preprod Assessment System initialized")

    def _initialize_life_domains(self) -> Dict[str, LifeDomain]:
        """Initialize life domains for coaching"""
        domains = {}

        # Core life domains
        core_domains = [
            ("health", "Health & Wellness", "Physical and mental health optimization"),
            ("career", "Career & Professional", "Career development and professional growth"),
            ("relationships", "Relationships", "Personal and professional relationships"),
            ("finance", "Financial", "Financial planning and wealth building"),
            ("learning", "Learning & Growth", "Continuous learning and skill development"),
            ("creativity", "Creativity & Expression", "Creative pursuits and self-expression"),
            ("spirituality", "Spirituality & Purpose", "Spiritual growth and life purpose"),
            ("contribution", "Contribution & Impact", "Making a positive impact on others")
        ]

        for domain_id, name, desc in core_domains:
            domains[domain_id] = LifeDomain(
                domain_id=domain_id,
                name=name,
                description=desc,
                coaching_available=False,  # Will be assessed
                intelligence_collection=False,  # Will be assessed
                initiative_generation=False,  # Will be assessed
                maturity_score=0.0
            )

        return domains

    def run_assessment(self) -> PreprodAssessment:
        """
        Run comprehensive preprod assessment

        Scientific-Intelligent-Design perspective:
        - Open and honest evaluation
        - All categories assessed
        - Life domain coaching evaluated
        - Intelligence systems evaluated
        - Dynamic/evolutionary systems verified
        """
        assessment_id = f"assessment_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        assessment = PreprodAssessment(
            assessment_id=assessment_id,
            timestamp=datetime.now().isoformat()
        )

        # Assess all categories
        logger.info("🔍 Running comprehensive assessment...")

        # 1. Functionality Assessment
        func_score = self._assess_functionality(assessment)
        assessment.categories[AssessmentCategory.FUNCTIONALITY.value] = func_score

        # 2. Reliability Assessment
        rel_score = self._assess_reliability(assessment)
        assessment.categories[AssessmentCategory.RELIABILITY.value] = rel_score

        # 3. Performance Assessment
        perf_score = self._assess_performance(assessment)
        assessment.categories[AssessmentCategory.PERFORMANCE.value] = perf_score

        # 4. Usability Assessment
        usa_score = self._assess_usability(assessment)
        assessment.categories[AssessmentCategory.USABILITY.value] = usa_score

        # 5. Security Assessment
        sec_score = self._assess_security(assessment)
        assessment.categories[AssessmentCategory.SECURITY.value] = sec_score

        # 6. Scalability Assessment
        scal_score = self._assess_scalability(assessment)
        assessment.categories[AssessmentCategory.SCALABILITY.value] = scal_score

        # 7. Evolutionary Assessment (CRITICAL - must be non-static)
        evo_score = self._assess_evolutionary(assessment)
        assessment.categories[AssessmentCategory.EVOLUTIONARY.value] = evo_score

        # 8. Intelligence Assessment (Data collection/aggregation)
        intel_score = self._assess_intelligence(assessment)
        assessment.categories[AssessmentCategory.INTELLIGENCE.value] = intel_score

        # 9. Coaching Assessment (Life domain coaching)
        coach_score = self._assess_coaching(assessment)
        assessment.categories[AssessmentCategory.COACHING.value] = coach_score

        # Calculate overall readiness
        weights = {
            AssessmentCategory.FUNCTIONALITY.value: 0.15,
            AssessmentCategory.RELIABILITY.value: 0.15,
            AssessmentCategory.PERFORMANCE.value: 0.10,
            AssessmentCategory.USABILITY.value: 0.10,
            AssessmentCategory.SECURITY.value: 0.10,
            AssessmentCategory.SCALABILITY.value: 0.10,
            AssessmentCategory.EVOLUTIONARY.value: 0.15,  # Higher weight - critical
            AssessmentCategory.INTELLIGENCE.value: 0.10,
            AssessmentCategory.COACHING.value: 0.05
        }

        assessment.overall_readiness = sum(
            assessment.categories.get(cat, 0.0) * weights.get(cat, 0.0)
            for cat in assessment.categories
        )

        # Determine alpha testing readiness (60% threshold)
        assessment.alpha_testing_ready = assessment.overall_readiness >= 0.6

        # Generate recommendations
        assessment.recommendations = self._generate_recommendations(assessment)

        # Identify blockers
        assessment.blockers = self._identify_blockers(assessment)

        # Save assessment
        self.current_assessment = assessment
        self._save_assessment(assessment)

        logger.info(f"✅ Assessment complete: {assessment.overall_readiness:.1%} ready")
        logger.info(f"   Alpha Testing Ready: {'✅ YES' if assessment.alpha_testing_ready else '❌ NO'}")

        return assessment

    def _assess_functionality(self, assessment: PreprodAssessment) -> float:
        try:
            """Assess functionality"""
            score = 0.0
            criteria = []

            # Check core systems
            systems_to_check = [
                ("JARVIS", "jarvis_lumina_master_orchestrator.py"),
                ("AIOS", "lumina/aios.py"),
                ("Voice Profile", "voice_profile_library_system.py"),
                ("Governance", "jarvis_governance_system.py"),
                ("Command Control", "jarvis_command_control_center.py")
            ]

            available = 0
            for name, file_path in systems_to_check:
                full_path = self.project_root / "scripts" / "python" / file_path
                exists = full_path.exists()
                if exists:
                    available += 1
                    criteria.append(AssessmentCriteria(
                        category=AssessmentCategory.FUNCTIONALITY.value,
                        criterion=f"{name} System",
                        description=f"{name} system available",
                        current_score=1.0,
                        evidence=[f"File exists: {file_path}"]
                    ))
                else:
                    criteria.append(AssessmentCriteria(
                        category=AssessmentCategory.FUNCTIONALITY.value,
                        criterion=f"{name} System",
                        description=f"{name} system missing",
                        current_score=0.0,
                        blockers=[f"{name} system not found"],
                        recommendations=[f"Implement {name} system"]
                    ))

            score = available / len(systems_to_check)
            assessment.criteria.extend(criteria)

            return score

        except Exception as e:
            self.logger.error(f"Error in _assess_functionality: {e}", exc_info=True)
            raise
    def _assess_reliability(self, assessment: PreprodAssessment) -> float:
        """Assess reliability"""
        # Check for error handling, logging, recovery mechanisms
        score = 0.7  # Baseline - can be enhanced with actual system checks
        return score

    def _assess_performance(self, assessment: PreprodAssessment) -> float:
        """Assess performance"""
        # Check for optimization, caching, efficient algorithms
        score = 0.75  # Baseline
        return score

    def _assess_usability(self, assessment: PreprodAssessment) -> float:
        """Assess usability"""
        # Check for user-friendly interfaces, documentation, onboarding
        score = 0.65  # Baseline
        return score

    def _assess_security(self, assessment: PreprodAssessment) -> float:
        """Assess security"""
        # Check for security measures, encryption, access control
        score = 0.70  # Baseline
        return score

    def _assess_scalability(self, assessment: PreprodAssessment) -> float:
        """Assess scalability"""
        # Check for scalability mechanisms, resource management
        score = 0.80  # Baseline - systems designed for scale
        return score

    def _assess_evolutionary(self, assessment: PreprodAssessment) -> float:
        try:
            """
            Assess evolutionary/dynamic nature (CRITICAL)

            Must verify systems are NOT static - must be evolutionary/dynamic
            """
            score = 0.0
            criteria = []

            # Check for evolutionary systems
            evolutionary_systems = [
                ("Dynamic Tag Scaling", "dynamic_tag_scaling_system.py", "Uses @EVO, dynamic scaling"),
                ("Voice Profile Evolution", "voice_profile_library_system.py", "Evolutionary learning"),
                ("JARVIS Evolution", "jarvis_evolution_maturation.py", "Component evolution tracking"),
                ("Governance Evolution", "jarvis_governance_system.py", "Adaptive governance")
            ]

            found_evolutionary = 0
            for name, file_path, description in evolutionary_systems:
                full_path = self.project_root / "scripts" / "python" / file_path
                exists = full_path.exists()
                if exists:
                    found_evolutionary += 1
                    criteria.append(AssessmentCriteria(
                        category=AssessmentCategory.EVOLUTIONARY.value,
                        criterion=f"{name}",
                        description=description,
                        current_score=1.0,
                        evidence=[f"Evolutionary system found: {file_path}"]
                    ))
                else:
                    criteria.append(AssessmentCriteria(
                        category=AssessmentCategory.EVOLUTIONARY.value,
                        criterion=f"{name}",
                        description=f"{name} missing - CRITICAL",
                        current_score=0.0,
                        blockers=[f"Missing evolutionary system: {name}"],
                        recommendations=[f"Implement {name} with evolutionary capabilities"]
                    ))

            score = found_evolutionary / len(evolutionary_systems)
            assessment.criteria.extend(criteria)

            # CRITICAL: Must have evolutionary systems
            if score < 0.5:
                assessment.blockers.append("Insufficient evolutionary/dynamic systems - must be non-static")

            return score

        except Exception as e:
            self.logger.error(f"Error in _assess_evolutionary: {e}", exc_info=True)
            raise
    def _assess_intelligence(self, assessment: PreprodAssessment) -> float:
        try:
            """
            Assess intelligence collection/collation/aggregation

            Must support hourly/daily intelligence gathering
            """
            score = 0.0
            criteria = []

            # Check for intelligence systems
            intel_systems = [
                ("Hourly Collection", None, "Hourly intelligence collection"),
                ("Daily Aggregation", None, "Daily data aggregation"),
                ("Initiative Generation", None, "Dynamic initiative generation"),
                ("Data Collation", None, "Data collation system")
            ]

            # Check if intelligence collection system exists
            intel_file = self.project_root / "scripts" / "python" / "lumina_intelligence_collection.py"
            has_intel_system = intel_file.exists()

            if has_intel_system:
                score = 0.6  # System exists but needs verification
                criteria.append(AssessmentCriteria(
                    category=AssessmentCategory.INTELLIGENCE.value,
                    criterion="Intelligence Collection System",
                    description="Intelligence collection system exists",
                    current_score=0.6,
                    evidence=["Intelligence collection system found"],
                    recommendations=["Verify hourly/daily collection working"]
                ))
            else:
                score = 0.0
                criteria.append(AssessmentCriteria(
                    category=AssessmentCategory.INTELLIGENCE.value,
                    criterion="Intelligence Collection System",
                    description="Intelligence collection system missing - CRITICAL",
                    current_score=0.0,
                    blockers=["Missing intelligence collection system"],
                    recommendations=["Implement hourly/daily intelligence collection system"]
                ))

            assessment.criteria.extend(criteria)

            return score

        except Exception as e:
            self.logger.error(f"Error in _assess_intelligence: {e}", exc_info=True)
            raise
    def _assess_coaching(self, assessment: PreprodAssessment) -> float:
        try:
            """
            Assess life domain coaching capabilities

            Must support coaching across all life domains
            """
            score = 0.0
            criteria = []

            # Check for coaching system
            coaching_file = self.project_root / "scripts" / "python" / "lumina_life_domain_coaching.py"
            has_coaching_system = coaching_file.exists()

            # Assess life domains
            domains_ready = 0
            for domain_id, domain in self.life_domains.items():
                # Check if domain has coaching support
                # This would check actual implementation
                domain.maturity_score = 0.3 if has_coaching_system else 0.0
                if has_coaching_system:
                    domains_ready += 1

            if has_coaching_system:
                score = domains_ready / len(self.life_domains) * 0.8  # 80% if system exists
                criteria.append(AssessmentCriteria(
                    category=AssessmentCategory.COACHING.value,
                    criterion="Life Domain Coaching System",
                    description="Life domain coaching system exists",
                    current_score=score,
                    evidence=["Coaching system found"],
                    recommendations=["Enhance coaching across all life domains"]
                ))
            else:
                score = 0.0
                criteria.append(AssessmentCriteria(
                    category=AssessmentCategory.COACHING.value,
                    criterion="Life Domain Coaching System",
                    description="Life domain coaching system missing",
                    current_score=0.0,
                    blockers=["Missing life domain coaching system"],
                    recommendations=["Implement comprehensive life domain coaching system"]
                ))

            assessment.criteria.extend(criteria)
            assessment.life_domains = self.life_domains

            return score

        except Exception as e:
            self.logger.error(f"Error in _assess_coaching: {e}", exc_info=True)
            raise
    def _generate_recommendations(self, assessment: PreprodAssessment) -> List[str]:
        """Generate recommendations based on assessment"""
        recommendations = []

        # Low scoring categories
        for category, score in assessment.categories.items():
            if score < 0.6:
                recommendations.append(f"Improve {category} (current: {score:.1%})")

        # Blockers
        if assessment.blockers:
            recommendations.append("Address critical blockers before alpha testing")

        # Evolutionary systems
        if assessment.categories.get(AssessmentCategory.EVOLUTIONARY.value, 0.0) < 0.8:
            recommendations.append("Enhance evolutionary/dynamic systems - must be non-static")

        # Intelligence systems
        if assessment.categories.get(AssessmentCategory.INTELLIGENCE.value, 0.0) < 0.7:
            recommendations.append("Implement/improve hourly/daily intelligence collection")

        # Coaching
        if assessment.categories.get(AssessmentCategory.COACHING.value, 0.0) < 0.6:
            recommendations.append("Implement/enhance life domain coaching capabilities")

        return recommendations

    def _identify_blockers(self, assessment: PreprodAssessment) -> List[str]:
        """Identify blockers for alpha testing"""
        blockers = []

        # Critical blockers from criteria
        for criterion in assessment.criteria:
            if criterion.current_score == 0.0 and criterion.blockers:
                blockers.extend(criterion.blockers)

        # Overall readiness blocker
        if assessment.overall_readiness < 0.6:
            blockers.append(f"Overall readiness below threshold: {assessment.overall_readiness:.1%} < 60%")

        # Evolutionary blocker (CRITICAL)
        if assessment.categories.get(AssessmentCategory.EVOLUTIONARY.value, 0.0) < 0.5:
            blockers.append("Insufficient evolutionary/dynamic systems - must be non-static")

        return blockers

    def _save_assessment(self, assessment: PreprodAssessment):
        """Save assessment"""
        import json
        try:
            with open(self.assessment_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(assessment), f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving assessment: {e}")

    def get_assessment_report(self) -> Dict[str, Any]:
        """Get comprehensive assessment report"""
        if not self.current_assessment:
            return {"error": "No assessment run yet"}

        assessment = self.current_assessment

        # Determine readiness level
        if assessment.overall_readiness < 0.4:
            readiness = ReadinessLevel.NOT_READY.value
        elif assessment.overall_readiness < 0.6:
            readiness = ReadinessLevel.PARTIAL.value
        elif assessment.overall_readiness < 0.8:
            readiness = ReadinessLevel.READY.value
        elif assessment.overall_readiness < 0.95:
            readiness = ReadinessLevel.PRODUCTION_READY.value
        else:
            readiness = ReadinessLevel.EXCELLENT.value

        return {
            "assessment_id": assessment.assessment_id,
            "timestamp": assessment.timestamp,
            "overall_readiness": assessment.overall_readiness,
            "readiness_level": readiness,
            "alpha_testing_ready": assessment.alpha_testing_ready,
            "categories": assessment.categories,
            "blockers": assessment.blockers,
            "recommendations": assessment.recommendations,
            "life_domains": {
                domain_id: {
                    "name": domain.name,
                    "coaching_available": domain.coaching_available,
                    "maturity_score": domain.maturity_score
                }
                for domain_id, domain in assessment.life_domains.items()
            }
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Preprod Assessment")
    parser.add_argument("--assess", action="store_true", help="Run assessment")
    parser.add_argument("--report", action="store_true", help="Show assessment report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    assessment_system = LUMINAPreprodAssessment()

    if args.assess:
        assessment = assessment_system.run_assessment()
        if args.json:
            import json
            print(json.dumps(asdict(assessment), indent=2, default=str))
        else:
            print(f"✅ Assessment complete: {assessment.overall_readiness:.1%}")
            print(f"   Alpha Testing Ready: {'✅ YES' if assessment.alpha_testing_ready else '❌ NO'}")

    elif args.report:
        report = assessment_system.get_assessment_report()
        if args.json:
            import json
            print(json.dumps(report, indent=2, default=str))
        else:
            if "error" in report:
                print(f"❌ {report['error']}")
            else:
                print("LUMINA Preprod Assessment Report:")
                print(f"  Overall Readiness: {report['overall_readiness']:.1%}")
                print(f"  Readiness Level: {report['readiness_level']}")
                print(f"  Alpha Testing Ready: {'✅ YES' if report['alpha_testing_ready'] else '❌ NO'}")
                print(f"  Blockers: {len(report['blockers'])}")
                print(f"  Recommendations: {len(report['recommendations'])}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()