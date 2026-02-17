#!/usr/bin/env python3
"""
JARVIS TCSinger Full Integration

Complete end-to-end integration of TCSinger for AI singing synthesis.
This implements the full inference pipeline.

Tags: #SINGING #AI #TCSINGER #INTEGRATION #REQUIRED @JARVIS @LUMINA
"""

import sys
import os
import json
import numpy as np
import torch
from pathlib import Path
from typing import Optional, Dict, Any, List
import logging
import yaml

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

logger = get_logger("JARVISTCSingerFull")


class JARVISTCSingerFullIntegration:
    """
    Complete TCSinger integration for AI singing synthesis

    This implements the full inference pipeline from lyrics+melody to audio.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize full TCSinger integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = project_root
        self.tcsinger_path = project_root / "models" / "singing_synthesis" / "TCSinger"

        # Add TCSinger to path
        if str(self.tcsinger_path) not in sys.path:
            sys.path.insert(0, str(self.tcsinger_path))

        os.environ['PYTHONPATH'] = str(self.tcsinger_path)

        self.checkpoints_dir = self.tcsinger_path / "checkpoints"
        self.phone_set_path = self.tcsinger_path / "ZHEN_checkpoint_phone_set.json"

        # Reference audio for style transfer
        self.prompt_audio_path = self.project_root / "data" / "karaoke_matrix_analysis" / "audio_1.wav"
        if not self.prompt_audio_path.exists():
            self.prompt_audio_path = self.project_root / "data" / "karaoke_matrix_analysis" / "audio_2.wav"

        logger.info("=" * 80)
        logger.info("🎵 JARVIS TCSINGER FULL INTEGRATION")
        logger.info("=" * 80)

        # Check availability
        self.models_available = self._check_models()
        self.phone_set_available = self.phone_set_path.exists()
        self.prompt_audio_available = self.prompt_audio_path.exists()

        if self.models_available and self.phone_set_available and self.prompt_audio_available:
            logger.info("✅ All TCSinger components available")
            self._initialize_models()
        else:
            logger.warning("⚠️  TCSinger not fully available:")
            if not self.models_available:
                logger.warning("   - Model checkpoints missing")
            if not self.phone_set_available:
                logger.warning("   - phone_set.json missing")
            if not self.prompt_audio_available:
                logger.warning("   - Prompt audio missing")

    def _check_models(self) -> bool:
        try:
            """Check if all required model checkpoints exist"""
            # Check for actual model files, not just directories
            required_files = {
                "TCSinger": "TCSinger/model_ckpt_steps_200000.ckpt",
                "SAD": "SAD/model_ckpt_steps_80000.ckpt",
                "SDLM": "SDLM/model_ckpt_steps_120000.ckpt",
                "hifigan": "hifigan/model_ckpt_steps_1000000.ckpt"
            }

            all_exist = True
            for name, file_path in required_files.items():
                full_path = self.checkpoints_dir / file_path
                if not full_path.exists():
                    logger.debug(f"Missing: {name} - {file_path}")
                    all_exist = False

            return all_exist

        except Exception as e:
            self.logger.error(f"Error in _check_models: {e}", exc_info=True)
            raise
    def _initialize_models(self):
        """Initialize TCSinger models (lazy loading)"""
        self.style_transfer = None
        self.ph_encoder = None
        logger.info("   Models will be loaded on first use")

    def sing(
        self,
        lyrics: str,
        melody: List[str],
        duration: float,
        voice_style: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Generate singing audio using TCSinger

        Args:
            lyrics: Song lyrics
            melody: List of musical notes
            duration: Total duration
            voice_style: Voice style (tenor, tenor2, etc.)

        Returns:
            Audio bytes (WAV format) or None if failed
        """
        if not (self.models_available and self.phone_set_available and self.prompt_audio_available):
            logger.error("❌ TCSinger not fully available")
            return None

        try:
            # Convert lyrics to phonemes
            phonemes = self._lyrics_to_phonemes(lyrics)
            if not phonemes:
                logger.error("❌ Failed to convert lyrics to phonemes")
                return None

            # Convert melody to TCSinger format
            notes_midi, note_durs, note_types = self._melody_to_tcsinger(melody, duration, len(phonemes))

            # Prepare input for StyleTransfer
            inp = self._prepare_tcsinger_input(phonemes, notes_midi, note_durs, note_types)

            # Run inference
            audio = self._run_tcsinger_inference(inp)

            if audio is not None:
                # Convert to bytes
                import soundfile as sf
                from io import BytesIO
                buffer = BytesIO()
                sf.write(buffer, audio, 48000, format='WAV')
                return buffer.getvalue()

            return None

        except Exception as e:
            logger.error(f"❌ TCSinger singing failed: {e}", exc_info=True)
            return None

    def _lyrics_to_phonemes(self, lyrics: str) -> List[str]:
        """Convert lyrics to phonemes using TCSinger text processor"""
        try:
            from data_gen.tts.txt_processors.en import TxtProcessor
            txt_processor = TxtProcessor()
            txt_struct, txt = txt_processor.process(lyrics, {})
            # Extract phonemes: [[word, [phonemes]], ...]
            phonemes = []
            for word, ph_list in txt_struct:
                phonemes.extend(ph_list)
            return phonemes
        except Exception as e:
            logger.error(f"❌ Phoneme conversion failed: {e}")
            return []

    def _melody_to_tcsinger(
        self,
        melody: List[str],
        duration: float,
        num_phonemes: int
    ) -> tuple:
        """Convert melody to TCSinger format (MIDI notes, durations, types)"""
        # Convert notes to MIDI
        notes_midi = [self._note_to_midi(note) for note in melody]

        # Calculate note durations (in frames, 256 hop size)
        samples_per_note = int(48000 * duration / len(melody)) if melody else int(48000 * duration)
        frames_per_note = samples_per_note // 256

        note_durs = [frames_per_note] * len(notes_midi)
        note_types = [2] * len(notes_midi)  # 2 = lyric (singing)

        # Match to phoneme count
        while len(notes_midi) < num_phonemes:
            notes_midi.append(notes_midi[-1] if notes_midi else 60)
            note_durs.append(frames_per_note)
            note_types.append(2)

        notes_midi = notes_midi[:num_phonemes]
        note_durs = note_durs[:num_phonemes]
        note_types = note_types[:num_phonemes]

        return notes_midi, note_durs, note_types

    def _note_to_midi(self, note: str) -> int:
        """Convert note name to MIDI number"""
        import re
        note_map = {
            'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3,
            'E': 4, 'F': 5, 'F#': 6, 'Gb': 6, 'G': 7, 'G#': 8,
            'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11
        }
        match = re.match(r'([A-G][#b]?)(\d+)', note)
        if match:
            note_name, octave = match.groups()
            base_note = note_map.get(note_name, 0)
            return base_note + (int(octave) + 1) * 12
        return 60  # Default to C4

    def _prepare_tcsinger_input(
        self,
        phonemes: List[str],
        notes_midi: List[int],
        note_durs: List[float],
        note_types: List[int]
    ) -> Dict[str, Any]:
        """Prepare input dictionary for TCSinger StyleTransfer"""
        # Use first 5 phonemes as prompt, rest as generation
        prompt_len = min(5, len(phonemes))

        inp = {
            'text_in': phonemes[:prompt_len],
            'note_in': notes_midi[:prompt_len],
            'note_dur_in': note_durs[:prompt_len],
            'note_type_in': note_types[:prompt_len],
            'text_gen': phonemes,
            'note_gen': notes_midi,
            'note_dur_gen': note_durs,
            'note_type_gen': note_types,
            'ref_audio': str(self.prompt_audio_path),
            'ph_durs': [0.1] * prompt_len  # Estimated durations
        }

        return inp

    def _run_tcsinger_inference(self, inp: Dict[str, Any]) -> Optional[np.ndarray]:
        """Run TCSinger StyleTransfer inference"""
        try:
            from inference.style_transfer import StyleTransfer
            from utils.commons.hparams import set_hparams, hparams as hp
            import tempfile
            import shutil
            import yaml

            logger.info("   🎵 Running TCSinger inference...")

            # Create temporary config directory structure
            temp_data_dir = self.tcsinger_path / "temp_data"
            temp_data_dir.mkdir(exist_ok=True)
            temp_binary_dir = temp_data_dir / "binary"
            temp_binary_dir.mkdir(exist_ok=True)
            temp_processed_dir = temp_data_dir / "processed"
            temp_processed_dir.mkdir(exist_ok=True)

            # Copy phone_set.json to temp location (required by BaseTTSInfer.__init__)
            # BaseTTSInfer.__init__ calls: build_token_encoder(os.path.join(hparams["processed_data_dir"], "phone_set.json"))
            temp_phone_set = temp_processed_dir / "phone_set.json"
            if self.phone_set_path.exists():
                shutil.copy(self.phone_set_path, temp_phone_set)
                logger.debug(f"   Copied phone_set.json to {temp_phone_set}")
            else:
                logger.error("❌ phone_set.json not found")
                return None

            # Use sdlm.yaml as base (StyleTransfer uses SDLM config)
            # Create temporary config file that extends sdlm.yaml
            temp_config = temp_data_dir / "config.yaml"
            config_content = f"""
base_config:
- {self.tcsinger_path}/egs/tcsinger.yaml
- {self.tcsinger_path}/egs/sad.yaml
task_cls: tasks.TCSinger.sdlm.SDLMTask
fs2_ckpt_dir: {self.checkpoints_dir}/TCSinger
decoder_ckpt_dir: {self.checkpoints_dir}/SAD
exp_name: {self.checkpoints_dir}/SDLM
binary_data_dir: {temp_binary_dir}
processed_data_dir: {temp_processed_dir}
vocoder_ckpt: {self.checkpoints_dir}/hifigan
max_input_tokens: 1500
max_ph: 1500
"""

            with open(temp_config, 'w') as f:
                f.write(config_content)

            # Set hparams from config (loads base configs and merges)
            logger.info("   🔧 Loading TCSinger configuration...")
            set_hparams(str(temp_config))

            # Verify hparams are set correctly
            if hp.get('exp_name') and hp.get('decoder_ckpt_dir'):
                logger.info(f"   ✅ Config loaded: exp_name={hp.get('exp_name')}")
            else:
                logger.warning("⚠️  Config may not be fully loaded")

            # Initialize StyleTransfer (this loads models in __init__)
            # StyleTransfer.__init__ calls BaseTTSInfer.__init__ which:
            # - Builds ph_encoder from phone_set.json (in processed_data_dir)
            # - Calls build_model() -> loads SDLM from exp_name
            # - Calls build_vocoder() -> loads HIFI-GAN from vocoder_ckpt
            # StyleTransfer.build_model() also loads SAD decoder from decoder_ckpt_dir
            logger.info("   🔧 Loading TCSinger models (this may take a moment)...")
            logger.info("   ⏳ Loading SDLM, SAD decoder, and HIFI-GAN vocoder...")
            try:
                infer_ins = StyleTransfer(hp)
                logger.info("   ✅ TCSinger models loaded successfully")
            except FileNotFoundError as e:
                logger.error(f"❌ Model checkpoint file not found: {e}")
                logger.info("   Download models: huggingface-cli download AaronZ345/TCSinger --local-dir checkpoints/")
                return None
            except Exception as e:
                logger.error(f"❌ Model loading failed: {e}")
                logger.debug("   This is expected if models aren't downloaded yet")
                return None

            # Run inference
            logger.info("   🎤 Generating singing audio...")
            wav_out, mel_out = infer_ins.infer_once(inp)

            # Convert to numpy array
            if isinstance(wav_out, torch.Tensor):
                audio = wav_out.cpu().numpy()
            elif isinstance(wav_out, np.ndarray):
                audio = wav_out
            else:
                audio = np.array(wav_out)

            # Ensure 1D array
            if len(audio.shape) > 1:
                audio = audio.flatten()

            logger.info(f"   ✅ Generated audio: {len(audio)} samples, {len(audio)/48000:.2f}s")

            # Cleanup temp directory
            try:
                shutil.rmtree(temp_data_dir)
            except:
                pass

            return audio

        except FileNotFoundError as e:
            logger.warning(f"⚠️  TCSinger checkpoint files not found: {e}")
            logger.info("   Download models: huggingface-cli download AaronZ345/TCSinger --local-dir checkpoints/")
            return None
        except Exception as e:
            logger.error(f"❌ TCSinger inference failed: {e}", exc_info=True)
            logger.debug("   This is expected if models aren't downloaded yet")
            return None


def main():
    """Test TCSinger full integration"""
    integration = JARVISTCSingerFullIntegration()

    audio = integration.sing(
        lyrics="Oh Danny boy, the pipes are calling",
        melody=['C4', 'E4', 'G4', 'C5'],
        duration=4.0
    )

    if audio:
        logger.info("✅ Singing generated successfully")
    else:
        logger.info("⚠️  Using fallback synthesis")


if __name__ == "__main__":


    main()