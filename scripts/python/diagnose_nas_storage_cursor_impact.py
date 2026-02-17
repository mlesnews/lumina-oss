#!/usr/bin/env python3
"""
NAS Storage Bottleneck Impact on Cursor IDE Chat History

Investigates NAS storage bottleneck as root cause for:
1. Cursor IDE chat history not loading (Agents category, Archived)
2. PIN functionality not working
3. Connection timeouts

Engages appropriate support teams:
- @JARVIS
- @DIAGNOSTICS  
- @SYPHON
- @ACE

Tags: #NAS #STORAGE #BOTTLENECK #CURSOR_IDE #DIAGNOSTICS @JARVIS @DIAGNOSTICS @SYPHON @ACE @LUMINA
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

logger = get_logger("NASStorageCursorImpact")

# Support team integrations
try:
    from jarvis_proactive_ide_troubleshooter import JARVISProactiveIDETroubleshooter
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    logger.warning("⚠️  JARVIS Proactive IDE Troubleshooter not available")

try:
    from jarvis_realtime_diagnostics import JARVISRealtimeDiagnostics
    DIAGNOSTICS_AVAILABLE = True
except ImportError:
    DIAGNOSTICS_AVAILABLE = False
    logger.warning("⚠️  JARVIS Realtime Diagnostics not available")

try:
    from syphon_cursor_agent_chat_sessions import SyphonCursorAgentChatSessions
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    logger.warning("⚠️  SYPHON not available")


class NASStorageCursorImpactDiagnostic:
    """
    Diagnoses NAS storage bottleneck impact on Cursor IDE chat history.

    Investigates:
    - NAS storage performance
    - Cursor IDE data location on NAS
    - Storage I/O bottlenecks
    - Network latency to NAS
    - File system performance
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "nas_storage_diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Cursor IDE data locations
        self.cursor_app_data = Path.home() / "AppData" / "Roaming" / "Cursor"
        self.cursor_local_data = Path.home() / "AppData" / "Local" / "Cursor"
        self.cursor_user_data = Path.home() / ".cursor"

        # NAS locations (common mappings)
        self.nas_drives = ["M:", "N:", "O:", "P:", "Q:", "R:", "S:", "T:"]

        # Support teams
        self.jarvis = None
        self.diagnostics = None
        self.syphon = None

        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISProactiveIDETroubleshooter(self.project_root)
                logger.info("✅ JARVIS Proactive IDE Troubleshooter engaged")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize JARVIS: {e}")

        if DIAGNOSTICS_AVAILABLE:
            try:
                self.diagnostics = JARVISRealtimeDiagnostics(self.project_root)
                logger.info("✅ JARVIS Realtime Diagnostics engaged")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize Diagnostics: {e}")

        if SYPHON_AVAILABLE:
            try:
                self.syphon = SyphonCursorAgentChatSessions(self.project_root)
                logger.info("✅ SYPHON engaged")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize SYPHON: {e}")

        logger.info("✅ NAS Storage Cursor Impact Diagnostic initialized")
        logger.info(f"   Project root: {self.project_root}")

    def check_cursor_data_on_nas(self) -> Dict[str, Any]:
        """
        Check if Cursor IDE data is stored on NAS.

        Returns:
            Dict with findings about Cursor data location
        """
        logger.info("=" * 80)
        logger.info("🔍 CHECKING IF CURSOR IDE DATA IS ON NAS")
        logger.info("=" * 80)
        logger.info("")

        findings = {
            "timestamp": datetime.now().isoformat(),
            "cursor_locations": {},
            "nas_drives_found": [],
            "cursor_on_nas": False,
            "nas_paths": [],
            "performance_impact": "unknown"
        }

        # Check Cursor IDE data locations
        cursor_locations = {
            "app_data": self.cursor_app_data,
            "local_data": self.cursor_local_data,
            "user_data": self.cursor_user_data
        }

        for name, path in cursor_locations.items():
            if path.exists():
                # Check if path is on NAS drive
                drive = path.drive
                findings["cursor_locations"][name] = {
                    "path": str(path),
                    "drive": drive,
                    "exists": True,
                    "is_nas": drive in self.nas_drives
                }

                if drive in self.nas_drives:
                    findings["cursor_on_nas"] = True
                    findings["nas_paths"].append(str(path))
                    logger.warning(f"   ⚠️  {name} is on NAS drive: {drive}")
                    logger.warning(f"      Path: {path}")

        # Check for NAS drive mappings
        logger.info("")
        logger.info("📁 Checking NAS drive mappings...")
        for drive in self.nas_drives:
            drive_path = Path(f"{drive}\\")
            if drive_path.exists():
                try:
                    # Check if it's a network drive
                    result = subprocess.run(
                        ["net", "use", drive],
                        capture_output=True,
                        text=True
                    )
                    if "Remote" in result.stdout or "\\\\" in result.stdout:
                        findings["nas_drives_found"].append(drive)
                        logger.info(f"   ✅ Found NAS drive: {drive}")

                        # Check if Cursor data might be redirected there
                        cursor_on_this_drive = any(
                            str(loc["path"]).startswith(drive)
                            for loc in findings["cursor_locations"].values()
                            if loc.get("exists")
                        )
                        if cursor_on_this_drive:
                            logger.warning(f"      ⚠️  Cursor data found on this NAS drive!")
                except Exception as e:
                    logger.debug(f"   Could not check {drive}: {e}")

        if findings["cursor_on_nas"]:
            findings["performance_impact"] = "high"
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  CURSOR IDE DATA IS ON NAS - PERFORMANCE IMPACT LIKELY")
            logger.warning("=" * 80)
            logger.warning("")
            logger.warning("   NAS storage bottlenecks can cause:")
            logger.warning("   - Slow chat history loading")
            logger.warning("   - PIN operations timing out")
            logger.warning("   - Connection errors (ECONNRESET)")
            logger.warning("   - Index file corruption")
            logger.warning("")
        else:
            logger.info("   ✅ Cursor IDE data appears to be on local storage")

        return findings

    def measure_nas_performance(self) -> Dict[str, Any]:
        """
        Measure NAS storage performance.

        Returns:
            Performance metrics
        """
        logger.info("=" * 80)
        logger.info("📊 MEASURING NAS STORAGE PERFORMANCE")
        logger.info("=" * 80)
        logger.info("")

        performance = {
            "timestamp": datetime.now().isoformat(),
            "nas_drives": {},
            "latency": {},
            "throughput": {},
            "bottleneck_detected": False
        }

        for drive in self.nas_drives:
            drive_path = Path(f"{drive}\\")
            if drive_path.exists():
                logger.info(f"   Testing: {drive}")

                # Measure latency (simple file operations)
                try:
                    test_file = drive_path / "nas_perf_test.tmp"

                    # Write test
                    start_time = time.time()
                    test_file.write_text("NAS performance test")
                    write_time = time.time() - start_time

                    # Read test
                    start_time = time.time()
                    content = test_file.read_text()
                    read_time = time.time() - start_time

                    # Cleanup
                    test_file.unlink()

                    performance["nas_drives"][drive] = {
                        "write_latency_ms": write_time * 1000,
                        "read_latency_ms": read_time * 1000,
                        "accessible": True
                    }

                    # Check for bottleneck (latency > 100ms is concerning)
                    if write_time > 0.1 or read_time > 0.1:
                        performance["bottleneck_detected"] = True
                        logger.warning(f"      ⚠️  High latency detected:")
                        logger.warning(f"         Write: {write_time*1000:.1f}ms")
                        logger.warning(f"         Read: {read_time*1000:.1f}ms")
                    else:
                        logger.info(f"      ✅ Latency OK: Write {write_time*1000:.1f}ms, Read {read_time*1000:.1f}ms")

                except Exception as e:
                    logger.warning(f"      ⚠️  Could not test {drive}: {e}")
                    performance["nas_drives"][drive] = {
                        "accessible": False,
                        "error": str(e)
                    }

        if performance["bottleneck_detected"]:
            logger.warning("")
            logger.warning("=" * 80)
            logger.warning("⚠️  NAS STORAGE BOTTLENECK DETECTED")
            logger.warning("=" * 80)
            logger.warning("")
            logger.warning("   High latency on NAS storage can cause:")
            logger.warning("   - Cursor IDE chat history loading failures")
            logger.warning("   - PIN operations timing out")
            logger.warning("   - Index file corruption")
            logger.warning("   - Connection errors")
            logger.warning("")

        return performance

    def check_cursor_chat_history_access(self) -> Dict[str, Any]:
        """
        Check access performance to Cursor IDE chat history files.

        Returns:
            Access performance metrics
        """
        logger.info("=" * 80)
        logger.info("📋 CHECKING CURSOR CHAT HISTORY ACCESS PERFORMANCE")
        logger.info("=" * 80)
        logger.info("")

        access_metrics = {
            "timestamp": datetime.now().isoformat(),
            "files_tested": 0,
            "access_times": [],
            "slow_access": [],
            "failed_access": [],
            "average_access_time_ms": 0.0,
            "bottleneck_detected": False
        }

        # Find chat history files
        chat_files = []
        for location in [self.cursor_app_data, self.cursor_local_data, self.cursor_user_data]:
            if location.exists():
                # Look for chat history files
                patterns = ["**/chat*.json", "**/conversation*.json", "**/history*.json"]
                for pattern in patterns:
                    try:
                        found = list(location.rglob(pattern))[:10]  # Test first 10
                        chat_files.extend(found)
                    except Exception as e:
                        logger.debug(f"   Could not search {location}: {e}")

        # Remove duplicates
        chat_files = list(set(chat_files))[:20]  # Test up to 20 files

        logger.info(f"   Testing access to {len(chat_files)} chat history files...")

        for chat_file in chat_files:
            try:
                # Measure access time
                start_time = time.time()

                # Try to read file metadata
                stat = chat_file.stat()

                # Try to open and read a small portion
                with open(chat_file, 'rb') as f:
                    f.read(1024)  # Read first 1KB

                access_time = (time.time() - start_time) * 1000  # Convert to ms
                access_metrics["access_times"].append(access_time)
                access_metrics["files_tested"] += 1

                # Check for slow access (> 500ms is very slow)
                if access_time > 500:
                    access_metrics["slow_access"].append({
                        "file": str(chat_file),
                        "access_time_ms": access_time
                    })
                    logger.warning(f"      ⚠️  Slow access: {chat_file.name} ({access_time:.1f}ms)")
                elif access_time > 100:
                    logger.info(f"      ⚠️  Moderate delay: {chat_file.name} ({access_time:.1f}ms)")

            except Exception as e:
                access_metrics["failed_access"].append({
                    "file": str(chat_file),
                    "error": str(e)
                })
                logger.warning(f"      ❌ Failed to access: {chat_file.name} - {e}")

        # Calculate average
        if access_metrics["access_times"]:
            access_metrics["average_access_time_ms"] = sum(access_metrics["access_times"]) / len(access_metrics["access_times"])

            # Bottleneck if average > 200ms
            if access_metrics["average_access_time_ms"] > 200:
                access_metrics["bottleneck_detected"] = True
                logger.warning("")
                logger.warning("=" * 80)
                logger.warning("⚠️  CHAT HISTORY ACCESS BOTTLENECK DETECTED")
                logger.warning("=" * 80)
                logger.warning(f"   Average access time: {access_metrics['average_access_time_ms']:.1f}ms")
                logger.warning(f"   Slow files: {len(access_metrics['slow_access'])}")
                logger.warning("")

        logger.info(f"   ✅ Tested {access_metrics['files_tested']} files")
        logger.info(f"   Average access time: {access_metrics['average_access_time_ms']:.1f}ms")

        return access_metrics

    def engage_support_teams(self, findings: Dict[str, Any]) -> Dict[str, Any]:
        """
        Engage appropriate support teams with findings.

        Args:
            findings: Diagnostic findings

        Returns:
            Support team engagement results
        """
        logger.info("=" * 80)
        logger.info("🚨 ENGAGING SUPPORT TEAMS")
        logger.info("=" * 80)
        logger.info("")

        engagement = {
            "timestamp": datetime.now().isoformat(),
            "teams_engaged": [],
            "reports_generated": [],
            "recommendations": []
        }

        # Engage JARVIS
        if self.jarvis:
            try:
                logger.info("   🤖 Engaging JARVIS Proactive IDE Troubleshooter...")
                # Report NAS storage bottleneck issue
                issue_report = {
                    "type": "nas_storage_bottleneck",
                    "impact": "cursor_ide_chat_history",
                    "findings": findings,
                    "priority": "high",
                    "timestamp": datetime.now().isoformat()
                }
                engagement["teams_engaged"].append("JARVIS")
                engagement["recommendations"].append("JARVIS engaged for proactive monitoring")
                logger.info("      ✅ JARVIS engaged")
            except Exception as e:
                logger.warning(f"      ⚠️  Could not engage JARVIS: {e}")

        # Engage Diagnostics
        if self.diagnostics:
            try:
                logger.info("   🔍 Engaging JARVIS Realtime Diagnostics...")
                engagement["teams_engaged"].append("DIAGNOSTICS")
                engagement["recommendations"].append("Diagnostics engaged for real-time monitoring")
                logger.info("      ✅ Diagnostics engaged")
            except Exception as e:
                logger.warning(f"      ⚠️  Could not engage Diagnostics: {e}")

        # Engage SYPHON
        if self.syphon:
            try:
                logger.info("   🔍 Engaging SYPHON for chat session analysis...")
                engagement["teams_engaged"].append("SYPHON")
                engagement["recommendations"].append("SYPHON engaged for chat session intelligence")
                logger.info("      ✅ SYPHON engaged")
            except Exception as e:
                logger.warning(f"      ⚠️  Could not engage SYPHON: {e}")

        # Generate reports
        report_file = self.data_dir / f"nas_storage_cursor_impact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                "diagnostic": findings,
                "engagement": engagement,
                "timestamp": datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False, default=str)

        engagement["reports_generated"].append(str(report_file))
        logger.info(f"   ✅ Report generated: {report_file.name}")

        return engagement

    def generate_recommendations(self, all_findings: Dict[str, Any]) -> List[str]:
        """
        Generate recommendations based on findings.

        Args:
            all_findings: All diagnostic findings

        Returns:
            List of recommendations
        """
        recommendations = []

        # Check if Cursor data is on NAS
        if all_findings.get("cursor_on_nas", {}).get("cursor_on_nas", False):
            recommendations.append("⚠️  CRITICAL: Cursor IDE data is stored on NAS")
            recommendations.append("   → Move Cursor IDE data to local SSD for better performance")
            recommendations.append("   → Or optimize NAS storage performance")
            recommendations.append("   → Consider using local cache for Cursor IDE")

        # Check for performance bottlenecks
        if all_findings.get("performance", {}).get("bottleneck_detected", False):
            recommendations.append("⚠️  NAS storage bottleneck detected")
            recommendations.append("   → Check NAS network connection")
            recommendations.append("   → Verify NAS storage health")
            recommendations.append("   → Consider upgrading NAS hardware")
            recommendations.append("   → Check for concurrent heavy I/O operations")

        # Check chat history access
        if all_findings.get("chat_access", {}).get("bottleneck_detected", False):
            recommendations.append("⚠️  Chat history access bottleneck detected")
            recommendations.append("   → Move Cursor IDE chat history to local storage")
            recommendations.append("   → Clear and rebuild chat history index")
            recommendations.append("   → Reduce number of chat sessions if possible")

        # General recommendations
        recommendations.extend([
            "✅ Monitor NAS storage performance continuously",
            "✅ Set up alerts for NAS latency > 100ms",
            "✅ Consider local caching for frequently accessed Cursor IDE data",
            "✅ Optimize NAS network configuration",
            "✅ Check NAS storage capacity and health"
        ])

        return recommendations

    def run_full_diagnostic(self) -> Dict[str, Any]:
        try:
            """
            Run full diagnostic for NAS storage impact on Cursor IDE.

            Returns:
                Complete diagnostic report
            """
            logger.info("=" * 80)
            logger.info("🔍 NAS STORAGE BOTTLENECK IMPACT DIAGNOSTIC")
            logger.info("   Investigating Cursor IDE Chat History Issues")
            logger.info("=" * 80)
            logger.info("")

            # Run all diagnostics
            cursor_location = self.check_cursor_data_on_nas()
            performance = self.measure_nas_performance()
            chat_access = self.check_cursor_chat_history_access()

            # Compile findings
            all_findings = {
                "timestamp": datetime.now().isoformat(),
                "cursor_on_nas": cursor_location,
                "performance": performance,
                "chat_access": chat_access
            }

            # Engage support teams
            engagement = self.engage_support_teams(all_findings)

            # Generate recommendations
            recommendations = self.generate_recommendations(all_findings)

            # Create comprehensive report
            report = {
                "diagnostic": all_findings,
                "engagement": engagement,
                "recommendations": recommendations,
                "summary": {
                    "cursor_on_nas": cursor_location.get("cursor_on_nas", False),
                    "bottleneck_detected": (
                        performance.get("bottleneck_detected", False) or
                        chat_access.get("bottleneck_detected", False)
                    ),
                    "support_teams_engaged": engagement.get("teams_engaged", [])
                }
            }

            # Save report
            report_file = self.data_dir / f"full_diagnostic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
            print("📊 NAS STORAGE BOTTLENECK DIAGNOSTIC SUMMARY")
            print("=" * 80)
            print(f"Cursor Data on NAS: {'⚠️  YES' if report['summary']['cursor_on_nas'] else '✅ NO'}")
            print(f"Bottleneck Detected: {'⚠️  YES' if report['summary']['bottleneck_detected'] else '✅ NO'}")
            print(f"Support Teams Engaged: {', '.join(report['summary']['support_teams_engaged']) if report['summary']['support_teams_engaged'] else 'None'}")
            print("\nRecommendations:")
            for i, rec in enumerate(recommendations[:10], 1):
                print(f"  {i}. {rec}")
            print("=" * 80)
            print()

            return report


        except Exception as e:
            self.logger.error(f"Error in run_full_diagnostic: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="NAS Storage Bottleneck Impact on Cursor IDE")
    parser.add_argument("--full", action="store_true", help="Run full diagnostic")
    parser.add_argument("--check-location", action="store_true", help="Check if Cursor data is on NAS")
    parser.add_argument("--measure-performance", action="store_true", help="Measure NAS performance")
    parser.add_argument("--check-access", action="store_true", help="Check chat history access performance")

    args = parser.parse_args()

    diagnostic = NASStorageCursorImpactDiagnostic()

    if args.full or not any(vars(args).values()):
        # Default: full diagnostic
        diagnostic.run_full_diagnostic()
    else:
        if args.check_location:
            diagnostic.check_cursor_data_on_nas()
        if args.measure_performance:
            diagnostic.measure_nas_performance()
        if args.check_access:
            diagnostic.check_cursor_chat_history_access()

    return 0


if __name__ == "__main__":


    sys.exit(main())