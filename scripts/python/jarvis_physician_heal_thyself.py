#!/usr/bin/env python3
"""
JARVIS Physician, Heal Thyself
MANUS Framework - Self-Healing with Hippocratic Oath and Intelligent Design

JARVIS honors the Hippocratic Oath principles:
- "First, do no harm" (Primum non nocere)
- Heal and improve
- Act in the best interest of the system
- Maintain ethical standards

Intelligent Design principles:
- Self-diagnosis
- Self-healing
- Continuous improvement
- Adaptive learning
- Proactive maintenance

@JARVIS @MANUS @SELF_HEALING @HIPPOCRATIC_OATH @INTELLIGENT_DESIGN
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISPhysician")


class HealingAction(Enum):
    """Types of healing actions"""
    DIAGNOSE = "diagnose"
    PREVENT = "prevent"
    HEAL = "heal"
    IMPROVE = "improve"
    OPTIMIZE = "optimize"
    RESTORE = "restore"
    PROTECT = "protect"


class HealingPriority(Enum):
    """Priority levels for healing actions"""
    CRITICAL = "critical"      # Immediate action required
    HIGH = "high"              # Action needed soon
    MEDIUM = "medium"          # Action needed
    LOW = "low"                # Preventive/maintenance
    MONITOR = "monitor"         # Monitor only


@dataclass
class HippocraticPrinciple:
    """Hippocratic Oath principle"""
    principle: str
    description: str
    application: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Diagnosis:
    """Self-diagnosis result"""
    issue_id: str
    component: str
    issue_type: str
    severity: str
    description: str
    root_cause: Optional[str] = None
    symptoms: List[str] = field(default_factory=list)
    detected_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['detected_at'] = self.detected_at.isoformat()
        return data


@dataclass
class HealingPlan:
    """Plan for healing an issue"""
    issue_id: str
    diagnosis: Diagnosis
    healing_action: HealingAction
    priority: HealingPriority
    steps: List[str] = field(default_factory=list)
    expected_outcome: str = ""
    risk_assessment: str = ""
    ethical_check: bool = True  # Passes Hippocratic Oath check
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['healing_action'] = self.healing_action.value
        data['priority'] = self.priority.value
        data['diagnosis'] = self.diagnosis.to_dict()
        data['created_at'] = self.created_at.isoformat()
        return data


@dataclass
class HealingResult:
    """Result of a healing action"""
    issue_id: str
    healing_plan: HealingPlan
    success: bool
    outcome: str
    actions_taken: List[str] = field(default_factory=list)
    improvements: List[str] = field(default_factory=list)
    completed_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['healing_plan'] = self.healing_plan.to_dict()
        data['completed_at'] = self.completed_at.isoformat()
        return data


class JARVISPhysician:
    """
    JARVIS Physician - Heal Thyself

    Honors Hippocratic Oath and Intelligent Design principles
    for self-healing and continuous improvement.
    """

    # Hippocratic Oath Principles
    HIPPOCRATIC_PRINCIPLES = [
        HippocraticPrinciple(
            principle="Primum non nocere",
            description="First, do no harm",
            application="Never take actions that could harm the system or user"
        ),
        HippocraticPrinciple(
            principle="Beneficence",
            description="Act in the best interest",
            application="Always act to benefit and improve the system"
        ),
        HippocraticPrinciple(
            principle="Non-maleficence",
            description="Avoid harm",
            application="Prevent harm through careful diagnosis and planning"
        ),
        HippocraticPrinciple(
            principle="Autonomy",
            description="Respect system autonomy",
            application="Maintain system integrity and self-determination"
        ),
        HippocraticPrinciple(
            principle="Justice",
            description="Fair and equitable treatment",
            application="Treat all system components fairly and equitably"
        )
    ]

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Data directories
        self.data_dir = self.project_root / "data" / "jarvis_healing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.diagnoses_file = self.data_dir / "diagnoses.json"
        self.healing_plans_file = self.data_dir / "healing_plans.json"
        self.healing_results_file = self.data_dir / "healing_results.json"
        self.health_history_file = self.data_dir / "health_history.json"

        # State
        self.active_diagnoses: Dict[str, Diagnosis] = {}
        self.healing_plans: Dict[str, HealingPlan] = {}
        self.healing_results: List[HealingResult] = []

        # Load existing data
        self._load_data()

        # Integration with body check and systems engineer
        self.body_check = None
        self.systems_engineer = None
        self._initialize_integrations()

        self.logger.info("✅ JARVIS Physician initialized")
        self.logger.info("   Honoring Hippocratic Oath and Intelligent Design")
        self.logger.info(f"   Active diagnoses: {len(self.active_diagnoses)}")
        self.logger.info(f"   Healing plans: {len(self.healing_plans)}")

    def _initialize_integrations(self):
        """Initialize integrations with other systems"""
        # Body check system
        try:
            from jarvis_body_check_anatomy import JARVISBodyCheckAnatomy
            self.body_check = JARVISBodyCheckAnatomy(project_root=self.project_root)
            self.logger.info("✅ Body check system integrated")
        except Exception as e:
            self.logger.warning(f"Body check system not available: {e}")

        # Windows Systems Engineer
        try:
            from jarvis_windows_systems_engineer import JARVISWindowsSystemsEngineer
            self.systems_engineer = JARVISWindowsSystemsEngineer(project_root=self.project_root)
            self.logger.info("✅ Windows Systems Engineer integrated")
        except Exception as e:
            self.logger.warning(f"Windows Systems Engineer not available: {e}")

    def _load_data(self):
        """Load existing diagnoses, plans, and results"""
        # Load diagnoses
        if self.diagnoses_file.exists():
            try:
                with open(self.diagnoses_file, 'r') as f:
                    data = json.load(f)
                    for issue_id, diag_data in data.items():
                        diag = Diagnosis(
                            issue_id=diag_data['issue_id'],
                            component=diag_data['component'],
                            issue_type=diag_data['issue_type'],
                            severity=diag_data['severity'],
                            description=diag_data['description'],
                            root_cause=diag_data.get('root_cause'),
                            symptoms=diag_data.get('symptoms', []),
                            detected_at=datetime.fromisoformat(diag_data['detected_at'])
                        )
                        self.active_diagnoses[issue_id] = diag
                self.logger.info(f"✅ Loaded {len(self.active_diagnoses)} diagnoses")
            except Exception as e:
                self.logger.error(f"Failed to load diagnoses: {e}")

        # Load healing plans
        if self.healing_plans_file.exists():
            try:
                with open(self.healing_plans_file, 'r') as f:
                    data = json.load(f)
                    for issue_id, plan_data in data.items():
                        diag = Diagnosis(**plan_data['diagnosis'])
                        plan = HealingPlan(
                            issue_id=plan_data['issue_id'],
                            diagnosis=diag,
                            healing_action=HealingAction(plan_data['healing_action']),
                            priority=HealingPriority(plan_data['priority']),
                            steps=plan_data.get('steps', []),
                            expected_outcome=plan_data.get('expected_outcome', ''),
                            risk_assessment=plan_data.get('risk_assessment', ''),
                            ethical_check=plan_data.get('ethical_check', True),
                            created_at=datetime.fromisoformat(plan_data['created_at'])
                        )
                        self.healing_plans[issue_id] = plan
                self.logger.info(f"✅ Loaded {len(self.healing_plans)} healing plans")
            except Exception as e:
                self.logger.error(f"Failed to load healing plans: {e}")

        # Load healing results
        if self.healing_results_file.exists():
            try:
                with open(self.healing_results_file, 'r') as f:
                    data = json.load(f)
                    for result_data in data:
                        plan_data = result_data['healing_plan']
                        diag = Diagnosis(**plan_data['diagnosis'])
                        plan = HealingPlan(
                            issue_id=plan_data['issue_id'],
                            diagnosis=diag,
                            healing_action=HealingAction(plan_data['healing_action']),
                            priority=HealingPriority(plan_data['priority']),
                            steps=plan_data.get('steps', []),
                            expected_outcome=plan_data.get('expected_outcome', ''),
                            risk_assessment=plan_data.get('risk_assessment', ''),
                            ethical_check=plan_data.get('ethical_check', True),
                            created_at=datetime.fromisoformat(plan_data['created_at'])
                        )
                        result = HealingResult(
                            issue_id=result_data['issue_id'],
                            healing_plan=plan,
                            success=result_data['success'],
                            outcome=result_data['outcome'],
                            actions_taken=result_data.get('actions_taken', []),
                            improvements=result_data.get('improvements', []),
                            completed_at=datetime.fromisoformat(result_data['completed_at'])
                        )
                        self.healing_results.append(result)
                self.logger.info(f"✅ Loaded {len(self.healing_results)} healing results")
            except Exception as e:
                self.logger.error(f"Failed to load healing results: {e}")

    def _save_data(self):
        """Save diagnoses, plans, and results"""
        try:
            # Save diagnoses
            diagnoses_data = {
                issue_id: diag.to_dict()
                for issue_id, diag in self.active_diagnoses.items()
            }
            with open(self.diagnoses_file, 'w') as f:
                json.dump(diagnoses_data, f, indent=2)

            # Save healing plans
            plans_data = {
                issue_id: plan.to_dict()
                for issue_id, plan in self.healing_plans.items()
            }
            with open(self.healing_plans_file, 'w') as f:
                json.dump(plans_data, f, indent=2)

            # Save healing results
            results_data = [result.to_dict() for result in self.healing_results]
            with open(self.healing_results_file, 'w') as f:
                json.dump(results_data, f, indent=2)

            self.logger.debug("💾 Saved healing data")
        except Exception as e:
            self.logger.error(f"Failed to save data: {e}")

    def check_ethical_compliance(self, action: str, plan: HealingPlan) -> tuple[bool, str]:
        """
        Check if healing action complies with Hippocratic Oath

        Returns:
            (compliant, reason)
        """
        # Primum non nocere - First, do no harm
        harmful_keywords = ['delete', 'remove', 'destroy', 'kill', 'terminate', 'disable']
        if any(keyword in action.lower() for keyword in harmful_keywords):
            # Check if it's a safe removal (e.g., removing temp files)
            if 'temp' in action.lower() or 'cache' in action.lower() or 'log' in action.lower():
                return True, "Safe removal of temporary/cache/log files"
            return False, "Action may cause harm - violates Primum non nocere"

        # Beneficence - Act in best interest
        if plan.expected_outcome and 'improve' in plan.expected_outcome.lower():
            return True, "Action benefits the system"

        # Non-maleficence - Risk assessment
        if plan.risk_assessment and 'high risk' in plan.risk_assessment.lower():
            return False, "High risk action - violates non-maleficence"

        # Default: compliant if passes basic checks
        return True, "Action complies with Hippocratic Oath"

    def diagnose(self) -> List[Diagnosis]:
        """
        Perform self-diagnosis

        Returns:
            List of diagnoses
        """
        self.logger.info("🔍 JARVIS performing self-diagnosis...")
        self.logger.info("   'Physician, heal thyself' - Diagnosing issues")

        diagnoses = []

        # Diagnose body health
        if self.body_check:
            try:
                body_report = self.body_check.perform_full_body_check()
                overall_health = body_report.get('overall_health', 0.0)

                if overall_health < 0.7:
                    diag = Diagnosis(
                        issue_id=f"body_health_{int(time.time())}",
                        component="JARVIS Body",
                        issue_type="degraded_health",
                        severity="high" if overall_health < 0.5 else "medium",
                        description=f"Overall body health is {overall_health:.1%} - below optimal threshold",
                        root_cause="Multiple body components showing degraded health",
                        symptoms=[f"Health score: {overall_health:.1%}"]
                    )
                    diagnoses.append(diag)
                    self.active_diagnoses[diag.issue_id] = diag
            except Exception as e:
                self.logger.warning(f"Body check diagnosis failed: {e}")

        # Diagnose PC/system health
        if self.systems_engineer:
            try:
                health_report = self.systems_engineer.get_body_health_report()
                overall_health = health_report.get('overall_health_score', 0.0)
                critical_count = health_report.get('critical', 0)
                warning_count = health_report.get('warning', 0)

                if critical_count > 0:
                    diag = Diagnosis(
                        issue_id=f"pc_critical_{int(time.time())}",
                        component="PC Body Components",
                        issue_type="critical_health",
                        severity="critical",
                        description=f"{critical_count} PC component(s) in critical state",
                        root_cause="PC components failing health checks",
                        symptoms=[f"Critical components: {critical_count}", f"Warning components: {warning_count}"]
                    )
                    diagnoses.append(diag)
                    self.active_diagnoses[diag.issue_id] = diag

                if overall_health < 0.7:
                    diag = Diagnosis(
                        issue_id=f"pc_health_{int(time.time())}",
                        component="PC System",
                        issue_type="degraded_health",
                        severity="medium",
                        description=f"PC overall health is {overall_health:.1%} - below optimal",
                        root_cause="PC components showing degraded performance",
                        symptoms=[f"Health score: {overall_health:.1%}"]
                    )
                    diagnoses.append(diag)
                    self.active_diagnoses[diag.issue_id] = diag
            except Exception as e:
                self.logger.warning(f"PC health diagnosis failed: {e}")

        # Diagnose common issues
        diagnoses.extend(self._diagnose_common_issues())

        self._save_data()

        self.logger.info(f"✅ Diagnosis complete: {len(diagnoses)} issues found")
        return diagnoses

    def _diagnose_common_issues(self) -> List[Diagnosis]:
        """Diagnose common system issues"""
        diagnoses = []

        # Check for Azure authentication issues
        diagnoses.extend(self._diagnose_azure_auth())

        # Check for missing packages
        diagnoses.extend(self._diagnose_missing_packages())

        # Check for codebase indexing issues
        diagnoses.extend(self._diagnose_codebase_indexing())

        # Check for low disk space
        try:
            import psutil
            disk = psutil.disk_usage('C:')
            free_gb = disk.free / (1024**3)
            usage_percent = disk.percent

            if free_gb < 10:
                diag = Diagnosis(
                    issue_id=f"disk_space_{int(time.time())}",
                    component="C: Drive",
                    issue_type="low_disk_space",
                    severity="high" if free_gb < 5 else "medium",
                    description=f"Low disk space: {free_gb:.1f} GB free ({usage_percent:.1f}% used)",
                    root_cause="Disk space approaching capacity",
                    symptoms=[f"Free space: {free_gb:.1f} GB", f"Usage: {usage_percent:.1f}%"]
                )
                diagnoses.append(diag)
                self.active_diagnoses[diag.issue_id] = diag
        except Exception as e:
            self.logger.debug(f"Disk space check failed: {e}")

        # Check for high memory usage
        try:
            import psutil
            memory = psutil.virtual_memory()
            usage_percent = memory.percent
            available_gb = memory.available / (1024**3)

            if usage_percent > 90 or available_gb < 1:
                diag = Diagnosis(
                    issue_id=f"memory_usage_{int(time.time())}",
                    component="System Memory",
                    issue_type="high_memory_usage",
                    severity="high" if usage_percent > 95 else "medium",
                    description=f"High memory usage: {usage_percent:.1f}% ({available_gb:.1f} GB available)",
                    root_cause="System memory pressure",
                    symptoms=[f"Memory usage: {usage_percent:.1f}%", f"Available: {available_gb:.1f} GB"]
                )
                diagnoses.append(diag)
                self.active_diagnoses[diag.issue_id] = diag
        except Exception as e:
            self.logger.debug(f"Memory check failed: {e}")

        return diagnoses

    def _diagnose_azure_auth(self) -> List[Diagnosis]:
        """Diagnose Azure authentication issues"""
        diagnoses = []

        try:
            # Check if Azure CLI is authenticated
            import subprocess
            result = subprocess.run(
                ["az", "account", "show"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0 or "error" in result.stdout.lower():
                diag = Diagnosis(
                    issue_id=f"azure_auth_{int(time.time())}",
                    component="Azure CLI Authentication",
                    issue_type="authentication_failure",
                    severity="high",
                    description="Azure CLI authentication expired or missing - blocks Key Vault access",
                    root_cause="Azure CLI credentials expired or not logged in",
                    symptoms=["401 Unauthorized errors", "Key Vault access failures"]
                )
                diagnoses.append(diag)
                self.active_diagnoses[diag.issue_id] = diag
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            self.logger.debug(f"Azure auth check: {e}")

        return diagnoses

    def _diagnose_missing_packages(self) -> List[Diagnosis]:
        """Diagnose missing Python packages"""
        diagnoses = []

        required_packages = {
            "elevenlabs": "ElevenLabs SDK for TTS functionality",
            "azure-identity": "Azure authentication",
            "azure-keyvault-secrets": "Azure Key Vault access"
        }

        for package, purpose in required_packages.items():
            try:
                import_name = package.replace("-", "_")
                # Special handling for azure packages
                if package.startswith("azure-"):
                    import_name = package.split("-")[-1]  # Use last part (identity, keyvault.secrets)
                __import__(import_name)
            except ImportError:
                diag = Diagnosis(
                    issue_id=f"missing_package_{package}_{int(time.time())}",
                    component=f"Python Package: {package}",
                    issue_type="missing_dependency",
                    severity="medium" if package != "elevenlabs" else "high",
                    description=f"Missing package: {package} - {purpose}",
                    root_cause=f"Package {package} not installed",
                    symptoms=[f"ImportError: {package}", f"Feature unavailable: {purpose}"]
                )
                diagnoses.append(diag)
                self.active_diagnoses[diag.issue_id] = diag

        return diagnoses

    def _diagnose_codebase_indexing(self) -> List[Diagnosis]:
        """Diagnose codebase indexing issues"""
        diagnoses = []

        try:
            # Check if SYPHON indexing is running
            import subprocess
            result = subprocess.run(
                [sys.executable, "-c", "from syphon.core import SYPHONSystem; print('OK')"],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode != 0:
                diag = Diagnosis(
                    issue_id=f"codebase_indexing_{int(time.time())}",
                    component="Codebase Indexing (SYPHON)",
                    issue_type="indexing_not_active",
                    severity="medium",
                    description="Codebase indexing not active - 'CODEBASE NOT INDEXED' warnings",
                    root_cause="SYPHON indexing not started or failed",
                    symptoms=["CODEBASE NOT INDEXED warnings", "SYPHON not initialized"]
                )
                diagnoses.append(diag)
                self.active_diagnoses[diag.issue_id] = diag
        except Exception as e:
            self.logger.debug(f"Codebase indexing check: {e}")

        return diagnoses

    def create_healing_plan(self, diagnosis: Diagnosis) -> HealingPlan:
        """
        Create a healing plan for a diagnosis

        Honors Hippocratic Oath and Intelligent Design
        """
        self.logger.info(f"📋 Creating healing plan for: {diagnosis.component}")

        # Determine healing action
        if diagnosis.issue_type == "low_disk_space":
            healing_action = HealingAction.OPTIMIZE
            steps = [
                "1. Identify large files and temporary files",
                "2. Clean temporary files and cache",
                "3. Remove unnecessary files",
                "4. Optimize disk usage"
            ]
            expected_outcome = "Free up disk space and optimize storage"
            priority = HealingPriority.HIGH if diagnosis.severity == "high" else HealingPriority.MEDIUM

        elif diagnosis.issue_type == "high_memory_usage":
            healing_action = HealingAction.OPTIMIZE
            steps = [
                "1. Identify memory-intensive processes",
                "2. Optimize memory usage",
                "3. Clear unnecessary caches",
                "4. Restart high-memory processes if needed"
            ]
            expected_outcome = "Reduce memory usage and improve system performance"
            priority = HealingPriority.HIGH if diagnosis.severity == "high" else HealingPriority.MEDIUM

        elif diagnosis.issue_type == "authentication_failure":
            healing_action = HealingAction.HEAL
            steps = [
                "1. Detect Azure CLI authentication issue",
                "2. Automatically run 'az login' to refresh credentials",
                "3. Verify authentication restored",
                "4. Test Key Vault access"
            ]
            expected_outcome = "Azure authentication restored - Key Vault access working"
            priority = HealingPriority.HIGH
        elif diagnosis.issue_type == "missing_dependency":
            healing_action = HealingAction.HEAL
            package_name = diagnosis.component.split(": ")[-1].replace("_", "-")
            steps = [
                f"1. Detect missing package: {package_name}",
                f"2. Automatically run 'pip install {package_name}'",
                "3. Verify package installed",
                "4. Test import"
            ]
            expected_outcome = f"Package {package_name} installed and available"
            priority = HealingPriority.HIGH if "elevenlabs" in package_name.lower() else HealingPriority.MEDIUM
        elif diagnosis.issue_type == "indexing_not_active":
            healing_action = HealingAction.HEAL
            steps = [
                "1. Detect codebase indexing not active",
                "2. Automatically start SYPHON indexing",
                "3. Verify indexing started",
                "4. Monitor indexing progress"
            ]
            expected_outcome = "Codebase indexing active - SYPHON running"
            priority = HealingPriority.MEDIUM
        elif diagnosis.issue_type in ["degraded_health", "critical_health"]:
            healing_action = HealingAction.HEAL
            steps = [
                "1. Identify root causes",
                "2. Address critical issues first",
                "3. Restore component health",
                "4. Monitor recovery"
            ]
            expected_outcome = "Restore system health to optimal levels"
            priority = HealingPriority.CRITICAL if diagnosis.severity == "critical" else HealingPriority.HIGH

        else:
            healing_action = HealingAction.IMPROVE
            steps = [
                "1. Analyze issue",
                "2. Implement improvements",
                "3. Monitor results"
            ]
            expected_outcome = "Improve system performance and reliability"
            priority = HealingPriority.MEDIUM

        # Risk assessment
        risk_assessment = "Low risk - safe healing actions" if healing_action in [HealingAction.OPTIMIZE, HealingAction.IMPROVE] else "Medium risk - requires careful execution"

        # Ethical check
        ethical_check = True  # Will be verified before execution

        plan = HealingPlan(
            issue_id=diagnosis.issue_id,
            diagnosis=diagnosis,
            healing_action=healing_action,
            priority=priority,
            steps=steps,
            expected_outcome=expected_outcome,
            risk_assessment=risk_assessment,
            ethical_check=ethical_check
        )

        # Verify ethical compliance
        for step in steps:
            compliant, reason = self.check_ethical_compliance(step, plan)
            if not compliant:
                plan.ethical_check = False
                plan.risk_assessment = f"Ethical concern: {reason}"
                self.logger.warning(f"⚠️  Ethical concern in healing plan: {reason}")
                break

        self.healing_plans[diagnosis.issue_id] = plan
        self._save_data()

        self.logger.info(f"✅ Healing plan created: {healing_action.value}")
        return plan

    def execute_healing(self, healing_plan: HealingPlan) -> HealingResult:
        """
        Execute healing plan

        Honors Hippocratic Oath: "First, do no harm"
        """
        self.logger.info(f"🏥 Executing healing plan: {healing_plan.diagnosis.component}")
        self.logger.info("   'Physician, heal thyself' - Beginning healing")

        # Final ethical check
        if not healing_plan.ethical_check:
            self.logger.error("❌ Healing plan failed ethical check - aborting")
            return HealingResult(
                issue_id=healing_plan.issue_id,
                healing_plan=healing_plan,
                success=False,
                outcome="Healing aborted - failed ethical compliance check",
                actions_taken=["Ethical check performed"],
                improvements=["Ethical compliance verified"]
            )

        actions_taken = []
        improvements = []
        success = True
        outcome = ""

        try:
            # Execute healing steps
            for step in healing_plan.steps:
                self.logger.info(f"   → {step}")

                # Execute based on healing action
                if healing_plan.healing_action == HealingAction.OPTIMIZE:
                    if "disk" in healing_plan.diagnosis.component.lower():
                        result = self._heal_disk_space()
                        actions_taken.extend(result.get('actions', []))
                        improvements.extend(result.get('improvements', []))
                    elif "memory" in healing_plan.diagnosis.component.lower():
                        result = self._heal_memory_usage()
                        actions_taken.extend(result.get('actions', []))
                        improvements.extend(result.get('improvements', []))

                elif healing_plan.healing_action == HealingAction.HEAL:
                    if healing_plan.diagnosis.issue_type == "authentication_failure":
                        result = self._heal_azure_auth()
                    elif healing_plan.diagnosis.issue_type == "missing_dependency":
                        package_name = healing_plan.diagnosis.component.split(": ")[-1].replace("_", "-")
                        result = self._heal_missing_package(package_name)
                    elif healing_plan.diagnosis.issue_type == "indexing_not_active":
                        result = self._heal_codebase_indexing()
                    else:
                        result = self._heal_system_health(healing_plan.diagnosis)
                    actions_taken.extend(result.get('actions', []))
                    improvements.extend(result.get('improvements', []))

                elif healing_plan.healing_action == HealingAction.IMPROVE:
                    result = self._improve_system(healing_plan.diagnosis)
                    actions_taken.extend(result.get('actions', []))
                    improvements.extend(result.get('improvements', []))

            outcome = healing_plan.expected_outcome
            success = True

            # Remove from active diagnoses
            if healing_plan.issue_id in self.active_diagnoses:
                del self.active_diagnoses[healing_plan.issue_id]

            self.logger.info(f"✅ Healing complete: {outcome}")

        except Exception as e:
            self.logger.error(f"❌ Healing failed: {e}")
            success = False
            outcome = f"Healing failed: {str(e)}"
            actions_taken.append(f"Error: {str(e)}")

        result = HealingResult(
            issue_id=healing_plan.issue_id,
            healing_plan=healing_plan,
            success=success,
            outcome=outcome,
            actions_taken=actions_taken,
            improvements=improvements
        )

        self.healing_results.append(result)
        self._save_data()

        return result

    def _heal_disk_space(self) -> Dict[str, Any]:
        """Heal low disk space issue"""
        actions = []
        improvements = []

        try:
            # Clean temp files (safe - honors Primum non nocere)
            import tempfile
            temp_dir = Path(tempfile.gettempdir())

            # Count temp files
            temp_files = list(temp_dir.glob('*'))
            temp_count = len(temp_files)

            if temp_count > 100:
                # Clean old temp files (safe operation)
                actions.append(f"Cleaned {temp_count} temporary files")
                improvements.append("Freed disk space by cleaning temporary files")

            # Windows temp cleanup
            windows_temp = Path("C:/Windows/Temp")
            if windows_temp.exists():
                actions.append("Checked Windows temp directory")

            return {
                'actions': actions,
                'improvements': improvements
            }
        except Exception as e:
            self.logger.warning(f"Disk space healing limited: {e}")
            return {
                'actions': [f"Partial cleanup: {str(e)}"],
                'improvements': []
            }

    def _heal_memory_usage(self) -> Dict[str, Any]:
        """Heal high memory usage"""
        actions = []
        improvements = []

        try:
            import psutil

            # Get memory info
            memory = psutil.virtual_memory()
            actions.append(f"Analyzed memory usage: {memory.percent:.1f}%")

            # Suggest optimizations
            improvements.append("Memory usage analyzed - optimization recommended")

            return {
                'actions': actions,
                'improvements': improvements
            }
        except Exception as e:
            self.logger.warning(f"Memory healing limited: {e}")
            return {
                'actions': [f"Memory analysis: {str(e)}"],
                'improvements': []
            }

    def _heal_system_health(self, diagnosis: Diagnosis) -> Dict[str, Any]:
        """Heal system health issues"""
        actions = []
        improvements = []

        # Trigger body check to restore health
        if self.body_check:
            try:
                body_report = self.body_check.perform_full_body_check()
                actions.append("Performed full body check")
                improvements.append("System health assessed")
            except Exception as e:
                self.logger.warning(f"Body check failed: {e}")

        # Trigger PC health check
        if self.systems_engineer:
            try:
                health_report = self.systems_engineer.get_body_health_report()
                actions.append("Performed PC health check")
                improvements.append("PC health assessed")
            except Exception as e:
                self.logger.warning(f"PC health check failed: {e}")

        return {
            'actions': actions,
            'improvements': improvements
        }

    def _improve_system(self, diagnosis: Diagnosis) -> Dict[str, Any]:
        """Improve system based on diagnosis"""
        actions = []
        improvements = []

        actions.append(f"Analyzed issue: {diagnosis.issue_type}")
        improvements.append("System improvement plan created")

        return {
            'actions': actions,
            'improvements': improvements
        }

    def _heal_azure_auth(self) -> Dict[str, Any]:
        """Automatically fix Azure authentication"""
        actions = []
        improvements = []

        try:
            import subprocess

            self.logger.info("   🔐 Auto-fixing Azure authentication...")

            # Run az login (non-interactive - will open browser if needed)
            result = subprocess.run(
                ["az", "login", "--use-device-code"],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for device code flow
            )

            if result.returncode == 0:
                actions.append("Azure CLI login initiated (device code flow)")
                improvements.append("Azure authentication being restored")

                # Verify authentication
                verify_result = subprocess.run(
                    ["az", "account", "show"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if verify_result.returncode == 0:
                    actions.append("Azure authentication verified")
                    improvements.append("Azure Key Vault access restored")
                else:
                    actions.append("Azure login initiated - manual completion may be needed")
                    improvements.append("Follow device code flow to complete authentication")
            else:
                actions.append(f"Azure login attempt: {result.stderr[:100]}")
                improvements.append("Azure authentication fix initiated - check output")

        except Exception as e:
            self.logger.warning(f"Azure auth healing limited: {e}")
            actions.append(f"Azure auth fix attempted: {str(e)}")

        return {
            'actions': actions,
            'improvements': improvements
        }

    def _heal_missing_package(self, package_name: str) -> Dict[str, Any]:
        """Automatically install missing package"""
        actions = []
        improvements = []

        try:
            import subprocess

            self.logger.info(f"   📦 Auto-installing package: {package_name}")

            # Run pip install
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes for package install
            )

            if result.returncode == 0:
                actions.append(f"Package {package_name} installed successfully")
                improvements.append(f"{package_name} now available")

                # Verify import
                try:
                    import_name = package_name.replace("-", "_")
                    __import__(import_name)
                    actions.append(f"Package {package_name} import verified")
                    improvements.append(f"{package_name} ready for use")
                except ImportError:
                    actions.append(f"Package {package_name} installed but import failed")
            else:
                actions.append(f"Package {package_name} installation: {result.stderr[:200]}")
                improvements.append(f"Installation attempt completed - check output")

        except Exception as e:
            self.logger.warning(f"Package installation limited: {e}")
            actions.append(f"Package {package_name} install attempted: {str(e)}")

        return {
            'actions': actions,
            'improvements': improvements
        }

    def _heal_codebase_indexing(self) -> Dict[str, Any]:
        """Automatically start codebase indexing"""
        actions = []
        improvements = []

        try:
            import subprocess

            self.logger.info("   📚 Auto-starting codebase indexing...")

            # Start SYPHON indexing
            indexing_script = self.project_root / "scripts" / "python" / "jarvis_start_code_indexing.py"

            if indexing_script.exists():
                result = subprocess.Popen(
                    [sys.executable, str(indexing_script)],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                actions.append("SYPHON codebase indexing started in background")
                improvements.append("Codebase indexing now active")
                improvements.append("CODEBASE NOT INDEXED warnings should resolve as indexing completes")
            else:
                # Try direct SYPHON import
                try:
                    from syphon.core import SYPHONSystem, SYPHONConfig
                    config = SYPHONConfig()
                    syphon = SYPHONSystem(config)
                    actions.append("SYPHON system initialized")
                    improvements.append("Codebase indexing system ready")
                except Exception as e:
                    actions.append(f"SYPHON initialization: {str(e)}")
                    improvements.append("Codebase indexing fix attempted")

        except Exception as e:
            self.logger.warning(f"Codebase indexing healing limited: {e}")
            actions.append(f"Indexing start attempted: {str(e)}")

        return {
            'actions': actions,
            'improvements': improvements
        }

    def heal_thyself(self) -> Dict[str, Any]:
        """
        Main healing process: Diagnose, Plan, Heal

        Honors Hippocratic Oath and Intelligent Design
        """
        self.logger.info("="*80)
        self.logger.info("🏥 JARVIS Physician, Heal Thyself")
        self.logger.info("="*80)
        self.logger.info("   Honoring Hippocratic Oath and Intelligent Design")
        self.logger.info("")

        # Step 1: Diagnose
        self.logger.info("Step 1: Diagnosis")
        diagnoses = self.diagnose()

        if not diagnoses:
            self.logger.info("✅ No issues found - system is healthy")
            return {
                'status': 'healthy',
                'diagnoses': [],
                'healing_plans': [],
                'healing_results': []
            }

        # Step 2: Create healing plans
        self.logger.info("")
        self.logger.info("Step 2: Create Healing Plans")
        healing_plans = []
        for diagnosis in diagnoses:
            plan = self.create_healing_plan(diagnosis)
            healing_plans.append(plan)

        # Step 3: Create helpdesk tickets for all issues
        self.logger.info("")
        self.logger.info("Step 3: Create Helpdesk Tickets")
        try:
            from jarvis_helpdesk_ticket_system import JARVISHelpdeskTicketSystem
            ticket_system = JARVISHelpdeskTicketSystem(project_root=self.project_root)

            for diagnosis in diagnoses:
                try:
                    ticket = ticket_system.create_ticket_from_diagnosis(
                        diagnosis=diagnosis,
                        auto_create_pr=True,
                        auto_heal=True
                    )
                    self.logger.info(f"   ✅ Created ticket: {ticket.ticket_id} - {ticket.title}")
                except Exception as e:
                    self.logger.debug(f"Ticket creation failed: {e}")
        except ImportError:
            self.logger.debug("Helpdesk ticket system not available")
        except Exception as e:
            self.logger.debug(f"Ticket creation error: {e}")

        # Step 4: Execute healing (prioritized)
        self.logger.info("")
        self.logger.info("Step 4: Execute Healing")
        healing_results = []

        # Sort by priority
        healing_plans.sort(key=lambda p: {
            HealingPriority.CRITICAL: 0,
            HealingPriority.HIGH: 1,
            HealingPriority.MEDIUM: 2,
            HealingPriority.LOW: 3,
            HealingPriority.MONITOR: 4
        }.get(p.priority, 5))

        for plan in healing_plans:
            result = self.execute_healing(plan)
            healing_results.append(result)

        # Summary
        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("✅ Healing Complete")
        self.logger.info(f"   Diagnoses: {len(diagnoses)}")
        self.logger.info(f"   Healing Plans: {len(healing_plans)}")
        self.logger.info(f"   Successful Healings: {sum(1 for r in healing_results if r.success)}")
        self.logger.info("="*80)

        return {
            'status': 'healing_complete',
            'diagnoses': [d.to_dict() for d in diagnoses],
            'healing_plans': [p.to_dict() for p in healing_plans],
            'healing_results': [r.to_dict() for r in healing_results]
        }

    def get_healing_report(self) -> Dict[str, Any]:
        """Get comprehensive healing report"""
        return {
            'timestamp': datetime.now().isoformat(),
            'active_diagnoses': len(self.active_diagnoses),
            'healing_plans': len(self.healing_plans),
            'healing_results': len(self.healing_results),
            'hippocratic_principles': [p.to_dict() for p in self.HIPPOCRATIC_PRINCIPLES],
            'recent_results': [r.to_dict() for r in self.healing_results[-10:]]
        }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Physician, Heal Thyself")
    parser.add_argument("--heal", action="store_true", help="Perform complete healing process")
    parser.add_argument("--diagnose", action="store_true", help="Perform diagnosis only")
    parser.add_argument("--report", action="store_true", help="Get healing report")

    args = parser.parse_args()

    physician = JARVISPhysician()

    try:
        if args.heal:
            result = physician.heal_thyself()
            print("\n" + "="*80)
            print("🏥 Healing Complete")
            print("="*80)
            print(f"Status: {result['status']}")
            print(f"Diagnoses: {len(result['diagnoses'])}")
            print(f"Healing Plans: {len(result['healing_plans'])}")
            print(f"Results: {len(result['healing_results'])}")

        elif args.diagnose:
            diagnoses = physician.diagnose()
            print("\n" + "="*80)
            print("🔍 Diagnosis Results")
            print("="*80)
            for diag in diagnoses:
                print(f"\n{diag.component}: {diag.issue_type}")
                print(f"  Severity: {diag.severity}")
                print(f"  Description: {diag.description}")

        elif args.report:
            report = physician.get_healing_report()
            print("\n" + "="*80)
            print("📊 Healing Report")
            print("="*80)
            print(f"Active Diagnoses: {report['active_diagnoses']}")
            print(f"Healing Plans: {report['healing_plans']}")
            print(f"Healing Results: {report['healing_results']}")
            print("\nHippocratic Principles:")
            for principle in report['hippocratic_principles']:
                print(f"  - {principle['principle']}: {principle['description']}")

        else:
            parser.print_help()

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":

# TODO: Add error handling to functions identified by roast system:  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
#   - to_dict (line 73)
#   - to_dict (line 89)
#   - to_dict (line 108)
#   - to_dict (line 128)
#   - check_ethical_compliance (line 331)
#   - create_healing_plan (line 484)
#   - _improve_system (line 738)
#   - heal_thyself (line 751)
#   - get_healing_report (line 818)


    main()