#!/usr/bin/env python3
"""
Codebase Intelligent Resume Analysis Tool
ANALYTICAL TOOL - Does NOT execute fixes, only analyzes

Purpose:
- Identify duplicate functionality
- Catalog interrupted work
- Map dependencies and precedence
- Categorize code by status (active/degraded/obsolete)

Approach: Analysis first, decision second, execution third
"""

import sys
import json
import ast
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict
import re
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CodebaseAnalysis")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class FileAnalysis:
    """Analysis of a single file"""
    path: str
    name: str
    size: int
    mtime: datetime
    functions: List[str]
    classes: List[str]
    imports: List[str]
    todo_count: int
    fixme_count: int
    hack_count: int
    content_hash: str
    similarity_score: float = 0.0
    status: str = "unknown"  # active, degraded, obsolete, duplicate


@dataclass
class DuplicateGroup:
    """Group of files with similar functionality"""
    files: List[str]
    similarity_reason: str
    suggested_primary: str
    suggested_archive: List[str]


@dataclass
class InterruptedWork:
    """Catalog of interrupted work"""
    file: str
    line: int
    marker: str  # TODO, FIXME, HACK, XXX  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
    description: str
    context: str


class CodebaseAnalyzer:
    """Analytical tool for codebase assessment"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.analyses: Dict[str, FileAnalysis] = {}
        self.duplicate_groups: List[DuplicateGroup] = []
        self.interrupted_work: List[InterruptedWork] = []
        self.patterns: Dict[str, Any] = {}

    def analyze_python_file(self, file_path: Path) -> Optional[FileAnalysis]:
        """Analyze a single Python file"""
        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            functions = []
            classes = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    classes.append(node.name)
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        imports.extend([alias.name for alias in node.names])
                    else:
                        imports.append(node.module or "")

            # Count markers
            todo_count = len(re.findall(r'TODO|FIXME', content, re.IGNORECASE))
            fixme_count = len(re.findall(r'FIXME', content, re.IGNORECASE))
            hack_count = len(re.findall(r'HACK|XXX', content, re.IGNORECASE))

            # Content hash for similarity
            content_hash = hashlib.md5(content.encode()).hexdigest()

            stat = file_path.stat()

            analysis = FileAnalysis(
                path=str(file_path.relative_to(self.root_path)),
                name=file_path.name,
                size=stat.st_size,
                mtime=datetime.fromtimestamp(stat.st_mtime),
                functions=functions,
                classes=classes,
                imports=imports,
                todo_count=todo_count,
                fixme_count=fixme_count,
                hack_count=hack_count,
                content_hash=content_hash
            )

            return analysis

        except Exception as e:
            logger.debug(f"Failed to analyze {file_path}: {e}")
            return None

    def find_duplicate_patterns(self) -> List[DuplicateGroup]:
        """Find files with similar functionality"""
        duplicate_groups = []

        # Group by name similarity
        name_groups = defaultdict(list)
        for path, analysis in self.analyses.items():
            # Normalize name (remove extensions, version numbers, etc.)
            base_name = re.sub(r'_\d+$|_v\d+|\.py$', '', analysis.name.lower())
            name_groups[base_name].append(path)

        # Find groups with multiple files
        for base_name, file_paths in name_groups.items():
            if len(file_paths) > 1:
                # Determine primary (newest, largest, or most functions)
                file_analyses = [self.analyses[path] for path in file_paths]
                file_analyses.sort(key=lambda x: (x.mtime, len(x.functions)), reverse=True)

                primary = file_analyses[0]
                duplicates = file_analyses[1:]

                duplicate_groups.append(DuplicateGroup(
                    files=[f.path for f in file_analyses],
                    similarity_reason=f"Similar base name: {base_name}",
                    suggested_primary=primary.path,
                    suggested_archive=[f.path for f in duplicates]
                ))

        # Group by function/class similarity
        function_groups = defaultdict(list)
        for path, analysis in self.analyses.items():
            key = tuple(sorted(analysis.functions))
            if len(key) > 0:
                function_groups[key].append(path)

        for functions, file_paths in function_groups.items():
            if len(file_paths) > 1:
                file_analyses = [self.analyses[path] for path in file_paths]
                file_analyses.sort(key=lambda x: (x.mtime, x.size), reverse=True)

                primary = file_analyses[0]
                duplicates = file_analyses[1:]

                duplicate_groups.append(DuplicateGroup(
                    files=[f.path for f in file_analyses],
                    similarity_reason=f"Similar functions: {', '.join(functions[:3])}",
                    suggested_primary=primary.path,
                    suggested_archive=[f.path for f in duplicates]
                ))

        return duplicate_groups

    def catalog_interrupted_work(self) -> List[InterruptedWork]:
        """Catalog all interrupted work markers"""
        interrupted = []

        for path, analysis in self.analyses.items():
            file_path = self.root_path / analysis.path
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.split('\n')

                for i, line in enumerate(lines, 1):
                    # Check for markers
                    for marker in ['TODO', 'FIXME', 'HACK', 'XXX']:
                        if marker in line.upper():
                            # Extract description
                            match = re.search(rf'{marker}[:\s]*(.+)', line, re.IGNORECASE)
                            description = match.group(1).strip() if match else ""

                            # Get context (3 lines before/after)
                            start = max(0, i - 4)
                            end = min(len(lines), i + 3)
                            context = '\n'.join(lines[start:end])

                            interrupted.append(InterruptedWork(
                                file=analysis.path,
                                line=i,
                                marker=marker,
                                description=description,
                                context=context
                            ))
            except Exception as e:
                logger.debug(f"Failed to read {file_path} for interrupted work: {e}")

        return interrupted

    def analyze_codebase(self, script_dir: Path = None) -> Dict[str, Any]:
        """Perform comprehensive codebase analysis"""
        if script_dir is None:
            script_dir = self.root_path / "scripts" / "python"

        logger.info(f"Analyzing codebase: {script_dir}")

        # Analyze all Python files
        python_files = list(script_dir.rglob("*.py"))
        logger.info(f"Found {len(python_files)} Python files")

        for py_file in python_files:
            analysis = self.analyze_python_file(py_file)
            if analysis:
                self.analyses[analysis.path] = analysis

        logger.info(f"Analyzed {len(self.analyses)} files")

        # Find duplicates
        logger.info("Finding duplicate patterns...")
        self.duplicate_groups = self.find_duplicate_patterns()
        logger.info(f"Found {len(self.duplicate_groups)} duplicate groups")

        # Catalog interrupted work
        logger.info("Cataloging interrupted work...")
        self.interrupted_work = self.catalog_interrupted_work()
        logger.info(f"Found {len(self.interrupted_work)} interrupted work items")

        # Generate report
        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive analysis report"""
        return {
            "analysis_date": datetime.now().isoformat(),
            "total_files_analyzed": len(self.analyses),
            "duplicate_groups": [
                {
                    "files": group.files,
                    "similarity_reason": group.similarity_reason,
                    "suggested_primary": group.suggested_primary,
                    "suggested_archive": group.suggested_archive
                }
                for group in self.duplicate_groups
            ],
            "interrupted_work_summary": {
                "total": len(self.interrupted_work),
                "by_marker": {
                    marker: len([w for w in self.interrupted_work if w.marker == marker])
                    for marker in ['TODO', 'FIXME', 'HACK', 'XXX']
                },
                "items": [
                    {
                        "file": item.file,
                        "line": item.line,
                        "marker": item.marker,
                        "description": item.description
                    }
                    for item in self.interrupted_work
                ]
            },
            "file_statistics": {
                "total_size": sum(a.size for a in self.analyses.values()),
                "average_size": sum(a.size for a in self.analyses.values()) / len(self.analyses) if self.analyses else 0,
                "files_with_todos": len([a for a in self.analyses.values() if a.todo_count > 0]),
                "files_with_fixmes": len([a for a in self.analyses.values() if a.fixme_count > 0]),
            }
        }


