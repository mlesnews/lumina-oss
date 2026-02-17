#!/usr/bin/env python3
"""
Bones — Lumina Doctor (Star Trek TOS)

Single command to diagnose EVERYTHING:
  - C3 Cluster Health (Ollama, Iron Legion, LiteLLM, SYPHON)
  - SPOF Analysis (single points of failure across tiers)
  - COMPUSEC Scan (temp file leaks, shell history, weasel holes)
  - n8n Workflow Status (6 workflows on NAS)
  - Service Registry Integrity (watchdog tasks, scheduled tasks)

"I'm a doctor, not a bricklayer!" — Dr. Leonard McCoy

Usage:
  python3 bones.py                    # Full diagnostic
  python3 bones.py --quick            # Health + SPOF only (fast)
  python3 bones.py --security         # COMPUSEC-focused scan
  python3 bones.py --json             # Machine-readable output
  python3 bones.py --persona emh      # Change the bedside manner

Tags: #Bones #Lumina_doctor #COMPUSEC #C3_Cluster @K-2SO @MARVIN
Origin: OpenClaw 'openclaw doctor' concept, adapted for Lumina
"""

import argparse
import json
import os
import re
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen
from urllib.error import URLError

# ── Paths ──────────────────────────────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent

# ── Personas ───────────────────────────────────────────────────────
PERSONAS = {
    "bones": {
        "name": "Dr. Leonard McCoy",
        "series": "TOS",
        "greeting": "I'm a doctor, not a systems administrator!",
        "signoff": "He's dead, Jim." if False else "All vitals stable. Bones signing off.",
        "critical": "Dammit Jim, the whole system's falling apart!",
    },
    "emh": {
        "name": "Emergency Medical Hologram",
        "series": "Voyager",
        "greeting": "Please state the nature of the medical emergency.",
        "signoff": "I have completed my diagnostic subroutines.",
        "critical": "This patient requires immediate intervention!",
    },
    "bashir": {
        "name": "Dr. Julian Bashir",
        "series": "DS9",
        "greeting": "Let's have a look at what's troubling you.",
        "signoff": "Prognosis looks good. Bashir out.",
        "critical": "We're losing them! Get me 50cc of redundancy, stat!",
    },
    "crusher": {
        "name": "Dr. Beverly Crusher",
        "series": "TNG",
        "greeting": "Medical scan in progress...",
        "signoff": "Patient is in stable condition. Crusher out.",
        "critical": "Captain, we have a serious problem down here.",
    },
    "phlox": {
        "name": "Dr. Phlox",
        "series": "Enterprise",
        "greeting": "Ah, a new patient! This should be fascinating.",
        "signoff": "Most satisfactory results. A good day for medicine!",
        "critical": "Most concerning! I've never seen readings like this.",
    },
}

TIMEOUT = 5  # seconds per endpoint check

# ── C3 Cluster Endpoints ──────────────────────────────────────────
ENDPOINTS = {
    # ULTRON / Falc (Primary)
    "ultron/ollama": {"url": "http://localhost:11434/api/tags", "tier": "ULTRON", "desc": "Ollama (RTX 5090)"},
    "ultron/litellm": {"url": "http://localhost:8080/health/liveliness", "tier": "ULTRON", "desc": "LiteLLM Gateway"},
    "ultron/cluster-ui": {"url": "http://localhost:8000/api/health", "tier": "ULTRON", "desc": "Cluster UI / SYPHON", "timeout": 10},
    # Iron Legion / KAIJU (Secondary)
    "iron-legion/router": {"url": "http://<NAS_IP>:3008/health", "tier": "IRON_LEGION", "desc": "Expert Router", "timeout": 8},
    "iron-legion/mark-i": {"url": "http://<NAS_IP>:3009/v1/models", "tier": "IRON_LEGION", "desc": "Mark I (14B)", "timeout": 8},
    "iron-legion/mark-iii": {"url": "http://<NAS_IP>:3003/v1/models", "tier": "IRON_LEGION", "desc": "Mark III (1.5B)"},
    "iron-legion/mark-vi": {"url": "http://<NAS_IP>:3006/v1/models", "tier": "IRON_LEGION", "desc": "Mark VI (7B)"},
    "iron-legion/syphon": {"url": "http://<NAS_IP>:8000/health", "tier": "IRON_LEGION", "desc": "SYPHON API"},
    # NAS (Tertiary)
    "nas/ollama": {"url": "http://<NAS_PRIMARY_IP>:11434/api/tags", "tier": "NAS", "desc": "NAS Ollama"},
    "nas/n8n": {"url": "http://<NAS_PRIMARY_IP>:5678/healthz", "tier": "NAS", "desc": "n8n Workflows"},
    "nas/smtp": {"url": "tcp://<NAS_PRIMARY_IP>:587", "tier": "NAS", "desc": "MailPlus SMTP"},
    "nas/imap": {"url": "tcp://<NAS_PRIMARY_IP>:993", "tier": "NAS", "desc": "MailPlus IMAP"},
}

