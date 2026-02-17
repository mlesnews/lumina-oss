#!/usr/bin/env python3
"""
IMVA Matrix Simulation Pipe
Pipes Iron Man Virtual Assistant through duo A & B matrix/lattice simulations

Runs IMVA as subprocess and feeds its data into parallel physics matrix simulations.
@WOPR @LUMINA @JARVIS
"""

import sys
import subprocess
import threading
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from queue import Queue
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IMVAMatrixSimulationPipe")

try:
    from physics_matrix_engine import NASPhysicsStorage, RealityMatrix, PhysicsSimulationState
    PHYSICS_MATRIX_AVAILABLE = True
except ImportError:
    PHYSICS_MATRIX_AVAILABLE = False
    logger.warning("Physics matrix engine not available")


class IMVAMatrixSimulationPipe:
    """
    Pipes IMVA execution through dual (A & B) matrix/lattice simulations
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # IMVA process
        self.imva_process = None
        self.imva_running = False

        # Data queues for matrix simulations
        self.matrix_a_queue = Queue()
        self.matrix_b_queue = Queue()

        # Matrix simulation threads
        self.matrix_a_thread = None
        self.matrix_b_thread = None
        self.matrix_a_running = False
        self.matrix_b_running = False

        # Physics matrix storage (if available)
        self.physics_storage = None
        if PHYSICS_MATRIX_AVAILABLE:
            nas_config = {
                'host': '<NAS_PRIMARY_IP>',
                'user': 'backupadm',
                'base_path': '/volume1/simulations/physics/imva'
            }
            try:
                self.physics_storage = NASPhysicsStorage(nas_config)
                self.logger.info("✅ Physics matrix storage initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Physics storage not available: {e}")

        # Simulation state
        self.matrix_a_state = None
        self.matrix_b_state = None
        self.simulation_start_time = None

    def start_imva(self):
        """Start IMVA as subprocess"""
        imva_script = self.project_root / "scripts" / "python" / "ironman_virtual_assistant.py"

        if not imva_script.exists():
            self.logger.error(f"❌ IMVA script not found: {imva_script}")
            return False

        try:
            self.logger.info("🚀 Starting IMVA process...")
            self.imva_process = subprocess.Popen(
                [sys.executable, str(imva_script), "--start"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1  # Line buffered
            )
            self.imva_running = True
            self.logger.info(f"✅ IMVA started (PID: {self.imva_process.pid})")
            return True
        except Exception as e:
            self.logger.error(f"❌ Failed to start IMVA: {e}")
            return False

    def _parse_imva_output(self, line: str) -> Optional[Dict[str, Any]]:
        """Parse IMVA output into data structure for matrix simulation"""
        try:
            # Extract relevant data from IMVA output
            data = {
                'timestamp': datetime.now().isoformat(),
                'raw_line': line.strip(),
                'source': 'imva'
            }

            # Try to extract structured data (position, state, etc.)
            if 'position' in line.lower() or 'x:' in line.lower():
                # Extract position data
                import re
                coords = re.findall(r'[xy]:\s*(\d+)', line.lower())
                if len(coords) >= 2:
                    data['position'] = {'x': int(coords[0]), 'y': int(coords[1])}

            if 'model' in line.lower() or 'mark' in line.lower():
                # Extract model information
                import re
                model_match = re.search(r'(Mark [IVX]+|ULTRON)', line, re.IGNORECASE)
                if model_match:
                    data['model'] = model_match.group(1)

            if 'lightsaber' in line.lower() or 'fight' in line.lower():
                data['combat_state'] = True

            return data
        except Exception as e:
            self.logger.debug(f"Error parsing IMVA output: {e}")
            return None

    def _matrix_a_simulation(self):
        """Matrix A simulation thread (parallel execution)"""
        self.logger.info("🔷 Matrix A simulation started")
        self.matrix_a_running = True

        # Initialize Matrix A
        matrix_a = RealityMatrix(
            matrix_id=f"imva_matrix_a_{int(time.time())}",
            physics_domain="virtual_assistant_dynamics",
            experiment_type="position_trajectory_analysis",
            control_parameters={'source': 'imva', 'matrix_type': 'A'},
            simulation_states=[],
            comparison_metrics={},
            statistical_results={}
        )

        state_counter = 0
        while self.matrix_a_running:
            try:
                # Get data from queue (non-blocking)
                try:
                    data = self.matrix_a_queue.get(timeout=1.0)

                    # Create simulation state
                    state = PhysicsSimulationState(
                        simulation_id=f"state_{state_counter}",
                        reality_id=matrix_a.matrix_id,
                        physics_domain=matrix_a.physics_domain,
                        time_step=0.033,  # ~30 FPS
                        current_time=state_counter * 0.033,
                        grid_data=data.get('position', {}),
                        observables={
                            'x': data.get('position', {}).get('x', 0),
                            'y': data.get('position', {}).get('y', 0),
                            'combat_state': data.get('combat_state', False)
                        },
                        metadata=data,
                        created_at=datetime.now()
                    )

                    matrix_a.simulation_states.append(state)
                    state_counter += 1

                    # Store state if physics storage available
                    if self.physics_storage and state_counter % 10 == 0:
                        try:
                            # Store every 10th state for performance
                            pass  # Storage would go here
                        except:
                            pass

                except:
                    # Queue timeout, continue
                    pass

                time.sleep(0.01)  # Small delay

            except Exception as e:
                self.logger.error(f"Error in Matrix A simulation: {e}")
                time.sleep(1)

        self.matrix_a_state = matrix_a
        self.logger.info(f"🔷 Matrix A simulation completed ({len(matrix_a.simulation_states)} states)")

    def _matrix_b_simulation(self):
        """Matrix B simulation thread (parallel execution)"""
        self.logger.info("🔶 Matrix B simulation started")
        self.matrix_b_running = True

        # Initialize Matrix B
        matrix_b = RealityMatrix(
            matrix_id=f"imva_matrix_b_{int(time.time())}",
            physics_domain="virtual_assistant_interaction",
            experiment_type="combat_dynamics_analysis",
            control_parameters={'source': 'imva', 'matrix_type': 'B'},
            simulation_states=[],
            comparison_metrics={},
            statistical_results={}
        )

        state_counter = 0
        while self.matrix_b_running:
            try:
                # Get data from queue (non-blocking)
                try:
                    data = self.matrix_b_queue.get(timeout=1.0)

                    # Create simulation state (different focus than Matrix A)
                    state = PhysicsSimulationState(
                        simulation_id=f"state_{state_counter}",
                        reality_id=matrix_b.matrix_id,
                        physics_domain=matrix_b.physics_domain,
                        time_step=0.033,
                        current_time=state_counter * 0.033,
                        grid_data=data.get('combat_state', False),
                        observables={
                            'combat_active': data.get('combat_state', False),
                            'model': data.get('model', 'Unknown'),
                            'timestamp': data.get('timestamp', '')
                        },
                        metadata=data,
                        created_at=datetime.now()
                    )

                    matrix_b.simulation_states.append(state)
                    state_counter += 1

                except:
                    # Queue timeout, continue
                    pass

                time.sleep(0.01)  # Small delay

            except Exception as e:
                self.logger.error(f"Error in Matrix B simulation: {e}")
                time.sleep(1)

        self.matrix_b_state = matrix_b
        self.logger.info(f"🔶 Matrix B simulation completed ({len(matrix_b.simulation_states)} states)")

    def _read_imva_output(self):
        """Read IMVA stdout and feed into matrix queues"""
        if not self.imva_process:
            return

        try:
            while self.imva_running and self.imva_process.poll() is None:
                line = self.imva_process.stdout.readline()
                if line:
                    # Parse and distribute to both matrices
                    data = self._parse_imva_output(line)
                    if data:
                        # Send to both Matrix A and Matrix B (parallel distribution)
                        self.matrix_a_queue.put(data)
                        self.matrix_b_queue.put(data)
                else:
                    time.sleep(0.1)
        except Exception as e:
            self.logger.error(f"Error reading IMVA output: {e}")

    def start(self):
        """Start the full pipeline: IMVA → Matrix A & B"""
        self.logger.info("=" * 70)
        self.logger.info("🚀 Starting IMVA → Matrix A & B Simulation Pipeline")
        self.logger.info("=" * 70)

        # Start Matrix simulations FIRST (parallel threads)
        self.matrix_a_thread = threading.Thread(target=self._matrix_a_simulation, daemon=True)
        self.matrix_b_thread = threading.Thread(target=self._matrix_b_simulation, daemon=True)
        self.matrix_a_thread.start()
        self.matrix_b_thread.start()

        # Start IMVA
        if not self.start_imva():
            self.stop()
            return False

        # Start reading IMVA output
        output_thread = threading.Thread(target=self._read_imva_output, daemon=True)
        output_thread.start()

        self.simulation_start_time = datetime.now()
        self.logger.info("✅ Pipeline started - IMVA → Matrix A & B (parallel)")
        self.logger.info("   Matrix A: Position trajectory analysis")
        self.logger.info("   Matrix B: Combat dynamics analysis")

        return True

    def stop(self):
        """Stop the pipeline"""
        self.logger.info("🛑 Stopping IMVA Matrix Simulation Pipeline...")

        # Stop IMVA
        self.imva_running = False
        if self.imva_process:
            try:
                self.imva_process.terminate()
                self.imva_process.wait(timeout=5)
            except:
                try:
                    self.imva_process.kill()
                except:
                    pass

        # Stop matrix simulations
        self.matrix_a_running = False
        self.matrix_b_running = False

        # Wait for threads
        if self.matrix_a_thread:
            self.matrix_a_thread.join(timeout=2)
        if self.matrix_b_thread:
            self.matrix_b_thread.join(timeout=2)

        # Report results
        if self.matrix_a_state:
            self.logger.info(f"📊 Matrix A: {len(self.matrix_a_state.simulation_states)} states collected")
        if self.matrix_b_state:
            self.logger.info(f"📊 Matrix B: {len(self.matrix_b_state.simulation_states)} states collected")

        self.logger.info("✅ Pipeline stopped")

    def run(self):
        """Run the pipeline (blocking)"""
        try:
            if self.start():
                # Keep running until interrupted
                while self.imva_running:
                    time.sleep(1)
                    # Check if IMVA process is still alive
                    if self.imva_process and self.imva_process.poll() is not None:
                        self.logger.info("IMVA process ended")
                        break
            else:
                self.logger.error("Failed to start pipeline")
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.stop()


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="IMVA Matrix Simulation Pipe - Dual A & B Matrix Simulation")
        parser.add_argument("--project-root", type=str, help="Project root directory")

        args = parser.parse_args()

        if args.project_root:
            project_root = Path(args.project_root)
        else:
            project_root = Path(__file__).parent.parent.parent

        pipe = IMVAMatrixSimulationPipe(project_root)
        pipe.run()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()