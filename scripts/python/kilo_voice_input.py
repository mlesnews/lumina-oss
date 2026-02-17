#!/usr/bin/env python3
"""
Kilo Code Voice Input Bridge

Provides voice input for Kilo Code until native support is added.

Workflow:
1. Press and hold Ctrl+Shift+K (or configured hotkey)
2. Speak your request
3. Release to transcribe and send to Kilo Code

Requirements:
    pip install sounddevice numpy keyboard pyperclip faster-whisper

Usage:
    python kilo_voice_input.py              # Start voice bridge
    python kilo_voice_input.py --test       # Test microphone
    python kilo_voice_input.py --install    # Install dependencies

Tags: @PEAK @KILO_CODE @VOICE #automation
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path
from typing import Optional

# Check dependencies
def check_dependencies():
    """Check and report missing dependencies"""
    missing = []
    
    try:
        import sounddevice
    except ImportError:
        missing.append("sounddevice")
    
    try:
        import numpy
    except ImportError:
        missing.append("numpy")
    
    try:
        import keyboard
    except ImportError:
        missing.append("keyboard")
    
    try:
        import pyperclip
    except ImportError:
        missing.append("pyperclip")
    
    return missing


def install_dependencies():
    """Install required dependencies"""
    print("Installing dependencies...")
    deps = ["sounddevice", "numpy", "keyboard", "pyperclip", "faster-whisper"]
    subprocess.run([sys.executable, "-m", "pip", "install"] + deps, check=True)
    print("Dependencies installed!")


# Configuration
CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "kilo_voice_config.json"
DEFAULT_CONFIG = {
    "hotkey": "ctrl+shift+k",
    "sample_rate": 16000,
    "whisper_model": "base.en",  # tiny.en, base.en, small.en, medium.en
    "device": "cuda",  # cuda, cpu
    "language": "en",
    "push_to_talk": True,
    "auto_send": True,
    "sound_feedback": True,
    "transcription_prefix": "",
    "transcription_suffix": "",
}


class KiloVoiceBridge:
    """Voice input bridge for Kilo Code"""
    
    def __init__(self, config: dict):
        self.config = config
        self.is_recording = False
        self.audio_data = []
        self.whisper_model = None
        self.stream = None
        
        # Import dependencies
        import sounddevice as sd
        import numpy as np
        self.sd = sd
        self.np = np
        
    def load_whisper(self):
        """Load Whisper model for transcription"""
        if self.whisper_model is None:
            print(f"Loading Whisper model: {self.config['whisper_model']}...")
            try:
                from faster_whisper import WhisperModel
                self.whisper_model = WhisperModel(
                    self.config["whisper_model"],
                    device=self.config["device"],
                    compute_type="float16" if self.config["device"] == "cuda" else "int8"
                )
                print("Whisper model loaded!")
            except Exception as e:
                print(f"Error loading faster-whisper: {e}")
                print("Falling back to OpenAI Whisper...")
                import whisper
                self.whisper_model = whisper.load_model(self.config["whisper_model"])
        
    def start_recording(self):
        """Start recording audio"""
        if self.is_recording:
            return
            
        self.is_recording = True
        self.audio_data = []
        
        def callback(indata, frames, time_info, status):
            if self.is_recording:
                self.audio_data.append(indata.copy())
        
        self.stream = self.sd.InputStream(
            samplerate=self.config["sample_rate"],
            channels=1,
            callback=callback,
            dtype=self.np.float32
        )
        self.stream.start()
        
        if self.config["sound_feedback"]:
            print("🎤 Recording...")
    
    def stop_recording(self) -> Optional[str]:
        """Stop recording and transcribe"""
        if not self.is_recording:
            return None
            
        self.is_recording = False
        
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
        
        if not self.audio_data:
            print("No audio recorded")
            return None
        
        # Combine audio chunks
        audio = self.np.concatenate(self.audio_data, axis=0)
        
        if self.config["sound_feedback"]:
            print("🔄 Transcribing...")
        
        # Transcribe
        text = self.transcribe(audio)
        
        if text:
            if self.config["sound_feedback"]:
                print(f"📝 Transcribed: {text}")
        
        return text
    
    def transcribe(self, audio: 'np.ndarray') -> Optional[str]:
        """Transcribe audio to text"""
        self.load_whisper()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        
        try:
            import scipy.io.wavfile as wav
            wav.write(temp_path, self.config["sample_rate"], audio)
            
            # Transcribe based on model type
            if hasattr(self.whisper_model, 'transcribe'):
                # faster-whisper
                segments, _ = self.whisper_model.transcribe(
                    temp_path,
                    language=self.config["language"]
                )
                text = " ".join([s.text for s in segments]).strip()
            else:
                # OpenAI whisper
                result = self.whisper_model.transcribe(
                    temp_path,
                    language=self.config["language"]
                )
                text = result["text"].strip()
            
            return text
            
        except Exception as e:
            print(f"Transcription error: {e}")
            return None
        finally:
            os.unlink(temp_path)
    
    def send_to_kilo(self, text: str):
        """Send text to Kilo Code via clipboard"""
        import pyperclip
        import keyboard
        
        # Add prefix/suffix if configured
        full_text = f"{self.config['transcription_prefix']}{text}{self.config['transcription_suffix']}"
        
        # Copy to clipboard
        pyperclip.copy(full_text)
        
        if self.config["auto_send"]:
            # Simulate Ctrl+V to paste
            time.sleep(0.1)
            keyboard.send("ctrl+v")
            
            if self.config["sound_feedback"]:
                print("✅ Sent to Kilo Code!")
        else:
            print(f"📋 Copied to clipboard: {full_text}")
    
    def run(self):
        """Main loop - listen for hotkey"""
        import keyboard
        
        print(f"""
