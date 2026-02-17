#!/usr/bin/env python3
"""
JARVIS: Comprehensive YouTube Analysis
Analyzes recommended feed, 30-day history, and recently viewed videos
Extracts learnings and insights for Lumina

Tags: #JARVIS #YOUTUBE #ANALYSIS #LEARNING #HISTORY #RECOMMENDED @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter, defaultdict

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

logger = get_logger("JARVISYouTubeAnalysis")


class JARVISYouTubeComprehensiveAnalysis:
    """
    JARVIS: Comprehensive YouTube Analysis

    Analyzes:
    - Recommended feed
    - 30-day watch history
    - Recently viewed videos
    - Learning videos
    """

    def __init__(self):
        """Initialize comprehensive YouTube analysis"""
        logger.info("=" * 80)
        logger.info("🎥 JARVIS: Comprehensive YouTube Analysis")
        logger.info("=" * 80)

        self.project_root = project_root
        self.data_dir = project_root / "data"

        # Data sources
        self.youtube_dir = self.data_dir / "youtube"
        self.syphon_dir = self.data_dir / "syphon" / "youtube_history"
        self.learning_dir = self.data_dir / "lumina_youtube_learning"

        # Analysis results
        self.recommended_videos = []
        self.history_videos = []
        self.recently_viewed = []
        self.learning_videos = []

        # Insights
        self.top_channels = Counter()
        self.top_topics = Counter()
        self.watch_patterns = []
        self.learnings = []

        logger.info("✅ JARVIS YouTube Analysis initialized")

    def analyze_all_sources(self) -> Dict[str, Any]:
        """
        Analyze all YouTube sources:
        - Recommended feed
        - 30-day history
        - Recently viewed
        - Learning videos
        """
        logger.info("\n📊 Analyzing All YouTube Sources...")

        # 1. Analyze recommended feed
        logger.info("\n1️⃣  Analyzing Recommended Feed...")
        self.recommended_videos = self._analyze_recommended_feed()

        # 2. Analyze 30-day history
        logger.info("\n2️⃣  Analyzing 30-Day Watch History...")
        self.history_videos = self._analyze_30_day_history()

        # 3. Analyze recently viewed
        logger.info("\n3️⃣  Analyzing Recently Viewed...")
        self.recently_viewed = self._analyze_recently_viewed()

        # 4. Analyze learning videos
        logger.info("\n4️⃣  Analyzing Learning Videos...")
        self.learning_videos = self._analyze_learning_videos()

        # Generate comprehensive insights
        logger.info("\n🧠 Generating Insights...")
        insights = self._generate_insights()

        return insights

    def _analyze_recommended_feed(self) -> List[Dict[str, Any]]:
        """Analyze recommended feed videos"""
        videos = []

        # Check for recommended feed data
        recommended_files = [
            self.youtube_dir / "recommended_feed.json",
            self.syphon_dir / "recommended.json",
            self.data_dir / "youtube_recommended.json"
        ]

        for file_path in recommended_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            videos.extend(data)
                        elif isinstance(data, dict) and 'videos' in data:
                            videos.extend(data['videos'])
                    logger.info(f"   ✅ Found recommended feed: {len(videos)} videos")
                    break
                except Exception as e:
                    logger.debug(f"   Error reading {file_path}: {e}")

        # If no file, try to extract from watch history (recent recommendations)
        if not videos:
            logger.info("   ℹ️  No recommended feed file found")
            logger.info("   ℹ️  Will analyze from watch history patterns")

        return videos

    def _analyze_30_day_history(self) -> List[Dict[str, Any]]:
        """Analyze 30-day watch history"""
        videos = []

        # Check multiple possible locations
        history_files = [
            self.youtube_dir / "watch_history.json",
            self.syphon_dir / "watch_history_30_days.json",
            self.syphon_dir / "history.json",
            self.data_dir / "youtube_watch_history.json"
        ]

        for file_path in history_files:
            if file_path.exists():
                try:
                    with open(file_path, 'r') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            videos = data
                        elif isinstance(data, dict) and 'videos' in data:
                            videos = data['videos']
                        elif isinstance(data, dict) and 'history' in data:
                            videos = data['history']

                    # Filter to last 30 days
                    cutoff_date = datetime.now() - timedelta(days=30)
                    filtered_videos = []
                    for video in videos:
                        try:
                            watch_date = None
                            if 'watch_date' in video:
                                watch_date = datetime.fromisoformat(video['watch_date'])
                            elif 'timestamp' in video:
                                watch_date = datetime.fromisoformat(video['timestamp'])
                            elif 'date' in video:
                                watch_date = datetime.fromisoformat(video['date'])

                            if watch_date and watch_date >= cutoff_date:
                                filtered_videos.append(video)
                        except:
                            # Include if we can't parse date
                            filtered_videos.append(video)

                    videos = filtered_videos
                    logger.info(f"   ✅ Found 30-day history: {len(videos)} videos")
                    break
                except Exception as e:
                    logger.debug(f"   Error reading {file_path}: {e}")

        if not videos:
            logger.info("   ℹ️  No 30-day history file found")
            logger.info("   ℹ️  Try running: python scripts/python/syphon_youtube_watch_history_30_days.py")

        return videos

    def _analyze_recently_viewed(self) -> List[Dict[str, Any]]:
        """Analyze recently viewed videos (last 7 days)"""
        videos = []

        # Get from history (last 7 days)
        cutoff_date = datetime.now() - timedelta(days=7)

        for video in self.history_videos:
            try:
                watch_date = None
                if 'watch_date' in video:
                    watch_date = datetime.fromisoformat(video['watch_date'])
                elif 'timestamp' in video:
                    watch_date = datetime.fromisoformat(video['timestamp'])
                elif 'date' in video:
                    watch_date = datetime.fromisoformat(video['date'])

                if watch_date and watch_date >= cutoff_date:
                    videos.append(video)
            except:
                pass

        logger.info(f"   ✅ Recently viewed (7 days): {len(videos)} videos")
        return videos

    def _analyze_learning_videos(self) -> List[Dict[str, Any]]:
        """Analyze learning videos from Lumina YouTube Learning"""
        videos = []

        if self.learning_dir.exists():
            for file_path in self.learning_dir.rglob("*.json"):
                try:
                    with open(file_path, 'r') as f:
                        video_data = json.load(f)

                        # Extract learnings
                        review = video_data.get('review', {})
                        learnings = review.get('learnings_for_lumina', []) or video_data.get('learnings', [])

                        video_info = {
                            'video_id': video_data.get('video_id', ''),
                            'url': video_data.get('url', ''),
                            'title': video_data.get('title', 'Unknown'),
                            'channel': video_data.get('channel', ''),
                            'rating': review.get('rating') if isinstance(review, dict) else None,
                            'learnings': learnings,
                            'metrics': video_data.get('metrics', {}),
                            'timestamp': video_data.get('timestamp', '')
                        }
                        videos.append(video_info)
                except Exception as e:
                    logger.debug(f"Error reading learning video {file_path}: {e}")

        logger.info(f"   ✅ Learning videos: {len(videos)} videos")
        return videos

    def _generate_insights(self) -> Dict[str, Any]:
        """Generate comprehensive insights"""
        insights = {
            'analysis_date': datetime.now().isoformat(),
            'sources': {
                'recommended_feed': len(self.recommended_videos),
                '30_day_history': len(self.history_videos),
                'recently_viewed': len(self.recently_viewed),
                'learning_videos': len(self.learning_videos)
            },
            'top_channels': {},
            'top_topics': {},
            'watch_patterns': {},
            'learnings': [],
            'recommendations': []
        }

        # Analyze channels
        all_videos = self.history_videos + self.recently_viewed
        for video in all_videos:
            channel = video.get('channel') or video.get('channel_name') or video.get('uploader')
            if channel:
                self.top_channels[channel] += 1

        insights['top_channels'] = dict(self.top_channels.most_common(10))

        # Analyze topics/themes
        for video in all_videos:
            title = video.get('title', '')
            description = video.get('description', '')
            text = (title + " " + description).lower()

            # Detect topics
            if any(word in text for word in ['ai', 'artificial intelligence', 'machine learning']):
                self.top_topics['AI/ML'] += 1
            if any(word in text for word in ['coding', 'programming', 'developer', 'software']):
                self.top_topics['Programming'] += 1
            if any(word in text for word in ['cinematic', 'film', 'movie', 'cinema']):
                self.top_topics['Cinematic'] += 1
            if any(word in text for word in ['star wars', 'darth', 'jedi', 'sith']):
                self.top_topics['Star Wars'] += 1
            if any(word in text for word in ['reaction', 'review', 'commentary']):
                self.top_topics['Reaction/Review'] += 1

        insights['top_topics'] = dict(self.top_topics.most_common(10))

        # Extract learnings from learning videos
        all_learnings = []
        for video in self.learning_videos:
            learnings = video.get('learnings', [])
            all_learnings.extend(learnings)

        insights['learnings'] = all_learnings

        # Watch patterns
        if self.history_videos:
            # Most watched day of week
            day_counts = Counter()
            for video in self.history_videos:
                try:
                    watch_date = None
                    if 'watch_date' in video:
                        watch_date = datetime.fromisoformat(video['watch_date'])
                    elif 'timestamp' in video:
                        watch_date = datetime.fromisoformat(video['timestamp'])

                    if watch_date:
                        day_counts[watch_date.strftime('%A')] += 1
                except:
                    pass

            insights['watch_patterns'] = {
                'most_active_day': day_counts.most_common(1)[0][0] if day_counts else None,
                'day_distribution': dict(day_counts)
            }

        # Generate recommendations
        insights['recommendations'] = self._generate_recommendations(insights)

        return insights

    def _generate_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on analysis"""
        recommendations = []

        # Based on top topics
        top_topic = max(insights['top_topics'].items(), key=lambda x: x[1]) if insights['top_topics'] else None
        if top_topic:
            recommendations.append(f"Continue exploring {top_topic[0]} content (watched {top_topic[1]} times)")

        # Based on learnings
        if insights['learnings']:
            recommendations.append(f"Apply {len(insights['learnings'])} learnings from analyzed videos")

        # Based on watch patterns
        if insights['watch_patterns'].get('most_active_day'):
            day = insights['watch_patterns']['most_active_day']
            recommendations.append(f"Most active viewing day: {day} - schedule content consumption accordingly")

        return recommendations

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive analysis report"""
        insights = self.analyze_all_sources()

        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_videos_analyzed': (
                    len(self.recommended_videos) +
                    len(self.history_videos) +
                    len(self.recently_viewed) +
                    len(self.learning_videos)
                ),
                'sources': insights['sources'],
                'top_channels_count': len(insights['top_channels']),
                'top_topics_count': len(insights['top_topics']),
                'total_learnings': len(insights['learnings'])
            },
            'insights': insights,
            'detailed': {
                'recommended_feed': self.recommended_videos[:10],  # Top 10
                'recently_viewed': self.recently_viewed[:10],
                'learning_videos': self.learning_videos,
                'top_channels': insights['top_channels'],
                'top_topics': insights['top_topics']
            }
        }

        return report


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description='JARVIS: Comprehensive YouTube Analysis')
        parser.add_argument('--report', action='store_true', help='Generate full report')
        parser.add_argument('--learnings-only', action='store_true', help='Show learnings only')
        parser.add_argument('--output', help='Output file for report')

        args = parser.parse_args()

        analyzer = JARVISYouTubeComprehensiveAnalysis()
        report = analyzer.get_comprehensive_report()

        if args.learnings_only:
            print("\n🧠 Learnings from YouTube:")
            print("=" * 80)
            for i, learning in enumerate(report['insights']['learnings'], 1):
                print(f"{i}. {learning}")
        elif args.report or not args.output:
            print("\n" + "=" * 80)
            print("🎥 JARVIS: Comprehensive YouTube Analysis Report")
            print("=" * 80)
            print(f"\n📊 Summary:")
            print(f"   Total Videos Analyzed: {report['summary']['total_videos_analyzed']}")
            print(f"   Recommended Feed: {report['summary']['sources']['recommended_feed']}")
            print(f"   30-Day History: {report['summary']['sources']['30_day_history']}")
            print(f"   Recently Viewed: {report['summary']['sources']['recently_viewed']}")
            print(f"   Learning Videos: {report['summary']['sources']['learning_videos']}")

            if report['detailed']['top_channels']:
                print(f"\n📺 Top Channels:")
                for channel, count in list(report['detailed']['top_channels'].items())[:5]:
                    print(f"   - {channel}: {count} videos")

            if report['detailed']['top_topics']:
                print(f"\n🎯 Top Topics:")
                for topic, count in list(report['detailed']['top_topics'].items())[:5]:
                    print(f"   - {topic}: {count} videos")

            if report['insights']['learnings']:
                print(f"\n🧠 Key Learnings ({len(report['insights']['learnings'])}):")
                for i, learning in enumerate(report['insights']['learnings'][:5], 1):
                    print(f"   {i}. {learning}")

            if report['insights']['recommendations']:
                print(f"\n💡 Recommendations:")
                for rec in report['insights']['recommendations']:
                    print(f"   - {rec}")

        if args.output:
            with open(args.output, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Report saved to: {args.output}")
        else:
            # Save default report
            report_file = analyzer.data_dir / "daily_work_cycles" / f"youtube_comprehensive_{datetime.now().strftime('%Y%m%d')}.json"
            report_file.parent.mkdir(parents=True, exist_ok=True)
            with open(report_file, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            print(f"\n📄 Report saved to: {report_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()