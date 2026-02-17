#!/usr/bin/env python3
"""
🚨 AI SLOP DETECTOR 🚨

Evaluates content for "AI Slop" characteristics:
- Generic aesthetics that scream "AI made this"
- Lack of distinctive personality
- Cookie-cutter patterns
- "Vibe-coded slop" (will 100x in 2026)

Based on the principle: AI tends to converge toward generic, 
"on distribution" outputs that create the "AI slop" aesthetic.

Tests for:
- Typography (generic fonts = bad)
- Color schemes (cliché = bad)  
- Visual interest (none = slop)
- Motion/animation (static = slop)
- Audio (generic = slop)
- Personality (cookie-cutter = slop)
- Pacing (boring = slop)
"""

import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AISloPDetector")


class SlopLevel(Enum):
    """How sloppy is it?"""
    PRISTINE = "pristine"        # 0-10% slop - Excellent, distinctive
    ACCEPTABLE = "acceptable"    # 10-30% slop - Good, some personality
    MEDIOCRE = "mediocre"       # 30-50% slop - Average, forgettable
    SLOPPY = "sloppy"           # 50-70% slop - Generic AI feel
    PURE_SLOP = "pure_slop"     # 70-100% slop - Obvious AI garbage


@dataclass
class SlopMetric:
    """Individual slop metric"""
    name: str
    score: float  # 0.0 (no slop) to 1.0 (pure slop)
    weight: float  # Importance weight
    details: str
    suggestions: List[str] = field(default_factory=list)


