#!/usr/bin/env python3
"""
JARVIS Consolidation Analysis

Analyzes JARVIS orchestration scripts to identify overlap and consolidation opportunities.
Part of Phase 2: Codebase Cleanup - JARVIS Consolidation
"""

import sys
import json
import ast
import logging
from pathlib import Path
from typing import Dict, List, Any, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISConsolidation")


@dataclass
class ScriptAnalysis:
    """Analysis of a JARVIS script"""
    script_path: str
    classes: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    main_purpose: str = ""
    line_count: int = 0


class JARVISConsolidationAnalyzer:
    """
    Analyze JARVIS scripts for consolidation opportunities
    """

    def __init__(self, project_root: Path):
        """Initialize analyzer"""
        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts" / "python"

        # JARVIS scripts to analyze (from gap analysis)
        self.jarvis_scripts = [
            "jarvis_helpdesk_integration.py",
            "jarvis_unified_interface.py",
            "jarvis_actual_execution.py",
            "jarvis_supervisor_integration.py",
            "jarvis_ai_coordination.py"
        ]

        logger.info("JARVIS Consolidation Analyzer initialized")

    def analyze_script(self, script_name: str) -> ScriptAnalysis:
        """Analyze a single script"""
        script_path = self.scripts_dir / script_name

        if not script_path.exists():
            logger.warning(f"Script not found: {script_name}")
            return ScriptAnalysis(script_path=str(script_path))

        try:
            with open(script_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Parse AST
            tree = ast.parse(content)

            analysis = ScriptAnalysis(
                script_path=str(script_path.relative_to(self.project_root)),
                line_count=len(content.splitlines())
            )

            # Extract classes
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    analysis.classes.append(node.name)
                elif isinstance(node, ast.FunctionDef):
                    analysis.functions.append(node.name)
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        analysis.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        analysis.imports.append(node.module)

            # Try to extract main purpose from docstrings
            if tree.body and isinstance(tree.body[0], ast.Expr) and isinstance(tree.body[0].value, ast.Str):
                analysis.main_purpose = tree.body[0].value.s.split('\n')[0] if tree.body[0].value.s else ""

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing {script_name}: {e}")
            return ScriptAnalysis(script_path=str(script_path))

    def find_overlaps(self, analyses: List[ScriptAnalysis]) -> Dict[str, Any]:
        """Find overlaps between scripts"""
        overlaps = {
            "shared_classes": {},
            "shared_functions": {},
            "shared_imports": {},
            "similar_purposes": []
        }

        # Find shared classes
        class_usage = {}
        for analysis in analyses:
            for cls in analysis.classes:
                if cls not in class_usage:
                    class_usage[cls] = []
                class_usage[cls].append(analysis.script_path)

        overlaps["shared_classes"] = {
            cls: scripts for cls, scripts in class_usage.items() if len(scripts) > 1
        }

        # Find shared functions
        func_usage = {}
        for analysis in analyses:
            for func in analysis.functions:
                if func not in func_usage:
                    func_usage[func] = []
                func_usage[func].append(analysis.script_path)

        overlaps["shared_functions"] = {
            func: scripts for func, scripts in func_usage.items() if len(scripts) > 1
        }

        # Find shared imports
        import_usage = {}
        for analysis in analyses:
            for imp in analysis.imports:
                if imp not in import_usage:
                    import_usage[imp] = []
                import_usage[imp].append(analysis.script_path)

        overlaps["shared_imports"] = {
            imp: scripts for imp, scripts in import_usage.items() 
            if len(scripts) > 1 and any('jarvis' in imp.lower() or 'helpdesk' in imp.lower() for s in scripts)
        }

        return overlaps

    def generate_consolidation_plan(self, analyses: List[ScriptAnalysis], overlaps: Dict[str, Any]) -> Dict[str, Any]:
        """Generate consolidation plan"""
        plan = {
            "timestamp": datetime.now().isoformat(),
            "scripts_analyzed": len(analyses),
            "consolidation_recommendations": [],
            "keep_scripts": [],
            "consolidate_into": None,
            "archive_scripts": [],
            "rationale": []
        }

        # Analyze which script should be the primary (largest, most features)
        primary = max(analyses, key=lambda a: a.line_count)
        plan["consolidate_into"] = primary.script_path

        # Recommendations
        for analysis in analyses:
            if analysis.script_path == primary.script_path:
                plan["keep_scripts"].append(analysis.script_path)
                plan["rationale"].append(f"Keep {analysis.script_path} as primary (largest: {analysis.line_count} lines)")
            else:
                plan["archive_scripts"].append(analysis.script_path)
                plan["rationale"].append(f"Archive {analysis.script_path} - functionality should merge into {primary.script_path}")

        # Add overlap-based recommendations
        if overlaps["shared_classes"]:
            plan["consolidation_recommendations"].append({
                "type": "shared_classes",
                "description": f"{len(overlaps['shared_classes'])} classes appear in multiple scripts",
                "action": "Consolidate shared classes into single location"
            })

        if overlaps["shared_functions"]:
            plan["consolidation_recommendations"].append({
                "type": "shared_functions",
                "description": f"{len(overlaps['shared_functions'])} functions appear in multiple scripts",
                "action": "Consolidate shared functions into single location"
            })

        return plan

    def analyze_all(self) -> Dict[str, Any]:
        """Analyze all JARVIS scripts"""
        analyses = []

        for script_name in self.jarvis_scripts:
            analysis = self.analyze_script(script_name)
            analyses.append(analysis)

        overlaps = self.find_overlaps(analyses)
        plan = self.generate_consolidation_plan(analyses, overlaps)

        return {
            "analyses": [asdict(a) for a in analyses],
            "overlaps": overlaps,
            "consolidation_plan": plan
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Consolidation Analysis")
        parser.add_argument("--output", type=Path, help="Output JSON file")

        args = parser.parse_args()

        analyzer = JARVISConsolidationAnalyzer(project_root)
        results = analyzer.analyze_all()

        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            print(f"Analysis saved to: {args.output}")
        else:
            print(json.dumps(results, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()