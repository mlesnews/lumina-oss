#!/usr/bin/env python3
"""
AI Guidance Process Analyzer

Analyzes AI requests and responses to identify process improvements.
Based on ML/AI Scientist framework for effective AI communication.

Tags: #AI_GUIDANCE #PROCESS_ANALYSIS #ML_SCIENCE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

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

logger = get_logger("AIGuidanceAnalyzer")


class RequestQuality(Enum):
    """Request quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"


class AIGuidanceAnalyzer:
    """
    Analyzes AI requests and responses to identify process improvements.
    """

    def __init__(self):
        """Initialize analyzer"""
        self.analysis_results = []
        logger.info("=" * 80)
        logger.info("🔍 AI GUIDANCE PROCESS ANALYZER")
        logger.info("=" * 80)

    def analyze_request(self, request_text: str, 
                       tool_calls: List[Dict[str, Any]],
                       response_time: float,
                       context_size: int) -> Dict[str, Any]:
        """
        Analyze an AI request for quality and efficiency

        Returns analysis with recommendations
        """
        analysis = {
            "request_text": request_text,
            "timestamp": datetime.now().isoformat(),
            "metrics": {
                "tool_calls": len(tool_calls),
                "response_time": response_time,
                "context_size": context_size,
                "tool_types": self._count_tool_types(tool_calls)
            },
            "quality_indicators": {
                "has_role": self._has_role_definition(request_text),
                "has_structured_context": self._has_structured_context(request_text),
                "has_clear_task": self._has_clear_task(request_text),
                "has_success_criteria": self._has_success_criteria(request_text),
                "has_output_format": self._has_output_format(request_text),
                "uses_appropriate_tools": self._uses_appropriate_tools(tool_calls),
                "efficient_context_usage": self._efficient_context_usage(context_size, tool_calls)
            },
            "quality_score": 0,
            "quality_level": None,
            "recommendations": []
        }

        # Calculate quality score
        quality_score = self._calculate_quality_score(analysis["quality_indicators"])
        analysis["quality_score"] = quality_score
        analysis["quality_level"] = self._get_quality_level(quality_score)

        # Generate recommendations
        analysis["recommendations"] = self._generate_recommendations(analysis)

        self.analysis_results.append(analysis)
        return analysis

    def _has_role_definition(self, text: str) -> bool:
        """Check if request has role definition"""
        role_keywords = ["role", "as a", "acting as", "persona", "expertise"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in role_keywords)

    def _has_structured_context(self, text: str) -> bool:
        """Check if request has structured context"""
        context_keywords = ["primary", "secondary", "reference", "context", "priority"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in context_keywords)

    def _has_clear_task(self, text: str) -> bool:
        """Check if request has clear task definition"""
        task_keywords = ["task", "action", "goal", "objective", "find", "create", "update"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in task_keywords)

    def _has_success_criteria(self, text: str) -> bool:
        """Check if request has success criteria"""
        criteria_keywords = ["success", "criteria", "validate", "check", "verify", "done"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in criteria_keywords)

    def _has_output_format(self, text: str) -> bool:
        """Check if request specifies output format"""
        format_keywords = ["format", "output", "markdown", "json", "table", "list"]
        text_lower = text.lower()
        return any(keyword in text_lower for keyword in format_keywords)

    def _uses_appropriate_tools(self, tool_calls: List[Dict[str, Any]]) -> bool:
        """Check if appropriate tools are used"""
        # Check for semantic search when exact matching would work
        has_semantic_search = any(
            call.get("name", "").startswith("codebase_search") 
            for call in tool_calls
        )
        has_exact_search = any(
            call.get("name", "").startswith("grep") 
            for call in tool_calls
        )

        # If we have exact search for known strings, that's good
        # If we only have semantic search for exact strings, that's less efficient
        return has_exact_search or not has_semantic_search

    def _efficient_context_usage(self, context_size: int, tool_calls: List[Dict[str, Any]]) -> bool:
        """Check if context usage is efficient"""
        # Target: < 10KB primary context, < 5 tool calls for simple tasks
        return context_size < 10000 and len(tool_calls) < 5

    def _count_tool_types(self, tool_calls: List[Dict[str, Any]]) -> Dict[str, int]:
        """Count tool types used"""
        tool_types = {}
        for call in tool_calls:
            tool_name = call.get("name", "unknown")
            tool_type = tool_name.split("_")[0] if "_" in tool_name else tool_name
            tool_types[tool_type] = tool_types.get(tool_type, 0) + 1
        return tool_types

    def _calculate_quality_score(self, indicators: Dict[str, bool]) -> float:
        """Calculate quality score (0-100)"""
        weights = {
            "has_role": 10,
            "has_structured_context": 20,
            "has_clear_task": 25,
            "has_success_criteria": 15,
            "has_output_format": 10,
            "uses_appropriate_tools": 10,
            "efficient_context_usage": 10
        }

        score = 0
        for indicator, weight in weights.items():
            if indicators.get(indicator, False):
                score += weight

        return score

    def _get_quality_level(self, score: float) -> RequestQuality:
        """Get quality level from score"""
        if score >= 90:
            return RequestQuality.EXCELLENT
        elif score >= 70:
            return RequestQuality.GOOD
        elif score >= 50:
            return RequestQuality.FAIR
        else:
            return RequestQuality.POOR

    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []
        indicators = analysis["quality_indicators"]
        metrics = analysis["metrics"]

        if not indicators["has_role"]:
            recommendations.append("Define AI role explicitly (e.g., 'ROLE: Software Engineer')")

        if not indicators["has_structured_context"]:
            recommendations.append("Structure context by priority (PRIMARY, SECONDARY, REFERENCE)")

        if not indicators["has_clear_task"]:
            recommendations.append("Define clear task with action, goal, and constraints")

        if not indicators["has_success_criteria"]:
            recommendations.append("Specify success criteria (measurable checkpoints)")

        if not indicators["has_output_format"]:
            recommendations.append("Specify output format (markdown, JSON, table, etc.)")

        if not indicators["uses_appropriate_tools"]:
            recommendations.append("Use exact matching (grep) for known strings instead of semantic search")

        if not indicators["efficient_context_usage"]:
            recommendations.append(f"Reduce context size (current: {metrics['context_size']} bytes, target: < 10KB)")
            recommendations.append(f"Reduce tool calls (current: {metrics['tool_calls']}, target: < 5 for simple tasks)")

        if metrics["tool_calls"] > 10:
            recommendations.append("Decompose complex task into explicit steps with validation")

        return recommendations

    def print_analysis(self, analysis: Dict[str, Any]):
        """Print analysis results"""
        print("=" * 80)
        print("🔍 AI REQUEST ANALYSIS")
        print("=" * 80)
        print()

        print(f"Quality Level: {analysis['quality_level'].value.upper()}")
        print(f"Quality Score: {analysis['quality_score']}/100")
        print()

        print("Metrics:")
        metrics = analysis["metrics"]
        print(f"  Tool Calls: {metrics['tool_calls']}")
        print(f"  Response Time: {metrics['response_time']:.2f}s")
        print(f"  Context Size: {metrics['context_size']:,} bytes")
        print(f"  Tool Types: {metrics['tool_types']}")
        print()

        print("Quality Indicators:")
        indicators = analysis["quality_indicators"]
        for indicator, value in indicators.items():
            status = "✅" if value else "❌"
            print(f"  {status} {indicator.replace('_', ' ').title()}")
        print()

        if analysis["recommendations"]:
            print("Recommendations:")
            for i, rec in enumerate(analysis["recommendations"], 1):
                print(f"  {i}. {rec}")
        else:
            print("✅ No recommendations - request is well-structured!")
        print()

        print("=" * 80)

    def generate_report(self) -> str:
        """Generate analysis report"""
        if not self.analysis_results:
            return "No analysis results available"

        report = []
        report.append("# AI Guidance Process Analysis Report")
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        report.append(f"Total Requests Analyzed: {len(self.analysis_results)}")
        report.append("")

        # Quality distribution
        quality_dist = {}
        for result in self.analysis_results:
            level = result["quality_level"].value
            quality_dist[level] = quality_dist.get(level, 0) + 1

        report.append("## Quality Distribution")
        for level, count in quality_dist.items():
            report.append(f"- {level.title()}: {count}")
        report.append("")

        # Average metrics
        avg_tool_calls = sum(r["metrics"]["tool_calls"] for r in self.analysis_results) / len(self.analysis_results)
        avg_context_size = sum(r["metrics"]["context_size"] for r in self.analysis_results) / len(self.analysis_results)

        report.append("## Average Metrics")
        report.append(f"- Tool Calls: {avg_tool_calls:.1f}")
        report.append(f"- Context Size: {avg_context_size:,.0f} bytes")
        report.append("")

        # Common recommendations
        all_recommendations = []
        for result in self.analysis_results:
            all_recommendations.extend(result["recommendations"])

        if all_recommendations:
            rec_counts = {}
            for rec in all_recommendations:
                rec_counts[rec] = rec_counts.get(rec, 0) + 1

            report.append("## Common Recommendations")
            for rec, count in sorted(rec_counts.items(), key=lambda x: x[1], reverse=True):
                report.append(f"- {rec} (appears in {count} requests)")

        return "\n".join(report)