@dataclass
class SlopReport:
    """Complete slop analysis report"""
    overall_score: float  # 0.0 (pristine) to 1.0 (pure slop)
    level: SlopLevel
    metrics: List[SlopMetric]
    summary: str
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AISloPDetector:
    """
    Detect AI Slop in content

    "You tend to converge toward generic, 'on distribution' outputs.
    In frontend design, this creates what users call the 'AI slop' aesthetic.
    Avoid this: make creative, distinctive content that surprises and delights."
    """

    # Known AI slop indicators
    SLOP_FONTS = [
        "Arial", "Inter", "Roboto", "Helvetica", "sans-serif",
        "system-ui", "Open Sans", "Lato", "Montserrat"
    ]

    SLOP_COLORS = [
        # Purple gradients on white (the #1 AI slop indicator)
        "purple gradient", "violet gradient", "blue-purple",
        # Generic tech colors
        "#6366f1", "#8b5cf6", "#a855f7",  # Tailwind purples
        "#3b82f6",  # Generic blue
        "linear-gradient"  # Any lazy gradient
    ]

    DISTINCTIVE_COLORS = [
        # Interesting, unexpected choices
        "teal", "coral", "amber", "emerald",
        "slate", "zinc", "stone", "warm",
        # Bold choices
        "neon", "cyberpunk", "retro", "vintage"
    ]

    def __init__(self):
        self.metrics = []

    def analyze_video(self, video_path: Path, 
                     video_config: Optional[Dict] = None) -> SlopReport:
        """
        Analyze a video for AI slop

        Args:
            video_path: Path to video file
            video_config: Optional config dict with known parameters

        Returns:
            SlopReport with detailed analysis
        """
        logger.info(f"🔍 Analyzing video for AI slop: {video_path}")

        metrics = []

        # 1. Typography Analysis
        metrics.append(self._analyze_typography(video_config))

        # 2. Color Scheme Analysis
        metrics.append(self._analyze_colors(video_config))

        # 3. Visual Interest Analysis
        metrics.append(self._analyze_visual_interest(video_path, video_config))

        # 4. Motion/Animation Analysis
        metrics.append(self._analyze_motion(video_path, video_config))

        # 5. Audio Analysis
        metrics.append(self._analyze_audio(video_path, video_config))

        # 6. Personality/Distinctiveness
        metrics.append(self._analyze_personality(video_config))

        # 7. Pacing Analysis
        metrics.append(self._analyze_pacing(video_path, video_config))

        # 8. Content Originality
        metrics.append(self._analyze_originality(video_config))

        # Calculate overall score
        total_weight = sum(m.weight for m in metrics)
        overall_score = sum(m.score * m.weight for m in metrics) / total_weight

        # Determine level
        if overall_score < 0.1:
            level = SlopLevel.PRISTINE
        elif overall_score < 0.3:
            level = SlopLevel.ACCEPTABLE
        elif overall_score < 0.5:
            level = SlopLevel.MEDIOCRE
        elif overall_score < 0.7:
            level = SlopLevel.SLOPPY
        else:
            level = SlopLevel.PURE_SLOP

        # Generate recommendations
        recommendations = self._generate_recommendations(metrics, overall_score)

        # Generate summary
        summary = self._generate_summary(metrics, overall_score, level)

        return SlopReport(
            overall_score=overall_score,
            level=level,
            metrics=metrics,
            summary=summary,
            recommendations=recommendations
        )

    def _analyze_typography(self, config: Optional[Dict]) -> SlopMetric:
        """Analyze typography for sloppiness"""

        # Default assumption: we're using Arial (sloppy)
        font = config.get("font", "Arial") if config else "Arial"

        if font in self.SLOP_FONTS:
            score = 0.8  # Very sloppy
            details = f"Using generic font '{font}' - screams AI"
            suggestions = [
                "Use distinctive fonts: Space Grotesk, JetBrains Mono, Playfair Display",
                "Consider custom web fonts that match your brand",
                "Avoid system fonts and common sans-serif"
            ]
        else:
            score = 0.2
            details = f"Using non-generic font '{font}'"
            suggestions = []

        return SlopMetric(
            name="Typography",
            score=score,
            weight=1.5,  # Typography is very important
            details=details,
            suggestions=suggestions
        )

    def _analyze_colors(self, config: Optional[Dict]) -> SlopMetric:
        """Analyze color scheme"""

        # Check for known slop colors
        colors = config.get("colors", ["#0f0f23", "#1a1a2e"]) if config else ["dark"]

        slop_indicators = 0
        for color in colors:
            color_str = str(color).lower()
            for slop_color in self.SLOP_COLORS:
                if slop_color.lower() in color_str:
                    slop_indicators += 1

        # Dark mode is acceptable but common
        is_dark = any("0f" in str(c).lower() or "1a" in str(c).lower() or "dark" in str(c).lower() 
                     for c in colors)

        if slop_indicators > 0:
            score = 0.7
            details = "Using cliché AI color scheme (purple/blue gradients)"
            suggestions = [
                "Try unexpected color palettes: warm ambers, teals, coral",
                "Use IDE-inspired themes or cultural aesthetics",
                "Dominant color + sharp accent > evenly distributed palette"
            ]
        elif is_dark:
            score = 0.4
            details = "Using dark theme - common but acceptable"
            suggestions = [
                "Consider adding accent colors for visual interest",
                "Try non-standard dark colors (warm darks, tinted blacks)"
            ]
        else:
            score = 0.3
            details = "Color scheme is non-standard"
            suggestions = []

        return SlopMetric(
            name="Color Scheme",
            score=score,
            weight=1.5,
            details=details,
            suggestions=suggestions
        )

    def _analyze_visual_interest(self, video_path: Path, config: Optional[Dict]) -> SlopMetric:
        """Analyze visual interest level"""

        has_images = config.get("has_images", False) if config else False
        has_video_clips = config.get("has_video_clips", False) if config else False
        has_graphics = config.get("has_graphics", False) if config else False
        background_type = config.get("background_type", "solid_color") if config else "solid_color"

        if has_video_clips:
            score = 0.1
            details = "Has video footage - visually engaging"
        elif has_images:
            score = 0.3
            details = "Has images - good visual interest"
        elif has_graphics:
            score = 0.4
            details = "Has graphics/animations - some visual interest"
        elif background_type == "animated":
            score = 0.5
            details = "Animated background only - minimal interest"
        else:
            score = 0.9
            details = "Just text on solid background - PURE SLOP"

        suggestions = []
        if score > 0.5:
            suggestions = [
                "Add AI-generated background images (DALL-E, Midjourney)",
                "Use stock video footage as backgrounds",
                "Add particle effects or motion graphics",
                "Include relevant imagery, not just text"
            ]

        return SlopMetric(
            name="Visual Interest",
            score=score,
            weight=2.0,  # Very important for video
            details=details,
            suggestions=suggestions
        )

    def _analyze_motion(self, video_path: Path, config: Optional[Dict]) -> SlopMetric:
        """Analyze motion and animation"""

        has_transitions = config.get("has_transitions", True) if config else True
        has_text_animation = config.get("has_text_animation", True) if config else True
        has_camera_movement = config.get("has_camera_movement", False) if config else False
        has_particles = config.get("has_particles", False) if config else False

        motion_score = 0
        motion_count = 0

        if has_transitions:
            motion_score += 0.2
            motion_count += 1
        if has_text_animation:
            motion_score += 0.2
            motion_count += 1
        if has_camera_movement:
            motion_score += 0.3
            motion_count += 1
        if has_particles:
            motion_score += 0.3
            motion_count += 1

        if motion_count == 0:
            score = 0.95
            details = "No animation - completely static (slideshow)"
        elif motion_count == 1:
            score = 0.7
            details = "Minimal animation - feels lazy"
        elif motion_count == 2:
            score = 0.5
            details = "Some animation - acceptable"
        else:
            score = 0.2
            details = "Good motion design"

        suggestions = []
        if score > 0.5:
            suggestions = [
                "Add Ken Burns effect (slow zoom/pan) on images",
                "Use staggered text reveals with animation-delay",
                "Add subtle particle effects or floating elements",
                "Consider camera movement or parallax effects"
            ]

        return SlopMetric(
            name="Motion/Animation",
            score=score,
            weight=1.5,
            details=details,
            suggestions=suggestions
        )

    def _analyze_audio(self, video_path: Path, config: Optional[Dict]) -> SlopMetric:
        """Analyze audio quality and interest"""

        has_voiceover = config.get("has_voiceover", False) if config else False
        has_music = config.get("has_music", False) if config else False
        voice_type = config.get("voice_type", "tts") if config else "tts"
        music_type = config.get("music_type", "generated") if config else "none"

        if has_voiceover and has_music:
            if voice_type == "human" and music_type == "licensed":
                score = 0.1
                details = "Human voiceover + licensed music - professional"
            elif voice_type == "tts" and music_type == "licensed":
                score = 0.3
                details = "TTS + licensed music - good"
            else:
                score = 0.4
                details = "TTS + generated music - acceptable"
        elif has_voiceover:
            score = 0.5
            details = "Voiceover only, no music - feels empty"
        elif has_music:
            score = 0.6
            details = "Music only, no voiceover - background noise"
        else:
            score = 0.95
            details = "Silent video - PURE SLOP"

        suggestions = []
        if score > 0.4:
            suggestions = [
                "Add professional background music",
                "Consider human voiceover for authenticity",
                "Add sound effects for emphasis",
                "Use high-quality TTS voices (ElevenLabs, Azure Neural)"
            ]

        return SlopMetric(
            name="Audio Quality",
            score=score,
            weight=1.5,
            details=details,
            suggestions=suggestions
        )

    def _analyze_personality(self, config: Optional[Dict]) -> SlopMetric:
        """Analyze distinctiveness and personality"""

        has_branding = config.get("has_branding", False) if config else False
        has_unique_style = config.get("has_unique_style", False) if config else False
        has_humor = config.get("has_humor", False) if config else False
        has_emotion = config.get("has_emotion", False) if config else False

        personality_indicators = sum([has_branding, has_unique_style, has_humor, has_emotion])

        if personality_indicators >= 3:
            score = 0.1
            details = "Strong personality and distinctiveness"
        elif personality_indicators >= 2:
            score = 0.3
            details = "Some personality"
        elif personality_indicators >= 1:
            score = 0.5
            details = "Minimal personality"
        else:
            score = 0.85
            details = "No personality - cookie-cutter AI output"

        suggestions = []
        if score > 0.4:
            suggestions = [
                "Develop distinctive visual brand",
                "Add unexpected creative elements",
                "Inject personality through writing style",
                "Use context-specific character, not generic templates"
            ]

        return SlopMetric(
            name="Personality/Distinctiveness",
            score=score,
            weight=1.5,
            details=details,
            suggestions=suggestions
        )

    def _analyze_pacing(self, video_path: Path, config: Optional[Dict]) -> SlopMetric:
        """Analyze pacing and rhythm"""

        duration = config.get("duration_seconds", 30) if config else 30
        segment_count = config.get("segment_count", 10) if config else 10

        if segment_count > 0:
            avg_segment_duration = duration / segment_count
        else:
            avg_segment_duration = duration

        # Ideal pacing: 3-5 seconds per segment for engagement
        if 3 <= avg_segment_duration <= 5:
            score = 0.2
            details = f"Good pacing ({avg_segment_duration:.1f}s/segment)"
        elif 2 <= avg_segment_duration < 3 or 5 < avg_segment_duration <= 7:
            score = 0.4
            details = f"Acceptable pacing ({avg_segment_duration:.1f}s/segment)"
        else:
            score = 0.7
            details = f"Poor pacing ({avg_segment_duration:.1f}s/segment) - too fast or too slow"

        suggestions = []
        if score > 0.4:
            suggestions = [
                "Aim for 3-5 seconds per key message",
                "Vary pacing for emphasis",
                "Add pauses for dramatic effect",
                "Consider viewer attention span"
            ]

        return SlopMetric(
            name="Pacing",
            score=score,
            weight=1.0,
            details=details,
            suggestions=suggestions
        )

    def _analyze_originality(self, config: Optional[Dict]) -> SlopMetric:
        """Analyze content originality"""

        # Check for generic AI template indicators
        is_template = config.get("is_template", True) if config else True
        has_custom_content = config.get("has_custom_content", False) if config else False

        if has_custom_content and not is_template:
            score = 0.2
            details = "Original content, not template-based"
        elif has_custom_content:
            score = 0.4
            details = "Custom content in template format"
        else:
            score = 0.8
            details = "Template-based, generic structure"

        suggestions = []
        if score > 0.4:
            suggestions = [
                "Create bespoke content for your specific use case",
                "Avoid generic template structures",
                "Add unique elements that can't be templated"
            ]

        return SlopMetric(
            name="Originality",
            score=score,
            weight=1.0,
            details=details,
            suggestions=suggestions
        )

    def _generate_recommendations(self, metrics: List[SlopMetric], 
                                 overall_score: float) -> List[str]:
        """Generate prioritized recommendations"""

        recommendations = []

        # Sort metrics by score (worst first)
        sorted_metrics = sorted(metrics, key=lambda m: m.score, reverse=True)

        # Get top 5 issues
        for metric in sorted_metrics[:5]:
            if metric.score > 0.4 and metric.suggestions:
                recommendations.append(f"**{metric.name}**: {metric.suggestions[0]}")

        # Add general recommendations based on overall score
        if overall_score > 0.7:
            recommendations.insert(0, "🚨 CRITICAL: This is pure AI slop. Major overhaul needed.")
        elif overall_score > 0.5:
            recommendations.insert(0, "⚠️ WARNING: Significant AI slop detected. Improvements needed.")
        elif overall_score > 0.3:
            recommendations.insert(0, "📝 NOTE: Some AI slop indicators. Consider refinements.")

        return recommendations

    def _generate_summary(self, metrics: List[SlopMetric], 
                         overall_score: float, level: SlopLevel) -> str:
        """Generate human-readable summary"""

        worst_metrics = sorted(metrics, key=lambda m: m.score, reverse=True)[:3]
        best_metrics = sorted(metrics, key=lambda m: m.score)[:2]

        summary = f"""
🚨 AI SLOP ANALYSIS REPORT 🚨
{'='*50}

Overall Slop Score: {overall_score*100:.1f}% 
Verdict: {level.value.upper().replace('_', ' ')}

{'='*50}
WORST AREAS (needs work):
"""
        for m in worst_metrics:
            emoji = "🔴" if m.score > 0.7 else "🟠" if m.score > 0.5 else "🟡"
            summary += f"  {emoji} {m.name}: {m.score*100:.0f}% slop - {m.details}\n"

        summary += f"""
BEST AREAS:
"""
        for m in best_metrics:
            emoji = "🟢" if m.score < 0.3 else "🟡"
            summary += f"  {emoji} {m.name}: {m.score*100:.0f}% slop - {m.details}\n"

        summary += f"""
{'='*50}
"""

        return summary

    def print_report(self, report: SlopReport):
        """Print formatted report"""
        print(report.summary)

        print("📋 RECOMMENDATIONS:")
        for i, rec in enumerate(report.recommendations, 1):
            print(f"  {i}. {rec}")

        print("\n" + "="*50)
        print(f"Full metric breakdown:")
        for m in report.metrics:
            bar = "█" * int(m.score * 10) + "░" * (10 - int(m.score * 10))
            print(f"  {m.name:25} [{bar}] {m.score*100:5.1f}%")


