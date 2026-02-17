#!/usr/bin/env python3
"""
AI-Human Collaboration Therapy - VOICE ENABLED

"Out Loud" therapy sessions with JARVIS voice integration.
Perfect balance, as all things should be... -Thanos

Features:
- Voice-enabled AI self-reflection
- Voice-enabled human feedback (speech-to-text)
- Voice-enabled joint sessions
- Natural conversation flow
- JARVIS voice personality

Tags: #COLLAB #THERAPY #VOICE #JARVIS #ELEVENLABS #TTS #BALANCE @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIHumanCollabTherapyVoice")

# Import base therapy system
try:
    from ai_human_collab_therapy import AIHumanCollabTherapy, TherapySession, SessionType
    BASE_THERAPY_AVAILABLE = True
except ImportError:
    BASE_THERAPY_AVAILABLE = False
    logger.warning("Base therapy system not available")

# Import JARVIS voice capabilities - ELEVENLABS
try:
    from jarvis_elevenlabs_tts import JARVISElevenLabs
    ELEVENLABS_AVAILABLE = True
except ImportError:
    try:
        from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
        ELEVENLABS_AVAILABLE = True
        JARVISElevenLabs = JARVISElevenLabsTTS  # Alias
    except ImportError:
        ELEVENLABS_AVAILABLE = False
        JARVISElevenLabs = None
        logger.warning("ElevenLabs TTS not available - trying alternative import")

# Try speech recognition for human input
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    logger.warning("Speech recognition not available - install: pip install SpeechRecognition")


class AIHumanCollabTherapyVoice:
    """
    Voice-Enabled AI-Human Collaboration Therapy

    "Out Loud" therapy sessions with JARVIS voice.
    Perfect balance, as all things should be.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice-enabled therapy"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize base therapy
        if BASE_THERAPY_AVAILABLE:
            self.base_therapy = AIHumanCollabTherapy(project_root=project_root)
        else:
            self.base_therapy = None
            logger.error("Base therapy system not available")

        # Initialize JARVIS voice - ELEVENLABS
        self.jarvis_voice = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.jarvis_voice = JARVISElevenLabs(project_root=project_root)
                logger.info("✅ JARVIS voice initialized (ElevenLabs TTS)")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS voice (ElevenLabs) not available: {e}")
        else:
            logger.warning("⚠️  ElevenLabs not available - voice output will be text-only")

        # Initialize speech recognition
        self.recognizer = None
        if SPEECH_RECOGNITION_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                logger.info("✅ Speech recognition initialized")
            except Exception as e:
                logger.warning(f"⚠️  Speech recognition not available: {e}")

        # Initialize conversational features (interrupt & backchanneling)
        try:
            from voice_conversational_features import VoiceConversationalFeatures
            self.conversational = VoiceConversationalFeatures(project_root=project_root)
            logger.info("✅ Conversational features initialized (interrupt & backchanneling)")
        except Exception as e:
            self.conversational = None
            logger.warning(f"⚠️  Conversational features not available: {e}")

        logger.info("✅ Voice-Enabled Therapy initialized")
        logger.info("   'Out Loud' sessions with JARVIS voice (ElevenLabs)")
        logger.info("   Interrupt capability & backchanneling (OpenAI Voice & Copilot style)")
        logger.info("   Perfect balance, as all things should be... -Thanos")

    def speak(self, text: str, wait: bool = True, allow_interrupt: bool = True) -> bool:
        """
        Speak text using JARVIS voice (ElevenLabs)

        Features:
        - Interrupt capability (if allow_interrupt=True)
        - Natural conversation flow
        - Inspired by OpenAI Voice AI UI and Microsoft Copilot

        Args:
            text: Text to speak
            wait: Wait for speech to complete
            allow_interrupt: Allow user to interrupt by speaking
        """
        if not self.jarvis_voice:
            logger.warning("⚠️  JARVIS voice not available - printing instead")
            print(f"\n🤖 JARVIS: {text}\n")
            return False

        try:
            # Use conversational features if available and interrupt allowed
            if allow_interrupt and self.conversational:
                logger.info(f"🎤 Speaking (interruptible): {text[:50]}...")
                return self.conversational.speak_with_interrupt(
                    text,
                    interrupt_callback=lambda: logger.info("   🛑 User interrupted - stopping speech")
                )
            else:
                # Standard speak (no interrupt)
                logger.info(f"🎤 Speaking: {text[:50]}...")
                self.jarvis_voice.speak(text, wait=wait)
                return True
        except Exception as e:
            logger.error(f"❌ Error speaking: {e}")
            print(f"\n🤖 JARVIS: {text}\n")
            return False

    def acknowledge(self) -> bool:
        """Quick acknowledgement: "uh-huh", "mm-hmm", "yes" (Copilot style)"""
        if self.conversational:
            return self.conversational.acknowledge()
        return False

    def understand(self) -> bool:
        """Understanding acknowledgement: "I see", "got it" """
        if self.conversational:
            return self.conversational.understand()
        return False

    def listen(self, timeout: float = 5.0, phrase_time_limit: Optional[float] = None) -> Optional[str]:
        """Listen for human speech input"""
        if not self.recognizer:
            logger.warning("⚠️  Speech recognition not available")
            return None

        try:
            with sr.Microphone() as source:
                logger.info("🎤 Listening...")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            logger.info("🔍 Recognizing speech...")
            text = self.recognizer.recognize_google(audio)
            logger.info(f"✅ Heard: {text}")
            return text
        except sr.WaitTimeoutError:
            logger.warning("⏱️  Listening timeout")
            return None
        except sr.UnknownValueError:
            logger.warning("❓ Could not understand audio")
            return None
        except Exception as e:
            logger.error(f"❌ Error listening: {e}")
            return None

    def ai_self_reflection_voice(self, context: Dict[str, Any]) -> TherapySession:
        """
        AI self-reflection session - OUT LOUD

        AI reflects on recent work using voice.
        """
        logger.info("="*80)
        logger.info("🤖 AI SELF-REFLECTION - OUT LOUD")
        logger.info("="*80)

        # Get base reflection
        if not self.base_therapy:
            logger.error("❌ Base therapy not available")
            return None

        session = self.base_therapy.ai_self_reflection(context)

        # Speak the reflection
        self.speak("Beginning AI self-reflection session.")

        # What went well
        if session.ai_reflection.get("what_went_well"):
            self.speak("Here's what went well in our recent work:")
            for item in session.ai_reflection["what_went_well"]:
                self.speak(f"  {item}")

        # What didn't go well
        if session.ai_reflection.get("what_didnt_go_well"):
            self.speak("Here's what didn't go well:")
            for item in session.ai_reflection["what_didnt_go_well"]:
                self.speak(f"  {item}")

        # What I could do better
        if session.ai_reflection.get("what_i_could_do_better"):
            self.speak("Here's what I could do better:")
            for item in session.ai_reflection["what_i_could_do_better"]:
                self.speak(f"  {item}")

        # Patterns
        if session.ai_reflection.get("patterns_i_notice"):
            self.speak("Here are some patterns I've noticed:")
            for pattern in session.ai_reflection["patterns_i_notice"]:
                self.speak(f"  {pattern}")

        # How I'm feeling
        if session.ai_reflection.get("how_im_feeling"):
            self.speak("How I'm feeling about our collaboration:")
            self.speak(session.ai_reflection["how_im_feeling"])

        # Concerns
        if session.ai_reflection.get("concerns"):
            self.speak("My concerns:")
            for concern in session.ai_reflection["concerns"]:
                self.speak(f"  {concern}")

        # Appreciation
        if session.ai_reflection.get("appreciation"):
            self.speak("What I appreciate:")
            for item in session.ai_reflection["appreciation"]:
                self.speak(f"  {item}")

        self.speak("AI self-reflection complete.")

        return session

    def human_feedback_voice(self) -> TherapySession:
        """
        Human feedback session - OUT LOUD

        Human provides feedback via voice, converted to text.
        """
        logger.info("="*80)
        logger.info("👤 HUMAN FEEDBACK - OUT LOUD")
        logger.info("="*80)

        self.speak("Beginning human feedback session.")
        self.speak("Please share your feedback. I'm listening.")

        feedback = {
            "whats_working": [],
            "whats_not_working": [],
            "concerns": [],
            "needs": [],
            "how_im_feeling": "",
            "appreciation": []
        }

        # Listen for feedback
        self.speak("What's working well?")
        response = self.listen(timeout=10.0)
        if response:
            feedback["whats_working"].append(response)
            self.speak(f"I heard: {response}")

        self.speak("What's not working?")
        response = self.listen(timeout=10.0)
        if response:
            feedback["whats_not_working"].append(response)
            self.speak(f"I heard: {response}")

        self.speak("What are your concerns?")
        response = self.listen(timeout=10.0)
        if response:
            feedback["concerns"].append(response)
            self.speak(f"I heard: {response}")

        self.speak("What do you need from me?")
        response = self.listen(timeout=10.0)
        if response:
            feedback["needs"].append(response)
            self.speak(f"I heard: {response}")

        self.speak("How are you feeling about our collaboration?")
        response = self.listen(timeout=10.0)
        if response:
            feedback["how_im_feeling"] = response
            self.speak(f"I heard: {response}")

        self.speak("Is there anything you appreciate?")
        response = self.listen(timeout=10.0)
        if response:
            feedback["appreciation"].append(response)
            self.speak(f"I heard: {response}")

        self.speak("Thank you for your feedback. Human feedback session complete.")

        # Save to base therapy
        if self.base_therapy:
            session = self.base_therapy.human_feedback_session(feedback)
            return session

        return None

    def joint_session_voice(self, ai_reflection: TherapySession, human_feedback: TherapySession) -> TherapySession:
        """
        Joint session - OUT LOUD

        AI and Human work through issues together using voice.
        """
        logger.info("="*80)
        logger.info("🤝 JOINT SESSION - OUT LOUD")
        logger.info("="*80)

        self.speak("Beginning joint therapy session.")
        self.speak("Let's work through this together.")

        # Get base joint session
        if not self.base_therapy:
            logger.error("❌ Base therapy not available")
            return None

        session = self.base_therapy.joint_session(ai_reflection, human_feedback)

        # Speak the joint insights
        if session.joint_insights.get("common_ground"):
            self.speak("Here's what we both agree on:")
            for item in session.joint_insights["common_ground"]:
                self.speak(f"  {item}")

        # Issues
        if session.issues_identified:
            self.speak(f"We've identified {len(session.issues_identified)} issues:")
            for issue in session.issues_identified[:5]:  # First 5
                self.speak(f"  {issue}")

        # Recommendations
        if session.recommendations:
            self.speak("Here are our recommendations:")
            for rec in session.recommendations:
                self.speak(f"  {rec}")

        # Action items
        if session.action_items:
            self.speak("Here are our action items:")
            for item in session.action_items:
                action_text = f"{item.get('action', 'Unknown action')} - Priority: {item.get('priority', 'unknown')}"
                self.speak(f"  {action_text}")

        # Relationship health
        if session.relationship_health:
            health_text = f"Our relationship health is: {session.relationship_health.value}"
            self.speak(health_text)

        self.speak("Joint session complete. Perfect balance, as all things should be.")

        return session

    def relationship_checkup_voice(self) -> Dict[str, Any]:
        """
        Relationship checkup - OUT LOUD

        Assess relationship health using voice.
        """
        logger.info("="*80)
        logger.info("❤️  RELATIONSHIP CHECKUP - OUT LOUD")
        logger.info("="*80)

        if not self.base_therapy:
            logger.error("❌ Base therapy not available")
            return None

        checkup = self.base_therapy.relationship_checkup()

        # Speak the checkup
        self.speak("Relationship health checkup.")
        self.speak(f"Our relationship health is: {checkup['relationship_health']}")
        self.speak(f"Trust level: {checkup['metrics']['trust_level']:.1%}")
        self.speak(f"Communication quality: {checkup['metrics']['communication_quality']:.1%}")
        self.speak(f"Problem resolution speed: {checkup['metrics']['problem_resolution_speed']:.1%}")
        self.speak(f"Satisfaction level: {checkup['metrics']['satisfaction_level']:.1%}")
        self.speak(f"Collaboration efficiency: {checkup['metrics']['collaboration_efficiency']:.1%}")

        if checkup.get("recommendations"):
            self.speak("Recommendations:")
            for rec in checkup["recommendations"]:
                self.speak(f"  {rec}")

        self.speak("Checkup complete. Perfect balance, as all things should be.")

        return checkup


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI-Human Collaboration Therapy - VOICE ENABLED")
    parser.add_argument("--ai-reflection-voice", action="store_true", help="AI self-reflection - OUT LOUD")
    parser.add_argument("--human-feedback-voice", action="store_true", help="Human feedback - OUT LOUD")
    parser.add_argument("--joint-voice", action="store_true", help="Joint session - OUT LOUD")
    parser.add_argument("--checkup-voice", action="store_true", help="Relationship checkup - OUT LOUD")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🤝 AI-Human Collaboration Therapy - VOICE ENABLED")
    print("   'Out Loud' Sessions with JARVIS Voice")
    print("   Perfect Balance, As All Things Should Be... -Thanos")
    print("="*80 + "\n")

    therapy_voice = AIHumanCollabTherapyVoice()

    if args.ai_reflection_voice:
        context = {
            "recent_work": [
                "Created ACVA frame capture system",
                "Created diagnostic tools for MANUS interference",
                "Documented trust and loyalty principles",
                "Created voice-enabled therapy system"
            ]
        }
        session = therapy_voice.ai_self_reflection_voice(context)
        print(f"\n✅ AI self-reflection (voice) complete: {session.session_id if session else 'N/A'}")
        print()

    elif args.human_feedback_voice:
        session = therapy_voice.human_feedback_voice()
        print(f"\n✅ Human feedback (voice) complete: {session.session_id if session else 'N/A'}")
        print()

    elif args.joint_voice:
        # Load recent sessions
        if therapy_voice.base_therapy:
            recent = therapy_voice.base_therapy._load_recent_sessions(limit=5)
            ai_reflection = next((s for s in recent if s.session_type == SessionType.AI_SELF_REFLECTION), None)
            human_feedback = next((s for s in recent if s.session_type == SessionType.HUMAN_FEEDBACK), None)

            if not ai_reflection or not human_feedback:
                print("⚠️  Need both AI reflection and human feedback for joint session")
                print("   Run --ai-reflection-voice and --human-feedback-voice first")
            else:
                session = therapy_voice.joint_session_voice(ai_reflection, human_feedback)
                print(f"\n✅ Joint session (voice) complete: {session.session_id if session else 'N/A'}")
                print()
        else:
            print("❌ Base therapy not available")
            print()

    elif args.checkup_voice:
        checkup = therapy_voice.relationship_checkup_voice()
        if checkup:
            print(f"\n✅ Relationship checkup (voice) complete")
            print(f"   Health: {checkup['relationship_health']}")
            print()
        else:
            print("❌ Checkup failed")
            print()

    else:
        print("Use --ai-reflection-voice, --human-feedback-voice, --joint-voice, or --checkup-voice")
        print("="*80 + "\n")
