#!/usr/bin/env python3
"""
Bio Brain Interface - Biological Brain-Computer Interface

Connects human neural activity with AI systems
Direct brain-to-AI communication interface

"KIND OF A BIO BRAININTERFACE"
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("BioBrainInterface")

# Import integrations
try:
    from babel_fish_translator import BabelFishTranslator
    BABEL_AVAILABLE = True
except ImportError:
    BABEL_AVAILABLE = False

try:
    from workflow_performance_tuner import WorkflowPerformanceTuner, TuningTarget
    TUNER_AVAILABLE = True
except ImportError:
    TUNER_AVAILABLE = False



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class NeuralSignalType(Enum):
    """Types of neural signals"""
    THOUGHT = "thought"  # Cognitive thought
    INTENT = "intent"  # Intent to act
    EMOTION = "emotion"  # Emotional state
    MEMORY = "memory"  # Memory recall
    IMAGINATION = "imagination"  # Creative thought
    DECISION = "decision"  # Decision making
    QUESTION = "question"  # Question/query


class InterfaceMode(Enum):
    """Interface modes"""
    PASSIVE = "passive"  # Monitor only
    ACTIVE = "active"  # Two-way communication
    SYMBIOTIC = "symbiotic"  # Full integration
    NEURAL_LINK = "neural_link"  # Direct neural link


@dataclass
class NeuralSignal:
    """Neural signal from brain"""
    signal_id: str
    signal_type: NeuralSignalType
    timestamp: str
    intensity: float = 0.0  # 0.0 - 1.0
    frequency: float = 0.0  # Hz
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['signal_type'] = self.signal_type.value
        return data


@dataclass
class AIResponse:
    """AI response to neural signal"""
    response_id: str
    original_signal_id: str
    timestamp: str
    response_type: str
    content: str
    neural_feedback: Optional[str] = None  # Feedback for brain
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class BrainInterfaceState:
    """Brain interface state"""
    connected: bool = False
    mode: InterfaceMode = InterfaceMode.PASSIVE
    signal_count: int = 0
    response_count: int = 0
    latency_ms: float = 0.0
    bandwidth_bps: float = 0.0
    last_signal_time: Optional[str] = None
    last_response_time: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['mode'] = self.mode.value
        return data


class BioBrainInterface:
    """
    Bio Brain Interface - Biological Brain-Computer Interface

    Connects human neural activity with AI systems
    Direct brain-to-AI communication
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Bio Brain Interface"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("BioBrainInterface")

        # Interface state
        self.state = BrainInterfaceState()

        # Signal processing
        self.neural_signals: List[NeuralSignal] = []
        self.ai_responses: List[AIResponse] = []

        # Translation layer
        self.babel_fish = None
        if BABEL_AVAILABLE:
            try:
                self.babel_fish = BabelFishTranslator(project_root)
                self.babel_fish.insert_fish()  # Auto-insert for brain interface
                self.logger.info("  ✅ Babel Fish integrated for neural translation")
            except Exception as e:
                self.logger.debug(f"  Babel Fish init error: {e}")

        # Performance tuning
        self.tuner = None
        if TUNER_AVAILABLE:
            try:
                self.tuner = WorkflowPerformanceTuner(project_root)
                self.logger.info("  ✅ Performance tuner integrated")
            except Exception as e:
                self.logger.debug(f"  Tuner init error: {e}")

        # Signal handlers
        self.signal_handlers: Dict[NeuralSignalType, List[Callable]] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "bio_brain_interface"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("🧠 Bio Brain Interface initialized")
        self.logger.info("   Neural signal processing ready")
        self.logger.info("   AI response generation ready")
        self.logger.info("   Brain-to-AI communication ready")

    def connect(self, mode: InterfaceMode = InterfaceMode.ACTIVE) -> bool:
        """Connect brain interface"""
        if self.state.connected:
            self.logger.info("  ℹ️  Interface already connected")
            return True

        self.state.connected = True
        self.state.mode = mode

        self.logger.info(f"  ✅ Brain interface connected ({mode.value} mode)")
        self.logger.info("     Neural signals: Active")
        self.logger.info("     AI responses: Active")

        return True

    def disconnect(self) -> bool:
        """Disconnect brain interface"""
        if not self.state.connected:
            self.logger.info("  ℹ️  Interface not connected")
            return False

        self.state.connected = False

        self.logger.info("  ⚠️  Brain interface disconnected")

        return True

    def receive_neural_signal(self, signal_type: NeuralSignalType, content: str,
                            intensity: float = 0.5, frequency: float = 0.0) -> NeuralSignal:
        """Receive neural signal from brain"""
        if not self.state.connected:
            self.logger.warning("  ⚠️  Interface not connected")
            return None

        signal = NeuralSignal(
            signal_id=f"signal_{len(self.neural_signals) + 1}_{int(time.time())}",
            signal_type=signal_type,
            timestamp=datetime.now().isoformat(),
            intensity=intensity,
            frequency=frequency,
            content=content
        )

        self.neural_signals.append(signal)
        self.state.signal_count += 1
        self.state.last_signal_time = signal.timestamp

        self.logger.debug(f"  📡 Received neural signal: {signal_type.value} - {content[:50]}")

        # Process signal
        response = self._process_neural_signal(signal)

        return signal

    def _process_neural_signal(self, signal: NeuralSignal) -> Optional[AIResponse]:
        """Process neural signal and generate AI response"""
        start_time = time.time()

        # Translate neural signal to AI format (using Babel Fish)
        if self.babel_fish:
            translated_content = self.babel_fish.translate(
                signal.content,
                source_language="neural",
                target_language="ai"
            )
        else:
            translated_content = signal.content

        # Generate AI response based on signal type
        response_content = self._generate_ai_response(signal, translated_content)

        # Translate AI response back to neural format
        if self.babel_fish:
            neural_feedback = self.babel_fish.translate(
                response_content,
                source_language="ai",
                target_language="neural"
            )
        else:
            neural_feedback = response_content

        # Calculate latency
        latency_ms = (time.time() - start_time) * 1000
        self.state.latency_ms = latency_ms

        # Create response
        response = AIResponse(
            response_id=f"response_{len(self.ai_responses) + 1}_{int(time.time())}",
            original_signal_id=signal.signal_id,
            timestamp=datetime.now().isoformat(),
            response_type=signal.signal_type.value,
            content=response_content,
            neural_feedback=neural_feedback
        )

        self.ai_responses.append(response)
        self.state.response_count += 1
        self.state.last_response_time = response.timestamp

        self.logger.info(f"  💭 AI response generated: {latency_ms:.1f}ms latency")

        return response

    def _generate_ai_response(self, signal: NeuralSignal, translated_content: str) -> str:
        """Generate AI response based on neural signal"""
        signal_type = signal.signal_type

        if signal_type == NeuralSignalType.QUESTION:
            return f"AI Response to question: {translated_content}"
        elif signal_type == NeuralSignalType.DECISION:
            return f"AI Decision support: Analyzing {translated_content}"
        elif signal_type == NeuralSignalType.INTENT:
            return f"AI Understanding intent: {translated_content}"
        elif signal_type == NeuralSignalType.THOUGHT:
            return f"AI Processing thought: {translated_content}"
        elif signal_type == NeuralSignalType.EMOTION:
            return f"AI Emotional recognition: {translated_content}"
        else:
            return f"AI Response: {translated_content}"

    def send_neural_feedback(self, response: AIResponse) -> bool:
        """Send AI response back to brain as neural feedback"""
        if not self.state.connected:
            return False

        if response.neural_feedback:
            self.logger.info(f"  🧠 Neural feedback sent: {response.neural_feedback[:50]}")
            return True

        return False

    def register_signal_handler(self, signal_type: NeuralSignalType, handler: Callable):
        """Register handler for specific signal type"""
        if signal_type not in self.signal_handlers:
            self.signal_handlers[signal_type] = []

        self.signal_handlers[signal_type].append(handler)
        self.logger.debug(f"  ✅ Registered handler for {signal_type.value}")

    def get_interface_status(self) -> Dict[str, Any]:
        """Get interface status"""
        return {
            "state": self.state.to_dict(),
            "signals_received": len(self.neural_signals),
            "responses_generated": len(self.ai_responses),
            "babel_fish_active": self.babel_fish is not None and self.babel_fish.fish_inserted,
            "tuner_active": self.tuner is not None,
            "handlers_registered": sum(len(handlers) for handlers in self.signal_handlers.values())
        }

    def optimize_interface(self) -> Dict[str, Any]:
        """Optimize brain interface performance"""
        if not self.tuner:
            return {"error": "Performance tuner not available"}

        result = self.tuner.tune_workflow("bio_brain_interface", TuningTarget.HYBRID)

        self.logger.info(f"  ⚡ Interface optimized: {result.get('expected_improvement', 0):.1f}% improvement")

        return result

    def get_neural_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get neural signal and response history"""
        return {
            "signals": [s.to_dict() for s in self.neural_signals[-limit:]],
            "responses": [r.to_dict() for r in self.ai_responses[-limit:]],
            "total_signals": len(self.neural_signals),
            "total_responses": len(self.ai_responses)
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bio Brain Interface - Brain-Computer Interface")
    parser.add_argument("--connect", action="store_true", help="Connect brain interface")
    parser.add_argument("--disconnect", action="store_true", help="Disconnect brain interface")
    parser.add_argument("--mode", type=str, choices=["passive", "active", "symbiotic", "neural_link"],
                       default="active", help="Interface mode")
    parser.add_argument("--signal", type=str, help="Send neural signal")
    parser.add_argument("--signal-type", type=str, choices=["thought", "intent", "question", "decision"],
                       default="thought", help="Signal type")
    parser.add_argument("--status", action="store_true", help="Get interface status")
    parser.add_argument("--optimize", action="store_true", help="Optimize interface")
    parser.add_argument("--history", type=int, help="Show neural history (limit)")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    interface = BioBrainInterface()

    if args.connect:
        mode = InterfaceMode(args.mode)
        interface.connect(mode)
        if not args.json:
            print(f"\n🧠 Brain Interface Connected ({args.mode} mode)")
            print("   Neural signals: Active")
            print("   AI responses: Active")

    elif args.disconnect:
        interface.disconnect()
        if not args.json:
            print("\n🧠 Brain Interface Disconnected")

    elif args.signal:
        if not interface.state.connected:
            interface.connect(InterfaceMode(args.mode))

        signal_type = NeuralSignalType(args.signal_type)
        signal = interface.receive_neural_signal(signal_type, args.signal)

        if signal:
            response = interface._process_neural_signal(signal)
            if response:
                interface.send_neural_feedback(response)

                if args.json:
                    print(json.dumps({
                        "signal": signal.to_dict(),
                        "response": response.to_dict()
                    }, indent=2))
                else:
                    print(f"\n🧠 Neural Signal Processed")
                    print("="*60)
                    print(f"Signal: {signal.signal_type.value}")
                    print(f"Content: {signal.content}")
                    print(f"\n💭 AI Response:")
                    print(f"   {response.content}")
                    if response.neural_feedback:
                        print(f"\n🧠 Neural Feedback:")
                        print(f"   {response.neural_feedback}")

    elif args.status:
        status = interface.get_interface_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🧠 Bio Brain Interface Status")
            print("="*60)
            print(f"Connected: {'✅ Yes' if status['state']['connected'] else '❌ No'}")
            print(f"Mode: {status['state']['mode']}")
            print(f"Signals Received: {status['signals_received']}")
            print(f"Responses Generated: {status['responses_generated']}")
            print(f"Latency: {status['state']['latency_ms']:.1f}ms")
            print(f"Babel Fish: {'✅ Active' if status['babel_fish_active'] else '❌ Inactive'}")
            print(f"Tuner: {'✅ Active' if status['tuner_active'] else '❌ Inactive'}")

    elif args.optimize:
        result = interface.optimize_interface()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"\n⚡ Interface Optimization")
            print("="*60)
            if "error" not in result:
                print(f"Expected Improvement: {result.get('expected_improvement', 0):.1f}%")
                print("\nRecommendations:")
                for rec in result.get('recommendations', [])[:5]:
                    print(f"  • {rec.get('recommendation', 'N/A')}")

    elif args.history:
        history = interface.get_neural_history(args.history)
        if args.json:
            print(json.dumps(history, indent=2))
        else:
            print("\n🧠 Neural History")
            print("="*60)
            print(f"Total Signals: {history['total_signals']}")
            print(f"Total Responses: {history['total_responses']}")
            print("\nRecent Signals:")
            for signal in history['signals']:
                print(f"  {signal['timestamp']}: {signal['signal_type']} - {signal['content'][:50]}")

    else:
        parser.print_help()
        print("\n🧠 Bio Brain Interface - Direct Brain-to-AI Communication")
        print("   Connect your brain. Communicate with AI. Think. Act.")

