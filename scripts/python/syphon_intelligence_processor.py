#!/usr/bin/env python3
"""
SYPHON Intelligence Processor - Transform SYPHON Data into Useful Information

Takes raw SYPHON extraction data and transforms it into:
- Actionable insights
- Task lists
- Decision summaries
- Intelligence reports
- Trend analysis

Tags: #SYPHON #INTELLIGENCE #PROCESSING #INSIGHTS @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonIntelligenceProcessor")


class SyphonIntelligenceProcessor:
    """
    Process SYPHON extraction data into useful, actionable information
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        
        # Load storage policy
        policy_file = self.project_root / "config" / "storage_policy.json"
        storage_policy = {"zero_local_storage_enforced": False}
        if policy_file.exists():
            with open(policy_file, "r", encoding="utf-8") as f:
                storage_policy = json.load(f)

        if storage_policy.get("zero_local_storage_enforced"):
            self.data_dir = Path(storage_policy["nas_paths"]["syphon_raw"])
            self.output_dir = Path(storage_policy["nas_paths"]["syphon_intelligence"])
            logger.info(f"🛡️  Enforcing Zero-Local-Storage Policy. Using NAS: {self.output_dir}")
        else:
            self.data_dir = self.project_root / "data" / "syphon_lumina_hourly"
            self.output_dir = self.project_root / "data" / "syphon_intelligence"
            
        self.output_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ SYPHON Intelligence Processor initialized")

    def load_execution_results(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Load recent execution results"""
        execution_files = sorted(
            self.data_dir.glob("execution_*.json"),
            key=lambda x: x.stat().st_mtime,
            reverse=True
        )[:limit]

        results = []
        for file in execution_files:
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    results.append(json.load(f))
            except Exception as e:
                logger.warning(f"⚠️  Error loading {file.name}: {e}")

        return results

    def extract_actionable_insights(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract actionable insights from SYPHON results"""
        insights = {
            "total_executions": len(results),
            "successful_executions": sum(1 for r in results if r.get("success", False)),
            "total_intelligence_items": sum(r.get("intelligence_extracted", 0) for r in results),
            "total_files_processed": sum(r.get("files_processed", 0) for r in results),
            "total_dirs_processed": sum(r.get("dirs_processed", 0) for r in results),
            "execution_timeline": [],
            "intelligence_trends": [],
            "actionable_items": [],
            "tasks": [],
            "decisions": [],
            "intelligence_summary": []
        }

        # Process each result
        for result in results:
            timestamp = result.get("timestamp", "")
            success = result.get("success", False)
            intelligence_count = result.get("intelligence_extracted", 0)

            insights["execution_timeline"].append({
                "timestamp": timestamp,
                "success": success,
                "intelligence_count": intelligence_count
            })

            # Extract from result data
            result_data = result.get("result", {})
            if isinstance(result_data, dict):
                intelligence = result_data.get("intelligence", {})

                # Handle both dict and list formats
                if isinstance(intelligence, dict):
                    # Collect actionable items
                    actionable = intelligence.get("actionable_items", [])
                    if isinstance(actionable, list):
                        insights["actionable_items"].extend(actionable)

                    # Collect tasks
                    tasks = intelligence.get("tasks", [])
                    if isinstance(tasks, list):
                        insights["tasks"].extend(tasks)

                    # Collect decisions
                    decisions = intelligence.get("decisions", [])
                    if isinstance(decisions, list):
                        insights["decisions"].extend(decisions)

                    # Collect intelligence
                    intel = intelligence.get("intelligence", [])
                    if isinstance(intel, list):
                        insights["intelligence_summary"].extend(intel)
                elif isinstance(intelligence, list):
                    # If intelligence is directly a list
                    insights["intelligence_summary"].extend(intelligence)

        # Deduplicate
        insights["actionable_items"] = list(set(insights["actionable_items"]))
        insights["tasks"] = self._deduplicate_tasks(insights["tasks"])
        insights["decisions"] = self._deduplicate_decisions(insights["decisions"])

        return insights

    def _deduplicate_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            """Deduplicate tasks"""
            seen = set()
            unique = []
            for task in tasks:
                task_key = json.dumps(task, sort_keys=True)
                if task_key not in seen:
                    seen.add(task_key)
                    unique.append(task)
            return unique

        except Exception as e:
            self.logger.error(f"Error in _deduplicate_tasks: {e}", exc_info=True)
            raise
    def _deduplicate_decisions(self, decisions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            """Deduplicate decisions"""
            seen = set()
            unique = []
            for decision in decisions:
                decision_key = json.dumps(decision, sort_keys=True)
                if decision_key not in seen:
                    seen.add(decision_key)
                    unique.append(decision)
            return unique

        except Exception as e:
            self.logger.error(f"Error in _deduplicate_decisions: {e}", exc_info=True)
            raise
    def generate_report(self, insights: Dict[str, Any]) -> str:
        """Generate human-readable report"""
        report = []
        report.append("="*80)
        report.append("SYPHON LUMINA INTELLIGENCE REPORT")
        report.append("="*80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Summary
        report.append("## SUMMARY")
        report.append(f"- Total Executions: {insights['total_executions']}")
        report.append(f"- Successful: {insights['successful_executions']}")
        report.append(f"- Total Intelligence Items: {insights['total_intelligence_items']}")
        report.append(f"- Total Files Processed: {insights['total_files_processed']}")
        report.append(f"- Total Directories Processed: {insights['total_dirs_processed']}")
        report.append("")

        # Actionable Items
        if insights["actionable_items"]:
            report.append("## ACTIONABLE ITEMS")
            for i, item in enumerate(insights["actionable_items"], 1):
                report.append(f"{i}. {item}")
            report.append("")

        # Tasks
        if insights["tasks"]:
            report.append("## TASKS")
            for i, task in enumerate(insights["tasks"], 1):
                if isinstance(task, dict):
                    task_desc = task.get("description", task.get("task", str(task)))
                    priority = task.get("priority", "normal")
                    report.append(f"{i}. [{priority.upper()}] {task_desc}")
                else:
                    report.append(f"{i}. {task}")
            report.append("")

        # Decisions
        if insights["decisions"]:
            report.append("## DECISIONS")
            for i, decision in enumerate(insights["decisions"], 1):
                if isinstance(decision, dict):
                    decision_desc = decision.get("description", decision.get("decision", str(decision)))
                    report.append(f"{i}. {decision_desc}")
                else:
                    report.append(f"{i}. {decision}")
            report.append("")

        # Intelligence Summary
        if insights["intelligence_summary"]:
            report.append("## INTELLIGENCE SUMMARY")
            for i, intel in enumerate(insights["intelligence_summary"][:10], 1):  # Top 10
                if isinstance(intel, dict):
                    intel_desc = intel.get("description", intel.get("insight", str(intel)))
                    report.append(f"{i}. {intel_desc}")
                else:
                    report.append(f"{i}. {intel}")
            report.append("")

        # Execution Timeline
        if insights["execution_timeline"]:
            report.append("## EXECUTION TIMELINE")
            for exec_item in insights["execution_timeline"][:5]:  # Last 5
                status = "✅" if exec_item["success"] else "❌"
                report.append(f"- {status} {exec_item['timestamp']}: {exec_item['intelligence_count']} items")
            report.append("")

        report.append("="*80)

        return "\n".join(report)

    def process_and_save(self, limit: int = 10) -> Dict[str, Any]:
        try:
            """Process SYPHON data and save results"""
            logger.info("🔍 Processing SYPHON intelligence data...")

            # Load results
            results = self.load_execution_results(limit=limit)
            logger.info(f"   Loaded {len(results)} execution results")

            if not results:
                logger.warning("⚠️  No execution results found")
                return {}

            # Extract insights
            insights = self.extract_actionable_insights(results)
            logger.info(f"   Extracted {len(insights['actionable_items'])} actionable items")
            logger.info(f"   Extracted {len(insights['tasks'])} tasks")
            logger.info(f"   Extracted {len(insights['decisions'])} decisions")

            # Generate report
            report = self.generate_report(insights)

            # Save results
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            # Save JSON
            json_file = self.output_dir / f"intelligence_{timestamp}.json"
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(insights, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"💾 Saved JSON: {json_file.name}")

            # Save report
            report_file = self.output_dir / f"intelligence_report_{timestamp}.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"💾 Saved Report: {report_file.name}")

            # Print report
            print("\n" + report)

            return insights


        except Exception as e:
            self.logger.error(f"Error in process_and_save: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 SYPHON INTELLIGENCE PROCESSOR")
    print("="*80 + "\n")

    processor = SyphonIntelligenceProcessor()
    insights = processor.process_and_save(limit=10)

    print("\n✅ Processing Complete")
    print("="*80 + "\n")
