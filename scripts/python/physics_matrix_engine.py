#!/usr/bin/env python3
"""
Physics Matrix Engine
@WOPR Computational Physics Simulation | Multi-Reality Scientific Computing

Advanced physics simulation engine with NAS-backed storage and proxy caching
for massive computational physics workloads and reality matrix comparisons.
"""

import sys
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import json
import hashlib
import threading
import queue
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("physics_matrix_engine")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

try:
    import paramiko
    import numpy as np
    PARAMIKO_AVAILABLE = True
    NUMPY_AVAILABLE = True
except ImportError:
    PARAMIKO_AVAILABLE = False
    NUMPY_AVAILABLE = False

@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class PhysicsSimulationState:
    """Complete physics simulation state with metadata"""
    simulation_id: str
    reality_id: str
    physics_domain: str
    time_step: float
    current_time: float
    grid_data: Any  # numpy array or similar
    observables: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    checksum: str = ""
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RealityMatrix:
    """A complete reality simulation matrix"""
    matrix_id: str
    physics_domain: str
    experiment_type: str
    control_parameters: Dict[str, Any]
    simulation_states: List[PhysicsSimulationState] = field(default_factory=list)
    comparison_metrics: Dict[str, List[float]] = field(default_factory=dict)
    statistical_results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

class NASPhysicsStorage:
    """
    NAS-backed physics data storage with intelligent caching
    """

    def __init__(self, nas_config: Dict[str, Any]):
        self.host = nas_config.get('host', '<NAS_PRIMARY_IP>')
        self.user = nas_config.get('user', 'backupadm')
        self.base_path = nas_config.get('base_path', '/volume1/simulations/physics')
        self.timeout = nas_config.get('timeout', 30)

        # Load NAS credentials from Azure Key Vault
        self.password = None
        try:
            from nas_azure_vault_integration import NASAzureVaultIntegration
            vault_integration = NASAzureVaultIntegration(nas_ip=self.host)
            credentials = vault_integration.get_nas_credentials()
            if credentials and credentials.get("password"):
                self.password = credentials["password"]
        except Exception as e:
            print(f"⚠️  Could not load NAS credentials: {e}")

        # Local cache for performance
        self.local_cache_dir = Path('data/cache/physics')
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)

        # Connection pooling
        self.ssh_clients = queue.Queue(maxsize=5)
        self._initialize_ssh_pool()

    def _initialize_ssh_pool(self):
        """Initialize SSH connection pool"""
        if not PARAMIKO_AVAILABLE:
            return

        for _ in range(3):  # Start with 3 connections
            try:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if self.password:
                    client.connect(
                        hostname=self.host,
                        port=22,
                        username=self.user,
                        password=self.password,
                        timeout=self.timeout,
                        allow_agent=False,      # Disable SSH agent (prevents publickey attempts)
                        look_for_keys=False     # Don't look for SSH keys (password-only auth)
                    )
                else:
                    # Fallback: try without password (may use SSH keys if available)
                    client.connect(
                        hostname=self.host,
                        username=self.user,
                        timeout=self.timeout,
                        allow_agent=False,
                        look_for_keys=False
                    )
                self.ssh_clients.put(client)
            except Exception as e:
                print(f"Failed to create SSH connection: {e}")

    def _get_ssh_client(self):
        """Get SSH client from pool"""
        try:
            return self.ssh_clients.get(timeout=5)
        except queue.Empty:
            # Create new connection if pool is empty
            if PARAMIKO_AVAILABLE:
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if self.password:
                    client.connect(
                        hostname=self.host,
                        port=22,
                        username=self.user,
                        password=self.password,
                        timeout=self.timeout,
                        allow_agent=False,      # Disable SSH agent (prevents publickey attempts)
                        look_for_keys=False     # Don't look for SSH keys (password-only auth)
                    )
                else:
                    # Fallback: try without password (may use SSH keys if available)
                    client.connect(
                        hostname=self.host,
                        username=self.user,
                        timeout=self.timeout,
                        allow_agent=False,
                        look_for_keys=False
                    )
                return client
            return None

    def _return_ssh_client(self, client):
        """Return SSH client to pool"""
        if client:
            try:
                self.ssh_clients.put(client, timeout=1)
            except queue.Full:
                client.close()

    def store_simulation_state(self, state: PhysicsSimulationState) -> bool:
        """
        Store physics simulation state with tiered caching
        """
        try:
            # Generate unique identifier
            state_hash = hashlib.md5(f"{state.simulation_id}_{state.reality_id}".encode()).hexdigest()

            # Local cache storage (L1/L2)
            local_metadata = {
                'simulation_id': state.simulation_id,
                'reality_id': state.reality_id,
                'physics_domain': state.physics_domain,
                'time_step': state.time_step,
                'current_time': state.current_time,
                'observables': state.observables,
                'metadata': state.metadata,
                'checksum': state.checksum,
                'created_at': state.created_at.isoformat()
            }

            metadata_file = self.local_cache_dir / f"{state_hash}.json"
            with open(metadata_file, 'w') as f:
                json.dump(local_metadata, f, indent=2)

            # Store grid data if available
            if hasattr(state, 'grid_data') and state.grid_data is not None:
                if NUMPY_AVAILABLE and isinstance(state.grid_data, np.ndarray):
                    data_file = self.local_cache_dir / f"{state_hash}.npy"
                    np.save(data_file, state.grid_data)

            # NAS storage (L3) - asynchronous
            threading.Thread(
                target=self._async_nas_store,
                args=(state, state_hash),
                daemon=True
            ).start()

            return True

        except Exception as e:
            print(f"Failed to store simulation state: {e}")
            return False

    def _async_nas_store(self, state: PhysicsSimulationState, state_hash: str):
        """Asynchronous NAS storage"""
        client = self._get_ssh_client()
        if not client:
            return

        try:
            # Create directory structure
            reality_path = f"{self.base_path}/{state.reality_id}"
            client.exec_command(f"mkdir -p {reality_path}")

            # Store metadata
            metadata_json = json.dumps({
                'simulation_id': state.simulation_id,
                'physics_domain': state.physics_domain,
                'time_step': state.time_step,
                'current_time': state.current_time,
                'observables': state.observables,
                'metadata': state.metadata,
                'checksum': state.checksum,
                'created_at': state.created_at.isoformat()
            }, indent=2)

            # Upload metadata (simplified - would need actual file transfer)
            stdin, stdout, stderr = client.exec_command(
                f"cat > {reality_path}/{state_hash}.json << 'EOF'\n{metadata_json}\nEOF"
            )

        except Exception as e:
            print(f"NAS storage failed: {e}")
        finally:
            self._return_ssh_client(client)

    def retrieve_simulation_state(self, simulation_id: str, reality_id: str) -> Optional[PhysicsSimulationState]:
        """
        Retrieve simulation state with cache hierarchy
        """
        state_hash = hashlib.md5(f"{simulation_id}_{reality_id}".encode()).hexdigest()

        # Try local cache first
        metadata_file = self.local_cache_dir / f"{state_hash}.json"
        if metadata_file.exists():
            try:
                with open(metadata_file, 'r') as f:
                    data = json.load(f)

                state = PhysicsSimulationState(
                    simulation_id=data['simulation_id'],
                    reality_id=data['reality_id'],
                    physics_domain=data['physics_domain'],
                    time_step=data['time_step'],
                    current_time=data['current_time'],
                    grid_data=None,  # Would load from .npy file
                    observables=data.get('observables', {}),
                    metadata=data.get('metadata', {}),
                    checksum=data.get('checksum', ''),
                    created_at=datetime.fromisoformat(data['created_at'])
                )

                # Load grid data if available
                data_file = self.local_cache_dir / f"{state_hash}.npy"
                if data_file.exists() and NUMPY_AVAILABLE:
                    state.grid_data = np.load(data_file)

                return state

            except Exception as e:
                print(f"Local cache retrieval failed: {e}")

        # Try NAS retrieval
        return self._nas_retrieve(simulation_id, reality_id)

    def _nas_retrieve(self, simulation_id: str, reality_id: str) -> Optional[PhysicsSimulationState]:
        """Retrieve from NAS storage"""
        client = self._get_ssh_client()
        if not client:
            return None

        try:
            state_hash = hashlib.md5(f"{simulation_id}_{reality_id}".encode()).hexdigest()
            reality_path = f"{self.base_path}/{reality_id}"
            metadata_file = f"{reality_path}/{state_hash}.json"

            # Check if file exists
            stdin, stdout, stderr = client.exec_command(f"test -f {metadata_file} && echo exists")
            if stdout.read().decode().strip() != "exists":
                return None

            # Download metadata (simplified)
            stdin, stdout, stderr = client.exec_command(f"cat {metadata_file}")
            metadata_json = stdout.read().decode()

            data = json.loads(metadata_json)

            return PhysicsSimulationState(
                simulation_id=data['simulation_id'],
                reality_id=data['reality_id'],
                physics_domain=data['physics_domain'],
                time_step=data['time_step'],
                current_time=data['current_time'],
                grid_data=None,  # Would need separate download
                observables=data.get('observables', {}),
                metadata=data.get('metadata', {}),
                checksum=data.get('checksum', ''),
                created_at=datetime.fromisoformat(data['created_at'])
            )

        except Exception as e:
            print(f"NAS retrieval failed: {e}")
            return None
        finally:
            self._return_ssh_client(client)

