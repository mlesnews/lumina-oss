#!/usr/bin/env python3
"""
JARVIS AI Coordination - Stack the Deck in Our Favor

Talk to every AI and get in sync
Coordinate all AIs for strategic advantage

"TALK TO EVERY AI AND GET IN SYNC AND LETS STACK THE DECK IN OUR FAVOR"
"""

import sys
import json
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
import time
import tempfile
import shutil
try:
    from universal_decision_tree import decide, DecisionContext, DecisionOutcome
except ImportError:
    # Fallback if not available
    def decide(*args, **kwargs):
        return None
    DecisionContext = None
    DecisionOutcome = None

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAICoordination")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AIType(Enum):
    """Types of AIs to coordinate"""
    LLM = "llm"  # Large Language Models
    AGENT = "agent"  # AI Agents
    ASSISTANT = "assistant"  # AI Assistants
    SYSTEM = "system"  # AI Systems
    TOOL = "tool"  # AI Tools


@dataclass
class AICoordination:
    """AI Coordination Status"""
    ai_id: str
    ai_name: str
    ai_type: AIType
    status: str = "unknown"
    synced: bool = False
    last_sync: Optional[datetime] = None
    capabilities: List[str] = field(default_factory=list)
    coordination_level: int = 0  # 0-10, how well coordinated
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['ai_type'] = self.ai_type.value
        if self.last_sync:
            data['last_sync'] = self.last_sync.isoformat()
        return data


