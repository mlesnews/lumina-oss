#!/usr/bin/env python3
"""
JARVIS Chat - Interactive Conversation Interface

Direct conversation with JARVIS - no IDE clicking needed.
"""

import sys
import time
from pathlib import Path

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

def main():
    """Start interactive JARVIS conversation"""
    print("="*80)
    print("🤖 JARVIS - Interactive Chat")
    print("="*80)
    print()

    try:
        from jarvis_fulltime_super_agent import get_jarvis_fulltime

        print("🔍 Connecting to JARVIS...")
        jarvis = get_jarvis_fulltime()
        print("✅ Connected!")
        print()

        # Start conversation
        print("💬 Starting conversation...")
        conv_id = jarvis.start_voice_conversation()
        print(f"✅ Conversation ID: {conv_id}")
        print()
        print("-" * 80)
        print()

        # Get initial greeting
        history = jarvis.get_conversation_history(conv_id)
        if history:
            for turn in history:
                if turn.get('speaker') == 'jarvis':
                    print(f"🤖 JARVIS: {turn.get('message', 'Hello!')}")
                    print()

        # Interactive loop
        print("💡 Type your message and press Enter. Type 'exit' or 'quit' to end.")
        print()

        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()

                if user_input.lower() in ['exit', 'quit', 'bye', 'goodbye']:
                    print("\n👋 JARVIS: Goodbye! Always here when you need me.")
                    break

                if not user_input:
                    continue

                # Send to JARVIS
                jarvis.speak(conv_id, user_input, speaker="human")

                # Wait a moment for response
                time.sleep(0.5)

                # Get response from conversation history
                history = jarvis.get_conversation_history(conv_id)
                if history:
                    # Get last JARVIS response
                    for turn in reversed(history):
                        if turn.get('speaker') == 'jarvis':
                            print(f"🤖 JARVIS: {turn.get('message', '...')}")
                            print()
                            break

            except KeyboardInterrupt:
                print("\n\n👋 JARVIS: Conversation interrupted. Goodbye!")
                break
            except EOFError:
                print("\n\n👋 JARVIS: Goodbye!")
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
        print("  2. Check Python dependencies")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":


    main()