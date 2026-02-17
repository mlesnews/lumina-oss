#!/usr/bin/env python3
"""
Compare Chat Focus Diagnostic Results
Executes both diagnostic tool and test script, then compares results
Optionally runs through Syphon for pattern analysis
"""

import json
import re
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CompareChatFocus")

def parse_autohotkey_log(log_file: Path) -> Dict[str, Any]:
    try:
        """Parse AutoHotkey diagnostic log file"""
        if not log_file.exists():
            return {"error": f"Log file not found: {log_file}"}

        results = {
            "file": str(log_file),
            "steps": [],
            "focus_changes": [],
            "timing": []
        }

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        current_step = None
        for i, line in enumerate(lines):
            # Extract step information
            if "STEP" in line and ":" in line:
                step_match = re.search(r'STEP (\d+):\s*(.+)', line)
                if step_match:
                    current_step = {
                        "step": step_match.group(1),
                        "name": step_match.group(2).strip(),
                        "timestamp": None,
                        "window": None,
                        "control": None,
                        "mouse": None
                    }
                    results["steps"].append(current_step)

            # Extract timestamp
            timestamp_match = re.search(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]', line)
            if timestamp_match and current_step:
                current_step["timestamp"] = timestamp_match.group(1)

            # Extract window info
            if "Window:" in line and current_step:
                window_match = re.search(r'Window:\s*(.+)', line)
                if window_match:
                    current_step["window"] = window_match.group(1).strip()

            # Extract control info
            if "Focused Control:" in line and current_step:
                control_match = re.search(r'Focused Control:\s*(.+)', line)
                if control_match:
                    current_step["control"] = control_match.group(1).strip()

            # Extract mouse position
            if "Mouse:" in line and current_step:
                mouse_match = re.search(r'Mouse:\s*(\d+),(\d+)', line)
                if mouse_match:
                    current_step["mouse"] = f"{mouse_match.group(1)},{mouse_match.group(2)}"

        return results

    except Exception as e:
        logger.error(f"Error in parse_autohotkey_log: {e}", exc_info=True)
        raise
def parse_test_log(log_file: Path) -> Dict[str, Any]:
    try:
        """Parse test script log file"""
        if not log_file.exists():
            return {"error": f"Log file not found: {log_file}"}

        results = {
            "file": str(log_file),
            "actions": [],
            "focus_verification": []
        }

        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        for line in lines:
            # Extract action steps
            if "STEP:" in line:
                step_match = re.search(r'STEP:\s*(\w+)\s*\|\s*(.+)', line)
                if step_match:
                    results["actions"].append({
                        "step": step_match.group(1),
                        "details": step_match.group(2).strip()
                    })

            # Extract focus verification
            if "VERIFY" in line:
                verify_match = re.search(r'VERIFY.*Control:\s*(.+?)\s*\|\s*Window:\s*(.+)', line)
                if verify_match:
                    results["focus_verification"].append({
                        "control": verify_match.group(1).strip(),
                        "window": verify_match.group(2).strip()
                    })

        return results

    except Exception as e:
        logger.error(f"Error in parse_test_log: {e}", exc_info=True)
        raise
