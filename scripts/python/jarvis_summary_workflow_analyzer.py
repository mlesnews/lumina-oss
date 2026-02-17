#!/usr/bin/env python3
"""
JARVIS Summary/Debrief Workflow Analyzer
Analyzes AI summaries and debriefs to identify workflow efficiency and effectiveness opportunities

Tags: #JARVIS #WORKFLOW #EFFICIENCY #EFFECTIVENESS #AI_SUMMARIES @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from collections import Counter, defaultdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISSummaryWorkflowAnalyzer")

PROJECT_ROOT = Path(__file__).parent.parent.parent


@dataclass
class WorkflowPattern:
    """Workflow pattern identified from summaries"""
    pattern_id: str
    pattern_type: str  # repetition, time, decision, error, knowledge_gap
    description: str
    frequency: int
    time_impact: Optional[float] = None  # hours
    effectiveness_score: Optional[float] = None  # 0-1
    opportunities: List[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class WorkflowOpportunity:
    """Workflow improvement opportunity"""
    opportunity_id: str
    title: str
    description: str
    opportunity_type: str  # automation, template, knowledge_base, optimization
    impact: str  # high, medium, low
    effort: str  # high, medium, low
    roi: str  # very_high, high, medium, low
    estimated_time_saved: Optional[float] = None  # hours/week
    priority: int = 5  # 1-10, 10 is highest


class SummaryWorkflowAnalyzer:
    """Analyze summaries/debriefs for workflow opportunities"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis" / "workflow_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.summaries: List[Dict[str, Any]] = []
        self.patterns: List[WorkflowPattern] = []
        self.opportunities: List[WorkflowOpportunity] = []

        self.logger = logger

    def load_summaries(self, summary_dir: Optional[Path] = None) -> int:
        """Load summaries from directory"""
        if summary_dir is None:
            # Try common summary locations
            summary_dirs = [
                self.project_root / "data" / "agent_chat_sessions",
                self.project_root / "data" / "agent_sessions",
                self.project_root / "data" / "homelab_model_validation",
                self.project_root / "data" / "r5_living_matrix" / "sessions",
            ]
        else:
            summary_dirs = [summary_dir]

        loaded = 0
        for summary_dir in summary_dirs:
            if not summary_dir.exists():
                continue

            # Load JSON summary files
            for summary_file in summary_dir.glob("*.json"):
                try:
                    with open(summary_file, 'r') as f:
                        summary = json.load(f)
                        summary['_source_file'] = str(summary_file)
                        summary['_loaded_at'] = datetime.now().isoformat()
                        self.summaries.append(summary)
                        loaded += 1
                except Exception as e:
                    self.logger.debug(f"Could not load {summary_file}: {e}")

        self.logger.info(f"📚 Loaded {loaded} summaries")
        return loaded

    def analyze_repetition_patterns(self) -> List[WorkflowPattern]:
        """Analyze repetition patterns in summaries"""
        patterns = []

        # Extract task/action patterns
        task_patterns = Counter()
        command_patterns = Counter()
        problem_patterns = Counter()

        for summary in self.summaries:
            # Extract tasks/actions
            content = self._get_summary_content(summary)

            # Find task patterns
            tasks = self._extract_tasks(content)
            for task in tasks:
                task_patterns[task] += 1

            # Find command patterns
            commands = self._extract_commands(content)
            for cmd in commands:
                command_patterns[cmd] += 1

            # Find problem patterns
            problems = self._extract_problems(content)
            for problem in problems:
                problem_patterns[problem] += 1

        # Identify high-frequency patterns
        for task, count in task_patterns.most_common(20):
            if count >= 3:  # Appears 3+ times
                pattern = WorkflowPattern(
                    pattern_id=f"repetition_{task.replace(' ', '_')}",
                    pattern_type="repetition",
                    description=f"Task '{task}' repeated {count} times",
                    frequency=count,
                    opportunities=[
                        f"Automate '{task}' task",
                        f"Create template for '{task}'",
                        f"Document '{task}' workflow"
                    ],
                    metadata={"task": task}
                )
                patterns.append(pattern)

        self.logger.info(f"🔁 Found {len(patterns)} repetition patterns")
        return patterns

    def analyze_time_patterns(self) -> List[WorkflowPattern]:
        """Analyze time patterns in summaries"""
        patterns = []

        # Extract time mentions
        time_patterns = defaultdict(list)

        for summary in self.summaries:
            content = self._get_summary_content(summary)

            # Find time mentions
            time_mentions = re.findall(r'(\d+)\s*(?:hours?|hrs?|minutes?|mins?|days?)', content, re.IGNORECASE)
            if time_mentions:
                # Extract context
                context = self._extract_time_context(content)
                time_patterns[context].extend(time_mentions)

        # Analyze time patterns
        for context, times in time_patterns.items():
            if len(times) >= 3:  # Appears 3+ times
                avg_time = sum(int(t) for t in times) / len(times)

                pattern = WorkflowPattern(
                    pattern_id=f"time_{context.replace(' ', '_')}",
                    pattern_type="time",
                    description=f"Task '{context}' takes average {avg_time:.1f} units",
                    frequency=len(times),
                    time_impact=avg_time,
                    opportunities=[
                        f"Optimize '{context}' task (currently {avg_time:.1f} units)",
                        f"Automate parts of '{context}' if possible",
                        f"Create checklist for '{context}' to reduce time"
                    ],
                    metadata={"context": context, "avg_time": avg_time}
                )
                patterns.append(pattern)

        self.logger.info(f"⏱️  Found {len(patterns)} time patterns")
        return patterns

    def analyze_decision_patterns(self) -> List[WorkflowPattern]:
        """Analyze decision patterns in summaries"""
        patterns = []

        # Extract decisions
        decision_patterns = defaultdict(lambda: {"success": 0, "failure": 0})

        for summary in self.summaries:
            content = self._get_summary_content(summary)

            # Find decisions
            decisions = self._extract_decisions(content)
            outcomes = self._extract_outcomes(content)

            for decision, outcome in zip(decisions, outcomes):
                if outcome in ["success", "resolved", "completed", "working"]:
                    decision_patterns[decision]["success"] += 1
                elif outcome in ["failed", "error", "problem", "issue"]:
                    decision_patterns[decision]["failure"] += 1

        # Analyze decision patterns
        for decision, counts in decision_patterns.items():
            total = counts["success"] + counts["failure"]
            if total >= 3:  # Appears 3+ times
                success_rate = counts["success"] / total if total > 0 else 0

                pattern = WorkflowPattern(
                    pattern_id=f"decision_{decision.replace(' ', '_')}",
                    pattern_type="decision",
                    description=f"Decision '{decision}' - {success_rate:.0%} success rate",
                    frequency=total,
                    effectiveness_score=success_rate,
                    opportunities=[
                        f"Document decision '{decision}' (success rate: {success_rate:.0%})",
                        f"Use '{decision}' when similar context appears" if success_rate > 0.8 else f"Review '{decision}' (low success rate)",
                        f"Create decision support for '{decision}'"
                    ],
                    metadata={"decision": decision, "success_rate": success_rate}
                )
                patterns.append(pattern)

        self.logger.info(f"🎯 Found {len(patterns)} decision patterns")
        return patterns

    def analyze_error_patterns(self) -> List[WorkflowPattern]:
        """Analyze error/problem patterns in summaries"""
        patterns = []

        # Extract errors/problems
        error_patterns = Counter()
        resolution_patterns = defaultdict(list)

        for summary in self.summaries:
            content = self._get_summary_content(summary)

            # Find errors
            errors = self._extract_errors(content)
            for error in errors:
                error_patterns[error] += 1

            # Find resolutions
            resolutions = self._extract_resolutions(content)
            for error, resolution in zip(errors, resolutions):
                if resolution:
                    resolution_patterns[error].append(resolution)

        # Analyze error patterns
        for error, count in error_patterns.most_common(20):
            if count >= 2:  # Appears 2+ times
                resolutions = resolution_patterns.get(error, [])

                pattern = WorkflowPattern(
                    pattern_id=f"error_{error.replace(' ', '_')}",
                    pattern_type="error",
                    description=f"Error '{error}' occurred {count} times",
                    frequency=count,
                    opportunities=[
                        f"Prevent '{error}' proactively",
                        f"Document resolution for '{error}'",
                        f"Create automation to handle '{error}'",
                        f"Add to knowledge base: '{error}' → {resolutions[0] if resolutions else 'TBD'}"
                    ],
                    metadata={"error": error, "resolutions": resolutions[:3]}
                )
                patterns.append(pattern)

        self.logger.info(f"❌ Found {len(patterns)} error patterns")
        return patterns

    def analyze_knowledge_gaps(self) -> List[WorkflowPattern]:
        """Analyze knowledge gap patterns"""
        patterns = []

        # Extract questions
        question_patterns = Counter()

        for summary in self.summaries:
            content = self._get_summary_content(summary)

            # Find questions
            questions = self._extract_questions(content)
            for question in questions:
                question_patterns[question] += 1

        # Identify knowledge gaps
        for question, count in question_patterns.most_common(20):
            if count >= 2:  # Asked 2+ times
                pattern = WorkflowPattern(
                    pattern_id=f"knowledge_gap_{question.replace(' ', '_')[:50]}",
                    pattern_type="knowledge_gap",
                    description=f"Question '{question}' asked {count} times",
                    frequency=count,
                    opportunities=[
                        f"Document answer to '{question}'",
                        f"Add '{question}' to knowledge base",
                        f"Create FAQ entry for '{question}'",
                        f"Proactive information: answer '{question}' before asked"
                    ],
                    metadata={"question": question}
                )
                patterns.append(pattern)

        self.logger.info(f"❓ Found {len(patterns)} knowledge gap patterns")
        return patterns

    def generate_opportunities(self) -> List[WorkflowOpportunity]:
        """Generate workflow improvement opportunities from patterns"""
        opportunities = []

        # Analyze patterns and generate opportunities
        for pattern in self.patterns:
            if pattern.pattern_type == "repetition" and pattern.frequency >= 5:
                # High-frequency repetition = automation opportunity
                opp = WorkflowOpportunity(
                    opportunity_id=f"opp_{pattern.pattern_id}",
                    title=f"Automate '{pattern.metadata.get('task', 'task')}'",
                    description=f"Task repeated {pattern.frequency} times - automate to save time",
                    opportunity_type="automation",
                    impact="high" if pattern.frequency >= 10 else "medium",
                    effort="medium",
                    roi="very_high" if pattern.frequency >= 10 else "high",
                    estimated_time_saved=pattern.frequency * 0.5,  # Estimate 30 min per occurrence
                    priority=8 if pattern.frequency >= 10 else 6
                )
                opportunities.append(opp)

            elif pattern.pattern_type == "time" and pattern.time_impact and pattern.time_impact > 1:
                # Long-running tasks = optimization opportunity
                opp = WorkflowOpportunity(
                    opportunity_id=f"opp_{pattern.pattern_id}",
                    title=f"Optimize '{pattern.metadata.get('context', 'task')}'",
                    description=f"Task takes {pattern.time_impact:.1f} units - optimize to reduce time",
                    opportunity_type="optimization",
                    impact="high" if pattern.time_impact > 2 else "medium",
                    effort="medium",
                    roi="high",
                    estimated_time_saved=pattern.time_impact * 0.3 * pattern.frequency,  # 30% reduction
                    priority=7 if pattern.time_impact > 2 else 5
                )
                opportunities.append(opp)

            elif pattern.pattern_type == "knowledge_gap" and pattern.frequency >= 3:
                # Frequent questions = knowledge base opportunity
                opp = WorkflowOpportunity(
                    opportunity_id=f"opp_{pattern.pattern_id}",
                    title=f"Document answer to '{pattern.metadata.get('question', 'question')[:50]}'",
                    description=f"Question asked {pattern.frequency} times - document to reduce questions",
                    opportunity_type="knowledge_base",
                    impact="medium",
                    effort="low",
                    roi="high",
                    estimated_time_saved=pattern.frequency * 0.25,  # 15 min saved per question
                    priority=6
                )
                opportunities.append(opp)

        # Sort by priority
        opportunities.sort(key=lambda x: x.priority, reverse=True)

        self.logger.info(f"💡 Generated {len(opportunities)} opportunities")
        return opportunities

    def _get_summary_content(self, summary: Dict[str, Any]) -> str:
        try:
            """Extract text content from summary"""
            # Try different content fields
            content_fields = ["content", "summary", "text", "description", "body", "message"]

            for field in content_fields:
                if field in summary:
                    if isinstance(summary[field], str):
                        return summary[field]
                    elif isinstance(summary[field], dict):
                        return json.dumps(summary[field])

            # Fallback: convert entire summary to string
            return json.dumps(summary)

        except Exception as e:
            self.logger.error(f"Error in _get_summary_content: {e}", exc_info=True)
            raise
    def _extract_tasks(self, content: str) -> List[str]:
        """Extract task mentions from content"""
        # Simple pattern matching - could be enhanced with NLP
        tasks = []

        # Look for task patterns
        task_patterns = [
            r'(?:create|build|implement|develop|configure|setup|install)\s+([^\.]+)',
            r'task[:\s]+([^\.]+)',
            r'work[:\s]+([^\.]+)',
        ]

        for pattern in task_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            tasks.extend(matches)

        return [t.strip() for t in tasks if len(t.strip()) > 5]

    def _extract_commands(self, content: str) -> List[str]:
        """Extract command mentions"""
        commands = []

        # Look for @ commands
        at_commands = re.findall(r'@(\w+)', content)
        commands.extend(at_commands)

        # Look for / commands
        slash_commands = re.findall(r'/(\w+)', content)
        commands.extend(slash_commands)

        return commands

    def _extract_problems(self, content: str) -> List[str]:
        """Extract problem mentions"""
        problems = []

        # Look for problem indicators
        problem_patterns = [
            r'problem[:\s]+([^\.]+)',
            r'issue[:\s]+([^\.]+)',
            r'error[:\s]+([^\.]+)',
            r'failed[:\s]+([^\.]+)',
        ]

        for pattern in problem_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            problems.extend(matches)

        return [p.strip() for p in problems if len(p.strip()) > 5]

    def _extract_time_context(self, content: str) -> str:
        """Extract context around time mentions"""
        # Find time mentions and extract surrounding context
        time_match = re.search(r'(\d+)\s*(?:hours?|hrs?|minutes?|mins?|days?)', content, re.IGNORECASE)
        if time_match:
            start = max(0, time_match.start() - 50)
            end = min(len(content), time_match.end() + 50)
            context = content[start:end].strip()
            return context[:100]  # Limit length
        return "unknown"

    def _extract_decisions(self, content: str) -> List[str]:
        """Extract decision mentions"""
        decisions = []

        # Look for decision patterns
        decision_patterns = [
            r'decided[:\s]+([^\.]+)',
            r'chose[:\s]+([^\.]+)',
            r'selected[:\s]+([^\.]+)',
            r'used[:\s]+([^\.]+)',
        ]

        for pattern in decision_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            decisions.extend(matches)

        return [d.strip() for d in decisions if len(d.strip()) > 5]

    def _extract_outcomes(self, content: str) -> List[str]:
        """Extract outcome mentions"""
        outcomes = []

        # Look for outcome indicators
        if re.search(r'\b(success|succeeded|working|resolved|completed|fixed)\b', content, re.IGNORECASE):
            outcomes.append("success")
        if re.search(r'\b(failed|error|problem|issue|broken)\b', content, re.IGNORECASE):
            outcomes.append("failure")

        return outcomes

    def _extract_errors(self, content: str) -> List[str]:
        """Extract error mentions"""
        errors = []

        # Look for error patterns
        error_patterns = [
            r'error[:\s]+([^\.]+)',
            r'failed[:\s]+([^\.]+)',
            r'issue[:\s]+([^\.]+)',
        ]

        for pattern in error_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            errors.extend(matches)

        return [e.strip() for e in errors if len(e.strip()) > 5]

    def _extract_resolutions(self, content: str) -> List[str]:
        """Extract resolution mentions"""
        resolutions = []

        # Look for resolution patterns
        resolution_patterns = [
            r'resolved[:\s]+([^\.]+)',
            r'fixed[:\s]+([^\.]+)',
            r'solution[:\s]+([^\.]+)',
        ]

        for pattern in resolution_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            resolutions.extend(matches)

        return [r.strip() for r in resolutions if len(r.strip()) > 5]

    def _extract_questions(self, content: str) -> List[str]:
        """Extract questions from content"""
        questions = []

        # Find question marks
        question_sentences = re.findall(r'([^\.!?]*\?)', content)
        questions.extend(question_sentences)

        # Find question words
        question_patterns = [
            r'(?:what|why|how|when|where|who)\s+([^\.]+)',
        ]

        for pattern in question_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            questions.extend(matches)

        return [q.strip() for q in questions if len(q.strip()) > 10]

    def analyze_all(self) -> Dict[str, Any]:
        try:
            """Run all analyses"""
            self.logger.info("=" * 80)
            self.logger.info("🔍 JARVIS SUMMARY WORKFLOW ANALYZER")
            self.logger.info("=" * 80)
            self.logger.info("")

            # Load summaries
            loaded = self.load_summaries()
            if loaded == 0:
                self.logger.warning("⚠️  No summaries loaded - check summary directories")
                return {}

            # Run analyses
            self.logger.info("")
            self.logger.info("Analyzing patterns...")
            self.logger.info("")

            repetition_patterns = self.analyze_repetition_patterns()
            time_patterns = self.analyze_time_patterns()
            decision_patterns = self.analyze_decision_patterns()
            error_patterns = self.analyze_error_patterns()
            knowledge_gaps = self.analyze_knowledge_gaps()

            # Combine all patterns
            self.patterns = repetition_patterns + time_patterns + decision_patterns + error_patterns + knowledge_gaps

            # Generate opportunities
            self.opportunities = self.generate_opportunities()

            # Generate report
            report = {
                "timestamp": datetime.now().isoformat(),
                "summaries_analyzed": len(self.summaries),
                "patterns_found": len(self.patterns),
                "opportunities_generated": len(self.opportunities),
                "patterns": {
                    "repetition": len(repetition_patterns),
                    "time": len(time_patterns),
                    "decision": len(decision_patterns),
                    "error": len(error_patterns),
                    "knowledge_gap": len(knowledge_gaps)
                },
                "top_opportunities": [
                    {
                        "title": opp.title,
                        "type": opp.opportunity_type,
                        "impact": opp.impact,
                        "roi": opp.roi,
                        "time_saved": opp.estimated_time_saved,
                        "priority": opp.priority
                    }
                    for opp in self.opportunities[:10]
                ],
                "patterns_detail": [asdict(p) for p in self.patterns[:20]],
                "opportunities_detail": [asdict(o) for o in self.opportunities]
            }

            # Save report
            report_file = self.data_dir / f"workflow_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)

            self.logger.info("")
            self.logger.info("=" * 80)
            self.logger.info("📊 ANALYSIS COMPLETE")
            self.logger.info("=" * 80)
            self.logger.info("")
            self.logger.info(f"Summaries Analyzed: {len(self.summaries)}")
            self.logger.info(f"Patterns Found: {len(self.patterns)}")
            self.logger.info(f"Opportunities Generated: {len(self.opportunities)}")
            self.logger.info("")
            self.logger.info("Top Opportunities:")
            for i, opp in enumerate(self.opportunities[:5], 1):
                self.logger.info(f"  {i}. {opp.title} (Priority: {opp.priority}, ROI: {opp.roi})")
            self.logger.info("")
            self.logger.info(f"📄 Full report saved: {report_file}")

            return report


        except Exception as e:
            self.logger.error(f"Error in analyze_all: {e}", exc_info=True)
            raise
def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Summary Workflow Analyzer")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--summary-dir', type=Path, help='Directory containing summaries')

    args = parser.parse_args()

    analyzer = SummaryWorkflowAnalyzer(project_root=args.project_root or PROJECT_ROOT)

    if args.summary_dir:
        analyzer.load_summaries(args.summary_dir)

    report = analyzer.analyze_all()

    return 0


if __name__ == "__main__":


    sys.exit(main())