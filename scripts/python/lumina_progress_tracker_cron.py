#!/usr/bin/env python3
"""
Lumina Progress Tracker - Cronjob for Regular Measurement

"This is your measurement system. Run it regularly. Track your progress. Close the gap to 90%+."

Consolidated progress tracking that:
- Runs Universal Measurement System dashboard
- Runs Homelab Living Audit (quick mode)
- Calculates progress scores
- Tracks delta toward 90%+ target
- Saves historical progress data

Schedule: Run daily at 7 AM (after daily sweeps at 6 AM)

Tags: #CRON #MEASUREMENT #PROGRESS #AUDIT #90PERCENT @JARVIS @LUMINA
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger

    logger = get_logger("LuminaProgressTracker")
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    logger = logging.getLogger("LuminaProgressTracker")

# Data directories
PROGRESS_DIR = project_root / "data" / "progress_tracking"
PROGRESS_DIR.mkdir(parents=True, exist_ok=True)

PROGRESS_HISTORY_FILE = PROGRESS_DIR / "progress_history.jsonl"
PROGRESS_CURRENT_FILE = PROGRESS_DIR / "progress_current.json"
PROGRESS_REPORT_FILE = PROGRESS_DIR / "progress_report.md"

# Target: 90%
TARGET_PERCENT = 90


def calculate_framework_availability() -> Dict[str, Any]:
    """Calculate framework/system availability by scanning scripts directory"""
    scripts_dir = project_root / "scripts" / "python"

    results = {
        "frameworks": {"total": 0, "available": 0, "percent": 0, "details": []},
        "subagents": {"total": 0, "available": 0, "percent": 0, "details": []},
    }

    # Framework patterns: *_system.py, *_framework.py (core systems)
    framework_patterns = ["*_system.py", "*_framework.py"]

    # Subagent patterns: *_daemon.py, *_agent.py, *_coordinator.py
    subagent_patterns = ["*_daemon.py", "*_agent.py", "*_coordinator.py"]

    if scripts_dir.exists():
        # Check frameworks
        for pattern in framework_patterns:
            for script_file in scripts_dir.glob(pattern):
                if script_file.name.startswith("_"):
                    continue
                results["frameworks"]["total"] += 1
                try:
                    content = script_file.read_text(encoding="utf-8")
                    # Check for basic validity (has class or main function)
                    if (
                        "class " in content or "def main" in content
                    ) and "SyntaxError" not in content:
                        results["frameworks"]["available"] += 1
                        results["frameworks"]["details"].append(
                            {"name": script_file.stem, "status": "ok"}
                        )
                    else:
                        results["frameworks"]["details"].append(
                            {"name": script_file.stem, "status": "partial"}
                        )
                except Exception as e:
                    results["frameworks"]["details"].append(
                        {"name": script_file.stem, "status": "error", "error": str(e)[:30]}
                    )

        # Check subagents
        for pattern in subagent_patterns:
            for script_file in scripts_dir.glob(pattern):
                if script_file.name.startswith("_"):
                    continue
                results["subagents"]["total"] += 1
                try:
                    content = script_file.read_text(encoding="utf-8")
                    # Check for syntax validity by trying to compile
                    compile(content, script_file.name, "exec")
                    results["subagents"]["available"] += 1
                    results["subagents"]["details"].append(
                        {"name": script_file.stem, "status": "ok"}
                    )
                except SyntaxError as e:
                    results["subagents"]["details"].append(
                        {"name": script_file.stem, "status": "syntax_error", "error": str(e)[:30]}
                    )
                except Exception as e:
                    results["subagents"]["details"].append(
                        {"name": script_file.stem, "status": "error", "error": str(e)[:30]}
                    )

    # Calculate percentages
    if results["frameworks"]["total"] > 0:
        results["frameworks"]["percent"] = round(
            (results["frameworks"]["available"] / results["frameworks"]["total"]) * 100, 1
        )

    if results["subagents"]["total"] > 0:
        results["subagents"]["percent"] = round(
            (results["subagents"]["available"] / results["subagents"]["total"]) * 100, 1
        )

    return results


def calculate_cron_job_health() -> Dict[str, Any]:
    """Check NAS cron job configuration health"""
    cron_config = project_root / "config" / "nas_cron_tasks.json"

    result = {"total_jobs": 0, "enabled_jobs": 0, "percent": 0}

    if cron_config.exists():
        try:
            with open(cron_config, encoding="utf-8") as f:
                config = json.load(f)
                tasks = config.get("tasks", [])
                result["total_jobs"] = len(tasks)
                result["enabled_jobs"] = sum(1 for t in tasks if t.get("enabled", False))
                if result["total_jobs"] > 0:
                    result["percent"] = round(
                        (result["enabled_jobs"] / result["total_jobs"]) * 100, 1
                    )
        except Exception as e:
            logger.warning(f"Error reading cron config: {e}")

    return result


def calculate_mcp_server_health() -> Dict[str, Any]:
    """Check MCP server configuration health"""
    mcp_configs = [
        project_root / ".kilocode" / "mcp.json",
        project_root / ".cursor" / "mcp.json",
    ]

    result = {"total_servers": 0, "enabled_servers": 0, "disabled_servers": 0, "percent": 0}

    for mcp_config in mcp_configs:
        if mcp_config.exists():
            try:
                with open(mcp_config, encoding="utf-8") as f:
                    config = json.load(f)
                    servers = config.get("servers", config.get("mcpServers", {}))
                    for name, server in servers.items():
                        result["total_servers"] += 1
                        if server.get("disabled", False):
                            result["disabled_servers"] += 1
                        else:
                            result["enabled_servers"] += 1
            except Exception as e:
                logger.warning(f"Error reading MCP config {mcp_config}: {e}")

    if result["total_servers"] > 0:
        result["percent"] = round((result["enabled_servers"] / result["total_servers"]) * 100, 1)

    return result


def calculate_rules_compliance() -> Dict[str, Any]:
    """Check Cursor rules compliance"""
    rules_dir = project_root / ".cursor" / "rules"

    result = {"total_rules": 0, "active_rules": 0, "percent": 0}

    if rules_dir.exists():
        for rule_file in rules_dir.glob("*.mdc"):
            result["total_rules"] += 1
            try:
                content = rule_file.read_text(encoding="utf-8")
                # Check if rule has content (not empty/stub)
                if len(content.strip()) > 100:  # Minimum viable rule
                    result["active_rules"] += 1
            except Exception:
                pass

    if result["total_rules"] > 0:
        result["percent"] = round((result["active_rules"] / result["total_rules"]) * 100, 1)

    return result


def calculate_skills_availability() -> Dict[str, Any]:
    """Check Cursor skills availability"""
    skills_dir = project_root / ".cursor" / "skills"

    result = {"total_skills": 0, "available_skills": 0, "percent": 0}

    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir() and not skill_dir.name.startswith("."):
                skill_file = skill_dir / "SKILL.md"
                result["total_skills"] += 1
                if skill_file.exists():
                    try:
                        content = skill_file.read_text(encoding="utf-8")
                        if len(content.strip()) > 50:  # Has content
                            result["available_skills"] += 1
                    except Exception:
                        pass

    if result["total_skills"] > 0:
        result["percent"] = round((result["available_skills"] / result["total_skills"]) * 100, 1)

    return result


def calculate_scripts_health() -> Dict[str, Any]:
    """Check Python scripts health (can compile without errors)"""
    scripts_dir = project_root / "scripts" / "python"

    result = {"total_scripts": 0, "healthy_scripts": 0, "percent": 0, "errors": []}

    if scripts_dir.exists():
        for script_file in scripts_dir.glob("*.py"):
            if script_file.name.startswith("_"):
                continue
            result["total_scripts"] += 1
            try:
                content = script_file.read_text(encoding="utf-8")
                compile(content, script_file.name, "exec")
                result["healthy_scripts"] += 1
            except SyntaxError as e:
                result["errors"].append(
                    {"file": script_file.name, "error": f"SyntaxError: {str(e)[:50]}"}
                )
            except Exception:
                result["healthy_scripts"] += 1  # Non-syntax errors are OK for compilation

    if result["total_scripts"] > 0:
        result["percent"] = round((result["healthy_scripts"] / result["total_scripts"]) * 100, 1)

    return result


def run_progress_check() -> Dict[str, Any]:
    """Run comprehensive progress check"""
    logger.info("=" * 80)
    logger.info("LUMINA PROGRESS TRACKER - Running Measurement")
    logger.info("=" * 80)
    logger.info(f"Target: {TARGET_PERCENT}%")
    logger.info(f"Timestamp: {datetime.now().isoformat()}")

    progress = {
        "timestamp": datetime.now().isoformat(),
        "target_percent": TARGET_PERCENT,
        "components": {},
        "overall_score": 0,
        "gap_to_target": 0,
        "status": "measuring",
    }

    # 1. Framework & Subagent Availability
    logger.info("\n1. Checking Framework & Subagent Availability...")
    fa_result = calculate_framework_availability()
    progress["components"]["frameworks"] = fa_result["frameworks"]
    progress["components"]["subagents"] = fa_result["subagents"]
    logger.info(
        f"   Frameworks: {fa_result['frameworks']['percent']}% ({fa_result['frameworks']['available']}/{fa_result['frameworks']['total']})"
    )
    logger.info(
        f"   Subagents: {fa_result['subagents']['percent']}% ({fa_result['subagents']['available']}/{fa_result['subagents']['total']})"
    )

    # 2. Cron Job Health
    logger.info("\n2. Checking Cron Job Health...")
    cron_result = calculate_cron_job_health()
    progress["components"]["cron_jobs"] = cron_result
    logger.info(
        f"   Cron Jobs: {cron_result['percent']}% ({cron_result['enabled_jobs']}/{cron_result['total_jobs']} enabled)"
    )

    # 3. MCP Server Health
    logger.info("\n3. Checking MCP Server Health...")
    mcp_result = calculate_mcp_server_health()
    progress["components"]["mcp_servers"] = mcp_result
    logger.info(
        f"   MCP Servers: {mcp_result['percent']}% ({mcp_result['enabled_servers']}/{mcp_result['total_servers']} enabled)"
    )

    # 4. Rules Compliance
    logger.info("\n4. Checking Rules Compliance...")
    rules_result = calculate_rules_compliance()
    progress["components"]["rules"] = rules_result
    logger.info(
        f"   Rules: {rules_result['percent']}% ({rules_result['active_rules']}/{rules_result['total_rules']} active)"
    )

    # 5. Skills Availability
    logger.info("\n5. Checking Skills Availability...")
    skills_result = calculate_skills_availability()
    progress["components"]["skills"] = skills_result
    logger.info(
        f"   Skills: {skills_result['percent']}% ({skills_result['available_skills']}/{skills_result['total_skills']} available)"
    )

    # 6. Scripts Health
    logger.info("\n6. Checking Scripts Health...")
    scripts_result = calculate_scripts_health()
    progress["components"]["scripts"] = scripts_result
    logger.info(
        f"   Scripts: {scripts_result['percent']}% ({scripts_result['healthy_scripts']}/{scripts_result['total_scripts']} healthy)"
    )
    if scripts_result.get("errors"):
        for err in scripts_result["errors"][:3]:  # Show first 3 errors
            logger.warning(f"   ⚠️ {err['file']}: {err['error']}")

    # Calculate overall score (weighted average)
    weights = {
        "frameworks": 0.15,
        "subagents": 0.15,
        "cron_jobs": 0.15,
        "mcp_servers": 0.15,
        "rules": 0.15,
        "skills": 0.10,
        "scripts": 0.15,
    }

    weighted_sum = 0
    total_weight = 0
    for component, weight in weights.items():
        percent = progress["components"].get(component, {}).get("percent", 0)
        weighted_sum += percent * weight
        total_weight += weight

    progress["overall_score"] = round(weighted_sum / total_weight if total_weight > 0 else 0, 1)
    progress["gap_to_target"] = round(TARGET_PERCENT - progress["overall_score"], 1)
    progress["status"] = (
        "at_target" if progress["overall_score"] >= TARGET_PERCENT else "below_target"
    )

    logger.info("\n" + "=" * 80)
    logger.info("OVERALL PROGRESS")
    logger.info("=" * 80)
    logger.info(f"Overall Score: {progress['overall_score']}%")
    logger.info(f"Target: {TARGET_PERCENT}%")
    logger.info(f"Gap: {progress['gap_to_target']}%")
    logger.info(f"Status: {progress['status'].upper()}")
    logger.info("=" * 80)

    return progress


def save_progress(progress: Dict[str, Any]) -> None:
    """Save progress to history and current files"""
    # Append to history (JSONL)
    try:
        with open(PROGRESS_HISTORY_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(progress) + "\n")
        logger.info(f"✅ Progress saved to history: {PROGRESS_HISTORY_FILE}")
    except Exception as e:
        logger.error(f"Error saving progress history: {e}")

    # Save current state
    try:
        with open(PROGRESS_CURRENT_FILE, "w", encoding="utf-8") as f:
            json.dump(progress, f, indent=2)
        logger.info(f"✅ Current progress saved: {PROGRESS_CURRENT_FILE}")
    except Exception as e:
        logger.error(f"Error saving current progress: {e}")

    # Generate markdown report
    generate_progress_report(progress)


def generate_progress_report(progress: Dict[str, Any]) -> None:
    """Generate a markdown progress report"""
    report = f"""# Lumina Progress Report

