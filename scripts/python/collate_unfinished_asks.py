#!/usr/bin/env python3
"""
Collate Unfinished Asks - Comprehensive Task Aggregation

Scans ALL environments (workspace and non-workspace) to find:
- Unfinished tasks from Master Todo List
- Incomplete workflow steps
- TODO/FIXME comments in code
- Environment-specific TODO files
- Workflow-specific pending items

Creates a unified ongoing list with recommendations for organization.
"""

import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum

# Import existing systems
try:
    from master_todo_tracker import MasterTodoTracker, TodoItem, TaskStatus, Priority
    from dual_todo_system import DualTodoSystem
    TODO_SYSTEMS_AVAILABLE = True
except ImportError:
    TODO_SYSTEMS_AVAILABLE = False
    MasterTodoTracker = None
    DualTodoSystem = None

try:
    from workflow_base import WorkflowBase
    WORKFLOW_BASE_AVAILABLE = True
except ImportError:
    WORKFLOW_BASE_AVAILABLE = False


class TaskSource(Enum):
    """Source of the unfinished task"""
    MASTER_TODO = "master_todo"
    VERIFIED_TODO = "verified_todo"
    WORKFLOW_STEP = "workflow_step"
    CODE_COMMENT = "code_comment"
    ENV_TODO_FILE = "env_todo_file"
    WORKFLOW_PATTERN = "workflow_pattern"


class OrganizationRecommendation(Enum):
    """Recommendation for where to organize the task"""
    MASTER_TODO = "master_todo"  # Add to master todo list
    WORKFLOW_SPECIFIC = "workflow_specific"  # Part of specific workflow
    ENVIRONMENT_SPECIFIC = "environment_specific"  # Environment-specific
    CODE_CLEANUP = "code_cleanup"  # Code cleanup task
    GENERIC_CATEGORY = "generic_category"  # Generic category in master


@dataclass
class UnfinishedAsk:
    """Unfinished ask/task from any source"""
    id: str
    title: str
    description: str = ""
    source: TaskSource = TaskSource.MASTER_TODO
    source_location: str = ""  # File path or system name
    status: str = "pending"
    priority: str = "medium"
    category: str = ""
    environment: str = ""  # Which workspace/environment
    created_date: Optional[str] = None
    updated_date: Optional[str] = None
    workflow_name: Optional[str] = None  # If part of a workflow
    step_number: Optional[int] = None  # If workflow step
    recommendation: OrganizationRecommendation = OrganizationRecommendation.MASTER_TODO
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["source"] = self.source.value
        data["recommendation"] = self.recommendation.value
        return data