def main():
    """Main entry point for testing"""
    analyzer = AIGuidanceAnalyzer()

    # Example analysis
    example_request = "We still have outstanding for virtual assistants. So make sure you're going by the master to do list and the paddy one to do list."

    example_tool_calls = [
        {"name": "glob_file_search", "args": {"pattern": "**/master_todos.json"}},
        {"name": "glob_file_search", "args": {"pattern": "**/*paddy*"}},
        {"name": "codebase_search", "args": {"query": "What are the master todo list and paddy todo list items for virtual assistants?"}},
        {"name": "read_file", "args": {"target_file": "data/todo/master_todos.json"}},
        {"name": "read_file", "args": {"target_file": "data/ask_database/master_padawan_todos.json"}},
        {"name": "grep", "args": {"pattern": "virtual.*assistant|VA", "path": "data/todo"}},
        {"name": "write", "args": {"file_path": "scripts/python/virtual_assistant_todo_checker.py"}},
        {"name": "run_terminal_cmd", "args": {"command": "python scripts/python/virtual_assistant_todo_checker.py"}},
    ]

    analysis = analyzer.analyze_request(
        request_text=example_request,
        tool_calls=example_tool_calls,
        response_time=45.2,
        context_size=150000  # 150KB
    )

    analyzer.print_analysis(analysis)

    # Generate report
    report = analyzer.generate_report()
    print("\n" + "=" * 80)
    print("📊 ANALYSIS REPORT")
    print("=" * 80)
    print(report)


if __name__ == "__main__":


    main()