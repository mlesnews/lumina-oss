#!/usr/bin/env python3
"""
Universal Matrix Simulation Pipe Module
Universal module for piping ANY data source through dual A & B matrix/lattice simulations

Can be integrated with @syphon to ingest ANYTHING and pipe through matrix simulations.
Integrates with @r5d4 (R5-D4) for knowledge aggregation.

@SYPHON @R5D4 @WOPR @LUMINA @JARVIS
"""

import sys
import subprocess
import threading
import time
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Iterator, Union
from datetime import datetime
from queue import Queue
from abc import ABC, abstractmethod
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

try:
    from physics_matrix_engine import NASPhysicsStorage, RealityMatrix, PhysicsSimulationState
    PHYSICS_MATRIX_AVAILABLE = True
except (ImportError, SyntaxError) as e:
    PHYSICS_MATRIX_AVAILABLE = False

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False

logger = get_logger("UniversalMatrixSimulationPipe")


class DataSource(ABC):
    """Abstract base class for any data source"""

    @abstractmethod
    def get_data_stream(self) -> Iterator[Dict[str, Any]]:
        """Get data stream from source"""
        pass

    @abstractmethod
    def get_source_name(self) -> str:
        """Get name of data source"""
        pass


class SubprocessDataSource(DataSource):
    """Data source from subprocess output"""

    def __init__(self, command: List[str], source_name: str = "subprocess"):
        self.command = command
        self.source_name = source_name
        self.process = None

    def get_data_stream(self) -> Iterator[Dict[str, Any]]:
        """Stream data from subprocess"""
        try:
            self.process = subprocess.Popen(
                self.command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )

            while self.process.poll() is None:
                line = self.process.stdout.readline()
                if line:
                    yield {
                        'timestamp': datetime.now().isoformat(),
                        'raw_line': line.strip(),
                        'source': self.source_name
                    }
                else:
                    time.sleep(0.01)
        except Exception as e:
            logger.error(f"Error reading from subprocess: {e}")

    def get_source_name(self) -> str:
        return self.source_name

    def stop(self):
        """Stop subprocess"""
        if self.process:
            try:
                self.process.terminate()
                self.process.wait(timeout=5)
            except:
                try:
                    self.process.kill()
                except:
                    pass


class QueueDataSource(DataSource):
    """Data source from queue (for SYPHON integration)"""

    def __init__(self, queue: Queue, source_name: str = "queue"):
        self.queue = queue
        self.source_name = source_name

    def get_data_stream(self) -> Iterator[Dict[str, Any]]:
        """Stream data from queue"""
        while True:
            try:
                data = self.queue.get(timeout=1.0)
                yield {
                    'timestamp': datetime.now().isoformat(),
                    'data': data,
                    'source': self.source_name
                }
            except:
                time.sleep(0.1)

    def get_source_name(self) -> str:
        return self.source_name


class FileDataSource(DataSource):
    """Data source from file (line-by-line or JSON)"""

    def __init__(self, file_path: Path, source_name: str = "file", format: str = "line"):
        self.file_path = Path(file_path)
        self.source_name = source_name
        self.format = format  # "line" or "json"

    def get_data_stream(self) -> Iterator[Dict[str, Any]]:
        """Stream data from file"""
        if not self.file_path.exists():
            logger.warning(f"File not found: {self.file_path}")
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                if self.format == "json":
                    # Read JSON array or JSONL
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                data = json.loads(line)
                                yield {
                                    'timestamp': datetime.now().isoformat(),
                                    'data': data,
                                    'source': self.source_name
                                }
                            except json.JSONDecodeError:
                                continue
                else:
                    # Line-by-line
                    for line in f:
                        if line.strip():
                            yield {
                                'timestamp': datetime.now().isoformat(),
                                'raw_line': line.strip(),
                                'source': self.source_name
                            }
        except Exception as e:
            logger.error(f"Error reading file: {e}")

    def get_source_name(self) -> str:
        return self.source_name


class IteratorDataSource(DataSource):
    """Data source from any Python iterator"""

    def __init__(self, iterator: Iterator[Any], source_name: str = "iterator", parser: Optional[Callable] = None):
        self.iterator = iterator
        self.source_name = source_name
        self.parser = parser or (lambda x: {'data': x})

    def get_data_stream(self) -> Iterator[Dict[str, Any]]:
        """Stream data from iterator"""
        for item in self.iterator:
            parsed = self.parser(item)
            yield {
                'timestamp': datetime.now().isoformat(),
                **parsed,
                'source': self.source_name
            }

    def get_source_name(self) -> str:
        return self.source_name


