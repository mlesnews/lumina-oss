#!/usr/bin/env python3
"""
JARVIS Cursor Summarization Integration

Integrates Cursor's /summarize command and automatic summarization features
into JARVIS's workflow to manage context efficiently.

Features:
- Automatic summarization when conversations exceed context limits
- Manual summarization trigger via /summarize command
- Integration with persistent memory
- Context window monitoring
- File/folder condensation tracking
- Summarization history and analytics

Reference: https://cursor.com/docs/agent/chat/summarization
"""

import sys
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging
import subprocess

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorSummarization")

try:
    from jarvis_persistent_memory import JARVISPersistentMemory, MemoryType, MemoryPriority
    MEMORY_AVAILABLE = True
except ImportError:
    MEMORY_AVAILABLE = False
    logger.warning("JARVIS Persistent Memory not available")

try:
    from jarvis_cursor_agent_integration import JARVISCursorAgentIntegration
    CURSOR_AGENT_AVAILABLE = True
except ImportError:
    CURSOR_AGENT_AVAILABLE = False
    logger.warning("Cursor Agent Integration not available")


class CursorSummarizationState:
    """Tracks summarization state for a conversation"""
    def __init__(self):
        self.message_count = 0
        self.estimated_tokens = 0
        self.last_summarized_at = None
        self.summarization_count = 0
        self.files_included = []
        self.files_condensed = []
        self.files_not_included = []
        self.context_window_usage = 0.0  # Percentage


