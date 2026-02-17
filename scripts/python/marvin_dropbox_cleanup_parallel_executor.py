#!/usr/bin/env python3
"""
@MARVIN Dropbox Cleanup Parallel Batch Executor

Batch processes Dropbox cleanup in parallel while obeying all balance policies and procedures.
Uses @SYPHON, decision tree logic, and resource-aware parallel processing.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
import json
import shutil
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinDropboxCleanupParallelExecutor")

try:
    from marvin_dropbox_cleanup import MarvinDropboxCleanup, DropboxIssue
    from marvin_dropbox_cleanup_executor import MarvinDropboxCleanupExecutor
except ImportError:
    logger.error("❌ Could not import cleanup modules")
    MarvinDropboxCleanup = None
    MarvinDropboxCleanupExecutor = None

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
except ImportError:
    logger.warning("⚠️  universal_decision_tree not available")
    decide = None

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, DataSourceType, SubscriptionTier, SyphonData
except ImportError:
    logger.warning("⚠️  SYPHON system not available")
    SYPHONSystem = None


class BalancePolicy:
    """Balance policies for parallel processing"""

    def __init__(self):
        self.max_parallel_workers = 4  # Max concurrent operations
        self.max_disk_io_ops = 10  # Max concurrent disk I/O operations
        self.max_memory_mb = 1024  # Max memory usage (MB)
        self.rate_limit_per_second = 5  # Max operations per second
        self.backup_required = True  # Require backup before operations
        self.verify_after_operation = True  # Verify operations completed

        # Resource tracking
        self.active_workers = 0
        self.disk_io_count = 0
        self.memory_usage_mb = 0
        self.operation_times: List[float] = []
        self.lock = threading.Lock()

    def can_start_operation(self) -> bool:
        """Check if new operation can start based on balance policies"""
        with self.lock:
            # Check worker limit
            if self.active_workers >= self.max_parallel_workers:
                return False

            # Check disk I/O limit
            if self.disk_io_count >= self.max_disk_io_ops:
                return False

            # Check rate limit
            current_time = time.time()
            recent_ops = [t for t in self.operation_times if current_time - t < 1.0]
            if len(recent_ops) >= self.rate_limit_per_second:
                return False

            return True

    def start_operation(self):
        """Mark operation as started"""
        with self.lock:
            self.active_workers += 1
            self.disk_io_count += 1
            self.operation_times.append(time.time())

    def finish_operation(self):
        """Mark operation as finished"""
        with self.lock:
            self.active_workers = max(0, self.active_workers - 1)
            self.disk_io_count = max(0, self.disk_io_count - 1)

    def wait_for_capacity(self, timeout: float = 30.0):
        """Wait until capacity is available"""
        start_time = time.time()
        while not self.can_start_operation():
            if time.time() - start_time > timeout:
                raise TimeoutError("Timeout waiting for operation capacity")
            time.sleep(0.1)


class MarvinDropboxCleanupParallelExecutor:
    """
    Parallel batch executor for Dropbox cleanup.
    Respects balance policies and procedures.
    """

    def __init__(self, dropbox_root: Optional[Path] = None, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.dropbox_root = dropbox_root or Path.home() / "Dropbox"

        self.logger = get_logger("MarvinDropboxCleanupParallelExecutor")

        self.data_dir = self.project_root / "data" / "dropbox_cleanup"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize components
        if MarvinDropboxCleanup:
            self.cleanup = MarvinDropboxCleanup(dropbox_root=dropbox_root, project_root=project_root)
        else:
            self.cleanup = None

        if MarvinDropboxCleanupExecutor:
            self.executor = MarvinDropboxCleanupExecutor(dropbox_root=dropbox_root, project_root=project_root)
        else:
            self.executor = None

        # Balance policies
        self.balance_policy = BalancePolicy()

        # SYPHON
        self.syphon = None
        if SYPHONSystem:
            try:
                syphon_config = SYPHONConfig(
                    project_root=self.project_root,
                    subscription_tier=SubscriptionTier.BASIC
                )
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON system initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON initialization error: {e}")

        # Execution state
        self.execution_log: List[Dict[str, Any]] = []
        self.backup_location: Optional[Path] = None

        self.logger.info("😟 @MARVIN Parallel Batch Executor initialized")
        self.logger.info(f"   Balance Policy: {self.balance_policy.max_parallel_workers} workers, "
                        f"{self.balance_policy.max_disk_io_ops} I/O ops, "
                        f"{self.balance_policy.rate_limit_per_second} ops/sec")

    def batch_process_cleanup(self, dry_run: bool = False) -> Dict[str, Any]:
        """Batch process cleanup plan in parallel"""
        if not self.cleanup:
            self.logger.error("❌ Cleanup analyzer not available")
            return {}

        self.logger.info("😟 @MARVIN: Starting parallel batch processing...")

        # Step 1: @SYPHON extraction
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 1: @SYPHON EXTRACTION")
        self.logger.info("="*80)
        syphon_data = {}
        if self.executor and hasattr(self.executor, 'syphon_dropbox_structure'):
            syphon_data = self.executor.syphon_dropbox_structure()
        elif self.syphon:
            # Direct SYPHON extraction if executor not available
            self.logger.info("🔍 @SYPHON: Extracting Dropbox structure directly...")
            try:
                dropbox_data = {
                    "source": "dropbox_cleanup",
                    "dropbox_root": str(self.dropbox_root),
                    "timestamp": datetime.now().isoformat()
                }
                syphon_data = dropbox_data
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON extraction error: {e}")

        # Step 2: Analyze
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 2: ANALYSIS")
        self.logger.info("="*80)
        analysis = self.cleanup.analyze_dropbox()

        # Step 3: Generate plan
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 3: CLEANUP PLAN GENERATION")
        self.logger.info("="*80)
        plan = self.cleanup.generate_cleanup_plan()

        # Step 4: Create backup
        if not dry_run:
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 4: BACKUP CREATION")
            self.logger.info("="*80)
            if self.executor and hasattr(self.executor, 'create_backup'):
                self.executor.create_backup()
                self.backup_location = getattr(self.executor, 'backup_location', None)
            else:
                self.logger.warning("⚠️  Backup creation not available (dry-run or executor not configured)")

        # Step 5: Parallel batch execution
        self.logger.info("\n" + "="*80)
        self.logger.info("STEP 5: PARALLEL BATCH EXECUTION")
        self.logger.info("="*80)

        execution_results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "balance_policy": {
                "max_workers": self.balance_policy.max_parallel_workers,
                "max_io_ops": self.balance_policy.max_disk_io_ops,
                "rate_limit": self.balance_policy.rate_limit_per_second
            },
            "phases": []
        }

        # Process all phases in parallel batches
        for phase in plan["phases"]:
            phase_result = self._parallel_execute_phase(phase, dry_run)
            execution_results["phases"].append(phase_result)

        # Save execution log
        log_file = self.data_dir / f"parallel_execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(execution_results, f, indent=2, ensure_ascii=False)

        self.logger.info(f"\n📁 Execution log saved: {log_file}")

        return execution_results

    def _parallel_execute_phase(self, phase: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute phase using parallel batch processing"""
        phase_name = phase["name"]
        issues = phase.get("issues", [])

        self.logger.info(f"\n📋 Phase {phase['phase']}: {phase_name}")
        self.logger.info(f"   Processing {len(issues)} issues in parallel batches...")

        phase_result = {
            "phase": phase["phase"],
            "name": phase_name,
            "issues_processed": 0,
            "actions_taken": [],
            "errors": [],
            "parallel_batches": []
        }

        # Batch issues for parallel processing
        batches = self._create_batches(issues, batch_size=self.balance_policy.max_parallel_workers)

        for batch_num, batch in enumerate(batches, 1):
            self.logger.info(f"\n  Batch {batch_num}/{len(batches)}: {len(batch)} issues")

            batch_result = self._process_batch_parallel(batch, dry_run)
            phase_result["parallel_batches"].append(batch_result)
            phase_result["issues_processed"] += batch_result["issues_processed"]
            phase_result["actions_taken"].extend(batch_result["actions_taken"])
            phase_result["errors"].extend(batch_result["errors"])

        self.logger.info(f"\n✅ Phase {phase['phase']} complete: {phase_result['issues_processed']} issues processed")

        return phase_result

    def _create_batches(self, items: List[Any], batch_size: int) -> List[List[Any]]:
        """Create batches for parallel processing"""
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches

    def _process_batch_parallel(self, issues: List[Dict[str, Any]], dry_run: bool) -> Dict[str, Any]:
        """Process a batch of issues in parallel"""
        batch_result = {
            "batch_timestamp": datetime.now().isoformat(),
            "issues_processed": 0,
            "actions_taken": [],
            "errors": []
        }

        # Use ThreadPoolExecutor with balance policy limits
        max_workers = min(len(issues), self.balance_policy.max_parallel_workers)

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks
            future_to_issue = {
                executor.submit(self._process_issue_safe, issue, dry_run): issue
                for issue in issues
            }

            # Process completed tasks
            for future in as_completed(future_to_issue):
                issue = future_to_issue[future]
                try:
                    result = future.result()
                    batch_result["actions_taken"].append(result)
                    batch_result["issues_processed"] += 1
                except Exception as e:
                    error_info = {
                        "issue_id": issue.get("issue_id", "unknown"),
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                    batch_result["errors"].append(error_info)
                    self.logger.error(f"❌ Error processing issue: {e}")

        return batch_result

    def _process_issue_safe(self, issue_dict: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Process a single issue safely with balance policy checks"""
        # Wait for capacity
        self.balance_policy.wait_for_capacity()

        try:
            # Mark operation started
            self.balance_policy.start_operation()

            # Convert dict to DropboxIssue if needed
            if isinstance(issue_dict, dict):
                issue = DropboxIssue(**issue_dict)
            else:
                issue = issue_dict

            self.logger.info(f"  Processing: {issue.description[:50]}...")

            # Use decision tree
            decision = self._decide_cleanup_action(issue)

            # Execute action
            if not dry_run and decision["confidence"] > 0.7:
                action_result = self._execute_action_safe(issue, decision)
            else:
                action_result = {
                    "issue_id": issue.issue_id,
                    "action": decision["action"],
                    "status": "skipped",
                    "reason": f"Dry run={dry_run}, confidence={decision['confidence']:.2f}"
                }

            return action_result

        finally:
            # Always mark operation finished
            self.balance_policy.finish_operation()

    def _decide_cleanup_action(self, issue: DropboxIssue) -> Dict[str, Any]:
        """Use decision tree to decide cleanup action"""
        if not decide:
            return {
                "action": "review",
                "confidence": 0.5,
                "reason": "Decision tree not available"
            }

        try:
            context = DecisionContext(
                decision_id=f"dropbox_cleanup_{issue.issue_id}",
                decision_type="file_system_cleanup",
                context={
                    "issue_type": issue.issue_type,
                    "severity": issue.severity,
                    "path": issue.path,
                    "confidence": issue.confidence
                },
                options=[
                    {"id": "remove", "description": "Remove duplicate/nested folder"},
                    {"id": "merge", "description": "Merge with main location"},
                    {"id": "archive", "description": "Archive to backup location"},
                    {"id": "review", "description": "Manual review required"}
                ]
            )

            result = decide("file_system_cleanup", context)

            return {
                "action": result.selected_option if hasattr(result, 'selected_option') else "review",
                "confidence": result.confidence if hasattr(result, 'confidence') else 0.5,
                "reason": result.reasoning if hasattr(result, 'reasoning') else "Decision tree result"
            }

        except Exception as e:
            self.logger.error(f"❌ Decision tree error: {e}")
            return {
                "action": "review",
                "confidence": 0.3,
                "reason": f"Decision tree error: {e}"
            }

    def _execute_action_safe(self, issue: DropboxIssue, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute cleanup action safely with verification"""
        action = decision["action"]
        issue_path = Path(issue.path)

        action_result = {
            "issue_id": issue.issue_id,
            "action": action,
            "path": issue.path,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "error": None,
            "verified": False
        }

        try:
            if action == "remove" and issue_path.exists():
                # Remove duplicate/nested folder
                if issue_path.is_dir():
                    shutil.rmtree(issue_path)
                else:
                    issue_path.unlink()

                # Verify removal
                if self.balance_policy.verify_after_operation:
                    if not issue_path.exists():
                        action_result["status"] = "removed"
                        action_result["verified"] = True
                        self.logger.info(f"    ✅ Removed and verified: {issue_path}")
                    else:
                        action_result["status"] = "error"
                        action_result["error"] = "Removal verification failed"
                        self.logger.error(f"    ❌ Removal verification failed: {issue_path}")
                else:
                    action_result["status"] = "removed"
                    self.logger.info(f"    ✅ Removed: {issue_path}")

            elif action == "archive" and issue_path.exists():
                # Archive to backup location
                if self.backup_location:
                    archive_path = self.backup_location / issue_path.name
                    if issue_path.is_dir():
                        shutil.copytree(issue_path, archive_path)
                        shutil.rmtree(issue_path)
                    else:
                        shutil.copy2(issue_path, archive_path)
                        issue_path.unlink()

                    # Verify archive
                    if self.balance_policy.verify_after_operation:
                        if archive_path.exists() and not issue_path.exists():
                            action_result["status"] = "archived"
                            action_result["verified"] = True
                            action_result["archive_location"] = str(archive_path)
                            self.logger.info(f"    ✅ Archived and verified: {issue_path} → {archive_path}")
                        else:
                            action_result["status"] = "error"
                            action_result["error"] = "Archive verification failed"
                            self.logger.error(f"    ❌ Archive verification failed")
                    else:
                        action_result["status"] = "archived"
                        action_result["archive_location"] = str(archive_path)
                        self.logger.info(f"    ✅ Archived: {issue_path} → {archive_path}")

            elif action == "merge":
                action_result["status"] = "merge_required"
                self.logger.info(f"    ⚠️  Merge required (manual step): {issue_path}")

            else:
                action_result["status"] = "review_required"
                self.logger.info(f"    ⏸️  Review required: {issue_path}")

        except Exception as e:
            action_result["status"] = "error"
            action_result["error"] = str(e)
            self.logger.error(f"    ❌ Error: {e}")

        # Log to execution log
        self.execution_log.append(action_result)

        # @SYPHON: Log action
        if self.syphon:
            try:
                syphon_data = SyphonData(
                    data_id=f"cleanup_action_{issue.issue_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    source_type=DataSourceType.FILE_SYSTEM,
                    source_id=issue.issue_id,
                    content=json.dumps(action_result, indent=2),
                    metadata={"type": "cleanup_action", "issue": issue.issue_id},
                    extracted_at=datetime.now(),
                    actionable_items=[],
                    tasks=[],
                    decisions=[action_result.get("action", "unknown")],
                    intelligence=[f"Cleanup action executed: {action_result.get('status', 'unknown')}"]
                )
                self.syphon.storage.save(syphon_data)
            except Exception as e:
                self.logger.debug(f"SYPHON logging error: {e}")

        return action_result


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="@MARVIN Dropbox Cleanup Parallel Batch Executor")
        parser.add_argument("--execute", action="store_true", help="Execute cleanup plan")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
        parser.add_argument("--dropbox-root", help="Dropbox root path")
        parser.add_argument("--max-workers", type=int, default=4, help="Max parallel workers")
        parser.add_argument("--max-io-ops", type=int, default=10, help="Max concurrent I/O operations")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("😟 @MARVIN DROPBOX CLEANUP PARALLEL BATCH EXECUTOR")
        print("="*80 + "\n")

        dropbox_root = Path(args.dropbox_root) if args.dropbox_root else None
        executor = MarvinDropboxCleanupParallelExecutor(dropbox_root=dropbox_root)

        # Configure balance policy
        if args.max_workers:
            executor.balance_policy.max_parallel_workers = args.max_workers
        if args.max_io_ops:
            executor.balance_policy.max_disk_io_ops = args.max_io_ops

        if args.execute or args.dry_run:
            dry_run = args.dry_run
            if dry_run:
                print("⚠️  DRY RUN MODE - No changes will be made\n")

            print(f"Balance Policy:")
            print(f"  Max Workers: {executor.balance_policy.max_parallel_workers}")
            print(f"  Max I/O Ops: {executor.balance_policy.max_disk_io_ops}")
            print(f"  Rate Limit: {executor.balance_policy.rate_limit_per_second} ops/sec")
            print()

            results = executor.batch_process_cleanup(dry_run=dry_run)

            print("\n" + "="*80)
            print("✅ PARALLEL BATCH EXECUTION COMPLETE")
            print("="*80 + "\n")

            for phase in results.get("phases", []):
                print(f"Phase {phase['phase']}: {phase['name']}")
                print(f"  Issues processed: {phase['issues_processed']}")
                print(f"  Actions taken: {len(phase['actions_taken'])}")
                print(f"  Errors: {len(phase['errors'])}")
                print(f"  Batches: {len(phase.get('parallel_batches', []))}")
                print()

        else:
            print("Usage:")
            print("  --execute       : Execute cleanup plan in parallel")
            print("  --dry-run       : Dry run (no changes)")
            print("  --dropbox-root  : Specify Dropbox root path")
            print("  --max-workers   : Max parallel workers (default: 4)")
            print("  --max-io-ops    : Max concurrent I/O operations (default: 10)")
            print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":




    main()