#!/usr/bin/env python3
"""
Project Projection Assessor - Long-Range Goals & AI Capability Assessment

Assesses:
1. Long-term project goals and timelines
2. AI capability for long-term task completion
3. Master Blueprint (One Ring) as recreation document
4. Living document maintenance requirements
5. Verification/validation systems
6. Workflow orchestration and selection
7. "Measure twice, cut once" quality assurance

"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class TaskComplexity(Enum):
    SIMPLE = "simple"  # Minutes to hours
    MODERATE = "moderate"  # Hours to days
    COMPLEX = "complex"  # Days to weeks
    ENTERPRISE = "enterprise"  # Weeks to months
    EPIC = "epic"  # Months to years


class ProjectStatus(Enum):
    PLANNING = "planning"
    DEVELOPMENT = "development"
    INTEGRATION = "integration"
    TESTING = "testing"
    DEPLOYMENT = "deployment"
    OPERATIONAL = "operational"
    MAINTENANCE = "maintenance"


@dataclass
class TaskProjection:
    """Projection for task completion"""
    task_id: str
    description: str
    complexity: TaskComplexity
    estimated_hours: float
    ai_capability_score: float  # 0.0-1.0
    success_probability: float  # 0.0-1.0
    requires_human_oversight: bool
    dependencies: List[str] = field(default_factory=list)
    verification_steps: List[str] = field(default_factory=list)


@dataclass
class ProjectProjection:
    """Long-term project projection"""
    project_id: str
    name: str
    status: ProjectStatus
    long_term_goals: List[str] = field(default_factory=list)
    estimated_completion: Optional[datetime] = None
    current_phase: str = ""
    completion_percentage: float = 0.0
    ai_capable_tasks: int = 0
    human_required_tasks: int = 0
    risk_factors: List[str] = field(default_factory=list)


class ProjectProjectionAssessor:
    """
    Assesses project projections and AI capability for long-term work

    "Measure twice, cut once" - Quality over speed
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        self.one_ring_blueprint_path = self.project_root / "config" / "one_ring_blueprint.json"
        self.projection_data_path = self.project_root / "data" / "projections"
        self.projection_data_path.mkdir(parents=True, exist_ok=True)

        # Load One Ring Blueprint
        self.blueprint = self._load_blueprint()

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("ProjectProjectionAssessor")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 📊 ProjectProjection - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    def _load_blueprint(self) -> Dict[str, Any]:
        """Load One Ring Master Blueprint"""
        if not self.one_ring_blueprint_path.exists():
            self.logger.warning("One Ring Blueprint not found")
            return {}

        try:
            with open(self.one_ring_blueprint_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading blueprint: {e}")
            return {}

    def assess_blueprint_recreation_capability(self) -> Dict[str, Any]:
        """
        Assess if One Ring Blueprint is sufficient for project recreation

        Measures blueprint completeness, accuracy, and living document status
        """
        assessment = {
            "blueprint_completeness_score": 0.0,
            "recreation_capability": 0.0,
            "living_document_status": "unknown",
            "last_updated": None,
            "completeness_checks": {},
            "missing_elements": [],
            "recommendations": []
        }

        if not self.blueprint:
            assessment["recreation_capability"] = 0.0
            assessment["recommendations"].append("One Ring Blueprint not found or not loadable")
            return assessment

        # Check blueprint metadata
        metadata = self.blueprint.get('blueprint_metadata', {})
        assessment["last_updated"] = metadata.get('last_updated')
        assessment["living_document_status"] = "active" if metadata.get('living_document') else "static"

        # Completeness checks
        checks = {
            "core_systems": bool(self.blueprint.get('core_systems')),
            "system_integrations": bool(self.blueprint.get('system_integrations')),
            "defense_architecture": bool(self.blueprint.get('defense_architecture')),
            "deployment_status": bool(self.blueprint.get('deployment_status')),
            "documentation_index": bool(self.blueprint.get('documentation_index')),
            "master_feedback_loop": bool(self.blueprint.get('core_systems', {}).get('master_feedback_loop')),
            "autonomous_execution": bool(self.blueprint.get('core_systems', {}).get('master_feedback_loop', {}).get('autonomous_execution'))
        }

        assessment["completeness_checks"] = checks

        # Calculate completeness score
        total_checks = len(checks)
        passed_checks = sum(1 for v in checks.values() if v)
        assessment["blueprint_completeness_score"] = passed_checks / total_checks if total_checks > 0 else 0.0

        # Assess recreation capability (0.0-1.0)
        # Factors:
        # - Completeness (40%)
        # - Living document status (20%)
        # - Recent updates (20%)
        # - Integration details (20%)

        recreation_score = 0.0

        # Completeness factor
        recreation_score += assessment["blueprint_completeness_score"] * 0.4

        # Living document factor
        if assessment["living_document_status"] == "active":
            recreation_score += 0.2

        # Recent updates factor (within last 7 days = full score)
        if assessment["last_updated"]:
            try:
                last_update = datetime.fromisoformat(assessment["last_updated"].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_update.replace(tzinfo=None)).days
                if days_ago <= 7:
                    recreation_score += 0.2
                elif days_ago <= 30:
                    recreation_score += 0.1
            except:
                pass

        # Integration details factor
        integrations = self.blueprint.get('system_integrations', {})
        if integrations:
            integration_count = len(integrations)
            if integration_count >= 5:
                recreation_score += 0.2
            elif integration_count >= 3:
                recreation_score += 0.1

        assessment["recreation_capability"] = min(1.0, recreation_score)

        # Identify missing elements
        if not checks.get("core_systems"):
            assessment["missing_elements"].append("Core systems definition")
        if not checks.get("system_integrations"):
            assessment["missing_elements"].append("System integrations mapping")
        if not checks.get("deployment_status"):
            assessment["missing_elements"].append("Deployment status tracking")

        # Generate recommendations
        if assessment["recreation_capability"] < 0.8:
            assessment["recommendations"].append("Blueprint needs enhancement for full recreation capability")

        if assessment["living_document_status"] != "active":
            assessment["recommendations"].append("Enable living document mode for continuous updates")

        if assessment["last_updated"]:
            try:
                last_update = datetime.fromisoformat(assessment["last_updated"].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_update.replace(tzinfo=None)).days
                if days_ago > 7:
                    assessment["recommendations"].append(f"Blueprint last updated {days_ago} days ago - needs sync")
            except:
                pass

        return assessment

    def assess_ai_capability_for_long_term_tasks(self, task_description: str, 
                                                  complexity: TaskComplexity) -> TaskProjection:
        """
        Assess AI capability for completing long-term tasks

        Factors:
        - Task complexity
        - Clarity of requirements
        - Available context (blueprint, documentation)
        - Verification mechanisms
        - Human oversight requirements
        """

        # Base estimates by complexity
        complexity_estimates = {
            TaskComplexity.SIMPLE: (1, 4),  # 1-4 hours
            TaskComplexity.MODERATE: (8, 40),  # 1-5 days
            TaskComplexity.COMPLEX: (40, 160),  # 1-4 weeks
            TaskComplexity.ENTERPRISE: (160, 640),  # 1-4 months
            TaskComplexity.EPIC: (640, 2560)  # 4-12 months
        }

        hours_range = complexity_estimates.get(complexity, (1, 8))
        estimated_hours = sum(hours_range) / 2  # Average

        # AI capability scoring (0.0-1.0)
        ai_capability = 0.0

        # Factor 1: Task clarity (30%)
        # Simple, clear tasks = higher capability
        clarity_keywords = ["implement", "create", "build", "fix", "update", "add"]
        has_clear_action = any(kw in task_description.lower() for kw in clarity_keywords)
        ai_capability += 0.3 if has_clear_action else 0.1

        # Factor 2: Available context (30%)
        # One Ring Blueprint provides context
        blueprint_completeness = self.assess_blueprint_recreation_capability()["blueprint_completeness_score"]
        ai_capability += blueprint_completeness * 0.3

        # Factor 3: Complexity factor (20%)
        # Simpler tasks = higher AI capability
        complexity_scores = {
            TaskComplexity.SIMPLE: 1.0,
            TaskComplexity.MODERATE: 0.8,
            TaskComplexity.COMPLEX: 0.6,
            TaskComplexity.ENTERPRISE: 0.4,
            TaskComplexity.EPIC: 0.2
        }
        ai_capability += complexity_scores.get(complexity, 0.5) * 0.2

        # Factor 4: Verification mechanisms (20%)
        # If we have verification systems, AI can work more autonomously
        has_verification = bool(self.blueprint.get('core_systems', {}).get('master_feedback_loop', {}).get('autonomous_execution'))
        ai_capability += 0.2 if has_verification else 0.1

        ai_capability = min(1.0, ai_capability)

        # Success probability (slightly lower than capability due to real-world factors)
        success_probability = ai_capability * 0.9  # 10% buffer for unexpected issues

        # Human oversight required for complex/enterprise/epic tasks
        requires_oversight = complexity in [TaskComplexity.ENTERPRISE, TaskComplexity.EPIC] or ai_capability < 0.7

        # Verification steps
        verification_steps = [
            "Code review and testing",
            "Integration verification",
            "Performance validation",
            "Documentation update"
        ]

        if complexity in [TaskComplexity.ENTERPRISE, TaskComplexity.EPIC]:
            verification_steps.extend([
                "Architecture review",
                "Security audit",
                "Stakeholder approval",
                "Phased deployment"
            ])

        task_id = f"task_{int(datetime.now().timestamp())}"

        return TaskProjection(
            task_id=task_id,
            description=task_description,
            complexity=complexity,
            estimated_hours=estimated_hours,
            ai_capability_score=ai_capability,
            success_probability=success_probability,
            requires_human_oversight=requires_oversight,
            verification_steps=verification_steps
        )

    def create_long_term_projection(self) -> ProjectProjection:
        """
        Create long-term project projection based on current state

        Analyzes:
        - Current project status
        - Long-term goals
        - AI vs human task breakdown
        - Risk factors
        - Estimated completion
        """

        # Analyze current state from blueprint
        core_systems = self.blueprint.get('core_systems', {})

        # Count operational systems
        operational_systems = sum(
            1 for sys_data in core_systems.values()
            if isinstance(sys_data, dict) and sys_data.get('status') == 'operational'
        )

        total_systems = len(core_systems)
        completion_percentage = (operational_systems / total_systems * 100) if total_systems > 0 else 0.0

        # Extract long-term goals
        long_term_goals = [
            "Complete Master Feedback Loop @CORE implementation",
            "Full autonomous execution system (@DOIT @ALWAYS)",
            "Complete One Ring Blueprint living document maintenance",
            "All systems integrated and verified",
            "Production-ready deployment across all platforms"
        ]

        # Assess task breakdown
        # Estimate based on system complexity
        ai_capable = 0
        human_required = 0

        for sys_name, sys_data in core_systems.items():
            if isinstance(sys_data, dict):
                status = sys_data.get('status', 'unknown')
                if status == 'operational':
                    ai_capable += 1  # Maintenance tasks
                else:
                    # Development/implementation tasks
                    if sys_name == 'master_feedback_loop':
                        ai_capable += 3  # AI can handle most of this
                        human_required += 1  # Architecture review
                    elif sys_name in ['lumina_jarvis_extension', 'jarvis_multi_platform_applications']:
                        ai_capable += 5
                        human_required += 2  # UI/UX and stakeholder approval
                    else:
                        ai_capable += 2
                        human_required += 1

        # Estimate completion (assuming steady progress)
        # Based on current completion percentage and remaining work
        remaining_work = 100 - completion_percentage

        # Project timeline: 3-6 months for remaining work (with AI assistance)
        months_remaining = (remaining_work / 100) * 6  # Max 6 months
        estimated_completion = datetime.now() + timedelta(days=months_remaining * 30)

        # Risk factors
        risk_factors = []

        blueprint_assessment = self.assess_blueprint_recreation_capability()
        if blueprint_assessment["recreation_capability"] < 0.8:
            risk_factors.append("Bluepring completeness below optimal for recreation")

        if blueprint_assessment["last_updated"]:
            try:
                last_update = datetime.fromisoformat(blueprint_assessment["last_updated"].replace('Z', '+00:00'))
                days_ago = (datetime.now() - last_update.replace(tzinfo=None)).days
                if days_ago > 7:
                    risk_factors.append(f"Blueprint not synced recently ({days_ago} days)")
            except:
                pass

        if completion_percentage < 50:
            risk_factors.append("Project less than 50% complete - significant work remaining")

        # Determine current phase
        if completion_percentage < 25:
            current_phase = "Early Development"
        elif completion_percentage < 50:
            current_phase = "Active Development"
        elif completion_percentage < 75:
            current_phase = "Integration Phase"
        elif completion_percentage < 95:
            current_phase = "Testing & Validation"
        else:
            current_phase = "Final Deployment"

        return ProjectProjection(
            project_id="lumina_master_project",
            name="Lumina Master Project - One Ring System",
            status=ProjectStatus.DEVELOPMENT if completion_percentage < 80 else ProjectStatus.INTEGRATION,
            long_term_goals=long_term_goals,
            estimated_completion=estimated_completion,
            current_phase=current_phase,
            completion_percentage=completion_percentage,
            ai_capable_tasks=ai_capable,
            human_required_tasks=human_required,
            risk_factors=risk_factors
        )

    def generate_projection_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive projection report"""

            blueprint_assessment = self.assess_blueprint_recreation_capability()
            project_projection = self.create_long_term_projection()

            # Example task assessments
            example_tasks = [
                ("Implement complete Master Feedback Loop @CORE with all integrations", TaskComplexity.ENTERPRISE),
                ("Create and maintain living One Ring Blueprint document", TaskComplexity.COMPLEX),
                ("Build autonomous execution system (@DOIT @ALWAYS)", TaskComplexity.ENTERPRISE),
                ("Verify and validate all system integrations", TaskComplexity.COMPLEX),
                ("Deploy production-ready multi-platform applications", TaskComplexity.EPIC)
            ]

            task_projections = [
                self.assess_ai_capability_for_long_term_tasks(desc, complexity)
                for desc, complexity in example_tasks
            ]

            report = {
                "generated_at": datetime.now().isoformat(),
                "project_projection": {
                    "project_id": project_projection.project_id,
                    "name": project_projection.name,
                    "status": project_projection.status.value,
                    "current_phase": project_projection.current_phase,
                    "completion_percentage": round(project_projection.completion_percentage, 1),
                    "estimated_completion": project_projection.estimated_completion.isoformat() if project_projection.estimated_completion else None,
                    "long_term_goals": project_projection.long_term_goals,
                    "ai_capable_tasks": project_projection.ai_capable_tasks,
                    "human_required_tasks": project_projection.human_required_tasks,
                    "risk_factors": project_projection.risk_factors
                },
                "blueprint_assessment": blueprint_assessment,
                "task_projections": [
                    {
                        "task_id": tp.task_id,
                        "description": tp.description,
                        "complexity": tp.complexity.value,
                        "estimated_hours": round(tp.estimated_hours, 1),
                        "ai_capability_score": round(tp.ai_capability_score, 2),
                        "success_probability": round(tp.success_probability, 2),
                        "requires_human_oversight": tp.requires_human_oversight,
                        "verification_steps": tp.verification_steps
                    }
                    for tp in task_projections
                ],
                "recommendations": {
                    "immediate_actions": [
                        "Sync One Ring Blueprint if outdated (>7 days)",
                        "Enable living document mode for continuous updates",
                        "Establish verification workflows for all tasks",
                        "Implement 'measure twice, cut once' quality gates"
                    ],
                    "long_term_strategies": [
                        "Maintain blueprint as single source of truth",
                        "Automate blueprint sync with all system changes",
                        "Build comprehensive verification test suite",
                        "Establish clear AI/human task boundaries",
                        "Create success metrics and tracking"
                    ]
                }
            }

            # Save report
            report_file = self.projection_data_path / f"projection_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info(f"Projection report saved: {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_projection_report: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    assessor = ProjectProjectionAssessor()

    print("\n" + "=" * 80)
    print("📊 PROJECT PROJECTION ASSESSOR")
    print("=" * 80)
    print("Long-Range Goals & AI Capability Assessment")
    print("Measure twice, cut once - Quality over speed")
    print()

    # Generate report
    report = assessor.generate_projection_report()

    # Display key findings
    print("🔍 KEY FINDINGS")
    print("─" * 80)

    # Blueprint Assessment
    blueprint = report["blueprint_assessment"]
    print(f"\n📋 One Ring Blueprint Assessment:")
    print(f"   Completeness Score: {blueprint['blueprint_completeness_score']:.1%}")
    print(f"   Recreation Capability: {blueprint['recreation_capability']:.1%}")
    print(f"   Living Document Status: {blueprint['living_document_status']}")
    print(f"   Last Updated: {blueprint['last_updated'] or 'Unknown'}")

    if blueprint['recreation_capability'] >= 0.8:
        print("   ✅ Blueprint is sufficient for project recreation")
    else:
        print("   ⚠️ Blueprint needs enhancement for full recreation capability")

    # Project Projection
    project = report["project_projection"]
    print(f"\n🎯 Project Status:")
    print(f"   Name: {project['name']}")
    print(f"   Status: {project['status']}")
    print(f"   Current Phase: {project['current_phase']}")
    print(f"   Completion: {project['completion_percentage']:.1f}%")

    if project['estimated_completion']:
        print(f"   Estimated Completion: {project['estimated_completion'][:10]}")

    print(f"   AI-Capable Tasks: {project['ai_capable_tasks']}")
    print(f"   Human-Required Tasks: {project['human_required_tasks']}")

    if project['risk_factors']:
        print(f"\n   ⚠️ Risk Factors:")
        for risk in project['risk_factors']:
            print(f"      - {risk}")

    # Task Projections
    print(f"\n📋 Task Projections (Example Tasks):")
    for tp in report["task_projections"]:
        print(f"\n   Task: {tp['description'][:60]}...")
        print(f"      Complexity: {tp['complexity']}")
        print(f"      Estimated Hours: {tp['estimated_hours']:.1f}")
        print(f"      AI Capability: {tp['ai_capability_score']:.1%}")
        print(f"      Success Probability: {tp['success_probability']:.1%}")
        print(f"      Human Oversight: {'Required' if tp['requires_human_oversight'] else 'Not Required'}")
        print(f"      Verification Steps: {len(tp['verification_steps'])}")

    # Recommendations
    print(f"\n💡 RECOMMENDATIONS")
    print("─" * 80)
    print("\n   Immediate Actions:")
    for action in report["recommendations"]["immediate_actions"]:
        print(f"      • {action}")

    print("\n   Long-Term Strategies:")
    for strategy in report["recommendations"]["long_term_strategies"]:
        print(f"      • {strategy}")

    print(f"\n✅ Assessment Complete")
    print(f"   Report saved to: {assessor.projection_data_path}/")
    print()


if __name__ == "__main__":



    main()