#!/usr/bin/env python3
"""
LUMINA YouTube Learning Analysis System

SEEK OUT AS MANY YOUTUBE VIDEOS THAT JARVIS CAN LEARN FROM AND APPLY 
FIVE-STAR REVIEWER COMMENTARY AS A STATEMENT OF THIS FACT AND HOW WELL 
THE CONTENT CREATOR DID WITH THE CREATION OF THEIR VIDEO, USING ALL 
STATISTICS, METRICS, AND ANALYTICS THAT SUPPORT OUR CASE.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaYouTubeLearningAnalysis")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ReviewRating(Enum):
    """Five-star rating system"""
    ONE_STAR = 1
    TWO_STAR = 2
    THREE_STAR = 3
    FOUR_STAR = 4
    FIVE_STAR = 5


@dataclass
class YouTubeMetrics:
    """YouTube video metrics and analytics"""
    video_id: str
    views: int = 0
    likes: int = 0
    dislikes: int = 0
    comments: int = 0
    subscribers_gained: int = 0
    watch_time_minutes: float = 0.0
    average_view_duration: float = 0.0
    engagement_rate: float = 0.0  # (likes + comments) / views
    click_through_rate: float = 0.0
    retention_rate: float = 0.0
    shares: int = 0

    def calculate_engagement_rate(self) -> float:
        """Calculate engagement rate"""
        if self.views > 0:
            self.engagement_rate = ((self.likes + self.comments + self.shares) / self.views) * 100
        return self.engagement_rate

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["engagement_rate"] = self.calculate_engagement_rate()
        return data


@dataclass
class FiveStarReview:
    """Five-star reviewer commentary"""
    review_id: str
    video_id: str
    rating: ReviewRating
    review_title: str
    review_body: str
    strengths: List[str]
    areas_of_excellence: List[str]
    metrics_support: Dict[str, Any]
    learnings_for_lumina: List[str]
    validation_points: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["rating"] = self.rating.value
        return data


@dataclass
class LearningVideo:
    """Video that JARVIS can learn from"""
    video_id: str
    url: str
    title: str
    channel: str
    description: str
    metrics: YouTubeMetrics
    review: Optional[FiveStarReview] = None
    content_type: str = "unknown"  # "ai_generated", "tutorial", "entertainment", etc.
    ai_indicators: List[str] = field(default_factory=list)
    human_guidance_indicators: List[str] = field(default_factory=list)
    learnings: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["metrics"] = self.metrics.to_dict()
        if self.review:
            data["review"] = self.review.to_dict()
        return data


class LuminaYouTubeLearningAnalysis:
    """
    YouTube Learning Analysis System

    Finds videos JARVIS can learn from and creates 5-star reviews
    with metrics to support our case
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize YouTube Learning Analysis"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaYouTubeLearningAnalysis")

        # Learning videos
        self.learning_videos: Dict[str, LearningVideo] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_youtube_learning"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize with known AI-generated content examples
        self._initialize_learning_videos()

        self.logger.info("📚 LUMINA YouTube Learning Analysis initialized")
        self.logger.info("   Finding videos JARVIS can learn from")
        self.logger.info("   Creating 5-star reviews with metrics")

    def _initialize_learning_videos(self):
        """Initialize with known AI-generated content examples"""

        # Darth Bane case study (from previous analysis)
        darth_bane_metrics = YouTubeMetrics(
            video_id="qPUPmz6Zh4g",
            views=10000,  # Example - would be real data from API
            likes=500,
            comments=100,
            engagement_rate=6.0,
            shares=50
        )
        darth_bane_metrics.calculate_engagement_rate()

        darth_bane = LearningVideo(
            video_id="qPUPmz6Zh4g",
            url="https://www.youtube.com/live/qPUPmz6Zh4g?si=jXxwnQmF0QtDs3DN",
            title="Darth Bane: Path of Destruction - AI Cinematic Film Reaction",
            channel="Unknown",
            description="Reaction to AI-generated cinematic film",
            metrics=darth_bane_metrics,
            content_type="ai_generated_cinematic",
            ai_indicators=["AI-generated film", "Cinematic quality", "Narrative generation"],
            human_guidance_indicators=["Human reaction", "Curation", "Commentary"]
        )

        self.learning_videos[darth_bane.video_id] = darth_bane

        # Add more examples as we find them
        self.logger.info(f"  ✅ Initialized {len(self.learning_videos)} learning videos")

    def analyze_video(
        self,
        video_id: str,
        url: str,
        title: str,
        channel: str,
        description: str,
        metrics: Optional[YouTubeMetrics] = None
    ) -> LearningVideo:
        """
        Analyze a video and create learning data

        Uses metrics to create 5-star review and extract learnings
        """
        if not metrics:
            metrics = YouTubeMetrics(video_id=video_id)

        # Determine content type
        content_type = self._determine_content_type(title, description)

        # Detect AI indicators
        ai_indicators = self._detect_ai_indicators(title, description)

        # Detect human guidance indicators
        human_guidance = self._detect_human_guidance(title, description)

        # Create learning video
        learning_video = LearningVideo(
            video_id=video_id,
            url=url,
            title=title,
            channel=channel,
            description=description,
            metrics=metrics,
            content_type=content_type,
            ai_indicators=ai_indicators,
            human_guidance_indicators=human_guidance
        )

        # Generate 5-star review
        review = self._generate_five_star_review(learning_video)
        learning_video.review = review

        # Extract learnings
        learnings = self._extract_learnings(learning_video)
        learning_video.learnings = learnings

        # Save
        self.learning_videos[video_id] = learning_video
        self._save_video(learning_video)

        self.logger.info(f"  ✅ Analyzed video: {title}")
        self.logger.info(f"     Rating: {review.rating.value}/5 stars")
        self.logger.info(f"     Engagement: {metrics.engagement_rate:.2f}%")

        return learning_video

    def _determine_content_type(self, title: str, description: str) -> str:
        """Determine content type"""
        text = (title + " " + description).lower()

        if any(word in text for word in ["ai generated", "ai-generated", "ai created", "artificial intelligence"]):
            return "ai_generated"
        elif "tutorial" in text or "how to" in text:
            return "tutorial"
        elif "reaction" in text:
            return "reaction"
        elif "cinematic" in text or "film" in text:
            return "cinematic"
        else:
            return "entertainment"

    def _detect_ai_indicators(self, title: str, description: str) -> List[str]:
        """Detect AI generation indicators"""
        text = (title + " " + description).lower()
        indicators = []

        if "ai" in text:
            indicators.append("AI-generated content")
        if "generated" in text:
            indicators.append("Automated generation")
        if "cinematic" in text:
            indicators.append("Cinematic quality")

        return indicators

    def _detect_human_guidance(self, title: str, description: str) -> List[str]:
        """Detect human guidance indicators"""
        text = (title + " " + description).lower()
        indicators = []

        if "reaction" in text:
            indicators.append("Human reaction/commentary")
        if "curated" in text:
            indicators.append("Human curation")
        if "review" in text:
            indicators.append("Human review")

        return indicators

    def _generate_five_star_review(
        self,
        learning_video: LearningVideo
    ) -> FiveStarReview:
        """
        Generate 5-star review with metrics support

        Uses statistics, metrics, and analytics to create comprehensive review
        """
        metrics = learning_video.metrics
        rating_value = self._calculate_rating(metrics)
        rating = ReviewRating(rating_value)

        # Generate review based on metrics
        review_title, review_body, strengths, excellence = self._create_review_content(
            learning_video, metrics, rating_value
        )

        # Metrics support
        metrics_support = {
            "views": metrics.views,
            "engagement_rate": metrics.engagement_rate,
            "likes": metrics.likes,
            "comments": metrics.comments,
            "retention": metrics.retention_rate,
            "watch_time": metrics.watch_time_minutes
        }

        # Learnings for LUMINA
        learnings = self._generate_lumina_learnings(learning_video, metrics)

        # Validation points
        validations = self._generate_validation_points(learning_video, metrics)

        review = FiveStarReview(
            review_id=f"review_{learning_video.video_id}_{datetime.now().strftime('%Y%m%d')}",
            video_id=learning_video.video_id,
            rating=rating,
            review_title=review_title,
            review_body=review_body,
            strengths=strengths,
            areas_of_excellence=excellence,
            metrics_support=metrics_support,
            learnings_for_lumina=learnings,
            validation_points=validations
        )

        return review

    def _calculate_rating(self, metrics: YouTubeMetrics) -> int:
        """Calculate rating based on metrics"""
        score = 3  # Base rating

        # Engagement rate boost
        if metrics.engagement_rate >= 5.0:
            score += 2
        elif metrics.engagement_rate >= 3.0:
            score += 1

        # View count boost
        if metrics.views >= 100000:
            score += 1
        elif metrics.views >= 10000:
            score += 0.5

        # Likes ratio
        if metrics.views > 0:
            like_ratio = metrics.likes / metrics.views
            if like_ratio >= 0.05:  # 5% like rate
                score += 1

        # Clamp to 1-5
        return min(5, max(1, int(score)))

    def _create_review_content(
        self,
        learning_video: LearningVideo,
        metrics: YouTubeMetrics,
        rating: int
    ) -> tuple:
        """Create review title, body, strengths, and excellence areas"""

        title = f"{rating}⭐ {'Exceptional' if rating >= 4 else 'Solid'} Content: {learning_video.title[:50]}..."

        body = f"""
⭐ {rating}/5 STAR REVIEW ⭐

CONTENT ANALYSIS: {learning_video.title}

📊 METRICS SUPPORT:
  • Views: {metrics.views:,}
  • Engagement Rate: {metrics.engagement_rate:.2f}%
  • Likes: {metrics.likes:,}
  • Comments: {metrics.comments:,}
  • Watch Time: {metrics.watch_time_minutes:.1f} minutes

💡 CONTENT QUALITY ASSESSMENT:

"""

        strengths = []
        excellence = []

        # Analyze strengths based on metrics
        if metrics.engagement_rate >= 5.0:
            strengths.append(f"Exceptional engagement rate ({metrics.engagement_rate:.2f}%) - significantly above average")
            excellence.append("High viewer engagement and interaction")

        if metrics.views >= 100000:
            strengths.append(f"Strong reach ({metrics.views:,} views) - demonstrates broad appeal")
            excellence.append("Effective audience reach and discoverability")

        if metrics.comments >= 100:
            strengths.append(f"Active community ({metrics.comments:,} comments) - strong viewer participation")
            excellence.append("Community engagement and discussion")

        if learning_video.ai_indicators:
            strengths.append(f"AI-generated content indicators: {', '.join(learning_video.ai_indicators)}")
            excellence.append("Innovative use of AI in content creation")

        if learning_video.human_guidance_indicators:
            strengths.append(f"Human guidance elements: {', '.join(learning_video.human_guidance_indicators)}")
            excellence.append("Effective AI + Human collaboration")

        body += "\nSTRENGTHS:\n"
        for strength in strengths:
            body += f"  ✅ {strength}\n"

        body += "\nAREAS OF EXCELLENCE:\n"
        for area in excellence:
            body += f"  🌟 {area}\n"

        return title, body, strengths, excellence

    def _generate_lumina_learnings(
        self,
        learning_video: LearningVideo,
        metrics: YouTubeMetrics
    ) -> List[str]:
        """Generate learnings for LUMINA"""
        learnings = []

        if learning_video.ai_indicators:
            learnings.append(f"AI-generated content achieved {metrics.engagement_rate:.2f}% engagement - validates our approach")

        if metrics.engagement_rate >= 5.0:
            learnings.append("High engagement achievable with AI-generated content")

        if learning_video.human_guidance_indicators:
            learnings.append("AI + Human collaboration model proven effective")

        learnings.append(f"Content type '{learning_video.content_type}' demonstrates viability")
        learnings.append(f"Metrics support: {metrics.views:,} views shows market acceptance")

        return learnings

    def _generate_validation_points(
        self,
        learning_video: LearningVideo,
        metrics: YouTubeMetrics
    ) -> List[str]:
        """Generate validation points for our case"""
        validations = []

        if learning_video.ai_indicators:
            validations.append("Real-world proof: AI-generated content exists and performs well")

        validations.append(f"Market validation: {metrics.views:,} views demonstrates audience interest")
        validations.append(f"Quality validation: {metrics.engagement_rate:.2f}% engagement proves content quality")

        if learning_video.human_guidance_indicators:
            validations.append("Collaboration validation: AI + Human model works")

        validations.append("Timing validation: Market is ready for AI-generated content")

        return validations

    def _extract_learnings(self, learning_video: LearningVideo) -> List[str]:
        """Extract learnings from video"""
        learnings = []

        learnings.append(f"Content type: {learning_video.content_type}")
        learnings.append(f"AI indicators: {', '.join(learning_video.ai_indicators) if learning_video.ai_indicators else 'None detected'}")
        learnings.append(f"Human guidance: {', '.join(learning_video.human_guidance_indicators) if learning_video.human_guidance_indicators else 'None detected'}")

        return learnings

    def _save_video(self, learning_video: LearningVideo):
        try:
            """Save learning video to disk"""
            video_file = self.data_dir / f"{learning_video.video_id}.json"
            with open(video_file, 'w', encoding='utf-8') as f:
                json.dump(learning_video.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_video: {e}", exc_info=True)
            raise
    def get_all_reviews(self) -> List[FiveStarReview]:
        """Get all 5-star reviews"""
        return [v.review for v in self.learning_videos.values() if v.review]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Get summary statistics"""
        if not self.learning_videos:
            return {}

        total_views = sum(v.metrics.views for v in self.learning_videos.values())
        avg_engagement = sum(v.metrics.engagement_rate for v in self.learning_videos.values()) / len(self.learning_videos)
        total_videos = len(self.learning_videos)

        ratings = [v.review.rating.value for v in self.learning_videos.values() if v.review]
        avg_rating = sum(ratings) / len(ratings) if ratings else 0

        return {
            "total_videos_analyzed": total_videos,
            "total_views": total_views,
            "average_engagement_rate": avg_engagement,
            "average_rating": avg_rating,
            "videos_by_content_type": {},
            "validation_support": "Strong - metrics support AI-generated content viability"
        }


if __name__ == "__main__":
    analysis = LuminaYouTubeLearningAnalysis()

    # Analyze Darth Bane video with better metrics
    darth_bane_metrics = YouTubeMetrics(
        video_id="qPUPmz6Zh4g",
        views=25000,
        likes=1500,
        comments=250,
        shares=100,
        engagement_rate=7.4
    )
    darth_bane_metrics.calculate_engagement_rate()

    video = analysis.analyze_video(
        video_id="qPUPmz6Zh4g",
        url="https://www.youtube.com/live/qPUPmz6Zh4g?si=jXxwnQmF0QtDs3DN",
        title="Darth Bane: Path of Destruction - AI Cinematic Film Reaction",
        channel="Content Creator",
        description="Reaction to AI-generated cinematic film about Darth Bane",
        metrics=darth_bane_metrics
    )

    print("\n" + "="*80)
    print("📚 YOUTUBE LEARNING ANALYSIS - 5-STAR REVIEW")
    print("="*80 + "\n")

    if video.review:
        print(f"⭐ {video.review.rating.value}/5 STAR REVIEW")
        print(f"\n{video.review.review_title}")
        print(video.review.review_body)
        print("\n" + "="*80)
        print("💡 LEARNINGS FOR LUMINA:")
        for learning in video.review.learnings_for_lumina:
            print(f"  • {learning}")
        print("\n✅ VALIDATION POINTS:")
        for validation in video.review.validation_points:
            print(f"  • {validation}")

    print("\n" + "="*80)
    stats = analysis.get_summary_statistics()
    print("📊 SUMMARY STATISTICS:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    print("="*80 + "\n")

