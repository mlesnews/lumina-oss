#!/usr/bin/env python3
"""
LUMINA Enhanced Elevator Pitch v2.0

Incorporates ALL expert feedback:
- 🩺 The Doc (Psychology): Urgency, social proof, strong CTA
- 🎤 Speech Pathologist: Pauses, energy map, delivery guide
- 🎙️ Wes Roth: "Category 9 earthquake" urgency
- 🎙️ Dylan Curious: "2026 authenticity" hope

Key improvements:
- URGENCY + HOPE formula
- Specific timeline (By 2026)
- Stronger metaphor (lighthouse)
- Acknowledge AI capabilities before human pivot
- Clear call-to-action
"""

import subprocess
import asyncio
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("EnhancedPitchV2")

# Hybrid TTS System (Local-first, no API restrictions)
HYBRID_TTS_AVAILABLE = False
try:
    from hybrid_tts_system import HybridTTSSystem
    HYBRID_TTS_AVAILABLE = True
except ImportError:
    HybridTTSSystem = None
    logger.info("Hybrid TTS System not available - will use fallback")

# Azure Speech SDK (fallback)
AZURE_SPEECH_AVAILABLE = False
try:
    import azure.cognitiveservices.speech as speechsdk
    AZURE_SPEECH_AVAILABLE = True
except ImportError:
    speechsdk = None


# =============================================================================
# GRAMMAR CHECK SYSTEM (Using LanguageTool + Custom Rules)
# =============================================================================

# Try to import language_tool_python for proper grammar checking
LANGUAGE_TOOL_AVAILABLE = False
try:
    import language_tool_python
    LANGUAGE_TOOL_AVAILABLE = True
except ImportError:
    pass

# Try MANUS Auto-Grammarly
MANUS_GRAMMARLY_AVAILABLE = False
try:
    from manus_auto_grammarly import MANUSAutoGrammarly
    MANUS_GRAMMARLY_AVAILABLE = True
except ImportError:
    pass


def check_grammar(text: str, use_language_tool: bool = True) -> Dict[str, Any]:
    """
    Check text for grammar issues using LanguageTool + custom rules
    Returns corrections and suggestions
    """
    import re
    issues = []
    corrected_text = text

    # === TRY LANGUAGE TOOL FIRST (most comprehensive) ===
    if use_language_tool and LANGUAGE_TOOL_AVAILABLE:
        try:
            tool = language_tool_python.LanguageTool('en-US')
            matches = tool.check(corrected_text)

            # Apply corrections (reverse order to maintain positions)
            for match in reversed(matches):
                if match.replacements:
                    replacement = match.replacements[0]
                    start = match.offset
                    end = match.offset + match.errorLength
                    original = corrected_text[start:end]
                    corrected_text = corrected_text[:start] + replacement + corrected_text[end:]
                    issues.append(f"LanguageTool: '{original}' → '{replacement}' ({match.ruleId})")

            tool.close()
        except Exception as e:
            logger.debug(f"LanguageTool error: {e}")

    # === CUSTOM RULES (TTS-specific and project-specific) ===
    custom_rules = [
        # Proper nouns - LUMINA project specific
        ("andre karpathy", "Andrej Karpathy"),
        ("Andre Karpathy", "Andrej Karpathy"),
        ("andrej karpathy", "Andrej Karpathy"),
        ("dylan curious", "Dylan Curious"),
        ("wes roth", "Wes Roth"),

        # TTS pronunciation helpers - add spaces for clarity
        ("AI-generated", "A.I. generated"),
        ("AI's", "A.I.'s"),
        (" AI ", " A.I. "),
        (" AI.", " A.I."),
        (" AI,", " A.I.,"),

        # Fix compound words for TTS
        ("out-think", "out think"),
        ("out-remember", "out remember"),  
        ("out-process", "out process"),

        # Awkward phrasing
        ("In all this noise, in all this", "In all this noise, in this"),

        # Common grammar errors
        ("its doubling", "it's doubling"),
        ("its advancing", "it's advancing"),
        ("can not", "cannot"),
        ("AI are", "AI is"),

        # Double punctuation
        ("..", "."),
        (",,", ","),
        ("  ", " "),  # Double spaces
    ]

    for pattern, replacement in custom_rules:
        if pattern in corrected_text:
            issues.append(f"Custom: '{pattern}' → '{replacement}'")
            corrected_text = corrected_text.replace(pattern, replacement)

    # === REGEX RULES ===
    regex_rules = [
        # Missing space after period
        (r'\.([A-Za-z])', r'. \1'),
        # Missing space after comma
        (r',([A-Za-z])', r', \1'),
        # Capitalization after periods
        (r'\. ([a-z])', lambda m: '. ' + m.group(1).upper()),
    ]

    for pattern, replacement in regex_rules:
        if callable(replacement):
            new_text = re.sub(pattern, replacement, corrected_text)
        else:
            new_text = re.sub(pattern, replacement, corrected_text)
        if new_text != corrected_text:
            issues.append(f"Regex fix: {pattern}")
            corrected_text = new_text

    # Clean up multiple spaces again
    while "  " in corrected_text:
        corrected_text = corrected_text.replace("  ", " ")

    return {
        "original": text,
        "corrected": corrected_text.strip(),
        "issues_found": len(issues),
        "issues": issues,
        "passed": len(issues) == 0,
        "language_tool_used": LANGUAGE_TOOL_AVAILABLE
    }