# ── SPOF Service Groups ──────────────────────────────────────────
SERVICE_GROUPS = {
    "LLM Inference": {"endpoints": ["ultron/ollama", "nas/ollama"], "min": 2},
    "Iron Legion": {"endpoints": ["iron-legion/mark-i", "iron-legion/mark-iii", "iron-legion/mark-vi"], "min": 1, "single_tier": True},
    "LiteLLM Gateway": {"endpoints": ["ultron/litellm"], "min": 1, "single_tier": True},
    "SYPHON Tractor Beam": {"endpoints": ["iron-legion/syphon", "ultron/cluster-ui"], "min": 1},
    "n8n Workflows": {"endpoints": ["nas/n8n"], "min": 1, "single_tier": True},
    "Email": {"endpoints": ["nas/smtp", "nas/imap"], "min": 2, "single_tier": True},
}


# ── Diagnostic Functions ──────────────────────────────────────────

def check_endpoint(name: str, config: dict) -> dict:
    """Check a single endpoint (HTTP or TCP)."""
    url = config["url"]
    timeout = config.get("timeout", TIMEOUT)
    result = {"name": name, "tier": config["tier"], "desc": config["desc"]}
    start = time.time()

    if url.startswith("tcp://"):
        host, port = url.replace("tcp://", "").split(":")
        try:
            s = socket.create_connection((host, int(port)), timeout=timeout)
            s.close()
            result["status"] = "up"
            result["detail"] = f"TCP {port} open"
        except Exception as e:
            result["status"] = "down"
            result["detail"] = str(e)[:60]
    else:
        try:
            req = Request(url, headers={"User-Agent": "Bones-Doctor/2.0"})
            resp = urlopen(req, timeout=timeout)
            body = resp.read().decode("utf-8", errors="replace")[:200]
            result["status"] = "up"
            # Try to extract useful info
            try:
                data = json.loads(body)
                if "models" in data:
                    result["detail"] = f"{len(data['models'])} models"
                elif "data" in data:
                    result["detail"] = f"{len(data['data'])} items"
                else:
                    result["detail"] = f"HTTP {resp.status}"
            except (json.JSONDecodeError, ValueError):
                result["detail"] = f"HTTP {resp.status}"
        except Exception as e:
            result["status"] = "down"
            result["detail"] = str(e)[:60]

    result["latency_ms"] = round((time.time() - start) * 1000)
    return result


def run_health_checks() -> List[dict]:
    """Check all C3 cluster endpoints."""
    return [check_endpoint(name, cfg) for name, cfg in ENDPOINTS.items()]


