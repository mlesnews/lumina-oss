"""
JARVIS @REC Recommendations Handler
Handles @REC tag for requesting AI recommendations.

@REC = Recommendations (asking AI for recommendations)

Author: JARVIS System
Date: 2026-01-09
Tags: #JARVIS @LUMINA #SHORT_TAGS @REC
"""

import re
from typing import Dict, List, Any, Optional
from pathlib import Path

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger(__name__)


class JARVISRECRecommendationsHandler:
    """
    Handles @REC tag for AI recommendations.

    @REC = Recommendations
    - Asking AI for recommendations, suggestions, or advice
    - Part of shorthand metatagging system
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize @REC recommendations handler.

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)

    def detect_rec_tag(self, message: str) -> bool:
        """
        Detect @REC tag in message.

        Args:
            message: User message

        Returns:
            True if @REC tag detected
        """
        # Case-insensitive match for @REC
        pattern = r'@REC\b'
        return bool(re.search(pattern, message, re.IGNORECASE))

    def extract_recommendation_request(self, message: str) -> Dict[str, Any]:
        """
        Extract recommendation request from message.

        Args:
            message: User message with @REC tag

        Returns:
            Dictionary with request details
        """
        request = {
            'has_rec_tag': self.detect_rec_tag(message),
            'message': message,
            'topics': [],
            'context': None,
            'specific_questions': []
        }

        if not request['has_rec_tag']:
            return request

        # Extract topics (after @REC)
        rec_match = re.search(r'@REC\s*(.+?)(?:\n|$)', message, re.IGNORECASE | re.DOTALL)
        if rec_match:
            rec_content = rec_match.group(1).strip()

            # Look for bullet points or list items
            lines = rec_content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('-') or line.startswith('*') or line.startswith('•'):
                    topic = line.lstrip('-*•').strip()
                    if topic:
                        request['topics'].append(topic)
                elif '?' in line:
                    request['specific_questions'].append(line)
                elif line:
                    if not request['context']:
                        request['context'] = line
                    else:
                        request['topics'].append(line)

        # If no structured topics, use entire content as context
        if not request['topics'] and not request['specific_questions']:
            if rec_match:
                request['context'] = rec_match.group(1).strip()

        return request

    def format_recommendations_response(self, recommendations: List[Dict[str, Any]],
                                      request: Dict[str, Any]) -> str:
        """
        Format recommendations response.

        Args:
            recommendations: List of recommendation dictionaries
            request: Original request details

        Returns:
            Formatted response string
        """
        lines = []
        lines.append("💡 **Recommendations**")
        lines.append("")

        if request.get('context'):
            lines.append(f"*Context: {request['context']}*")
            lines.append("")

        for i, rec in enumerate(recommendations, 1):
            title = rec.get('title', f'Recommendation {i}')
            description = rec.get('description', '')
            reasoning = rec.get('reasoning', '')
            priority = rec.get('priority', 'medium')

            priority_icon = {
                'high': '🔴',
                'medium': '🟡',
                'low': '🟢'
            }.get(priority, '🟡')

            lines.append(f"**{i}. {priority_icon} {title}**")
            if description:
                lines.append(f"   {description}")
            if reasoning:
                lines.append(f"   *Reasoning: {reasoning}*")
            lines.append("")

        return "\n".join(lines)

    def generate_recommendations(self, request: Dict[str, Any],
                                context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Generate recommendations based on request.

        Args:
            request: Recommendation request details
            context: Optional context (system state, architecture, etc.)

        Returns:
            List of recommendation dictionaries
        """
        recommendations = []

        # This would integrate with JARVIS intelligence system
        # For now, return structured format

        if request.get('topics'):
            for topic in request['topics']:
                recommendations.append({
                    'title': f"Recommendation for: {topic}",
                    'description': f"Consider the following for {topic}...",
                    'reasoning': "Based on current architecture and best practices",
                    'priority': 'medium'
                })
        elif request.get('context'):
            recommendations.append({
                'title': f"Recommendation: {request['context']}",
                'description': "Consider the following approach...",
                'reasoning': "Based on current system state and architecture",
                'priority': 'medium'
            })

        return recommendations


def handle_rec_recommendations(message: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """
    Convenience function to handle @REC recommendations.

    Args:
        message: User message
        context: Optional context

    Returns:
        Recommendations response if @REC detected, None otherwise
    """
    handler = JARVISRECRecommendationsHandler()

    if handler.detect_rec_tag(message):
        request = handler.extract_recommendation_request(message)
        recommendations = handler.generate_recommendations(request, context)
        return handler.format_recommendations_response(recommendations, request)

    return None


if __name__ == "__main__":
    # Test
    handler = JARVISRECRecommendationsHandler()

    test_messages = [
        "@REC What database should we use?",
        "@REC Based on our architecture, what would you recommend?",
        "@REC I need recommendations for:\n- Database optimization\n- API design",
        "Regular message without @REC"
    ]

    for msg in test_messages:
        print(f"\n{'='*60}")
        print(f"Message: {msg}")
        print(f"{'='*60}")

        if handler.detect_rec_tag(msg):
            request = handler.extract_recommendation_request(msg)
            print(f"Request: {request}")
            recommendations = handler.generate_recommendations(request)
            response = handler.format_recommendations_response(recommendations, request)
            print(f"\nResponse:\n{response}")
        else:
            print("No @REC tag detected")