def grammar_check_all_scenes(scenes: List[Dict]) -> List[Dict]:
    """Run grammar check on all scene texts using LanguageTool + custom rules"""

    tool_status = "LanguageTool" if LANGUAGE_TOOL_AVAILABLE else "Custom rules only"
    logger.info(f"📝 Running Grammar Check ({tool_status})...")

    corrected_scenes = []
    total_fixes = 0

    for scene in scenes:
        result = check_grammar(scene["text"])

        if result["issues_found"] > 0:
            logger.info(f"   Scene {scene['id']}: {result['issues_found']} fix(es)")
            for issue in result["issues"][:5]:  # Show first 5
                logger.info(f"      • {issue}")
            if result["issues_found"] > 5:
                logger.info(f"      ... and {result['issues_found'] - 5} more")
            total_fixes += result["issues_found"]

        # Create corrected scene
        corrected_scene = scene.copy()
        corrected_scene["text"] = result["corrected"]
        corrected_scenes.append(corrected_scene)

    logger.info(f"   ✅ Grammar check complete: {total_fixes} total fixes applied")
    return corrected_scenes


# =============================================================================
# ENHANCED PITCH v2.0 - EXPERT-INFORMED
# =============================================================================

ENHANCED_PITCH_V2 = """
[SCENE 1 - HOOK / PATTERN INTERRUPT]
You know what Andrej Karpathy just said?

[SCENE 2 - URGENCY FROM WES ROTH]
He called it a category nine earthquake.
AI is advancing so fast, even the experts can't keep up.
It's doubling every four months.

[SCENE 3 - THE PROBLEM / FEAR TRIGGER]
And here's what terrifies me:
In all this noise, in all this overwhelming flood of AI-generated content...
individual human voices are getting drowned out.

[PAUSE - 2 BEATS - LET IT LAND]

[SCENE 4 - THE REVEAL / HERO MOMENT]
That's why I spent two years building something different.
I call it... LUMINA.

[PAUSE - LET IT RING]

[SCENE 5 - LIGHTHOUSE METAPHOR]
Think of LUMINA as a lighthouse for your voice.
In an ocean of AI-generated noise...
we make sure YOUR signal gets through.

[SCENE 6 - DIFFERENTIATION / ENEMY]
See, most AI tries to give you THE answer.
One answer. The optimal response.
Cold. Calculated. Inhuman.

[SCENE 7 - RHETORICAL QUESTION]
But that's not how the real world works, is it?

[PAUSE - 2 BEATS - WAIT FOR NODDING]

[SCENE 8 - THE HUMAN PIVOT / DYLAN'S INSIGHT]
Dylan Curious said something beautiful:
2026 might be the year we view authenticity as refreshing again.
The quirkiness. The outliers. The black sheep.

[SCENE 9 - EMOTIONAL CLIMAX - SLOW DOWN]
In a world where AI can out-think us,
out-remember us,
out-process us...

There's one thing that remains uniquely, irreplaceably yours:

Your perspective.

[BEAT]

That's what makes us human.

[BREATH - EMOTIONAL PEAK]

[SCENE 10 - LUMINA'S PROMISE]
LUMINA captures that.
It illuminates individual perspectives...
and shares them with the people who need to hear them.

[SCENE 11 - PERSONAL CREDO / AUTHENTICITY]
Because here's what I believe:

[SOFTER, INTIMATE]
For whatever your opinion is worth...

[RISE, CONVICTION]
which is EVERYTHING...

it deserves to be heard.

[SCENE 12 - INCLUSION PROMISE]
While others talk about who AI will leave behind...
we're building the bridge that brings everyone across.

We're not leaving anyone behind.

[SCENE 13 - URGENCY CTA]
The window to make your voice matter is narrowing.
By 2026, the landscape will look completely different.

[SCENE 14 - CALL TO ACTION]
Want to be one of the first to step through?

Go to lumina.io today.
Share your perspective.
Be heard.

[SCENE 15 - TAGLINE]
LUMINA.
Illuminating the world, one perspective at a time.
"""

