#!/usr/bin/env python3
"""
SYPHON Virtual Assistant Improvement System

Uses SYPHON intelligence extraction to fix and improve all virtual assistants.
Extracts patterns, issues, and improvements from VA code and applies fixes.

Tags: #SYPHON #VA #IMPROVEMENT #FIX @JARVIS @LUMINA @SYPHON
"""

import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SyphonVAImprovement")

# SYPHON integration
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None


@dataclass
class VAImprovement:
    """Virtual Assistant improvement"""
    va_name: str
    improvement_type: str  # fix, enhancement, optimization, integration
    description: str
    priority: str  # critical, high, medium, low
    code_changes: List[Dict[str, Any]] = field(default_factory=list)
    syphon_extracted: bool = False
    applied: bool = False


class SyphonVAImprovementSystem:
    """SYPHON-based VA improvement system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.va_files = self._find_va_files()
        self.improvements: List[VAImprovement] = []

        # Initialize SYPHON
        if SYPHON_AVAILABLE:
            syphon_config = SYPHONConfig(
                project_root=project_root,
                enable_regex_tools=True,
                enable_grep=True,
                enable_awk=True,
                enable_sed=True
            )
            self.syphon = SYPHONSystem(syphon_config)
            logger.info("✅ SYPHON system initialized for VA improvement")
        else:
            self.syphon = None
            logger.warning("⚠️  SYPHON not available, using basic analysis")

    def _find_va_files(self) -> List[Path]:
        """Find all virtual assistant files"""
        va_patterns = [
            "*_virtual_assistant.py",
            "*va*.py",
            "ironman*.py",
            "kenny*.py",
            "ace*.py"
        ]

        va_files = []
        scripts_dir = self.project_root / "scripts" / "python"

        for pattern in va_patterns:
            va_files.extend(scripts_dir.glob(pattern))

        # Remove duplicates and filter
        va_files = list(set(va_files))
        va_files = [f for f in va_files if f.is_file() and "virtual_assistant" in f.name.lower() or 
                   any(va_name in f.name.lower() for va_name in ["ironman", "kenny", "ace", "anakin"])]

        return va_files

    def extract_intelligence_from_va(self, va_file: Path) -> Dict[str, Any]:
        """Extract intelligence from VA file using SYPHON"""
        logger.info(f"Extracting intelligence from: {va_file.name}")

        intelligence = {
            "file": str(va_file),
            "name": va_file.stem,
            "issues": [],
            "improvements": [],
            "patterns": [],
            "missing_integrations": [],
            "syphon_enhancements": []
        }

        try:
            # Read file content
            with open(va_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Use SYPHON to extract intelligence
            if self.syphon:
                # Extract using SYPHON code extractor
                try:
                    from syphon.extractors import CodeExtractor
                    code_extractor = CodeExtractor()

                    # Extract patterns, issues, improvements
                    extraction = code_extractor.extract(content, source_type=DataSourceType.CODE)

                    if extraction and extraction.data:
                        intelligence["syphon_extracted"] = True
                        intelligence["extraction_result"] = extraction.data
                except Exception as e:
                    logger.debug(f"SYPHON extraction error: {e}")

            # Analyze code structure
            intelligence.update(self._analyze_va_code(content, va_file))

        except Exception as e:
            logger.error(f"Error extracting from {va_file}: {e}")
            intelligence["error"] = str(e)

        return intelligence

    def _analyze_va_code(self, content: str, va_file: Path) -> Dict[str, Any]:
        """Analyze VA code for issues and improvements"""
        analysis = {
            "has_syphon": False,
            "has_jarvis": False,
            "has_r5": False,
            "has_action_sequences": False,
            "has_helpdesk": False,
            "issues": [],
            "improvements": []
        }

        # Check for SYPHON integration
        if "SYPHON" in content or "syphon" in content.lower():
            analysis["has_syphon"] = True
        else:
            analysis["issues"].append({
                "type": "missing_integration",
                "severity": "high",
                "description": "Missing SYPHON integration",
                "fix": "Add SYPHON intelligence extraction"
            })

        # Check for JARVIS integration
        if "JARVIS" in content or "jarvis" in content.lower():
            analysis["has_jarvis"] = True
        else:
            analysis["issues"].append({
                "type": "missing_integration",
                "severity": "high",
                "description": "Missing JARVIS integration",
                "fix": "Add JARVIS workflow orchestration"
            })

        # Check for R5 integration
        if "R5" in content or "r5" in content.lower() or "r5_living_context" in content.lower():
            analysis["has_r5"] = True
        else:
            analysis["issues"].append({
                "type": "missing_integration",
                "severity": "medium",
                "description": "Missing R5 integration",
                "fix": "Add R5 context aggregation"
            })

        # Check for action sequences
        if "action_sequence" in content.lower() or "va_action_sequence" in content.lower():
            analysis["has_action_sequences"] = True
        else:
            analysis["issues"].append({
                "type": "missing_feature",
                "severity": "medium",
                "description": "Missing action sequence system",
                "fix": "Integrate VAActionSequenceSystem"
            })

        # Check for @helpdesk integration
        if "helpdesk" in content.lower() or "droid_actor" in content.lower():
            analysis["has_helpdesk"] = True
        else:
            analysis["issues"].append({
                "type": "missing_integration",
                "severity": "low",
                "description": "Missing @helpdesk integration",
                "fix": "Add @helpdesk droid coordination"
            })

        # Check for error handling
        if content.count("try:") < 3:
            analysis["issues"].append({
                "type": "code_quality",
                "severity": "medium",
                "description": "Insufficient error handling",
                "fix": "Add comprehensive try/except blocks"
            })

        # Check for logging
        if "logger" not in content.lower() or content.count("logger.") < 5:
            analysis["issues"].append({
                "type": "code_quality",
                "severity": "low",
                "description": "Insufficient logging",
                "fix": "Add comprehensive logging"
            })

        return analysis

    def generate_improvements(self) -> List[VAImprovement]:
        """Generate improvements for all VAs"""
        logger.info("Generating improvements for all virtual assistants...")

        for va_file in self.va_files:
            intelligence = self.extract_intelligence_from_va(va_file)

            # Create improvements based on intelligence
            va_name = intelligence["name"]

            # Missing SYPHON integration
            if not intelligence.get("has_syphon", False):
                self.improvements.append(VAImprovement(
                    va_name=va_name,
                    improvement_type="integration",
                    description="Add SYPHON intelligence extraction",
                    priority="high",
                    syphon_extracted=True
                ))

            # Missing JARVIS integration
            if not intelligence.get("has_jarvis", False):
                self.improvements.append(VAImprovement(
                    va_name=va_name,
                    improvement_type="integration",
                    description="Add JARVIS workflow orchestration",
                    priority="high",
                    syphon_extracted=True
                ))

            # Missing R5 integration
            if not intelligence.get("has_r5", False):
                self.improvements.append(VAImprovement(
                    va_name=va_name,
                    improvement_type="integration",
                    description="Add R5 context aggregation",
                    priority="medium",
                    syphon_extracted=True
                ))

            # Missing action sequences
            if not intelligence.get("has_action_sequences", False):
                self.improvements.append(VAImprovement(
                    va_name=va_name,
                    improvement_type="enhancement",
                    description="Integrate VAActionSequenceSystem",
                    priority="medium",
                    syphon_extracted=True
                ))

            # Add issues as improvements
            for issue in intelligence.get("issues", []):
                self.improvements.append(VAImprovement(
                    va_name=va_name,
                    improvement_type="fix",
                    description=issue.get("description", "Fix issue"),
                    priority=issue.get("severity", "medium"),
                    syphon_extracted=True
                ))

        return self.improvements

    def apply_improvements(self, va_file: Path, improvements: List[VAImprovement]) -> Dict[str, Any]:
        """Apply improvements to a VA file"""
        logger.info(f"Applying improvements to: {va_file.name}")

        results = {
            "file": str(va_file),
            "improvements_applied": 0,
            "improvements_failed": 0,
            "changes": []
        }

        try:
            with open(va_file, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content

            # Apply SYPHON integration if missing
            syphon_improvements = [imp for imp in improvements if "SYPHON" in imp.description and imp.va_name == va_file.stem]
            if syphon_improvements and "SYPHON_AVAILABLE" not in content:
                content = self._add_syphon_integration(content, va_file)
                results["improvements_applied"] += 1
                results["changes"].append("Added SYPHON integration")

            # Apply JARVIS integration if missing
            jarvis_improvements = [imp for imp in improvements if "JARVIS" in imp.description and imp.va_name == va_file.stem]
            if jarvis_improvements and "JARVIS_AVAILABLE" not in content:
                content = self._add_jarvis_integration(content, va_file)
                results["improvements_applied"] += 1
                results["changes"].append("Added JARVIS integration")

            # Apply R5 integration if missing
            r5_improvements = [imp for imp in improvements if "R5" in imp.description and imp.va_name == va_file.stem]
            if r5_improvements and "R5_AVAILABLE" not in content:
                content = self._add_r5_integration(content, va_file)
                results["improvements_applied"] += 1
                results["changes"].append("Added R5 integration")

            # Apply action sequences if missing
            action_seq_improvements = [imp for imp in improvements if "action_sequence" in imp.description.lower() and imp.va_name == va_file.stem]
            if action_seq_improvements and "VAActionSequenceSystem" not in content:
                content = self._add_action_sequences(content, va_file)
                results["improvements_applied"] += 1
                results["changes"].append("Added action sequence system")

            # Save if changes were made
            if content != original_content:
                backup_file = va_file.with_suffix(f".{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup")
                with open(backup_file, 'w', encoding='utf-8') as f:
                    f.write(original_content)

                with open(va_file, 'w', encoding='utf-8') as f:
                    f.write(content)

                logger.info(f"✅ Applied {results['improvements_applied']} improvements to {va_file.name}")
                logger.info(f"   Backup saved: {backup_file.name}")
            else:
                logger.info(f"ℹ️  No changes needed for {va_file.name}")

        except Exception as e:
            logger.error(f"Error applying improvements to {va_file}: {e}")
            results["improvements_failed"] += 1
            results["error"] = str(e)

        return results

    def _add_syphon_integration(self, content: str, va_file: Path) -> str:
        """Add SYPHON integration to VA"""
        syphon_code = '''
# SYPHON integration (@SYPHON) - Intelligence extraction and VA enhancement
try:
    from syphon import SYPHONSystem, SYPHONConfig, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None
    DataSourceType = None
'''

        # Find insertion point (after imports)
        import_end = content.rfind("import")
        if import_end > 0:
            next_line = content.find("\n", import_end) + 1
            content = content[:next_line] + syphon_code + content[next_line:]

        # Add SYPHON initialization in __init__
        if "def __init__" in content and "self.syphon" not in content:
            init_pos = content.find("def __init__")
            if init_pos > 0:
                # Find end of __init__ method (simplified - look for next def or class)
                init_end = content.find("\n    def ", init_pos)
                if init_end == -1:
                    init_end = content.find("\nclass ", init_pos)
                if init_end == -1:
                    init_end = len(content)

                syphon_init = '''
        # SYPHON integration - Intelligence extraction for VA enhancement
        self.syphon = None
        self.syphon_enhancement_interval = 60.0  # Extract intelligence every 60 seconds
        self.last_syphon_enhancement = time.time()
        self.syphon_enhanced_knowledge = []
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                self.logger.info("✅ SYPHON intelligence extraction integrated for VA enhancement")
            except Exception as e:
                self.logger.warning(f"⚠️  SYPHON integration failed: {e}")
'''
                content = content[:init_end] + syphon_init + content[init_end:]

        return content

    def _add_jarvis_integration(self, content: str, va_file: Path) -> str:
        """Add JARVIS integration to VA"""
        jarvis_code = '''
# JARVIS integration
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None
'''

        import_end = content.rfind("import")
        if import_end > 0:
            next_line = content.find("\n", import_end) + 1
            content = content[:next_line] + jarvis_code + content[next_line:]

        if "def __init__" in content and "self.jarvis" not in content:
            init_pos = content.find("def __init__")
            init_end = content.find("\n    def ", init_pos)
            if init_end == -1:
                init_end = content.find("\nclass ", init_pos)
            if init_end == -1:
                init_end = len(content)

            jarvis_init = '''
        # JARVIS integration - Workflow orchestration
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root)
                self.logger.info("✅ JARVIS workflow orchestration integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS integration failed: {e}")
'''
            content = content[:init_end] + jarvis_init + content[init_end:]

        return content

    def _add_r5_integration(self, content: str, va_file: Path) -> str:
        """Add R5 integration to VA"""
        r5_code = '''
# R5 Living Context Matrix integration
try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None
'''

        import_end = content.rfind("import")
        if import_end > 0:
            next_line = content.find("\n", import_end) + 1
            content = content[:next_line] + r5_code + content[next_line:]

        if "def __init__" in content and "self.r5" not in content:
            init_pos = content.find("def __init__")
            init_end = content.find("\n    def ", init_pos)
            if init_end == -1:
                init_end = content.find("\nclass ", init_pos)
            if init_end == -1:
                init_end = len(content)

            r5_init = '''
        # R5 Living Context Matrix - Context aggregation
        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5 context aggregation integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  R5 integration failed: {e}")
'''
            content = content[:init_end] + r5_init + content[init_end:]

        return content

    def _add_action_sequences(self, content: str, va_file: Path) -> str:
        """Add action sequence system integration"""
        action_seq_code = '''
# VA Action Sequence System integration
try:
    from va_action_sequence_system import VAActionSequenceSystem
    from integrate_va_action_sequences import integrate_action_sequences_im, integrate_action_sequences_ac
    ACTION_SEQUENCES_AVAILABLE = True
except ImportError:
    ACTION_SEQUENCES_AVAILABLE = False
    VAActionSequenceSystem = None
    integrate_action_sequences_im = None
    integrate_action_sequences_ac = None
'''

        import_end = content.rfind("import")
        if import_end > 0:
            next_line = content.find("\n", import_end) + 1
            content = content[:next_line] + action_seq_code + content[next_line:]

        if "def __init__" in content and "action_sequence_system" not in content:
            init_pos = content.find("def __init__")
            init_end = content.find("\n    def ", init_pos)
            if init_end == -1:
                init_end = content.find("\nclass ", init_pos)
            if init_end == -1:
                init_end = len(content)

            action_seq_init = '''
        # Integrate VA Action Sequence System
        if ACTION_SEQUENCES_AVAILABLE:
            try:
                if "ironman" in str(va_file).lower():
                    integrate_action_sequences_im(self)
                elif "ac" in str(va_file).lower() or "armory" in str(va_file).lower():
                    integrate_action_sequences_ac(self)
                self.logger.info("✅ VA Action Sequence System integrated")
            except Exception as e:
                self.logger.warning(f"⚠️  Action sequence integration failed: {e}")
'''
            content = content[:init_end] + action_seq_init + content[init_end:]

        return content

    def improve_all_vas(self) -> Dict[str, Any]:
        """Improve all virtual assistants"""
        logger.info("=" * 80)
        logger.info("🔧 SYPHON VA IMPROVEMENT SYSTEM")
        logger.info("=" * 80)
        logger.info("")

        # Generate improvements
        improvements = self.generate_improvements()

        logger.info(f"Found {len(self.va_files)} virtual assistants")
        logger.info(f"Generated {len(improvements)} improvements")
        logger.info("")

        # Apply improvements
        results = {
            "timestamp": datetime.now().isoformat(),
            "vas_processed": len(self.va_files),
            "improvements_generated": len(improvements),
            "vas_improved": 0,
            "improvements_applied": 0,
            "results": []
        }

        for va_file in self.va_files:
            va_improvements = [imp for imp in improvements if imp.va_name == va_file.stem]
            if va_improvements:
                result = self.apply_improvements(va_file, va_improvements)
                results["results"].append(result)
                if result["improvements_applied"] > 0:
                    results["vas_improved"] += 1
                    results["improvements_applied"] += result["improvements_applied"]

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 IMPROVEMENT SUMMARY")
        logger.info("=" * 80)
        logger.info(f"VAs Processed: {results['vas_processed']}")
        logger.info(f"VAs Improved: {results['vas_improved']}")
        logger.info(f"Improvements Applied: {results['improvements_applied']}")
        logger.info("")

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="SYPHON VA Improvement System")
        parser.add_argument("--analyze", action="store_true", help="Analyze VAs only")
        parser.add_argument("--improve", action="store_true", help="Apply improvements")
        parser.add_argument("--all", action="store_true", help="Analyze and improve all VAs")

        args = parser.parse_args()

        system = SyphonVAImprovementSystem(project_root)

        if args.analyze or args.all:
            improvements = system.generate_improvements()
            print("=" * 80)
            print("📊 VA ANALYSIS RESULTS")
            print("=" * 80)
            print(f"Found {len(system.va_files)} virtual assistants:")
            for va_file in system.va_files:
                print(f"  - {va_file.name}")
            print()
            print(f"Generated {len(improvements)} improvements:")
            for imp in improvements:
                print(f"  [{imp.priority.upper()}] {imp.va_name}: {imp.description}")
            print()

        if args.improve or args.all:
            results = system.improve_all_vas()

            # Save results
            results_file = project_root / "data" / "syphon_va_improvements.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"✅ Results saved: {results_file.name}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()