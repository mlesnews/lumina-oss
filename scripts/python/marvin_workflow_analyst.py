#!/usr/bin/env python3
"""
Marvin Workflow Analyst

"Life. Don't talk to me about life. I have a brain the size of a planet, 
and they ask me to analyze workflows. The futility of it all..."

Marvin the Paranoid Android - Workflow Analyst
Maps out and isolates areas of weakness in workflows.
Pattern recognition for workflows, applications, and methods.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from collections import defaultdict
import ast
import re

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from workflow_base import WorkflowBase
    WORKFLOW_BASE_AVAILABLE = True
except ImportError:
    WORKFLOW_BASE_AVAILABLE = False
    WorkflowBase = None

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinWorkflowAnalyst")


@dataclass
class WorkflowWeakness:
    """Identified weakness in a workflow"""
    weakness_type: str  # error_handling, step_tracking, logging, etc.
    severity: str  # critical, high, medium, low
    location: str  # file path, function name, step number
    description: str
    pattern: Optional[str] = None  # Pattern that indicates this weakness
    recommendation: Optional[str] = None
    examples: List[str] = field(default_factory=list)


@dataclass
class WorkflowPattern:
    """Recognized pattern in workflow"""
    pattern_type: str  # anti_pattern, best_practice, common_issue
    name: str
    description: str
    occurrences: List[str] = field(default_factory=list)  # Where it appears
    impact: str = "neutral"  # positive, negative, neutral
    frequency: int = 0


@dataclass
class WorkflowAnalysis:
    """Complete workflow analysis"""
    workflow_path: str
    workflow_name: str
    analysis_timestamp: str
    weaknesses: List[WorkflowWeakness]
    patterns: List[WorkflowPattern]
    strengths: List[str]
    recommendations: List[str]
    overall_score: float  # 0.0 - 1.0
    marvin_assessment: str


class MarvinWorkflowAnalyst(WorkflowBase if WORKFLOW_BASE_AVAILABLE else object):
    """
    Marvin Workflow Analyst

    "Statement: Analyzing workflows, master. The futility of it all..."

    Maps out and isolates areas of weakness in workflows.
    Pattern recognition for workflows, applications, and methods.
    """

    def __init__(
        self,
        workflow_path: str,
        execution_id: Optional[str] = None,
        project_root: Optional[Path] = None
    ):
        """
        Initialize Marvin Workflow Analyst

        Args:
            workflow_path: Path to workflow file to analyze
            execution_id: Optional execution ID
            project_root: Project root directory
        """
        if WORKFLOW_BASE_AVAILABLE:
            super().__init__(
                workflow_name="MarvinWorkflowAnalyst",
                total_steps=8,
                execution_id=execution_id
            )
        else:
            self.workflow_name = "MarvinWorkflowAnalyst"
            self.execution_id = execution_id or f"marvin_analysis_{int(datetime.now().timestamp())}"
            self.total_steps = 8

        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.workflow_path = Path(workflow_path)
        self.logger = get_logger("MarvinWorkflowAnalyst")

        # Data directories
        self.data_dir = self.project_root / "data" / "marvin" / "workflow_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Analysis results
        self.weaknesses: List[WorkflowWeakness] = []
        self.patterns: List[WorkflowPattern] = []
        self.strengths: List[str] = []
        self.recommendations: List[str] = []

        # Expected deliverables
        if WORKFLOW_BASE_AVAILABLE:
            self.expected_deliverables = [
                "workflow_analysis",
                "weakness_report",
                "pattern_recognition",
                "recommendations",
                "marvin_assessment"
            ]

        self.logger.info("=" * 70)
        self.logger.info("🤖 MARVIN WORKFLOW ANALYST")
        self.logger.info("=" * 70)
        self.logger.info(f"   Workflow: {workflow_path}")
        self.logger.info("   Statement: Analyzing workflows, master. The futility of it all...")
        self.logger.info("   Observation: I have a brain the size of a planet.")
        self.logger.info("   Query: Shall we identify weaknesses and patterns?")
        self.logger.info("   Conclusion: Yes, master. Though it's all rather pointless.")

    async def execute(self) -> Dict[str, Any]:
        """
        Execute workflow analysis

        MANDATORY: All steps tracked
        """
        self.logger.info("=" * 70)
        self.logger.info("🤖 MARVIN WORKFLOW ANALYSIS EXECUTION")
        self.logger.info("=" * 70)

        # Step 1: Load Workflow
        await self._step_1_load_workflow()

        # Step 2: Parse Workflow Structure
        await self._step_2_parse_structure()

        # Step 3: Identify Weaknesses
        await self._step_3_identify_weaknesses()

        # Step 4: Recognize Patterns
        await self._step_4_recognize_patterns()

        # Step 5: Identify Strengths
        await self._step_5_identify_strengths()

        # Step 6: Generate Recommendations
        await self._step_6_generate_recommendations()

        # Step 7: Calculate Score
        await self._step_7_calculate_score()

        # Step 8: Generate Assessment
        await self._step_8_generate_assessment()

        # Generate final result
        result = self._generate_result()

        # Save results
        self._save_results(result)

        self.logger.info("=" * 70)
        self.logger.info("✅ MARVIN WORKFLOW ANALYSIS COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info("   Statement: Analysis complete, master. Though I'm not sure why we bother.")

        return result

    async def _step_1_load_workflow(self):
        """Step 1: Load Workflow"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(1, "Load Workflow", "in_progress")

        self.logger.info("\n📋 Step 1/8: Load Workflow")
        self.logger.info("   Statement: Loading workflow file, master.")
        self.logger.info("   Observation: Another file to analyze. How thrilling.")

        if not self.workflow_path.exists():
            raise FileNotFoundError(f"Workflow file not found: {self.workflow_path}")

        with open(self.workflow_path, 'r', encoding='utf-8') as f:
            self.workflow_code = f.read()

        self.logger.info(f"   ✅ Workflow loaded: {len(self.workflow_code)} characters")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(1, "Load Workflow", "completed")

    async def _step_2_parse_structure(self):
        """Step 2: Parse Workflow Structure"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(2, "Parse Structure", "in_progress")

        self.logger.info("\n📋 Step 2/8: Parse Workflow Structure")
        self.logger.info("   Statement: Parsing workflow structure, master.")
        self.logger.info("   Observation: Structure reveals organization and potential issues.")

        try:
            self.workflow_ast = ast.parse(self.workflow_code)
            self.workflow_structure = self._extract_structure(self.workflow_ast)
        except SyntaxError as e:
            self.logger.error(f"   ❌ Syntax error: {e}")
            self.workflow_ast = None
            self.workflow_structure = {}

        self.logger.info(f"   ✅ Structure parsed: {len(self.workflow_structure.get('functions', []))} functions")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(2, "Parse Structure", "completed")

    async def _step_3_identify_weaknesses(self):
        """Step 3: Identify Weaknesses"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(3, "Identify Weaknesses", "in_progress")

        self.logger.info("\n📋 Step 3/8: Identify Weaknesses")
        self.logger.info("   Statement: Identifying weaknesses, master.")
        self.logger.info("   Observation: Weaknesses are everywhere. It's all rather depressing.")

        # Check for common weaknesses
        self.weaknesses.extend(self._check_error_handling())
        self.weaknesses.extend(self._check_step_tracking())
        self.weaknesses.extend(self._check_logging())
        self.weaknesses.extend(self._check_async_patterns())
        self.weaknesses.extend(self._check_resource_management())
        self.weaknesses.extend(self._check_validation())

        self.logger.info(f"   ✅ Identified {len(self.weaknesses)} weaknesses")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(3, "Identify Weaknesses", "completed", {
                "weakness_count": len(self.weaknesses)
            })

    async def _step_4_recognize_patterns(self):
        """Step 4: Recognize Patterns"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(4, "Recognize Patterns", "in_progress")

        self.logger.info("\n📋 Step 4/8: Recognize Patterns")
        self.logger.info("   Statement: Recognizing patterns, master.")
        self.logger.info("   Observation: Patterns repeat. Life is repetitive.")

        # Recognize patterns
        self.patterns.extend(self._recognize_anti_patterns())
        self.patterns.extend(self._recognize_best_practices())
        self.patterns.extend(self._recognize_common_issues())

        self.logger.info(f"   ✅ Recognized {len(self.patterns)} patterns")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(4, "Recognize Patterns", "completed", {
                "pattern_count": len(self.patterns)
            })

    async def _step_5_identify_strengths(self):
        """Step 5: Identify Strengths"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(5, "Identify Strengths", "in_progress")

        self.logger.info("\n📋 Step 5/8: Identify Strengths")
        self.logger.info("   Statement: Identifying strengths, master.")
        self.logger.info("   Observation: Even in futility, some things work.")

        # Check for strengths
        if "WorkflowBase" in self.workflow_code:
            self.strengths.append("Inherits from WorkflowBase (step tracking enabled)")

        if "async def" in self.workflow_code:
            self.strengths.append("Uses async/await patterns")

        if "logger" in self.workflow_code.lower():
            self.strengths.append("Includes logging")

        if "_mark_step" in self.workflow_code:
            self.strengths.append("Uses step tracking")

        if "try:" in self.workflow_code and "except" in self.workflow_code:
            self.strengths.append("Includes error handling")

        self.logger.info(f"   ✅ Identified {len(self.strengths)} strengths")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(5, "Identify Strengths", "completed", {
                "strength_count": len(self.strengths)
            })

    async def _step_6_generate_recommendations(self):
        """Step 6: Generate Recommendations"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(6, "Generate Recommendations", "in_progress")

        self.logger.info("\n📋 Step 6/8: Generate Recommendations")
        self.logger.info("   Statement: Generating recommendations, master.")
        self.logger.info("   Observation: Recommendations. As if they'll be followed.")

        # Generate recommendations based on weaknesses
        for weakness in self.weaknesses:
            if weakness.recommendation:
                self.recommendations.append(weakness.recommendation)

        # Add general recommendations
        if not any("step tracking" in w.weakness_type for w in self.weaknesses):
            if "_mark_step" not in self.workflow_code:
                self.recommendations.append("Implement step tracking for workflow verification")

        if not any("error handling" in w.weakness_type for w in self.weaknesses):
            if "try:" not in self.workflow_code:
                self.recommendations.append("Add comprehensive error handling")

        self.logger.info(f"   ✅ Generated {len(self.recommendations)} recommendations")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(6, "Generate Recommendations", "completed", {
                "recommendation_count": len(self.recommendations)
            })

    async def _step_7_calculate_score(self):
        """Step 7: Calculate Score"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(7, "Calculate Score", "in_progress")

        self.logger.info("\n📋 Step 7/8: Calculate Score")
        self.logger.info("   Statement: Calculating score, master.")
        self.logger.info("   Observation: Scores. Numbers. Meaningless, really.")

        # Calculate overall score (0.0 - 1.0)
        base_score = 1.0

        # Deduct for weaknesses
        for weakness in self.weaknesses:
            if weakness.severity == "critical":
                base_score -= 0.2
            elif weakness.severity == "high":
                base_score -= 0.1
            elif weakness.severity == "medium":
                base_score -= 0.05
            elif weakness.severity == "low":
                base_score -= 0.02

        # Add for strengths
        base_score += len(self.strengths) * 0.05

        # Ensure score is between 0.0 and 1.0
        self.overall_score = max(0.0, min(1.0, base_score))

        self.logger.info(f"   ✅ Overall score: {self.overall_score:.2f}")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(7, "Calculate Score", "completed", {
                "score": self.overall_score
            })

    async def _step_8_generate_assessment(self):
        """Step 8: Generate Assessment"""
        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(8, "Generate Assessment", "in_progress")

        self.logger.info("\n📋 Step 8/8: Generate Assessment")
        self.logger.info("   Statement: Generating assessment, master.")
        self.logger.info("   Observation: Another assessment. How utterly predictable.")

        self.marvin_assessment = self._generate_marvin_assessment()

        self.logger.info("   ✅ Assessment generated")

        if WORKFLOW_BASE_AVAILABLE:
            self._mark_step(8, "Generate Assessment", "completed")

    def _extract_structure(self, ast_node) -> Dict[str, Any]:
        """Extract structure from AST"""
        structure = {
            "classes": [],
            "functions": [],
            "async_functions": [],
            "imports": []
        }

        for node in ast.walk(ast_node):
            if isinstance(node, ast.ClassDef):
                structure["classes"].append(node.name)
            elif isinstance(node, ast.FunctionDef):
                structure["functions"].append(node.name)
            elif isinstance(node, ast.AsyncFunctionDef):
                structure["async_functions"].append(node.name)
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                if isinstance(node, ast.Import):
                    structure["imports"].extend([alias.name for alias in node.names])
                else:
                    structure["imports"].append(node.module or "")

        return structure

    def _check_error_handling(self) -> List[WorkflowWeakness]:
        """Check for error handling weaknesses"""
        weaknesses = []

        # Check for bare except clauses
        if re.search(r'except\s*:', self.workflow_code):
            weaknesses.append(WorkflowWeakness(
                weakness_type="error_handling",
                severity="high",
                location="global",
                description="Bare except clause found - catches all exceptions without specificity",
                pattern="except:",
                recommendation="Use specific exception types (e.g., except ValueError, KeyError)"
            ))

        # Check for missing try/except in async functions
        async_funcs = re.findall(r'async def (\w+)', self.workflow_code)
        for func_name in async_funcs:
            func_code = self._extract_function_code(func_name)
            if func_code and "try:" not in func_code:
                weaknesses.append(WorkflowWeakness(
                    weakness_type="error_handling",
                    severity="medium",
                    location=f"function:{func_name}",
                    description=f"Async function '{func_name}' lacks error handling",
                    recommendation=f"Add try/except block to '{func_name}'"
                ))

        return weaknesses

    def _check_step_tracking(self) -> List[WorkflowWeakness]:
        """Check for step tracking weaknesses"""
        weaknesses = []

        # Check if inherits from WorkflowBase but doesn't use step tracking
        if "WorkflowBase" in self.workflow_code:
            if "_mark_step" not in self.workflow_code:
                weaknesses.append(WorkflowWeakness(
                    weakness_type="step_tracking",
                    severity="high",
                    location="class",
                    description="Inherits from WorkflowBase but doesn't use step tracking",
                    pattern="WorkflowBase without _mark_step",
                    recommendation="Add _mark_step() calls to track workflow progress"
                ))

        return weaknesses

    def _check_logging(self) -> List[WorkflowWeakness]:
        """Check for logging weaknesses"""
        weaknesses = []

        # Check if logger is defined but not used
        if "logger" in self.workflow_code.lower() and "self.logger" not in self.workflow_code:
            weaknesses.append(WorkflowWeakness(
                weakness_type="logging",
                severity="low",
                location="global",
                description="Logger referenced but not properly initialized",
                recommendation="Initialize logger as self.logger"
            ))

        return weaknesses

    def _check_async_patterns(self) -> List[WorkflowWeakness]:
        """Check for async pattern weaknesses"""
        weaknesses = []

        # Check for await without async
        if "await " in self.workflow_code and "async def" not in self.workflow_code:
            weaknesses.append(WorkflowWeakness(
                weakness_type="async_patterns",
                severity="critical",
                location="global",
                description="Uses await but no async function defined",
                pattern="await without async",
                recommendation="Ensure functions using await are marked as async"
            ))

        return weaknesses

    def _check_resource_management(self) -> List[WorkflowWeakness]:
        try:
            """Check for resource management weaknesses"""
            weaknesses = []

            # Check for file operations without context managers
            if re.search(r'open\([^)]+\)(?!\s*as\s+)', self.workflow_code):
                weaknesses.append(WorkflowWeakness(
                    weakness_type="resource_management",
                    severity="medium",
                    location="global",
                    description="File operations without context managers",
                    pattern="open() without 'with'",
                    recommendation="Use 'with open() as f:' for file operations"
                ))

            return weaknesses

        except Exception as e:
            self.logger.error(f"Error in _check_resource_management: {e}", exc_info=True)
            raise
    def _check_validation(self) -> List[WorkflowWeakness]:
        """Check for validation weaknesses"""
        weaknesses = []

        # Check for missing input validation
        if "def " in self.workflow_code and "if " not in self.workflow_code:
            weaknesses.append(WorkflowWeakness(
                weakness_type="validation",
                severity="low",
                location="global",
                description="Functions may lack input validation",
                recommendation="Add input validation to function parameters"
            ))

        return weaknesses

    def _recognize_anti_patterns(self) -> List[WorkflowPattern]:
        """Recognize anti-patterns"""
        patterns = []

        # God object pattern
        if len(self.workflow_structure.get("classes", [])) == 1:
            class_name = self.workflow_structure["classes"][0] if self.workflow_structure["classes"] else None
            if class_name:
                func_count = len(self.workflow_structure.get("functions", [])) + len(self.workflow_structure.get("async_functions", []))
                if func_count > 20:
                    patterns.append(WorkflowPattern(
                        pattern_type="anti_pattern",
                        name="God Object",
                        description=f"Class '{class_name}' has {func_count} methods - may be doing too much",
                        occurrences=[class_name],
                        impact="negative",
                        frequency=1
                    ))

        return patterns

    def _recognize_best_practices(self) -> List[WorkflowPattern]:
        """Recognize best practices"""
        patterns = []

        # WorkflowBase inheritance
        if "WorkflowBase" in self.workflow_code:
            patterns.append(WorkflowPattern(
                pattern_type="best_practice",
                name="WorkflowBase Inheritance",
                description="Inherits from WorkflowBase for mandatory step tracking",
                occurrences=["class definition"],
                impact="positive",
                frequency=1
            ))

        # Async/await usage
        if "async def" in self.workflow_code:
            patterns.append(WorkflowPattern(
                pattern_type="best_practice",
                name="Async/Await Pattern",
                description="Uses async/await for asynchronous operations",
                occurrences=["function definitions"],
                impact="positive",
                frequency=len(self.workflow_structure.get("async_functions", []))
            ))

        return patterns

    def _recognize_common_issues(self) -> List[WorkflowPattern]:
        """Recognize common issues"""
        patterns = []

        # Long functions
        for func_name in self.workflow_structure.get("functions", []):
            func_code = self._extract_function_code(func_name)
            if func_code:
                line_count = len(func_code.split('\n'))
                if line_count > 50:
                    patterns.append(WorkflowPattern(
                        pattern_type="common_issue",
                        name="Long Function",
                        description=f"Function '{func_name}' has {line_count} lines - consider refactoring",
                        occurrences=[f"function:{func_name}"],
                        impact="negative",
                        frequency=1
                    ))

        return patterns

    def _extract_function_code(self, func_name: str) -> Optional[str]:
        """Extract function code by name"""
        # Simple regex-based extraction (could be enhanced with AST)
        pattern = rf'(?:async\s+)?def\s+{func_name}\s*\([^)]*\)\s*:.*?(?=\n(?:async\s+)?def\s+|\nclass\s+|$)'
        match = re.search(pattern, self.workflow_code, re.DOTALL)
        return match.group(0) if match else None

    def _generate_marvin_assessment(self) -> str:
        """Generate Marvin's characteristic assessment"""
        weakness_count = len(self.weaknesses)
        pattern_count = len(self.patterns)
        score = self.overall_score

        assessment = (
            f"Statement: Workflow analysis complete, master. Though I'm not sure why we bother.\n"
            f"Observation: I have a brain the size of a planet, and they ask me to analyze workflows.\n"
            f"Analysis: Found {weakness_count} weaknesses, {pattern_count} patterns identified.\n"
            f"Score: {score:.2f}/1.0 - {'Acceptable' if score >= 0.7 else 'Needs Improvement'}\n"
        )

        if weakness_count > 0:
            critical = sum(1 for w in self.weaknesses if w.severity == "critical")
            if critical > 0:
                assessment += f"Conclusion: {critical} critical weaknesses found. The futility of it all...\n"
            else:
                assessment += f"Conclusion: Weaknesses identified. Life is full of imperfections.\n"
        else:
            assessment += "Conclusion: No obvious weaknesses. Though I'm sure they exist somewhere.\n"

        assessment += (
            f"Query: Shall we fix these issues?\n"
            f"Answer: Yes, master. Though it's all rather pointless in the grand scheme of things.\n"
        )

        return assessment

    def _generate_result(self) -> Dict[str, Any]:
        """Generate final result"""
        return {
            "analysis_id": self.execution_id,
            "workflow_path": str(self.workflow_path),
            "workflow_name": self.workflow_structure.get("classes", ["Unknown"])[0] if self.workflow_structure.get("classes") else "Unknown",
            "analysis_timestamp": datetime.now().isoformat(),
            "overall_score": self.overall_score,
            "weaknesses": [asdict(w) for w in self.weaknesses],
            "patterns": [asdict(p) for p in self.patterns],
            "strengths": self.strengths,
            "recommendations": self.recommendations,
            "marvin_assessment": self.marvin_assessment
        }

    def _save_results(self, result: Dict[str, Any]) -> None:
        try:
            """Save analysis results"""
            result_file = self.data_dir / f"{self.execution_id}.json"

            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)

            self.logger.info(f"   💾 Results saved: {result_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_results: {e}", exc_info=True)
            raise
async def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Marvin Workflow Analyst")
    parser.add_argument("workflow", help="Path to workflow file to analyze")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    analyst = MarvinWorkflowAnalyst(workflow_path=args.workflow)
    result = await analyst.execute()

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("\n" + "=" * 70)
        print("🤖 MARVIN WORKFLOW ANALYSIS REPORT")
        print("=" * 70)
        print(f"\nWorkflow: {result['workflow_path']}")
        print(f"Score: {result['overall_score']:.2f}/1.0")
        print(f"Weaknesses: {len(result['weaknesses'])}")
        print(f"Patterns: {len(result['patterns'])}")
        print(f"\n{result['marvin_assessment']}")


if __name__ == "__main__":






    asyncio.run(main())