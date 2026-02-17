#!/usr/bin/env python3
"""
Codebase Cleanup Automation

Automated codebase cleanup system that:
- Removes duplicates
- Archives obsolete code
- Consolidates functionality
- Removes unused code

Part of Phase 2: Codebase Cleanup Automation
"""

import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CodebaseCleanupAutomation")

try:
    from codebase_cleanup_archive_obsolete import CodebaseCleanupArchive
    from jarvis_consolidation_analysis import JARVISConsolidationAnalyzer
    from analyze_codebase_intelligent_resume import analyze_codebase
    CLEANUP_TOOLS_AVAILABLE = True
except ImportError as e:
    CLEANUP_TOOLS_AVAILABLE = False
    logger.warning(f"Cleanup tools not available: {e}")


@dataclass
class CleanupTask:
    """A cleanup task to execute"""
    task_id: str
    task_type: str  # archive, consolidate, remove, deduplicate
    description: str
    target_files: List[str]
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1


@dataclass
class CleanupResult:
    """Result of cleanup operation"""
    task_id: str
    success: bool
    message: str
    files_processed: int = 0
    files_archived: int = 0
    files_removed: int = 0
    files_consolidated: int = 0
    errors: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


class CodebaseCleanupAutomation:
    """
    Automated codebase cleanup system

    Orchestrates all cleanup operations:
    - Archive obsolete code
    - Consolidate duplicate functionality
    - Remove unused code
    - Deduplicate files
    """

    def __init__(self, project_root: Path):
        """Initialize cleanup automation"""
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts" / "python"
        self.archive_system = None
        self.cleanup_tasks: List[CleanupTask] = []
        self.cleanup_history: List[CleanupResult] = []

        if CLEANUP_TOOLS_AVAILABLE:
            try:
                self.archive_system = CodebaseCleanupArchive(self.project_root)
            except Exception as e:
                logger.warning(f"Archive system not available: {e}")

        logger.info("Codebase Cleanup Automation initialized")

    def analyze_codebase(self) -> Dict[str, Any]:
        """Analyze codebase for cleanup opportunities"""
        analysis = {
            "timestamp": datetime.now().isoformat(),
            "obsolete_files": {},
            "duplicates": [],
            "consolidation_opportunities": {},
            "unused_code": []
        }

        # Analyze obsolete files (demos, tests, examples)
        if self.archive_system:
            obsolete = self.archive_system.identify_obsolete_files(self.scripts_dir)
            analysis["obsolete_files"] = {
                category: [str(f.relative_to(self.project_root)) for f in files]
                for category, files in obsolete.items()
            }

        # Analyze JARVIS consolidation
        try:
            jarvis_analyzer = JARVISConsolidationAnalyzer(self.project_root)
            jarvis_analysis = jarvis_analyzer.analyze_all()
            analysis["consolidation_opportunities"]["jarvis"] = jarvis_analysis["consolidation_plan"]
        except Exception as e:
            logger.warning(f"JARVIS analysis failed: {e}")

        # Analyze duplicates (using existing analyzer if available)
        try:
            # This would use analyze_codebase_intelligent_resume if available
            # For now, placeholder
            analysis["duplicates"] = []
        except Exception as e:
            logger.debug(f"Duplicate analysis not available: {e}")

        return analysis

    def generate_cleanup_plan(self, analysis: Dict[str, Any]) -> List[CleanupTask]:
        """Generate cleanup tasks from analysis"""
        tasks = []

        # Archive obsolete files
        obsolete_files = analysis.get("obsolete_files", {})
        for category, files in obsolete_files.items():
            if files:
                tasks.append(CleanupTask(
                    task_id=f"archive_{category}_{int(datetime.now().timestamp())}",
                    task_type="archive",
                    description=f"Archive {category} files",
                    target_files=files,
                    parameters={"category": category},
                    priority=1
                ))

        # Consolidate JARVIS scripts
        jarvis_plan = analysis.get("consolidation_opportunities", {}).get("jarvis", {})
        if jarvis_plan and jarvis_plan.get("archive_scripts"):
            tasks.append(CleanupTask(
                task_id=f"consolidate_jarvis_{int(datetime.now().timestamp())}",
                task_type="consolidate",
                description="Consolidate JARVIS orchestration scripts",
                target_files=jarvis_plan.get("archive_scripts", []),
                parameters={
                    "consolidate_into": jarvis_plan.get("consolidate_into"),
                    "plan": jarvis_plan
                },
                priority=2
            ))

        self.cleanup_tasks = tasks
        return tasks

    def execute_cleanup_task(self, task: CleanupTask, dry_run: bool = False) -> CleanupResult:
        """Execute a cleanup task"""
        start_time = datetime.now()

        try:
            if task.task_type == "archive":
                return self._execute_archive_task(task, dry_run)
            elif task.task_type == "consolidate":
                return self._execute_consolidate_task(task, dry_run)
            elif task.task_type == "remove":
                return self._execute_remove_task(task, dry_run)
            elif task.task_type == "deduplicate":
                return self._execute_deduplicate_task(task, dry_run)
            else:
                return CleanupResult(
                    task_id=task.task_id,
                    success=False,
                    message=f"Unknown task type: {task.task_type}",
                    errors=[f"Unsupported task type: {task.task_type}"]
                )
        except Exception as e:
            logger.error(f"Error executing cleanup task {task.task_id}: {e}", exc_info=True)
            return CleanupResult(
                task_id=task.task_id,
                success=False,
                message=f"Task failed: {str(e)}",
                errors=[str(e)]
            )

    def _execute_archive_task(self, task: CleanupTask, dry_run: bool) -> CleanupResult:
        try:
            """Execute archive task"""
            if not self.archive_system:
                return CleanupResult(
                    task_id=task.task_id,
                    success=False,
                    message="Archive system not available",
                    errors=["Archive system not initialized"]
                )

            category = task.parameters.get("category", "unknown")
            files_archived = 0
            errors = []

            for file_path_str in task.target_files:
                file_path = self.project_root / file_path_str
                if file_path.exists():
                    reason = f"Obsolete {category} file - automated cleanup"
                    success = self.archive_system.archive_file(
                        file_path, category, reason, dry_run=dry_run
                    )
                    if success:
                        files_archived += 1
                    else:
                        errors.append(f"Failed to archive: {file_path_str}")

            return CleanupResult(
                task_id=task.task_id,
                success=len(errors) == 0,
                message=f"Archived {files_archived} files" + (" (dry run)" if dry_run else ""),
                files_archived=files_archived,
                errors=errors
            )

        except Exception as e:
            self.logger.error(f"Error in _execute_archive_task: {e}", exc_info=True)
            raise
    def _execute_consolidate_task(self, task: CleanupTask, dry_run: bool) -> CleanupResult:
        try:
            """Execute consolidate task"""
            # For consolidation, we archive the scripts to be consolidated
            # Actual consolidation (merging code) would be a separate manual step
            if not self.archive_system:
                return CleanupResult(
                    task_id=task.task_id,
                    success=False,
                    message="Archive system not available",
                    errors=["Archive system not initialized"]
                )

            consolidate_into = task.parameters.get("consolidate_into", "")
            files_archived = 0
            errors = []

            for file_path_str in task.target_files:
                file_path = self.project_root / file_path_str
                if file_path.exists():
                    reason = f"Consolidation candidate - merge into {consolidate_into}"
                    success = self.archive_system.archive_file(
                        file_path, "consolidation", reason, dry_run=dry_run
                    )
                    if success:
                        files_archived += 1
                    else:
                        errors.append(f"Failed to archive: {file_path_str}")

            return CleanupResult(
                task_id=task.task_id,
                success=len(errors) == 0,
                message=f"Archived {files_archived} files for consolidation" + (" (dry run)" if dry_run else ""),
                files_archived=files_archived,
                errors=errors
            )

        except Exception as e:
            self.logger.error(f"Error in _execute_consolidate_task: {e}", exc_info=True)
            raise
    def _execute_remove_task(self, task: CleanupTask, dry_run: bool) -> CleanupResult:
        """Execute remove task"""
        # Removal should be done via archive, not direct deletion
        # This is a safety measure
        return CleanupResult(
            task_id=task.task_id,
            success=False,
            message="Direct removal not supported - use archive instead",
            errors=["Direct file removal disabled for safety"]
        )

    def _execute_deduplicate_task(self, task: CleanupTask, dry_run: bool) -> CleanupResult:
        """Execute deduplicate task"""
        # Placeholder - would implement duplicate detection and removal
        return CleanupResult(
            task_id=task.task_id,
            success=False,
            message="Deduplication not yet implemented",
            errors=["Deduplication feature not implemented"]
        )

    def run_full_cleanup(self, dry_run: bool = False) -> Dict[str, Any]:
        """Run full automated cleanup"""
        logger.info("Starting full codebase cleanup" + (" (dry run)" if dry_run else ""))

        # Analyze
        analysis = self.analyze_codebase()

        # Generate plan
        tasks = self.generate_cleanup_plan(analysis)

        # Execute tasks
        results = []
        for task in tasks:
            result = self.execute_cleanup_task(task, dry_run=dry_run)
            results.append(result)
            self.cleanup_history.append(result)

        # Summary
        summary = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "tasks_executed": len(tasks),
            "tasks_successful": sum(1 for r in results if r.success),
            "tasks_failed": sum(1 for r in results if not r.success),
            "total_files_archived": sum(r.files_archived for r in results),
            "total_files_consolidated": sum(r.files_consolidated for r in results),
            "results": [
                {
                    "task_id": r.task_id,
                    "success": r.success,
                    "message": r.message,
                    "files_archived": r.files_archived,
                    "files_consolidated": r.files_consolidated
                }
                for r in results
            ]
        }

        logger.info(f"Cleanup complete: {summary['tasks_successful']}/{summary['tasks_executed']} tasks successful")
        return summary


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Codebase Cleanup Automation")
        parser.add_argument("--analyze", action="store_true", help="Analyze codebase")
        parser.add_argument("--plan", action="store_true", help="Generate cleanup plan")
        parser.add_argument("--cleanup", action="store_true", help="Run cleanup")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (don't actually clean)")
        parser.add_argument("--output", type=Path, help="Output JSON file")

        args = parser.parse_args()

        automation = CodebaseCleanupAutomation(project_root)

        if args.analyze:
            analysis = automation.analyze_codebase()
            output = json.dumps(analysis, indent=2)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Analysis saved to: {args.output}")
            else:
                print(output)
            return

        if args.plan:
            analysis = automation.analyze_codebase()
            tasks = automation.generate_cleanup_plan(analysis)
            plan = {
                "timestamp": datetime.now().isoformat(),
                "tasks": [
                    {
                        "task_id": t.task_id,
                        "type": t.task_type,
                        "description": t.description,
                        "target_files": t.target_files,
                        "priority": t.priority
                    }
                    for t in tasks
                ]
            }
            output = json.dumps(plan, indent=2)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Plan saved to: {args.output}")
            else:
                print(output)
            return

        if args.cleanup:
            summary = automation.run_full_cleanup(dry_run=args.dry_run)
            output = json.dumps(summary, indent=2)
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(output)
                print(f"Cleanup summary saved to: {args.output}")
            else:
                print(output)
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()