#!/usr/bin/env python3
"""
JARVIS Enhanced Launcher - Unified Entry Point

Launches the enhanced JARVIS virtual assistant with all capabilities:
- Role management (JARVIS, Ultron, Ultimate Iron Man)
- Iron Legion expert integration
- Interactive desktop assistant
- Command interface

Tags: #JARVIS #LAUNCHER #ENHANCED @JARVIS @LUMINA
"""

import sys
import argparse
from pathlib import Path

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

logger = get_logger("JARVISLauncher")


def launch_enhanced_desktop():
    """Launch enhanced desktop assistant"""
    try:
        from jarvis_desktop_assistant_enhanced import JARVISDesktopAssistantEnhanced
        assistant = JARVISDesktopAssistantEnhanced()
        assistant.run()
    except ImportError as e:
        logger.error(f"❌ Could not import enhanced desktop assistant: {e}")
        logger.info("   Falling back to basic desktop assistant...")
        try:
            from jarvis_desktop_assistant import JARVISDesktopAssistant
            assistant = JARVISDesktopAssistant()
            assistant.run()
        except ImportError:
            logger.error("❌ Basic desktop assistant also not available")
            sys.exit(1)


def launch_basic_desktop():
    """Launch basic desktop assistant"""
    try:
        from jarvis_desktop_assistant import JARVISDesktopAssistant
        assistant = JARVISDesktopAssistant()
        assistant.run()
    except ImportError as e:
        logger.error(f"❌ Could not import desktop assistant: {e}")
        sys.exit(1)


def test_core():
    """Test enhanced core functionality"""
    try:
        from jarvis_enhanced_core import JarvisEnhancedCore
        core = JarvisEnhancedCore()

        print("\n" + "=" * 80)
        print("🧪 JARVIS ENHANCED CORE TEST")
        print("=" * 80 + "\n")

        # Test capabilities
        print("1. System Status:")
        result = core.execute_capability("system_status")
        print(f"   {result}\n")

        print("2. List Roles:")
        result = core.execute_capability("list_roles")
        print(f"   {result}\n")

        print("3. List Experts:")
        result = core.execute_capability("list_experts")
        print(f"   {result}\n")

        print("4. Test Query Routing:")
        test_queries = [
            "write a python function",
            "solve this complex problem",
            "quick answer please"
        ]
        for query in test_queries:
            result = core.process_command(f"query {query}")
            print(f"   Query: '{query}'")
            print(f"   Result: {result.get('expert', 'No expert')}\n")

        print("=" * 80)
        print("✅ TEST COMPLETE")
        print("=" * 80)

    except ImportError as e:
        logger.error(f"❌ Could not import enhanced core: {e}")
        sys.exit(1)


def show_info():
    """Show JARVIS information"""
    print("\n" + "=" * 80)
    print("🦾 JARVIS ENHANCED VIRTUAL ASSISTANT")
    print("=" * 80)
    print()
    print("JARVIS is the unified virtual assistant that can wear different 'hats' (roles):")
    print()
    print("  • JARVIS (default): Balanced assistant")
    print("  • Ultron: Advanced reasoning and complex tasks")
    print("  • Ultimate Iron Man: High-fidelity visual and premium features")
    print()
    print("All Iron Man AIs are additional roles that JARVIS can switch between.")
    print()
    print("Features:")
    print("  • Role management and switching")
    print("  • Iron Legion expert integration (7 specialized models)")
    print("  • Interactive desktop assistant")
    print("  • Command interface")
    print("  • Right-click context menu")
    print()
    print("Usage:")
    print("  python jarvis_launcher_enhanced.py              # Launch enhanced desktop")
    print("  python jarvis_launcher_enhanced.py --basic       # Launch basic desktop")
    print("  python jarvis_launcher_enhanced.py --test        # Test core functionality")
    print("  python jarvis_launcher_enhanced.py --info        # Show this information")
    print()
    print("=" * 80)
    print()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="JARVIS Enhanced Launcher - Unified Virtual Assistant",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        "--basic",
        action="store_true",
        help="Launch basic desktop assistant (no enhanced features)"
    )

    parser.add_argument(
        "--test",
        action="store_true",
        help="Test enhanced core functionality"
    )

    parser.add_argument(
        "--info",
        action="store_true",
        help="Show JARVIS information"
    )

    args = parser.parse_args()

    if args.info:
        show_info()
    elif args.test:
        test_core()
    elif args.basic:
        launch_basic_desktop()
    else:
        launch_enhanced_desktop()


if __name__ == "__main__":


    main()