def detect_spofs(results: List[dict]) -> List[dict]:
    """Analyze results for single points of failure."""
    result_map = {r["name"]: r for r in results}
    spofs = []

    for group_name, cfg in SERVICE_GROUPS.items():
        endpoints = cfg["endpoints"]
        single_tier = cfg.get("single_tier", False)
        up = [ep for ep in endpoints if result_map.get(ep, {}).get("status") == "up"]

        if len(up) == 0 and len(endpoints) > 0:
            spofs.append({"group": group_name, "severity": "CRITICAL",
                          "detail": f"ALL {len(endpoints)} endpoints DOWN", "up": 0, "total": len(endpoints)})
        elif single_tier and len(endpoints) == 1:
            status = result_map.get(endpoints[0], {}).get("status", "unknown")
            tier = result_map.get(endpoints[0], {}).get("tier", "?")
            spofs.append({"group": group_name,
                          "severity": "CRITICAL" if status == "down" else "WARNING",
                          "detail": f"Single-tier ({tier} only)", "up": len(up), "total": len(endpoints)})
        elif len(up) < cfg["min"]:
            spofs.append({"group": group_name, "severity": "HIGH",
                          "detail": f"{len(up)}/{len(endpoints)} up (need {cfg['min']})",
                          "up": len(up), "total": len(endpoints)})

    return spofs


def scan_temp_secrets() -> List[dict]:
    """Hunt for leaked secrets in temp directories (weasel holes)."""
    findings = []
    temp_dirs = ["/tmp"]

    secret_name_patterns = [
        r'\.(secret|api_key|token|password|cred|n8n_api|key_|auth)',
        r'(apikey|api_key|auth_token|session_token|jwt|bearer)',
        r'(nas_auth|n8n_cred|n8n_apikey|vault_secret)',
    ]

    for temp_dir in temp_dirs:
        if not os.path.isdir(temp_dir):
            continue
        try:
            for entry in os.scandir(temp_dir):
                if not entry.is_file():
                    continue
                for pattern in secret_name_patterns:
                    if re.search(pattern, entry.name, re.IGNORECASE):
                        findings.append({
                            "file": entry.path,
                            "type": "temp_file_secret",
                            "severity": "CRITICAL",
                            "detail": f"Secret-named temp file: {entry.name} ({entry.stat().st_size}B)",
                        })
                        break
                # Small files: check content
                try:
                    if entry.stat().st_size < 1024 and entry.stat().st_size > 10:
                        with open(entry.path, 'r', errors='ignore') as f:
                            content = f.read(1024)
                        if re.search(r'eyJ[A-Za-z0-9_-]{20,}\.eyJ', content):
                            findings.append({
                                "file": entry.path, "type": "jwt_in_temp",
                                "severity": "CRITICAL", "detail": "JWT token in temp file",
                            })
                        elif re.search(r'"sid"\s*:\s*"[A-Za-z0-9]{20,}"', content):
                            findings.append({
                                "file": entry.path, "type": "session_in_temp",
                                "severity": "HIGH", "detail": "Session token in temp file",
                            })
                except (PermissionError, OSError):
                    pass
        except PermissionError:
            pass

    return findings


def scan_shell_history() -> List[dict]:
    """Check shell history for leaked secrets."""
    findings = []
    history_files = [
        os.path.expanduser("~/.bash_history"),
        os.path.expanduser("~/.zsh_history"),
        os.path.expanduser("~/.python_history"),
    ]
    patterns = [
        (r'--password[= ]\S+', "CLI password argument"),
        (r'export\s+\w*(PASS|SECRET|TOKEN|KEY)\w*=\S+', "Secret in export"),
        (r'curl.*-H.*Bearer\s+[A-Za-z0-9._-]{20,}', "Bearer token in curl"),
        (r'curl.*-u\s+\S+:\S+', "Inline credentials in curl"),
    ]

    for hf in history_files:
        if not os.path.isfile(hf):
            continue
        try:
            with open(hf, 'r', errors='ignore') as f:
                line_count = 0
                secret_lines = 0
                for line in f:
                    line_count += 1
                    for pattern, desc in patterns:
                        if re.search(pattern, line, re.IGNORECASE):
                            secret_lines += 1
                            break
                if secret_lines > 0:
                    findings.append({
                        "file": hf, "type": "history_secrets",
                        "severity": "HIGH",
                        "detail": f"{secret_lines} lines with secrets in {line_count} total",
                    })
        except (PermissionError, OSError):
            pass

    return findings


