#!/usr/bin/env python3
"""
JARVIS Doctor - System Health Diagnostics

Inspired by OpenClaw's `openclaw doctor` command.
Self-diagnosis tool that checks all Lumina systems.

Usage:
    python jarvis_doctor.py
    python jarvis_doctor.py --verbose
    python jarvis_doctor.py --fix  # Attempt auto-fixes

Tags: #DOCTOR #HEALTH #DIAGNOSTICS #JARVIS @PEAK
"""

import json
import logging
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List

script_dir = Path(__file__).parent
project_root = Path.home() / "lumina"
cluster_dir = project_root / "docker" / "cluster-ui"
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Suppress Azure SDK verbose HTTP logging
for _azure_logger in ("azure", "azure.core", "azure.identity", "urllib3"):
    logging.getLogger(_azure_logger).setLevel(logging.WARNING)

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDoctor")


@dataclass
class CheckResult:
    """Result of a health check"""

    name: str
    status: str  # ok, warning, error, skipped
    message: str
    details: Dict = field(default_factory=dict)
    fix_available: bool = False
    fix_command: str = ""


class JARVISDoctor:
    """
    JARVIS Doctor - Comprehensive system health diagnostics

    Checks:
    - AI Clusters (Ollama, BitNet)
    - NAS connectivity and drives
    - Azure Key Vault access
    - MCP servers
    - Daily sweeps status
    - Framework/subagent health
    - Extension status
    """

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[CheckResult] = []
        self.project_root = project_root

    def run_all_checks(self) -> Dict:
        """Run all diagnostic checks"""
        print("=" * 60)
        print("🩺 JARVIS DOCTOR - System Health Diagnostics")
        print("=" * 60)
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Project: {self.project_root}")
        print("=" * 60)
        print()

        # Run all checks
        self._check_ai_clusters()
        self._check_nas_connectivity()
        self._check_nas_drives()
        self._check_trading_system()
        self._check_daily_sweeps()
        self._check_azure_keyvault()
        self._check_backup_sentinel()
        self._check_git_status()

        # Summary
        return self._print_summary()

    def _add_result(self, result: CheckResult):
        """Add a check result"""
        self.results.append(result)

        # Print result
        icon = {"ok": "✅", "warning": "⚠️", "error": "❌", "skipped": "⏭️"}.get(result.status, "❓")

        print(f"{icon} {result.name}: {result.message}")

        if self.verbose and result.details:
            for key, value in result.details.items():
                print(f"   └─ {key}: {value}")

    def _check_ai_clusters(self):
        """Check AI cluster connectivity"""
        print("\n📡 AI CLUSTERS")
        print("-" * 40)

        # Check ULTRON (localhost Ollama)
        try:
            import urllib.request

            response = urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5)
            data = json.loads(response.read())
            models = len(data.get("models", []))
            self._add_result(
                CheckResult(
                    name="ULTRON (localhost:11434)",
                    status="ok",
                    message=f"Online - {models} models loaded",
                    details={"models": [m["name"] for m in data.get("models", [])[:5]]},
                )
            )
        except Exception as e:
            self._add_result(
                CheckResult(
                    name="ULTRON (localhost:11434)",
                    status="error",
                    message=f"Offline - {e}",
                    fix_available=True,
                    fix_command="ollama serve",
                )
            )

        # Check KAIJU (<NAS_IP>)
        try:
            import urllib.request

            response = urllib.request.urlopen("http://<NAS_IP>:11434/api/tags", timeout=5)
            self._add_result(
                CheckResult(name="KAIJU (<NAS_IP>:11434)", status="ok", message="Online")
            )
        except Exception:
            self._add_result(
                CheckResult(
                    name="KAIJU (<NAS_IP>:11434)",
                    status="warning",
                    message="Offline or unreachable",
                )
            )

        # Check BitNet — binary + API server
        bitnet_path = Path.home() / "bitnet" / "build" / "bin" / "llama-cli"
        if bitnet_path.exists():
            # Binary compiled — now check if API server is live on port 11435
            try:
                import urllib.request

                response = urllib.request.urlopen("http://localhost:11435/health", timeout=3)
                self._add_result(
                    CheckResult(name="BitNet (CPU)", status="ok", message="Compiled + API server live (port 11435)")
                )
            except Exception:
                self._add_result(
                    CheckResult(name="BitNet (CPU)", status="ok", message="Compiled (API server not running)")
                )
        else:
            self._add_result(
                CheckResult(name="BitNet (CPU)", status="warning", message="Not compiled")
            )

    def _check_nas_connectivity(self):
        """Check NAS connectivity"""
        print("\n🗄️ NAS CONNECTIVITY")
        print("-" * 40)

        nas_ip = "<NAS_PRIMARY_IP>"
        try:
            import socket

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex((nas_ip, 5000))  # DSM port
            sock.close()

            if result == 0:
                self._add_result(
                    CheckResult(name=f"NAS ({nas_ip})", status="ok", message="Reachable")
                )
            else:
                self._add_result(
                    CheckResult(name=f"NAS ({nas_ip})", status="error", message="Not reachable")
                )
        except Exception as e:
            self._add_result(
                CheckResult(
                    name=f"NAS ({nas_ip})", status="error", message=f"Connection failed: {e}"
                )
            )

    def _check_nas_drives(self):
        """Check NAS mount points (WSL)"""
        print("\n💾 NAS MOUNTS")
        print("-" * 40)

        import os
        expected_mounts = {
            "/mnt/nas_homes": "homes",
            "/mnt/nas_jupyter": "jupyter",
        }

        for mount_path, purpose in expected_mounts.items():
            p = Path(mount_path)
            if p.exists() and os.path.ismount(mount_path):
                self._add_result(
                    CheckResult(name=f"Mount {mount_path}", status="ok", message=f"Mounted ({purpose})")
                )
            elif p.exists():
                self._add_result(
                    CheckResult(
                        name=f"Mount {mount_path}",
                        status="warning",
                        message=f"Dir exists but not mounted ({purpose})",
                        fix_available=True,
                        fix_command="mount-nas",
                    )
                )
            else:
                self._add_result(
                    CheckResult(
                        name=f"Mount {mount_path}",
                        status="error",
                        message=f"Not mounted ({purpose})",
                        fix_available=True,
                        fix_command="mount-nas",
                    )
                )

    def _check_azure_keyvault(self):
        """Check Azure Key Vault access"""
        print("\n🔐 AZURE KEY VAULT")
        print("-" * 40)

        try:
            from azure.identity import AzureCliCredential
            from azure.keyvault.secrets import SecretClient

            credential = AzureCliCredential()
            client = SecretClient(
                vault_url="https://jarvis-lumina.vault.azure.net/", credential=credential
            )

            # Try to list secrets (just check access)
            secrets = list(client.list_properties_of_secrets())[:1]
            self._add_result(
                CheckResult(
                    name="Azure Key Vault", status="ok", message="Connected (jarvis-lumina)"
                )
            )
        except Exception as e:
            self._add_result(
                CheckResult(
                    name="Azure Key Vault",
                    status="error",
                    message=f"Access failed: {str(e)[:50]}",
                    fix_available=True,
                    fix_command="az login",
                )
            )

    def _check_daily_sweeps(self):
        """Check @SYPHON intel sweep status"""
        print("\n🔍 @SYPHON SWEEPS")
        print("-" * 40)

        confidence_file = cluster_dir / "data" / "trading" / "state" / "confidence_aggregator.json"

        if confidence_file.exists():
            try:
                with open(confidence_file) as f:
                    state = json.load(f)

                pct = state.get("readiness_pct", 0)
                label = state.get("readiness_label", "UNKNOWN")
                cycle = state.get("cycle_count", 0)
                self._add_result(
                    CheckResult(
                        name="Confidence",
                        status="ok" if pct >= 50 else "warning",
                        message=f"{pct}% [{label}] (cycle {cycle})",
                    )
                )
            except Exception as e:
                self._add_result(
                    CheckResult(name="Confidence", status="error", message=f"State corrupt: {e}")
                )
        else:
            self._add_result(
                CheckResult(
                    name="Confidence",
                    status="warning",
                    message="No confidence state — run_intel.py may not have run yet",
                )
            )

        # Check if intel runner is active
        try:
            result = subprocess.run(
                ["pgrep", "-f", "run_intel.py"],
                capture_output=True, text=True, timeout=5,
            )
            if result.stdout.strip():
                self._add_result(
                    CheckResult(name="Intel Runner", status="ok", message=f"Running (PID {result.stdout.strip().split()[0]})")
                )
            else:
                self._add_result(
                    CheckResult(
                        name="Intel Runner",
                        status="warning",
                        message="Not running",
                        fix_available=True,
                        fix_command="cd docker/cluster-ui && python run_intel.py &",
                    )
                )
        except Exception:
            self._add_result(
                CheckResult(name="Intel Runner", status="skipped", message="Could not check")
            )

    def _check_trading_system(self):
        """Check trading system health"""
        print("\n📈 TRADING SYSTEM")
        print("-" * 40)

        # Check if trading runner is active
        try:
            result = subprocess.run(
                ["pgrep", "-f", "run_trading.py"],
                capture_output=True, text=True, timeout=5,
            )
            if result.stdout.strip():
                self._add_result(
                    CheckResult(name="Trading Runner", status="ok", message=f"Running (PID {result.stdout.strip().split()[0]})")
                )
            else:
                self._add_result(
                    CheckResult(name="Trading Runner", status="warning", message="Not running")
                )
        except Exception:
            self._add_result(
                CheckResult(name="Trading Runner", status="skipped", message="Could not check")
            )

        # Circuit breaker
        cb_file = cluster_dir / "data" / "trading" / "state" / "circuit_breaker.json"
        if cb_file.exists():
            try:
                with open(cb_file) as f:
                    cb = json.load(f)
                level = cb.get("level", "unknown")
                losses = cb.get("consecutive_losses", 0)
                self._add_result(
                    CheckResult(
                        name="Circuit Breaker",
                        status="ok" if level == "operational" else "error",
                        message=f"{level} ({losses} consecutive losses)",
                    )
                )
            except Exception:
                self._add_result(
                    CheckResult(name="Circuit Breaker", status="error", message="State corrupt")
                )
        else:
            self._add_result(
                CheckResult(name="Circuit Breaker", status="warning", message="No state file")
            )

        # Emergency stop
        estop = cluster_dir / "data" / "trading" / "EMERGENCY_STOP"
        if estop.exists():
            self._add_result(
                CheckResult(name="Emergency Stop", status="error", message="ENGAGED — trading halted")
            )
        else:
            self._add_result(
                CheckResult(name="Emergency Stop", status="ok", message="Not engaged")
            )

    def _check_backup_sentinel(self):
        """Check backup health via sentinel"""
        print("\n🛡️ BACKUP SENTINEL")
        print("-" * 40)

        sentinel = project_root / "scripts" / "backup_sentinel.py"
        if not sentinel.exists():
            self._add_result(
                CheckResult(name="Backup Sentinel", status="error", message="Script missing")
            )
            return

        try:
            result = subprocess.run(
                [sys.executable, str(sentinel), "check", "--json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                data = json.loads(result.stdout)
                summary = data.get("summary", {})
                coverage = summary.get("coverage_pct", 0)
                health = summary.get("health", "UNKNOWN")
                issues = len(summary.get("critical_issues", []))

                self._add_result(
                    CheckResult(
                        name="Backup Coverage",
                        status="ok" if health == "HEALTHY" else "error",
                        message=f"{coverage}% ({health}, {issues} critical issues)",
                    )
                )
            else:
                self._add_result(
                    CheckResult(name="Backup Coverage", status="warning", message="Sentinel check failed")
                )
        except Exception as e:
            self._add_result(
                CheckResult(name="Backup Coverage", status="warning", message=f"Error: {str(e)[:40]}")
            )

    def _check_git_status(self):
        """Check git repository status"""
        print("\n📂 GIT STATUS")
        print("-" * 40)

        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                changes = len(result.stdout.strip().split("\n")) if result.stdout.strip() else 0
                if changes == 0:
                    self._add_result(
                        CheckResult(name="Git Repository", status="ok", message="Clean")
                    )
                else:
                    self._add_result(
                        CheckResult(
                            name="Git Repository",
                            status="warning",
                            message=f"{changes} uncommitted changes",
                        )
                    )
            else:
                self._add_result(
                    CheckResult(
                        name="Git Repository", status="error", message="Not a git repository"
                    )
                )
        except Exception as e:
            self._add_result(
                CheckResult(
                    name="Git Repository", status="skipped", message=f"Could not check: {e}"
                )
            )

    def _print_summary(self) -> Dict:
        """Print summary and return results"""
        print()
        print("=" * 60)
        print("📊 SUMMARY")
        print("=" * 60)

        ok_count = sum(1 for r in self.results if r.status == "ok")
        warning_count = sum(1 for r in self.results if r.status == "warning")
        error_count = sum(1 for r in self.results if r.status == "error")
        skipped_count = sum(1 for r in self.results if r.status == "skipped")

        total = len(self.results)
        health_score = (ok_count / total * 100) if total > 0 else 0

        print(f"   ✅ OK:       {ok_count}")
        print(f"   ⚠️  Warning:  {warning_count}")
        print(f"   ❌ Error:    {error_count}")
        print(f"   ⏭️  Skipped:  {skipped_count}")
        print()
        print(f"   Health Score: {health_score:.0f}%")

        # Overall status
        if error_count == 0 and warning_count == 0:
            print()
            print("   🎉 All systems healthy!")
        elif error_count > 0:
            print()
            print("   ⚠️  Issues detected - see errors above")

            # List fixes
            fixes = [r for r in self.results if r.fix_available]
            if fixes:
                print()
                print("   Available fixes:")
                for r in fixes:
                    print(f"   └─ {r.name}: {r.fix_command}")

        print()
        print("=" * 60)

        return {
            "timestamp": datetime.now().isoformat(),
            "health_score": health_score,
            "ok": ok_count,
            "warning": warning_count,
            "error": error_count,
            "skipped": skipped_count,
            "results": [
                {
                    "name": r.name,
                    "status": r.status,
                    "message": r.message,
                    "fix_available": r.fix_available,
                    "fix_command": r.fix_command,
                }
                for r in self.results
            ],
        }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Doctor - System Health Diagnostics")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    parser.add_argument("--fix", action="store_true", help="Attempt auto-fixes (not implemented)")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    doctor = JARVISDoctor(verbose=args.verbose)
    results = doctor.run_all_checks()

    if args.json:
        print(json.dumps(results, indent=2))

    # Save results
    results_dir = project_root / "data" / "doctor_reports"
    results_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results_file = results_dir / f"doctor_report_{timestamp}.json"

    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"📄 Report saved: {results_file.name}")

    # Return exit code based on health
    if results["error"] > 0:
        sys.exit(1)
    elif results["warning"] > 0:
        sys.exit(0)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