# Scene-by-scene breakdown for video production
PITCH_SCENES_V2 = [
    {
        "id": 1,
        "text": "You know what Andrej Karpathy just said?",
        "visual": "Dark background, spotlight slowly emerging, tech news graphics subtle",
        "mood": "curious_hook",
        "energy": 4,
        "duration": 3.5,
        "delivery_notes": "Curious, slight lean forward, eyebrow raise"
    },
    {
        "id": 2,
        "text": "He called it a category nine earthquake. AI is advancing so fast, even the experts can't keep up. It's doubling every four months.",
        "visual": "Seismograph visual, numbers ticking up rapidly, urgency graphics",
        "mood": "urgency",
        "energy": 6,
        "duration": 8.0,
        "delivery_notes": "Build intensity, 'category nine' emphasized, specific numbers land"
    },
    {
        "id": 3,
        "text": "And here's what terrifies me: In all this noise, in all this overwhelming flood of AI-generated content... individual human voices are getting drowned out.",
        "visual": "Person drowning in digital noise, fragmented faces, overwhelm",
        "mood": "fear_concern",
        "energy": 3,
        "duration": 9.0,
        "delivery_notes": "Drop volume on 'terrifies', slow on 'drowned out'"
    },
    {
        "id": 4,
        "text": "That's why I spent two years building something different. I call it... LUMINA.",
        "visual": "Darkness, then warm glow emerging, LUMINA logo reveal",
        "mood": "reveal_hope",
        "energy": 7,
        "duration": 6.0,
        "delivery_notes": "PAUSE before. 'LUMINA' - let it ring, proud, like naming a ship"
    },
    {
        "id": 5,
        "text": "Think of LUMINA as a lighthouse for your voice. In an ocean of AI-generated noise... we make sure YOUR signal gets through.",
        "visual": "Lighthouse beam cutting through fog, signal visualization",
        "mood": "metaphor_hope",
        "energy": 6,
        "duration": 7.0,
        "delivery_notes": "Lighthouse metaphor - visualize it, YOUR emphasized"
    },
    {
        "id": 6,
        "text": "See, most AI tries to give you THE answer. One answer. The optimal response. Cold. Calculated. Inhuman.",
        "visual": "Robot giving sterile response, cold blue tones, clinical",
        "mood": "contrast_enemy",
        "energy": 4,
        "duration": 7.0,
        "delivery_notes": "Air quotes on 'THE answer', robotic delivery on last three words"
    },
    {
        "id": 7,
        "text": "But that's not how the real world works, is it?",
        "visual": "Question mark dissolving into multiple colorful perspectives",
        "mood": "challenge",
        "energy": 5,
        "duration": 3.5,
        "delivery_notes": "Rhetorical - PAUSE after, wait for mental nodding"
    },
    {
        "id": 8,
        "text": "Dylan Curious said something beautiful: 2026 might be the year we view authenticity as refreshing again. The quirkiness. The outliers. The black sheep.",
        "visual": "Diverse faces lighting up, neurodivergent appreciation",
        "mood": "hope_warmth",
        "energy": 6,
        "duration": 9.0,
        "delivery_notes": "Warm smile on 'beautiful', list with rhythm: quirkiness, outliers, black sheep"
    },
    {
        "id": 9,
        "text": "In a world where AI can out-think us, out-remember us, out-process us... There's one thing that remains uniquely, irreplaceably yours: Your perspective. That's what makes us human.",
        "visual": "AI capabilities shown, then pivot to human warmth, kaleidoscope of faces",
        "mood": "emotional_peak",
        "energy": 9,
        "duration": 12.0,
        "delivery_notes": "THIS IS THE CLIMAX. Build AI capabilities, then pivot. SLOW on 'Your perspective'. LAND 'human'."
    },
    {
        "id": 10,
        "text": "LUMINA captures that. It illuminates individual perspectives... and shares them with the people who need to hear them.",
        "visual": "Lighthouse illuminating connections, people connecting",
        "mood": "confident",
        "energy": 7,
        "duration": 6.0,
        "delivery_notes": "'Illuminates' - give it space, ties to brand"
    },
    {
        "id": 11,
        "text": "Because here's what I believe: For whatever your opinion is worth... which is EVERYTHING... it deserves to be heard.",
        "visual": "Intimate close-up, then expanding to include others",
        "mood": "intimate_to_conviction",
        "energy": 8,
        "duration": 8.0,
        "delivery_notes": "SIGNATURE MOMENT. Soft on 'worth', RISE on 'EVERYTHING', conviction on 'heard'"
    },
    {
        "id": 12,
        "text": "While others talk about who AI will leave behind... we're building the bridge that brings everyone across. We're not leaving anyone behind.",
        "visual": "Bridge building, hands reaching, inclusive imagery",
        "mood": "determined_inclusive",
        "energy": 7,
        "duration": 7.0,
        "delivery_notes": "Contrast: 'others talk' vs 'we're building'. Promise voice."
    },
    {
        "id": 13,
        "text": "The window to make your voice matter is narrowing. By 2026, the landscape will look completely different.",
        "visual": "Window/door slowly closing, timeline visualization",
        "mood": "urgency_scarcity",
        "energy": 6,
        "duration": 5.0,
        "delivery_notes": "Urgency without fear. Specific year lands."
    },
    {
        "id": 14,
        "text": "Want to be one of the first to step through? Go to lumina.io today. Share your perspective. Be heard.",
        "visual": "Door opening with light, clear CTA graphics",
        "mood": "invitation_action",
        "energy": 7,
        "duration": 6.0,
        "delivery_notes": "Genuine invitation. Clear action steps. End strong."
    },
    {
        "id": 15,
        "text": "LUMINA. Illuminating the world, one perspective at a time.",
        "visual": "Logo with tagline, warm glow, closing",
        "mood": "closing_warm",
        "energy": 6,
        "duration": 4.0,
        "delivery_notes": "Confident period. Let it settle."
    }
]