class UniversalMatrixSimulationPipe:
    """
    Universal Matrix Simulation Pipe - Can pipe ANY data source through dual A & B matrix simulations

    Features:
    - Accepts any data source (subprocess, queue, file, iterator, etc.)
    - Dual parallel matrix simulations (A & B)
    - Configurable parsers for different data types
    - R5-D4 integration for knowledge aggregation
    - SYPHON integration ready
    """

    def __init__(self, project_root: Path, matrix_a_config: Optional[Dict[str, Any]] = None, 
                 matrix_b_config: Optional[Dict[str, Any]] = None, enable_r5: bool = True):
        self.project_root = project_root
        self.logger = logger

        # Matrix configurations
        self.matrix_a_config = matrix_a_config or {
            'physics_domain': 'data_trajectory_analysis',
            'experiment_type': 'trajectory_simulation',
            'focus': 'position_trajectory'
        }
        self.matrix_b_config = matrix_b_config or {
            'physics_domain': 'data_interaction_analysis',
            'experiment_type': 'interaction_simulation',
            'focus': 'interaction_dynamics'
        }

        # Data queues
        self.matrix_a_queue = Queue()
        self.matrix_b_queue = Queue()

        # Matrix simulation threads
        self.matrix_a_thread = None
        self.matrix_b_thread = None
        self.matrix_a_running = False
        self.matrix_b_running = False

        # Data source
        self.data_source: Optional[DataSource] = None
        self.data_source_thread = None
        self.running = False

        # Physics matrix storage
        self.physics_storage = None
        if PHYSICS_MATRIX_AVAILABLE:
            nas_config = {
                'host': '<NAS_PRIMARY_IP>',
                'user': 'backupadm',
                'base_path': '/volume1/simulations/universal_matrix'
            }
            try:
                self.physics_storage = NASPhysicsStorage(nas_config)
                self.logger.info("✅ Physics matrix storage initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Physics storage not available: {e}")

        # R5-D4 integration (knowledge aggregation)
        self.r5_system = None
        if enable_r5 and R5_AVAILABLE:
            try:
                self.r5_system = R5LivingContextMatrix(project_root)
                self.logger.info("✅ R5-D4 (Knowledge Matrix) integration enabled")
            except Exception as e:
                self.logger.warning(f"⚠️  R5-D4 not available: {e}")

        # Simulation state
        self.matrix_a_state = None
        self.matrix_b_state = None
        self.simulation_start_time = None

        # Data parser (customizable)
        self.data_parser: Optional[Callable[[Dict[str, Any]], Dict[str, Any]]] = None

    def set_data_parser(self, parser: Callable[[Dict[str, Any]], Dict[str, Any]]):
        """Set custom data parser function"""
        self.data_parser = parser

    def set_data_source(self, data_source: DataSource):
        """Set data source"""
        self.data_source = data_source
        self.logger.info(f"📥 Data source set: {data_source.get_source_name()}")

    def _default_parser(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Default data parser - extracts common patterns"""
        parsed = {
            'timestamp': data.get('timestamp', datetime.now().isoformat()),
            'source': data.get('source', 'unknown')
        }

        # Try to extract position data
        if 'position' in data:
            parsed['position'] = data['position']
        elif 'x' in data and 'y' in data:
            parsed['position'] = {'x': data['x'], 'y': data['y']}
        elif 'raw_line' in data:
            # Try to parse position from text
            import re
            coords = re.findall(r'[xy]:\s*(\d+)', data['raw_line'].lower())
            if len(coords) >= 2:
                parsed['position'] = {'x': int(coords[0]), 'y': int(coords[1])}

        # Extract other common fields
        for key in ['model', 'state', 'combat_state', 'action', 'event', 'status']:
            if key in data:
                parsed[key] = data[key]

        # Include raw data
        parsed['raw_data'] = data

        return parsed

    def _matrix_a_simulation(self):
        """Matrix A simulation thread (parallel execution)"""
        self.logger.info("🔷 Matrix A simulation started")
        self.matrix_a_running = True

        matrix_a = RealityMatrix(
            matrix_id=f"matrix_a_{int(time.time())}",
            physics_domain=self.matrix_a_config.get('physics_domain', 'data_trajectory_analysis'),
            experiment_type=self.matrix_a_config.get('experiment_type', 'trajectory_simulation'),
            control_parameters={
                'source': self.data_source.get_source_name() if self.data_source else 'unknown',
                'matrix_type': 'A',
                **self.matrix_a_config
            },
            simulation_states=[],
            comparison_metrics={},
            statistical_results={}
        )

        state_counter = 0
        while self.matrix_a_running:
            try:
                try:
                    data = self.matrix_a_queue.get(timeout=1.0)

                    # Parse data
                    if self.data_parser:
                        parsed = self.data_parser(data)
                    else:
                        parsed = self._default_parser(data)

                    # Create simulation state
                    state = PhysicsSimulationState(
                        simulation_id=f"state_{state_counter}",
                        reality_id=matrix_a.matrix_id,
                        physics_domain=matrix_a.physics_domain,
                        time_step=0.033,  # ~30 FPS
                        current_time=state_counter * 0.033,
                        grid_data=parsed.get('position', {}),
                        observables={
                            'x': parsed.get('position', {}).get('x', 0),
                            'y': parsed.get('position', {}).get('y', 0),
                            **{k: v for k, v in parsed.items() if k not in ['position', 'raw_data']}
                        },
                        metadata=parsed,
                        created_at=datetime.now()
                    )

                    matrix_a.simulation_states.append(state)
                    state_counter += 1

                    # Store to R5-D4 if available
                    if self.r5_system and state_counter % 10 == 0:
                        try:
                            # Aggregate knowledge to R5-D4
                            session_data = {
                                'session_id': f"matrix_a_{state_counter}",
                                'timestamp': datetime.now(),
                                'messages': [{
                                    'role': 'system',
                                    'content': f"Matrix A state: {parsed}"
                                }],
                                'patterns': [],
                                'whatif_scenarios': [],
                                'metadata': {'matrix_type': 'A', 'state_id': state.simulation_id}
                            }
                            # R5 aggregation would go here
                        except:
                            pass

                except:
                    pass

                time.sleep(0.01)

            except Exception as e:
                self.logger.error(f"Error in Matrix A simulation: {e}")
                time.sleep(1)

        self.matrix_a_state = matrix_a
        self.logger.info(f"🔷 Matrix A completed ({len(matrix_a.simulation_states)} states)")

    def _matrix_b_simulation(self):
        """Matrix B simulation thread (parallel execution)"""
        self.logger.info("🔶 Matrix B simulation started")
        self.matrix_b_running = True

        matrix_b = RealityMatrix(
            matrix_id=f"matrix_b_{int(time.time())}",
            physics_domain=self.matrix_b_config.get('physics_domain', 'data_interaction_analysis'),
            experiment_type=self.matrix_b_config.get('experiment_type', 'interaction_simulation'),
            control_parameters={
                'source': self.data_source.get_source_name() if self.data_source else 'unknown',
                'matrix_type': 'B',
                **self.matrix_b_config
            },
            simulation_states=[],
            comparison_metrics={},
            statistical_results={}
        )

        state_counter = 0
        while self.matrix_b_running:
            try:
                try:
                    data = self.matrix_b_queue.get(timeout=1.0)

                    # Parse data (different focus than Matrix A)
                    if self.data_parser:
                        parsed = self.data_parser(data)
                    else:
                        parsed = self._default_parser(data)

                    # Create simulation state (different focus)
                    state = PhysicsSimulationState(
                        simulation_id=f"state_{state_counter}",
                        reality_id=matrix_b.matrix_id,
                        physics_domain=matrix_b.physics_domain,
                        time_step=0.033,
                        current_time=state_counter * 0.033,
                        grid_data=parsed.get('state', parsed.get('combat_state', False)),
                        observables={
                            'interaction_active': parsed.get('combat_state', False),
                            'event_type': parsed.get('event', 'unknown'),
                            'status': parsed.get('status', 'unknown'),
                            **{k: v for k, v in parsed.items() if k not in ['position', 'raw_data']}
                        },
                        metadata=parsed,
                        created_at=datetime.now()
                    )

                    matrix_b.simulation_states.append(state)
                    state_counter += 1

                except:
                    pass

                time.sleep(0.01)

            except Exception as e:
                self.logger.error(f"Error in Matrix B simulation: {e}")
                time.sleep(1)

        self.matrix_b_state = matrix_b
        self.logger.info(f"🔶 Matrix B completed ({len(matrix_b.simulation_states)} states)")

    def _read_data_source(self):
        """Read from data source and feed into matrix queues"""
        if not self.data_source:
            self.logger.error("No data source set")
            return

        try:
            for data in self.data_source.get_data_stream():
                if not self.running:
                    break

                # Distribute to both matrices (parallel)
                self.matrix_a_queue.put(data)
                self.matrix_b_queue.put(data)

        except Exception as e:
            self.logger.error(f"Error reading data source: {e}")

    def start(self):
        """Start the pipeline"""
        if not self.data_source:
            self.logger.error("❌ No data source set. Use set_data_source() first.")
            return False

        self.logger.info("=" * 70)
        self.logger.info(f"🚀 Starting Universal Matrix Simulation Pipeline")
        self.logger.info(f"   Source: {self.data_source.get_source_name()}")
        self.logger.info(f"   Matrix A: {self.matrix_a_config.get('physics_domain', 'trajectory')}")
        self.logger.info(f"   Matrix B: {self.matrix_b_config.get('physics_domain', 'interaction')}")
        if self.r5_system:
            self.logger.info(f"   R5-D4: Knowledge aggregation enabled")
        self.logger.info("=" * 70)

        self.running = True

        # Start matrix simulations FIRST
        self.matrix_a_thread = threading.Thread(target=self._matrix_a_simulation, daemon=True)
        self.matrix_b_thread = threading.Thread(target=self._matrix_b_simulation, daemon=True)
        self.matrix_a_thread.start()
        self.matrix_b_thread.start()

        # Start reading data source
        self.data_source_thread = threading.Thread(target=self._read_data_source, daemon=True)
        self.data_source_thread.start()

        self.simulation_start_time = datetime.now()
        self.logger.info("✅ Pipeline started - Data → Matrix A & B (parallel)")

        return True

    def stop(self):
        """Stop the pipeline"""
        self.logger.info("🛑 Stopping Universal Matrix Simulation Pipeline...")

        self.running = False

        # Stop data source
        if isinstance(self.data_source, SubprocessDataSource):
            self.data_source.stop()

        # Stop matrix simulations
        self.matrix_a_running = False
        self.matrix_b_running = False

        # Wait for threads
        if self.matrix_a_thread:
            self.matrix_a_thread.join(timeout=2)
        if self.matrix_b_thread:
            self.matrix_b_thread.join(timeout=2)
        if self.data_source_thread:
            self.data_source_thread.join(timeout=2)

        # Report results
        if self.matrix_a_state:
            self.logger.info(f"📊 Matrix A: {len(self.matrix_a_state.simulation_states)} states")
        if self.matrix_b_state:
            self.logger.info(f"📊 Matrix B: {len(self.matrix_b_state.simulation_states)} states")

        self.logger.info("✅ Pipeline stopped")

    def run(self, duration: Optional[float] = None):
        """Run the pipeline (blocking)"""
        try:
            if self.start():
                # Run for specified duration or until interrupted
                if duration:
                    time.sleep(duration)
                else:
                    # Keep running until interrupted
                    while self.running:
                        time.sleep(1)
            else:
                self.logger.error("Failed to start pipeline")
        except KeyboardInterrupt:
            self.logger.info("Interrupted by user")
        finally:
            self.stop()


def main():
    try:
        """Main entry point - example usage"""
        import argparse

        parser = argparse.ArgumentParser(description="Universal Matrix Simulation Pipe - Pipe ANYTHING through dual A & B matrices")
        parser.add_argument("--source", type=str, help="Data source type: subprocess, file, queue")
        parser.add_argument("--source-arg", type=str, help="Source argument (command, file path, etc.)")
        parser.add_argument("--project-root", type=str, help="Project root directory")
        parser.add_argument("--duration", type=float, help="Run duration in seconds")

        args = parser.parse_args()

        if args.project_root:
            project_root = Path(args.project_root)
        else:
            project_root = Path(__file__).parent.parent.parent

        pipe = UniversalMatrixSimulationPipe(project_root, enable_r5=True)

        # Set data source based on arguments
        if args.source == "subprocess" and args.source_arg:
            import shlex
            command = shlex.split(args.source_arg)
            data_source = SubprocessDataSource(command, "subprocess")
            pipe.set_data_source(data_source)
        elif args.source == "file" and args.source_arg:
            data_source = FileDataSource(Path(args.source_arg), "file")
            pipe.set_data_source(data_source)
        else:
            parser.print_help()
            return

        pipe.run(duration=args.duration)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()