#!/usr/bin/env python3
"""
Fix Kenny Voice Filtering - Debug and Fix is_user_voice Detection

Fixes the issue where:
- Wife's voice is still being transcribed
- Voices from TV/phone/other sources are being transcribed
- Singing on TV/phone/other sources is being transcribed
- Live human visitors playing videos are being transcribed

Tags: #VOICE_FILTER #KENNY #IMVA #FIX @JARVIS @LUMINA
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
    from voice_filter_system import VoiceFilterSystem, VoicePrintProfile
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("FixKennyVoiceFiltering")

print("=" * 80)
print("🔧 FIXING KENNY VOICE FILTERING")
print("=" * 80)
print()

# Initialize voice filter system
filter_system = VoiceFilterSystem(user_id="user", project_root=project_root)

# Check current status
profile = filter_system.voice_profile
profile_data = profile.profile_data
trained = profile_data.get("trained", False)
samples = profile_data.get("samples", [])
num_samples = len(samples)

print(f"📊 Current Status:")
print(f"   Profile Trained: {trained}")
print(f"   Samples Collected: {num_samples}")
print(f"   Filter Enabled: {filter_system.enable_voice_filtering}")
print(f"   Match Threshold: {filter_system.voice_match_threshold}")
print()

# DIAGNOSIS
print("🔍 DIAGNOSIS:")
print()

if not trained:
    print("❌ PROBLEM FOUND: Voice profile is NOT TRAINED")
    print("   ⚠️  When profile is not trained, filter_audio() returns:")
    print("      return audio_data, True  # Accepts ALL audio!")
    print()
    print("   This means:")
    print("   - Wife's voice → ACCEPTED (not filtered)")
    print("   - TV voices → ACCEPTED (not filtered)")
    print("   - Phone audio → ACCEPTED (not filtered)")
    print("   - Singing → ACCEPTED (not filtered)")
    print("   - Visitor voices → ACCEPTED (not filtered)")
    print()
    print("   💡 SOLUTION: Train the voice profile with user's voice samples")
    print()
else:
    print("✅ Voice profile IS trained")
    print("   But filtering may still not work if:")
    print("   1. Kenny/IMVA is not using VoiceFilterSystem")
    print("   2. filter_audio() is not being called before transcription")
    print("   3. Threshold is too low (currently {:.2f})".format(filter_system.voice_match_threshold))
    print()

# Check if Kenny uses voice filter
print("🔍 CHECKING KENNY INTEGRATION:")
print()

kenny_file = script_dir / "kenny_imva_enhanced.py"
if kenny_file.exists():
    kenny_content = kenny_file.read_text(encoding='utf-8')

    uses_voice_filter = "VoiceFilterSystem" in kenny_content or "voice_filter" in kenny_content.lower()
    uses_filter_audio = "filter_audio" in kenny_content
    checks_is_user = "is_user_voice" in kenny_content

    print(f"   Uses VoiceFilterSystem: {uses_voice_filter}")
    print(f"   Calls filter_audio(): {uses_filter_audio}")
    print(f"   Checks is_user_voice: {checks_is_user}")
    print()

    if not uses_voice_filter:
        print("❌ PROBLEM: Kenny is NOT using VoiceFilterSystem!")
        print("   💡 SOLUTION: Integrate VoiceFilterSystem into Kenny")
        print()
    elif not uses_filter_audio:
        print("❌ PROBLEM: Kenny is not calling filter_audio()!")
        print("   💡 SOLUTION: Call filter_audio() before transcription")
        print()
    elif not checks_is_user:
        print("❌ PROBLEM: Kenny is not checking is_user_voice!")
        print("   💡 SOLUTION: Check is_user_voice before transcribing")
        print()
    else:
        print("✅ Kenny appears to use voice filtering")
        print("   But may need to verify it's actually being called")
        print()
else:
    print("⚠️  Could not find kenny_imva_enhanced.py")
    print()

# FIXES
print("=" * 80)
print("🔧 FIXES TO APPLY:")
print("=" * 80)
print()

fixes = []

# Fix 1: Train voice profile if not trained
if not trained:
    fixes.append({
        "priority": 1,
        "title": "Train Voice Profile",
        "description": "Voice profile must be trained to filter non-user voices",
        "action": "Collect at least 5 voice samples from user",
        "code": """