class UnfinishedAsksCollator:
    """
    Collates all unfinished asks from all sources across all environments
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.workspace_roots = self._discover_workspaces()

        self.unfinished_asks: Dict[str, UnfinishedAsk] = {}

        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        """Setup logging"""
        logger = logging.getLogger("UnfinishedAsksCollator")
        logger.setLevel(logging.INFO)

        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 📋 %(name)s - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)

        return logger

    def _discover_workspaces(self) -> List[Path]:
        try:
            """Discover all workspace roots"""
            workspaces = [self.project_root]

            # Known workspace paths from user_info
            known_paths = [
                Path(r"C:\Users\mlesn\Dropbox\my_projects\.lumina"),
                Path(r"C:\Users\mlesn\Dropbox\my_projects\<COMPANY>-financial-services_llc-env"),
                Path(r"C:\Users\mlesn\Dropbox\my_projects\<COMPANY>-financial-services_llc-env_portable"),
                Path(r"C:\Users\mlesn\Dropbox\my_projects\<COMPANY_ID>-env"),
            ]

            for path in known_paths:
                if path.exists() and path not in workspaces:
                    workspaces.append(path)

            return workspaces

        except Exception as e:
            self.logger.error(f"Error in _discover_workspaces: {e}", exc_info=True)
            raise
    def collate_all(self) -> Dict[str, Any]:
        """
        Collate all unfinished asks from all sources
        """
        self.logger.info("🔍 Starting comprehensive collation of unfinished asks...")

        # 1. Master Todo List
        if TODO_SYSTEMS_AVAILABLE:
            self._collate_master_todos()
            self._collate_verified_todos()

        # 2. Workflow steps
        self._collate_workflow_steps()

        # 3. Code comments (TODO/FIXME)
        self._collate_code_comments()

        # 4. Environment TODO files
        self._collate_env_todo_files()

        # 5. Workflow patterns
        self._collate_workflow_patterns()

        # Generate recommendations
        self._generate_recommendations()

        stats = self._generate_stats()

        self.logger.info(f"✅ Collation complete: {stats['total']} unfinished asks found")

        return {
            "stats": stats,
            "asks": {ask_id: ask.to_dict() for ask_id, ask in self.unfinished_asks.items()},
            "recommendations": self._get_organization_recommendations()
        }

    def _collate_master_todos(self):
        """Collate unfinished tasks from Master Todo List"""
        self.logger.info("📋 Collating Master Todo List...")

        try:
            for workspace_root in self.workspace_roots:
                try:
                    tracker = MasterTodoTracker(workspace_root)

                    # Get all non-complete todos
                    pending = tracker.get_todos(status=TaskStatus.PENDING)
                    in_progress = tracker.get_todos(status=TaskStatus.IN_PROGRESS)

                    for todo in pending + in_progress:
                        ask = UnfinishedAsk(
                            id=f"master_{todo.id}",
                            title=todo.title,
                            description=todo.description,
                            source=TaskSource.MASTER_TODO,
                            source_location=str(tracker.todo_file),
                            status=todo.status.value,
                            priority=todo.priority.value,
                            category=todo.category,
                            environment=workspace_root.name,
                            created_date=todo.created_date,
                            updated_date=todo.updated_date,
                            tags=todo.tags.copy(),
                            metadata={"todo_id": todo.id}
                        )
                        self.unfinished_asks[ask.id] = ask

                    self.logger.info(f"   Found {len(pending) + len(in_progress)} unfinished todos in {workspace_root.name}")
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Could not load todos from {workspace_root.name}: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error collating master todos: {e}")

    def _collate_verified_todos(self):
        """Collate unfinished tasks from Verified Todo List"""
        self.logger.info("🔍 Collating Verified Todo List...")

        try:
            for workspace_root in self.workspace_roots:
                try:
                    dual_system = DualTodoSystem(workspace_root)
                    verified = dual_system.get_verified_todos()

                    # Get unverified or incomplete verified todos
                    for verified_todo in verified:
                        if verified_todo.status != TaskStatus.COMPLETE:
                            ask = UnfinishedAsk(
                                id=f"verified_{verified_todo.todo_id}",
                                title=verified_todo.title,
                                description=verified_todo.description,
                                source=TaskSource.VERIFIED_TODO,
                                source_location=str(dual_system.verified_file),
                                status=verified_todo.status.value,
                                priority="high",  # Verified todos are high priority
                                category="verified",
                                environment=workspace_root.name,
                                tags=["verified", "triple-checked"],
                                metadata={"todo_id": verified_todo.todo_id}
                            )
                            self.unfinished_asks[ask.id] = ask

                    self.logger.info(f"   Found {len([v for v in verified if v.status != TaskStatus.COMPLETE])} unfinished verified todos in {workspace_root.name}")
                except Exception as e:
                    self.logger.warning(f"   ⚠️ Could not load verified todos from {workspace_root.name}: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error collating verified todos: {e}")

    def _collate_workflow_steps(self):
        """Collate incomplete workflow steps"""
        self.logger.info("🔄 Collating workflow steps...")

        # Look for workflow execution data
        workflow_data_dirs = [
            self.project_root / "data" / "workflows",
            self.project_root / "state" / "workflows",
            self.project_root / "logs"
        ]

        for data_dir in workflow_data_dirs:
            if not data_dir.exists():
                continue

            # Look for workflow state files
            for state_file in data_dir.rglob("*.json"):
                try:
                    with open(state_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # Check if it's workflow data
                    if "workflow_name" in data and "step_tracker" in data:
                        workflow_name = data["workflow_name"]
                        step_tracker = data.get("step_tracker", {})

                        if isinstance(step_tracker, dict):
                            total_steps = step_tracker.get("total_steps", 0)
                            steps = step_tracker.get("steps", {})

                            # Find incomplete steps
                            completed_steps = [s for s, step_data in steps.items() 
                                             if step_data.get("status") == "completed"]
                            missing_steps = [s for s in range(1, total_steps + 1) 
                                           if str(s) not in completed_steps]

                            for step_num in missing_steps:
                                step_data = steps.get(str(step_num), {})
                                ask = UnfinishedAsk(
                                    id=f"workflow_{workflow_name}_{step_num}_{state_file.stem}",
                                    title=f"{workflow_name} - Step {step_num}",
                                    description=step_data.get("step_name", f"Step {step_num} of {workflow_name}"),
                                    source=TaskSource.WORKFLOW_STEP,
                                    source_location=str(state_file),
                                    status="pending",
                                    priority="high",
                                    category="workflow_step",
                                    environment=self.project_root.name,
                                    workflow_name=workflow_name,
                                    step_number=step_num,
                                    recommendation=OrganizationRecommendation.WORKFLOW_SPECIFIC,
                                    tags=["workflow", "step_tracking"],
                                    metadata={"execution_id": data.get("execution_id")}
                                )
                                self.unfinished_asks[ask.id] = ask
                except Exception as e:
                    self.logger.debug(f"   Could not parse {state_file}: {e}")

    def _collate_code_comments(self):
        """Collate TODO/FIXME comments from code"""
        self.logger.info("💬 Collating code comments...")

        todo_patterns = [
            (r'TODO[:\s]+(.+)', 'TODO'),
            (r'FIXME[:\s]+(.+)', 'FIXME'),
            (r'XXX[:\s]+(.+)', 'XXX'),
            (r'HACK[:\s]+(.+)', 'HACK'),
            (r'NOTE[:\s]+(.+)', 'NOTE'),
        ]

        code_extensions = ['.py', '.ts', '.js', '.tsx', '.jsx', '.md']

        for workspace_root in self.workspace_roots:
            code_count = 0
            for ext in code_extensions:
                for code_file in workspace_root.rglob(f"*{ext}"):
                    # Skip certain directories
                    if any(skip in str(code_file) for skip in ['node_modules', '__pycache__', '.git', 'venv', '.venv']):
                        continue

                    try:
                        with open(code_file, 'r', encoding='utf-8', errors='ignore') as f:
                            lines = f.readlines()

                        for line_num, line in enumerate(lines, 1):
                            for pattern, tag in todo_patterns:
                                match = re.search(pattern, line, re.IGNORECASE)
                                if match:
                                    todo_text = match.group(1).strip()
                                    if len(todo_text) > 5:  # Filter out very short TODOs
                                        ask = UnfinishedAsk(
                                            id=f"code_{workspace_root.name}_{code_file.stem}_{line_num}_{hash(todo_text) % 10000}",
                                            title=f"{tag}: {todo_text[:60]}",
                                            description=f"Line {line_num} in {code_file.relative_to(workspace_root)}",
                                            source=TaskSource.CODE_COMMENT,
                                            source_location=str(code_file.relative_to(workspace_root)),
                                            status="pending",
                                            priority="medium",
                                            category="code_cleanup",
                                            environment=workspace_root.name,
                                            recommendation=OrganizationRecommendation.CODE_CLEANUP,
                                            tags=[tag.lower(), "code_comment"],
                                            metadata={"line_number": line_num, "file": str(code_file)}
                                        )
                                        self.unfinished_asks[ask.id] = ask
                                        code_count += 1
                    except Exception as e:
                        self.logger.debug(f"   Could not read {code_file}: {e}")

            self.logger.info(f"   Found {code_count} code comments in {workspace_root.name}")

    def _collate_env_todo_files(self):
        """Collate TODO items from environment-specific TODO files"""
        self.logger.info("📄 Collating environment TODO files...")

        todo_file_patterns = ['TODO.md', 'TODO.txt', 'TODO*.md', '**/TODO.md']

        for workspace_root in self.workspace_roots:
            for pattern in todo_file_patterns:
                for todo_file in workspace_root.rglob(pattern):
                    try:
                        with open(todo_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Parse markdown TODO items
                        todo_items = re.findall(r'- \[ \](.+?)(?=\n- \[|$)', content, re.MULTILINE | re.DOTALL)

                        for todo_text in todo_items:
                            todo_text = todo_text.strip()
                            if len(todo_text) > 5:
                                ask = UnfinishedAsk(
                                    id=f"env_{workspace_root.name}_{hash(todo_text) % 100000}",
                                    title=todo_text[:100],
                                    description=f"From {todo_file.relative_to(workspace_root)}",
                                    source=TaskSource.ENV_TODO_FILE,
                                    source_location=str(todo_file.relative_to(workspace_root)),
                                    status="pending",
                                    priority="medium",
                                    category="environment_specific",
                                    environment=workspace_root.name,
                                    recommendation=OrganizationRecommendation.ENVIRONMENT_SPECIFIC,
                                    tags=["env_todo", "markdown"],
                                    metadata={"file": str(todo_file)}
                                )
                                self.unfinished_asks[ask.id] = ask
                    except Exception as e:
                        self.logger.debug(f"   Could not read {todo_file}: {e}")

    def _collate_workflow_patterns(self):
        """Collate workflow-specific patterns (e.g., incomplete workflows)"""
        self.logger.info("🔀 Collating workflow patterns...")

        # Look for workflow definitions and check for incomplete patterns
        workflow_files = list(self.project_root.rglob("**/workflow*.py"))
        workflow_files.extend(self.project_root.rglob("**/*workflow*.py"))

        for workflow_file in workflow_files:
            if '__pycache__' in str(workflow_file):
                continue

            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Look for incomplete workflow implementations
                if 'class' in content and 'Workflow' in content:
                    # Check for abstract methods or incomplete implementations
                    if '@abstractmethod' in content or 'pass' in content:
                        # Extract class name
                        class_match = re.search(r'class\s+(\w+.*?):', content)
                        if class_match:
                            class_name = class_match.group(1)
                            ask = UnfinishedAsk(
                                id=f"pattern_{workflow_file.stem}_{hash(class_name) % 10000}",
                                title=f"Incomplete workflow: {class_name}",
                                description=f"Workflow class in {workflow_file.relative_to(self.project_root)} may need implementation",
                                source=TaskSource.WORKFLOW_PATTERN,
                                source_location=str(workflow_file.relative_to(self.project_root)),
                                status="pending",
                                priority="low",
                                category="workflow_implementation",
                                environment=self.project_root.name,
                                workflow_name=class_name,
                                recommendation=OrganizationRecommendation.WORKFLOW_SPECIFIC,
                                tags=["workflow", "implementation"],
                                metadata={"file": str(workflow_file)}
                            )
                            self.unfinished_asks[ask.id] = ask
            except Exception as e:
                self.logger.debug(f"   Could not analyze {workflow_file}: {e}")

    def _generate_recommendations(self):
        """Generate organization recommendations for each ask"""
        for ask in self.unfinished_asks.values():
            # Already has recommendation from source, but refine based on context
            if ask.source == TaskSource.CODE_COMMENT:
                ask.recommendation = OrganizationRecommendation.CODE_CLEANUP
            elif ask.source == TaskSource.WORKFLOW_STEP or ask.workflow_name:
                ask.recommendation = OrganizationRecommendation.WORKFLOW_SPECIFIC
            elif ask.source == TaskSource.ENV_TODO_FILE:
                ask.recommendation = OrganizationRecommendation.ENVIRONMENT_SPECIFIC
            elif ask.category in ["code_cleanup", "todo_comment"]:
                ask.recommendation = OrganizationRecommendation.CODE_CLEANUP
            elif ask.category in ["workflow_step", "workflow_implementation"]:
                ask.recommendation = OrganizationRecommendation.WORKFLOW_SPECIFIC
            else:
                # Default to master todo, but could be generic category
                if ask.category:
                    ask.recommendation = OrganizationRecommendation.GENERIC_CATEGORY
                else:
                    ask.recommendation = OrganizationRecommendation.MASTER_TODO

    def _generate_stats(self) -> Dict[str, Any]:
        """Generate statistics about unfinished asks"""
        total = len(self.unfinished_asks)

        by_source = {}
        by_recommendation = {}
        by_environment = {}
        by_priority = {}
        by_category = {}

        for ask in self.unfinished_asks.values():
            by_source[ask.source.value] = by_source.get(ask.source.value, 0) + 1
            by_recommendation[ask.recommendation.value] = by_recommendation.get(ask.recommendation.value, 0) + 1
            by_environment[ask.environment] = by_environment.get(ask.environment, 0) + 1
            by_priority[ask.priority] = by_priority.get(ask.priority, 0) + 1
            by_category[ask.category or "uncategorized"] = by_category.get(ask.category or "uncategorized", 0) + 1

        return {
            "total": total,
            "by_source": by_source,
            "by_recommendation": by_recommendation,
            "by_environment": by_environment,
            "by_priority": by_priority,
            "by_category": by_category
        }

    def _get_organization_recommendations(self) -> Dict[str, Any]:
        """Get recommendations for organizing tasks"""
        stats = self._generate_stats()

        recommendations = {
            "master_todo_candidates": len([a for a in self.unfinished_asks.values() 
                                         if a.recommendation == OrganizationRecommendation.MASTER_TODO]),
            "workflow_specific_candidates": len([a for a in self.unfinished_asks.values() 
                                               if a.recommendation == OrganizationRecommendation.WORKFLOW_SPECIFIC]),
            "code_cleanup_candidates": len([a for a in self.unfinished_asks.values() 
                                          if a.recommendation == OrganizationRecommendation.CODE_CLEANUP]),
            "environment_specific_candidates": len([a for a in self.unfinished_asks.values() 
                                                  if a.recommendation == OrganizationRecommendation.ENVIRONMENT_SPECIFIC]),
            "generic_category_candidates": len([a for a in self.unfinished_asks.values() 
                                                if a.recommendation == OrganizationRecommendation.GENERIC_CATEGORY]),
        }

        return recommendations

    def generate_report(self) -> str:
        """Generate comprehensive report"""
        stats = self._generate_stats()
        org_recs = self._get_organization_recommendations()

        report = []
        report.append("# Unfinished Asks Collation Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        report.append("## Summary")
        report.append(f"- **Total Unfinished Asks**: {stats['total']}")
        report.append("")

        report.append("## By Source")
        for source, count in sorted(stats['by_source'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {source}: {count}")
        report.append("")

        report.append("## By Recommendation")
        for rec, count in sorted(stats['by_recommendation'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {rec}: {count}")
        report.append("")

        report.append("## By Environment")
        for env, count in sorted(stats['by_environment'].items(), key=lambda x: x[1], reverse=True):
            report.append(f"- {env}: {count}")
        report.append("")

        report.append("## By Priority")
        for priority, count in sorted(stats['by_priority'].items(), key=lambda x: {'high': 0, 'medium': 1, 'low': 2}.get(x[0], 3)):
            report.append(f"- {priority}: {count}")
        report.append("")

        report.append("## Organization Recommendations")
        report.append("")
        report.append("### Add to Master Todo List")
        report.append(f"- **Count**: {org_recs['master_todo_candidates']}")
        master_todos = [a for a in self.unfinished_asks.values() 
                       if a.recommendation == OrganizationRecommendation.MASTER_TODO]
        for ask in master_todos[:10]:  # Show first 10
            report.append(f"  - [{ask.priority.upper()}] {ask.title}")
        if len(master_todos) > 10:
            report.append(f"  - ... and {len(master_todos) - 10} more")
        report.append("")

        report.append("### Workflow-Specific (Pattern Todo List)")
        report.append(f"- **Count**: {org_recs['workflow_specific_candidates']}")
        workflow_todos = [a for a in self.unfinished_asks.values() 
                         if a.recommendation == OrganizationRecommendation.WORKFLOW_SPECIFIC]
        for ask in workflow_todos[:10]:
            report.append(f"  - [{ask.priority.upper()}] {ask.title} ({ask.workflow_name or 'N/A'})")
        if len(workflow_todos) > 10:
            report.append(f"  - ... and {len(workflow_todos) - 10} more")
        report.append("")

        report.append("### Code Cleanup")
        report.append(f"- **Count**: {org_recs['code_cleanup_candidates']}")
        code_todos = [a for a in self.unfinished_asks.values() 
                     if a.recommendation == OrganizationRecommendation.CODE_CLEANUP]
        for ask in code_todos[:10]:
            report.append(f"  - {ask.title} ({ask.source_location})")
        if len(code_todos) > 10:
            report.append(f"  - ... and {len(code_todos) - 10} more")
        report.append("")

        report.append("### Environment-Specific")
        report.append(f"- **Count**: {org_recs['environment_specific_candidates']}")
        env_todos = [a for a in self.unfinished_asks.values() 
                    if a.recommendation == OrganizationRecommendation.ENVIRONMENT_SPECIFIC]
        for ask in env_todos[:10]:
            report.append(f"  - {ask.title} ({ask.environment})")
        if len(env_todos) > 10:
            report.append(f"  - ... and {len(env_todos) - 10} more")
        report.append("")

        report.append("## Next Steps")
        report.append("")
        report.append("1. **Review Recommendations**: Decide which tasks go to Master Todo vs Workflow-Specific")
        report.append("2. **Create Workflow Todo Lists**: For workflow-specific tasks, create pattern-based todo lists")
        report.append("3. **Organize by Category**: Group generic category tasks in Master Todo")
        report.append("4. **Code Cleanup**: Schedule code cleanup tasks separately")
        report.append("5. **Environment Tasks**: Keep environment-specific tasks in their respective environments")
        report.append("")

        return "\n".join(report)

    def save_results(self, output_file: Optional[Path] = None):
        try:
            """Save collation results"""
            if output_file is None:
                output_file = self.project_root / "data" / "todo" / "unfinished_asks_collation.json"

            output_file.parent.mkdir(parents=True, exist_ok=True)

            results = {
                "generated_at": datetime.now().isoformat(),
                "stats": self._generate_stats(),
                "asks": {ask_id: ask.to_dict() for ask_id, ask in self.unfinished_asks.items()},
                "recommendations": self._get_organization_recommendations()
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Results saved to: {output_file}")

            # Also save report
            report_file = self.project_root / "UNFINISHED_ASKS_REPORT.md"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(self.generate_report())

            self.logger.info(f"📄 Report saved to: {report_file}")


        except Exception as e:
            self.logger.error(f"Error in save_results: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    collator = UnfinishedAsksCollator()

    print("🔍 Collating All Unfinished Asks...")
    print("=" * 80)

    results = collator.collate_all()

    print("\n📊 Statistics:")
    stats = results['stats']
    print(f"   Total: {stats['total']}")
    print(f"   By Source: {stats['by_source']}")
    print(f"   By Recommendation: {stats['by_recommendation']}")

    print("\n💾 Saving results...")
    collator.save_results()

    print("\n✅ Collation complete!")
    print(f"   Report: UNFINISHED_ASKS_REPORT.md")
    print(f"   Data: data/todo/unfinished_asks_collation.json")


if __name__ == "__main__":



    main()