class EnhancedPitchV2Generator:
    """Generate Enhanced Elevator Pitch v2.0"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.output_dir = self.project_root / "output" / "videos" / "pitch_v2"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.temp_dir = self.project_root / "output" / "videos" / "temp_v2"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

        self.audio_dir = self.temp_dir / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.width = 1920
        self.height = 1080
        self.fps = 30

        self.ffmpeg_available = self._check_ffmpeg()

        # Hybrid TTS System (Local-first, no API restrictions)
        self.hybrid_tts = None
        self.hybrid_tts_available = False
        self._init_hybrid_tts()

        # Legacy Azure/Edge (fallback)
        self.tts_available = self._check_tts()
        self.azure_speech_available = False
        self.azure_speech_config = None
        self._init_azure_speech()

        logger.info("🎬 Enhanced Pitch v2.0 Generator")
        logger.info(f"   FFmpeg: {'✅' if self.ffmpeg_available else '❌'}")
        logger.info(f"   Hybrid TTS: {'✅' if self.hybrid_tts_available else '❌'}")
        if self.hybrid_tts_available and self.hybrid_tts:
            status = self.hybrid_tts.get_status()
            logger.info(f"      Engine: {status['best_engine']}")
        logger.info(f"   Azure TTS: {'✅' if self.azure_speech_available else '❌'}")
        logger.info(f"   Edge TTS: {'✅' if self.tts_available else '❌'}")

    def _check_ffmpeg(self) -> bool:
        try:
            result = subprocess.run(['ffmpeg', '-version'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False

    def _init_hybrid_tts(self) -> None:
        """Initialize Hybrid TTS System (Local-first)"""
        if not HYBRID_TTS_AVAILABLE:
            return

        try:
            # Use "local" as preferred engine (no API restrictions)
            self.hybrid_tts = HybridTTSSystem(preferred_engine="local")
            if self.hybrid_tts.best_engine != "none":
                self.hybrid_tts_available = True
                logger.info(f"   ✅ Hybrid TTS initialized: {self.hybrid_tts.best_engine}")
        except Exception as e:
            logger.debug(f"Hybrid TTS init failed: {e}")

    def _check_tts(self) -> bool:
        try:
            import edge_tts
            return True
        except ImportError:
            return False

    def _init_azure_speech(self) -> None:
        """Initialize Azure Speech SDK from Key Vault"""
        if not AZURE_SPEECH_AVAILABLE:
            return

        try:
            # Try to get credentials from Key Vault
            from azure_service_bus_integration import AzureKeyVaultClient

            vault_url = os.getenv("AZURE_KEY_VAULT_URL", "https://jarvis-lumina.vault.azure.net/")
            vault_client = AzureKeyVaultClient(vault_url=vault_url)

            speech_key = vault_client.get_secret("azure-speech-key")
            speech_region = vault_client.get_secret("azure-speech-region") or "eastus"

            if speech_key:
                self.azure_speech_config = speechsdk.SpeechConfig(
                    subscription=speech_key,
                    region=speech_region
                )
                # Use neural voice
                self.azure_speech_config.speech_synthesis_voice_name = "en-US-GuyNeural"
                self.azure_speech_available = True
                logger.info("   ✅ Azure Speech SDK initialized from Key Vault")
        except ImportError:
            logger.debug("Azure Key Vault client not available")
        except Exception as e:
            logger.debug(f"Azure Speech init failed: {e}")

    def _generate_azure_ssml(self, text: str) -> str:
        """
        Generate SSML with proper pronunciation.
        Using SUBSTITUTION approach - spell out words phonetically.

        LUMINA = "Loo-meena" (phonetic spelling TTS understands)
        """
        # Clean text
        clean_text = text.replace("[", "").replace("]", "")
        clean_text = " ".join(line.strip() for line in clean_text.split("\n") 
                             if line.strip() and not line.strip().startswith("["))

        # Build SSML - NORMAL rate, let natural speech flow
        ssml = '''<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" 
                         xmlns:mstts="https://www.w3.org/2001/mstts" xml:lang="en-US">
            <voice name="en-US-GuyNeural">
                <prosody rate="0%" pitch="+0%">'''

        # Use SUBSTITUTION for pronunciation fixes
        # This tells TTS to read the alias instead of the written word
        text_fixed = clean_text

        # LUMINA -> "Loo-meena" (phonetic that TTS reads correctly)
        for variant in ["LUMINA", "Lumina", "lumina"]:
            text_fixed = text_fixed.replace(
                variant, 
                '<sub alias="Loo meena">LUMINA</sub>'
            )

        # lumina.io -> "Loo meena dot I O"
        text_fixed = text_fixed.replace(
            "lumina.io",
            '<sub alias="Loo meena dot I O">lumina.io</sub>'
        )

        # AI -> "A. I." with periods for natural pause
        text_fixed = text_fixed.replace(" AI ", " A.I. ")
        text_fixed = text_fixed.replace(" AI.", " A.I.")
        text_fixed = text_fixed.replace(" AI,", " A.I.,")
        text_fixed = text_fixed.replace(" AI-", " A.I. ")
        text_fixed = text_fixed.replace("AI-generated", "A.I. generated")

        # Fix hyphenated compound words - just remove hyphens
        text_fixed = text_fixed.replace("out-think", "out think")
        text_fixed = text_fixed.replace("out-remember", "out remember")
        text_fixed = text_fixed.replace("out-process", "out process")

        # Natural sentence pauses only - let TTS handle the rest
        text_fixed = text_fixed.replace("...", ". . .")  # Ellipsis as three dots

        ssml += text_fixed
        ssml += '''</prosody>
            </voice>
        </speak>'''

        return ssml

    def _synthesize_azure_speech(self, text: str, output_file: Path) -> bool:
        """Synthesize speech using Azure Speech SDK with SSML"""
        if not self.azure_speech_available or not self.azure_speech_config:
            return False

        try:
            # Generate SSML
            ssml = self._generate_azure_ssml(text)

            # Configure audio output
            audio_config = speechsdk.audio.AudioOutputConfig(filename=str(output_file))

            # Create synthesizer
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=self.azure_speech_config,
                audio_config=audio_config
            )

            # Synthesize
            result = synthesizer.speak_ssml_async(ssml).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                return output_file.exists()
            else:
                logger.warning(f"Azure TTS failed: {result.reason}")
                return False

        except Exception as e:
            logger.warning(f"Azure TTS error: {e}")
            return False

    def prepare_text_for_tts(self, text: str) -> str:
        """
        Prepare text for TTS with proper spacing, pronunciation, and pauses.
        Uses SSML-compatible formatting for Edge TTS.
        """
        # Clean brackets and stage directions
        clean_text = text.replace("[", "").replace("]", "")
        clean_text = " ".join(line.strip() for line in clean_text.split("\n") 
                             if line.strip() and not line.strip().startswith("["))

        # PRONUNCIATION FIXES
        # LUMINA = "LOO-mih-nah" - spell it phonetically
        clean_text = clean_text.replace("LUMINA", "Loo-mee-nah")
        clean_text = clean_text.replace("Lumina", "Loo-mee-nah")
        clean_text = clean_text.replace("lumina", "loo-mee-nah")
        clean_text = clean_text.replace("lumina.io", "loo-mee-nah dot eye oh")

        # Fix common AI names
        clean_text = clean_text.replace("Andrej Karpathy", "Andre Kar-pah-thee")
        clean_text = clean_text.replace("AI", "A. I.")  # Spell out AI

        # ADD PAUSES - replace punctuation with pauses
        # Period = longer pause
        clean_text = clean_text.replace(". ", "... ")
        clean_text = clean_text.replace("? ", "?... ")
        clean_text = clean_text.replace("! ", "!... ")

        # Comma = shorter pause  
        clean_text = clean_text.replace(", ", ",, ")

        # Ellipsis = dramatic pause
        clean_text = clean_text.replace("...", ".......")

        # Colon = pause
        clean_text = clean_text.replace(": ", ":... ")

        # Add space between words that might get smushed
        # Hyphenated emphasis words
        clean_text = clean_text.replace("out-think", "out think")
        clean_text = clean_text.replace("out-remember", "out remember")
        clean_text = clean_text.replace("out-process", "out process")
        clean_text = clean_text.replace("AI-generated", "A. I. generated")

        # Ensure spaces around key words
        words_to_emphasize = ["YOUR", "EVERYTHING", "human", "perspective", "LUMINA"]
        for word in words_to_emphasize:
            clean_text = clean_text.replace(f" {word} ", f"  {word}  ")
            clean_text = clean_text.replace(f" {word}.", f"  {word}.")
            clean_text = clean_text.replace(f" {word},", f"  {word},")

        # Clean up multiple spaces but keep intentional pauses
        while "    " in clean_text:
            clean_text = clean_text.replace("    ", "   ")

        return clean_text

    async def _generate_voiceover_async(self, text: str, output_file: Path,
                                        voice: str = "en-US-GuyNeural") -> bool:
        # Try Hybrid TTS first (local-first, no API restrictions)
        if self.hybrid_tts_available and self.hybrid_tts:
            try:
                result = self.hybrid_tts.synthesize(
                    text=text,
                    output_file=output_file,
                    voice=voice if voice != "en-US-GuyNeural" else "default",
                    engine="local"  # Force local (no API keys needed)
                )

                if result.get("success"):
                    logger.info(f"   ✅ Hybrid TTS ({result.get('engine', 'local')}): {text[:30]}...")
                    return True
                else:
                    logger.warning(f"   ⚠️  Hybrid TTS failed: {result.get('error')}, falling back...")
            except Exception as e:
                logger.debug(f"Hybrid TTS error: {e}, falling back...")

        # Fallback: Try Azure Speech SDK (better pronunciation than Edge)
        if self.azure_speech_available:
            wav_file = output_file.with_suffix('.wav')
            if self._synthesize_azure_speech(text, wav_file):
                # Convert WAV to MP3 for consistency
                try:
                    subprocess.run([
                        'ffmpeg', '-y', '-i', str(wav_file),
                        '-acodec', 'libmp3lame', '-q:a', '2',
                        str(output_file)
                    ], capture_output=True, timeout=30)
                    wav_file.unlink()  # Delete WAV
                    if output_file.exists():
                        logger.info(f"   ✅ Azure TTS: {text[:30]}...")
                        return True
                except:
                    pass

        # Fallback to edge_tts
        try:
            import edge_tts

            # Prepare text with pronunciation fixes and pauses
            clean_text = self.prepare_text_for_tts(text)

            # Use slower rate for clarity
            communicate = edge_tts.Communicate(
                clean_text, 
                voice,
                rate="-10%",  # Slightly slower for clarity
                pitch="+0Hz"
            )
            await communicate.save(str(output_file))
            return output_file.exists()
        except Exception as e:
            logger.error(f"TTS error: {e}")
            return False

    def generate_voiceover(self, text: str, output_file: Path,
                          voice: str = "en-US-GuyNeural") -> bool:
        return asyncio.run(self._generate_voiceover_async(text, output_file, voice))

    def get_audio_duration(self, audio_file: Path) -> float:
        try:
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', str(audio_file)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except:
            pass
        return 4.0

    def get_mood_colors(self, mood: str) -> tuple:
        """Get background colors based on mood"""
        mood_colors = {
            "curious_hook": ("0x0a0a1a", "0x1a1a3a"),
            "urgency": ("0x1a0a0a", "0x3a1a1a"),
            "fear_concern": ("0x0a0a0a", "0x1a1a1a"),
            "reveal_hope": ("0x0a1a2a", "0x1a3a4a"),
            "metaphor_hope": ("0x0a1a1a", "0x1a3a3a"),
            "contrast_enemy": ("0x0a0a1a", "0x1a1a2a"),
            "challenge": ("0x1a1a0a", "0x3a3a1a"),
            "hope_warmth": ("0x1a1a0a", "0x3a3a2a"),
            "emotional_peak": ("0x2a1a1a", "0x4a2a2a"),
            "confident": ("0x0a1a2a", "0x1a3a4a"),
            "intimate_to_conviction": ("0x1a0a1a", "0x3a1a3a"),
            "determined_inclusive": ("0x0a1a0a", "0x1a3a1a"),
            "urgency_scarcity": ("0x1a1a0a", "0x3a3a1a"),
            "invitation_action": ("0x1a2a1a", "0x2a4a2a"),
            "closing_warm": ("0x1a1a2a", "0x2a2a4a")
        }
        return mood_colors.get(mood, ("0x0a0a1a", "0x1a1a2a"))

    def grammar_check(self, text: str) -> str:
        """
        Grammar and style check for subtitles - Grammarly CLI style
        Fixes common issues automatically
        """
        fixed = text

        # === GRAMMAR FIXES ===

        # Fix double spaces
        while "  " in fixed:
            fixed = fixed.replace("  ", " ")

        # Fix sentence case after periods
        import re
        fixed = re.sub(r'\.(\s+)([a-z])', lambda m: f'.{m.group(1)}{m.group(2).upper()}', fixed)

        # Fix common contractions that sound weird in TTS
        # "It's" is fine, but ensure consistency

        # Fix missing periods at end of sentences
        if fixed and fixed[-1] not in '.!?':
            fixed = fixed + '.'

        # Fix comma splices (very basic)
        # "This is great, this is amazing" -> "This is great. This is amazing."

        # === STYLE FIXES ===

        # Remove filler words that weaken the message
        filler_patterns = [
            (r'\bjust\b', ''),           # "just" often weakens
            (r'\breally\b', ''),          # "really" is filler
            (r'\bvery\b', ''),            # "very" is weak
            (r'\bactually\b', ''),        # "actually" is filler
            (r'\bbasically\b', ''),       # "basically" is filler
        ]

        # Note: Apply these carefully - sometimes they're intentional
        # For now, we skip aggressive removal

        # === PUNCTUATION FIXES ===

        # Fix multiple punctuation
        fixed = re.sub(r'\.{2,}', '...', fixed)  # Multiple dots -> ellipsis
        fixed = re.sub(r'\?{2,}', '?', fixed)    # Multiple ? -> single
        fixed = re.sub(r'!{2,}', '!', fixed)     # Multiple ! -> single

        # Fix space before punctuation
        fixed = re.sub(r'\s+([.,!?;:])', r'\1', fixed)

        # Fix missing space after punctuation
        fixed = re.sub(r'([.,!?;:])([A-Za-z])', r'\1 \2', fixed)

        # === SPECIFIC FIXES FOR THIS PITCH ===

        # Ensure "LUMINA" is capitalized consistently in subtitles
        fixed = re.sub(r'\blumina\b', 'LUMINA', fixed, flags=re.IGNORECASE)

        # Fix "AI" capitalization
        fixed = re.sub(r'\bai\b', 'AI', fixed)
        fixed = re.sub(r'\bAi\b', 'AI', fixed)

        # Clean up result
        fixed = " ".join(fixed.split())

        return fixed

    def clean_text_for_ffmpeg(self, text: str, max_chars_per_line: int = 45) -> str:
        """Clean and format text for FFmpeg drawtext filter"""
        # First, apply grammar check
        clean = self.grammar_check(text)

        # FFmpeg drawtext requires specific escaping
        # Remove or replace characters that cause issues
        replacements = [
            ("'", ""),           # Remove apostrophes (FFmpeg issue)
            ('"', ""),           # Remove quotes (FFmpeg issue)
            (":", " -"),         # Replace colons (FFmpeg issue)
            ("%", " percent"),   # Replace percent (FFmpeg issue)
            ("\\", ""),          # Remove backslashes
            ("[", ""),           # Remove brackets
            ("]", ""),           # Remove brackets
            ("...", "..."),      # Keep ellipsis clean
        ]

        for old, new in replacements:
            clean = clean.replace(old, new)

        # Clean up extra spaces
        clean = " ".join(clean.split())

        # Word wrap for multi-line display
        words = clean.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 > max_chars_per_line:
                if current_line:
                    lines.append(" ".join(current_line))
                current_line = [word]
                current_length = len(word)
            else:
                current_line.append(word)
                current_length += len(word) + 1

        if current_line:
            lines.append(" ".join(current_line))

        # Limit to 3 lines max
        lines = lines[:3]

        # Join with FFmpeg newline escape
        return "\\n".join(lines)

    def create_scene_video(self, scene: Dict, voice: str = "en-US-GuyNeural") -> Optional[Path]:
        try:
            """Create video for a single scene"""

            scene_id = f"v2_scene_{scene['id']}_{int(time.time() * 1000)}"
            audio_file = self.audio_dir / f"{scene_id}.mp3"
            video_file = self.temp_dir / f"{scene_id}.mp4"

            text = scene["text"]
            mood = scene["mood"]
            colors = self.get_mood_colors(mood)

            logger.info(f"📝 Scene {scene['id']}: {text[:40]}...")

            # Generate voiceover
            if self.tts_available:
                success = self.generate_voiceover(text, audio_file, voice)
                if success:
                    duration = self.get_audio_duration(audio_file) + 1.0  # Add pause
                else:
                    duration = scene.get("duration", 5.0)
                    audio_file = None
            else:
                duration = scene.get("duration", 5.0)
                audio_file = None

            # Clean text for FFmpeg subtitles
            safe_text = self.clean_text_for_ffmpeg(text)

            # Video filter with gradient background and text
            vf = (
                f"drawbox=x=0:y={self.height-220}:w={self.width}:h=220:color=black@0.75:t=fill,"
                f"drawtext=text='{safe_text}':"
                f"fontsize=38:fontcolor=white:"
                f"x=(w-text_w)/2:y={self.height-180}:"
                f"font=Arial:"
                f"line_spacing=12:"
                f"shadowcolor=black@0.9:shadowx=3:shadowy=3"
            )

            if audio_file and audio_file.exists():
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c={colors[0]}:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-i', str(audio_file),
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-c:a', 'aac', '-b:a', '192k',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    '-shortest',
                    str(video_file)
                ]
            else:
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c={colors[0]}:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-vf', vf,
                    '-c:v', 'libx264', '-preset', 'fast', '-crf', '23',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

            if not video_file.exists():
                scene_num = scene['id']
                logger.warning(f"   ⚠️ Scene {scene_num} failed, using simple fallback")
                # Simpler fallback
                simple_vf = (
                    f"drawtext=text='Scene {scene_num}':"
                    f"fontsize=48:fontcolor=white:"
                    f"x=(w-text_w)/2:y=(h-text_h)/2:"
                    f"font=Arial"
                )
                cmd = [
                    'ffmpeg', '-y',
                    '-f', 'lavfi',
                    '-i', f'color=c={colors[0]}:s={self.width}x{self.height}:d={duration}:r={self.fps}',
                    '-vf', simple_vf,
                    '-c:v', 'libx264', '-preset', 'fast',
                    '-t', str(duration),
                    '-pix_fmt', 'yuv420p',
                    str(video_file)
                ]
                subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            return video_file if video_file.exists() else None

        except Exception as e:
            self.logger.error(f"Error in create_scene_video: {e}", exc_info=True)
            raise
    def generate_pitch_video(self, voice: str = "en-US-GuyNeural") -> Dict[str, Any]:
        """Generate complete Enhanced Pitch v2.0 video"""

        logger.info("🎬 Generating ENHANCED PITCH v2.0")
        logger.info(f"   Scenes: {len(PITCH_SCENES_V2)}")

        # Run grammar check on all scenes FIRST
        checked_scenes = grammar_check_all_scenes(PITCH_SCENES_V2)

        output_filename = f"LUMINA_Enhanced_Pitch_v2_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        output_path = self.output_dir / output_filename

        try:
            scene_videos = []

            for scene in checked_scenes:
                video_path = self.create_scene_video(scene, voice)
                if video_path:
                    scene_videos.append(video_path)

            if not scene_videos:
                return {"error": "No scenes created"}

            # Concatenate
            logger.info("🔗 Assembling final video...")

            concat_file = self.temp_dir / f"concat_v2_{int(time.time())}.txt"
            with open(concat_file, 'w') as f:
                for vid in scene_videos:
                    f.write(f"file '{vid}'\n")

            cmd = [
                'ffmpeg', '-y',
                '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c:v', 'libx264', '-preset', 'medium', '-crf', '18',
                '-c:a', 'aac', '-b:a', '192k',
                '-pix_fmt', 'yuv420p',
                str(output_path)
            ]

            subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if not output_path.exists():
                return {"error": "Final video not created"}

            file_size = output_path.stat().st_size
            file_size_mb = file_size / (1024 * 1024)

            # Calculate total duration
            total_duration = sum(s.get("duration", 5.0) for s in PITCH_SCENES_V2)

            logger.info(f"✅ Enhanced Pitch v2.0 Created!")
            logger.info(f"   📁 {output_path}")
            logger.info(f"   📊 Size: {file_size_mb:.2f} MB")
            logger.info(f"   ⏱️  Duration: ~{total_duration:.0f}s")

            return {
                "success": True,
                "output_file": str(output_path),
                "file_size_mb": round(file_size_mb, 2),
                "duration_seconds": total_duration,
                "scenes": len(scene_videos),
                "version": "2.0",
                "experts_incorporated": ["The Doc (Psychology)", "Speech Pathologist", "Wes Roth", "Dylan Curious"]
            }

        except Exception as e:
            logger.error(f"❌ Failed: {e}")
            import traceback
            traceback.print_exc()
            return {"error": str(e)}


def print_pitch_script():
    """Print the enhanced pitch script with delivery notes"""
    print("="*70)
    print("📜 LUMINA ENHANCED PITCH v2.0 - FULL SCRIPT")
    print("="*70)
    print()
    print("EXPERTS INCORPORATED:")
    print("  🩺 The Doc (Psychology) - Urgency, social proof, CTA")
    print("  🎤 Speech Pathologist - Pauses, energy, delivery")
    print("  🎙️ Wes Roth - 'Category 9 earthquake' urgency")
    print("  🎙️ Dylan Curious - '2026 authenticity' hope")
    print()
    print("-"*70)

    for scene in PITCH_SCENES_V2:
        print(f"\n[SCENE {scene['id']}] - Energy: {'█' * scene['energy']}{'░' * (10-scene['energy'])} {scene['energy']}/10")
        print(f"  Mood: {scene['mood']}")
        print(f"  Text: \"{scene['text']}\"")
        print(f"  🎤 Delivery: {scene['delivery_notes']}")
        print(f"  ⏱️  Duration: {scene['duration']}s")

    print()
    print("-"*70)
    total_duration = sum(s["duration"] for s in PITCH_SCENES_V2)
    print(f"\n📊 TOTAL DURATION: ~{total_duration:.0f} seconds ({total_duration/60:.1f} minutes)")
    print(f"📊 SCENES: {len(PITCH_SCENES_V2)}")
    print()


def main():
    print_pitch_script()

    print("="*70)
    print("🎬 GENERATING VIDEO...")
    print("="*70)

    generator = EnhancedPitchV2Generator()
    result = generator.generate_pitch_video(voice="en-US-GuyNeural")

    print()
    print("="*70)
    if result.get("success"):
        print("✅ ENHANCED PITCH v2.0 COMPLETE!")
        print(f"   📁 {result['output_file']}")
        print(f"   📊 {result['file_size_mb']:.2f} MB")
        print(f"   ⏱️  ~{result['duration_seconds']:.0f} seconds")
        print(f"   🎯 Experts: {', '.join(result['experts_incorporated'])}")
    else:
        print(f"❌ Failed: {result.get('error')}")
    print("="*70)


if __name__ == "__main__":



    main()