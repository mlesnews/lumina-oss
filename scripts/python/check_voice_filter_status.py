#!/usr/bin/env python3
"""
Check Voice Filter Status - Verify Voice Filter Setup
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from voice_filter_system import VoiceFilterSystem
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("VoiceFilterStatus")

print("=" * 80)
print("🎤 VOICE FILTER STATUS CHECK")
print("=" * 80)
print()

# Initialize voice filter system
filter_system = VoiceFilterSystem(user_id="user", project_root=project_root)

# Check profile status
profile = filter_system.voice_profile
profile_data = profile.profile_data

trained = profile_data.get("trained", False)
samples = profile_data.get("samples", [])
num_samples = len(samples)

print(f"📊 Voice Profile Status:")
print(f"   User ID: {profile.user_id}")
print(f"   Profile File: {profile.profile_file}")
print(f"   Trained: {trained}")
print(f"   Samples Collected: {num_samples}")
print()

print(f"⚙️  Filter Settings:")
print(f"   Filter Enabled: {filter_system.enable_voice_filtering}")
print(f"   Voice Match Threshold: {filter_system.voice_match_threshold} (75% - strict, filters TV/background)")
print(f"   Noise Gate Threshold: {filter_system.noise_gate_threshold}")
print()

if trained:
    print("✅ Voice filter is ACTIVE")
    print("   🎯 Filtering: TV audio, background speakers, wife's voice")
    print("   ✅ Accepting: User's voice only")
    print()
    print("📝 Profile Details:")
    if profile_data.get("voice_features"):
        features = profile_data["voice_features"]
        print(f"   Dominant Frequency: {features.get('dominant_frequency', 'N/A'):.1f} Hz")
        print(f"   Spectral Centroid: {features.get('spectral_centroid', 'N/A'):.1f}")
        print(f"   Energy: {features.get('energy', 'N/A'):.2e}")
    if profile_data.get("trained_at"):
        print(f"   Trained At: {profile_data['trained_at']}")
else:
    print("⚠️  Voice filter is NOT ACTIVE")
    print("   ⚠️  Profile not trained yet - accepting ALL audio")
    print("   📚 Need at least 3 voice samples to train profile")
    print()
    if num_samples > 0:
        print(f"   Progress: {num_samples} samples collected (need 3+)")
        print("   💡 Profile will auto-train when you speak (during transcription)")
    else:
        print("   No samples collected yet")
        print("   💡 Start transcription to collect voice samples")

print()
print("=" * 80)
print()

if trained:
    print("✅ Voice filter is ready - will filter out TV/background audio")
else:
    print("⚠️  Voice filter needs training - will accept all audio until trained")
    print("   💡 Speak during transcription to train the profile automatically")

print()
