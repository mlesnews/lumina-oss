#!/usr/bin/env python3
"""
Activate Full VA Voice/VFX/Collaboration System

Master script to activate:
- Full voice mode (speech recognition + TTS)
- AI VFX system (particles, glow, beams)
- Company-wide collaboration
- Real-time VA coordination
- Complete avatar system

This is the ONE command to activate everything.

Usage:
    python activate_full_va_voice_vfx_collaboration.py --start
    python activate_full_va_voice_vfx_collaboration.py --demo
    python activate_full_va_voice_vfx_collaboration.py --status

Tags: #VOICE #VFX #COLLABORATION #FULL_MODE #MASTER @JARVIS @LUMINA
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("ActivateFullVASystem")

# Import master integration system
try:
    from va_full_voice_vfx_collaboration_integration import VAFullVoiceVFXCollaborationIntegration
    INTEGRATION_AVAILABLE = True
except ImportError:
    INTEGRATION_AVAILABLE = False
    logger.error("❌ Integration system not available")
    sys.exit(1)


def print_banner():
    """Print activation banner"""
    print("=" * 80)
    print("🚀 FULL VA VOICE/VFX/COLLABORATION SYSTEM")
    print("=" * 80)
    print()
    print("Activating:")
    print("  ✅ Full Voice Mode (Speech Recognition + TTS)")
    print("  ✅ AI VFX System (Particles, Glow, Beams)")
    print("  ✅ Company-Wide Collaboration")
    print("  ✅ Real-Time VA Coordination")
    print("  ✅ Complete Avatar System")
    print()
    print("=" * 80)
    print()


def start_full_system():
    """Start the complete system"""
    print_banner()

    logger.info("🚀 Starting Full VA Voice/VFX/Collaboration System...")

    project_root = Path(__file__).parent.parent.parent
    integration = VAFullVoiceVFXCollaborationIntegration(project_root)

    # Start full integration
    integration.start_full_integration()

    print()
    print("✅ FULL SYSTEM ACTIVE")
    print()
    print("Features:")
    print("  🎤 Full Voice Mode - All VAs can speak and listen")
    print("  ✨ AI VFX System - Visual effects for all avatars")
    print("  🤝 Company Collaboration - VAs work together")
    print("  📊 Real-Time Coordination - Live status updates")
    print()
    print("VAs Active:")
    print("  - Iron Man (High Priority)")
    print("  - Kenny (Medium Priority)")
    print("  - Anakin (Medium Priority)")
    print("  - JARVIS (Critical Priority)")
    print()
    print("Press Ctrl+C to stop")
    print()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print()
        print("🛑 Stopping system...")
        integration.stop_full_integration()
        print("✅ System stopped")
        sys.exit(0)


def run_demo():
    try:
        """Run collaboration demonstration"""
        print_banner()

        logger.info("🎬 Running Full Collaboration Demonstration...")

        project_root = Path(__file__).parent.parent.parent
        integration = VAFullVoiceVFXCollaborationIntegration(project_root)

        # Initialize systems
        integration.initialize_systems()
        integration._register_all_vas()

        # Start collaboration mode
        if integration.collaboration_system:
            integration.collaboration_system.start_full_collaboration_mode()

        print()
        print("🎬 Starting Demonstration...")
        print()

        # Run demonstration
        integration.demonstrate_collaboration()

        print()
        print("✅ Demonstration Complete")
        print()

        # Show status
        status = integration.get_full_status()
        print("System Status:")
        print(json.dumps(status, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in run_demo: {e}", exc_info=True)
        raise
def show_status():
    try:
        """Show system status"""
        project_root = Path(__file__).parent.parent.parent
        integration = VAFullVoiceVFXCollaborationIntegration(project_root)

        # Initialize to get status
        integration.initialize_systems()

        status = integration.get_full_status()

        print("=" * 80)
        print("📊 FULL VA SYSTEM STATUS")
        print("=" * 80)
        print()
        print(json.dumps(status, indent=2, default=str))
        print()


    except Exception as e:
        logger.error(f"Error in show_status: {e}", exc_info=True)
        raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Activate Full VA Voice/VFX/Collaboration System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Start full system
  python activate_full_va_voice_vfx_collaboration.py --start

  # Run demonstration
  python activate_full_va_voice_vfx_collaboration.py --demo

  # Show status
  python activate_full_va_voice_vfx_collaboration.py --status
        """
    )

    parser.add_argument("--start", action="store_true", 
                       help="Start full voice/VFX/collaboration system")
    parser.add_argument("--demo", action="store_true",
                       help="Run collaboration demonstration")
    parser.add_argument("--status", action="store_true",
                       help="Show system status")

    args = parser.parse_args()

    if args.start:
        start_full_system()
    elif args.demo:
        run_demo()
    elif args.status:
        show_status()
    else:
        parser.print_help()
        print()
        print("💡 Tip: Use --start to activate the full system")
        print("💡 Tip: Use --demo to see a collaboration demonstration")


if __name__ == "__main__":


    main()