def main():
    try:
        """Main function - ANALYSIS ONLY"""
        import argparse

        parser = argparse.ArgumentParser(description="Analyze codebase for intelligent resume planning")
        parser.add_argument("--root", default=str(project_root), help="Root directory to analyze")
        parser.add_argument("--output", help="Output JSON file for analysis results")

        args = parser.parse_args()

        root = Path(args.root)
        analyzer = CodebaseAnalyzer(root)

        logger.info("=" * 80)
        logger.info("CODEBASE INTELLIGENT RESUME ANALYSIS")
        logger.info("=" * 80)
        logger.info("ANALYTICAL TOOL - Does NOT execute fixes")
        logger.info("=" * 80)
        logger.info("")

        # Analyze
        report = analyzer.analyze_codebase()

        # Output results
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = project_root / "data" / "codebase_analysis" / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"\n✓ Analysis complete")
        logger.info(f"✓ Report saved: {output_file}")
        logger.info(f"\nSUMMARY:")
        logger.info(f"  Files analyzed: {report['total_files_analyzed']}")
        logger.info(f"  Duplicate groups: {len(report['duplicate_groups'])}")
        logger.info(f"  Interrupted work items: {report['interrupted_work_summary']['total']}")
        logger.info(f"\nNEXT STEPS:")
        logger.info(f"  1. Review analysis report")
        logger.info(f"  2. Determine precedence based on dependencies")
        logger.info(f"  3. Create execution plan")
        logger.info(f"  4. Execute fixes in precedence order")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())