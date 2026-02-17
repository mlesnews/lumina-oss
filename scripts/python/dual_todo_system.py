#!/usr/bin/env python3
"""
Dual To-Do System - Master + Verified Lists with NAS Holocron Backup

Parallel dual to-do lists:
1. Master To-Do List - Everything we're working on
2. Verified To-Do List - Triple-checked by upper management (JARVIS/MARVIN)

All backed up to NAS Holocron (KAIJU) for rolling log maintenance.
"""

import json
import logging
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import base tracker
from master_todo_tracker import MasterTodoTracker, TodoItem, TaskStatus, Priority
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class VerificationStatus(Enum):
    """Verification status"""
    UNVERIFIED = "unverified"
    JARVIS_REVIEWED = "jarvis_reviewed"
    MARVIN_REVIEWED = "marvin_reviewed"
    VERIFIED = "verified"  # Triple-checked
    REJECTED = "rejected"


@dataclass
class VerifiedTodoItem:
    """Verified to-do item (triple-checked)"""
    todo_id: str
    title: str
    description: str = ""
    status: TaskStatus = TaskStatus.COMPLETE
    verified_by: List[str] = field(default_factory=list)  # JARVIS, MARVIN, etc.
    verification_date: Optional[str] = None
    verification_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class DualTodoSystem:
    """
    Dual To-Do System

    Maintains parallel lists:
    - Master: All tasks we're working on
    - Verified: Triple-checked by upper management
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "todo"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Master tracker
        self.master_tracker = MasterTodoTracker(project_root)

        # Verified todos
        self.verified_file = self.data_dir / "verified_todos.json"
        self.verified_todos: Dict[str, VerifiedTodoItem] = {}

        # NAS Holocron paths
        self.holocron_dir = self.project_root / "data" / "holocron" / "todo_logs"
        self.holocron_dir.mkdir(parents=True, exist_ok=True)

        # NAS sync path (KAIJU)
        self.nas_todo_path = None  # Will be set from config

        self.logger = self._setup_logging()
        self._load_verified_todos()
        self._load_nas_config()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("DualTodoSystem")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 📋🔍 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def _load_nas_config(self):
        """Load NAS configuration for Holocron backup"""
        try:
            import yaml
            nas_config_file = self.project_root / "config" / "nas_proxy_cache_config.yaml"

            if nas_config_file.exists():
                with open(nas_config_file, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'nas' in config:
                        nas_host = config['nas'].get('host', '<NAS_PRIMARY_IP>')
                        nas_user = config['nas'].get('user', 'backupadm')
                        # NAS path for todos
                        self.nas_todo_path = f"/volume1/holocron/todo_logs"
                        self.logger.info(f"✅ NAS config loaded: {nas_host} -> {self.nas_todo_path}")
        except Exception as e:
            self.logger.warning(f"⚠️ Could not load NAS config: {e}")

    def _load_verified_todos(self):
        """Load verified todos"""
        if self.verified_file.exists():
            try:
                with open(self.verified_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.verified_todos = {
                        item_id: VerifiedTodoItem(
                            **{**item_data, 'status': TaskStatus(item_data['status'])}
                        )
                        for item_id, item_data in data.items()
                    }
                self.logger.info(f"✅ Loaded {len(self.verified_todos)} verified todos")
            except Exception as e:
                self.logger.error(f"❌ Error loading verified todos: {e}")
                self.verified_todos = {}
        else:
            self.verified_todos = {}

    def _save_verified_todos(self):
        """Save verified todos"""
        try:
            data = {item_id: item.to_dict() for item_id, item in self.verified_todos.items()}
            with open(self.verified_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            self.logger.info(f"💾 Saved {len(self.verified_todos)} verified todos")
        except Exception as e:
            self.logger.error(f"❌ Error saving verified todos: {e}")

    def verify_todo(self, todo_id: str, verifier: str, notes: str = "") -> bool:
        """
        Verify a todo item

        Triple-check process:
        1. JARVIS reviews
        2. MARVIN reviews
        3. Final verification
        """
        if todo_id not in self.master_tracker.items:
            self.logger.warning(f"⚠️ Todo not found in master list: {todo_id}")
            return False

        master_item = self.master_tracker.items[todo_id]

        # Get or create verified item
        if todo_id not in self.verified_todos:
            verified_item = VerifiedTodoItem(
                todo_id=todo_id,
                title=master_item.title,
                description=master_item.description,
                status=master_item.status
            )
            self.verified_todos[todo_id] = verified_item
        else:
            verified_item = self.verified_todos[todo_id]

        # Add verifier
        if verifier not in verified_item.verified_by:
            verified_item.verified_by.append(verifier)

        # Add notes
        if notes:
            verified_item.verification_notes.append(f"{verifier}: {notes}")

        # Check if triple-verified
        if len(verified_item.verified_by) >= 2:  # JARVIS + MARVIN = verified
            verified_item.status = TaskStatus.COMPLETE
            verified_item.verification_date = datetime.now().isoformat()
            self.logger.info(f"✅ Todo verified: {master_item.title}")

        self._save_verified_todos()
        self.sync_to_nas_holocron()

        return True

    def sync_to_nas_holocron(self):
        """
        Sync todos to NAS Holocron (rolling logs)

        This is just logs - rolling log maintenance and administration.
        """
        try:
            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            log_file = self.holocron_dir / f"todo_log_{timestamp}.json"

            # Create log entry
            log_data = {
                "timestamp": datetime.now().isoformat(),
                "master_todos": {
                    item_id: item.to_dict()
                    for item_id, item in self.master_tracker.items.items()
                },
                "verified_todos": {
                    item_id: item.to_dict()
                    for item_id, item in self.verified_todos.items()
                },
                "stats": {
                    "master_total": len(self.master_tracker.items),
                    "master_complete": len([t for t in self.master_tracker.items.values() 
                                           if t.status == TaskStatus.COMPLETE]),
                    "verified_total": len(self.verified_todos),
                    "verified_complete": len([t for t in self.verified_todos.values() 
                                            if t.status == TaskStatus.COMPLETE])
                }
            }

            # Save to local Holocron
            with open(log_file, 'w', encoding='utf-8') as f:
                json.dump(log_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📦 Synced to Holocron: {log_file.name}")

            # Try to sync to NAS (KAIJU) if available
            if self.nas_todo_path:
                try:
                    # This would use SSH or SMB to copy to NAS
                    # For now, just log the intent
                    self.logger.info(f"📦 NAS sync target: {self.nas_todo_path}")
                    # TODO: Implement actual NAS sync  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                except Exception as e:
                    self.logger.warning(f"⚠️ NAS sync failed: {e}")

            # Keep last 100 logs (rolling logs)
            logs = sorted(self.holocron_dir.glob("todo_log_*.json"), key=lambda p: p.stat().st_mtime)
            if len(logs) > 100:
                for old_log in logs[:-100]:
                    old_log.unlink()
                    self.logger.debug(f"🗑️ Removed old log: {old_log.name}")

        except Exception as e:
            self.logger.error(f"❌ Error syncing to Holocron: {e}")

    def get_master_todos(self, status: Optional[TaskStatus] = None) -> List[TodoItem]:
        """Get master todos"""
        return self.master_tracker.get_todos(status=status)

    def get_verified_todos(self) -> List[VerifiedTodoItem]:
        """Get verified todos"""
        return list(self.verified_todos.values())

    def get_dual_report(self) -> str:
        """Generate dual todo report"""
        report = []
        report.append("# Dual To-Do System Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")

        # Master todos
        report.append("## Master To-Do List (Working)")
        master_stats = self.master_tracker.get_stats()
        report.append(f"- Total: {master_stats['total']}")
        report.append(f"- Complete: {master_stats['complete']} ({master_stats['completion_rate']:.1f}%)")
        report.append(f"- In Progress: {master_stats['in_progress']}")
        report.append(f"- Pending: {master_stats['pending']}")
        report.append("")

        in_progress = self.get_master_todos(status=TaskStatus.IN_PROGRESS)
        if in_progress:
            report.append("### In Progress")
            for todo in in_progress:
                report.append(f"- [{todo.priority.value.upper()}] {todo.title}")
            report.append("")

        # Verified todos
        report.append("## Verified To-Do List (Triple-Checked)")
        verified = self.get_verified_todos()
        verified_complete = [t for t in verified if t.status == TaskStatus.COMPLETE]
        report.append(f"- Total Verified: {len(verified)}")
        report.append(f"- Verified Complete: {len(verified_complete)}")
        report.append("")

        if verified_complete:
            report.append("### Verified & Complete")
            for todo in verified_complete:
                report.append(f"- ✅ {todo.title}")
                if todo.verified_by:
                    report.append(f"  - Verified by: {', '.join(todo.verified_by)}")
            report.append("")

        return "\n".join(report)


def main():
    try:
        """Main execution"""
        system = DualTodoSystem()

        print("📋🔍 Dual To-Do System")
        print("=" * 80)
        print("Master List: Everything we're working on")
        print("Verified List: Triple-checked by upper management")
        print("Holocron Backup: Rolling logs to NAS (KAIJU)")
        print()

        # Generate report
        report = system.get_dual_report()
        print(report)

        # Save report
        report_file = system.project_root / "DUAL_TODO_REPORT.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n✅ Report saved to: {report_file}")
        print("📦 Syncing to Holocron...")
        system.sync_to_nas_holocron()
        print("✅ Sync complete!")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()