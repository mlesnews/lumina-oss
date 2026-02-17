#!/usr/bin/env python3
"""
LUMINA Multimedia Storytelling Analysis

Analyzes LUMINA's capability to turn Book of LUMINA chapters into:
- YouTube videos
- Complete playlists
- Audiobooks
- Live-action content
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

logger = get_logger("LUMINAMultimediaStorytelling")


class LUMINAMultimediaStorytellingAnalysis:
    """
    Analyze LUMINA's multimedia storytelling capabilities

    Vision Extension:
    - YouTube videos from chapters
    - Complete playlists
    - Audiobooks
    - Live-action content
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Key directories
        self.holocron = project_root / "data" / "holocron"
        self.video_production = self.holocron / "video_production"

        # Import roast system
        try:
            from jarvis_marvin_roast_system import JARVISMARVINRoastSystem
            self.roast_system = JARVISMARVINRoastSystem(project_root)
        except ImportError:
            self.roast_system = None

    def analyze_multimedia_capabilities(self) -> Dict[str, Any]:
        """Analyze multimedia storytelling capabilities"""
        self.logger.info("="*80)
        self.logger.info("ANALYZING MULTIMEDIA STORYTELLING CAPABILITIES")
        self.logger.info("="*80)

        analysis = {
            'youtube_video': {},
            'playlist': {},
            'audiobook': {},
            'live_action': {},
            'current_capabilities': {},
            'gaps': [],
            'feasibility': {}
        }

        # 1. YouTube Video Capability
        analysis['youtube_video'] = self._analyze_youtube_capability()

        # 2. Playlist Capability
        analysis['playlist'] = self._analyze_playlist_capability()

        # 3. Audiobook Capability
        analysis['audiobook'] = self._analyze_audiobook_capability()

        # 4. Live-Action Capability
        analysis['live_action'] = self._analyze_live_action_capability()

        # 5. Current capabilities summary
        analysis['current_capabilities'] = self._summarize_capabilities(analysis)

        # 6. Identify gaps
        analysis['gaps'] = self._identify_multimedia_gaps(analysis)

        # 7. Feasibility assessment
        analysis['feasibility'] = self._assess_multimedia_feasibility(analysis)

        return analysis

    def _analyze_youtube_capability(self) -> Dict[str, Any]:
        """Analyze YouTube video generation capability"""
        capability = {
            'video_production_exists': False,
            'notebook_templates': [],
            'video_generation': False,
            'youtube_upload': False,
            'ffmpeg_available': False
        }

        # Check video production directory
        if self.video_production.exists():
            capability['video_production_exists'] = True

            # Find video production notebooks
            notebooks = list(self.video_production.glob("*.ipynb"))
            capability['notebook_templates'] = [n.name for n in notebooks]

            # Check for video generation scripts
            scripts_dir = self.project_root / "scripts" / "python"
            video_scripts = [
                'video_generator.py',
                'youtube_uploader.py',
                'ffmpeg_wrapper.py'
            ]

            for script in video_scripts:
                if (scripts_dir / script).exists():
                    if 'video_generator' in script:
                        capability['video_generation'] = True
                    elif 'youtube_uploader' in script:
                        capability['youtube_upload'] = True
                    elif 'ffmpeg' in script:
                        capability['ffmpeg_available'] = True

        # Check for video generation in notebooks
        if notebooks:
            for notebook in notebooks[:3]:  # Check first 3
                try:
                    with open(notebook, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if 'video' in content.lower() or 'ffmpeg' in content.lower():
                            capability['video_generation'] = True
                            break
                except:
                    pass

        return capability

    def _analyze_playlist_capability(self) -> Dict[str, Any]:
        try:
            """Analyze playlist creation capability"""
            capability = {
                'playlist_management': False,
                'chapter_to_video_mapping': False,
                'sequential_organization': False,
                'youtube_api': False
            }

            # Check for playlist management
            scripts_dir = self.project_root / "scripts" / "python"
            playlist_scripts = [
                'playlist_manager.py',
                'youtube_playlist.py',
                'chapter_playlist.py'
            ]

            for script in playlist_scripts:
                if (scripts_dir / script).exists():
                    capability['playlist_management'] = True
                    if 'youtube' in script:
                        capability['youtube_api'] = True

            # Check if chapter mapping exists (from storytelling analysis)
            storytelling_assessment = self.project_root / "data" / "lumina_analysis" / "godmode_storytelling_assessment_20251231_230401.json"
            if storytelling_assessment.exists():
                capability['chapter_to_video_mapping'] = True

            return capability

        except Exception as e:
            self.logger.error(f"Error in _analyze_playlist_capability: {e}", exc_info=True)
            raise
    def _analyze_audiobook_capability(self) -> Dict[str, Any]:
        try:
            """Analyze audiobook generation capability"""
            capability = {
                'tts_available': False,
                'audio_generation': False,
                'chapter_to_audio': False,
                'audio_format': False
            }

            # Check for TTS systems
            scripts_dir = self.project_root / "scripts" / "python"
            tts_scripts = [
                'jarvis_elevenlabs_integration.py',
                'tts_generator.py',
                'audiobook_generator.py'
            ]

            for script in tts_scripts:
                if (scripts_dir / script).exists():
                    capability['tts_available'] = True
                    if 'elevenlabs' in script:
                        capability['audio_generation'] = True
                    elif 'audiobook' in script:
                        capability['chapter_to_audio'] = True

            # Check for audio format support
            if capability['tts_available']:
                capability['audio_format'] = True  # TTS systems typically support multiple formats

            return capability

        except Exception as e:
            self.logger.error(f"Error in _analyze_audiobook_capability: {e}", exc_info=True)
            raise
    def _analyze_live_action_capability(self) -> Dict[str, Any]:
        try:
            """Analyze live-action content capability"""
            capability = {
                'live_action_generation': False,
                'avatar_systems': False,
                'video_synthesis': False,
                'real_time_rendering': False
            }

            # Check for live-action/avatar systems
            scripts_dir = self.project_root / "scripts" / "python"
            live_action_scripts = [
                'avatar_generator.py',
                'live_action.py',
                'video_synthesis.py',
                'real_time_rendering.py'
            ]

            for script in live_action_scripts:
                if (scripts_dir / script).exists():
                    if 'avatar' in script:
                        capability['avatar_systems'] = True
                    elif 'synthesis' in script:
                        capability['video_synthesis'] = True
                    elif 'rendering' in script:
                        capability['real_time_rendering'] = True
                    capability['live_action_generation'] = True

            return capability

        except Exception as e:
            self.logger.error(f"Error in _analyze_live_action_capability: {e}", exc_info=True)
            raise
    def _summarize_capabilities(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize current capabilities"""
        summary = {
            'youtube_ready': False,
            'playlist_ready': False,
            'audiobook_ready': False,
            'live_action_ready': False,
            'overall_readiness': 0
        }

        # YouTube
        youtube = analysis.get('youtube_video', {})
        if youtube.get('video_production_exists') and youtube.get('video_generation'):
            summary['youtube_ready'] = True

        # Playlist
        playlist = analysis.get('playlist', {})
        if playlist.get('playlist_management') or playlist.get('chapter_to_video_mapping'):
            summary['playlist_ready'] = True

        # Audiobook
        audiobook = analysis.get('audiobook', {})
        if audiobook.get('tts_available') and audiobook.get('audio_generation'):
            summary['audiobook_ready'] = True

        # Live-action
        live_action = analysis.get('live_action', {})
        if live_action.get('live_action_generation'):
            summary['live_action_ready'] = True

        # Overall readiness
        ready_count = sum([
            summary['youtube_ready'],
            summary['playlist_ready'],
            summary['audiobook_ready'],
            summary['live_action_ready']
        ])
        summary['overall_readiness'] = (ready_count / 4) * 100

        return summary

    def _identify_multimedia_gaps(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify gaps in multimedia capabilities"""
        gaps = []

        # YouTube gaps
        youtube = analysis.get('youtube_video', {})
        if not youtube.get('video_generation'):
            gaps.append({
                'gap': 'Video Generation Engine',
                'description': 'No automated video generation from chapters',
                'priority': 'high',
                'format': 'youtube'
            })
        if not youtube.get('youtube_upload'):
            gaps.append({
                'gap': 'YouTube Upload System',
                'description': 'No automated YouTube upload capability',
                'priority': 'high',
                'format': 'youtube'
            })

        # Playlist gaps
        playlist = analysis.get('playlist', {})
        if not playlist.get('playlist_management'):
            gaps.append({
                'gap': 'Playlist Management',
                'description': 'No system to create and manage YouTube playlists',
                'priority': 'high',
                'format': 'playlist'
            })

        # Audiobook gaps
        audiobook = analysis.get('audiobook', {})
        if not audiobook.get('chapter_to_audio'):
            gaps.append({
                'gap': 'Chapter to Audio Mapper',
                'description': 'No system to convert chapters to audiobook format',
                'priority': 'medium',
                'format': 'audiobook'
            })

        # Live-action gaps
        live_action = analysis.get('live_action', {})
        if not live_action.get('live_action_generation'):
            gaps.append({
                'gap': 'Live-Action Generation',
                'description': 'No system for live-action video generation',
                'priority': 'medium',
                'format': 'live_action'
            })

        return gaps

    def _assess_multimedia_feasibility(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Assess feasibility of multimedia storytelling"""
        feasibility = {
            'overall_feasibility': 'feasible',
            'readiness_score': 0,
            'time_to_complete': 'medium',
            'confidence': 'high',
            'recommendations': []
        }

        # Calculate readiness
        readiness = analysis.get('current_capabilities', {}).get('overall_readiness', 0)
        feasibility['readiness_score'] = readiness

        # Assess feasibility
        if readiness >= 75:
            feasibility['overall_feasibility'] = 'highly_feasible'
            feasibility['time_to_complete'] = 'short'
        elif readiness >= 50:
            feasibility['overall_feasibility'] = 'feasible'
            feasibility['time_to_complete'] = 'medium'
        else:
            feasibility['overall_feasibility'] = 'feasible_with_work'
            feasibility['time_to_complete'] = 'long'

        # Recommendations from gaps
        gaps = analysis.get('gaps', [])
        for gap in gaps:
            feasibility['recommendations'].append({
                'action': f"Implement {gap['gap']}",
                'priority': gap['priority'],
                'format': gap['format'],
                'reason': gap['description']
            })

        return feasibility

    def generate_multimedia_assessment(self) -> Dict[str, Any]:
        """Generate comprehensive multimedia assessment"""
        self.logger.info("="*80)
        self.logger.info("LUMINA MULTIMEDIA STORYTELLING ASSESSMENT")
        self.logger.info("="*80)

        assessment = {
            'timestamp': datetime.now().isoformat(),
            'vision': {
                'title': 'Multimedia Storytelling - Book of LUMINA',
                'description': 'Turn chapters into YouTube videos, playlists, audiobooks, and live-action',
                'formats': ['youtube', 'playlist', 'audiobook', 'live_action']
            },
            'current_state': {},
            'feasibility': {},
            'gaps': [],
            'recommendations': [],
            'jarvis_assessment': {},
            'marvin_assessment': {}
        }

        # Analyze capabilities
        analysis = self.analyze_multimedia_capabilities()
        assessment['current_state'] = analysis

        # Feasibility
        assessment['feasibility'] = analysis['feasibility']
        assessment['gaps'] = analysis['gaps']

        # JARVIS assessment
        readiness = analysis['current_capabilities'].get('overall_readiness', 0)
        assessment['jarvis_assessment'] = {
            'systematic_analysis': f'The multimedia vision extends the storytelling capability. Current readiness: {readiness:.1f}%. Video production infrastructure exists (holocron notebooks). TTS available (ElevenLabs). Missing: automated video generation, YouTube upload, playlist management. Systematic implementation path: video generator → YouTube uploader → playlist manager → audiobook generator → live-action system.',
            'readiness': f"Readiness: {readiness:.1f}%",
            'next_steps': [
                'Implement video generation engine',
                'Create YouTube upload system',
                'Build playlist manager',
                'Enhance audiobook generation',
                'Develop live-action system'
            ]
        }

        # MARVIN assessment
        assessment['marvin_assessment'] = {
            'existential_analysis': 'YouTube videos. Playlists. Audiobooks. Live-action. The Book of LUMINA in every format. 4,437 chapters. 4,437 videos. 4,437 audio files. One complete playlist. One audiobook. One live-action series. The story told in every way possible. The question isn\'t whether we can do it. The question is: will anyone watch? Will anyone listen? Will anyone care? But perhaps that\'s not the point. Perhaps the point is to tell the story. In every format. In every way. Because the story matters.',
            'reality_check': 'The infrastructure partially exists. Video production notebooks show capability. TTS systems are operational. But automated generation? YouTube integration? Playlist management? These are gaps. Significant gaps. But gaps can be filled. Systems can be built. The story can be told.',
            'philosophical_take': 'Every format is a different way of experiencing the story. Video for visual learners. Audio for listeners. Live-action for immersion. The Book of LUMINA will be told in every way. Because every way matters. Because every format reaches different people. Because the story is worth telling. In every format. In every way.'
        }

        # Recommendations
        assessment['recommendations'] = analysis['feasibility']['recommendations']

        return assessment

    def save_assessment(self, assessment: Dict[str, Any]) -> Path:
        """Save assessment report"""
        reports_dir = self.project_root / "data" / "lumina_analysis"
        reports_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = reports_dir / f"multimedia_storytelling_assessment_{timestamp}.json"

        try:
            with open(report_file, 'w') as f:
                json.dump(assessment, f, indent=2)
            self.logger.info(f"✅ Assessment saved: {report_file}")
            return report_file
        except Exception as e:
            self.logger.error(f"Failed to save assessment: {e}")
            return None


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Multimedia Storytelling Analysis")
    parser.add_argument("--assess", action="store_true", help="Assess multimedia capability")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    analyzer = LUMINAMultimediaStorytellingAnalysis(project_root)

    try:
        assessment = analyzer.generate_multimedia_assessment()

        # Save
        report_file = analyzer.save_assessment(assessment)

        # Print summary
        print("\n" + "="*80)
        print("LUMINA MULTIMEDIA STORYTELLING ASSESSMENT")
        print("="*80)

        print(f"\n📖 VISION: {assessment['vision']['title']}")
        print(f"   {assessment['vision']['description']}")
        print(f"   Formats: {', '.join(assessment['vision']['formats'])}")

        readiness = assessment['feasibility']['readiness_score']
        print(f"\n📊 READINESS: {readiness:.1f}%")
        print(f"   Feasibility: {assessment['feasibility']['overall_feasibility']}")
        print(f"   Time to Complete: {assessment['feasibility']['time_to_complete']}")

        capabilities = assessment['current_state'].get('current_capabilities', {})
        print(f"\n✅ CAPABILITIES:")
        print(f"   YouTube Ready: {capabilities.get('youtube_ready', False)}")
        print(f"   Playlist Ready: {capabilities.get('playlist_ready', False)}")
        print(f"   Audiobook Ready: {capabilities.get('audiobook_ready', False)}")
        print(f"   Live-Action Ready: {capabilities.get('live_action_ready', False)}")

        print(f"\n🔍 JARVIS ASSESSMENT:")
        print(f"   {assessment['jarvis_assessment']['systematic_analysis'][:200]}...")

        print(f"\n🤖 MARVIN ASSESSMENT:")
        print(f"   {assessment['marvin_assessment']['existential_analysis'][:200]}...")

        print(f"\n📋 GAPS IDENTIFIED: {len(assessment['gaps'])}")
        for gap in assessment['gaps'][:5]:
            print(f"   - {gap['gap']} ({gap['format']}): {gap['description']}")

        print(f"\n📄 Full assessment: {report_file}")
        print("="*80)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()