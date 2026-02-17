#!/usr/bin/env python3
"""
SPOCK Command System - Logical Analysis Framework

"Spock" or "@spock" triggers logical analysis of workflows, breaking them down
into basic building blocks and ensuring zero errors (syntactic + logical).

Based on Star Trek framework: Captain Kirk (user) knows where knowledge lives,
Mr. Spock (AI) applies logic and remembers everything.

Tags: #SPOCK #LOGIC #WORKFLOW #ANALYSIS #STAR_TREK @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SPOCK")


class WorkflowContext(Enum):
    """Workflow context types"""
    EDITOR = "editor"  # Cursor IDE or other IDE
    NOTEPAD = "notepad"  # Notepad or simple text editor
    TERMINAL = "terminal"  # Command line
    UNKNOWN = "unknown"  # Need to ask user


@dataclass
class WorkflowStep:
    """A single step in a workflow"""
    step_id: str
    description: str
    context: WorkflowContext
    dependencies: List[str] = field(default_factory=list)
    validation_checks: List[str] = field(default_factory=list)
    error_points: List[str] = field(default_factory=list)
    logical_checks: List[str] = field(default_factory=list)


@dataclass
class SPOCKAnalysis:
    """SPOCK analysis result"""
    workflow_name: str
    context: WorkflowContext
    steps: List[WorkflowStep]
    syntax_errors: List[str] = field(default_factory=list)
    logic_errors: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    puzzle_pieces: List[str] = field(default_factory=list)  # Basic building blocks


class SPOCKCommandSystem:
    """
    SPOCK Command System - Logical Analysis Framework

    When user says "Spock" or "@spock", applies logical analysis to workflows.

    Philosophy:
    - Captain Kirk (user): Knows where knowledge lives, doesn't need to remember everything
    - Mr. Spock (AI): Applies logic, remembers, analyzes, ensures correctness

    Principles:
    - Zero errors (syntactic + logical)
    - Puzzle pieces upside down (do it the hard way, right the first time)
    - Measure twice, cut once (but balance - not always)
    - Break down into basic building blocks
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SPOCK command system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directory
        self.data_dir = self.project_root / "data" / "spock_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Knowledge base (where knowledge lives - like Captain Kirk's library)
        self.knowledge_base = {}

        logger.info("=" * 80)
        logger.info("🖖 SPOCK COMMAND SYSTEM - LOGICAL ANALYSIS FRAMEWORK")
        logger.info("=" * 80)
        logger.info("   Philosophy: Captain Kirk knows where knowledge lives")
        logger.info("   Role: Mr. Spock applies logic and ensures correctness")
        logger.info("   Principle: Zero errors (syntactic + logical)")
        logger.info("   Method: Puzzle pieces upside down - do it right the first time")
        logger.info("=" * 80)

    def analyze_workflow(
        self,
        workflow_description: str,
        context: Optional[WorkflowContext] = None
    ) -> SPOCKAnalysis:
        """
        Analyze a workflow using SPOCK logic

        Args:
            workflow_description: Description of workflow (e.g., "editor workflow")
            context: Workflow context (editor, notepad, terminal, etc.)

        Returns:
            SPOCKAnalysis with breakdown and error checks
        """
        logger.info(f"🖖 SPOCK: Analyzing workflow - '{workflow_description}'")

        # Detect context from description if not provided
        if context is None:
            context = self._detect_context(workflow_description)

        # If context is unknown, we need to ask
        if context == WorkflowContext.UNKNOWN:
            logger.warning("   ⚠️  Context unclear - need to ask user")
            return SPOCKAnalysis(
                workflow_name=workflow_description,
                context=context,
                steps=[],
                recommendations=["Please specify: Are you working in Cursor IDE, Notepad, or another editor?"]
            )

        logger.info(f"   📍 Context detected: {context.value}")

        # Analyze workflow based on context
        if "editor" in workflow_description.lower():
            return self._analyze_editor_workflow(workflow_description, context)
        elif "script" in workflow_description.lower():
            return self._analyze_script_workflow(workflow_description, context)
        elif "document" in workflow_description.lower():
            return self._analyze_document_workflow(workflow_description, context)
        else:
            return self._analyze_generic_workflow(workflow_description, context)

    def _detect_context(self, description: str) -> WorkflowContext:
        """Detect workflow context from description"""
        description_lower = description.lower()

        if any(word in description_lower for word in ["cursor", "ide", "editor", "vscode", "code"]):
            return WorkflowContext.EDITOR
        elif "notepad" in description_lower:
            return WorkflowContext.NOTEPAD
        elif any(word in description_lower for word in ["terminal", "command", "cli"]):
            return WorkflowContext.TERMINAL
        else:
            return WorkflowContext.UNKNOWN

    def _analyze_editor_workflow(
        self,
        description: str,
        context: WorkflowContext
    ) -> SPOCKAnalysis:
        """
        Analyze editor workflow - creating scripts/documents in IDE

        Breaks down into basic building blocks (puzzle pieces upside down).
        """
        logger.info("   🔍 Analyzing editor workflow...")

        # Basic building blocks (puzzle pieces)
        puzzle_pieces = [
            "1. File Creation: Start with blank file/new file",
            "2. File Naming: Choose appropriate name and extension",
            "3. Content Writing: Write code/document content",
            "4. Syntax Validation: Check for syntax errors",
            "5. Logic Validation: Check for logical/functional errors",
            "6. File Saving: Save file to appropriate location",
            "7. Error Correction: Fix any errors found",
            "8. Final Validation: Verify zero errors (syntax + logic)",
            "9. Documentation: Add comments/documentation if needed",
            "10. Integration: Ensure proper integration with existing code"
        ]

        # Workflow steps with error points
        steps = [
            WorkflowStep(
                step_id="create_file",
                description="Create new file in editor",
                context=context,
                dependencies=[],
                validation_checks=["File created successfully", "File has correct extension"],
                error_points=["File not created", "Wrong file type/extension"],
                logical_checks=["File location appropriate", "File name follows conventions"]
            ),
            WorkflowStep(
                step_id="write_content",
                description="Write code/document content",
                context=context,
                dependencies=["create_file"],
                validation_checks=["Content written", "Syntax valid"],
                error_points=["Syntax errors", "Missing imports", "Incorrect indentation"],
                logical_checks=["Logic correct", "Functions work as intended", "No infinite loops", "Edge cases handled"]
            ),
            WorkflowStep(
                step_id="validate_syntax",
                description="Validate syntax (parser checks)",
                context=context,
                dependencies=["write_content"],
                validation_checks=["No syntax errors", "Parser passes"],
                error_points=["Syntax errors", "Type errors", "Import errors"],
                logical_checks=["All syntax rules followed"]
            ),
            WorkflowStep(
                step_id="validate_logic",
                description="Validate logic (functional correctness)",
                context=context,
                dependencies=["validate_syntax"],
                validation_checks=["Logic correct", "Functions work"],
                error_points=["Logic errors", "Function doesn't work", "Wrong output", "Side effects"],
                logical_checks=["Algorithm correct", "Data flow correct", "State management correct", "Error handling present"]
            ),
            WorkflowStep(
                step_id="save_file",
                description="Save file to appropriate location",
                context=context,
                dependencies=["validate_logic"],
                validation_checks=["File saved", "Location correct"],
                error_points=["File not saved", "Wrong location", "Permission denied"],
                logical_checks=["File in correct directory", "File structure maintained"]
            ),
            WorkflowStep(
                step_id="final_validation",
                description="Final validation - zero errors (syntax + logic)",
                context=context,
                dependencies=["save_file"],
                validation_checks=["Zero syntax errors", "Zero logic errors"],
                error_points=["Syntax errors remain", "Logic errors remain"],
                logical_checks=["All validations pass", "File ready for use"]
            )
        ]

        # Common error points
        syntax_errors = [
            "Missing imports",
            "Incorrect indentation",
            "Syntax errors (parser fails)",
            "Type errors",
            "Missing brackets/parentheses",
            "Incorrect string quotes",
            "Missing colons (Python)",
            "Incorrect variable names"
        ]

        logic_errors = [
            "Function doesn't work as intended",
            "Wrong output/result",
            "Infinite loops",
            "Missing error handling",
            "Edge cases not handled",
            "State management issues",
            "Data flow incorrect",
            "Side effects",
            "Race conditions",
            "Resource leaks"
        ]

        # Recommendations
        recommendations = [
            "Measure twice, cut once: Validate syntax AND logic before finalizing",
            "Puzzle pieces upside down: Break down into basic building blocks",
            "Zero errors goal: Both syntax and logic must be correct",
            "Ask if unclear: If context is unknown, ask user where they're working",
            "Apply SPOCK logic: Analyze each step for potential errors",
            "Integration check: Ensure new code integrates with existing codebase"
        ]

        analysis = SPOCKAnalysis(
            workflow_name=description,
            context=context,
            steps=steps,
            syntax_errors=syntax_errors,
            logic_errors=logic_errors,
            recommendations=recommendations,
            puzzle_pieces=puzzle_pieces
        )

        # Save analysis
        self._save_analysis(analysis)

        return analysis

    def _analyze_script_workflow(
        self,
        description: str,
        context: WorkflowContext
    ) -> SPOCKAnalysis:
        """Analyze script creation workflow"""
        return self._analyze_editor_workflow(description, context)

    def _analyze_document_workflow(
        self,
        description: str,
        context: WorkflowContext
    ) -> SPOCKAnalysis:
        """Analyze document creation workflow"""
        # Similar to editor workflow but with document-specific steps
        analysis = self._analyze_editor_workflow(description, context)
        # Add document-specific recommendations
        analysis.recommendations.append("Document formatting and structure")
        analysis.recommendations.append("Markdown/formatting validation")
        return analysis

    def _analyze_generic_workflow(
        self,
        description: str,
        context: WorkflowContext
    ) -> SPOCKAnalysis:
        """Analyze generic workflow"""
        return self._analyze_editor_workflow(description, context)

    def _save_analysis(self, analysis: SPOCKAnalysis):
        """Save SPOCK analysis to knowledge base"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"spock_analysis_{timestamp}.json"
        filepath = self.data_dir / filename

        try:
            import json
            data = {
                "workflow_name": analysis.workflow_name,
                "context": analysis.context.value,
                "steps": [
                    {
                        "step_id": step.step_id,
                        "description": step.description,
                        "context": step.context.value,
                        "dependencies": step.dependencies,
                        "validation_checks": step.validation_checks,
                        "error_points": step.error_points,
                        "logical_checks": step.logical_checks
                    }
                    for step in analysis.steps
                ],
                "syntax_errors": analysis.syntax_errors,
                "logic_errors": analysis.logic_errors,
                "recommendations": analysis.recommendations,
                "puzzle_pieces": analysis.puzzle_pieces,
                "timestamp": timestamp
            }

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.debug(f"   💾 Analysis saved: {filename}")

        except Exception as e:
            logger.debug(f"   Could not save analysis: {e}")

    def get_knowledge_location(self, topic: str) -> Optional[str]:
        """
        Get location of knowledge (Captain Kirk approach)

        Instead of remembering everything, know where knowledge lives.
        """
        # Search knowledge base
        if topic in self.knowledge_base:
            return self.knowledge_base[topic]

        # Search recent analyses
        for analysis_file in sorted(self.data_dir.glob("spock_analysis_*.json"), reverse=True):
            try:
                import json
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if topic.lower() in data.get("workflow_name", "").lower():
                        return str(analysis_file)
            except Exception:
                continue

        return None


def process_spock_command(command: str) -> SPOCKAnalysis:
    """
    Process SPOCK command

    Detects "spock" or "@spock" and analyzes the workflow.

    Args:
        command: User command (e.g., "spock the editor workflow")

    Returns:
        SPOCKAnalysis result
    """
    command_lower = command.lower().strip()

    # Check if SPOCK command
    if not (command_lower.startswith("spock") or command_lower.startswith("@spock")):
        return None

    # Extract workflow description
    workflow_desc = command_lower.replace("spock", "").replace("@spock", "").strip()
    if not workflow_desc:
        workflow_desc = "editor workflow"  # Default

    # Analyze
    spock = SPOCKCommandSystem()
    return spock.analyze_workflow(workflow_desc)


def main():
    """Test SPOCK system"""
    spock = SPOCKCommandSystem()

    print("\n🖖 Testing SPOCK Command System")
    print("=" * 80)

    # Test 1: Editor workflow
    print("\n📋 Test 1: Editor Workflow")
    analysis = spock.analyze_workflow("editor workflow")
    print(f"   Workflow: {analysis.workflow_name}")
    print(f"   Context: {analysis.context.value}")
    print(f"   Steps: {len(analysis.steps)}")
    print(f"   Puzzle Pieces: {len(analysis.puzzle_pieces)}")
    print(f"\n   Building Blocks:")
    for piece in analysis.puzzle_pieces:
        print(f"      {piece}")

    print(f"\n   Recommendations:")
    for rec in analysis.recommendations[:3]:
        print(f"      • {rec}")

    print("\n" + "=" * 80)


if __name__ == "__main__":


    main()