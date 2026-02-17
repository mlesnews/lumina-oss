#!/usr/bin/env python3
"""
JARVIS @ASK Processor

Processes incomplete and unvalidated @asks from the course correction plan.
Uses @REARVIEW_MIRROR for guidance and maintains @JEDI @PATHFINDER vigilance.

Tags: #ASK_PROCESSING #REARVIEW_MIRROR #JEDI #PATHFINDER @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

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

logger = get_logger("JARVISAskProcessor")


class AskProcessor:
    """Process incomplete and unvalidated @asks"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ask_processing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.processed = []
        self.failed = []
        self.skipped = []

        # Compound log integration
        try:
            from jarvis_compound_log_health_monitor import CompoundLogHealthMonitor
            self.compound_monitor = CompoundLogHealthMonitor(project_root)
            self.compound_log_enabled = True
        except ImportError:
            self.compound_monitor = None
            self.compound_log_enabled = False
            logger.warning("Compound log monitor not available")

    def load_course_correction_plan(self) -> Optional[Dict[str, Any]]:
        try:
            """Load latest course correction plan"""
            correction_dir = project_root / "data" / "ask_course_correction"
            if correction_dir.exists():
                plan_files = list(correction_dir.glob("course_correction_plan_*.json"))
                if plan_files:
                    latest = max(plan_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, 'r', encoding='utf-8') as f:
                        return json.load(f)
            return None

        except Exception as e:
            self.logger.error(f"Error in load_course_correction_plan: {e}", exc_info=True)
            raise
    def analyze_ask_context(self, ask: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze ask context to determine what needs to be done"""
        file_path = ask.get("file", "")
        context = ask.get("context", "")

        analysis = {
            "file": file_path,
            "line": ask.get("line", 0),
            "match": ask.get("match", ""),
            "action_needed": "UNKNOWN",
            "can_complete": False,
            "reason": ""
        }

        # Check if file exists
        full_path = project_root / file_path
        if not full_path.exists():
            analysis["can_complete"] = False
            analysis["reason"] = "File does not exist"
            return analysis

        # Read file content
        try:
            content = full_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.split('\n')

            # Get context around the ask
            line_num = ask.get("line", 1) - 1
            start_line = max(0, line_num - 5)
            end_line = min(len(lines), line_num + 10)
            context_lines = lines[start_line:end_line]

            # Analyze context
            context_text = '\n'.join(context_lines).lower()

            # Check for completion indicators
            if any(word in context_text for word in ['complete', 'completed', 'done', 'finished', 'implemented']):
                analysis["action_needed"] = "VALIDATE"
                analysis["can_complete"] = True
                analysis["reason"] = "Appears to be completed, needs validation"
            elif any(word in context_text for word in ['todo', 'pending', 'incomplete', 'not done', 'missing']):
                analysis["action_needed"] = "COMPLETE"
                analysis["can_complete"] = True
                analysis["reason"] = "Needs completion"
            else:
                analysis["action_needed"] = "REVIEW"
                analysis["can_complete"] = True
                analysis["reason"] = "Needs review to determine action"

        except Exception as e:
            analysis["can_complete"] = False
            analysis["reason"] = f"Error reading file: {str(e)}"

        return analysis

    def process_ask(self, ask_data: Dict[str, Any], priority: str = "MEDIUM") -> Dict[str, Any]:
        """Process a single ask"""
        ask = ask_data.get("ask", {})
        file_path = ask.get("file", "")

        logger.info(f"Processing: {file_path} (Priority: {priority})")

        # Analyze ask
        analysis = self.analyze_ask_context(ask)

        result = {
            "timestamp": datetime.now().isoformat(),
            "ask": ask,
            "priority": priority,
            "analysis": analysis,
            "status": "PROCESSED",
            "action_taken": None
        }

        if not analysis["can_complete"]:
            result["status"] = "SKIPPED"
            result["reason"] = analysis["reason"]
            self.skipped.append(result)
            logger.info(f"  ⏭️  Skipped: {analysis['reason']}")
            return result

        # Determine action based on analysis
        if analysis["action_needed"] == "VALIDATE":
            result["action_taken"] = "Marked for validation"
            result["status"] = "VALIDATED"
            logger.info(f"  ✅ Validated")
        elif analysis["action_needed"] == "COMPLETE":
            result["action_taken"] = "Marked for completion"
            result["status"] = "MARKED_FOR_COMPLETION"
            logger.info(f"  📝 Marked for completion")
        elif analysis["action_needed"] == "REVIEW":
            result["action_taken"] = "Marked for review"
            result["status"] = "MARKED_FOR_REVIEW"
            logger.info(f"  🔍 Marked for review")

        self.processed.append(result)
        return result

    def process_batch(self, asks: List[Dict[str, Any]], limit: int = 10) -> Dict[str, Any]:
        """Process a batch of asks"""
        logger.info("=" * 80)
        logger.info("⚔️ @JEDI @PATHFINDER - PROCESSING @ASK BATCH")
        logger.info("=" * 80)
        logger.info("")

        # Write to compound log
        if self.compound_log_enabled and self.compound_monitor:
            self.compound_monitor.write_to_compound_log(
                f"Starting batch processing: {len(asks)} asks, limit: {limit}",
                "ASK_PROCESSOR"
            )

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": len(asks),
            "processed": 0,
            "skipped": 0,
            "failed": 0,
            "results": []
        }

        # Process up to limit
        for i, ask_data in enumerate(asks[:limit]):
            try:
                priority = ask_data.get("priority", "MEDIUM")
                result = self.process_ask(ask_data, priority)
                results["results"].append(result)
                results["processed"] += 1

                if result["status"] == "SKIPPED":
                    results["skipped"] += 1
                elif result["status"] == "FAILED":
                    results["failed"] += 1

            except Exception as e:
                logger.error(f"  ❌ Error processing ask: {str(e)}")
                results["failed"] += 1
                self.failed.append({
                    "ask": ask_data,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ BATCH PROCESSING COMPLETE")
        logger.info("=" * 80)
        logger.info(f"   Processed: {results['processed']}")
        logger.info(f"   Skipped: {results['skipped']}")
        logger.info(f"   Failed: {results['failed']}")
        logger.info("")

        # Write to compound log
        if self.compound_log_enabled and self.compound_monitor:
            self.compound_monitor.write_to_compound_log(
                f"Batch processing complete: Processed={results['processed']}, Skipped={results['skipped']}, Failed={results['failed']}",
                "ASK_PROCESSOR"
            )

        # Save results
        results_file = self.data_dir / f"processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, default=str)

        logger.info(f"📄 Results saved: {results_file}")
        logger.info("")

        return results

    def process_all_prioritized(self, limit: int = None) -> Dict[str, Any]:
        """Process all prioritized asks from course correction plan"""
        plan = self.load_course_correction_plan()

        if not plan:
            logger.error("No course correction plan found. Run --analyze --plan first.")
            return {}

        incomplete_asks = plan.get("course_correction", {}).get("incomplete_asks", {}).get("prioritized", [])

        if not incomplete_asks:
            logger.warning("No prioritized asks found in plan.")
            return {}

        # If limit is None, process all
        if limit is None:
            limit = len(incomplete_asks)

        logger.info(f"Processing {min(limit, len(incomplete_asks))} prioritized asks...")
        logger.info("")

        return self.process_batch(incomplete_asks, limit)

    def process_all_incomplete(self) -> Dict[str, Any]:
        try:
            """Process ALL incomplete asks from analysis"""
            import time

            # Load latest analysis
            analysis_dir = project_root / "data" / "ask_stack_delver"
            if analysis_dir.exists():
                analysis_files = list(analysis_dir.glob("ask_stack_delve_*.json"))
                if analysis_files:
                    latest = max(analysis_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, 'r', encoding='utf-8') as f:
                        analysis = json.load(f)

                    incomplete_asks = analysis.get("completion_analysis", {}).get("incomplete_asks", [])

                    if not incomplete_asks:
                        logger.warning("No incomplete asks found in analysis.")
                        return {}

                    # Extract just the ask data
                    asks_data = [ask_status.get("ask", {}) for ask_status in incomplete_asks]

                    # Prioritize them
                    prioritized = []
                    for ask in asks_data:
                        file_path = ask.get("file", "")
                        priority = "LOW"
                        if "jarvis" in file_path.lower() or "master" in file_path.lower():
                            priority = "HIGH"
                        elif "system" in file_path.lower() or "core" in file_path.lower():
                            priority = "MEDIUM"

                        prioritized.append({
                            "ask": ask,
                            "status": "INCOMPLETE",
                            "priority": priority,
                            "file": file_path
                        })

                    # Sort by priority
                    priority_order = {"HIGH": 0, "MEDIUM": 1, "LOW": 2}
                    prioritized.sort(key=lambda x: priority_order.get(x["priority"], 3))

                    logger.info(f"Processing ALL {len(prioritized)} incomplete asks...")
                    logger.info("")

                    # Process in batches to avoid memory issues
                    batch_size = 100
                    all_results = {
                        "timestamp": datetime.now().isoformat(),
                        "total": len(prioritized),
                        "processed": 0,
                        "skipped": 0,
                        "failed": 0,
                        "results": []
                    }

                    start_time = time.time()
                    total_batches = (len(prioritized) + batch_size - 1) // batch_size

                    for i in range(0, len(prioritized), batch_size):
                        batch_start = time.time()
                        batch_num = i // batch_size + 1
                        batch = prioritized[i:i+batch_size]

                        logger.info("")
                        logger.info("=" * 80)
                        logger.info(f"📦 BATCH {batch_num}/{total_batches} - Processing {len(batch)} asks...")
                        logger.info("=" * 80)

                        batch_results = self.process_batch(batch, len(batch))

                        batch_time = time.time() - batch_start
                        asks_per_min = (len(batch) / batch_time * 60) if batch_time > 0 else 0

                        all_results["processed"] += batch_results["processed"]
                        all_results["skipped"] += batch_results["skipped"]
                        all_results["failed"] += batch_results["failed"]
                        all_results["results"].extend(batch_results["results"])

                        # Progress update
                        elapsed = time.time() - start_time
                        remaining_batches = total_batches - batch_num
                        avg_batch_time = elapsed / batch_num if batch_num > 0 else 0
                        eta_seconds = avg_batch_time * remaining_batches
                        eta_minutes = eta_seconds / 60

                        logger.info("")
                        logger.info(f"📊 Batch {batch_num} Complete:")
                        logger.info(f"   Processed: {batch_results['processed']}")
                        logger.info(f"   Rate: {asks_per_min:.2f} asks/min")
                        logger.info(f"   Time: {batch_time:.2f} seconds")
                        logger.info(f"   Overall Progress: {all_results['processed']}/{all_results['total']} ({all_results['processed']/all_results['total']*100:.1f}%)")
                        logger.info(f"   ETA: {eta_minutes:.1f} minutes remaining")
                        logger.info("")

                    # Save combined results
                    results_file = self.data_dir / f"all_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    with open(results_file, 'w', encoding='utf-8') as f:
                        json.dump(all_results, f, indent=2, default=str)

                    total_time = time.time() - start_time
                    total_asks_per_min = (all_results['processed'] / total_time * 60) if total_time > 0 else 0

                    logger.info("")
                    logger.info("=" * 80)
                    logger.info("✅ ALL INCOMPLETE ASKS PROCESSING COMPLETE")
                    logger.info("=" * 80)
                    logger.info(f"   Total Processed: {all_results['processed']}")
                    logger.info(f"   Skipped: {all_results['skipped']}")
                    logger.info(f"   Failed: {all_results['failed']}")
                    logger.info(f"   Total Time: {total_time/60:.2f} minutes")
                    logger.info(f"   Average Rate: {total_asks_per_min:.2f} asks/min")
                    logger.info(f"📄 Results saved: {results_file}")
                    logger.info("")

                    return all_results

            logger.error("No analysis found. Run jarvis_ask_stack_analyzer.py --delve first.")
            return {}


        except Exception as e:
            self.logger.error(f"Error in process_all_incomplete: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS @ASK Processor")
        parser.add_argument("--process", type=int, default=10, help="Number of asks to process (default: 10)")
        parser.add_argument("--all", action="store_true", help="Process all prioritized asks")
        parser.add_argument("--all-incomplete", action="store_true", help="Process ALL incomplete asks (not just prioritized)")
        parser.add_argument("--limit", type=int, default=None, help="Limit for --all (default: None = all)")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        processor = AskProcessor(project_root)

        if args.all_incomplete:
            results = processor.process_all_incomplete()
            print(json.dumps(results, indent=2, default=str))
        elif args.all:
            results = processor.process_all_prioritized(args.limit)
            print(json.dumps(results, indent=2, default=str))
        else:
            plan = processor.load_course_correction_plan()
            if plan:
                incomplete_asks = plan.get("course_correction", {}).get("incomplete_asks", {}).get("prioritized", [])
                results = processor.process_batch(incomplete_asks, args.process)
                print(json.dumps(results, indent=2, default=str))
            else:
                logger.error("No course correction plan found. Run jarvis_ask_course_corrector.py --analyze --plan first.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()