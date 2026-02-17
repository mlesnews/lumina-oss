#!/usr/bin/env python3
"""
JARVIS Script Consolidator

Consolidates similar scripts into unified modules.
Groups scripts by functionality and creates consolidated versions.

Tags: #CONSOLIDATION #SCRIPT_MANAGEMENT #MODULARIZATION @JARVIS @LUMINA
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISScriptConsolidator")


class ScriptConsolidator:
    """Consolidate scripts into modules"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts" / "python"
        self.archive_dir = project_root / "scripts" / "python" / "_archived_consolidated"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        self.consolidation_plan = {}
        self.consolidated_modules = {}

    def load_analysis(self) -> Dict[str, Any]:
        try:
            """Load latest consolidation analysis"""
            analysis_dir = project_root / "data" / "script_consolidation"
            reports = sorted(analysis_dir.glob("consolidation_analysis_*.json"))
            if not reports:
                raise FileNotFoundError("No consolidation analysis found. Run analyzer first.")

            with open(reports[-1], 'r', encoding='utf-8') as f:
                return json.load(f)

        except Exception as e:
            self.logger.error(f"Error in load_analysis: {e}", exc_info=True)
            raise
    def create_consolidation_plan(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Create consolidation plan from analysis"""
        plan = {
            "timestamp": datetime.now().isoformat(),
            "modules": {},
            "duplicates_to_merge": [],
            "categories_to_consolidate": []
        }

        # Handle duplicates first
        for name, scripts in analysis.get("duplicates", {}).items():
            if len(scripts) > 1:
                plan["duplicates_to_merge"].append({
                    "name": name,
                    "scripts": scripts,
                    "target_module": f"consolidated_{name}.py"
                })

        # Handle large categories - use category_details which has script lists
        category_details = analysis.get("category_details", {})
        for category, scripts in category_details.items():
            if len(scripts) > 10:  # Only consolidate categories with 10+ scripts
                plan["categories_to_consolidate"].append({
                    "category": category,
                    "count": len(scripts),
                    "scripts": scripts[:20]  # Limit to 20 for initial consolidation
                })

        return plan

    def consolidate_duplicates(self, duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Consolidate duplicate scripts"""
        results = {
            "consolidated": [],
            "archived": [],
            "errors": []
        }

        for dup in duplicates:
            try:
                scripts = [self.project_root / s for s in dup["scripts"]]
                target = self.scripts_dir / dup["target_module"]

                # Read all scripts and merge
                merged_content = self._merge_scripts(scripts, dup["name"])

                # Write consolidated script
                target.write_text(merged_content, encoding='utf-8')
                results["consolidated"].append(str(target.relative_to(self.project_root)))

                # Archive originals
                for script in scripts:
                    if script.exists():
                        archive_path = self.archive_dir / script.name
                        shutil.move(str(script), str(archive_path))
                        results["archived"].append(str(script.relative_to(self.project_root)))

                logger.info(f"✅ Consolidated {len(scripts)} scripts into {target.name}")

            except Exception as e:
                logger.error(f"❌ Error consolidating {dup['name']}: {e}")
                results["errors"].append({"name": dup["name"], "error": str(e)})

        return results

    def _merge_scripts(self, scripts: List[Path], name: str) -> str:
        """Merge multiple scripts into one"""
        merged = f'''#!/usr/bin/env python3
"""
Consolidated {name.replace('_', ' ').title()}

This module consolidates multiple related scripts into a unified interface.
Generated: {datetime.now().isoformat()}

Tags: #CONSOLIDATED #MODULE @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("Consolidated{name.title().replace('_', '')}")


'''

        # Add imports and classes from all scripts
        all_imports = set()
        all_classes = []
        all_functions = []

        for script in scripts:
            if not script.exists():
                continue
            try:
                content = script.read_text(encoding='utf-8', errors='ignore')

                # Extract imports
                import re
                imports = re.findall(r'^(import\s+\S+|from\s+\S+\s+import\s+[^\n]+)', content, re.MULTILINE)
                all_imports.update(imports)

                # Extract classes
                classes = re.findall(r'^class\s+(\w+).*?:', content, re.MULTILINE)
                for cls in classes:
                    # Extract class definition
                    class_match = re.search(rf'^class\s+{cls}.*?(?=^class\s+\w+|^def\s+\w+|^if\s+__name__|$)', content, re.MULTILINE | re.DOTALL)
                    if class_match:
                        all_classes.append(class_match.group(0))

                # Extract main functions
                main_funcs = re.findall(r'^def\s+(main|run|execute).*?(?=^def\s+\w+|^if\s+__name__|$)', content, re.MULTILINE | re.DOTALL)
                all_functions.extend(main_funcs)

            except Exception as e:
                logger.warning(f"Error processing {script}: {e}")

        # Add imports
        merged += "\n".join(sorted(all_imports)) + "\n\n"

        # Add classes
        for cls in all_classes:
            merged += cls + "\n\n"

        # Add functions
        for func in all_functions:
            merged += func + "\n\n"

        # Add main entry point
        merged += f'''
def main():
    """Main entry point - consolidated from {len(scripts)} scripts"""
    import argparse

    parser = argparse.ArgumentParser(description="Consolidated {name.replace('_', ' ').title()}")
    parser.add_argument("--list", action="store_true", help="List available functions")

    args = parser.parse_args()

    if args.list:
        print("Available consolidated functions:")
        # List functions
    else:
        logger.info("Consolidated module loaded")


if __name__ == "__main__":
    main()
'''

        return merged

    def consolidate(self, dry_run: bool = False) -> Dict[str, Any]:
        try:
            """Run consolidation"""
            logger.info("🔄 Starting script consolidation...")

            # Load analysis
            analysis = self.load_analysis()

            # Create plan
            plan = self.create_consolidation_plan(analysis)

            if dry_run:
                logger.info("🔍 DRY RUN - No changes will be made")
                return {
                    "plan": plan,
                    "dry_run": True
                }

            # Consolidate duplicates
            results = self.consolidate_duplicates(plan["duplicates_to_merge"])

            # Save consolidation report
            report = {
                "timestamp": datetime.now().isoformat(),
                "plan": plan,
                "results": results
            }

            report_file = self.project_root / "data" / "script_consolidation" / f"consolidation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"💾 Consolidation report saved: {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in consolidate: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Script Consolidator")
        parser.add_argument("--dry-run", action="store_true", help="Show plan without making changes")
        parser.add_argument("--consolidate", action="store_true", help="Run consolidation")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        consolidator = ScriptConsolidator(project_root)

        if args.consolidate or not args.dry_run:
            result = consolidator.consolidate(dry_run=args.dry_run)

            if args.dry_run:
                print("\n" + "=" * 80)
                print("🔍 CONSOLIDATION PLAN (DRY RUN)")
                print("=" * 80)
                print(json.dumps(result["plan"], indent=2, default=str))
            else:
                print("\n" + "=" * 80)
                print("✅ CONSOLIDATION COMPLETE")
                print("=" * 80)
                print(f"📊 Consolidated: {len(result['results']['consolidated'])} modules")
                print(f"📦 Archived: {len(result['results']['archived'])} scripts")
                if result['results']['errors']:
                    print(f"❌ Errors: {len(result['results']['errors'])}")
        else:
            result = consolidator.consolidate(dry_run=True)
            print(json.dumps(result["plan"], indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()