class PhysicsMatrixEngine:
    """
    Core physics matrix engine for multi-reality simulations
    """

    def __init__(self, config_path: Optional[str] = None):
        self.config = self._load_config(config_path)
        self.nas_storage = NASPhysicsStorage(self.config.get('nas_physics_storage', {}))
        self.active_matrices: Dict[str, RealityMatrix] = {}
        self.physics_engines = self._initialize_physics_engines()

        print("🧮 Physics Matrix Engine initialized")

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration"""
        if not config_path:
            config_path = script_dir.parent / "config" / "physics_simulation_config.yaml"

        try:
            import yaml
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception:
            # Return default config
            return {
                'nas_physics_storage': {
                    'host': '<NAS_PRIMARY_IP>',
                    'user': 'backupadm',
                    'base_path': '/volume1/simulations/physics'
                }
            }

    def _initialize_physics_engines(self) -> Dict[str, Any]:
        """Initialize available physics engines"""
        return {
            'fluid_dynamics': {
                'capabilities': ['navier_stokes', 'turbulence', 'multiphase'],
                'typical_grid_size': (1000, 1000, 100),
                'memory_per_cell': 64  # bytes
            },
            'molecular_dynamics': {
                'capabilities': ['molecular_mechanics', 'quantum_effects'],
                'typical_particles': 100000,
                'memory_per_particle': 256
            },
            'quantum_mechanics': {
                'capabilities': ['density_functional_theory', 'wave_functions'],
                'typical_grid_size': (100, 100, 100),
                'memory_per_cell': 1024
            },
            'electromagnetic': {
                'capabilities': ['maxwell_equations', 'wave_propagation'],
                'typical_grid_size': (500, 500, 500),
                'memory_per_cell': 128
            },
            'thermodynamics': {
                'capabilities': ['chemical_kinetics', 'heat_transfer'],
                'typical_species': 50,
                'memory_per_species': 64
            }
        }

    def create_reality_matrix(self, matrix_id: str, physics_domain: str,
                            experiment_type: str, control_params: Dict[str, Any]) -> Optional[RealityMatrix]:
        """
        Create a new reality matrix for physics simulation
        """
        if physics_domain not in self.physics_engines:
            print(f"Unsupported physics domain: {physics_domain}")
            return None

        matrix = RealityMatrix(
            matrix_id=matrix_id,
            physics_domain=physics_domain,
            experiment_type=experiment_type,
            control_parameters=control_params
        )

        self.active_matrices[matrix_id] = matrix
        print(f"✅ Created reality matrix: {matrix_id} ({physics_domain})")

        return matrix

    def run_physics_simulation(self, matrix_id: str, simulation_config: Dict[str, Any]) -> bool:
        """
        Run physics simulation within reality matrix
        """
        if matrix_id not in self.active_matrices:
            print(f"Matrix not found: {matrix_id}")
            return False

        matrix = self.active_matrices[matrix_id]
        print(f"🔬 Running {matrix.physics_domain} simulation in matrix: {matrix_id}")

        # Initialize simulation state
        initial_state = self._create_simulation_state(matrix, simulation_config)

        # Simulation parameters
        time_step = simulation_config.get('time_step', 0.01)
        total_time = simulation_config.get('total_time', 1.0)
        current_time = 0.0

        # Main simulation loop
        while current_time < total_time:
            # Physics computation
            new_state = self._compute_physics_step(initial_state, time_step)

            # Store state
            self.nas_storage.store_simulation_state(new_state)

            # Update matrix
            matrix.simulation_states.append(new_state)

            # Update observables
            self._update_observables(matrix, new_state)

            current_time += time_step
            initial_state = new_state

        # Run statistical analysis
        self._run_matrix_statistics(matrix)

        print(f"✅ Physics simulation completed for matrix: {matrix_id}")
        return True

    def _create_simulation_state(self, matrix: RealityMatrix, config: Dict[str, Any]) -> PhysicsSimulationState:
        """Create initial simulation state"""
        engine_config = self.physics_engines[matrix.physics_domain]

        # Initialize grid data based on physics domain
        if NUMPY_AVAILABLE:
            if matrix.physics_domain == 'fluid_dynamics':
                grid_shape = config.get('grid_shape', (100, 100, 10))
                grid_data = np.random.rand(*grid_shape, 3) * 0.1  # velocity components
            elif matrix.physics_domain == 'quantum_mechanics':
                grid_shape = config.get('grid_shape', (50, 50, 50))
                grid_data = np.random.rand(*grid_shape) + 1j * np.random.rand(*grid_shape)
                grid_data = grid_data / np.linalg.norm(grid_data)
            else:
                grid_shape = config.get('grid_shape', (100, 100))
                grid_data = np.random.rand(*grid_shape)
        else:
            grid_data = None

        return PhysicsSimulationState(
            simulation_id=f"{matrix.matrix_id}_{int(time.time())}",
            reality_id=matrix.matrix_id,
            physics_domain=matrix.physics_domain,
            time_step=config.get('time_step', 0.01),
            current_time=0.0,
            grid_data=grid_data,
            metadata={
                'experiment_type': matrix.experiment_type,
                'control_parameters': matrix.control_parameters,
                'grid_shape': config.get('grid_shape', (100, 100))
            }
        )

    def _compute_physics_step(self, state: PhysicsSimulationState, time_step: float) -> PhysicsSimulationState:
        """Compute next physics state (simplified)"""
        new_state = PhysicsSimulationState(
            simulation_id=state.simulation_id,
            reality_id=state.reality_id,
            physics_domain=state.physics_domain,
            time_step=time_step,
            current_time=state.current_time + time_step,
            grid_data=state.grid_data,
            observables=state.observables.copy(),
            metadata=state.metadata.copy()
        )

        # Simplified physics computation
        if NUMPY_AVAILABLE and state.grid_data is not None:
            if state.physics_domain == 'fluid_dynamics':
                # Simple advection-diffusion
                diffusion = 0.01
                noise = np.random.normal(0, 0.01, state.grid_data.shape)
                new_state.grid_data = state.grid_data + diffusion * noise

            elif state.physics_domain == 'quantum_mechanics':
                # Simple wave function evolution
                phase_shift = np.exp(-1j * time_step)
                new_state.grid_data = state.grid_data * phase_shift

        # Update observables
        if NUMPY_AVAILABLE and new_state.grid_data is not None:
            new_state.observables.update({
                'mean_amplitude': float(np.mean(np.abs(new_state.grid_data))),
                'max_amplitude': float(np.max(np.abs(new_state.grid_data))),
                'total_energy': float(np.sum(new_state.grid_data**2)),
                'entropy': float(-np.sum(new_state.grid_data * np.log(np.abs(new_state.grid_data) + 1e-10)))
            })

        return new_state

    def _update_observables(self, matrix: RealityMatrix, state: PhysicsSimulationState):
        """Update matrix observables"""
        for key, value in state.observables.items():
            if key not in matrix.comparison_metrics:
                matrix.comparison_metrics[key] = []
            matrix.comparison_metrics[key].append(value)

    def _run_matrix_statistics(self, matrix: RealityMatrix):
        """Run statistical analysis on matrix results"""
        stats = {}

        for metric, values in matrix.comparison_metrics.items():
            if len(values) > 1:
                if NUMPY_AVAILABLE:
                    stats[f'{metric}_mean'] = float(np.mean(values))
                    stats[f'{metric}_std'] = float(np.std(values))
                    stats[f'{metric}_trend'] = float(np.polyfit(range(len(values)), values, 1)[0])
                else:
                    stats[f'{metric}_mean'] = sum(values) / len(values)
                    stats[f'{metric}_count'] = len(values)

        matrix.statistical_results = stats

    def compare_matrices(self, matrix_ids: List[str]) -> Dict[str, Any]:
        """
        Compare multiple reality matrices statistically
        """
        matrices = []
        for mid in matrix_ids:
            if mid in self.active_matrices:
                matrices.append(self.active_matrices[mid])

        if len(matrices) < 2:
            return {"error": "Need at least 2 matrices to compare"}

        comparison = {
            'matrices_compared': len(matrices),
            'physics_domains': list(set(m.physics_domain for m in matrices)),
            'experiment_types': list(set(m.experiment_type for m in matrices)),
            'comparison_results': {},
            'timestamp': datetime.now().isoformat()
        }

        # Compare common metrics
        common_metrics = set()
        for matrix in matrices:
            common_metrics.update(matrix.comparison_metrics.keys())

        for metric in common_metrics:
            metric_comparison = {}
            for matrix in matrices:
                if metric in matrix.comparison_metrics:
                    values = matrix.comparison_metrics[metric]
                    if values:
                        metric_comparison[matrix.matrix_id] = {
                            'final_value': values[-1],
                            'mean': sum(values) / len(values),
                            'count': len(values)
                        }

            if len(metric_comparison) >= 2:
                comparison['comparison_results'][metric] = metric_comparison

        return comparison

def main():
    try:
        """Main physics matrix interface"""
        print("🧮 Physics Matrix Engine - @WOPR Reality Simulation")
        print("=" * 60)

        engine = PhysicsMatrixEngine()

        # Create multiple reality matrices
        matrices = [
            ('baseline_fluid', 'fluid_dynamics', 'control_experiment'),
            ('experimental_fluid', 'fluid_dynamics', 'intervention_test'),
            ('quantum_reality', 'quantum_mechanics', 'quantum_simulation')
        ]

        created_matrices = []
        for matrix_id, physics_domain, experiment_type in matrices:
            matrix = engine.create_reality_matrix(
                matrix_id,
                physics_domain,
                experiment_type,
                {'random_seed': 42, 'precision': 'double'}
            )

            if matrix:
                created_matrices.append(matrix_id)

                # Run simulation
                config = {
                    'time_step': 0.01,
                    'total_time': 0.1,
                    'grid_shape': (50, 50) if physics_domain != 'quantum_mechanics' else (30, 30, 30)
                }

                engine.run_physics_simulation(matrix_id, config)

        # Compare matrices
        if len(created_matrices) >= 2:
            comparison = engine.compare_matrices(created_matrices)
            print("\n📊 Matrix Comparison Results:")
            print(json.dumps(comparison, indent=2))

        print("\n✅ Physics matrix operations completed")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()