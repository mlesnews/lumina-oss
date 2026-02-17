#!/usr/bin/env python3
"""
JARVIS Hiring Manager System

For technical/financial opportunities:
- Skill comparison and matching
- Slot assignment (Assistant Engineer, Engineer, Senior, etc.)
- Employee power structure analysis
- Grooming candidates from lower positions
- Merit-based assessment (#Merit)

Tags: #HIRING #RECRUITMENT #MERIT #SKILL_MATCHING #GROOMING @JARVIS @LUMINA
"""

import sys
import json
import re
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

logger = get_logger("JARVISHiringManager")


class RoleLevel(Enum):
    """Role levels in power structure"""
    JUNIOR = {"level": 1, "title": "Junior Engineer", "grooming_potential": "HIGH"}
    ASSISTANT = {"level": 2, "title": "Assistant Engineer", "grooming_potential": "HIGH"}
    ENGINEER = {"level": 3, "title": "Engineer", "grooming_potential": "MEDIUM"}
    SENIOR = {"level": 4, "title": "Senior Engineer", "grooming_potential": "MEDIUM"}
    LEAD = {"level": 5, "title": "Lead Engineer", "grooming_potential": "LOW"}
    PRINCIPAL = {"level": 6, "title": "Principal Engineer", "grooming_potential": "LOW"}
    ARCHITECT = {"level": 7, "title": "Architect", "grooming_potential": "VERY_LOW"}


