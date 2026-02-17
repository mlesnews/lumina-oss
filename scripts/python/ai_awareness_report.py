#!/usr/bin/env python3
"""
AI Awareness Report

Generates a report of what the AI can see/access in the current workspace.
Helps humans understand the AI's context and limitations.

Usage:
    python ai_awareness_report.py [--json] [--brief]

Tags: #transparency #self-awareness #visibility @JARVIS
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

# Project root
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def get_workspace_info() -> Dict[str, Any]:
    """Get workspace information."""
    return {
        "project_root": str(PROJECT_ROOT),
        "workspace_name": PROJECT_ROOT.name,
        "exists": PROJECT_ROOT.exists(),
    }


def get_rules() -> List[Dict[str, str]]:
    """Get active Cursor rules."""
    rules_dir = PROJECT_ROOT / ".cursor" / "rules"
    rules = []
    if rules_dir.exists():
        for f in rules_dir.glob("*.mdc"):
            rules.append({"name": f.stem, "path": str(f.relative_to(PROJECT_ROOT))})
    return rules


def get_skills() -> List[Dict[str, str]]:
    """Get available skills."""
    skills_dir = PROJECT_ROOT / ".cursor" / "skills"
    skills = []
    if skills_dir.exists():
        for d in skills_dir.iterdir():
            if d.is_dir() and (d / "SKILL.md").exists():
                skills.append(
                    {"name": d.name, "path": str((d / "SKILL.md").relative_to(PROJECT_ROOT))}
                )
    return skills


def get_memories() -> List[Dict[str, str]]:
    """Get persistent memories."""
    memories_dir = PROJECT_ROOT / ".cursor" / "memories"
    memories = []
    if memories_dir.exists():
        for f in memories_dir.glob("*.md"):
            memories.append({"name": f.stem, "path": str(f.relative_to(PROJECT_ROOT))})
    return memories


def get_key_configs() -> List[Dict[str, str]]:
    """Get key config files the AI uses."""
    key_configs = [
        "config/host_identity_registry.json",
        "config/homelab_inventory_registry.json",
        "config/jarvis_homelab_control_config.json",
        "config/cursor_ide_qol_registry.json",
        "config/homelab_ai_ecosystem.json",
        ".cursor/mcp.json",
    ]
    configs = []
    for cfg in key_configs:
        path = PROJECT_ROOT / cfg
        configs.append(
            {
                "name": Path(cfg).name,
                "path": cfg,
                "exists": path.exists(),
            }
        )
    return configs


def get_mcp_status() -> Dict[str, Any]:
    """Get MCP gateway status."""
    try:
        result = subprocess.run(
            ["docker", "mcp", "client", "ls"], capture_output=True, text=True, timeout=10
        )
        connected = "cursor" in result.stdout.lower() and "connected" in result.stdout.lower()
        return {
            "docker_mcp_available": True,
            "cursor_connected": connected,
            "output": result.stdout.strip(),
        }
    except Exception as e:
        return {"docker_mcp_available": False, "error": str(e)}


def get_git_status() -> Dict[str, Any]:
    """Get Git repository status."""
    try:
        # Branch
        branch_result = subprocess.run(
            ["git", "branch", "--show-current"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=5,
        )
        branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "unknown"

        # Status summary
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=10,
        )
        changes = (
            len([l for l in status_result.stdout.strip().split("\n") if l.strip()])
            if status_result.returncode == 0
            else 0
        )

        return {"is_git_repo": True, "branch": branch, "uncommitted_changes": changes}
    except Exception as e:
        return {"is_git_repo": False, "error": str(e)}


def get_limitations() -> List[str]:
    """List known AI limitations."""
    return [
        "Cannot see Cursor UI state (toggles, panels) without @mdv screenshot",
        "Cannot see real-time IDE notifications without running monitor script",
        "Cannot access other machines without SSH/API configured",
        "Cannot fetch secrets from vaults without explicit call",
        "Cannot read user's intent unless stated clearly",
        "No persistent memory across sessions unless written to .cursor/memories/",
    ]


def generate_report(brief: bool = False) -> Dict[str, Any]:
    """Generate the full awareness report."""
    report = {
        "timestamp": datetime.now().isoformat(),
        "workspace": get_workspace_info(),
        "rules": get_rules(),
        "skills": get_skills(),
        "memories": get_memories(),
        "key_configs": get_key_configs(),
        "mcp_status": get_mcp_status(),
        "git_status": get_git_status(),
        "limitations": get_limitations(),
    }

    if brief:
        # Summarize
        report = {
            "timestamp": report["timestamp"],
            "workspace": report["workspace"]["workspace_name"],
            "rules_count": len(report["rules"]),
            "skills_count": len(report["skills"]),
            "memories_count": len(report["memories"]),
            "configs_available": sum(1 for c in report["key_configs"] if c["exists"]),
            "mcp_connected": report["mcp_status"].get("cursor_connected", False),
            "git_branch": report["git_status"].get("branch", "n/a"),
            "git_changes": report["git_status"].get("uncommitted_changes", 0),
            "limitations_count": len(report["limitations"]),
        }

    return report


def print_human_readable(report: Dict[str, Any], brief: bool = False) -> None:
    """Print report in human-readable format."""
    print("=" * 60)
    print("AI AWARENESS REPORT")
    print(f"Generated: {report['timestamp']}")
    print("=" * 60)

    if brief:
        print(f"\nWorkspace: {report['workspace']}")
        print(
            f"Rules: {report['rules_count']} | Skills: {report['skills_count']} | Memories: {report['memories_count']}"
        )
        print(f"Key configs available: {report['configs_available']}")
        print(f"MCP connected: {report['mcp_connected']}")
        print(f"Git: {report['git_branch']} ({report['git_changes']} uncommitted changes)")
        print(f"Known limitations: {report['limitations_count']}")
    else:
        print(f"\n📁 WORKSPACE: {report['workspace']['project_root']}")

        print(f"\n📜 RULES ({len(report['rules'])}):")
        for r in report["rules"]:
            print(f"   • {r['name']}")

        print(f"\n🛠️  SKILLS ({len(report['skills'])}):")
        for s in report["skills"]:
            print(f"   • {s['name']}")

        print(f"\n🧠 MEMORIES ({len(report['memories'])}):")
        for m in report["memories"]:
            print(f"   • {m['name']}")

        print("\n⚙️  KEY CONFIGS:")
        for c in report["key_configs"]:
            status = "✓" if c["exists"] else "✗"
            print(f"   {status} {c['path']}")

        print("\n🔌 MCP STATUS:")
        mcp = report["mcp_status"]
        if mcp.get("docker_mcp_available"):
            status = "connected" if mcp.get("cursor_connected") else "not connected"
            print(f"   Docker MCP: available, Cursor: {status}")
        else:
            print(f"   Docker MCP: not available ({mcp.get('error', 'unknown')})")

        print("\n📊 GIT STATUS:")
        git = report["git_status"]
        if git.get("is_git_repo"):
            print(f"   Branch: {git['branch']}")
            print(f"   Uncommitted changes: {git['uncommitted_changes']}")
        else:
            print(f"   Not a git repo or error: {git.get('error', 'unknown')}")

        print("\n⚠️  KNOWN LIMITATIONS:")
        for lim in report["limitations"]:
            print(f"   • {lim}")

    print("\n" + "=" * 60)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Generate AI awareness report")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--brief", action="store_true", help="Brief summary only")
    args = parser.parse_args()

    report = generate_report(brief=args.brief)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print_human_readable(report, brief=args.brief)


if __name__ == "__main__":
    main()
