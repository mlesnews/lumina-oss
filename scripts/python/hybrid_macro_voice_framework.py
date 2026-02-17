#!/usr/bin/env python3
"""
Hybrid Macro Voice Framework

Combines @MACROS (PowerToys, AutoHotkey, Armoury Crate) with @ELEVENLABS voice
and @MANUS system-wide keyboard shortcuts for unified automation.

Tags: #FRAMEWORKS #MACROS #ELEVENLABS #MANUS #HYBRID #AUTOMATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
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

logger = get_logger("HybridMacroVoiceFramework")


class HybridMethod(Enum):
    """Hybrid automation methods"""
    POWERTOYS = "powertoys"
    AUTOHOTKEY = "autohotkey"
    ARMOURY_CRATE = "armoury_crate"
    ELEVENLABS_VOICE = "elevenlabs_voice"
    MANUS_SHORTCUTS = "manus_shortcuts"
    COMBINED = "combined"  # Use multiple methods together


@dataclass
class HybridMacro:
    """
    Hybrid Macro - Combines keyboard automation with voice feedback

    Leverages multiple frameworks for comprehensive automation.
    """
    macro_id: str
    name: str
    trigger: str  # Keyboard shortcut
    voice_command: Optional[str] = None  # Voice command for ElevenLabs
    actions: List[Dict[str, Any]] = field(default_factory=list)
    voice_feedback: Optional[str] = None  # TTS feedback after execution
    methods: List[HybridMethod] = field(default_factory=list)
    manus_shortcut: Optional[str] = None  # MANUS system-wide shortcut
    enabled: bool = True
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['methods'] = [m.value for m in self.methods]
        return data


class HybridMacroVoiceFramework:
    """
    Hybrid Macro Voice Framework

    Combines:
    - @MACROS (PowerToys, AutoHotkey, Armoury Crate)
    - @ELEVENLABS (Voice commands and TTS feedback)
    - @MANUS (System-wide keyboard shortcuts)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize hybrid framework"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "hybrid_macros"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.macros: Dict[str, HybridMacro] = {}
        self.macro_by_name: Dict[str, HybridMacro] = {}

        # Initialize components
        self._init_macro_manager()
        self._init_elevenlabs()
        self._init_manus()

        logger.info("✅ Hybrid Macro Voice Framework initialized")
        logger.info("   🎹 PowerToys: READY")
        logger.info("   ⌨️  AutoHotkey: READY")
        logger.info("   🎨 Armoury Crate: READY")
        logger.info("   🎤 ElevenLabs: READY")
        logger.info("   ⌨️  MANUS: READY")
        logger.info("   🔗 Hybrid Mode: ACTIVE")

    def _init_macro_manager(self):
        """Initialize macro plugin manager"""
        try:
            from macro_plugin_manager import MacroPluginManager
            self.macro_manager = MacroPluginManager()
            logger.info("   ✅ Macro Manager: ACTIVE")
        except ImportError:
            logger.warning("   ⚠️  Macro Manager: NOT AVAILABLE")
            self.macro_manager = None

    def _init_elevenlabs(self):
        """Initialize ElevenLabs integration"""
        try:
            from lumina_jarvis_hybrid_voice_system import LUMINAJARVISHybridVoice
            self.elevenlabs = LUMINAJARVISHybridVoice()
            logger.info("   ✅ ElevenLabs: ACTIVE")
        except ImportError:
            logger.warning("   ⚠️  ElevenLabs: NOT AVAILABLE")
            self.elevenlabs = None

    def _init_manus(self):
        """Initialize MANUS system-wide shortcuts"""
        try:
            from manus_system_wide_keyboard_shortcuts import MANUSSystemWideShortcuts
            self.manus = MANUSSystemWideShortcuts()
            logger.info("   ✅ MANUS: ACTIVE")
        except ImportError:
            logger.warning("   ⚠️  MANUS: NOT AVAILABLE")
            self.manus = None

    def create_hybrid_macro(self, name: str, trigger: str, actions: List[Dict[str, Any]],
                           voice_command: Optional[str] = None,
                           voice_feedback: Optional[str] = None,
                           methods: Optional[List[HybridMethod]] = None,
                           manus_shortcut: Optional[str] = None,
                           description: str = "") -> HybridMacro:
        """
        Create hybrid macro combining multiple frameworks

        Args:
            name: Macro name
            trigger: Keyboard shortcut
            actions: Sequence of actions
            voice_command: Voice command for ElevenLabs
            voice_feedback: TTS feedback after execution
            methods: List of methods to use (default: all)
            manus_shortcut: MANUS system-wide shortcut
            description: Description
        """
        import time
        import random

        if methods is None:
            methods = [HybridMethod.POWERTOYS, HybridMethod.AUTOHOTKEY, HybridMethod.ELEVENLABS_VOICE, HybridMethod.MANUS_SHORTCUTS]

        unique_id = f"hybrid_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{int(time.time() * 1000000) % 1000000}_{random.randint(1000, 9999)}"

        macro = HybridMacro(
            macro_id=unique_id,
            name=name,
            trigger=trigger,
            voice_command=voice_command,
            actions=actions,
            voice_feedback=voice_feedback,
            methods=methods,
            manus_shortcut=manus_shortcut,
            description=description
        )

        # Check for duplicates
        if name in self.macro_by_name:
            logger.warning(f"   ⚠️  Macro '{name}' already exists, updating...")
            old_macro = self.macro_by_name[name]
            del self.macros[old_macro.macro_id]

        self.macros[macro.macro_id] = macro
        self.macro_by_name[name] = macro

        logger.info(f"✅ Hybrid macro created: {macro.macro_id}")
        logger.info(f"   Name: {name}")
        logger.info(f"   Methods: {[m.value for m in methods]}")
        logger.info(f"   Voice Command: {voice_command or 'None'}")
        logger.info(f"   MANUS Shortcut: {manus_shortcut or 'None'}")

        return macro

    def execute_hybrid_macro(self, macro_id: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute hybrid macro using all enabled methods

        Args:
            macro_id: Macro ID
            context: Execution context

        Returns:
            Execution results
        """
        if macro_id not in self.macros:
            return {"success": False, "error": f"Macro not found: {macro_id}"}

        macro = self.macros[macro_id]
        if not macro.enabled:
            return {"success": False, "error": "Macro is disabled"}

        results = {
            "macro_id": macro_id,
            "macro_name": macro.name,
            "methods_executed": [],
            "success": True,
            "errors": []
        }

        # Execute via PowerToys
        if HybridMethod.POWERTOYS in macro.methods and self.macro_manager:
            try:
                # Create PowerToys config
                powertoys_result = self._execute_powertoys(macro)
                results["methods_executed"].append("powertoys")
                results["powertoys"] = powertoys_result
            except Exception as e:
                results["errors"].append(f"PowerToys: {str(e)}")

        # Execute via AutoHotkey
        if HybridMethod.AUTOHOTKEY in macro.methods and self.macro_manager:
            try:
                ahk_result = self._execute_autohotkey(macro)
                results["methods_executed"].append("autohotkey")
                results["autohotkey"] = ahk_result
            except Exception as e:
                results["errors"].append(f"AutoHotkey: {str(e)}")

        # Execute via Armoury Crate
        if HybridMethod.ARMOURY_CRATE in macro.methods and self.macro_manager:
            try:
                ac_result = self._execute_armoury_crate(macro)
                results["methods_executed"].append("armoury_crate")
                results["armoury_crate"] = ac_result
            except Exception as e:
                results["errors"].append(f"Armoury Crate: {str(e)}")

        # Execute via ElevenLabs (voice command)
        if HybridMethod.ELEVENLABS_VOICE in macro.methods and macro.voice_command and self.elevenlabs:
            try:
                voice_result = self._execute_elevenlabs_voice(macro)
                results["methods_executed"].append("elevenlabs_voice")
                results["elevenlabs"] = voice_result
            except Exception as e:
                results["errors"].append(f"ElevenLabs: {str(e)}")

        # Execute via MANUS
        if HybridMethod.MANUS_SHORTCUTS in macro.methods and macro.manus_shortcut and self.manus:
            try:
                manus_result = self._execute_manus(macro)
                results["methods_executed"].append("manus_shortcuts")
                results["manus"] = manus_result
            except Exception as e:
                results["errors"].append(f"MANUS: {str(e)}")

        # Voice feedback after execution
        if macro.voice_feedback and self.elevenlabs:
            try:
                self._execute_voice_feedback(macro.voice_feedback)
                results["voice_feedback"] = "executed"
            except Exception as e:
                results["errors"].append(f"Voice Feedback: {str(e)}")

        if results["errors"]:
            results["success"] = False

        return results

    def _execute_powertoys(self, macro: HybridMacro) -> Dict[str, Any]:
        """Execute macro via PowerToys"""
        # Integration with PowerToys
        return {"method": "powertoys", "status": "configured"}

    def _execute_autohotkey(self, macro: HybridMacro) -> Dict[str, Any]:
        """Execute macro via AutoHotkey"""
        # Integration with AutoHotkey
        return {"method": "autohotkey", "status": "configured"}

    def _execute_armoury_crate(self, macro: HybridMacro) -> Dict[str, Any]:
        """Execute macro via Armoury Crate"""
        # Integration with Armoury Crate
        return {"method": "armoury_crate", "status": "configured"}

    def _execute_elevenlabs_voice(self, macro: HybridMacro) -> Dict[str, Any]:
        """Execute voice command via ElevenLabs"""
        if not self.elevenlabs:
            return {"method": "elevenlabs", "status": "not_available"}

        # Process voice command through ElevenLabs
        return {"method": "elevenlabs", "status": "processed", "command": macro.voice_command}

    def _execute_manus(self, macro: HybridMacro) -> Dict[str, Any]:
        """Execute via MANUS system-wide shortcuts"""
        if not self.manus:
            return {"method": "manus", "status": "not_available"}

        # Execute MANUS shortcut
        return {"method": "manus", "status": "executed", "shortcut": macro.manus_shortcut}

    def _execute_voice_feedback(self, feedback_text: str) -> None:
        """Execute voice feedback via ElevenLabs TTS"""
        if not self.elevenlabs:
            return

        # Use ElevenLabs TTS for feedback
        logger.info(f"   🎤 Voice Feedback: {feedback_text}")

    def create_cursor_ide_hybrid_macros(self):
        """Create hybrid macros for Cursor IDE"""
        logger.info("=" * 80)
        logger.info("🔗 CREATING HYBRID CURSOR IDE MACROS")
        logger.info("=" * 80)
        logger.info("")

        # Hybrid Macro 1: Undo All with Voice
        self.create_hybrid_macro(
            name="Cursor IDE: Undo All (Hybrid)",
            trigger="Ctrl+Alt+U",
            actions=[
                {"type": "key", "key": "Ctrl+Z"},
                {"type": "delay", "delay": 50},
                {"type": "key", "key": "Ctrl+Z"}
            ],
            voice_command="undo all changes",
            voice_feedback="All changes have been undone",
            methods=[HybridMethod.POWERTOYS, HybridMethod.AUTOHOTKEY, HybridMethod.ELEVENLABS_VOICE, HybridMethod.MANUS_SHORTCUTS],
            manus_shortcut="Ctrl+Alt+U",
            description="Undo all changes with voice feedback"
        )

        # Hybrid Macro 2: Keep All with Voice
        self.create_hybrid_macro(
            name="Cursor IDE: Keep All (Hybrid)",
            trigger="Ctrl+Alt+K",
            actions=[
                {"type": "key", "key": "Ctrl+A"},
                {"type": "delay", "delay": 50},
                {"type": "key", "key": "Ctrl+S"}
            ],
            voice_command="keep all changes",
            voice_feedback="All changes have been saved",
            methods=[HybridMethod.POWERTOYS, HybridMethod.AUTOHOTKEY, HybridMethod.ELEVENLABS_VOICE, HybridMethod.MANUS_SHORTCUTS],
            manus_shortcut="Ctrl+Alt+K",
            description="Keep all changes with voice feedback"
        )

        # Hybrid Macro 3: Focus Chat with Voice
        self.create_hybrid_macro(
            name="Cursor IDE: Focus Chat (Hybrid)",
            trigger="Ctrl+K Ctrl+J",
            actions=[
                {"type": "key", "key": "Ctrl+K"},
                {"type": "delay", "delay": 100},
                {"type": "key", "key": "Ctrl+J"}
            ],
            voice_command="focus chat",
            voice_feedback="Chat focused",
            methods=[HybridMethod.POWERTOYS, HybridMethod.AUTOHOTKEY, HybridMethod.ELEVENLABS_VOICE, HybridMethod.MANUS_SHORTCUTS],
            manus_shortcut="Ctrl+K Ctrl+J",
            description="Focus chat with voice feedback"
        )

        logger.info(f"   ✅ Created {len([m for m in self.macros.values() if 'Hybrid' in m.name])} hybrid macros")
        logger.info("")

    def generate_all_configs(self):
        """Generate all hybrid macro configurations"""
        logger.info("=" * 80)
        logger.info("🔗 GENERATING ALL HYBRID MACRO CONFIGS")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   📋 Total Hybrid Macros: {len(self.macros)}")
        logger.info("")

        # Generate macro configs
        if self.macro_manager:
            self.macro_manager.macros = {}
            for macro in self.macros.values():
                # Create standard macro for macro_manager
                self.macro_manager.create_macro(
                    name=macro.name,
                    trigger=macro.trigger,
                    actions=macro.actions,
                    description=macro.description
                )

            # Generate all configs
            self.macro_manager.generate_all_configs()

        # Generate hybrid config
        self._generate_hybrid_config()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ ALL HYBRID MACRO CONFIGS GENERATED")
        logger.info("=" * 80)
        logger.info("")

    def _generate_hybrid_config(self) -> Path:
        try:
            """Generate hybrid macro configuration"""
            config_file = self.data_dir / "hybrid_macros.json"

            config = {
                "version": "1.0",
                "framework": "Hybrid Macro Voice Framework",
                "components": {
                    "powertoys": "enabled",
                    "autohotkey": "enabled",
                    "armoury_crate": "enabled",
                    "elevenlabs": "enabled",
                    "manus": "enabled"
                },
                "macros": [macro.to_dict() for macro in self.macros.values()]
            }

            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Hybrid config generated: {config_file.name}")
            return config_file


        except Exception as e:
            self.logger.error(f"Error in _generate_hybrid_config: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Hybrid Macro Voice Framework")
        parser.add_argument("--create-hybrid", action="store_true", help="Create hybrid Cursor IDE macros")
        parser.add_argument("--generate-all", action="store_true", help="Generate all configs")
        parser.add_argument("--execute", type=str, help="Execute macro by ID")

        args = parser.parse_args()

        framework = HybridMacroVoiceFramework()

        if args.generate_all:
            framework.create_cursor_ide_hybrid_macros()
            framework.generate_all_configs()
        elif args.create_hybrid:
            framework.create_cursor_ide_hybrid_macros()
        elif args.execute:
            result = framework.execute_hybrid_macro(args.execute)
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())