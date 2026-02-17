#!/usr/bin/env python3
"""
LUMINA Editor Workflow Daemon - End-to-End Automation

"The Battle Cry: YO JOE!"
Periodically sweeps the editor focus and triggers @TRIAD fixes.

Tags: #DAEMON #AUTOMATION #YO_JOE #EDITOR_WORKFLOW @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path

# Setup paths for lumina_core
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from lumina_core import BaseDaemon, EditorWorkflow, V3Verifier

class EditorWorkflowDaemon(BaseDaemon):
    """
    Automated Editor Workflow Daemon
    """

    def __init__(self, interval: int = 300): # Default 5 minutes
        super().__init__(
            daemon_name="EditorWorkflowDaemon",
            log_subdirectory="editor_workflow",
            interval=interval
        )
        self.workflow = EditorWorkflow(self.project_root)
        self.verifier = V3Verifier(self.project_root)
        self.state_file = (self.project_root / "data" / "editor_workflow" / 
                          "editor_state.json")

    def _run_cycle(self) -> bool:
        """
        Cycle Logic:
        1. Read current 'Open Files' from state.
        2. Perform Spectrum Sweep.
        3. Flag Dirty files for immediate fixing.
        4. Clear Clean files.
        """
        self.logger.info("Starting automation cycle...")

        # Load current editor focus
        if not self.state_file.exists():
            self.logger.warning("No editor_state.json found. Waiting for focus...")
            return True

        try:
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                open_files = state.get("open_files", [])
        except (IOError, json.JSONDecodeError) as e:
            self.logger.error("Failed to read editor state: %s", e)
            return False

        if not open_files:
            self.logger.info("No files in focus. Cycle complete.")
            return True

        # 1. Sweep
        self.logger.info("Sweeping %d files...", len(open_files))
        stack = self.workflow.sweep(open_files)

        # 2. Log Results
        dirty_count = (len(stack.red_stack) + len(stack.orange_stack) + 
                      len(stack.cyan_stack))
        self.logger.info("Sweep complete. Dirty: %d, Clean: %d", 
                         dirty_count, len(stack.green_stack))

        if dirty_count > 0:
            self.logger.warning("📌 %d files require @TRIAD action.", dirty_count)
            # INFO: In a full-auto environment, this would trigger the AI Fixer.

        # 3. Handle Safe to Close
        safe_files = self.workflow.get_safe_to_close()
        if safe_files:
            self.logger.info("✅ %d files are GREY/GREEN and safe to close.", 
                             len(safe_files))

        return True

def main():
    daemon = EditorWorkflowDaemon(interval=60) # 1 minute for high-fidelity
    daemon.run()

if __name__ == "__main__":


    main()