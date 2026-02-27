"""
AIOS Kernel — Intent processor and execution engine.

The kernel receives user intents, classifies priority, selects execution mode,
and returns structured results. This is the central dispatch loop of the AI OS.

Pattern extracted from production: aios_kernel_core.py

Example:
    kernel = AIOSKernel()
    intent = UserIntent(raw_input="deploy the trading bot")
    result = kernel.process(intent)
    print(result.success, result.response)
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class Priority(Enum):
    """Intent priority levels."""
    CRITICAL = "critical"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"
    BACKGROUND = "background"


class ExecutionMode(Enum):
    """How the kernel processes an intent."""
    AUTONOMOUS = "autonomous"       # Full auto — no human in loop
    ASSISTED = "assisted"           # AI proposes, human confirms
    MANUAL = "manual_override"      # Human drives, AI advises
    LEARNING = "learning"           # Observe only, build patterns


@dataclass
class UserIntent:
    """A request the kernel needs to process."""
    raw_input: str
    priority: Priority = Priority.NORMAL
    execution_mode: ExecutionMode = ExecutionMode.ASSISTED
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AIOSResult:
    """Structured result from kernel processing."""
    success: bool
    response: str
    execution_time: float = 0.0
    confidence: float = 0.0
    actions_taken: List[str] = field(default_factory=list)
    needs_human_review: bool = False
    learning_opportunities: List[str] = field(default_factory=list)


class AIOSKernel:
    """
    AI Operating System kernel.

    Processes intents through a pipeline:
    1. Classify priority
    2. Select execution mode
    3. Run registered handlers
    4. Return structured result

    Args:
        default_mode: Default execution mode for unclassified intents.
        handlers: Dict mapping intent keywords to handler callables.
    """

    def __init__(
        self,
        default_mode: ExecutionMode = ExecutionMode.ASSISTED,
        handlers: Optional[Dict[str, Callable]] = None,
    ):
        self.default_mode = default_mode
        self._handlers: Dict[str, Callable] = handlers or {}
        self._metrics = {
            "intents_processed": 0,
            "total_execution_time": 0.0,
            "success_count": 0,
        }

    def register_handler(self, keyword: str, handler: Callable) -> None:
        """Register a handler for intents matching a keyword."""
        self._handlers[keyword] = handler
        logger.debug("Registered handler for '%s'", keyword)

    def process(self, intent: UserIntent) -> AIOSResult:
        """
        Process a user intent through the kernel pipeline.

        Args:
            intent: The user intent to process.

        Returns:
            AIOSResult with success status, response, and metadata.
        """
        start = time.monotonic()
        self._metrics["intents_processed"] += 1

        try:
            # Find matching handler
            handler = self._match_handler(intent)

            if handler is None:
                return AIOSResult(
                    success=False,
                    response=f"No handler registered for: {intent.raw_input[:100]}",
                    execution_time=time.monotonic() - start,
                    needs_human_review=True,
                )

            # Execute handler
            response = handler(intent)
            elapsed = time.monotonic() - start

            self._metrics["success_count"] += 1
            self._metrics["total_execution_time"] += elapsed

            return AIOSResult(
                success=True,
                response=str(response),
                execution_time=elapsed,
                confidence=1.0,
                actions_taken=[f"handler:{handler.__name__}"],
                needs_human_review=(intent.execution_mode == ExecutionMode.ASSISTED),
            )

        except Exception as exc:
            elapsed = time.monotonic() - start
            logger.error("Kernel error processing intent: %s", exc)
            return AIOSResult(
                success=False,
                response=f"Error: {exc}",
                execution_time=elapsed,
                needs_human_review=True,
                learning_opportunities=[f"Handler exception: {type(exc).__name__}"],
            )

    def _match_handler(self, intent: UserIntent) -> Optional[Callable]:
        """Find the first handler whose keyword appears in the intent."""
        text = intent.raw_input.lower()
        for keyword, handler in self._handlers.items():
            if keyword.lower() in text:
                return handler
        return None

    @property
    def metrics(self) -> Dict[str, Any]:
        """Return kernel processing metrics."""
        total = self._metrics["intents_processed"]
        return {
            **self._metrics,
            "success_rate": (
                self._metrics["success_count"] / total if total > 0 else 0.0
            ),
            "avg_execution_time": (
                self._metrics["total_execution_time"] / total if total > 0 else 0.0
            ),
        }
