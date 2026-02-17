#!/usr/bin/env python3
"""
Virtual Assistant Metrics Integration

Extends all metrics, GPU, phone, and HUD functionality to ALL virtual assistants:
- Kenny
- Jarvis (all versions)
- Iron Man virtual assistant
- Ace (Armory Crate virtual assistant)
- Gandalf
- Tony Stark
- Mace Windu
- All avatars, clones, personal assistants
- Jedi Masters (Jedi High Council members)

Uses Iron Man and Ace as templates for all other assistants.

@VIRTUAL_ASSISTANT @METRICS @HUD @TEMPLATE @AVATAR @CLONE @JEDI
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
logger = get_logger("virtual_assistant_metrics_integration")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import metrics systems
try:
    from jarvis_live_metrics_dashboard import LiveMetricsDashboard
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False

try:
    from jarvis_hud_system import JARVISHUDSystem
    HUD_AVAILABLE = True
except ImportError:
    HUD_AVAILABLE = False

try:
    from jarvis_hud_metrics_integration import JARVISHUDMetricsIntegration
    HUD_METRICS_AVAILABLE = True
except ImportError:
    HUD_METRICS_AVAILABLE = False


class VirtualAssistantType:
    """Virtual assistant types"""
    KENNY = "kenny"
    JARVIS = "jarvis"
    IRON_MAN = "iron_man"
    ACE = "ace"
    GANDALF = "gandalf"
    TONY_STARK = "tony_stark"
    MACE_WINDU = "mace_windu"
    JEDI_MASTER = "jedi_master"
    JEDI_COUNCIL = "jedi_council"
    AVATAR = "avatar"
    CLONE = "clone"
    PERSONAL_ASSISTANT = "personal_assistant"


@dataclass
class VirtualAssistantConfig:
    """Virtual assistant configuration"""
    assistant_id: str
    assistant_name: str
    assistant_type: str
    template: str  # "iron_man" or "ace"
    metrics_enabled: bool = True
    hud_enabled: bool = True
    gpu_metrics: bool = True
    phone_metrics: bool = True
    display_style: str = "iron_man"  # iron_man or ace
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            **field(default_factory=dict).default_factory(),
            "assistant_id": self.assistant_id,
            "assistant_name": self.assistant_name,
            "assistant_type": self.assistant_type,
            "template": self.template,
            "metrics_enabled": self.metrics_enabled,
            "hud_enabled": self.hud_enabled,
            "gpu_metrics": self.gpu_metrics,
            "phone_metrics": self.phone_metrics,
            "display_style": self.display_style,
            "metadata": self.metadata
        }


class VirtualAssistantMetricsIntegration:
    """
    Virtual Assistant Metrics Integration

    Extends metrics, GPU, phone, and HUD functionality to ALL virtual assistants.
    Uses Iron Man and Ace as templates.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize virtual assistant metrics integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("VAMetricsIntegration")

        # Systems
        self.metrics_dashboard = None
        self.jarvis_hud = None
        self.hud_metrics = None

        # Virtual assistant registry
        self.assistants: Dict[str, VirtualAssistantConfig] = {}

        # Initialize systems
        self._initialize_systems()

        # Register all virtual assistants
        self._register_all_assistants()

        self.logger.info("=" * 80)
        self.logger.info("🤖 VIRTUAL ASSISTANT METRICS INTEGRATION")
        self.logger.info("=" * 80)
        self.logger.info(f"   Registered Assistants: {len(self.assistants)}")
        self.logger.info("=" * 80)

    def _initialize_systems(self):
        """Initialize metrics and HUD systems"""
        # Initialize metrics dashboard
        if METRICS_AVAILABLE:
            try:
                self.metrics_dashboard = LiveMetricsDashboard()
                self.logger.info("✅ Metrics Dashboard: INITIALIZED")
            except Exception as e:
                self.logger.warning(f"⚠️  Metrics Dashboard initialization failed: {e}")

        # Initialize JARVIS HUD
        if HUD_AVAILABLE:
            try:
                self.jarvis_hud = JARVISHUDSystem(project_root=self.project_root)
                self.logger.info("✅ JARVIS HUD: INITIALIZED")
            except Exception as e:
                self.logger.warning(f"⚠️  JARVIS HUD initialization failed: {e}")

        # Initialize HUD metrics integration
        if HUD_METRICS_AVAILABLE:
            try:
                self.hud_metrics = JARVISHUDMetricsIntegration(project_root=self.project_root)
                self.logger.info("✅ HUD Metrics Integration: INITIALIZED")
            except Exception as e:
                self.logger.warning(f"⚠️  HUD Metrics Integration initialization failed: {e}")

    def _register_all_assistants(self):
        """Register all virtual assistants"""
        # Core assistants (using Iron Man and Ace as templates)
        self._register_assistant("kenny", "Kenny", VirtualAssistantType.KENNY, "iron_man",
                               metadata={"character": "South Park", "style": "comedy"})
        self._register_assistant("jarvis", "JARVIS", VirtualAssistantType.JARVIS, "iron_man",
                               metadata={"character": "Iron Man", "style": "tech"})
        self._register_assistant("iron_man", "Iron Man", VirtualAssistantType.IRON_MAN, "iron_man",
                               metadata={"character": "Tony Stark", "style": "tech", "template": True})
        self._register_assistant("ace", "Ace", VirtualAssistantType.ACE, "ace",
                               metadata={"character": "Armory Crate", "style": "combat", "template": True})

        # Character assistants (using templates)
        self._register_assistant("gandalf", "Gandalf", VirtualAssistantType.GANDALF, "iron_man",
                               metadata={"character": "Lord of the Rings", "style": "wizard"})
        self._register_assistant("tony_stark", "Tony Stark", VirtualAssistantType.TONY_STARK, "iron_man",
                               metadata={"character": "Iron Man", "style": "tech"})
        self._register_assistant("mace_windu", "Mace Windu", VirtualAssistantType.MACE_WINDU, "ace",
                               metadata={"character": "Star Wars", "style": "jedi", "council": True})

        # Jedi assistants (using Ace template - Jedi High Council members)
        self._register_assistant("jedi_master", "Jedi Master", VirtualAssistantType.JEDI_MASTER, "ace",
                               metadata={"character": "Star Wars", "style": "jedi", "rank": "master"})
        self._register_assistant("jedi_council", "Jedi High Council", VirtualAssistantType.JEDI_COUNCIL, "ace",
                               metadata={"character": "Star Wars", "style": "jedi", "rank": "council", "council": True})

        # Generic types (using templates)
        self._register_assistant("avatar", "Avatar", VirtualAssistantType.AVATAR, "iron_man",
                               metadata={"type": "generic", "template": "iron_man"})
        self._register_assistant("clone", "Clone", VirtualAssistantType.CLONE, "ace",
                               metadata={"type": "generic", "template": "ace"})
        self._register_assistant("personal_assistant", "Personal Assistant", VirtualAssistantType.PERSONAL_ASSISTANT, "iron_man",
                               metadata={"type": "generic", "template": "iron_man"})

    def _register_assistant(self, assistant_id: str, assistant_name: str, 
                          assistant_type: str, template: str, metadata: Dict[str, Any] = None):
        """Register a virtual assistant"""
        config = VirtualAssistantConfig(
            assistant_id=assistant_id,
            assistant_name=assistant_name,
            assistant_type=assistant_type,
            template=template,
            metrics_enabled=True,
            hud_enabled=True,
            gpu_metrics=True,
            phone_metrics=True,
            display_style=template,
            metadata=metadata or {}
        )

        self.assistants[assistant_id] = config
        self.logger.info(f"   ✅ Registered: {assistant_name} (Template: {template})")

    def enable_metrics_for_assistant(self, assistant_id: str) -> bool:
        """Enable metrics for a specific assistant"""
        if assistant_id not in self.assistants:
            self.logger.warning(f"⚠️  Assistant not found: {assistant_id}")
            return False

        assistant = self.assistants[assistant_id]
        assistant.metrics_enabled = True

        self.logger.info(f"✅ Metrics enabled for: {assistant.assistant_name}")
        return True

    def enable_hud_for_assistant(self, assistant_id: str) -> bool:
        """Enable HUD for a specific assistant"""
        if assistant_id not in self.assistants:
            self.logger.warning(f"⚠️  Assistant not found: {assistant_id}")
            return False

        assistant = self.assistants[assistant_id]
        assistant.hud_enabled = True

        self.logger.info(f"✅ HUD enabled for: {assistant.assistant_name}")
        return True

    def get_assistant_metrics(self, assistant_id: str) -> Optional[Dict[str, Any]]:
        """Get metrics for a specific assistant"""
        if assistant_id not in self.assistants:
            return None

        assistant = self.assistants[assistant_id]

        if not assistant.metrics_enabled or not self.metrics_dashboard:
            return None

        # Get metrics
        metrics = self.metrics_dashboard._get_system_metrics()

        # Add assistant-specific metadata
        metrics["assistant_id"] = assistant_id
        metrics["assistant_name"] = assistant.assistant_name
        metrics["assistant_type"] = assistant.assistant_type
        metrics["template"] = assistant.template
        metrics["display_style"] = assistant.display_style

        return metrics

    def display_metrics_in_assistant(self, assistant_id: str):
        """Display metrics in assistant's HUD/interface"""
        if assistant_id not in self.assistants:
            self.logger.warning(f"⚠️  Assistant not found: {assistant_id}")
            return False

        assistant = self.assistants[assistant_id]

        if not assistant.hud_enabled:
            self.logger.debug(f"HUD not enabled for: {assistant.assistant_name}")
            return False

        # Get metrics
        metrics = self.get_assistant_metrics(assistant_id)
        if not metrics:
            return False

        # Display in HUD based on template
        if assistant.template == "iron_man":
            return self._display_iron_man_style(assistant, metrics)
        elif assistant.template == "ace":
            return self._display_ace_style(assistant, metrics)
        else:
            # Default to Iron Man style
            return self._display_iron_man_style(assistant, metrics)

    def _display_iron_man_style(self, assistant: VirtualAssistantConfig, 
                                metrics: Dict[str, Any]) -> bool:
        """Display metrics in Iron Man style HUD"""
        if not self.jarvis_hud:
            return False

        try:
            # Iron Man style displays
            displays = [
                {
                    "display_id": f"{assistant.assistant_id}_status",
                    "display_type": "metrics",
                    "position": {"x": 10, "y": 10},
                    "size": {"width": 300, "height": 150},
                    "content": {
                        "title": f"{assistant.assistant_name} Status",
                        "metrics": {
                            "Uptime": f"{metrics.get('uptime', 0):.2f}h",
                            "Active": metrics.get('active_actions', 0),
                            "Success": f"{metrics.get('success_rate', 0)*100:.1f}%"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#00ff00",  # Iron Man green
                        "text_color": "#00ff00"
                    }
                }
            ]

            # Add GPU if available
            if metrics.get('gpu_usage', 0) > 0:
                displays.append({
                    "display_id": f"{assistant.assistant_id}_gpu",
                    "display_type": "metrics",
                    "position": {"x": 320, "y": 10},
                    "size": {"width": 300, "height": 100},
                    "content": {
                        "title": f"GPU: {metrics.get('gpu_name', 'GPU')[:20]}",
                        "metrics": {
                            "Usage": f"{metrics.get('gpu_usage', 0):.1f}%",
                            "Memory": f"{metrics.get('gpu_memory_used', 0):.1f}/{metrics.get('gpu_memory_total', 0):.1f} GB"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#ff8800",
                        "text_color": "#ff8800"
                    }
                })

            # Add phone if connected
            if metrics.get('phone_connected', False):
                displays.append({
                    "display_id": f"{assistant.assistant_id}_phone",
                    "display_type": "metrics",
                    "position": {"x": 10, "y": 170},
                    "size": {"width": 300, "height": 100},
                    "content": {
                        "title": f"Phone: {metrics.get('phone_type', 'Device')}",
                        "metrics": {
                            "Battery": f"{metrics.get('phone_battery', 0)}%",
                            "Status": "Connected"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#00ff88",
                        "text_color": "#00ff88"
                    }
                })

            # Update HUD
            for display in displays:
                self.jarvis_hud.update_display(display)

            return True

        except Exception as e:
            self.logger.error(f"Error displaying Iron Man style: {e}")
            return False

    def _display_ace_style(self, assistant: VirtualAssistantConfig,
                          metrics: Dict[str, Any]) -> bool:
        """Display metrics in Ace (Armory Crate) style HUD"""
        if not self.jarvis_hud:
            return False

        try:
            # Ace style displays (different color scheme)
            displays = [
                {
                    "display_id": f"{assistant.assistant_id}_status",
                    "display_type": "metrics",
                    "position": {"x": 10, "y": 10},
                    "size": {"width": 300, "height": 150},
                    "content": {
                        "title": f"{assistant.assistant_name} Status",
                        "metrics": {
                            "Uptime": f"{metrics.get('uptime', 0):.2f}h",
                            "Active": metrics.get('active_actions', 0),
                            "Success": f"{metrics.get('success_rate', 0)*100:.1f}%"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#0088ff",  # Ace blue
                        "text_color": "#0088ff"
                    }
                }
            ]

            # Add GPU if available
            if metrics.get('gpu_usage', 0) > 0:
                displays.append({
                    "display_id": f"{assistant.assistant_id}_gpu",
                    "display_type": "metrics",
                    "position": {"x": 320, "y": 10},
                    "size": {"width": 300, "height": 100},
                    "content": {
                        "title": f"GPU: {metrics.get('gpu_name', 'GPU')[:20]}",
                        "metrics": {
                            "Usage": f"{metrics.get('gpu_usage', 0):.1f}%",
                            "Memory": f"{metrics.get('gpu_memory_used', 0):.1f}/{metrics.get('gpu_memory_total', 0):.1f} GB"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#ff0088",
                        "text_color": "#ff0088"
                    }
                })

            # Add phone if connected
            if metrics.get('phone_connected', False):
                displays.append({
                    "display_id": f"{assistant.assistant_id}_phone",
                    "display_type": "metrics",
                    "position": {"x": 10, "y": 170},
                    "size": {"width": 300, "height": 100},
                    "content": {
                        "title": f"Phone: {metrics.get('phone_type', 'Device')}",
                        "metrics": {
                            "Battery": f"{metrics.get('phone_battery', 0)}%",
                            "Status": "Connected"
                        }
                    },
                    "style": {
                        "background_color": "rgba(0, 0, 0, 0.8)",
                        "border_color": "#88ff00",
                        "text_color": "#88ff00"
                    }
                })

            # Update HUD
            for display in displays:
                self.jarvis_hud.update_display(display)

            return True

        except Exception as e:
            self.logger.error(f"Error displaying Ace style: {e}")
            return False

    def enable_all_assistants(self):
        """Enable metrics and HUD for all assistants"""
        for assistant_id in self.assistants:
            self.enable_metrics_for_assistant(assistant_id)
            self.enable_hud_for_assistant(assistant_id)

        self.logger.info(f"✅ Enabled metrics and HUD for all {len(self.assistants)} assistants")

    def get_all_assistants_status(self) -> Dict[str, Any]:
        """Get status of all assistants"""
        return {
            "total_assistants": len(self.assistants),
            "assistants": {
                assistant_id: {
                    "name": config.assistant_name,
                    "type": config.assistant_type,
                    "template": config.template,
                    "metrics_enabled": config.metrics_enabled,
                    "hud_enabled": config.hud_enabled,
                    "gpu_metrics": config.gpu_metrics,
                    "phone_metrics": config.phone_metrics
                }
                for assistant_id, config in self.assistants.items()
            }
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Virtual Assistant Metrics Integration")
        parser.add_argument("--list", action="store_true", help="List all assistants")
        parser.add_argument("--enable-all", action="store_true", help="Enable all assistants")
        parser.add_argument("--enable", type=str, help="Enable specific assistant")
        parser.add_argument("--status", action="store_true", help="Show status")

        args = parser.parse_args()

        integration = VirtualAssistantMetricsIntegration()

        if args.list:
            status = integration.get_all_assistants_status()
            print(json.dumps(status, indent=2))

        if args.enable_all:
            integration.enable_all_assistants()
            print("✅ All assistants enabled")

        if args.enable:
            integration.enable_metrics_for_assistant(args.enable)
            integration.enable_hud_for_assistant(args.enable)
            print(f"✅ Assistant enabled: {args.enable}")

        if args.status:
            status = integration.get_all_assistants_status()
            print(json.dumps(status, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()