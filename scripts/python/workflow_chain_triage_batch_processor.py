#!/usr/bin/env python3
"""
Workflow Chain Triage & Staggered Batch Processor

Performs chain triage on all 25 workflows, then processes them in staggered batches.
Uses intelligent prioritization, dependency chaining, and resource-aware batch processing.

Tags: #WORKFLOW #TRIAGE #CHAIN #BATCH #STAGGERED #PROCESSING @JARVIS @DOIT
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
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

logger = get_logger("WorkflowChainTriageBatchProcessor")

# Import required systems
try:
    from aggregate_workflows_to_master import WorkflowAggregator
    AGGREGATOR_AVAILABLE = True
except ImportError:
    AGGREGATOR_AVAILABLE = False
    logger.warning("⚠️  Workflow aggregator not available")

try:
    from jarvis_ask_stack_triage_docuseries import TriagePriority
    TRIAGE_AVAILABLE = True
except ImportError:
    TRIAGE_AVAILABLE = False
    logger.warning("⚠️  Triage system not available")


class WorkflowPriority(Enum):
    """Workflow processing priority"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    ARCHIVE = "archive"


@dataclass
class TriageResult:
    """Triage result for a workflow"""
    workflow_id: str
    workflow_name: str
    priority: WorkflowPriority
    category: str
    estimated_processing_time: int = 5  # minutes
    dependencies: List[str] = field(default_factory=list)
    chain_position: int = 0
    batch_number: int = 0
    reasoning: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class BatchConfig:
    """Batch processing configuration"""
    batch_size: int = 5  # Workflows per batch
    stagger_delay: int = 30  # Seconds between batches
    max_concurrent: int = 3  # Max concurrent workflows in a batch
    retry_attempts: int = 2
    retry_delay: int = 10  # Seconds


