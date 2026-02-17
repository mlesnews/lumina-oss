#!/usr/bin/env python3
"""
JARVIS Hands-Free Demo - Test Mode (No Azure Required)

Simulates voice interaction for testing the conversation flow.
Use this to test the logic before setting up Azure Speech SDK.
"""

import sys
import time
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISHandsFreeTest")


class JARVISHandsFreeTest:
    """Test mode - simulates voice interaction"""

    def __init__(self):
        self.logger = get_logger("JARVISHandsFreeTest")
        self.jarvis = None
        self.marvin = None
        self._load_agents()

    def _load_agents(self):
        """Load JARVIS and MARVIN"""
        try:
            from jarvis_vector_explorer import JARVISVectorExplorer
            self.jarvis = JARVISVectorExplorer()
            self.logger.info("✅ JARVIS loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  JARVIS not available: {e}")

        try:
            from marvin_dropbox_cleanup import MarvinDropboxCleanup
            self.marvin = MarvinDropboxCleanup()
            self.logger.info("✅ MARVIN loaded")
        except Exception as e:
            self.logger.warning(f"⚠️  MARVIN not available: {e}")

    def speak(self, text: str, wait: bool = False):
        """Simulate JARVIS speaking"""
        print(f"\n🗣️  JARVIS: {text}\n")
        if wait:
            time.sleep(0.5)

    def listen(self) -> str:
        """Simulate listening - get input from user"""
        return input("👂 You: ").strip()

    def test_basic_conversation(self):
        """Test basic conversation flow"""
        print("\n" + "="*60)
        print("🧪 TEST MODE - Basic Conversation")
        print("="*60 + "\n")

        self.speak("Hello. I'm JARVIS. I'm ready to work with you, hands-free. How can I help?")

        response = self.listen()

        if "explore" in response.lower():
            self.speak("Let's explore that together. What problem would you like to explore?")
            problem = self.listen()
            if problem:
                self._test_exploration(problem)
        elif "marvin" in response.lower():
            self.speak("MARVIN is here. What would you like MARVIN to do?")
        elif "test" in response.lower():
            self.speak("Test mode is working! This simulates voice interaction.")
        else:
            self.speak(f"I heard: {response}. How can I help?")

    def _test_exploration(self, problem: str):
        """Test vector exploration"""
        if not self.jarvis:
            self.speak("JARVIS Vector Explorer is not available in test mode.")
            return

        self.speak(f"Let's explore: {problem}")
        self.speak("Identifying vectors to explore...")

        vectors = self.jarvis.identify_vectors(problem)
        self.speak(f"I've identified {len(vectors)} vectors.")

        # Test with first vector
        if vectors:
            vector = vectors[0]
            self.speak(f"Let's explore {vector.name}.")

            if vector.questions:
                question = vector.questions[0]
                self.speak(question)
                response = self.listen()

                if response:
                    self.speak(f"Got it. {response}")

        # Find paths
        self.speak("Finding paths forward...")
        paths = self.jarvis.find_paths_forward()
        self.speak(f"I found {len(paths)} possible paths.")

        # Recommend
        recommended = self.jarvis.recommend_path()
        if recommended:
            self.speak(f"I recommend: {recommended.name}. "
                      f"Feasibility: {int(recommended.feasibility * 100)}%, "
                      f"Impact: {int(recommended.impact * 100)}%.")
        else:
            self.speak("I couldn't determine a clear recommendation.")

    def test_dictation_mode(self):
        """Test dictation mode"""
        print("\n" + "="*60)
        print("🧪 TEST MODE - Dictation")
        print("="*60 + "\n")

        self.speak("Dictation mode activated. I'll transcribe everything you say. Say 'send' when done.")

        dictation_buffer = []

        while True:
            text = self.listen()

            if "send" in text.lower() or "done" in text.lower():
                full_text = " ".join(dictation_buffer + [text.replace("send", "").replace("done", "").strip()])
                self.speak(f"I transcribed: {full_text}")
                self.speak("Ready to send? Type 'yes' to send, 'no' to continue dictating.")

                response = self.listen()

                if "yes" in response.lower():
                    self.speak("Sending...")
                    self.speak(f"Dictation saved. {len(full_text)} characters.")
                    break
                else:
                    self.speak("Continuing dictation...")
            else:
                dictation_buffer.append(text)
                self.speak(f"Got it. {text}")

    def test_pause_detection(self):
        """Test pause detection"""
        print("\n" + "="*60)
        print("🧪 TEST MODE - Pause Detection")
        print("="*60 + "\n")

        self.speak("Starting pause detection mode. Type your segments, press Enter after each. Type 'done' when finished.")

        segments = []

        while True:
            segment = self.listen()
            if "done" in segment.lower():
                break
            if segment:
                segments.append(segment)
                self.speak(f"Segment {len(segments)}: {segment}")

        self.speak(f"I heard {len(segments)} segments: {', '.join(segments)}")

    def run_interactive_test(self):
        """Run interactive test menu"""
        print("\n" + "="*60)
        print("🤖 JARVIS Hands-Free Demo - TEST MODE")
        print("="*60)
        print("\nThis is a simulation mode to test the conversation flow.")
        print("In real mode, JARVIS will speak and listen via Azure Speech SDK.")
        print("\nTest Options:")
        print("  1. Basic Conversation")
        print("  2. Vector Exploration")
        print("  3. Dictation Mode")
        print("  4. Pause Detection")
        print("  5. Exit")

        while True:
            choice = input("\nSelect test (1-5): ").strip()

            if choice == "1":
                self.test_basic_conversation()
            elif choice == "2":
                problem = input("Enter problem to explore: ").strip()
                if problem:
                    self._test_exploration(problem)
            elif choice == "3":
                self.test_dictation_mode()
            elif choice == "4":
                self.test_pause_detection()
            elif choice == "5":
                self.speak("Test mode ended. Goodbye!")
                break
            else:
                print("Invalid choice. Please select 1-5.")


def main():
    """Run test mode"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Hands-Free Demo - Test Mode")
    parser.add_argument("--interactive", action="store_true", help="Interactive test menu")
    parser.add_argument("--conversation", action="store_true", help="Test conversation")
    parser.add_argument("--dictation", action="store_true", help="Test dictation")
    parser.add_argument("--pause", action="store_true", help="Test pause detection")

    args = parser.parse_args()

    test = JARVISHandsFreeTest()

    if args.interactive:
        test.run_interactive_test()
    elif args.conversation:
        test.test_basic_conversation()
    elif args.dictation:
        test.test_dictation_mode()
    elif args.pause:
        test.test_pause_detection()
    else:
        print("🤖 JARVIS Hands-Free Demo - TEST MODE")
        print("\nThis simulates voice interaction for testing.")
        print("Use --interactive for menu, or --conversation, --dictation, --pause")
        print("\nFor real voice interaction, set up Azure Speech SDK:")
        print("  1. pip install azure-cognitiveservices-speech")
        print("  2. export AZURE_SPEECH_KEY='your-key'")
        print("  3. python jarvis_hands_free_demo.py --demo")


if __name__ == "__main__":



    main()