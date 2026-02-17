#!/usr/bin/env python3
"""
Documentation to Implementation Tracker

Analyzes documentation files and extracts actionable implementation tasks,
tracking the ratio of documentation to actual code implementation.

Goal: Shift from 90% docs / 10% code to 50% docs / 50% code

@IMPLEMENTATION @TRACKING @DOCUMENTATION
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class ImplementationTask:
    """Single actionable implementation task extracted from docs"""
    task_id: str
    source_doc: str
    title: str
    description: str
    priority: int = 5  # 1-10, 1 is highest
    status: str = "pending"  # pending, in_progress, completed, blocked
    estimated_effort: str = "unknown"  # small, medium, large, xlarge
    implementation_type: str = "code"  # code, config, integration, test
    target_files: List[str] = None
    dependencies: List[str] = None
    created_at: str = None
    updated_at: str = None
    completed_at: Optional[str] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now().isoformat()
        if self.updated_at is None:
            self.updated_at = datetime.now().isoformat()
        if self.target_files is None:
            self.target_files = []
        if self.dependencies is None:
            self.dependencies = []

    def to_dict(self):
        return asdict(self)


@dataclass
class DocAnalysis:
    """Analysis of a single documentation file"""
    doc_path: str
    doc_type: str  # complete, quick_ref, guide, spec, etc.
    has_implementation: bool = False
    implementation_status: str = "unknown"  # complete, partial, missing
    tasks_extracted: int = 0
    code_references: List[str] = None
    implementation_files: List[str] = None

    def __post_init__(self):
        if self.code_references is None:
            self.code_references = []
        if self.implementation_files is None:
            self.implementation_files = []


class DocToImplementationTracker:
    """
    Tracks documentation and converts it to actionable implementation tasks
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize tracker"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("DocToImplementationTracker")

        # Storage
        self.tasks: Dict[str, ImplementationTask] = {}
        self.doc_analyses: Dict[str, DocAnalysis] = {}

        # Output directories
        self.output_dir = self.project_root / "data" / "implementation_tracking"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Patterns for extracting tasks
        self.task_patterns = [
            r"TODO[:\s]+(.+)",
            r"FIXME[:\s]+(.+)",
            r"IMPLEMENT[:\s]+(.+)",
            r"NOT IMPLEMENTED[:\s]+(.+)",
            r"PENDING[:\s]+(.+)",
            r"\[ \][\s]+(.+)",  # Unchecked markdown checkbox
            r"## Implementation[:\s]+(.+)",
            r"### Implementation[:\s]+(.+)",
            r"Status[:\s]+.*pending.*",
            r"Status[:\s]+.*TODO.*",
        ]

        # Patterns for finding code references
        self.code_patterns = [
            r"`([a-zA-Z_][a-zA-Z0-9_/\.]+\.py)`",
            r"scripts/python/([a-zA-Z_][a-zA-Z0-9_]+\.py)",
            r"from ([a-zA-Z_][a-zA-Z0-9_]+) import",
            r"import ([a-zA-Z_][a-zA-Z0-9_]+)",
        ]

        self.logger.info("=" * 80)
        self.logger.info("📋 Documentation to Implementation Tracker")
        self.logger.info("=" * 80)

    def analyze_documentation(self, doc_path: Path) -> DocAnalysis:
        """Analyze a single documentation file"""
        try:
            content = doc_path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.warning(f"⚠️  Could not read {doc_path}: {e}")
            return None

        analysis = DocAnalysis(
            doc_path=str(doc_path.relative_to(self.project_root)),
            doc_type=self._classify_doc(doc_path)
        )

        # Extract tasks
        tasks = self._extract_tasks(content, doc_path)
        analysis.tasks_extracted = len(tasks)

        # Find code references
        code_refs = self._find_code_references(content)
        analysis.code_references = code_refs

        # Check if implementation exists
        implementation_files = self._find_implementation_files(doc_path, code_refs)
        analysis.implementation_files = implementation_files
        analysis.has_implementation = len(implementation_files) > 0

        # Determine implementation status
        if analysis.has_implementation and analysis.tasks_extracted == 0:
            analysis.implementation_status = "complete"
        elif analysis.has_implementation and analysis.tasks_extracted > 0:
            analysis.implementation_status = "partial"
        else:
            analysis.implementation_status = "missing"

        return analysis

    def _classify_doc(self, doc_path: Path) -> str:
        """Classify documentation type"""
        name_lower = doc_path.name.lower()

        if "complete" in name_lower:
            return "complete"
        elif "quick_reference" in name_lower or "quick_ref" in name_lower:
            return "quick_ref"
        elif "guide" in name_lower:
            return "guide"
        elif "spec" in name_lower or "specification" in name_lower:
            return "spec"
        elif "operations" in name_lower or "operations" in name_lower:
            return "operations"
        elif "summary" in name_lower:
            return "summary"
        else:
            return "other"

    def _extract_tasks(self, content: str, doc_path: Path) -> List[Dict[str, Any]]:
        """Extract actionable tasks from documentation"""
        tasks = []

        for pattern in self.task_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                task_text = match.group(1) if match.groups() else match.group(0)

                # Skip if it's just a status indicator
                if any(word in task_text.lower() for word in ["status", "complete", "done", "finished"]):
                    continue

                tasks.append({
                    "text": task_text.strip(),
                    "line": content[:match.start()].count('\n') + 1,
                    "pattern": pattern
                })

        return tasks

    def _find_code_references(self, content: str) -> List[str]:
        """Find references to code files"""
        refs = []

        for pattern in self.code_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                ref = match.group(1)
                if ref not in refs:
                    refs.append(ref)

        return refs

    def _find_implementation_files(self, doc_path: Path, code_refs: List[str]) -> List[str]:
        try:
            """Find actual implementation files"""
            impl_files = []

            # Check referenced files
            for ref in code_refs:
                # Try different path variations
                possible_paths = [
                    self.project_root / ref,
                    self.project_root / "scripts" / "python" / ref,
                    doc_path.parent / ref,
                ]

                for path in possible_paths:
                    if path.exists() and path.is_file():
                        rel_path = str(path.relative_to(self.project_root))
                        if rel_path not in impl_files:
                            impl_files.append(rel_path)
                        break

            return impl_files

        except Exception as e:
            self.logger.error(f"Error in _find_implementation_files: {e}", exc_info=True)
            raise
    def scan_all_docs(self, doc_dir: Optional[Path] = None) -> Dict[str, DocAnalysis]:
        try:
            """Scan all documentation files"""
            if doc_dir is None:
                doc_dir = self.project_root / "docs"

            if not doc_dir.exists():
                self.logger.warning(f"⚠️  Docs directory not found: {doc_dir}")
                return {}

            self.logger.info(f"📚 Scanning documentation in: {doc_dir}")

            analyses = {}
            doc_files = list(doc_dir.rglob("*.md"))

            self.logger.info(f"   Found {len(doc_files)} documentation files")

            for doc_file in doc_files:
                analysis = self.analyze_documentation(doc_file)
                if analysis:
                    analyses[analysis.doc_path] = analysis

            self.doc_analyses = analyses
            return analyses

        except Exception as e:
            self.logger.error(f"Error in scan_all_docs: {e}", exc_info=True)
            raise
    def generate_implementation_tasks(self) -> List[ImplementationTask]:
        try:
            """Generate implementation tasks from documentation analyses"""
            tasks = []
            task_counter = 1

            for doc_path, analysis in self.doc_analyses.items():
                # Create tasks for missing implementations
                if analysis.implementation_status == "missing":
                    # Determine priority based on doc type
                    if analysis.doc_type == "quick_ref":
                        priority = 3  # High priority - users need these
                    elif analysis.doc_type == "operations":
                        priority = 4  # High priority - core functionality
                    elif analysis.doc_type == "complete":
                        priority = 5  # Medium-high - should be complete
                    elif analysis.doc_type == "guide":
                        priority = 6  # Medium - helpful but not critical
                    else:
                        priority = 7  # Medium-low - other docs

                    # Determine effort based on tasks extracted
                    if analysis.tasks_extracted > 10:
                        effort = "large"
                    elif analysis.tasks_extracted > 5:
                        effort = "medium"
                    elif analysis.tasks_extracted > 0:
                        effort = "small"
                    else:
                        effort = "unknown"

                    task = ImplementationTask(
                        task_id=f"impl_{task_counter:04d}",
                        source_doc=doc_path,
                        title=f"Implement: {Path(doc_path).stem}",
                        description=f"Documentation exists but no implementation found: {doc_path}\nTasks extracted: {analysis.tasks_extracted}\nCode references: {len(analysis.code_references)}",
                        priority=priority,
                        status="pending",
                        estimated_effort=effort,
                        implementation_type="code",
                        target_files=analysis.implementation_files or []
                    )
                    tasks.append(task)
                    task_counter += 1

                # Also create tasks for partial implementations that need completion
                elif analysis.implementation_status == "partial" and analysis.tasks_extracted > 0:
                    task = ImplementationTask(
                        task_id=f"impl_{task_counter:04d}",
                        source_doc=doc_path,
                        title=f"Complete: {Path(doc_path).stem}",
                        description=f"Partial implementation exists but {analysis.tasks_extracted} tasks remain: {doc_path}",
                        priority=6,  # Medium priority
                        status="pending",
                        estimated_effort="small" if analysis.tasks_extracted < 5 else "medium",
                        implementation_type="code",
                        target_files=analysis.implementation_files or []
                    )
                    tasks.append(task)
                    task_counter += 1

            # Store tasks
            for task in tasks:
                self.tasks[task.task_id] = task

            return tasks

        except Exception as e:
            self.logger.error(f"Error in generate_implementation_tasks: {e}", exc_info=True)
            raise
    def calculate_ratio(self) -> Dict[str, Any]:
        """Calculate documentation to implementation ratio"""
        total_docs = len(self.doc_analyses)

        if total_docs == 0:
            return {
                "total_docs": 0,
                "docs_with_impl": 0,
                "docs_without_impl": 0,
                "complete_impl": 0,
                "partial_impl": 0,
                "missing_impl": 0,
                "ratio_docs_to_impl": 0.0,
                "impl_percentage": 0.0
            }

        docs_with_impl = sum(1 for a in self.doc_analyses.values() if a.has_implementation)
        docs_without_impl = total_docs - docs_with_impl

        complete_impl = sum(1 for a in self.doc_analyses.values() if a.implementation_status == "complete")
        partial_impl = sum(1 for a in self.doc_analyses.values() if a.implementation_status == "partial")
        missing_impl = sum(1 for a in self.doc_analyses.values() if a.implementation_status == "missing")

        impl_percentage = (docs_with_impl / total_docs) * 100 if total_docs > 0 else 0

        return {
            "total_docs": total_docs,
            "docs_with_impl": docs_with_impl,
            "docs_without_impl": docs_without_impl,
            "complete_impl": complete_impl,
            "partial_impl": partial_impl,
            "missing_impl": missing_impl,
            "ratio_docs_to_impl": total_docs / docs_with_impl if docs_with_impl > 0 else float('inf'),
            "impl_percentage": impl_percentage,
            "target_ratio": 1.0,  # 50/50 = 1:1
            "current_ratio": total_docs / docs_with_impl if docs_with_impl > 0 else float('inf'),
            "gap": max(0, (total_docs / docs_with_impl) - 1.0) if docs_with_impl > 0 else float('inf')
        }

    def generate_report(self) -> str:
        """Generate human-readable report"""
        ratio = self.calculate_ratio()

        report = []
        report.append("=" * 80)
        report.append("📊 DOCUMENTATION TO IMPLEMENTATION RATIO REPORT")
        report.append("=" * 80)
        report.append("")
        report.append(f"Total Documentation Files: {ratio['total_docs']}")
        report.append(f"  ✅ Complete Implementation: {ratio['complete_impl']}")
        report.append(f"  ⚠️  Partial Implementation: {ratio['partial_impl']}")
        report.append(f"  ❌ Missing Implementation: {ratio['missing_impl']}")
        report.append("")
        report.append(f"Implementation Coverage: {ratio['impl_percentage']:.1f}%")
        report.append(f"Current Ratio: {ratio['current_ratio']:.2f}:1 (docs:impl)")
        report.append(f"Target Ratio: {ratio['target_ratio']:.2f}:1 (50/50)")
        report.append("")

        if ratio['impl_percentage'] < 50:
            gap = 50 - ratio['impl_percentage']
            report.append(f"⚠️  GAP: Need to implement {gap:.1f}% more to reach 50/50")
            report.append(f"   That's approximately {int(ratio['total_docs'] * gap / 100)} more files to implement")
        else:
            report.append("✅ Target ratio achieved!")

        report.append("")
        report.append("=" * 80)

        return "\n".join(report)

    def save_analysis(self):
        try:
            """Save analysis to disk"""
            state_file = self.output_dir / "doc_analysis.json"
            tasks_file = self.output_dir / "implementation_tasks.json"

            # Save analyses
            analyses_dict = {
                path: {
                    "doc_path": analysis.doc_path,
                    "doc_type": analysis.doc_type,
                    "has_implementation": analysis.has_implementation,
                    "implementation_status": analysis.implementation_status,
                    "tasks_extracted": analysis.tasks_extracted,
                    "code_references": analysis.code_references,
                    "implementation_files": analysis.implementation_files
                }
                for path, analysis in self.doc_analyses.items()
            }

            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "analyses": analyses_dict,
                    "ratio": self.calculate_ratio(),
                    "generated_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)

            # Save tasks
            tasks_dict = {
                task_id: task.to_dict()
                for task_id, task in self.tasks.items()
            }

            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "tasks": tasks_dict,
                    "total_tasks": len(tasks_dict),
                    "generated_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Analysis saved: {state_file}")
            self.logger.info(f"💾 Tasks saved: {tasks_file}")


        except Exception as e:
            self.logger.error(f"Error in save_analysis: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Documentation to Implementation Tracker")
    parser.add_argument("--scan", action="store_true",
                       help="Scan all documentation files")
    parser.add_argument("--report", action="store_true",
                       help="Generate and display report")
    parser.add_argument("--generate-tasks", action="store_true",
                       help="Generate implementation tasks from missing implementations")
    parser.add_argument("--doc-dir", type=str,
                       help="Documentation directory to scan (default: docs)")

    args = parser.parse_args()

    tracker = DocToImplementationTracker()

    if args.doc_dir:
        doc_dir = Path(args.doc_dir)
    else:
        doc_dir = tracker.project_root / "docs"

    if args.scan:
        tracker.scan_all_docs(doc_dir)
        tracker.save_analysis()
        print("✅ Documentation scan complete")

    if args.generate_tasks:
        if not tracker.doc_analyses:
            tracker.scan_all_docs(doc_dir)
        tasks = tracker.generate_implementation_tasks()
        tracker.save_analysis()
        print(f"✅ Generated {len(tasks)} implementation tasks")

    if args.report:
        if not tracker.doc_analyses:
            tracker.scan_all_docs(doc_dir)
        print(tracker.generate_report())
        tracker.save_analysis()

    if not any([args.scan, args.report, args.generate_tasks]):
        # Default: scan and report
        tracker.scan_all_docs(doc_dir)
        print(tracker.generate_report())
        tracker.save_analysis()


if __name__ == "__main__":


    main()