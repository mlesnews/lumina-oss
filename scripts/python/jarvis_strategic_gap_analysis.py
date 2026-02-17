#!/usr/bin/env python3
"""
JARVIS Strategic Gap Analysis - Bobby Fischer Meets Tinker Tailor Soldier Spy

Strategic analysis system to find gaps, missing pieces, and hidden issues.
Bobby Fischer-style pattern recognition + Tinker Tailor Soldier Spy gap detection.

Tags: #BOBBY_FISCHER #TINKER_TAILOR #STRATEGIC #GAP_ANALYSIS #MINDTHEGAP #FINDITFIRST @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
import ast
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISStrategicGap")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISStrategicGap")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISStrategicGap")


class StrategicGapAnalyzer:
    """Bobby Fischer + Tinker Tailor Soldier Spy gap analysis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "strategic_gap_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.analysis_file = self.data_dir / "gap_analysis.jsonl"
        self.gaps_file = self.data_dir / "gaps_found.json"

        # Known systems and their expected integrations
        self.known_systems = {
            "jarvis_mental_health_advancement.py": {
                "integrations": ["lumina_logger_comprehensive", "jarvis_ai_identity_self_awareness"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            },
            "jarvis_friendship_balance.py": {
                "integrations": ["lumina_logger_comprehensive"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            },
            "jarvis_literature_media_interest.py": {
                "integrations": ["lumina_logger_comprehensive", "jarvis_ttrpg_ai_dm_audiobook"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            },
            "jarvis_paradigm_shift_reality_inversion.py": {
                "integrations": ["lumina_logger_comprehensive", "jarvis_ttrpg_ai_dm_audiobook"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            },
            "jarvis_family_entertainment_spectrum.py": {
                "integrations": ["lumina_logger_comprehensive", "jarvis_literature_media_interest"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            },
            "jarvis_come_to_life.py": {
                "integrations": ["lumina_logger_comprehensive"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            },
            "jarvis_autoproc_executor.py": {
                "integrations": ["lumina_logger_comprehensive"],
                "dependencies": ["config/ai_post_startup_checklist.json"]
            }
        }

    def find_gaps(self) -> Dict[str, Any]:
        """Find gaps - Bobby Fischer strategic analysis"""
        gaps = {
            "analysis_id": f"gap_analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "strategy": "Bobby Fischer + Tinker Tailor Soldier Spy",
            "gaps_found": [],
            "missing_integrations": [],
            "missing_dependencies": [],
            "orphaned_files": [],
            "broken_links": [],
            "pattern_anomalies": []
        }

        logger.info("=" * 80)
        logger.info("♟️ STRATEGIC GAP ANALYSIS")
        logger.info("=" * 80)
        logger.info("Mode: Bobby Fischer pattern recognition")
        logger.info("Mission: Tinker Tailor Soldier Spy - find the gaps")
        logger.info("=" * 80)

        # Check each known system
        scripts_dir = self.project_root / "scripts" / "python"
        for system_file, expected in self.known_systems.items():
            system_path = scripts_dir / system_file

            if not system_path.exists():
                gaps["missing_dependencies"].append({
                    "type": "missing_system",
                    "file": system_file,
                    "expected_location": str(system_path),
                    "severity": "high"
                })
                continue

            # Check integrations
            missing_integrations = self._check_integrations(system_path, expected.get("integrations", []))
            if missing_integrations:
                gaps["missing_integrations"].extend(missing_integrations)

            # Check dependencies
            missing_deps = self._check_dependencies(expected.get("dependencies", []))
            if missing_deps:
                gaps["missing_dependencies"].extend(missing_deps)

        # Find orphaned files (files not referenced)
        gaps["orphaned_files"] = self._find_orphaned_files()

        # Find broken links (imports that don't exist)
        gaps["broken_links"] = self._find_broken_imports()

        # Pattern anomalies (Bobby Fischer - see patterns others miss)
        gaps["pattern_anomalies"] = self._find_pattern_anomalies()

        # Compile gaps list
        gaps["gaps_found"] = self._compile_gaps_list(gaps)

        # Save analysis
        try:
            with open(self.analysis_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(gaps) + '\n')

            with open(self.gaps_file, 'w', encoding='utf-8') as f:
                json.dump(gaps, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving gap analysis: {e}")

        logger.info(f"🔍 Gaps found: {len(gaps['gaps_found'])}")
        logger.info(f"   Missing integrations: {len(gaps['missing_integrations'])}")
        logger.info(f"   Missing dependencies: {len(gaps['missing_dependencies'])}")
        logger.info(f"   Orphaned files: {len(gaps['orphaned_files'])}")
        logger.info(f"   Broken links: {len(gaps['broken_links'])}")
        logger.info(f"   Pattern anomalies: {len(gaps['pattern_anomalies'])}")

        return gaps

    def _check_integrations(self, file_path: Path, expected_integrations: List[str]) -> List[Dict[str, Any]]:
        """Check if expected integrations exist in file"""
        missing = []

        if not file_path.exists():
            return missing

        try:
            content = file_path.read_text(encoding='utf-8')

            for integration in expected_integrations:
                # Check if integration is imported or referenced
                if integration not in content:
                    missing.append({
                        "type": "missing_integration",
                        "file": file_path.name,
                        "missing": integration,
                        "severity": "medium",
                        "note": "Expected integration not found in file"
                    })
        except Exception as e:
            logger.debug(f"Error checking integrations in {file_path}: {e}")

        return missing

    def _check_dependencies(self, dependencies: List[str]) -> List[Dict[str, Any]]:
        try:
            """Check if dependencies exist"""
            missing = []

            for dep in dependencies:
                dep_path = self.project_root / dep
                if not dep_path.exists():
                    missing.append({
                        "type": "missing_dependency",
                        "dependency": dep,
                        "expected_location": str(dep_path),
                        "severity": "high"
                    })

            return missing

        except Exception as e:
            self.logger.error(f"Error in _check_dependencies: {e}", exc_info=True)
            raise
    def _find_orphaned_files(self) -> List[Dict[str, Any]]:
        """Find files that aren't referenced anywhere (Tinker Tailor - find the mole)"""
        orphaned = []
        scripts_dir = self.project_root / "scripts" / "python"

        if not scripts_dir.exists():
            return orphaned

        # Get all Python files
        all_files = list(scripts_dir.glob("*.py"))

        # Check if each file is referenced
        for file_path in all_files:
            if file_path.name.startswith("__"):
                continue

            # Check if file is in startup checklist
            checklist_path = self.project_root / "config" / "ai_post_startup_checklist.json"
            referenced = False

            if checklist_path.exists():
                try:
                    with open(checklist_path, 'r', encoding='utf-8') as f:
                        checklist = json.load(f)
                        checklist_str = json.dumps(checklist)
                        if file_path.name in checklist_str:
                            referenced = True
                except Exception:
                    pass

            # Check if file is imported by other files
            if not referenced:
                for other_file in all_files:
                    if other_file == file_path:
                        continue
                    try:
                        content = other_file.read_text(encoding='utf-8')
                        if file_path.stem in content:
                            referenced = True
                            break
                    except Exception:
                        pass

            if not referenced:
                orphaned.append({
                    "file": file_path.name,
                    "path": str(file_path),
                    "severity": "low",
                    "note": "File not referenced in checklist or by other files"
                })

        return orphaned

    def _find_broken_imports(self) -> List[Dict[str, Any]]:
        """Find broken import statements (Bobby Fischer - see the broken pattern)"""
        broken = []
        scripts_dir = self.project_root / "scripts" / "python"

        if not scripts_dir.exists():
            return broken

        for file_path in scripts_dir.glob("*.py"):
            if file_path.name.startswith("__"):
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                tree = ast.parse(content, filename=str(file_path))

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name.split('.')[0]
                            if not self._module_exists(module_name, scripts_dir):
                                broken.append({
                                    "file": file_path.name,
                                    "import": alias.name,
                                    "severity": "high",
                                    "note": "Import may be broken"
                                })
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module.split('.')[0]
                            if not self._module_exists(module_name, scripts_dir):
                                broken.append({
                                    "file": file_path.name,
                                    "import": node.module,
                                    "severity": "high",
                                    "note": "Import may be broken"
                                })
            except SyntaxError:
                # Skip files with syntax errors
                pass
            except Exception as e:
                logger.debug(f"Error checking imports in {file_path}: {e}")

        return broken

    def _module_exists(self, module_name: str, scripts_dir: Path) -> bool:
        """Check if module exists"""
        # Check if it's a standard library module
        try:
            __import__(module_name)
            return True
        except ImportError:
            pass

        # Check if it's a local file
        module_file = scripts_dir / f"{module_name}.py"
        if module_file.exists():
            return True

        # Check if it's in a subdirectory
        module_dir = scripts_dir / module_name
        if module_dir.exists() and (module_dir / "__init__.py").exists():
            return True

        return False

    def _find_pattern_anomalies(self) -> List[Dict[str, Any]]:
        """Find pattern anomalies (Bobby Fischer - see what others miss)"""
        anomalies = []

        # Check for inconsistent naming patterns
        scripts_dir = self.project_root / "scripts" / "python"
        if scripts_dir.exists():
            files = list(scripts_dir.glob("jarvis_*.py"))
            jarvis_files = [f.name for f in files]

            # Check if all jarvis files follow naming convention
            for file_name in jarvis_files:
                if not file_name.startswith("jarvis_") or not file_name.endswith(".py"):
                    anomalies.append({
                        "type": "naming_anomaly",
                        "file": file_name,
                        "severity": "low",
                        "note": "Doesn't follow jarvis_*.py pattern"
                    })

        # Check for missing logger usage
        if scripts_dir.exists():
            for file_path in scripts_dir.glob("jarvis_*.py"):
                try:
                    content = file_path.read_text(encoding='utf-8')
                    if "logger" not in content and "logging" not in content:
                        anomalies.append({
                            "type": "missing_logger",
                            "file": file_path.name,
                            "severity": "medium",
                            "note": "File doesn't use logging"
                        })
                except Exception:
                    pass

        return anomalies

    def _compile_gaps_list(self, gaps: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Compile all gaps into a single list"""
        all_gaps = []

        all_gaps.extend(gaps.get("missing_integrations", []))
        all_gaps.extend(gaps.get("missing_dependencies", []))
        all_gaps.extend(gaps.get("orphaned_files", []))
        all_gaps.extend(gaps.get("broken_links", []))
        all_gaps.extend(gaps.get("pattern_anomalies", []))

        # Sort by severity
        severity_order = {"high": 0, "medium": 1, "low": 2}
        all_gaps.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 2))

        return all_gaps

    def get_gaps_summary(self) -> Dict[str, Any]:
        """Get summary of gaps found"""
        if self.gaps_file.exists():
            try:
                with open(self.gaps_file, 'r', encoding='utf-8') as f:
                    gaps = json.load(f)
                    return {
                        "total_gaps": len(gaps.get("gaps_found", [])),
                        "by_severity": {
                            "high": len([g for g in gaps.get("gaps_found", []) if g.get("severity") == "high"]),
                            "medium": len([g for g in gaps.get("gaps_found", []) if g.get("severity") == "medium"]),
                            "low": len([g for g in gaps.get("gaps_found", []) if g.get("severity") == "low"])
                        },
                        "categories": {
                            "missing_integrations": len(gaps.get("missing_integrations", [])),
                            "missing_dependencies": len(gaps.get("missing_dependencies", [])),
                            "orphaned_files": len(gaps.get("orphaned_files", [])),
                            "broken_links": len(gaps.get("broken_links", [])),
                            "pattern_anomalies": len(gaps.get("pattern_anomalies", []))
                        },
                        "last_analysis": gaps.get("timestamp")
                    }
            except Exception:
                pass

        return {"status": "no_analysis_found"}


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Strategic Gap Analysis")
        parser.add_argument("--find-gaps", action="store_true", help="Find gaps (Bobby Fischer + Tinker Tailor)")
        parser.add_argument("--summary", action="store_true", help="Get gaps summary")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analyzer = StrategicGapAnalyzer(project_root)

        if args.find_gaps:
            gaps = analyzer.find_gaps()
            print("=" * 80)
            print("♟️ STRATEGIC GAP ANALYSIS")
            print("=" * 80)
            print(f"\nStrategy: Bobby Fischer pattern recognition")
            print(f"Mission: Tinker Tailor Soldier Spy - find the gaps")
            print(f"\nTotal gaps found: {len(gaps['gaps_found'])}")
            print(f"\nBy category:")
            print(f"  Missing integrations: {len(gaps['missing_integrations'])}")
            print(f"  Missing dependencies: {len(gaps['missing_dependencies'])}")
            print(f"  Orphaned files: {len(gaps['orphaned_files'])}")
            print(f"  Broken links: {len(gaps['broken_links'])}")
            print(f"  Pattern anomalies: {len(gaps['pattern_anomalies'])}")
            print("\nHigh priority gaps:")
            high_priority = [g for g in gaps['gaps_found'] if g.get('severity') == 'high']
            for gap in high_priority[:10]:  # Show first 10
                print(f"  - {gap.get('type', 'unknown')}: {gap.get('file', gap.get('dependency', 'unknown'))}")
            print("=" * 80)
            print(json.dumps(gaps, indent=2, default=str))

        elif args.summary:
            summary = analyzer.get_gaps_summary()
            print(json.dumps(summary, indent=2, default=str))

        else:
            # Default: find gaps
            gaps = analyzer.find_gaps()
            print("=" * 80)
            print("♟️ STRATEGIC GAP ANALYSIS")
            print("=" * 80)
            print(f"\nBobby Fischer: Pattern recognition")
            print(f"Tinker Tailor Soldier Spy: Find the gaps")
            print(f"\nGaps found: {len(gaps['gaps_found'])}")
            print(f"Mind the gap: {len([g for g in gaps['gaps_found'] if g.get('severity') == 'high'])} high priority")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()