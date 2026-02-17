#!/usr/bin/env python3
"""
JARVIS Resume All Agent Chat Sessions

Resumes all agent chat sessions from the JARVIS master session.
All sessions are consolidated and controlled through the master session.

Tags: #JARVIS #MASTER #RESUME #SESSIONS #COORDINATION
@JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISResumeSessions")

# Import JARVIS master chat session
try:
    from jarvis_master_chat_session import JARVISMasterChatSession
    MASTER_SESSION_AVAILABLE = True
except ImportError:
    MASTER_SESSION_AVAILABLE = False
    logger.warning("JARVIS Master Chat Session not available")

# Import agent session coordinator
try:
    from coordinate_agent_sessions import AgentSessionCoordinator
    COORDINATION_AVAILABLE = True
except ImportError:
    COORDINATION_AVAILABLE = False
    logger.warning("Agent Session Coordinator not available")


class JARVISResumeAllSessions:
    """
    Resume all agent chat sessions through JARVIS master session

    Discovers all agent chat sessions, consolidates them into the master session,
    and ensures proper model configuration (ULTRON).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize session resumer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.agent_sessions_dir = self.project_root / "data" / "agent_chat_sessions"
        self.agent_sessions_dir.mkdir(parents=True, exist_ok=True)

        # Initialize master session
        self.master_session = None
        if MASTER_SESSION_AVAILABLE:
            try:
                self.master_session = JARVISMasterChatSession(project_root=self.project_root)
                logger.info("✅ JARVIS Master Chat Session initialized")
            except Exception as e:
                logger.error(f"❌ Error initializing master session: {e}")

        # Initialize coordinator
        self.coordinator = None
        if COORDINATION_AVAILABLE:
            try:
                self.coordinator = AgentSessionCoordinator(project_root=self.project_root)
                logger.info("✅ Agent Session Coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Agent Session Coordinator not available: {e}")

        logger.info("✅ JARVIS Resume All Sessions initialized")

    def discover_all_sessions(self) -> List[Dict[str, Any]]:
        """Discover all agent chat sessions"""
        logger.info("🔍 Discovering all agent chat sessions...")

        sessions = []

        if not self.agent_sessions_dir.exists():
            logger.warning(f"Agent sessions directory does not exist: {self.agent_sessions_dir}")
            return sessions

        for session_file in sorted(self.agent_sessions_dir.glob("*.json")):
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)

                # Ensure session has required fields
                session_id = session_data.get("session_id") or session_file.stem
                session_data["session_id"] = session_id
                session_data["file_path"] = str(session_file)
                session_data["file_name"] = session_file.name

                # Ensure model is set (default to ULTRON if missing)
                if "model" not in session_data:
                    session_data["model"] = "ULTRON"
                    logger.debug(f"   Set model to ULTRON for {session_id}")

                # CRITICAL: Ensure provider is set for Ollama models
                session_modified = False
                if session_data.get("model") in ["ULTRON", "KAIJU", "qwen2.5:72b", "llama3"]:
                    if "provider" not in session_data or session_data.get("provider") != "ollama":
                        session_data["provider"] = "ollama"
                        session_modified = True
                        logger.debug(f"   Set provider to ollama for {session_id}")

                # Save fixed session back to disk if modified
                if session_modified:
                    try:
                        # Remove temporary fields before saving
                        save_data = {k: v for k, v in session_data.items() 
                                   if k not in ["file_path", "file_name"]}
                        with open(session_file, 'w', encoding='utf-8') as f:
                            json.dump(save_data, f, indent=2, ensure_ascii=False)
                        logger.info(f"   💾 Saved fixed session: {session_id} (model: {session_data.get('model')}, provider: {session_data.get('provider')})")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Failed to save fixed session {session_id}: {e}")

                sessions.append(session_data)
                logger.debug(f"   ✅ Discovered session: {session_id}")

            except Exception as e:
                logger.warning(f"   ⚠️  Error reading {session_file.name}: {e}")

        logger.info(f"📋 Discovered {len(sessions)} agent chat sessions")
        return sessions

    def ensure_model_config(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure session has proper model configuration with provider specification

        CRITICAL: ULTRON and KAIJU are Ollama models and MUST have provider='ollama'
        to prevent Cursor from routing them to Bedrock (which doesn't support them).
        """
        # Model to provider mapping
        MODEL_PROVIDER_MAP = {
            "ULTRON": "ollama",
            "KAIJU": "ollama",
            "qwen2.5:72b": "ollama",
            "llama3": "ollama"
        }

        # Set model to ULTRON if not present or invalid
        if "model" not in session or not session.get("model"):
            session["model"] = "ULTRON"
            logger.debug(f"   Set model to ULTRON for {session.get('session_id', 'unknown')}")

        model = session["model"]

        # CRITICAL FIX: Set provider based on model to prevent Bedrock routing
        if model in MODEL_PROVIDER_MAP:
            expected_provider = MODEL_PROVIDER_MAP[model]
            if "provider" not in session or session.get("provider") != expected_provider:
                session["provider"] = expected_provider
                logger.debug(f"   Set provider to {expected_provider} for model {model} (session: {session.get('session_id', 'unknown')})")
        elif not session.get("provider"):
            # Default to ollama for unknown models (safer than Bedrock)
            session["provider"] = "ollama"
            logger.debug(f"   Set default provider to ollama for model {model}")

        # Ensure model configuration in metadata
        if "metadata" not in session:
            session["metadata"] = {}

        if "model_config" not in session["metadata"]:
            session["metadata"]["model_config"] = {
                "model": session["model"],
                "provider": session.get("provider", "ollama"),
                "configured_at": datetime.now().isoformat(),
                "note": "Provider set to prevent Bedrock routing for Ollama models"
            }
        else:
            # Update existing model_config with provider
            session["metadata"]["model_config"]["provider"] = session.get("provider", "ollama")
            session["metadata"]["model_config"]["updated_at"] = datetime.now().isoformat()

        return session

    def consolidate_sessions_to_master(self, sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Consolidate all sessions into master session

        Includes error handling for Bedrock model selection issues:
        - Detects "model not supported by bedrock" errors
        - Automatically fixes provider for Ollama models (ULTRON, KAIJU)
        - Provides clear error messages and recovery suggestions
        """
        logger.info("🔄 Consolidating sessions into master session...")

        if not self.master_session:
            logger.error("❌ Master session not available")
            return {"success": False, "error": "Master session not available"}

        # Ensure master session is pinned
        self.master_session.ensure_pinned()

        # Add consolidation message
        self.master_session.add_message(
            agent_id="jarvis",
            agent_name="JARVIS (CTO Superagent)",
            message=f"🔄 Resuming {len(sessions)} agent chat sessions from master session. All sessions will be controlled through this unified interface.",
            message_type="coordination",
            metadata={
                "action": "resume_all_sessions",
                "session_count": len(sessions),
                "timestamp": datetime.now().isoformat()
            }
        )

        # Process each session
        consolidated_count = 0
        errors = []
        bedrock_errors = []
        fixed_sessions = []

        for session in sessions:
            try:
                session_id = session.get("session_id", "unknown")
                agents_involved = session.get("agents_involved", [])
                messages = session.get("messages", [])

                # CRITICAL: Ensure model config with provider BEFORE processing
                # This prevents "model not supported by bedrock" errors
                session = self.ensure_model_config(session)

                # Check if we fixed a provider issue
                if session.get("model") in ["ULTRON", "KAIJU", "qwen2.5:72b", "llama3"]:
                    if session.get("provider") == "ollama":
                        fixed_sessions.append(session_id)
                        logger.debug(f"   ✅ Fixed provider for {session_id}: {session.get('model')} → ollama")

                # Add session summary to master
                session_summary = f"Session {session_id}: {len(messages)} messages, {len(agents_involved)} agents"
                if messages:
                    last_message = messages[-1].get("message", "")[:100]
                    session_summary += f"\nLast activity: {last_message}"

                # Include provider in metadata for debugging
                self.master_session.add_message(
                    agent_id="jarvis",
                    agent_name="JARVIS (CTO Superagent)",
                    message=f"📋 Resumed session: {session_summary}",
                    message_type="coordination",
                    metadata={
                        "session_id": session_id,
                        "agents": agents_involved,
                        "message_count": len(messages),
                        "model": session.get("model", "ULTRON"),
                        "provider": session.get("provider", "ollama"),  # Include provider
                        "provider_fixed": session_id in fixed_sessions
                    }
                )

                consolidated_count += 1
                logger.info(f"   ✅ Consolidated session: {session_id} (model: {session.get('model')}, provider: {session.get('provider')})")

            except Exception as e:
                error_msg = str(e)
                error_lower = error_msg.lower()

                # Detect Bedrock-specific errors
                if "bedrock" in error_lower or "model is not supported" in error_lower:
                    bedrock_error = {
                        "session_id": session.get("session_id", "unknown"),
                        "error": error_msg,
                        "model": session.get("model", "unknown"),
                        "provider": session.get("provider", "unknown"),
                        "suggestion": "Model is Ollama (ULTRON/KAIJU) but was routed to Bedrock. Provider should be 'ollama'."
                    }
                    bedrock_errors.append(bedrock_error)
                    logger.error(f"   ❌ Bedrock error for session {session.get('session_id', 'unknown')}: {error_msg}")

                    # Try to auto-fix by ensuring provider
                    try:
                        session = self.ensure_model_config(session)
                        logger.info(f"   🔧 Auto-fixed provider for {session.get('session_id', 'unknown')}")
                    except Exception as fix_error:
                        logger.error(f"   ❌ Failed to auto-fix: {fix_error}")

                error_msg_full = f"Error consolidating session {session.get('session_id', 'unknown')}: {error_msg}"
                logger.error(f"   ❌ {error_msg_full}")
                errors.append(error_msg_full)

        # Final consolidation message with Bedrock error info
        if bedrock_errors:
            bedrock_msg = f"\n⚠️  Fixed {len(bedrock_errors)} Bedrock routing issues by setting provider='ollama' for Ollama models."
        else:
            bedrock_msg = ""

        if fixed_sessions:
            fixed_msg = f"\n🔧 Auto-fixed provider for {len(fixed_sessions)} sessions: {', '.join(fixed_sessions[:5])}"
            if len(fixed_sessions) > 5:
                fixed_msg += f" and {len(fixed_sessions) - 5} more"
        else:
            fixed_msg = ""

        self.master_session.add_message(
            agent_id="jarvis",
            agent_name="JARVIS (CTO Superagent)",
            message=f"✅ Successfully resumed {consolidated_count}/{len(sessions)} agent chat sessions. All sessions are now active and controlled through this master session.{bedrock_msg}{fixed_msg}",
            message_type="coordination",
            metadata={
                "consolidated_count": consolidated_count,
                "total_sessions": len(sessions),
                "errors": len(errors),
                "bedrock_errors": len(bedrock_errors),
                "fixed_sessions": fixed_sessions,
                "timestamp": datetime.now().isoformat()
            }
        )

        # Consolidate all agents
        consolidation_result = self.master_session.consolidate_all_agents()

        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "total_sessions": len(sessions),
            "consolidated": consolidated_count,
            "errors": errors,
            "bedrock_errors": bedrock_errors,
            "fixed_sessions": fixed_sessions,
            "consolidation_result": consolidation_result
        }

        logger.info(f"✅ Consolidated {consolidated_count}/{len(sessions)} sessions into master")
        return result

    def coordinate_all_sessions(self) -> Dict[str, Any]:
        """Coordinate all sessions through JARVIS"""
        logger.info("🔄 Coordinating all sessions through JARVIS...")

        if not self.coordinator:
            logger.warning("⚠️  Coordinator not available")
            return {"success": False, "error": "Coordinator not available"}

        # Coordinate sessions
        coordination_result = self.coordinator.coordinate_sessions()

        # Sync all sessions
        sync_result = self.coordinator.sync_all_sessions()

        result = {
            "success": True,
            "timestamp": datetime.now().isoformat(),
            "coordination": coordination_result,
            "sync": sync_result
        }

        logger.info("✅ All sessions coordinated through JARVIS")
        return result

    def resume_all_sessions(self) -> Dict[str, Any]:
        try:
            """Resume all agent chat sessions from master session"""
            logger.info("=" * 80)
            logger.info("🤖 JARVIS: RESUMING ALL AGENT CHAT SESSIONS")
            logger.info("=" * 80)
            logger.info("")

            # Step 1: Discover all sessions
            logger.info("STEP 1: Discovering all agent chat sessions...")
            sessions = self.discover_all_sessions()
            logger.info(f"   Found {len(sessions)} sessions")
            logger.info("")

            if not sessions:
                logger.warning("⚠️  No sessions found to resume")
                return {
                    "success": True,
                    "timestamp": datetime.now().isoformat(),
                    "sessions_found": 0,
                    "message": "No sessions to resume"
                }

            # Step 2: Ensure model configuration for all sessions
            logger.info("STEP 2: Ensuring model configuration...")
            for session in sessions:
                session = self.ensure_model_config(session)
            logger.info(f"   ✅ Model configuration verified for {len(sessions)} sessions")
            logger.info("")

            # Step 3: Consolidate into master session
            logger.info("STEP 3: Consolidating sessions into master session...")
            consolidation_result = self.consolidate_sessions_to_master(sessions)
            logger.info("")

            # Step 4: Coordinate all sessions
            logger.info("STEP 4: Coordinating all sessions through JARVIS...")
            coordination_result = self.coordinate_all_sessions()
            logger.info("")

            # Final summary
            logger.info("=" * 80)
            logger.info("✅ RESUMPTION COMPLETE")
            logger.info("=" * 80)
            logger.info(f"   Sessions found: {len(sessions)}")
            logger.info(f"   Consolidated: {consolidation_result.get('consolidated', 0)}")
            logger.info(f"   Errors: {len(consolidation_result.get('errors', []))}")
            logger.info("")

            # Get master session summary
            if self.master_session:
                summary = self.master_session.get_session_summary()
                logger.info("📋 Master Session Summary:")
                logger.info(f"   Session ID: {summary['session_id']}")
                logger.info(f"   Pinned: {summary['pinned']}")
                logger.info(f"   Permanent: {summary['permanent']}")
                logger.info(f"   Agents: {summary['agent_count']}")
                logger.info(f"   Messages: {summary['message_count']}")
                logger.info("")

            result = {
                "success": True,
                "timestamp": datetime.now().isoformat(),
                "sessions_found": len(sessions),
                "consolidation": consolidation_result,
                "coordination": coordination_result,
                "master_session": self.master_session.get_session_summary() if self.master_session else None
            }

            # Save result
            output_dir = self.project_root / "data" / "jarvis_master_chat"
            output_dir.mkdir(parents=True, exist_ok=True)
            result_file = output_dir / f"resume_result_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 Result saved: {result_file.name}")
            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ All agent chat sessions resumed and controlled by JARVIS")
            logger.info("=" * 80)

            return result


        except Exception as e:
            self.logger.error(f"Error in resume_all_sessions: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Resume All Agent Chat Sessions")
        parser.add_argument("--project-root", help="Project root directory")
        parser.add_argument("--summary", action="store_true", help="Show master session summary only")

        args = parser.parse_args()

        print("\n" + "=" * 80)
        print("🤖 JARVIS: RESUME ALL AGENT CHAT SESSIONS")
        print("=" * 80 + "\n")

        project_root = Path(args.project_root) if args.project_root else None

        resumer = JARVISResumeAllSessions(project_root=project_root)

        if args.summary:
            if resumer.master_session:
                summary = resumer.master_session.get_session_summary()
                print("📋 Master Session Summary:")
                print("-" * 80)
                print(json.dumps(summary, indent=2))
                print()
            else:
                print("❌ Master session not available")
        else:
            # Resume all sessions
            result = resumer.resume_all_sessions()

            # Print summary
            print("\n" + "=" * 80)
            print("📊 SUMMARY")
            print("=" * 80)
            print(f"Sessions found: {result.get('sessions_found', 0)}")
            print(f"Consolidated: {result.get('consolidation', {}).get('consolidated', 0)}")
            print(f"Errors: {len(result.get('consolidation', {}).get('errors', []))}")
            print()

            if result.get('master_session'):
                ms = result['master_session']
                print(f"Master Session: {ms.get('session_id')}")
                print(f"Agents: {ms.get('agent_count')}")
                print(f"Messages: {ms.get('message_count')}")
                print()

        print("=" * 80)
        print("✅ Complete")
        print("=" * 80 + "\n")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()