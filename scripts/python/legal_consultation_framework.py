#!/usr/bin/env python3
"""
Legal Consultation Framework

Virtual Legal Team for LUMINA Open-Source Project
- Fair use analysis
- Voice cloning/actor voice rights
- Copyright compliance
- Right of publicity
- Fan-created content guidelines
- Real law firm engagement when needed

Tags: #LEGAL #FAIR_USE #VOICE_CLONING #COPYRIGHT #RIGHT_OF_PUBLICITY @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LegalConsultation")


class LegalRiskLevel(Enum):
    """Legal risk assessment levels"""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"
    REQUIRES_REAL_LAWYER = "requires_real_lawyer"


class UseCaseType(Enum):
    """Types of use cases for legal analysis"""
    VOICE_CLONING_ACTOR = "voice_cloning_actor"
    FAN_CONTENT_NON_MONETIZED = "fan_content_non_monetized"
    OPEN_SOURCE_PROJECT = "open_source_project"
    EDUCATIONAL = "educational"
    PARODY_SATIRE = "parody_satire"
    TRANSFORMATIVE = "transformative"
    COMMERCIAL = "commercial"


class LegalConsultationFramework:
    """
    Virtual Legal Team for LUMINA

    Provides legal guidance on:
    - Fair use analysis
    - Voice cloning/actor voice rights
    - Copyright compliance
    - Right of publicity
    - Fan-created content
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize legal consultation framework"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "legal"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Legal consultation history
        self.consultation_history_file = self.data_dir / "consultation_history.jsonl"

        # Real law firm contacts (when needed)
        self.law_firm_contacts_file = self.data_dir / "law_firm_contacts.json"
        self._load_law_firm_contacts()

        logger.info("✅ Legal Consultation Framework initialized")
        logger.info("   Virtual legal team ready")
        logger.info("   Real law firm engagement available when needed")

    def _load_law_firm_contacts(self):
        """Load real law firm contacts"""
        if self.law_firm_contacts_file.exists():
            try:
                with open(self.law_firm_contacts_file, 'r') as f:
                    self.law_firm_contacts = json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load law firm contacts: {e}")
                self.law_firm_contacts = {}
        else:
            # Default structure
            self.law_firm_contacts = {
                "intellectual_property": [],
                "entertainment_law": [],
                "technology_law": [],
                "copyright_specialists": []
            }
            self._save_law_firm_contacts()

    def _save_law_firm_contacts(self):
        """Save law firm contacts"""
        try:
            with open(self.law_firm_contacts_file, 'w') as f:
                json.dump(self.law_firm_contacts, f, indent=2)
        except Exception as e:
            logger.error(f"❌ Could not save law firm contacts: {e}")

    def analyze_voice_cloning_use(self, 
                                  actor_name: str,
                                  character_name: Optional[str] = None,
                                  use_case: UseCaseType = UseCaseType.FAN_CONTENT_NON_MONETIZED,
                                  is_open_source: bool = True,
                                  is_non_monetized: bool = True,
                                  is_transformative: bool = True,
                                  is_educational: bool = False,
                                  is_parody: bool = False) -> Dict[str, Any]:
        """
        Analyze legal implications of voice cloning for actor voices

        Args:
            actor_name: Name of actor
            character_name: Character name (if applicable)
            use_case: Type of use case
            is_open_source: Is this open-source?
            is_non_monetized: Is this non-monetized?
            is_transformative: Is this transformative use?
            is_educational: Is this educational?
            is_parody: Is this parody/satire?

        Returns:
            Legal analysis with risk assessment and recommendations
        """
        logger.info(f"⚖️  Analyzing voice cloning use: {actor_name} ({character_name or 'N/A'})")

        # Risk factors
        risk_factors = []
        protective_factors = []

        # Right of Publicity Analysis
        right_of_publicity_risk = self._analyze_right_of_publicity(
            actor_name, character_name, use_case
        )

        # Fair Use Analysis
        fair_use_analysis = self._analyze_fair_use(
            use_case, is_open_source, is_non_monetized,
            is_transformative, is_educational, is_parody
        )

        # Copyright Analysis
        copyright_analysis = self._analyze_copyright(
            actor_name, character_name, use_case
        )

        # Overall Risk Assessment
        overall_risk = self._assess_overall_risk(
            right_of_publicity_risk,
            fair_use_analysis,
            copyright_analysis
        )

        # Recommendations
        recommendations = self._generate_recommendations(
            overall_risk, right_of_publicity_risk,
            fair_use_analysis, copyright_analysis
        )

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "actor_name": actor_name,
            "character_name": character_name,
            "use_case": use_case.value,
            "risk_assessment": {
                "overall_risk": overall_risk.value,
                "right_of_publicity": right_of_publicity_risk,
                "fair_use": fair_use_analysis,
                "copyright": copyright_analysis
            },
            "protective_factors": protective_factors,
            "risk_factors": risk_factors,
            "recommendations": recommendations,
            "requires_real_lawyer": overall_risk == LegalRiskLevel.REQUIRES_REAL_LAWYER
        }

        # Log consultation
        self._log_consultation(analysis)

        return analysis

    def _analyze_right_of_publicity(self, 
                                    actor_name: str,
                                    character_name: Optional[str],
                                    use_case: UseCaseType) -> Dict[str, Any]:
        """
        Analyze Right of Publicity implications

        Right of Publicity protects:
        - Person's name, likeness, voice
        - Commercial use requires permission
        - Non-commercial use may be protected
        """
        risk_level = LegalRiskLevel.MODERATE
        factors = []

        # Non-commercial use is generally safer
        if use_case in [UseCaseType.FAN_CONTENT_NON_MONETIZED, UseCaseType.OPEN_SOURCE_PROJECT]:
            risk_level = LegalRiskLevel.LOW
            factors.append("Non-commercial use reduces right of publicity risk")
        else:
            risk_level = LegalRiskLevel.HIGH
            factors.append("Commercial use increases right of publicity risk")

        # Transformative use helps
        if use_case == UseCaseType.TRANSFORMATIVE:
            risk_level = LegalRiskLevel.LOW
            factors.append("Transformative use may be protected")

        # Parody/satire protection
        if use_case == UseCaseType.PARODY_SATIRE:
            risk_level = LegalRiskLevel.LOW
            factors.append("Parody/satire may be protected under First Amendment")

        return {
            "risk_level": risk_level.value,
            "factors": factors,
            "note": "Right of Publicity varies by state. California and New York have strong protections."
        }

    def _analyze_fair_use(self,
                         use_case: UseCaseType,
                         is_open_source: bool,
                         is_non_monetized: bool,
                         is_transformative: bool,
                         is_educational: bool,
                         is_parody: bool) -> Dict[str, Any]:
        """
        Analyze Fair Use factors

        Fair Use factors (17 U.S.C. § 107):
        1. Purpose and character of use
        2. Nature of copyrighted work
        3. Amount used
        4. Effect on market
        """
        factors = []
        fair_use_score = 0  # 0-4, higher is better

        # Factor 1: Purpose and character
        if is_transformative:
            fair_use_score += 1
            factors.append("✅ Transformative use favors fair use")
        if is_educational:
            fair_use_score += 1
            factors.append("✅ Educational use favors fair use")
        if is_parody:
            fair_use_score += 1
            factors.append("✅ Parody/satire favors fair use")
        if is_non_monetized:
            fair_use_score += 0.5
            factors.append("✅ Non-commercial use favors fair use")
        if is_open_source:
            fair_use_score += 0.5
            factors.append("✅ Open-source project favors fair use")

        # Factor 4: Effect on market
        if is_non_monetized:
            fair_use_score += 1
            factors.append("✅ Non-monetized use reduces market impact")
        else:
            fair_use_score -= 1
            factors.append("⚠️  Commercial use may impact market")

        # Risk assessment
        if fair_use_score >= 3:
            risk_level = LegalRiskLevel.LOW
        elif fair_use_score >= 2:
            risk_level = LegalRiskLevel.MODERATE
        elif fair_use_score >= 1:
            risk_level = LegalRiskLevel.HIGH
        else:
            risk_level = LegalRiskLevel.CRITICAL

        return {
            "risk_level": risk_level.value,
            "fair_use_score": fair_use_score,
            "factors": factors,
            "note": "Fair use is a defense, not a right. Each case is fact-specific."
        }

    def _analyze_copyright(self,
                          actor_name: str,
                          character_name: Optional[str],
                          use_case: UseCaseType) -> Dict[str, Any]:
        """
        Analyze Copyright implications

        Voice recordings may be copyrighted.
        Character voices may be protected.
        """
        risk_level = LegalRiskLevel.MODERATE
        factors = []

        # Character voices may be copyrighted
        if character_name:
            factors.append("⚠️  Character voice may be copyrighted by studio/owner")
            risk_level = LegalRiskLevel.MODERATE

        # Actor's voice performance may be copyrighted
        factors.append("⚠️  Actor's voice performance may be copyrighted")

        # Fair use may apply
        if use_case in [UseCaseType.FAN_CONTENT_NON_MONETIZED, UseCaseType.TRANSFORMATIVE]:
            factors.append("✅ Fair use may apply to non-commercial fan content")
            risk_level = LegalRiskLevel.LOW

        return {
            "risk_level": risk_level.value,
            "factors": factors,
            "note": "Copyright protection varies. Fair use is fact-specific."
        }

    def _assess_overall_risk(self,
                            right_of_publicity: Dict[str, Any],
                            fair_use: Dict[str, Any],
                            copyright: Dict[str, Any]) -> LegalRiskLevel:
        """Assess overall legal risk"""
        risks = [
            LegalRiskLevel[right_of_publicity["risk_level"].upper()],
            LegalRiskLevel[fair_use["risk_level"].upper()],
            LegalRiskLevel[copyright["risk_level"].upper()]
        ]

        # Highest risk wins
        if LegalRiskLevel.CRITICAL in risks or LegalRiskLevel.REQUIRES_REAL_LAWYER in risks:
            return LegalRiskLevel.REQUIRES_REAL_LAWYER
        elif LegalRiskLevel.HIGH in risks:
            return LegalRiskLevel.HIGH
        elif LegalRiskLevel.MODERATE in risks:
            return LegalRiskLevel.MODERATE
        else:
            return LegalRiskLevel.LOW

    def _generate_recommendations(self,
                                 overall_risk: LegalRiskLevel,
                                 right_of_publicity: Dict[str, Any],
                                 fair_use: Dict[str, Any],
                                 copyright: Dict[str, Any]) -> List[str]:
        """Generate legal recommendations"""
        recommendations = []

        if overall_risk == LegalRiskLevel.REQUIRES_REAL_LAWYER:
            recommendations.append("🚨 REQUIRES REAL LAWYER: Engage entertainment/IP attorney")
            recommendations.append("   Contact law firm specializing in entertainment law")
            recommendations.append("   Get written legal opinion before proceeding")

        elif overall_risk == LegalRiskLevel.HIGH:
            recommendations.append("⚠️  HIGH RISK: Strongly recommend consulting real lawyer")
            recommendations.append("   Consider getting legal opinion")
            recommendations.append("   Document all fair use factors")

        elif overall_risk == LegalRiskLevel.MODERATE:
            recommendations.append("⚠️  MODERATE RISK: Consider consulting lawyer")
            recommendations.append("   Document non-commercial, transformative use")
            recommendations.append("   Include disclaimers")

        else:  # LOW
            recommendations.append("✅ LOW RISK: Likely acceptable for open-source, non-monetized use")
            recommendations.append("   Document fair use factors")
            recommendations.append("   Include disclaimers")
            recommendations.append("   Monitor for legal changes")

        # General recommendations
        recommendations.append("📋 Best Practices:")
        recommendations.append("   - Include clear disclaimers (fan content, non-commercial)")
        recommendations.append("   - Document transformative/educational purpose")
        recommendations.append("   - Do not monetize without permission")
        recommendations.append("   - Respect actor/studio rights")
        recommendations.append("   - Be prepared to remove if requested")

        return recommendations

    def _log_consultation(self, analysis: Dict[str, Any]):
        """Log legal consultation"""
        try:
            with open(self.consultation_history_file, 'a') as f:
                f.write(json.dumps(analysis) + '\n')
        except Exception as e:
            logger.warning(f"⚠️  Could not log consultation: {e}")

    def add_law_firm_contact(self,
                            firm_name: str,
                            contact_name: str,
                            email: str,
                            phone: Optional[str] = None,
                            specialties: List[str] = None,
                            notes: Optional[str] = None):
        """Add real law firm contact"""
        if specialties is None:
            specialties = []

        contact = {
            "firm_name": firm_name,
            "contact_name": contact_name,
            "email": email,
            "phone": phone,
            "specialties": specialties,
            "notes": notes,
            "added_date": datetime.now().isoformat()
        }

        # Add to appropriate category
        for specialty in specialties:
            if specialty.lower() in ["ip", "intellectual property", "copyright"]:
                self.law_firm_contacts["intellectual_property"].append(contact)
            elif specialty.lower() in ["entertainment", "entertainment law"]:
                self.law_firm_contacts["entertainment_law"].append(contact)
            elif specialty.lower() in ["technology", "tech law"]:
                self.law_firm_contacts["technology_law"].append(contact)
            else:
                self.law_firm_contacts["copyright_specialists"].append(contact)

        self._save_law_firm_contacts()
        logger.info(f"✅ Added law firm contact: {firm_name}")

    def get_law_firm_recommendations(self, specialty: str = "entertainment_law") -> List[Dict[str, Any]]:
        """Get recommended law firms for specialty"""
        return self.law_firm_contacts.get(specialty, [])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Legal Consultation Framework")
    parser.add_argument("--analyze", action="store_true", help="Analyze voice cloning use")
    parser.add_argument("--actor", type=str, help="Actor name")
    parser.add_argument("--character", type=str, help="Character name")
    parser.add_argument("--use-case", type=str, default="fan_content_non_monetized",
                       choices=[uc.value for uc in UseCaseType])

    args = parser.parse_args()

    print("\n" + "="*80)
    print("⚖️  Legal Consultation Framework")
    print("   Virtual Legal Team for LUMINA Open-Source Project")
    print("="*80 + "\n")

    framework = LegalConsultationFramework()

    if args.analyze and args.actor:
        analysis = framework.analyze_voice_cloning_use(
            actor_name=args.actor,
            character_name=args.character,
            use_case=UseCaseType(args.use_case),
            is_open_source=True,
            is_non_monetized=True,
            is_transformative=True
        )

        print(f"\n📊 Legal Analysis for: {args.actor} ({args.character or 'N/A'})")
        print(f"   Use Case: {analysis['use_case']}")
        print(f"   Overall Risk: {analysis['risk_assessment']['overall_risk'].upper()}")
        print(f"\n⚖️  Right of Publicity: {analysis['risk_assessment']['right_of_publicity']['risk_level'].upper()}")
        for factor in analysis['risk_assessment']['right_of_publicity']['factors']:
            print(f"   {factor}")
        print(f"\n📜 Fair Use: {analysis['risk_assessment']['fair_use']['risk_level'].upper()}")
        print(f"   Fair Use Score: {analysis['risk_assessment']['fair_use']['fair_use_score']}/4")
        for factor in analysis['risk_assessment']['fair_use']['factors']:
            print(f"   {factor}")
        print(f"\n©️  Copyright: {analysis['risk_assessment']['copyright']['risk_level'].upper()}")
        for factor in analysis['risk_assessment']['copyright']['factors']:
            print(f"   {factor}")
        print(f"\n💡 Recommendations:")
        for rec in analysis['recommendations']:
            print(f"   {rec}")

        if analysis['requires_real_lawyer']:
            print(f"\n🚨 REQUIRES REAL LAWYER")
            print(f"   Contact entertainment/IP attorney before proceeding")
    else:
        print("Use --analyze --actor <name> [--character <name>] [--use-case <type>]")
        print("="*80 + "\n")
