#!/usr/bin/env python3
"""
Video Script Generator - Creates 40-minute episode scripts with commercial integration

Generates complete video scripts for Quantum Dimensions anime series with:
- 20 minutes of educational content
- 20 minutes of commercials (2-minute intervals)
- 80s/90s Cartoon Network & Crunchyroll style
- Team coordination (Michelle, team members)

Tags: #VIDEOSCRIPT #PRODUCTION #ANIME #80s90s #CARTOONNETWORK #CRUNCHYROLL
      @LUMINA @JARVIS #QUANTUMDIMENSIONS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

# Add project root to path
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

logger = get_logger("VideoScriptGenerator")


@dataclass
class ScriptLine:
    """Individual script line"""
    timestamp: str  # MM:SS format
    character: str  # Character name or "NARRATOR"
    dialogue: str
    action: str = ""  # Stage directions
    animation_notes: str = ""
    sound_effect: str = ""
    music_cue: str = ""


@dataclass
class CommercialScript:
    """Commercial script (2 minutes)"""
    break_number: int
    commercial_type: str
    script_lines: List[ScriptLine] = field(default_factory=list)
    visuals: List[str] = field(default_factory=list)
    music: str = ""
    call_to_action: str = ""


@dataclass
class EpisodeScript:
    """Complete episode script"""
    episode_id: str
    title: str
    season: int
    episode: int
    content_script: List[ScriptLine] = field(default_factory=list)
    commercial_scripts: List[CommercialScript] = field(default_factory=list)
    style_notes: Dict[str, Any] = field(default_factory=dict)
    total_duration_minutes: int = 40


class VideoScriptGenerator:
    """
    Generates video scripts with 80s/90s Cartoon Network & Crunchyroll style
    """

    def __init__(self):
        """Initialize script generator"""
        self.logger = get_logger("VideoScriptGenerator")

        # 80s/90s Cartoon Network style elements
        self.style_elements = {
            "opening_style": "Neon glow title card with synthesizer music",
            "transition_style": "Wipe transitions, screen shakes, impact frames",
            "character_intro": "Dramatic pose with speed lines",
            "educational_moment": "Screen split with visual metaphor",
            "closing_style": "Next episode preview with retro graphics"
        }

        # Commercial templates
        self.commercial_templates = self._load_commercial_templates()

    def _load_commercial_templates(self) -> Dict[str, List[str]]:
        """Load commercial script templates"""
        return {
            "sponsor": [
                "[UPBEAT 80s SYNTH MUSIC]",
                "This episode of Quantum Dimensions is brought to you by [SPONSOR]!",
                "[VISUAL: Sponsor logo with neon glow]",
                "Supporting quantum education for the next generation!",
                "[CALL TO ACTION]"
            ],
            "lumina_product": [
                "[FUTURISTIC MUSIC]",
                "Discover the LUMINA ecosystem!",
                "[VISUAL: JARVIS, KAIJU, ULTRON logos]",
                "Where AI meets reality - JARVIS, KAIJU, ULTRON, and more!",
                "Visit lumina.ai to learn more!"
            ],
            "educational": [
                "[INSPIRATIONAL MUSIC]",
                "Master quantum dimensions with our certification program!",
                "[VISUAL: Certification badges]",
                "Learn 10x faster with bio-imprinting techniques!",
                "Enroll at quantumdimensions.edu today!"
            ],
            "merchandise": [
                "[CATCHY JINGLE]",
                "Get your Quantum Dimensions merchandise!",
                "[VISUAL: T-shirts, posters, collectibles]",
                "Show your love for quantum physics!",
                "Shop at quantumdimensions.shop!"
            ],
            "next_episode": [
                "[SUSPENSE MUSIC]",
                "Next time on Quantum Dimensions...",
                "[VISUAL: Preview clips]",
                "[NEXT EPISODE TITLE]",
                "Don't miss it! Subscribe and hit the notification bell!"
            ],
            "certification": [
                "[EPIC MUSIC]",
                "Earn your spacefaring certification!",
                "[VISUAL: Space travel imagery]",
                "Prepare for the stars - start your journey today!",
                "Visit quantumdimensions.edu/certification"
            ]
        }

    def generate_episode_script(self, episode_data: Dict[str, Any],
                               curriculum_episode: Optional[Dict[str, Any]] = None) -> EpisodeScript:
        """
        Generate complete episode script

        Args:
            episode_data: Episode production data
            curriculum_episode: Curriculum episode data

        Returns:
            EpisodeScript
        """
        episode_id = episode_data.get("episode_id", "S01E01")
        title = episode_data.get("title", "Episode")
        season = episode_data.get("season", 1)
        episode_num = episode_data.get("episode", 1)

        script = EpisodeScript(
            episode_id=episode_id,
            title=title,
            season=season,
            episode=episode_num
        )

        # Generate content script (20 minutes)
        content_script = self._generate_content_script(
            episode_data, curriculum_episode
        )
        script.content_script = content_script

        # Generate commercial scripts (20 minutes, 10 breaks)
        commercial_scripts = self._generate_commercial_scripts(episode_data)
        script.commercial_scripts = commercial_scripts

        # Add style notes
        script.style_notes = {
            "era": "80s_90s_cartoon_network",
            "animation_style": "hand_drawn_traditional",
            "color_palette": ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"],
            "effects": ["screen_shake", "speed_lines", "impact_frames", "sparkle_effects"],
            "music_style": "synthesizer_heavy_80s_90s",
            "sound_effects": "classic_cartoon_sfx"
        }

        return script

    def _generate_content_script(self, episode_data: Dict[str, Any],
                                 curriculum_episode: Optional[Dict[str, Any]]) -> List[ScriptLine]:
        """Generate 20-minute content script"""
        script_lines = []
        current_time_seconds = 0.0

        # Opening (30 seconds)
        script_lines.append(ScriptLine(
            timestamp=self._format_time(current_time_seconds),
            character="NARRATOR",
            dialogue="Previously on Quantum Dimensions...",
            action="[FADE IN: Recap montage]",
            music_cue="[THEME MUSIC - 80s SYNTH]"
        ))
        current_time_seconds += 30

        script_lines.append(ScriptLine(
            timestamp=self._format_time(current_time_seconds),
            character="NARRATOR",
            dialogue=f"Quantum Dimensions: {episode_data.get('title', 'Episode')}",
            action="[TITLE CARD: Neon glow effect, 80s style]",
            animation_notes="Bold black outlines, cel shading, large expressive eyes",
            music_cue="[THEME MUSIC CONTINUES]"
        ))
        current_time_seconds += 30

        # Main content (19 minutes)
        segments = episode_data.get("content_segments", [])

        for segment in segments[:10]:  # 10 segments × ~2 minutes each
            segment_script = self._generate_segment_script(
                segment, curriculum_episode, current_time_seconds
            )
            script_lines.extend(segment_script)
            current_time_seconds += segment.get("duration_minutes", 2.0) * 60

        return script_lines

    def _generate_segment_script(self, segment: Dict[str, Any],
                                 curriculum_episode: Optional[Dict[str, Any]],
                                 start_time: float) -> List[ScriptLine]:
        """Generate script for a content segment (~2 minutes)"""
        lines = []
        current_time = float(start_time)

        # Opening line
        lines.append(ScriptLine(
            timestamp=self._format_time(current_time),
            character="ALEX",
            dialogue="I can't believe we're exploring dimensions!",
            action="[ALEX in dramatic pose with speed lines]",
            animation_notes="80s style: exaggerated proportions, bold outlines"
        ))
        current_time += 15

        # Educational content
        if curriculum_episode:
            learning_obj = curriculum_episode.get("learning_objectives", [])
            if learning_obj:
                lines.append(ScriptLine(
                    timestamp=self._format_time(current_time),
                    character="NARRATOR",
                    dialogue=f"Today we're learning: {learning_obj[0]}",
                    action="[SCREEN SPLIT: Visual metaphor appears]",
                    animation_notes="Educational moment - clear visual explanation"
                ))
                current_time += 20

        # Story progression
        lines.append(ScriptLine(
            timestamp=self._format_time(current_time),
            character="ALEX",
            dialogue="This is amazing! I can see how dimensions work!",
            action="[VISUAL: Dimensional visualization]",
            sound_effect="[SPARKLE EFFECT]",
            animation_notes="80s sparkle effects, motion blur"
        ))
        current_time += 25

        # Continue with segment content...
        # (Additional lines to fill ~2 minutes)

        return lines

    def _generate_commercial_scripts(self, episode_data: Dict[str, Any]) -> List[CommercialScript]:
        """Generate commercial scripts for all breaks"""
        commercials = []
        commercial_breaks = episode_data.get("commercial_breaks", [])

        for break_data in commercial_breaks:
            comm_type = break_data.get("commercial_type", "sponsor")
            commercial = CommercialScript(
                break_number=break_data.get("break_number", 1),
                commercial_type=comm_type
            )

            # Generate script lines from template
            template = self.commercial_templates.get(comm_type, self.commercial_templates["sponsor"])

            current_time = 0
            for line_text in template:
                if line_text.startswith("["):
                    # Action/music cue
                    if "MUSIC" in line_text:
                        commercial.music = line_text
                    else:
                        commercial.visuals.append(line_text)
                else:
                    # Dialogue
                    commercial.script_lines.append(ScriptLine(
                        timestamp=self._format_time(current_time),
                        character="NARRATOR",
                        dialogue=line_text,
                        action=commercial.visuals[-1] if commercial.visuals else ""
                    ))
                    current_time += 24  # ~24 seconds per line for 2-minute commercial

            commercial.call_to_action = break_data.get("call_to_action", "Learn more")
            commercials.append(commercial)

        return commercials

    def _format_time(self, seconds: float) -> str:
        """Format seconds to MM:SS"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"

    def export_script(self, script: EpisodeScript, output_path: Path) -> None:
        try:
            """Export script to text file"""
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n")
                f.write(f"QUANTUM DIMENSIONS - EPISODE SCRIPT\n")
                f.write(f"{script.episode_id}: {script.title}\n")
                f.write("="*80 + "\n\n")

                f.write("STYLE GUIDE: 80s/90s Cartoon Network & Crunchyroll\n")
                f.write("- Hand-drawn traditional animation\n")
                f.write("- Bold black outlines, cel shading\n")
                f.write("- Large expressive eyes, exaggerated proportions\n")
                f.write("- Synthesizer-heavy 80s/90s music\n")
                f.write("- Classic cartoon sound effects\n")
                f.write("- Neon glow effects, wipe transitions\n\n")

                f.write("="*80 + "\n")
                f.write("CONTENT SCRIPT (20 minutes)\n")
                f.write("="*80 + "\n\n")

                for line in script.content_script:
                    f.write(f"[{line.timestamp}] {line.character}\n")
                    if line.action:
                        f.write(f"ACTION: {line.action}\n")
                    f.write(f"{line.dialogue}\n")
                    if line.animation_notes:
                        f.write(f"ANIMATION: {line.animation_notes}\n")
                    if line.sound_effect:
                        f.write(f"SFX: {line.sound_effect}\n")
                    if line.music_cue:
                        f.write(f"MUSIC: {line.music_cue}\n")
                    f.write("\n")

                f.write("\n" + "="*80 + "\n")
                f.write("COMMERCIAL BREAKS (20 minutes total, 10 breaks × 2 min)\n")
                f.write("="*80 + "\n\n")

                for commercial in script.commercial_scripts:
                    f.write(f"COMMERCIAL BREAK #{commercial.break_number} ({commercial.commercial_type})\n")
                    f.write("-" * 80 + "\n")
                    if commercial.music:
                        f.write(f"{commercial.music}\n")
                    for line in commercial.script_lines:
                        f.write(f"[{line.timestamp}] {line.character}: {line.dialogue}\n")
                        if line.action:
                            f.write(f"  ACTION: {line.action}\n")
                    for visual in commercial.visuals:
                        f.write(f"VISUAL: {visual}\n")
                    f.write(f"CALL TO ACTION: {commercial.call_to_action}\n")
                    f.write("\n")

                f.write("\n" + "="*80 + "\n")
                f.write("END OF SCRIPT\n")
                f.write("="*80 + "\n")

            self.logger.info(f"✅ Script exported to {output_path}")


        except Exception as e:
            self.logger.error(f"Error in export_script: {e}", exc_info=True)
            raise
