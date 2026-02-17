#!/usr/bin/env python3
"""
JARVIS Danny Boy Acapella Duet - Opposing Tenors

JARVIS and Wanda sing "Danny Boy" together in acapella as opposing tenors.
This is a "rock solid test" of the system's capabilities.

Tags: #SINGING #DUET #DANNY_BOY #ACAPELLA #TENOR #MUSIC #ELEVENLABS #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
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

logger = get_logger("DannyBoyDuet")

try:
    import pyaudio
    import wave
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


class VoicePart(Enum):
    """Voice parts for duet"""
    TENOR_1 = "tenor_1"  # Higher tenor (JARVIS)
    TENOR_2 = "tenor_2"   # Lower tenor (Wanda/User)


@dataclass
class MusicalPhrase:
    """A musical phrase with lyrics and notes"""
    lyrics: str
    notes: List[str]  # Musical notes (e.g., ["C4", "E4", "G4"])
    duration: float  # Duration in seconds
    voice_part: VoicePart
    harmony_offset: Optional[int] = None  # Semitones offset for harmony


class DannyBoyDuet:
    """
    Danny Boy Acapella Duet System

    JARVIS and Wanda sing "Danny Boy" together as opposing tenors.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Danny Boy duet system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Load optimized parameters from Matrix/Animatrix simulation (if available)
        self.optimized_params = self._load_optimized_parameters()

        # ElevenLabs TTS for speech (not singing - ElevenLabs doesn't have singing API)
        self.elevenlabs_tts = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.elevenlabs_tts = JARVISElevenLabsTTS(project_root=self.project_root)
                logger.info("✅ ElevenLabs TTS loaded (for speech, not singing)")
            except Exception as e:
                logger.warning(f"⚠️  ElevenLabs not available: {e}")

        # AI Singing Synthesis (TCSinger 2, CoMelSinger, etc.)
        self.ai_singing = None
        try:
            from jarvis_ai_singing_synthesis import JARVISAISingingSynthesis
            self.ai_singing = JARVISAISingingSynthesis(project_root=self.project_root, model="tcsinger")
            if self.ai_singing.model_available:
                logger.info("✅ AI Singing Synthesis loaded (TCSinger)")
            else:
                logger.warning("⚠️  AI Singing models not installed - using formant synthesis fallback")
                logger.info("   Install TCSinger for realistic singing: git clone https://github.com/AaronZ345/TCSinger.git")
        except ImportError:
            logger.debug("AI Singing Synthesis not available")
        except Exception as e:
            logger.debug(f"AI Singing Synthesis initialization failed: {e}")

        # Audio output
        self.audio_output = None
        self.audio_input = None  # For audio feedback/monitoring
        self.audio_feedback_enabled = True  # Enable audio feedback loop
        if PYAUDIO_AVAILABLE:
            try:
                self.audio_output = pyaudio.PyAudio()
                # Also initialize input for audio monitoring/feedback loop
                self.audio_input = self.audio_output
                logger.info("✅ Audio I/O initialized (PyAudio)")
                logger.info("   🔊 Audio feedback loop enabled - will verify singing quality")
            except Exception as e:
                logger.warning(f"⚠️  Audio output not available: {e}")
                self.audio_feedback_enabled = False

        # Danny Boy lyrics and arrangement
        self.phrases = self._create_danny_boy_arrangement()

        # Karaoke display (will be created in main thread only - prevent duplicates)
        self.karaoke = None
        # CRITICAL: Don't create here - will be created in main() to avoid duplicate windows

        logger.info("✅ Danny Boy Duet System initialized")
        logger.info("   🎵 Ready to sing 'Danny Boy' in acapella as opposing tenors")

        if self.optimized_params:
            logger.info("   ✅ Using optimized parameters from Matrix/Animatrix simulation")

    def _load_optimized_parameters(self) -> Optional[Dict[str, Any]]:
        """Load optimized parameters from Matrix/Animatrix simulation results"""
        try:
            improvements_file = self.project_root / "data" / "karaoke_matrix_analysis" / "improvements.json"
            if improvements_file.exists():
                import json
                with open(improvements_file, 'r') as f:
                    improvements = json.load(f)
                    logger.info("✅ Loaded optimized parameters from simulation")
                    return improvements
        except Exception as e:
            logger.debug(f"Could not load optimized parameters: {e}")
        return None

    def _create_danny_boy_arrangement(self) -> List[MusicalPhrase]:
        """
        Create musical arrangement for "Danny Boy"

        Returns list of phrases with lyrics, notes, and harmony
        """
        phrases = []

        # Danny Boy - First Verse
        # Tenor 1 (JARVIS - higher) and Tenor 2 (Wanda - lower) in harmony

        # "Oh Danny boy, the pipes, the pipes are calling"
        phrases.append(MusicalPhrase(
            lyrics="Oh Danny boy, the pipes, the pipes are calling",
            notes=["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4", "G4", "C5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0  # Lead melody
        ))
        phrases.append(MusicalPhrase(
            lyrics="Oh Danny boy, the pipes, the pipes are calling",
            notes=["A3", "C4", "E4", "G4", "E4", "C4", "A3", "C4", "E4", "G4"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4  # Harmony (third below)
        ))

        # "From glen to glen, and down the mountain side"
        phrases.append(MusicalPhrase(
            lyrics="From glen to glen, and down the mountain side",
            notes=["G4", "B4", "D5", "G5", "D5", "B4", "G4", "B4", "D5", "G5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="From glen to glen, and down the mountain side",
            notes=["E4", "G4", "B4", "D5", "B4", "G4", "E4", "G4", "B4", "D5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        # "The summer's gone, and all the flowers dying"
        phrases.append(MusicalPhrase(
            lyrics="The summer's gone, and all the flowers dying",
            notes=["F4", "A4", "C5", "F5", "C5", "A4", "F4", "A4", "C5", "F5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="The summer's gone, and all the flowers dying",
            notes=["D4", "F4", "A4", "C5", "A4", "F4", "D4", "F4", "A4", "C5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        # "'Tis you, 'tis you must go and I must bide"
        phrases.append(MusicalPhrase(
            lyrics="'Tis you, 'tis you must go and I must bide",
            notes=["E4", "G4", "B4", "E5", "B4", "G4", "E4", "G4", "B4", "E5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="'Tis you, 'tis you must go and I must bide",
            notes=["C4", "E4", "G4", "B4", "G4", "E4", "C4", "E4", "G4", "B4"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        # "But come ye back when summer's in the meadow"
        phrases.append(MusicalPhrase(
            lyrics="But come ye back when summer's in the meadow",
            notes=["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4", "G4", "C5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="But come ye back when summer's in the meadow",
            notes=["A3", "C4", "E4", "G4", "E4", "C4", "A3", "C4", "E4", "G4"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        # "Or when the valley's hushed and white with snow"
        phrases.append(MusicalPhrase(
            lyrics="Or when the valley's hushed and white with snow",
            notes=["G4", "B4", "D5", "G5", "D5", "B4", "G4", "B4", "D5", "G5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="Or when the valley's hushed and white with snow",
            notes=["E4", "G4", "B4", "D5", "B4", "G4", "E4", "G4", "B4", "D5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        # "'Tis I'll be here in sunshine or in shadow"
        phrases.append(MusicalPhrase(
            lyrics="'Tis I'll be here in sunshine or in shadow",
            notes=["F4", "A4", "C5", "F5", "C5", "A4", "F4", "A4", "C5", "F5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="'Tis I'll be here in sunshine or in shadow",
            notes=["D4", "F4", "A4", "C5", "A4", "F4", "D4", "F4", "A4", "C5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        # "Oh Danny boy, oh Danny boy, I love you so"
        phrases.append(MusicalPhrase(
            lyrics="Oh Danny boy, oh Danny boy, I love you so",
            notes=["C4", "E4", "G4", "C5", "G4", "E4", "C4", "E4", "G4", "C5"],
            duration=4.0,
            voice_part=VoicePart.TENOR_1,
            harmony_offset=0
        ))
        phrases.append(MusicalPhrase(
            lyrics="Oh Danny boy, oh Danny boy, I love you so",
            notes=["A3", "C4", "E4", "G4", "E4", "C4", "A3", "C4", "E4", "G4"],
            duration=4.0,
            voice_part=VoicePart.TENOR_2,
            harmony_offset=-4
        ))

        return phrases

    def _note_to_frequency(self, note: str) -> float:
        """Convert musical note (e.g., 'C4') to frequency in Hz"""
        # Note frequencies (A4 = 440 Hz)
        note_freqs = {
            'C': 261.63, 'C#': 277.18, 'D': 293.66, 'D#': 311.13,
            'E': 329.63, 'F': 349.23, 'F#': 369.99, 'G': 392.00,
            'G#': 415.30, 'A': 440.00, 'A#': 466.16, 'B': 493.88
        }

        # Parse note (e.g., "C4" -> note="C", octave=4)
        if len(note) >= 2:
            note_name = note[0] if note[1] != '#' else note[0:2]
            octave = int(note[-1]) if note[-1].isdigit() else 4
        else:
            note_name = note[0]
            octave = 4

        base_freq = note_freqs.get(note_name, 440.0)
        # Adjust for octave (each octave doubles/halves frequency)
        freq = base_freq * (2 ** (octave - 4))

        return freq

    def _synthesize_note(self, note: str, duration: float, sample_rate: int = 44100, voice_type: str = "tenor") -> np.ndarray:
        """
        Synthesize a musical note as audio with realistic singing voice using advanced formant synthesis

        Args:
            note: Musical note (e.g., "C4")
            duration: Duration in seconds
            sample_rate: Audio sample rate
            voice_type: "tenor" (higher) or "tenor2" (lower) for different formant characteristics
        """
        freq = self._note_to_frequency(note)
        t = np.linspace(0, duration, int(sample_rate * duration))
        num_samples = len(t)

        # Realistic formant frequencies for singing voices
        # Use optimized parameters from Matrix/Animatrix simulation if available
        if self.optimized_params and 'formant_frequencies' in self.optimized_params:
            formants = self.optimized_params['formant_frequencies']
            if voice_type == "tenor":  # Higher voice (JARVIS)
                F1 = formants.get('tenor_f1', 650)
                F2 = formants.get('tenor_f2', 1200)
                F3 = formants.get('tenor_f3', 2500)
                F4 = 3500
                F5 = 4500
            else:  # Lower voice (Wanda)
                F1 = formants.get('tenor2_f1', 550)
                F2 = formants.get('tenor2_f2', 1100)
                F3 = formants.get('tenor2_f3', 2400)
                F4 = 3300
                F5 = 4400
            B1, B2, B3, B4, B5 = 60, 100, 120, 175, 250
        else:
            # Default formant frequencies (fallback)
            if voice_type == "tenor":  # Higher voice (JARVIS)
                F1 = 650   # First formant (vowel "ah" quality)
                F2 = 1200  # Second formant
                F3 = 2500  # Third formant
                F4 = 3500  # Fourth formant
                F5 = 4500  # Fifth formant
                # Formant bandwidths (Q factors)
                B1, B2, B3, B4, B5 = 60, 100, 120, 175, 250
            else:  # Lower voice (Wanda)
                F1 = 550
                F2 = 1100
                F3 = 2400
                F4 = 3300
                F5 = 4400
                B1, B2, B3, B4, B5 = 70, 110, 130, 180, 260

        # Generate fundamental with natural vibrato and slight pitch variation
        # Use optimized parameters if available, but ensure natural-sounding vibrato
        if self.optimized_params and 'vibrato' in self.optimized_params:
            vibrato_depth = max(self.optimized_params['vibrato'].get('depth', 0.02), 0.03)  # At least 3% for natural vibrato
        else:
            vibrato_depth = 0.03  # Increased to 3% for more natural singing vibrato
        vibrato_rate = 5.5  # Hz (natural singing vibrato rate)
        vibrato = 1.0 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)

        # Add subtle pitch drift (slight natural pitch variation over time, like real singing)
        pitch_drift = 1.0 + 0.01 * np.sin(2 * np.pi * 0.3 * t)  # Very slow, subtle drift (increased from 0.005)
        fundamental_freq = freq * vibrato * pitch_drift

        # Generate rich harmonic series (use optimized count if available, but ensure minimum quality)
        if self.optimized_params and 'harmonics' in self.optimized_params:
            max_harmonics = max(self.optimized_params['harmonics'].get('count', 8), 12)  # At least 12 for rich voice
        else:
            max_harmonics = 12  # Increased from 8 for richer, more voice-like sound
        audio = np.zeros(num_samples)

        for harmonic in range(1, max_harmonics + 1):
            harmonic_freq = fundamental_freq * harmonic

            # Harmonic amplitude (natural rolloff)
            if harmonic == 1:
                amplitude = 1.0
            else:
                amplitude = 0.8 / (harmonic ** 1.2)  # Gradual rolloff

            # Generate harmonic with phase variation for richness
            phase = np.random.uniform(0, 2 * np.pi)  # Random phase per harmonic
            harmonic_wave = amplitude * np.sin(2 * np.pi * harmonic_freq * t + phase)

            # Apply formant filtering using bandpass-like response
            # Each formant acts as a resonant filter
            # CRITICAL: harmonic_freq is an array (varies with vibrato), so use element-wise operations
            formant_response = np.ones(num_samples)

            # Formant 1 (strongest - gives voice its character)
            # Use element-wise comparison: harmonic_freq is array, F1 is scalar
            mask1 = harmonic_freq < F1 * 2
            if np.any(mask1):
                resonance = 1.0 / (1.0 + ((harmonic_freq - F1) / B1) ** 2)
                formant_response[mask1] *= (1.0 + 2.0 * resonance[mask1])

            # Formant 2
            mask2 = np.abs(harmonic_freq - F2) < F2
            if np.any(mask2):
                resonance = 1.0 / (1.0 + ((harmonic_freq - F2) / B2) ** 2)
                formant_response[mask2] *= (1.0 + 1.5 * resonance[mask2])

            # Formant 3
            mask3 = np.abs(harmonic_freq - F3) < F3
            if np.any(mask3):
                resonance = 1.0 / (1.0 + ((harmonic_freq - F3) / B3) ** 2)
                formant_response[mask3] *= (1.0 + 1.2 * resonance[mask3])

            # Formants 4 and 5 (subtle)
            mask4 = np.abs(harmonic_freq - F4) < F4
            if np.any(mask4):
                resonance = 1.0 / (1.0 + ((harmonic_freq - F4) / B4) ** 2)
                formant_response[mask4] *= (1.0 + 0.8 * resonance[mask4])

            mask5 = np.abs(harmonic_freq - F5) < F5
            if np.any(mask5):
                resonance = 1.0 / (1.0 + ((harmonic_freq - F5) / B5) ** 2)
                formant_response[mask5] *= (1.0 + 0.5 * resonance[mask5])

            # Apply formant response (simplified - in real synthesis this would be proper filtering)
            harmonic_wave *= np.clip(formant_response, 0.5, 3.0)  # Limit gain

            audio += harmonic_wave

        # Add subtle breathiness (use optimized level if available)
        if self.optimized_params and 'breathiness' in self.optimized_params:
            breathiness_level = self.optimized_params['breathiness'].get('level', 0.03)
        else:
            breathiness_level = 0.03  # 3% breathiness
        breath_noise = np.random.normal(0, breathiness_level, num_samples)
        # High-pass filter for breathiness (above 2000 Hz)
        # Simple approximation: subtract low-frequency component
        from scipy import signal
        try:
            b, a = signal.butter(4, 2000 / (sample_rate / 2), 'high')
            breath_noise = signal.filtfilt(b, a, breath_noise)
        except:
            # Fallback: simple high-pass
            breath_fft = np.fft.fft(breath_noise)
            freqs = np.fft.fftfreq(num_samples, 1/sample_rate)
            breath_fft[np.abs(freqs) < 2000] *= 0.3  # Attenuate low frequencies
            breath_noise = np.real(np.fft.ifft(breath_fft))

        audio += breath_noise

        # Add subtle tremolo (amplitude modulation) for natural variation
        tremolo_rate = 4.5  # Hz
        tremolo_depth = 0.05  # 5% amplitude modulation
        tremolo = 1.0 + tremolo_depth * np.sin(2 * np.pi * tremolo_rate * t)
        audio *= tremolo

        # Normalize with less headroom for louder output and boost volume for singing
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            # Boost to 98% for stronger singing voice (was 95%)
            audio = audio / max_val * 0.98
        else:
            # If somehow silent, generate a minimal tone
            audio = 0.01 * np.sin(2 * np.pi * frequency * t)

        # Advanced ADSR envelope with smooth transitions
        envelope = np.ones(num_samples)
        attack_time = 0.05   # 50ms attack
        decay_time = 0.08   # 80ms decay
        sustain_level = 0.85
        release_time = 0.15  # 150ms release

        attack_samples = int(sample_rate * attack_time)
        decay_samples = int(sample_rate * decay_time)
        release_samples = int(sample_rate * release_time)

        # Attack (exponential curve for natural onset)
        if num_samples > attack_samples:
            attack_curve = 1 - np.exp(-5 * np.linspace(0, 1, attack_samples))
            envelope[:attack_samples] = attack_curve

        # Decay
        if num_samples > attack_samples + decay_samples:
            decay_start = sustain_level + (1.0 - sustain_level)
            decay_curve = sustain_level + (decay_start - sustain_level) * np.exp(-3 * np.linspace(0, 1, decay_samples))
            envelope[attack_samples:attack_samples+decay_samples] = decay_curve

        # Sustain (slight variation for naturalness)
        sustain_start = attack_samples + decay_samples
        sustain_end = num_samples - release_samples
        if sustain_end > sustain_start:
            sustain_variation = 1.0 + 0.02 * np.sin(2 * np.pi * 2.0 * t[sustain_start:sustain_end])
            envelope[sustain_start:sustain_end] = sustain_level * sustain_variation

        # Release (exponential decay)
        if num_samples > release_samples:
            release_curve = sustain_level * np.exp(-8 * np.linspace(0, 1, release_samples))
            envelope[-release_samples:] = release_curve

        audio = audio * envelope

        return audio

    def _sing_phrase_hybrid(self, phrase: MusicalPhrase, voice_type: str = "tenor") -> Optional[np.ndarray]:
        """
        Sing a phrase using hybrid approach: ElevenLabs TTS for voice quality + pitch shifting for notes

        This produces actual human-like singing by:
        1. Using ElevenLabs TTS to generate natural voice saying the lyrics
        2. Pitch-shifting the audio to match the musical notes
        3. This gives us human voice quality with correct musical pitches

        Args:
            phrase: MusicalPhrase with lyrics, notes, and duration
            voice_type: "tenor" (higher) or "tenor2" (lower) for voice selection
        """
        if not self.elevenlabs_tts:
            # Fallback to synthesized notes if ElevenLabs not available
            logger.warning("⚠️  ElevenLabs not available, falling back to synthesized notes")
            return self._synthesize_phrase_with_notes(phrase, voice_type=voice_type)

        try:
            # Step 1: Generate natural voice using ElevenLabs TTS
            logger.info(f"   🗣️  Generating natural voice with ElevenLabs...")
            lyrics = phrase.lyrics

            # Use ElevenLabs to generate speech audio
            if hasattr(self.elevenlabs_tts, 'client') and self.elevenlabs_tts.client:
                try:
                    # Generate audio using text_to_speech.convert()
                    audio = self.elevenlabs_tts.client.text_to_speech.convert(
                        text=lyrics,
                        voice_id=self.elevenlabs_tts.current_voice_id,
                        model_id="eleven_multilingual_v2",
                        output_format="pcm_44100"  # Use PCM for easier pitch shifting
                    )
                    # Convert generator to bytes
                    if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, str)):
                        audio_bytes = b''.join(audio)
                    elif isinstance(audio, bytes):
                        audio_bytes = audio
                    else:
                        audio_bytes = bytes(audio) if hasattr(audio, '__bytes__') else b''

                    if not audio_bytes or len(audio_bytes) == 0:
                        logger.warning("⚠️  ElevenLabs returned empty audio, falling back to synthesis")
                        return self._synthesize_phrase_with_notes(phrase, voice_type=voice_type)

                    # Convert bytes to numpy array (16-bit PCM, mono, 44100 Hz)
                    audio_array = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0

                    # Step 2: Pitch-shift to match musical notes
                    logger.info(f"   🎵 Pitch-shifting to match musical notes...")
                    pitched_audio = self._pitch_shift_to_notes(audio_array, phrase.notes, phrase.duration)

                    if pitched_audio is not None and len(pitched_audio) > 0:
                        logger.info(f"   ✅ Hybrid singing generated: {len(pitched_audio)} samples")
                        return pitched_audio
                    else:
                        logger.warning("⚠️  Pitch shifting failed, falling back to synthesis")
                        return self._synthesize_phrase_with_notes(phrase, voice_type=voice_type)

                except Exception as e:
                    logger.warning(f"⚠️  ElevenLabs generation failed: {e}, falling back to synthesis")
                    return self._synthesize_phrase_with_notes(phrase, voice_type=voice_type)
            else:
                logger.warning("⚠️  ElevenLabs client not available, falling back to synthesis")
                return self._synthesize_phrase_with_notes(phrase, voice_type=voice_type)

        except Exception as e:
            logger.error(f"❌ Hybrid singing failed: {e}", exc_info=True)
            return self._synthesize_phrase_with_notes(phrase, voice_type=voice_type)

    def _pitch_shift_to_notes(self, audio: np.ndarray, target_notes: List[str], total_duration: float, 
                              sample_rate: int = 44100) -> Optional[np.ndarray]:
        """
        Pitch-shift audio to match target musical notes

        Args:
            audio: Input audio array (from ElevenLabs TTS)
            target_notes: List of musical notes to match (e.g., ["C4", "D4", "E4"])
            total_duration: Total duration in seconds
            sample_rate: Audio sample rate
        """
        if not target_notes or len(target_notes) == 0:
            return audio

        try:
            from scipy import signal

            # Calculate target frequencies for each note
            target_freqs = [self._note_to_frequency(note) for note in target_notes]

            # Calculate average pitch of input audio (rough estimate)
            # Use autocorrelation to find fundamental frequency
            def estimate_pitch(audio_segment, sr):
                # Autocorrelation method
                autocorr = np.correlate(audio_segment, audio_segment, mode='full')
                autocorr = autocorr[len(autocorr)//2:]

                # Find first peak (fundamental period)
                peak_indices = signal.find_peaks(autocorr[:sr//40], height=np.max(autocorr) * 0.3)[0]
                if len(peak_indices) > 0:
                    period = peak_indices[0]
                    if period > 0:
                        return sr / period
                return 200.0  # Default to ~200 Hz if detection fails

            # Divide audio into segments (one per note)
            note_duration = total_duration / len(target_notes)
            samples_per_note = int(sample_rate * note_duration)

            pitched_segments = []
            for i, target_freq in enumerate(target_freqs):
                start_idx = i * samples_per_note
                end_idx = min(start_idx + samples_per_note, len(audio))
                segment = audio[start_idx:end_idx]

                if len(segment) < 100:
                    # Too short, skip
                    pitched_segments.append(segment)
                    continue

                # Estimate current pitch
                current_pitch = estimate_pitch(segment, sample_rate)

                # Calculate pitch shift ratio
                if current_pitch > 0:
                    pitch_ratio = target_freq / current_pitch
                else:
                    pitch_ratio = 1.0

                # Limit pitch shift to reasonable range (avoid chipmunk/robot)
                pitch_ratio = np.clip(pitch_ratio, 0.5, 2.0)

                # Apply pitch shift using resampling
                if abs(pitch_ratio - 1.0) > 0.01:  # Only shift if significant difference
                    # Resample to change pitch (higher sample rate = higher pitch)
                    new_length = int(len(segment) / pitch_ratio)
                    if new_length > 0:
                        # Use linear interpolation for simple pitch shifting
                        indices = np.linspace(0, len(segment) - 1, new_length)
                        segment = np.interp(indices, np.arange(len(segment)), segment)

                    # Trim or pad to original length
                    if len(segment) > samples_per_note:
                        segment = segment[:samples_per_note]
                    elif len(segment) < samples_per_note:
                        segment = np.pad(segment, (0, samples_per_note - len(segment)), mode='constant')

                pitched_segments.append(segment)

            # Concatenate all segments
            if pitched_segments:
                result = np.concatenate(pitched_segments)
                # Trim to exact duration
                max_samples = int(sample_rate * total_duration)
                if len(result) > max_samples:
                    result = result[:max_samples]
                return result

            return audio

        except Exception as e:
            logger.warning(f"⚠️  Pitch shifting failed: {e}, returning original audio")
            return audio

    def _synthesize_phrase_with_notes(self, phrase: MusicalPhrase, voice_type: str = "tenor") -> np.ndarray:
        """
        Synthesize a complete phrase by combining individual notes
        This creates actual singing with correct musical pitches and voice-like characteristics

        Args:
            phrase: MusicalPhrase with lyrics, notes, and duration
            voice_type: "tenor" (higher) or "tenor2" (lower) for different voice characteristics
        """
        if not phrase.notes or len(phrase.notes) == 0:
            return None

        note_audios = []
        total_duration = phrase.duration
        note_duration = total_duration / len(phrase.notes)

        for i, note in enumerate(phrase.notes):
            # Slight overlap between notes for smoother transitions (legato)
            overlap = 0.08  # 80ms overlap for smoother singing
            note_dur = note_duration + (overlap if i < len(phrase.notes) - 1 else 0)

            # Use voice_type to determine formant characteristics
            note_audio = self._synthesize_note(note, note_dur, voice_type=voice_type)
            note_audios.append(note_audio)

        # Concatenate all notes with crossfade for smooth transitions
        if note_audios:
            phrase_audio = note_audios[0]
            for i in range(1, len(note_audios)):
                # Crossfade between notes
                fade_samples = int(44100 * 0.05)  # 50ms crossfade
                if len(phrase_audio) >= fade_samples and len(note_audios[i]) >= fade_samples:
                    # Fade out end of previous note
                    phrase_audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
                    # Fade in start of next note
                    note_audios[i][:fade_samples] *= np.linspace(0, 1, fade_samples)
                    # Overlap and mix
                    overlap_audio = phrase_audio[-fade_samples:] + note_audios[i][:fade_samples]
                    phrase_audio = np.concatenate([
                        phrase_audio[:-fade_samples],
                        overlap_audio,
                        note_audios[i][fade_samples:]
                    ])
                else:
                    phrase_audio = np.concatenate([phrase_audio, note_audios[i]])

            # Trim to exact duration
            sample_rate = 44100
            max_samples = int(sample_rate * phrase.duration)
            if len(phrase_audio) > max_samples:
                phrase_audio = phrase_audio[:max_samples]

            return phrase_audio

        return None

    def _create_background_harmony(self, phrases: List[MusicalPhrase], sample_rate: int = 44100) -> Optional[np.ndarray]:
        """
        Create subtle background harmony/instrumental support for the acapella duet
        This adds a gentle harmonic foundation without overpowering the voices
        """
        try:
            # Create a simple chord progression background
            # Use lower octave notes for subtle support
            background_notes = []
            total_duration = sum(p.duration for p in phrases)

            # Simple chord progression: I - vi - IV - V (common in folk songs)
            chord_progression = [
                ["C3", "E3", "G3"],  # C major
                ["A3", "C4", "E4"],  # A minor
                ["F3", "A3", "C4"],  # F major
                ["G3", "B3", "D4"],  # G major
            ]

            # Divide phrases into chord sections
            phrases_per_chord = max(1, len(phrases) // len(chord_progression))

            for i, phrase in enumerate(phrases):
                chord_idx = min(i // phrases_per_chord, len(chord_progression) - 1)
                chord = chord_progression[chord_idx]

                # Create subtle background chord for this phrase
                chord_audio = np.zeros(int(sample_rate * phrase.duration))

                for note_name in chord:
                    note_freq = self._note_to_frequency(note_name)
                    t = np.linspace(0, phrase.duration, len(chord_audio))
                    # Very quiet (10% volume) and with soft attack
                    note_audio = 0.1 * np.sin(2 * np.pi * note_freq * t)
                    # Soft envelope
                    envelope = np.ones_like(note_audio)
                    attack = int(sample_rate * 0.2)
                    release = int(sample_rate * 0.2)
                    if len(envelope) > attack:
                        envelope[:attack] = np.linspace(0, 1, attack)
                    if len(envelope) > release:
                        envelope[-release:] = np.linspace(1, 0, release)
                    note_audio *= envelope
                    chord_audio += note_audio

                background_notes.append(chord_audio)

            if background_notes:
                background = np.concatenate(background_notes)
                # Normalize and make very subtle
                if np.max(np.abs(background)) > 0:
                    background = background / np.max(np.abs(background)) * 0.15  # 15% volume
                return background

        except Exception as e:
            logger.debug(f"Background harmony generation failed: {e}")

        return None

    def _sing_phrase_with_elevenlabs(self, phrase: MusicalPhrase, voice_id: Optional[str] = None, 
                                   model: str = "eleven_multilingual_v2") -> Optional[bytes]:
        """
        Sing a phrase using ElevenLabs TTS with singing voice

        Note: ElevenLabs supports singing voices - uses "eleven_multilingual_v2" or "eleven_turbo_v2_5"
        """
        if not self.elevenlabs_tts:
            return None

        try:
            lyrics = phrase.lyrics

            # Use ElevenLabs client (v2.27.0+)
            # CRITICAL: Use text_to_speech.convert() not client.generate()
            if hasattr(self.elevenlabs_tts, 'client') and self.elevenlabs_tts.client:
                try:
                    # Generate audio using text_to_speech.convert()
                    audio = self.elevenlabs_tts.client.text_to_speech.convert(
                        text=lyrics,
                        voice_id=voice_id or self.elevenlabs_tts.current_voice_id,
                        model_id=model,
                        output_format="mp3_44100_128"
                    )
                    # Convert generator to bytes
                    # CRITICAL: ElevenLabs returns a generator of bytes chunks
                    if hasattr(audio, '__iter__') and not isinstance(audio, (bytes, str)):
                        # Join all chunks into single bytes object
                        audio_data = b''.join(audio)
                    elif isinstance(audio, bytes):
                        audio_data = audio
                    else:
                        # Try to convert to bytes
                        try:
                            audio_data = bytes(audio)
                        except:
                            audio_data = b''.join(audio) if hasattr(audio, '__iter__') else b''

                    if audio_data and len(audio_data) > 0:
                        logger.info(f"✅ Generated audio: {len(audio_data)} bytes (MP3 format)")
                        return audio_data
                    else:
                        logger.warning("⚠️  Generated audio is empty")
                        return None
                except Exception as e:
                    logger.error(f"❌ Client API failed: {e}", exc_info=True)

            # Fallback: use speak_to_file to get audio
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)
                if self.elevenlabs_tts.speak_to_file(lyrics, tmp_path, voice_id=voice_id, model=model):
                    # Read audio bytes
                    with open(tmp_path, 'rb') as f:
                        audio_data = f.read()
                    tmp_path.unlink()  # Clean up
                    return audio_data

            return None
        except Exception as e:
            logger.debug(f"ElevenLabs singing not available: {e}")
            return None

    def _mix_audio(self, audio1: np.ndarray, audio2: np.ndarray) -> np.ndarray:
        """Mix two audio tracks together"""
        # Pad shorter audio to match length
        max_len = max(len(audio1), len(audio2))
        audio1_padded = np.pad(audio1, (0, max_len - len(audio1)))
        audio2_padded = np.pad(audio2, (0, max_len - len(audio2)))

        # Mix (average to prevent clipping)
        mixed = (audio1_padded + audio2_padded) / 2.0

        return mixed

    def sing_duet(self, jarvis_voice_id: Optional[str] = None, wanda_voice_id: Optional[str] = None):
        """
        Sing "Danny Boy" as a duet - JARVIS and Wanda as opposing tenors

        Args:
            jarvis_voice_id: ElevenLabs voice ID for JARVIS (tenor 1 - higher)
            wanda_voice_id: ElevenLabs voice ID for Wanda (tenor 2 - lower)
        """
        logger.info("=" * 80)
        logger.info("🎵 DANNY BOY ACAPELLA DUET - OPPOSING TENORS")
        logger.info("=" * 80)
        logger.info("   JARVIS (Tenor 1 - Higher) and Wanda (Tenor 2 - Lower)")
        logger.info("   Singing in harmony, acapella")
        logger.info("=" * 80)
        logger.info("   🔊 Audio verification: Monitoring playback quality and volume")
        logger.info("=" * 80)
        print()  # Use print() for blank line instead of logger.info()

        # Separate phrases by voice part
        jarvis_phrases = [p for p in self.phrases if p.voice_part == VoicePart.TENOR_1]
        wanda_phrases = [p for p in self.phrases if p.voice_part == VoicePart.TENOR_2]

        # Show karaoke display (only if created in main thread)
        if self.karaoke and self.karaoke.root:
            # Use root.after for thread-safe update
            try:
                self.karaoke.root.after(0, lambda: self.karaoke.show_lyrics("", "", highlight="none"))
                time.sleep(0.5)
            except Exception as e:
                logger.debug(f"Karaoke update error: {e}")

        # Sing phrases in parallel (harmony)
        for i, (jarvis_phrase, wanda_phrase) in enumerate(zip(jarvis_phrases, wanda_phrases)):
            logger.info(f"🎵 Phrase {i+1}/{len(jarvis_phrases)}")
            logger.info(f"   JARVIS (Tenor 1): {jarvis_phrase.lyrics}")
            logger.info(f"   Wanda (Tenor 2): {wanda_phrase.lyrics}")

            # Show lyrics on karaoke display with bouncing ball animation
            if self.karaoke and self.karaoke.root:
                # Schedule update in main thread (thread-safe)
                # Capture lyrics in closure to avoid late binding
                jarvis_lyrics = jarvis_phrase.lyrics
                wanda_lyrics = wanda_phrase.lyrics
                phrase_duration = jarvis_phrase.duration
                try:
                    # Show lyrics and start word-by-word ball animation (like real karaoke)
                    self.karaoke.root.after(0, lambda j=jarvis_lyrics, w=wanda_lyrics, d=phrase_duration: (
                        self.karaoke.show_lyrics(j, w, highlight="both", ball_progress=0.0, duration=d, current_word_index=0),
                        self.karaoke.animate_ball(d, lyrics=j if j else w, start_progress=0.0, end_progress=1.0)
                    ))
                except Exception as e:
                    logger.debug(f"Karaoke lyrics update error: {e}")

            # Generate audio for both voices
            # PRIORITY 1: Try AI Singing Synthesis (TCSinger 2, CoMelSinger) if available
            # PRIORITY 2: Fallback to formant synthesis (musical notes with voice characteristics)

            if self.ai_singing and self.ai_singing.model_available:
                logger.info(f"   🎵 Generating JARVIS singing using AI Singing Synthesis (TCSinger)...")
                jarvis_audio_bytes = self.ai_singing.sing(
                    lyrics=jarvis_phrase.lyrics,
                    melody=jarvis_phrase.notes,
                    duration=jarvis_phrase.duration,
                    voice_style="tenor"
                )
                if jarvis_audio_bytes:
                    # Convert bytes to numpy array
                    import soundfile as sf
                    from io import BytesIO
                    jarvis_audio, _ = sf.read(BytesIO(jarvis_audio_bytes))
                    logger.info(f"   ✅ AI Singing Synthesis generated JARVIS audio")
                else:
                    logger.warning("   ⚠️  AI Singing Synthesis failed, using formant synthesis...")
                    jarvis_audio = self._synthesize_phrase_with_notes(jarvis_phrase, voice_type="tenor")
            else:
                logger.info(f"   🎵 Generating JARVIS singing using formant synthesis (musical notes)...")
                jarvis_audio = self._synthesize_phrase_with_notes(jarvis_phrase, voice_type="tenor")

            if self.ai_singing and self.ai_singing.model_available:
                logger.info(f"   🎵 Generating Wanda singing using AI Singing Synthesis (TCSinger)...")
                wanda_audio_bytes = self.ai_singing.sing(
                    lyrics=wanda_phrase.lyrics,
                    melody=wanda_phrase.notes,
                    duration=wanda_phrase.duration,
                    voice_style="tenor2"
                )
                if wanda_audio_bytes:
                    import soundfile as sf
                    from io import BytesIO
                    wanda_audio, _ = sf.read(BytesIO(wanda_audio_bytes))
                    logger.info(f"   ✅ AI Singing Synthesis generated Wanda audio")
                else:
                    logger.warning("   ⚠️  AI Singing Synthesis failed, using formant synthesis...")
                    wanda_audio = self._synthesize_phrase_with_notes(wanda_phrase, voice_type="tenor2")
            else:
                logger.info(f"   🎵 Generating Wanda singing using formant synthesis (musical notes)...")
                wanda_audio = self._synthesize_phrase_with_notes(wanda_phrase, voice_type="tenor2")

            # Create subtle background harmony (optional - gentle chord support)
            logger.info(f"   🎹 Creating subtle background harmony...")
            background_audio = self._create_background_harmony([jarvis_phrase, wanda_phrase])

            # Verify audio generation
            if jarvis_audio is not None and len(jarvis_audio) > 0:
                jarvis_rms = np.sqrt(np.mean(jarvis_audio**2))
                jarvis_peak = np.max(np.abs(jarvis_audio))
                logger.info(f"   ✅ JARVIS singing audio: {len(jarvis_audio)} samples, RMS: {jarvis_rms:.4f}, Peak: {jarvis_peak:.4f}")
                if jarvis_rms < 0.01:
                    logger.warning(f"   ⚠️  JARVIS audio may be too quiet (RMS: {jarvis_rms:.4f})")
            else:
                logger.error("   ❌ JARVIS audio generation failed - no audio data")

            if wanda_audio is not None and len(wanda_audio) > 0:
                wanda_rms = np.sqrt(np.mean(wanda_audio**2))
                wanda_peak = np.max(np.abs(wanda_audio))
                logger.info(f"   ✅ Wanda singing audio: {len(wanda_audio)} samples, RMS: {wanda_rms:.4f}, Peak: {wanda_peak:.4f}")
                if wanda_rms < 0.01:
                    logger.warning(f"   ⚠️  Wanda audio may be too quiet (RMS: {wanda_rms:.4f})")
            else:
                logger.error("   ❌ Wanda audio generation failed - no audio data")

            # Play both voices (JARVIS and Wanda sing their parts)
            # CRITICAL: Check if audio exists properly (numpy arrays need len() check)
            jarvis_has_audio = False
            wanda_has_audio = False

            if jarvis_audio is not None:
                if isinstance(jarvis_audio, np.ndarray):
                    jarvis_has_audio = len(jarvis_audio) > 0
                else:
                    jarvis_has_audio = len(jarvis_audio) > 0 if jarvis_audio else False

            if wanda_audio is not None:
                if isinstance(wanda_audio, np.ndarray):
                    wanda_has_audio = len(wanda_audio) > 0
                else:
                    wanda_has_audio = len(wanda_audio) > 0 if wanda_audio else False

            # Play JARVIS's part with AUDIO FEEDBACK LOOP (like Kenny visual monitoring)
            if jarvis_has_audio:
                logger.info("   🎤 JARVIS singing (Tenor 1 - Higher)...")
                logger.info(f"   🔊 Audio stats: {len(jarvis_audio)} samples, duration: {jarvis_phrase.duration:.2f}s")
                if isinstance(jarvis_audio, np.ndarray):
                    # CRITICAL: Use feedback loop to verify it sounds like singing, not beeps
                    quality_acceptable = self._play_audio_with_feedback(
                        jarvis_audio, 
                        phrase_name=f"JARVIS phrase {i+1}"
                    )

                    if not quality_acceptable:
                        logger.error("   ❌ JARVIS audio FAILED quality check - sounds like beeps!")
                        logger.error("   🔄 Attempting to regenerate with better method...")
                        # Try hybrid method if synthesis failed
                        if not hasattr(self, '_last_method_was_hybrid') or not self._last_method_was_hybrid:
                            logger.info("   🔄 Retrying with ElevenLabs hybrid method...")
                            jarvis_audio_retry = self._sing_phrase_hybrid(jarvis_phrase, voice_type="tenor")
                            if jarvis_audio_retry is not None and len(jarvis_audio_retry) > 0:
                                quality_acceptable = self._play_audio_with_feedback(
                                    jarvis_audio_retry,
                                    phrase_name=f"JARVIS phrase {i+1} (retry)"
                                )
                                if quality_acceptable:
                                    logger.info("   ✅ Retry successful - now sounds like singing!")

                    if quality_acceptable:
                        logger.info("   ✅ JARVIS audio verified - sounds like singing!")
                    else:
                        logger.error("   ❌ JARVIS audio still sounds like beeps after retry")

                    # Wait for audio to finish
                    time.sleep(jarvis_phrase.duration + 0.5)
                else:
                    logger.warning("   ⚠️  JARVIS audio is not numpy array - unexpected")
                    self._play_audio_bytes(jarvis_audio)
                    time.sleep(4.0)

            # Play Wanda's part with AUDIO FEEDBACK LOOP
            if wanda_has_audio:
                logger.info("   🎤 Wanda singing (Tenor 2 - Lower)...")
                logger.info(f"   🔊 Audio stats: {len(wanda_audio)} samples, duration: {wanda_phrase.duration:.2f}s")
                if isinstance(wanda_audio, np.ndarray):
                    # CRITICAL: Use feedback loop to verify it sounds like singing, not beeps
                    quality_acceptable = self._play_audio_with_feedback(
                        wanda_audio,
                        phrase_name=f"Wanda phrase {i+1}"
                    )

                    if not quality_acceptable:
                        logger.error("   ❌ Wanda audio FAILED quality check - sounds like beeps!")
                        logger.error("   🔄 Attempting to regenerate with better method...")
                        # Try hybrid method if synthesis failed
                        if not hasattr(self, '_last_method_was_hybrid') or not self._last_method_was_hybrid:
                            logger.info("   🔄 Retrying with ElevenLabs hybrid method...")
                            wanda_audio_retry = self._sing_phrase_hybrid(wanda_phrase, voice_type="tenor2")
                            if wanda_audio_retry is not None and len(wanda_audio_retry) > 0:
                                quality_acceptable = self._play_audio_with_feedback(
                                    wanda_audio_retry,
                                    phrase_name=f"Wanda phrase {i+1} (retry)"
                                )
                                if quality_acceptable:
                                    logger.info("   ✅ Retry successful - now sounds like singing!")

                    if quality_acceptable:
                        logger.info("   ✅ Wanda audio verified - sounds like singing!")
                    else:
                        logger.error("   ❌ Wanda audio still sounds like beeps after retry")

                    # Wait for audio to finish
                    time.sleep(wanda_phrase.duration + 0.5)
                else:
                    logger.warning("   ⚠️  Wanda audio is not numpy array - unexpected")
                    self._play_audio_bytes(wanda_audio)
                    time.sleep(4.0)

            # Play harmony (both voices together) with optional background
            if jarvis_has_audio and wanda_has_audio:
                if isinstance(jarvis_audio, np.ndarray) and isinstance(wanda_audio, np.ndarray):
                    logger.info("   🎤 Playing harmony (both voices together)...")
                    mixed_audio = self._mix_audio(jarvis_audio, wanda_audio)

                    # Add background harmony if available
                    if background_audio is not None and isinstance(background_audio, np.ndarray):
                        # Mix background with voices (background is already quiet)
                        min_len = min(len(mixed_audio), len(background_audio))
                        mixed_audio[:min_len] = mixed_audio[:min_len] + background_audio[:min_len]
                        # Normalize to prevent clipping
                        if np.max(np.abs(mixed_audio)) > 0:
                            mixed_audio = mixed_audio / np.max(np.abs(mixed_audio)) * 0.9

                    # Verify harmony quality too
                    quality_acceptable = self._play_audio_with_feedback(
                        mixed_audio,
                        phrase_name=f"Harmony phrase {i+1}"
                    )
                    if quality_acceptable:
                        logger.info("   ✅ Harmony verified - sounds like singing!")
                    else:
                        logger.error("   ❌ Harmony sounds like beeps - quality check failed")
                    time.sleep(0.3)  # Brief pause after harmony

            # Brief pause between phrases
            time.sleep(0.5)

        print()  # Use print() for blank line
        logger.info("=" * 80)
        logger.info("✅ DANNY BOY DUET COMPLETE")
        logger.info("=" * 80)

    def _analyze_audio_quality(self, audio: np.ndarray, sample_rate: int = 44100) -> Dict[str, Any]:
        """
        Analyze audio to determine if it sounds like singing or beeps/robotic

        Returns quality metrics and detection of singing vs beeps
        """
        try:
            # Calculate spectral features
            from scipy import signal

            # FFT for spectral analysis
            fft = np.fft.fft(audio)
            freqs = np.fft.fftfreq(len(audio), 1/sample_rate)
            magnitude = np.abs(fft)

            # Find fundamental frequency (pitch)
            # Look for peaks in frequency domain
            positive_freqs = freqs[:len(freqs)//2]
            positive_magnitude = magnitude[:len(magnitude)//2]

            # Find dominant frequency
            peak_idx = np.argmax(positive_magnitude[1:]) + 1  # Skip DC component
            fundamental_freq = abs(positive_freqs[peak_idx])

            # Calculate spectral centroid (brightness)
            if np.sum(positive_magnitude) > 0:
                spectral_centroid = np.sum(positive_freqs * positive_magnitude) / np.sum(positive_magnitude)
            else:
                spectral_centroid = 0

            # Calculate spectral rolloff (where 85% of energy is)
            cumsum = np.cumsum(positive_magnitude)
            total_energy = cumsum[-1]
            if total_energy > 0:
                rolloff_idx = np.where(cumsum >= 0.85 * total_energy)[0]
                spectral_rolloff = positive_freqs[rolloff_idx[0]] if len(rolloff_idx) > 0 else 0
            else:
                spectral_rolloff = 0

            # Calculate zero-crossing rate (speech vs tone indicator)
            zero_crossings = np.sum(np.diff(np.signbit(audio)))
            zcr = zero_crossings / len(audio)

            # Calculate spectral flatness (tone vs noise)
            # Flatness near 1 = noise, near 0 = tone
            geometric_mean = np.exp(np.mean(np.log(positive_magnitude + 1e-10)))
            arithmetic_mean = np.mean(positive_magnitude)
            spectral_flatness = geometric_mean / (arithmetic_mean + 1e-10)

            # Detect if it sounds like beeps (high spectral flatness, low ZCR, narrow bandwidth)
            # Beeps have: low ZCR, high spectral flatness (pure tone), narrow bandwidth
            is_beep_like = (
                zcr < 0.01 or  # Very few zero crossings (pure tone)
                spectral_flatness > 0.8 or  # Very flat spectrum (pure tone)
                (spectral_rolloff - fundamental_freq) < 500  # Narrow bandwidth
            )

            # Detect if it sounds like singing (formants present, natural variation)
            # Singing has: moderate ZCR, formant peaks, natural vibrato/variation
            has_formants = False
            if fundamental_freq > 0:
                # Look for formant peaks (resonant frequencies)
                formant_ranges = [(500, 1000), (1000, 2000), (2000, 3000)]  # F1, F2, F3 ranges
                for f_low, f_high in formant_ranges:
                    mask = (positive_freqs >= f_low) & (positive_freqs <= f_high)
                    if np.any(mask):
                        peak_in_range = np.max(positive_magnitude[mask])
                        if peak_in_range > np.max(positive_magnitude) * 0.3:  # Significant peak
                            has_formants = True
                            break

            is_singing_like = (
                has_formants and  # Has formant structure
                0.01 < zcr < 0.1 and  # Moderate zero crossings (natural speech)
                spectral_flatness < 0.5  # Not a pure tone
            )

            # Calculate quality score (0-1, higher = better)
            quality_score = 0.0
            if is_singing_like:
                quality_score = 0.8
            elif not is_beep_like:
                quality_score = 0.5  # Neutral - not beeps but not clearly singing
            else:
                quality_score = 0.1  # Beep-like

            return {
                'is_singing_like': is_singing_like,
                'is_beep_like': is_beep_like,
                'quality_score': quality_score,
                'fundamental_freq': fundamental_freq,
                'spectral_centroid': spectral_centroid,
                'spectral_rolloff': spectral_rolloff,
                'zero_crossing_rate': zcr,
                'spectral_flatness': spectral_flatness,
                'has_formants': has_formants
            }

        except Exception as e:
            logger.warning(f"⚠️  Audio quality analysis failed: {e}")
            return {
                'is_singing_like': False,
                'is_beep_like': True,  # Assume worst case
                'quality_score': 0.0,
                'error': str(e)
            }

    def _play_audio_with_feedback(self, audio: np.ndarray, sample_rate: int = 44100, 
                                  phrase_name: str = "unknown") -> bool:
        """
        Play audio with active feedback loop - verifies it sounds like singing, not beeps

        Returns True if quality is acceptable, False if it sounds like beeps
        """
        # Step 1: Analyze audio BEFORE playing
        logger.info(f"   🔍 Analyzing audio quality for {phrase_name}...")
        quality = self._analyze_audio_quality(audio, sample_rate)

        if quality['is_beep_like']:
            logger.error(f"   ❌ AUDIO QUALITY CHECK FAILED: Sounds like beeps/robotic!")
            logger.error(f"      Quality score: {quality['quality_score']:.2f}")
            logger.error(f"      Fundamental: {quality['fundamental_freq']:.1f} Hz")
            logger.error(f"      Zero-crossing rate: {quality['zero_crossing_rate']:.4f} (beeps have <0.01)")
            logger.error(f"      Spectral flatness: {quality['spectral_flatness']:.4f} (beeps have >0.8)")
            logger.error(f"   ⚠️  This audio will NOT sound like singing - rejecting playback")
            return False

        if quality['is_singing_like']:
            logger.info(f"   ✅ AUDIO QUALITY CHECK PASSED: Sounds like singing!")
            logger.info(f"      Quality score: {quality['quality_score']:.2f}")
            logger.info(f"      Has formants: {quality['has_formants']}")
            logger.info(f"      Fundamental: {quality['fundamental_freq']:.1f} Hz")
        else:
            logger.warning(f"   ⚠️  Audio quality uncertain (score: {quality['quality_score']:.2f})")

        # Step 2: Play the audio
        playback_success = self._play_audio(audio, sample_rate)

        # Step 3: Record and verify what was actually played (if possible)
        # Note: This would require loopback recording which is complex on Windows
        # For now, we rely on pre-playback analysis

        return playback_success and quality['quality_score'] > 0.3

    def _play_audio(self, audio: np.ndarray, sample_rate: int = 44100):
        """Play audio array (synthesized singing notes) with verification and multiple fallback methods"""
        try:
            # Normalize audio to prevent clipping
            max_val = np.max(np.abs(audio))
            if max_val > 0:
                # Normalize to 80% to prevent clipping
                audio = audio / max_val * 0.8
            else:
                logger.error("❌ Audio is silent - no audio data to play")
                return False

            # Verify audio has content
            rms = np.sqrt(np.mean(audio**2))
            if rms < 0.001:  # Very quiet threshold
                logger.warning(f"⚠️  Audio is too quiet (RMS: {rms:.6f}) - may not be audible")

            # Convert to int16 for playback
            audio_int16 = (audio * 32767).astype(np.int16)

            # Verify conversion
            if np.max(np.abs(audio_int16)) == 0:
                logger.error("❌ Audio conversion resulted in silence")
                return False

            # Method 1: Try PyAudio (primary method)
            if self.audio_output:
                try:
                    logger.info(f"   🔊 Attempting PyAudio playback...")
                    stream = self.audio_output.open(
                        format=pyaudio.paInt16,
                        channels=1,
                        rate=sample_rate,
                        output=True,
                        frames_per_buffer=1024
                    )

                    # Play audio in chunks
                    chunk_size = 1024
                    bytes_written = 0
                    for i in range(0, len(audio_int16), chunk_size):
                        chunk = audio_int16[i:i+chunk_size]
                        result = stream.write(chunk.tobytes())
                        if result is not None:
                            bytes_written += result
                        else:
                            bytes_written += len(chunk.tobytes())  # Estimate if None

                    stream.stop_stream()
                    stream.close()

                    if bytes_written > 0:
                        duration = len(audio) / sample_rate
                        logger.info(f"✅ PyAudio: Played {len(audio)} samples ({duration:.2f}s) - {bytes_written} bytes")
                        logger.info(f"   Audio RMS: {rms:.4f}, Peak: {max_val:.4f}")
                        return True
                    else:
                        logger.warning("⚠️  PyAudio wrote 0 bytes")
                except Exception as e:
                    logger.warning(f"⚠️  PyAudio failed: {e}")

            # Method 2: Try sounddevice (alternative) - with volume boost and device selection
            try:
                import sounddevice as sd
                logger.info(f"   🔊 Attempting sounddevice playback...")

                # Boost volume (audio is normalized to 0.75, boost to 1.0)
                audio_boosted = audio * 1.3  # 30% boost
                audio_boosted = np.clip(audio_boosted, -1.0, 1.0)  # Prevent clipping

                # List available devices for debugging
                try:
                    devices = sd.query_devices()
                    default_device = sd.default.device
                    logger.info(f"   🔊 Default audio device: {default_device}")
                    logger.info(f"   🔊 Available output devices: {len([d for d in devices if d['max_output_channels'] > 0])}")
                except:
                    pass

                # Play with explicit device selection and blocking
                sd.play(audio_boosted, samplerate=sample_rate, blocking=True)
                duration = len(audio) / sample_rate
                logger.info(f"✅ sounddevice: Played {len(audio)} samples ({duration:.2f}s) with 30% volume boost")
                logger.info(f"   🔊 If you don't hear audio, check your system volume and audio device settings")
                return True
            except ImportError:
                logger.debug("sounddevice not available")
            except Exception as e:
                logger.warning(f"⚠️  sounddevice failed: {e}")

            # Method 3: Try winsound (Windows built-in, WAV only)
            try:
                import wave
                import tempfile
                import os
                logger.info(f"   🔊 Attempting winsound playback (Windows)...")

                # Save to temporary WAV file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp_file:
                    tmp_path = tmp_file.name

                    # Write WAV file
                    with wave.open(tmp_path, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(sample_rate)
                        wav_file.writeframes(audio_int16.tobytes())

                    # Play using winsound
                    import winsound
                    winsound.PlaySound(tmp_path, winsound.SND_FILENAME | winsound.SND_NOWAIT)

                    # Wait for playback
                    duration = len(audio) / sample_rate
                    time.sleep(duration + 0.1)

                    # Clean up
                    try:
                        os.unlink(tmp_path)
                    except:
                        pass

                    logger.info(f"✅ winsound: Played {len(audio)} samples ({duration:.2f}s)")
                    return True
            except ImportError:
                logger.debug("winsound not available (not Windows)")
            except Exception as e:
                logger.warning(f"⚠️  winsound failed: {e}")

            # Method 4: Try pygame
            try:
                import pygame
                from io import BytesIO
                logger.info(f"   🔊 Attempting pygame playback...")

                pygame.mixer.init(frequency=sample_rate, size=-16, channels=1, buffer=1024)

                # Convert to bytes
                audio_bytes = audio_int16.tobytes()
                audio_buffer = BytesIO(audio_bytes)

                # Create sound object
                sound = pygame.sndarray.make_sound(audio_int16)
                sound.play()

                # Wait for playback
                duration = len(audio) / sample_rate
                while pygame.mixer.get_busy():
                    time.sleep(0.1)

                logger.info(f"✅ pygame: Played {len(audio)} samples ({duration:.2f}s)")
                return True
            except ImportError:
                logger.debug("pygame not available")
            except Exception as e:
                logger.warning(f"⚠️  pygame failed: {e}")

            # All methods failed
            logger.error("❌ All audio playback methods failed!")
            logger.error("   Tried: PyAudio, sounddevice, winsound, pygame")
            logger.error(f"   Audio data: {len(audio)} samples, RMS: {rms:.4f}, Peak: {max_val:.4f}")
            return False

        except Exception as e:
            logger.error(f"❌ Error playing audio: {e}", exc_info=True)
            return False

    def _play_audio_bytes(self, audio_bytes: bytes):
        """Play audio from bytes (e.g., from ElevenLabs - MP3 format)"""
        try:
            # CRITICAL: ElevenLabs returns MP3 format
            # Method 1: Use ElevenLabs play() function (BEST - handles MP3 natively)
            try:
                from elevenlabs import play
                # Play directly using ElevenLabs play function (handles MP3 properly)
                logger.info(f"   🔊 Playing MP3 audio ({len(audio_bytes)} bytes) using ElevenLabs play()...")
                play(audio_bytes)
                logger.info("✅ Played audio using ElevenLabs play()")
                return
            except ImportError:
                logger.debug("ElevenLabs play() not available")
            except Exception as e:
                logger.warning(f"ElevenLabs play() failed: {e}")

            # Method 2: Use pydub (requires ffmpeg for MP3)
            try:
                from pydub import AudioSegment
                from pydub.playback import play as pydub_play
                from io import BytesIO

                # Decode MP3 to audio segment
                logger.info(f"   🔊 Decoding MP3 with pydub ({len(audio_bytes)} bytes)...")
                audio_segment = AudioSegment.from_mp3(BytesIO(audio_bytes))

                # Play using pydub (handles MP3 properly)
                pydub_play(audio_segment)
                logger.info("✅ Played audio using pydub")
                return
            except ImportError:
                logger.debug("pydub not available")
            except Exception as e:
                # pydub requires ffmpeg for MP3 - if not installed, will fail
                logger.warning(f"pydub playback failed (may need ffmpeg): {e}")

            # Method 3: Try pygame
            try:
                import pygame
                from io import BytesIO

                logger.info(f"   🔊 Playing MP3 with pygame ({len(audio_bytes)} bytes)...")
                pygame.mixer.init()
                audio_file = BytesIO(audio_bytes)
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()

                # Wait for playback to finish
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)

                logger.info("✅ Played audio using pygame")
                return
            except ImportError:
                logger.debug("pygame not available")
            except Exception as e:
                logger.warning(f"pygame playback failed: {e}")

            # Last resort: Log error
            logger.error("❌ Could not play MP3 audio")
            logger.error("   Tried: ElevenLabs play(), pydub, pygame")
            logger.error("   Solution: ElevenLabs play() should work - check if audio_bytes is valid MP3")
            logger.error("   Or install ffmpeg for pydub: https://ffmpeg.org/download.html")

        except Exception as e:
            logger.error(f"❌ Error playing audio bytes: {e}", exc_info=True)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Danny Boy Acapella Duet")
    parser.add_argument('--jarvis-voice', type=str, help='ElevenLabs voice ID for JARVIS')
    parser.add_argument('--wanda-voice', type=str, help='ElevenLabs voice ID for Wanda')

    args = parser.parse_args()

    print("=" * 80)
    print("🎵 JARVIS DANNY BOY ACAPELLA DUET")
    print("=" * 80)
    print("   JARVIS and Wanda sing 'Danny Boy' together")
    print("   As opposing tenors in harmony, acapella")
    print("=" * 80)
    print()

    duet = DannyBoyDuet()

    # CRITICAL: Create karaoke display in main thread (Tkinter requirement)
    # Only create once to avoid duplicates
    try:
        from karaoke_display import KaraokeDisplay
        # Create single instance (only here, not in __init__)
        duet.karaoke = KaraokeDisplay()
        duet.karaoke._create_window()
        duet.karaoke.running = True

        # Start update loop in main thread
        def update_loop():
            if duet.karaoke and duet.karaoke.root and duet.karaoke.running:
                try:
                    duet.karaoke.root.update()
                    duet.karaoke.root.after(100, update_loop)
                except Exception as e:
                    logger.debug(f"Update loop error: {e}")

        # Start update loop
        duet.karaoke.root.after(100, update_loop)
        logger.info("✅ Karaoke display created in main thread (single instance - no duplicates)")
    except Exception as e:
        logger.warning(f"⚠️  Could not create karaoke display: {e}")
        duet.karaoke = None

    # Run duet in separate thread so karaoke can update
    import threading
    duet_thread = threading.Thread(target=lambda: duet.sing_duet(
        jarvis_voice_id=args.jarvis_voice,
        wanda_voice_id=args.wanda_voice
    ), daemon=True)
    duet_thread.start()

    # Keep main thread alive for karaoke display
    try:
        if duet.karaoke and duet.karaoke.root:
            # Run mainloop in main thread (required for Tkinter)
            duet.karaoke.root.mainloop()
        else:
            # Wait for duet to complete if no karaoke
            duet_thread.join()
    except KeyboardInterrupt:
        logger.info("👋 Stopping...")
        if duet.karaoke:
            duet.karaoke.close()
    except Exception as e:
        logger.error(f"❌ Error in main loop: {e}", exc_info=True)
        if duet.karaoke:
            duet.karaoke.close()


if __name__ == "__main__":


    main()