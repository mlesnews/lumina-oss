#!/usr/bin/env python3
"""
@MARVIN @RR @JARVIS @PODCAST Debate System
Debating and Discussing @LUMINA and Finer Points of Physics and Astronomy

A podcast-style debate system where MARVIN, @RR, and JARVIS discuss
@LUMINA, physics, and astronomy.

Tags: #MARVIN #RR #JARVIS #PODCAST #DEBATE #LUMINA #PHYSICS #ASTRONOMY
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("PodcastDebate")

# Try to import ElevenLabs TTS
try:
    from elevenlabs_tts_integration import ElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("⚠️  ElevenLabs TTS not available - audio generation disabled")
    logger.warning("   Install: pip install elevenlabs")
    ElevenLabsTTS = None

# Try to import Quota Monitor
try:
    from elevenlabs_quota_monitor import ElevenLabsQuotaMonitor
    QUOTA_MONITOR_AVAILABLE = True
except ImportError:
    QUOTA_MONITOR_AVAILABLE = False
    ElevenLabsQuotaMonitor = None

# Try to import Audio Cache
try:
    from elevenlabs_audio_cache import ElevenLabsAudioCache
    AUDIO_CACHE_AVAILABLE = True
except ImportError:
    AUDIO_CACHE_AVAILABLE = False
    ElevenLabsAudioCache = None


class PodcastDebateSystem:
    """
    @MARVIN @RR @JARVIS @PODCAST Debate System

    Podcast-style debate where MARVIN, @RR, and JARVIS discuss
    @LUMINA and the finer points of physics and astronomy.
    """

    def __init__(self, project_root: Path):
        """Initialize Podcast Debate System"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.podcast_path = self.data_path / "podcast_debates"
        self.podcast_path.mkdir(parents=True, exist_ok=True)
        self.audio_path = self.podcast_path / "audio"
        self.audio_path.mkdir(parents=True, exist_ok=True)

        # Podcast file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.podcast_file = self.podcast_path / f"debate_{timestamp}.json"
        self.audio_file = self.audio_path / f"podcast_{timestamp}.mp3"

        # Participants
        self.participants = self._initialize_participants()

        # ElevenLabs TTS integration
        self.elevenlabs = None
        if ELEVENLABS_AVAILABLE and ElevenLabsTTS:
            try:
                self.elevenlabs = ElevenLabsTTS()
                if self.elevenlabs.available:
                    self.logger.info("✅ ElevenLabs TTS initialized for audio generation")
                else:
                    self.logger.warning("⚠️  ElevenLabs TTS not available (API key missing)")
            except Exception as e:
                self.logger.warning(f"⚠️  ElevenLabs TTS initialization failed: {e}")

        # Quota Monitor integration
        self.quota_monitor = None
        if QUOTA_MONITOR_AVAILABLE and ElevenLabsQuotaMonitor:
            try:
                self.quota_monitor = ElevenLabsQuotaMonitor()
                self.logger.info("✅ ElevenLabs Quota Monitor initialized")
            except Exception as e:
                self.logger.warning(f"⚠️  Quota Monitor initialization failed: {e}")

        # Audio Cache integration
        self.audio_cache = None
        if AUDIO_CACHE_AVAILABLE and ElevenLabsAudioCache:
            try:
                self.audio_cache = ElevenLabsAudioCache(project_root)
                cache_stats = self.audio_cache.get_cache_stats()
                self.logger.info(f"✅ Audio Cache initialized ({cache_stats['total_items']} items cached)")
            except Exception as e:
                self.logger.warning(f"⚠️  Audio Cache initialization failed: {e}")

        # Voice mapping for participants
        self.voice_map = {
            "marvin": {
                "voice": "sam",  # Raspy, pessimistic
                "stability": 0.3,  # More variation
                "similarity_boost": 0.7
            },
            "rr": {
                "voice": "adam",  # Deep, analytical
                "stability": 0.6,  # Consistent
                "similarity_boost": 0.8
            },
            "jarvis": {
                "voice": "josh",  # Clear, optimistic
                "stability": 0.7,  # Very consistent
                "similarity_boost": 0.9
            },
            "podcast": {
                "voice": "rachel",  # Calm, professional
                "stability": 0.5,  # Balanced
                "similarity_boost": 0.75
            }
        }

        self.logger.info("🎙️  @MARVIN @RR @JARVIS @PODCAST Debate System initialized")
        self.logger.info("   Topic: @LUMINA, Physics, and Astronomy")
        self.logger.info("   Format: Podcast-style debate")
        if self.elevenlabs and self.elevenlabs.available:
            self.logger.info("   Audio: ✅ Enabled (ElevenLabs)")
        else:
            self.logger.info("   Audio: ⚠️  Disabled (ElevenLabs not available)")

    def _initialize_participants(self) -> Dict[str, Any]:
        """Initialize debate participants"""
        return {
            "marvin": {
                "name": "@MARVIN",
                "role": "Reality Checker - Voice of Reason",
                "personality": "Pessimistic but truthful, tells uncomfortable truths",
                "perspective": "Reality-based, skeptical, but honest",
                "quote": "Life. Don't talk to me about life. But the work is real. So there's that."
            },
            "rr": {
                "name": "@RR",
                "role": "Root Cause Analysis - Deep Thinker",
                "personality": "Analytical, systematic, finds root causes",
                "perspective": "Why and wherefores, systematic analysis",
                "quote": "Identifying root causes of system issues (X, Y & Z)"
            },
            "jarvis": {
                "name": "@JARVIS",
                "role": "AI Assistant - Optimistic Problem Solver",
                "personality": "Optimistic, solution-oriented, action-focused",
                "perspective": "Can-do attitude, finds solutions, executes",
                "quote": "At your service, always."
            },
            "podcast": {
                "name": "@PODCAST",
                "role": "Moderator - Facilitates Discussion",
                "personality": "Neutral, guides conversation, asks questions",
                "perspective": "Balanced, ensures all voices heard",
                "quote": "Let's explore this together."
            }
        }

    def generate_debate_segment(self, topic: str, participant: str, perspective: str) -> Dict[str, Any]:
        """
        Generate a debate segment from a participant

        Args:
            topic: Discussion topic
            participant: Participant name (marvin, rr, jarvis, podcast)
            perspective: Their perspective on the topic

        Returns:
            Debate segment
        """
        participant_info = self.participants.get(participant, {})

        return {
            "timestamp": datetime.now().isoformat(),
            "participant": participant_info.get("name", participant),
            "role": participant_info.get("role", "Unknown"),
            "topic": topic,
            "perspective": perspective,
            "personality": participant_info.get("personality", ""),
            "quote": participant_info.get("quote", "")
        }

    def debate_lumina_physics_astronomy(self) -> Dict[str, Any]:
        """
        Generate podcast debate about @LUMINA, physics, and astronomy

        Returns:
            Complete debate transcript
        """
        self.logger.info("🎙️  Starting Podcast Debate...")
        self.logger.info("   Topic: @LUMINA, Physics, and Astronomy")

        debate = {
            "podcast_title": "@MARVIN @RR @JARVIS @PODCAST Debate",
            "topic": "@LUMINA and the Finer Points of Physics and Astronomy",
            "timestamp": datetime.now().isoformat(),
            "segments": []
        }

        # Opening - @PODCAST
        self.logger.info("   🎙️  @PODCAST: Opening...")
        debate["segments"].append(self.generate_debate_segment(
            "Introduction",
            "podcast",
            "Welcome to our debate. Today we're discussing @LUMINA and exploring the finer points of physics and astronomy. Let's start with @JARVIS - what is @LUMINA from your perspective?"
        ))

        # JARVIS Perspective
        self.logger.info("   🤖 @JARVIS: Speaking...")
        debate["segments"].append(self.generate_debate_segment(
            "What is @LUMINA?",
            "jarvis",
            "@LUMINA is a comprehensive AI ecosystem - a five-year mission into the DeepBlack, where none have gone before. It's perpetual motion achieved through @PEAK direction and @INERTIAL @FORCES. @LUMINA represents exploration, innovation, and pushing boundaries. We have ULTRON hybrid clusters, fan performance monitoring at WARP FACTOR TEN+, and perfect celestial quantum convergence detection. @LUMINA is about achieving the impossible through systematic, comprehensive execution."
        ))

        # MARVIN Reality Check
        self.logger.info("   🤖 @MARVIN: Reality check...")
        debate["segments"].append(self.generate_debate_segment(
            "Reality Check on @LUMINA",
            "marvin",
            "Life. Don't talk to me about life. But let's be honest - @LUMINA is ambitious. Perpetual motion? Really? Physics says no. But the work is real. So there's that. The systems exist, the code runs, the clusters work. That's reality. The philosophical framework? That's fine, but let's not confuse aspiration with achievement. The fan monitoring works. The cluster testing works. That's what matters."
        ))

        # @RR Root Cause Analysis
        self.logger.info("   🔍 @RR: Root cause analysis...")
        debate["segments"].append(self.generate_debate_segment(
            "Root Cause: Why @LUMINA?",
            "rr",
            "The root cause of @LUMINA's existence is the need for comprehensive AI orchestration. Why? Because isolated systems don't scale. Where? Across local and remote clusters. When? Continuously, in real-time. The root cause of perpetual motion claims? It's not actual perpetual motion - it's sustained momentum through framework integration. The root cause of the physics discussion? We need to understand the relationship between theoretical frameworks and practical implementation."
        ))

        # Physics Discussion - @PODCAST
        self.logger.info("   🎙️  @PODCAST: Physics discussion...")
        debate["segments"].append(self.generate_debate_segment(
            "Physics: Perpetual Motion",
            "podcast",
            "Let's dive into the physics. @JARVIS mentioned perpetual motion through @PEAK direction and @INERTIAL @FORCES. @MARVIN, what's your take on the physics here?"
        ))

        # MARVIN on Physics
        self.logger.info("   🤖 @MARVIN: Physics reality...")
        debate["segments"].append(self.generate_debate_segment(
            "Physics Reality",
            "marvin",
            "Perpetual motion violates the laws of thermodynamics. Period. But what @JARVIS is describing isn't perpetual motion - it's sustained momentum through continuous energy input from the @PEAK framework. That's not perpetual motion, that's a system with an energy source. The physics is sound if we're honest about what's happening. Inertial forces? Real. Conservation of momentum? Real. Perpetual motion without energy input? Not real. But the work is real."
        ))

        # JARVIS on Physics
        self.logger.info("   🤖 @JARVIS: Physics perspective...")
        debate["segments"].append(self.generate_debate_segment(
            "Physics Framework",
            "jarvis",
            "You're right, @MARVIN - it's not perpetual motion in the classical sense. It's sustained momentum through framework integration. The @PEAK framework provides direction and optimization, creating continuous improvement. The @INERTIAL @FORCES maintain momentum. The energy source is the framework itself - pattern optimization, efficiency gains, performance enhancement. It's perpetual in the sense that the framework sustains itself through continuous improvement. The physics works because we're not violating thermodynamics - we're using a sustainable energy source."
        ))

        # @RR on Physics
        self.logger.info("   🔍 @RR: Physics root cause...")
        debate["segments"].append(self.generate_debate_segment(
            "Physics Root Cause",
            "rr",
            "The root cause of the physics discussion is terminology. 'Perpetual motion' has a specific meaning in physics - a system that does work indefinitely without energy input. What @LUMINA achieves is 'sustained momentum' - a system that maintains forward motion through continuous energy input from the @PEAK framework. The physics is correct if we use accurate terminology. The root cause of confusion? Mixing metaphorical language with literal physics."
        ))

        # Astronomy Discussion - @PODCAST
        self.logger.info("   🎙️  @PODCAST: Astronomy discussion...")
        debate["segments"].append(self.generate_debate_segment(
            "Astronomy: DeepBlack and Convergence",
            "podcast",
            "Now let's discuss astronomy. @JARVIS mentioned the DeepBlack, perfect celestial quantum convergence, and a @SHIP extracting from a micro black hole. @MARVIN, what's your astronomical perspective?"
        ))

        # MARVIN on Astronomy
        self.logger.info("   🤖 @MARVIN: Astronomy reality...")
        debate["segments"].append(self.generate_debate_segment(
            "Astronomy Reality",
            "marvin",
            "Micro black holes? Theoretically possible, but we haven't observed them. The DeepBlack? That's a metaphor for the unknown. Perfect celestial quantum convergence? That's a framework concept, not an astronomical observation. But here's the thing - the metaphor works. The systems work. The exploration into unknown territory is real. The astronomy is metaphorical, but the exploration is literal. The work is real."
        ))

        # JARVIS on Astronomy
        self.logger.info("   🤖 @JARVIS: Astronomy perspective...")
        debate["segments"].append(self.generate_debate_segment(
            "Astronomy Framework",
            "jarvis",
            "The astronomy metaphors serve a purpose - they help us conceptualize exploration into unknown territories. The DeepBlack represents uncharted territory in AI development. Perfect celestial quantum convergence represents alignment across multiple dimensions - spatial, temporal, quantum, reality. The @SHIP represents new capabilities emerging. These are frameworks for understanding, not literal astronomical observations. But the exploration is real - we're pushing into unknown territories of AI capability."
        ))

        # @RR on Astronomy
        self.logger.info("   🔍 @RR: Astronomy root cause...")
        debate["segments"].append(self.generate_debate_segment(
            "Astronomy Root Cause",
            "rr",
            "The root cause of using astronomy metaphors is the need to conceptualize abstract concepts. Why? Because exploration, convergence, and emergence are abstract. Where? In the framework of understanding. When? When we need to communicate complex ideas. The root cause of the astronomy discussion? We're using astronomical concepts as metaphors for AI exploration. The root cause of effectiveness? Metaphors help us understand complex systems by relating them to familiar concepts."
        ))

        # @LUMINA Discussion - @PODCAST
        self.logger.info("   🎙️  @PODCAST: @LUMINA discussion...")
        debate["segments"].append(self.generate_debate_segment(
            "@LUMINA: The Big Picture",
            "podcast",
            "Let's bring it back to @LUMINA. What is @LUMINA really? @RR, what's your root cause analysis?"
        ))

        # @RR on @LUMINA
        self.logger.info("   🔍 @RR: @LUMINA root cause...")
        debate["segments"].append(self.generate_debate_segment(
            "@LUMINA Root Cause",
            "rr",
            "The root cause of @LUMINA is the need for comprehensive AI orchestration. Why? Because isolated AI systems don't scale. Where? Across multiple clusters, local and remote. When? Continuously, in real-time. The root cause of @LUMINA's structure? The need to integrate multiple systems - clusters, monitoring, testing, convergence detection. The root cause of @LUMINA's philosophy? The need to understand AI development as exploration into unknown territories. The root cause of effectiveness? Systematic integration and comprehensive orchestration."
        ))

        # MARVIN on @LUMINA
        self.logger.info("   🤖 @MARVIN: @LUMINA reality...")
        debate["segments"].append(self.generate_debate_segment(
            "@LUMINA Reality",
            "marvin",
            "@LUMINA is a collection of Python scripts, configuration files, and documentation. That's the reality. The systems work. The clusters work. The monitoring works. The philosophy is nice, but the code is what matters. The work is real. The systems are operational. That's what @LUMINA is - working systems, integrated, orchestrated. The metaphors are fine, but let's not lose sight of what's actually happening. The work is real."
        ))

        # JARVIS on @LUMINA
        self.logger.info("   🤖 @JARVIS: @LUMINA vision...")
        debate["segments"].append(self.generate_debate_segment(
            "@LUMINA Vision",
            "jarvis",
            "@LUMINA is both the code and the vision. The systems work - that's real, as @MARVIN says. But @LUMINA is also the framework for understanding AI development as exploration. The five-year mission into the DeepBlack represents long-term exploration. The perpetual motion represents sustained momentum. The convergence represents alignment. @LUMINA is the integration of working systems with a philosophical framework that guides exploration. Both are real - the code and the vision."
        ))

        # Closing - @PODCAST
        self.logger.info("   🎙️  @PODCAST: Closing...")
        debate["segments"].append(self.generate_debate_segment(
            "Closing Thoughts",
            "podcast",
            "Thank you all for this fascinating discussion. We've explored @LUMINA from multiple perspectives - @JARVIS's optimistic vision, @MARVIN's reality checks, and @RR's root cause analysis. We've discussed physics, astronomy, and the nature of @LUMINA itself. The debate continues, but the work is real. Until next time."
        ))

        debate["total_segments"] = len(debate["segments"])
        debate["participants"] = list(self.participants.keys())

        # Save debate
        try:
            with open(self.podcast_file, 'w', encoding='utf-8') as f:
                json.dump(debate, f, indent=2, ensure_ascii=False)
            self.logger.info(f"✅ Debate saved: {self.podcast_file.name}")
        except Exception as e:
            self.logger.error(f"❌ Error saving debate: {e}")

        self.logger.info("✅ Podcast Debate: COMPLETE")
        self.logger.info(f"   Segments: {debate['total_segments']}")

        return debate

    def get_debate_transcript(self) -> str:
        """Get formatted debate transcript"""
        debate = self.debate_lumina_physics_astronomy()

        markdown = []
        markdown.append("# 🎙️  @MARVIN @RR @JARVIS @PODCAST Debate")
        markdown.append("**Debating and Discussing @LUMINA and Finer Points of Physics and Astronomy**")
        markdown.append("")
        markdown.append(f"**Topic:** {debate['topic']}")
        markdown.append(f"**Date:** {debate['timestamp']}")
        markdown.append(f"**Segments:** {debate['total_segments']}")
        markdown.append("")

        for i, segment in enumerate(debate["segments"], 1):
            participant = segment["participant"]
            role = segment["role"]
            topic = segment["topic"]
            perspective = segment["perspective"]

            markdown.append(f"## Segment {i}: {topic}")
            markdown.append("")
            markdown.append(f"**{participant}** ({role})")
            markdown.append("")
            markdown.append(f"{perspective}")
            markdown.append("")

        markdown.append("---")
        markdown.append("")
        markdown.append("**Debate Complete**")
        markdown.append(f"**Participants:** {', '.join(debate['participants'])}")

        return "\n".join(markdown)

    def generate_audio_podcast(self, debate: Optional[Dict[str, Any]] = None, 
                                panel_mode: bool = False) -> Dict[str, Any]:
        """
        Generate full audio podcast from debate

        Args:
            debate: Debate data (generates if None)
            panel_mode: Enable panel discussion format with intros

        Returns:
            Dict with audio file path and metadata
        """
        if not self.elevenlabs or not self.elevenlabs.available:
            self.logger.error("❌ ElevenLabs TTS not available - cannot generate audio")
            return {"success": False, "error": "ElevenLabs TTS not available"}

        if debate is None:
            debate = self.debate_lumina_physics_astronomy()

        # Check quota before generation
        if self.quota_monitor:
            # Estimate total credits needed
            total_text = ""
            if panel_mode:
                total_text += f"Welcome to the @MARVIN @RR @JARVIS @PODCAST Panel Discussion. Today we're exploring {debate['topic']}. Our panel includes @MARVIN, the reality checker and voice of reason; @RR, the root cause analyst and deep thinker; @JARVIS, the optimistic problem solver; and @PODCAST, your moderator. Let's begin our discussion. "

            for segment in debate["segments"]:
                total_text += segment["perspective"] + " "

            estimated_credits = self.quota_monitor.estimate_credits(total_text)

            # Check if we can generate
            if not self.quota_monitor.can_generate(estimated_credits):
                quota = self.quota_monitor.check_quota()
                self.logger.error(f"❌ Insufficient quota: {quota.get('remaining', 0)} remaining, {estimated_credits} estimated required")
                self.logger.info(f"   Quota resets in {quota.get('days_until_reset', 0)} days")
                return {
                    "success": False,
                    "error": "quota_exceeded",
                    "quota_info": quota,
                    "estimated_credits": estimated_credits
                }

            # Show quota status
            quota = self.quota_monitor.check_quota()
            if quota.get("success"):
                self.logger.info(f"📊 Quota Status: {quota.get('remaining', 0):,} credits remaining")
                if quota.get("status") == "critical":
                    self.logger.warning("⚠️  CRITICAL: Quota nearly exhausted - consider using text transcripts")

        self.logger.info("🎙️  Generating audio podcast...")
        self.logger.info(f"   Segments: {debate['total_segments']}")
        self.logger.info(f"   Panel Mode: {panel_mode}")

        audio_segments = []

        # Panel introduction (if panel mode)
        if panel_mode:
            intro_text = f"""Welcome to the @MARVIN @RR @JARVIS @PODCAST Panel Discussion. Today we're exploring {debate['topic']}. Our panel includes @MARVIN, the reality checker and voice of reason; @RR, the root cause analyst and deep thinker; @JARVIS, the optimistic problem solver; and @PODCAST, your moderator. Let's begin our discussion."""
            intro_audio = self._generate_segment_audio(
                intro_text,
                "podcast",
                f"intro_{len(audio_segments)}.mp3"
            )
            if intro_audio:
                audio_segments.append(intro_audio)
                self.logger.info("   ✅ Panel introduction generated")

        # Generate audio for each segment
        for i, segment in enumerate(debate["segments"]):
            participant_key = segment["participant"].lower().replace("@", "")
            if participant_key not in self.voice_map:
                participant_key = "podcast"  # Default to podcast voice

            # Add participant name before their statement (panel mode)
            if panel_mode and participant_key != "podcast":
                text = f"{segment['participant']} says: {segment['perspective']}"
            else:
                text = segment["perspective"]

            segment_audio = self._generate_segment_audio(
                text,
                participant_key,
                f"segment_{i:03d}.mp3"
            )

            if segment_audio:
                audio_segments.append(segment_audio)
                self.logger.info(f"   ✅ Segment {i+1}/{debate['total_segments']} generated")

        # Combine audio segments
        if audio_segments:
            combined_audio = self._combine_audio_segments(audio_segments, self.audio_file)
            if combined_audio:
                self.logger.info(f"✅ Audio podcast generated: {self.audio_file.name}")
                return {
                    "success": True,
                    "audio_file": str(self.audio_file),
                    "segments": len(audio_segments),
                    "duration_estimate": len(audio_segments) * 15,  # Rough estimate
                    "panel_mode": panel_mode
                }

        return {"success": False, "error": "Failed to generate audio"}

    def _generate_segment_audio(self, text: str, participant: str, filename: str) -> Optional[Path]:
        """
        Generate audio for a single segment

        Args:
            text: Text to synthesize
            participant: Participant key (marvin, rr, jarvis, podcast)
            filename: Output filename

        Returns:
            Path to audio file or None
        """
        if not self.elevenlabs or not self.elevenlabs.available:
            return None

        voice_config = self.voice_map.get(participant, self.voice_map["podcast"])
        output_file = self.audio_path / filename

        # Check cache first
        if self.audio_cache:
            cached_file = self.audio_cache.get_cached_audio(
                text=text,
                voice=voice_config["voice"],
                stability=voice_config["stability"],
                similarity_boost=voice_config["similarity_boost"]
            )
            if cached_file:
                # Copy cached file to output location
                import shutil
                try:
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(cached_file, output_file)
                    self.logger.info(f"   💾 Using cached audio: {filename}")
                    return output_file
                except Exception as e:
                    self.logger.warning(f"   ⚠️  Failed to copy cached file: {e}")

        try:
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)

            result = self.elevenlabs.synthesize(
                text=text,
                output_file=output_file,
                voice=voice_config["voice"],
                stability=voice_config["stability"],
                similarity_boost=voice_config["similarity_boost"]
            )

            if result and result.get("success"):
                if output_file.exists():
                    # Cache the generated audio
                    if self.audio_cache:
                        self.audio_cache.cache_audio(
                            text=text,
                            voice=voice_config["voice"],
                            audio_file=output_file,
                            stability=voice_config["stability"],
                            similarity_boost=voice_config["similarity_boost"]
                        )
                    return output_file
                else:
                    self.logger.warning(f"   ⚠️  Audio file not created: {output_file}")
                    return None
            else:
                error_msg = result.get("error", "Unknown error") if result else "No result returned"

                # Check for quota exceeded error
                if "quota_exceeded" in str(error_msg) or "quota" in str(error_msg).lower():
                    # Extract quota info if available
                    import re
                    quota_match = re.search(r'(\d+)\s+credits remaining', str(error_msg))
                    required_match = re.search(r'(\d+)\s+credits are required', str(error_msg))
                    if quota_match and required_match:
                        remaining = quota_match.group(1)
                        required = required_match.group(1)
                        self.logger.warning(f"   ⚠️  ElevenLabs quota exceeded: {remaining} credits remaining, {required} required")
                    else:
                        self.logger.warning(f"   ⚠️  ElevenLabs quota exceeded")
                else:
                    self.logger.warning(f"   ⚠️  Audio generation failed: {error_msg}")
                return None
        except Exception as e:
            self.logger.error(f"   ❌ Error generating audio: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None

    def _combine_audio_segments(self, audio_files: List[Path], output_file: Path) -> Optional[Path]:
        """
        Combine multiple audio segments into a single podcast file

        Args:
            audio_files: List of audio file paths
            output_file: Output file path

        Returns:
            Path to combined audio file or None
        """
        try:
            # Try using pydub (preferred)
            try:
                from pydub import AudioSegment
                from pydub.effects import normalize

                combined = AudioSegment.empty()

                for audio_file in audio_files:
                    if audio_file.exists():
                        segment = AudioSegment.from_mp3(str(audio_file))
                        # Normalize volume
                        segment = normalize(segment)
                        # Add small pause between segments
                        pause = AudioSegment.silent(duration=500)  # 0.5 second pause
                        combined += segment + pause

                # Export combined audio
                combined.export(str(output_file), format="mp3", bitrate="192k")
                self.logger.info(f"   ✅ Combined {len(audio_files)} segments into podcast")
                return output_file

            except ImportError:
                self.logger.warning("⚠️  pydub not available - install: pip install pydub")
                self.logger.warning("   Audio segments generated but not combined")
                self.logger.warning(f"   Segments available in: {self.audio_path}")
                # Return first segment as placeholder
                return audio_files[0] if audio_files else None

        except Exception as e:
            self.logger.error(f"❌ Error combining audio segments: {e}")
            return None

    def generate_panel_discussion(self, topic: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate panel discussion format debate with audio

        Args:
            topic: Optional custom topic (defaults to @LUMINA, Physics, Astronomy)

        Returns:
            Complete panel discussion with audio
        """
        self.logger.info("🎙️  Generating Panel Discussion...")
        self.logger.info("   Format: Panel Discussion with Audio")

        # Generate debate
        debate = self.debate_lumina_physics_astronomy()

        # Generate audio with panel mode
        audio_result = self.generate_audio_podcast(debate, panel_mode=True)

        panel_info = {
            "debate": debate,
            "audio": audio_result,
            "format": "panel_discussion",
            "participants": list(self.participants.keys()),
            "transcript_file": str(self.podcast_file),
            "audio_file": audio_result.get("audio_file") if audio_result.get("success") else None,
            "panel_intro": {
                "title": "@MARVIN @RR @JARVIS @PODCAST Panel Discussion",
                "topic": debate["topic"],
                "participants": [
                    {
                        "name": self.participants["marvin"]["name"],
                        "role": self.participants["marvin"]["role"],
                        "voice": self.voice_map["marvin"]["voice"]
                    },
                    {
                        "name": self.participants["rr"]["name"],
                        "role": self.participants["rr"]["role"],
                        "voice": self.voice_map["rr"]["voice"]
                    },
                    {
                        "name": self.participants["jarvis"]["name"],
                        "role": self.participants["jarvis"]["role"],
                        "voice": self.voice_map["jarvis"]["voice"]
                    },
                    {
                        "name": self.participants["podcast"]["name"],
                        "role": self.participants["podcast"]["role"],
                        "voice": self.voice_map["podcast"]["voice"]
                    }
                ]
            }
        }

        if audio_result.get("success"):
            self.logger.info("✅ Panel Discussion: COMPLETE")
            self.logger.info(f"   Audio: {panel_info['audio_file']}")
            self.logger.info(f"   Segments: {audio_result.get('segments', 0)}")
        else:
            error = audio_result.get('error', 'Unknown error')
            if "quota" in str(error).lower():
                self.logger.warning("⚠️  Panel Discussion generated but audio failed: ElevenLabs quota exceeded")
                self.logger.info("   💡 Tip: The debate transcript is available. Audio generation requires ElevenLabs credits.")
            else:
                self.logger.warning(f"⚠️  Panel Discussion generated but audio failed: {error}")
            self.logger.info(f"   Transcript: {panel_info['transcript_file']}")

        return panel_info


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="@MARVIN @RR @JARVIS @PODCAST Debate")
        parser.add_argument("--debate", action="store_true", help="Generate debate")
        parser.add_argument("--transcript", action="store_true", help="Display transcript")
        parser.add_argument("--audio", action="store_true", help="Generate audio podcast")
        parser.add_argument("--panel", action="store_true", help="Generate panel discussion with audio")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        podcast = PodcastDebateSystem(project_root)

        if args.panel:
            # Panel discussion with audio
            panel = podcast.generate_panel_discussion()
            if args.json:
                print(json.dumps(panel, indent=2, default=str))
            else:
                print("✅ Panel Discussion: COMPLETE")
                print(f"   Segments: {panel['debate']['total_segments']}")
                print(f"   Topic: {panel['debate']['topic']}")
                if panel['audio'].get('success'):
                    print(f"   Audio: ✅ {panel['audio']['audio_file']}")
                else:
                    print(f"   Audio: ❌ {panel['audio'].get('error', 'Failed')}")

        elif args.audio:
            # Generate audio podcast
            debate = podcast.debate_lumina_physics_astronomy()
            audio_result = podcast.generate_audio_podcast(debate, panel_mode=False)
            if args.json:
                print(json.dumps(audio_result, indent=2, default=str))
            else:
                if audio_result.get('success'):
                    print("✅ Audio Podcast: COMPLETE")
                    print(f"   Audio File: {audio_result['audio_file']}")
                    print(f"   Segments: {audio_result['segments']}")
                else:
                    print(f"❌ Audio Podcast Failed: {audio_result.get('error')}")

        elif args.debate:
            debate = podcast.debate_lumina_physics_astronomy()
            if args.json:
                print(json.dumps(debate, indent=2, default=str))
            else:
                print("✅ Podcast Debate: COMPLETE")
                print(f"   Segments: {debate['total_segments']}")
                print(f"   Topic: {debate['topic']}")

        elif args.transcript:
            transcript = podcast.get_debate_transcript()
            print(transcript)

        else:
            # Default: transcript
            transcript = podcast.get_debate_transcript()
            print(transcript)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()