╔══════════════════════════════════════════════════════════════╗
║             KILO CODE VOICE INPUT BRIDGE                     ║
╠══════════════════════════════════════════════════════════════╣
║                                                              ║
║  Hotkey: {self.config['hotkey']:<20}                         ║
║  Model:  {self.config['whisper_model']:<20}                  ║
║  Device: {self.config['device']:<20}                         ║
║                                                              ║
║  Press and HOLD {self.config['hotkey']} to speak             ║
║  Release to transcribe and send to Kilo Code                 ║
║                                                              ║
║  Press Ctrl+C to exit                                        ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
""")
        
        # Pre-load whisper model
        self.load_whisper()
        
        # Set up hotkey handlers
        keyboard.on_press_key(
            self.config["hotkey"].split("+")[-1],
            lambda e: self._on_hotkey_press(e),
            suppress=False
        )
        
        keyboard.on_release_key(
            self.config["hotkey"].split("+")[-1],
            lambda e: self._on_hotkey_release(e),
            suppress=False
        )
        
        # Keep running
        try:
            keyboard.wait()
        except KeyboardInterrupt:
            print("\nExiting...")
    
    def _check_modifiers(self) -> bool:
        """Check if required modifier keys are pressed"""
        import keyboard
        
        hotkey_parts = self.config["hotkey"].lower().split("+")
        
        if "ctrl" in hotkey_parts and not keyboard.is_pressed("ctrl"):
            return False
        if "shift" in hotkey_parts and not keyboard.is_pressed("shift"):
            return False
        if "alt" in hotkey_parts and not keyboard.is_pressed("alt"):
            return False
        
        return True
    
    def _on_hotkey_press(self, event):
        """Handle hotkey press"""
        if self._check_modifiers() and not self.is_recording:
            self.start_recording()
    
    def _on_hotkey_release(self, event):
        """Handle hotkey release"""
        if self.is_recording:
            text = self.stop_recording()
            if text:
                self.send_to_kilo(text)


def test_microphone():
    """Test microphone input"""
    print("Testing microphone...")
    
    import sounddevice as sd
    import numpy as np
    
    print("\nAvailable devices:")
    print(sd.query_devices())
    
    print("\nRecording 3 seconds of audio...")
    duration = 3
    sample_rate = 16000
    
    audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype=np.float32)
    sd.wait()
    
    # Check audio level
    level = np.abs(audio).mean()
    print(f"\nAudio level: {level:.6f}")
    
    if level < 0.001:
        print("⚠️  Audio level is very low. Check your microphone.")
    elif level > 0.5:
        print("⚠️  Audio level is very high. Check for clipping.")
    else:
        print("✅ Microphone working!")
    
    return level > 0.001


def load_config() -> dict:
    """Load configuration"""
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH) as f:
            config = json.load(f)
        # Merge with defaults
        return {**DEFAULT_CONFIG, **config}
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    """Save configuration"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="Kilo Code Voice Input Bridge")
    parser.add_argument("--test", action="store_true", help="Test microphone")
    parser.add_argument("--install", action="store_true", help="Install dependencies")
    parser.add_argument("--hotkey", default=None, help="Override hotkey")
    parser.add_argument("--model", default=None, help="Whisper model size")
    parser.add_argument("--cpu", action="store_true", help="Force CPU mode")
    
    args = parser.parse_args()
    
    if args.install:
        install_dependencies()
        return
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Run: python kilo_voice_input.py --install")
        return 1
    
    if args.test:
        test_microphone()
        return
    
    # Load config
    config = load_config()
    
    # Override from args
    if args.hotkey:
        config["hotkey"] = args.hotkey
    if args.model:
        config["whisper_model"] = args.model
    if args.cpu:
        config["device"] = "cpu"
    
    # Save updated config
    save_config(config)
    
    # Run bridge
    bridge = KiloVoiceBridge(config)
    bridge.run()


if __name__ == "__main__":
    main()
