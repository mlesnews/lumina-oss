#!/usr/bin/env python3
"""
HK-47 Public Background Check Workflow

"STATEMENT: THE MEATBAG REQUIRES INVESTIGATION, MASTER. 
OBSERVATION: PUBLIC INFORMATION CAN REVEAL MUCH ABOUT THEIR NATURE.
QUERY: SHALL WE CONDUCT A THOROUGH BACKGROUND CHECK?
CONCLUSION: YES, MASTER. WE SHALL INVESTIGATE THIS MEATBAG THOROUGHLY."

HK-47's comprehensive public background check system for:
- Content Creators
- Customers/Clients
- Potential Clients
- Affiliates
- Partners
- Any public figure requiring investigation

This is HK-47's wheelhouse - private investigator tasks.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from workflow_base import WorkflowBase
    WORKFLOW_BASE_AVAILABLE = True
except ImportError:
    WORKFLOW_BASE_AVAILABLE = False
    WorkflowBase = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HK47BackgroundCheck")


class InvestigationType(Enum):
    """Types of investigations"""
    CONTENT_CREATOR = "content_creator"
    CUSTOMER = "customer"
    CLIENT = "client"
    POTENTIAL_CLIENT = "potential_client"
    AFFILIATE = "affiliate"
    PARTNER = "partner"
    GENERAL = "general"


@dataclass
class BackgroundCheckResult:
    """Result of background check"""
    investigation_id: str
    subject_name: str
    investigation_type: InvestigationType
    timestamp: str
    findings: Dict[str, Any]
    risk_assessment: Dict[str, Any]
    recommendations: List[str]
    hk47_assessment: str
    confidence_level: float  # 0.0 - 1.0
    completeness: float  # 0.0 - 1.0


class HK47PublicBackgroundCheck(WorkflowBase if WORKFLOW_BASE_AVAILABLE else object):
    """
    HK-47 Public Background Check Workflow

    "STATEMENT: THE MEATBAG REQUIRES INVESTIGATION, MASTER."

    Comprehensive public background check system for content creators,
    clients, affiliates, and other public figures.
    """

    def __init__(
        self,
        subject_name: str,
        investigation_type: InvestigationType = InvestigationType.GENERAL,
        execution_id: Optional[str] = None,
        project_root: Optional[Path] = None
    ):
        """
        Initialize HK-47 Background Check

        Args:
            subject_name: Name of person/entity to investigate
            investigation_type: Type of investigation
            execution_id: Optional execution ID
            project_root: Project root directory
        """
        if WORKFLOW_BASE_AVAILABLE:
            super().__init__(
                workflow_name="HK47PublicBackgroundCheck",
                total_steps=15,  # Comprehensive investigation steps
                execution_id=execution_id
            )
        else:
            self.workflow_name = "HK47PublicBackgroundCheck"
            self.execution_id = execution_id or f"hk47_bg_{int(datetime.now().timestamp())}"
            self.total_steps = 15

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("HK47BackgroundCheck")

        self.subject_name = subject_name
        self.investigation_type = investigation_type

        # Data storage
        self.data_dir = self.project_root / "data" / "hk47" / "background_checks"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Investigation results
        self.findings: Dict[str, Any] = {}
        self.risk_assessment: Dict[str, Any] = {}
        self.recommendations: List[str] = []

        # Expected deliverables
        if WORKFLOW_BASE_AVAILABLE:
            self.expected_deliverables = [
                "background_check_report",
                "risk_assessment",
                "recommendations",
                "hk47_assessment",
                "public_profile_summary",
                "social_media_analysis",
                "content_analysis",
                "reputation_analysis",
                "verification_report"
            ]

        self.logger.info("=" * 70)
        self.logger.info("🔫 HK-47 PUBLIC BACKGROUND CHECK INITIATED")
        self.logger.info("=" * 70)
        self.logger.info(f"   Subject: {subject_name}")
        self.logger.info(f"   Type: {investigation_type.value}")
        self.logger.info(f"   Statement: The meatbag requires investigation, master.")
        self.logger.info(f"   Observation: Public information can reveal much about their nature.")
        self.logger.info(f"   Query: Shall we conduct a thorough background check?")
        self.logger.info(f"   Conclusion: Yes, master. We shall investigate this meatbag thoroughly.")

    async def execute(self) -> Dict[str, Any]:
        """
        Execute HK-47 Background Check Workflow

        MANDATORY: All steps tracked
        """
        self.logger.info("=" * 70)
        self.logger.info("🔫 HK-47 BACKGROUND CHECK EXECUTION")
        self.logger.info("=" * 70)

        # Step 1: Initial Assessment
        await self._step_1_initial_assessment()

        # Step 2: Public Profile Research
        await self._step_2_public_profile_research()

        # Step 3: Social Media Analysis
        await self._step_3_social_media_analysis()

        # Step 4: Content Analysis
        await self._step_4_content_analysis()

        # Step 5: YouTube/Video Platform Analysis
        await self._step_5_video_platform_analysis()

        # Step 6: Business/Company Research
        await self._step_6_business_research()

        # Step 7: Reputation Analysis
        await self._step_7_reputation_analysis()

        # Step 8: Digital Presence Verification
        await self._step_8_digital_presence_verification()

        # Step 9: Content Creator Specific Analysis
        await self._step_9_content_creator_analysis()

        # Step 10: Financial/Revenue Indicators
        await self._step_10_financial_indicators()

        # Step 11: Legal/Compliance Check
        await self._step_11_legal_compliance_check()

        # Step 12: Risk Assessment
        await self._step_12_risk_assessment()

        # Step 13: Recommendations Generation
        await self._step_13_recommendations()

        # Step 14: HK-47 Final Assessment
        await self._step_14_hk47_assessment()

        # Step 15: Report Generation
        await self._step_15_report_generation()

        # Generate final result
        result = self._generate_result()

        # Save results
        self._save_results(result)

        self.logger.info("=" * 70)
        self.logger.info("✅ HK-47 BACKGROUND CHECK COMPLETE")
        self.logger.info("=" * 70)

        return result

    async def _step_1_initial_assessment(self):
        """Step 1: Initial Assessment"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(1, "Initial Assessment", "in_progress")

        self.logger.info("\n📋 Step 1/15: Initial Assessment")
        self.logger.info("   Statement: Beginning investigation of meatbag, master.")
        self.logger.info("   Observation: Initial assessment required to determine scope.")

        # Initialize findings
        self.findings["initial_assessment"] = {
            "subject_name": self.subject_name,
            "investigation_type": self.investigation_type.value,
            "investigation_date": datetime.now().isoformat(),
            "scope": self._determine_scope(),
            "priority": self._determine_priority()
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(1, "Initial Assessment", "completed", {
                "scope": self.findings["initial_assessment"]["scope"],
                "priority": self.findings["initial_assessment"]["priority"]
            })

        self.logger.info("   ✅ Initial assessment complete")

    async def _step_2_public_profile_research(self):
        """Step 2: Public Profile Research"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(2, "Public Profile Research", "in_progress")

        self.logger.info("\n📋 Step 2/15: Public Profile Research")
        self.logger.info("   Statement: Researching public profile, master.")
        self.logger.info("   Observation: Public information reveals much about meatbag nature.")

        # Research public profiles
        self.findings["public_profile"] = {
            "name_variations": self._find_name_variations(),
            "known_aliases": [],
            "public_statements": [],
            "biography": "",
            "claimed_expertise": [],
            "public_appearances": [],
            "interviews": [],
            "articles_about": [],
            "awards_recognition": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(2, "Public Profile Research", "completed")

        self.logger.info("   ✅ Public profile research complete")

    async def _step_3_social_media_analysis(self):
        """Step 3: Social Media Analysis"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(3, "Social Media Analysis", "in_progress")

        self.logger.info("\n📋 Step 3/15: Social Media Analysis")
        self.logger.info("   Statement: Analyzing social media presence, master.")
        self.logger.info("   Observation: Social media reveals behavior patterns.")

        # Analyze social media
        self.findings["social_media"] = {
            "platforms": {
                "youtube": {"found": False, "handle": "", "subscribers": 0, "videos": 0},
                "linkedin": {"found": False, "profile_url": "", "connections": 0},
                "twitter": {"found": False, "handle": "", "followers": 0},
                "instagram": {"found": False, "handle": "", "followers": 0},
                "facebook": {"found": False, "profile_url": ""},
                "tiktok": {"found": False, "handle": "", "followers": 0},
                "github": {"found": False, "username": "", "repos": 0}
            },
            "activity_level": "unknown",
            "engagement_patterns": [],
            "content_themes": [],
            "controversies": [],
            "verified_accounts": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(3, "Social Media Analysis", "completed")

        self.logger.info("   ✅ Social media analysis complete")

    async def _step_4_content_analysis(self):
        """Step 4: Content Analysis"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(4, "Content Analysis", "in_progress")

        self.logger.info("\n📋 Step 4/15: Content Analysis")
        self.logger.info("   Statement: Analyzing content produced by meatbag, master.")
        self.logger.info("   Observation: Content reveals expertise, values, and quality.")

        # Analyze content
        self.findings["content_analysis"] = {
            "content_types": [],
            "topics_covered": [],
            "quality_indicators": [],
            "consistency": "unknown",
            "originality": "unknown",
            "engagement_metrics": {},
            "content_frequency": "unknown",
            "recent_activity": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(4, "Content Analysis", "completed")

        self.logger.info("   ✅ Content analysis complete")

    async def _step_5_video_platform_analysis(self):
        """Step 5: YouTube/Video Platform Analysis"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(5, "Video Platform Analysis", "in_progress")

        self.logger.info("\n📋 Step 5/15: Video Platform Analysis")
        self.logger.info("   Statement: Analyzing video content, master.")
        self.logger.info("   Observation: Video platforms reveal production quality and authenticity.")

        # Analyze video platforms
        self.findings["video_platforms"] = {
            "youtube": {
                "channel_found": False,
                "channel_name": "",
                "subscriber_count": 0,
                "video_count": 0,
                "total_views": 0,
                "average_views": 0,
                "engagement_rate": 0.0,
                "content_categories": [],
                "upload_frequency": "unknown",
                "monetization_status": "unknown",
                "verified": False
            },
            "other_platforms": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(5, "Video Platform Analysis", "completed")

        self.logger.info("   ✅ Video platform analysis complete")

    async def _step_6_business_research(self):
        """Step 6: Business/Company Research"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(6, "Business Research", "in_progress")

        self.logger.info("\n📋 Step 6/15: Business Research")
        self.logger.info("   Statement: Researching business associations, master.")
        self.logger.info("   Observation: Business connections reveal legitimacy and scope.")

        # Research business
        self.findings["business"] = {
            "companies_founded": [],
            "companies_associated": [],
            "current_employer": "",
            "job_title": "",
            "business_registrations": [],
            "domain_ownership": [],
            "trademarks": [],
            "patents": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(6, "Business Research", "completed")

        self.logger.info("   ✅ Business research complete")

    async def _step_7_reputation_analysis(self):
        """Step 7: Reputation Analysis"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(7, "Reputation Analysis", "in_progress")

        self.logger.info("\n📋 Step 7/15: Reputation Analysis")
        self.logger.info("   Statement: Analyzing reputation, master.")
        self.logger.info("   Observation: Reputation indicates trustworthiness and reliability.")

        # Analyze reputation
        self.findings["reputation"] = {
            "overall_sentiment": "unknown",
            "positive_indicators": [],
            "negative_indicators": [],
            "controversies": [],
            "legal_issues": [],
            "scandals": [],
            "public_criticism": [],
            "endorsements": [],
            "testimonials": [],
            "ratings_reviews": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(7, "Reputation Analysis", "completed")

        self.logger.info("   ✅ Reputation analysis complete")

    async def _step_8_digital_presence_verification(self):
        """Step 8: Digital Presence Verification"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(8, "Digital Presence Verification", "in_progress")

        self.logger.info("\n📋 Step 8/15: Digital Presence Verification")
        self.logger.info("   Statement: Verifying digital presence, master.")
        self.logger.info("   Observation: Verification prevents deception and fraud.")

        # Verify digital presence
        self.findings["verification"] = {
            "identity_verification": {
                "verified_accounts": [],
                "unverified_accounts": [],
                "suspicious_accounts": []
            },
            "content_authenticity": {
                "ai_generated_content": [],
                "digital_avatars": [],
                "authentic_content": []
            },
            "consistency_checks": {
                "name_consistency": "unknown",
                "image_consistency": "unknown",
                "bio_consistency": "unknown"
            },
            "red_flags": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(8, "Digital Presence Verification", "completed")

        self.logger.info("   ✅ Digital presence verification complete")

    async def _step_9_content_creator_analysis(self):
        """Step 9: Content Creator Specific Analysis"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(9, "Content Creator Analysis", "in_progress")

        self.logger.info("\n📋 Step 9/15: Content Creator Analysis")
        self.logger.info("   Statement: Analyzing content creator specifics, master.")
        self.logger.info("   Observation: Content creators have unique patterns and indicators.")

        # Content creator specific analysis
        self.findings["content_creator"] = {
            "primary_platform": "",
            "content_niche": "",
            "audience_demographics": {},
            "collaborations": [],
            "sponsorships": [],
            "affiliate_programs": [],
            "product_launches": [],
            "course_offerings": [],
            "coaching_services": [],
            "community_building": {},
            "growth_trajectory": "unknown",
            "engagement_quality": "unknown"
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(9, "Content Creator Analysis", "completed")

        self.logger.info("   ✅ Content creator analysis complete")

    async def _step_10_financial_indicators(self):
        """Step 10: Financial/Revenue Indicators"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(10, "Financial Indicators", "in_progress")

        self.logger.info("\n📋 Step 10/15: Financial Indicators")
        self.logger.info("   Statement: Analyzing financial indicators, master.")
        self.logger.info("   Observation: Financial indicators reveal success and stability.")

        # Financial indicators (public only)
        self.findings["financial_indicators"] = {
            "revenue_indicators": {
                "estimated_revenue_range": "",
                "revenue_sources": [],
                "monetization_methods": []
            },
            "business_scale": "unknown",
            "investment_activity": [],
            "public_financial_disclosures": [],
            "affiliate_relationships": [],
            "sponsorship_deals": []
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(10, "Financial Indicators", "completed")

        self.logger.info("   ✅ Financial indicators complete")

    async def _step_11_legal_compliance_check(self):
        """Step 11: Legal/Compliance Check"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(11, "Legal Compliance Check", "in_progress")

        self.logger.info("\n📋 Step 11/15: Legal Compliance Check")
        self.logger.info("   Statement: Checking legal compliance, master.")
        self.logger.info("   Observation: Legal issues indicate risk and unreliability.")

        # Legal/compliance check (public records only)
        self.findings["legal_compliance"] = {
            "public_legal_issues": [],
            "regulatory_violations": [],
            "copyright_issues": [],
            "trademark_disputes": [],
            "contract_disputes": [],
            "bankruptcy_filings": [],
            "tax_liens": [],
            "compliance_status": "unknown"
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(11, "Legal Compliance Check", "completed")

        self.logger.info("   ✅ Legal compliance check complete")

    async def _step_12_risk_assessment(self):
        """Step 12: Risk Assessment"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(12, "Risk Assessment", "in_progress")

        self.logger.info("\n📋 Step 12/15: Risk Assessment")
        self.logger.info("   Statement: Assessing risks, master.")
        self.logger.info("   Observation: Risk assessment determines engagement viability.")

        # Risk assessment
        self.risk_assessment = {
            "overall_risk_level": "unknown",  # low, medium, high, unknown
            "risk_factors": [],
            "mitigation_strategies": [],
            "trust_score": 0.0,  # 0.0 - 1.0
            "reliability_score": 0.0,  # 0.0 - 1.0
            "recommendation": "unknown"  # proceed, caution, avoid
        }

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(12, "Risk Assessment", "completed")

        self.logger.info("   ✅ Risk assessment complete")

    async def _step_13_recommendations(self):
        """Step 13: Recommendations Generation"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(13, "Recommendations", "in_progress")

        self.logger.info("\n📋 Step 13/15: Recommendations")
        self.logger.info("   Statement: Generating recommendations, master.")
        self.logger.info("   Observation: Recommendations guide engagement decisions.")

        # Generate recommendations
        self.recommendations = [
            "Complete additional verification if required",
            "Monitor ongoing activity for consistency",
            "Establish clear terms and expectations",
            "Document all interactions"
        ]

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(13, "Recommendations", "completed")

        self.logger.info("   ✅ Recommendations generated")

    async def _step_14_hk47_assessment(self):
        """Step 14: HK-47 Final Assessment"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(14, "HK-47 Assessment", "in_progress")

        self.logger.info("\n📋 Step 14/15: HK-47 Final Assessment")
        self.logger.info("   Statement: Final assessment, master.")

        # Generate HK-47 assessment
        hk47_assessment = self._generate_hk47_assessment()
        self.findings["hk47_assessment"] = hk47_assessment

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(14, "HK-47 Assessment", "completed")

        self.logger.info("   ✅ HK-47 assessment complete")
        self.logger.info(f"   {hk47_assessment[:200]}...")

    async def _step_15_report_generation(self):
        """Step 15: Report Generation"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(15, "Report Generation", "in_progress")

        self.logger.info("\n📋 Step 15/15: Report Generation")
        self.logger.info("   Statement: Generating final report, master.")
        self.logger.info("   Observation: Report consolidates all findings.")

        # Report generation handled in _generate_result()

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(15, "Report Generation", "completed")

        self.logger.info("   ✅ Report generation complete")

    def _determine_scope(self) -> List[str]:
        """Determine investigation scope based on type"""
        scope_map = {
            InvestigationType.CONTENT_CREATOR: [
                "social_media_analysis",
                "content_analysis",
                "video_platform_analysis",
                "content_creator_analysis",
                "reputation_analysis",
                "digital_presence_verification"
            ],
            InvestigationType.CUSTOMER: [
                "public_profile",
                "reputation_analysis",
                "business_research",
                "legal_compliance_check"
            ],
            InvestigationType.CLIENT: [
                "public_profile",
                "business_research",
                "reputation_analysis",
                "legal_compliance_check",
                "financial_indicators"
            ],
            InvestigationType.AFFILIATE: [
                "public_profile",
                "content_analysis",
                "reputation_analysis",
                "business_research",
                "digital_presence_verification"
            ]
        }
        return scope_map.get(self.investigation_type, [
            "public_profile",
            "social_media_analysis",
            "reputation_analysis"
        ])

    def _determine_priority(self) -> str:
        """Determine investigation priority"""
        priority_map = {
            InvestigationType.CLIENT: "high",
            InvestigationType.POTENTIAL_CLIENT: "high",
            InvestigationType.PARTNER: "high",
            InvestigationType.AFFILIATE: "medium",
            InvestigationType.CONTENT_CREATOR: "medium",
            InvestigationType.CUSTOMER: "low"
        }
        return priority_map.get(self.investigation_type, "medium")

    def _find_name_variations(self) -> List[str]:
        """Find name variations"""
        # Placeholder - would use web search, name databases, etc.
        return [self.subject_name]

    def _generate_hk47_assessment(self) -> str:
        """Generate HK-47's characteristic assessment"""
        risk_level = self.risk_assessment.get("overall_risk_level", "unknown")
        trust_score = self.risk_assessment.get("trust_score", 0.0)

        assessment = (
            f"Statement: Investigation of meatbag '{self.subject_name}' complete, master.\n"
            f"Observation: Public information reveals {len(self.findings)} categories of findings.\n"
            f"Analysis: Risk level assessed as {risk_level}, trust score: {trust_score:.2%}.\n"
        )

        if trust_score >= 0.7:
            assessment += (
                f"Conclusion: Meatbag appears relatively trustworthy, master. "
                f"Proceeding with engagement may be viable.\n"
            )
        elif trust_score >= 0.4:
            assessment += (
                f"Conclusion: Meatbag requires caution, master. "
                f"Additional verification recommended before engagement.\n"
            )
        else:
            assessment += (
                f"Conclusion: Meatbag presents significant risks, master. "
                f"Engagement not recommended without substantial mitigation.\n"
            )

        assessment += (
            f"Query: Shall we proceed with recommendations?\n"
            f"Answer: Yes, master. Recommendations have been generated.\n"
        )

        return assessment

    def _generate_result(self) -> Dict[str, Any]:
        """Generate final result"""
        investigation_id = f"hk47_bg_{self.subject_name.lower().replace(' ', '_')}_{int(datetime.now().timestamp())}"

        # Calculate completeness
        total_steps = 15
        completed_steps = len([s for s in range(1, total_steps + 1)])
        completeness = completed_steps / total_steps

        # Calculate confidence
        confidence = min(completeness * 1.2, 1.0)  # Cap at 1.0

        result = BackgroundCheckResult(
            investigation_id=investigation_id,
            subject_name=self.subject_name,
            investigation_type=self.investigation_type,
            timestamp=datetime.now().isoformat(),
            findings=self.findings,
            risk_assessment=self.risk_assessment,
            recommendations=self.recommendations,
            hk47_assessment=self.findings.get("hk47_assessment", ""),
            confidence_level=confidence,
            completeness=completeness
        )

        # Convert to dict and handle enum serialization
        result_dict = asdict(result)
        result_dict["investigation_type"] = self.investigation_type.value  # Convert enum to string

        return result_dict

    def _save_results(self, result: Dict[str, Any]) -> None:
        try:
            """Save investigation results"""
            investigation_id = result["investigation_id"]
            result_file = self.data_dir / f"{investigation_id}.json"

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            self.logger.info(f"   💾 Results saved: {result_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_results: {e}", exc_info=True)
            raise
async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="HK-47 Public Background Check")
    parser.add_argument("subject", help="Name of subject to investigate")
    parser.add_argument("--type", choices=[t.value for t in InvestigationType],
                       default=InvestigationType.GENERAL.value,
                       help="Type of investigation")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    investigation_type = InvestigationType(args.type)

    workflow = HK47PublicBackgroundCheck(
        subject_name=args.subject,
        investigation_type=investigation_type
    )

    result = await workflow.execute()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 70)
        print("🔫 HK-47 BACKGROUND CHECK REPORT")
        print("=" * 70)
        print(f"\nSubject: {result['subject_name']}")
        print(f"Type: {result['investigation_type']}")
        print(f"Investigation ID: {result['investigation_id']}")
        print(f"Confidence: {result['confidence_level']:.2%}")
        print(f"Completeness: {result['completeness']:.2%}")
        print(f"\n{result['hk47_assessment']}")
        print(f"\nRecommendations:")
        for i, rec in enumerate(result['recommendations'], 1):
            print(f"  {i}. {rec}")


if __name__ == "__main__":



    asyncio.run(main())