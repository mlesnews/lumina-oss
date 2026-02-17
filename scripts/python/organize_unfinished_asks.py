#!/usr/bin/env python3
"""
Organize Unfinished Asks - Integration with Master Todo System

Organizes collated unfinished asks into:
1. Master Todo List (generic categories)
2. Workflow-Specific Todo Lists (pattern-based)
3. Code Cleanup Tracking
4. Environment-Specific (kept in respective environments)

This creates an ongoing list that integrates with existing systems.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

from master_todo_tracker import MasterTodoTracker, TodoItem, TaskStatus, Priority
from dual_todo_system import DualTodoSystem


class UnfinishedAsksOrganizer:
    """
    Organizes unfinished asks into appropriate tracking systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.collation_file = self.project_root / "data" / "todo" / "unfinished_asks_collation.json"

        self.master_tracker = MasterTodoTracker(project_root)
        self.dual_system = DualTodoSystem(project_root)

        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("UnfinishedAsksOrganizer")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 📋 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def load_collation(self) -> Dict[str, Any]:
        try:
            """Load collated unfinished asks"""
            if not self.collation_file.exists():
                self.logger.error(f"❌ Collation file not found: {self.collation_file}")
                self.logger.info("   Run collate_unfinished_asks.py first")
                return {}

            with open(self.collation_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_collation: {e}", exc_info=True)
            raise
    def organize_to_master_todo(self, asks: List[Dict[str, Any]], category: str = "unfinished_asks"):
        """
        Add asks to Master Todo List with appropriate categories
        """
        self.logger.info(f"📋 Organizing {len(asks)} asks to Master Todo List...")

        added_count = 0
        skipped_count = 0

        for ask in asks:
            # Check if already exists
            existing = [t for t in self.master_tracker.items.values() 
                       if t.title == ask['title'] or ask['id'] in t.metadata.get('source_ids', [])]

            if existing:
                self.logger.debug(f"   ⏭️  Skipping (already exists): {ask['title'][:50]}")
                skipped_count += 1
                continue

            # Determine priority
            priority = Priority.HIGH if ask.get('priority') == 'high' else Priority.MEDIUM

            # Add to master todo
            todo_id = self.master_tracker.add_todo(
                title=ask['title'],
                description=ask.get('description', ''),
                category=ask.get('category', category),
                priority=priority,
                status=TaskStatus.PENDING,
                tags=ask.get('tags', []) + ['collated', 'unfinished_ask'],
                dependencies=ask.get('dependencies', [])
            )

            # Update metadata
            if todo_id in self.master_tracker.items:
                item = self.master_tracker.items[todo_id]
                item.metadata = {
                    **item.metadata,
                    'source_id': ask['id'],
                    'source': ask.get('source', 'unknown'),
                    'source_location': ask.get('source_location', ''),
                    'environment': ask.get('environment', ''),
                }

            added_count += 1

        self.master_tracker._save_todos()
        self.logger.info(f"   ✅ Added {added_count} asks, skipped {skipped_count} duplicates")

        return added_count

    def create_workflow_todo_list(self, workflow_name: str, asks: List[Dict[str, Any]]) -> Path:
        try:
            """
            Create a workflow-specific todo list file
            """
            workflow_todo_dir = self.project_root / "data" / "todo" / "workflows"
            workflow_todo_dir.mkdir(parents=True, exist_ok=True)

            workflow_file = workflow_todo_dir / f"{workflow_name}_todos.md"

            content = []
            content.append(f"# {workflow_name} - Workflow Todo List")
            content.append(f"Generated: {datetime.now().isoformat()}")
            content.append("")
            content.append("This is a workflow-specific todo list (pattern-based).")
            content.append("Tasks here are part of the workflow execution pattern.")
            content.append("")
            content.append("## Unfinished Tasks")
            content.append("")

            for ask in asks:
                priority_emoji = "🔴" if ask.get('priority') == 'high' else "🟡" if ask.get('priority') == 'medium' else "🟢"
                content.append(f"- [{priority_emoji}] **{ask['title']}**")
                if ask.get('description'):
                    content.append(f"  - {ask['description']}")
                if ask.get('step_number'):
                    content.append(f"  - Step: {ask['step_number']}")
                content.append("")

            with open(workflow_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))

            self.logger.info(f"   ✅ Created workflow todo list: {workflow_file}")

            return workflow_file

        except Exception as e:
            self.logger.error(f"Error in create_workflow_todo_list: {e}", exc_info=True)
            raise
    def create_code_cleanup_tracking(self, asks: List[Dict[str, Any]]) -> Path:
        try:
            """
            Create code cleanup tracking file
            """
            cleanup_file = self.project_root / "data" / "todo" / "code_cleanup_tracking.json"

            cleanup_data = {
                "generated_at": datetime.now().isoformat(),
                "total_tasks": len(asks),
                "tasks": asks
            }

            # Load existing if present
            if cleanup_file.exists():
                with open(cleanup_file, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
                    # Merge, avoiding duplicates
                    existing_ids = {t['id'] for t in existing.get('tasks', [])}
                    new_tasks = [t for t in asks if t['id'] not in existing_ids]
                    cleanup_data['tasks'] = existing.get('tasks', []) + new_tasks
                    cleanup_data['total_tasks'] = len(cleanup_data['tasks'])

            with open(cleanup_file, 'w', encoding='utf-8') as f:
                json.dump(cleanup_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"   ✅ Created/updated code cleanup tracking: {cleanup_file}")

            return cleanup_file

        except Exception as e:
            self.logger.error(f"Error in create_code_cleanup_tracking: {e}", exc_info=True)
            raise
    def organize_all(self):
        """
        Organize all unfinished asks according to recommendations
        """
        self.logger.info("🔍 Loading collated unfinished asks...")
        collation = self.load_collation()

        if not collation:
            return

        asks_data = collation.get('asks', {})
        asks = list(asks_data.values())

        self.logger.info(f"📊 Organizing {len(asks)} unfinished asks...")

        # Group by recommendation
        by_recommendation = {}
        for ask in asks:
            rec = ask.get('recommendation', 'master_todo')
            if rec not in by_recommendation:
                by_recommendation[rec] = []
            by_recommendation[rec].append(ask)

        # 1. Master Todo / Generic Category
        master_todos = by_recommendation.get('master_todo', []) + by_recommendation.get('generic_category', [])
        if master_todos:
            self.organize_to_master_todo(master_todos, category="unfinished_asks")

        # 2. Workflow-Specific
        workflow_todos = by_recommendation.get('workflow_specific', [])
        if workflow_todos:
            # Group by workflow
            by_workflow = {}
            for ask in workflow_todos:
                workflow_name = ask.get('workflow_name', 'unknown_workflow')
                if workflow_name not in by_workflow:
                    by_workflow[workflow_name] = []
                by_workflow[workflow_name].append(ask)

            for workflow_name, workflow_asks in by_workflow.items():
                self.create_workflow_todo_list(workflow_name, workflow_asks)

        # 3. Code Cleanup
        code_cleanup = by_recommendation.get('code_cleanup', [])
        if code_cleanup:
            self.create_code_cleanup_tracking(code_cleanup)

        # 4. Environment-Specific - Keep in their environments (already there)
        env_specific = by_recommendation.get('environment_specific', [])
        if env_specific:
            self.logger.info(f"   ℹ️  {len(env_specific)} environment-specific tasks kept in their respective environments")

        # Generate summary
        self._generate_organization_summary(collation, by_recommendation)

    def _generate_organization_summary(self, collation: Dict[str, Any], by_recommendation: Dict[str, List]):
        try:
            """Generate organization summary"""
            summary_file = self.project_root / "UNFINISHED_ASKS_ORGANIZATION.md"

            stats = collation.get('stats', {})

            content = []
            content.append("# Unfinished Asks Organization Summary")
            content.append(f"Generated: {datetime.now().isoformat()}")
            content.append("")
            content.append("## Overview")
            content.append(f"- **Total Unfinished Asks**: {stats.get('total', 0)}")
            content.append("")

            content.append("## Organization Strategy")
            content.append("")
            content.append("### 1. Master Todo List")
            master_count = len(by_recommendation.get('master_todo', [])) + len(by_recommendation.get('generic_category', []))
            content.append(f"- **Count**: {master_count}")
            content.append("- **Location**: `data/todo/master_todos.json`")
            content.append("- **Integration**: Integrated with Master Todo Tracker")
            content.append("- **Categories**: Added to appropriate categories in Master Todo")
            content.append("")

            content.append("### 2. Workflow-Specific Todo Lists (Pattern-Based)")
            workflow_count = len(by_recommendation.get('workflow_specific', []))
            content.append(f"- **Count**: {workflow_count}")
            content.append("- **Location**: `data/todo/workflows/*_todos.md`")
            content.append("- **Purpose**: Tasks that are part of specific workflow execution patterns")
            content.append("- **Usage**: These are workflow steps that need to be part of the pattern todo list")
            content.append("")

            content.append("### 3. Code Cleanup Tracking")
            cleanup_count = len(by_recommendation.get('code_cleanup', []))
            content.append(f"- **Count**: {cleanup_count}")
            content.append("- **Location**: `data/todo/code_cleanup_tracking.json`")
            content.append("- **Purpose**: Track code cleanup tasks (TODO/FIXME comments)")
            content.append("- **Usage**: Separate tracking for code quality improvements")
            content.append("")

            content.append("### 4. Environment-Specific")
            env_count = len(by_recommendation.get('environment_specific', []))
            content.append(f"- **Count**: {env_count}")
            content.append("- **Location**: Respective environment TODO.md files")
            content.append("- **Purpose**: Tasks specific to each environment")
            content.append("- **Usage**: Keep in their respective environments")
            content.append("")

            content.append("## Decision Guide")
            content.append("")
            content.append("### When to Add to Master Todo List")
            content.append("- Generic tasks that apply across the project")
            content.append("- High-priority items that need tracking")
            content.append("- Tasks that don't fit into workflow-specific patterns")
            content.append("- Items that should be part of the general development pipeline")
            content.append("")

            content.append("### When to Use Workflow-Specific Todo Lists")
            content.append("- Tasks that are steps in a specific workflow")
            content.append("- Pattern-based tasks (e.g., workflow execution steps)")
            content.append("- Tasks that are part of a workflow's todo list pattern")
            content.append("- Items that need to be tracked as part of workflow execution")
            content.append("")

            content.append("### When to Use Code Cleanup Tracking")
            content.append("- TODO/FIXME comments in code")
            content.append("- Code quality improvements")
            content.append("- Technical debt items")
            content.append("- Refactoring tasks")
            content.append("")

            content.append("### When to Keep Environment-Specific")
            content.append("- Tasks specific to a particular environment")
            content.append("- Environment configuration tasks")
            content.append("- Environment-specific features")
            content.append("")

            content.append("## Ongoing Maintenance")
            content.append("")
            content.append("1. **Regular Collation**: Run `collate_unfinished_asks.py` periodically")
            content.append("2. **Review Organization**: Review organization recommendations")
            content.append("3. **Update Master Todo**: Add high-priority items to Master Todo")
            content.append("4. **Workflow Integration**: Integrate workflow-specific tasks into workflow patterns")
            content.append("5. **Code Cleanup**: Schedule code cleanup tasks regularly")
            content.append("")

            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write("\n".join(content))

            self.logger.info(f"📄 Organization summary saved to: {summary_file}")


        except Exception as e:
            self.logger.error(f"Error in _generate_organization_summary: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    organizer = UnfinishedAsksOrganizer()

    print("📋 Organizing Unfinished Asks...")
    print("=" * 80)

    organizer.organize_all()

    print("\n✅ Organization complete!")
    print("   Summary: UNFINISHED_ASKS_ORGANIZATION.md")


if __name__ == "__main__":



    main()