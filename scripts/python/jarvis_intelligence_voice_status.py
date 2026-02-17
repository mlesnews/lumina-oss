#!/usr/bin/env python3
"""
JARVIS Intelligence & Voice Status Checker

Quick status check for:
- Intelligence gathering sources
- Voice system capabilities
- Hands-free automation readiness

Tags: #JARVIS #INTELLIGENCE #VOICE #STATUS #DIAGNOSTIC @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISStatus")


class JARVISIntelligenceVoiceStatus:
    """Check status of intelligence and voice systems"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.status = {}

    def check_intelligence_sources(self) -> Dict[str, Any]:
        """Check intelligence gathering sources"""
        sources = {
            "core_intelligence": self._check_core_intelligence(),
            "intelligence_analysis": self._check_intelligence_analysis(),
            "syphon_system": self._check_syphon_system(),
            "email_intelligence": self._check_email_intelligence(),
            "video_intelligence": self._check_video_intelligence(),
        }
        return sources

    def _check_core_intelligence(self) -> Dict[str, Any]:
        """Check core intelligence system"""
        try:
            from jarvis_core_intelligence import JARVISCoreIntelligence
            intelligence = JARVISCoreIntelligence(self.project_root)
            report = intelligence.get_status_report()
            return {
                "status": "✅ Active",
                "memories": report["memories_count"],
                "contexts": report["contexts_count"],
                "conversations": report["conversation_turns"],
                "details": report
            }
        except Exception as e:
            return {
                "status": "❌ Error",
                "error": str(e)
            }

    def _check_intelligence_analysis(self) -> Dict[str, Any]:
        """Check intelligence analysis system"""
        try:
            analysis_file = self.project_root / "scripts" / "python" / "jarvis_intelligence_analysis.py"
            if analysis_file.exists():
                # Try to import and check
                try:
                    from jarvis_intelligence_analysis import IntelligenceAnalyzer
                    analyzer = IntelligenceAnalyzer(self.project_root)
                    return {
                        "status": "✅ Available",
                        "domains": list(analyzer.life_domains.keys()),
                        "syphon_integrated": analyzer.syphon is not None
                    }
                except Exception as e:
                    return {
                        "status": "⚠️  File exists but import failed",
                        "error": str(e)
                    }
            else:
                return {
                    "status": "❌ Not found",
                    "file": str(analysis_file)
                }
        except Exception as e:
            return {
                "status": "❌ Error",
                "error": str(e)
            }

    def _check_syphon_system(self) -> Dict[str, Any]:
        """Check SYPHON system availability"""
        try:
            from syphon_system import SYPHONSystem, DataSourceType
            syphon = SYPHONSystem(self.project_root)
            return {
                "status": "✅ Available",
                "data_sources": [ds.value for ds in DataSourceType]
            }
        except ImportError:
            try:
                from scripts.python.syphon_system import SYPHONSystem, DataSourceType
                return {
                    "status": "✅ Available (via scripts)",
                    "data_sources": [ds.value for ds in DataSourceType]
                }
            except Exception as e:
                return {
                    "status": "❌ Not available",
                    "error": str(e)
                }
        except Exception as e:
            return {
                "status": "⚠️  Error",
                "error": str(e)
            }

    def _check_email_intelligence(self) -> Dict[str, Any]:
        try:
            """Check email intelligence system"""
            email_file = self.project_root / "scripts" / "python" / "email_intelligence_filter.py"
            return {
                "status": "✅ Available" if email_file.exists() else "❌ Not found",
                "file": str(email_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _check_email_intelligence: {e}", exc_info=True)
            raise
    def _check_video_intelligence(self) -> Dict[str, Any]:
        try:
            """Check video intelligence system"""
            video_file = self.project_root / "scripts" / "python" / "ingest_ada_jarvis_intelligence.py"
            return {
                "status": "✅ Available" if video_file.exists() else "❌ Not found",
                "file": str(video_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _check_video_intelligence: {e}", exc_info=True)
            raise
    def check_voice_systems(self) -> Dict[str, Any]:
        """Check voice system capabilities"""
        systems = {
            "hands_free_control": self._check_hands_free_control(),
            "full_voice_mode": self._check_full_voice_mode(),
            "voice_interface": self._check_voice_interface(),
            "hybrid_voice": self._check_hybrid_voice(),
        }
        return systems

    def _check_hands_free_control(self) -> Dict[str, Any]:
        """Check hands-free voice control"""
        try:
            from jarvis_hands_free_voice_control import JARVISHandsFreeVoiceControl
            control = JARVISHandsFreeVoiceControl(self.project_root, silent_mode=True)
            return {
                "status": "✅ Available",
                "manus_available": control.manus_available,
                "voice_available": control.voice_available,
                "command_types": len(control.command_patterns),
                "features": [
                    "No clicking required",
                    "No pasting required",
                    "No copying required",
                    "Full IDE control",
                    "Continuous listening"
                ]
            }
        except Exception as e:
            return {
                "status": "❌ Error",
                "error": str(e)
            }

    def _check_full_voice_mode(self) -> Dict[str, Any]:
        """Check full voice mode"""
        try:
            from jarvis_full_voice_mode import JARVISFullVoiceMode
            voice_mode = JARVISFullVoiceMode(self.project_root)
            return {
                "status": "✅ Available",
                "voice_system_available": voice_mode.voice_activation is not None,
                "gui_available": hasattr(voice_mode, 'gui')
            }
        except Exception as e:
            return {
                "status": "❌ Error",
                "error": str(e)
            }

    def _check_voice_interface(self) -> Dict[str, Any]:
        try:
            """Check voice interface"""
            voice_file = self.project_root / "scripts" / "python" / "jarvis_voice_interface.py"
            return {
                "status": "✅ Available" if voice_file.exists() else "❌ Not found",
                "file": str(voice_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _check_voice_interface: {e}", exc_info=True)
            raise
    def _check_hybrid_voice(self) -> Dict[str, Any]:
        try:
            """Check hybrid voice system"""
            hybrid_file = self.project_root / "scripts" / "python" / "lumina_jarvis_hybrid_voice_system.py"
            return {
                "status": "✅ Available" if hybrid_file.exists() else "❌ Not found",
                "file": str(hybrid_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _check_hybrid_voice: {e}", exc_info=True)
            raise
    def check_automation_features(self) -> Dict[str, Any]:
        """Check automation features"""
        features = {
            "auto_send": self._check_auto_send(),
            "outreach_automation": self._check_outreach_automation(),
            "desktop_recording": self._check_desktop_recording(),
            "manus_integration": self._check_manus_integration(),
        }
        return features

    def _check_auto_send(self) -> Dict[str, Any]:
        """Check auto-send capability"""
        # Check if auto-send is implemented in hands-free control
        try:
            from jarvis_hands_free_voice_control import JARVISHandsFreeVoiceControl
            control = JARVISHandsFreeVoiceControl(self.project_root, silent_mode=True)
            # Check if process_voice_input has auto-send logic
            has_auto_send = hasattr(control, '_auto_send') or 'auto_send' in str(control.process_voice_input.__code__.co_names)
            return {
                "status": "✅ Implemented" if has_auto_send else "⚠️  Not implemented",
                "note": "Auto-send after voice command completion"
            }
        except:
            return {
                "status": "❌ Cannot check",
                "note": "System not available"
            }

    def _check_outreach_automation(self) -> Dict[str, Any]:
        """Check outreach automation"""
        # Look for outreach-related files
        outreach_files = list(self.project_root.glob("**/*outreach*.py"))
        return {
            "status": "✅ Available" if outreach_files else "⚠️  Not found",
            "files": [str(f.relative_to(self.project_root)) for f in outreach_files[:5]]
        }

    def _check_desktop_recording(self) -> Dict[str, Any]:
        """Check desktop recording capability"""
        recording_files = list(self.project_root.glob("**/*recording*.py"))
        return {
            "status": "✅ Available" if recording_files else "⚠️  Not found",
            "files": [str(f.relative_to(self.project_root)) for f in recording_files[:5]]
        }

    def _check_manus_integration(self) -> Dict[str, Any]:
        """Check MANUS integration"""
        try:
            from manus_unified_control import MANUSUnifiedControl
            return {
                "status": "✅ Available",
                "note": "MANUS unified control system"
            }
        except:
            return {
                "status": "❌ Not available",
                "note": "MANUS system not found"
            }

    def get_full_status(self) -> Dict[str, Any]:
        """Get complete status report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "intelligence_sources": self.check_intelligence_sources(),
            "voice_systems": self.check_voice_systems(),
            "automation_features": self.check_automation_features(),
        }

    def print_status(self, json_output: bool = False):
        """Print status report"""
        status = self.get_full_status()

        if json_output:
            print(json.dumps(status, indent=2, default=str))
        else:
            print("=" * 80)
            print("🔍 JARVIS INTELLIGENCE & VOICE STATUS REPORT")
            print("=" * 80)
            print(f"Generated: {status['timestamp']}")
            print()

            # Intelligence Sources
            print("📊 INTELLIGENCE GATHERING SOURCES")
            print("-" * 80)
            for name, info in status["intelligence_sources"].items():
                status_icon = info.get("status", "❓")
                print(f"  {status_icon} {name.replace('_', ' ').title()}")
                if "error" in info:
                    print(f"     Error: {info['error']}")
                elif "memories" in info:
                    print(f"     Memories: {info['memories']}, Contexts: {info['contexts']}")
                elif "domains" in info:
                    print(f"     Domains: {len(info['domains'])}")
            print()

            # Voice Systems
            print("🎙️  VOICE SYSTEMS")
            print("-" * 80)
            for name, info in status["voice_systems"].items():
                status_icon = info.get("status", "❓")
                print(f"  {status_icon} {name.replace('_', ' ').title()}")
                if "command_types" in info:
                    print(f"     Command Types: {info['command_types']}")
                if "manus_available" in info:
                    print(f"     MANUS: {'✅' if info['manus_available'] else '❌'}")
                if "voice_available" in info:
                    print(f"     Voice: {'✅' if info['voice_available'] else '❌'}")
            print()

            # Automation Features
            print("🚀 AUTOMATION FEATURES")
            print("-" * 80)
            for name, info in status["automation_features"].items():
                status_icon = info.get("status", "❓")
                print(f"  {status_icon} {name.replace('_', ' ').title()}")
                if "note" in info:
                    print(f"     {info['note']}")
            print()

            print("=" * 80)


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Intelligence & Voice Status Checker")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--intelligence-only", action="store_true", help="Check intelligence only")
    parser.add_argument("--voice-only", action="store_true", help="Check voice only")
    parser.add_argument("--automation-only", action="store_true", help="Check automation only")

    args = parser.parse_args()

    checker = JARVISIntelligenceVoiceStatus()

    if args.intelligence_only:
        sources = checker.check_intelligence_sources()
        if args.json:
            print(json.dumps(sources, indent=2, default=str))
        else:
            print("📊 INTELLIGENCE SOURCES:")
            for name, info in sources.items():
                print(f"  {info.get('status', '❓')} {name}")
    elif args.voice_only:
        systems = checker.check_voice_systems()
        if args.json:
            print(json.dumps(systems, indent=2, default=str))
        else:
            print("🎙️  VOICE SYSTEMS:")
            for name, info in systems.items():
                print(f"  {info.get('status', '❓')} {name}")
    elif args.automation_only:
        features = checker.check_automation_features()
        if args.json:
            print(json.dumps(features, indent=2, default=str))
        else:
            print("🚀 AUTOMATION FEATURES:")
            for name, info in features.items():
                print(f"  {info.get('status', '❓')} {name}")
    else:
        checker.print_status(json_output=args.json)


if __name__ == "__main__":


    main()