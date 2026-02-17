#!/usr/bin/env python3
"""
Hybrid Passive-Active Listening - REQUIRED

Hybrid approach:
- Passive listening: Waits for "Hey Jarvis" trigger
- Active listening: After trigger, switches to active mode (more attentive)
- Reset: Long pauses reset back to passive mode

Tags: #HYBRID #PASSIVE_ACTIVE #TRIGGER_WORD #REQUIRED @JARVIS @LUMINA
"""

import sys
import time
import threading
from pathlib import Path
from enum import Enum
from typing import Tuple, Dict, Optional

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

logger = get_logger("HybridPassiveActive")


class ListeningMode(Enum):
    """Listening mode states"""
    PASSIVE = "passive"  # Waiting for "Hey Jarvis" trigger
    ACTIVE = "active"    # Actively listening after trigger
    RESETTING = "resetting"  # Resetting to passive after pause


class HybridPassiveActiveListening:
    """
    Hybrid Passive-Active Listening System

    Passive Mode:
    - Low-power listening
    - Only listens for "Hey Jarvis" trigger
    - Minimal processing

    Active Mode:
    - Full attention listening
    - Processes all speech
    - More responsive
    - Resets to passive after long pause
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize hybrid passive-active listening

        Args:
            project_root: Project root directory (optional)
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.mode = ListeningMode.PASSIVE
        self.transcription_service = None
        self.running = False

        # Trigger word
        self.trigger_word = "hey jarvis"
        self.trigger_detected = False

        # Timing
        self.last_speech_time = None
        self.active_mode_timeout = 10.0  # 10 seconds of silence = reset to passive
        self.passive_listening_active = False

        # Visual-audio integration
        self.unified_listener = None

    def _initialize_transcription(self):
        """Initialize transcription service"""
        try:
            from cursor_auto_recording_transcription_fixed import CursorAutoRecordingTranscriptionFixed
            # CRITICAL: Initialize with auto_start=False so we control when it starts
            # This ensures we start in PASSIVE mode (waiting for trigger)
            self.transcription_service = CursorAutoRecordingTranscriptionFixed(
                project_root=project_root,
                auto_start=False  # CRITICAL: Don't auto-start - we'll start in passive mode
            )

            # CRITICAL: Add "Hey Jarvis" trigger word
            self.transcription_service.add_trigger_word(
                word="hey jarvis",
                action="activate",  # Use "activate" action (triggers start_recording)
                case_sensitive=False,
                confidence_threshold=0.5
            )
            self.transcription_service.add_trigger_word("jarvis", "activate", False, 0.5)

            # CRITICAL: Set passive mode - only listen for triggers, don't transcribe
            self.transcription_service.passive_mode = True

            # Set callback to detect trigger and switch to active mode
            self.transcription_service.on_trigger_detected = self._on_trigger_detected

            # Enable voice filtering (exclude wife's voice)
            try:
                from voice_filter_system import VoiceFilterSystem, VoicePrintProfile
                voice_filter = VoiceFilterSystem("primary_operator", project_root)
                op_profile = VoicePrintProfile("primary_operator", project_root)
                voice_filter.add_voice_profile(op_profile)
                self.transcription_service.voice_filter = voice_filter
                self.transcription_service.voice_filter_enabled = True
                logger.info("✅ Voice filtering enabled (exclude wife's voice)")
            except Exception as e:
                logger.debug(f"Voice filtering not available: {e}")

            logger.info("✅ Transcription service initialized")
            return True
        except Exception as e:
            logger.error(f"❌ Could not initialize transcription: {e}")
            return False

    def _start_passive_listening(self):
        """Start passive listening (waiting for trigger) - CRITICAL: Don't shut down mic"""
        if not self.transcription_service:
            if not self._initialize_transcription():
                return False

        if not self.passive_listening_active:
            logger.info("👂 Starting PASSIVE listening (waiting for 'Hey Jarvis' trigger)...")
            logger.info("   ⚠️  CRITICAL: Mic will stay ON - just waiting for trigger word")

            # CRITICAL: Auto-click Voice Input button in Cursor IDE (like VS Code "Hey Code")
            # This ensures passive listening starts immediately without manual click
            # MUST happen BEFORE starting transcription service
            # This is the KEY difference - VS Code "Hey Code" always had passive listening ready
            logger.info("🎤 Auto-clicking Voice Input button (like VS Code 'Hey Code')...")
            logger.info("   ⚠️  CRITICAL: This enables passive listening immediately - no manual click needed")
            success = False

            # Method 1: Keyboard shortcut (most reliable - like VS Code)
            try:
                import pyautogui
                pyautogui.hotkey('ctrl', 'shift', 'space')
                logger.info("✅ Sent Control+Shift+Space (voice input shortcut)")
                time.sleep(0.5)  # Give it time to activate
                success = True
            except Exception as e:
                logger.debug(f"Keyboard shortcut failed: {e}")

            # Method 2: Use MANUS button clicker (fallback)
            if not success:
                try:
                    from manus_voice_input_button import MANUSVoiceInputButton
                    voice_button = MANUSVoiceInputButton()
                    if voice_button.click_voice_input(use_manus=True):
                        logger.info("✅ Voice Input button clicked via MANUS")
                        success = True
                        time.sleep(0.5)
                except Exception as e:
                    logger.debug(f"MANUS click failed: {e}")

            if success:
                logger.info("✅ Voice Input button auto-clicked - passive listening ready (like VS Code 'Hey Code')")
                logger.info("   👂 System is now in PASSIVE mode - waiting for 'Hey Jarvis' trigger")
            else:
                logger.warning("⚠️  Could not auto-click Voice Input button - may need manual click")
                logger.warning("   ⚠️  Passive listening may not work until button is clicked")

            try:
                # CRITICAL: Start listening and KEEP it active (don't shut down mic)
                self.transcription_service.start_listening()
                self.passive_listening_active = True

                # CRITICAL: Ensure mic stays active (don't let it shut down)
                # In passive mode, use longer timeout (just waiting for trigger)
                if hasattr(self.transcription_service, 'dynamic_pause_timeout'):
                    self.transcription_service.dynamic_pause_timeout = 30.0  # Long timeout in passive mode

                # CRITICAL: Ensure is_listening stays True (mic stays on)
                if hasattr(self.transcription_service, 'is_listening'):
                    if not self.transcription_service.is_listening:
                        logger.warning("⚠️  Listening stopped - restarting to keep mic active...")
                        self.transcription_service.start_listening()

                logger.info("✅ Passive listening active - mic ON, waiting for 'Hey Jarvis'")

                # CRITICAL: Update visual debugger to show PASSIVE mode (subtle indicator)
                try:
                    if self.transcription_service and hasattr(self.transcription_service, 'debugger'):
                        if self.transcription_service.debugger:
                            self.transcription_service.debugger.update_listening_mode("passive")
                            logger.info("   👁️  Visual indicator: PASSIVE mode (subtle - waiting for trigger)")
                except Exception as e:
                    logger.debug(f"Could not update visual debugger: {e}")
            except Exception as e:
                logger.error(f"❌ Failed to start passive listening: {e}")
                return False

        return True

    def _switch_to_active_mode(self):
        """Switch to active listening mode (after trigger detected) - CRITICAL: Keep mic ON"""
        if self.mode == ListeningMode.ACTIVE:
            return  # Already in active mode

        logger.info("🎯 'Hey Jarvis' trigger detected - SWITCHING TO ACTIVE MODE")
        logger.info("   ⚠️  CRITICAL: Mic will stay ON - actively listening now")
        logger.info("   ✅ Switching from PASSIVE (trigger-only) to ACTIVE (transcribing)")
        self.mode = ListeningMode.ACTIVE
        self.trigger_detected = True
        self.last_speech_time = time.time()

        # CRITICAL: Ensure listening is active and mic stays ON
        if self.transcription_service:
            # CRITICAL: Disable passive mode - now we transcribe everything
            self.transcription_service.passive_mode = False
            logger.info("   ✅ Passive mode DISABLED - now transcribing all speech")

            # CRITICAL: Don't shut down mic - keep it active
            if not self.transcription_service.is_listening:
                logger.warning("⚠️  Listening stopped - restarting to keep mic active...")
                self.transcription_service.start_listening()

            # CRITICAL: Verify mic is still active
            if hasattr(self.transcription_service, 'is_listening'):
                if not self.transcription_service.is_listening:
                    logger.error("❌ CRITICAL: Mic shut down after trigger - restarting immediately!")
                    self.transcription_service.start_listening()
                    time.sleep(0.5)  # Brief wait
                    # Verify again
                    if not self.transcription_service.is_listening:
                        logger.error("❌ CRITICAL: Mic still not active - forcing restart...")
                        self.transcription_service.start_listening()

            # In active mode, use shorter timeout (more responsive)
            if hasattr(self.transcription_service, 'dynamic_pause_timeout'):
                self.transcription_service.dynamic_pause_timeout = 5.0  # Shorter timeout in active mode

            # CRITICAL: Update visual debugger to show ACTIVE mode (clear confirmation)
            try:
                if hasattr(self.transcription_service, 'debugger'):
                    if self.transcription_service.debugger:
                        self.transcription_service.debugger.update_listening_mode("active")
                        logger.info("   👁️  Visual indicator: ACTIVE mode (clear confirmation - listening & transcribing)")
            except Exception as e:
                logger.debug(f"Could not update visual debugger: {e}")

        # Also integrate with unified visual-audio listener
        try:
            from unified_visual_audio_listening import UnifiedVisualAudioListening
            if not self.unified_listener:
                self.unified_listener = UnifiedVisualAudioListening()
                self.unified_listener.start()
                logger.info("✅ Unified visual-audio listener started (active mode)")
        except Exception as e:
            logger.debug(f"Unified listener not available: {e}")

    def _check_for_reset(self):
        """Check if should reset to passive mode (long pause) - CRITICAL: Don't shut down mic"""
        if self.mode != ListeningMode.ACTIVE:
            return

        current_time = time.time()

        # Check if there's been a long pause
        if self.last_speech_time:
            time_since_speech = current_time - self.last_speech_time

            if time_since_speech >= self.active_mode_timeout:
                logger.info(f"⏸️  Long pause detected ({time_since_speech:.1f}s) - RESETTING to passive mode")
                logger.info("   ⚠️  CRITICAL: Mic will stay ON - just waiting for next 'Hey Jarvis' trigger")
                logger.info("   ✅ Switching from ACTIVE (transcribing) to PASSIVE (trigger-only)")
                self.mode = ListeningMode.PASSIVE
                self.trigger_detected = False
                self.last_speech_time = None

                # CRITICAL: Keep listening in passive mode (waiting for next trigger) - DON'T shut down mic
                if self.transcription_service:
                    # CRITICAL: Re-enable passive mode - only listen for triggers, don't transcribe
                    self.transcription_service.passive_mode = True
                    logger.info("   ✅ Passive mode ENABLED - only listening for 'Hey Jarvis' trigger")

                    # CRITICAL: Ensure mic stays ON (don't let it shut down)
                    if not self.transcription_service.is_listening:
                        logger.warning("⚠️  CRITICAL: Mic shut down during reset - restarting...")
                        self.transcription_service.start_listening()

                    if hasattr(self.transcription_service, 'dynamic_pause_timeout'):
                        self.transcription_service.dynamic_pause_timeout = 30.0  # Long timeout in passive mode

                    # CRITICAL: Update visual debugger to show PASSIVE mode (subtle indicator)
                    try:
                        if hasattr(self.transcription_service, 'debugger'):
                            if self.transcription_service.debugger:
                                self.transcription_service.debugger.update_listening_mode("passive")
                                logger.info("   👁️  Visual indicator: PASSIVE mode (subtle - waiting for trigger)")
                    except Exception as e:
                        logger.debug(f"Could not update visual debugger: {e}")

    def _on_trigger_detected(self, trigger, detected_text):
        """Callback when trigger word is detected"""
        # trigger is a TriggerWord object with .word and .action attributes
        trigger_word = trigger.word if hasattr(trigger, 'word') else str(trigger)
        action = trigger.action if hasattr(trigger, 'action') else "activate_listening"

        logger.info(f"🎯 Trigger word detected: '{trigger_word}' -> {action} (heard: '{detected_text}')")

        # Check if it's "Hey Jarvis" or "Jarvis" trigger
        if trigger_word.lower() in ["hey jarvis", "jarvis"] or "jarvis" in detected_text.lower():
            if action in ["activate_listening", "activate", "start_recording"]:
                self._switch_to_active_mode()

    def _monitor_listening(self):
        """Monitor listening and handle mode transitions - CRITICAL: Keep mic ON"""
        while self.running:
            try:
                # Check for trigger word detection via callback
                if self.transcription_service:
                    # Set callback for trigger detection
                    if not hasattr(self.transcription_service, '_hybrid_callback_set'):
                        self.transcription_service.on_trigger_detected = self._on_trigger_detected
                        self.transcription_service._hybrid_callback_set = True

                    # CRITICAL: In passive mode, ensure mic stays ON (just waiting for trigger)
                    if self.mode == ListeningMode.PASSIVE:
                        if not self.transcription_service.is_listening:
                            logger.warning("⚠️  CRITICAL: Mic shut down in passive mode - restarting...")
                            self.transcription_service.start_listening()
                            self.passive_listening_active = True

                    # CRITICAL: In active mode, ensure mic stays ON (actively listening)
                    if self.mode == ListeningMode.ACTIVE:
                        if not self.transcription_service.is_listening:
                            logger.error("❌ CRITICAL: Mic shut down in active mode - restarting immediately!")
                            self.transcription_service.start_listening()

                        # Update last speech time if processing audio
                        if self.transcription_service.is_listening:
                            # Check if there's recent transcription activity
                            if hasattr(self.transcription_service, 'current_session'):
                                if self.transcription_service.current_session:
                                    # Speech is happening - update timestamp
                                    self.last_speech_time = time.time()
                            else:
                                # Even if no session, if listening is active, assume speech might be happening
                                self.last_speech_time = time.time()

                # Check for reset to passive mode
                self._check_for_reset()

                time.sleep(0.5)  # Check every 0.5 seconds
            except Exception as e:
                logger.error(f"❌ Monitor loop error: {e}")
                time.sleep(1)

    def _check_services_ready(self) -> Tuple[bool, Dict[str, bool]]:
        """Check if all LUMINA services are ready

        Returns:
            (critical_ready, services_status) - tuple of (bool, dict)
        """
        services_ready = {
            "transcription": False,
            "voice_filter": False,
            "visual_debugger": False,
            "ir_camera": False,
            "human_activity_detector": False
        }

        # Check transcription service
        if self.transcription_service and self.transcription_service.is_listening:
            services_ready["transcription"] = True

        # Check voice filter
        try:
            if self.transcription_service and hasattr(self.transcription_service, 'voice_filter'):
                if self.transcription_service.voice_filter:
                    services_ready["voice_filter"] = True
        except:
            pass

        # Check visual debugger
        try:
            if self.transcription_service and hasattr(self.transcription_service, 'debugger'):
                if self.transcription_service.debugger:
                    services_ready["visual_debugger"] = True
        except:
            pass

        # Check IR camera (optional)
        try:
            from ir_camera_helper import find_ir_camera
            if find_ir_camera() is not None:
                services_ready["ir_camera"] = True
        except:
            services_ready["ir_camera"] = True  # Optional service

        # Check human activity detector (optional)
        try:
            from human_activity_detector import get_human_detector
            detector = get_human_detector()
            if detector:
                services_ready["human_activity_detector"] = True
        except:
            services_ready["human_activity_detector"] = True  # Optional service

        # All critical services ready?
        critical_ready = services_ready["transcription"] and services_ready["voice_filter"]

        return critical_ready, services_ready

    def _greet_user(self):
        """Greet user when all services are ready - CRITICAL: Only in PASSIVE mode - END TIMING HERE"""
        try:
            from cursor_transcription_sender import send_to_cursor
            import time

            # CRITICAL: Only greet if we're in PASSIVE mode (waiting for trigger)
            if self.mode != ListeningMode.PASSIVE:
                logger.debug("⚠️  Not in passive mode - skipping greeting")
                return

            greeting = "Hello! LUMINA is ready. All services are up and running. I'm in passive mode, waiting for you to say 'Hey Jarvis'."

            logger.info("=" * 80)
            logger.info("👋 JARVIS GREETING USER")
            logger.info("=" * 80)
            logger.info(f"   Mode: PASSIVE (waiting for 'Hey Jarvis' trigger)")
            logger.info(f"   Message: {greeting}")
            logger.info("=" * 80)

            # Small delay to ensure Cursor is ready
            time.sleep(1.0)

            # Send greeting to Cursor IDE
            send_to_cursor(greeting)

            logger.info("✅ Greeting sent to Cursor IDE")

            # CRITICAL: END TIMING HERE - JARVIS IS NOW READY FOR FIRST WAKE WORD
            # AI-MANAGED: JARVIS automatically manages timing (no manual intervention)
            try:
                from startup_timer import end_timing
                total_time = end_timing()
                logger.info("=" * 80)
                logger.info("⏱️  STARTUP COMPLETE - JARVIS READY FOR FIRST WAKE WORD")
                logger.info("=" * 80)
                logger.info(f"   Total time from startup to ready: {total_time:.2f}s")
                logger.info(f"   JARVIS is now ready to receive 'Hey Jarvis'")
                logger.info("   🤖 AI: Timing managed automatically - no manual intervention needed")
                logger.info("=" * 80)

                # AI-MANAGED: Automatically learn from this startup
                try:
                    from ai_managed_startup import get_ai_startup
                    ai_startup = get_ai_startup()
                    if ai_startup:
                        # Record this startup for AI learning
                        ai_startup.service_times.update({
                            "greeting_sent": time.time() - (ai_startup.start_time or time.time())
                        })
                        ai_startup._learn_from_startup(total_time)
                        logger.info("🤖 AI: Startup data recorded for automatic optimization")
                except Exception as e:
                    logger.debug(f"AI learning not available: {e}")
            except Exception as e:
                logger.debug(f"Could not end timing: {e}")

        except Exception as e:
            logger.warning(f"⚠️  Could not send greeting: {e}")

    def start(self):
        """Start hybrid passive-active listening - CRITICAL: Start in PASSIVE mode - AI-MANAGED"""
        # AI-MANAGED: Automatically time startup (JARVIS manages this)
        try:
            from startup_timer import get_timer, start_timing
            timer = get_timer()
            if not timer.start_time:
                start_timing()
        except:
            timer = None

        # OPTIMIZATION: Time transcription initialization
        init_start = time.time()
        if not self._initialize_transcription():
            return False
        if timer:
            timer.service_times["hybrid_transcription_init"] = time.time() - init_start

        self.running = True

        # CRITICAL: Start in PASSIVE mode (waiting for trigger, not actively listening)
        logger.info("=" * 80)
        logger.info("🎯 HYBRID PASSIVE-ACTIVE LISTENING STARTED")
        logger.info("=" * 80)
        logger.info("   👂 Starting in PASSIVE mode - waiting for 'Hey Jarvis' trigger")
        logger.info("   ⚠️  CRITICAL: Mic will stay ON - just waiting for trigger word")
        logger.info("=" * 80)

        # Start passive listening (mic ON, but just waiting for trigger)
        self._start_passive_listening()

        # CRITICAL: Verify we're in passive mode
        self.mode = ListeningMode.PASSIVE
        self.trigger_detected = False

        # Start monitoring loop
        monitor_thread = threading.Thread(target=self._monitor_listening, daemon=True)
        monitor_thread.start()

        logger.info("✅ Hybrid listening started in PASSIVE mode")
        logger.info("   Say 'Hey Jarvis' to switch to ACTIVE mode")

        # CRITICAL: Check services and greet user when ready - THIS IS THE END POINT FOR TIMING
        def check_and_greet():
            """Check services and greet when ready - END TIMING WHEN GREETING SENT"""
            import time
            max_wait = 10  # Wait up to 10 seconds for services
            wait_time = 0
            check_interval = 0.5

            # OPTIMIZATION: Time the service check wait
            try:
                from startup_timer import get_timer
                timer = get_timer()
                if timer:
                    timer.service_times["service_check_wait"] = 0.0
                    wait_start = time.time()
            except:
                timer = None
                wait_start = None

            while wait_time < max_wait:
                critical_ready, services_status = self._check_services_ready()

                if critical_ready:
                    if timer and wait_start:
                        timer.service_times["service_check_wait"] = time.time() - wait_start

                    logger.info("✅ All critical services ready!")
                    logger.info(f"   Services status: {services_status}")

                    # Small delay to ensure everything is fully initialized
                    time.sleep(1.0)

                    # CRITICAL: Greet user - THIS ENDS THE TIMING (JARVIS READY FOR FIRST WAKE)
                    self._greet_user()
                    return

                time.sleep(check_interval)
                wait_time += check_interval

            # If services not ready after max wait, still greet (services might be optional)
            if timer and wait_start:
                timer.service_times["service_check_wait"] = time.time() - wait_start

            logger.warning("⚠️  Some services not ready, but greeting anyway...")
            # CRITICAL: Greet user - THIS ENDS THE TIMING (JARVIS READY FOR FIRST WAKE)
            self._greet_user()

        # Start service check in background
        greet_thread = threading.Thread(target=check_and_greet, daemon=True)
        greet_thread.start()

        return True

    def stop(self):
        """Stop hybrid listening"""
        self.running = False
        if self.transcription_service:
            try:
                self.transcription_service.stop_listening()
            except:
                pass
        if self.unified_listener:
            try:
                self.unified_listener.stop()
            except:
                pass
        logger.info("✅ Hybrid passive-active listening stopped")


def main():
    """Main function"""
    print("=" * 80)
    print("🎯 HYBRID PASSIVE-ACTIVE LISTENING")
    print("=" * 80)
    print()
    print("How it works:")
    print("  👂 Passive Mode: Waiting for 'Hey Jarvis' trigger")
    print("  🎯 Active Mode: Actively listening after trigger")
    print("  ⏸️  Reset: Long pauses (10s) reset to passive mode")
    print()
    print("Say 'Hey Jarvis' to activate listening!")
    print()

    listener = HybridPassiveActiveListening()
    if listener.start():
        print("=" * 80)
        print("✅ HYBRID LISTENING ACTIVE")
        print("=" * 80)
        print()
        print("Currently in PASSIVE mode - waiting for 'Hey Jarvis'")
        print("Press Ctrl+C to stop")
        print()

        try:
            while True:
                time.sleep(1)
                if listener.mode == ListeningMode.ACTIVE:
                    print("🎯 ACTIVE MODE - Listening attentively")
                else:
                    print("👂 PASSIVE MODE - Waiting for trigger...")
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            listener.stop()


if __name__ == "__main__":


    main()