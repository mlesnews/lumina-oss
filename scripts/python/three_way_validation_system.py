#!/usr/bin/env python3
"""
Three-Way Validation System - Checks and Balances

Like U.S. Government:
- Blueprint = Legislative (sets rules/plans)
- Master Todo = Administrative (execution/implementation)
- Holocrons = Judicial (records/evidence/archives)

QUORUM ESTABLISHED when all three agree. If not, proceed to BAU/Triage.

Tags: #VALIDATION #BLUEPRINT #MASTER_TODO #HOLOCRON #TRIAGE #BAU #QUORUM #CHECKS_BALANCES @JARVIS @LUMINA
"""

import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("three_way_validation")


@dataclass
class QuorumCheck:
    """Quorum check result - checks and balances"""

    system_name: str
    blueprint_value: Any = None
    todo_value: Any = None
    holocron_value: Any = None
    quorum_established: bool = False
    discrepancies: List[str] = field(default_factory=list)
    sync_required: bool = False


@dataclass
class ValidationResult:
    """Result of three-way validation with quorum checks"""

    validation_id: str
    timestamp: str
    blueprint_status: Dict[str, Any] = field(default_factory=dict)
    todo_status: Dict[str, Any] = field(default_factory=dict)
    holocron_status: Dict[str, Any] = field(default_factory=dict)
    quorum_checks: List[Dict[str, Any]] = field(default_factory=list)
    quorum_established: bool = False
    gaps: List[Dict[str, Any]] = field(default_factory=list)
    triage_items: List[Dict[str, Any]] = field(default_factory=list)
    bau_items: List[Dict[str, Any]] = field(default_factory=list)
    ecosystem_health: str = "unknown"  # "healthy", "needs_attention", "critical"
    recommendations: List[str] = field(default_factory=list)