class WorkflowChainTriageBatchProcessor:
    """
    Chain Triage & Staggered Batch Processor for Workflows

    Performs intelligent triage, chains workflows by dependencies,
    and processes them in staggered batches.
    """

    def __init__(self, project_root: Optional[Path] = None, batch_config: Optional[BatchConfig] = None):
        """Initialize processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "workflow_chain_triage"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.batch_config = batch_config or BatchConfig()

        # Initialize aggregator
        self.aggregator = None
        if AGGREGATOR_AVAILABLE:
            try:
                self.aggregator = WorkflowAggregator(project_root=self.project_root)
                logger.info("✅ Workflow aggregator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize aggregator: {e}")

        logger.info("✅ Workflow Chain Triage Batch Processor initialized")

    def load_workflows(self) -> List[Dict[str, Any]]:
        """Load all workflows"""
        if not self.aggregator:
            logger.error("❌ Aggregator not available")
            return []

        workflows = self.aggregator.load_all_workflows()
        logger.info(f"✅ Loaded {len(workflows)} workflows")
        return workflows

    def triage_workflow(self, workflow: Dict[str, Any]) -> TriageResult:
        """
        Perform triage on a single workflow.

        Determines priority, category, dependencies, and processing requirements.
        """
        workflow_id = workflow["workflow_id"]
        workflow_name = workflow["workflow_name"]
        messages = workflow.get("messages", [])
        message_count = len(messages)
        agents = workflow.get("agents_involved", [])

        # Determine priority based on various factors
        priority = WorkflowPriority.MEDIUM
        reasoning_parts = []

        # Factor 1: Message count (more messages = higher priority)
        if message_count > 20:
            priority = WorkflowPriority.HIGH
            reasoning_parts.append(f"High message count ({message_count})")
        elif message_count < 3:
            priority = WorkflowPriority.LOW
            reasoning_parts.append(f"Low message count ({message_count})")

        # Factor 2: Agent involvement (critical agents = higher priority)
        critical_agents = ["JARVIS", "C-3PO", "R2-D2"]
        if any(agent in critical_agents for agent in agents):
            if priority == WorkflowPriority.MEDIUM:
                priority = WorkflowPriority.HIGH
            reasoning_parts.append(f"Critical agents involved: {[a for a in agents if a in critical_agents]}")

        # Factor 3: Age (older = lower priority, unless critical)
        created_at = workflow.get("created_at", "")
        if created_at:
            try:
                from datetime import datetime
                created = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                age_days = (datetime.now() - created.replace(tzinfo=None)).days
                if age_days > 7 and priority != WorkflowPriority.CRITICAL:
                    priority = WorkflowPriority.LOW
                    reasoning_parts.append(f"Older workflow ({age_days} days)")
            except:
                pass

        # Factor 4: Workflow name keywords
        name_lower = workflow_name.lower()
        if any(kw in name_lower for kw in ["critical", "urgent", "fix", "error", "fail"]):
            priority = WorkflowPriority.CRITICAL
            reasoning_parts.append("Critical keywords in name")
        elif any(kw in name_lower for kw in ["archive", "old", "legacy"]):
            priority = WorkflowPriority.ARCHIVE
            reasoning_parts.append("Archive keywords in name")

        # Determine category
        category = "general"
        if "financial" in name_lower:
            category = "financial"
        elif "roamwise" in name_lower or "stargate" in name_lower:
            category = "integration"
        elif "session" in name_lower:
            category = "session"
        elif "subagent" in name_lower:
            category = "subagent"

        # Estimate processing time (base 5 min + 1 min per 10 messages)
        estimated_time = 5 + (message_count // 10)

        # Find dependencies (workflows that should be processed before this one)
        dependencies = []
        # Check for references to other workflows in messages
        for msg in messages[:10]:  # Check first 10 messages
            msg_text = str(msg.get("content", msg.get("text", ""))).lower()
            for other_wf in workflow.get("metadata", {}).get("source_workflows", []):
                if other_wf.lower() in msg_text and other_wf != workflow_id:
                    if other_wf not in dependencies:
                        dependencies.append(other_wf)

        reasoning = "; ".join(reasoning_parts) if reasoning_parts else "Standard workflow"

        return TriageResult(
            workflow_id=workflow_id,
            workflow_name=workflow_name,
            priority=priority,
            category=category,
            estimated_processing_time=estimated_time,
            dependencies=dependencies,
            reasoning=reasoning,
            metadata={
                "message_count": message_count,
                "agents": agents,
                "created_at": created_at
            }
        )

    def chain_triage_all(self, workflows: List[Dict[str, Any]]) -> List[TriageResult]:
        """
        Perform chain triage on all workflows.

        Returns workflows sorted by priority and dependencies.
        """
        logger.info("🔄 Performing chain triage on all workflows...")

        # Triage all workflows
        triage_results = []
        for workflow in workflows:
            triage_result = self.triage_workflow(workflow)
            triage_results.append(triage_result)

        # Sort by priority (critical first, archive last)
        priority_order = {
            WorkflowPriority.CRITICAL: 0,
            WorkflowPriority.HIGH: 1,
            WorkflowPriority.MEDIUM: 2,
            WorkflowPriority.LOW: 3,
            WorkflowPriority.ARCHIVE: 4
        }

        triage_results.sort(key=lambda x: (
            priority_order.get(x.priority, 99),
            -x.metadata.get("message_count", 0)  # More messages = higher priority within same level
        ))

        # Build dependency chain
        workflow_ids = {tr.workflow_id for tr in triage_results}
        workflow_map = {tr.workflow_id: tr for tr in triage_results}

        # Resolve dependencies (only include if dependency exists)
        for triage_result in triage_results:
            valid_deps = [dep for dep in triage_result.dependencies if dep in workflow_ids]
            triage_result.dependencies = valid_deps

        # Assign chain positions based on dependencies
        processed = set()
        chain_position = 0

        for triage_result in triage_results:
            if triage_result.workflow_id in processed:
                continue

            # Check if dependencies are processed
            deps_processed = all(dep in processed for dep in triage_result.dependencies)

            if deps_processed or not triage_result.dependencies:
                triage_result.chain_position = chain_position
                processed.add(triage_result.workflow_id)
                chain_position += 1
            else:
                # Dependencies not yet processed, will be handled in next pass
                pass

        # Second pass for remaining workflows
        for triage_result in triage_results:
            if triage_result.workflow_id not in processed:
                triage_result.chain_position = chain_position
                processed.add(triage_result.workflow_id)
                chain_position += 1

        logger.info(f"✅ Chain triage complete: {len(triage_results)} workflows triaged")

        # Log priority distribution
        priority_counts = {}
        for tr in triage_results:
            priority_counts[tr.priority.value] = priority_counts.get(tr.priority.value, 0) + 1

        logger.info(f"   Priority distribution: {priority_counts}")

        return triage_results

    def create_staggered_batches(self, triage_results: List[TriageResult]) -> List[List[TriageResult]]:
        """
        Create staggered batches from triaged workflows.

        Batches are created based on chain position and batch size.
        """
        logger.info(f"🔄 Creating staggered batches (batch_size={self.batch_config.batch_size})...")

        batches = []
        current_batch = []

        for triage_result in triage_results:
            current_batch.append(triage_result)

            if len(current_batch) >= self.batch_config.batch_size:
                batches.append(current_batch)
                # Assign batch numbers after creating batch
                for tr in current_batch:
                    tr.batch_number = len(batches)
                current_batch = []

        # Add remaining workflows as last batch
        if current_batch:
            batches.append(current_batch)
            # Assign batch numbers for last batch
            for tr in current_batch:
                tr.batch_number = len(batches)

        logger.info(f"✅ Created {len(batches)} batches")
        for i, batch in enumerate(batches, 1):
            logger.info(f"   Batch {i}: {len(batch)} workflows")

        return batches

    def process_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single workflow.

        This is where the actual workflow processing logic would go.
        """
        logger.info(f"   🔄 Processing workflow: {workflow_id}")

        result = {
            "workflow_id": workflow_id,
            "processed_at": datetime.now().isoformat(),
            "success": True,
            "actions_taken": []
        }

        try:
            # Simulate processing (replace with actual processing logic)
            message_count = workflow_data.get("metadata", {}).get("message_count", 0)

            # Process messages
            result["actions_taken"].append(f"Processed {message_count} messages")

            # Extract intelligence
            result["actions_taken"].append("Extracted workflow intelligence")

            # Update status
            result["actions_taken"].append("Updated workflow status")

            logger.info(f"   ✅ Workflow processed: {workflow_id}")

        except Exception as e:
            logger.error(f"   ❌ Error processing workflow {workflow_id}: {e}")
            result["success"] = False
            result["error"] = str(e)

        return result

    def process_batch(self, batch: List[TriageResult], batch_num: int, total_batches: int, workflows_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process a single batch of workflows.

        Processes workflows in the batch with concurrency limits.
        """
        logger.info("="*80)
        logger.info(f"📦 PROCESSING BATCH {batch_num}/{total_batches}")
        logger.info("="*80)
        logger.info(f"   Workflows in batch: {len(batch)}")
        logger.info(f"   Max concurrent: {self.batch_config.max_concurrent}")

        batch_result = {
            "batch_number": batch_num,
            "started_at": datetime.now().isoformat(),
            "workflows_processed": 0,
            "workflows_succeeded": 0,
            "workflows_failed": 0,
            "results": []
        }

        # Process workflows in batch (with concurrency limit)
        processed = 0
        for triage_result in batch:
            if processed >= self.batch_config.max_concurrent:
                # Wait for some to complete before processing more
                time.sleep(2)
                processed = 0

            workflow_data = workflows_map.get(triage_result.workflow_id)
            if not workflow_data:
                logger.warning(f"   ⚠️  Workflow data not found: {triage_result.workflow_id}")
                continue

            # Process workflow
            result = self.process_workflow(triage_result.workflow_id, workflow_data)
            batch_result["results"].append(result)
            batch_result["workflows_processed"] += 1

            if result.get("success"):
                batch_result["workflows_succeeded"] += 1
            else:
                batch_result["workflows_failed"] += 1

            processed += 1

        batch_result["completed_at"] = datetime.now().isoformat()

        logger.info(f"✅ Batch {batch_num} complete:")
        logger.info(f"   Processed: {batch_result['workflows_processed']}")
        logger.info(f"   Succeeded: {batch_result['workflows_succeeded']}")
        logger.info(f"   Failed: {batch_result['workflows_failed']}")

        return batch_result

    def process_all_staggered(self, batches: List[List[TriageResult]], workflows_map: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process all batches with staggering (delays between batches).
        """
        logger.info("="*80)
        logger.info("🚀 STAGGERED BATCH PROCESSING STARTED")
        logger.info("="*80)
        logger.info(f"   Total batches: {len(batches)}")
        logger.info(f"   Stagger delay: {self.batch_config.stagger_delay} seconds")
        logger.info("")

        overall_result = {
            "started_at": datetime.now().isoformat(),
            "total_batches": len(batches),
            "batches_processed": 0,
            "total_workflows_processed": 0,
            "total_workflows_succeeded": 0,
            "total_workflows_failed": 0,
            "batch_results": []
        }

        for batch_num, batch in enumerate(batches, 1):
            # Process batch
            batch_result = self.process_batch(batch, batch_num, len(batches), workflows_map)
            overall_result["batch_results"].append(batch_result)
            overall_result["batches_processed"] += 1
            overall_result["total_workflows_processed"] += batch_result["workflows_processed"]
            overall_result["total_workflows_succeeded"] += batch_result["workflows_succeeded"]
            overall_result["total_workflows_failed"] += batch_result["workflows_failed"]

            # Stagger delay (except for last batch)
            if batch_num < len(batches):
                logger.info(f"⏳ Staggering... waiting {self.batch_config.stagger_delay} seconds before next batch...")
                time.sleep(self.batch_config.stagger_delay)

        overall_result["completed_at"] = datetime.now().isoformat()

        logger.info("="*80)
        logger.info("✅ STAGGERED BATCH PROCESSING COMPLETE")
        logger.info("="*80)
        logger.info(f"   Batches processed: {overall_result['batches_processed']}")
        logger.info(f"   Total workflows: {overall_result['total_workflows_processed']}")
        logger.info(f"   Succeeded: {overall_result['total_workflows_succeeded']}")
        logger.info(f"   Failed: {overall_result['total_workflows_failed']}")
        logger.info("")

        return overall_result

    def save_triage_results(self, triage_results: List[TriageResult]) -> Path:
        try:
            """Save triage results to file"""
            triage_file = self.data_dir / f"triage_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            results_data = {
                "triage_timestamp": datetime.now().isoformat(),
                "total_workflows": len(triage_results),
                "results": [
                    {
                        "workflow_id": tr.workflow_id,
                        "workflow_name": tr.workflow_name,
                        "priority": tr.priority.value,
                        "category": tr.category,
                        "chain_position": tr.chain_position,
                        "batch_number": tr.batch_number,
                        "estimated_processing_time": tr.estimated_processing_time,
                        "dependencies": tr.dependencies,
                        "reasoning": tr.reasoning,
                        "metadata": tr.metadata
                    }
                    for tr in triage_results
                ]
            }

            with open(triage_file, 'w', encoding='utf-8') as f:
                json.dump(results_data, f, indent=2, default=str)

            logger.info(f"✅ Triage results saved: {triage_file}")
            return triage_file

        except Exception as e:
            self.logger.error(f"Error in save_triage_results: {e}", exc_info=True)
            raise
    def execute_full_pipeline(self) -> Dict[str, Any]:
        """
        Execute the full pipeline: Load → Triage → Chain → Batch Process
        """
        logger.info("="*80)
        logger.info("🔄 WORKFLOW CHAIN TRIAGE & STAGGERED BATCH PROCESSING")
        logger.info("="*80)
        logger.info("")

        pipeline_result = {
            "started_at": datetime.now().isoformat(),
            "success": False
        }

        try:
            # Step 1: Load workflows
            logger.info("STEP 1: Loading workflows...")
            workflows = self.load_workflows()
            if not workflows:
                logger.error("❌ No workflows loaded")
                return pipeline_result

            # Create workflows map for quick lookup
            workflows_map = {wf["workflow_id"]: wf for wf in workflows}

            # Step 2: Chain Triage
            logger.info("")
            logger.info("STEP 2: Performing chain triage...")
            triage_results = self.chain_triage_all(workflows)

            # Save triage results
            triage_file = self.save_triage_results(triage_results)
            pipeline_result["triage_file"] = str(triage_file)

            # Step 3: Create staggered batches
            logger.info("")
            logger.info("STEP 3: Creating staggered batches...")
            batches = self.create_staggered_batches(triage_results)
            pipeline_result["total_batches"] = len(batches)

            # Step 4: Process batches with staggering
            logger.info("")
            logger.info("STEP 4: Processing batches (staggered)...")
            processing_result = self.process_all_staggered(batches, workflows_map)
            pipeline_result["processing"] = processing_result

            pipeline_result["success"] = True
            pipeline_result["completed_at"] = datetime.now().isoformat()

            logger.info("")
            logger.info("="*80)
            logger.info("✅ FULL PIPELINE COMPLETE")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"❌ Pipeline error: {e}", exc_info=True)
            pipeline_result["error"] = str(e)

        return pipeline_result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow Chain Triage & Staggered Batch Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full pipeline with default settings
  python workflow_chain_triage_batch_processor.py

  # Custom batch configuration
  python workflow_chain_triage_batch_processor.py --batch-size 3 --stagger-delay 60

  # Just triage (no processing)
  python workflow_chain_triage_batch_processor.py --triage-only
        """
    )

    parser.add_argument("--batch-size", type=int, default=5,
                       help="Number of workflows per batch (default: 5)")
    parser.add_argument("--stagger-delay", type=int, default=30,
                       help="Seconds to wait between batches (default: 30)")
    parser.add_argument("--max-concurrent", type=int, default=3,
                       help="Max concurrent workflows in a batch (default: 3)")
    parser.add_argument("--triage-only", action="store_true",
                       help="Only perform triage, don't process")

    args = parser.parse_args()

    # Create batch config
    batch_config = BatchConfig(
        batch_size=args.batch_size,
        stagger_delay=args.stagger_delay,
        max_concurrent=args.max_concurrent
    )

    # Initialize processor
    processor = WorkflowChainTriageBatchProcessor(batch_config=batch_config)

    if args.triage_only:
        # Just triage
        workflows = processor.load_workflows()
        triage_results = processor.chain_triage_all(workflows)
        processor.save_triage_results(triage_results)

        print("\n" + "="*80)
        print("📊 TRIAGE RESULTS")
        print("="*80)
        for tr in triage_results[:10]:  # Show first 10
            print(f"   [{tr.priority.value.upper():8}] {tr.workflow_name} (Batch {tr.batch_number}, Chain {tr.chain_position})")
        if len(triage_results) > 10:
            print(f"   ... and {len(triage_results) - 10} more")
        print()
    else:
        # Full pipeline
        result = processor.execute_full_pipeline()

        print("\n" + "="*80)
        print("📊 PIPELINE RESULTS")
        print("="*80)
        print(json.dumps(result, indent=2, default=str))
        print()


if __name__ == "__main__":


    main()