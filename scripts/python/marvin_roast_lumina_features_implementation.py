#!/usr/bin/env python3
"""
MARVIN Roast: @LUMINA Features & Functionality Implementation Plan

@MARVIN performs critical analysis (roast) of the exploration and mapping work,
then creates a comprehensive implementation plan.

Tags: #MARVIN #ROAST #LUMINA #FEATURES #IMPLEMENTATION #PLAN @MARVIN @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("MARVINRoastLuminaFeatures")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MARVINRoastLuminaFeatures")


@dataclass
class RoastFinding:
    """A finding from MARVIN's roast"""
    severity: str  # critical, high, medium, low, info
    category: str  # gap, inconsistency, missing, incomplete, risk
    finding: str
    evidence: str
    recommendation: str
    priority: int  # 1-10, 10 = highest


@dataclass
class ImplementationTask:
    """An implementation task"""
    task_id: str
    title: str
    description: str
    priority: int
    dependencies: List[str] = field(default_factory=list)
    estimated_effort: str = "unknown"
    assignee: Optional[str] = None
    status: str = "pending"
    category: str = "implementation"


class MARVINRoastLuminaFeatures:
    """
    MARVIN's critical analysis (roast) of @LUMINA Features & Functionality mapping
    and implementation plan generation.
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.roast_findings: List[RoastFinding] = []
        self.implementation_tasks: List[ImplementationTask] = []

        logger.info("="*80)
        logger.info("🔥 MARVIN ROAST: @LUMINA Features & Functionality")
        logger.info("="*80)
        logger.info("")

    def roast(self) -> Dict[str, Any]:
        try:
            """
            Perform comprehensive roast of the exploration and mapping work

            Returns roast results with findings and recommendations
            """
            logger.info("🔥 Starting MARVIN roast...")
            logger.info("")

            # Load the feature map and tracking data
            feature_map_file = self.project_root / "docs" / "system" / "LUMINA_FEATURES_FUNCTIONALITY_MAP.md"
            tracking_file = self.project_root / "data" / "syphon" / "lumina_features_tracking.json"

            # Roast: Check if files exist
            if not feature_map_file.exists():
                self.roast_findings.append(RoastFinding(
                    severity="critical",
                    category="missing",
                    finding="Feature map documentation file does not exist",
                    evidence=f"Expected: {feature_map_file}",
                    recommendation="Create comprehensive feature map documentation",
                    priority=10
                ))

            if not tracking_file.exists():
                self.roast_findings.append(RoastFinding(
                    severity="high",
                    category="missing",
                    finding="Feature tracking JSON file does not exist",
                    evidence=f"Expected: {tracking_file}",
                    recommendation="Create feature tracking JSON file",
                    priority=8
                ))

            # Roast: Check cross-references
            self._roast_cross_references()

            # Roast: Check integration points
            self._roast_integration_points()

            # Roast: Check @SYPHON integration
            self._roast_syphon_integration()

            # Roast: Check implementation gaps
            self._roast_implementation_gaps()

            # Generate implementation plan
            self._generate_implementation_plan()

            # Compile roast results
            roast_results = {
                "roast_metadata": {
                    "roasted_by": "@MARVIN",
                    "roast_date": datetime.now().isoformat(),
                    "target": "@LUMINA Features & Functionality Implementation",
                    "total_findings": len(self.roast_findings),
                    "critical_findings": len([f for f in self.roast_findings if f.severity == "critical"]),
                    "high_findings": len([f for f in self.roast_findings if f.severity == "high"]),
                    "medium_findings": len([f for f in self.roast_findings if f.severity == "medium"]),
                    "low_findings": len([f for f in self.roast_findings if f.severity == "low"]),
                    "info_findings": len([f for f in self.roast_findings if f.severity == "info"])
                },
                "findings": [
                    {
                        "severity": f.severity,
                        "category": f.category,
                        "finding": f.finding,
                        "evidence": f.evidence,
                        "recommendation": f.recommendation,
                        "priority": f.priority
                    }
                    for f in self.roast_findings
                ],
                "implementation_plan": {
                    "total_tasks": len(self.implementation_tasks),
                    "tasks": [
                        {
                            "task_id": t.task_id,
                            "title": t.title,
                            "description": t.description,
                            "priority": t.priority,
                            "dependencies": t.dependencies,
                            "estimated_effort": t.estimated_effort,
                            "assignee": t.assignee,
                            "status": t.status,
                            "category": t.category
                        }
                        for t in self.implementation_tasks
                    ]
                }
            }

            return roast_results

        except Exception as e:
            self.logger.error(f"Error in roast: {e}", exc_info=True)
            raise
    def _roast_cross_references(self):
        """Roast cross-reference completeness"""
        logger.info("   🔍 Roasting cross-references...")

        # Check @inventory files
        inventory_files = [
            "data/software_inventory/inventory.json",
            "data/homelab_inventory/master_inventory.json"
        ]

        for inv_file in inventory_files:
            file_path = self.project_root / inv_file
            if not file_path.exists():
                self.roast_findings.append(RoastFinding(
                    severity="medium",
                    category="missing",
                    finding=f"Inventory file missing: {inv_file}",
                    evidence=f"File not found: {file_path}",
                    recommendation=f"Create or verify inventory file exists",
                    priority=6
                ))

        # Check @holocron
        holocron_file = self.project_root / "data" / "holocrons" / "holocrons_compound_log.json"
        if not holocron_file.exists():
            self.roast_findings.append(RoastFinding(
                severity="medium",
                category="missing",
                finding="Holocron compound log missing",
                evidence=f"File not found: {holocron_file}",
                recommendation="Create holocron compound log if needed",
                priority=5
            ))

        # Check One Ring Blueprint
        blueprint_file = self.project_root / "config" / "one_ring_blueprint.json"
        if not blueprint_file.exists():
            self.roast_findings.append(RoastFinding(
                severity="critical",
                category="missing",
                finding="One Ring Master Blueprint missing",
                evidence=f"File not found: {blueprint_file}",
                recommendation="One Ring Blueprint is critical - must exist",
                priority=10
            ))
        else:
            # Verify blueprint is up to date
            try:
                with open(blueprint_file, 'r') as f:
                    blueprint = json.load(f)
                    last_updated = blueprint.get("blueprint_metadata", {}).get("last_updated")
                    if last_updated:
                        # Check if updated recently (within 30 days)
                        from dateutil import parser
                        update_date = parser.parse(last_updated)
                        days_old = (datetime.now() - update_date.replace(tzinfo=None)).days
                        if days_old > 30:
                            self.roast_findings.append(RoastFinding(
                                severity="medium",
                                category="incomplete",
                                finding="One Ring Blueprint may be outdated",
                                evidence=f"Last updated: {last_updated} ({days_old} days ago)",
                                recommendation="Review and update One Ring Blueprint",
                                priority=7
                            ))
            except Exception as e:
                self.roast_findings.append(RoastFinding(
                    severity="high",
                    category="inconsistency",
                    finding="One Ring Blueprint file may be corrupted",
                    evidence=f"Error reading: {e}",
                    recommendation="Verify blueprint file integrity",
                    priority=8
                ))

        # Check Jedi Master/Padawan
        todo_file = self.project_root / "data" / "ask_database" / "master_padawan_todos.json"
        if not todo_file.exists():
            self.roast_findings.append(RoastFinding(
                severity="low",
                category="missing",
                finding="Jedi Master/Padawan todolist missing",
                evidence=f"File not found: {todo_file}",
                recommendation="Create todolist if needed",
                priority=4
            ))

    def _roast_integration_points(self):
        try:
            """Roast integration point completeness"""
            logger.info("   🔍 Roasting integration points...")

            # Check if integration points are documented
            integration_checks = [
                ("Master Feedback Loop", "scripts/python/master_feedback_loop_enhancer.py"),
                ("JARVIS", "scripts/python/jarvis_doit_executor.py"),
                ("@DOIT", "scripts/python/doit_chain_of_thought_enhanced.py"),
                ("Local-First AI Policy", "scripts/python/doit_local_first_ai_policy.py"),
                ("SYPHON", "scripts/python/syphon_perl_integration.py")
            ]

            for name, file_path in integration_checks:
                full_path = self.project_root / file_path
                if not full_path.exists():
                    self.roast_findings.append(RoastFinding(
                        severity="high",
                        category="missing",
                        finding=f"Integration point missing: {name}",
                        evidence=f"File not found: {file_path}",
                        recommendation=f"Verify {name} implementation exists",
                        priority=8
                    ))

        except Exception as e:
            self.logger.error(f"Error in _roast_integration_points: {e}", exc_info=True)
            raise
    def _roast_syphon_integration(self):
        """Roast @SYPHON integration completeness"""
        logger.info("   🔍 Roasting @SYPHON integration...")

        # Check @SYPHON command file
        syphon_cmd = self.project_root / ".cursor" / "commands" / "@syphon.md"
        if not syphon_cmd.exists():
            self.roast_findings.append(RoastFinding(
                severity="high",
                category="missing",
                finding="@SYPHON command documentation missing",
                evidence=f"File not found: {syphon_cmd}",
                recommendation="Create @SYPHON command documentation",
                priority=9
            ))
        else:
            # Check if integration section exists
            try:
                with open(syphon_cmd, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "@LUMINA Features & Functionality Integration" not in content:
                        self.roast_findings.append(RoastFinding(
                            severity="medium",
                            category="incomplete",
                            finding="@SYPHON command missing integration section",
                            evidence="Integration section not found in @syphon.md",
                            recommendation="Add @LUMINA Features & Functionality integration section",
                            priority=6
                        ))
            except Exception as e:
                self.roast_findings.append(RoastFinding(
                    severity="medium",
                    category="inconsistency",
                    finding="Error reading @SYPHON command file",
                    evidence=f"Error: {e}",
                    recommendation="Verify file accessibility",
                    priority=5
                ))

        # Check tracking file
        tracking_file = self.project_root / "data" / "syphon" / "lumina_features_tracking.json"
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    tracking = json.load(f)
                    if tracking.get("total_systems", 0) < 20:
                        self.roast_findings.append(RoastFinding(
                            severity="low",
                            category="incomplete",
                            finding="Feature tracking may be incomplete",
                            evidence=f"Only {tracking.get('total_systems', 0)} systems tracked (expected 25+)",
                            recommendation="Verify all systems are tracked",
                            priority=5
                        ))
            except Exception as e:
                self.roast_findings.append(RoastFinding(
                    severity="medium",
                    category="inconsistency",
                    finding="Feature tracking file may be corrupted",
                    evidence=f"Error reading: {e}",
                    recommendation="Verify tracking file integrity",
                    priority=6
                ))

    def _roast_implementation_gaps(self):
        try:
            """Roast implementation gaps"""
            logger.info("   🔍 Roasting implementation gaps...")

            # Check if implementation plan exists
            impl_plan = self.project_root / "docs" / "system" / "SYPHON_LUMINA_INTEGRATION_COMPLETE.md"
            if not impl_plan.exists():
                self.roast_findings.append(RoastFinding(
                    severity="high",
                    category="missing",
                    finding="Implementation plan documentation missing",
                    evidence=f"File not found: {impl_plan}",
                    recommendation="Create comprehensive implementation plan",
                    priority=9
                ))

            # Check for automated sync
            sync_script = self.project_root / "scripts" / "python" / "living_blueprint_sync.py"
            if not sync_script.exists():
                self.roast_findings.append(RoastFinding(
                    severity="medium",
                    category="missing",
                    finding="Living blueprint sync script missing",
                    evidence=f"File not found: {sync_script}",
                    recommendation="Create automated sync script for One Ring Blueprint",
                    priority=7
                ))

            # Check for real-time updates
            self.roast_findings.append(RoastFinding(
                severity="info",
                category="gap",
                finding="Real-time feature tracking not implemented",
                evidence="No automated system to update tracking as features change",
                recommendation="Implement real-time feature tracking system",
                priority=5
            ))

            # Check for pattern recognition
            self.roast_findings.append(RoastFinding(
                severity="info",
                category="gap",
                finding="Pattern recognition across systems not implemented",
                evidence="No automated pattern recognition system",
                recommendation="Implement pattern recognition for cross-system analysis",
                priority=4
            ))

        except Exception as e:
            self.logger.error(f"Error in _roast_implementation_gaps: {e}", exc_info=True)
            raise
    def _generate_implementation_plan(self):
        """Generate comprehensive implementation plan based on roast findings"""
        logger.info("   📋 Generating implementation plan...")

        # Group findings by priority
        critical_findings = [f for f in self.roast_findings if f.severity == "critical"]
        high_findings = [f for f in self.roast_findings if f.severity == "high"]
        medium_findings = [f for f in self.roast_findings if f.severity == "medium"]

        task_id = 1

        # Critical priority tasks
        for finding in critical_findings:
            self.implementation_tasks.append(ImplementationTask(
                task_id=f"TASK-{task_id:03d}",
                title=f"CRITICAL: {finding.finding[:60]}",
                description=finding.recommendation,
                priority=10,
                estimated_effort="1-2 days",
                assignee="@JARVIS",
                status="pending",
                category="critical"
            ))
            task_id += 1

        # High priority tasks
        for finding in high_findings:
            self.implementation_tasks.append(ImplementationTask(
                task_id=f"TASK-{task_id:03d}",
                title=f"HIGH: {finding.finding[:60]}",
                description=finding.recommendation,
                priority=8,
                estimated_effort="2-4 days",
                assignee="@JARVIS",
                status="pending",
                category="high"
            ))
            task_id += 1

        # Medium priority tasks
        for finding in medium_findings[:10]:  # Limit to top 10 medium priority
            self.implementation_tasks.append(ImplementationTask(
                task_id=f"TASK-{task_id:03d}",
                title=f"MEDIUM: {finding.finding[:60]}",
                description=finding.recommendation,
                priority=6,
                estimated_effort="3-5 days",
                assignee="@JARVIS",
                status="pending",
                category="medium"
            ))
            task_id += 1

        # Add standard implementation tasks
        self.implementation_tasks.append(ImplementationTask(
            task_id=f"TASK-{task_id:03d}",
            title="Implement automated feature tracking sync",
            description="Create system to automatically sync feature tracking with One Ring Blueprint and other systems",
            priority=7,
            dependencies=[],
            estimated_effort="5-7 days",
            assignee="@JARVIS",
            status="pending",
            category="automation"
        ))
        task_id += 1

        self.implementation_tasks.append(ImplementationTask(
            task_id=f"TASK-{task_id:03d}",
            title="Implement real-time feature updates",
            description="Create system to update feature tracking in real-time as systems change",
            priority=6,
            dependencies=["TASK-001"],
            estimated_effort="7-10 days",
            assignee="@JARVIS",
            status="pending",
            category="automation"
        ))
        task_id += 1

        self.implementation_tasks.append(ImplementationTask(
            task_id=f"TASK-{task_id:03d}",
            title="Implement pattern recognition across systems",
            description="Create system to identify patterns and relationships across all @LUMINA systems",
            priority=5,
            dependencies=["TASK-001"],
            estimated_effort="10-14 days",
            assignee="@SYPHON",
            status="pending",
            category="intelligence"
        ))
        task_id += 1

        self.implementation_tasks.append(ImplementationTask(
            task_id=f"TASK-{task_id:03d}",
            title="Implement integration analysis system",
            description="Create system to analyze and visualize integration relationships between systems",
            priority=6,
            dependencies=["TASK-001"],
            estimated_effort="7-10 days",
            assignee="@R5",
            status="pending",
            category="analysis"
        ))
        task_id += 1

        self.implementation_tasks.append(ImplementationTask(
            task_id=f"TASK-{task_id:03d}",
            title="Implement dependency mapping system",
            description="Create system to map dependencies between @LUMINA systems",
            priority=5,
            dependencies=["TASK-001"],
            estimated_effort="5-7 days",
            assignee="@JARVIS",
            status="pending",
            category="mapping"
        ))

    def save_roast_results(self, results: Dict[str, Any]) -> Path:
        try:
            """Save roast results to file"""
            output_dir = self.project_root / "data" / "marvin_roasts"
            output_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"lumina_features_roast_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"   💾 Roast results saved: {output_file}")
            return output_file

        except Exception as e:
            self.logger.error(f"Error in save_roast_results: {e}", exc_info=True)
            raise
    def generate_implementation_plan_doc(self, results: Dict[str, Any]) -> Path:
        """Generate markdown implementation plan document"""
        output_file = self.project_root / "docs" / "system" / "LUMINA_FEATURES_IMPLEMENTATION_PLAN.md"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# @LUMINA Features & Functionality - Implementation Plan\n\n")
            f.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}\n")
            f.write("**Status:** 📋 **IMPLEMENTATION PLAN GENERATED**\n")
            f.write("**Roasted By:** @MARVIN\n\n")
            f.write("---\n\n")

            # Roast Summary
            metadata = results["roast_metadata"]
            f.write("## 🔥 MARVIN Roast Summary\n\n")
            f.write(f"- **Total Findings:** {metadata['total_findings']}\n")
            f.write(f"- **Critical:** {metadata['critical_findings']}\n")
            f.write(f"- **High:** {metadata['high_findings']}\n")
            f.write(f"- **Medium:** {metadata['medium_findings']}\n")
            f.write(f"- **Low:** {metadata['low_findings']}\n")
            f.write(f"- **Info:** {metadata['info_findings']}\n\n")
            f.write("---\n\n")

            # Critical Findings
            critical = [f for f in results["findings"] if f["severity"] == "critical"]
            if critical:
                f.write("## 🚨 Critical Findings\n\n")
                for finding in critical:
                    f.write(f"### {finding['finding']}\n\n")
                    f.write(f"**Evidence:** {finding['evidence']}\n\n")
                    f.write(f"**Recommendation:** {finding['recommendation']}\n\n")
                    f.write(f"**Priority:** {finding['priority']}/10\n\n")
                    f.write("---\n\n")

            # High Priority Findings
            high = [f for f in results["findings"] if f["severity"] == "high"]
            if high:
                f.write("## ⚠️ High Priority Findings\n\n")
                for finding in high:
                    f.write(f"### {finding['finding']}\n\n")
                    f.write(f"**Evidence:** {finding['evidence']}\n\n")
                    f.write(f"**Recommendation:** {finding['recommendation']}\n\n")
                    f.write(f"**Priority:** {finding['priority']}/10\n\n")
                    f.write("---\n\n")

            # Implementation Plan
            f.write("## 📋 Implementation Plan\n\n")
            f.write(f"**Total Tasks:** {results['implementation_plan']['total_tasks']}\n\n")

            # Group by priority
            tasks_by_priority = {}
            for task in results["implementation_plan"]["tasks"]:
                priority = task["priority"]
                if priority not in tasks_by_priority:
                    tasks_by_priority[priority] = []
                tasks_by_priority[priority].append(task)

            # Sort by priority (descending)
            for priority in sorted(tasks_by_priority.keys(), reverse=True):
                tasks = tasks_by_priority[priority]
                f.write(f"### Priority {priority} Tasks\n\n")
                for task in tasks:
                    f.write(f"#### {task['task_id']}: {task['title']}\n\n")
                    f.write(f"**Description:** {task['description']}\n\n")
                    f.write(f"**Category:** {task['category']}\n\n")
                    f.write(f"**Estimated Effort:** {task['estimated_effort']}\n\n")
                    f.write(f"**Assignee:** {task['assignee']}\n\n")
                    f.write(f"**Status:** {task['status']}\n\n")
                    if task['dependencies']:
                        f.write(f"**Dependencies:** {', '.join(task['dependencies'])}\n\n")
                    f.write("---\n\n")

        logger.info(f"   📄 Implementation plan saved: {output_file}")
        return output_file


def main():
    """Main execution"""
    project_root = Path(__file__).parent.parent.parent

    roaster = MARVINRoastLuminaFeatures(project_root)
    results = roaster.roast()

    # Save results
    roast_file = roaster.save_roast_results(results)
    impl_plan = roaster.generate_implementation_plan_doc(results)

    # Print summary
    logger.info("")
    logger.info("="*80)
    logger.info("🔥 MARVIN ROAST COMPLETE")
    logger.info("="*80)
    logger.info("")
    logger.info(f"📊 Roast Summary:")
    logger.info(f"   Total Findings: {results['roast_metadata']['total_findings']}")
    logger.info(f"   Critical: {results['roast_metadata']['critical_findings']}")
    logger.info(f"   High: {results['roast_metadata']['high_findings']}")
    logger.info(f"   Medium: {results['roast_metadata']['medium_findings']}")
    logger.info("")
    logger.info(f"📋 Implementation Plan:")
    logger.info(f"   Total Tasks: {results['implementation_plan']['total_tasks']}")
    logger.info("")
    logger.info(f"💾 Files Generated:")
    logger.info(f"   Roast Results: {roast_file}")
    logger.info(f"   Implementation Plan: {impl_plan}")
    logger.info("")
    logger.info("="*80)

    return 0


if __name__ == "__main__":


    sys.exit(main())