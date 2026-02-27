"""Tests for the gatekeeper quality gate."""

from lumina.workflow.gatekeeper import Gatekeeper, GateColor, AuditResult


def test_all_green_when_no_findings():
    gk = Gatekeeper()
    gk.add_check("empty", GateColor.RED, lambda: [])
    result = gk.audit()
    assert result.status == GateColor.GREEN
    assert result.can_proceed is True


def test_red_blocks():
    gk = Gatekeeper()
    gk.add_check("syntax", GateColor.RED, lambda: ["SyntaxError on line 1"])
    result = gk.audit()
    assert result.status == GateColor.RED
    assert result.can_proceed is False
    assert result.has_errors is True


def test_orange_warning():
    gk = Gatekeeper()
    gk.add_check("todos", GateColor.ORANGE, lambda: ["TODO on line 5"])
    result = gk.audit()
    assert result.status == GateColor.ORANGE
    assert result.has_warnings is True
    assert result.can_proceed is False


def test_precedence_red_over_orange():
    gk = Gatekeeper()
    gk.add_check("warnings", GateColor.ORANGE, lambda: ["warning"])
    gk.add_check("errors", GateColor.RED, lambda: ["error"])
    result = gk.audit()
    assert result.status == GateColor.RED


def test_cyan_needs_commit():
    gk = Gatekeeper()
    gk.add_check("git", GateColor.CYAN, lambda: ["Modified: main.py"])
    result = gk.audit()
    assert result.needs_commit is True


def test_blue_suggestions():
    gk = Gatekeeper()
    gk.add_check("arch", GateColor.BLUE, lambda: ["Consider refactoring"])
    result = gk.audit()
    assert result.status == GateColor.BLUE
    assert result.can_proceed is False  # BLUE is above GREY threshold


def test_grey_can_proceed():
    gk = Gatekeeper()
    gk.add_check("git_clean", GateColor.GREY, lambda: ["All committed"])
    result = gk.audit()
    assert result.status == GateColor.GREY
    assert result.can_proceed is True


def test_checker_exception_becomes_red():
    gk = Gatekeeper()
    gk.add_check("broken", GateColor.BLUE, lambda: [][0])  # IndexError
    result = gk.audit()
    assert result.status == GateColor.RED
    assert "Check failed" in result.findings[0].message


def test_summary():
    gk = Gatekeeper()
    gk.add_check("a", GateColor.RED, lambda: ["err1", "err2"])
    gk.add_check("b", GateColor.ORANGE, lambda: ["warn1"])
    result = gk.audit()
    summary = result.summary()
    assert "RED" in summary


def test_multiple_checks():
    gk = Gatekeeper()
    gk.add_check("c1", GateColor.GREEN, lambda: [])
    gk.add_check("c2", GateColor.GREEN, lambda: [])
    gk.add_check("c3", GateColor.GREEN, lambda: [])
    result = gk.audit()
    assert result.checks_run == 3
    assert result.status == GateColor.GREEN
