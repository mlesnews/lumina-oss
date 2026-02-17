#!/usr/bin/env python3
"""
LUMINA Standardization & Modularization Analyzer

Analyzes the LUMINA codebase for opportunities of standardization and modularization
of any/all applicable, actionable, viable code & codebase.

Tags: #STANDARDIZATION #MODULARIZATION #CODEBASE #ANALYSIS #REFACTORING @JARVIS @LUMINA @DOIT
"""

import ast
import json
import re
import sys
from collections import defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from lumina_core.paths import get_script_dir, setup_paths

script_dir = get_script_dir()
project_root_global = script_dir.parent.parent

setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name: str):
        """Fallback logger"""
        return logging.getLogger(name)

logger = get_logger("LuminaStandardizationAnalyzer")


@dataclass
class CodePattern:
    """Code pattern identified for standardization"""
    pattern_type: str
    description: str
    occurrences: List[Dict[str, Any]] = field(default_factory=list)
    standardization_opportunity: str = ""
    priority: str = "medium"  # low, medium, high, critical
    estimated_impact: str = ""
    recommended_module: Optional[str] = None


@dataclass
class Duplication:
    """Code duplication identified"""
    code_hash: str
    pattern: str
    files: List[str] = field(default_factory=list)
    lines: List[Tuple[str, int]] = field(default_factory=list)
    standardization_opportunity: str = ""
    recommended_module: Optional[str] = None


@dataclass
class ModularizationOpportunity:
    """Modularization opportunity"""
    name: str
    description: str
    files: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    classes: List[str] = field(default_factory=list)
    recommended_module: str = ""
    estimated_benefit: str = ""
    priority: str = "medium"


@dataclass
class StandardizationReport:
    """Comprehensive standardization report"""
    generated_at: str
    project_root: str
    patterns: List[CodePattern] = field(default_factory=list)
    duplications: List[Duplication] = field(default_factory=list)
    modularization_opportunities: List[ModularizationOpportunity] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)


