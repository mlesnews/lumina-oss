#!/usr/bin/env python3
"""
Video Production Integration
Integration tools for actual video/animation production

Supports:
- AI video generation prompts (Runway, Pika, etc.)
- Animation software integration
- Voice synthesis prompts
- Music generation prompts
- Asset generation

Tags: #VIDEOPRODUCTION #AIGENERATION #ANIMATION @LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VideoProductionIntegration")


@dataclass
class VideoGenerationPrompt:
    """Prompt for AI video generation"""
    scene_description: str
    style_reference: str
    duration_seconds: int
    camera_movement: str = ""
    character_actions: List[str] = field(default_factory=list)
    background_description: str = ""
    mood: str = ""
    color_palette: str = ""


@dataclass
class AnimationAsset:
    """Animation asset specification"""
    asset_type: str  # character, background, prop, effect
    name: str
    description: str
    style_notes: str = ""
    reference_images: List[str] = field(default_factory=list)


class VideoProductionIntegration:
    """
    Integration tools for video production

    Generates prompts and specifications for:
    - AI video generation (Runway, Pika, etc.)
    - Animation software
    - Voice synthesis
    - Music generation
    """

    def __init__(self):
        self.logger = get_logger("VideoProductionIntegration")

        # 80s/90s Cartoon Network / Crunchyroll style references
        self.style_references = {
            "80s_cartoon_network": "Vibrant colors, cel animation, exaggerated expressions, dynamic action lines",
            "90s_anime": "Detailed backgrounds, expressive characters, dramatic camera angles, speed lines",
            "crunchyroll_modern": "Modern anime polish with 80s/90s aesthetic, high quality animation",
            "color_palette": "Saturated colors: bright blues, vibrant purples, electric greens, warm oranges",
            "animation_style": "Smooth 2D animation with cel-shaded look, expressive character movements"
        }

    def generate_video_prompt(self, scene: Dict[str, Any]) -> VideoGenerationPrompt:
        """
        Generate AI video generation prompt from scene

        Args:
            scene: Scene dictionary from episode script

        Returns:
            VideoGenerationPrompt for AI video generation
        """
        # Combine visual description with style
        style_ref = f"{self.style_references['80s_cartoon_network']}, {self.style_references['90s_anime']}"

        # Extract camera movement from animation notes
        camera_movement = ""
        if "camera" in scene.get("animation_notes", "").lower():
            if "wide" in scene["animation_notes"].lower():
                camera_movement = "Cinematic wide shot, slow pan"
            elif "close" in scene["animation_notes"].lower():
                camera_movement = "Close-up, dramatic focus"
            elif "dynamic" in scene["animation_notes"].lower():
                camera_movement = "Dynamic camera movement, speed lines, impact frames"

        # Extract character actions from dialogue
        character_actions = []
        for dialogue in scene.get("dialogue", []):
            character = dialogue.get("character", "")
            if character and character != "Narrator":
                character_actions.append(f"{character} speaking expressively")

        prompt = VideoGenerationPrompt(
            scene_description=scene.get("visual_description", scene.get("description", "")),
            style_reference=style_ref,
            duration_seconds=int(scene.get("duration_seconds", 30)),
            camera_movement=camera_movement or "Smooth anime-style camera work",
            character_actions=character_actions,
            background_description=scene.get("visual_description", ""),
            mood=self._extract_mood(scene),
            color_palette=self.style_references["color_palette"]
        )

        return prompt

    def _extract_mood(self, scene: Dict[str, Any]) -> str:
        """Extract mood from scene"""
        desc = scene.get("description", "").lower() + " " + scene.get("visual_description", "").lower()

        if any(word in desc for word in ["epic", "inspiring", "stars", "space"]):
            return "Epic, inspiring, spacefaring"
        elif any(word in desc for word in ["discover", "learn", "understand"]):
            return "Educational, curious, discovery"
        elif any(word in desc for word in ["dramatic", "intense", "action"]):
            return "Dramatic, intense, action-packed"
        else:
            return "Engaging, educational, entertaining"

    def generate_ai_video_prompt_text(self, prompt: VideoGenerationPrompt) -> str:
        """
        Generate text prompt for AI video generation tools

        Format optimized for Runway, Pika, Stable Video, etc.
        """
        prompt_text = f"""Create an anime-style video scene:

