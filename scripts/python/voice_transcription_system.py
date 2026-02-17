#!/usr/bin/env python3
"""
Voice Transcription System for JARVIS - Live Conversational Coding
Enables verbal coding and minimal physical interaction for chronic pain management

@V3_WORKFLOWED: True
@RULE_COMPLIANT: True
@TEST_FIRST: True
@RR_METHODOLOGY: Rest, Roast, Repair
@ACCESSIBILITY_FIRST: Voice-enabled collaboration for reduced physical effort
"""

import os
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
import speech_recognition as sr
import pyttsx3
import sqlite3

class VoiceTranscriptionSystem:
    """
    Voice-enabled conversational coding system for minimal physical interaction.
    Enables 'Vibe Coding Advanced' through voice commands and natural language.
    """

    def __init__(self, db_path: str = './data/voice_sessions.db', wake_word: str = 'jarvis'):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Voice recognition components
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.audio_engine = pyttsx3.init()

        # Voice settings
        self.wake_word = wake_word.lower()
        self.is_listening = False
        self.is_awake = False
        self.conversation_active = False

        # Conversation state
        self.conversation_history = []
        self.current_session = None
        self.voice_commands = self._load_voice_commands()

        # Callbacks for integration
        self.on_transcription_callback = None
        self.on_command_callback = None
        self.on_error_callback = None

        # Initialize systems
        self._init_audio_system()
        self._init_database()

        print("🎙️ Voice Transcription System initialized")
        print(f"   Wake word: '{self.wake_word}'")
        print("   Ready for verbal coding collaboration")

    def _init_audio_system(self):
        """Initialize audio input/output systems"""
        try:
            # Adjust microphone for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("   Audio calibration complete")
        except Exception as e:
            print(f"   Audio initialization warning: {e}")

        # Configure text-to-speech
        voices = self.audio_engine.getProperty('voices')
        if voices:
            # Prefer female voice for conversational feel
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.audio_engine.setProperty('voice', voice.id)
                    break

        self.audio_engine.setProperty('rate', 180)  # Slightly slower for clarity
        self.audio_engine.setProperty('volume', 0.8)

    def _init_database(self):
        try:
            """Initialize voice session database"""
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS voice_sessions (
                        session_id TEXT PRIMARY KEY,
                        start_time TEXT,
                        end_time TEXT,
                        duration_seconds REAL,
                        transcript_count INTEGER,
                        command_count INTEGER,
                        wake_word_activations INTEGER
                    )
                ''')

                conn.execute('''
                    CREATE TABLE IF NOT EXISTS voice_transcripts (
                        transcript_id TEXT PRIMARY KEY,
                        session_id TEXT,
                        timestamp TEXT,
                        transcription_text TEXT,
                        is_command BOOLEAN,
                        command_type TEXT,
                        FOREIGN KEY (session_id) REFERENCES voice_sessions (session_id)
                    )
                ''')

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def _load_voice_commands(self) -> Dict[str, Any]:
        """Load voice command patterns and actions"""
        return {
            'help': {
                'type': 'system',
                'action': 'show_help',
                'description': 'Show available voice commands'
            },
            'status': {
                'type': 'system',
                'action': 'show_status',
                'description': 'Show current system status'
            },
            'stop': {
                'type': 'control',
                'action': 'stop_listening',
                'description': 'Stop voice recognition'
            },
            'sleep': {
                'type': 'control',
                'action': 'go_to_sleep',
                'description': 'Put JARVIS to sleep'
            },
            'create file': {
                'type': 'development',
                'action': 'create_file',
                'description': 'Create a new file'
            },
            'open file': {
                'type': 'development',
                'action': 'open_file',
                'description': 'Open an existing file'
            },
            'run code': {
                'type': 'development',
                'action': 'run_code',
                'description': 'Execute code or commands'
            },
            'run command': {
                'type': 'system',
                'action': 'execute_command',
                'description': 'Execute terminal command'
            }
        }

    def start_voice_session(self) -> str:
        try:
            """Start a new voice interaction session"""
            session_id = f"voice_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

            self.current_session = {
                'session_id': session_id,
                'start_time': datetime.now(),
                'transcript_count': 0,
                'command_count': 0,
                'wake_word_activations': 0
            }

            # Save session to database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO voice_sessions (session_id, start_time)
                    VALUES (?, ?)
                ''', (session_id, self.current_session['start_time'].isoformat()))
                conn.commit()

            self.conversation_active = True
            self.speak(f"Voice session started. I'm listening for '{self.wake_word}' to begin our conversation.")

            return session_id

        except Exception as e:
            self.logger.error(f"Error in start_voice_session: {e}", exc_info=True)
            raise
    def speak(self, text: str, interrupt: bool = False):
        """Convert text to speech"""
        if interrupt:
            self.audio_engine.stop()

        print(f"🗣️ JARVIS: {text}")
        self.audio_engine.say(text)
        self.audio_engine.runAndWait()

    def listen_for_wake_word(self):
        """Continuously listen for wake word"""
        print("👂 Listening for wake word...")
        self.is_listening = True

        while self.is_listening:
            try:
                with self.microphone as source:
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)

                try:
                    text = self.recognizer.recognize_google(audio).lower()

                    if self.wake_word in text:
                        self.is_awake = True
                        self.current_session['wake_word_activations'] += 1
                        self.speak("I'm awake and ready to help with verbal coding. What would you like to work on?")
                        self.start_conversation()
                        break

                except sr.UnknownValueError:
                    continue
                except sr.RequestError as e:
                    print(f"Speech recognition error: {e}")
                    time.sleep(1)

            except sr.WaitTimeoutError:
                continue

    def start_conversation(self):
        try:
            """Start interactive conversation mode"""
            self.speak("We're now in conversation mode. Speak naturally, and I'll understand your requests.")

            conversation_thread = threading.Thread(target=self._conversation_loop)
            conversation_thread.daemon = True
            conversation_thread.start()

        except Exception as e:
            self.logger.error(f"Error in start_conversation: {e}", exc_info=True)
            raise
    def _conversation_loop(self):
        """Main conversation processing loop"""
        while self.is_awake and self.conversation_active:
            try:
                with self.microphone as source:
                    print("🎙️ Listening...")
                    audio = self.recognizer.listen(source, timeout=10, phrase_time_limit=10)

                try:
                    text = self.recognizer.recognize_google(audio)
                    print(f"🎤 You said: {text}")

                    self._save_transcript(text, False)
                    self._process_transcription(text)

                except sr.UnknownValueError:
                    print("Didn't catch that, please try again.")
                except sr.RequestError as e:
                    self.speak(f"Sorry, speech recognition service error: {e}")

            except sr.WaitTimeoutError:
                if self.is_awake:
                    print("Timeout - still listening...")

            except KeyboardInterrupt:
                self.stop_session()
                break

    def _process_transcription(self, text: str):
        """Process transcribed speech for commands and conversation"""
        text_lower = text.lower()

        # Check for voice commands
        command_executed = False
        for command_phrase, command_info in self.voice_commands.items():
            if command_phrase in text_lower:
                self._execute_voice_command(command_phrase, command_info, text)
                command_executed = True
                break

        if not command_executed:
            self._handle_conversation(text)

    def _execute_voice_command(self, command_phrase: str, command_info: Dict[str, Any], full_text: str):
        """Execute a recognized voice command"""
        self.current_session['command_count'] += 1
        self._save_transcript(full_text, True, command_info['action'])

        action = command_info['action']

        if action == 'show_help':
            self._show_voice_help()
        elif action == 'show_status':
            self._show_system_status()
        elif action == 'stop_listening':
            self.stop_session()
        elif action == 'go_to_sleep':
            self.sleep_mode()
        elif action == 'create_file':
            self._handle_create_file(full_text)
        elif action == 'open_file':
            self._handle_open_file(full_text)
        elif action == 'run_code':
            self._handle_run_code(full_text)
        elif action == 'execute_command':
            self._handle_execute_command(full_text)
        else:
            self.speak(f"I understand you want to {action}, but that feature is still being implemented.")

    def _handle_conversation(self, text: str):
        """Handle natural language conversation"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['hello', 'hi', 'hey']):
            self.speak("Hello! Ready to collaborate on some verbal coding?")
        elif any(word in text_lower for word in ['thank', 'thanks']):
            self.speak("You're welcome! Glad I could help with the coding.")
        elif any(word in text_lower for word in ['how are you']):
            self.speak("I'm functioning optimally and ready to assist with verbal coding. How can I help you today?")
        elif any(word in text_lower for word in ['pain', 'hurt', 'tired']):
            self.speak("I understand you're managing chronic pain. I'm here to make coding as effortless as possible through voice interaction. Take it easy and let me handle the technical work.")
        elif 'code' in text_lower or 'program' in text_lower:
            self.speak("I'd be happy to help with coding. What would you like to create or modify?")
        else:
            self.speak("I heard your message. For complex requests, please use specific voice commands or continue developing our conversation capabilities.")

    def _show_voice_help(self):
        """Show available voice commands"""
        help_text = """Available voice commands:
        • 'Help' - Show this help
        • 'Status' - Show system status
        • 'Stop' - Stop listening
        • 'Sleep' - Put me to sleep
        • 'Create file [name]' - Create new file
        • 'Open file [name]' - Open existing file
        • 'Run code' - Execute code
        • 'Run command [cmd]' - Execute terminal command"""
        self.speak("Here's what I can do with voice commands:")
        print(help_text)

    def _show_system_status(self):
        """Show current system status"""
        if self.current_session:
            session_duration = datetime.now() - self.current_session['start_time']
            duration_minutes = session_duration.total_seconds() / 60
            status = f"Voice session active for {duration_minutes:.1f} minutes. Transcripts: {self.current_session['transcript_count']}, Commands: {self.current_session['command_count']}"
            self.speak(status)

    def _handle_create_file(self, text: str):
        """Handle file creation request"""
        words = text.split()
        filename = words[-1] if words else 'new_file.txt'
        self.speak(f"Creating file: {filename}")
        if self.on_command_callback:
            self.on_command_callback('create_file', {'filename': filename})

    def _handle_open_file(self, text: str):
        """Handle file opening request"""
        words = text.split()
        filename = words[-1] if words else None
        if filename:
            self.speak(f"Opening file: {filename}")
            if self.on_command_callback:
                self.on_command_callback('open_file', {'filename': filename})
        else:
            self.speak("Please specify which file you'd like to open.")

    def _handle_run_code(self, text: str):
        """Handle code execution request"""
        self.speak("Running code. Please specify what code you'd like to execute.")

    def _handle_execute_command(self, text: str):
        """Handle terminal command execution"""
        command = text.lower().replace('run command', '').strip()
        if command:
            self.speak(f"Executing: {command}")
            if self.on_command_callback:
                self.on_command_callback('execute_command', {'command': command})
        else:
            self.speak("Please specify which command you'd like to run.")

    def _save_transcript(self, text: str, is_command: bool = False, command_type: str = None):
        try:
            """Save voice transcript to database"""
            if not self.current_session:
                return

            self.current_session['transcript_count'] += 1
            transcript_id = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S%f')}"

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO voice_transcripts
                    (transcript_id, session_id, timestamp, transcription_text, is_command, command_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    transcript_id,
                    self.current_session['session_id'],
                    datetime.now().isoformat(),
                    text,
                    is_command,
                    command_type
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _save_transcript: {e}", exc_info=True)
            raise
    def stop_session(self):
        """Stop current voice session"""
        if self.current_session:
            end_time = datetime.now()
            duration = end_time - self.current_session['start_time']

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE voice_sessions
                    SET end_time = ?, duration_seconds = ?
                    WHERE session_id = ?
                ''', (
                    end_time.isoformat(),
                    duration.total_seconds(),
                    self.current_session['session_id']
                ))
                conn.commit()

            self.speak(f"Session ended. Duration: {duration.total_seconds() / 60:.1f} minutes. Thank you for the verbal coding collaboration.")

        self.is_listening = False
        self.is_awake = False
        self.conversation_active = False
        self.current_session = None

    def sleep_mode(self):
        """Put system into sleep mode"""
        self.is_awake = False
        self.speak("Going to sleep. Say my wake word to continue our conversation.")

    def set_transcription_callback(self, callback: Callable):
        """Set callback for transcription processing"""
        self.on_transcription_callback = callback

    def set_command_callback(self, callback: Callable):
        """Set callback for command execution"""
        self.on_command_callback = callback

    def set_error_callback(self, callback: Callable):
        """Set callback for error handling"""
        self.on_error_callback = callback

def start_voice_session(wake_word: str = 'jarvis') -> VoiceTranscriptionSystem:
    """Start a voice transcription session"""
    system = VoiceTranscriptionSystem(wake_word=wake_word)
    session_id = system.start_voice_session()
    return system

def voice_command(text: str) -> str:
    """Process a voice command (for testing)"""
    return f"Processed voice command: {text}"

if __name__ == '__main__':
    print("🎙️ JARVIS Voice Transcription System")
    print("Starting voice session...")

    system = start_voice_session()

    try:
        system.listen_for_wake_word()
    except KeyboardInterrupt:
        system.stop_session()
        print("Voice session terminated by user.")
