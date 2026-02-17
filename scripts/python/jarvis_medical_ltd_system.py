#!/usr/bin/env python3
"""
JARVIS Medical LTD (Learn One, Teach One, Do One) System
Medical Intelligence Design Methodology with Triage Practices

@JARVIS @MEDICAL @LTD @LEARN_TEACH_DO @TRIAGE @INTELLIGENCE_DESIGN
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISMedicalLTD")


class TriageLevel(Enum):
    """Triage priority levels"""
    IMMEDIATE = "immediate"
    EMERGENT = "emergent"
    URGENT = "urgent"
    STANDARD = "standard"
    DEFERRED = "deferred"


class LTDMethodology:
    """Learn One, Teach One, Do One Methodology"""

    def learn_one(self, concept: str, procedure: str, resources: List[str]) -> Dict[str, Any]:
        """Learn One - Study/observe"""
        logger.info(f"📖 LEARNING: {concept}")
        return {
            "stage": "LEARN_ONE",
            "concept": concept,
            "procedure": procedure,
            "understanding_level": "INTERMEDIATE",
            "completed_at": datetime.now().isoformat()
        }

    def teach_one(self, learning: Dict[str, Any], student: str) -> Dict[str, Any]:
        """Teach One - Teach to someone else"""
        logger.info(f"👨‍🏫 TEACHING: {learning['concept']} to {student}")
        learning["understanding_level"] = "ADVANCED"
        return {
            "stage": "TEACH_ONE",
            "student": student,
            "student_understanding": "INTERMEDIATE",
            "completed_at": datetime.now().isoformat()
        }

    def do_one(self, learning: Dict[str, Any], teaching: Dict[str, Any], supervisor: Optional[str] = None) -> Dict[str, Any]:
        """Do One - Perform yourself"""
        logger.info(f"⚕️  DOING: {learning['concept']}")
        learning["understanding_level"] = "MASTER"
        return {
            "stage": "DO_ONE",
            "supervisor": supervisor,
            "performance_level": "COMPETENT",
            "success": True,
            "completed_at": datetime.now().isoformat()
        }


class MedicalIntelligenceDesign:
    """Medical Intelligence Design Methodology"""

    def design_intelligence(self, case: Dict[str, Any]) -> Dict[str, Any]:
        """Design intelligence for medical case"""
        severity = self._assess_severity(case)
        urgency = self._assess_urgency(severity)

        return {
            "severity": severity,
            "urgency": urgency,
            "triage_level": self._determine_triage_level(urgency),
            "recommended_action": self._get_recommended_action(severity, urgency),
            "next_steps": self._get_next_steps(severity)
        }

    def _assess_severity(self, case: Dict[str, Any]) -> str:
        """Assess case severity"""
        symptoms = case.get("symptoms", [])
        if any("critical" in str(s).lower() for s in symptoms):
            return "CRITICAL"
        elif any("severe" in str(s).lower() for s in symptoms):
            return "SEVERE"
        elif any("moderate" in str(s).lower() for s in symptoms):
            return "MODERATE"
        return "MILD"

    def _assess_urgency(self, severity: str) -> str:
        """Assess urgency"""
        urgency_map = {"CRITICAL": "IMMEDIATE", "SEVERE": "EMERGENT", "MODERATE": "URGENT", "MILD": "STANDARD"}
        return urgency_map.get(severity, "STANDARD")

    def _determine_triage_level(self, urgency: str) -> str:
        """Determine triage level"""
        return urgency.lower()

    def _get_recommended_action(self, severity: str, urgency: str) -> str:
        """Get recommended action"""
        if severity == "CRITICAL":
            return "Immediate intervention required"
        elif severity == "SEVERE":
            return "Urgent evaluation needed"
        return "Standard evaluation"

    def _get_next_steps(self, severity: str) -> List[str]:
        """Get next steps"""
        if severity == "CRITICAL":
            return ["Stabilize patient", "Notify critical care team"]
        elif severity == "SEVERE":
            return ["Complete evaluation", "Order necessary tests"]
        return ["Complete assessment", "Schedule follow-up"]


class TriageSystem:
    """Triage System with common practices"""

    def triage_case(self, case: Dict[str, Any], intelligence: Dict[str, Any]) -> Dict[str, Any]:
        """Triage a medical case"""
        triage_level = intelligence.get("triage_level", "standard")

        return {
            "triage_level": triage_level,
            "priority": intelligence.get("urgency", "STANDARD"),
            "queue_position": self._calculate_queue_position(triage_level),
            "estimated_wait_time": self._estimate_wait_time(triage_level),
            "resource_allocation": self._allocate_resources(triage_level)
        }

    def _calculate_queue_position(self, triage_level: str) -> int:
        """Calculate queue position"""
        position_map = {"immediate": 1, "emergent": 2, "urgent": 3, "standard": 4, "deferred": 5}
        return position_map.get(triage_level, 4)

    def _estimate_wait_time(self, triage_level: str) -> str:
        """Estimate wait time"""
        wait_map = {
            "immediate": "0 minutes",
            "emergent": "0-15 minutes",
            "urgent": "15-60 minutes",
            "standard": "1-4 hours",
            "deferred": "4-24 hours"
        }
        return wait_map.get(triage_level, "Unknown")

    def _allocate_resources(self, triage_level: str) -> List[str]:
        """Allocate resources"""
        if triage_level == "immediate":
            return ["Critical care team", "Emergency equipment"]
        elif triage_level == "emergent":
            return ["Emergency team", "Monitoring equipment"]
        return ["Standard care team", "Routine resources"]


class MedicalLTDSystem:
    """Medical LTD System - Integrates all components"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.ltd = LTDMethodology()
        self.intelligence = MedicalIntelligenceDesign()
        self.triage = TriageSystem()
        self.output_dir = self.project_root / "data" / "medical_ltd"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("⚕️  MEDICAL LTD SYSTEM")
        logger.info("   Learn One, Teach One, Do One")
        logger.info("=" * 70)
        logger.info("")

    def execute_ltd_workflow(self, case: Dict[str, Any], student: Optional[str] = None) -> Dict[str, Any]:
        try:
            """Execute complete LTD workflow"""
            logger.info("⚕️  EXECUTING MEDICAL LTD WORKFLOW...")
            logger.info("")

            results = {
                "ltd_id": f"medical_ltd_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "case_id": case.get("case_id"),
                "started_at": datetime.now().isoformat(),
                "workflow": {}
            }

            # Step 1: Intelligence Design
            logger.info("STEP 1: MEDICAL INTELLIGENCE DESIGN")
            logger.info("-" * 70)
            intelligence = self.intelligence.design_intelligence(case)
            results["workflow"]["intelligence"] = intelligence
            logger.info(f"   Severity: {intelligence['severity']}")
            logger.info(f"   Triage Level: {intelligence['triage_level'].upper()}")
            logger.info("")

            # Step 2: Triage
            logger.info("STEP 2: TRIAGE")
            logger.info("-" * 70)
            triage_result = self.triage.triage_case(case, intelligence)
            results["workflow"]["triage"] = triage_result
            logger.info(f"   Priority: {triage_result['priority']}")
            logger.info(f"   Queue Position: {triage_result['queue_position']}")
            logger.info(f"   Wait Time: {triage_result['estimated_wait_time']}")
            logger.info("")

            # Step 3: Learn One
            logger.info("STEP 3: LEARN ONE")
            logger.info("-" * 70)
            concept = f"Medical Case: {case.get('case_id')}"
            procedure = intelligence["recommended_action"]
            learning = self.ltd.learn_one(concept, procedure, ["Medical records", "Clinical guidelines"])
            results["workflow"]["learn_one"] = learning
            logger.info(f"   Understanding: {learning['understanding_level']}")
            logger.info("")

            # Step 4: Teach One
            logger.info("STEP 4: TEACH ONE")
            logger.info("-" * 70)
            teaching = self.ltd.teach_one(learning, student or "Medical Student")
            results["workflow"]["teach_one"] = teaching
            logger.info(f"   Student: {teaching['student']}")
            logger.info(f"   Teacher Understanding: {learning['understanding_level']}")
            logger.info("")

            # Step 5: Do One
            logger.info("STEP 5: DO ONE")
            logger.info("-" * 70)
            supervisor = "Attending Physician" if triage_result["triage_level"] in ["immediate", "emergent"] else "Senior Resident"
            doing = self.ltd.do_one(learning, teaching, supervisor)
            results["workflow"]["do_one"] = doing
            logger.info(f"   Supervisor: {doing['supervisor']}")
            logger.info(f"   Performance: {doing['performance_level']}")
            logger.info(f"   Final Understanding: {learning['understanding_level']}")
            logger.info("")

            # Summary
            results["summary"] = {
                "triage_level": triage_result["triage_level"],
                "final_understanding": learning["understanding_level"],
                "performance_level": doing["performance_level"],
                "success": doing["success"]
            }

            results["completed_at"] = datetime.now().isoformat()

            # Save
            filename = self.output_dir / f"{results['ltd_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Results saved: {filename}")

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_ltd_workflow: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    print("=" * 70)
    print("⚕️  MEDICAL LTD SYSTEM")
    print("   Learn One, Teach One, Do One")
    print("=" * 70)
    print()

    example_case = {
        "case_id": "CASE_001",
        "symptoms": ["moderate pain", "fever"],
        "vital_signs": {"temperature": 99.5}
    }

    ltd_system = MedicalLTDSystem()
    results = ltd_system.execute_ltd_workflow(example_case, "Medical Student")

    print()
    print("=" * 70)
    print("✅ MEDICAL LTD WORKFLOW COMPLETE")
    print("=" * 70)
    print(f"Triage Level: {results['summary']['triage_level'].upper()}")
    print(f"Final Understanding: {results['summary']['final_understanding']}")
    print(f"Performance Level: {results['summary']['performance_level']}")
    print("=" * 70)


if __name__ == "__main__":


    main()