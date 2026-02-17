#!/usr/bin/env python3
"""
JARVIS Talk Now - Direct Conversation Interface

Quick interface to talk directly to JARVIS without IDE bottlenecks.
"""

import sys
import time
from pathlib import Path

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

def main():
    """Start JARVIS conversation"""
    print("="*80)
    print("🎤 JARVIS - Direct Conversation Interface")
    print("="*80)
    print()

    try:
        from jarvis_fulltime_super_agent import get_jarvis_fulltime

        print("🔍 Initializing JARVIS...")
        jarvis = get_jarvis_fulltime()
        print("✅ JARVIS initialized")
        print()

        # Start a conversation
        print("💬 Starting conversation with JARVIS...")
        print("   (Type 'exit' or 'quit' to end)")
        print()
        print("-" * 80)

        # Start voice conversation properly
        conv_id = jarvis.start_voice_conversation()
        print(f"✅ Conversation started: {conv_id}")
        print()

        # Get initial greeting from conversation history
        history = jarvis.get_conversation_history(conv_id)
        if history:
            last_turn = history[-1]
            if last_turn.get('speaker') == 'jarvis':
                print(f"JARVIS: {last_turn.get('message', 'Hello!')}")
                print()

        # Interactive loop
        while True:
            try:
                user_input = input("You: ").strip()

                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("\n👋 Ending conversation. Goodbye!")
                    break

                if not user_input:
                    continue

                # Send to JARVIS
                jarvis.speak(conv_id, user_input, speaker="human")

                # Get response from conversation history
                history = jarvis.get_conversation_history(conv_id)
                if history:
                    # Get last JARVIS response
                    for turn in reversed(history):
                        if turn.get('speaker') == 'jarvis':
                            print(f"JARVIS: {turn.get('message', '...')}")
                            print()
                            break

            except KeyboardInterrupt:
                print("\n\n👋 Conversation interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 Conversation ended. Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                print("   Continuing...")
                print()

    except ImportError as e:
        print(f"❌ Failed to import JARVIS: {e}")
        print()
        print("Troubleshooting:")
        print("  1. Check if jarvis_fulltime_super_agent.py exists")
        print("  2. Check Python path and dependencies")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting JARVIS: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import time


    main()