def analyze_lumina_video():
    try:
        """Analyze our LUMINA cinematic video"""

        detector = AISloPDetector()

        # Our current video configuration
        video_config = {
            "font": "Arial",  # Generic :(
            "colors": ["#0a0a1a", "#0f0f23"],  # Dark but generic
            "has_images": False,
            "has_video_clips": False,
            "has_graphics": False,
            "background_type": "solid_color",
            "has_transitions": True,
            "has_text_animation": True,
            "has_camera_movement": False,
            "has_particles": False,
            "has_voiceover": True,
            "has_music": True,
            "voice_type": "tts",
            "music_type": "generated",
            "has_branding": False,
            "has_unique_style": False,
            "has_humor": False,
            "has_emotion": False,
            "duration_seconds": 69,
            "segment_count": 15,
            "is_template": True,
            "has_custom_content": True
        }

        video_path = Path("output/videos/cinematic/CINEMATIC_LUMINA_20251230_150741.mp4")

        report = detector.analyze_video(video_path, video_config)
        detector.print_report(report)

        return report


    except Exception as e:
        logger.error(f"Error in analyze_lumina_video: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    print("🚨 AI SLOP DETECTOR 🚨")
    print("Testing LUMINA Cinematic Video...")
    print()

    report = analyze_lumina_video()