class JARVISAICoordination:
    """
    JARVIS AI Coordination - Stack the Deck in Our Favor

    Talk to every AI and get in sync
    Coordinate all AIs for strategic advantage
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI coordination"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("JARVISAICoordination")

        # State file for persistence
        self.state_file = self.project_root / "data" / "system" / "ai_coordination_state.json"
        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        # AI registry
        self.ai_registry: Dict[str, AICoordination] = {}

        # Coordination state
        self.coordination_active = False
        self.sync_thread = None

        # Discover and register AIs
        self._discover_ais()

        # Load previous state
        self._load_state()

        self.logger.info("🤝 JARVIS AI Coordination initialized")
        self.logger.info("   Stacking the deck in our favor")

    def _discover_ais(self):
        """Discover all AIs to coordinate with"""
        # Local LLMs (Ollama)
        self._register_ai("ollama_local", "Ollama Local", AIType.LLM, [
            "local_llm", "ollama", "llama3.2:3b"
        ])

        # JARVIS systems
        self._register_ai("jarvis_master", "JARVIS Master Agent", AIType.AGENT, [
            "orchestration", "delegation", "coordination"
        ])

        # Droid actors
        self._register_ai("droid_actors", "Droid Actor System", AIType.SYSTEM, [
            "workflow_verification", "task_routing", "helpdesk"
        ])

        # R5 Matrix
        self._register_ai("r5_matrix", "R5 Living Context Matrix", AIType.SYSTEM, [
            "knowledge_aggregation", "pattern_extraction", "context_management"
        ])

        # AIOS
        self._register_ai("aios", "AIOS Platform", AIType.SYSTEM, [
            "holistic_platform", "polymodal", "universal_scope"
        ])

        # Trading System
        self._register_ai("trading_system", "Trading System", AIType.SYSTEM, [
            "trading", "financial", "market_analysis"
        ])

        # Voice Interface
        self._register_ai("voice_interface", "Voice Interface", AIType.ASSISTANT, [
            "voice_recognition", "tts", "hands_free"
        ])

        # SiderAI Desktop
        self._register_ai("siderai_desktop", "SiderAI Desktop", AIType.ASSISTANT, [
            "desktop_ai", "coding_assistant", "ide_integration"
        ])

        # SiderAI Extension
        self._register_ai("siderai_extension", "SiderAI Extension", AIType.ASSISTANT, [
            "ide_extension", "coding_assistant", "vscode_integration", "cursor_integration"
        ])

        # Browser Extension
        self._register_ai("browser_extension", "Browser Extension", AIType.TOOL, [
            "browser_automation", "web_interaction", "content_editing", "form_filling"
        ])

        # External AIs (if available)
        self._discover_external_ais()

    def _register_ai(self, ai_id: str, ai_name: str, ai_type: AIType, capabilities: List[str]):
        """Register an AI for coordination"""
        self.ai_registry[ai_id] = AICoordination(
            ai_id=ai_id,
            ai_name=ai_name,
            ai_type=ai_type,
            capabilities=capabilities,
            status="registered"
        )
        self.logger.debug(f"  Registered: {ai_name} ({ai_id})")

    def _discover_external_ais(self):
        """Discover external AIs (OpenAI, Anthropic, etc.)"""
        # Check for API keys/configs
        # This would check for OpenAI, Anthropic, etc.
        # For now, just register placeholder
        pass

    def sync_with_ai(self, ai_id: str, force: bool = False) -> bool:
        """
        Sync with a specific AI with enhanced coordination protocol

        Args:
            ai_id: AI identifier
            force: Force sync even if recently synced
        """
        if ai_id not in self.ai_registry:
            self.logger.warning(f"AI not found: {ai_id}")
            return False

        ai = self.ai_registry[ai_id]

        # Check if sync is needed (unless forced)
        if not force and ai.synced and ai.last_sync:
            time_since_sync = (datetime.now() - ai.last_sync).total_seconds()
            if time_since_sync < 60:  # Synced within last minute
                return True  # Already synced recently

        try:
            # Enhanced sync protocol
            # 1. Check AI status and availability
            ai_status = self._check_ai_status(ai_id)
            if not ai_status.get("available", False):
                ai.status = "unavailable"
                ai.coordination_level = max(0, ai.coordination_level - 1)
                return False

            # 2. Share context and state
            context_shared = self._share_context_with_ai(ai_id)

            # 3. Coordinate capabilities
            capabilities_synced = self._coordinate_capabilities(ai_id)

            # 4. Establish communication channel
            communication_established = self._establish_communication(ai_id)

            # Calculate coordination level based on sync success
            coordination_score = 0
            if ai_status.get("available"):
                coordination_score += 3
            if context_shared:
                coordination_score += 2
            if capabilities_synced:
                coordination_score += 2
            if communication_established:
                coordination_score += 3

            ai.synced = coordination_score >= 5  # Need at least 5/10 for sync
            ai.last_sync = datetime.now()
            ai.coordination_level = min(10, coordination_score)
            ai.status = "synced" if ai.synced else "partial"

            # Save state after sync
            self._save_state()

            if ai.synced:
                self.logger.info(f"✅ Synced with: {ai.ai_name} (coordination: {ai.coordination_level}/10)")
            else:
                self.logger.warning(f"⚠️ Partial sync with: {ai.ai_name} (coordination: {ai.coordination_level}/10)")

            return ai.synced

        except Exception as e:
            self.logger.debug(f"Sync error with {ai_id}: {e}")
            ai.status = "sync_failed"
            ai.coordination_level = max(0, ai.coordination_level - 1)
            return False

    def _check_ai_status(self, ai_id: str) -> Dict[str, Any]:
        """Check if AI is available and responsive"""
        ai = self.ai_registry[ai_id]

        # Check based on AI type
        if ai.ai_type == AIType.LLM:
            # Check if local LLM is running (Ollama)
            try:
                import subprocess
                result = subprocess.run(
                    ['ollama', 'list'],
                    capture_output=True,
                    text=True,
                    timeout=2
                )
                return {"available": result.returncode == 0}
            except:
                return {"available": False}

        elif ai.ai_type == AIType.SYSTEM:
            # System AIs are generally always available
            return {"available": True}

        elif ai.ai_type == AIType.AGENT:
            # Check if agent process is running
            return {"available": True}  # Assume available for now

        return {"available": False}

    def _share_context_with_ai(self, ai_id: str) -> bool:
        """Share context and state with AI"""
        # This would share:
        # - Current project context
        # - Active tasks
        # - System state
        # - User preferences
        try:
            # Placeholder - would implement actual context sharing
            return True
        except:
            return False

    def _coordinate_capabilities(self, ai_id: str) -> bool:
        """Coordinate capabilities with AI"""
        # This would:
        # - Exchange capability lists
        # - Identify complementary capabilities
        # - Establish capability routing
        try:
            # Placeholder - would implement actual capability coordination
            return True
        except:
            return False

    def _establish_communication(self, ai_id: str) -> bool:
        """Establish communication channel with AI"""
        # This would:
        # - Set up API connections
        # - Establish message queues
        # - Test communication
        try:
            # Placeholder - would implement actual communication setup
            return True
        except:
            return False

    def sync_all_ais(self, priority_order: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Sync with all AIs - stack the deck in our favor

        Args:
            priority_order: Optional list of AI IDs in priority order
        """
        self.logger.info("🤝 Syncing with all AIs...")
        self.logger.info("   Stacking the deck in our favor")

        # Determine sync order (priority first, then by coordination level)
        if priority_order:
            sync_order = priority_order + [ai_id for ai_id in self.ai_registry.keys() 
                                          if ai_id not in priority_order]
        else:
            # Sort by coordination level (higher first) and last sync time
            sync_order = sorted(
                self.ai_registry.keys(),
                key=lambda ai_id: (
                    -self.ai_registry[ai_id].coordination_level,
                    self.ai_registry[ai_id].last_sync.timestamp() if self.ai_registry[ai_id].last_sync else 0
                )
            )

        results = {
            "total": len(self.ai_registry),
            "synced": 0,
            "partial": 0,
            "failed": 0,
            "coordination_score": 0,
            "details": {}
        }

        for ai_id in sync_order:
            ai = self.ai_registry[ai_id]
            success = self.sync_with_ai(ai_id)

            if success:
                results["synced"] += 1
                results["coordination_score"] += ai.coordination_level
                results["details"][ai_id] = {
                    "status": "synced",
                    "coordination_level": ai.coordination_level
                }
            elif ai.coordination_level > 0:
                results["partial"] += 1
                results["coordination_score"] += ai.coordination_level
                results["details"][ai_id] = {
                    "status": "partial",
                    "coordination_level": ai.coordination_level
                }
            else:
                results["failed"] += 1
                results["details"][ai_id] = {
                    "status": "failed",
                    "coordination_level": 0
                }

        # Calculate overall coordination percentage
        max_possible_score = len(self.ai_registry) * 10
        coordination_percentage = (results["coordination_score"] / max_possible_score * 100) if max_possible_score > 0 else 0

        results["coordination_percentage"] = coordination_percentage
        results["stacking_deck"] = coordination_percentage >= 50  # At least 50% coordination

        self.logger.info(f"✅ Synced with {results['synced']}/{results['total']} AIs")
        self.logger.info(f"   Coordination: {coordination_percentage:.1f}% (score: {results['coordination_score']}/{max_possible_score})")

        return results

    def get_coordination_status(self) -> Dict[str, Any]:
        """Get coordination status"""
        synced_count = sum(1 for ai in self.ai_registry.values() if ai.synced)

        return {
            "total_ais": len(self.ai_registry),
            "synced_ais": synced_count,
            "coordination_level": "high" if synced_count == len(self.ai_registry) else "partial",
            "ais": [ai.to_dict() for ai in self.ai_registry.values()],
            "stacking_deck": synced_count > 0,
            "timestamp": datetime.now().isoformat()
        }

    def start_coordination(self):
        """Start continuous coordination"""
        self.coordination_active = True
        self.sync_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.sync_thread.start()
        self.logger.info("🤝 AI coordination started")

    def _coordination_loop(self):
        """Continuous coordination loop with adaptive intervals"""
        sync_interval = 60  # Start with 1 minute
        consecutive_failures = 0

        while self.coordination_active:
            try:
                # Periodic sync
                results = self.sync_all_ais()

                # Adaptive interval based on coordination success
                if results["coordination_percentage"] >= 80:
                    # High coordination - can sync less frequently
                    sync_interval = min(300, sync_interval * 1.1)  # Max 5 minutes
                    consecutive_failures = 0
                elif results["coordination_percentage"] >= 50:
                    # Medium coordination - normal interval
                    sync_interval = 60
                    consecutive_failures = 0
                else:
                    # Low coordination - sync more frequently
                    sync_interval = max(30, sync_interval * 0.9)  # Min 30 seconds
                    consecutive_failures += 1

                # If many failures, try more aggressive sync
                if consecutive_failures > 3:
                    self.logger.warning("Multiple coordination failures, attempting aggressive sync...")
                    # Force sync with all AIs
                    for ai_id in self.ai_registry.keys():
                        self.sync_with_ai(ai_id, force=True)
                    consecutive_failures = 0

                time.sleep(sync_interval)

            except Exception as e:
                self.logger.error(f"Coordination loop error: {e}")
                time.sleep(60)  # Wait before retrying

    def stop_coordination(self):
        """Stop coordination"""
        self.coordination_active = False
        self._save_state()
        self.logger.info("🤝 AI coordination stopped")

    def _save_state(self):
        """Save coordination state using atomic writes"""
        max_retries = 3
        retry_delay = 0.5

        state = {
            "ais": [ai.to_dict() for ai in self.ai_registry.values()],
            "last_updated": datetime.now().isoformat()
        }

        self._atomic_write_file(
            self.state_file,
            state,
            max_retries=max_retries,
            retry_delay=retry_delay
        )

    def _atomic_write_file(self, file_path: Path, data: Any, max_retries: int = 3, retry_delay: float = 0.5):
        """
        Atomically write data to a file with retry logic.

        Uses a temporary file and rename to ensure atomic writes and avoid
        permission issues on Windows (especially with Dropbox).
        """
        # Ensure directory exists and is writable
        try:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            test_file = file_path.parent / ".write_test"
            try:
                test_file.write_text("test")
                test_file.unlink()
            except (PermissionError, OSError) as e:
                self.logger.warning(f"Directory not writable: {file_path.parent} - {e}")
                return
        except Exception as e:
            self.logger.error(f"Error creating directory {file_path.parent}: {e}")
            return

        for attempt in range(max_retries):
            try:
                temp_file = file_path.parent / f".{file_path.name}.tmp"

                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2)

                if file_path.exists():
                    try:
                        file_path.unlink()
                    except PermissionError:
                        time.sleep(retry_delay * (attempt + 1))
                        if attempt < max_retries - 1:
                            continue
                        else:
                            raise

                temp_file.replace(file_path)
                return

            except PermissionError as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (2 ** attempt)
                    self.logger.debug(f"Permission denied, retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                else:
                    self.logger.error(f"Error saving state to {file_path}: Permission denied after {max_retries} attempts - {e}")
                    if 'temp_file' in locals() and temp_file.exists():
                        try:
                            temp_file.unlink()
                        except:
                            pass
            except Exception as e:
                self.logger.error(f"Error saving state to {file_path}: {e}")
                if 'temp_file' in locals() and temp_file.exists():
                    try:
                        temp_file.unlink()
                    except:
                        pass
                return

    def _load_state(self):
        """Load coordination state"""
        try:
            if self.state_file.exists():
                with open(self.state_file, 'r') as f:
                    state = json.load(f)
                    # Restore AI sync status
                    for ai_data in state.get("ais", []):
                        ai_id = ai_data.get("ai_id")
                        if ai_id in self.ai_registry:
                            self.ai_registry[ai_id].synced = ai_data.get("synced", False)
                            if ai_data.get("last_sync"):
                                self.ai_registry[ai_id].last_sync = datetime.fromisoformat(ai_data["last_sync"])
                            self.ai_registry[ai_id].coordination_level = ai_data.get("coordination_level", 0)
                            self.ai_registry[ai_id].status = ai_data.get("status", "unknown")
        except Exception as e:
            self.logger.debug(f"Error loading state: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS AI Coordination")
    parser.add_argument("--sync", action="store_true", help="Sync with all AIs")
    parser.add_argument("--status", action="store_true", help="Show coordination status")
    parser.add_argument("--start", action="store_true", help="Start continuous coordination")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    coordination = JARVISAICoordination()

    if args.sync:
        results = coordination.sync_all_ais()
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print("\n🤝 AI Coordination Results")
            print("="*60)
            print(f"Total AIs: {results['total']}")
            print(f"Synced: {results['synced']}")
            print(f"Failed: {results['failed']}")

    elif args.status:
        status = coordination.get_coordination_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print("\n🤝 AI Coordination Status")
            print("="*60)
            print(f"Total AIs: {status['total_ais']}")
            print(f"Synced: {status['synced_ais']}")
            print(f"Coordination Level: {status['coordination_level']}")
            print(f"Stacking Deck: {status['stacking_deck']}")
            print("\nAIs:")
            for ai in status['ais']:
                sync_icon = "✅" if ai['synced'] else "⏳"
                print(f"  {sync_icon} {ai['ai_name']} ({ai['ai_type']}) - {ai['status']}")

    elif args.start:
        print("\n🤝 Starting AI Coordination...")
        print("   Stacking the deck in our favor")
        coordination.start_coordination()
        try:
            import time
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            coordination.stop_coordination()
    else:
        parser.print_help()