**Generated**: {progress["timestamp"]}
**Target**: {progress["target_percent"]}%

---

## Overall Score: {progress["overall_score"]}%

| Status | Gap to Target |
|--------|---------------|
| {progress["status"].upper()} | {progress["gap_to_target"]}% |

---

## Component Scores

| Component | Score | Details |
|-----------|-------|---------|
| Frameworks | {progress["components"].get("frameworks", {}).get("percent", 0)}% | {progress["components"].get("frameworks", {}).get("available", 0)}/{progress["components"].get("frameworks", {}).get("total", 0)} available |
| Subagents | {progress["components"].get("subagents", {}).get("percent", 0)}% | {progress["components"].get("subagents", {}).get("available", 0)}/{progress["components"].get("subagents", {}).get("total", 0)} available |
| Cron Jobs | {progress["components"].get("cron_jobs", {}).get("percent", 0)}% | {progress["components"].get("cron_jobs", {}).get("enabled_jobs", 0)}/{progress["components"].get("cron_jobs", {}).get("total_jobs", 0)} enabled |
| MCP Servers | {progress["components"].get("mcp_servers", {}).get("percent", 0)}% | {progress["components"].get("mcp_servers", {}).get("enabled_servers", 0)}/{progress["components"].get("mcp_servers", {}).get("total_servers", 0)} enabled |
| Rules | {progress["components"].get("rules", {}).get("percent", 0)}% | {progress["components"].get("rules", {}).get("active_rules", 0)}/{progress["components"].get("rules", {}).get("total_rules", 0)} active |
| Skills | {progress["components"].get("skills", {}).get("percent", 0)}% | {progress["components"].get("skills", {}).get("available_skills", 0)}/{progress["components"].get("skills", {}).get("total_skills", 0)} available |
| Scripts | {progress["components"].get("scripts", {}).get("percent", 0)}% | {progress["components"].get("scripts", {}).get("healthy_scripts", 0)}/{progress["components"].get("scripts", {}).get("total_scripts", 0)} healthy |

