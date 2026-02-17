#!/usr/bin/env python3
"""
JARVIS Auto-Add Cursor Rules

Automatically detects patterns via @SYPHON and @WOPR, then adds rules to .cursorrules
using the "+ADD NEW RULE?" feature integration.

Tags: #pattern @syphon @wopr @jarvis @lumina
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutoAddCursorRules")

# Import integrations
try:
    from cursor_add_new_rule_integration import CursorAddNewRuleIntegration
    RULE_INTEGRATION_AVAILABLE = True
except ImportError:
    RULE_INTEGRATION_AVAILABLE = False
    logger.warning("⚠️  Cursor rule integration not available")

try:
    from syphon_cursor_agent_chat_sessions import SyphonCursorAgentChatSessions
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("⚠️  SYPHON not available")

try:
    from jarvis_proactive_ide_problem_monitor import JARVISProactiveIDEProblemMonitor
    JARVIS_MONITOR_AVAILABLE = True
except ImportError:
    JARVIS_MONITOR_AVAILABLE = False
    logger.warning("⚠️  JARVIS monitor not available")


class JARVISAutoAddCursorRules:
    """
    JARVIS Auto-Add Cursor Rules

    Automatically detects patterns via @SYPHON and @WOPR,
    then adds rules to .cursorrules using "+ADD NEW RULE?" integration.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS auto-add rules"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_auto_rules"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize integrations
        self.rule_integration = None
        self.syphon = None
        self.jarvis_monitor = None

        if RULE_INTEGRATION_AVAILABLE:
            try:
                self.rule_integration = CursorAddNewRuleIntegration(self.project_root)
                logger.info("✅ Cursor rule integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize rule integration: {e}")

        if SYPHON_AVAILABLE:
            try:
                self.syphon = SyphonCursorAgentChatSessions(self.project_root)
                logger.info("✅ SYPHON initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize SYPHON: {e}")

        if JARVIS_MONITOR_AVAILABLE:
            try:
                self.jarvis_monitor = JARVISProactiveIDEProblemMonitor(self.project_root)
                logger.info("✅ JARVIS monitor initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize JARVIS monitor: {e}")

        # Pattern detection rules
        self.pattern_detectors = {
            "repeated_errors": self._detect_repeated_errors,
            "code_smells": self._detect_code_smells,
            "missing_patterns": self._detect_missing_patterns,
            "best_practices": self._detect_best_practices,
            "anti_patterns": self._detect_anti_patterns
        }

        logger.info("✅ JARVIS Auto-Add Cursor Rules initialized")
        logger.info("   Pattern detection: Active")
        logger.info("   SYPHON integration: " + ("✅" if SYPHON_AVAILABLE else "❌"))
        logger.info("   WOPR integration: Ready")

    def _detect_repeated_errors(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect repeated errors and suggest rules"""
        rules = []

        # Check for repeated error patterns
        errors = analysis.get("errors", [])
        if len(errors) > 3:
            error_types = {}
            for error in errors:
                error_msg = error.get("message", "").lower()
                # Categorize errors
                if "import" in error_msg or "module" in error_msg:
                    error_types["import_errors"] = error_types.get("import_errors", 0) + 1
                elif "type" in error_msg or "attribute" in error_msg:
                    error_types["type_errors"] = error_types.get("type_errors", 0) + 1
                elif "connection" in error_msg or "timeout" in error_msg:
                    error_types["connection_errors"] = error_types.get("connection_errors", 0) + 1

            # Suggest rules for frequent errors
            if error_types.get("import_errors", 0) > 2:
                rules.append("Always verify imports exist before using them")
                rules.append("Use try/except for optional imports")

            if error_types.get("type_errors", 0) > 2:
                rules.append("Always use type hints to prevent type errors")
                rules.append("Validate input types before processing")

            if error_types.get("connection_errors", 0) > 2:
                rules.append("Always implement retry logic for network connections")
                rules.append("Use connection pooling for frequent connections")

        return rules

    def _detect_code_smells(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect code smells and suggest rules"""
        rules = []

        # Check for common code smells
        patterns = analysis.get("patterns", {})

        if patterns.get("has_todos", False):
            rules.append("Resolve TODOs before committing code")

        if patterns.get("has_workflow", False):
            rules.append("Document workflow patterns in code comments")

        if patterns.get("has_coordination", False):
            rules.append("Use coordination patterns for multi-agent systems")

        return rules

    def _detect_missing_patterns(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect missing patterns and suggest rules"""
        rules = []

        # Check for missing patterns
        tools_used = analysis.get("tools_used", [])
        if not tools_used:
            rules.append("Use appropriate tools for automation tasks")

        # Check for missing error handling
        errors = analysis.get("errors", [])
        completions = analysis.get("completions", [])
        if len(errors) > len(completions):
            rules.append("Always implement error handling for all operations")
            rules.append("Log errors with context for debugging")

        return rules

    def _detect_best_practices(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect best practices and suggest rules"""
        rules = []

        # Check for best practices
        metadata = analysis.get("metadata", {})

        # Check for proper logging
        if "logging" not in str(metadata).lower():
            rules.append("Use lumina_logger for all logging operations")

        # Check for proper error handling
        errors = analysis.get("errors", [])
        if errors:
            rules.append("Always handle errors gracefully with try/except blocks")
            rules.append("Provide meaningful error messages")

        return rules

    def _detect_anti_patterns(self, analysis: Dict[str, Any]) -> List[str]:
        """Detect anti-patterns and suggest rules"""
        rules = []

        # Check for anti-patterns
        patterns = analysis.get("patterns", {})

        if patterns.get("has_errors", False) and not patterns.get("has_completions", False):
            rules.append("Never leave error states unresolved")
            rules.append("Always implement error recovery mechanisms")

        return rules

    def extract_patterns_via_syphon(self) -> Dict[str, Any]:
        """
        Extract patterns via @SYPHON.

        Returns:
            Pattern analysis from SYPHON
        """
        logger.info("=" * 80)
        logger.info("🔍 @SYPHON: EXTRACTING PATTERNS")
        logger.info("=" * 80)
        logger.info("")

        if not self.syphon:
            logger.warning("⚠️  SYPHON not available")
            return {}

        try:
            # Analyze all sessions
            analysis = self.syphon.analyze_all_sessions()

            logger.info("✅ SYPHON analysis complete")
            logger.info(f"   Sessions analyzed: {analysis.get('total_sessions', 0)}")
            logger.info(f"   Patterns detected: {len(analysis.get('aggregated', {}).get('workflow_patterns', {}))}")

            return analysis

        except Exception as e:
            logger.error(f"❌ Error in SYPHON analysis: {e}")
            return {}

    def analyze_patterns_via_wopr(self, syphon_data: Dict[str, Any]) -> List[str]:
        """
        Analyze patterns via @WOPR and generate rule suggestions.

        Args:
            syphon_data: Data from SYPHON analysis

        Returns:
            List of suggested rules
        """
        logger.info("=" * 80)
        logger.info("🤖 @WOPR: ANALYZING PATTERNS")
        logger.info("=" * 80)
        logger.info("")

        suggested_rules = []

        # Analyze aggregated data
        aggregated = syphon_data.get("aggregated", {})

        # Analyze errors
        errors = aggregated.get("errors", [])
        if errors:
            error_analysis = {"errors": errors}
            suggested_rules.extend(self._detect_repeated_errors(error_analysis))

        # Analyze patterns
        workflow_patterns = aggregated.get("workflow_patterns", {})
        pattern_analysis = {"patterns": workflow_patterns}
        suggested_rules.extend(self._detect_code_smells(pattern_analysis))
        suggested_rules.extend(self._detect_missing_patterns(pattern_analysis))

        # Analyze completions
        completions = aggregated.get("completions", [])
        completion_analysis = {
            "completions": completions,
            "errors": errors
        }
        suggested_rules.extend(self._detect_best_practices(completion_analysis))
        suggested_rules.extend(self._detect_anti_patterns(completion_analysis))

        # WOPR-specific pattern analysis
        # Check for coordination patterns
        if workflow_patterns.get("has_coordination", False):
            suggested_rules.append("Use @JARVIS coordination patterns for multi-agent systems")

        # Check for SYPHON patterns
        if workflow_patterns.get("tool_usage", False):
            suggested_rules.append("Use @SYPHON for intelligence extraction")

        # Remove duplicates
        suggested_rules = list(dict.fromkeys(suggested_rules))

        logger.info(f"✅ WOPR analysis complete")
        logger.info(f"   Suggested rules: {len(suggested_rules)}")
        if suggested_rules:
            logger.info("   Top suggestions:")
            for i, rule in enumerate(suggested_rules[:5], 1):
                logger.info(f"      {i}. {rule}")

        return suggested_rules

    def auto_add_rules(self, rules: List[str], auto_confirm: bool = False) -> Dict[str, Any]:
        """
        Automatically add rules to .cursorrules.

        Args:
            rules: List of rules to add
            auto_confirm: Whether to auto-confirm additions

        Returns:
            Addition results
        """
        logger.info("=" * 80)
        logger.info("➕ AUTO-ADDING RULES")
        logger.info("=" * 80)
        logger.info("")

        if not self.rule_integration:
            logger.error("❌ Rule integration not available")
            return {"error": "Rule integration not available"}

        results = {
            "timestamp": datetime.now().isoformat(),
            "rules_proposed": len(rules),
            "rules_added": 0,
            "rules_skipped": 0,
            "added_rules": [],
            "skipped_rules": []
        }

        # Get existing rules to avoid duplicates
        existing_rules = self.rule_integration.parse_cursorrules()
        existing_rule_texts = {r["rule"].lower() for r in existing_rules.get("rules", [])}

        for rule in rules:
            # Check if rule already exists
            if rule.lower() in existing_rule_texts:
                logger.info(f"   ⏭️  Skipping (exists): {rule[:60]}...")
                results["rules_skipped"] += 1
                results["skipped_rules"].append(rule)
                continue

            # Add rule
            if auto_confirm:
                result = self.rule_integration.add_new_rule(
                    rule,
                    section="auto_detected",
                    source="jarvis_auto_syphon_wopr"
                )

                if result.get("added"):
                    logger.info(f"   ✅ Added: {rule[:60]}...")
                    results["rules_added"] += 1
                    results["added_rules"].append(rule)
                else:
                    logger.warning(f"   ⚠️  Failed: {rule[:60]}...")
                    results["rules_skipped"] += 1
                    results["skipped_rules"].append(rule)
            else:
                # Just propose, don't add
                logger.info(f"   💡 Proposed: {rule[:60]}...")
                results["added_rules"].append(rule)

        logger.info("")
        logger.info(f"✅ Auto-add complete: {results['rules_added']} added, {results['rules_skipped']} skipped")

        return results

    def run_full_auto_analysis(self, auto_add: bool = False) -> Dict[str, Any]:
        try:
            """
            Run full automatic analysis and rule addition.

            Args:
                auto_add: Whether to automatically add rules (default: False, just propose)

            Returns:
                Complete analysis results
            """
            logger.info("=" * 80)
            logger.info("🚀 JARVIS AUTO-ADD CURSOR RULES")
            logger.info("   Pattern Detection via @SYPHON & @WOPR")
            logger.info("=" * 80)
            logger.info("")

            # Step 1: Extract patterns via SYPHON
            syphon_data = self.extract_patterns_via_syphon()

            if not syphon_data:
                logger.warning("⚠️  No SYPHON data available")
                return {"error": "No SYPHON data"}

            # Step 2: Analyze patterns via WOPR
            suggested_rules = self.analyze_patterns_via_wopr(syphon_data)

            if not suggested_rules:
                logger.info("   ℹ️  No new rules suggested")
                return {
                    "syphon_data": syphon_data,
                    "suggested_rules": [],
                    "added": 0
                }

            # Step 3: Auto-add rules
            if auto_add:
                add_results = self.auto_add_rules(suggested_rules, auto_confirm=True)
            else:
                # Just propose
                add_results = {
                    "rules_proposed": len(suggested_rules),
                    "rules_added": 0,
                    "added_rules": suggested_rules
                }
                logger.info("")
                logger.info("💡 Proposed Rules (use --auto-add to add them):")
                for i, rule in enumerate(suggested_rules, 1):
                    logger.info(f"   {i}. {rule}")

            # Compile results
            results = {
                "timestamp": datetime.now().isoformat(),
                "syphon_analysis": syphon_data,
                "suggested_rules": suggested_rules,
                "add_results": add_results,
                "summary": {
                    "rules_proposed": len(suggested_rules),
                    "rules_added": add_results.get("rules_added", 0),
                    "rules_skipped": add_results.get("rules_skipped", 0)
                }
            }

            # Save results
            results_file = self.data_dir / f"auto_rules_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ AUTO-ANALYSIS COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Rules proposed: {results['summary']['rules_proposed']}")
            logger.info(f"   Rules added: {results['summary']['rules_added']}")
            logger.info(f"   Results saved: {results_file.name}")
            logger.info("")

            return results


        except Exception as e:
            self.logger.error(f"Error in run_full_auto_analysis: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Auto-Add Cursor Rules")
    parser.add_argument("--auto-add", action="store_true", help="Automatically add rules (default: just propose)")
    parser.add_argument("--syphon-only", action="store_true", help="Only run SYPHON analysis")
    parser.add_argument("--wopr-only", action="store_true", help="Only run WOPR analysis")

    args = parser.parse_args()

    jarvis_auto = JARVISAutoAddCursorRules()

    if args.syphon_only:
        jarvis_auto.extract_patterns_via_syphon()
    elif args.wopr_only:
        # Need SYPHON data first
        syphon_data = jarvis_auto.extract_patterns_via_syphon()
        jarvis_auto.analyze_patterns_via_wopr(syphon_data)
    else:
        # Full analysis
        jarvis_auto.run_full_auto_analysis(auto_add=args.auto_add)

    return 0


if __name__ == "__main__":


    sys.exit(main())