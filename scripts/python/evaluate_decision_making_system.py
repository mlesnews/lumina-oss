#!/usr/bin/env python3
"""
End-to-End Decision-Making System Evaluation
Deep dive analysis of all decision points, flows, and patterns

ANALYTICAL TOOL - Evaluates decision-making system comprehensively
"""

import sys
import json
import ast
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set, Optional, Tuple
from collections import defaultdict
from dataclasses import dataclass, asdict, field
import inspect
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DecisionSystemEval")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DecisionPoint:
    """A single decision point in the system"""
    file: str
    function: str
    line: int
    decision_type: str  # routing, selection, evaluation, priority, etc.
    criteria: List[str]  # What criteria are used
    methods: List[str]  # Methods/functions used for decision
    dependencies: List[str]  # What the decision depends on
    confidence_scoring: bool = False
    explanation_required: bool = False
    fallback_strategy: Optional[str] = None


@dataclass
class DecisionFlow:
    """A flow of decisions"""
    flow_id: str
    name: str
    entry_point: str
    decision_points: List[DecisionPoint]
    flow_path: List[str]
    outcomes: List[str]
    dependencies: List[str]


@dataclass
class DecisionPattern:
    """Pattern of decision-making"""
    pattern_name: str
    occurrences: List[DecisionPoint]
    pattern_type: str  # scoring, routing, selection, evaluation
    consistency: float  # How consistent is the pattern
    quality_indicators: Dict[str, Any]