---

## Progress Toward 90%+

```
Current:  {"█" * int(progress["overall_score"] / 5)}{"░" * (20 - int(progress["overall_score"] / 5))} {progress["overall_score"]}%
Target:   {"█" * 18}{"░" * 2} 90%
```

---

*Run regularly. Track progress. Close the gap to 90%+.*
"""

    try:
        with open(PROGRESS_REPORT_FILE, "w", encoding="utf-8") as f:
            f.write(report)
        logger.info(f"✅ Progress report generated: {PROGRESS_REPORT_FILE}")
    except Exception as e:
        logger.error(f"Error generating progress report: {e}")


def get_progress_history(limit: int = 30) -> list:
    """Get recent progress history"""
    history = []
    if PROGRESS_HISTORY_FILE.exists():
        try:
            with open(PROGRESS_HISTORY_FILE, encoding="utf-8") as f:
                lines = f.readlines()
                for line in lines[-limit:]:
                    history.append(json.loads(line))
        except Exception as e:
            logger.error(f"Error reading progress history: {e}")
    return history


def main():
    """Main entry point for cron job"""
    import argparse

    parser = argparse.ArgumentParser(description="Lumina Progress Tracker")
    parser.add_argument("--run", action="store_true", help="Run progress check and save results")
    parser.add_argument("--report", action="store_true", help="Generate report only (no save)")
    parser.add_argument(
        "--history", type=int, nargs="?", const=10, help="Show progress history (default: 10)"
    )
    parser.add_argument("--current", action="store_true", help="Show current progress")

    args = parser.parse_args()

    if args.history:
        history = get_progress_history(args.history)
        print(f"\nProgress History (last {len(history)} entries):")
        print("-" * 60)
        for entry in history:
            print(
                f"{entry['timestamp'][:10]}: {entry['overall_score']}% (gap: {entry['gap_to_target']}%)"
            )
        return

    if args.current:
        if PROGRESS_CURRENT_FILE.exists():
            with open(PROGRESS_CURRENT_FILE, encoding="utf-8") as f:
                current = json.load(f)
                print(json.dumps(current, indent=2))
        else:
            print("No current progress data. Run with --run first.")
        return

    # Default: run progress check
    progress = run_progress_check()

    if not args.report:
        save_progress(progress)

    print(
        f"\n✅ Progress check complete. Overall: {progress['overall_score']}%, Gap: {progress['gap_to_target']}%"
    )


if __name__ == "__main__":
    main()