def main():
    """Generate sample video script"""
    from anime_production_tracker import AnimeProductionTracker, load_curriculum_episodes

    # Initialize tracker and generator
    tracker = AnimeProductionTracker()
    generator = VideoScriptGenerator()

    # Load curriculum
    curriculum_data = load_curriculum_episodes()

    # Create production plan for first episode
    if curriculum_data and "series" in curriculum_data:
        seasons = curriculum_data["series"].get("seasons", [])
        if seasons and seasons[0].get("episodes"):
            first_episode = seasons[0]["episodes"][0]

            episode_prod = tracker.create_episode_production(
                season=1,
                episode=1,
                title=first_episode.get("title", "The Tiny Dot"),
                curriculum_data={
                    "learning_objectives": first_episode.get("learning_objectives", []),
                    "key_concepts": first_episode.get("key_concepts", [])
                }
            )

            # Generate script
            episode_data = {
                "episode_id": episode_prod.episode_id,
                "title": episode_prod.title,
                "season": episode_prod.season_number,
                "episode": episode_prod.episode_number,
                "content_segments": [
                    {
                        "segment_number": seg.segment_number,
                        "duration_minutes": seg.duration_minutes,
                        "learning_objectives": seg.learning_objectives,
                        "key_concepts": seg.key_concepts
                    }
                    for seg in episode_prod.content_segments
                ],
                "commercial_breaks": [
                    {
                        "break_number": comm.break_number,
                        "commercial_type": comm.commercial_type.value,
                        "call_to_action": comm.call_to_action
                    }
                    for comm in episode_prod.commercial_breaks
                ]
            }

            script = generator.generate_episode_script(
                episode_data,
                curriculum_episode=first_episode
            )

            # Export script
            output_path = script_dir / f"scripts_{script.episode_id}.txt"
            generator.export_script(script, output_path)

            print("="*80)
            print("VIDEO SCRIPT GENERATED")
            print("="*80)
            print(f"\nEpisode: {script.episode_id} - {script.title}")
            print(f"Content Script Lines: {len(script.content_script)}")
            print(f"Commercial Breaks: {len(script.commercial_scripts)}")
            print(f"Style: 80s/90s Cartoon Network & Crunchyroll")
            print(f"\n✅ Script exported to: {output_path}")
            print("="*80)


if __name__ == "__main__":


    main()