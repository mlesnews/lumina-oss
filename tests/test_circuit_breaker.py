"""Tests for the circuit breaker state machine."""

import tempfile
from pathlib import Path

from lumina.safety.circuit_breaker import CircuitBreaker, Level


def test_default_level_is_yellow():
    """Fail-closed: new circuit breaker starts at YELLOW, not GREEN."""
    cb = CircuitBreaker()
    assert cb.level == Level.YELLOW


def test_green_when_no_violations():
    cb = CircuitBreaker()
    level, reason = cb.check({"error_rate": 0.01, "loss_pct": 0.5})
    assert level == Level.GREEN
    assert "passed" in reason.lower()


def test_yellow_on_threshold():
    cb = CircuitBreaker()
    level, _ = cb.check({"error_rate": 0.05})
    assert level == Level.YELLOW


def test_red_on_high_errors():
    cb = CircuitBreaker()
    level, _ = cb.check({"error_rate": 0.25})
    assert level == Level.RED


def test_black_on_extreme():
    cb = CircuitBreaker()
    level, _ = cb.check({"error_rate": 0.60})
    assert level == Level.BLACK


def test_can_proceed():
    cb = CircuitBreaker()
    cb.check({"error_rate": 0.01})
    assert cb.can_proceed() is True

    cb.check({"error_rate": 0.25})
    assert cb.can_proceed() is False


def test_is_halted():
    cb = CircuitBreaker()
    cb.check({"error_rate": 0.01})
    assert cb.is_halted() is False

    cb.check({"error_rate": 0.25})
    assert cb.is_halted() is True


def test_reset():
    cb = CircuitBreaker()
    cb.check({"error_rate": 0.25})
    assert cb.level == Level.RED
    cb.reset()
    assert cb.level == Level.GREEN


def test_state_persistence():
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        state_path = Path(f.name)

    try:
        cb1 = CircuitBreaker(state_file=state_path)
        cb1.check({"error_rate": 0.25})
        assert cb1.level == Level.RED

        cb2 = CircuitBreaker(state_file=state_path)
        assert cb2.level == Level.RED
    finally:
        state_path.unlink(missing_ok=True)


def test_custom_thresholds():
    cb = CircuitBreaker(thresholds={
        Level.YELLOW: {"cpu": 70},
        Level.RED: {"cpu": 95},
    })
    level, _ = cb.check({"cpu": 80})
    assert level == Level.YELLOW

    level, _ = cb.check({"cpu": 96})
    assert level == Level.RED