class DecisionSystemEvaluator:
    """Comprehensive decision-making system evaluator"""

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.decision_points: List[DecisionPoint] = []
        self.decision_flows: List[DecisionFlow] = []
        self.decision_patterns: Dict[str, DecisionPattern] = {}

        # Key decision-making files to analyze
        self.decision_files = [
            "scripts/python/jarvis_auto_decision.py",
            "scripts/python/jarvis_syphon_decisioning.py",
            "scripts/python/droid_actor_system.py",
            "scripts/python/watcher_uatu_jarvis_integration.py",
            "scripts/python/download_router.py",
            "scripts/python/intelligent_llm_router.py",
            "scripts/python/peak_ai_orchestrator.py",
        ]

    def analyze_file_for_decisions(self, file_path: Path) -> List[DecisionPoint]:
        """Analyze a file for decision points"""
        decisions = []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content, filename=str(file_path))
            lines = content.split('\n')

            # Walk AST to find decision-making patterns
            for node in ast.walk(tree):
                # Look for function definitions
                if isinstance(node, ast.FunctionDef):
                    func_name = node.name
                    func_line = node.lineno

                    # Check function body for decision patterns
                    decision_type = self._identify_decision_type(node, content)
                    if decision_type:
                        criteria = self._extract_decision_criteria(node, content)
                        methods = self._extract_decision_methods(node, content)
                        dependencies = self._extract_dependencies(node, content)
                        confidence = self._has_confidence_scoring(node, content)
                        explanation = self._requires_explanation(node, content)
                        fallback = self._has_fallback_strategy(node, content)

                        decisions.append(DecisionPoint(
                            file=str(file_path.relative_to(self.root_path)),
                            function=func_name,
                            line=func_line,
                            decision_type=decision_type,
                            criteria=criteria,
                            methods=methods,
                            dependencies=dependencies,
                            confidence_scoring=confidence,
                            explanation_required=explanation,
                            fallback_strategy=fallback
                        ))

        except Exception as e:
            logger.debug(f"Failed to analyze {file_path}: {e}")

        return decisions

    def _identify_decision_type(self, node: ast.FunctionDef, content: str) -> Optional[str]:
        """Identify what type of decision this function makes"""
        func_content = ast.get_source_segment(content, node) or ""
        func_lower = func_content.lower()
        func_name_lower = node.name.lower()

        # Decision type patterns
        if any(keyword in func_name_lower for keyword in ['route', 'routing']):
            return "routing"
        elif any(keyword in func_name_lower for keyword in ['select', 'choose', 'pick']):
            return "selection"
        elif any(keyword in func_name_lower for keyword in ['evaluate', 'assess', 'score']):
            return "evaluation"
        elif any(keyword in func_name_lower for keyword in ['prioritize', 'priority']):
            return "prioritization"
        elif any(keyword in func_name_lower for keyword in ['decide', 'decision']):
            return "decision"
        elif any(keyword in func_lower for keyword in ['if', 'elif', 'match', 'case']):
            # Has conditional logic - might be decision-making
            if any(keyword in func_lower for keyword in ['score', 'weight', 'calculate']):
                return "scoring"
            elif any(keyword in func_lower for keyword in ['best', 'optimal', 'maximum']):
                return "optimization"

        return None

    def _extract_decision_criteria(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract decision criteria from function"""
        criteria = []
        func_content = ast.get_source_segment(content, node) or ""

        # Look for criteria patterns
        patterns = [
            r'criteria["\']?\s*[:=]',
            r'score["\']?\s*[:=]',
            r'weight["\']?\s*[:=]',
            r'priority["\']?\s*[:=]',
            r'factor["\']?\s*[:=]',
            r'evaluation["\']?\s*[:=]',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, func_content, re.IGNORECASE)
            for match in matches:
                # Try to extract the criteria name/description
                line_start = func_content.rfind('\n', 0, match.start())
                line_end = func_content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(func_content)
                line = func_content[line_start:line_end].strip()
                if line:
                    criteria.append(line[:100])  # Limit length

        return criteria[:10]  # Limit to 10

    def _extract_decision_methods(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract methods/functions used in decision-making"""
        methods = []
        func_content = ast.get_source_segment(content, node) or ""

        # Look for function calls
        for call_node in ast.walk(node):
            if isinstance(call_node, ast.Call):
                if isinstance(call_node.func, ast.Name):
                    methods.append(call_node.func.id)
                elif isinstance(call_node.func, ast.Attribute):
                    methods.append(call_node.func.attr)

        return list(set(methods))[:20]  # Limit and deduplicate

    def _extract_dependencies(self, node: ast.FunctionDef, content: str) -> List[str]:
        """Extract dependencies for decision"""
        dependencies = []

        # Look for attribute accesses (self.something, config.something)
        for attr_node in ast.walk(node):
            if isinstance(attr_node, ast.Attribute):
                if isinstance(attr_node.value, ast.Name):
                    dependencies.append(f"{attr_node.value.id}.{attr_node.attr}")

        return list(set(dependencies))[:20]

    def _has_confidence_scoring(self, node: ast.FunctionDef, content: str) -> bool:
        """Check if function has confidence scoring"""
        func_content = ast.get_source_segment(content, node) or ""
        confidence_keywords = ['confidence', 'score', 'certainty', 'probability']
        return any(keyword in func_content.lower() for keyword in confidence_keywords)

    def _requires_explanation(self, node: ast.FunctionDef, content: str) -> bool:
        """Check if function requires/returns explanation"""
        func_content = ast.get_source_segment(content, node) or ""
        explanation_keywords = ['reason', 'explain', 'rationale', 'justification', 'why']
        return any(keyword in func_content.lower() for keyword in explanation_keywords)

    def _has_fallback_strategy(self, node: ast.FunctionDef, content: str) -> Optional[str]:
        """Check if function has fallback strategy"""
        func_content = ast.get_source_segment(content, node) or ""
        fallback_patterns = [
            r'fallback',
            r'default',
            r'else:',
            r'except',
            r'finally'
        ]

        for pattern in fallback_patterns:
            if re.search(pattern, func_content, re.IGNORECASE):
                # Try to extract fallback description
                matches = list(re.finditer(pattern, func_content, re.IGNORECASE))
                if matches:
                    match = matches[0]
                    line_start = func_content.rfind('\n', 0, match.start())
                    line_end = func_content.find('\n', match.end() + 50)
                    if line_end == -1:
                        line_end = len(func_content)
                    fallback_context = func_content[line_start:line_end].strip()[:100]
                    return fallback_context

        return None

    def identify_decision_flows(self) -> List[DecisionFlow]:
        """Identify flows of decisions"""
        flows = []

        # Group decisions by file to identify flows
        by_file = defaultdict(list)
        for decision in self.decision_points:
            by_file[decision.file].append(decision)

        # Identify flows within files
        for file, decisions in by_file.items():
            if len(decisions) > 1:
                # Potential flow - decisions in same file
                flow = DecisionFlow(
                    flow_id=f"flow_{file.replace('/', '_').replace('.py', '')}",
                    name=f"Decision flow in {file}",
                    entry_point=decisions[0].function,
                    decision_points=decisions,
                    flow_path=[d.function for d in sorted(decisions, key=lambda x: x.line)],
                    outcomes=[],
                    dependencies=list(set([dep for d in decisions for dep in d.dependencies]))
                )
                flows.append(flow)

        return flows

    def identify_decision_patterns(self) -> Dict[str, DecisionPattern]:
        """Identify patterns in decision-making"""
        patterns = {}

        # Group by decision type
        by_type = defaultdict(list)
        for decision in self.decision_points:
            by_type[decision.decision_type].append(decision)

        # Create patterns for each type
        for decision_type, decisions in by_type.items():
            if len(decisions) > 1:
                # Calculate consistency (how similar are the methods used)
                all_methods = [set(d.methods) for d in decisions]
                if all_methods:
                    common_methods = set.intersection(*all_methods) if len(all_methods) > 1 else all_methods[0]
                    total_methods = set.union(*all_methods) if len(all_methods) > 1 else all_methods[0]
                    consistency = len(common_methods) / len(total_methods) if total_methods else 0.0
                else:
                    consistency = 0.0

                patterns[decision_type] = DecisionPattern(
                    pattern_name=f"{decision_type}_pattern",
                    occurrences=decisions,
                    pattern_type=decision_type,
                    consistency=consistency,
                    quality_indicators={
                        "total_occurrences": len(decisions),
                        "has_confidence_scoring": sum(1 for d in decisions if d.confidence_scoring) / len(decisions),
                        "has_explanation": sum(1 for d in decisions if d.explanation_required) / len(decisions),
                        "has_fallback": sum(1 for d in decisions if d.fallback_strategy) / len(decisions),
                    }
                )

        return patterns

    def evaluate_decision_quality(self) -> Dict[str, Any]:
        """Evaluate overall decision-making quality"""
        total_decisions = len(self.decision_points)

        if total_decisions == 0:
            return {"error": "No decisions found"}

        quality_metrics = {
            "total_decision_points": total_decisions,
            "decision_types": {
                dt: len([d for d in self.decision_points if d.decision_type == dt])
                for dt in set(d.decision_type for d in self.decision_points)
            },
            "confidence_scoring_coverage": sum(1 for d in self.decision_points if d.confidence_scoring) / total_decisions,
            "explanation_coverage": sum(1 for d in self.decision_points if d.explanation_required) / total_decisions,
            "fallback_coverage": sum(1 for d in self.decision_points if d.fallback_strategy) / total_decisions,
            "average_criteria_per_decision": sum(len(d.criteria) for d in self.decision_points) / total_decisions,
            "decision_flows": len(self.decision_flows),
            "decision_patterns": len(self.decision_patterns),
        }

        return quality_metrics

    def analyze_system(self) -> Dict[str, Any]:
        try:
            """Perform comprehensive analysis"""
            logger.info("Analyzing decision-making system...")

            # Analyze all decision files
            for rel_path in self.decision_files:
                file_path = self.root_path / rel_path
                if file_path.exists():
                    logger.info(f"Analyzing {rel_path}...")
                    decisions = self.analyze_file_for_decisions(file_path)
                    self.decision_points.extend(decisions)
                    logger.info(f"  Found {len(decisions)} decision points")

            logger.info(f"Total decision points found: {len(self.decision_points)}")

            # Identify flows
            logger.info("Identifying decision flows...")
            self.decision_flows = self.identify_decision_flows()
            logger.info(f"Found {len(self.decision_flows)} decision flows")

            # Identify patterns
            logger.info("Identifying decision patterns...")
            self.decision_patterns = self.identify_decision_patterns()
            logger.info(f"Found {len(self.decision_patterns)} decision patterns")

            # Evaluate quality
            logger.info("Evaluating decision quality...")
            quality = self.evaluate_decision_quality()

            # Generate comprehensive report
            return self.generate_report(quality)

        except Exception as e:
            self.logger.error(f"Error in analyze_system: {e}", exc_info=True)
            raise
    def generate_report(self, quality: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive evaluation report"""
        return {
            "evaluation_date": datetime.now().isoformat(),
            "evaluation_scope": "End-to-End Decision-Making System",
            "quality_metrics": quality,
            "decision_points": [
                {
                    "file": d.file,
                    "function": d.function,
                    "line": d.line,
                    "type": d.decision_type,
                    "criteria_count": len(d.criteria),
                    "methods_count": len(d.methods),
                    "has_confidence_scoring": d.confidence_scoring,
                    "requires_explanation": d.explanation_required,
                    "has_fallback": d.fallback_strategy is not None
                }
                for d in self.decision_points
            ],
            "decision_flows": [
                {
                    "flow_id": flow.flow_id,
                    "name": flow.name,
                    "entry_point": flow.entry_point,
                    "decision_count": len(flow.decision_points),
                    "flow_path": flow.flow_path
                }
                for flow in self.decision_flows
            ],
            "decision_patterns": {
                pattern_name: {
                    "pattern_type": pattern.pattern_type,
                    "occurrences": len(pattern.occurrences),
                    "consistency": pattern.consistency,
                    "quality_indicators": pattern.quality_indicators
                }
                for pattern_name, pattern in self.decision_patterns.items()
            },
            "analysis": {
                "strengths": self._identify_strengths(),
                "weaknesses": self._identify_weaknesses(),
                "recommendations": self._generate_recommendations()
            }
        }

    def _identify_strengths(self) -> List[str]:
        """Identify strengths of decision-making system"""
        strengths = []

        if len(self.decision_points) > 0:
            strengths.append(f"Found {len(self.decision_points)} decision points - comprehensive decision coverage")

        confidence_pct = sum(1 for d in self.decision_points if d.confidence_scoring) / len(self.decision_points) * 100
        if confidence_pct > 50:
            strengths.append(f"{confidence_pct:.1f}% of decisions have confidence scoring")

        if len(self.decision_patterns) > 0:
            strengths.append(f"Identified {len(self.decision_patterns)} decision patterns - reusable patterns")

        if len(self.decision_flows) > 0:
            strengths.append(f"{len(self.decision_flows)} decision flows identified - systematic approach")

        return strengths

    def _identify_weaknesses(self) -> List[str]:
        """Identify weaknesses of decision-making system"""
        weaknesses = []

        if len(self.decision_points) == 0:
            weaknesses.append("No decision points found - system may lack explicit decision-making")
            return weaknesses

        explanation_pct = sum(1 for d in self.decision_points if d.explanation_required) / len(self.decision_points) * 100
        if explanation_pct < 50:
            weaknesses.append(f"Only {explanation_pct:.1f}% of decisions require explanation - low explainability")

        fallback_pct = sum(1 for d in self.decision_points if d.fallback_strategy) / len(self.decision_points) * 100
        if fallback_pct < 50:
            weaknesses.append(f"Only {fallback_pct:.1f}% of decisions have fallback strategies - limited resilience")

        avg_criteria = sum(len(d.criteria) for d in self.decision_points) / len(self.decision_points)
        if avg_criteria < 2:
            weaknesses.append(f"Average {avg_criteria:.1f} criteria per decision - decisions may be simplistic")

        return weaknesses

    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations for improvement"""
        recommendations = []

        if len(self.decision_points) == 0:
            recommendations.append("Add explicit decision-making functions with clear criteria")
            return recommendations

        explanation_pct = sum(1 for d in self.decision_points if d.explanation_required) / len(self.decision_points) * 100
        if explanation_pct < 70:
            recommendations.append("Increase explainability - require explanations for more decisions")

        fallback_pct = sum(1 for d in self.decision_points if d.fallback_strategy) / len(self.decision_points) * 100
        if fallback_pct < 70:
            recommendations.append("Add fallback strategies to more decisions for resilience")

        if len(self.decision_patterns) < 3:
            recommendations.append("Establish more decision-making patterns for consistency")

        recommendations.append("Document decision criteria explicitly in code")
        recommendations.append("Implement decision logging/tracking for auditability")
        recommendations.append("Create decision-making guidelines and best practices")

        return recommendations


def main():
    try:
        """Main function - EVALUATION ONLY"""
        import argparse

        parser = argparse.ArgumentParser(description="End-to-End Decision-Making System Evaluation")
        parser.add_argument("--root", default=str(project_root), help="Root directory")
        parser.add_argument("--output", help="Output JSON file")

        args = parser.parse_args()

        root = Path(args.root)
        evaluator = DecisionSystemEvaluator(root)

        logger.info("=" * 80)
        logger.info("END-TO-END DECISION-MAKING SYSTEM EVALUATION")
        logger.info("=" * 80)
        logger.info("ANALYTICAL TOOL - Comprehensive deep dive")
        logger.info("=" * 80)
        logger.info("")

        # Analyze
        report = evaluator.analyze_system()

        # Output
        if args.output:
            output_file = Path(args.output)
        else:
            output_file = project_root / "data" / "decision_system_evaluation" / f"evaluation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"\n✓ Evaluation complete")
        logger.info(f"✓ Report saved: {output_file}")
        logger.info(f"\nSUMMARY:")
        logger.info(f"  Decision Points: {report['quality_metrics'].get('total_decision_points', 0)}")
        logger.info(f"  Decision Flows: {report['quality_metrics'].get('decision_flows', 0)}")
        logger.info(f"  Decision Patterns: {report['quality_metrics'].get('decision_patterns', 0)}")
        logger.info(f"\nSTRENGTHS:")
        for strength in report['analysis']['strengths']:
            logger.info(f"  ✓ {strength}")
        logger.info(f"\nWEAKNESSES:")
        for weakness in report['analysis']['weaknesses']:
            logger.info(f"  ⚠ {weakness}")
        logger.info(f"\nRECOMMENDATIONS:")
        for rec in report['analysis']['recommendations']:
            logger.info(f"  → {rec}")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())