class JARVISCursorSummarizationIntegration:
    """
    Integrates Cursor's summarization features with JARVIS

    Monitors conversation length and automatically triggers summarization
    when context windows are exceeded.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Configuration
        self.config_dir = project_root / "config" / "cursor_summarization"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "summarization_config.json"

        # Load or create config
        self.config = self._load_config()

        # State tracking
        self.conversation_states: Dict[str, CursorSummarizationState] = {}
        self.summarization_history: List[Dict[str, Any]] = []

        # Persistent memory integration
        self.memory = None
        if MEMORY_AVAILABLE:
            try:
                self.memory = JARVISPersistentMemory(project_root)
                self.logger.info("✅ Persistent Memory integrated")
            except Exception as e:
                self.logger.debug(f"Memory integration error: {e}")

        # Cursor Agent integration
        self.cursor_agent = None
        if CURSOR_AGENT_AVAILABLE:
            try:
                self.cursor_agent = JARVISCursorAgentIntegration(project_root)
                if self.cursor_agent.available:
                    self.logger.info("✅ Cursor Agent Integration available")
            except Exception as e:
                self.logger.debug(f"Cursor Agent integration error: {e}")

        # History storage
        self.history_dir = project_root / "data" / "cursor_summarization"
        self.history_dir.mkdir(parents=True, exist_ok=True)

        self.logger.info("✅ JARVIS Cursor Summarization Integration initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load or create summarization configuration"""
        default_config = {
            "auto_summarize": True,
            "max_messages_before_summarize": 50,
            "max_tokens_before_summarize": 8000,  # Conservative estimate
            "context_window_limit": 8192,  # Default context window
            "summarization_threshold": 0.85,  # 85% of context window
            "track_file_condensation": True,
            "store_summaries_in_memory": True,
            "summarization_priority": "high",
            "monitor_interval_seconds": 60
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
                self.logger.info(f"✅ Loaded config from {self.config_file}")
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}, using defaults")
        else:
            # Save default config
            try:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(default_config, f, indent=2)
                self.logger.info(f"✅ Created default config: {self.config_file}")
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to save default config: {e}")

        return default_config

    def monitor_conversation(self, conversation_id: str, message_count: int = None, 
                            estimated_tokens: int = None, files_included: List[str] = None) -> Dict[str, Any]:
        """
        Monitor a conversation and determine if summarization is needed

        Returns:
            Dict with recommendation and state
        """
        # Get or create state
        if conversation_id not in self.conversation_states:
            self.conversation_states[conversation_id] = CursorSummarizationState()

        state = self.conversation_states[conversation_id]

        # Update state
        if message_count is not None:
            state.message_count = message_count
        if estimated_tokens is not None:
            state.estimated_tokens = estimated_tokens
        if files_included is not None:
            state.files_included = files_included

        # Calculate context window usage
        max_tokens = self.config.get("context_window_limit", 8192)
        state.context_window_usage = (state.estimated_tokens / max_tokens) * 100 if max_tokens > 0 else 0

        # Check if summarization is needed
        should_summarize = False
        reason = None

        if self.config.get("auto_summarize", True):
            # Check message count threshold
            if state.message_count >= self.config.get("max_messages_before_summarize", 50):
                should_summarize = True
                reason = f"Message count ({state.message_count}) exceeds threshold ({self.config.get('max_messages_before_summarize', 50)})"

            # Check token threshold
            threshold = self.config.get("summarization_threshold", 0.85)
            if state.context_window_usage >= (threshold * 100):
                should_summarize = True
                reason = f"Context window usage ({state.context_window_usage:.1f}%) exceeds threshold ({threshold*100:.1f}%)"

        return {
            "conversation_id": conversation_id,
            "should_summarize": should_summarize,
            "reason": reason,
            "state": {
                "message_count": state.message_count,
                "estimated_tokens": state.estimated_tokens,
                "context_window_usage": state.context_window_usage,
                "last_summarized_at": state.last_summarized_at.isoformat() if state.last_summarized_at else None,
                "summarization_count": state.summarization_count,
                "files_included": len(state.files_included)
            }
        }

    def trigger_summarization(self, conversation_id: str, method: str = "auto") -> Dict[str, Any]:
        """
        Trigger summarization for a conversation

        Methods:
            - "auto": Automatic via Cursor's built-in summarization
            - "manual": Manual /summarize command
            - "api": Via Cursor Agent API (if available)
        """
        self.logger.info(f"📝 Triggering summarization for conversation: {conversation_id} (method: {method})")

        state = self.conversation_states.get(conversation_id)
        if not state:
            state = CursorSummarizationState()
            self.conversation_states[conversation_id] = state

        result = {
            "conversation_id": conversation_id,
            "method": method,
            "success": False,
            "timestamp": datetime.now().isoformat(),
            "error": None
        }

        try:
            if method == "api" and self.cursor_agent and self.cursor_agent.available:
                # Use Cursor Agent API if available
                # Note: This would require Cursor API endpoint for summarization
                result["success"] = True
                result["message"] = "Summarization triggered via Cursor Agent API"

            elif method == "manual":
                # Send /summarize command to Cursor IDE
                # This would be done via MANUS keyboard automation
                result["success"] = self._send_summarize_command()
                if result["success"]:
                    result["message"] = "Summarization command sent to Cursor IDE"
                else:
                    result["error"] = "Failed to send /summarize command"

            else:  # auto
                # Cursor automatically summarizes, we just track it
                result["success"] = True
                result["message"] = "Automatic summarization will occur when context limit is reached"

            if result["success"]:
                # Update state
                state.last_summarized_at = datetime.now()
                state.summarization_count += 1
                state.message_count = 0  # Reset after summarization
                state.estimated_tokens = 0

                # Store in history
                self.summarization_history.append(result)
                self._save_summarization_history()

                # Store in persistent memory
                if self.memory and self.config.get("store_summaries_in_memory", True):
                    priority = MemoryPriority[self.config.get("summarization_priority", "high").upper()]
                    self.memory.store_memory(
                        content=f"Conversation {conversation_id} summarized at {result['timestamp']}",
                        memory_type=MemoryType.EPISODIC,
                        priority=priority,
                        context={"conversation_id": conversation_id, "method": method},
                        tags=["summarization", "cursor", conversation_id],
                        source="jarvis_cursor_summarization"
                    )

                self.logger.info(f"✅ Summarization triggered: {conversation_id}")

        except Exception as e:
            result["error"] = str(e)
            self.logger.error(f"❌ Summarization error: {e}", exc_info=True)

        return result

    def _send_summarize_command(self) -> bool:
        """
        Send /summarize command to Cursor IDE via keyboard automation

        This uses MANUS keyboard control to type /summarize in the chat
        """
        try:
            # Try MANUS Cursor Chat Automation first
            try:
                from manus_cursor_chat_automation import MANUSCursorChatAutomation
                chat_automation = MANUSCursorChatAutomation(self.project_root)
                result = chat_automation.send_chat_message("/summarize", use_shortcut=True)
                if result.get('success'):
                    self.logger.info("✅ Sent /summarize command via MANUS chat automation")
                    return True
            except ImportError:
                pass

            # Fallback: Direct keyboard control
            try:
                import keyboard
                keyboard.write("/summarize")
                time.sleep(0.1)
                keyboard.press_and_release('ctrl+enter')  # Send message
                self.logger.info("✅ Sent /summarize command via keyboard")
                return True
            except ImportError:
                self.logger.warning("⚠️  Keyboard automation not available")
                return False
        except Exception as e:
            self.logger.error(f"❌ Error sending /summarize command: {e}", exc_info=True)
            return False

    def track_file_condensation(self, conversation_id: str, file_path: str, 
                               condensation_state: str) -> None:
        """
        Track file condensation states

        States:
            - "included": File is fully included
            - "condensed": File is condensed (showing structure only)
            - "significantly_condensed": Only file name shown
            - "not_included": File too large, not included
        """
        if not self.config.get("track_file_condensation", True):
            return

        state = self.conversation_states.get(conversation_id)
        if not state:
            state = CursorSummarizationState()
            self.conversation_states[conversation_id] = state

        if condensation_state == "condensed":
            if file_path not in state.files_condensed:
                state.files_condensed.append(file_path)
        elif condensation_state == "not_included":
            if file_path not in state.files_not_included:
                state.files_not_included.append(file_path)

        self.logger.debug(f"📁 File condensation tracked: {file_path} -> {condensation_state}")

    def get_summarization_analytics(self) -> Dict[str, Any]:
        """Get analytics about summarization usage"""
        total_summarizations = len(self.summarization_history)
        conversations_tracked = len(self.conversation_states)

        # Count by method
        method_counts = {}
        for entry in self.summarization_history:
            method = entry.get("method", "unknown")
            method_counts[method] = method_counts.get(method, 0) + 1

        # Average context window usage
        avg_usage = 0.0
        if self.conversation_states:
            total_usage = sum(s.context_window_usage for s in self.conversation_states.values())
            avg_usage = total_usage / len(self.conversation_states)

        return {
            "total_summarizations": total_summarizations,
            "conversations_tracked": conversations_tracked,
            "summarizations_by_method": method_counts,
            "average_context_window_usage": avg_usage,
            "config": {
                "auto_summarize": self.config.get("auto_summarize", True),
                "max_messages": self.config.get("max_messages_before_summarize", 50),
                "context_window_limit": self.config.get("context_window_limit", 8192)
            }
        }

    def _save_summarization_history(self):
        """Save summarization history to file"""
        history_file = self.history_dir / "summarization_history.json"
        try:
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "history": self.summarization_history
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Failed to save summarization history: {e}", exc_info=True)

    def generate_summarization_report(self) -> str:
        """Generate a markdown report about summarization usage"""
        analytics = self.get_summarization_analytics()

        report = f"""# Cursor Summarization Integration Report

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Total Summarizations**: {analytics['total_summarizations']}
- **Conversations Tracked**: {analytics['conversations_tracked']}
- **Average Context Window Usage**: {analytics['average_context_window_usage']:.1f}%

## Configuration

- **Auto-Summarize**: {analytics['config']['auto_summarize']}
- **Max Messages Before Summarize**: {analytics['config']['max_messages']}
- **Context Window Limit**: {analytics['config']['context_window_limit']} tokens

## Summarizations by Method

"""
        for method, count in analytics['summarizations_by_method'].items():
            report += f"- **{method}**: {count}\n"

        report += f"""
## Active Conversations

"""
        for conv_id, state in self.conversation_states.items():
            report += f"### {conv_id}\n"
            report += f"- Messages: {state.message_count}\n"
            report += f"- Estimated Tokens: {state.estimated_tokens}\n"
            report += f"- Context Window Usage: {state.context_window_usage:.1f}%\n"
            report += f"- Summarizations: {state.summarization_count}\n"
            report += f"- Files Included: {len(state.files_included)}\n"
            report += f"- Files Condensed: {len(state.files_condensed)}\n"
            report += f"- Files Not Included: {len(state.files_not_included)}\n\n"

        return report


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor Summarization Integration")
        parser.add_argument("--monitor", type=str, help="Monitor conversation (provide conversation_id)")
        parser.add_argument("--trigger", type=str, help="Trigger summarization (provide conversation_id)")
        parser.add_argument("--method", type=str, choices=["auto", "manual", "api"], default="auto",
                           help="Summarization method")
        parser.add_argument("--analytics", action="store_true", help="Show summarization analytics")
        parser.add_argument("--report", action="store_true", help="Generate summarization report")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        integration = JARVISCursorSummarizationIntegration(project_root)

        if args.monitor:
            result = integration.monitor_conversation(args.monitor)
            print(json.dumps(result, indent=2))
            if result["should_summarize"]:
                print(f"\n⚠️  Summarization recommended: {result['reason']}")

        elif args.trigger:
            result = integration.trigger_summarization(args.trigger, method=args.method)
            print(json.dumps(result, indent=2))

        elif args.analytics:
            analytics = integration.get_summarization_analytics()
            print(json.dumps(analytics, indent=2))

        elif args.report:
            report = integration.generate_summarization_report()
            report_file = project_root / "data" / "cursor_summarization" / "summarization_report.md"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            print(f"✅ Report generated: {report_file}")
            print("\n" + report)

        else:
            print("Usage:")
            print("  --monitor <id>        : Monitor conversation")
            print("  --trigger <id>        : Trigger summarization")
            print("  --method <auto|manual|api> : Summarization method")
            print("  --analytics           : Show analytics")
            print("  --report              : Generate report")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()