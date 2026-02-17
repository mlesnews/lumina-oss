#!/usr/bin/env python3
"""
JARVIS SYPHON Deep Validation Results
Extract actionable intelligence from deep validation results

@JARVIS @SYPHON @VALIDATION @INTELLIGENCE @ACTIONABLE
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSyphonValidation")


class JARVISSyphonDeepValidation:
    """
    SYPHON Deep Validation Results

    Extracts actionable intelligence from deep validation results:
    - Actionable items (fixes, improvements)
    - Tasks (validation tasks, follow-ups)
    - Decisions (validation decisions, priorities)
    - Intelligence (patterns, insights, recommendations)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON validation system"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # SYPHON output
        self.syphon_dir = self.project_root / "data" / "syphon_validation"
        self.syphon_dir.mkdir(parents=True, exist_ok=True)

        # Validation results directory
        self.validation_dir = self.project_root / "data" / "system_validation"

        logger.info("=" * 70)
        logger.info("🔍 JARVIS SYPHON DEEP VALIDATION")
        logger.info("   Extracting Actionable Intelligence")
        logger.info("=" * 70)
        logger.info("")

    def syphon_validation_results(self, validation_file: Optional[Path] = None) -> Dict[str, Any]:
        """SYPHON validation results"""
        # Find latest validation file if not specified
        if validation_file is None:
            validation_files = sorted(self.validation_dir.glob("deep_validation_*.json"), reverse=True)
            if not validation_files:
                logger.error("No validation files found")
                return {"success": False, "message": "No validation files found"}
            validation_file = validation_files[0]

        logger.info(f"📄 SYPHONing validation file: {validation_file.name}")
        logger.info("")

        # Load validation results
        try:
            with open(validation_file, 'r', encoding='utf-8') as f:
                validation_data = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load validation file: {e}")
            return {"success": False, "error": str(e)}

        # Extract intelligence
        logger.info("🔍 EXTRACTING INTELLIGENCE...")
        logger.info("")

        # 1. Actionable Items
        logger.info("1. ACTIONABLE ITEMS")
        logger.info("-" * 70)
        actionable_items = self._extract_actionable_items(validation_data)
        logger.info(f"   Extracted {len(actionable_items)} actionable items")

        # 2. Tasks
        logger.info("\n2. TASKS")
        logger.info("-" * 70)
        tasks = self._extract_tasks(validation_data)
        logger.info(f"   Extracted {len(tasks)} tasks")

        # 3. Decisions
        logger.info("\n3. DECISIONS")
        logger.info("-" * 70)
        decisions = self._extract_decisions(validation_data)
        logger.info(f"   Extracted {len(decisions)} decisions")

        # 4. Intelligence
        logger.info("\n4. INTELLIGENCE")
        logger.info("-" * 70)
        intelligence = self._extract_intelligence(validation_data)
        logger.info(f"   Extracted {len(intelligence)} intelligence items")

        # 5. Patterns
        logger.info("\n5. PATTERNS")
        logger.info("-" * 70)
        patterns = self._extract_patterns(validation_data)
        logger.info(f"   Extracted {len(patterns)} patterns")

        # Compile SYPHON results
        syphon_results = {
            "syphon_id": f"validation_syphon_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "source_file": str(validation_file),
            "extracted_at": datetime.now().isoformat(),
            "validation_id": validation_data.get("validation_id"),
            "validation_summary": validation_data.get("summary", {}),
            "actionable_items": actionable_items,
            "tasks": tasks,
            "decisions": decisions,
            "intelligence": intelligence,
            "patterns": patterns
        }

        # Save SYPHON results
        self._save_syphon_results(syphon_results)

        logger.info("\n" + "=" * 70)
        logger.info("✅ SYPHON COMPLETE")
        logger.info("=" * 70)
        logger.info(f"Actionable Items: {len(actionable_items)}")
        logger.info(f"Tasks: {len(tasks)}")
        logger.info(f"Decisions: {len(decisions)}")
        logger.info(f"Intelligence: {len(intelligence)}")
        logger.info(f"Patterns: {len(patterns)}")
        logger.info("=" * 70)

        return syphon_results

    def _extract_actionable_items(self, validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract actionable items from validation results"""
        actionable_items = []

        validations = validation_data.get("validations", {})
        summary = validation_data.get("summary", {})

        # Fix V3 verification import issue
        if validations.get("v3_verification", {}).get("status") == "PARTIAL":
            actionable_items.append({
                "priority": "HIGH",
                "category": "FIX",
                "item": "Fix V3 Verification Import Issue",
                "description": "V3 verification import failed - needs path resolution fix",
                "validation": "v3_verification",
                "status": "PARTIAL"
            })
            logger.info("   • [HIGH] Fix V3 Verification Import Issue")

        # Address any failed validations
        if summary.get("failed", 0) > 0:
            actionable_items.append({
                "priority": "MEDIUM",
                "category": "IMPROVEMENT",
                "item": "Address Failed Validations",
                "description": f"{summary.get('failed', 0)} validation(s) failed - needs investigation",
                "failed_count": summary.get("failed", 0),
                "pass_rate": summary.get("pass_rate", "0%")
            })
            logger.info(f"   • [MEDIUM] Address {summary.get('failed', 0)} Failed Validation(s)")

        # Enhance validation coverage
        if summary.get("pass_rate", "0%") != "100.0%":
            actionable_items.append({
                "priority": "LOW",
                "category": "ENHANCEMENT",
                "item": "Improve Validation Pass Rate",
                "description": f"Current pass rate: {summary.get('pass_rate', '0%')} - aim for 100%",
                "current_rate": summary.get("pass_rate", "0%"),
                "target_rate": "100.0%"
            })
            logger.info(f"   • [LOW] Improve Validation Pass Rate to 100%")

        return actionable_items

    def _extract_tasks(self, validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract tasks from validation results"""
        tasks = []

        validations = validation_data.get("validations", {})

        # Task: Fix V3 verification
        if validations.get("v3_verification", {}).get("status") == "PARTIAL":
            tasks.append({
                "task": "Fix V3 Verification Import Path",
                "description": "Resolve import path issue for V3Verification class",
                "validation": "v3_verification",
                "priority": "HIGH"
            })
            logger.info("   • Fix V3 Verification Import Path [HIGH]")

        # Task: Validate all Python files
        if validations.get("syntax", {}).get("status") == "PASS":
            tasks.append({
                "task": "Maintain Syntax Validation",
                "description": "Continue validating all Python files for syntax errors",
                "validation": "syntax",
                "priority": "LOW"
            })
            logger.info("   • Maintain Syntax Validation [LOW]")

        # Task: Monitor data integrity
        if validations.get("data_integrity", {}).get("status") == "PASS":
            tasks.append({
                "task": "Continue Data Integrity Monitoring",
                "description": "Maintain data integrity validation for all JSON files",
                "validation": "data_integrity",
                "priority": "MEDIUM"
            })
            logger.info("   • Continue Data Integrity Monitoring [MEDIUM]")

        return tasks

    def _extract_decisions(self, validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract decisions from validation results"""
        decisions = []

        summary = validation_data.get("summary", {})
        validations = validation_data.get("validations", {})

        # Decision: Validation status
        validation_status = summary.get("validation_status", "UNKNOWN")
        decisions.append({
            "decision": "Validation Status Assessment",
            "description": f"System validation status: {validation_status}",
            "status": validation_status,
            "pass_rate": summary.get("pass_rate", "0%"),
            "recommendation": "PASS" if validation_status == "PASS" else "Address issues before production"
        })
        logger.info(f"   • Validation Status: {validation_status}")

        # Decision: V3 verification priority
        if validations.get("v3_verification", {}).get("status") == "PARTIAL":
            decisions.append({
                "decision": "V3 Verification Priority",
                "description": "V3 verification has import issue - decide on fix priority",
                "priority": "HIGH",
                "recommendation": "Fix import path to ensure V3 verification works correctly"
            })
            logger.info("   • V3 Verification: HIGH Priority Fix")

        # Decision: System readiness
        if summary.get("pass_rate", "0%") == "100.0%":
            decisions.append({
                "decision": "System Readiness",
                "description": "All systems validated - ready for production",
                "readiness": "READY",
                "recommendation": "Proceed with confidence"
            })
            logger.info("   • System Readiness: READY")
        else:
            decisions.append({
                "decision": "System Readiness",
                "description": f"Pass rate: {summary.get('pass_rate', '0%')} - needs improvement",
                "readiness": "NEEDS_IMPROVEMENT",
                "recommendation": "Address validation issues before production"
            })
            logger.info("   • System Readiness: NEEDS_IMPROVEMENT")

        return decisions

    def _extract_intelligence(self, validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract intelligence from validation results"""
        intelligence = []

        validations = validation_data.get("validations", {})
        summary = validation_data.get("summary", {})

        # Intelligence: System health
        pass_rate = float(summary.get("pass_rate", "0%").replace("%", ""))
        if pass_rate >= 90:
            intelligence.append({
                "type": "SYSTEM_HEALTH",
                "insight": "System Health: Excellent",
                "description": f"Pass rate of {summary.get('pass_rate', '0%')} indicates strong system health",
                "confidence": "HIGH",
                "pass_rate": summary.get("pass_rate", "0%")
            })
            logger.info(f"   • System Health: Excellent ({summary.get('pass_rate', '0%')})")

        # Intelligence: Core systems status
        if validations.get("core_systems", {}).get("status") == "PASS":
            intelligence.append({
                "type": "CORE_SYSTEMS",
                "insight": "Core Systems: All Validated",
                "description": "All core JARVIS systems are validated and functional",
                "confidence": "HIGH",
                "systems_count": validations.get("core_systems", {}).get("validated", 0)
            })
            logger.info("   • Core Systems: All Validated")

        # Intelligence: Financial systems status
        if validations.get("financial_systems", {}).get("status") == "PASS":
            intelligence.append({
                "type": "FINANCIAL_SYSTEMS",
                "insight": "Financial Systems: Fully Operational",
                "description": "All financial systems validated with data directories",
                "confidence": "HIGH",
                "scripts_count": validations.get("financial_systems", {}).get("scripts_validated", 0),
                "data_dirs_count": validations.get("financial_systems", {}).get("data_dirs_validated", 0)
            })
            logger.info("   • Financial Systems: Fully Operational")

        # Intelligence: End-to-end workflows
        if validations.get("end_to_end_workflows", {}).get("status") == "PASS":
            intelligence.append({
                "type": "WORKFLOWS",
                "insight": "End-to-End Workflows: All Components Present",
                "description": "All end-to-end workflows have all required components",
                "confidence": "HIGH",
                "workflows_count": validations.get("end_to_end_workflows", {}).get("validated", 0)
            })
            logger.info("   • End-to-End Workflows: All Components Present")

        return intelligence

    def _extract_patterns(self, validation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract patterns from validation results"""
        patterns = []

        validations = validation_data.get("validations", {})

        # Pattern: High pass rate
        summary = validation_data.get("summary", {})
        if summary.get("pass_rate", "0%") == "90.0%":
            patterns.append({
                "pattern": "90% Pass Rate Pattern",
                "description": "Consistent 90% pass rate indicates strong system validation",
                "category": "VALIDATION_PATTERN",
                "pass_rate": "90.0%"
            })
            logger.info("   • 90% Pass Rate Pattern")

        # Pattern: Core systems always pass
        if validations.get("core_systems", {}).get("status") == "PASS":
            patterns.append({
                "pattern": "Core Systems Reliability",
                "description": "Core systems consistently pass validation",
                "category": "SYSTEM_PATTERN",
                "reliability": "HIGH"
            })
            logger.info("   • Core Systems Reliability Pattern")

        # Pattern: Data integrity maintained
        if validations.get("data_integrity", {}).get("status") == "PASS":
            patterns.append({
                "pattern": "Data Integrity Maintenance",
                "description": "All data directories maintain valid JSON structure",
                "category": "DATA_PATTERN",
                "integrity": "MAINTAINED"
            })
            logger.info("   • Data Integrity Maintenance Pattern")

        # Pattern: V3 verification import issue
        if validations.get("v3_verification", {}).get("status") == "PARTIAL":
            patterns.append({
                "pattern": "V3 Verification Import Issue",
                "description": "Recurring import path issue with V3 verification",
                "category": "ISSUE_PATTERN",
                "severity": "MEDIUM"
            })
            logger.info("   • V3 Verification Import Issue Pattern")

        return patterns

    def _save_syphon_results(self, syphon_results: Dict[str, Any]) -> None:
        """Save SYPHON results"""
        try:
            filename = self.syphon_dir / f"{syphon_results['syphon_id']}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(syphon_results, f, indent=2, default=str)
            logger.info(f"✅ SYPHON results saved: {filename}")
        except Exception as e:
            logger.error(f"Failed to save SYPHON results: {e}")


def main():
    """Main execution"""
    print("=" * 70)
    print("🔍 JARVIS SYPHON DEEP VALIDATION")
    print("   Extracting Actionable Intelligence")
    print("=" * 70)
    print()

    syphon = JARVISSyphonDeepValidation()
    results = syphon.syphon_validation_results()

    print()
    print("=" * 70)
    print("✅ SYPHON COMPLETE")
    print("=" * 70)
    if results.get("success", True):
        print(f"Actionable Items: {len(results.get('actionable_items', []))}")
        print(f"Tasks: {len(results.get('tasks', []))}")
        print(f"Decisions: {len(results.get('decisions', []))}")
        print(f"Intelligence: {len(results.get('intelligence', []))}")
        print(f"Patterns: {len(results.get('patterns', []))}")
    else:
        print(f"Error: {results.get('message', 'Unknown error')}")
    print("=" * 70)


if __name__ == "__main__":


    main()