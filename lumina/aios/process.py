"""
Molecule process model — trigger + action + stopper + exit.

A Molecule is the fundamental unit of work in the AIOS. It encapsulates:
- Trigger: condition that starts execution
- Action: the work to perform
- Stopper: condition that halts execution early
- Exit: cleanup and result packaging

Pattern extracted from production: molecule_evaluator.py

Example:
    def my_trigger(ctx):
        return ctx.get("price") > 100

    def my_action(ctx):
        return {"order": "buy", "price": ctx["price"]}

    mol = Molecule(
        name="price_breakout",
        trigger=my_trigger,
        action=my_action,
    )
    runner = MoleculeRunner()
    result = runner.run(mol, {"price": 105})
    print(result.success, result.output)
"""

import logging
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)


class MoleculeState(Enum):
    """Lifecycle states of a molecule."""
    IDLE = "idle"
    TRIGGERED = "triggered"
    RUNNING = "running"
    STOPPED = "stopped"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class MoleculeResult:
    """Result from running a molecule."""
    molecule_name: str
    success: bool
    state: MoleculeState
    output: Any = None
    execution_time: float = 0.0
    stopped_by: Optional[str] = None
    error: Optional[str] = None


@dataclass
class Molecule:
    """
    A unit of work with trigger-action-stopper-exit lifecycle.

    Args:
        name: Unique identifier for this molecule.
        trigger: Callable(context) -> bool. Returns True to start execution.
        action: Callable(context) -> Any. The work to perform.
        stopper: Optional callable(context) -> bool. Returns True to halt.
        exit_handler: Optional callable(result, context) -> Any. Cleanup.
        metadata: Arbitrary metadata dict.
    """
    name: str
    trigger: Callable[[Dict], bool]
    action: Callable[[Dict], Any]
    stopper: Optional[Callable[[Dict], bool]] = None
    exit_handler: Optional[Callable[[Any, Dict], Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MoleculeRunner:
    """
    Executes molecules through their lifecycle.

    Args:
        max_concurrent: Maximum molecules running simultaneously.
    """

    def __init__(self, max_concurrent: int = 10):
        self._max_concurrent = max_concurrent
        self._history: List[MoleculeResult] = []

    def run(self, molecule: Molecule, context: Dict[str, Any]) -> MoleculeResult:
        """
        Execute a molecule through its full lifecycle.

        1. Check trigger condition
        2. If triggered, run action
        3. Check stopper during execution
        4. Run exit handler if present

        Args:
            molecule: The molecule to execute.
            context: Execution context passed to all callables.

        Returns:
            MoleculeResult with execution details.
        """
        start = time.monotonic()

        # Phase 1: Trigger
        try:
            triggered = molecule.trigger(context)
        except Exception as exc:
            result = MoleculeResult(
                molecule_name=molecule.name,
                success=False,
                state=MoleculeState.FAILED,
                error=f"Trigger error: {exc}",
                execution_time=time.monotonic() - start,
            )
            self._history.append(result)
            return result

        if not triggered:
            result = MoleculeResult(
                molecule_name=molecule.name,
                success=True,
                state=MoleculeState.IDLE,
                execution_time=time.monotonic() - start,
            )
            self._history.append(result)
            return result

        # Phase 2: Stopper pre-check
        if molecule.stopper:
            try:
                if molecule.stopper(context):
                    result = MoleculeResult(
                        molecule_name=molecule.name,
                        success=True,
                        state=MoleculeState.STOPPED,
                        stopped_by="pre_check",
                        execution_time=time.monotonic() - start,
                    )
                    self._history.append(result)
                    return result
            except Exception as exc:
                logger.warning("Stopper error for %s: %s", molecule.name, exc)

        # Phase 3: Action
        try:
            output = molecule.action(context)
            state = MoleculeState.COMPLETED
        except Exception as exc:
            result = MoleculeResult(
                molecule_name=molecule.name,
                success=False,
                state=MoleculeState.FAILED,
                error=f"Action error: {exc}",
                execution_time=time.monotonic() - start,
            )
            self._history.append(result)
            return result

        # Phase 4: Exit handler
        if molecule.exit_handler:
            try:
                output = molecule.exit_handler(output, context)
            except Exception as exc:
                logger.warning("Exit handler error for %s: %s", molecule.name, exc)

        result = MoleculeResult(
            molecule_name=molecule.name,
            success=True,
            state=state,
            output=output,
            execution_time=time.monotonic() - start,
        )
        self._history.append(result)
        return result

    def evaluate_all(
        self,
        molecules: List[Molecule],
        context: Dict[str, Any],
    ) -> List[MoleculeResult]:
        """Run all molecules against the same context. Returns list of results."""
        return [self.run(mol, context) for mol in molecules]

    @property
    def history(self) -> List[MoleculeResult]:
        """Recent execution history."""
        return list(self._history)