def compare_results(diagnostic_results: Dict, test_results: Dict) -> Dict[str, Any]:
    """Compare diagnostic and test results"""
    comparison = {
        "diagnostic_file": diagnostic_results.get("file"),
        "test_file": test_results.get("file"),
        "differences": [],
        "focus_issues": [],
        "recommendations": []
    }

    # Compare focus states
    diagnostic_focus = []
    for step in diagnostic_results.get("steps", []):
        if step.get("control"):
            diagnostic_focus.append({
                "step": step.get("step"),
                "control": step.get("control"),
                "window": step.get("window")
            })

    test_focus = test_results.get("focus_verification", [])

    # Find differences
    if len(diagnostic_focus) > 0 and len(test_focus) > 0:
        # Compare first and last focus states
        diag_first = diagnostic_focus[0]
        diag_last = diagnostic_focus[-1]
        test_first = test_focus[0] if test_focus else {}
        test_last = test_focus[-1] if test_focus else {}

        if diag_first.get("control") != test_first.get("control"):
            comparison["differences"].append({
                "type": "initial_focus",
                "diagnostic": diag_first.get("control"),
                "test": test_first.get("control")
            })

        if diag_last.get("control") != test_last.get("control"):
            comparison["differences"].append({
                "type": "final_focus",
                "diagnostic": diag_last.get("control"),
                "test": test_last.get("control")
            })

    # Identify focus issues
    for step in diagnostic_results.get("steps", []):
        control = step.get("control", "")
        if control and "editor" in control.lower() and "chat" not in control.lower():
            comparison["focus_issues"].append({
                "step": step.get("step"),
                "issue": "Focus on editor instead of chat",
                "control": control
            })

    # Generate recommendations
    if comparison["focus_issues"]:
        comparison["recommendations"].append(
            "Focus is going to editor - need to explicitly focus chat input"
        )
        comparison["recommendations"].append(
            "Try mouse click method (Method 6) as it's most reliable"
        )
        comparison["recommendations"].append(
            "Increase wait time after Ctrl+L to 700ms+ for layout to stabilize"
        )

    return comparison

def run_syphon_analysis(results: Dict[str, Any]) -> Dict[str, Any]:
    """Run results through Syphon for pattern analysis"""
    try:
        from lumina.syphon import Syphon
        syphon = Syphon()

        # Search for focus patterns
        focus_patterns = syphon.search(
            pattern="focus|control|window",
            path=results.get("diagnostic_file", ""),
            case_sensitive=False
        )

        return {
            "syphon_analysis": True,
            "patterns_found": focus_patterns.get("matches", []),
            "pattern_count": len(focus_patterns.get("matches", []))
        }
    except Exception as e:
        logger.warning(f"Syphon analysis not available: {e}")
        return {
            "syphon_analysis": False,
            "error": str(e)
        }

def main():
    try:
        """Main comparison function"""
        logger.info("=" * 60)
        logger.info("Chat Focus Results Comparison Tool")
        logger.info("=" * 60)
        logger.info("")

        # Find log files
        log_dir = project_root / "logs"
        today = datetime.now().strftime("%Y%m%d")

        diagnostic_log = log_dir / f"ChatFocus_Diagnostic_{today}.log"
        test_log = log_dir / f"RAltMacro_TEST_{today}.log"

        logger.info(f"Looking for diagnostic log: {diagnostic_log}")
        logger.info(f"Looking for test log: {test_log}")
        logger.info("")

        # Parse logs
        logger.info("Parsing diagnostic log...")
        diagnostic_results = parse_autohotkey_log(diagnostic_log)

        logger.info("Parsing test log...")
        test_results = parse_test_log(test_log)

        # Compare
        logger.info("Comparing results...")
        comparison = compare_results(diagnostic_results, test_results)

        # Run through Syphon if requested
        logger.info("Running Syphon analysis...")
        syphon_results = run_syphon_analysis(comparison)
        comparison["syphon"] = syphon_results

        # Output results
        output_file = log_dir / f"ChatFocus_Comparison_{today}.json"
        with open(output_file, 'w') as f:
            json.dump(comparison, f, indent=2)

        logger.info("")
        logger.info("=" * 60)
        logger.info("COMPARISON RESULTS")
        logger.info("=" * 60)
        logger.info(f"Differences found: {len(comparison['differences'])}")
        logger.info(f"Focus issues found: {len(comparison['focus_issues'])}")
        logger.info(f"Recommendations: {len(comparison['recommendations'])}")
        logger.info("")
        logger.info("Differences:")
        for diff in comparison["differences"]:
            logger.info(f"  - {diff['type']}: {diff.get('diagnostic')} vs {diff.get('test')}")
        logger.info("")
        logger.info("Focus Issues:")
        for issue in comparison["focus_issues"]:
            logger.info(f"  - Step {issue['step']}: {issue['issue']} ({issue['control']})")
        logger.info("")
        logger.info("Recommendations:")
        for rec in comparison["recommendations"]:
            logger.info(f"  - {rec}")
        logger.info("")
        logger.info(f"Full results saved to: {output_file}")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()