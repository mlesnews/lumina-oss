#!/usr/bin/env python3
"""Voice Filter System.

This module implements real‑time audio filtering based on voice activity
detection, speaker recognition, and audio‑to‑transcription comparison.
It exposes the :class:`VoiceFilterSystem` class which can be instantiated
with a user ID and optional project root.  The system is designed to be
plugged into the larger Cursor ecosystem.
"""

"""
Voice Filter System - @EVO @ADAPT @IMPROVISE @OVERC

Automatic filtering of unknown voices and sounds not in session scope.
Integrates with Voice Profile Library System for dynamic, evolutionary filtering.

Core Values:
- Adapt: Adapts to new voices, conditions, contexts automatically
- Improvise: Makes filtering decisions with incomplete information
- Overcome: Handles edge cases, unknown scenarios, filtering challenges

Tags: #VOICE_FILTER #DYNAMIC_SCALING #EVO #ADAPT #IMPROVISE #OVERCOME
      @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    from voice_profile_library_system import SoundType, VoiceProfileLibrarySystem

    get_logger = get_adaptive_logger  # Use adaptive logger for DEBUG mode
except ImportError:
    try:
        from lumina_logger import get_logger
        from voice_profile_library_system import SoundType, VoiceProfileLibrarySystem
    except ImportError as e:
        import logging

        logging.basicConfig(level=logging.DEBUG)  # DEBUG in testing mode

        def get_logger(name):
            return logging.getLogger(name)

        logger = get_logger("VoiceFilter")
        logger.warning("⚠️  Could not import voice profile library: %s", e)
        VoiceProfileLibrarySystem = None
        SoundType = None

logger = get_logger("VoiceFilter")


@dataclass
class FilterResult:
    """Result of audio filtering decision"""

    should_process: bool
    should_filter: bool
    reason: str
    confidence: float
    profile_id: Optional[str] = None
    confidence_level: Optional[str] = None
    adaptation_applied: bool = False
    recognition_feedback: Optional[str] = None  # Feedback about what was heard
    pronunciation_suggestion: Optional[str] = None  # Suggestion if confidence low


class VoiceFilterSystem:
    """
    Voice Filter System - @EVO @ADAPT @IMPROVISE @OVERCOME

    Automatically filters out:
    - Unknown voices not in session scope
    - Background sounds not in allowed types
    - Third-party audio not relevant to current session
      (TV, voice assistants like Alexa/Google/Siri, etc.)
    - Tertiary speakers (Glenda, wife, etc.) - always filtered

    Core Values Applied:
    - Adapt: System adapts filtering based on session context
    - Improvise: Makes best filtering decisions with available data
    - Overcome: Handles filtering challenges and learns from mistakes
    """

    def __init__(
        self,
        user_id: str = "user",
        project_root: Optional[Path] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize voice filter system

        Args:
            user_id: Primary user ID
            project_root: Project root directory
            session_id: Current session ID (creates scope if not exists)
        """
        if project_root is None:
            project_root_path = Path(__file__).parent.parent.parent
        else:
            project_root_path = Path(project_root)

        # Store as instance variable (avoid redefining outer scope variable)
        self.project_root = project_root_path
        self.user_id = user_id
        self.session_id = session_id or f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Initialize voice profile library
        if VoiceProfileLibrarySystem is None:
            logger.error("❌ Voice Profile Library System not available")
            self.profile_library = None
            self.enabled = False
        else:
            try:
                self.profile_library = VoiceProfileLibrarySystem(project_root=self.project_root)
                self.enabled = True

                # Ensure session scope exists
                if self.session_id not in self.profile_library.session_scopes:
                    self.profile_library.create_session_scope(
                        session_id=self.session_id,
                        initial_profiles=[],
                        auto_learn=True,
                        strict_mode=False,
                    )

                # Add user profile if not exists
                user_profile_id = f"user_{user_id}"
                if user_profile_id not in self.profile_library.voice_profiles:
                    self.profile_library.add_voice_profile(
                        profile_id=user_profile_id,
                        name=f"User {user_id}",
                        user_id=user_id,
                        session_id=self.session_id,
                    )
                    # Add to session scope
                    scope = self.profile_library.session_scopes[self.session_id]
                    scope.active_profiles.add(user_profile_id)
                    # Access protected method for session scope management
                    self.profile_library._save_session_scopes()  # pylint: disable=protected-access

                # Ensure Glenda is registered as tertiary (always filtered)
                # She's not in scope - this is OUR conversation
                self._ensure_glenda_registered_as_tertiary()

                logger.info("✅ Voice Filter System initialized - FULL-TIME FILTERING ACTIVE")
                logger.info("   Session: %s", self.session_id)
                logger.info("   User: %s", user_id)
                logger.info(
                    "   Tertiary (ALWAYS FILTERED): Glenda, wife, background, "
                    "third-party devices (Alexa, Google, Siri, etc.)"
                )
                logger.info("   Core Values: Adapt, Improvise, Overcome")
                logger.info("   Status: ACTIVE - continuously filtering (full-time)")
            except (ImportError, AttributeError, ValueError) as e:
                logger.error("❌ Failed to initialize voice profile library: %s", e)
                self.profile_library = None
                self.enabled = False

        # Filtering statistics
        self.stats = {
            "total_processed": 0,
            "filtered_out": 0,
            "allowed_through": 0,
            "unknown_voices": 0,
            "known_voices": 0,
            "low_confidence_detections": 0,
            "pronunciation_feedback_given": 0,
        }

        # Feedback settings for better sync
        self.provide_feedback = True  # Enable real-time feedback
        self.low_confidence_threshold = 0.7  # Below this, provide feedback
        self.feedback_history = []  # Track recent feedback for pattern detection

        # Speaker priority tracking
        # Hierarchy: PRIMARY (user) > SECONDARY (assistant) >
        # TERTIARY (ALWAYS FILTERED during conversations -
        # Glenda, wife, etc.)
        self.primary_speaker_id = f"user_{user_id}"  # Primary speaker
        self.secondary_speaker_id = "assistant"  # Secondary (JARVIS)
        self.primary_speaker_active = False  # Track if primary is speaking
        # Extended timeout: 60 seconds after primary stops
        # (DOUBLED: 30->60 to prevent interruptions)
        self.primary_speaker_timeout = 60.0
        self.last_primary_activity = None  # Timestamp of last primary activity
        # ALWAYS filter tertiary speakers (Glenda, wife, background) - no exceptions
        # This is OUR conversation - tertiary speakers are not in scope
        self.tertiary_always_filtered = True
        # Glenda/wife profile IDs to always filter - EXPANDED for better detection
        # Also includes TV/background audio and third-party voice assistants that should be filtered
        self.tertiary_profile_ids = {
            "wife",
            "glenda",
            "wife_glenda",
            "glenda_wife",
            "konda",
            "kanda",
            "genda",
            "glinda",  # Common mispronunciations/variations
            "tv",
            "television",
            "background",
            "background_tv",
            "tv_audio",  # TV/background audio
            # Third-party voice assistants (ALWAYS FILTERED - not in scope)
            "alexa",
            "echo",
            "amazon_alexa",
            "google",
            "google_assistant",
            "assistant_google",
            "siri",
            "cortana",
            "bixby",
            "samsung_bixby",
            "smart_speaker",
            "voice_assistant",
            "third_party",
            "third_party_voice",
        }
        # AGGRESSIVE filtering: Filter ANY voice that's not primary or secondary
        # Even if we're not 100% sure it's Glenda, if it's not YOU, filter it
        self.aggressive_tertiary_filtering = True

        # Invited profiles - explicitly invited to conversation (wife, third parties, etc.)
        # When a profile is invited, it's temporarily allowed through the filter
        self.invited_profiles = set()  # Set of profile IDs that are explicitly invited
        self.invite_expiry = {}  # Dict of profile_id -> expiry timestamp
        self.default_invite_duration = 3600  # Default: 1 hour invite duration

        # Greeting detection - automatically invite when wife greets us
        self.greeting_patterns = [
            "hello",
            "hi",
            "hey",
            "good morning",
            "good afternoon",
            "good evening",
            "greetings",
            "howdy",
            "hi there",
            "hello there",
            "hey there",
            "good day",
            "pleasure",
            "nice to meet",
            "nice to see",
        ]
        self.greeting_detection_enabled = True

        # ULTRA-AGGRESSIVE filtering thresholds for audio-transcription comparison
        # Maximum sensitivity for wife voice detection (prevent bleed-through)
        self.aggressive_mismatch_threshold = 0.6  # 60% = mismatch (ultra-aggressive)
        self.aggressive_filter_threshold = 0.5  # 50% = filter (ultra-aggressive)
        # Wife's voice is bleeding through - need maximum filtering

        # Workflow tracker integration - track all interactions
        try:
            from workflow_tracker_integration import get_workflow_tracker, track_voice_interaction

            self.workflow_tracker = get_workflow_tracker(
                project_root=self.project_root, auto_start=True
            )
            self.track_voice_interaction = track_voice_interaction
        except ImportError:
            self.workflow_tracker = None
            self.track_voice_interaction = None

        # Audio-to-transcription comparison - real-time pattern detection
        try:
            from audio_transcription_comparison import AudioTranscriptionComparator

            self.audio_comparator = AudioTranscriptionComparator(project_root=self.project_root)
            logger.info("   ✅ Audio-Transcription Comparator integrated")
        except ImportError:
            self.audio_comparator = None
            logger.warning("   ⚠️  Audio-Transcription Comparator not available")

        # Grammarly integration - grammar/spelling correction after confirmation
        try:
            from grammarly_integration import GrammarlyIntegration

            self.grammarly = GrammarlyIntegration(project_root=self.project_root)
            logger.info("   ✅ Grammarly Integration initialized")
        except ImportError:
            self.grammarly = None
            logger.warning("   ⚠️  Grammarly Integration not available")

    def extract_audio_features(self, audio_data: Any) -> Dict[str, Any]:
        """
        Extract features from audio data for voice/sound identification

        @ADAPT: Adapts feature extraction based on available audio data
        @IMPROVISE: Works with various audio formats and qualities
        @OVERCOME: Handles missing or corrupted audio data

        This is a simplified implementation. In production, you would use:
        - MFCC (Mel-frequency cepstral coefficients)
        - Spectral features
        - Pitch, formants, etc.
        - Deep learning embeddings
        """
        # Placeholder for actual feature extraction
        # In real implementation, use librosa, pyAudioAnalysis, or similar

        features = {
            "duration": getattr(audio_data, "duration", 0.0),
            "sample_rate": getattr(audio_data, "sample_rate", 16000),
            "channels": getattr(audio_data, "channels", 1),
            # Add more features as needed
        }

        # Try to extract more features if audio processing libraries available
        try:
            import numpy as np

            if hasattr(audio_data, "audio"):
                audio_array = audio_data.audio
                if isinstance(audio_array, np.ndarray):
                    features["mean_amplitude"] = float(np.mean(np.abs(audio_array)))
                    features["std_amplitude"] = float(np.std(audio_array))
                    features["max_amplitude"] = float(np.max(np.abs(audio_array)))
        except (ImportError, AttributeError):
            pass

        return features

    def should_filter(
        self,
        audio_data: Any,
        audio_features: Optional[Dict[str, Any]] = None,
        sound_type: Optional[SoundType] = None,
        transcription_text: Optional[str] = None,
    ) -> FilterResult:
        """
        Determine if audio should be filtered out

        @ADAPT: Adapts filtering based on session scope and confidence
        @IMPROVISE: Makes filtering decisions with incomplete information
        @OVERCOME: Handles edge cases and learns from mistakes

        Args:
            audio_data: Audio data (format depends on source)
            audio_features: Pre-extracted features (optional)
            sound_type: Type of sound (voice, background, etc.)
            transcription_text: Transcribed text (for greeting detection)

        Returns:
            FilterResult with filtering decision and metadata
        """
        if not self.enabled or self.profile_library is None:
            # System not enabled - allow through
            return FilterResult(
                should_process=True, should_filter=False, reason="system_disabled", confidence=0.5
            )

        self.stats["total_processed"] += 1

        # CRITICAL BYPASS: Wake word commands always allowed through
        # This ensures user can always trigger JARVIS, even if voice
        # is not recognized as primary speaker
        if transcription_text:
            transcript_lower = transcription_text.lower().strip()
            wake_words = [
                "hey jarvis",
                "jarvis",
                "hey jarvis,",
                "hey jarvis.",
                "hey jarvis!",
                "hey jarvis test",
                "jarvis test",
            ]

            # Check if transcript starts with or contains wake word
            if any(
                transcript_lower.startswith(wake) or wake in transcript_lower[:50]
                for wake in wake_words
            ):
                logger.info("   ✅ WAKE WORD DETECTED - bypassing filter (user trigger)")

                # Mark as primary speaker to prevent future filtering
                self.primary_speaker_active = True
                self.last_primary_activity = datetime.now()

                # Return allow result
                return FilterResult(
                    should_process=True,
                    should_filter=False,
                    reason="wake_word_bypass",
                    confidence=1.0,
                    profile_id=self.primary_speaker_id,
                )

        # Extract features if not provided
        if audio_features is None:
            audio_features = self.extract_audio_features(audio_data)

        # TV DETECTION: Check if audio might be TV/television (PRIORITY FILTER)
        # TV audio typically has:
        # - Consistent volume levels (not natural speech patterns)
        # - Background music/sound effects
        # - Multiple speakers (dialog)
        # - Lower frequency content (TV speakers)
        # FILTER TV IMMEDIATELY - it's bleeding through and
        # interrupting workflow
        is_tv_audio = self._detect_tv_audio(audio_features, transcription_text)

        # AGGRESSIVE TV FILTERING: Filter TV audio BEFORE other checks
        if is_tv_audio:
            logger.info(
                "   🚫 TV AUDIO DETECTED - FILTERING IMMEDIATELY (bleed-through prevention)"
            )
            # Learn TV audio pattern
            if self.profile_library:
                self._learn_tertiary_audio(
                    audio_features, "tv_bleed_through_prevention", "tv_audio", "tv"
                )
            # Return filtered result immediately
            return FilterResult(
                should_process=False,
                should_filter=True,
                reason="tv_audio_immediate_filter",
                confidence=0.98,
                profile_id="tv_audio",
            )

        # REAL-TIME AUDIO-TO-TRANSCRIPTION COMPARISON
        # Compare transcribed text to actual audio live feed
        # Look for patterns or lack of patterns to define results and break loops
        comparison_result = None

        if self.audio_comparator and transcription_text:
            try:
                comparison_result = self.audio_comparator.compare_audio_to_transcription(
                    audio_data=audio_data,
                    transcription_text=transcription_text,
                    expected_speaker=self.primary_speaker_id,
                )

                # Use comparison to improve filtering
                # ULTRA-AGGRESSIVE: Filter if confidence is low OR if
                # pattern suggests mismatch
                # Wife's voice is bleeding through - maximum filtering
                should_filter_from_comparison = (
                    comparison_result.should_filter
                    or comparison_result.match_confidence < (self.aggressive_filter_threshold)
                    or comparison_result.pattern_type in ["voice_mismatch", "inconsistent", "noise"]
                    or
                    # ULTRA-AGGRESSIVE: Filter if primary is active and
                    # confidence is even slightly low
                    (self.primary_speaker_active and comparison_result.match_confidence < 0.7)
                    # 70% threshold when primary active
                )

                if should_filter_from_comparison:
                    # Audio doesn't match transcription - likely wrong speaker (e.g., wife)
                    logger.info(
                        "   🚫 FILTERED via audio-transcription comparison: %s "
                        "(confidence: %.2f, pattern: %s)",
                        comparison_result.reasoning,
                        comparison_result.match_confidence,
                        comparison_result.pattern_type or "none",
                    )
                    return FilterResult(
                        should_process=False,
                        should_filter=True,
                        reason=f"audio_transcription_mismatch: {comparison_result.reasoning}",
                        confidence=1.0 - comparison_result.match_confidence,
                        profile_id=None,
                    )

                # Break loop if patterns don't match
                if comparison_result.should_break_loop:
                    logger.info(
                        "   🔄 Breaking loop - pattern mismatch: %s", comparison_result.reasoning
                    )

                # ONE TRUE SOURCE: If confidence is high enough, feed to Grammarly AI-Driven CLI
                # This is the workflow: auto-accept all corrections (no manual GUI clicking)
                if (
                    not comparison_result.should_filter
                    and comparison_result.match_confidence >= 0.7
                ):
                    try:
                        # Try AI-driven Grammarly CLI first (auto-accept workflow)
                        from grammarly_ai_driven_cli import get_grammarly_ai_cli

                        cli = get_grammarly_ai_cli()
                        corrected_text = cli.process_transcript(
                            transcription_text, auto_accept=True
                        )
                        if corrected_text != transcription_text:
                            logger.info(
                                "   ✅ Grammarly AI-driven: %d corrections auto-accepted",
                                len(corrected_text) - len(transcription_text),  # Approximate
                            )
                            # Use corrected text for downstream processing
                            transcription_text = corrected_text
                    except ImportError:
                        # Fallback to regular Grammarly integration
                        if self.grammarly:
                            try:
                                grammar_result = self.grammarly.process_confirmed_transcription(
                                    transcription_text=transcription_text,
                                    comparison_confidence=comparison_result.match_confidence,
                                )
                                if grammar_result.corrected_text != grammar_result.original_text:
                                    logger.info(
                                        "   ✅ Grammar corrected: %d corrections applied",
                                        len(grammar_result.corrections),
                                    )
                                    # Grammar-corrected text available in grammar_result
                                    # for downstream processing if needed
                            except (AttributeError, TypeError, ValueError, ImportError) as e:
                                logger.debug("   Grammar check failed: %s", e)
                    except (AttributeError, TypeError, ValueError) as e:
                        logger.debug("   Grammarly AI-driven CLI failed: %s", e)
            except (AttributeError, TypeError, ValueError, ImportError) as e:
                logger.debug("   Audio-transcription comparison failed: %s", e)

        # AUTOMATIC GREETING DETECTION & INVITATION
        # If we detect a greeting from wife/third party, automatically invite them
        # This follows @peak butler's standard - warm, professional, friendly salutation
        if transcription_text:
            greeting_profile = self._detect_greeting(transcription_text)
            if greeting_profile and greeting_profile.lower() not in self.invited_profiles:
                # Auto-invite on greeting detection
                self.invite_to_conversation(
                    profile_id=greeting_profile, duration_seconds=self.default_invite_duration
                )
                # Generate and log butler-style greeting
                greeting_message = self._generate_butler_greeting(greeting_profile)
                logger.info("   👋 %s", greeting_message)
                # Note: The greeting message could be sent to chat if needed
                # For now, we log it and the invitation is automatic

        # Determine sound type if not provided
        if sound_type is None:
            # Try to identify if it's voice or other sound
            # This is simplified - in production, use audio classification
            sound_type = SoundType.VOICE  # Default assumption

        # Try to identify voice FIRST to determine speaker priority
        profile_id = None
        confidence_level = None
        is_tertiary = False
        is_wife = False

        if sound_type == SoundType.VOICE or sound_type is None:
            identified_profile, ident_confidence, ident_level = self.profile_library.identify_voice(
                audio_features=audio_features, session_id=self.session_id
            )
            if identified_profile:
                profile_id = identified_profile
                confidence_level = ident_level.name if ident_level else None

                # ENFORCE SPEAKER PRIORITY: PRIMARY > SECONDARY > NO TERTIARY
                # If primary speaker is active, filter out tertiary speakers
                if profile_id == self.primary_speaker_id:
                    # Primary speaker detected - mark as active
                    self.primary_speaker_active = True
                    self.last_primary_activity = datetime.now()
                    logger.info("   ✅ PRIMARY SPEAKER ACTIVE: %s", profile_id)
                    # Primary speaker - NEVER filter
                    should_filter = False
                    reason = "primary_speaker_allowed"
                    confidence = ident_confidence
                elif profile_id == self.secondary_speaker_id:
                    # Secondary speaker (assistant) - allow if primary not recently active
                    if self.primary_speaker_active and self.last_primary_activity:
                        # Check if primary timeout has passed
                        time_since_primary = (
                            datetime.now() - self.last_primary_activity
                        ).total_seconds()
                        if time_since_primary < self.primary_speaker_timeout:
                            # Primary was recently active - filter secondary
                            should_filter = True
                            reason = "primary_speaker_priority"
                            confidence = 0.9
                            logger.info(
                                "   🚫 FILTERED SECONDARY (primary priority): %s", profile_id
                            )
                        else:
                            # Primary timeout passed - allow secondary
                            self.primary_speaker_active = False
                            should_filter = False
                            reason = "secondary_speaker_allowed"
                            confidence = ident_confidence
                            logger.debug(
                                "   ✅ Secondary speaker allowed (primary timeout): %s", profile_id
                            )
                    else:
                        should_filter = False
                        reason = "secondary_speaker_allowed"
                        confidence = ident_confidence
                        logger.debug("   ✅ Secondary speaker allowed: %s", profile_id)
                else:
                    # Tertiary speaker (Glenda, wife, background,
                    # third-party devices, etc.) -
                    # ALWAYS FILTER to prevent workflow interruption
                    # This is OUR collaborative process - tertiary speakers
                    # interrupt OUR workflow
                    # Check for wife/Glenda/TV/third-party by multiple
                    # name variations and profile ID set
                    profile_lower = profile_id.lower()
                    is_tertiary = (
                        profile_id in self.tertiary_profile_ids
                        or "wife" in profile_lower
                        or "glenda" in profile_lower
                        or "konda" in profile_lower  # Common mispronunciation
                        or "kanda" in profile_lower
                        or "genda" in profile_lower
                        or "tv" in profile_lower
                        or "television" in profile_lower
                        or is_tv_audio  # TV detection result
                        # Third-party voice assistants (ALWAYS FILTERED)
                        or "alexa" in profile_lower
                        or "echo" in profile_lower
                        or "google" in profile_lower
                        and "assistant" in profile_lower
                        or "siri" in profile_lower
                        or "cortana" in profile_lower
                        or "bixby" in profile_lower
                        or "smart_speaker" in profile_lower
                        or "voice_assistant" in profile_lower
                        or "third_party" in profile_lower
                    )
                    is_wife = (
                        "wife" in profile_lower
                        or "glenda" in profile_lower
                        or "konda" in profile_lower
                        or "kanda" in profile_lower
                        or "genda" in profile_lower
                    )  # For learning purposes

        # ULTRA-AGGRESSIVE: Filter ANY non-primary/secondary voice when primary is active
        # Wife's voice is bleeding through - need maximum filtering
        if self.primary_speaker_active:
            # PRIMARY IS ACTIVE - filter EVERYTHING that's not primary
            # This prevents wife/Glenda from bleeding through
            if profile_id != self.primary_speaker_id:
                is_tertiary = True
                logger.info(
                    "   🚫 ULTRA-AGGRESSIVE FILTER (PRIMARY ACTIVE): "
                    "Filtering non-primary voice: %s (wife bleed-through prevention)",
                    profile_id,
                )

        # AGGRESSIVE: If aggressive filtering enabled, filter ANY non-primary/secondary
        # Even if we're not 100% sure it's Glenda, filter it if it's not YOU
        if self.aggressive_tertiary_filtering and not is_tertiary:
            # Still filter it - it's not primary or secondary, so it's tertiary
            is_tertiary = True
            logger.debug(
                "   🚫 AGGRESSIVE FILTER: Non-primary/secondary voice filtered: %s", profile_id
            )

        # ALWAYS filter tertiary speakers - no exceptions during
        # conversations
        # This prevents workflow performance degradation
        # Glenda/wife/TV is NEVER allowed through - this is OUR conversation
        # TV audio is a learning example - filter it and learn from it
        if (
            profile_id
            and profile_id != self.primary_speaker_id
            and profile_id != self.secondary_speaker_id
        ):
            if is_tv_audio:
                # TV detected - always filter and learn
                should_filter = True
                reason = "tv_audio_filtered"
                confidence = 0.95
                logger.info(
                    "   🚫 FILTERED TV AUDIO (learning example - always filtered): %s",
                    profile_id or "tv_audio",
                )
            elif self.tertiary_always_filtered or is_tertiary:
                # Check if profile is explicitly invited - if so, allow through
                if profile_id and self._is_invited(profile_id):
                    should_filter = False
                    reason = "invited_to_conversation"
                    confidence = 0.95
                    logger.info(
                        "   ✅ ALLOWED INVITED PROFILE: %s (explicitly invited to conversation)",
                        profile_id,
                    )
                else:
                    should_filter = True
                if self.primary_speaker_active:
                    reason = "tertiary_filtered_primary_active"
                    confidence = 0.99  # Higher confidence for Glenda/wife
                    logger.info(
                        "   🚫 FILTERED TERTIARY (PRIMARY ACTIVE - "
                        "workflow protection): %s - NOT IN SCOPE",
                        profile_id,
                    )
                elif self.last_primary_activity:
                    # Check if primary was recently active (extended timeout)
                    time_since_primary = (
                        datetime.now() - self.last_primary_activity
                    ).total_seconds()
                    if time_since_primary < self.primary_speaker_timeout:
                        # Primary was recently active - filter tertiary
                        # (prevent interruption)
                        should_filter = True
                        reason = "tertiary_filtered_primary_recent"
                        confidence = 0.95
                        logger.info(
                            "   🚫 FILTERED TERTIARY (PRIMARY RECENT - prevent interruption): %s",
                            profile_id,
                        )
                    else:
                        # Even after timeout, filter tertiary to maintain workflow
                        should_filter = True
                        reason = "tertiary_filtered_workflow_protection"
                        confidence = 0.9
                        logger.debug(
                            "   🚫 FILTERED TERTIARY (workflow protection): %s", profile_id
                        )
                else:
                    # No primary activity yet, but still filter tertiary
                    # (they're not in scope)
                    should_filter = True
                    reason = "tertiary_not_in_scope"
                    confidence = 0.85
                    logger.debug("   🚫 FILTERED TERTIARY (not in scope): %s", profile_id)

                # Learn tertiary audio (wife/Glenda/TV/background) silently in background
                # (doesn't affect filtering - tertiary is always filtered out)
                if is_wife and self.profile_library:
                    self._learn_tertiary_audio(audio_features, reason, profile_id, "voice")
                if is_tv_audio and self.profile_library:
                    # Learn TV audio as tertiary (always filtered)
                    # Use TV detection result to learn TV audio patterns
                    logger.debug("   📺 TV audio detected - learning as tertiary filter example")
                    self._learn_tertiary_audio(
                        audio_features, f"tv_detected_{reason}", "tv_audio", "tv"
                    )
            else:
                # Fallback (shouldn't happen with tertiary_always_filtered=True)
                should_filter = True
                reason = "tertiary_filtered_default"
                confidence = 0.8
        elif not profile_id:
            # Unknown voice - filter AGGRESSIVELY to prevent workflow interruption
            # Unknown voices could be tertiary speakers (Glenda, wife, TV, Alexa, etc.)
            # we haven't identified yet
            # Check if it's TV audio first (learning example)
            if is_tv_audio:
                should_filter = True
                reason = "tv_audio_unknown_voice"
                confidence = 0.95
                logger.info(
                    "   🚫 FILTERED TV AUDIO (unknown voice, learning example): %s",
                    profile_id or "tv_audio",
                )
                # Learn TV audio
                if self.profile_library:
                    self._learn_tertiary_audio(audio_features, reason, "tv_audio", "tv")
            # AGGRESSIVE MODE: Filter ALL unknown voices immediately
            elif self.aggressive_tertiary_filtering:
                should_filter = True
                reason = "unknown_voice_aggressive_filter"
                confidence = 0.98  # High confidence in filtering unknown voices
                logger.info(
                    "   🚫 AGGRESSIVE FILTER: Unknown voice filtered "
                    "(could be Glenda/wife/TV/third-party device): %s",
                    profile_id or "unknown",
                )
            else:
                should_filter, reason, confidence = self.profile_library.should_filter_audio(
                    audio_features=audio_features, session_id=self.session_id, sound_type=sound_type
                )

            # CRITICAL: If primary is active or was recently active,
            # ULTRA-AGGRESSIVE filtering of unknown voices
            # This prevents Glenda/wife/Alexa from bleeding through
            # Wife's voice is STILL bleeding through - maximum filtering
            if self.primary_speaker_active:
                should_filter = True
                reason = "unknown_voice_filtered_primary_active_ultra_aggressive"
                confidence = 0.99  # Maximum confidence - prevent wife bleed-through
                logger.info(
                    "   🚫 ULTRA-AGGRESSIVE FILTER: Unknown voice filtered "
                    "(PRIMARY ACTIVE - preventing wife/Glenda bleed-through): %s",
                    profile_id or "unknown",
                )
                # Learn as wife/Glenda immediately for better future detection
                if self.profile_library:
                    self._learn_tertiary_audio(
                        audio_features,
                        "wife_bleed_through_prevention_ultra",
                        "wife_glenda",
                        "voice",
                    )
            elif self.last_primary_activity:
                # Check if primary was recently active
                time_since_primary = (datetime.now() - self.last_primary_activity).total_seconds()
                if time_since_primary < self.primary_speaker_timeout:
                    # Primary was recently active - filter unknown voices
                    should_filter = True
                    reason = "unknown_voice_filtered_primary_recent"
                    confidence = 0.9
                    logger.info(
                        "   🚫 FILTERED UNKNOWN VOICE (PRIMARY RECENT - "
                        "preventing bleed-through): %s",
                        profile_id or "unknown",
                    )
                else:
                    # No primary activity - still filter unknown voices by default
                    # (they're not in scope)
                    should_filter = True
                    reason = "unknown_voice_not_in_scope"
                    confidence = 0.85
                    logger.debug(
                        "   🚫 FILTERED UNKNOWN VOICE (not in scope): %s", profile_id or "unknown"
                    )
            else:
                # No primary activity - still filter unknown voices by default
                # (they're not in scope)
                should_filter = True
                reason = "unknown_voice_not_in_scope"
                confidence = 0.85
                logger.debug(
                    "   🚫 FILTERED UNKNOWN VOICE (not in scope): %s", profile_id or "unknown"
                )
        else:
            # Not voice - use normal filtering logic
            should_filter, reason, confidence = self.profile_library.should_filter_audio(
                audio_features=audio_features, session_id=self.session_id, sound_type=sound_type
            )

        # Handle last_primary_activity check for unknown voices
        if not profile_id and self.last_primary_activity:
            time_since_primary = (datetime.now() - self.last_primary_activity).total_seconds()
            if time_since_primary < self.primary_speaker_timeout:
                should_filter = True
                reason = "unknown_voice_filtered_primary_recent"
                confidence = 0.9
                logger.info("   🚫 FILTERED UNKNOWN VOICE (PRIMARY RECENT - prevent interruption)")

        # Update statistics
        if should_filter:
            self.stats["filtered_out"] += 1
            if profile_id is None:
                self.stats["unknown_voices"] += 1
        else:
            self.stats["allowed_through"] += 1
            if profile_id:
                self.stats["known_voices"] += 1

        # Track voice interaction in workflow tracker
        if self.track_voice_interaction:
            try:
                self.track_voice_interaction(
                    filtered=should_filter, reason=reason, profile_id=profile_id
                )
            except (AttributeError, TypeError, ValueError):
                pass  # Don't break voice filtering if tracker fails

        # Apply dynamic adaptation
        adaptation_applied = False
        recognition_feedback = None
        pronunciation_suggestion = None

        if profile_id and not should_filter:
            # Record successful identification for learning
            self.profile_library.record_voice_sample(
                profile_id=profile_id,
                audio_features=audio_features,
                was_correct=True,
                effectiveness=confidence,
            )
            adaptation_applied = True

            # Provide feedback if confidence is low
            if self.provide_feedback and confidence < self.low_confidence_threshold:
                self.stats["low_confidence_detections"] += 1
                recognition_feedback = (
                    f"Recognized as {profile_id} with {confidence:.1%} confidence. "
                    f"Audio quality may be affecting recognition."
                )
                pronunciation_suggestion = self._generate_pronunciation_suggestion(
                    profile_id, confidence, audio_features
                )
                self.feedback_history.append(
                    {
                        "timestamp": datetime.now(),
                        "profile_id": profile_id,
                        "confidence": confidence,
                        "feedback": recognition_feedback,
                    }
                )
                # Keep only last 10 feedback entries
                if len(self.feedback_history) > 10:
                    self.feedback_history.pop(0)

        # Check for patterns in low confidence (might indicate pronunciation issues)
        if len(self.feedback_history) >= 3:
            recent_low = [
                f
                for f in self.feedback_history[-3:]
                if f["confidence"] < self.low_confidence_threshold
            ]
            if len(recent_low) >= 3:
                pronunciation_suggestion = (
                    "⚠️ Pattern detected: Multiple low-confidence detections. "
                    "Consider: speaking more clearly, reducing background noise, "
                    "or speaking slightly slower for better recognition."
                )
                self.stats["pronunciation_feedback_given"] += 1

        return FilterResult(
            should_process=not should_filter,
            should_filter=should_filter,
            reason=reason,
            confidence=confidence,
            profile_id=profile_id,
            confidence_level=confidence_level,
            adaptation_applied=adaptation_applied,
            recognition_feedback=recognition_feedback,
            pronunciation_suggestion=pronunciation_suggestion,
        )

    def add_voice_to_session(
        self, profile_id: str, name: str, audio_features: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Add a voice profile to current session scope

        @ADAPT: Adapts session scope to include new voice
        @IMPROVISE: Works with minimal profile data
        @OVERCOME: Handles profile conflicts and updates
        """
        if not self.enabled or self.profile_library is None:
            return False

        try:
            self.profile_library.add_voice_profile(
                profile_id=profile_id,
                name=name,
                session_id=self.session_id,
                voice_features=audio_features,
            )

            # Ensure in session scope
            scope = self.profile_library.session_scopes[self.session_id]
            scope.active_profiles.add(profile_id)
            # Access protected method for session scope management
            self.profile_library._save_session_scopes()  # pylint: disable=protected-access

            logger.info("   ✅ Added voice to session: %s (%s)", profile_id, name)
            return True
        except (AttributeError, KeyError, ValueError) as e:
            logger.error("   ❌ Failed to add voice: %s", e)
            return False

    def remove_voice_from_session(self, profile_id: str) -> bool:
        """Remove voice from current session scope"""
        if not self.enabled or self.profile_library is None:
            return False

        if self.session_id not in self.profile_library.session_scopes:
            return False

        scope = self.profile_library.session_scopes[self.session_id]
        if profile_id in scope.active_profiles:
            scope.active_profiles.remove(profile_id)
            # Access protected method for session scope management
            self.profile_library._save_session_scopes()  # pylint: disable=protected-access
            logger.info("   ✅ Removed voice from session: %s", profile_id)
            return True

        return False

    def set_session_strict_mode(self, strict: bool = True):
        """Set strict filtering mode for session"""
        if not self.enabled or self.profile_library is None:
            return

        if self.session_id in self.profile_library.session_scopes:
            scope = self.profile_library.session_scopes[self.session_id]
            scope.strict_mode = strict
            scope.last_updated = datetime.now().isoformat()
            # Access protected method for session scope management
            self.profile_library._save_session_scopes()  # pylint: disable=protected-access
            logger.info("   ✅ Set strict mode: %s", strict)

    def set_session_auto_learn(self, auto_learn: bool = True):
        """Set auto-learn mode for session"""
        if not self.enabled or self.profile_library is None:
            return

        if self.session_id in self.profile_library.session_scopes:
            scope = self.profile_library.session_scopes[self.session_id]
            scope.auto_learn = auto_learn
            scope.last_updated = datetime.now().isoformat()
            # Access protected method for session scope management
            self.profile_library._save_session_scopes()  # pylint: disable=protected-access
            logger.info("   ✅ Set auto-learn: %s", auto_learn)

    def invite_to_conversation(
        self, profile_id: str, duration_seconds: Optional[int] = None
    ) -> bool:
        """
        Explicitly invite a profile (wife, third party, etc.) to the conversation.
        When invited, their voice will be allowed through the filter.

        Args:
            profile_id: Profile ID to invite (e.g., "wife", "glenda", "third_party_1")
            duration_seconds: How long the invite lasts (default: 1 hour)

        Returns:
            True if invite was successful
        """
        if not profile_id:
            return False

        duration = duration_seconds or self.default_invite_duration
        expiry = datetime.now().timestamp() + duration

        self.invited_profiles.add(profile_id.lower())
        self.invite_expiry[profile_id.lower()] = expiry

        logger.info(
            "   ✅ INVITED TO CONVERSATION: %s (expires in %d seconds)", profile_id, duration
        )
        return True

    def revoke_invite(self, profile_id: str) -> bool:
        """
        Revoke an invitation - profile will be filtered again.

        Args:
            profile_id: Profile ID to revoke invite for

        Returns:
            True if revoke was successful
        """
        if not profile_id:
            return False

        profile_lower = profile_id.lower()
        if profile_lower in self.invited_profiles:
            self.invited_profiles.remove(profile_lower)
            if profile_lower in self.invite_expiry:
                del self.invite_expiry[profile_lower]
            logger.info("   🚫 REVOKED INVITE: %s (will be filtered again)", profile_id)
            return True

        return False

    def _is_invited(self, profile_id: str) -> bool:
        """
        Check if a profile is currently invited to the conversation.
        Also checks if invite has expired.

        Args:
            profile_id: Profile ID to check

        Returns:
            True if profile is invited and invite hasn't expired
        """
        if not profile_id:
            return False

        profile_lower = profile_id.lower()

        # Check if invited
        if profile_lower not in self.invited_profiles:
            return False

        # Check if expired
        if profile_lower in self.invite_expiry:
            expiry = self.invite_expiry[profile_lower]
            if datetime.now().timestamp() > expiry:
                # Expired - remove from invited set
                self.invited_profiles.remove(profile_lower)
                del self.invite_expiry[profile_lower]
                logger.debug("   ⏰ Invite expired for: %s", profile_id)
                return False

        return True

    def get_invited_profiles(self) -> List[str]:
        """
        Get list of currently invited profiles (not expired).

        Returns:
            List of profile IDs that are currently invited
        """
        # Clean up expired invites
        current_time = datetime.now().timestamp()
        expired = [pid for pid, expiry in self.invite_expiry.items() if current_time > expiry]
        for pid in expired:
            self.invited_profiles.discard(pid)
            del self.invite_expiry[pid]

        return list(self.invited_profiles)

    def _detect_greeting(self, transcription_text: str) -> Optional[str]:
        """
        Detect if transcription contains a greeting from wife or third party.
        Returns profile_id if greeting detected, None otherwise.

        Args:
            transcription_text: The transcribed text to check

        Returns:
            Profile ID if greeting detected (e.g., "wife"), None otherwise
        """
        if not transcription_text or not self.greeting_detection_enabled:
            return None

        text_lower = transcription_text.lower().strip()

        # Check if text contains a greeting pattern
        contains_greeting = any(
            greeting in text_lower[:100]  # Check first 100 chars
            for greeting in self.greeting_patterns
        )

        if not contains_greeting:
            return None

        # Check if this is from a tertiary speaker (wife, etc.)
        # We detect this by checking if the profile would be in tertiary_profile_ids
        # If it's a greeting, we assume it's from wife/glenda and invite them
        # The actual profile identification happens later, but we can detect
        # greetings from any tertiary speaker
        for profile_id in ["wife", "glenda"]:
            # If greeting detected, assume it's from wife/glenda and invite
            # The actual voice identification will confirm this later
            logger.info(
                "   👋 GREETING DETECTED (assuming %s): %s", profile_id, transcription_text[:50]
            )
            return profile_id  # Return first matching profile (wife takes priority)

        return None

    def _generate_butler_greeting(self, profile_id: str) -> str:
        """
        Generate a warm, professional, butler-style greeting.
        Follows @peak butler's standard for meeting someone for the first time.

        Args:
            profile_id: Profile ID of the person being greeted (e.g., "wife")

        Returns:
            Warm, professional greeting message
        """
        # Map profile IDs to appropriate names
        name_map = {"wife": "Madam", "glenda": "Glenda", "third_party": "Guest"}

        name = name_map.get(profile_id.lower(), "Guest")

        # Generate time-appropriate greeting
        from datetime import datetime

        hour = datetime.now().hour

        if 5 <= hour < 12:
            time_greeting = "Good morning"
        elif 12 <= hour < 17:
            time_greeting = "Good afternoon"
        elif 17 <= hour < 21:
            time_greeting = "Good evening"
        else:
            time_greeting = "Good evening"

        # Butler-style greetings (warm, professional, friendly)
        greetings = [
            f"{time_greeting}, {name}. It's a pleasure to have you join our conversation. How may I assist you today?",
            f"{time_greeting}, {name}. Welcome to our conversation. I'm here to help in any way I can.",
            f"{time_greeting}, {name}. It's wonderful to have you with us. Please feel free to join in whenever you'd like.",
            f"{time_greeting}, {name}. A warm welcome to you. I'm delighted you've joined us.",
        ]

        # Select greeting based on profile (consistent but varied)
        import hashlib

        profile_hash = int(hashlib.md5(profile_id.encode()).hexdigest(), 16)
        selected = greetings[profile_hash % len(greetings)]

        return selected

    def _ensure_glenda_registered_as_tertiary(self):
        """
        Ensure Glenda is registered as tertiary speaker (always filtered)
        Called during initialization to guarantee she's never in scope
        """
        if not self.enabled or self.profile_library is None:
            return

        # Add Glenda to tertiary profile IDs set
        for glenda_id in ["glenda", "wife", "wife_glenda", "glenda_wife"]:
            self.tertiary_profile_ids.add(glenda_id)

        logger.debug("   🚫 Glenda registered as tertiary (ALWAYS FILTERED)")

    def register_tertiary_speaker(
        self, profile_id: str, name: str, audio_features: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Register a tertiary speaker (e.g., Glenda, wife) that should be filtered
        ALWAYS - not just when primary is active. They're never in scope.

        @ADAPT: Adds tertiary speaker profile to system
        @IMPROVISE: Works with minimal profile data
        @OVERCOME: Handles profile conflicts
        """
        if not self.enabled or self.profile_library is None:
            return False

        try:
            # Add voice profile
            self.profile_library.add_voice_profile(
                profile_id=profile_id,
                name=name,
                session_id=self.session_id,
                voice_features=audio_features,
            )

            # DO NOT add to session scope active_profiles - tertiary speakers are filtered
            # They exist in the library for identification but are not in scope
            # Add to tertiary profile IDs set
            self.tertiary_profile_ids.add(profile_id.lower())
            if "glenda" in profile_id.lower() or "wife" in profile_id.lower():
                # Also add variations
                self.tertiary_profile_ids.add("glenda")
                self.tertiary_profile_ids.add("wife")
                self.tertiary_profile_ids.add("wife_glenda")

            logger.info("   ✅ Registered tertiary speaker: %s (%s)", profile_id, name)
            logger.info("   🚫 ALWAYS FILTERED - not in scope (this is OUR conversation)")
            return True
        except (AttributeError, KeyError, ValueError) as e:
            logger.error("   ❌ Failed to register tertiary speaker: %s", e)
            return False

    def get_speaker_status(self) -> Dict[str, Any]:
        """Get current speaker priority status"""
        return {
            "primary_speaker_id": self.primary_speaker_id,
            "secondary_speaker_id": self.secondary_speaker_id,
            "primary_speaker_active": self.primary_speaker_active,
            "last_primary_activity": (
                self.last_primary_activity.isoformat() if self.last_primary_activity else None
            ),
            "primary_speaker_timeout": self.primary_speaker_timeout,
            "hierarchy": "PRIMARY > SECONDARY > NO TERTIARY",
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get filtering statistics"""
        stats = self.stats.copy()

        if self.enabled and self.profile_library:
            session_stats = self.profile_library.get_session_statistics(self.session_id)
            stats["session"] = session_stats

        return stats

    def _learn_tertiary_audio(
        self,
        audio_features: Dict[str, Any],
        context: str,
        detected_profile_id: Optional[str] = None,
        audio_type: str = "voice",  # "voice", "tv", "background"
    ):
        """
        Silently learn tertiary audio (wife/Glenda/TV/background) in background

        Called whenever tertiary audio is detected, even when filtering.
        This allows us to train audio profiles continuously WITHOUT
        affecting workflow performance or filtering decisions.

        Learning happens silently - it doesn't interrupt OUR collaborative process.
        Tertiary audio is ALWAYS filtered out - this is just for better identification.

        Args:
            audio_features: Audio features to learn from
            context: Context of detection
            detected_profile_id: Detected profile ID
            audio_type: Type of audio ("voice", "tv", "background")
        """
        if not self.profile_library:
            return

        try:
            # Determine profile ID based on audio type
            if audio_type == "tv":
                profile_id_to_use = "tv_audio"
                profile_name = "TV Audio"
            elif audio_type == "background":
                profile_id_to_use = "background_audio"
                profile_name = "Background Audio"
            else:
                # Voice - use detected profile ID or default to "wife"
                profile_id_to_use = detected_profile_id or "wife"
                profile_name = "Glenda (Wife)"

                # Also check for Glenda variations
                if detected_profile_id and "glenda" in detected_profile_id.lower():
                    profile_id_to_use = "wife_glenda"  # Unified profile ID

            # Check if profile exists
            if profile_id_to_use not in self.profile_library.voice_profiles:
                # Create profile if it doesn't exist
                self.profile_library.add_voice_profile(
                    profile_id=profile_id_to_use, name=profile_name, voice_features=audio_features
                )
                logger.debug(
                    "   📚 Created %s profile (background learning, ALWAYS FILTERED)", profile_name
                )

            # Update profile with this audio sample
            audio_profile = self.profile_library.voice_profiles.get(profile_id_to_use)
            if audio_profile:
                # Merge audio features into profile
                if not audio_profile.voice_features:
                    audio_profile.voice_features = {}

                # Update features (merge/average with existing)
                for key, value in audio_features.items():
                    if key in audio_profile.voice_features:
                        # Average with existing (learning)
                        if isinstance(value, (int, float)) and isinstance(
                            audio_profile.voice_features[key], (int, float)
                        ):
                            # Weighted average (more weight to new samples as we learn)
                            # 30% new, 70% existing (conservative learning)
                            weight = 0.3
                            audio_profile.voice_features[key] = (
                                weight * value + (1 - weight) * audio_profile.voice_features[key]
                            )
                        else:
                            # Keep existing or update
                            audio_profile.voice_features[key] = value
                    else:
                        # New feature
                        audio_profile.voice_features[key] = value

                # Update profile stats
                audio_profile.sample_count += 1
                audio_profile.last_seen = datetime.now().isoformat()

                # Save updated profile (silently, in background)
                # Access protected method for profile persistence
                self.profile_library._save_profiles()  # pylint: disable=protected-access

                # Only log at debug level - don't interrupt workflow
                # Tertiary audio is being learned but ALWAYS filtered - never interrupts
                logger.debug(
                    "   📚 Learning %s (sample #%d, ALWAYS FILTERED: %s)",
                    profile_name,
                    audio_profile.sample_count,
                    context,
                )

        except (AttributeError, KeyError, ValueError) as e:
            logger.debug("   Could not learn tertiary audio: %s", e)

    def _detect_tv_audio(
        self, audio_features: Dict[str, Any], transcription_text: Optional[str] = None
    ) -> bool:
        """
        Detect if audio is from TV/television (AGGRESSIVE DETECTION)

        TV audio characteristics:
        - Consistent volume (not natural speech patterns)
        - Background music/sound effects
        - Multiple speakers (dialog)
        - Lower frequency content
        - Transcription might contain TV-related words
        - Continuous audio (not natural speech pauses)

        Args:
            audio_features: Extracted audio features
            transcription_text: Optional transcription text

        Returns:
            True if likely TV audio, False otherwise
        """
        # AGGRESSIVE TV DETECTION: Check transcription first (most reliable)
        if transcription_text:
            tv_indicators = [
                "tv",
                "television",
                "show",
                "episode",
                "commercial",
                "advertisement",
                "channel",
                "program",
                "series",
                "gospel",
                "matthew",
                "mark",
                "luke",
                "john",  # Religious content often on TV
                "reading",
                "holy",
                "according to",  # Religious phrases
                "news",
                "weather",
                "sports",
                "movie",
                "film",
                "broadcast",
                "live",
                "breaking",
                "coverage",
            ]
            text_lower = transcription_text.lower()
            # Check for TV-related phrases (more aggressive)
            tv_phrases = [
                "reading from",
                "according to",
                "holy gospel",
                "commercial break",
                "stay tuned",
                "coming up next",
            ]
            if any(indicator in text_lower for indicator in tv_indicators):
                logger.debug("   📺 TV audio detected via transcription keywords")
                return True
            if any(phrase in text_lower for phrase in tv_phrases):
                logger.debug("   📺 TV audio detected via transcription phrases")
                return True

        # Check audio features for TV characteristics (more sensitive thresholds)
        # TV audio often has:
        # - Lower std_amplitude (more consistent volume)
        # - Different frequency characteristics
        if "std_amplitude" in audio_features:
            std = audio_features["std_amplitude"]
            # TV audio tends to have lower variance (more consistent)
            # More aggressive: lower threshold
            if std < 0.2:  # Consistent volume (increased from 0.15)
                logger.debug("   📺 TV audio detected via consistent volume pattern")
                return True

        # Check for background music indicators (if available)
        if "mean_amplitude" in audio_features and "std_amplitude" in audio_features:
            mean = audio_features["mean_amplitude"]
            std = audio_features["std_amplitude"]
            # TV often has steady background with consistent levels
            # More aggressive thresholds
            if mean > 0.25 and std < 0.25:  # Moderate volume, low variance (more sensitive)
                logger.debug("   📺 TV audio detected via amplitude pattern")
                return True

        # Check duration - TV audio is often continuous
        if "duration" in audio_features:
            duration = audio_features.get("duration", 0)
            # TV audio often has longer continuous segments
            if duration > 5.0:  # Long continuous audio (likely TV)
                logger.debug("   📺 TV audio detected via long duration")
                return True

        return False

    def _generate_pronunciation_suggestion(
        self,
        profile_id: str,  # pylint: disable=unused-argument
        confidence: float,
        audio_features: Dict[str, Any],
    ) -> Optional[str]:
        """
        Generate pronunciation/recognition feedback to help sync better

        @ADAPT: Adapts feedback based on confidence and audio quality
        @IMPROVISE: Provides actionable suggestions
        @OVERCOME: Helps overcome recognition challenges
        """
        suggestions = []

        # Check audio quality indicators
        if "mean_amplitude" in audio_features:
            amplitude = audio_features["mean_amplitude"]
            if amplitude < 0.1:
                suggestions.append("Volume may be too low - try speaking louder")
            elif amplitude > 0.9:
                suggestions.append("Volume may be too high - try speaking softer")

        if "std_amplitude" in audio_features:
            std = audio_features["std_amplitude"]
            if std > 0.3:
                suggestions.append("Audio seems inconsistent - try steady pace")

        # Confidence-based suggestions
        if confidence < 0.5:
            suggestions.append("Low confidence - try: clearer enunciation, slower pace")
        elif confidence < 0.7:
            suggestions.append("Moderate confidence - speaking clearly helps")

        # Check for background noise (high std might indicate noise)
        if "std_amplitude" in audio_features and audio_features["std_amplitude"] > 0.25:
            suggestions.append("Background noise detected - quieter environment may help")

        if suggestions:
            return " | ".join(suggestions)
        return None

    def get_recognition_feedback(self) -> Dict[str, Any]:
        """
        Get recent recognition feedback to help sync better

        Returns feedback about what the system is hearing vs what was intended
        """
        if not self.feedback_history:
            return {"status": "no_feedback", "message": "No recent feedback available"}

        recent = self.feedback_history[-5:]  # Last 5 feedback entries
        avg_confidence = sum(f["confidence"] for f in recent) / len(recent)

        feedback = {
            "status": "feedback_available",
            "recent_detections": len(recent),
            "average_confidence": avg_confidence,
            "confidence_level": (
                "high" if avg_confidence >= 0.8 else "moderate" if avg_confidence >= 0.6 else "low"
            ),
            "suggestions": [],
        }

        if avg_confidence < 0.7:
            feedback["suggestions"].append(
                "Recognition confidence is below optimal. "
                "Consider: speaking more clearly, reducing background noise, "
                "or checking microphone positioning."
            )

        # Check for patterns
        low_conf_count = sum(1 for f in recent if f["confidence"] < 0.7)
        if low_conf_count >= 3:
            feedback["suggestions"].append(
                "Pattern detected: Multiple low-confidence recognitions. "
                "This might indicate pronunciation or audio quality issues."
            )

        return feedback

    def enable_feedback(self, enable: bool = True):
        """Enable or disable real-time recognition feedback"""
        self.provide_feedback = enable
        logger.info("   ✅ Recognition feedback: %s", "enabled" if enable else "disabled")

    def set_confidence_threshold(self, threshold: float):
        """Set confidence threshold for providing feedback (0.0-1.0)"""
        self.low_confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info("   ✅ Confidence threshold set to: %.2f", self.low_confidence_threshold)

    def evolve(self):
        """Evolve the filtering system based on usage"""
        if not self.enabled or self.profile_library is None:
            return

        self.profile_library.evolve_profiles()
        logger.info("   🔄 Evolved voice filter system")


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Filter System")
    parser.add_argument("--user-id", type=str, default="user", help="User ID")
    parser.add_argument("--session-id", type=str, help="Session ID")
    parser.add_argument(
        "--add-voice", type=str, nargs=2, metavar=("ID", "NAME"), help="Add voice to session"
    )
    parser.add_argument("--stats", action="store_true", help="Show statistics")
    parser.add_argument("--evolve", action="store_true", help="Evolve system")
    parser.add_argument("--feedback", action="store_true", help="Show recognition feedback")
    parser.add_argument("--enable-feedback", action="store_true", help="Enable real-time feedback")
    parser.add_argument(
        "--confidence-threshold", type=float, help="Set confidence threshold (0.0-1.0)"
    )
    parser.add_argument(
        "--invite",
        type=str,
        metavar="PROFILE_ID",
        help="Invite profile to conversation (e.g., 'wife', 'glenda')",
    )
    parser.add_argument(
        "--invite-duration",
        type=int,
        default=3600,
        help="Invite duration in seconds (default: 3600 = 1 hour)",
    )
    parser.add_argument(
        "--revoke-invite", type=str, metavar="PROFILE_ID", help="Revoke invitation for profile"
    )
    parser.add_argument(
        "--list-invited", action="store_true", help="List currently invited profiles"
    )

    args = parser.parse_args()

    system = VoiceFilterSystem(user_id=args.user_id, session_id=args.session_id)

    if args.add_voice:
        profile_id, name = args.add_voice
        system.add_voice_to_session(profile_id, name)

    if args.stats:
        stats = system.get_statistics()
        print(f"Total processed: {stats['total_processed']}")
        print(f"Filtered out: {stats['filtered_out']}")
        print(f"Allowed through: {stats['allowed_through']}")

    if args.enable_feedback:
        system.enable_feedback(True)
        print("✅ Real-time feedback enabled")

    if args.confidence_threshold is not None:
        system.set_confidence_threshold(args.confidence_threshold)
        print(f"✅ Confidence threshold set to {args.confidence_threshold}")

    if args.feedback:
        feedback = system.get_recognition_feedback()
        print("\n📊 Recognition Feedback:")
        print(f"Status: {feedback.get('status', 'unknown')}")
        if feedback.get("status") == "feedback_available":
            print(f"Recent detections: {feedback.get('recent_detections', 0)}")
            print(f"Average confidence: {feedback.get('average_confidence', 0):.1%}")
            print(f"Confidence level: {feedback.get('confidence_level', 'unknown')}")
            if feedback.get("suggestions"):
                print("\n💡 Suggestions:")
                for suggestion in feedback["suggestions"]:
                    print(f"  - {suggestion}")
        else:
            print(feedback.get("message", "No feedback available"))

    if args.evolve:
        system.evolve()
        print("✅ Evolved system")

    if args.invite:
        success = system.invite_to_conversation(
            profile_id=args.invite, duration_seconds=args.invite_duration
        )
        if success:
            print(f"✅ Invited {args.invite} to conversation (duration: {args.invite_duration}s)")
        else:
            print(f"❌ Failed to invite {args.invite}")

    if args.revoke_invite:
        success = system.revoke_invite(args.revoke_invite)
        if success:
            print(f"✅ Revoked invite for {args.revoke_invite}")
        else:
            print(f"❌ {args.revoke_invite} was not invited")

    if args.list_invited:
        invited = system.get_invited_profiles()
        if invited:
            print("\n📋 Currently Invited Profiles:")
            for profile_id in invited:
                expiry = system.invite_expiry.get(profile_id.lower(), 0)
                if expiry:
                    remaining = int(expiry - datetime.now().timestamp())
                    print(f"  - {profile_id} (expires in {remaining}s)")
                else:
                    print(f"  - {profile_id} (no expiry)")
        else:
            print("📋 No profiles currently invited")


if __name__ == "__main__":


    main()
if __name__ == "__main__":

    main()