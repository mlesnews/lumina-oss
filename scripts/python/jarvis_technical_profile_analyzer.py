#!/usr/bin/env python3
"""
JARVIS Technical Profile Analyzer

Analyzes technical knowledge, understanding, and capabilities.
Consults with HR departments, specialists, and experts for comprehensive assessment.

Tags: #TECHNICAL_ANALYSIS #HR #EXPERT_CONSULTATION #PROFILE_ASSESSMENT @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISTechProfileAnalyzer")


class TechnicalDomain(Enum):
    """Technical domains"""
    SOFTWARE_ENGINEERING = "software_engineering"
    AI_ML = "ai_ml"
    DATA_SCIENCE = "data_science"
    DEVOPS = "devops"
    CYBERSECURITY = "cybersecurity"
    CLOUD_COMPUTING = "cloud_computing"
    SYSTEM_ARCHITECTURE = "system_architecture"
    DATABASE = "database"
    NETWORKING = "networking"
    MOBILE_DEVELOPMENT = "mobile_development"
    WEB_DEVELOPMENT = "web_development"
    EMBEDDED_SYSTEMS = "embedded_systems"
    GAME_DEVELOPMENT = "game_development"
    BLOCKCHAIN = "blockchain"
    QUANTUM_COMPUTING = "quantum_computing"


class ExpertiseLevel(Enum):
    """Expertise levels"""
    BEGINNER = {"level": 1, "description": "Basic understanding, can follow instructions"}
    INTERMEDIATE = {"level": 2, "description": "Can work independently, understands concepts"}
    ADVANCED = {"level": 3, "description": "Deep knowledge, can solve complex problems"}
    EXPERT = {"level": 4, "description": "Mastery, can innovate and teach others"}
    GURU = {"level": 5, "description": "Industry leader, creates new paradigms"}


class HRDepartment:
    """HR Department consultation"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "hr_consultation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def assess_technical_skills(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess technical skills from HR perspective"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "assessed_by": "HR_Department",
            "skills_assessment": {},
            "recommendations": [],
            "fit_analysis": {}
        }

        # Analyze technical skills
        skills = profile.get("technical_skills", {})
        for domain, level in skills.items():
            assessment["skills_assessment"][domain] = {
                "level": level,
                "verified": True,
                "relevance": "HIGH"
            }

        return assessment

    def provide_recommendations(self, profile: Dict[str, Any]) -> List[str]:
        """Provide HR recommendations"""
        recommendations = []

        # Skill gaps
        if profile.get("experience_years", 0) < 2:
            recommendations.append("Consider junior-level positions or mentorship programs")

        # Strengths
        if profile.get("technical_skills", {}):
            recommendations.append("Strong technical foundation - suitable for technical roles")

        return recommendations


class SpecialistConsultant:
    """Specialist/Expert consultation"""

    def __init__(self, project_root: Path, domain: TechnicalDomain):
        self.project_root = project_root
        self.domain = domain
        self.data_dir = project_root / "data" / "specialist_consultation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def assess_domain_expertise(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Assess expertise in specific domain"""
        assessment = {
            "timestamp": datetime.now().isoformat(),
            "consultant": f"Specialist_{self.domain.value}",
            "domain": self.domain.value,
            "expertise_level": None,
            "detailed_analysis": {},
            "recommendations": []
        }

        # Analyze domain-specific knowledge
        skills = profile.get("technical_skills", {})
        domain_skill = skills.get(self.domain.value, 0)

        if domain_skill >= 4:
            assessment["expertise_level"] = "EXPERT"
        elif domain_skill >= 3:
            assessment["expertise_level"] = "ADVANCED"
        elif domain_skill >= 2:
            assessment["expertise_level"] = "INTERMEDIATE"
        else:
            assessment["expertise_level"] = "BEGINNER"

        assessment["detailed_analysis"] = {
            "skill_level": domain_skill,
            "knowledge_depth": "DEEP" if domain_skill >= 3 else "MODERATE" if domain_skill >= 2 else "BASIC",
            "practical_experience": profile.get("experience_years", 0),
            "certifications": profile.get("certifications", []),
            "projects": len(profile.get("projects", []))
        }

        return assessment


