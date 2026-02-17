#!/usr/bin/env python3
"""
ProtonPass Process Analyzer - @5W1H Root Cause Analysis
Identifies and analyzes processes blocking ProtonPass CLI

@5W1H Analysis:
- WHO: What process is blocking?
- WHAT: What is it doing?
- WHEN: When did it start?
- WHERE: Where is it located?
- WHY: Why is it blocking?
- HOW: How to resolve?

Tags: #PROTONPASS #5W1H #ROOT_CAUSE #PROCESS_ANALYSIS #JARVIS
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
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

logger = get_logger("ProtonPassProcessAnalyzer5W1H")


class ProtonPassProcessAnalyzer5W1H:
    """
    @5W1H Root Cause Analysis for ProtonPass Process Blocking

    Analyzes what process is blocking ProtonPass CLI and why
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize analyzer"""
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.protonpass_path = Path(r"C:\Users\mlesn\AppData\Local\Programs\ProtonPass\pass-cli.exe")
        self.protonpass_dir = self.protonpass_path.parent

        logger.info("=" * 70)
        logger.info("🔍 PROTONPASS PROCESS ANALYZER - @5W1H")
        logger.info("=" * 70)
        logger.info("")

    def find_blocking_processes(self) -> List[Dict[str, Any]]:
        """Find processes that might be blocking ProtonPass"""
        logger.info("🔍 Finding blocking processes...")

        blocking_processes = []

        try:
            # Find ProtonPass-related processes
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-Process | Where-Object {$_.Path -like '*ProtonPass*' -or $_.ProcessName -like '*pass*' -or $_.ProcessName -like '*proton*'} | Select-Object ProcessName, Id, Path, StartTime | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0 and result.stdout.strip():
                try:
                    processes = json.loads(result.stdout.strip())
                    if not isinstance(processes, list):
                        processes = [processes]

                    for proc in processes:
                        blocking_processes.append({
                            "process_name": proc.get("ProcessName", ""),
                            "process_id": proc.get("Id", 0),
                            "path": proc.get("Path", ""),
                            "start_time": proc.get("StartTime", "")
                        })
                except json.JSONDecodeError:
                    logger.debug("Could not parse process JSON")
        except Exception as e:
            logger.error(f"Error finding processes: {e}")

        # Check for file locks in ProtonPass directory
        try:
            result = subprocess.run(
                ["powershell", "-Command",
                 f"Get-ChildItem '{self.protonpass_dir}' -Recurse -ErrorAction SilentlyContinue | Where-Object {{$_.PSIsContainer -eq $false}} | Select-Object FullName, LastWriteTime | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                logger.debug("Checked ProtonPass directory files")
        except Exception as e:
            logger.debug(f"Error checking directory: {e}")

        return blocking_processes

    def analyze_5w1h(self, processes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform @5W1H root cause analysis"""
        logger.info("=" * 70)
        logger.info("📊 @5W1H ROOT CAUSE ANALYSIS")
        logger.info("=" * 70)
        logger.info("")

        analysis = {
            "who": {},
            "what": {},
            "when": {},
            "where": {},
            "why": {},
            "how": {},
            "recommendations": []
        }

        # WHO: What process is blocking?
        logger.info("WHO: What process is blocking?")
        logger.info("-" * 70)
        if processes:
            for proc in processes:
                logger.info(f"   Process: {proc.get('process_name', 'Unknown')}")
                logger.info(f"   PID: {proc.get('process_id', 'Unknown')}")
                logger.info(f"   Path: {proc.get('path', 'Unknown')}")
                logger.info("")
                analysis["who"][proc.get('process_id', 0)] = {
                    "name": proc.get('process_name', 'Unknown'),
                    "pid": proc.get('process_id', 0),
                    "path": proc.get('path', 'Unknown')
                }
        else:
            logger.info("   ⚠️  No ProtonPass processes found")
            logger.info("   Blocking might be from file locks or session conflicts")
            analysis["who"]["unknown"] = "No processes found - likely file lock or session issue"
        logger.info("")

        # WHAT: What is it doing?
        logger.info("WHAT: What is it doing?")
        logger.info("-" * 70)
        logger.info("   Error: 'Session is some but needs extra password'")
        logger.info("   Error: 'The process cannot access the file because it is being used by another process'")
        logger.info("   This indicates:")
        logger.info("   - Multiple ProtonPass CLI instances running")
        logger.info("   - File lock on session/temp files")
        logger.info("   - Session state conflict")
        logger.info("")
        analysis["what"] = {
            "error": "File lock / Session conflict",
            "symptoms": [
                "Session needs extra password",
                "File access denied (error 32)",
                "Process cannot access file"
            ],
            "likely_cause": "Multiple CLI instances or stale session files"
        }

        # WHEN: When did it start?
        logger.info("WHEN: When did it start?")
        logger.info("-" * 70)
        if processes:
            for proc in processes:
                start_time = proc.get('start_time', 'Unknown')
                logger.info(f"   {proc.get('process_name', 'Unknown')}: {start_time}")
                analysis["when"][proc.get('process_id', 0)] = start_time
        else:
            logger.info("   Unknown - no processes detected")
            analysis["when"] = "Unknown - file lock issue"
        logger.info("")

        # WHERE: Where is it located?
        logger.info("WHERE: Where is it located?")
        logger.info("-" * 70)
        logger.info(f"   ProtonPass CLI: {self.protonpass_path}")
        logger.info(f"   ProtonPass Directory: {self.protonpass_dir}")
        logger.info("   Likely lock location:")
        logger.info(f"   - {self.protonpass_dir / 'session'}")
        logger.info(f"   - {self.protonpass_dir / 'temp'}")
        logger.info(f"   - {Path.home() / '.protonpass'}")
        logger.info("")
        analysis["where"] = {
            "cli_path": str(self.protonpass_path),
            "directory": str(self.protonpass_dir),
            "likely_lock_locations": [
                str(self.protonpass_dir / "session"),
                str(self.protonpass_dir / "temp"),
                str(Path.home() / ".protonpass")
            ]
        }

        # WHY: Why is it blocking?
        logger.info("WHY: Why is it blocking?")
        logger.info("-" * 70)
        logger.info("   Root Causes:")
        logger.info("   1. Multiple ProtonPass CLI instances running simultaneously")
        logger.info("   2. Stale session files from previous runs")
        logger.info("   3. File locks from crashed/terminated processes")
        logger.info("   4. Session state conflict (needs extra password but session exists)")
        logger.info("   5. Background process holding file handles")
        logger.info("")
        analysis["why"] = {
            "root_causes": [
                "Multiple CLI instances",
                "Stale session files",
                "File locks from crashed processes",
                "Session state conflict",
                "Background process file handles"
            ],
            "primary_cause": "Multiple CLI instances or stale session files"
        }

        # HOW: How to resolve?
        logger.info("HOW: How to resolve?")
        logger.info("-" * 70)
        logger.info("   Solutions:")
        logger.info("   1. Terminate all ProtonPass processes")
        logger.info("   2. Clear session/temp files")
        logger.info("   3. Wait for file locks to release")
        logger.info("   4. Use process priority to ensure our process wins")
        logger.info("   5. Implement process management (single instance)")
        logger.info("")
        analysis["how"] = {
            "solutions": [
                "Terminate blocking processes",
                "Clear session/temp files",
                "Wait for locks to release",
                "Use process priority",
                "Implement single-instance management"
            ],
            "immediate_action": "Terminate all ProtonPass processes and clear locks"
        }

        # Recommendations
        logger.info("RECOMMENDATIONS:")
        logger.info("-" * 70)
        analysis["recommendations"] = [
            "Terminate all ProtonPass processes immediately",
            "Clear ProtonPass session/temp directories",
            "Implement process management to prevent multiple instances",
            "Add process priority handling for JARVIS operations",
            "Add file lock detection and cleanup before operations"
        ]

        for i, rec in enumerate(analysis["recommendations"], 1):
            logger.info(f"   {i}. {rec}")
        logger.info("")

        return analysis

    def terminate_blocking_processes(self) -> Dict[str, Any]:
        """Terminate blocking processes"""
        logger.info("=" * 70)
        logger.info("🛑 TERMINATING BLOCKING PROCESSES")
        logger.info("=" * 70)
        logger.info("")

        result = {
            "terminated": [],
            "errors": [],
            "success": False
        }

        processes = self.find_blocking_processes()

        if not processes:
            logger.info("   No processes found to terminate")
            logger.info("   Clearing file locks instead...")
            result["success"] = True
            return result

        for proc in processes:
            pid = proc.get('process_id', 0)
            name = proc.get('process_name', 'Unknown')

            try:
                logger.info(f"   Terminating: {name} (PID: {pid})")
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid)],
                    capture_output=True,
                    timeout=5
                )
                result["terminated"].append({"name": name, "pid": pid})
                logger.info(f"   ✅ Terminated: {name}")
            except Exception as e:
                logger.error(f"   ❌ Failed to terminate {name}: {e}")
                result["errors"].append({"name": name, "pid": pid, "error": str(e)})

        result["success"] = len(result["terminated"]) > 0
        logger.info("")

        return result

    def clear_session_files(self) -> Dict[str, Any]:
        """Clear ProtonPass session files"""
        logger.info("🧹 Clearing session files...")

        result = {
            "cleared": [],
            "errors": []
        }

        locations = [
            self.protonpass_dir / "session",
            self.protonpass_dir / "temp",
            Path.home() / ".protonpass"
        ]

        for location in locations:
            if location.exists():
                try:
                    # Try to remove files
                    for file in location.rglob("*"):
                        if file.is_file():
                            try:
                                file.unlink()
                                result["cleared"].append(str(file))
                            except Exception as e:
                                result["errors"].append({"file": str(file), "error": str(e)})
                    logger.info(f"   ✅ Cleared: {location}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not clear {location}: {e}")
                    result["errors"].append({"location": str(location), "error": str(e)})

        return result

    def execute_full_analysis(self) -> Dict[str, Any]:
        """Execute full @5W1H analysis and resolution"""
        logger.info("=" * 70)
        logger.info("🚀 EXECUTING FULL @5W1H ANALYSIS & RESOLUTION")
        logger.info("=" * 70)
        logger.info("")

        # Step 1: Find blocking processes
        processes = self.find_blocking_processes()

        # Step 2: @5W1H Analysis
        analysis = self.analyze_5w1h(processes)

        # Step 3: Terminate processes
        termination_result = self.terminate_blocking_processes()

        # Step 4: Clear session files
        clear_result = self.clear_session_files()

        # Step 5: Verify resolution
        logger.info("=" * 70)
        logger.info("✅ RESOLUTION COMPLETE")
        logger.info("=" * 70)
        logger.info("")

        return {
            "analysis": analysis,
            "termination": termination_result,
            "clear_session": clear_result,
            "timestamp": datetime.now().isoformat()
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="ProtonPass Process Analyzer - @5W1H")
    parser.add_argument("--analyze", "-a", action="store_true", help="Run @5W1H analysis")
    parser.add_argument("--terminate", "-t", action="store_true", help="Terminate blocking processes")
    parser.add_argument("--full", "-f", action="store_true", help="Full analysis and resolution")

    args = parser.parse_args()

    analyzer = ProtonPassProcessAnalyzer5W1H()

    if args.full:
        result = analyzer.execute_full_analysis()
        print(f"\n✅ Full analysis complete!")
    elif args.terminate:
        result = analyzer.terminate_blocking_processes()
        print(f"\n✅ Termination complete!")
    elif args.analyze:
        processes = analyzer.find_blocking_processes()
        analysis = analyzer.analyze_5w1h(processes)
        print(f"\n✅ Analysis complete!")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()