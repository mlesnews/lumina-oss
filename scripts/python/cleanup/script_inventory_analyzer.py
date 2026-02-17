#!/usr/bin/env python3
"""
Script Inventory Analyzer - Phase 1 Discovery Tool

Analyzes all Python scripts in the project to create a comprehensive inventory.
Part of LUMINA 2.0.0 Cleanup Implementation Plan.

Tags: #CLEANUP #INVENTORY #ANALYSIS #PHASE1 @LUMINA
"""

import ast
import json
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ScriptInventoryAnalyzer")


class ScriptInventoryAnalyzer:
    """Analyzes all Python scripts to create comprehensive inventory"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts" / "python"
        self.output_dir = project_root / "data" / "cleanup"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.inventory: List[Dict[str, Any]] = []
        self.categories: Dict[str, List[str]] = defaultdict(list)
        self.imports: Dict[str, Set[str]] = defaultdict(set)
        self.functions: Dict[str, List[str]] = defaultdict(list)
        self.classes: Dict[str, List[str]] = defaultdict(list)

    def analyze_script(self, script_path: Path) -> Optional[Dict[str, Any]]:
        """Analyze a single Python script"""
        try:
            with open(script_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()

            # Parse AST
            try:
                tree = ast.parse(content)
            except SyntaxError:
                logger.warning(f"Syntax error in {script_path}")
                return None

            # Extract metadata
            script_info = {
                "path": str(script_path.relative_to(self.project_root)),
                "full_path": str(script_path),
                "name": script_path.name,
                "size_bytes": script_path.stat().st_size,
                "lines": len(content.splitlines()),
                "last_modified": datetime.fromtimestamp(script_path.stat().st_mtime).isoformat(),
                "imports": [],
                "functions": [],
                "classes": [],
                "docstring": ast.get_docstring(tree),
                "has_main": False,
                "category": self._categorize_script(script_path, content),
            }

            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        script_info["imports"].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        script_info["imports"].append(node.module)

            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    script_info["functions"].append(node.name)
                elif isinstance(node, ast.ClassDef):
                    script_info["classes"].append(node.name)
                elif isinstance(node, ast.If) and isinstance(node.test, ast.Compare):
                    if isinstance(node.test.left, ast.Name) and node.test.left.id == "__name__":
                        script_info["has_main"] = True

            return script_info

        except Exception as e:
            logger.error(f"Error analyzing {script_path}: {e}")
            return None

    def _categorize_script(self, script_path: Path, content: str) -> str:
        """Categorize script by path and content"""
        path_str = str(script_path).lower()
        content_lower = content.lower()

        # Check path patterns
        if "homelab" in path_str:
            return "homelab"
        elif "jarvis" in path_str:
            return "jarvis"
        elif "lumina" in path_str:
            return "lumina_core"
        elif "wopr" in path_str or "simulator" in path_str:
            return "wopr"
        elif "nas" in path_str:
            return "infrastructure_nas"
        elif "docker" in path_str or "container" in path_str:
            return "infrastructure_docker"
        elif "cluster" in path_str or "ultron" in path_str:
            return "infrastructure_cluster"
        elif "ai" in path_str or "ml" in path_str or "model" in path_str:
            return "ai_ml"
        elif "syphon" in path_str:
            return "data_syphon"
        elif "workflow" in path_str or "n8n" in path_str:
            return "workflow"
        elif "monitor" in path_str or "health" in path_str:
            return "monitoring"
        elif "fix" in path_str or "repair" in path_str:
            return "fixes"
        elif "ui" in path_str or "widget" in path_str or "desktop" in path_str:
            return "ui"
        elif "test" in path_str or "demo" in path_str or "example" in path_str:
            return "test_demo"
        elif "utils" in path_str or "helper" in path_str:
            return "utils"
        elif "cleanup" in path_str or "archive" in path_str:
            return "cleanup"
        else:
            return "other"

    def scan_all_scripts(self):
        """Scan all Python scripts in the project"""
        logger.info("=" * 80)
        logger.info("SCRIPT INVENTORY ANALYZER - Phase 1 Discovery")
        logger.info("=" * 80)

        script_files = list(self.scripts_dir.rglob("*.py"))
        logger.info(f"Found {len(script_files)} Python scripts")

        for i, script_path in enumerate(script_files, 1):
            if i % 100 == 0:
                logger.info(f"Analyzing script {i}/{len(script_files)}...")

            # Skip certain directories
            if any(
                skip in str(script_path)
                for skip in ["__pycache__", ".git", "venv", ".venv", "node_modules"]
            ):
                continue

            script_info = self.analyze_script(script_path)
            if script_info:
                self.inventory.append(script_info)
                self.categories[script_info["category"]].append(script_info["path"])

                # Track imports
                for imp in script_info["imports"]:
                    self.imports[script_info["path"]].add(imp)

                # Track functions and classes
                self.functions[script_info["path"]] = script_info["functions"]
                self.classes[script_info["path"]] = script_info["classes"]

        logger.info(f"Analyzed {len(self.inventory)} scripts")

    def generate_reports(self):
        """Generate inventory reports"""
        logger.info("Generating reports...")

        # Full inventory
        inventory_file = self.output_dir / "script_inventory.json"
        with open(inventory_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "total_scripts": len(self.inventory),
                    "inventory": self.inventory,
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info(f"✅ Inventory saved: {inventory_file}")

        # Categories
        categories_file = self.output_dir / "script_categories.json"
        with open(categories_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "categories": {k: len(v) for k, v in self.categories.items()},
                    "category_details": dict(self.categories),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info(f"✅ Categories saved: {categories_file}")

        # Summary statistics
        stats = {
            "timestamp": datetime.now().isoformat(),
            "total_scripts": len(self.inventory),
            "total_lines": sum(s["lines"] for s in self.inventory),
            "total_size_mb": sum(s["size_bytes"] for s in self.inventory) / 1024 / 1024,
            "categories": {k: len(v) for k, v in self.categories.items()},
            "scripts_with_main": len([s for s in self.inventory if s["has_main"]]),
            "scripts_with_docstrings": len([s for s in self.inventory if s["docstring"]]),
            "total_functions": sum(len(s["functions"]) for s in self.inventory),
            "total_classes": sum(len(s["classes"]) for s in self.inventory),
            "total_imports": sum(len(s["imports"]) for s in self.inventory),
        }

        stats_file = self.output_dir / "script_statistics.json"
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Statistics saved: {stats_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("SCRIPT INVENTORY SUMMARY")
        print("=" * 80)
        print(f"Total Scripts: {stats['total_scripts']}")
        print(f"Total Lines: {stats['total_lines']:,}")
        print(f"Total Size: {stats['total_size_mb']:.2f} MB")
        print("\nCategories:")
        for category, count in sorted(
            stats["categories"].items(), key=lambda x: x[1], reverse=True
        ):
            print(f"  {category}: {count}")
        print(f"\nScripts with main: {stats['scripts_with_main']}")
        print(f"Scripts with docstrings: {stats['scripts_with_docstrings']}")
        print(f"Total functions: {stats['total_functions']}")
        print(f"Total classes: {stats['total_classes']}")
        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Script Inventory Analyzer - Phase 1 Discovery")
    parser.add_argument("--output-dir", help="Output directory (default: data/cleanup)")

    args = parser.parse_args()

    analyzer = ScriptInventoryAnalyzer(project_root)

    if args.output_dir:
        analyzer.output_dir = Path(args.output_dir)
        analyzer.output_dir.mkdir(parents=True, exist_ok=True)

    analyzer.scan_all_scripts()
    analyzer.generate_reports()


if __name__ == "__main__":
    main()