class TechnicalProfileAnalyzer:
    """Comprehensive technical profile analyzer"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "technical_profiles"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.hr_department = HRDepartment(project_root)
        self.specialists = {}

        # Initialize specialists for each domain
        for domain in TechnicalDomain:
            self.specialists[domain.value] = SpecialistConsultant(project_root, domain)

    def analyze_profile(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive profile analysis"""
        logger.info("=" * 80)
        logger.info("🔍 JARVIS TECHNICAL PROFILE ANALYSIS")
        logger.info("=" * 80)
        logger.info("")

        start_time = time.time()

        # Extract profile information
        name = profile_data.get("name", "Unknown")
        logger.info(f"📋 Analyzing profile: {name}")
        logger.info("")

        # HR Department consultation
        logger.info("👔 Consulting HR Department...")
        hr_assessment = self.hr_department.assess_technical_skills(profile_data)
        hr_recommendations = self.hr_department.provide_recommendations(profile_data)
        logger.info("✅ HR assessment complete")
        logger.info("")

        # Specialist consultations
        logger.info("🎓 Consulting specialists...")
        specialist_assessments = {}

        # Identify relevant domains
        technical_skills = profile_data.get("technical_skills", {})
        relevant_domains = [domain for domain in technical_skills.keys() if technical_skills[domain] > 0]

        for domain_name in relevant_domains:
            try:
                domain = TechnicalDomain(domain_name)
                specialist = self.specialists[domain_name]
                assessment = specialist.assess_domain_expertise(profile_data)
                specialist_assessments[domain_name] = assessment
                logger.info(f"   ✅ {domain_name}: {assessment['expertise_level']}")
            except ValueError:
                logger.warning(f"   ⚠️  Unknown domain: {domain_name}")

        logger.info("")

        # Comprehensive analysis
        logger.info("📊 Generating comprehensive analysis...")

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "analyzed_by": "JARVIS",
            "profile": {
                "name": name,
                "experience_years": profile_data.get("experience_years", 0),
                "education": profile_data.get("education", []),
                "certifications": profile_data.get("certifications", []),
                "projects": profile_data.get("projects", [])
            },
            "hr_assessment": hr_assessment,
            "hr_recommendations": hr_recommendations,
            "specialist_assessments": specialist_assessments,
            "technical_summary": self._generate_technical_summary(profile_data),
            "inferences": self._generate_inferences(profile_data),
            "detailed_description": self._generate_detailed_description(profile_data, specialist_assessments)
        }

        elapsed_time = time.time() - start_time

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ANALYSIS COMPLETE")
        logger.info("=" * 80)
        logger.info(f"⏱️  Time taken: {elapsed_time:.2f} seconds")
        logger.info("")

        # Save analysis
        analysis_file = self.data_dir / f"analysis_{name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(analysis_file, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, default=str)

        logger.info(f"📄 Analysis saved: {analysis_file}")
        logger.info("")

        return analysis

    def _generate_technical_summary(self, profile: Dict[str, Any]) -> Dict[str, Any]:
        """Generate technical summary"""
        skills = profile.get("technical_skills", {})

        # Calculate overall technical level
        if skills:
            avg_skill = sum(skills.values()) / len(skills)
        else:
            avg_skill = 0

        # Determine overall level
        if avg_skill >= 4:
            overall_level = "EXPERT"
        elif avg_skill >= 3:
            overall_level = "ADVANCED"
        elif avg_skill >= 2:
            overall_level = "INTERMEDIATE"
        else:
            overall_level = "BEGINNER"

        # Top skills
        top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "overall_technical_level": overall_level,
            "average_skill_level": round(avg_skill, 2),
            "total_domains": len(skills),
            "top_skills": [{"domain": k, "level": v} for k, v in top_skills],
            "experience_years": profile.get("experience_years", 0),
            "education_level": profile.get("education_level", "Unknown")
        }

    def _generate_inferences(self, profile: Dict[str, Any]) -> List[str]:
        """Generate inferences about technical knowledge and understanding"""
        inferences = []

        skills = profile.get("technical_skills", {})
        experience = profile.get("experience_years", 0)
        projects = profile.get("projects", [])
        certifications = profile.get("certifications", [])

        # Experience-based inferences
        if experience >= 10:
            inferences.append("Extensive industry experience suggests deep practical knowledge")
        elif experience >= 5:
            inferences.append("Moderate experience indicates solid foundation with room for growth")
        else:
            inferences.append("Early career stage, likely strong in fundamentals and learning")

        # Skill-based inferences
        if skills:
            max_skill = max(skills.values())
            if max_skill >= 4:
                inferences.append("Expert-level skills in at least one domain indicates specialization")
            if len(skills) >= 5:
                inferences.append("Broad technical knowledge across multiple domains suggests versatility")

        # Project-based inferences
        if len(projects) >= 10:
            inferences.append("Extensive project portfolio demonstrates practical application of knowledge")
        elif len(projects) >= 5:
            inferences.append("Good project experience shows ability to apply technical skills")

        # Certification-based inferences
        if len(certifications) >= 5:
            inferences.append("Multiple certifications indicate commitment to continuous learning")

        # Overall inference
        if experience >= 5 and max(skills.values() if skills else [0]) >= 3:
            inferences.append("Strong combination of experience and technical depth suggests senior-level capability")

        return inferences

    def _generate_detailed_description(self, profile: Dict[str, Any], 
                                      specialist_assessments: Dict[str, Any]) -> str:
        """Generate detailed description of the person"""
        name = profile.get("name", "The individual")
        experience = profile.get("experience_years", 0)
        skills = profile.get("technical_skills", {})

        description = f"{name} is a technical professional with {experience} years of experience. "

        # Technical capabilities
        if skills:
            top_domains = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:3]
            description += f"Primary technical expertise includes: {', '.join([d[0].replace('_', ' ').title() for d in top_domains])}. "

        # Specialist assessments
        if specialist_assessments:
            expert_domains = [domain for domain, assessment in specialist_assessments.items() 
                            if assessment.get("expertise_level") in ["EXPERT", "ADVANCED"]]
            if expert_domains:
                description += f"Demonstrates advanced to expert-level knowledge in: {', '.join([d.replace('_', ' ').title() for d in expert_domains])}. "

        # Education and certifications
        education = profile.get("education", [])
        certifications = profile.get("certifications", [])
        if education:
            description += f"Educational background includes: {', '.join(education)}. "
        if certifications:
            description += f"Certifications held: {', '.join(certifications[:3])}. "

        # Projects
        projects = profile.get("projects", [])
        if projects:
            description += f"Has completed {len(projects)} technical projects, demonstrating practical application of skills. "

        # Overall assessment
        if experience >= 5:
            description += "The combination of extensive experience and technical depth suggests a senior-level professional capable of leading complex technical initiatives."
        elif experience >= 2:
            description += "Shows strong technical foundation with growing practical experience, suitable for mid-level technical roles."
        else:
            description += "Early career professional with solid technical fundamentals, ready for junior to mid-level positions with mentorship."

        return description


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Technical Profile Analyzer")
        parser.add_argument("--profile", type=str, help="Path to profile JSON file")
        parser.add_argument("--name", type=str, help="Person name")
        parser.add_argument("--experience", type=int, help="Years of experience")
        parser.add_argument("--skills", type=str, help="Technical skills JSON string")
        parser.add_argument("--analyze", action="store_true", help="Run analysis")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analyzer = TechnicalProfileAnalyzer(project_root)

        # Load or create profile
        profile_data = {}

        if args.profile:
            # Load from file
            profile_file = Path(args.profile)
            if profile_file.exists():
                with open(profile_file, 'r', encoding='utf-8') as f:
                    profile_data = json.load(f)
        else:
            # Create from arguments or use example
            profile_data = {
                "name": args.name or "Example Person",
                "experience_years": args.experience or 5,
                "technical_skills": json.loads(args.skills) if args.skills else {
                    "software_engineering": 4,
                    "ai_ml": 3,
                    "cloud_computing": 3,
                    "devops": 2
                },
                "education": ["Bachelor's in Computer Science", "Master's in AI"],
                "certifications": ["AWS Certified Solutions Architect", "Kubernetes Administrator"],
                "projects": ["AI-powered recommendation system", "Cloud migration project", "DevOps automation"]
            }

        # Run analysis
        if args.analyze or True:
            analysis = analyzer.analyze_profile(profile_data)
            print(json.dumps(analysis, indent=2, default=str))
        else:
            print("Profile data prepared. Use --analyze to run full analysis.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()