class LuminaStandardizationAnalyzer:
    """
    LUMINA Standardization & Modularization Analyzer

    Analyzes codebase for:
    - Code patterns that can be standardized
    - Code duplications that can be modularized
    - Opportunities for creating reusable modules
    - Inconsistencies in implementation
    """

    def __init__(self, root_path: Optional[Path] = None):
        """Initialize analyzer"""
        if root_path is None:
            from lumina_core.paths import get_project_root
            self.project_root = Path(get_project_root())
        else:
            self.project_root = Path(root_path)

        self.scripts_dir = self.project_root / "scripts" / "python"
        self.data_dir = self.project_root / "data" / "standardization"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Patterns to identify
        self.patterns: List[CodePattern] = []
        self.duplications: List[Duplication] = []
        self.modularization_opportunities: List[ModularizationOpportunity] = []

        logger.info("✅ LUMINA Standardization Analyzer initialized")
        logger.info("   Project Root: %s", self.project_root)
        logger.info("   Scripts Directory: %s", self.scripts_dir)

    def analyze_codebase(self) -> StandardizationReport:
        """Analyze entire codebase for standardization opportunities"""
        logger.info("=" * 80)
        logger.info("LUMINA Codebase Standardization & Modularization Analysis")
        logger.info("=" * 80)
        logger.info("")

        # Get all Python files
        python_files = list(self.scripts_dir.rglob("*.py"))
        logger.info("📁 Analyzing %d Python files...", len(python_files))
        logger.info("")

        # Analyze patterns
        logger.info("🔍 Analyzing code patterns...")
        self._analyze_logger_patterns(python_files)
        self._analyze_project_root_patterns(python_files)
        self._analyze_path_management_patterns(python_files)
        self._analyze_config_loading_patterns(python_files)
        self._analyze_daemon_patterns(python_files)
        self._analyze_manager_patterns(python_files)

        # Analyze duplications
        logger.info("")
        logger.info("🔄 Analyzing code duplications...")
        self._analyze_code_duplications(python_files)

        # Analyze modularization opportunities
        logger.info("")
        logger.info("📦 Analyzing modularization opportunities...")
        self._analyze_modularization_opportunities(python_files)

        # Generate report
        report = self._generate_report()

        # Save report
        self._save_report(report)

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ Analysis Complete")
        logger.info("=" * 80)
        logger.info("   Patterns identified: %d", len(self.patterns))
        logger.info("   Duplications found: %d", len(self.duplications))
        logger.info("   Modularization opportunities: %d", len(self.modularization_opportunities))

        return report

    def _analyze_logger_patterns(self, files: List[Path]):
        """Analyze logger initialization patterns"""
        logger.info("   Analyzing logger patterns...")

        patterns = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Pattern 1: lumina_logger import
                if re.search(r'from\s+lumina_logger\s+import\s+get_logger', content):
                    patterns['lumina_logger'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "from lumina_core.logging import get_logger"
                    })

                # Pattern 2: lumina_adaptive_logger import
                if re.search(
                    r'from\s+lumina_adaptive_logger\s+import\s+get_adaptive_logger',
                    content
                ):
                    patterns['lumina_adaptive_logger'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "from lumina_core.logging import get_logger"
                    })

                # Pattern 3: logging.basicConfig fallback
                if re.search(r'logging\.basicConfig', content):
                    patterns['basic_config_fallback'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "logging.basicConfig fallback"
                    })

                # Pattern 4: Inconsistent error handling
                if re.search(r'except\s+ImportError.*get_logger\s*=\s*lambda', content, re.DOTALL):
                    patterns['lambda_fallback'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "lambda fallback for logger"
                    })

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        # Create pattern entries
        if patterns['lumina_logger']:
            self.patterns.append(CodePattern(
                pattern_type="logger_initialization",
                description="Logger initialization using lumina_logger",
                occurrences=patterns['lumina_logger'],
                standardization_opportunity=(
                    "Standardize on lumina_logger.get_logger() with consistent error handling"
                ),
                priority="high",
                estimated_impact="High - affects all scripts",
                recommended_module="lumina_core.logging"
            ))

        if patterns['lumina_adaptive_logger']:
            self.patterns.append(CodePattern(
                pattern_type="logger_initialization_adaptive",
                description="Logger initialization using lumina_adaptive_logger",
                occurrences=patterns['lumina_adaptive_logger'],
                standardization_opportunity=(
                    "Consider consolidating with lumina_logger or create unified interface"
                ),
                priority="medium",
                estimated_impact="Medium - affects subset of scripts",
                recommended_module="lumina_core.logging"
            ))

        if patterns['basic_config_fallback']:
            self.patterns.append(CodePattern(
                pattern_type="logger_fallback",
                description="Logger fallback using logging.basicConfig",
                occurrences=patterns['basic_config_fallback'],
                standardization_opportunity="Standardize fallback pattern in lumina_core.logging",
                priority="high",
                estimated_impact="High - affects error handling",
                recommended_module="lumina_core.logging"
            ))

    def _analyze_project_root_patterns(self, files: List[Path]):
        """Analyze project root detection patterns"""
        logger.info("   Analyzing project root patterns...")

        patterns = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Pattern 1: Path(__file__).parent.parent.parent
                if re.search(r'Path\(__file__\)\.parent\.parent\.parent', content):
                    patterns['parent_parent_parent'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "Path(__file__).parent.parent.parent"
                    })

                # Pattern 2: Path(__file__).parent.parent
                if re.search(r'Path\(__file__\)\.parent\.parent(?!\.)', content):
                    patterns['parent_parent'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "Path(__file__).parent.parent"
                    })

                # Pattern 3: script_dir pattern
                if re.search(r'script_dir\s*=\s*Path\(__file__\)\.parent', content):
                    patterns['script_dir'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": (
                            "from lumina_core.paths import get_script_dir; "
                            "script_dir = get_script_dir()"
                        )
                    })

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        # Create pattern entries
        if patterns['parent_parent_parent'] or patterns['parent_parent']:
            combined_occurrences = (
                patterns['parent_parent_parent'] +
                patterns['parent_parent']
            )
            self.patterns.append(CodePattern(
                pattern_type="project_root_detection",
                description="Inconsistent project root detection",
                occurrences=combined_occurrences,
                standardization_opportunity=(
                    "Create lumina_core.paths.get_project_root() utility"
                ),
                priority="high",
                estimated_impact="High - affects path resolution",
                recommended_module="lumina_core.paths"
            ))

    def _analyze_path_management_patterns(self, files: List[Path]):
        """Analyze path management patterns"""
        logger.info("   Analyzing path management patterns...")

        patterns = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Pattern: sys.path.insert
                if re.search(r'sys\.path\.insert\(0,\s*str\(', content):
                    patterns['sys_path_insert'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "sys.path.insert(0, ...)"
                    })

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        if patterns['sys_path_insert']:
            self.patterns.append(CodePattern(
                pattern_type="path_management",
                description="Inconsistent sys.path management",
                occurrences=patterns['sys_path_insert'],
                standardization_opportunity="Create lumina_core.paths.setup_paths() utility",
                priority="medium",
                estimated_impact="Medium - affects import resolution",
                recommended_module="lumina_core.paths"
            ))

    def _analyze_config_loading_patterns(self, files: List[Path]):
        """Analyze configuration loading patterns"""
        logger.info("   Analyzing config loading patterns...")

        patterns = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Pattern: JSON config loading
                if re.search(r'with\s+open.*\.json.*[\'"]r[\'"]', content):
                    patterns['json_config'].append({
                        "file": str(file_path.relative_to(self.project_root)),
                        "pattern": "JSON config loading"
                    })

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        if patterns['json_config']:
            self.patterns.append(CodePattern(
                pattern_type="config_loading",
                description="Inconsistent configuration loading",
                occurrences=patterns['json_config'],
                standardization_opportunity="Create lumina_core.config.ConfigLoader utility",
                priority="medium",
                estimated_impact="Medium - affects configuration management",
                recommended_module="lumina_core.config"
            ))

    def _analyze_daemon_patterns(self, files: List[Path]):
        """Analyze daemon patterns"""
        logger.info("   Analyzing daemon patterns...")

        daemon_files = []

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                if 'daemon' in file_path.name.lower() or 'BaseDaemon' in content:
                    daemon_files.append(str(file_path.relative_to(self.project_root)))

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        if daemon_files:
            self.modularization_opportunities.append(ModularizationOpportunity(
                name="Daemon Base Class",
                description="Standardize daemon implementation using BaseDaemon",
                files=daemon_files,
                recommended_module="lumina_core.daemon",
                estimated_benefit="Consistent daemon behavior, easier maintenance",
                priority="high"
            ))

    def _analyze_manager_patterns(self, files: List[Path]):
        """Analyze manager/service/helper class patterns"""
        logger.info("   Analyzing manager patterns...")

        managers = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')

                # Find class definitions
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        if any(x in class_name for x in ['Manager', 'Service', 'Helper']):
                            managers[class_name].append({
                                "file": str(file_path.relative_to(self.project_root)),
                                "class": class_name
                            })

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        if managers:
            # Collect all unique files
            all_files = set()
            for m_list in managers.values():
                for m in m_list:
                    if isinstance(m, dict) and "file" in m:
                        all_files.add(m["file"])

            self.modularization_opportunities.append(ModularizationOpportunity(
                name="Manager/Service/Helper Classes",
                description="Standardize manager/service/helper class patterns",
                files=list(all_files),
                classes=list(managers.keys()),
                recommended_module="lumina_core.managers",
                estimated_benefit="Consistent interfaces, shared base classes",
                priority="medium"
            ))

    def _analyze_code_duplications(self, files: List[Path]):
        """Analyze code duplications"""
        logger.info("   Analyzing code duplications...")

        # Simple hash-based duplication detection
        code_blocks = defaultdict(list)

        for file_path in files:
            try:
                content = file_path.read_text(encoding='utf-8')
                lines = content.split('\n')

                # Look for common patterns (5+ lines)
                for i in range(len(lines) - 4):
                    block = '\n'.join(lines[i:i+5])
                    # Simple hash
                    block_hash = hash(block.strip())
                    if block.strip() and len(block.strip()) > 50:  # Meaningful block
                        code_blocks[block_hash].append(
                            (str(file_path.relative_to(self.project_root)), i+1)
                        )

            except (OSError, UnicodeDecodeError) as e:
                logger.debug("   Error analyzing %s: %s", file_path, e)

        # Find duplications (appears in 2+ files)
        for block_hash, locations in code_blocks.items():
            if len(locations) >= 2:
                files_involved = list({loc[0] for loc in locations})
                if len(files_involved) >= 2:
                    self.duplications.append(Duplication(
                        code_hash=str(block_hash),
                        pattern="Code block duplication",
                        files=files_involved,
                        lines=locations,
                        standardization_opportunity="Extract to shared utility module",
                        recommended_module="lumina_core.utils"
                    ))

    def _analyze_modularization_opportunities(self, files: List[Path]):
        """Analyze modularization opportunities"""
        logger.info("   Analyzing modularization opportunities...")

        # Group related files
        file_groups = defaultdict(list)

        for file_path in files:
            name = file_path.stem.lower()

            # Group by prefix/suffix
            if name.startswith('ask_ticket'):
                file_groups['ask_ticket'].append(str(file_path.relative_to(self.project_root)))
            elif name.startswith('apicli'):
                file_groups['apicli'].append(str(file_path.relative_to(self.project_root)))
            elif 'daemon' in name:
                file_groups['daemon'].append(str(file_path.relative_to(self.project_root)))
            elif 'cron' in name:
                file_groups['cron'].append(str(file_path.relative_to(self.project_root)))

        # Create opportunities
        for group_name, group_files in file_groups.items():
            if len(group_files) >= 2:
                self.modularization_opportunities.append(ModularizationOpportunity(
                    name=f"{group_name.title()} Module",
                    description=f"Modularize {group_name} related functionality",
                    files=group_files,
                    recommended_module=f"lumina_{group_name}",
                    estimated_benefit="Better organization, easier maintenance",
                    priority="medium"
                ))

    def _generate_report(self) -> StandardizationReport:
        """Generate comprehensive report"""
        report = StandardizationReport(
            generated_at=datetime.now().isoformat(),
            project_root=str(self.project_root),
            patterns=self.patterns,
            duplications=self.duplications,
            modularization_opportunities=self.modularization_opportunities
        )

        # Generate recommendations
        recommendations = []

        # High priority patterns
        high_priority = [p for p in self.patterns if p.priority == "high"]
        if high_priority:
            recommendations.append(
                f"Address {len(high_priority)} high-priority standardization patterns"
            )

        # Critical duplications
        if len(self.duplications) > 10:
            recommendations.append(
                f"Refactor {len(self.duplications)} code duplications into shared modules"
            )

        # Modularization opportunities
        if self.modularization_opportunities:
            recommendations.append(
                f"Implement {len(self.modularization_opportunities)} modularization opportunities"
            )

        # Specific recommendations
        if any(p.recommended_module == "lumina_core.logging" for p in self.patterns):
            recommendations.append(
                "Create lumina_core.logging module for standardized logger initialization"
            )

        if any(p.recommended_module == "lumina_core.paths" for p in self.patterns):
            recommendations.append(
                "Create lumina_core.paths module for standardized path management"
            )

        report.recommendations = recommendations

        # Summary
        report.summary = {
            "total_patterns": len(self.patterns),
            "high_priority_patterns": len([p for p in self.patterns if p.priority == "high"]),
            "total_duplications": len(self.duplications),
            "total_modularization_opportunities": len(self.modularization_opportunities),
            "recommended_modules": list(set(
                [p.recommended_module for p in self.patterns if p.recommended_module] +
                [m.recommended_module for m in self.modularization_opportunities
                 if m.recommended_module]
            ))
        }

        return report

    def _save_report(self, report: StandardizationReport):
        try:
            """Save report to file"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_file = self.data_dir / f"standardization_report_{timestamp}.json"

            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(report), f, indent=2, ensure_ascii=False)

            logger.info("   Report saved: %s", report_file)


        except Exception as e:
            self.logger.error(f"Error in _save_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="LUMINA Standardization & Modularization Analyzer"
    )
    parser.add_argument("--analyze", action="store_true", help="Analyze codebase")
    parser.add_argument("--output", type=str, help="Output directory for report")

    args = parser.parse_args()

    analyzer = LuminaStandardizationAnalyzer()

    if args.analyze:
        report = analyzer.analyze_codebase()

        print("\n📊 LUMINA Standardization & Modularization Report")
        print(f"   Generated: {report.generated_at}")
        print(f"\n   Patterns: {report.summary['total_patterns']} "
              f"({report.summary['high_priority_patterns']} high priority)")
        print(f"   Duplications: {report.summary['total_duplications']}")
        print(f"   Modularization Opportunities: "
              f"{report.summary['total_modularization_opportunities']}")
        print("\n   Recommended Modules:")
        for module in report.summary['recommended_modules']:
            print(f"     - {module}")
        print("\n   Recommendations:")
        for rec in report.recommendations:
            print(f"     - {rec}")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()