class ThreeWayValidationSystem:
    """Three-way validation using Blueprint, Master Todo, and Holocrons - Checks and Balances"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.blueprint_file = project_root / "config" / "one_ring_blueprint.json"
        self.master_todo_file = project_root / "data" / "roadmap" / "master_todo_list.json"
        self.master_roadmap_file = project_root / "data" / "roadmap" / "master_roadmap.json"
        self.holocron_dir = project_root / "data" / "holocrons"
        self.homelab_holocron_file = (
            project_root / "data" / "homelab_audit" / "holocron_audit_*.json"
        )

    def load_blueprint(self) -> Dict[str, Any]:
        """Load blueprint state"""
        if self.blueprint_file.exists():
            with open(self.blueprint_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_master_todo(self) -> Dict[str, Any]:
        """Load master todo list"""
        if self.master_todo_file.exists():
            with open(self.master_todo_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_master_roadmap(self) -> Dict[str, Any]:
        """Load master roadmap"""
        if self.master_roadmap_file.exists():
            with open(self.master_roadmap_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def load_holocrons(self) -> List[Dict[str, Any]]:
        """Load relevant holocrons"""
        holocrons = []

        # Load homelab holocron
        holocron_files = list(self.project_root.glob("data/homelab_audit/holocron_*.json"))
        if holocron_files:
            latest = sorted(holocron_files, reverse=True)[0]
            with open(latest, encoding="utf-8") as f:
                holocrons.append(json.load(f))

        # Load other relevant holocrons
        if self.holocron_dir.exists():
            for holocron_file in sorted(self.holocron_dir.glob("*.json"), reverse=True)[:5]:
                try:
                    with open(holocron_file, encoding="utf-8") as f:
                        holocrons.append(json.load(f))
                except:
                    pass

        return holocrons

    def validate_blueprint(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Validate blueprint state"""
        status = {
            "exists": bool(blueprint),
            "last_updated": blueprint.get("blueprint_metadata", {}).get("last_updated"),
            "version": blueprint.get("blueprint_metadata", {}).get("version"),
            "systems_tracked": len(blueprint.get("core_systems", {})),
            "status": "healthy" if blueprint else "missing",
        }
        return status

    def validate_todo(self, todo_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate master todo list state"""
        todos = todo_data.get("todos", [])
        status = {
            "exists": bool(todo_data),
            "total_todos": len(todos),
            "pending": len([t for t in todos if t.get("status") == "pending"]),
            "in_progress": len([t for t in todos if t.get("status") == "in_progress"]),
            "completed": len([t for t in todos if t.get("status") == "completed"]),
            "critical": len([t for t in todos if t.get("priority") == "critical"]),
            "high": len([t for t in todos if t.get("priority") == "high"]),
            "last_updated": todo_data.get("last_updated"),
            "status": "healthy" if todo_data else "missing",
        }
        return status

    def validate_holocrons(self, holocrons: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate holocron state"""
        status = {
            "exists": len(holocrons) > 0,
            "total_holocrons": len(holocrons),
            "homelab_holocrons": len([h for h in holocrons if "homelab" in str(h).lower()]),
            "latest_timestamp": max([h.get("timestamp", "") for h in holocrons], default=""),
            "status": "healthy" if holocrons else "missing",
        }
        return status

    def check_quorum(
        self, blueprint: Dict[str, Any], todo_data: Dict[str, Any], holocrons: List[Dict[str, Any]]
    ) -> List[QuorumCheck]:
        """
        CHECKS AND BALANCES: Establish quorum across all three systems

        Like U.S. Government:
        - Blueprint = Legislative (sets rules/plans)
        - Master Todo = Administrative (execution/implementation)
        - Holocrons = Judicial (records/evidence/archives)

        Quorum established when all three agree. If not, discrepancies identified.
        """
        quorum_checks = []

        # Check 1: System Coverage Quorum
        blueprint_systems = set(blueprint.get("core_systems", {}).keys())
        todo_categories = set(t.get("category", "") for t in todo_data.get("todos", []))
        holocron_systems = set()

        # Extract systems from holocrons
        for holocron in holocrons:
            if isinstance(holocron, dict):
                # Check various holocron structures
                if "data" in holocron:
                    data = holocron["data"]
                    if isinstance(data, dict):
                        if "system" in data:
                            holocron_systems.add(data["system"])
                        if "category" in data:
                            holocron_systems.add(data["category"])
                        if "connected_to" in data:
                            connected = data["connected_to"]
                            if isinstance(connected, dict):
                                for key in connected.keys():
                                    if connected.get(key):
                                        holocron_systems.add(key)

        # All systems should appear in all three
        all_systems = blueprint_systems | todo_categories | holocron_systems

        for system in all_systems:
            check = QuorumCheck(
                system_name=system,
                blueprint_value=system in blueprint_systems,
                todo_value=system in todo_categories,
                holocron_value=system in holocron_systems,
            )

            # Quorum established if all three have this system
            check.quorum_established = (
                check.blueprint_value and check.todo_value and check.holocron_value
            )

            if not check.quorum_established:
                check.sync_required = True
                discrepancies = []
                if not check.blueprint_value:
                    discrepancies.append("Missing in Blueprint (Legislative)")
                if not check.todo_value:
                    discrepancies.append("Missing in Master Todo (Administrative)")
                if not check.holocron_value:
                    discrepancies.append("Missing in Holocrons (Judicial)")
                check.discrepancies = discrepancies

            quorum_checks.append(check)

        # Check 2: Timestamp Quorum (last updated should be recent)
        blueprint_updated = blueprint.get("blueprint_metadata", {}).get("last_updated", "")
        todo_updated = todo_data.get("last_updated", "")
        latest_holocron = max([h.get("timestamp", "") for h in holocrons], default="")

        timestamp_check = QuorumCheck(
            system_name="last_updated",
            blueprint_value=blueprint_updated,
            todo_value=todo_updated,
            holocron_value=latest_holocron,
        )

        # Check if all timestamps are within reasonable range (e.g., last 30 days)
        try:
            cutoff = datetime.now() - timedelta(days=30)
            blueprint_recent = True
            todo_recent = True
            holocron_recent = True

            if blueprint_updated:
                bp_date = datetime.fromisoformat(blueprint_updated.replace("Z", "+00:00"))
                blueprint_recent = bp_date.replace(tzinfo=None) > cutoff
            if todo_updated:
                td_date = datetime.fromisoformat(todo_updated.replace("Z", "+00:00"))
                todo_recent = td_date.replace(tzinfo=None) > cutoff
            if latest_holocron:
                hc_date = datetime.fromisoformat(latest_holocron.replace("Z", "+00:00"))
                holocron_recent = hc_date.replace(tzinfo=None) > cutoff

            timestamp_check.quorum_established = (
                blueprint_recent and todo_recent and holocron_recent
            )

            if not timestamp_check.quorum_established:
                timestamp_check.sync_required = True
                discrepancies = []
                if not blueprint_recent:
                    discrepancies.append("Blueprint (Legislative) is stale")
                if not todo_recent:
                    discrepancies.append("Master Todo (Administrative) is stale")
                if not holocron_recent:
                    discrepancies.append("Holocrons (Judicial) are stale")
                timestamp_check.discrepancies = discrepancies
        except:
            timestamp_check.quorum_established = False
            timestamp_check.sync_required = True
            timestamp_check.discrepancies = ["Unable to parse timestamps"]

        quorum_checks.append(timestamp_check)

        return quorum_checks

    def identify_gaps(
        self, blueprint: Dict[str, Any], todo_data: Dict[str, Any], holocrons: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify gaps - only when quorum is NOT established"""
        gaps = []

        # Get quorum checks first
        quorum_checks = self.check_quorum(blueprint, todo_data, holocrons)

        # Only create gaps for systems where quorum is NOT established
        for check in quorum_checks:
            if not check.quorum_established:
                gaps.append(
                    {
                        "gap_type": "quorum_failure",
                        "system": check.system_name,
                        "description": f"Quorum NOT established for '{check.system_name}': {', '.join(check.discrepancies)}",
                        "discrepancies": check.discrepancies,
                        "sync_required": check.sync_required,
                        "priority": "high" if check.sync_required else "medium",
                    }
                )

        return gaps

    def perform_triage(
        self, gaps: List[Dict[str, Any]], todo_data: Dict[str, Any]
    ) -> Tuple[List[Dict], List[Dict]]:
        """Perform triage and BAU prioritization - integrates with existing NAS Kron Triage system"""
        triage_items = []
        bau_items = []

        # Critical gaps go to triage (immediate action)
        for gap in gaps:
            if gap.get("priority") == "critical":
                triage_items.append(
                    {
                        "type": "gap",
                        "item": gap,
                        "action": "address_immediately",
                        "priority": "critical",
                        "bau_category": "critical",
                    }
                )

        # High priority todos go to triage
        for todo in todo_data.get("todos", []):
            if todo.get("priority") == "critical":
                triage_items.append(
                    {
                        "type": "todo",
                        "item": todo,
                        "action": "execute_immediately",
                        "priority": "critical",
                        "bau_category": "critical",
                    }
                )
            elif todo.get("priority") == "high":
                triage_items.append(
                    {
                        "type": "todo",
                        "item": todo,
                        "action": "schedule_soon",
                        "priority": "high",
                        "bau_category": "standard",
                    }
                )

        # Medium/low priority go to BAU
        for todo in todo_data.get("todos", []):
            if todo.get("priority") == "medium":
                bau_items.append(
                    {
                        "type": "todo",
                        "item": todo,
                        "action": "schedule_bau",
                        "priority": "medium",
                        "bau_category": "standard",
                    }
                )
            elif todo.get("priority") == "low":
                bau_items.append(
                    {
                        "type": "todo",
                        "item": todo,
                        "action": "schedule_bau",
                        "priority": "low",
                        "bau_category": "maintenance",
                    }
                )

        for gap in gaps:
            if gap.get("priority") == "medium":
                bau_items.append(
                    {
                        "type": "gap",
                        "item": gap,
                        "action": "address_bau",
                        "priority": "medium",
                        "bau_category": "standard",
                    }
                )
            elif gap.get("priority") == "low":
                bau_items.append(
                    {
                        "type": "gap",
                        "item": gap,
                        "action": "address_bau",
                        "priority": "low",
                        "bau_category": "maintenance",
                    }
                )

        return triage_items, bau_items

    def update_whopper_patterns(self, result: ValidationResult):
        """Update Whopper patterns with validation results"""
        whopper_file = self.project_root / "data" / "nas_kron_triage" / "whopper_patterns.json"

        if not whopper_file.exists():
            logger.warning("Whopper patterns file not found")
            return

        try:
            with open(whopper_file, encoding="utf-8") as f:
                whopper_data = json.load(f)

            # Add validation patterns
            if "validation_patterns" not in whopper_data:
                whopper_data["validation_patterns"] = {}

            whopper_data["validation_patterns"][result.validation_id] = {
                "timestamp": result.timestamp,
                "quorum_established": result.quorum_established,
                "ecosystem_health": result.ecosystem_health,
                "gaps_count": len(result.gaps),
                "triage_count": len(result.triage_items),
                "bau_count": len(result.bau_items),
                "blueprint_systems": result.blueprint_status.get("systems_tracked", 0),
                "todo_count": result.todo_status.get("total_todos", 0),
                "holocron_count": result.holocron_status.get("total_holocrons", 0),
            }

            # Update comprehensive patterns
            if "comprehensive_patterns" not in whopper_data:
                whopper_data["comprehensive_patterns"] = {}

            whopper_data["comprehensive_patterns"]["three_way_validation"] = {
                "last_validation": result.timestamp,
                "quorum_established": result.quorum_established,
                "health_status": result.ecosystem_health,
                "gaps": len(result.gaps),
                "recommendations": result.recommendations,
            }

            with open(whopper_file, "w", encoding="utf-8") as f:
                json.dump(whopper_data, f, indent=2, ensure_ascii=False, default=str)

            logger.info("✅ Whopper patterns updated")
        except Exception as e:
            logger.error(f"Failed to update Whopper patterns: {e}")

    def assess_ecosystem_health(
        self, blueprint_status: Dict, todo_status: Dict, holocron_status: Dict, gaps: List[Dict]
    ) -> str:
        """Assess overall ecosystem health"""
        if not blueprint_status.get("exists") or not todo_status.get("exists"):
            return "critical"

        if len(gaps) > 10:
            return "needs_attention"

        critical_todos = todo_status.get("critical", 0)
        if critical_todos > 5:
            return "needs_attention"

        return "healthy"

    def generate_recommendations(
        self, blueprint_status: Dict, todo_status: Dict, holocron_status: Dict, gaps: List[Dict]
    ) -> List[str]:
        """Generate recommendations"""
        recommendations = []

        if not blueprint_status.get("exists"):
            recommendations.append("Create blueprint file")

        if not todo_status.get("exists"):
            recommendations.append("Create master todo list")

        if not holocron_status.get("exists"):
            recommendations.append("Create holocrons for current state")

        if len(gaps) > 0:
            recommendations.append(f"Address {len(gaps)} identified gaps")

        critical_todos = todo_status.get("critical", 0)
        if critical_todos > 0:
            recommendations.append(f"Address {critical_todos} critical todos")

        return recommendations

    def run_validation(self) -> ValidationResult:
        """Run three-way validation with checks and balances"""
        logger.info("=" * 80)
        logger.info("THREE-WAY VALIDATION SYSTEM - CHECKS AND BALANCES")
        logger.info("=" * 80)

        # Load all three sources
        blueprint = self.load_blueprint()
        todo_data = self.load_master_todo()
        roadmap_data = self.load_master_roadmap()
        holocrons = self.load_holocrons()

        # Validate each source
        blueprint_status = self.validate_blueprint(blueprint)
        todo_status = self.validate_todo(todo_data)
        holocron_status = self.validate_holocrons(holocrons)

        # CHECKS AND BALANCES: Check quorum across all three systems
        quorum_checks = self.check_quorum(blueprint, todo_data, holocrons)
        quorum_established = all(check.quorum_established for check in quorum_checks)

        # Only identify gaps and proceed to work if quorum is NOT established
        gaps = []
        triage_items = []
        bau_items = []

        if not quorum_established:
            # Quorum NOT established - proceed to identify discrepancies
            logger.info("❌ QUORUM NOT ESTABLISHED - Proceeding to identify discrepancies")
            gaps = self.identify_gaps(blueprint, todo_data, holocrons)

            # Perform triage on discrepancies
            triage_items, bau_items = self.perform_triage(gaps, todo_data)
        else:
            # Quorum established - all three systems agree, no work needed
            logger.info(
                "✅ QUORUM ESTABLISHED - All three systems (Blueprint, Todo, Holocrons) agree"
            )
            logger.info("   No discrepancies found - system is in good state")

        # Assess ecosystem health
        ecosystem_health = self.assess_ecosystem_health(
            blueprint_status, todo_status, holocron_status, gaps
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(
            blueprint_status, todo_status, holocron_status, gaps
        )

        # Create validation result
        result = ValidationResult(
            validation_id=f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            timestamp=datetime.now().isoformat(),
            blueprint_status=blueprint_status,
            todo_status=todo_status,
            holocron_status=holocron_status,
            quorum_checks=[asdict(qc) for qc in quorum_checks],
            quorum_established=quorum_established,
            gaps=gaps,
            triage_items=triage_items,
            bau_items=bau_items,
            ecosystem_health=ecosystem_health,
            recommendations=recommendations,
        )

        # Update Whopper patterns
        self.update_whopper_patterns(result)

        return result

    def save_validation_result(self, result: ValidationResult, output_file: Path):
        """Save validation result"""
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(result), f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Validation result saved: {output_file}")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Three-Way Validation System (Blueprint, Master Todo, Holocrons) - Checks and Balances"
    )
    parser.add_argument("--output", help="Output file (default: validation_<timestamp>.json)")
    parser.add_argument("--report", action="store_true", help="Generate markdown report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    validator = ThreeWayValidationSystem(project_root)

    print("Running three-way validation with checks and balances...")
    result = validator.run_validation()

    # Save result
    output_dir = project_root / "data" / "validation"
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.output:
        output_file = Path(args.output)
    else:
        output_file = output_dir / f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

    validator.save_validation_result(result, output_file)

    # Print summary
    print("\n" + "=" * 80)
    print("THREE-WAY VALIDATION RESULTS - CHECKS AND BALANCES")
    print("=" * 80)
    print("\n📋 SYSTEM STATUS:")
    print(f"  Blueprint (Legislative): {result.blueprint_status.get('status', 'unknown')}")
    print(f"  Master Todo (Administrative): {result.todo_status.get('status', 'unknown')}")
    print(f"  Holocrons (Judicial): {result.holocron_status.get('status', 'unknown')}")

    print("\n⚖️  QUORUM CHECK:")
    if result.quorum_established:
        print("  ✅ QUORUM ESTABLISHED - All three systems agree")
        print("  ✅ System is in good state - No work needed")
    else:
        print("  ❌ QUORUM NOT ESTABLISHED - Discrepancies found")
        print("  ⚠️  Proceeding to BAU/Triage to resolve discrepancies")
        print(f"\n  Quorum Checks: {len(result.quorum_checks)}")
        failed_checks = [
            qc for qc in result.quorum_checks if not qc.get("quorum_established", True)
        ]
        print(f"  Failed Checks: {len(failed_checks)}")
        for check in failed_checks[:5]:  # Show first 5
            print(f"    - {check.get('system_name')}: {', '.join(check.get('discrepancies', []))}")

    print(f"\n📊 ECOSYSTEM HEALTH: {result.ecosystem_health.upper()}")

    if not result.quorum_established:
        print(f"\n🔍 DISCREPANCIES IDENTIFIED: {len(result.gaps)}")
        print(f"  Triage Items: {len(result.triage_items)}")
        print(f"  BAU Items: {len(result.bau_items)}")
        print("\n💡 Recommendations:")
        for rec in result.recommendations:
            print(f"  - {rec}")
    else:
        print("\n✅ All systems synchronized - No action required")

    print("=" * 80)

    if args.json:
        print(json.dumps(asdict(result), indent=2, default=str))

    if args.report:
        # Generate markdown report
        report_file = output_file.parent / f"{output_file.stem}_report.md"
        with open(report_file, "w", encoding="utf-8") as f:
            f.write("# Three-Way Validation Report - Checks and Balances\n\n")
            f.write(f"**Date**: {result.timestamp}\n\n")
            f.write(
                f"## ⚖️  QUORUM STATUS: {'ESTABLISHED ✅' if result.quorum_established else 'NOT ESTABLISHED ❌'}\n\n"
            )
            f.write(f"## Ecosystem Health: {result.ecosystem_health.upper()}\n\n")
            f.write("## Blueprint Status (Legislative)\n\n")
            for key, value in result.blueprint_status.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n## Todo Status (Administrative)\n\n")
            for key, value in result.todo_status.items():
                f.write(f"- **{key}**: {value}\n")
            f.write("\n## Holocron Status (Judicial)\n\n")
            for key, value in result.holocron_status.items():
                f.write(f"- **{key}**: {value}\n")
            f.write(f"\n## Quorum Checks ({len(result.quorum_checks)})\n\n")
            for check in result.quorum_checks[:10]:
                status = "✅" if check.get("quorum_established") else "❌"
                f.write(
                    f"- {status} **{check.get('system_name')}**: {', '.join(check.get('discrepancies', ['Quorum established']))}\n"
                )
            if not result.quorum_established:
                f.write(f"\n## Gaps ({len(result.gaps)})\n\n")
                for gap in result.gaps:
                    f.write(f"- **{gap.get('gap_type')}**: {gap.get('description')}\n")
                f.write(f"\n## Triage Items ({len(result.triage_items)})\n\n")
                for item in result.triage_items[:10]:
                    f.write(
                        f"- {item.get('action')}: {item.get('item', {}).get('title', item.get('item', {}).get('description', 'N/A'))}\n"
                    )
                f.write(f"\n## BAU Items ({len(result.bau_items)})\n\n")
                for item in result.bau_items[:10]:
                    f.write(
                        f"- {item.get('action')}: {item.get('item', {}).get('title', item.get('item', {}).get('description', 'N/A'))}\n"
                    )
        print(f"Report saved: {report_file}")


if __name__ == "__main__":
    main()
