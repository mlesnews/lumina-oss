"""Tests for the health aggregator."""

import pytest

from lumina.aios.health import HealthAggregator, HealthReport


def test_weights_must_sum_to_one():
    with pytest.raises(ValueError, match="sum to 1.0"):
        HealthAggregator(dimensions={"a": 0.3, "b": 0.3})


def test_basic_scoring():
    agg = HealthAggregator(dimensions={"a": 0.5, "b": 0.5})
    agg.score("a", 1.0, "perfect")
    agg.score("b", 0.5, "half")
    report = agg.evaluate()
    assert report.score_pct == pytest.approx(75.0)


def test_missing_dimension_scores_zero():
    agg = HealthAggregator(dimensions={"a": 0.5, "b": 0.5})
    agg.score("a", 1.0)
    report = agg.evaluate()
    assert report.score_pct == pytest.approx(50.0)


def test_unknown_dimension_raises():
    agg = HealthAggregator(dimensions={"a": 1.0})
    with pytest.raises(KeyError, match="Unknown dimension"):
        agg.score("b", 0.5)


def test_threshold_labels():
    agg = HealthAggregator(
        dimensions={"health": 1.0},
        thresholds={"BAD": 30, "OK": 60, "GOOD": 80},
    )

    agg.score("health", 0.2)
    report = agg.evaluate()
    assert report.label == "BAD"

    agg.score("health", 0.7)
    report = agg.evaluate()
    assert report.label == "OK"

    agg.score("health", 0.9)
    report = agg.evaluate()
    assert report.label == "GOOD"


def test_score_clamped():
    agg = HealthAggregator(dimensions={"x": 1.0})
    agg.score("x", 1.5)  # Over 1.0
    report = agg.evaluate()
    assert report.score_pct == pytest.approx(100.0)

    agg.score("x", -0.5)  # Under 0.0
    report = agg.evaluate()
    assert report.score_pct == pytest.approx(0.0)


def test_to_dict():
    agg = HealthAggregator(dimensions={"uptime": 1.0})
    agg.score("uptime", 0.95, "99.5%")
    report = agg.evaluate()
    d = report.to_dict()
    assert "score_pct" in d
    assert "dimensions" in d
    assert len(d["dimensions"]) == 1


def test_trend():
    agg = HealthAggregator(dimensions={"x": 1.0})
    assert agg.get_trend() == "insufficient_data"

    for val in [0.5, 0.6, 0.7, 0.8, 0.9]:
        agg.score("x", val)
        agg.evaluate()
    assert agg.get_trend() == "improving"


def test_recommendation_mentions_weak():
    agg = HealthAggregator(dimensions={"strong": 0.5, "weak": 0.5})
    agg.score("strong", 0.9)
    agg.score("weak", 0.1)
    report = agg.evaluate()
    assert "weak" in report.recommendation.lower()


def test_runnable_module():
    """Verify the __main__ block runs without error."""
    import subprocess
    result = subprocess.run(
        ["python3", "-m", "lumina.aios.health"],
        capture_output=True, text=True, timeout=10,
        cwd="/home/mlesn/lumina-oss",
    )
    assert result.returncode == 0
    assert "Health:" in result.stdout
