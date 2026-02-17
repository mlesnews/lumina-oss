#!/usr/bin/env python3
"""
NAS Storage Indirect Impact on Cursor IDE

Investigates indirect NAS storage bottleneck impacts:
- Dropbox sync to NAS
- Network performance degradation
- Storage I/O contention
- File system delays

Tags: #NAS #STORAGE #BOTTLENECK #DROPBOX #CURSOR_IDE #DIAGNOSTICS @JARVIS @DIAGNOSTICS @SYPHON @ACE
"""

import sys
import json
import time
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("NASIndirectImpact")


class NASIndirectImpactDiagnostic:
    """
    Diagnoses indirect NAS storage bottleneck impacts on Cursor IDE.

    Investigates:
    - Dropbox sync to NAS
    - Network performance
    - Storage I/O contention
    - File system delays affecting Cursor IDE
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "nas_storage_diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Check if workspace is in Dropbox
        self.workspace_path = self.project_root
        self.is_dropbox = "Dropbox" in str(self.workspace_path)

        logger.info("✅ NAS Indirect Impact Diagnostic initialized")
        logger.info(f"   Workspace: {self.workspace_path}")
        logger.info(f"   In Dropbox: {self.is_dropbox}")

    def check_dropbox_nas_sync(self) -> Dict[str, Any]:
        """
        Check if Dropbox is syncing to NAS and causing bottlenecks.

        Returns:
            Dropbox sync analysis
        """
        logger.info("=" * 80)
        logger.info("🔍 CHECKING DROPBOX → NAS SYNC IMPACT")
        logger.info("=" * 80)
        logger.info("")

        findings = {
            "timestamp": datetime.now().isoformat(),
            "workspace_in_dropbox": self.is_dropbox,
            "dropbox_sync_active": False,
            "nas_sync_detected": False,
            "performance_impact": "unknown",
            "recommendations": []
        }

        if self.is_dropbox:
            logger.warning("   ⚠️  Workspace is in Dropbox directory")
            logger.warning(f"      Path: {self.workspace_path}")
            logger.warning("")
            logger.warning("   Dropbox syncing to NAS can cause:")
            logger.warning("   - File system delays")
            logger.warning("   - I/O contention")
            logger.warning("   - Network bandwidth saturation")
            logger.warning("   - Cursor IDE chat history access delays")
            logger.warning("")

            findings["performance_impact"] = "high"
            findings["recommendations"].extend([
                "⚠️  Consider excluding Cursor IDE data from Dropbox sync",
                "⚠️  Move Cursor IDE workspace outside Dropbox if possible",
                "⚠️  Configure Dropbox to exclude .cursor directories",
                "⚠️  Monitor Dropbox sync activity during Cursor IDE usage"
            ])

            # Check for Dropbox process
            try:
                result = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq Dropbox.exe"],
                    capture_output=True,
                    text=True
                )
                if "Dropbox.exe" in result.stdout:
                    findings["dropbox_sync_active"] = True
                    logger.info("   ✅ Dropbox process is running")
                else:
                    logger.info("   ℹ️  Dropbox process not found")
            except Exception as e:
                logger.debug(f"   Could not check Dropbox process: {e}")

            # Check if Dropbox folder is on NAS
            dropbox_path = Path.home() / "Dropbox"
            if dropbox_path.exists():
                # Check if it's a network path or on NAS drive
                dropbox_drive = dropbox_path.drive
                nas_drives = ["M:", "N:", "O:", "P:", "Q:", "R:", "S:", "T:"]

                if dropbox_drive in nas_drives:
                    findings["nas_sync_detected"] = True
                    logger.warning(f"   ⚠️  Dropbox folder is on NAS drive: {dropbox_drive}")
                    logger.warning("      This can cause significant performance issues!")
                else:
                    # Check if it's a network path
                    try:
                        result = subprocess.run(
                            ["net", "use"],
                            capture_output=True,
                            text=True
                        )
                        if "Dropbox" in result.stdout or "\\\\" in str(dropbox_path):
                            findings["nas_sync_detected"] = True
                            logger.warning("   ⚠️  Dropbox may be on network storage")
                    except Exception:
                        pass

        else:
            logger.info("   ✅ Workspace is not in Dropbox")

        return findings

    def measure_network_performance(self) -> Dict[str, Any]:
        """
        Measure network performance to NAS.

        Returns:
            Network performance metrics
        """
        logger.info("=" * 80)
        logger.info("📊 MEASURING NETWORK PERFORMANCE TO NAS")
        logger.info("=" * 80)
        logger.info("")

        performance = {
            "timestamp": datetime.now().isoformat(),
            "nas_drives": {},
            "network_latency": {},
            "bottleneck_detected": False
        }

        nas_drives = ["M:", "N:", "O:", "P:", "Q:", "R:", "S:", "T:"]

        for drive in nas_drives:
            drive_path = Path(f"{drive}\\")
            if drive_path.exists():
                logger.info(f"   Testing network performance: {drive}")

                try:
                    # Get network path
                    result = subprocess.run(
                        ["net", "use", drive],
                        capture_output=True,
                        text=True
                    )

                    if "Remote" in result.stdout:
                        # Extract network path
                        lines = result.stdout.split('\n')
                        network_path = None
                        for line in lines:
                            if "\\\\" in line:
                                network_path = line.strip()
                                break

                        if network_path:
                            logger.info(f"      Network path: {network_path}")

                            # Measure latency with multiple file operations
                            latencies = []
                            for i in range(5):
                                test_file = drive_path / f"network_test_{i}.tmp"
                                try:
                                    start_time = time.time()
                                    test_file.write_text(f"Test {i}")
                                    write_time = time.time() - start_time

                                    start_time = time.time()
                                    test_file.read_text()
                                    read_time = time.time() - start_time

                                    test_file.unlink()

                                    avg_latency = (write_time + read_time) / 2
                                    latencies.append(avg_latency * 1000)  # Convert to ms
                                except Exception as e:
                                    logger.debug(f"      Test {i} failed: {e}")

                            if latencies:
                                avg_latency = sum(latencies) / len(latencies)
                                max_latency = max(latencies)

                                performance["nas_drives"][drive] = {
                                    "network_path": network_path,
                                    "average_latency_ms": avg_latency,
                                    "max_latency_ms": max_latency,
                                    "test_count": len(latencies)
                                }

                                # Check for bottleneck (> 50ms average is concerning for network storage)
                                if avg_latency > 50:
                                    performance["bottleneck_detected"] = True
                                    logger.warning(f"      ⚠️  High network latency: {avg_latency:.1f}ms avg, {max_latency:.1f}ms max")
                                else:
                                    logger.info(f"      ✅ Network latency OK: {avg_latency:.1f}ms avg")

                except Exception as e:
                    logger.warning(f"      ⚠️  Could not test {drive}: {e}")

        if performance["bottleneck_detected"]:
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  NETWORK STORAGE BOTTLENECK DETECTED")
            logger.warning("=" * 80)
            logger.warning("")
            logger.warning("   High network latency to NAS can cause:")
            logger.warning("   - Cursor IDE chat history loading delays")
            logger.warning("   - PIN operations timing out")
            logger.warning("   - File system operations hanging")
            logger.warning("   - Connection errors (ECONNRESET)")
            logger.warning("")

        return performance

    def check_storage_io_contention(self) -> Dict[str, Any]:
        """
        Check for storage I/O contention that could affect Cursor IDE.

        Returns:
            I/O contention analysis
        """
        logger.info("=" * 80)
        logger.info("🔍 CHECKING STORAGE I/O CONTENTION")
        logger.info("=" * 80)
        logger.info("")

        contention = {
            "timestamp": datetime.now().isoformat(),
            "active_processes": [],
            "high_io_processes": [],
            "contention_detected": False,
            "recommendations": []
        }

        # Check for processes that might be causing I/O contention
        high_io_processes = [
            "Dropbox.exe",
            "OneDrive.exe",
            "GoogleDriveFS.exe",
            "svchost.exe",  # Windows services
            "System"
        ]

        try:
            result = subprocess.run(
                ["tasklist", "/FO", "CSV"],
                capture_output=True,
                text=True
            )

            for line in result.stdout.split('\n')[1:]:  # Skip header
                if line.strip():
                    parts = line.split(',')
                    if len(parts) >= 1:
                        process_name = parts[0].strip('"')
                        if process_name in high_io_processes:
                            contention["active_processes"].append(process_name)
                            logger.info(f"   Found high I/O process: {process_name}")

                            if process_name in ["Dropbox.exe", "OneDrive.exe"]:
                                contention["high_io_processes"].append(process_name)
                                contention["contention_detected"] = True
                                logger.warning(f"      ⚠️  {process_name} can cause I/O contention")

        except Exception as e:
            logger.warning(f"   ⚠️  Could not check processes: {e}")

        if contention["contention_detected"]:
            contention["recommendations"].extend([
                "⚠️  Pause Dropbox/OneDrive sync during Cursor IDE usage",
                "⚠️  Exclude Cursor IDE directories from sync",
                "⚠️  Schedule sync during off-hours",
                "⚠️  Monitor sync activity and Cursor IDE performance correlation"
            ])

        return contention

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        try:
            """
            Generate comprehensive diagnostic report.

            Returns:
                Complete diagnostic report
            """
            logger.info("=" * 80)
            logger.info("🔍 NAS INDIRECT IMPACT DIAGNOSTIC")
            logger.info("   Investigating Indirect NAS Bottleneck on Cursor IDE")
            logger.info("=" * 80)
            logger.info("")

            # Run all diagnostics
            dropbox_analysis = self.check_dropbox_nas_sync()
            network_performance = self.measure_network_performance()
            io_contention = self.check_storage_io_contention()

            # Compile findings
            report = {
                "timestamp": datetime.now().isoformat(),
                "dropbox_analysis": dropbox_analysis,
                "network_performance": network_performance,
                "io_contention": io_contention,
                "summary": {
                    "workspace_in_dropbox": dropbox_analysis["workspace_in_dropbox"],
                    "bottleneck_detected": (
                        dropbox_analysis.get("performance_impact") == "high" or
                        network_performance.get("bottleneck_detected", False) or
                        io_contention.get("contention_detected", False)
                    ),
                    "root_cause_likely": "nas_storage_bottleneck" if (
                        dropbox_analysis.get("nas_sync_detected", False) or
                        network_performance.get("bottleneck_detected", False)
                    ) else "unknown"
                },
                "recommendations": []
            }

            # Compile all recommendations
            report["recommendations"].extend(dropbox_analysis.get("recommendations", []))
            report["recommendations"].extend(io_contention.get("recommendations", []))

            if report["summary"]["bottleneck_detected"]:
                report["recommendations"].extend([
                    "🚨 CRITICAL: NAS storage bottleneck is likely root cause",
                    "   → Move Cursor IDE workspace outside Dropbox",
                    "   → Or exclude Cursor IDE data from Dropbox sync",
                    "   → Optimize NAS network configuration",
                    "   → Consider local caching for Cursor IDE data",
                    "   → Monitor NAS performance during Cursor IDE usage"
                ])

            # Save report
            report_file = self.data_dir / f"nas_indirect_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ DIAGNOSTIC COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Report saved: {report_file.name}")
            logger.info("")

            # Print summary
            print("\n" + "=" * 80)
            print("📊 NAS INDIRECT IMPACT DIAGNOSTIC SUMMARY")
            print("=" * 80)
            print(f"Workspace in Dropbox: {'⚠️  YES' if report['summary']['workspace_in_dropbox'] else '✅ NO'}")
            print(f"Bottleneck Detected: {'⚠️  YES' if report['summary']['bottleneck_detected'] else '✅ NO'}")
            print(f"Root Cause: {report['summary']['root_cause_likely']}")
            print("\nKey Recommendations:")
            for i, rec in enumerate(report["recommendations"][:8], 1):
                print(f"  {i}. {rec}")
            print("=" * 80)
            print()

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_comprehensive_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    diagnostic = NASIndirectImpactDiagnostic()
    diagnostic.generate_comprehensive_report()
    return 0


if __name__ == "__main__":


    sys.exit(main())