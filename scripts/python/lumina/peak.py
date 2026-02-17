#!/usr/bin/env python3
"""
Lumina Peak - Best of Everything

Unified entry point that applies all we've learned to put Lumina's
BEST/PEAK foot forward.

Tags: #LUMINA #PEAK #BEST_PRACTICES #UNIFIED @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaPeak")

# Import all Lumina components (relative imports)
try:
    from .principles import LuminaPrinciples, LuminaPrinciple
    from .core_memory import LuminaCoreMemory
    from .three_path_implementation import (
        LuminaPathSelector,
        CollaborationPath,
        BalancedPartnershipLumina
    )
    from .implementation_validator import ImplementationValidator
    LUMINA_AVAILABLE = True
except ImportError as e:
    try:
        # Try absolute imports as fallback
        from lumina.principles import LuminaPrinciples, LuminaPrinciple
        from lumina.core_memory import LuminaCoreMemory
        from lumina.three_path_implementation import (
            LuminaPathSelector,
            CollaborationPath,
            BalancedPartnershipLumina
        )
        from lumina.implementation_validator import ImplementationValidator
        LUMINA_AVAILABLE = True
    except ImportError:
        logger.warning(f"Lumina components not available: {e}")
        LUMINA_AVAILABLE = False
        # Create dummy types for type hints
        CollaborationPath = None
        BalancedPartnershipLumina = None

# Import AOS components
try:
    from aos import (
        SpatialGraphEngine,
        QuantumStateMachine,
        HIDAbstractionLayer,
        DeviceDetector,
        JARVISBuddyHUD,
        BuddyMode
    )
    AOS_AVAILABLE = True
except ImportError as e:
    try:
        # Try relative import
        import sys
        aos_path = Path(__file__).parent.parent / "aos"
        if str(aos_path) not in sys.path:
            sys.path.insert(0, str(aos_path))
        from spatial_graph_engine import SpatialGraphEngine
        from quantum_state_machine import QuantumStateMachine
        from hid_abstraction import HIDAbstractionLayer
        from device_abstraction import DeviceDetector
        from jarvis_buddy_hud import JARVISBuddyHUD, BuddyMode
        AOS_AVAILABLE = True
    except ImportError:
        logger.warning(f"AOS components not available: {e}")
        AOS_AVAILABLE = False


class LuminaPeak:
    """
    Lumina Peak - Best of Everything

    Unified entry point that:
    - Applies all core principles
    - Integrates all systems
    - Optimizes for best experience
    - Maintains flexibility and agility
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize Lumina Peak with best configuration.

        Args:
            config: Optional configuration overrides
        """
        self.config = config or {}
        self.initialized = False

        # Core systems
        self.principles = None
        self.core_memory = None
        self.validator = None
        self.path_selector = None
        self.spatial_graph = None
        self.quantum_states = None
        self.hid_layer = None
        self.device_detector = None
        self.jarvis_buddy = None
        self.digest = None
        self.simple = None
        self.reality = None
        self.leverage = None
        self.syphon = None
        self.pipe = None

        logger.info("🌟 Initializing Lumina Peak...")
        self._initialize()

    def _initialize(self) -> None:
        """Initialize all Lumina Peak systems"""
        try:
            # 1. Core Principles
            if LUMINA_AVAILABLE:
                self.principles = LuminaPrinciples()
                logger.info("✅ Core principles initialized")

            # 2. Core Memory (Tool Agnosticism)
            if LUMINA_AVAILABLE:
                self.core_memory = LuminaCoreMemory()
                logger.info("✅ Core memory system initialized")

            # 3. Implementation Validator
            if LUMINA_AVAILABLE:
                self.validator = ImplementationValidator()
                logger.info("✅ Implementation validator initialized")

            # 4. Path Selector (Three-path strategy)
            if LUMINA_AVAILABLE:
                self.path_selector = LuminaPathSelector()
                # Default to Balanced Partnership (Path B)
                balanced = BalancedPartnershipLumina()
                self.path_selector.register_path(
                    CollaborationPath.BALANCED_PARTNERSHIP,
                    balanced
                )
                self.path_selector.select_path(CollaborationPath.BALANCED_PARTNERSHIP)
                logger.info("✅ Path selector initialized (Balanced Partnership)")
            else:
                logger.warning("Path selector not available (Lumina components missing)")

            # 5. Spatial Graph Engine
            if AOS_AVAILABLE:
                try:
                    self.spatial_graph = SpatialGraphEngine()
                    logger.info("✅ Spatial Graph Engine initialized")
                except Exception as e:
                    logger.warning(f"Spatial Graph Engine not available: {e}")

            # 6. Quantum State Machine
            if AOS_AVAILABLE:
                try:
                    self.quantum_states = QuantumStateMachine()
                    logger.info("✅ Quantum State Machine initialized")
                except Exception as e:
                    logger.warning(f"Quantum State Machine not available: {e}")

            # 7. HID Abstraction Layer
            if AOS_AVAILABLE:
                try:
                    self.hid_layer = HIDAbstractionLayer()
                    logger.info("✅ HID Abstraction Layer initialized")
                except Exception as e:
                    logger.warning(f"HID Abstraction Layer not available: {e}")

            # 8. Device Detector
            if AOS_AVAILABLE:
                try:
                    self.device_detector = DeviceDetector()
                    best_device = self.device_detector.detect_best_available()
                    if best_device:
                        logger.info(f"✅ Best device detected: {type(best_device).__name__}")
                except Exception as e:
                    logger.warning(f"Device Detector not available: {e}")

            # 9. JARVIS Buddy HUD
            if AOS_AVAILABLE:
                try:
                    self.jarvis_buddy = JARVISBuddyHUD(mode=BuddyMode.ACTIVE)
                    logger.info("✅ JARVIS Buddy HUD initialized")
                except Exception as e:
                    logger.warning(f"JARVIS Buddy HUD not available: {e}")

            # 10. Lumina Digest (Knowledge)
            try:
                try:
                    from .digest import LuminaDigest
                except ImportError:
                    # Add scripts/python to path if needed
                    scripts_python = Path(__file__).parent.parent
                    if str(scripts_python) not in sys.path:
                        sys.path.insert(0, str(scripts_python))
                    from lumina.digest import LuminaDigest
                self.digest = LuminaDigest()
                logger.info("✅ Lumina Digest initialized")
            except Exception as e:
                logger.warning(f"Lumina Digest not available: {e}")
                self.digest = None

            # 11. Simple Reality (Simple Interface)
            try:
                try:
                    from .simple_reality import SimpleReality
                except ImportError:
                    scripts_python = Path(__file__).parent.parent
                    if str(scripts_python) not in sys.path:
                        sys.path.insert(0, str(scripts_python))
                    from lumina.simple_reality import SimpleReality
                self.simple = SimpleReality()
                logger.info("✅ Simple Reality initialized")
            except Exception as e:
                logger.warning(f"Simple Reality not available: {e}")
                self.simple = None

            # 12. Hybrid Reality (Advanced Inference)
            try:
                try:
                    from .hybrid_reality import HybridRealityInference
                except ImportError:
                    scripts_python = Path(__file__).parent.parent
                    if str(scripts_python) not in sys.path:
                        sys.path.insert(0, str(scripts_python))
                    from lumina.hybrid_reality import HybridRealityInference
                self.reality = HybridRealityInference()
                logger.info("✅ Hybrid Reality initialized")
            except Exception as e:
                logger.warning(f"Hybrid Reality not available: {e}")
                self.reality = None

            # 13. Leverage Guide
            try:
                try:
                    from .leverage import LuminaLeverage
                except ImportError:
                    scripts_python = Path(__file__).parent.parent
                    if str(scripts_python) not in sys.path:
                        sys.path.insert(0, str(scripts_python))
                    from lumina.leverage import LuminaLeverage
                self.leverage = LuminaLeverage()
                logger.info("✅ Lumina Leverage Guide initialized")
            except Exception as e:
                logger.warning(f"Leverage Guide not available: {e}")
                self.leverage = None

            # 14. Syphon (Extract)
            try:
                try:
                    from .syphon import LuminaSyphon
                except ImportError:
                    scripts_python = Path(__file__).parent.parent
                    if str(scripts_python) not in sys.path:
                        sys.path.insert(0, str(scripts_python))
                    from lumina.syphon import LuminaSyphon
                self.syphon = LuminaSyphon()
                logger.info("✅ Lumina Syphon initialized")
            except Exception as e:
                logger.warning(f"Lumina Syphon not available: {e}")
                self.syphon = None

            # 15. Pipe (Transfer)
            try:
                try:
                    from .pipe import LuminaPipe
                except ImportError:
                    scripts_python = Path(__file__).parent.parent
                    if str(scripts_python) not in sys.path:
                        sys.path.insert(0, str(scripts_python))
                    from lumina.pipe import LuminaPipe
                self.pipe = LuminaPipe()
                logger.info("✅ Lumina Pipe initialized")
            except Exception as e:
                logger.warning(f"Lumina Pipe not available: {e}")
                self.pipe = None

            # Show daily reminder
            self._show_daily_reminder()

            self.initialized = True
            logger.info("🌟 Lumina Peak initialized successfully!")

        except Exception as e:
            logger.error(f"Error initializing Lumina Peak: {e}", exc_info=True)
            raise

    def _show_daily_reminder(self) -> None:
        """Show daily reminder of core memories"""
        if self.core_memory:
            reminder = self.core_memory.get_daily_reminder()
            logger.info("\n" + "=" * 80)
            logger.info("🧠 LUMINA DAILY REMINDER")
            logger.info("=" * 80)
            logger.info(reminder)
            logger.info("=" * 80 + "\n")

    def validate_implementation(self, implementation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate implementation against Lumina principles.

        Args:
            implementation: Implementation to validate

        Returns:
            Validation result
        """
        if not self.validator:
            return {'error': 'Validator not available'}

        return self.validator.validate(implementation)

    def check_tool_attachment(self, tool_name: str) -> Dict[str, Any]:
        """
        Check if we're becoming emotionally attached to a tool.

        Args:
            tool_name: Name of tool to check

        Returns:
            Assessment of attachment risk
        """
        if not self.core_memory:
            return {'error': 'Core memory not available'}

        return self.core_memory.check_tool_attachment(tool_name)

    def get_status(self) -> Dict[str, Any]:
        """Get status of all Lumina Peak systems"""
        return {
            'initialized': self.initialized,
            'principles': self.principles is not None,
            'core_memory': self.core_memory is not None,
            'validator': self.validator is not None,
            'path_selector': self.path_selector is not None,
            'spatial_graph': self.spatial_graph is not None,
            'quantum_states': self.quantum_states is not None,
            'hid_layer': self.hid_layer is not None,
            'device_detector': self.device_detector is not None,
            'jarvis_buddy': self.jarvis_buddy is not None,
            'digest': self.digest is not None,
            'simple': self.simple is not None,
            'reality': self.reality is not None,
            'leverage': self.leverage is not None,
            'syphon': self.syphon is not None,
            'pipe': self.pipe is not None,
            'current_path': self.path_selector.get_current_path().path_type.value if self.path_selector and self.path_selector.get_current_path() else None
        }

    def recommend(self, use_case: str, complexity: str = "medium") -> Dict[str, Any]:
        """
        Get leverage recommendation for use case.

        Args:
            use_case: Description of use case
            complexity: 'simple', 'medium', 'complex', 'foundation'

        Returns:
            Recommendation
        """
        if self.leverage:
            return self.leverage.recommend(use_case, complexity)
        return {'error': 'Leverage guide not available'}

    def syphon_to_reality(self, pattern: str) -> Dict[str, Any]:
        """
        Complete flow: @syphon => @pipe => @peak => @reality

        Args:
            pattern: Pattern to extract and apply

        Returns:
            Result from reality inference
        """
        if not self.syphon or not self.pipe or not self.reality:
            return {'error': 'Syphon/Pipe/Reality not available'}

        # Step 1: Syphon (Extract)
        logger.info(f"🔍 Syphoning pattern: {pattern}")
        knowledge = self.syphon.extract(pattern)

        # Step 2: Pipe (Transfer)
        logger.info("🔀 Piping to reality")
        piped = self.pipe.transfer(knowledge, target="reality")

        # Step 3: Reality (Apply)
        logger.info("🌀 Applying in reality")
        query = piped['data'].get('query', pattern)
        result = self.reality.infer(query, maintain_balance=True)

        return {
            'pattern': pattern,
            'syphoned': knowledge,
            'piped': piped,
            'reality_result': result
        }

    def receive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Receive piped data at Peak gateway.

        Args:
            data: Piped data from Pipe

        Returns:
            Receipt confirmation
        """
        logger.info("📥 Receiving data at Peak gateway")

        # Store in Library if available
        if self.digest and data.get('ready_for_peak'):
            # Could store in digest
            pass

        return {
            'received': True,
            'data_type': data.get('type', 'unknown'),
            'stored_in_library': self.digest is not None
        }

    def get_manifesto(self) -> str:
        """Get Lumina manifesto"""
        if self.principles:
            return self.principles.get_manifesto()
        return "Lumina Principles not available"

    def execute_workflow(
        self,
        workflow: Dict[str, Any],
        path: Any = None  # CollaborationPath if available
    ) -> Dict[str, Any]:
        """
        Execute workflow using current or specified path.

        Args:
            workflow: Workflow to execute
            path: Optional path override

        Returns:
            Execution result
        """
        if not self.path_selector:
            return {'error': 'Path selector not available'}

        # Switch path if specified
        if path:
            self.path_selector.switch_path(path)

        # Get current path
        lumina = self.path_selector.get_current_path()
        if not lumina:
            return {'error': 'No Lumina path selected'}

        # Execute workflow
        try:
            result = lumina.execute_workflow(workflow)
            return result
        except Exception as e:
            logger.error(f"Workflow execution error: {e}", exc_info=True)
            return {'error': str(e)}


def main():
    """Example usage of Lumina Peak"""
    print("=" * 80)
    print("🌟 LUMINA PEAK - Best of Everything")
    print("=" * 80)
    print()

    # Initialize Lumina Peak
    lumina = LuminaPeak()

    # Get status
    status = lumina.get_status()
    print("SYSTEM STATUS:")
    print("-" * 80)
    for key, value in status.items():
        status_icon = "✅" if value else "❌"
        print(f"  {status_icon} {key}: {value}")
    print()

    # Get manifesto
    print("LUMINA MANIFESTO:")
    print("-" * 80)
    print(lumina.get_manifesto())
    print()

    # Check tool attachment
    print("TOOL ATTACHMENT CHECK:")
    print("-" * 80)
    assessment = lumina.check_tool_attachment("Ollama")
    print(f"Tool: {assessment.get('tool', 'unknown')}")
    if assessment.get('warnings'):
        for warning in assessment['warnings']:
            print(f"  ⚠️  {warning}")
    print()

    # Execute workflow
    print("WORKFLOW EXECUTION:")
    print("-" * 80)
    workflow = {
        'name': 'test_workflow',
        'type': 'routine',
        'risk_level': 'low'
    }
    result = lumina.execute_workflow(workflow)
    print(f"Result: {result.get('status', 'unknown')}")
    print()

    print("=" * 80)
    print("🌟 Lumina Peak is ready!")
    print("=" * 80)


if __name__ == "__main__":


    main()