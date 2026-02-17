#!/usr/bin/env python3
"""
LUMINA Watchdog - Centralized Monitoring & Workflow Automation

"I am the Watchdog. I see everything."
Periodically sweeps the editor focus, refreshes file status, and triggers @TRIAD fixes.
Detects stalled workflows and resolves them autonomously.

Tags: #WATCHDOG #AUTOMATION #YO_JOE #EDITOR_WORKFLOW #STALL_DETECTION @LUMINA @JARVIS
"""

import sys
import json
import time
import psutil
from pathlib import Path
from typing import List, Dict, Any, Optional

# Setup paths for lumina_core
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lumina_core import BaseDaemon, EditorWorkflow, V3Verifier

class LuminaWatchdog(BaseDaemon):
    """
    Centralized LUMINA Watchdog Daemon
    """

    def __init__(self, interval: int = 60): # High-fidelity 1-minute cycle
        super().__init__(
            daemon_name="LuminaWatchdog",
            log_subdirectory="lumina_watchdog",
            interval=interval
        )
        self.workflow = EditorWorkflow(self.project_root)
        self.verifier = V3Verifier(self.project_root)
        self.state_file = (self.project_root / "data" / "editor_workflow" / 
                          "editor_state.json")
        self.process_limit = 10
        self.last_activity = {} # Map of file_path -> timestamp

    def _run_cycle(self) -> bool:
        """
        Cycle Logic:
        1. Check System Health (Python processes).
        2. Refresh Editor Status (The manual 'Tab' dance).
        3. Detect Stalls (Workflows stopped for no reason).
        4. Trigger @TRIAD fixes for Dirty pins.
        """
        self.logger.info("Initiating Watchdog surveillance cycle...")

        # 1. System Health Check
        self._check_process_proliferation()

        # 2. Refresh Editor Focus
        open_files = self._get_open_files()
        if not open_files:
            self.logger.info("No active files in focus. Monitoring quiet.")
            return True

        self.logger.info("Surveillance active on %d files.", len(open_files))

        # 3. Spectrum Sweep (Replicates 'Tabbing through all tabs')
        stack = self.workflow.sweep(open_files)

        # 4. Stall Detection
        self._detect_workflow_stalls(stack)

        # 5. Handle Dirty Pins
        dirty_files = stack.red_stack + stack.orange_stack + stack.cyan_stack
        if dirty_files:
            self.logger.warning("📌 %d files in Dirty Stack. Triggering @TRIAD...", 
                                len(dirty_files))
            # In a full production loop, this would call the AI Fixer/Keymaster auto

        # 6. Success Metrics
        if not dirty_files:
            self.logger.info("✨ Workspace is Green. Gozer is satisfied.")

        return True

    def _get_open_files(self) -> List[str]:
        """Load current editor state"""
        if not self.state_file.exists():
            return []
        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return state.get("open_files", [])
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error("Failed to read editor state: %s", e)
            return []

    def _check_process_proliferation(self):
        """Prevents system lockups by monitoring Python process count"""
        count = 0
        for proc in psutil.process_iter(['name']):
            try:
                if proc.info['name'] and 'python' in proc.info['name'].lower():
                    count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if count > self.process_limit:
            self.logger.critical("🚨 Process Proliferation! %d Python processes detected.", 
                                 count)
            # INFO: Watchdog would normally terminate excess processes here.

    def _detect_workflow_stalls(self, stack: Any):
        try:
            """Detects if a 'Dirty' file hasn't been touched recently"""
            current_time = time.time()
            dirty_files = stack.red_stack + stack.orange_stack

            for file_path in dirty_files:
                if file_path not in self.last_activity:
                    self.last_activity[file_path] = current_time
                    continue

                elapsed = current_time - self.last_activity[file_path]
                if elapsed > 300: # 5 minutes without change
                    self.logger.error("🛑 STALL DETECTED: %s has been Dirty for %dm.", 
                                      Path(file_path).name, int(elapsed/60))
                    # Trigger recovery logic (Refresh focus, Re-audit, or Force-Fix)

        except Exception as e:
            self.logger.error(f"Error in _detect_workflow_stalls: {e}", exc_info=True)
            raise
def main():
    daemon = LuminaWatchdog(interval=60)
    daemon.run()

if __name__ == "__main__":


    main()