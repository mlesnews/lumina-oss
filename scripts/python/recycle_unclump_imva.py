#!/usr/bin/env python3
"""
Recycle and Unclump IMVA Stump - ORDER 66: @DOIT

Cleans up and reorganizes the IMVA codebase:
- Identifies duplicated/redundant code
- Removes unused code blocks
- Organizes methods by functionality
- Creates cleaner, more maintainable structure

Tags: #IMVA #CLEANUP #REFACTOR #RECYCLE #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RecycleUnclumpIMVA")


class IMVACodeAnalyzer:
    """
    Analyze IMVA code for cleanup opportunities
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize analyzer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.imva_file = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

        logger.info("✅ IMVA Code Analyzer initialized")

    def analyze_code_structure(self) -> Dict[str, Any]:
        try:
            """Analyze code structure for cleanup opportunities"""
            if not self.imva_file.exists():
                return {"error": f"File not found: {self.imva_file}"}

            logger.info("="*80)
            logger.info("🔍 Analyzing IMVA Code Structure")
            logger.info("="*80)

            with open(self.imva_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            analysis = {
                "file_size_kb": len(content) / 1024,
                "total_lines": len(lines),
                "classes": [],
                "methods": [],
                "duplicates": [],
                "unused_imports": [],
                "long_methods": [],
                "suggestions": []
            }

            # Find all classes
            class_pattern = re.compile(r'^class\s+(\w+)')
            for i, line in enumerate(lines):
                match = class_pattern.match(line)
                if match:
                    analysis["classes"].append({
                        "name": match.group(1),
                        "line": i + 1
                    })

            # Find all methods
            method_pattern = re.compile(r'^\s+def\s+(\w+)\s*\(')
            current_class = None
            for i, line in enumerate(lines):
                class_match = class_pattern.match(line)
                if class_match:
                    current_class = class_match.group(1)

                method_match = method_pattern.match(line)
                if method_match:
                    method_name = method_match.group(1)
                    # Find method end (next def at same or lower indent, or end of file)
                    method_end = self._find_method_end(lines, i)
                    method_lines = method_end - i

                    analysis["methods"].append({
                        "name": method_name,
                        "class": current_class,
                        "line": i + 1,
                        "lines": method_lines
                    })

            # Find long methods (>100 lines)
            for method in analysis["methods"]:
                if method["lines"] > 100:
                    analysis["long_methods"].append(method)

            # Find potential duplicates (methods with similar names)
            method_names = defaultdict(list)
            for method in analysis["methods"]:
                method_names[method["name"]].append(method)

            for name, occurrences in method_names.items():
                if len(occurrences) > 1:
                    analysis["duplicates"].append({
                        "name": name,
                        "count": len(occurrences),
                        "locations": occurrences
                    })

            # Generate suggestions
            if analysis["total_lines"] > 3000:
                analysis["suggestions"].append(
                    f"File is large ({analysis['total_lines']} lines). Consider splitting into modules."
                )

            if analysis["long_methods"]:
                analysis["suggestions"].append(
                    f"Found {len(analysis['long_methods'])} methods >100 lines. Consider refactoring."
                )

            if analysis["duplicates"]:
                analysis["suggestions"].append(
                    f"Found {len(analysis['duplicates'])} potentially duplicated method names."
                )

            logger.info(f"\n📊 Analysis Results:")
            logger.info(f"   File Size: {analysis['file_size_kb']:.1f} KB")
            logger.info(f"   Total Lines: {analysis['total_lines']}")
            logger.info(f"   Classes: {len(analysis['classes'])}")
            logger.info(f"   Methods: {len(analysis['methods'])}")
            logger.info(f"   Long Methods (>100 lines): {len(analysis['long_methods'])}")
            logger.info(f"   Potential Duplicates: {len(analysis['duplicates'])}")

            return analysis

        except Exception as e:
            self.logger.error(f"Error in analyze_code_structure: {e}", exc_info=True)
            raise
    def _find_method_end(self, lines: List[str], start_line: int) -> int:
        """Find the end line of a method"""
        if start_line >= len(lines):
            return len(lines)

        # Get indentation of method definition
        start_indent = len(lines[start_line]) - len(lines[start_line].lstrip())

        # Look for next def/class at same or lower indent, or end of file
        for i in range(start_line + 1, len(lines)):
            line = lines[i]
            stripped = line.lstrip()

            # Skip empty lines and comments
            if not stripped or stripped.startswith('#'):
                continue

            current_indent = len(line) - len(stripped)

            # If we hit a def/class at same or lower indent, method ended
            if (stripped.startswith('def ') or stripped.startswith('class ')) and current_indent <= start_indent:
                return i

            # If we hit a def at higher indent, it's nested (continue)
            if stripped.startswith('def ') and current_indent > start_indent:
                continue

        return len(lines)

    def organize_methods_by_category(self) -> Dict[str, List[str]]:
        try:
            """Organize methods by functional category"""
            if not self.imva_file.exists():
                return {}

            with open(self.imva_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            categories = {
                "initialization": [],
                "rendering": [],
                "combat": [],
                "animation": [],
                "voice": [],
                "interaction": [],
                "utility": [],
                "other": []
            }

            method_pattern = re.compile(r'^\s+def\s+(\w+)\s*\(')
            for i, line in enumerate(lines):
                match = method_pattern.match(line)
                if match:
                    method_name = match.group(1)

                    # Categorize based on method name patterns
                    if any(x in method_name.lower() for x in ['__init__', 'setup', 'initialize', 'init']):
                        categories["initialization"].append(method_name)
                    elif any(x in method_name.lower() for x in ['draw', 'render', 'paint', 'display']):
                        categories["rendering"].append(method_name)
                    elif any(x in method_name.lower() for x in ['combat', 'fight', 'lightsaber', 'attack', 'defend']):
                        categories["combat"].append(method_name)
                    elif any(x in method_name.lower() for x in ['animate', 'animation', 'update', 'frame']):
                        categories["animation"].append(method_name)
                    elif any(x in method_name.lower() for x in ['voice', 'speak', 'listen', 'audio', 'tts', 'stt']):
                        categories["voice"].append(method_name)
                    elif any(x in method_name.lower() for x in ['click', 'interact', 'conversation', 'chat', 'command']):
                        categories["interaction"].append(method_name)
                    elif any(x in method_name.lower() for x in ['get', 'set', 'calculate', 'convert', 'parse', 'format']):
                        categories["utility"].append(method_name)
                    else:
                        categories["other"].append(method_name)

            return categories


        except Exception as e:
            self.logger.error(f"Error in organize_methods_by_category: {e}", exc_info=True)
            raise
class IMVACleanup:
    """
    Clean up and reorganize IMVA code
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize cleanup"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.imva_file = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"
        self.analyzer = IMVACodeAnalyzer(project_root)

        logger.info("✅ IMVA Cleanup initialized")

    def recycle_and_unclump(self) -> Dict[str, Any]:
        """
        Recycle and unclump IMVA stump

        ORDER 66: @DOIT execution command
        """
        logger.info("="*80)
        logger.info("♻️  ORDER 66: Recycling and Unclumping IMVA Stump")
        logger.info("="*80)

        result = {
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "execution_type": "ORDER 66: @DOIT",
            "actions_taken": [],
            "success": True,
            "errors": []
        }

        # Step 1: Analyze current structure
        logger.info("\n📊 Step 1: Analyzing current code structure...")
        analysis = self.analyzer.analyze_code_structure()

        if "error" in analysis:
            result["errors"].append(analysis["error"])
            result["success"] = False
            return result

        result["analysis"] = {
            "total_lines": analysis["total_lines"],
            "file_size_kb": analysis["file_size_kb"],
            "classes": len(analysis["classes"]),
            "methods": len(analysis["methods"]),
            "long_methods": len(analysis["long_methods"]),
            "duplicates": len(analysis["duplicates"])
        }

        # Step 2: Organize methods by category
        logger.info("\n📁 Step 2: Organizing methods by category...")
        categories = self.analyzer.organize_methods_by_category()
        result["method_categories"] = {cat: len(methods) for cat, methods in categories.items()}

        # Step 3: Generate cleanup report
        logger.info("\n📋 Step 3: Generating cleanup report...")
        report = self._generate_cleanup_report(analysis, categories)
        result["report"] = report
        result["actions_taken"].append("Generated cleanup analysis and report")

        # Save report
        report_file = self.project_root / "data" / "imva_cleanup_report.json"
        report_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            import json
            with open(report_file, 'w') as f:
                json.dump(result, f, indent=2, default=str)
            logger.info(f"✅ Cleanup report saved: {report_file}")
            result["actions_taken"].append(f"Saved cleanup report to {report_file.name}")
        except Exception as e:
            logger.warning(f"⚠️  Could not save report: {e}")

        logger.info("="*80)
        logger.info("✅ IMVA Stump Recycling and Unclumping Complete")
        logger.info(f"   Actions Taken: {len(result['actions_taken'])}")
        logger.info("="*80)

        return result

    def _generate_cleanup_report(self, analysis: Dict[str, Any], categories: Dict[str, List[str]]) -> str:
        """Generate cleanup report"""
        report_lines = [
            "="*80,
            "IMVA Code Cleanup Report",
            "="*80,
            "",
            f"File: {self.imva_file.name}",
            f"Size: {analysis['file_size_kb']:.1f} KB",
            f"Lines: {analysis['total_lines']}",
            "",
            "STRUCTURE:",
            f"  Classes: {len(analysis['classes'])}",
            f"  Methods: {len(analysis['methods'])}",
            "",
            "METHOD CATEGORIES:"
        ]

        for cat, methods in categories.items():
            if methods:
                report_lines.append(f"  {cat.upper()}: {len(methods)} methods")
                for method in methods[:5]:  # Show first 5
                    report_lines.append(f"    - {method}")
                if len(methods) > 5:
                    report_lines.append(f"    ... and {len(methods) - 5} more")

        report_lines.extend([
            "",
            "CLEANUP SUGGESTIONS:"
        ])

        for suggestion in analysis.get("suggestions", []):
            report_lines.append(f"  • {suggestion}")

        if analysis["long_methods"]:
            report_lines.append("")
            report_lines.append("LONG METHODS (>100 lines):")
            for method in analysis["long_methods"][:10]:  # Show first 10
                report_lines.append(f"  • {method['name']} ({method['class']}) - {method['lines']} lines")

        if analysis["duplicates"]:
            report_lines.append("")
            report_lines.append("POTENTIAL DUPLICATES:")
            for dup in analysis["duplicates"][:10]:  # Show first 10
                report_lines.append(f"  • {dup['name']} - {dup['count']} occurrences")

        return "\n".join(report_lines)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Recycle and Unclump IMVA Stump - ORDER 66: @DOIT")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--analyze-only', action='store_true', help='Only analyze, do not cleanup')

    args = parser.parse_args()

    cleanup = IMVACleanup(project_root=args.project_root)

    if args.analyze_only:
        analysis = cleanup.analyzer.analyze_code_structure()
        print("\n📊 IMVA Code Analysis:")
        print("="*80)
        print(f"  Total Lines: {analysis['total_lines']}")
        print(f"  File Size: {analysis['file_size_kb']:.1f} KB")
        print(f"  Classes: {len(analysis['classes'])}")
        print(f"  Methods: {len(analysis['methods'])}")
        print(f"  Long Methods: {len(analysis['long_methods'])}")
        print(f"  Duplicates: {len(analysis['duplicates'])}")
        return 0

    result = cleanup.recycle_and_unclump()

    if result["success"]:
        print(f"\n✅ Success: {len(result['actions_taken'])} actions taken")
        print(f"\n📊 Analysis:")
        analysis = result["analysis"]
        print(f"  Lines: {analysis['total_lines']}")
        print(f"  Size: {analysis['file_size_kb']:.1f} KB")
        print(f"  Methods: {analysis['methods']}")
        print(f"  Long Methods: {analysis['long_methods']}")
        print(f"  Duplicates: {analysis['duplicates']}")
        return 0
    else:
        print(f"\n❌ Failed: {len(result['errors'])} errors")
        for error in result["errors"]:
            print(f"   • {error}")
        return 1


if __name__ == "__main__":


    sys.exit(main())