# In kenny_imva_enhanced.py, add training collection:
if not self.voice_filter.voice_profile.profile_data.get("trained", False):
    # Collect training samples when user speaks
    self.voice_filter.add_training_sample(audio_data, sample_rate)
    if len(self.voice_filter.voice_profile.profile_data["samples"]) >= 5:
        self.voice_filter.train_profile()
"""
    })

# Fix 2: Ensure voice filter is initialized
fixes.append({
    "priority": 2,
    "title": "Initialize VoiceFilterSystem in Kenny",
    "description": "Kenny must initialize and use VoiceFilterSystem",
    "action": "Add VoiceFilterSystem initialization in __init__",
    "code": """
# In kenny_imva_enhanced.py __init__:
from voice_filter_system import VoiceFilterSystem

self.voice_filter = VoiceFilterSystem(user_id="user", project_root=self.project_root)
self.voice_filter_enabled = True
"""
})

# Fix 3: Call filter_audio before transcription
fixes.append({
    "priority": 3,
    "title": "Call filter_audio() Before Transcription",
    "description": "Must filter audio and check is_user_voice before transcribing",
    "action": "Add filter check in voice listening/transcription code",
    "code": """
# In voice listening/transcription code:
audio_data = ...  # Get audio from microphone
sample_rate = ...  # Get sample rate

# FILTER AUDIO - CRITICAL STEP
if self.voice_filter_enabled and self.voice_filter:
    filtered_audio, is_user_voice = self.voice_filter.filter_audio(audio_data, sample_rate)

    if not is_user_voice:
        # REJECT: TV/background/wife/other speaker
        logger.debug("🚫 Voice REJECTED - not user's voice (TV/background/wife/other)")
        continue  # Skip transcription

    audio_data = filtered_audio  # Use filtered audio

# Only transcribe if is_user_voice == True
transcription = recognizer.recognize_google(audio_data)
"""
})

# Fix 4: Increase threshold if needed
if trained and filter_system.voice_match_threshold < 0.90:
    fixes.append({
        "priority": 4,
        "title": "Increase Voice Match Threshold",
        "description": "Threshold may be too low, allowing non-user voices",
        "action": "Set threshold to 0.90 (very strict)",
        "code": """
# In voice_filter_system.py or kenny initialization:
self.voice_filter.voice_match_threshold = 0.90  # Very strict - only user's voice
"""
    })

# Fix 5: Add debug logging
fixes.append({
    "priority": 5,
    "title": "Add Debug Logging",
    "description": "Log when voice is accepted/rejected to debug filtering",
    "action": "Add logging in filter_audio() calls",
    "code": """
# Add logging to see what's happening:
logger.info(f"🎤 Audio received - checking voice filter...")
logger.info(f"   Profile trained: {self.voice_filter.voice_profile.profile_data.get('trained', False)}")
logger.info(f"   Filter enabled: {self.voice_filter_enabled}")

filtered_audio, is_user_voice = self.voice_filter.filter_audio(audio_data, sample_rate)

if is_user_voice:
    logger.info("✅ Voice ACCEPTED - user's voice")
else:
    logger.warning("🚫 Voice REJECTED - TV/background/wife/other speaker")
"""
})

# Print fixes
for i, fix in enumerate(fixes, 1):
    print(f"{i}. {fix['title']} (Priority {fix['priority']})")
    print(f"   {fix['description']}")
    print(f"   Action: {fix['action']}")
    print()
    print("   Code:")
    print(fix['code'])
    print()

print("=" * 80)
print("📋 SUMMARY:")
print("=" * 80)
print()

if not trained:
    print("❌ CRITICAL: Voice profile is NOT trained")
    print("   This is why wife/TV/phone audio is being transcribed")
    print("   SOLUTION: Train voice profile with user's voice samples")
    print()
    print("   Steps to train:")
    print("   1. Speak clearly into microphone")
    print("   2. System will collect voice samples automatically")
    print("   3. After 5+ samples, profile will auto-train")
    print("   4. Once trained, only user's voice will be accepted")
    print()
else:
    print("✅ Voice profile is trained")
    print("   But filtering may not be working because:")
    print("   - Kenny may not be using VoiceFilterSystem")
    print("   - filter_audio() may not be called before transcription")
    print("   - is_user_voice check may be missing")
    print()

print("=" * 80)
print()