SCENE: {prompt.scene_description}

STYLE: {prompt.style_reference}
- 80s/90s Cartoon Network / Crunchyroll anime aesthetic
- Vibrant, saturated color palette: {prompt.color_palette}
- Cel-shaded 2D animation style with modern polish
- Expressive character animations
- Dynamic camera work: {prompt.camera_movement}

CHARACTERS: {', '.join(prompt.character_actions) if prompt.character_actions else 'Main character exploring dimensions'}

MOOD: {prompt.mood}

BACKGROUND: {prompt.background_description}

DURATION: {prompt.duration_seconds} seconds
ANIMATION: Smooth, expressive, with speed lines and impact frames
COLOR: Vibrant, saturated, high contrast
CAMERA: {prompt.camera_movement}
"""
        return prompt_text

    def generate_voice_synthesis_prompt(self, dialogue: Dict[str, str], character: str) -> Dict[str, Any]:
        """
        Generate voice synthesis prompt

        Args:
            dialogue: {"character": "...", "line": "..."}
            character: Character name

        Returns:
            Voice synthesis specification
        """
        # Character voice profiles (80s/90s anime style)
        voice_profiles = {
            "Alex": {
                "age": "young adult",
                "gender": "neutral",
                "tone": "curious, energetic, determined",
                "style": "80s anime protagonist - expressive, emotional"
            },
            "Narrator": {
                "age": "adult",
                "gender": "neutral",
                "tone": "wise, engaging, educational",
                "style": "Classic anime narrator - dramatic but clear"
            },
            "Guide": {
                "age": "adult",
                "gender": "neutral",
                "tone": "helpful, knowledgeable, patient",
                "style": "Mentor character - warm and encouraging"
            },
            "Space Captain": {
                "age": "adult",
                "gender": "neutral",
                "tone": "inspiring, confident, spacefaring",
                "style": "Leader character - strong and visionary"
            }
        }

        profile = voice_profiles.get(character, voice_profiles["Alex"])

        return {
            "character": character,
            "line": dialogue.get("line", ""),
            "voice_profile": profile,
            "emotion": self._extract_emotion(dialogue.get("line", "")),
            "style_notes": f"80s/90s anime voice acting style: {profile['style']}",
            "audio_settings": {
                "sample_rate": 44100,
                "bit_depth": 16,
                "format": "wav"
            }
        }

    def _extract_emotion(self, line: str) -> str:
        """Extract emotion from dialogue line"""
        line_lower = line.lower()

        if any(word in line_lower for word in ["!", "amazing", "wow", "incredible"]):
            return "excited, enthusiastic"
        elif any(word in line_lower for word in ["?", "wonder", "curious", "how"]):
            return "curious, questioning"
        elif any(word in line_lower for word in ["understand", "learn", "teach"]):
            return "thoughtful, learning"
        elif any(word in line_lower for word in ["stars", "space", "journey"]):
            return "inspiring, determined"
        else:
            return "neutral, engaging"

    def generate_music_prompt(self, scene: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate music composition prompt

        Args:
            scene: Scene dictionary

        Returns:
            Music generation specification
        """
        music_cue = scene.get("music_cue", "")

        # Extract music style from cue
        if "80s synth" in music_cue.lower() or "synth-pop" in music_cue.lower():
            style = "80s synth-pop with anime orchestral elements"
            instruments = ["synthesizer", "drum machine", "orchestral strings", "brass"]
            tempo = "upbeat, 120-140 BPM"
        elif "orchestral" in music_cue.lower() or "epic" in music_cue.lower():
            style = "Epic orchestral anime soundtrack"
            instruments = ["full orchestra", "choir", "brass section", "strings"]
            tempo = "moderate to fast, 100-120 BPM"
        elif "thoughtful" in music_cue.lower() or "calm" in music_cue.lower():
            style = "Thoughtful, reflective anime music"
            instruments = ["piano", "strings", "woodwinds"]
            tempo = "slow to moderate, 60-90 BPM"
        else:
            style = "80s/90s anime soundtrack style"
            instruments = ["synthesizer", "orchestral elements", "electric guitar"]
            tempo = "moderate, 100-120 BPM"

        return {
            "scene": scene.get("title", ""),
            "style": style,
            "instruments": instruments,
            "tempo": tempo,
            "mood": self._extract_mood(scene),
            "duration_seconds": scene.get("duration_seconds", 30),
            "reference": "80s/90s Cartoon Network and Crunchyroll anime soundtracks",
            "prompt_text": f"Compose {style} music for anime scene. Mood: {self._extract_mood(scene)}. Instruments: {', '.join(instruments)}. Tempo: {tempo}. Duration: {scene.get('duration_seconds', 30)} seconds. Reference: 80s/90s anime soundtracks."
        }

    def generate_asset_specifications(self, script: Dict[str, Any]) -> List[AnimationAsset]:
        """
        Generate animation asset specifications from episode script

        Args:
            script: Episode script dictionary

        Returns:
            List of AnimationAsset specifications
        """
        assets = []

        # Main character
        assets.append(AnimationAsset(
            asset_type="character",
            name="Alex (The Quantum Explorer)",
            description="Main protagonist - young explorer discovering dimensions. Expressive, large eyes, dynamic poses.",
            style_notes="80s/90s Cartoon Network / Crunchyroll style: vibrant colors, expressive features, anime aesthetic"
        ))

        # Extract other characters from dialogue
        characters_seen = set()
        for scene in script.get("scenes", []):
            for dialogue in scene.get("dialogue", []):
                char = dialogue.get("character", "")
                if char and char not in characters_seen and char != "Alex":
                    characters_seen.add(char)
                    assets.append(AnimationAsset(
                        asset_type="character",
                        name=char,
                        description=f"Supporting character: {char}. 80s/90s anime style.",
                        style_notes="Matching main character style, expressive, vibrant"
                    ))

        # Backgrounds
        assets.append(AnimationAsset(
            asset_type="background",
            name="Dimensional Space",
            description="Abstract dimensional space with vibrant colors, geometric patterns, representing different dimensions",
            style_notes="80s/90s anime background style: detailed, atmospheric, vibrant colors"
        ))

        assets.append(AnimationAsset(
            asset_type="background",
            name="Space Scene",
            description="Epic space scene with stars, galaxies, spacecraft - inspiring and beautiful",
            style_notes="Cinematic space background, detailed, atmospheric"
        ))

        # Effects
        assets.append(AnimationAsset(
            asset_type="effect",
            name="Speed Lines",
            description="Dynamic speed lines for action and movement - classic 80s/90s anime effect",
            style_notes="Bold, dynamic, high contrast"
        ))

        assets.append(AnimationAsset(
            asset_type="effect",
            name="Impact Frames",
            description="Impact frames for dramatic moments - screen flash, impact effects",
            style_notes="High contrast, dramatic, 80s/90s anime style"
        ))

        assets.append(AnimationAsset(
            asset_type="effect",
            name="Dimensional Portal",
            description="Portal effect for dimensional transitions - swirling colors, geometric patterns",
            style_notes="Vibrant, dynamic, dimensional"
        ))

        return assets

    def generate_production_manifest(self, script_path: Path) -> Dict[str, Any]:
        try:
            """
            Generate complete production manifest for an episode

            Args:
                script_path: Path to episode script JSON

            Returns:
                Complete production manifest
            """
            with open(script_path, 'r', encoding='utf-8') as f:
                script = json.load(f)

            # Generate all prompts and specifications
            video_prompts = []
            voice_prompts = []
            music_prompts = []

            for scene in script.get("scenes", []):
                # Video prompt
                video_prompt = self.generate_video_prompt(scene)
                video_prompts.append({
                    "scene_number": scene.get("scene_number"),
                    "prompt_text": self.generate_ai_video_prompt_text(video_prompt),
                    "duration_seconds": video_prompt.duration_seconds
                })

                # Voice prompts
                for dialogue in scene.get("dialogue", []):
                    voice_prompt = self.generate_voice_synthesis_prompt(
                        dialogue, 
                        dialogue.get("character", "Alex")
                    )
                    voice_prompts.append(voice_prompt)

                # Music prompt
                music_prompt = self.generate_music_prompt(scene)
                music_prompts.append(music_prompt)

            # Assets
            assets = self.generate_asset_specifications(script)

            manifest = {
                "episode": f"S{script.get('season_number', 0):02d}E{script.get('episode_number', 0):02d}",
                "title": script.get("title", ""),
                "production_team": script.get("team_credits", []),
                "video_generation": {
                    "total_scenes": len(video_prompts),
                    "prompts": video_prompts,
                    "total_duration_seconds": sum(p["duration_seconds"] for p in video_prompts)
                },
                "voice_synthesis": {
                    "total_lines": len(voice_prompts),
                    "characters": list(set(p["character"] for p in voice_prompts)),
                    "prompts": voice_prompts
                },
                "music_composition": {
                    "total_tracks": len(music_prompts),
                    "prompts": music_prompts
                },
                "animation_assets": [
                    {
                        "type": asset.asset_type,
                        "name": asset.name,
                        "description": asset.description,
                        "style_notes": asset.style_notes
                    }
                    for asset in assets
                ],
                "commercial_breaks": script.get("commercial_breaks", []),
                "style_guide": {
                    "animation_style": "80s/90s Cartoon Network cel animation with modern Crunchyroll polish",
                    "color_palette": "Vibrant, saturated colors with high contrast",
                    "reference": "80s/90s Cartoon Network and Crunchyroll anime"
                }
            }

            return manifest


        except Exception as e:
            self.logger.error(f"Error in generate_production_manifest: {e}", exc_info=True)
            raise