class MeritAssessment:
    """#Merit-based assessment system"""

    def __init__(self):
        self.merit_factors = {
            "technical_skills": 0.30,
            "experience": 0.25,
            "achievements": 0.20,
            "growth_potential": 0.15,
            "cultural_fit": 0.10
        }

    def calculate_merit_score(self, candidate: Dict[str, Any]) -> float:
        """Calculate merit score (0-100)"""
        score = 0.0

        # Technical skills (30%)
        skills = candidate.get("technical_skills", {})
        if skills:
            avg_skill = sum(skills.values()) / len(skills)
            score += avg_skill * 20 * self.merit_factors["technical_skills"]  # Scale to 0-30

        # Experience (25%)
        experience = candidate.get("experience_years", 0)
        experience_score = min(experience / 10, 1.0)  # Cap at 10 years = 100%
        score += experience_score * 100 * self.merit_factors["experience"]

        # Achievements (20%)
        achievements = candidate.get("achievements", [])
        achievement_score = min(len(achievements) / 10, 1.0)  # Cap at 10 achievements
        score += achievement_score * 100 * self.merit_factors["achievements"]

        # Growth potential (15%)
        growth_potential = candidate.get("growth_potential", 0.5)
        score += growth_potential * 100 * self.merit_factors["growth_potential"]

        # Cultural fit (10%)
        cultural_fit = candidate.get("cultural_fit", 0.7)
        score += cultural_fit * 100 * self.merit_factors["cultural_fit"]

        return round(score, 2)

    def assess_merit(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive merit assessment"""
        merit_score = self.calculate_merit_score(candidate)

        if merit_score >= 85:
            merit_level = "EXCEPTIONAL"
        elif merit_score >= 70:
            merit_level = "HIGH"
        elif merit_score >= 55:
            merit_level = "GOOD"
        elif merit_score >= 40:
            merit_level = "ADEQUATE"
        else:
            merit_level = "NEEDS_IMPROVEMENT"

        return {
            "merit_score": merit_score,
            "merit_level": merit_level,
            "factors": {
                "technical_skills": candidate.get("technical_skills", {}),
                "experience_years": candidate.get("experience_years", 0),
                "achievements_count": len(candidate.get("achievements", [])),
                "growth_potential": candidate.get("growth_potential", 0.5),
                "cultural_fit": candidate.get("cultural_fit", 0.7)
            },
            "assessment": f"#Merit score: {merit_score}/100 ({merit_level})"
        }


class HiringManager:
    """Hiring Manager for technical/financial opportunities"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "hiring_manager"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.merit_assessor = MeritAssessment()
        self.open_slots = {}
        self.candidates = []

    def add_open_slot(self, role_level: RoleLevel, count: int, requirements: Dict[str, Any]):
        """Add open position slot"""
        slot_id = f"{role_level.value['title'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}"

        self.open_slots[slot_id] = {
            "slot_id": slot_id,
            "role_level": role_level.value["title"],
            "level": role_level.value["level"],
            "count": count,
            "filled": 0,
            "available": count,
            "requirements": requirements,
            "grooming_potential": role_level.value["grooming_potential"],
            "created_at": datetime.now().isoformat()
        }

        logger.info(f"📋 Added slot: {role_level.value['title']} (x{count})")

    def add_candidate(self, candidate: Dict[str, Any]):
        """Add candidate for evaluation"""
        candidate_id = f"CAND_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        candidate["candidate_id"] = candidate_id
        candidate["added_at"] = datetime.now().isoformat()

        self.candidates.append(candidate)
        logger.info(f"👤 Added candidate: {candidate.get('name', 'Unknown')}")

    def match_candidate_to_slots(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Match candidate to appropriate slots"""
        matches = {
            "candidate": candidate.get("name", "Unknown"),
            "candidate_id": candidate.get("candidate_id"),
            "matches": [],
            "recommended_slot": None,
            "grooming_recommendation": None
        }

        # Calculate merit score
        merit_assessment = self.merit_assessor.assess_merit(candidate)
        candidate["merit_score"] = merit_assessment["merit_score"]
        candidate["merit_level"] = merit_assessment["merit_level"]

        # Match to each slot
        for slot_id, slot in self.open_slots.items():
            match_score = self._calculate_match_score(candidate, slot)

            match = {
                "slot_id": slot_id,
                "role_level": slot["role_level"],
                "level": slot["level"],
                "match_score": match_score,
                "fit": self._determine_fit(match_score),
                "available": slot["available"] > 0,
                "grooming_potential": slot["grooming_potential"]
            }

            matches["matches"].append(match)

        # Sort by match score
        matches["matches"].sort(key=lambda x: x["match_score"], reverse=True)

        # Recommend best match
        if matches["matches"]:
            best_match = matches["matches"][0]
            matches["recommended_slot"] = {
                "slot_id": best_match["slot_id"],
                "role_level": best_match["role_level"],
                "match_score": best_match["match_score"],
                "fit": best_match["fit"]
            }

            # Grooming recommendation
            if best_match["level"] > 1 and best_match["grooming_potential"] == "HIGH":
                matches["grooming_recommendation"] = {
                    "recommended": True,
                    "reason": "High grooming potential - can grow from lower position",
                    "current_level": best_match["level"],
                    "target_level": best_match["level"] + 1,
                    "compromise": "Candidate grows while company provides opportunity"
                }

        return matches

    def _calculate_match_score(self, candidate: Dict[str, Any], slot: Dict[str, Any]) -> float:
        """Calculate match score between candidate and slot"""
        score = 0.0

        # Skill matching
        candidate_skills = candidate.get("technical_skills", {})
        required_skills = slot["requirements"].get("technical_skills", {})

        if required_skills:
            skill_matches = 0
            total_required = len(required_skills)

            for skill, required_level in required_skills.items():
                candidate_level = candidate_skills.get(skill, 0)
                if candidate_level >= required_level:
                    skill_matches += 1

            skill_score = skill_matches / total_required if total_required > 0 else 0
            score += skill_score * 40  # 40% weight

        # Experience matching
        required_experience = slot["requirements"].get("experience_years", 0)
        candidate_experience = candidate.get("experience_years", 0)

        if required_experience > 0:
            experience_score = min(candidate_experience / required_experience, 1.5)  # Can be 1.5x overqualified
            score += min(experience_score, 1.0) * 30  # 30% weight, cap at 100%

        # Merit score
        merit_score = candidate.get("merit_score", 0)
        score += (merit_score / 100) * 30  # 30% weight

        return round(score, 2)

    def _determine_fit(self, match_score: float) -> str:
        """Determine fit level"""
        if match_score >= 80:
            return "EXCELLENT"
        elif match_score >= 65:
            return "GOOD"
        elif match_score >= 50:
            return "ADEQUATE"
        elif match_score >= 35:
            return "MARGINAL"
        else:
            return "POOR"

    def evaluate_grooming_potential(self, candidate: Dict[str, Any], 
                                   target_slot: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate if candidate can be groomed from lower position"""
        current_level = target_slot["level"]
        target_level = current_level + 1

        grooming_assessment = {
            "candidate": candidate.get("name", "Unknown"),
            "current_slot": target_slot["role_level"],
            "target_level": target_level,
            "groomable": False,
            "growth_potential": candidate.get("growth_potential", 0.5),
            "merit_score": candidate.get("merit_score", 0),
            "compromise_analysis": {},
            "recommendation": ""
        }

        # Check if groomable
        growth_potential = candidate.get("growth_potential", 0.5)
        merit_score = candidate.get("merit_score", 0)

        if growth_potential >= 0.7 and merit_score >= 60:
            grooming_assessment["groomable"] = True
            grooming_assessment["compromise_analysis"] = {
                "candidate_compromise": "Takes lower position to grow",
                "company_compromise": "Provides opportunity and mentorship",
                "mutual_benefit": "Both parties invest in growth",
                "merit_based": "#Merit determines success"
            }
            grooming_assessment["recommendation"] = (
                f"✅ GROOMABLE: Place in {target_slot['role_level']} slot. "
                f"High growth potential ({growth_potential*100:.0f}%) and merit score ({merit_score:.0f}). "
                f"Candidate can grow based on their own merit while company provides opportunity."
            )
        else:
            grooming_assessment["recommendation"] = (
                f"❌ NOT GROOMABLE: Growth potential ({growth_potential*100:.0f}%) or merit ({merit_score:.0f}) "
                f"insufficient for grooming from lower position."
            )

        return grooming_assessment

    def compare_skills_to_opportunities(self, candidate: Dict[str, Any]) -> Dict[str, Any]:
        """Compare candidate skills to all open opportunities"""
        logger.info("=" * 80)
        logger.info("🔍 SKILL COMPARISON: Candidate vs. Opportunities")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"📋 Candidate: {candidate.get('name', 'Unknown')}")
        logger.info("")

        # Get matches
        matches = self.match_candidate_to_slots(candidate)

        # Display matches
        logger.info("📊 Slot Matches:")
        for match in matches["matches"]:
            logger.info(f"   {match['role_level']}: {match['match_score']:.1f}% ({match['fit']})")
            if match["available"]:
                logger.info(f"      ✅ Available")
            else:
                logger.info(f"      ❌ Filled")

        logger.info("")

        # Recommended slot
        if matches["recommended_slot"]:
            logger.info(f"🎯 Recommended Slot: {matches['recommended_slot']['role_level']}")
            logger.info(f"   Match Score: {matches['recommended_slot']['match_score']:.1f}%")
            logger.info(f"   Fit: {matches['recommended_slot']['fit']}")
            logger.info("")

        # Grooming recommendation
        if matches["grooming_recommendation"]:
            logger.info("🌱 Grooming Recommendation:")
            logger.info(f"   {matches['grooming_recommendation']['reason']}")
            logger.info(f"   Current Level: {matches['grooming_recommendation']['current_level']}")
            logger.info(f"   Target Level: {matches['grooming_recommendation']['target_level']}")
            logger.info(f"   Compromise: {matches['grooming_recommendation']['compromise']}")
            logger.info("")

        # Merit assessment
        merit = self.merit_assessor.assess_merit(candidate)
        logger.info(f"⭐ #Merit Assessment: {merit['merit_score']}/100 ({merit['merit_level']})")
        logger.info("")

        logger.info("=" * 80)
        logger.info("✅ COMPARISON COMPLETE")
        logger.info("=" * 80)
        logger.info("")

        return matches

    def fill_slots_with_compromise(self) -> Dict[str, Any]:
        """Fill slots with compromise strategy (grooming from lower positions)"""
        logger.info("=" * 80)
        logger.info("🎯 FILLING SLOTS WITH COMPROMISE STRATEGY")
        logger.info("=" * 80)
        logger.info("")

        assignments = {
            "timestamp": datetime.now().isoformat(),
            "strategy": "COMPROMISE_GROOMING",
            "assignments": [],
            "grooming_opportunities": []
        }

        # Sort candidates by merit score
        sorted_candidates = sorted(self.candidates, 
                                 key=lambda c: c.get("merit_score", 0), 
                                 reverse=True)

        # Assign candidates to slots
        for candidate in sorted_candidates:
            matches = self.match_candidate_to_slots(candidate)

            if matches["recommended_slot"]:
                slot_id = matches["recommended_slot"]["slot_id"]
                slot = self.open_slots[slot_id]

                # Check if slot available
                if slot["available"] > 0:
                    # Evaluate grooming potential
                    grooming = self.evaluate_grooming_potential(candidate, slot)

                    assignment = {
                        "candidate": candidate.get("name", "Unknown"),
                        "candidate_id": candidate.get("candidate_id"),
                        "assigned_slot": slot["role_level"],
                        "match_score": matches["recommended_slot"]["match_score"],
                        "merit_score": candidate.get("merit_score", 0),
                        "grooming_assessment": grooming
                    }

                    assignments["assignments"].append(assignment)

                    if grooming["groomable"]:
                        assignments["grooming_opportunities"].append(assignment)
                        logger.info(f"✅ Assigned: {candidate.get('name')} → {slot['role_level']} (GROOMABLE)")
                    else:
                        logger.info(f"✅ Assigned: {candidate.get('name')} → {slot['role_level']}")

                    # Update slot
                    slot["filled"] += 1
                    slot["available"] -= 1

        logger.info("")
        logger.info(f"📊 Total Assignments: {len(assignments['assignments'])}")
        logger.info(f"🌱 Grooming Opportunities: {len(assignments['grooming_opportunities'])}")
        logger.info("")

        return assignments


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Hiring Manager System")
        parser.add_argument("--add-slot", type=str, help="Add slot: level,count,requirements_json")
        parser.add_argument("--add-candidate", type=str, help="Path to candidate JSON file")
        parser.add_argument("--compare", type=str, help="Compare candidate: candidate_id or name")
        parser.add_argument("--fill-slots", action="store_true", help="Fill slots with compromise strategy")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = HiringManager(project_root)

        # Example: Add slots
        manager.add_open_slot(
            RoleLevel.ASSISTANT,
            3,
            {
                "technical_skills": {"software_engineering": 2, "python": 2},
                "experience_years": 1
            }
        )

        manager.add_open_slot(
            RoleLevel.ENGINEER,
            2,
            {
                "technical_skills": {"software_engineering": 3, "python": 3, "cloud_computing": 2},
                "experience_years": 3
            }
        )

        # Example: Add candidate
        example_candidate = {
            "name": "Example Candidate",
            "experience_years": 2,
            "technical_skills": {
                "software_engineering": 3,
                "python": 3,
                "cloud_computing": 2
            },
            "growth_potential": 0.8,
            "cultural_fit": 0.85,
            "achievements": ["Project A", "Project B"]
        }

        manager.add_candidate(example_candidate)

        # Compare
        if args.compare:
            candidate = next((c for c in manager.candidates 
                             if c.get("name") == args.compare or c.get("candidate_id") == args.compare), 
                            example_candidate)
            matches = manager.compare_skills_to_opportunities(candidate)
            print(json.dumps(matches, indent=2, default=str))
        elif args.fill_slots:
            assignments = manager.fill_slots_with_compromise()
            print(json.dumps(assignments, indent=2, default=str))
        else:
            # Default: Compare example candidate
            matches = manager.compare_skills_to_opportunities(example_candidate)
            print(json.dumps(matches, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()