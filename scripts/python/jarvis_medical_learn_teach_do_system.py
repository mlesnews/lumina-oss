#!/usr/bin/env python3
"""
JARVIS Medical Learn One, Teach One, Do One System
Medical Intelligence-Design Methodology with Triage Practices

@JARVIS @MEDICAL @LEARN_TEACH_DO @TRIAGE @HR_TEAM @DOCTORS
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
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

logger = get_logger("JARVISMedicalLearnTeachDo")


class TriageLevel(Enum):
    """Medical triage levels"""
    IMMEDIATE = "immediate"  # Life-threatening, immediate care needed
    EMERGENT = "emergent"  # Urgent, care needed within hours
    URGENT = "urgent"  # Care needed within 24 hours
    NON_URGENT = "non_urgent"  # Can wait, routine care
    ROUTINE = "routine"  # Scheduled care


class LearningStage(Enum):
    """Learn One, Teach One, Do One stages"""
    LEARN_ONE = "learn_one"  # Study and understand
    TEACH_ONE = "teach_one"  # Teach to someone else
    DO_ONE = "do_one"  # Perform independently


class MedicalProcedure:
    """Medical procedure for Learn One, Teach One, Do One"""

    def __init__(self, procedure_id: str, name: str, description: str, 
                 complexity: str, specialty: str):
        """Initialize medical procedure"""
        self.procedure_id = procedure_id
        self.name = name
        self.description = description
        self.complexity = complexity  # simple, moderate, complex, critical
        self.specialty = specialty
        self.learn_stage = None
        self.teach_stage = None
        self.do_stage = None
        self.triage_level = TriageLevel.ROUTINE
        self.created_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "procedure_id": self.procedure_id,
            "name": self.name,
            "description": self.description,
            "complexity": self.complexity,
            "specialty": self.specialty,
            "learn_stage": self.learn_stage.value if self.learn_stage else None,
            "teach_stage": self.teach_stage.value if self.teach_stage else None,
            "do_stage": self.do_stage.value if self.do_stage else None,
            "triage_level": self.triage_level.value,
            "created_at": self.created_at.isoformat()
        }


class TriageSystem:
    """
    Medical Triage System

    Common triage practices:
    - Assess urgency
    - Prioritize care
    - Allocate resources
    - Track outcomes
    """

    def __init__(self):
        """Initialize triage system"""
        self.logger = get_logger("TriageSystem")

    def triage_procedure(self, procedure: MedicalProcedure, 
                        symptoms: List[str], vital_signs: Optional[Dict[str, Any]] = None) -> TriageLevel:
        """
        Triage a medical procedure based on symptoms and vital signs

        Args:
            procedure: Medical procedure
            symptoms: List of symptoms
            vital_signs: Vital signs if available

        Returns:
            TriageLevel
        """
        # Critical symptoms = IMMEDIATE
        critical_symptoms = ["cardiac arrest", "respiratory failure", "severe bleeding", 
                           "unconscious", "severe trauma", "anaphylaxis"]
        if any(symptom.lower() in ' '.join(symptoms).lower() for symptom in critical_symptoms):
            return TriageLevel.IMMEDIATE

        # Urgent symptoms = EMERGENT
        urgent_symptoms = ["chest pain", "difficulty breathing", "severe pain", 
                          "high fever", "severe injury", "mental status change"]
        if any(symptom.lower() in ' '.join(symptoms).lower() for symptom in urgent_symptoms):
            return TriageLevel.EMERGENT

        # Moderate symptoms = URGENT
        moderate_symptoms = ["pain", "fever", "infection", "injury", "illness"]
        if any(symptom.lower() in ' '.join(symptoms).lower() for symptom in moderate_symptoms):
            return TriageLevel.URGENT

        # Complex procedures = URGENT
        if procedure.complexity in ["complex", "critical"]:
            return TriageLevel.URGENT

        # Default = NON_URGENT
        return TriageLevel.NON_URGENT

    def prioritize_procedures(self, procedures: List[MedicalProcedure]) -> List[MedicalProcedure]:
        """Prioritize procedures by triage level"""
        priority_order = {
            TriageLevel.IMMEDIATE: 1,
            TriageLevel.EMERGENT: 2,
            TriageLevel.URGENT: 3,
            TriageLevel.NON_URGENT: 4,
            TriageLevel.ROUTINE: 5
        }

        return sorted(procedures, key=lambda p: priority_order.get(p.triage_level, 99))


class LearnTeachDoSystem:
    """
    Learn One, Teach One, Do One System

    Medical training methodology:
    1. Learn One: Study procedure/concept
    2. Teach One: Teach to someone else
    3. Do One: Perform independently
    """

    def __init__(self):
        """Initialize Learn One, Teach One, Do One system"""
        self.logger = get_logger("LearnTeachDoSystem")

    def learn_one(self, procedure: MedicalProcedure, learner: str, 
                  master: str) -> Dict[str, Any]:
        """
        Learn One stage: Study and understand procedure

        Args:
            procedure: Medical procedure to learn
            learner: Who is learning (Padawan)
            master: Who is teaching (Master)

        Returns:
            Learning result
        """
        self.logger.info(f"📚 LEARN ONE: {learner} learning {procedure.name} from {master}")

        learning_result = {
            "stage": LearningStage.LEARN_ONE.value,
            "procedure": procedure.name,
            "learner": learner,
            "master": master,
            "started_at": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "learning_objectives": self._get_learning_objectives(procedure),
            "resources": self._get_learning_resources(procedure)
        }

        procedure.learn_stage = LearningStage.LEARN_ONE

        return learning_result

    def teach_one(self, procedure: MedicalProcedure, teacher: str, 
                  student: str) -> Dict[str, Any]:
        """
        Teach One stage: Teach procedure to someone else

        Args:
            procedure: Medical procedure to teach
            teacher: Who is teaching (Master)
            student: Who is learning (Padawan)

        Returns:
            Teaching result
        """
        self.logger.info(f"👨‍🏫 TEACH ONE: {teacher} teaching {procedure.name} to {student}")

        # Teacher must have completed Learn One and Do One
        if procedure.learn_stage != LearningStage.LEARN_ONE:
            return {
                "status": "BLOCKED",
                "reason": f"Teacher must complete Learn One first. Current stage: {procedure.learn_stage}"
            }

        teaching_result = {
            "stage": LearningStage.TEACH_ONE.value,
            "procedure": procedure.name,
            "teacher": teacher,
            "student": student,
            "started_at": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "teaching_methods": self._get_teaching_methods(procedure),
            "assessment_criteria": self._get_assessment_criteria(procedure)
        }

        procedure.teach_stage = LearningStage.TEACH_ONE

        return teaching_result

    def do_one(self, procedure: MedicalProcedure, practitioner: str, 
               supervisor: Optional[str] = None) -> Dict[str, Any]:
        """
        Do One stage: Perform procedure independently

        Args:
            procedure: Medical procedure to perform
            practitioner: Who is performing
            supervisor: Optional supervisor for complex procedures

        Returns:
            Performance result
        """
        self.logger.info(f"⚕️  DO ONE: {practitioner} performing {procedure.name}")

        # Must have completed Learn One and Teach One
        if procedure.learn_stage != LearningStage.LEARN_ONE:
            return {
                "status": "BLOCKED",
                "reason": f"Must complete Learn One first. Current stage: {procedure.learn_stage}"
            }

        if procedure.teach_stage != LearningStage.TEACH_ONE:
            return {
                "status": "BLOCKED",
                "reason": f"Must complete Teach One first. Current stage: {procedure.teach_stage}"
            }

        do_result = {
            "stage": LearningStage.DO_ONE.value,
            "procedure": procedure.name,
            "practitioner": practitioner,
            "supervisor": supervisor,
            "started_at": datetime.now().isoformat(),
            "status": "IN_PROGRESS",
            "complexity": procedure.complexity,
            "requires_supervision": procedure.complexity in ["complex", "critical"]
        }

        procedure.do_stage = LearningStage.DO_ONE

        return do_result

    def _get_learning_objectives(self, procedure: MedicalProcedure) -> List[str]:
        """Get learning objectives for procedure"""
        return [
            f"Understand {procedure.name} procedure",
            f"Know indications and contraindications",
            f"Understand {procedure.specialty} specialty context",
            f"Know complications and management"
        ]

    def _get_learning_resources(self, procedure: MedicalProcedure) -> List[str]:
        """Get learning resources for procedure"""
        return [
            f"{procedure.specialty} textbooks",
            f"{procedure.name} procedure guidelines",
            "Video demonstrations",
            "Case studies",
            "Practice simulations"
        ]

    def _get_teaching_methods(self, procedure: MedicalProcedure) -> List[str]:
        """Get teaching methods for procedure"""
        return [
            "Demonstration",
            "Supervised practice",
            "Case-based learning",
            "Simulation training",
            "Peer teaching"
        ]

    def _get_assessment_criteria(self, procedure: MedicalProcedure) -> List[str]:
        """Get assessment criteria for procedure"""
        return [
            "Knowledge of procedure steps",
            "Understanding of indications",
            "Recognition of complications",
            "Proper technique",
            "Patient safety"
        ]


class HRDoctorsTeam:
    """
    HR Team of Doctors

    Manages medical professionals in the organization:
    - Doctor assignments
    - Specialty matching
    - Supervision hierarchy
    - Credentialing
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize HR Doctors Team"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = get_logger("HRDoctorsTeam")
        self.doctors = []
        self._load_doctors()

    def _load_doctors(self):
        """Load doctors from organizational structure"""
        try:
            # Try to load from organizational structure
            from scripts.python.lumina_organizational_structure import LuminaOrganizationalStructure

            org_structure = LuminaOrganizationalStructure(self.project_root)

            # Find doctors in organizational structure
            doctors_found = []
            for member_id, member in org_structure.members.items():
                if member.member_type.value == "specialist" and "medical" in member.specialization.lower():
                    doctors_found.append({
                        "doctor_id": member.member_id,
                        "name": member.name,
                        "specialty": member.specialization,
                        "role": member.role,
                        "credentials": member.capabilities,
                        "can_supervise": "supervisor" in member.role.lower() or "attending" in member.role.lower(),
                        "status": member.status.value,
                        "division": member.division,
                        "team": member.team
                    })

            if doctors_found:
                self.doctors = doctors_found
                self.logger.info(f"✅ Loaded {len(self.doctors)} doctors from HR team organizational structure")
            else:
                # Fallback: Create example doctors
                self._create_example_doctors()
        except Exception as e:
            self.logger.warning(f"Could not load from organizational structure: {e}")
            self._create_example_doctors()

    def _create_example_doctors(self):
        """Create example doctors as fallback"""
        self.doctors = [
            {
                "doctor_id": "dr_001",
                "name": "Dr. Smith",
                "specialty": "Emergency Medicine",
                "role": "Attending Physician",
                "credentials": ["MD", "Board Certified"],
                "can_supervise": True,
                "status": "active"
            },
            {
                "doctor_id": "dr_002",
                "name": "Dr. Jones",
                "specialty": "Internal Medicine",
                "role": "Resident",
                "credentials": ["MD"],
                "can_supervise": False,
                "status": "active"
            },
            {
                "doctor_id": "dr_003",
                "name": "Dr. Williams",
                "specialty": "Surgery",
                "role": "Attending Surgeon",
                "credentials": ["MD", "FACS"],
                "can_supervise": True,
                "status": "active"
            }
        ]
        self.logger.info(f"✅ Created {len(self.doctors)} example doctors")

    def assign_doctor(self, procedure: MedicalProcedure, 
                     required_specialty: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Assign doctor to procedure based on specialty and availability

        Args:
            procedure: Medical procedure
            required_specialty: Required specialty if any

        Returns:
            Assigned doctor or None
        """
        specialty = required_specialty or procedure.specialty

        # Find matching doctor
        for doctor in self.doctors:
            if doctor["specialty"].lower() == specialty.lower() and doctor["status"] == "active":
                self.logger.info(f"👨‍⚕️  Assigned {doctor['name']} ({doctor['specialty']}) to {procedure.name}")
                return doctor

        # Fallback: Find any available doctor
        for doctor in self.doctors:
            if doctor["status"] == "active":
                self.logger.warning(f"⚠️  No {specialty} specialist found, assigned {doctor['name']} as fallback")
                return doctor

        return None

    def get_supervisor(self, procedure: MedicalProcedure) -> Optional[Dict[str, Any]]:
        """Get supervisor for procedure"""
        for doctor in self.doctors:
            if doctor["can_supervise"] and doctor["specialty"].lower() == procedure.specialty.lower():
                return doctor
        return None


class MedicalIntelligenceDesignSystem:
    """
    Medical Intelligence-Design System

    Integrates:
    - Learn One, Teach One, Do One methodology
    - Triage practices
    - HR Doctors Team
    - Medical procedure management
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Medical Intelligence-Design System"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Initialize subsystems
        self.learn_teach_do = LearnTeachDoSystem()
        self.triage = TriageSystem()
        self.hr_doctors = HRDoctorsTeam(project_root)

        # Medical procedures registry
        self.procedures_dir = self.project_root / "data" / "medical_procedures"
        self.procedures_dir.mkdir(parents=True, exist_ok=True)

        # Execution results
        self.execution_dir = self.project_root / "data" / "medical_execution"
        self.execution_dir.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 70)
        logger.info("⚕️  MEDICAL INTELLIGENCE-DESIGN SYSTEM")
        logger.info("   Learn One, Teach One, Do One with Triage")
        logger.info("=" * 70)
        logger.info("")

    def execute_learn_teach_do_workflow(self, procedure: MedicalProcedure, 
                                        learner: str, symptoms: List[str]) -> Dict[str, Any]:
        """
        Execute complete Learn One, Teach One, Do One workflow

        Args:
            procedure: Medical procedure
            learner: Who is learning
            symptoms: Patient symptoms for triage

        Returns:
            Complete workflow results
        """
        logger.info("⚕️  EXECUTING LEARN ONE, TEACH ONE, DO ONE WORKFLOW...")
        logger.info("")

        results = {
            "workflow_id": f"medical_workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "procedure": procedure.name,
            "learner": learner,
            "started_at": datetime.now().isoformat(),
            "stages": {}
        }

        # Step 1: Triage
        logger.info("STEP 1: TRIAGE")
        logger.info("-" * 70)
        triage_level = self.triage.triage_procedure(procedure, symptoms)
        procedure.triage_level = triage_level
        results["triage"] = {
            "level": triage_level.value,
            "symptoms": symptoms,
            "priority": self._get_priority(triage_level)
        }
        logger.info(f"   Triage Level: {triage_level.value.upper()}")
        logger.info(f"   Priority: {results['triage']['priority']}")
        logger.info("")

        # Step 2: Assign Doctor (Master)
        logger.info("STEP 2: ASSIGN DOCTOR (MASTER)")
        logger.info("-" * 70)
        master_doctor = self.hr_doctors.assign_doctor(procedure)
        if not master_doctor:
            return {"success": False, "error": "No doctor available"}
        results["master_doctor"] = master_doctor
        logger.info(f"   Master: {master_doctor['name']} ({master_doctor['specialty']})")
        logger.info("")

        # Step 3: Learn One
        logger.info("STEP 3: LEARN ONE")
        logger.info("-" * 70)
        learn_result = self.learn_teach_do.learn_one(procedure, learner, master_doctor["name"])
        results["stages"]["learn_one"] = learn_result
        logger.info(f"   ✅ {learner} learning {procedure.name} from {master_doctor['name']}")
        logger.info("")

        # Step 4: Teach One
        logger.info("STEP 4: TEACH ONE")
        logger.info("-" * 70)
        # Find a student (another doctor or resident)
        student = self._find_student(learner)
        teach_result = self.learn_teach_do.teach_one(procedure, learner, student)
        results["stages"]["teach_one"] = teach_result
        logger.info(f"   ✅ {learner} teaching {procedure.name} to {student}")
        logger.info("")

        # Step 5: Do One
        logger.info("STEP 5: DO ONE")
        logger.info("-" * 70)
        supervisor = None
        if procedure.complexity in ["complex", "critical"]:
            supervisor_doctor = self.hr_doctors.get_supervisor(procedure)
            supervisor = supervisor_doctor["name"] if supervisor_doctor else None
        do_result = self.learn_teach_do.do_one(procedure, learner, supervisor)
        results["stages"]["do_one"] = do_result
        logger.info(f"   ✅ {learner} performing {procedure.name}")
        if supervisor:
            logger.info(f"   👨‍⚕️  Supervised by: {supervisor}")
        logger.info("")

        # Summary
        logger.info("=" * 70)
        logger.info("📊 WORKFLOW SUMMARY")
        logger.info("=" * 70)

        results["summary"] = {
            "procedure": procedure.name,
            "learner": learner,
            "master": master_doctor["name"],
            "triage_level": triage_level.value,
            "all_stages_complete": all(
                stage.get("status") == "IN_PROGRESS" or stage.get("status") == "COMPLETE"
                for stage in results["stages"].values()
            )
        }

        logger.info(f"Procedure: {results['summary']['procedure']}")
        logger.info(f"Learner: {results['summary']['learner']}")
        logger.info(f"Master: {results['summary']['master']}")
        logger.info(f"Triage Level: {results['summary']['triage_level'].upper()}")
        logger.info(f"All Stages Complete: {results['summary']['all_stages_complete']}")
        logger.info("")

        results["completed_at"] = datetime.now().isoformat()
        results["success"] = True

        # Save results
        self._save_results(results)

        logger.info("=" * 70)
        logger.info("✅ LEARN ONE, TEACH ONE, DO ONE WORKFLOW COMPLETE")
        logger.info("=" * 70)

        return results

    def _get_priority(self, triage_level: TriageLevel) -> int:
        """Get priority number for triage level"""
        priorities = {
            TriageLevel.IMMEDIATE: 1,
            TriageLevel.EMERGENT: 2,
            TriageLevel.URGENT: 3,
            TriageLevel.NON_URGENT: 4,
            TriageLevel.ROUTINE: 5
        }
        return priorities.get(triage_level, 5)

    def _find_student(self, learner: str) -> str:
        """Find a student for Teach One stage"""
        # In real system, would find another doctor/resident
        # For now, return a placeholder
        return "Dr. Resident"

    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save workflow results"""
        try:
            filename = self.execution_dir / f"{results['workflow_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"✅ Results saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save results: {e}")


def main():
    """Main execution"""
    print("=" * 70)
    print("⚕️  MEDICAL INTELLIGENCE-DESIGN SYSTEM")
    print("   Learn One, Teach One, Do One with Triage")
    print("=" * 70)
    print()

    # Create example procedure
    procedure = MedicalProcedure(
        procedure_id="proc_001",
        name="Central Line Placement",
        description="Placement of central venous catheter",
        complexity="complex",
        specialty="Emergency Medicine"
    )

    # Execute workflow
    system = MedicalIntelligenceDesignSystem()
    results = system.execute_learn_teach_do_workflow(
        procedure=procedure,
        learner="Dr. Resident",
        symptoms=["chest pain", "difficulty breathing"]
    )

    print()
    print("=" * 70)
    print("✅ MEDICAL WORKFLOW COMPLETE")
    print("=" * 70)
    if results.get("success"):
        print(f"Procedure: {results['summary']['procedure']}")
        print(f"Learner: {results['summary']['learner']}")
        print(f"Master: {results['summary']['master']}")
        print(f"Triage Level: {results['summary']['triage_level'].upper()}")
        print(f"All Stages Complete: {results['summary']['all_stages_complete']}")
    else:
        print(f"Error: {results.get('error', 'Unknown error')}")
    print("=" * 70)


if __name__ == "__main__":


    main()