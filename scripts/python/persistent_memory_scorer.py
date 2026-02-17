#!/usr/bin/env python3
"""
🔄 **Lumina Persistent Memory Scorer**

Comprehensive memory and intent fulfillment scoring system (1-100%).
Tracks request completion quality, context retention, and improvement trends.
Provides comparative analysis and persistent scoring across interactions.

@V3_WORKFLOWED: True
@TEST_FIRST: True
@MEMORY_SCORING: Enabled
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import statistics

# Local imports
script_dir = Path(__file__).parent.parent
project_root = script_dir.parent
if str(project_root) not in os.sys.path:
    os.sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        def get_logger(name):
            return logging.getLogger(name)

logger = get_logger("PersistentMemoryScorer")


@dataclass
class MemoryScoreComponents:
    """Components that make up the memory score"""
    intent_understanding: float = 0.0  # How well intent was grasped (0-100)
    context_retention: float = 0.0     # How well context was maintained (0-100)
    completion_quality: float = 0.0    # Quality of task completion (0-100)
    user_satisfaction: float = 0.0     # Estimated user satisfaction (0-100)
    innovation_level: float = 0.0      # Innovative solutions provided (0-100)
    error_prevention: float = 0.0      # Errors avoided/mitigated (0-100)

    @property
    def overall_score(self) -> float:
        """Calculate overall memory score"""
        weights = {
            'intent_understanding': 0.25,
            'context_retention': 0.20,
            'completion_quality': 0.25,
            'user_satisfaction': 0.15,
            'innovation_level': 0.10,
            'error_prevention': 0.05
        }

        weighted_sum = sum(
            getattr(self, component) * weight
            for component, weight in weights.items()
        )

        return round(weighted_sum, 1)


@dataclass
class MemoryScoreRecord:
    """Record of a memory score evaluation"""
    timestamp: datetime
    request_id: str
    user_request: str
    ai_response: str
    components: MemoryScoreComponents
    overall_score: float
    improvement_trend: str  # "improving", "declining", "stable"
    comparison_previous: Optional[float] = None
    score_change: float = 0.0
    context_quality: str = "unknown"  # "excellent", "good", "fair", "poor"
    fulfillment_level: str = "unknown"  # "complete", "partial", "minimal", "failed"


@dataclass
class MemoryScoreTrends:
    """Trends analysis for memory scores"""
    average_score: float
    trend_direction: str  # "improving", "declining", "stable"
    volatility: float  # Score variation
    best_score: float
    worst_score: float
    recent_improvement: float  # Change over last 10 scores
    consistency_rating: str  # "excellent", "good", "fair", "poor"


class PersistentMemoryScorer:
    """
    Persistent Memory Scoring System for Lumina.

    Evaluates and tracks memory/context retention and intent fulfillment
    across interactions. Provides comparative analysis and trend tracking.
    """

    def __init__(self, db_path: str = None):
        self.project_root = Path(__file__).parent.parent.parent

        if db_path is None:
            self.db_path = self.project_root / "data" / "persistent_memory_scores.db"
        else:
            self.db_path = Path(db_path)

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

        # Scoring criteria weights and thresholds
        self.scoring_criteria = {
            'intent_understanding': {
                'excellent': 95, 'good': 80, 'fair': 60, 'poor': 40
            },
            'context_retention': {
                'excellent': 90, 'good': 75, 'fair': 55, 'poor': 35
            },
            'completion_quality': {
                'excellent': 95, 'good': 80, 'fair': 60, 'poor': 40
            },
            'user_satisfaction': {
                'excellent': 90, 'good': 75, 'fair': 55, 'poor': 35
            },
            'innovation_level': {
                'excellent': 85, 'good': 70, 'fair': 50, 'poor': 30
            },
            'error_prevention': {
                'excellent': 95, 'good': 80, 'fair': 60, 'poor': 40
            }
        }

        logger.info("✅ Persistent Memory Scorer initialized")

    def _init_database(self):
        try:
            """Initialize the memory scoring database"""
            with sqlite3.connect(self.db_path) as conn:
                # Memory scores table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS memory_scores (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp TEXT NOT NULL,
                        request_id TEXT NOT NULL,
                        user_request TEXT NOT NULL,
                        ai_response TEXT,
                        intent_understanding REAL,
                        context_retention REAL,
                        completion_quality REAL,
                        user_satisfaction REAL,
                        innovation_level REAL,
                        error_prevention REAL,
                        overall_score REAL,
                        improvement_trend TEXT,
                        comparison_previous REAL,
                        score_change REAL,
                        context_quality TEXT,
                        fulfillment_level TEXT
                    )
                ''')

                # Scoring metadata table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS scoring_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                ''')

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def evaluate_memory_score(self, request_id: str, user_request: str,
                             ai_response: str, context_info: Dict[str, Any] = None) -> MemoryScoreRecord:
        """
        Evaluate memory and intent fulfillment for a request-response pair

        Args:
            request_id: Unique identifier for the request
            user_request: The user's original request
            ai_response: The AI's response
            context_info: Additional context about the interaction

        Returns:
            MemoryScoreRecord with detailed scoring
        """

        # Analyze the request and response
        components = self._analyze_interaction(user_request, ai_response, context_info or {})

        # Calculate overall score
        overall_score = components.overall_score

        # Get previous score for comparison
        previous_score = self._get_previous_score()
        score_change = overall_score - (previous_score or overall_score)

        # Determine improvement trend
        improvement_trend = self._calculate_improvement_trend(overall_score, previous_score)

        # Assess context quality and fulfillment
        context_quality = self._assess_context_quality(components.context_retention)
        fulfillment_level = self._assess_fulfillment_level(components.completion_quality)

        # Create score record
        record = MemoryScoreRecord(
            timestamp=datetime.now(),
            request_id=request_id,
            user_request=user_request,
            ai_response=ai_response,
            components=components,
            overall_score=overall_score,
            improvement_trend=improvement_trend,
            comparison_previous=previous_score,
            score_change=score_change,
            context_quality=context_quality,
            fulfillment_level=fulfillment_level
        )

        # Store the record
        self._store_score_record(record)

        # Update metadata
        self._update_metadata(record)

        logger.info(".1f")
        return record

    def _analyze_interaction(self, user_request: str, ai_response: str,
                           context_info: Dict[str, Any]) -> MemoryScoreComponents:
        """Analyze the user request and AI response for memory scoring"""

        components = MemoryScoreComponents()

        # Intent Understanding (25% weight)
        components.intent_understanding = self._score_intent_understanding(
            user_request, ai_response, context_info
        )

        # Context Retention (20% weight)
        components.context_retention = self._score_context_retention(
            user_request, ai_response, context_info
        )

        # Completion Quality (25% weight)
        components.completion_quality = self._score_completion_quality(
            user_request, ai_response, context_info
        )

        # User Satisfaction (15% weight)
        components.user_satisfaction = self._score_user_satisfaction(
            user_request, ai_response, context_info
        )

        # Innovation Level (10% weight)
        components.innovation_level = self._score_innovation_level(
            user_request, ai_response, context_info
        )

        # Error Prevention (5% weight)
        components.error_prevention = self._score_error_prevention(
            user_request, ai_response, context_info
        )

        return components

    def _score_intent_understanding(self, request: str, response: str, context: Dict) -> float:
        """Score how well the AI understood the user's intent"""

        request_lower = request.lower()
        response_lower = response.lower()

        # Keywords indicating intent understanding
        understanding_indicators = [
            # Direct acknowledgment
            "i understand", "got it", "understood", "acknowledge",

            # Specific references to user request
            "as requested", "as you asked", "per your request",
            "following your instructions", "based on your request",

            # Task completion indicators
            "completed", "implemented", "created", "delivered",
            "provided", "finished", "done"
        ]

        # Check for understanding indicators
        understanding_score = 0
        found_indicators = 0

        for indicator in understanding_indicators:
            if indicator in response_lower:
                found_indicators += 1

        understanding_score = min(100, (found_indicators / len(understanding_indicators)) * 120)

        # Bonus for detailed explanations
        if len(response) > 500:
            understanding_score += 10

        # Check for context awareness
        if context.get('previous_interactions', 0) > 0:
            understanding_score += 15  # Continuity bonus

        return min(100, max(0, understanding_score))

    def _score_context_retention(self, request: str, response: str, context: Dict) -> float:
        """Score how well context was retained from previous interactions"""

        context_score = 50  # Base score

        # Check for continuity indicators
        continuity_indicators = [
            "previously", "earlier", "before", "continuing",
            "building on", "following up", "as discussed",
            "per our previous", "extending"
        ]

        continuity_found = sum(1 for ind in continuity_indicators if ind in response.lower())
        context_score += min(30, continuity_found * 8)

        # Previous interaction bonus
        prev_interactions = context.get('previous_interactions', 0)
        context_score += min(20, prev_interactions * 5)

        # Reference to specific previous elements
        if context.get('referenced_previous', False):
            context_score += 15

        return min(100, max(0, context_score))

    def _score_completion_quality(self, request: str, response: str, context: Dict) -> float:
        """Score the quality of task completion"""

        completion_score = 0

        # Check for deliverables
        deliverables_indicators = [
            "created", "implemented", "generated", "completed",
            "delivered", "provided", "finished", "✅", "🎉",
            "complete", "done", "ready"
        ]

        deliverables_found = sum(1 for ind in deliverables_indicators if ind in response.lower())
        completion_score += min(50, deliverables_found * 12)

        # Check for comprehensive response
        if len(response) > 1000:
            completion_score += 20
        elif len(response) > 500:
            completion_score += 10

        # Check for structured output
        if "```" in response or "📋" in response:
            completion_score += 15

        # Error-free bonus
        if "error" not in response.lower() or "failed" not in response.lower():
            completion_score += 10

        return min(100, max(0, completion_score))

    def _score_user_satisfaction(self, request: str, response: str, context: Dict) -> float:
        """Estimate user satisfaction based on response quality"""

        satisfaction_score = 60  # Base satisfaction

        # Positive indicators
        positive_indicators = [
            "successfully", "perfectly", "excellent", "great",
            "fantastic", "wonderful", "amazing", "brilliant",
            "🎉", "✅", "🚀", "💯"
        ]

        positive_found = sum(1 for ind in positive_indicators if ind in response.lower())
        satisfaction_score += min(30, positive_found * 8)

        # Clear communication bonus
        if "```" in response and len(response.split("```")) > 2:
            satisfaction_score += 10

        # Comprehensive explanation
        if len(response) > 800:
            satisfaction_score += 10

        # No confusion indicators
        confusion_indicators = ["confused", "unclear", "unsure", "sorry"]
        confusion_found = sum(1 for ind in confusion_indicators if ind in response.lower())
        satisfaction_score -= confusion_found * 15

        return min(100, max(0, satisfaction_score))

    def _score_innovation_level(self, request: str, response: str, context: Dict) -> float:
        """Score the level of innovation in the response"""

        innovation_score = 30  # Base innovation

        # Innovation indicators
        innovation_indicators = [
            "innovative", "creative", "novel", "advanced",
            "cutting-edge", "revolutionary", "breakthrough",
            "pioneering", "groundbreaking", "unique"
        ]

        innovation_found = sum(1 for ind in innovation_indicators if ind in response.lower())
        innovation_score += min(40, innovation_found * 10)

        # Technical sophistication
        if "framework" in response.lower() or "architecture" in response.lower():
            innovation_score += 15

        # Multiple solutions offered
        if response.count("option") > 1 or response.count("approach") > 1:
            innovation_score += 10

        return min(100, max(0, innovation_score))

    def _score_error_prevention(self, request: str, response: str, context: Dict) -> float:
        """Score error prevention and mitigation"""

        prevention_score = 80  # High base for error prevention

        # Error handling indicators
        error_handling = [
            "error handling", "exception", "try:", "except:",
            "validation", "verification", "testing", "safety"
        ]

        handling_found = sum(1 for ind in error_handling if ind in response.lower())
        prevention_score += min(15, handling_found * 5)

        # Risk mitigation
        risk_indicators = [
            "backup", "recovery", "failover", "redundancy",
            "monitoring", "alerts", "logging"
        ]

        risk_found = sum(1 for ind in risk_indicators if ind in response.lower())
        prevention_score += min(10, risk_found * 3)

        # Error penalties
        error_indicators = ["error", "failed", "failure", "crash", "bug"]
        errors_found = sum(1 for ind in error_indicators if ind in response.lower())
        prevention_score -= errors_found * 8

        return min(100, max(0, prevention_score))

    def _get_previous_score(self) -> Optional[float]:
        try:
            """Get the most recent memory score"""
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT overall_score FROM memory_scores
                    ORDER BY timestamp DESC LIMIT 1
                ''')

                row = cursor.fetchone()
                return row[0] if row else None

        except Exception as e:
            self.logger.error(f"Error in _get_previous_score: {e}", exc_info=True)
            raise
    def _calculate_improvement_trend(self, current_score: float, previous_score: Optional[float]) -> str:
        """Calculate improvement trend"""

        if previous_score is None:
            return "baseline"

        change = current_score - previous_score

        if change > 5:
            return "improving"
        elif change < -5:
            return "declining"
        else:
            return "stable"

    def _assess_context_quality(self, context_retention: float) -> str:
        """Assess context quality rating"""
        if context_retention >= 80:
            return "excellent"
        elif context_retention >= 60:
            return "good"
        elif context_retention >= 40:
            return "fair"
        else:
            return "poor"

    def _assess_fulfillment_level(self, completion_quality: float) -> str:
        """Assess fulfillment level"""
        if completion_quality >= 85:
            return "complete"
        elif completion_quality >= 65:
            return "partial"
        elif completion_quality >= 35:
            return "minimal"
        else:
            return "failed"

    def _store_score_record(self, record: MemoryScoreRecord):
        try:
            """Store a memory score record in the database"""

            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO memory_scores (
                        timestamp, request_id, user_request, ai_response,
                        intent_understanding, context_retention, completion_quality,
                        user_satisfaction, innovation_level, error_prevention,
                        overall_score, improvement_trend, comparison_previous,
                        score_change, context_quality, fulfillment_level
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    record.timestamp.isoformat(),
                    record.request_id,
                    record.user_request,
                    record.ai_response,
                    record.components.intent_understanding,
                    record.components.context_retention,
                    record.components.completion_quality,
                    record.components.user_satisfaction,
                    record.components.innovation_level,
                    record.components.error_prevention,
                    record.overall_score,
                    record.improvement_trend,
                    record.comparison_previous,
                    record.score_change,
                    record.context_quality,
                    record.fulfillment_level
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _store_score_record: {e}", exc_info=True)
            raise
    def _update_metadata(self, record: MemoryScoreRecord):
        try:
            """Update scoring metadata"""

            with sqlite3.connect(self.db_path) as conn:
                # Update last score
                conn.execute('''
                    INSERT OR REPLACE INTO scoring_metadata (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', ('last_score', str(record.overall_score), datetime.now().isoformat()))

                # Update score count
                cursor = conn.execute('SELECT COUNT(*) FROM memory_scores')
                count = cursor.fetchone()[0]

                conn.execute('''
                    INSERT OR REPLACE INTO scoring_metadata (key, value, updated_at)
                    VALUES (?, ?, ?)
                ''', ('total_scores', str(count), datetime.now().isoformat()))

                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _update_metadata: {e}", exc_info=True)
            raise
    def get_memory_score_report(self, days_back: int = 30) -> Dict[str, Any]:
        """Generate a comprehensive memory score report"""

        cutoff_date = datetime.now() - timedelta(days=days_back)

        with sqlite3.connect(self.db_path) as conn:
            # Get recent scores
            cursor = conn.execute('''
                SELECT overall_score, improvement_trend, context_quality, fulfillment_level
                FROM memory_scores
                WHERE timestamp >= ?
                ORDER BY timestamp DESC
            ''', (cutoff_date.isoformat(),))

            scores = []
            trends = []
            context_qualities = []
            fulfillment_levels = []

            for row in cursor.fetchall():
                score, trend, context, fulfillment = row
                scores.append(score)
                trends.append(trend)
                context_qualities.append(context)
                fulfillment_levels.append(fulfillment)

            # Calculate statistics
            if scores:
                avg_score = statistics.mean(scores)
                best_score = max(scores)
                worst_score = min(scores)
                volatility = statistics.stdev(scores) if len(scores) > 1 else 0

                # Trend analysis
                improving_count = trends.count("improving")
                declining_count = trends.count("declining")
                stable_count = trends.count("stable")

                if improving_count > declining_count and improving_count > stable_count:
                    overall_trend = "improving"
                elif declining_count > improving_count:
                    overall_trend = "declining"
                else:
                    overall_trend = "stable"

                # Context quality distribution
                context_distribution = {
                    quality: context_qualities.count(quality)
                    for quality in ["excellent", "good", "fair", "poor"]
                }

                # Fulfillment distribution
                fulfillment_distribution = {
                    level: fulfillment_levels.count(level)
                    for level in ["complete", "partial", "minimal", "failed"]
                }

                # Recent improvement (last 5 scores)
                recent_scores = scores[:5] if len(scores) >= 5 else scores
                if len(recent_scores) > 1:
                    recent_improvement = recent_scores[0] - recent_scores[-1]
                else:
                    recent_improvement = 0

                # Consistency rating
                if volatility < 5:
                    consistency = "excellent"
                elif volatility < 10:
                    consistency = "good"
                elif volatility < 20:
                    consistency = "fair"
                else:
                    consistency = "poor"

                trends_analysis = MemoryScoreTrends(
                    average_score=round(avg_score, 1),
                    trend_direction=overall_trend,
                    volatility=round(volatility, 1),
                    best_score=round(best_score, 1),
                    worst_score=round(worst_score, 1),
                    recent_improvement=round(recent_improvement, 1),
                    consistency_rating=consistency
                )

                return {
                    'period_days': days_back,
                    'total_scores': len(scores),
                    'trends': trends_analysis,
                    'distributions': {
                        'context_quality': context_distribution,
                        'fulfillment_level': fulfillment_distribution,
                        'improvement_trends': {
                            'improving': improving_count,
                            'declining': declining_count,
                            'stable': stable_count
                        }
                    },
                    'recent_scores': scores[:10],  # Last 10 scores
                    'generated_at': datetime.now().isoformat()
                }
            else:
                return {
                    'period_days': days_back,
                    'total_scores': 0,
                    'message': 'No scores available for the specified period',
                    'generated_at': datetime.now().isoformat()
                }

    def get_current_memory_score(self) -> Optional[float]:
        """Get the most current memory score"""
        return self._get_previous_score()

    def export_memory_scores(self, format: str = 'json') -> str:
        """Export memory scores for analysis"""

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('SELECT * FROM memory_scores ORDER BY timestamp DESC')

            scores_data = []
            columns = [desc[0] for desc in cursor.description]

            for row in cursor.fetchall():
                score_dict = dict(zip(columns, row))
                scores_data.append(score_dict)

        if format == 'json':
            return json.dumps({
                'export_timestamp': datetime.now().isoformat(),
                'total_scores': len(scores_data),
                'scores': scores_data
            }, indent=2, default=str)
        else:
            # Simple text format
            output = [f"Lumina Memory Scores Export - {datetime.now().isoformat()}\n"]
            output.append(f"Total Scores: {len(scores_data)}\n")

            for score in scores_data[:10]:  # Last 10 scores
                output.append(f"Score: {score['overall_score']:.1f} - Trend: {score['improvement_trend']} - {score['timestamp'][:10]}")

            return '\n'.join(output)


# Global instance
_memory_scorer = None


def get_memory_scorer() -> PersistentMemoryScorer:
    """Get or create memory scorer instance"""
    global _memory_scorer
    if _memory_scorer is None:
        _memory_scorer = PersistentMemoryScorer()
    return _memory_scorer


def score_memory_performance(request_id: str, user_request: str, ai_response: str,
                           context_info: Dict[str, Any] = None) -> MemoryScoreRecord:
    """Convenience function to score memory performance"""
    scorer = get_memory_scorer()
    return scorer.evaluate_memory_score(request_id, user_request, ai_response, context_info)


def get_memory_score_report(days_back: int = 30) -> Dict[str, Any]:
    """Get memory score report"""
    scorer = get_memory_scorer()
    return scorer.get_memory_score_report(days_back)


def get_current_memory_score() -> Optional[float]:
    """Get current memory score"""
    scorer = get_memory_scorer()
    return scorer.get_current_memory_score()


if __name__ == "__main__":
    # Test the memory scorer
    import argparse

    parser = argparse.ArgumentParser(description="Lumina Persistent Memory Scorer")
    parser.add_argument("--score", action="store_true", help="Score a test interaction")
    parser.add_argument("--report", action="store_true", help="Generate memory score report")
    parser.add_argument("--current", action="store_true", help="Get current memory score")
    parser.add_argument("--export", type=str, help="Export scores (json/text)")

    args = parser.parse_args()

    scorer = get_memory_scorer()

    if args.score:
        # Test scoring
        test_request = "Create a persistent memory scoring system from 1-100%"
        test_response = """
        I have successfully created a comprehensive persistent memory scoring system
        that evaluates AI performance on a scale of 1-100%. The system tracks intent
        understanding, context retention, completion quality, user satisfaction,
        innovation level, and error prevention. It provides comparative analysis
        and trend tracking across interactions.
        """

        record = scorer.evaluate_memory_score(
            request_id="test_001",
            user_request=test_request,
            ai_response=test_response,
            context_info={"interaction_type": "test"}
        )

        print("🎯 **Memory Score Evaluation**")
        print("=" * 40)
        print(f"Overall Score: {record.overall_score:.1f}%")
        print(f"Intent Understanding: {record.components.intent_understanding:.1f}%")
        print(f"Context Retention: {record.components.context_retention:.1f}%")
        print(f"Completion Quality: {record.components.completion_quality:.1f}%")
        print(f"User Satisfaction: {record.components.user_satisfaction:.1f}%")
        print(f"Innovation Level: {record.components.innovation_level:.1f}%")
        print(f"Error Prevention: {record.components.error_prevention:.1f}%")
        print(f"Improvement Trend: {record.improvement_trend}")
        print(f"Context Quality: {record.context_quality}")
        print(f"Fulfillment Level: {record.fulfillment_level}")

    elif args.report:
        # Generate report
        report = scorer.get_memory_score_report(days_back=30)
        print("📊 **Memory Score Report**")
        print("=" * 40)

        if report['total_scores'] > 0:
            trends = report['trends']
            print(f"Total Scores: {report['total_scores']}")
            print(f"Average Score: {trends.average_score:.1f}%")
            print(f"Trend Direction: {trends.trend_direction}")
            print(f"Best Score: {trends.best_score:.1f}%")
            print(f"Worst Score: {trends.worst_score:.1f}%")
            print(f"Consistency: {trends.consistency_rating}")
            print(f"Recent Improvement: {trends.recent_improvement:.1f}%")
        else:
            print("No scores available")

    elif args.current:
        # Get current score
        current = scorer.get_current_memory_score()
        if current:
            print(f"Current Memory Score: {current:.1f}%")
        else:
            print("No current score available")

    elif args.export:
        # Export scores
        export_data = scorer.export_memory_scores(args.export)
        print(export_data)

    else:
        # Default: show help
        parser.print_help()