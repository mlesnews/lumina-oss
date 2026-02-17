#!/usr/bin/env python3
"""
YouTube 30-Day Instruction Processor

Processes 30 days of YouTube recommendations and history to extract
actionable instructions for successful living.

This system:
- Extracts YouTube watch history and recommendations
- Processes 30 days of data
- Analyzes content for actionable insights
- Generates instruction book format
- Integrates with VA collaboration system

Usage:
    python youtube_30day_instruction_processor.py --process
    python youtube_30day_instruction_processor.py --analyze
    python youtube_30day_instruction_processor.py --generate-instructions

Tags: #YOUTUBE #INSTRUCTIONS #PROCESSING #30DAY #LIFEGUIDE @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("YouTube30DayProcessor")

# Try to import YouTube API
try:
    from googleapiclient.discovery import build
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    import pickle
    import os
    YOUTUBE_API_AVAILABLE = True
except ImportError:
    YOUTUBE_API_AVAILABLE = False
    logger.warning("⚠️  YouTube API not available - install: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")

# Try to import VA collaboration system
try:
    from va_full_voice_vfx_collaboration_integration import VAFullVoiceVFXCollaborationIntegration
    VA_COLLABORATION_AVAILABLE = True
except ImportError:
    VA_COLLABORATION_AVAILABLE = False
    logger.warning("⚠️  VA collaboration system not available")


class YouTube30DayProcessor:
    """Process 30 days of YouTube data for instruction extraction"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "youtube_30day"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.history_file = self.data_dir / "watch_history.json"
        self.recommendations_file = self.data_dir / "recommendations.json"
        self.instructions_file = self.data_dir / "instructions_book.json"
        self.analysis_file = self.data_dir / "analysis.json"

        self.youtube_service = None
        self.va_integration = None

        if VA_COLLABORATION_AVAILABLE:
            try:
                self.va_integration = VAFullVoiceVFXCollaborationIntegration(project_root)
                self.va_integration.initialize_systems()
                logger.info("✅ VA collaboration system initialized")
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize VA collaboration: {e}")

    def _get_youtube_service(self):
        """Get YouTube API service"""
        if not YOUTUBE_API_AVAILABLE:
            logger.error("❌ YouTube API not available")
            return None

        if self.youtube_service:
            return self.youtube_service

        try:
            # Try to load credentials
            creds = None
            token_file = self.data_dir / "token.pickle"
            credentials_file = self.project_root / "config" / "youtube_credentials.json"

            if token_file.exists():
                with open(token_file, 'rb') as token:
                    creds = pickle.load(token)

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                elif credentials_file.exists():
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(credentials_file),
                        ['https://www.googleapis.com/auth/youtube.readonly']
                    )
                    creds = flow.run_local_server(port=0)
                else:
                    logger.warning("⚠️  YouTube credentials not found")
                    logger.info("   Create config/youtube_credentials.json with OAuth2 credentials")
                    return None

                with open(token_file, 'wb') as token:
                    pickle.dump(creds, token)

            self.youtube_service = build('youtube', 'v3', credentials=creds)
            logger.info("✅ YouTube API service initialized")
            return self.youtube_service

        except Exception as e:
            logger.error(f"❌ Error initializing YouTube service: {e}")
            return None

    def extract_watch_history(self, days: int = 30) -> List[Dict[str, Any]]:
        """Extract watch history for specified days"""
        logger.info(f"📺 Extracting {days} days of YouTube watch history...")

        service = self._get_youtube_service()
        if not service:
            logger.warning("⚠️  Using fallback: Load from existing history file")
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []

        history = []
        try:
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            # Get watch history (requires YouTube Data API v3 with history scope)
            # Note: This requires special permissions and may need alternative approach
            request = service.videos().list(
                part='snippet,contentDetails,statistics',
                myRating='like',
                maxResults=50
            )

            # For now, we'll use a fallback approach
            # In production, you'd use Takeout export or browser extension
            logger.info("📋 Using browser history export method")
            logger.info("   Export your YouTube watch history from:")
            logger.info("   https://takeout.google.com/")
            logger.info("   Or use browser extension to extract history")

            return history

        except Exception as e:
            logger.error(f"❌ Error extracting watch history: {e}")
            return []

    def extract_recommendations(self) -> List[Dict[str, Any]]:
        """Extract current recommendations"""
        logger.info("📺 Extracting YouTube recommendations...")

        service = self._get_youtube_service()
        if not service:
            logger.warning("⚠️  Using fallback: Load from existing recommendations file")
            if self.recommendations_file.exists():
                with open(self.recommendations_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return []

        recommendations = []
        try:
            # Get recommended videos
            request = service.videos().list(
                part='snippet,contentDetails,statistics',
                chart='mostPopular',
                regionCode='US',
                maxResults=50
            )

            response = request.execute()

            for item in response.get('items', []):
                recommendations.append({
                    'video_id': item['id'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'view_count': item['statistics'].get('viewCount', 0),
                    'like_count': item['statistics'].get('likeCount', 0),
                    'category': item['snippet'].get('categoryId', 'Unknown')
                })

            logger.info(f"✅ Extracted {len(recommendations)} recommendations")
            return recommendations

        except Exception as e:
            logger.error(f"❌ Error extracting recommendations: {e}")
            return []

    def load_browser_history(self, history_file: Optional[Path] = None) -> List[Dict[str, Any]]:
        """Load watch history from browser export or Takeout"""
        if history_file is None:
            # Look for common export locations
            possible_locations = [
                self.data_dir / "watch-history.json",
                self.data_dir / "watch-history.html",
                self.project_root / "data" / "youtube_takeout" / "watch-history.json"
            ]

            for loc in possible_locations:
                if loc.exists():
                    history_file = loc
                    break

        if not history_file or not history_file.exists():
            logger.warning("⚠️  No history file found")
            logger.info("   Export your YouTube watch history from:")
            logger.info("   https://takeout.google.com/")
            logger.info("   Save as: data/youtube_30day/watch-history.json")
            return []

        logger.info(f"📂 Loading history from: {history_file}")

        try:
            if history_file.suffix == '.json':
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                    # Handle different export formats
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict):
                        # Google Takeout format
                        return data.get('Video', []) or data.get('items', [])
                    else:
                        return []
            else:
                # HTML format - would need parsing
                logger.warning("⚠️  HTML format not yet supported")
                return []

        except Exception as e:
            logger.error(f"❌ Error loading history: {e}")
            return []

    def analyze_content(self, videos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze video content for actionable instructions"""
        logger.info(f"🔍 Analyzing {len(videos)} videos for instructions...")

        analysis = {
            'total_videos': len(videos),
            'categories': {},
            'topics': {},
            'instructions': [],
            'patterns': {},
            'insights': []
        }

        # Categorize videos
        for video in videos:
            title = video.get('title', '').lower()
            description = video.get('description', '').lower()
            channel = video.get('channel', '').lower()

            # Extract category
            category = video.get('category', 'Unknown')
            analysis['categories'][category] = analysis['categories'].get(category, 0) + 1

            # Extract topics and instructions
            text = f"{title} {description}"

            # Look for instruction patterns
            instruction_patterns = [
                r'how to (.+?)(?:\.|$|,)',
                r'tips? for (.+?)(?:\.|$|,)',
                r'guide to (.+?)(?:\.|$|,)',
                r'learn (.+?)(?:\.|$|,)',
                r'master (.+?)(?:\.|$|,)',
                r'steps? to (.+?)(?:\.|$|,)',
                r'ways? to (.+?)(?:\.|$|,)',
                r'secrets? of (.+?)(?:\.|$|,)',
                r'principles? of (.+?)(?:\.|$|,)',
                r'rules? for (.+?)(?:\.|$|,)',
            ]

            for pattern in instruction_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    instruction = match.strip()
                    if len(instruction) > 5 and len(instruction) < 100:
                        analysis['instructions'].append({
                            'instruction': instruction,
                            'source': video.get('title', 'Unknown'),
                            'channel': channel,
                            'video_id': video.get('video_id', ''),
                            'pattern': pattern
                        })

            # Extract topics
            topic_keywords = [
                'productivity', 'success', 'happiness', 'health', 'wealth',
                'relationships', 'mindset', 'growth', 'learning', 'business',
                'finance', 'fitness', 'nutrition', 'meditation', 'creativity',
                'leadership', 'communication', 'time management', 'goal setting'
            ]

            for keyword in topic_keywords:
                if keyword in text:
                    analysis['topics'][keyword] = analysis['topics'].get(keyword, 0) + 1

        # Find patterns
        instruction_texts = [inst['instruction'] for inst in analysis['instructions']]
        common_words = {}
        for inst in instruction_texts:
            words = inst.lower().split()
            for word in words:
                if len(word) > 3:
                    common_words[word] = common_words.get(word, 0) + 1

        analysis['patterns'] = dict(sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:20])

        logger.info(f"✅ Extracted {len(analysis['instructions'])} instructions")
        logger.info(f"   Categories: {len(analysis['categories'])}")
        logger.info(f"   Topics: {len(analysis['topics'])}")

        return analysis

    def generate_instruction_book(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate instruction book format from analysis"""
        logger.info("📖 Generating instruction book...")

        # Group instructions by topic
        instructions_by_topic = {}
        for inst in analysis['instructions']:
            # Determine topic from instruction text
            topic = 'General'
            instruction_lower = inst['instruction'].lower()

            topic_mapping = {
                'productivity': ['productivity', 'efficient', 'organize', 'time management'],
                'success': ['success', 'achieve', 'accomplish', 'win'],
                'health': ['health', 'fitness', 'exercise', 'nutrition', 'diet'],
                'wealth': ['wealth', 'money', 'finance', 'invest', 'income'],
                'relationships': ['relationship', 'communication', 'social', 'friends'],
                'mindset': ['mindset', 'mental', 'attitude', 'positive', 'confidence'],
                'learning': ['learn', 'study', 'education', 'skill', 'knowledge'],
                'creativity': ['creative', 'art', 'design', 'innovate', 'ideas']
            }

            for topic_name, keywords in topic_mapping.items():
                if any(keyword in instruction_lower for keyword in keywords):
                    topic = topic_name
                    break

            if topic not in instructions_by_topic:
                instructions_by_topic[topic] = []

            instructions_by_topic[topic].append(inst)

        # Generate instruction book
        instruction_book = {
            'title': '30-Day YouTube Instruction Book: Instructions to Live Successfully',
            'generated_at': datetime.now().isoformat(),
            'source': '30 days of YouTube recommendations and history',
            'total_instructions': len(analysis['instructions']),
            'categories': analysis['categories'],
            'topics': analysis['topics'],
            'chapters': []
        }

        # Create chapters
        for topic, instructions in instructions_by_topic.items():
            chapter = {
                'chapter_title': f'Chapter: {topic.title()}',
                'instructions': instructions[:20],  # Top 20 per topic
                'count': len(instructions)
            }
            instruction_book['chapters'].append(chapter)

        # Add insights
        instruction_book['insights'] = [
            f"Processed {analysis['total_videos']} videos over 30 days",
            f"Extracted {len(analysis['instructions'])} actionable instructions",
            f"Identified {len(analysis['topics'])} key topics",
            f"Found {len(analysis['categories'])} content categories"
        ]

        logger.info(f"✅ Generated instruction book with {len(instruction_book['chapters'])} chapters")

        return instruction_book

    def process_30_days(self) -> Dict[str, Any]:
        try:
            """Process 30 days of YouTube data"""
            logger.info("=" * 80)
            logger.info("🚀 PROCESSING 30 DAYS OF YOUTUBE DATA")
            logger.info("=" * 80)
            logger.info("")

            # Step 1: Extract watch history
            logger.info("📺 Step 1: Extracting watch history...")
            history = self.load_browser_history()

            if not history:
                logger.warning("⚠️  No history found - trying to extract from API...")
                history = self.extract_watch_history(days=30)

            if history:
                with open(self.history_file, 'w', encoding='utf-8') as f:
                    json.dump(history, f, indent=2, default=str)
                logger.info(f"✅ Saved {len(history)} history items")
            else:
                logger.warning("⚠️  No history available - using recommendations only")

            # Step 2: Extract recommendations
            logger.info("")
            logger.info("📺 Step 2: Extracting recommendations...")
            recommendations = self.extract_recommendations()

            if recommendations:
                with open(self.recommendations_file, 'w', encoding='utf-8') as f:
                    json.dump(recommendations, f, indent=2, default=str)
                logger.info(f"✅ Saved {len(recommendations)} recommendations")

            # Step 3: Combine and analyze
            logger.info("")
            logger.info("🔍 Step 3: Analyzing content...")
            all_videos = history + recommendations

            if not all_videos:
                logger.error("❌ No videos to process")
                return {}

            analysis = self.analyze_content(all_videos)

            with open(self.analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)
            logger.info(f"✅ Saved analysis")

            # Step 4: Generate instruction book
            logger.info("")
            logger.info("📖 Step 4: Generating instruction book...")
            instruction_book = self.generate_instruction_book(analysis)

            with open(self.instructions_file, 'w', encoding='utf-8') as f:
                json.dump(instruction_book, f, indent=2, default=str)
            logger.info(f"✅ Saved instruction book")

            # Step 5: Present with VA system
            if self.va_integration:
                logger.info("")
                logger.info("🎤 Step 5: Presenting with VA collaboration system...")
                self._present_with_vas(instruction_book)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ PROCESSING COMPLETE")
            logger.info("=" * 80)
            logger.info("")
            logger.info(f"📄 Instruction book: {self.instructions_file}")
            logger.info(f"📊 Analysis: {self.analysis_file}")
            logger.info("")

            return {
                'history_count': len(history),
                'recommendations_count': len(recommendations),
                'total_videos': len(all_videos),
                'instructions_extracted': len(analysis['instructions']),
                'instruction_book': instruction_book
            }

        except Exception as e:
            self.logger.error(f"Error in process_30_days: {e}", exc_info=True)
            raise
    def _present_with_vas(self, instruction_book: Dict[str, Any]):
        """Present results using VA collaboration system"""
        try:
            # JARVIS presents summary
            summary = f"""
            Processed 30 days of YouTube data.
            Extracted {instruction_book['total_instructions']} actionable instructions.
            Organized into {len(instruction_book['chapters'])} chapters.
            Ready to guide successful living.
            """

            self.va_integration.voice_system.speak("jarvis", summary, blocking=False)

            # Create VFX effects
            self.va_integration.vfx_system.create_glow_effect("jarvis", duration=3.0)

            # Present each chapter
            for i, chapter in enumerate(instruction_book['chapters'][:3]):  # Top 3 chapters
                chapter_text = f"Chapter {i+1}: {chapter['chapter_title']} with {chapter['count']} instructions."
                self.va_integration.voice_system.speak("jarvis", chapter_text, blocking=False)
                time.sleep(1)

            logger.info("✅ Presented with VA collaboration system")

        except Exception as e:
            logger.warning(f"⚠️  Error presenting with VAs: {e}")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Process 30 days of YouTube data")
        parser.add_argument("--process", action="store_true", help="Process 30 days of data")
        parser.add_argument("--analyze", action="store_true", help="Analyze existing data")
        parser.add_argument("--generate-instructions", action="store_true", help="Generate instruction book")
        parser.add_argument("--history-file", type=Path, help="Path to watch history file")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        processor = YouTube30DayProcessor(project_root)

        if args.process or (not args.analyze and not args.generate_instructions):
            # Full processing
            result = processor.process_30_days()

            print("=" * 80)
            print("📊 PROCESSING RESULTS")
            print("=" * 80)
            print(f"History items: {result.get('history_count', 0)}")
            print(f"Recommendations: {result.get('recommendations_count', 0)}")
            print(f"Total videos: {result.get('total_videos', 0)}")
            print(f"Instructions extracted: {result.get('instructions_extracted', 0)}")
            print("=" * 80)

        elif args.analyze:
            # Analyze existing data
            if processor.analysis_file.exists():
                with open(processor.analysis_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                print(json.dumps(analysis, indent=2, default=str))
            else:
                logger.error("❌ No analysis file found. Run --process first.")

        elif args.generate_instructions:
            # Generate instruction book
            if processor.analysis_file.exists():
                with open(processor.analysis_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                instruction_book = processor.generate_instruction_book(analysis)
                print(json.dumps(instruction_book, indent=2, default=str))
            else:
                logger.error("❌ No analysis file found. Run --process first.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()