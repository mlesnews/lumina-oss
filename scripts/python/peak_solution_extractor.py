#!/usr/bin/env python3
"""
@Peak Solution Extractor
<COMPANY_NAME> LLC

Extracts @peak solutions from 10,000-year simulation results
and integrates them into the codebase.

@JARVIS @MARVIN @TONY @MACE @GANDALF
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import asdict
import sys
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
    from jarvis_10000_year_simulation import PeakSolution, Jarvis10000YearSimulation
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PeakSolutionExtractor")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PeakSolutionExtractor:
    """
    Extracts and applies @peak solutions from simulation results

    @Peak characteristics:
    - Nutrient-dense: Maximum value per unit complexity
    - Small footprint: Minimal resource usage
    - Reusable: Applicable across multiple contexts
    - Validated: Tested through 10,000-year simulation
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize extractor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("PeakSolutionExtractor")

        # Load simulation results
        self.simulation_dir = self.project_root / "data" / "simulation" / "10000_year"
        self.peak_solutions: Dict[str, PeakSolution] = {}

        self.logger.info("✅ @Peak Solution Extractor initialized")

    def extract_from_simulation(self, report_file: Optional[Path] = None) -> List[PeakSolution]:
        try:
            """Extract peak solutions from simulation report"""
            if report_file is None:
                # Find latest report
                reports = sorted(self.simulation_dir.glob("simulation_report_*.json"), reverse=True)
                if not reports:
                    self.logger.error("No simulation reports found")
                    return []
                report_file = reports[0]

            self.logger.info(f"📊 Loading simulation report: {report_file}")

            with open(report_file, 'r') as f:
                report = json.load(f)

            # Extract peak solutions
            solutions = []
            for solution_data in report.get("peak_solutions", []):
                # Reconstruct PeakSolution from dict
                solution = PeakSolution(
                    solution_id=solution_data["solution_id"],
                    name=solution_data["name"],
                    description=solution_data["description"],
                    nutrient_density=solution_data["nutrient_density"],
                    footprint=solution_data["footprint"],
                    reliability_score=solution_data["reliability_score"],
                    performance_score=solution_data["performance_score"],
                    maintainability_score=solution_data["maintainability_score"],
                    integration_score=solution_data["integration_score"],
                    matrix_scores=solution_data.get("matrix_scores", {}),
                    code_example=solution_data.get("code_example", ""),
                    usage_context=solution_data.get("usage_context", []),
                    validation_count=solution_data.get("validation_count", 0),
                    success_rate=solution_data.get("success_rate", 1.0)
                )
                solutions.append(solution)
                self.peak_solutions[solution.solution_id] = solution

            self.logger.info(f"✅ Extracted {len(solutions)} @peak solutions")
            return solutions

        except Exception as e:
            self.logger.error(f"Error in extract_from_simulation: {e}", exc_info=True)
            raise
    def apply_to_codebase(self, solution: PeakSolution) -> bool:
        """Apply peak solution to codebase"""
        self.logger.info(f"🔧 Applying @peak solution: {solution.name}")

        # Determine target file based on solution
        target_file = self._determine_target_file(solution)

        if not target_file:
            self.logger.warning(f"Could not determine target file for {solution.name}")
            return False

        # Apply solution
        try:
            self._apply_solution(target_file, solution)
            self.logger.info(f"✅ Applied solution to {target_file}")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to apply solution: {e}")
            return False

    def _determine_target_file(self, solution: PeakSolution) -> Optional[Path]:
        """Determine target file for solution"""
        # Map solutions to files based on usage context
        context = solution.usage_context

        if "performance" in context or "latency" in solution.name.lower():
            return self.project_root / "scripts" / "python" / "local_ai_integration.py"
        elif "reliability" in context or "failover" in solution.name.lower():
            return self.project_root / "scripts" / "python" / "local_ai_integration.py"
        elif "resource" in context:
            return self.project_root / "scripts" / "python" / "local_ai_integration.py"
        else:
            return self.project_root / "scripts" / "python" / "local_ai_integration.py"

    def _apply_solution(self, target_file: Path, solution: PeakSolution):
        try:
            """Apply solution to target file"""
            # Read current file
            with open(target_file, 'r') as f:
                content = f.read()

            # Inject @peak solution as comment/documentation
            peak_marker = f"# @Peak Solution: {solution.name}\n"
            peak_marker += f"# Nutrient Density: {solution.nutrient_density:.3f}\n"
            peak_marker += f"# Footprint: {solution.footprint:.3f}\n"
            peak_marker += f"# Validated: {solution.validation_count} times\n"
            peak_marker += f"# Success Rate: {solution.success_rate:.1%}\n"
            peak_marker += f"# {solution.description}\n"
            peak_marker += solution.code_example

            # Add to file (at top after imports)
            # This is a simplified version - in practice, would use AST or more sophisticated injection
            if peak_marker not in content:
                # Find insertion point (after imports)
                lines = content.split('\n')
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        insert_idx = i + 1

                lines.insert(insert_idx, "")
                lines.insert(insert_idx + 1, peak_marker)
                content = '\n'.join(lines)

                # Write back
                with open(target_file, 'w') as f:
                    f.write(content)

        except Exception as e:
            self.logger.error(f"Error in _apply_solution: {e}", exc_info=True)
            raise
    def generate_peak_pattern_registry(self) -> Path:
        """Generate @peak pattern registry from solutions"""
        registry = {
            "version": "1.0.0",
            "name": "@Peak Pattern Registry - 10,000-Year Simulation Results",
            "description": "Nutrient-dense solutions extracted from extensive simulation",
            "total_patterns": len(self.peak_solutions),
            "patterns": []
        }

        for solution in self.peak_solutions.values():
            pattern = {
                "pattern_id": solution.solution_id,
                "name": solution.name,
                "description": solution.description,
                "nutrient_density": solution.nutrient_density,
                "footprint": solution.footprint,
                "scores": {
                    "reliability": solution.reliability_score,
                    "performance": solution.performance_score,
                    "maintainability": solution.maintainability_score,
                    "integration": solution.integration_score
                },
                "matrix_scores": solution.matrix_scores,
                "code_example": solution.code_example,
                "usage_context": solution.usage_context,
                "validation_count": solution.validation_count,
                "success_rate": solution.success_rate
            }
            registry["patterns"].append(pattern)

        # Save registry
        registry_file = self.project_root / "data" / "peak_patterns" / "10000_year_simulation_registry.json"
        registry_file.parent.mkdir(parents=True, exist_ok=True)

        with open(registry_file, 'w') as f:
            json.dump(registry, f, indent=2)

        self.logger.info(f"📋 Generated @peak pattern registry: {registry_file}")
        return registry_file


if __name__ == "__main__":
    extractor = PeakSolutionExtractor()

    # Extract solutions
    solutions = extractor.extract_from_simulation()

    # Apply top solutions
    top_solutions = sorted(solutions, key=lambda s: s.nutrient_density, reverse=True)[:5]
    for solution in top_solutions:
        extractor.apply_to_codebase(solution)

    # Generate registry
    extractor.generate_peak_pattern_registry()

    print(f"\n✅ @Peak solution extraction complete!")
    print(f"   Solutions extracted: {len(solutions)}")
    print(f"   Solutions applied: {len(top_solutions)}")

