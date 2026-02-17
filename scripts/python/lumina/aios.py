#!/usr/bin/env python3
"""
AIOS - AI Operating System

Complete integration of all Lumina components into a unified AI Operating System.

Connects all the dots:
- Lumina Peak (Gateway)
- Lumina Library (Jedi Archives)
- Hybrid Reality (Inference)
- Simple Reality (Interface)
- Reality Layer Zero (Foundation)
- PEGL (Logic/Physics Transformation)
- @syphon => @pipe => @peak <=> @reality (Flow)
- AOS Core (Spatial Graph, Quantum State Machine, HID Layer)
- Docker Foundation (Infrastructure)
- Core Principles (Tool Agnosticism)

Tags: #AIOS #AI_OPERATING_SYSTEM #INTEGRATION #COMPLETE @JARVIS @LUMINA
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

logger = get_logger("AIOS")


class AIOS:
    """
    AIOS - AI Operating System

    Complete integration of all Lumina components into a unified system.

    Architecture:
    1. Entry Layer: Lumina Peak (Gateway)
    2. Knowledge Layer: Library, Digest
    3. Inference Layer: Hybrid Reality, Simple Reality, Layer Zero
    4. Transformation Layer: PEGL, Flow (@syphon => @pipe)
    5. AOS Core: Spatial Graph, Quantum State Machine, HID Layer
    6. Foundation: Reality Layer Zero
    7. Infrastructure: Docker microservices
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize AIOS - AI Operating System.

        Args:
            config: Optional configuration
        """
        self.config = config or {}
        logger.info("🚀 Initializing AIOS - AI Operating System...")
        logger.info("   Connecting all the dots...")

        # Initialize all components
        self._initialize_entry_layer()
        self._initialize_knowledge_layer()
        self._initialize_inference_layer()
        self._initialize_transformation_layer()
        self._initialize_aos_core()
        self._initialize_foundation()
        self._initialize_ai_connection()
        self._initialize_homelab()
        self._initialize_simulators()
        self._initialize_ab_testing()
        self._initialize_quantum_entanglement()
        self._initialize_storytelling()
        self._initialize_production_systems()
        self._initialize_kernel()
        self._initialize_voice_profile_system()

        logger.info("✅ AIOS initialized - All dots connected!")

    def _initialize_entry_layer(self):
        """Initialize Entry Layer: Lumina Peak"""
        try:
            from .peak import LuminaPeak
            self.peak = LuminaPeak()
            logger.info("✅ Entry Layer: Lumina Peak initialized")
        except Exception as e:
            logger.warning(f"Entry Layer not fully available: {e}")
            self.peak = None

    def _initialize_knowledge_layer(self):
        """Initialize Knowledge Layer: Library, Digest"""
        # Access through Peak
        if self.peak:
            self.library = self.peak.digest  # Jedi Archives
            self.digest = self.peak.digest
            logger.info("✅ Knowledge Layer: Library (Jedi Archives) initialized")
        else:
            try:
                from .digest import LuminaDigest
                self.library = LuminaDigest()
                self.digest = self.library
                logger.info("✅ Knowledge Layer: Library (standalone) initialized")
            except Exception as e:
                logger.warning(f"Knowledge Layer not available: {e}")
                self.library = None
                self.digest = None

    def _initialize_inference_layer(self):
        """Initialize Inference Layer: Reality systems"""
        # Access through Peak
        if self.peak:
            self.reality = self.peak.reality  # Hybrid Reality
            self.simple = self.peak.simple  # Simple Reality
            logger.info("✅ Inference Layer: Reality systems initialized")
        else:
            try:
                from .hybrid_reality import HybridRealityInference
                from .simple_reality import SimpleReality
                self.reality = HybridRealityInference()
                self.simple = SimpleReality()
                logger.info("✅ Inference Layer: Reality systems (standalone) initialized")
            except Exception as e:
                logger.warning(f"Inference Layer not fully available: {e}")
                self.reality = None
                self.simple = None

        # Reality Layer Zero (Foundation)
        try:
            from .reality_layer_zero import RealityLayerZero
            self.layer_zero = RealityLayerZero("aios_foundation")
            logger.info("✅ Inference Layer: Reality Layer Zero initialized")
        except Exception as e:
            logger.warning(f"Reality Layer Zero not available: {e}")
            self.layer_zero = None

    def _initialize_transformation_layer(self):
        """Initialize Transformation Layer: PEGL, Flow"""
        # PEGL
        try:
            from .pegl import PEGL
            self.pegl = PEGL()
            logger.info("✅ Transformation Layer: PEGL initialized")
        except Exception as e:
            logger.warning(f"PEGL not available: {e}")
            self.pegl = None

        # Flow: @syphon => @pipe
        try:
            from .syphon import Syphon
            from .pipe import Pipe
            self.syphon = Syphon()
            self.pipe = Pipe()
            logger.info("✅ Transformation Layer: Flow (@syphon => @pipe) initialized")
        except Exception as e:
            logger.warning(f"Flow not available: {e}")
            self.syphon = None
            self.pipe = None

    def _initialize_aos_core(self):
        """Initialize AOS Core: Spatial Graph, Quantum State Machine, HID Layer"""
        # Access through Peak
        if self.peak:
            self.spatial_graph = self.peak.spatial_graph
            self.quantum_states = self.peak.quantum_states
            self.hid_layer = self.peak.hid_layer
            logger.info("✅ AOS Core: Spatial Graph, Quantum States, HID Layer initialized")
        else:
            try:
                from aos import SpatialGraphEngine, QuantumStateMachine, HIDAbstractionLayer
                self.spatial_graph = SpatialGraphEngine()
                self.quantum_states = QuantumStateMachine()
                self.hid_layer = HIDAbstractionLayer()
                logger.info("✅ AOS Core: Components (standalone) initialized")
            except Exception as e:
                logger.warning(f"AOS Core not fully available: {e}")
                self.spatial_graph = None
                self.quantum_states = None
                self.hid_layer = None

    def _initialize_foundation(self):
        """Initialize Foundation: Reality Layer Zero"""
        # Foundation is already initialized in inference layer
        self.foundation = self.layer_zero
        if self.foundation:
            logger.info("✅ Foundation: Reality Layer Zero ready")

    def _initialize_ai_connection(self):
        """Initialize AI Connection Layer"""
        try:
            from .ai_connection import AIConnectionManager
            self.ai_connection = AIConnectionManager()
            logger.info("✅ AI Connection Layer initialized")
        except Exception as e:
            logger.warning(f"AI Connection Layer not available: {e}")
            self.ai_connection = None

    def _initialize_homelab(self):
        """Initialize Homelab Integration"""
        try:
            from .homelab_integration import HomelabIntegration
            self.homelab = HomelabIntegration()
            logger.info("✅ Homelab Integration initialized")
        except Exception as e:
            logger.warning(f"Homelab Integration not available: {e}")
            self.homelab = None

        # Simulators
        self.simulators = None

        # A/B Testing & Curve Grading
        self.ab_testing = None
        self.curve_grading = None

        # Quantum Entanglement
        self.quantum_entanglement = None
        self.curve_grading = None

        # Quantum Entanglement
        self.quantum_entanglement = None

    def _initialize_simulators(self):
        """Initialize Simulators (WOPR, Matrix, Animatrix)"""
        try:
            from .simulator_orchestrator import SimulatorOrchestrator
            self.simulators = SimulatorOrchestrator()
            logger.info("✅ Simulators (WOPR, Matrix, Animatrix) initialized")
        except Exception as e:
            logger.warning(f"Simulators not available: {e}")
            self.simulators = None

    def _initialize_ab_testing(self):
        """Initialize A/B Testing and Curve Grading"""
        try:
            from .ab_testing import ABTestManager
            from .curve_grading import ProgressiveCurveGrading
            self.ab_testing = ABTestManager()
            self.curve_grading = ProgressiveCurveGrading()
            logger.info("✅ A/B Testing & Curve Grading initialized")
        except Exception as e:
            logger.warning(f"A/B Testing not available: {e}")
            self.ab_testing = None
            self.curve_grading = None

    def _initialize_quantum_entanglement(self):
        """Initialize Quantum Entanglement Simulator"""
        try:
            from .quantum_entanglement import QuantumEntanglementSimulator
            self.quantum_entanglement = QuantumEntanglementSimulator()
            logger.info("✅ Quantum Entanglement Simulator initialized")
        except Exception as e:
            logger.warning(f"Quantum Entanglement not available: {e}")
            self.quantum_entanglement = None

    def _initialize_storytelling(self):
        """Initialize Storytelling Engine"""
        try:
            from .storytelling_engine import StorytellingEngine
            self.storytelling = StorytellingEngine()
            logger.info("✅ Storytelling Engine initialized")
        except Exception as e:
            logger.warning(f"Storytelling Engine not available: {e}")
            self.storytelling = None

    def _initialize_production_systems(self):
        """Initialize Production Systems (Dynamic Scaling, Volt-Kernel)"""
        try:
            from .dynamic_scaling import DynamicScalingModule
            self.dynamic_scaling = DynamicScalingModule()
            logger.info("✅ Dynamic Scaling Module initialized")
        except Exception as e:
            logger.warning(f"Dynamic Scaling not available: {e}")
            self.dynamic_scaling = None

        try:
            from .volt_kernel import VoltKernel
            self.volt_kernel = VoltKernel()
            logger.info("✅ Volt-Kernel initialized")
        except Exception as e:
            logger.warning(f"Volt-Kernel not available: {e}")
            self.volt_kernel = None

        try:
            from .production_activation import ProductionActivation
            self.production_activation = ProductionActivation()
            logger.info("✅ Production Activation System initialized")
        except Exception as e:
            logger.warning(f"Production Activation not available: {e}")
            self.production_activation = None

    def _initialize_voice_profile_system(self):
        """Initialize Voice Profile Library System (@AIO)"""
        try:
            from voice_profile_library_system import VoiceProfileLibrarySystem
            from voice_filter_system import VoiceFilterSystem

            self.voice_profile_library = VoiceProfileLibrarySystem(project_root=project_root)
            logger.info("✅ Voice Profile Library System (@AIO) initialized")

            # Voice filter system will be created per-session
            self.voice_filter_system = None
            logger.info("   Voice filtering available - create per session")
        except Exception as e:
            logger.warning(f"Voice Profile System not available: {e}")
            self.voice_profile_library = None
            self.voice_filter_system = None

    def _initialize_kernel(self):
        """Initialize AIOS Kernel (Operating System)"""
        try:
            # Import kernel integration
            import sys
            from pathlib import Path
            kernel_path = Path(__file__).parent.parent / "aios" / "kernel"
            if str(kernel_path) not in sys.path:
                sys.path.insert(0, str(kernel_path))

            from aios_kernel_integration import AIOSKernelIntegration

            self.kernel = AIOSKernelIntegration()
            logger.info("✅ AIOS Kernel (Operating System) initialized")
        except Exception as e:
            logger.warning(f"AIOS Kernel not fully available: {e}")
            self.kernel = None

    def _initialize_ab_testing(self):
        """Initialize A/B Testing and Curve Grading"""
        try:
            from .ab_testing import ABTestManager
            from .curve_grading import ProgressiveCurveGrading
            self.ab_testing = ABTestManager()
            self.curve_grading = ProgressiveCurveGrading()
            logger.info("✅ A/B Testing & Curve Grading initialized")
        except Exception as e:
            logger.warning(f"A/B Testing not available: {e}")
            self.ab_testing = None
            self.curve_grading = None

    def _initialize_quantum_entanglement(self):
        """Initialize Quantum Entanglement Simulator"""
        try:
            from .quantum_entanglement import QuantumEntanglementSimulator
            self.quantum_entanglement = QuantumEntanglementSimulator()
            logger.info("✅ Quantum Entanglement Simulator initialized")
        except Exception as e:
            logger.warning(f"Quantum Entanglement not available: {e}")
            self.quantum_entanglement = None

    def infer(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Execute inference through AI connection layer.

        Args:
            query: Query to infer
            **kwargs: Additional parameters

        Returns:
            Inference result
        """
        if self.ai_connection:
            return self.ai_connection.infer(query, **kwargs)
        elif self.reality:
            return self.reality.infer(query, maintain_balance=True)
        else:
            return {'error': 'No inference available'}

    def execute(
        self,
        query: str,
        use_flow: bool = True,
        use_pegl: bool = False
    ) -> Dict[str, Any]:
        """
        Execute query through AIOS.

        Args:
            query: Query to execute
            use_flow: Use @syphon => @pipe => @peak flow
            use_pegl: Use PEGL transformation

        Returns:
            Execution result
        """
        logger.info(f"🚀 Executing query through AIOS: {query}")

        result = {
            'query': query,
            'steps': [],
            'result': None
        }

        # Step 1: Flow (if enabled)
        if use_flow and self.syphon and self.pipe:
            logger.info("Step 1: Flow (@syphon => @pipe)")
            syphon_results = self.syphon.search(query, "scripts/python/lumina")
            processed = self.pipe.process(syphon_results)
            result['steps'].append({
                'step': 'flow',
                'syphon_matches': syphon_results.get('match_count', 0),
                'processed': processed.get('processed', False)
            })

        # Step 2: PEGL Transformation (if enabled)
        if use_pegl and self.pegl:
            logger.info("Step 2: PEGL Transformation")
            patterns = self.pegl.extract_patterns(query)
            result['steps'].append({
                'step': 'pegl',
                'patterns_extracted': patterns.get('count', 0)
            })

        # Step 3: Knowledge (Library)
        if self.library:
            logger.info("Step 3: Knowledge (Library - Jedi Archives)")
            knowledge = self.library.knowledge(query)
            result['steps'].append({
                'step': 'knowledge',
                'found': 'error' not in knowledge
            })

        # Step 4: Inference (Reality or AI Connection)
        if self.reality:
            logger.info("Step 4: Inference (Hybrid Reality)")
            inference = self.reality.infer(query, maintain_balance=True)
            result['steps'].append({
                'step': 'inference',
                'layer': inference.get('layer', 'unknown')
            })
            result['result'] = inference
        elif self.ai_connection:
            logger.info("Step 4: Inference (AI Connection)")
            ai_result = self.ai_connection.infer(query)
            result['steps'].append({
                'step': 'ai_inference',
                'source': ai_result.get('source', 'unknown')
            })
            result['result'] = ai_result

        # Step 5: Simple Interface (if needed)
        if self.simple and not result['result']:
            logger.info("Step 5: Simple Interface")
            simple_result = self.simple.infer(query)
            result['result'] = simple_result

        logger.info("✅ AIOS execution complete")
        return result

    def create_voice_filter(self, user_id: str = "user", session_id: Optional[str] = None):
        """
        Create a voice filter system for a session

        @AIO: AIOS-integrated voice filtering

        Args:
            user_id: User ID
            session_id: Optional session ID

        Returns:
            VoiceFilterSystem instance
        """
        if self.voice_profile_library is None:
            logger.warning("Voice Profile Library not available")
            return None

        try:
            from voice_filter_system import VoiceFilterSystem
            filter_system = VoiceFilterSystem(
                user_id=user_id,
                project_root=project_root,
                session_id=session_id
            )
            self.voice_filter_system = filter_system
            logger.info(f"✅ Voice filter created for session: {session_id or 'default'}")
            return filter_system
        except Exception as e:
            logger.error(f"Failed to create voice filter: {e}")
            return None

    def get_status(self) -> Dict[str, Any]:
        """Get AIOS status"""
        return {
            'initialized': True,
            'entry_layer': {
                'peak': self.peak is not None
            },
            'knowledge_layer': {
                'library': self.library is not None,
                'digest': self.digest is not None
            },
            'inference_layer': {
                'reality': self.reality is not None,
                'simple': self.simple is not None,
                'layer_zero': self.layer_zero is not None
            },
            'transformation_layer': {
                'pegl': self.pegl is not None,
                'syphon': self.syphon is not None,
                'pipe': self.pipe is not None
            },
            'aos_core': {
                'spatial_graph': self.spatial_graph is not None,
                'quantum_states': self.quantum_states is not None,
                'hid_layer': self.hid_layer is not None
            },
            'foundation': {
                'layer_zero': self.foundation is not None
            },
            'infrastructure': {
                'docker': 'Available (external)',
                'api_gateway': 'Available (external)'
            },
            'ai_connection': {
                'available': self.ai_connection is not None,
                'services': self.ai_connection.get_available_services() if self.ai_connection else []
            },
            'homelab': {
                'available': self.homelab is not None,
                'services': self.homelab.get_available_services() if self.homelab else [],
                'status': self.homelab.get_status() if self.homelab else {}
            },
            'simulators': {
                'available': self.simulators is not None,
                'wopr': self.simulators.wopr is not None if self.simulators else False,
                'matrix': self.simulators.matrix is not None if self.simulators else False,
                'animatrix': self.simulators.animatrix is not None if self.simulators else False,
                'status': self.simulators.get_status() if self.simulators else {}
            },
            'ab_testing': {
                'available': self.ab_testing is not None,
                'curve_grading': self.curve_grading is not None
            },
            'quantum_entanglement': {
                'available': self.quantum_entanglement is not None
            },
            'storytelling': {
                'available': self.storytelling is not None,
                'patterns': len(self.storytelling.patterns) if self.storytelling else 0,
            },
            'voice_profile_system': {
                'available': self.voice_profile_library is not None,
                'profiles_count': len(self.voice_profile_library.voice_profiles) if self.voice_profile_library else 0,
                'sound_profiles_count': len(self.voice_profile_library.sound_profiles) if self.voice_profile_library else 0,
                'active_filter': self.voice_filter_system is not None,
                'feedback_cycles': len(self.storytelling.feedback_history) if self.storytelling else 0
            },
            'production': {
                'dynamic_scaling': {
                    'available': self.dynamic_scaling is not None,
                    'current_scale': self.dynamic_scaling.current_scale if self.dynamic_scaling else 1.0
                },
                'volt_kernel': {
                    'available': self.volt_kernel is not None,
                    'hardware': self.volt_kernel.get_kernel_status()['hardware'] if self.volt_kernel else {}
                },
                'production_activation': {
                    'available': self.production_activation is not None
                }
            }
        }


def main():
    try:
        """Example usage - AIOS in action"""
        print("=" * 80)
        print("🚀 AIOS - AI Operating System")
        print("   All dots connected, all systems integrated")
        print("=" * 80)
        print()

        # Initialize AIOS
        aios = AIOS()

        # Get status
        print("AIOS STATUS:")
        print("-" * 80)
        status = aios.get_status()
        for layer, components in status.items():
            if layer != 'initialized':
                print(f"\n{layer.upper().replace('_', ' ')}:")
                for component, available in components.items():
                    print(f"  {component}: {'✅' if available else '❌'}")
        print()

        # Execute query
        print("EXECUTING QUERY:")
        print("-" * 80)
        result = aios.execute("balance", use_flow=True, use_pegl=True)
        print(f"Query: {result['query']}")
        print(f"Steps: {len(result['steps'])}")
        for step in result['steps']:
            print(f"  - {step['step']}: {step}")
        if result['result']:
            print(f"Result: Available")
        print()

        print("=" * 80)
        print("🚀 AIOS - All dots connected!")
        print("=" * 80)


    except Exception as e:
        self.logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()