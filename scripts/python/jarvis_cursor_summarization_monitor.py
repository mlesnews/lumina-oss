#!/usr/bin/env python3
"""
JARVIS Cursor Summarization Monitor

Continuous monitor that watches conversation length and automatically
triggers summarization when needed.

Integrates with:
- Cursor Summarization Integration
- Persistent Memory
- Workflow Transparency System
"""

import sys
import time
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorSummarizationMonitor")

try:
    from jarvis_cursor_summarization_integration import JARVISCursorSummarizationIntegration
    SUMMARIZATION_AVAILABLE = True
except ImportError:
    SUMMARIZATION_AVAILABLE = False
    logger.error("Cursor Summarization Integration not available")

try:
    from jarvis_workflow_transparency_system import JARVISWorkflowTransparencySystem
    WORKFLOW_TRANSPARENCY_AVAILABLE = True
except ImportError:
    WORKFLOW_TRANSPARENCY_AVAILABLE = False
    logger.warning("Workflow Transparency System not available")


class JARVISCursorSummarizationMonitor:
    """
    Continuous monitor for Cursor summarization

    Watches conversations and automatically triggers summarization
    when context limits are approached.
    """

    def __init__(self, project_root: Path, check_interval: int = 60):
        self.project_root = project_root
        self.logger = logger
        self.check_interval = check_interval
        self.running = False

        if not SUMMARIZATION_AVAILABLE:
            self.logger.error("❌ Cannot start monitor: Summarization integration not available")
            self.summarization = None
        else:
            self.summarization = JARVISCursorSummarizationIntegration(project_root)

        self.workflow_transparency = None
        if WORKFLOW_TRANSPARENCY_AVAILABLE:
            try:
                self.workflow_transparency = JARVISWorkflowTransparencySystem(project_root)
            except Exception as e:
                self.logger.debug(f"Workflow transparency not available: {e}")

        # Track active conversations
        self.active_conversations: Dict[str, Dict[str, Any]] = {}

        self.logger.info("✅ JARVIS Cursor Summarization Monitor initialized")

    def start_monitoring(self):
        """Start continuous monitoring"""
        if not self.summarization:
            self.logger.error("❌ Cannot start: Summarization integration not available")
            return

        self.running = True
        self.logger.info("================================================================================")
        self.logger.info("JARVIS CURSOR SUMMARIZATION MONITOR STARTED")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info("Press Ctrl+C to stop")
        self.logger.info("================================================================================")

        try:
            while self.running:
                self._monitor_cycle()
                time.sleep(self.check_interval)
        except KeyboardInterrupt:
            self.stop_monitoring()
        except Exception as e:
            self.logger.error(f"❌ Monitor error: {e}", exc_info=True)
            self.stop_monitoring()

    def _monitor_cycle(self):
        """Single monitoring cycle"""
        self.logger.debug(f"Monitoring cycle: {datetime.now().isoformat()}")

        # Get active conversations from workflow transparency (if available)
        conversations = self._get_active_conversations()

        for conv_id, conv_data in conversations.items():
            try:
                # Monitor conversation
                message_count = conv_data.get('message_count', 0)
                estimated_tokens = conv_data.get('estimated_tokens', 0)
                files_included = conv_data.get('files_included', [])

                result = self.summarization.monitor_conversation(
                    conversation_id=conv_id,
                    message_count=message_count,
                    estimated_tokens=estimated_tokens,
                    files_included=files_included
                )

                # Update active conversations
                self.active_conversations[conv_id] = result['state']

                # Check if summarization is needed
                if result['should_summarize']:
                    self.logger.warning(f"⚠️  Summarization needed for {conv_id}: {result['reason']}")

                    # Trigger summarization
                    summarize_result = self.summarization.trigger_summarization(
                        conversation_id=conv_id,
                        method="auto"
                    )

                    if summarize_result['success']:
                        self.logger.info(f"✅ Summarization triggered for {conv_id}")
                    else:
                        self.logger.error(f"❌ Failed to trigger summarization: {summarize_result.get('error')}")

            except Exception as e:
                self.logger.error(f"❌ Error monitoring conversation {conv_id}: {e}", exc_info=True)

    def _get_active_conversations(self) -> Dict[str, Dict[str, Any]]:
        """
        Get active conversations from various sources

        This is a placeholder - in production, would integrate with:
        - Cursor IDE API (if available)
        - Workflow Transparency System
        - Chat history files
        """
        conversations = {}

        # Try to get from workflow transparency
        if self.workflow_transparency:
            try:
                # This would need to be implemented in workflow transparency
                # For now, we'll use a placeholder
                pass
            except Exception:
                pass

        # Fallback: Use summarization integration's tracked conversations
        if self.summarization:
            for conv_id, state in self.summarization.conversation_states.items():
                conversations[conv_id] = {
                    'message_count': state.message_count,
                    'estimated_tokens': state.estimated_tokens,
                    'files_included': state.files_included
                }

        return conversations

    def stop_monitoring(self):
        """Stop monitoring"""
        self.running = False
        self.logger.info("JARVIS CURSOR SUMMARIZATION MONITOR STOPPED")

    def get_monitor_status(self) -> Dict[str, Any]:
        """Get current monitor status"""
        return {
            "running": self.running,
            "check_interval": self.check_interval,
            "active_conversations": len(self.active_conversations),
            "conversations": self.active_conversations
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor Summarization Monitor")
        parser.add_argument("--start", action="store_true", help="Start monitoring")
        parser.add_argument("--interval", type=int, default=60, help="Check interval in seconds")
        parser.add_argument("--status", action="store_true", help="Show monitor status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = JARVISCursorSummarizationMonitor(project_root, check_interval=args.interval)

        if args.start:
            monitor.start_monitoring()
        elif args.status:
            status = monitor.get_monitor_status()
            import json
            print(json.dumps(status, indent=2))
        else:
            print("Usage:")
            print("  --start              : Start monitoring")
            print("  --interval <seconds> : Set check interval (default: 60)")
            print("  --status             : Show monitor status")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()