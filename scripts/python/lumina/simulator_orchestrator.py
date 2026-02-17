#!/usr/bin/env python3
"""
Simulator Orchestrator - Unified Simulation Management

Orchestrates WOPR, Matrix, and Animatrix simulators through
@syphon => @pipe => @peak flow.

Tags: #SIMULATIONS #ORCHESTRATION #WOPR #MATRIX #ANIMATRIX @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SimulatorOrchestrator")


class SimulatorOrchestrator:
    """
    Simulator Orchestrator

    Orchestrates all simulators through @syphon => @pipe => @peak flow:
    - WOPR Simulator (Strategic/War games)
    - Matrix Simulator (Reality layers)
    - Animatrix Simulator (Story simulations)
    """

    def __init__(self):
        """Initialize Simulator Orchestrator"""
        logger.info("🎮 Initializing Simulator Orchestrator...")

        # Initialize simulators
        try:
            try:
                from .wopr_simulator import WOPRSimulator
            except ImportError:
                from lumina.wopr_simulator import WOPRSimulator
            self.wopr = WOPRSimulator()
            logger.info("✅ WOPR Simulator initialized")
        except Exception as e:
            logger.warning(f"WOPR Simulator not available: {e}")
            self.wopr = None

        try:
            try:
                from .matrix_simulator import MatrixSimulator
            except ImportError:
                from lumina.matrix_simulator import MatrixSimulator
            self.matrix = MatrixSimulator()
            logger.info("✅ Matrix Simulator initialized")
        except Exception as e:
            logger.warning(f"Matrix Simulator not available: {e}")
            self.matrix = None

        try:
            try:
                from .animatrix_simulator import AnimatrixSimulator, AnimatrixStory
            except ImportError:
                from lumina.animatrix_simulator import AnimatrixSimulator, AnimatrixStory
            self.animatrix = AnimatrixSimulator()
            self.AnimatrixStory = AnimatrixStory
            logger.info("✅ Animatrix Simulator initialized")
        except Exception as e:
            logger.warning(f"Animatrix Simulator not available: {e}")
            self.animatrix = None

        # Flow integration
        try:
            try:
                from .syphon import Syphon
                from .pipe import Pipe
            except ImportError:
                from lumina.syphon import Syphon
                from lumina.pipe import Pipe
            self.syphon = Syphon()
            self.pipe = Pipe()
            logger.info("✅ Flow integration (@syphon => @pipe) initialized")
        except Exception as e:
            logger.warning(f"Flow integration not available: {e}")
            self.syphon = None
            self.pipe = None

        logger.info("✅ Simulator Orchestrator initialized")

    def simulate(
        self,
        simulation_type: str,
        scenario: str,
        use_flow: bool = True
    ) -> Dict[str, Any]:
        """
        Run simulation through orchestrator.

        Args:
            simulation_type: Type of simulation (wopr, matrix, animatrix)
            scenario: Scenario to simulate
            use_flow: Use @syphon => @pipe flow

        Returns:
            Simulation result
        """
        logger.info(f"🎮 Orchestrating simulation: {simulation_type} - {scenario}")

        result = {
            'type': simulation_type,
            'scenario': scenario,
            'steps': []
        }

        # Step 1: @syphon (if enabled)
        if use_flow and self.syphon:
            logger.info("Step 1: @syphon - Extracting patterns")
            syphon_results = self.syphon.search(scenario, "scripts/python/lumina")
            result['steps'].append({
                'step': 'syphon',
                'matches': syphon_results.get('match_count', 0)
            })

            # Step 2: @pipe
            if self.pipe:
                logger.info("Step 2: @pipe - Processing")
                processed = self.pipe.process(syphon_results)
                result['steps'].append({
                    'step': 'pipe',
                    'processed': processed.get('processed', False)
                })

        # Step 3: Execute simulation
        simulation_type_lower = simulation_type.lower()

        if simulation_type_lower == 'wopr' and self.wopr:
            logger.info("Step 3: WOPR Simulation")
            sim_result = self.wopr.simulate(scenario)
            result['steps'].append({'step': 'wopr', 'executed': True})
            result['result'] = sim_result

        elif simulation_type_lower == 'matrix' and self.matrix:
            logger.info("Step 3: Matrix Simulation")
            sim_result = self.matrix.simulate_layer(scenario)
            result['steps'].append({'step': 'matrix', 'executed': True})
            result['result'] = sim_result

        elif simulation_type_lower == 'animatrix' and self.animatrix:
            logger.info("Step 3: Animatrix Simulation")
            # Try to match scenario to AnimatrixStory
            story = self._match_story(scenario)
            if story:
                sim_result = self.animatrix.simulate_story(story)
                result['steps'].append({'step': 'animatrix', 'executed': True})
                result['result'] = sim_result
            else:
                result['error'] = f'Story not found: {scenario}'
        else:
            result['error'] = f'Unknown simulation type: {simulation_type}'

        logger.info("✅ Simulation orchestration complete")
        return result

    def _match_story(self, scenario: str) -> Optional[Any]:
        """Match scenario to AnimatrixStory"""
        if not self.animatrix or not hasattr(self, 'AnimatrixStory'):
            return None

        scenario_lower = scenario.lower()
        for story in self.AnimatrixStory:
            if story.value.replace('_', ' ') in scenario_lower:
                return story
        return None

    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status"""
        return {
            'wopr': self.wopr is not None,
            'matrix': self.matrix is not None,
            'animatrix': self.animatrix is not None,
            'flow': {
                'syphon': self.syphon is not None,
                'pipe': self.pipe is not None
            }
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("🎮 SIMULATOR ORCHESTRATOR")
    print("   @syphon => @pipe => @peak <=> @WOPR/@MATRIX/@ANIMATRIX")
    print("=" * 80)
    print()

    orchestrator = SimulatorOrchestrator()

    # Status
    print("ORCHESTRATOR STATUS:")
    print("-" * 80)
    status = orchestrator.get_status()
    print(f"WOPR: {'✅' if status['wopr'] else '❌'}")
    print(f"Matrix: {'✅' if status['matrix'] else '❌'}")
    print(f"Animatrix: {'✅' if status['animatrix'] else '❌'}")
    print(f"Flow (@syphon => @pipe): {'✅' if status['flow']['syphon'] and status['flow']['pipe'] else '❌'}")
    print()

    # WOPR simulation
    print("WOPR SIMULATION:")
    print("-" * 80)
    result = orchestrator.simulate("wopr", "global_thermonuclear_war", use_flow=True)
    print(f"Type: {result['type']}")
    print(f"Steps: {len(result['steps'])}")
    if 'result' in result:
        print(f"Result: {result['result'].get('result', 'N/A')}")
    print()

    # Matrix simulation
    print("MATRIX SIMULATION:")
    print("-" * 80)
    result = orchestrator.simulate("matrix", "utopian", use_flow=True)
    print(f"Type: {result['type']}")
    if 'result' in result:
        print(f"Layer: {result['result'].get('layer', 'N/A')}")
        print(f"Message: {result['result'].get('message', 'N/A')}")
    print()

    print("=" * 80)
    print("🎮 Simulator Orchestrator - All simulators unified")
    print("=" * 80)


if __name__ == "__main__":


    main()