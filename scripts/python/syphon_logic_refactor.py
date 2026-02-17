#!/usr/bin/env python3
"""
@SYPHON Logic Refactor System
<COMPANY_NAME> LLC

@SYPHON refactors the world by:
- Extracting reusable logic patterns
- Applying decision trees everywhere beneficial
- Refactoring code to use shared logic
- Creating reusable components

@JARVIS @MARVIN @TONY @MACE @GANDALF @SYPHON
"""

import json
import ast
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SyphonLogicRefactor")
except:
    logger = None


@dataclass
class LogicPattern:
    """Reusable logic pattern"""
    pattern_id: str
    name: str
    description: str
    code: str
    usage_contexts: List[str] = field(default_factory=list)
    decision_tree_applicable: bool = False
    refactored_count: int = 0


@dataclass
class RefactorResult:
    """Refactoring result"""
    file_path: Path
    patterns_applied: List[str]
    lines_changed: int
    decision_trees_added: int
    success: bool
    errors: List[str] = field(default_factory=list)


class SyphonLogicRefactor:
    """
    @SYPHON Logic Refactor System

    Extracts and reuses logic patterns across the entire codebase.
    Applies decision trees everywhere beneficial.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize refactor system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger or self._get_logger()

        # Patterns registry
        self.patterns: Dict[str, LogicPattern] = {}
        self._load_patterns()

        # Decision tree integration
        try:
            from universal_decision_tree import get_decision_tree, DecisionContext
            self.decision_tree = get_decision_tree()
            self.has_decision_tree = True
        except:
            self.decision_tree = None
            self.has_decision_tree = False
            self.logger.warning("Decision tree system not available")

        self.logger.info("✅ @SYPHON Logic Refactor System initialized")

    def refactor_codebase(self,
                             target_dirs: Optional[List[Path]] = None,
                             apply_decision_trees: bool = True) -> List[RefactorResult]:
        try:
            """
            Refactor codebase to use reusable logic patterns

            Args:
                target_dirs: Directories to refactor (default: scripts/python)
                apply_decision_trees: Apply decision trees where beneficial

            Returns:
                List of refactoring results
            """
            if target_dirs is None:
                target_dirs = [self.project_root / "scripts" / "python"]

            results = []

            for target_dir in target_dirs:
                if not target_dir.exists():
                    continue

                # Find Python files
                python_files = list(target_dir.rglob("*.py"))

                self.logger.info(f"🔍 Found {len(python_files)} Python files in {target_dir}")

                for file_path in python_files:
                    # Skip this file and test files
                    if "test" in file_path.name.lower() or "refactor" in file_path.name.lower():
                        continue

                    result = self._refactor_file(file_path, apply_decision_trees)
                    if result.success or result.patterns_applied:
                        results.append(result)

            # Save refactoring report
            self._save_refactor_report(results)

            return results

        except Exception as e:
            self.logger.error(f"Error in refactor_codebase: {e}", exc_info=True)
            raise
    def _refactor_file(self, 
                      file_path: Path,
                      apply_decision_trees: bool) -> RefactorResult:
        """Refactor a single file"""
        try:
            content = file_path.read_text()
            original_content = content

            patterns_applied = []
            decision_trees_added = 0

            # Check for decision tree opportunities
            if apply_decision_trees and self.has_decision_tree:
                # Look for if/else chains that could use decision trees
                if self._has_decision_opportunity(content):
                    content = self._add_decision_tree(content)
                    decision_trees_added += 1
                    patterns_applied.append("decision_tree")

            # Apply other patterns
            for pattern_id, pattern in self.patterns.items():
                if pattern.code in content and pattern_id not in patterns_applied:
                    # Pattern already exists or can be applied
                    patterns_applied.append(pattern_id)

            # Calculate changes
            lines_changed = len(content.split('\n')) - len(original_content.split('\n'))

            # Only write if changes were made
            if content != original_content:
                file_path.write_text(content)
                self.logger.info(f"✅ Refactored: {file_path.name} ({len(patterns_applied)} patterns)")

            return RefactorResult(
                file_path=file_path,
                patterns_applied=patterns_applied,
                lines_changed=lines_changed,
                decision_trees_added=decision_trees_added,
                success=True
            )

        except Exception as e:
            return RefactorResult(
                file_path=file_path,
                patterns_applied=[],
                lines_changed=0,
                decision_trees_added=0,
                success=False,
                errors=[str(e)]
            )

    def _has_decision_opportunity(self, content: str) -> bool:
        """Check if code has decision tree opportunities"""
        # Look for if/else chains with multiple conditions
        if_count = content.count("if ")
        elif_count = content.count("elif ")
        else_count = content.count("else:")

        # Multiple conditions suggest decision tree opportunity
        if if_count + elif_count >= 3:
            return True

        # Look for AI provider selection logic
        ai_providers = ["openai", "anthropic", "grok", "local", "ollama"]
        provider_mentions = sum(1 for provider in ai_providers if provider in content.lower())

        if provider_mentions >= 2:
            return True

        return False

    def _add_decision_tree(self, content: str) -> str:
        """Add decision tree to code"""
        # Add import
        if "from universal_decision_tree import" not in content:
            # Find last import
            lines = content.split('\n')
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    last_import_idx = i

            # Insert after last import
            lines.insert(last_import_idx + 1, "from universal_decision_tree import decide, DecisionContext, DecisionOutcome")
            content = '\n'.join(lines)

        # Add decision tree usage comment
        if "# Decision tree" not in content.lower():
            # Add comment near top of file
            lines = content.split('\n')
            # Find first function or class
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("def ") or line.strip().startswith("class "):
                    insert_idx = i
                    break

            comment = [
                "",
                "# @SYPHON: Decision tree logic applied",
                "# Use: result = decide('ai_fallback', DecisionContext(...))",
                ""
            ]

            lines[insert_idx:insert_idx] = comment
            content = '\n'.join(lines)

        return content

    def extract_pattern(self, code: str, pattern_name: str) -> Optional[LogicPattern]:
        """Extract a reusable pattern from code"""
        pattern_id = f"pattern_{len(self.patterns) + 1}"

        pattern = LogicPattern(
            pattern_id=pattern_id,
            name=pattern_name,
            description=f"Extracted pattern: {pattern_name}",
            code=code,
            decision_tree_applicable=self._has_decision_opportunity(code)
        )

        self.patterns[pattern_id] = pattern
        self._save_patterns()

        self.logger.info(f"✅ Extracted pattern: {pattern_name}")

        return pattern

    def _load_patterns(self):
        """Load patterns from registry"""
        patterns_file = self.project_root / "data" / "syphon" / "logic_patterns.json"

        if patterns_file.exists():
            try:
                with open(patterns_file, 'r') as f:
                    data = json.load(f)
                    for pattern_data in data.get("patterns", []):
                        pattern = LogicPattern(**pattern_data)
                        self.patterns[pattern.pattern_id] = pattern

                self.logger.info(f"✅ Loaded {len(self.patterns)} logic patterns")
            except Exception as e:
                self.logger.error(f"Failed to load patterns: {e}")

    def _save_patterns(self):
        try:
            """Save patterns to registry"""
            patterns_file = self.project_root / "data" / "syphon" / "logic_patterns.json"
            patterns_file.parent.mkdir(parents=True, exist_ok=True)

            data = {
                "version": "1.0.0",
                "patterns": [
                    {
                        "pattern_id": p.pattern_id,
                        "name": p.name,
                        "description": p.description,
                        "code": p.code,
                        "usage_contexts": p.usage_contexts,
                        "decision_tree_applicable": p.decision_tree_applicable,
                        "refactored_count": p.refactored_count
                    }
                    for p in self.patterns.values()
                ]
            }

            with open(patterns_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_patterns: {e}", exc_info=True)
            raise
    def _save_refactor_report(self, results: List[RefactorResult]):
        try:
            """Save refactoring report"""
            report_file = self.project_root / "data" / "syphon" / "refactor_report.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)

            report = {
                "timestamp": datetime.now().isoformat(),
                "total_files": len(results),
                "successful": sum(1 for r in results if r.success),
                "patterns_applied": sum(len(r.patterns_applied) for r in results),
                "decision_trees_added": sum(r.decision_trees_added for r in results),
                "results": [
                    {
                        "file": str(r.file_path),
                        "patterns": r.patterns_applied,
                        "decision_trees": r.decision_trees_added,
                        "success": r.success,
                        "errors": r.errors
                    }
                    for r in results
                ]
            }

            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2)

            self.logger.info(f"💾 Refactor report saved: {report_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_refactor_report: {e}", exc_info=True)
            raise
    def _get_logger(self):
        """Get logger"""
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger("SyphonLogicRefactor")


if __name__ == "__main__":
    from datetime import datetime

    refactor = SyphonLogicRefactor()

    print("\n🔧 @SYPHON Logic Refactor System")
    print("=" * 60)

    # Refactor codebase
    results = refactor.refactor_codebase(apply_decision_trees=True)

    print(f"\n✅ Refactoring complete!")
    print(f"   Files processed: {len(results)}")
    print(f"   Patterns applied: {sum(len(r.patterns_applied) for r in results)}")
    print(f"   Decision trees added: {sum(r.decision_trees_added for r in results)}")