def check_registries() -> List[dict]:
    """Verify watchdog and scheduled task registries are intact."""
    findings = []
    registries = [
        (PROJECT_ROOT / "data" / "watchdog_guarddog" / "watchdog_tasks.json", "Watchdog Kennel"),
        (PROJECT_ROOT / "config" / "lumina_scheduled_tasks.json", "Scheduled Tasks Pack"),
    ]

    for path, label in registries:
        if not path.exists():
            findings.append({"file": str(path), "type": "missing_registry",
                             "severity": "HIGH", "detail": f"{label} not found"})
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                count = len(data.get("tasks", data.get("watchdog_tasks", data)))
            elif isinstance(data, list):
                count = len(data)
            else:
                count = 0
            findings.append({"file": str(path), "type": "registry_ok",
                             "severity": "OK", "detail": f"{label}: {count} entries"})
        except (json.JSONDecodeError, OSError) as e:
            findings.append({"file": str(path), "type": "corrupt_registry",
                             "severity": "CRITICAL", "detail": f"{label} corrupt: {e}"})

    return findings


# ── Report Formatting ─────────────────────────────────────────────

RED = "\033[31m"
YEL = "\033[33m"
GRN = "\033[32m"
CYN = "\033[36m"
RST = "\033[0m"
BLD = "\033[1m"


