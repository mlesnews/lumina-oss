#!/usr/bin/env python3
"""
Kilo Code + Ultron Connectivity Diagnostic.

Checks:
1. Ollama at http://localhost:11434 (Ultron) is reachable.
2. Repo config (kilo_code_optimized_config.json) uses base_url 11434 for local Ultron.
3. Optional: host_identity_registry ultron.primary = 11434.

#automation: run from repo root: python scripts/python/diagnose_kilo_code_ultron_connectivity.py
Exit 0 if all checks pass; 1 if any critical check fails.
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict

try:
    import requests  # type: ignore[import-untyped]
except ImportError:
    print("ERROR: requests not installed. pip install requests")
    sys.exit(2)

ULTRON_OLLAMA_URL = "http://localhost:11434"
TIMEOUT = 10
REPO_ROOT_NAMES = (".lumina", "config", "data", "docs", "scripts")


def find_repo_root() -> Path | None:
    """Find repo root by looking for config/ and .lumina or key dirs."""
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        if (parent / "config").is_dir() and (parent / "config").joinpath("host_identity_registry.json").exists():
            return parent
        if (parent / ".lumina").is_dir() and (parent / "config").is_dir():
            return parent
    return None


def check_ollama(base_url: str = ULTRON_OLLAMA_URL) -> Dict[str, Any]:
    """Check if Ollama is running and returns /api/tags."""
    result: Dict[str, Any] = {"status": "unknown", "accessible": False, "error": None, "models": []}
    try:
        r = requests.get(f"{base_url}/api/tags", timeout=TIMEOUT)
        r.raise_for_status()
        data = r.json()
        result["status"] = "running"
        result["accessible"] = True
        result["models"] = [m.get("name", "") for m in data.get("models", [])]
    except requests.exceptions.ConnectionError:
        result["status"] = "not_running"
        result["error"] = f"Cannot connect to {base_url}. Is Ollama running? (ollama serve)"
    except requests.exceptions.Timeout:
        result["status"] = "timeout"
        result["error"] = f"Timeout after {TIMEOUT}s"
    except Exception as e:  # pylint: disable=broad-except
        result["status"] = "error"
        result["error"] = str(e)
    return result


def check_kilo_code_config(repo_root: Path) -> Dict[str, Any]:
    """Check kilo_code_optimized_config.json primary_llm.base_url for Ultron (11434)."""
    result: Dict[str, Any] = {"path": None, "exists": False, "base_url": None, "ok": False, "message": None}
    path = repo_root / "config" / "kilo_code_optimized_config.json"
    result["path"] = str(path)
    if not path.exists():
        result["message"] = "Config file not found"
        return result
    result["exists"] = True
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        llm = data.get("llm_config", {}).get("primary_llm", {})
        base_url = llm.get("base_url") or ""
        result["base_url"] = base_url
        if "11434" in base_url and "localhost" in base_url:
            result["ok"] = True
            result["message"] = "base_url points to Ultron Ollama (11434)"
        elif "11437" in base_url:
            result["message"] = "base_url uses 11437; on laptop Ollama is 11434. Update to http://localhost:11434"
        else:
            result["message"] = f"base_url {base_url!r}; expected http://localhost:11434 for Ultron"
    except Exception as e:  # pylint: disable=broad-except
        result["message"] = f"Error reading config: {e}"
    return result


def check_host_registry(repo_root: Path) -> Dict[str, Any]:
    """Check host_identity_registry cluster_endpoints_derived.ultron.primary."""
    result: Dict[str, Any] = {"path": None, "exists": False, "ultron_primary": None, "ok": False, "message": None}
    path = repo_root / "config" / "host_identity_registry.json"
    result["path"] = str(path)
    if not path.exists():
        result["message"] = "Host identity registry not found"
        return result
    result["exists"] = True
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        derived = data.get("cluster_endpoints_derived", {}) or {}
        ultron = derived.get("ultron", {}) or {}
        primary = ultron.get("primary") or ""
        result["ultron_primary"] = primary
        if "11434" in primary:
            result["ok"] = True
            result["message"] = "Ultron primary is 11434"
        else:
            result["message"] = f"Ultron primary is {primary!r}; expected http://localhost:11434"
    except Exception as e:  # pylint: disable=broad-except
        result["message"] = f"Error reading registry: {e}"
    return result


def run_diagnostic() -> Dict[str, Any]:
    """Run all checks. Returns dict with ollama, kilo_config, host_registry, recommendations."""
    repo_root = find_repo_root()
    if not repo_root:
        print("WARN: Repo root not found (no config/host_identity_registry.json). Using CWD for config paths.")
        repo_root = Path.cwd()

    ollama = check_ollama()
    kilo_config = check_kilo_code_config(repo_root)
    host_registry = check_host_registry(repo_root)

    recommendations = []
    if not ollama["accessible"]:
        recommendations.append({
            "priority": "critical",
            "action": "Start Ollama",
            "detail": "Run: ollama serve. Then verify: curl http://localhost:11434/api/tags",
        })
    if not kilo_config.get("ok") and kilo_config.get("exists"):
        recommendations.append({
            "priority": "high",
            "action": "Align Kilo Code repo config",
            "detail": "Set config/kilo_code_optimized_config.json llm_config.primary_llm.base_url to http://localhost:11434",
        })
    if not host_registry.get("ok") and host_registry.get("exists"):
        recommendations.append({
            "priority": "medium",
            "action": "Align host identity registry",
            "detail": "Set config/host_identity_registry.json cluster_endpoints_derived.ultron.primary to http://localhost:11434",
        })
    recommendations.append({
        "priority": "info",
        "action": "Set Kilo Code profile in UI",
        "detail": "Kilo Code uses its own settings (gear). Set API profile base URL to http://localhost:11434 (or /v1). See docs/system/KILO_CODE_ULTRON_CONNECTIVITY.md",
    })

    return {
        "ollama": ollama,
        "kilo_config": kilo_config,
        "host_registry": host_registry,
        "recommendations": recommendations,
        "repo_root": str(repo_root),
    }


def main() -> int:
    print("Kilo Code + Ultron connectivity diagnostic\n")
    result = run_diagnostic()

    print("1. Ollama (Ultron) at", ULTRON_OLLAMA_URL)
    o = result["ollama"]
    print(f"   Status: {o['status']}")
    if o.get("error"):
        print(f"   Error: {o['error']}")
    if o.get("models"):
        print(f"   Models: {', '.join(o['models'][:8])}{' ...' if len(o['models']) > 8 else ''}")

    print("\n2. Repo config (kilo_code_optimized_config.json)")
    k = result["kilo_config"]
    print(f"   Path: {k['path']}")
    print(f"   base_url: {k.get('base_url') or 'N/A'}")
    print(f"   OK: {k.get('ok')} - {k.get('message') or ''}")

    print("\n3. Host identity registry (ultron.primary)")
    h = result["host_registry"]
    print(f"   ultron_primary: {h.get('ultron_primary') or 'N/A'}")
    print(f"   OK: {h.get('ok')} - {h.get('message') or ''}")

    if result["recommendations"]:
        print("\nRecommendations:")
        for rec in result["recommendations"]:
            print(f"   [{rec['priority'].upper()}] {rec['action']}: {rec['detail']}")

    critical = [r for r in result["recommendations"] if r["priority"] == "critical"]
    failed = not result["ollama"]["accessible"] or (result["kilo_config"].get("exists") and not result["kilo_config"].get("ok"))
    exit_code = 1 if (critical or failed) else 0
    print(f"\nExit: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
