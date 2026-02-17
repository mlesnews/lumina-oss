#!/usr/bin/env python3
"""
@MARVIN Dropbox Cleanup Executor

Automatically executes the full Dropbox cleanup plan using @SYPHON and decision tree logic.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import json
import shutil

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinDropboxCleanupExecutor")

try:
    from marvin_dropbox_cleanup import MarvinDropboxCleanup, DropboxIssue
except ImportError:
    logger.error("❌ Could not import marvin_dropbox_cleanup")
    MarvinDropboxCleanup = None

try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
except ImportError:
    logger.warning("⚠️  universal_decision_tree not available")
    decide = None

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, DataSourceType, SubscriptionTier
except ImportError:
    logger.warning("⚠️  SYPHON system not available")
    SYPHONSystem = None


class MarvinDropboxCleanupExecutor:
    """
    Executes Dropbox cleanup plan using @SYPHON and decision tree logic.
    """

    def __init__(self, dropbox_root: Optional[Path] = None, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.dropbox_root = dropbox_root or Path.home() / "Dropbox"

        self.logger = get_logger("MarvinDropboxCleanupExecutor")

        self.data_dir = self.project_root / "data" / "dropbox_cleanup"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize cleanup analyzer
        if MarvinDropboxCleanup:
            self.cleanup = MarvinDropboxCleanup(dropbox_root=dropbox_root, project_root=project_root)
        else:
            self.cleanup = None

        # Initialize SYPHON
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

        self.logger.info("😟 @MARVIN Dropbox Cleanup Executor initialized")

    def syphon_dropbox_structure(self) -> Dict[str, Any]:
        """@SYPHON: Extract Dropbox structure data"""
        if not self.syphon:
            self.logger.warning("⚠️  SYPHON not available, skipping extraction")
            return {}

        self.logger.info("🔍 @SYPHON: Extracting Dropbox structure...")

        try:
            # Extract folder structure
            dropbox_data = {
                "source": "dropbox_cleanup",
                "dropbox_root": str(self.dropbox_root),
                "timestamp": datetime.now().isoformat(),
                "structure": self._extract_folder_structure(self.dropbox_root)
            }

            # Save to SYPHON
            from syphon.core import SyphonData
            syphon_data = SyphonData(
                data_id=f"dropbox_structure_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                source_type=DataSourceType.FILE_SYSTEM,
                source_id=str(self.dropbox_root),
                content=json.dumps(dropbox_data, indent=2),
                metadata={"type": "dropbox_structure", "dropbox_root": str(self.dropbox_root)},
                extracted_at=datetime.now(),
                actionable_items=[],
                tasks=[],
                decisions=[],
                intelligence=["Dropbox structure extracted for cleanup analysis"]
            )

            self.syphon.storage.save(syphon_data)
            self.logger.info("✅ @SYPHON: Dropbox structure extracted")

            return dropbox_data

        except Exception as e:
            self.logger.error(f"❌ @SYPHON extraction error: {e}")
            return {}

    def _extract_folder_structure(self, root: Path, max_depth: int = 3) -> Dict[str, Any]:
        """Extract folder structure recursively"""
        structure = {
            "path": str(root),
            "name": root.name,
            "is_dir": root.is_dir(),
            "children": []
        }

        if not root.exists() or not root.is_dir():
            return structure

        try:
            for item in root.iterdir():
                if item.is_dir() and max_depth > 0:
                    child_structure = self._extract_folder_structure(item, max_depth - 1)
                    structure["children"].append(child_structure)
                elif item.is_file():
                    structure["children"].append({
                        "path": str(item),
                        "name": item.name,
                        "is_dir": False,
                        "size": item.stat().st_size if item.exists() else 0
                    })
        except PermissionError:
            pass
        except Exception as e:
            self.logger.debug(f"Error extracting {root}: {e}")

        return structure

    def decide_cleanup_action(self, issue: DropboxIssue) -> Dict[str, Any]:
        """Use decision tree to decide cleanup action"""
        if not decide:
            # Fallback decision
            return {
                "action": "review",
                "confidence": 0.5,
                "reason": "Decision tree not available, manual review required"
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

    def create_backup(self) -> bool:
        try:
            """Create backup before cleanup"""
            self.logger.info("💾 Creating backup...")

            backup_dir = self.data_dir / "backups" / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            backup_dir.mkdir(parents=True, exist_ok=True)

            # Create backup manifest
            manifest = {
                "timestamp": datetime.now().isoformat(),
                "dropbox_root": str(self.dropbox_root),
                "backup_location": str(backup_dir),
                "note": "Backup created before Dropbox cleanup execution"
            }

            manifest_file = backup_dir / "backup_manifest.json"
            with open(manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            self.backup_location = backup_dir
            self.logger.info(f"✅ Backup manifest created: {backup_dir}")
            self.logger.warning("⚠️  NOTE: Full file backup not implemented (would be very large)")
            self.logger.info("   Recommendation: Create full backup manually before execution")

            return True

        except Exception as e:
            self.logger.error(f"Error in create_backup: {e}", exc_info=True)
            raise
    def execute_cleanup_plan(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            """Execute the full cleanup plan"""
            if not self.cleanup:
                self.logger.error("❌ Cleanup analyzer not available")
                return {}

            self.logger.info("😟 @MARVIN: Executing Dropbox cleanup plan...")

            # Step 1: @SYPHON extraction
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 1: @SYPHON EXTRACTION")
            self.logger.info("="*80)
            syphon_data = self.syphon_dropbox_structure()

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
                self.create_backup()

            # Step 5: Execute phases
            self.logger.info("\n" + "="*80)
            self.logger.info("STEP 5: EXECUTION")
            self.logger.info("="*80)

            execution_results = {
                "timestamp": datetime.now().isoformat(),
                "dry_run": dry_run,
                "phases": []
            }

            for phase in plan["phases"]:
                phase_result = self._execute_phase(phase, dry_run)
                execution_results["phases"].append(phase_result)

            # Save execution log
            log_file = self.data_dir / f"execution_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(execution_results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"\n📁 Execution log saved: {log_file}")

            return execution_results

        except Exception as e:
            self.logger.error(f"Error in execute_cleanup_plan: {e}", exc_info=True)
            raise
    def _execute_phase(self, phase: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """Execute a single cleanup phase"""
        phase_name = phase["name"]
        self.logger.info(f"\n📋 Executing Phase {phase['phase']}: {phase_name}")

        phase_result = {
            "phase": phase["phase"],
            "name": phase_name,
            "issues_processed": 0,
            "actions_taken": [],
            "errors": []
        }

        for issue_dict in phase.get("issues", []):
            # Convert dict back to DropboxIssue if needed
            if isinstance(issue_dict, dict):
                issue = DropboxIssue(**issue_dict)
            else:
                issue = issue_dict

            self.logger.info(f"\n  Processing: {issue.description}")
            self.logger.info(f"    Path: {issue.path}")
            self.logger.info(f"    Suggested: {issue.suggested_action}")

            # Use decision tree
            decision = self.decide_cleanup_action(issue)
            self.logger.info(f"    Decision: {decision['action']} (confidence: {decision['confidence']:.2f})")

            # Execute action
            if not dry_run and decision["confidence"] > 0.7:
                action_result = self._execute_action(issue, decision)
                phase_result["actions_taken"].append(action_result)
            else:
                self.logger.info(f"    ⏸️  Skipped (dry_run={dry_run}, confidence={decision['confidence']:.2f})")
                phase_result["actions_taken"].append({
                    "issue_id": issue.issue_id,
                    "action": decision["action"],
                    "status": "skipped",
                    "reason": "Dry run or low confidence"
                })

            phase_result["issues_processed"] += 1

        self.logger.info(f"\n✅ Phase {phase['phase']} complete: {phase_result['issues_processed']} issues processed")

        return phase_result

    def _execute_action(self, issue: DropboxIssue, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a cleanup action"""
        action = decision["action"]
        issue_path = Path(issue.path)

        action_result = {
            "issue_id": issue.issue_id,
            "action": action,
            "path": issue.path,
            "timestamp": datetime.now().isoformat(),
            "status": "unknown",
            "error": None
        }

        try:
            if action == "remove" and issue_path.exists():
                # Remove duplicate/nested folder
                if issue_path.is_dir():
                    shutil.rmtree(issue_path)
                    action_result["status"] = "removed"
                    self.logger.info(f"    ✅ Removed: {issue_path}")
                else:
                    issue_path.unlink()
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
                    action_result["status"] = "archived"
                    action_result["archive_location"] = str(archive_path)
                    self.logger.info(f"    ✅ Archived: {issue_path} → {archive_path}")

            elif action == "merge":
                # Merge logic would go here
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

        return action_result


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="@MARVIN Dropbox Cleanup Executor")
        parser.add_argument("--execute", action="store_true", help="Execute cleanup plan")
        parser.add_argument("--dry-run", action="store_true", help="Dry run (no changes)")
        parser.add_argument("--dropbox-root", help="Dropbox root path")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("😟 @MARVIN DROPBOX CLEANUP EXECUTOR")
        print("="*80 + "\n")

        dropbox_root = Path(args.dropbox_root) if args.dropbox_root else None
        executor = MarvinDropboxCleanupExecutor(dropbox_root=dropbox_root)

        if args.execute or args.dry_run:
            dry_run = args.dry_run
            if dry_run:
                print("⚠️  DRY RUN MODE - No changes will be made\n")

            results = executor.execute_cleanup_plan(dry_run=dry_run)

            print("\n" + "="*80)
            print("✅ EXECUTION COMPLETE")
            print("="*80 + "\n")

            for phase in results.get("phases", []):
                print(f"Phase {phase['phase']}: {phase['name']}")
                print(f"  Issues processed: {phase['issues_processed']}")
                print(f"  Actions taken: {len(phase['actions_taken'])}")
                print()

        else:
            print("Usage:")
            print("  --execute       : Execute cleanup plan")
            print("  --dry-run       : Dry run (no changes)")
            print("  --dropbox-root  : Specify Dropbox root path")
            print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":




    main()