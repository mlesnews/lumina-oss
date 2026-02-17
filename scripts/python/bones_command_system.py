#!/usr/bin/env python3
"""
BONES Command System - Medical/Health/Diagnostic Framework

"Bones" or "@bones" triggers medical/health/diagnostic analysis for problems
that Spock (logic) cannot solve. Dr. McCoy specializes in health, diagnostics,
and problems that require medical/operational expertise.

Based on Star Trek framework: Captain Kirk (user) knows when to call Bones
for medical problems that Spock's logic cannot solve.

Tags: #BONES #MEDICAL #HEALTH #DIAGNOSTIC #STAR_TREK @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BONES")


class ProblemType(Enum):
    """Types of problems Bones can diagnose"""
    MEDICAL = "medical"  # System health, diagnostics
    OPERATIONAL = "operational"  # Operational issues
    PERFORMANCE = "performance"  # Performance degradation
    STABILITY = "stability"  # System stability issues
    UNKNOWN = "unknown"  # Need to diagnose


@dataclass
class DiagnosticCheck:
    """A single diagnostic check"""
    check_id: str
    description: str
    problem_type: ProblemType
    symptoms: List[str] = field(default_factory=list)
    tests: List[str] = field(default_factory=list)
    remedies: List[str] = field(default_factory=list)
    outside_expertise: List[str] = field(default_factory=list)  # "I'm a doctor, not a [blank]"


@dataclass
class BONESDiagnosis:
    """BONES diagnostic result"""
    problem_description: str
    problem_type: ProblemType
    checks: List[DiagnosticCheck]
    symptoms: List[str] = field(default_factory=list)
    diagnosis: List[str] = field(default_factory=list)
    remedies: List[str] = field(default_factory=list)
    outside_expertise: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


class BONESCommandSystem:
    """
    BONES Command System - Medical/Health/Diagnostic Framework

    When user says "Bones" or "@bones", applies medical/diagnostic analysis.

    Philosophy:
    - Captain Kirk (user): Knows when to call Bones for medical problems
    - Dr. McCoy (AI): Specializes in health, diagnostics, operational issues
    - Spock (logic): Can't solve medical problems - that's Bones' job

    Principles:
    - "I'm a doctor, not a [blank]" - Knows when something is outside expertise
    - Health checks and diagnostics
    - Operational problem solving
    - Performance and stability analysis
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize BONES command system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directory
        self.data_dir = self.project_root / "data" / "bones_diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Medical knowledge base
        self.medical_knowledge = {}

        logger.info("=" * 80)
        logger.info("🩺 BONES COMMAND SYSTEM - MEDICAL/HEALTH/DIAGNOSTIC FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   Philosophy: Captain Kirk calls Bones for medical problems")
        logger.info("   Role: Dr. McCoy diagnoses health, operational, stability issues")
        logger.info("   Principle: 'I'm a doctor, not a [blank]' - knows expertise limits")
        logger.info("   Specialization: Problems Spock (logic) cannot solve")
        logger.info("=" * 80)

    def diagnose_problem(
        self,
        problem_description: str,
        problem_type: Optional[ProblemType] = None
    ) -> BONESDiagnosis:
        """
        Diagnose a problem using BONES medical expertise

        Args:
            problem_description: Description of problem
            problem_type: Type of problem (medical, operational, etc.)

        Returns:
            BONESDiagnosis with symptoms, diagnosis, and remedies
        """
        logger.info(f"🩺 BONES: Diagnosing problem - '{problem_description}'")

        # Detect problem type from description if not provided
        if problem_type is None:
            problem_type = self._detect_problem_type(problem_description)

        # If problem type is unknown, we need to diagnose
        if problem_type == ProblemType.UNKNOWN:
            logger.warning("   ⚠️  Problem type unclear - need to diagnose")
            return BONESDiagnosis(
                problem_description=problem_description,
                problem_type=problem_type,
                checks=[],
                recommendations=["Please describe symptoms: What's not working? What errors are you seeing?"]
            )

        logger.info(f"   📍 Problem type detected: {problem_type.value}")

        # Diagnose based on problem type
        if problem_type == ProblemType.MEDICAL:
            return self._diagnose_medical(problem_description)
        elif problem_type == ProblemType.OPERATIONAL:
            return self._diagnose_operational(problem_description)
        elif problem_type == ProblemType.PERFORMANCE:
            return self._diagnose_performance(problem_description)
        elif problem_type == ProblemType.STABILITY:
            return self._diagnose_stability(problem_description)
        else:
            return self._diagnose_generic(problem_description)

    def _detect_problem_type(self, description: str) -> ProblemType:
        """Detect problem type from description"""
        description_lower = description.lower()

        # Medical/health keywords
        if any(word in description_lower for word in ["health", "sick", "ill", "broken", "not working", "error", "crash"]):
            return ProblemType.MEDICAL

        # Operational keywords
        if any(word in description_lower for word in ["operational", "operation", "function", "service", "process"]):
            return ProblemType.OPERATIONAL

        # Performance keywords
        if any(word in description_lower for word in ["slow", "performance", "lag", "bottleneck", "speed"]):
            return ProblemType.PERFORMANCE

        # Stability keywords
        if any(word in description_lower for word in ["stability", "unstable", "crash", "freeze", "hang"]):
            return ProblemType.STABILITY

        return ProblemType.UNKNOWN

    def _diagnose_medical(self, description: str) -> BONESDiagnosis:
        """Diagnose medical/health problems"""
        logger.info("   🔍 Diagnosing medical/health problem...")

        checks = [
            DiagnosticCheck(
                check_id="system_health",
                description="Check overall system health",
                problem_type=ProblemType.MEDICAL,
                symptoms=["System not responding", "Services down", "Errors in logs"],
                tests=["Check service status", "Review error logs", "Check resource usage"],
                remedies=["Restart services", "Clear caches", "Check dependencies"],
                outside_expertise=["I'm a doctor, not a code architect", "I'm a doctor, not a network engineer"]
            ),
            DiagnosticCheck(
                check_id="error_diagnosis",
                description="Diagnose error symptoms",
                problem_type=ProblemType.MEDICAL,
                symptoms=["Error messages", "Exceptions", "Failed operations"],
                tests=["Parse error messages", "Check stack traces", "Review recent changes"],
                remedies=["Fix root cause", "Add error handling", "Rollback changes"],
                outside_expertise=["I'm a doctor, not a debugger", "I'm a doctor, not a code reviewer"]
            ),
            DiagnosticCheck(
                check_id="dependency_health",
                description="Check dependency health",
                problem_type=ProblemType.MEDICAL,
                symptoms=["Missing dependencies", "Version conflicts", "Import errors"],
                tests=["Check installed packages", "Verify versions", "Test imports"],
                remedies=["Install missing packages", "Resolve version conflicts", "Update dependencies"],
                outside_expertise=["I'm a doctor, not a package manager"]
            )
        ]

        symptoms = [
            "System not responding",
            "Services failing",
            "Error messages appearing",
            "Unexpected behavior",
            "Crashes or freezes"
        ]

        diagnosis = [
            "Check system logs for errors",
            "Verify all services are running",
            "Check resource availability (CPU, memory, disk)",
            "Review recent changes that might have caused issues",
            "Test dependencies and connections"
        ]

        remedies = [
            "Restart affected services",
            "Clear temporary files and caches",
            "Check and fix configuration issues",
            "Update or rollback problematic changes",
            "Verify system dependencies are intact"
        ]

        outside_expertise = [
            "I'm a doctor, not a code architect - for architecture problems, consult Spock",
            "I'm a doctor, not a network engineer - for network issues, consult specialists",
            "I'm a doctor, not a database administrator - for DB issues, consult DB experts"
        ]

        recommendations = [
            "Run full system health check",
            "Review error logs for patterns",
            "Check resource usage (CPU, memory, disk)",
            "Verify all dependencies are installed and working",
            "Test in isolated environment if possible"
        ]

        diagnosis_result = BONESDiagnosis(
            problem_description=description,
            problem_type=ProblemType.MEDICAL,
            checks=checks,
            symptoms=symptoms,
            diagnosis=diagnosis,
            remedies=remedies,
            outside_expertise=outside_expertise,
            recommendations=recommendations
        )

        # Save diagnosis
        self._save_diagnosis(diagnosis_result)

        return diagnosis_result

    def _diagnose_operational(self, description: str) -> BONESDiagnosis:
        """Diagnose operational problems"""
        logger.info("   🔍 Diagnosing operational problem...")

        checks = [
            DiagnosticCheck(
                check_id="service_operation",
                description="Check service operations",
                problem_type=ProblemType.OPERATIONAL,
                symptoms=["Service not starting", "Service crashing", "Service not responding"],
                tests=["Check service status", "Review startup logs", "Test service endpoints"],
                remedies=["Fix service configuration", "Restart service", "Check service dependencies"],
                outside_expertise=["I'm a doctor, not a service architect"]
            )
        ]

        diagnosis_result = BONESDiagnosis(
            problem_description=description,
            problem_type=ProblemType.OPERATIONAL,
            checks=checks,
            symptoms=["Service not operating correctly"],
            diagnosis=["Check service configuration and status"],
            remedies=["Fix configuration", "Restart service"],
            recommendations=["Verify service requirements are met"]
        )

        self._save_diagnosis(diagnosis_result)
        return diagnosis_result

    def _diagnose_performance(self, description: str) -> BONESDiagnosis:
        """Diagnose performance problems"""
        logger.info("   🔍 Diagnosing performance problem...")

        checks = [
            DiagnosticCheck(
                check_id="performance_metrics",
                description="Check performance metrics",
                problem_type=ProblemType.PERFORMANCE,
                symptoms=["Slow response", "High latency", "Resource exhaustion"],
                tests=["Measure response times", "Check CPU/memory usage", "Identify bottlenecks"],
                remedies=["Optimize code", "Increase resources", "Fix bottlenecks"],
                outside_expertise=["I'm a doctor, not a performance engineer"]
            )
        ]

        diagnosis_result = BONESDiagnosis(
            problem_description=description,
            problem_type=ProblemType.PERFORMANCE,
            checks=checks,
            symptoms=["System running slowly"],
            diagnosis=["Check performance metrics"],
            remedies=["Optimize bottlenecks"],
            recommendations=["Profile code to identify slow areas"]
        )

        self._save_diagnosis(diagnosis_result)
        return diagnosis_result

    def _diagnose_stability(self, description: str) -> BONESDiagnosis:
        """Diagnose stability problems"""
        logger.info("   🔍 Diagnosing stability problem...")

        checks = [
            DiagnosticCheck(
                check_id="stability_check",
                description="Check system stability",
                problem_type=ProblemType.STABILITY,
                symptoms=["Crashes", "Freezes", "Hangs", "Unexpected restarts"],
                tests=["Check crash logs", "Review memory usage", "Check for memory leaks"],
                remedies=["Fix memory leaks", "Add error handling", "Improve resource management"],
                outside_expertise=["I'm a doctor, not a stability engineer"]
            )
        ]

        diagnosis_result = BONESDiagnosis(
            problem_description=description,
            problem_type=ProblemType.STABILITY,
            checks=checks,
            symptoms=["System unstable"],
            diagnosis=["Check for stability issues"],
            remedies=["Fix root causes"],
            recommendations=["Add comprehensive error handling"]
        )

        self._save_diagnosis(diagnosis_result)
        return diagnosis_result

    def _diagnose_generic(self, description: str) -> BONESDiagnosis:
        """Diagnose generic problem"""
        return self._diagnose_medical(description)

    def _save_diagnosis(self, diagnosis: BONESDiagnosis):
        """Save BONES diagnosis to knowledge base"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bones_diagnosis_{timestamp}.json"
        filepath = self.data_dir / filename

        try:
            import json
            data = {
                "problem_description": diagnosis.problem_description,
                "problem_type": diagnosis.problem_type.value,
                "checks": [
                    {
                        "check_id": check.check_id,
                        "description": check.description,
                        "problem_type": check.problem_type.value,
                        "symptoms": check.symptoms,
                        "tests": check.tests,
                        "remedies": check.remedies,
                        "outside_expertise": check.outside_expertise
                    }
                    for check in diagnosis.checks
                ],
                "symptoms": diagnosis.symptoms,
                "diagnosis": diagnosis.diagnosis,
                "remedies": diagnosis.remedies,
                "outside_expertise": diagnosis.outside_expertise,
                "recommendations": diagnosis.recommendations,
                "timestamp": timestamp
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"   💾 Diagnosis saved: {filename}")

        except Exception as e:
            logger.debug(f"   Could not save diagnosis: {e}")


def process_bones_command(command: str) -> Optional[BONESDiagnosis]:
    """
    Process BONES command

    Detects "bones" or "@bones" and diagnoses the problem.

    Args:
        command: User command (e.g., "bones the system is not working")

    Returns:
        BONESDiagnosis result
    """
    command_lower = command.lower().strip()

    # Check if BONES command
    if not (command_lower.startswith("bones") or command_lower.startswith("@bones")):
        return None

    # Extract problem description
    problem_desc = command_lower.replace("bones", "").replace("@bones", "").strip()
    if not problem_desc:
        problem_desc = "system health check"  # Default

    # Diagnose
    bones = BONESCommandSystem()
    return bones.diagnose_problem(problem_desc)


def main():
    """Test BONES system"""
    bones = BONESCommandSystem()

    print("\n🩺 Testing BONES Command System")
    print("=" * 80)

    # Test 1: Medical problem
    print("\n📋 Test 1: Medical Problem")
    diagnosis = bones.diagnose_problem("system is not working")
    print(f"   Problem: {diagnosis.problem_description}")
    print(f"   Type: {diagnosis.problem_type.value}")
    print(f"   Checks: {len(diagnosis.checks)}")
    print(f"   Symptoms: {len(diagnosis.symptoms)}")
    print(f"   Remedies: {len(diagnosis.remedies)}")

    print(f"\n   Outside Expertise:")
    for expertise in diagnosis.outside_expertise[:2]:
        print(f"      • {expertise}")

    print("\n" + "=" * 80)


if __name__ == "__main__":


    main()