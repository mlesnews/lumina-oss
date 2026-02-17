#!/usr/bin/env python3
"""
Cursor Agent Mode Automation System

Comprehensive automation for all Cursor IDE agent chat menu modes with @auto mode support.
Automates: Agent, Plan, Debug, Ask, and evolves new modes as needed.

@MARVIN @JARVIS @TONY @MACE @GANDALF
Enhanced with NAS Proxy-Cache and full Lumina integration.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
import hashlib
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from nas_physics_cache import TieredPhysicsCache
    CACHE_AVAILABLE = True
except ImportError:
    CACHE_AVAILABLE = False

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorAgentModeAutomation")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AgentMode(Enum):
    """Agent mode types"""
    AGENT = "agent"
    PLAN = "plan"
    DEBUG = "debug"
    ASK = "ask"
    REFACTOR = "refactor"  # Future mode
    TEST = "test"  # Future mode
    REVIEW = "review"  # Future mode
    EXPLAIN = "explain"  # Future mode
    OPTIMIZE = "optimize"  # Future mode


class ModeIntentClassifier:
    """Classify user intent to determine appropriate agent mode"""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.mode_keywords = self._load_mode_keywords()
        self.cache = None

        # Initialize cache if available
        if CACHE_AVAILABLE and config.get('auto_mode', {}).get('enabled', True):
            try:
                cache_config = self._load_cache_config()
                self.cache = TieredPhysicsCache(cache_config)
            except Exception as e:
                logger.warning(f"Cache initialization failed: {e}")

    def _load_mode_keywords(self) -> Dict[str, List[str]]:
        """Load keywords for mode detection"""
        return {
            AgentMode.PLAN.value: [
                "plan", "design", "architecture", "design", "roadmap", "strategy",
                "structure", "layout", "outline", "blueprint", "schema", "model"
            ],
            AgentMode.DEBUG.value: [
                "debug", "fix", "error", "bug", "issue", "problem", "broken",
                "not working", "fails", "exception", "crash", "troubleshoot",
                "stack trace", "log", "diagnose"
            ],
            AgentMode.ASK.value: [
                "what", "how", "why", "when", "where", "explain", "tell me",
                "describe", "clarify", "information", "question", "answer"
            ],
            AgentMode.AGENT.value: []  # Default/fallback mode
        }

    def _load_cache_config(self) -> Dict[str, Any]:
        """Load cache configuration"""
        cache_config_file = project_root / "config" / "nas_proxy_cache_config.yaml"
        nas_ssh_config_file = project_root / "config" / "lumina_nas_ssh_config.json"

        nas_config = {
            'host': '<NAS_PRIMARY_IP>',
            'user': 'backupadm',
            'base_path': '/volume1/cache/cursor_agent_modes',
            'timeout': 30
        }

        # Load from configs (similar to other integrations)
        if nas_ssh_config_file.exists():
            try:
                with open(nas_ssh_config_file, 'r') as f:
                    ssh_config = json.load(f)
                    if 'nas' in ssh_config:
                        nas_config.update({
                            'host': ssh_config['nas'].get('host', nas_config['host']),
                            'user': ssh_config['nas'].get('username', nas_config['user']),
                            'timeout': ssh_config['nas'].get('timeout', nas_config['timeout'])
                        })
                        if 'password_source' in ssh_config['nas'] and ssh_config['nas']['password_source'] == 'azure_key_vault':
                            nas_config['vault_name'] = ssh_config['nas'].get('key_vault_name', 'jarvis-lumina')
                            nas_config['password_secret_name'] = ssh_config['nas'].get('password_secret_name', 'nas-password')
            except Exception as e:
                logger.debug(f"Could not load SSH config: {e}")

        return {
            'memory_limit': 256 * 1024 * 1024,  # 256MB
            'ssd_cache_dir': str(project_root / 'data' / 'cache' / 'cursor_agent_modes'),
            'ssd_limit': 5 * 1024 * 1024 * 1024,  # 5GB
            'nas_config': nas_config
        }

    def classify_intent(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> AgentMode:
        """
        Classify user intent and determine appropriate mode.

        Args:
            user_message: User's message/query
            context: Optional context (open files, errors, etc.)

        Returns:
            Recommended AgentMode
        """
        # Check cache first
        cache_key = None
        if self.cache:
            try:
                message_hash = hashlib.md5(user_message.lower().encode()).hexdigest()
                cache_key = f"mode_classify_{message_hash}"
                cached_mode = self.cache.get(cache_key)
                if cached_mode:
                    return AgentMode(cached_mode)
            except Exception:
                pass

        # Classify based on keywords and context
        message_lower = user_message.lower()

        # Check for mode-specific keywords
        mode_scores = {}
        for mode, keywords in self.mode_keywords.items():
            score = sum(1 for keyword in keywords if keyword in message_lower)
            if score > 0:
                mode_scores[mode] = score

        # Context-based classification
        if context:
            # If there are errors, prefer DEBUG mode
            if context.get('has_errors') or context.get('error_messages'):
                mode_scores[AgentMode.DEBUG.value] = mode_scores.get(AgentMode.DEBUG.value, 0) + 2

            # If asking for explanation, prefer ASK mode
            if any(word in message_lower for word in ['what', 'how', 'why', 'explain']):
                mode_scores[AgentMode.ASK.value] = mode_scores.get(AgentMode.ASK.value, 0) + 2

        # Select mode with highest score, default to AGENT
        if mode_scores:
            selected_mode = max(mode_scores.items(), key=lambda x: x[1])[0]
            mode = AgentMode(selected_mode)
        else:
            mode = AgentMode.AGENT  # Default fallback

        # Cache the result
        if self.cache and cache_key:
            try:
                self.cache.put(
                    cache_key,
                    mode.value,
                    physics_domain="cursor_agent_modes",
                    ttl_seconds=3600,  # 1 hour
                    metadata={"message_length": len(user_message)}
                )
            except Exception:
                pass

        return mode


class CursorAgentModeAutomation:
    """
    Comprehensive automation system for Cursor IDE agent modes.

    Handles:
    - Automatic mode detection and switching
    - Mode-specific processing
    - Integration with all Lumina systems
    - Mode evolution and new mode support
    """

    def __init__(self, config_path: Optional[Path] = None):
        """Initialize automation system"""
        self.config_path = config_path or (project_root / "config" / "cursor_agent_modes.json")
        self.config = self._load_config()
        self.intent_classifier = ModeIntentClassifier(self.config)
        self.cache = self.intent_classifier.cache
        self.logger = get_logger("CursorAgentModeAutomation")

        # Initialize mode handlers
        self.mode_handlers = self._initialize_mode_handlers()

        self.logger.info("✅ Cursor Agent Mode Automation initialized")

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")

        # Return default config
        return {
            "auto_mode": {"enabled": True, "comprehensive": True, "robust": True},
            "modes": {}
        }

    def _initialize_mode_handlers(self) -> Dict[AgentMode, Dict[str, Any]]:
        """Initialize handlers for each mode"""
        handlers = {}

        for mode_name, mode_config in self.config.get("modes", {}).items():
            try:
                mode = AgentMode(mode_name)
                handlers[mode] = {
                    "config": mode_config,
                    "enabled": mode_config.get("enabled", True),
                    "auto_mode": mode_config.get("auto_mode", {}),
                    "capabilities": mode_config.get("capabilities", []),
                    "integrations": mode_config.get("integrations", {})
                }
            except ValueError:
                # Unknown mode, skip
                continue

        return handlers

    def detect_mode(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> AgentMode:
        """
        Detect appropriate mode for user message.

        Args:
            user_message: User's message/query
            context: Optional context information

        Returns:
            Recommended AgentMode
        """
        auto_mode = self.config.get("auto_mode", {})
        if not auto_mode.get("enabled", True):
            return AgentMode.AGENT  # Default if auto mode disabled

        # Use intent classifier
        mode = self.intent_classifier.classify_intent(user_message, context)

        self.logger.debug(f"Detected mode: {mode.value} for message: {user_message[:50]}...")
        return mode

    def process_with_mode(
        self,
        mode: AgentMode,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process user message with specific mode.

        Args:
            mode: Agent mode to use
            user_message: User's message
            context: Optional context

        Returns:
            Processing result with mode-specific handling
        """
        handler = self.mode_handlers.get(mode)
        if not handler or not handler["enabled"]:
            # Fallback to agent mode
            mode = AgentMode.AGENT
            handler = self.mode_handlers.get(mode, {})

        mode_config = handler.get("config", {})
        capabilities = handler.get("capabilities", [])
        integrations = handler.get("integrations", {})

        # Prepare mode-specific context
        mode_context = {
            "mode": mode.value,
            "mode_name": mode_config.get("name", mode.value),
            "mode_description": mode_config.get("description", ""),
            "capabilities": capabilities,
            "integrations": integrations,
            "user_message": user_message,
            "context": context or {},
            "timestamp": datetime.now().isoformat()
        }

        # Apply mode-specific processing
        result = {
            "mode": mode.value,
            "mode_name": mode_config.get("name", mode.value),
            "processed": True,
            "context": mode_context,
            "capabilities_available": capabilities,
            "integrations_enabled": integrations
        }

        self.logger.info(f"Processed with mode: {mode.value}")
        return result

    def auto_process(self, user_message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Automatically detect mode and process message.

        This is the main @auto mode handler - fully comprehensive and robust.

        Args:
            user_message: User's message
            context: Optional context

        Returns:
            Complete processing result
        """
        auto_mode = self.config.get("auto_mode", {})
        if not auto_mode.get("enabled", True):
            # Auto mode disabled, use default agent mode
            return self.process_with_mode(AgentMode.AGENT, user_message, context)

        # Detect mode
        detected_mode = self.detect_mode(user_message, context)

        # Process with detected mode
        result = self.process_with_mode(detected_mode, user_message, context)

        # Add auto mode metadata
        result["auto_mode"] = {
            "enabled": True,
            "mode_detected": detected_mode.value,
            "comprehensive": auto_mode.get("comprehensive", True),
            "robust": auto_mode.get("robust", True)
        }

        return result

    def get_available_modes(self) -> List[Dict[str, Any]]:
        """Get list of all available modes"""
        modes = []
        for mode, handler in self.mode_handlers.items():
            if handler["enabled"]:
                mode_config = handler["config"]
                modes.append({
                    "mode": mode.value,
                    "name": mode_config.get("name", mode.value),
                    "description": mode_config.get("description", ""),
                    "capabilities": handler["capabilities"],
                    "auto_mode_enabled": handler["auto_mode"].get("enabled", False)
                })
        return modes

    def evolve_mode(self, mode_name: str, mode_config: Dict[str, Any]) -> bool:
        """
        Evolve/create new mode dynamically.

        Args:
            mode_name: Name of new mode
            mode_config: Configuration for new mode

        Returns:
            True if mode was successfully added
        """
        try:
            # Add to config
            if "modes" not in self.config:
                self.config["modes"] = {}

            self.config["modes"][mode_name] = mode_config

            # Save config
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

            # Reload handlers
            self.mode_handlers = self._initialize_mode_handlers()

            self.logger.info(f"✅ Evolved new mode: {mode_name}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to evolve mode {mode_name}: {e}")
            return False

    def get_mode_statistics(self) -> Dict[str, Any]:
        """Get statistics about modes"""
        total_modes = len(self.mode_handlers)
        active_modes = sum(1 for h in self.mode_handlers.values() if h["enabled"])

        return {
            "total_modes": total_modes,
            "active_modes": active_modes,
            "auto_mode_enabled": self.config.get("auto_mode", {}).get("enabled", False),
            "modes": [mode.value for mode in self.mode_handlers.keys()]
        }


def main():
    """Main entry point for testing"""
    print("🤖 Cursor Agent Mode Automation System")
    print("=" * 60)

    automation = CursorAgentModeAutomation()

    # Test mode detection
    test_messages = [
        ("How do I implement a new feature?", {}),
        ("There's a bug in my code", {"has_errors": True}),
        ("Plan the architecture for this system", {}),
        ("What does this function do?", {})
    ]

    print("\n📋 Mode Detection Tests:")
    for message, context in test_messages:
        mode = automation.detect_mode(message, context)
        print(f"  '{message[:40]}...' → {mode.value.upper()}")

    # Test auto processing
    print("\n🔄 Auto Mode Processing Tests:")
    for message, context in test_messages[:2]:
        result = automation.auto_process(message, context)
        print(f"  Mode: {result['mode']}, Auto: {result.get('auto_mode', {}).get('mode_detected')}")

    # Show available modes
    print("\n📊 Available Modes:")
    modes = automation.get_available_modes()
    for mode_info in modes:
        print(f"  • {mode_info['name']} ({mode_info['mode']}): {mode_info['description'][:50]}...")

    # Show statistics
    stats = automation.get_mode_statistics()
    print(f"\n📈 Statistics:")
    print(f"  Total modes: {stats['total_modes']}")
    print(f"  Active modes: {stats['active_modes']}")
    print(f"  Auto mode enabled: {stats['auto_mode_enabled']}")


if __name__ == "__main__":



    main()