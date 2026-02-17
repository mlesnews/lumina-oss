#!/usr/bin/env python3
"""
JARVIS Script Consolidation Analyzer

Analyzes all Python scripts to identify consolidation opportunities.
Categorizes scripts, finds duplicates, and suggests consolidation strategies.

Tags: #CONSOLIDATION #ANALYSIS #SCRIPT_MANAGEMENT @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Any, Set
from datetime import datetime

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

logger = get_logger("JARVISScriptConsolidation")


class ScriptConsolidationAnalyzer:
    """Analyze scripts for consolidation opportunities"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.scripts_dir = project_root / "scripts" / "python"
        self.data_dir = project_root / "data" / "script_consolidation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.scripts = []
        self.categories = defaultdict(list)
        self.duplicates = defaultdict(list)
        self.similar = defaultdict(list)
        self.patterns = Counter()

    def find_all_scripts(self) -> List[Path]:
        """Find all Python scripts"""
        scripts = []
        for script_path in self.scripts_dir.rglob("*.py"):
            # Skip cache, data, and subdirectories
            if any(skip in str(script_path) for skip in ["__pycache__", "data", "anime_production"]):
                continue
            scripts.append(script_path)
        return sorted(scripts)

    def categorize_script(self, script_path: Path) -> List[str]:
        """Categorize a script based on name and content"""
        name = script_path.stem.lower()
        categories = []

        # Prefix-based categories
        prefixes = {
            "jarvis_": "jarvis",
            "cursor_": "cursor",
            "manus_": "manus",
            "marvin_": "marvin",
            "r5_": "r5",
            "v3_": "v3",
            "ironman_": "ironman",
            "anakin_": "anakin",
            "babelfish_": "babelfish",
            "atlas_": "atlas",
            "dewey_": "dewey",
            "deathstar_": "deathstar",
            "boss_fight_": "boss_fight",
            "deep_thought": "deep_thought",
            "ai_": "ai",
            "auto_": "automation",
            "deploy_": "deployment",
            "configure_": "configuration",
            "check_": "diagnostics",
            "create_": "creation",
            "analyze_": "analysis",
            "audit_": "audit",
            "diagnose_": "diagnostics",
            "fix_": "fix",
            "troubleshoot_": "troubleshooting",
            "repair_": "repair",
            "unlock_": "unlock",
            "enable_": "enable",
            "disable_": "disable",
            "start_": "start",
            "stop_": "stop",
            "launch_": "launch",
            "run_": "run",
            "execute_": "execution",
            "process_": "processing",
            "handle_": "handling",
            "manage_": "management",
            "monitor_": "monitoring",
            "track_": "tracking",
            "sync_": "sync",
            "convert_": "conversion",
            "transform_": "transformation",
            "migrate_": "migration",
            "backup_": "backup",
            "restore_": "restore",
            "cleanup_": "cleanup",
            "archive_": "archive",
            "remove_": "remove",
            "delete_": "delete",
            "update_": "update",
            "apply_": "apply",
            "complete_": "completion",
            "finish_": "finish",
            "end_": "end",
        }

        for prefix, category in prefixes.items():
            if name.startswith(prefix):
                categories.append(category)
                break

        # Action-based categories
        actions = {
            "monitor": "monitoring",
            "track": "tracking",
            "check": "diagnostics",
            "diagnose": "diagnostics",
            "fix": "fix",
            "repair": "repair",
            "troubleshoot": "troubleshooting",
            "configure": "configuration",
            "setup": "setup",
            "deploy": "deployment",
            "manage": "management",
            "process": "processing",
            "handle": "handling",
            "sync": "sync",
            "convert": "conversion",
            "transform": "transformation",
            "migrate": "migration",
            "backup": "backup",
            "restore": "restore",
            "cleanup": "cleanup",
            "archive": "archive",
        }

        for action, category in actions.items():
            if action in name:
                if category not in categories:
                    categories.append(category)

        # Domain-based categories
        domains = {
            "keyboard": "keyboard",
            "lighting": "lighting",
            "model": "model",
            "ai": "ai",
            "llm": "llm",
            "voice": "voice",
            "audio": "audio",
            "video": "video",
            "email": "email",
            "nas": "nas",
            "azure": "azure",
            "aws": "aws",
            "docker": "docker",
            "cluster": "cluster",
            "health": "health",
            "log": "logging",
            "ask": "ask",
            "ticket": "ticket",
            "workflow": "workflow",
            "template": "template",
            "syphon": "syphon",
            "r5": "r5",
            "compound": "compound",
            "unified": "unified",
        }

        for domain, category in domains.items():
            if domain in name:
                if category not in categories:
                    categories.append(category)

        # Default category
        if not categories:
            categories.append("other")

        return categories

    def analyze_script_content(self, script_path: Path) -> Dict[str, Any]:
        """Analyze script content for patterns"""
        try:
            content = script_path.read_text(encoding='utf-8', errors='ignore')

            # Extract imports
            imports = re.findall(r'^import\s+(\S+)', content, re.MULTILINE)
            imports.extend(re.findall(r'^from\s+(\S+)\s+import', content, re.MULTILINE))

            # Extract classes
            classes = re.findall(r'^class\s+(\w+)', content, re.MULTILINE)

            # Extract functions
            functions = re.findall(r'^def\s+(\w+)', content, re.MULTILINE)

            # Extract docstrings
            docstring = re.search(r'"""(.*?)"""', content, re.DOTALL)
            docstring_text = docstring.group(1) if docstring else ""

            # Extract tags
            tags = re.findall(r'#(\w+)', content)
            tags.extend(re.findall(r'@(\w+)', content))

            return {
                "imports": imports,
                "classes": classes,
                "functions": functions,
                "docstring": docstring_text[:200] if docstring_text else "",
                "tags": tags,
                "lines": len(content.splitlines()),
                "size": len(content)
            }
        except Exception as e:
            logger.warning(f"Error analyzing {script_path}: {e}")
            return {}

    def find_duplicates(self) -> Dict[str, List[Path]]:
        """Find duplicate or very similar scripts"""
        duplicates = defaultdict(list)

        # Group by name patterns
        name_groups = defaultdict(list)
        for script in self.scripts:
            # Normalize name (remove prefixes, suffixes)
            normalized = script.stem.lower()
            normalized = re.sub(r'^(jarvis_|cursor_|manus_|marvin_|r5_|v3_|ironman_|anakin_)', '', normalized)
            normalized = re.sub(r'(_fix|_repair|_troubleshoot|_diagnose|_check|_monitor|_manage|_handle|_process)$', '', normalized)
            name_groups[normalized].append(script)

        # Find groups with multiple files
        for normalized, scripts in name_groups.items():
            if len(scripts) > 1:
                duplicates[normalized] = scripts

        return duplicates

    def find_similar_scripts(self) -> Dict[str, List[Dict[str, Any]]]:
        """Find scripts with similar functionality"""
        similar = defaultdict(list)

        # Group by category and analyze content similarity
        for script in self.scripts:
            categories = self.categorize_script(script)
            content = self.analyze_script_content(script)

            for category in categories:
                similar[category].append({
                    "path": str(script.relative_to(self.project_root)),
                    "name": script.stem,
                    "categories": categories,
                    "content": content
                })

        return similar

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis"""
        logger.info("🔍 Starting script consolidation analysis...")

        # Find all scripts
        self.scripts = self.find_all_scripts()
        logger.info(f"📊 Found {len(self.scripts)} scripts")

        # Categorize scripts
        for script in self.scripts:
            categories = self.categorize_script(script)
            for category in categories:
                self.categories[category].append(str(script.relative_to(self.project_root)))

        # Find duplicates
        self.duplicates = self.find_duplicates()

        # Find similar scripts
        self.similar = self.find_similar_scripts()

        # Generate report
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_scripts": len(self.scripts),
            "categories": {
                cat: len(scripts) for cat, scripts in self.categories.items()
            },
            "duplicates": {
                name: [str(s.relative_to(self.project_root)) for s in scripts]
                for name, scripts in self.duplicates.items()
            },
            "category_details": {
                cat: scripts[:10]  # Top 10 per category
                for cat, scripts in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True)[:20]
            },
            "consolidation_opportunities": self._identify_consolidation_opportunities()
        }

        return report

    def _identify_consolidation_opportunities(self) -> List[Dict[str, Any]]:
        """Identify specific consolidation opportunities"""
        opportunities = []

        # Duplicate scripts
        for name, scripts in self.duplicates.items():
            if len(scripts) > 1:
                opportunities.append({
                    "type": "duplicate",
                    "name": name,
                    "scripts": [str(s.relative_to(self.project_root)) for s in scripts],
                    "recommendation": f"Consolidate {len(scripts)} scripts into one"
                })

        # Category-based consolidation
        for category, scripts in sorted(self.categories.items(), key=lambda x: len(x[1]), reverse=True):
            if len(scripts) > 5:
                opportunities.append({
                    "type": "category_consolidation",
                    "category": category,
                    "count": len(scripts),
                    "sample_scripts": scripts[:5],
                    "recommendation": f"Consider consolidating {len(scripts)} {category} scripts into modules"
                })

        return opportunities

    def save_report(self, report: Dict[str, Any]):
        try:
            """Save analysis report"""
            report_file = self.data_dir / f"consolidation_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)

            logger.info(f"💾 Report saved to: {report_file}")
            return report_file

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
    def print_summary(self, report: Dict[str, Any]):
        """Print analysis summary"""
        print("\n" + "=" * 80)
        print("📊 JARVIS SCRIPT CONSOLIDATION ANALYSIS")
        print("=" * 80)
        print(f"📅 Timestamp: {report['timestamp']}")
        print(f"📁 Total Scripts: {report['total_scripts']}")
        print()

        print("📂 Categories (Top 20):")
        print("-" * 80)
        for cat, count in sorted(report['categories'].items(), key=lambda x: x[1], reverse=True)[:20]:
            print(f"   {cat:30} {count:4} scripts")
        print()

        print("🔄 Duplicates Found:")
        print("-" * 80)
        for name, scripts in list(report['duplicates'].items())[:10]:
            print(f"   {name}: {len(scripts)} scripts")
            for script in scripts[:3]:
                print(f"      - {script}")
        print()

        print("💡 Consolidation Opportunities:")
        print("-" * 80)
        for opp in report['consolidation_opportunities'][:20]:
            print(f"   [{opp['type']}] {opp.get('name', opp.get('category', 'unknown'))}")
            print(f"      {opp['recommendation']}")
        print()

        print("=" * 80)


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Script Consolidation Analyzer")
        parser.add_argument("--analyze", action="store_true", help="Run analysis")
        parser.add_argument("--report", action="store_true", help="Show report summary")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analyzer = ScriptConsolidationAnalyzer(project_root)

        if args.analyze or not args.report:
            report = analyzer.analyze()
            report_file = analyzer.save_report(report)
            analyzer.print_summary(report)
            print(f"\n💾 Full report: {report_file}")
        else:
            # Load latest report
            reports = sorted(analyzer.data_dir.glob("consolidation_analysis_*.json"))
            if reports:
                with open(reports[-1], 'r', encoding='utf-8') as f:
                    report = json.load(f)
                analyzer.print_summary(report)
            else:
                print("❌ No reports found. Run with --analyze first.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()