def main():
    try:
        """Generate production manifests for episodes"""
        integration = VideoProductionIntegration()

        # Find episode scripts
        scripts_dir = script_dir / "anime_production" / "episodes" / "scripts"

        if not scripts_dir.exists():
            print(f"❌ Scripts directory not found: {scripts_dir}")
            print("   Run anime_video_production_pipeline.py first to generate scripts")
            return

        # Generate manifest for first episode
        script_files = list(scripts_dir.glob("S*.json"))
        if not script_files:
            print("❌ No episode scripts found")
            return

        print("="*80)
        print("VIDEO PRODUCTION INTEGRATION")
        print("Generating production manifests for AI video generation")
        print("="*80)

        for script_file in script_files[:1]:  # Process first episode as example
            print(f"\n📋 Processing: {script_file.name}")

            manifest = integration.generate_production_manifest(script_file)

            # Save manifest
            manifest_dir = script_dir / "anime_production" / "manifests"
            manifest_dir.mkdir(parents=True, exist_ok=True)

            manifest_path = manifest_dir / f"manifest_{manifest['episode']}.json"
            with open(manifest_path, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)

            print(f"✅ Manifest generated: {manifest_path}")
            print(f"   Video Scenes: {manifest['video_generation']['total_scenes']}")
            print(f"   Voice Lines: {manifest['voice_synthesis']['total_lines']}")
            print(f"   Music Tracks: {manifest['music_composition']['total_tracks']}")
            print(f"   Assets: {len(manifest['animation_assets'])}")

            # Show example video prompt
            if manifest['video_generation']['prompts']:
                print(f"\n📹 Example Video Generation Prompt:")
                print("-" * 80)
                print(manifest['video_generation']['prompts'][0]['prompt_text'])
                print("-" * 80)

        print("\n" + "="*80)
        print("✅ Production manifests ready for AI video generation!")
        print("="*80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()