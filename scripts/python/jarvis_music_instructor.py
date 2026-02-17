#!/usr/bin/env python3
"""
JARVIS Music Instructor - Teaching Danny Boy Duet

JARVIS acts as a music instructor, teaching Glenda and the user to sing
"Danny Boy" as opposing tenors. Provides guidance, feedback, and corrections.

Tags: #MUSIC_INSTRUCTION #SINGING_COACH #DANNY_BOY #VOICE_TRAINING #ELEVENLABS #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass
from enum import Enum

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

logger = get_logger("JARVISMusicInstructor")

try:
    import speech_recognition as sr
    SPEECH_REC_AVAILABLE = True
except ImportError:
    SPEECH_REC_AVAILABLE = False
    logger.warning("⚠️  speech_recognition not available")

try:
    import pyaudio
    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False
    logger.warning("⚠️  pyaudio not available")

try:
    from jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("⚠️  ElevenLabs not available")

try:
    from jarvis_danny_boy_duet import DannyBoyDuet, MusicalPhrase, VoicePart
    DANNY_BOY_AVAILABLE = True
except ImportError:
    DANNY_BOY_AVAILABLE = False
    logger.warning("⚠️  Danny Boy duet not available")


class InstructionPhase(Enum):
    """Phases of music instruction"""
    INTRODUCTION = "introduction"
    DEMONSTRATION = "demonstration"  # JARVIS demonstrates with ElevenLabs
    LEARNING = "learning"  # Teaching individual parts
    PRACTICE = "practice"  # Student practice with feedback
    DUET_REHEARSAL = "duet_rehearsal"  # Singing together
    PERFORMANCE = "performance"  # Final performance


@dataclass
class StudentProgress:
    """Track student progress"""
    student_name: str
    voice_part: VoicePart
    phrases_learned: List[int] = None  # Indices of phrases learned
    current_phrase: int = 0
    attempts: int = 0
    feedback_received: List[str] = None

    def __post_init__(self):
        if self.phrases_learned is None:
            self.phrases_learned = []
        if self.feedback_received is None:
            self.feedback_received = []


class JARVISMusicInstructor:
    """
    JARVIS Music Instructor

    Teaches Glenda and the user to sing "Danny Boy" as opposing tenors.
    Provides guidance, feedback, and corrections.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Music Instructor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root

        # ElevenLabs TTS for instruction and demonstration
        self.elevenlabs_tts = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.elevenlabs_tts = JARVISElevenLabsTTS(project_root=self.project_root)
                logger.info("✅ ElevenLabs TTS loaded for instruction")
            except Exception as e:
                logger.warning(f"⚠️  ElevenLabs not available: {e}")

        # Danny Boy arrangement
        self.duet_system = None
        if DANNY_BOY_AVAILABLE:
            try:
                self.duet_system = DannyBoyDuet(project_root=self.project_root)
                logger.info("✅ Danny Boy arrangement loaded")
            except Exception as e:
                logger.warning(f"⚠️  Danny Boy not available: {e}")

        # Speech recognition for listening to students
        self.recognizer = None
        self.microphone = None
        if SPEECH_REC_AVAILABLE:
            try:
                self.recognizer = sr.Recognizer()
                self.microphone = sr.Microphone()
                logger.info("✅ Speech recognition ready for listening to students")
            except Exception as e:
                logger.warning(f"⚠️  Speech recognition not available: {e}")

        # Students
        self.glenda = StudentProgress("Glenda", VoicePart.TENOR_2)  # Lower tenor
        self.user = StudentProgress("User", VoicePart.TENOR_1)  # Higher tenor

        # Current phase
        self.current_phase = InstructionPhase.INTRODUCTION

        logger.info("✅ JARVIS Music Instructor initialized")
        logger.info("   🎵 Ready to teach 'Danny Boy' duet")

    def _speak(self, text: str):
        """Speak instruction using ElevenLabs"""
        if self.elevenlabs_tts:
            self.elevenlabs_tts.speak(text)
        else:
            print(f"JARVIS: {text}")

    def _listen_to_student(self, timeout: float = 10.0) -> Optional[str]:
        """Listen to student singing"""
        if not self.recognizer or not self.microphone:
            return None

        try:
            with self.microphone as source:
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

                # Listen for audio
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=15.0)

                # Recognize speech
                text = self.recognizer.recognize_google(audio, language="en-US")
                return text
        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except Exception as e:
            logger.debug(f"Error listening to student: {e}")
            return None

    def _analyze_pitch(self, audio_data: np.ndarray, sample_rate: int) -> Dict:
        """Analyze pitch of student's singing"""
        try:
            # FFT analysis
            fft_data = np.abs(np.fft.fft(audio_data))
            freqs = np.fft.fftfreq(len(fft_data), 1/sample_rate)

            # Find dominant frequency (pitch)
            dominant_freq_idx = np.argmax(fft_data[:len(fft_data)//2])
            dominant_freq = abs(freqs[dominant_freq_idx])

            # Energy
            energy = np.sum(audio_data ** 2)

            return {
                "pitch": dominant_freq,
                "energy": energy,
                "has_audio": energy > 0.01
            }
        except Exception as e:
            logger.debug(f"Pitch analysis error: {e}")
            return {"pitch": 0, "energy": 0, "has_audio": False}

    def _provide_feedback(self, student: StudentProgress, phrase: MusicalPhrase, 
                         pitch_analysis: Dict) -> str:
        """Provide feedback on student's singing"""
        feedback = []

        # Check if student is on pitch
        expected_pitch = self.duet_system._note_to_frequency(phrase.notes[0]) if self.duet_system else 0

        if pitch_analysis["has_audio"]:
            student_pitch = pitch_analysis["pitch"]

            if expected_pitch > 0:
                pitch_diff = abs(student_pitch - expected_pitch)
                pitch_diff_percent = (pitch_diff / expected_pitch) * 100

                if pitch_diff_percent < 5:
                    feedback.append("Excellent pitch! You're right on key.")
                elif pitch_diff_percent < 10:
                    feedback.append("Good pitch! Just a little adjustment needed.")
                elif student_pitch < expected_pitch:
                    feedback.append("Try singing a bit higher - you're slightly flat.")
                else:
                    feedback.append("Try singing a bit lower - you're slightly sharp.")

            # Energy/volume feedback
            if pitch_analysis["energy"] < 0.1:
                feedback.append("Sing with more confidence - I can barely hear you!")
            elif pitch_analysis["energy"] > 1.0:
                feedback.append("Great volume! You're projecting well.")
        else:
            feedback.append("I didn't hear you sing. Please try again.")

        return " ".join(feedback) if feedback else "Keep practicing!"

    def _record_student_audio(self, duration: float = 10.0) -> Optional[Tuple[np.ndarray, int]]:
        """Record student's singing for analysis"""
        if not PYAUDIO_AVAILABLE:
            return None

        try:

            sample_rate = 44100
            chunk = 1024
            frames = []

            audio = pyaudio.PyAudio()
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=sample_rate,
                input=True,
                frames_per_buffer=chunk
            )

            logger.info(f"🎤 Recording for {duration} seconds...")

            for _ in range(0, int(sample_rate / chunk * duration)):
                data = stream.read(chunk)
                frames.append(data)

            stream.stop_stream()
            stream.close()
            audio.terminate()

            # Convert to numpy array
            audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)

            return audio_data, sample_rate
        except Exception as e:
            logger.debug(f"Error recording audio: {e}")
            return None

    def start_instruction(self):
        """Start music instruction session"""
        logger.info("=" * 80)
        logger.info("🎵 JARVIS MUSIC INSTRUCTION - DANNY BOY DUET")
        logger.info("=" * 80)
        logger.info("   Teaching Glenda and User to sing as opposing tenors")
        logger.info("=" * 80)
        logger.info()

        # Phase 1: Introduction
        self._phase_introduction()

        # Phase 2: Demonstration (ElevenLabs test)
        self._phase_demonstration()

        # Phase 3: Learning individual parts
        self._phase_learning()

        # Phase 4: Practice with feedback
        self._phase_practice()

        # Phase 5: Duet rehearsal
        self._phase_duet_rehearsal()

        # Phase 6: Performance
        self._phase_performance()

        logger.info()
        logger.info("=" * 80)
        logger.info("✅ MUSIC INSTRUCTION COMPLETE")
        logger.info("=" * 80)

    def _phase_introduction(self):
        """Phase 1: Introduction"""
        self.current_phase = InstructionPhase.INTRODUCTION

        logger.info("📚 PHASE 1: INTRODUCTION")
        logger.info("-" * 80)

        intro_text = """
        Welcome to your music lesson! I'm JARVIS, your music instructor.

        Today, we're going to learn to sing "Danny Boy" together as a duet.
        Glenda, you'll be singing the lower tenor part (Tenor 2).
        And you, my friend, will be singing the higher tenor part (Tenor 1).

        We'll start by hearing how it should sound, then I'll teach you each part,
        and finally, we'll sing it together.

        Are you ready to begin?
        """

        self._speak(intro_text.strip())
        time.sleep(2)

    def _phase_demonstration(self):
        """Phase 2: Demonstration (ElevenLabs test)"""
        self.current_phase = InstructionPhase.DEMONSTRATION

        logger.info()
        logger.info("🎤 PHASE 2: DEMONSTRATION")
        logger.info("-" * 80)
        logger.info("   Testing ElevenLabs voice capabilities...")

        demo_text = """
        First, let me demonstrate how "Danny Boy" should sound when sung
        by two opposing tenors. I'll sing it using my voice synthesis system.

        Listen carefully to the harmony between the two tenor parts.
        """

        self._speak(demo_text.strip())
        time.sleep(2)

        # Demonstrate with ElevenLabs (if available)
        if self.duet_system:
            logger.info("   🎵 Playing demonstration...")
            self._speak("Here's how it sounds when sung by two opposing tenors:")
            time.sleep(1)

            # Play full demonstration using ElevenLabs or synthesized notes
            if self.elevenlabs_tts:
                # Use ElevenLabs to demonstrate (test voice capabilities)
                self._speak("This is a demonstration of my voice synthesis capabilities.")
                time.sleep(1)
                # Play the duet
                self.duet_system.sing_duet()
            else:
                # Fallback: synthesized notes
                self._speak("I'll demonstrate the melody and harmony using synthesized notes.")
                if self.duet_system:
                    self.duet_system.sing_duet()

        self._speak("That's how the duet should sound. Now, let's learn your parts!")
        time.sleep(2)

    def _phase_learning(self):
        """Phase 3: Learning individual parts"""
        self.current_phase = InstructionPhase.LEARNING

        logger.info()
        logger.info("📖 PHASE 3: LEARNING INDIVIDUAL PARTS")
        logger.info("-" * 80)

        if not self.duet_system or not self.duet_system.phrases:
            logger.warning("⚠️  Danny Boy arrangement not available")
            return

        # Get phrases for each voice part
        jarvis_phrases = [p for p in self.duet_system.phrases if p.voice_part == VoicePart.TENOR_1]
        glenda_phrases = [p for p in self.duet_system.phrases if p.voice_part == VoicePart.TENOR_2]

        # Teach User (Tenor 1 - Higher)
        self._speak("Let's start with your part - the higher tenor.")
        time.sleep(1)

        for i, phrase in enumerate(jarvis_phrases):
            logger.info(f"   Teaching phrase {i+1}/{len(jarvis_phrases)}: {phrase.lyrics}")

            instruction = f"""
            Phrase {i+1}: {phrase.lyrics}

            Listen to the melody. The notes are: {', '.join(phrase.notes[:3])}...

            Try singing this phrase after me.
            """

            self._speak(instruction.strip())
            time.sleep(2)

            # Demonstrate phrase
            if self.elevenlabs_tts:
                self._speak(phrase.lyrics)

            time.sleep(1)
            self.user.current_phrase = i

        # Teach Glenda (Tenor 2 - Lower)
        self._speak("Now, Glenda, let's learn your part - the lower tenor.")
        time.sleep(1)

        for i, phrase in enumerate(glenda_phrases):
            logger.info(f"   Teaching phrase {i+1}/{len(glenda_phrases)}: {phrase.lyrics}")

            instruction = f"""
            Phrase {i+1}: {phrase.lyrics}

            Your part is the harmony - you'll be singing a third below the melody.
            The notes are: {', '.join(phrase.notes[:3])}...

            Try singing this phrase after me.
            """

            self._speak(instruction.strip())
            time.sleep(2)

            # Demonstrate phrase
            if self.elevenlabs_tts:
                self._speak(phrase.lyrics)

            time.sleep(1)
            self.glenda.current_phrase = i

    def _phase_practice(self):
        """Phase 4: Practice with feedback"""
        self.current_phase = InstructionPhase.PRACTICE

        logger.info()
        logger.info("🎯 PHASE 4: PRACTICE WITH FEEDBACK")
        logger.info("-" * 80)

        if not self.duet_system or not self.duet_system.phrases:
            return

        # Practice each phrase with feedback
        jarvis_phrases = [p for p in self.duet_system.phrases if p.voice_part == VoicePart.TENOR_1]
        glenda_phrases = [p for p in self.duet_system.phrases if p.voice_part == VoicePart.TENOR_2]

        self._speak("Now let's practice each phrase. I'll listen and give you feedback.")
        time.sleep(2)

        # Practice User's part
        self._speak("Let's practice your part first.")
        for i, phrase in enumerate(jarvis_phrases):
            logger.info(f"   Practice phrase {i+1}: {phrase.lyrics}")

            self._speak(f"Sing phrase {i+1}: {phrase.lyrics}")
            self._speak("Ready? Go ahead and sing...")

            # Record and analyze student's singing
            audio_data = self._record_student_audio(duration=10.0)

            if audio_data:
                audio_array, sample_rate = audio_data
                pitch_analysis = self._analyze_pitch(audio_array, sample_rate)

                # Provide detailed feedback
                feedback = self._provide_feedback(self.user, phrase, pitch_analysis)
                self._speak(feedback)

                # Also check if lyrics match
                audio_text = self._listen_to_student(timeout=5.0)
                if audio_text:
                    logger.info(f"   Heard: {audio_text}")
                    if phrase.lyrics.lower() in audio_text.lower() or audio_text.lower() in phrase.lyrics.lower():
                        self._speak("Great! You're singing the right words. Keep working on the pitch and timing.")
                    else:
                        self._speak("Good effort! Make sure you're singing the correct lyrics.")
            else:
                self._speak("I didn't hear you sing. Please try again.")

            time.sleep(2)

        # Practice Glenda's part
        self._speak("Now, Glenda, let's practice your part.")
        for i, phrase in enumerate(glenda_phrases):
            logger.info(f"   Practice phrase {i+1}: {phrase.lyrics}")

            self._speak(f"Sing phrase {i+1}: {phrase.lyrics}")
            self._speak("Ready? Go ahead and sing...")

            # Record and analyze Glenda's singing
            audio_data = self._record_student_audio(duration=10.0)

            if audio_data:
                audio_array, sample_rate = audio_data
                pitch_analysis = self._analyze_pitch(audio_array, sample_rate)

                # Provide detailed feedback
                feedback = self._provide_feedback(self.glenda, phrase, pitch_analysis)
                self._speak(feedback)

                # Also check if lyrics match
                audio_text = self._listen_to_student(timeout=5.0)
                if audio_text:
                    logger.info(f"   Heard: {audio_text}")
                    if phrase.lyrics.lower() in audio_text.lower() or audio_text.lower() in phrase.lyrics.lower():
                        self._speak("Excellent! You're singing the right words. Keep working on the harmony.")
                    else:
                        self._speak("Good effort! Make sure you're singing the correct lyrics.")
            else:
                self._speak("I didn't hear you sing. Please try again.")

            time.sleep(2)

    def _phase_duet_rehearsal(self):
        """Phase 5: Duet rehearsal"""
        self.current_phase = InstructionPhase.DUET_REHEARSAL

        logger.info()
        logger.info("🎼 PHASE 5: DUET REHEARSAL")
        logger.info("-" * 80)

        self._speak("""
        Excellent progress! Now let's sing it together as a duet.

        Remember:
        - You sing the higher tenor part (Tenor 1)
        - Glenda sings the lower tenor part (Tenor 2)
        - We'll sing in harmony, just like JARVIS and Wanda would

        Let's start from the beginning. Ready? One, two, three...
        """)

        time.sleep(3)

        # Guide them through singing together
        self._speak("Sing together now - I'll listen and guide you.")
        time.sleep(1)

        # Listen to their duet
        audio_text = self._listen_to_student(timeout=60.0)  # Longer timeout for full song

        if audio_text:
            logger.info(f"   Heard duet: {audio_text}")
            self._speak("Wonderful! I heard you singing together. That's beautiful harmony!")
        else:
            self._speak("I didn't hear you sing. Please try again.")

        time.sleep(2)

    def _phase_performance(self):
        """Phase 6: Final performance"""
        self.current_phase = InstructionPhase.PERFORMANCE

        logger.info()
        logger.info("🎭 PHASE 6: FINAL PERFORMANCE")
        logger.info("-" * 80)

        self._speak("""
        Perfect! Now it's time for your final performance.

        Sing "Danny Boy" together as opposing tenors, just like we practiced.
        This is your moment to shine!

        Take a deep breath, and when you're ready, begin.
        """)

        time.sleep(3)

        # Listen to final performance
        self._speak("I'm listening... sing your hearts out!")

        audio_text = self._listen_to_student(timeout=90.0)  # Full song

        if audio_text:
            logger.info(f"   Performance heard: {audio_text}")
            self._speak("""
            Bravo! That was magnificent!

            You've successfully learned to sing "Danny Boy" as opposing tenors,
            just like JARVIS and Wanda would sing it.

            Your harmony was beautiful, and you both sang with confidence.
            Well done!
            """)
        else:
            self._speak("I didn't hear your performance. Please try again when you're ready.")

        time.sleep(2)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Music Instructor - Teaching Danny Boy Duet")
    parser.add_argument('--skip-demo', action='store_true', help='Skip ElevenLabs demonstration')

    args = parser.parse_args()

    print("=" * 80)
    print("🎵 JARVIS MUSIC INSTRUCTOR")
    print("=" * 80)
    print("   Teaching Glenda and User to sing 'Danny Boy' as opposing tenors")
    print("=" * 80)
    print()

    instructor = JARVISMusicInstructor()
    instructor.start_instruction()


if __name__ == "__main__":


    main()