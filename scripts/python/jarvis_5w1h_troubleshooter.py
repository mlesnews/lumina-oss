#!/usr/bin/env python3
"""
JARVIS 5W1H Troubleshooting System

Implements the 5W1H (Who, What, When, Where, Why, How) methodology for
systematic problem-solving and troubleshooting when JARVIS encounters
question marks (?) in user queries or system notifications.

Features:
- Automatic 5W1H analysis for troubleshooting queries
- Systematic problem decomposition
- Root cause analysis integration
- Solution recommendation engine
- Knowledge base integration for similar issues

When JARVIS detects a "?" in queries, it automatically applies:
1. WHO - Identify affected users/systems/components
2. WHAT - Define the exact problem or symptom
3. WHEN - Determine timing and frequency patterns
4. WHERE - Locate the problem in the system architecture
5. WHY - Analyze root causes and contributing factors
6. HOW - Provide step-by-step resolution procedures
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
logger = logging.getLogger("jarvis_5w1h_troubleshooter")



@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class W1H_Analysis:
    """5W1H analysis result"""
    query: str
    timestamp: datetime

    # 5W1H components
    who: Dict[str, Any] = field(default_factory=dict)
    what: Dict[str, Any] = field(default_factory=dict)
    when: Dict[str, Any] = field(default_factory=dict)
    where: Dict[str, Any] = field(default_factory=dict)
    why: Dict[str, Any] = field(default_factory=dict)
    how: Dict[str, Any] = field(default_factory=dict)

    # Analysis metadata
    confidence_score: float = 0.0
    complexity_level: str = "medium"
    similar_issues: List[Dict[str, Any]] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)


@dataclass
class TroubleshootingPattern:
    """Pattern for recognizing troubleshooting scenarios"""
    pattern_type: str
    keywords: List[str]
    question_indicators: List[str]
    context_clues: List[str]
    analysis_template: Dict[str, Any]


class JARVIS_5W1H_Troubleshooter:
    """JARVIS 5W1H systematic troubleshooting system"""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "troubleshooting"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Setup logging
        self.logger = logging.getLogger("JARVIS_5W1H")
        self.logger.setLevel(logging.INFO)

        # Load knowledge base and patterns
        self.knowledge_base = self._load_knowledge_base()
        self.troubleshooting_patterns = self._load_patterns()
        self.analysis_history = self._load_analysis_history()

    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load troubleshooting knowledge base"""
        kb_file = self.data_dir / "knowledge_base.json"

        if kb_file.exists():
            try:
                with open(kb_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        # Default knowledge base
        return {
            "common_issues": {
                "extension_not_available": {
                    "symptoms": ["formatter not available", "extension configured but missing"],
                    "root_causes": ["extension not installed", "extension disabled", "version incompatibility"],
                    "solutions": ["install extension", "enable extension", "check version compatibility"]
                },
                "file_reopen_required": {
                    "symptoms": ["setting not taking effect", "please reopen file"],
                    "root_causes": ["setting requires restart", "file buffer not updated", "language server restart needed"],
                    "solutions": ["reopen file", "reload window", "restart language server"]
                },
                "performance_degradation": {
                    "symptoms": ["slow response", "high cpu usage", "memory issues"],
                    "root_causes": ["extension conflicts", "large workspace", "resource leaks"],
                    "solutions": ["disable conflicting extensions", "optimize workspace", "restart services"]
                }
            },
            "system_components": {
                "extensions": ["formatter", "language_server", "debugger", "linter"],
                "services": ["task_daemon", "jarvis_core", "syphon_processor"],
                "files": [".vscode/settings.json", ".vscode/tasks.json", "requirements.txt"]
            }
        }

    def _load_patterns(self) -> List[TroubleshootingPattern]:
        """Load troubleshooting pattern recognition"""
        return [
            TroubleshootingPattern(
                pattern_type="extension_issue",
                keywords=["extension", "formatter", "linter", "language server"],
                question_indicators=["not available", "not working", "configured but", "cannot find"],
                context_clues=["vscode", "cursor", "editor", "formatting"],
                analysis_template={
                    "who": {"affected": "user", "component": "extension_system"},
                    "what": {"type": "extension_malfunction", "severity": "medium"},
                    "when": {"timing": "immediate", "frequency": "persistent"},
                    "where": {"location": "editor_extensions", "scope": "workspace"}
                }
            ),
            TroubleshootingPattern(
                pattern_type="configuration_issue",
                keywords=["setting", "config", "configuration", "preference"],
                question_indicators=["not taking effect", "not working", "please reopen", "restart required"],
                context_clues=["file", "workspace", "user settings", "global settings"],
                analysis_template={
                    "who": {"affected": "user", "component": "configuration_system"},
                    "what": {"type": "setting_application_failure", "severity": "low"},
                    "when": {"timing": "after_change", "frequency": "one_time"},
                    "where": {"location": "settings_files", "scope": "user_or_workspace"}
                }
            ),
            TroubleshootingPattern(
                pattern_type="performance_issue",
                keywords=["slow", "performance", "cpu", "memory", "lag"],
                question_indicators=["running slow", "high usage", "not responding", "frozen"],
                context_clues=["extension", "service", "editor", "workspace"],
                analysis_template={
                    "who": {"affected": "system_performance", "component": "resource_management"},
                    "what": {"type": "performance_degradation", "severity": "high"},
                    "when": {"timing": "ongoing", "frequency": "continuous"},
                    "where": {"location": "system_resources", "scope": "global"}
                }
            )
        ]

    def _load_analysis_history(self) -> List[Dict[str, Any]]:
        """Load analysis history"""
        history_file = self.data_dir / "analysis_history.json"

        if history_file.exists():
            try:
                with open(history_file, 'r') as f:
                    return json.load(f)
            except Exception:
                pass

        return []

    def detect_troubleshooting_query(self, query: str) -> bool:
        """Detect if a query contains troubleshooting indicators"""
        query_lower = query.lower()

        # Check for question marks
        has_question_mark = '?' in query

        # Check for troubleshooting keywords
        troubleshooting_keywords = [
            "problem", "issue", "error", "bug", "not working", "broken",
            "failed", "cannot", "unable", "doesn't", "won't", "can't",
            "help", "fix", "troubleshoot", "debug", "resolve"
        ]

        has_troubleshooting_keyword = any(keyword in query_lower for keyword in troubleshooting_keywords)

        # Check for error patterns
        error_patterns = [
            r"extension.*not.*available",
            r"formatter.*not.*available",
            r"please.*reopen.*file",
            r"setting.*not.*effect",
            r"cannot.*find",
            r"not.*working"
        ]

        has_error_pattern = any(re.search(pattern, query_lower) for pattern in error_patterns)

        return has_question_mark or has_troubleshooting_keyword or has_error_pattern

    def analyze_query_5w1h(self, query: str) -> W1H_Analysis:
        """Perform 5W1H analysis on a troubleshooting query"""

        analysis = W1H_Analysis(
            query=query,
            timestamp=datetime.now()
        )

        # Identify pattern
        matched_pattern = self._identify_pattern(query)

        if matched_pattern:
            # Apply pattern template
            analysis.who = matched_pattern.analysis_template.get("who", {})
            analysis.what = matched_pattern.analysis_template.get("what", {})
            analysis.when = matched_pattern.analysis_template.get("when", {})
            analysis.where = matched_pattern.analysis_template.get("where", {})
            analysis.why = self._analyze_root_causes(query, matched_pattern)
            analysis.how = self._generate_solutions(query, matched_pattern)
            analysis.confidence_score = 0.8
            analysis.complexity_level = matched_pattern.analysis_template.get("what", {}).get("severity", "medium")
        else:
            # Fallback analysis
            analysis = self._perform_fallback_analysis(query, analysis)

        # Find similar issues
        analysis.similar_issues = self._find_similar_issues(query)

        # Generate recommended actions
        analysis.recommended_actions = self._generate_recommended_actions(analysis)

        # Save to history
        self._save_analysis(analysis)

        return analysis

    def _identify_pattern(self, query: str) -> Optional[TroubleshootingPattern]:
        """Identify the most relevant troubleshooting pattern"""
        query_lower = query.lower()
        best_match = None
        best_score = 0

        for pattern in self.troubleshooting_patterns:
            score = 0

            # Check keywords
            keyword_matches = sum(1 for keyword in pattern.keywords if keyword in query_lower)
            score += keyword_matches * 2

            # Check question indicators
            question_matches = sum(1 for indicator in pattern.question_indicators if indicator in query_lower)
            score += question_matches * 3

            # Check context clues
            context_matches = sum(1 for clue in pattern.context_clues if clue in query_lower)
            score += context_matches * 1

            if score > best_score:
                best_score = score
                best_match = pattern

        return best_match if best_score > 0 else None

    def _analyze_root_causes(self, query: str, pattern: TroubleshootingPattern) -> Dict[str, Any]:
        """Analyze root causes based on pattern and query"""
        root_causes = {
            "primary": [],
            "contributing": [],
            "probability": {}
        }

        query_lower = query.lower()

        # Extension issues
        if pattern.pattern_type == "extension_issue":
            if "prettier" in query_lower or "formatter" in query_lower:
                root_causes["primary"].append("Extension not installed or disabled")
                root_causes["contributing"].extend([
                    "VSCode/Cursor restart required",
                    "Extension marketplace connectivity issue",
                    "Version incompatibility"
                ])
                root_causes["probability"] = {"extension_missing": 0.7, "version_conflict": 0.2, "marketplace_issue": 0.1}

        # Configuration issues
        elif pattern.pattern_type == "configuration_issue":
            if "reopen" in query_lower or "setting" in query_lower:
                root_causes["primary"].append("Configuration change requires file/window reload")
                root_causes["contributing"].extend([
                    "Language server restart needed",
                    "Editor buffer not refreshed",
                    "Workspace settings override"
                ])
                root_causes["probability"] = {"reload_required": 0.8, "server_restart": 0.15, "settings_override": 0.05}

        # Performance issues
        elif pattern.pattern_type == "performance_issue":
            root_causes["primary"].append("Resource contention or extension conflict")
            root_causes["contributing"].extend([
                "Large workspace size",
                "Multiple heavy extensions running",
                "Memory leaks in extensions",
                "CPU-intensive operations"
            ])
            root_causes["probability"] = {"extension_conflict": 0.4, "resource_contention": 0.3, "memory_leak": 0.3}

        return root_causes

    def _generate_solutions(self, query: str, pattern: TroubleshootingPattern) -> Dict[str, Any]:
        """Generate solution procedures"""
        solutions = {
            "immediate_actions": [],
            "step_by_step": [],
            "preventive_measures": [],
            "estimated_resolution_time": "15 minutes"
        }

        # Extension issues
        if pattern.pattern_type == "extension_issue":
            solutions["immediate_actions"] = [
                "Check if extension is installed and enabled",
                "Verify extension version compatibility",
                "Try reloading VSCode/Cursor window"
            ]
            solutions["step_by_step"] = [
                "1. Open Extensions panel (Ctrl+Shift+X)",
                "2. Search for the extension name",
                "3. Install or enable if found",
                "4. Reload window (Ctrl+Shift+P → 'Developer: Reload Window')",
                "5. Check if error persists"
            ]
            solutions["preventive_measures"] = [
                "Keep extensions updated regularly",
                "Review extension compatibility before major updates",
                "Monitor extension performance impact"
            ]

        # Configuration issues
        elif pattern.pattern_type == "configuration_issue":
            solutions["immediate_actions"] = [
                "Reopen the affected file",
                "Reload VSCode/Cursor window",
                "Check workspace vs user settings"
            ]
            solutions["step_by_step"] = [
                "1. Save all files",
                "2. Close and reopen the file (Ctrl+W then Ctrl+O)",
                "3. If issue persists, reload window (Ctrl+Shift+P → 'Developer: Reload Window')",
                "4. Check .vscode/settings.json for conflicting settings"
            ]
            solutions["preventive_measures"] = [
                "Use workspace settings for project-specific configurations",
                "Document setting changes that require restarts",
                "Test configuration changes in development environment first"
            ]

        # Performance issues
        elif pattern.pattern_type == "performance_issue":
            solutions["immediate_actions"] = [
                "Check system resource usage",
                "Disable potentially problematic extensions",
                "Close unused files and editors"
            ]
            solutions["step_by_step"] = [
                "1. Open Process Explorer (Ctrl+Shift+P → 'Developer: Show Running Extensions')",
                "2. Identify high-resource extensions",
                "3. Temporarily disable suspicious extensions",
                "4. Monitor performance improvement",
                "5. Re-enable extensions one by one to identify culprit"
            ]
            solutions["preventive_measures"] = [
                "Regularly review and optimize extension usage",
                "Monitor system resources during development",
                "Consider lightweight alternatives for heavy extensions"
            ]

        return solutions

    def _perform_fallback_analysis(self, query: str, analysis: W1H_Analysis) -> W1H_Analysis:
        """Perform basic analysis when no pattern matches"""
        analysis.who = {"affected": "user", "component": "unknown"}
        analysis.what = {"description": "Unspecified issue", "severity": "unknown"}
        analysis.when = {"timing": "unspecified", "frequency": "unknown"}
        analysis.where = {"location": "unknown", "scope": "unknown"}
        analysis.why = {"primary": ["Unknown"], "contributing": [], "probability": {}}
        analysis.how = {
            "immediate_actions": ["Investigate further"],
            "step_by_step": ["1. Gather more information", "2. Check logs", "3. Try basic troubleshooting"],
            "preventive_measures": ["Monitor system health"]
        }
        analysis.confidence_score = 0.3
        analysis.complexity_level = "high"

        return analysis

    def _find_similar_issues(self, query: str) -> List[Dict[str, Any]]:
        """Find similar issues from history"""
        similar = []

        # Simple keyword matching for now
        query_keywords = set(query.lower().split())

        for entry in self.analysis_history[-20:]:  # Last 20 analyses
            entry_keywords = set(entry["query"].lower().split())
            overlap = len(query_keywords & entry_keywords)

            if overlap >= 2:  # At least 2 matching keywords
                similar.append({
                    "query": entry["query"],
                    "timestamp": entry["timestamp"],
                    "resolution": entry.get("resolution", "Unknown"),
                    "similarity_score": overlap / len(query_keywords)
                })

        return similar[:3]  # Top 3 similar issues

    def _generate_recommended_actions(self, analysis: W1H_Analysis) -> List[str]:
        """Generate recommended actions based on analysis"""
        actions = []

        # Immediate actions from HOW analysis
        if analysis.how.get("immediate_actions"):
            actions.extend(analysis.how["immediate_actions"])

        # Pattern-specific actions
        if analysis.what.get("severity") == "high":
            actions.append("Escalate to senior developer if issue persists")
        elif analysis.what.get("severity") == "low":
            actions.append("Document issue for future reference")

        # Based on confidence score
        if analysis.confidence_score < 0.5:
            actions.insert(0, "Gather more diagnostic information")

        # Similar issues handling
        if analysis.similar_issues:
            actions.append("Reference similar resolved issues for additional solutions")

        return actions

    def _save_analysis(self, analysis: W1H_Analysis):
        """Save analysis to history"""
        try:
            history_entry = {
                "query": analysis.query,
                "timestamp": analysis.timestamp.isoformat(),
                "who": analysis.who,
                "what": analysis.what,
                "when": analysis.when,
                "where": analysis.where,
                "why": analysis.why,
                "how": analysis.how,
                "confidence_score": analysis.confidence_score,
                "complexity_level": analysis.complexity_level,
                "recommended_actions": analysis.recommended_actions
            }

            self.analysis_history.append(history_entry)

            # Keep only last 100 entries
            if len(self.analysis_history) > 100:
                self.analysis_history = self.analysis_history[-100:]

            # Save to file
            history_file = self.data_dir / "analysis_history.json"
            with open(history_file, 'w') as f:
                json.dump(self.analysis_history, f, indent=2)

        except Exception as e:
            self.logger.error(f"Failed to save analysis: {e}")

    def format_analysis_report(self, analysis: W1H_Analysis) -> str:
        """Format analysis as a comprehensive report"""
        report = f"""
# 🔍 JARVIS 5W1H Troubleshooting Analysis

**Query:** {analysis.query}
**Timestamp:** {analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}
**Confidence:** {analysis.confidence_score:.1%} | **Complexity:** {analysis.complexity_level}

## 1. WHO - Affected Parties & Components
- **Primary Affected:** {analysis.who.get('affected', 'Unknown')}
- **System Component:** {analysis.who.get('component', 'Unknown')}

## 2. WHAT - Problem Definition
- **Issue Type:** {analysis.what.get('type', 'Unknown')}
- **Severity Level:** {analysis.what.get('severity', 'Unknown')}
- **Description:** {analysis.what.get('description', 'Not specified')}

## 3. WHEN - Timing Analysis
- **Occurrence Timing:** {analysis.when.get('timing', 'Unknown')}
- **Frequency Pattern:** {analysis.when.get('frequency', 'Unknown')}

## 4. WHERE - Location Analysis
- **System Location:** {analysis.where.get('location', 'Unknown')}
- **Scope of Impact:** {analysis.where.get('scope', 'Unknown')}

## 5. WHY - Root Cause Analysis
"""

        # Root causes
        why_section = analysis.why
        if why_section.get('primary'):
            report += "**Primary Causes:**\n"
            for cause in why_section['primary']:
                report += f"- {cause}\n"

        if why_section.get('contributing'):
            report += "\n**Contributing Factors:**\n"
            for factor in why_section['contributing']:
                report += f"- {factor}\n"

        if why_section.get('probability'):
            report += "\n**Probability Assessment:**\n"
            for cause, prob in why_section['probability'].items():
                report += f"- {cause}: {prob:.1%}\n"

        report += f"""
## 6. HOW - Resolution Procedures

### Immediate Actions
"""
        for action in analysis.how.get('immediate_actions', []):
            report += f"- {action}\n"

        report += "\n### Step-by-Step Resolution\n"
        for step in analysis.how.get('step_by_step', []):
            report += f"1. {step}\n"

        report += "\n### Preventive Measures\n"
        for measure in analysis.how.get('preventive_measures', []):
            report += f"- {measure}\n"

        # Similar issues
        if analysis.similar_issues:
            report += "\n## 📚 Similar Resolved Issues\n"
            for issue in analysis.similar_issues:
                report += f"- **{issue['query']}** (Similarity: {issue['similarity_score']:.1%})\n"
                report += f"  Resolution: {issue.get('resolution', 'Unknown')}\n"

        # Recommended actions
        if analysis.recommended_actions:
            report += "\n## 🎯 Recommended Actions\n"
            for i, action in enumerate(analysis.recommended_actions, 1):
                report += f"{i}. {action}\n"

        report += f"\n## 📊 Analysis Metadata\n"
        report += f"- **Estimated Resolution Time:** {analysis.how.get('estimated_resolution_time', 'Unknown')}\n"
        report += f"- **Analysis Confidence:** {analysis.confidence_score:.1%}\n"
        report += f"- **Complexity Assessment:** {analysis.complexity_level}\n"

        return report

    async def troubleshoot_query(self, query: str) -> str:
        """Main troubleshooting interface - analyze query and return report"""
        if not self.detect_troubleshooting_query(query):
            return f"Query does not appear to be a troubleshooting request: {query}"

        self.logger.info(f"Analyzing troubleshooting query: {query}")
        analysis = self.analyze_query_5w1h(query)

        report = self.format_analysis_report(analysis)
        return report


def main():
    try:
        """Main CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS 5W1H Troubleshooter")
        parser.add_argument("query", help="Troubleshooting query to analyze")
        parser.add_argument("--format", choices=["report", "json"], default="report",
                           help="Output format")

        args = parser.parse_args()

        troubleshooter = JARVIS_5W1H_Troubleshooter()

        async def run_analysis():
            result = await troubleshooter.troubleshoot_query(args.query)

            if args.format == "json":
                # Extract analysis for JSON output
                analysis = troubleshooter.analyze_query_5w1h(args.query)
                print(json.dumps({
                    "query": analysis.query,
                    "who": analysis.who,
                    "what": analysis.what,
                    "when": analysis.when,
                    "where": analysis.where,
                    "why": analysis.why,
                    "how": analysis.how,
                    "confidence_score": analysis.confidence_score,
                    "recommended_actions": analysis.recommended_actions
                }, indent=2))
            else:
                print(result)

        asyncio.run(run_analysis())


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()