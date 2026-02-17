#!/usr/bin/env python3
"""
Voice Profile Library System - @EVO @ADAPT @IMPROVISE @OVERCOME

Dynamic, evolutionary voice and sound profile system that:
- Builds profile libraries with confidence levels
- Automatically filters unknown voices/sounds not in session scope
- Dynamically scales and adapts everywhere
- Applies core values: Adapt, Improvise, Overcome
- Eliminates all static areas - everything evolves

Tags: #VOICE_PROFILE #DYNAMIC_SCALING #EVO #ADAPT #IMPROVISE #OVERCOME @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict
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

logger = get_logger("VoiceProfileLibrary")


class ConfidenceLevel(Enum):
    """Confidence levels for voice/sound recognition"""
    UNKNOWN = 0.0  # Unknown - filter out
    LOW = 0.3  # Low confidence - filter out
    MEDIUM = 0.6  # Medium confidence - may filter
    HIGH = 0.8  # High confidence - include
    CERTAIN = 0.95  # Certain - always include


class SoundType(Enum):
    """Types of sounds to profile"""
    VOICE = "voice"
    BACKGROUND_NOISE = "background_noise"
    SYSTEM_SOUND = "system_sound"
    MUSIC = "music"
    UNKNOWN = "unknown"


@dataclass
class VoiceProfile:
    """Dynamic voice profile with evolutionary learning"""
    profile_id: str
    name: str
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    voice_features: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.7  # Dynamic - evolves
    sample_count: int = 0
    last_seen: str = ""
    success_rate: float = 0.0
    false_positive_rate: float = 0.0
    false_negative_rate: float = 0.0
    effectiveness_history: List[float] = field(default_factory=list)
    evolution_metadata: Dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    is_in_scope: bool = True  # Session scope
    adaptation_level: float = 1.0  # Dynamic scaling factor


@dataclass
class SoundProfile:
    """Dynamic sound profile for non-voice sounds"""
    profile_id: str
    sound_type: SoundType
    name: str
    features: Dict[str, Any] = field(default_factory=dict)
    confidence_threshold: float = 0.6  # Dynamic - evolves
    sample_count: int = 0
    last_seen: str = ""
    filter_out: bool = True  # Whether to filter this sound
    effectiveness_history: List[float] = field(default_factory=list)
    evolution_metadata: Dict[str, Any] = field(default_factory=dict)
    adaptation_level: float = 1.0  # Dynamic scaling factor


@dataclass
class SessionScope:
    """Session scope for voice/sound filtering"""
    session_id: str
    active_profiles: Set[str] = field(default_factory=set)
    allowed_sound_types: Set[SoundType] = field(default_factory=lambda: {SoundType.VOICE})
    confidence_floor: float = 0.7  # Dynamic - adapts
    auto_learn: bool = True  # Auto-learn new voices in session
    strict_mode: bool = False  # Strict filtering (no unknowns)
    created_at: str = ""
    last_updated: str = ""


class VoiceProfileLibrarySystem:
    """
    Voice Profile Library System - @EVO @ADAPT @IMPROVISE @OVERCOME

    Core Values:
    - Adapt: System adapts to new voices, conditions, contexts
    - Improvise: System improvises when profiles incomplete or uncertain
    - Overcome: System overcomes filtering challenges, learns from mistakes

    Principles:
    - No static areas - everything evolves
    - Dynamic scaling everywhere
    - Automatic filtering of out-of-scope audio
    - Confidence-based decision making
    - Evolutionary learning from usage
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize voice profile library system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "voice_profile_library"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Data files
        self.profiles_file = self.data_dir / "voice_profiles.json"
        self.sound_profiles_file = self.data_dir / "sound_profiles.json"
        self.sessions_file = self.data_dir / "session_scopes.json"
        self.evolution_history_file = self.data_dir / "evolution_history.json"

        # Profile storage
        self.voice_profiles: Dict[str, VoiceProfile] = {}
        self.sound_profiles: Dict[str, SoundProfile] = {}
        self.session_scopes: Dict[str, SessionScope] = {}

        # Load existing data
        self._load_profiles()
        self._load_sound_profiles()
        self._load_session_scopes()

        # Dynamic scaling context
        self.system_load: float = 0.0
        self.adaptation_rate: float = 1.0  # How fast to adapt

        logger.info("✅ Voice Profile Library System initialized")
        logger.info(f"   Voice profiles: {len(self.voice_profiles)}")
        logger.info(f"   Sound profiles: {len(self.sound_profiles)}")
        logger.info(f"   Active sessions: {len(self.session_scopes)}")
        logger.info("   Core Values: Adapt, Improvise, Overcome")
        logger.info("   Evolution: Enabled - No static areas")

    def _load_profiles(self):
        """Load voice profiles"""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.voice_profiles = {
                        k: VoiceProfile(**v) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load profiles: {e}")

    def _save_profiles(self):
        """Save voice profiles"""
        try:
            with open(self.profiles_file, 'w', encoding='utf-8') as f:
                json.dump({
                    k: asdict(v) for k, v in self.voice_profiles.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving profiles: {e}")

    def _load_sound_profiles(self):
        """Load sound profiles"""
        if self.sound_profiles_file.exists():
            try:
                with open(self.sound_profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sound_profiles = {
                        k: SoundProfile(
                            profile_id=v['profile_id'],
                            sound_type=SoundType(v['sound_type']),
                            name=v['name'],
                            features=v.get('features', {}),
                            confidence_threshold=v.get('confidence_threshold', 0.6),
                            sample_count=v.get('sample_count', 0),
                            last_seen=v.get('last_seen', ''),
                            filter_out=v.get('filter_out', True),
                            effectiveness_history=v.get('effectiveness_history', []),
                            evolution_metadata=v.get('evolution_metadata', {}),
                            adaptation_level=v.get('adaptation_level', 1.0)
                        ) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load sound profiles: {e}")

    def _save_sound_profiles(self):
        """Save sound profiles"""
        try:
            with open(self.sound_profiles_file, 'w', encoding='utf-8') as f:
                json.dump({
                    k: {
                        **asdict(v),
                        'sound_type': v.sound_type.value
                    } for k, v in self.sound_profiles.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving sound profiles: {e}")

    def _load_session_scopes(self):
        """Load session scopes"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.session_scopes = {
                        k: SessionScope(
                            session_id=v['session_id'],
                            active_profiles=set(v.get('active_profiles', [])),
                            allowed_sound_types={SoundType(st) for st in v.get('allowed_sound_types', ['voice'])},
                            confidence_floor=v.get('confidence_floor', 0.7),
                            auto_learn=v.get('auto_learn', True),
                            strict_mode=v.get('strict_mode', False),
                            created_at=v.get('created_at', ''),
                            last_updated=v.get('last_updated', '')
                        ) for k, v in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load session scopes: {e}")

    def _save_session_scopes(self):
        """Save session scopes"""
        try:
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump({
                    k: {
                        **asdict(v),
                        'active_profiles': list(v.active_profiles),
                        'allowed_sound_types': [st.value for st in v.allowed_sound_types]
                    } for k, v in self.session_scopes.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving session scopes: {e}")

    def create_session_scope(
        self,
        session_id: str,
        initial_profiles: Optional[List[str]] = None,
        auto_learn: bool = True,
        strict_mode: bool = False
    ) -> SessionScope:
        """
        Create a new session scope

        @ADAPT: Adapts to session requirements
        @IMPROVISE: Creates scope even with incomplete information
        @OVERCOME: Handles missing profiles gracefully
        """
        scope = SessionScope(
            session_id=session_id,
            active_profiles=set(initial_profiles or []),
            allowed_sound_types={SoundType.VOICE},
            confidence_floor=0.7,
            auto_learn=auto_learn,
            strict_mode=strict_mode,
            created_at=datetime.now().isoformat(),
            last_updated=datetime.now().isoformat()
        )

        self.session_scopes[session_id] = scope
        self._save_session_scopes()

        logger.info(f"   ✅ Created session scope: {session_id}")
        logger.info(f"      Active profiles: {len(scope.active_profiles)}")
        logger.info(f"      Auto-learn: {auto_learn}, Strict: {strict_mode}")

        return scope

    def add_voice_profile(
        self,
        profile_id: str,
        name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        voice_features: Optional[Dict[str, Any]] = None
    ) -> VoiceProfile:
        """
        Add or update a voice profile

        @ADAPT: Adapts to new voice characteristics
        @IMPROVISE: Works with incomplete feature data
        @OVERCOME: Handles profile conflicts and updates
        """
        if profile_id in self.voice_profiles:
            # Update existing profile
            profile = self.voice_profiles[profile_id]
            if voice_features:
                profile.voice_features.update(voice_features)
            if name:
                profile.name = name
            if user_id:
                profile.user_id = user_id
            if session_id:
                profile.session_id = session_id
            profile.last_seen = datetime.now().isoformat()
        else:
            # Create new profile
            profile = VoiceProfile(
                profile_id=profile_id,
                name=name,
                user_id=user_id,
                session_id=session_id,
                voice_features=voice_features or {},
                last_seen=datetime.now().isoformat(),
                evolution_metadata={
                    "created_at": datetime.now().isoformat(),
                    "evolution_type": "adaptive",
                    "learning_enabled": True
                }
            )

        self.voice_profiles[profile_id] = profile
        self._save_profiles()

        # Add to session scope if provided
        if session_id and session_id in self.session_scopes:
                    self.session_scopes[session_id].active_profiles.add(profile_id)
                    self.session_scopes[session_id].last_updated = datetime.now().isoformat()
                    self._save_session_scopes()

        logger.info(f"   ✅ Added/updated voice profile: {profile_id} ({name})")

        return profile

    def add_sound_profile(
        self,
        profile_id: str,
        sound_type: SoundType,
        name: str,
        features: Optional[Dict[str, Any]] = None,
        filter_out: bool = True
    ) -> SoundProfile:
        """
        Add or update a sound profile

        @ADAPT: Adapts to new sound patterns
        @IMPROVISE: Works with minimal feature data
        @OVERCOME: Handles ambiguous sound classification
        """
        if profile_id in self.sound_profiles:
            profile = self.sound_profiles[profile_id]
            if features:
                profile.features.update(features)
            if name:
                profile.name = name
            profile.last_seen = datetime.now().isoformat()
        else:
            profile = SoundProfile(
                profile_id=profile_id,
                sound_type=sound_type,
                name=name,
                features=features or {},
                filter_out=filter_out,
                last_seen=datetime.now().isoformat(),
                evolution_metadata={
                    "created_at": datetime.now().isoformat(),
                    "evolution_type": "adaptive",
                    "learning_enabled": True
                }
            )

        self.sound_profiles[profile_id] = profile
        self._save_sound_profiles()

        logger.info(f"   ✅ Added/updated sound profile: {profile_id} ({name}, {sound_type.value})")

        return profile

    def identify_voice(
        self,
        audio_features: Dict[str, Any],
        session_id: Optional[str] = None
    ) -> Tuple[Optional[str], float, ConfidenceLevel]:
        """
        Identify voice from audio features

        @ADAPT: Adapts confidence thresholds based on context
        @IMPROVISE: Makes best guess even with incomplete data
        @OVERCOME: Handles unknown voices gracefully

        Returns: (profile_id, confidence_score, confidence_level)
        """
        if not self.voice_profiles:
            return (None, 0.0, ConfidenceLevel.UNKNOWN)

        # Get session scope if provided
        scope = None
        if session_id and session_id in self.session_scopes:
            scope = self.session_scopes[session_id]

        best_match = None
        best_confidence = 0.0

        # Check profiles in scope first
        profiles_to_check = []
        if scope:
            # Check in-scope profiles first
            for profile_id in scope.active_profiles:
                if profile_id in self.voice_profiles:
                    profiles_to_check.append(self.voice_profiles[profile_id])
            # Then check other active profiles
            for profile in self.voice_profiles.values():
                if profile.is_active and profile.profile_id not in scope.active_profiles:
                    profiles_to_check.append(profile)
        else:
            # Check all active profiles
            profiles_to_check = [p for p in self.voice_profiles.values() if p.is_active]

        # Calculate confidence for each profile
        for profile in profiles_to_check:
            confidence = self._calculate_voice_confidence(
                audio_features,
                profile.voice_features,
                profile.confidence_threshold,
                profile.adaptation_level
            )

            if confidence > best_confidence:
                best_confidence = confidence
                best_match = profile.profile_id

        # Determine confidence level
        if best_confidence >= 0.95:
            level = ConfidenceLevel.CERTAIN
        elif best_confidence >= 0.8:
            level = ConfidenceLevel.HIGH
        elif best_confidence >= 0.6:
            level = ConfidenceLevel.MEDIUM
        elif best_confidence >= 0.3:
            level = ConfidenceLevel.LOW
        else:
            level = ConfidenceLevel.UNKNOWN

        # Apply dynamic confidence threshold based on session scope
        if scope:
            effective_threshold = max(
                scope.confidence_floor,
                best_match and self.voice_profiles[best_match].confidence_threshold or 0.7
            )
            if best_confidence < effective_threshold:
                # Below threshold - return unknown
                return (None, best_confidence, ConfidenceLevel.UNKNOWN)

        return (best_match, best_confidence, level)

    def _calculate_voice_confidence(
        self,
        audio_features: Dict[str, Any],
        profile_features: Dict[str, Any],
        base_threshold: float,
        adaptation_level: float
    ) -> float:
        """
        Calculate confidence score for voice match

        @ADAPT: Adapts calculation based on available features
        @IMPROVISE: Works with partial feature matches
        @OVERCOME: Handles missing or mismatched features
        """
        if not profile_features:
            return 0.0

        # Simple feature matching (can be enhanced with ML models)
        matches = 0
        total_features = 0

        for key, value in profile_features.items():
            total_features += 1
            if key in audio_features:
                # Calculate similarity (simplified - can use cosine similarity, etc.)
                if isinstance(value, (int, float)) and isinstance(audio_features[key], (int, float)):
                    # Numerical similarity
                    diff = abs(value - audio_features[key])
                    max_val = max(abs(value), abs(audio_features[key]), 1.0)
                    similarity = 1.0 - min(diff / max_val, 1.0)
                    if similarity > 0.7:  # 70% similarity threshold
                        matches += 1
                elif value == audio_features[key]:
                    # Exact match
                    matches += 1

        if total_features == 0:
            return 0.0

        base_confidence = matches / total_features

        # Apply adaptation level (dynamic scaling)
        confidence = base_confidence * adaptation_level

        # Apply base threshold influence
        if confidence >= base_threshold:
            # Boost confidence if above threshold
            confidence = min(1.0, confidence * 1.1)
        else:
            # Reduce confidence if below threshold
            confidence = confidence * 0.9

        return min(1.0, max(0.0, confidence))

    def should_filter_audio(
        self,
        audio_features: Dict[str, Any],
        session_id: Optional[str] = None,
        sound_type: Optional[SoundType] = None
    ) -> Tuple[bool, str, float]:
        """
        Determine if audio should be filtered out

        @ADAPT: Adapts filtering based on session scope and context
        @IMPROVISE: Makes filtering decisions with incomplete information
        @OVERCOME: Handles edge cases and unknown scenarios

        Returns: (should_filter, reason, confidence)
        """
        if not session_id or session_id not in self.session_scopes:
            # No session scope - allow by default (or use global settings)
            return (False, "no_session_scope", 0.5)

        scope = self.session_scopes[session_id]

        # Check if it's a known voice in scope
        if sound_type != SoundType.VOICE or sound_type is None:
            # Try to identify as voice first
            profile_id, confidence, level = self.identify_voice(audio_features, session_id)

            if profile_id and level in [ConfidenceLevel.HIGH, ConfidenceLevel.CERTAIN]:
                # Known voice in scope - don't filter
                return (False, f"known_voice:{profile_id}", confidence)
            elif profile_id and level == ConfidenceLevel.MEDIUM:
                # Medium confidence - check if in scope
                if profile_id in scope.active_profiles:
                    return (False, f"in_scope_voice:{profile_id}", confidence)
                else:
                    return (True, f"out_of_scope_voice:{profile_id}", confidence)
            elif level in [ConfidenceLevel.LOW, ConfidenceLevel.UNKNOWN]:
                # Unknown or low confidence voice
                if scope.strict_mode:
                    return (True, "unknown_voice_strict_mode", confidence)
                elif scope.auto_learn:
                    # Auto-learn: don't filter, but mark for learning
                    return (False, "auto_learning_unknown", confidence)
                else:
                    return (True, "unknown_voice", confidence)

        # Check sound profiles
        if sound_type:
            # Check if this sound type should be filtered
            if sound_type not in scope.allowed_sound_types:
                return (True, f"sound_type_not_allowed:{sound_type.value}", 0.8)

            # Check against sound profiles
            for sound_profile in self.sound_profiles.values():
                if sound_profile.sound_type == sound_type and sound_profile.filter_out:
                    # Check if this matches the sound profile
                    match_confidence = self._calculate_sound_match(
                        audio_features,
                        sound_profile.features
                    )
                    if match_confidence > sound_profile.confidence_threshold:
                        return (True, f"known_filtered_sound:{sound_profile.profile_id}", match_confidence)

        # Default: don't filter (allow through)
        return (False, "allowed", 0.5)

    def _calculate_sound_match(
        self,
        audio_features: Dict[str, Any],
        profile_features: Dict[str, Any]
    ) -> float:
        """Calculate match confidence for sound profile"""
        if not profile_features:
            return 0.0

        matches = 0
        total = 0

        for key, value in profile_features.items():
            total += 1
            if key in audio_features:
                if isinstance(value, (int, float)) and isinstance(audio_features[key], (int, float)):
                    diff = abs(value - audio_features[key])
                    max_val = max(abs(value), abs(audio_features[key]), 1.0)
                    similarity = 1.0 - min(diff / max_val, 1.0)
                    if similarity > 0.6:
                        matches += 1
                elif value == audio_features[key]:
                    matches += 1

        return matches / total if total > 0 else 0.0

    def record_voice_sample(
        self,
        profile_id: str,
        audio_features: Dict[str, Any],
        was_correct: bool,
        effectiveness: Optional[float] = None
    ):
        """
        Record a voice sample for evolutionary learning

        @ADAPT: Adapts profile based on new samples
        @IMPROVISE: Learns from partial or noisy samples
        @OVERCOME: Improves even from incorrect identifications
        """
        if profile_id not in self.voice_profiles:
            return

        profile = self.voice_profiles[profile_id]
        profile.sample_count += 1
        profile.last_seen = datetime.now().isoformat()

        # Update features (adaptive learning)
        if was_correct and audio_features:
            # Merge new features with existing (weighted average)
            for key, value in audio_features.items():
                if key in profile.voice_features:
                    # Weighted average: 70% old, 30% new
                    if isinstance(value, (int, float)) and isinstance(profile.voice_features[key], (int, float)):
                        profile.voice_features[key] = (
                            profile.voice_features[key] * 0.7 + value * 0.3
                        )
                else:
                    profile.voice_features[key] = value

        # Update effectiveness
        if effectiveness is None:
            effectiveness = 1.0 if was_correct else 0.0

        profile.effectiveness_history.append(effectiveness)
        if len(profile.effectiveness_history) > 100:
            profile.effectiveness_history.pop(0)

        profile.success_rate = sum(profile.effectiveness_history) / len(profile.effectiveness_history)

        # Evolutionary learning: adjust confidence threshold
        if profile.success_rate > 0.9:
            # High success - can lower threshold slightly (more permissive)
            profile.confidence_threshold = max(0.5, profile.confidence_threshold * 0.98)
        elif profile.success_rate < 0.7:
            # Low success - raise threshold (more strict)
            profile.confidence_threshold = min(0.95, profile.confidence_threshold * 1.02)

        # Update adaptation level based on effectiveness
        if effectiveness > 0.8:
            profile.adaptation_level = min(1.5, profile.adaptation_level * 1.01)
        elif effectiveness < 0.5:
            profile.adaptation_level = max(0.5, profile.adaptation_level * 0.99)

        self._save_profiles()

        logger.debug(f"   📊 Recorded sample for {profile_id}: success={was_correct}, effectiveness={effectiveness:.2f}")

    def evolve_profiles(self):
        """
        Evolve all profiles based on usage patterns

        @ADAPT: Adapts all profiles to current conditions
        @IMPROVISE: Finds optimal settings through evolution
        @OVERCOME: Improves system performance continuously
        """
        evolved_count = 0

        for profile_id, profile in self.voice_profiles.items():
            if profile.sample_count < 5:
                continue  # Need minimum samples

            # Evolutionary adjustments
            old_threshold = profile.confidence_threshold

            # Adjust based on success rate
            if profile.success_rate < 0.5:
                profile.confidence_threshold = min(0.95, profile.confidence_threshold * 1.05)
                profile.evolution_metadata["evolution_note"] = "Raised threshold due to low success"
            elif profile.success_rate > 0.95:
                profile.confidence_threshold = max(0.5, profile.confidence_threshold * 0.95)
                profile.evolution_metadata["evolution_note"] = "Lowered threshold due to high success"

            if old_threshold != profile.confidence_threshold:
                evolved_count += 1
                profile.evolution_metadata["last_evolution"] = datetime.now().isoformat()

        if evolved_count > 0:
            self._save_profiles()
            logger.info(f"   🔄 Evolved {evolved_count} voice profiles")

        # Evolve sound profiles
        sound_evolved = 0
        for profile_id, profile in self.sound_profiles.items():
            if profile.sample_count < 3:
                continue

            # Adjust filter behavior based on effectiveness
            if len(profile.effectiveness_history) > 0:
                avg_effectiveness = sum(profile.effectiveness_history) / len(profile.effectiveness_history)
                if avg_effectiveness < 0.5:
                    # Low effectiveness - adjust threshold
                    profile.confidence_threshold = min(0.9, profile.confidence_threshold * 1.1)
                    sound_evolved += 1

        if sound_evolved > 0:
            self._save_sound_profiles()
            logger.info(f"   🔄 Evolved {sound_evolved} sound profiles")

    def get_session_statistics(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        if session_id not in self.session_scopes:
            return {}

        scope = self.session_scopes[session_id]
        profile_stats = []

        for profile_id in scope.active_profiles:
            if profile_id in self.voice_profiles:
                profile = self.voice_profiles[profile_id]
                profile_stats.append({
                    "profile_id": profile_id,
                    "name": profile.name,
                    "confidence_threshold": profile.confidence_threshold,
                    "success_rate": profile.success_rate,
                    "sample_count": profile.sample_count,
                    "adaptation_level": profile.adaptation_level
                })

        return {
            "session_id": session_id,
            "active_profiles": len(scope.active_profiles),
            "profile_details": profile_stats,
            "confidence_floor": scope.confidence_floor,
            "auto_learn": scope.auto_learn,
            "strict_mode": scope.strict_mode,
            "created_at": scope.created_at,
            "last_updated": scope.last_updated
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Voice Profile Library System")
        parser.add_argument("--create-session", type=str, metavar="SESSION_ID", help="Create new session scope")
        parser.add_argument("--add-profile", type=str, nargs=3, metavar=("ID", "NAME", "USER_ID"), help="Add voice profile")
        parser.add_argument("--identify", type=str, metavar="SESSION_ID", help="Test voice identification")
        parser.add_argument("--evolve", action="store_true", help="Evolve all profiles")
        parser.add_argument("--stats", type=str, metavar="SESSION_ID", help="Get session statistics")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = VoiceProfileLibrarySystem()

        if args.create_session:
            scope = system.create_session_scope(args.create_session)
            if args.json:
                print(json.dumps(asdict(scope), indent=2, default=str))
            else:
                print(f"✅ Created session: {scope.session_id}")

        elif args.add_profile:
            profile_id, name, user_id = args.add_profile
            profile = system.add_voice_profile(profile_id, name, user_id)
            if args.json:
                print(json.dumps(asdict(profile), indent=2, default=str))
            else:
                print(f"✅ Added profile: {profile.profile_id} ({profile.name})")

        elif args.evolve:
            system.evolve_profiles()
            print("✅ Evolved all profiles")

        elif args.stats:
            stats = system.get_session_statistics(args.stats)
            if args.json:
                print(json.dumps(stats, indent=2, default=str))
            else:
                print(f"Session: {stats.get('session_id')}")
                print(f"Active profiles: {stats.get('active_profiles', 0)}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()