def print_diagnosis(persona: dict, health: List[dict], spofs: List[dict],
                    temp_secrets: Optional[List[dict]], history: Optional[List[dict]],
                    registries: Optional[List[dict]], quick: bool = False):
    """Print the full Bones diagnostic report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    up = sum(1 for r in health if r["status"] == "up")
    total = len(health)
    critical_spofs = [s for s in spofs if s["severity"] == "CRITICAL"]
    sec_findings = (len(temp_secrets or []) +
                    sum(1 for h in (history or []) if h["severity"] != "OK"))

    # Header
    print(f"\n{'='*62}")
    print(f"  {BLD}BONES DIAGNOSTIC REPORT{RST} — {persona['name']} ({persona['series']})")
    print(f"  {now}")
    print(f"  \"{persona['greeting']}\"")
    print(f"{'='*62}")

    # ── Vital Signs (Health) ──
    print(f"\n  {BLD}VITAL SIGNS{RST} — C3 Cluster Health")
    print(f"  {'─'*50}")
    current_tier = None
    for r in sorted(health, key=lambda x: (x["tier"], x["name"])):
        if r["tier"] != current_tier:
            current_tier = r["tier"]
            print(f"  {CYN}{current_tier}{RST}")
        icon = f"{GRN}UP{RST}" if r["status"] == "up" else f"{RED}DN{RST}"
        print(f"    [{icon}] {r['desc']:<28} {r['latency_ms']:>5}ms  {r.get('detail','')[:30]}")

    print(f"\n    Endpoints: {GRN}{up}{RST}/{total} healthy")

    # ── SPOF Analysis ──
    print(f"\n  {BLD}SPOF SCAN{RST} — Single Points of Failure")
    print(f"  {'─'*50}")
    if not spofs:
        print(f"    {GRN}No single points of failure detected.{RST}")
    else:
        for s in sorted(spofs, key=lambda x: {"CRITICAL": 0, "HIGH": 1, "WARNING": 2}.get(x["severity"], 3)):
            sev = s["severity"]
            color = RED if sev == "CRITICAL" else YEL if sev == "HIGH" else CYN
            print(f"    [{color}{sev}{RST}] {s['group']}: {s['detail']} ({s['up']}/{s['total']} up)")

        total_groups = len(SERVICE_GROUPS)
        spof_groups = len(set(s["group"] for s in spofs))
        score = round(((total_groups - spof_groups) / total_groups) * 100) if total_groups else 0
        print(f"\n    Resilience: {score}% ({total_groups - spof_groups}/{total_groups} groups redundant)")

    if not quick:
        # ── COMPUSEC (Security) ──
        print(f"\n  {BLD}COMPUSEC{RST} — Security Posture")
        print(f"  {'─'*50}")

        if temp_secrets:
            for ts in temp_secrets:
                print(f"    [{RED}CRIT{RST}] {ts['detail']}")
        else:
            print(f"    {GRN}Temp dirs clean — no leaked secrets{RST}")

        for h in (history or []):
            if h["severity"] != "OK":
                color = RED if h["severity"] == "CRITICAL" else YEL
                print(f"    [{color}{h['severity']}{RST}] {h['detail']}")

        if sec_findings == 0:
            print(f"    {GRN}COMPUSEC posture: CLEAN{RST}")
        else:
            print(f"    {RED}COMPUSEC posture: {sec_findings} issue(s) found{RST}")

        # ── Registries ──
        print(f"\n  {BLD}REGISTRIES{RST} — Service Configuration")
        print(f"  {'─'*50}")
        for reg in (registries or []):
            if reg["severity"] == "OK":
                print(f"    {GRN}OK{RST} {reg['detail']}")
            else:
                color = RED if reg["severity"] == "CRITICAL" else YEL
                print(f"    [{color}{reg['severity']}{RST}] {reg['detail']}")

    # ── Prognosis ──
    print(f"\n{'='*62}")
    if critical_spofs or sec_findings > 0 or up < total // 2:
        print(f"  {RED}{BLD}PROGNOSIS: CRITICAL{RST}")
        print(f"  \"{persona['critical']}\"")
        exit_code = 2
    elif up < total or spofs:
        print(f"  {YEL}{BLD}PROGNOSIS: DEGRADED{RST}")
        print(f"  Some systems need attention, but we'll pull through.")
        exit_code = 1
    else:
        print(f"  {GRN}{BLD}PROGNOSIS: HEALTHY{RST}")
        print(f"  \"{persona['signoff']}\"")
        exit_code = 0
    print(f"{'='*62}\n")
    return exit_code


# ── Main ──────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bones — Lumina Doctor. Full system diagnostic.",
    )
    parser.add_argument("--persona", choices=list(PERSONAS), default="bones",
                        help="Doctor persona (default: bones)")
    parser.add_argument("--quick", action="store_true",
                        help="Quick check: health + SPOF only (skip security)")
    parser.add_argument("--security", action="store_true",
                        help="Security-focused: COMPUSEC scan only")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()

    persona = PERSONAS[args.persona]
    report = {}

    if args.security:
        # Security scan only
        temp_secrets = scan_temp_secrets()
        history = scan_shell_history()
        report = {"temp_secrets": temp_secrets, "history": history,
                  "total_findings": len(temp_secrets) + len([h for h in history if h["severity"] != "OK"])}
        if args.json:
            print(json.dumps(report, indent=2))
        else:
            print(f"\n  {BLD}COMPUSEC SCAN{RST}")
            if temp_secrets:
                for ts in temp_secrets:
                    print(f"  [{RED}CRIT{RST}] {ts['detail']}")
            else:
                print(f"  {GRN}Temp dirs clean{RST}")
            for h in history:
                if h["severity"] != "OK":
                    print(f"  [{YEL}{h['severity']}{RST}] {h['detail']}")
            print(f"\n  Total findings: {report['total_findings']}")
        return 1 if report["total_findings"] > 0 else 0

    # Health checks (always)
    health = run_health_checks()
    spofs = detect_spofs(health)
    report["health"] = health
    report["spofs"] = spofs

    if not args.quick:
        # Full diagnostic
        temp_secrets = scan_temp_secrets()
        history = scan_shell_history()
        registries = check_registries()
        report["temp_secrets"] = temp_secrets
        report["history"] = history
        report["registries"] = registries
    else:
        temp_secrets = None
        history = None
        registries = None

    if args.json:
        print(json.dumps(report, indent=2, default=str))
        return 0

    return print_diagnosis(persona, health, spofs, temp_secrets, history, registries,
                           quick=args.quick)


if __name__ == "__main__":
    sys.exit(main())
