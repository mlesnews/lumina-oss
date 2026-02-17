#!/usr/bin/env python3
"""
Hybrid Context & Confidence System

Integrates short@tag context metatagging, chat context management, and AI confidence scoring
into a unified hybrid solution for enhanced AI contextual understanding and confidence assessment.

Features:
- Enhanced short@tag context extraction with semantic analysis
- Intelligent chat context management with conversation history
- AI confidence scoring integrated with tag-based context weights
- Unified hybrid API for context-aware confidence assessment

@lumina @jarvis @r5 #peak
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict, deque

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import confidence scorer if available
try:
    from llm_confidence_scorer import (
        LLMConfidenceScorer,
        ConfidenceScore,
        ConfidenceLevel,
        HallucinationDetection
    )
    CONFIDENCE_SCORER_AVAILABLE = True
except ImportError:
    CONFIDENCE_SCORER_AVAILABLE = False
    LLMConfidenceScorer = None
    ConfidenceScore = None
    ConfidenceLevel = None
    HallucinationDetection = None

logger = get_logger("HybridContextConfidence")


class TagType(Enum):
    """Types of tags in the system"""
    MENTION = "@"  # @tag format
    HASHTAG = "#"  # #tag format


@dataclass
class TagContext:
    """Enhanced context information for a tag"""
    tag: str
    tag_type: TagType
    category: str
    description: str
    context_weight: float  # 0.0-1.0
    ai_weight: float  # 0.0-1.0
    human_weight: float  # 0.0-1.0
    semantic_keywords: List[str] = field(default_factory=list)
    related_tags: List[str] = field(default_factory=list)
    usage_frequency: int = 0
    last_used: Optional[str] = None
    confidence_boost: float = 0.0  # Additional confidence from tag context


@dataclass
class ChatContext:
    """Chat conversation context"""
    conversation_id: str
    messages: List[Dict[str, Any]] = field(default_factory=list)
    extracted_tags: Set[str] = field(default_factory=set)
    context_summary: str = ""
    topic_keywords: List[str] = field(default_factory=list)
    conversation_depth: int = 0
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class HybridContextScore:
    """Unified hybrid context and confidence score"""
    # Context components
    tag_context_score: float  # 0.0-1.0
    chat_context_score: float  # 0.0-1.0
    semantic_coherence: float  # 0.0-1.0

    # Confidence components
    ai_confidence: float  # 0.0-1.0
    tag_confidence_boost: float  # 0.0-1.0
    context_confidence: float  # 0.0-1.0

    # Combined score
    hybrid_confidence: float  # 0.0-1.0
    confidence_level: str  # "high", "medium", "low"

    # Metadata
    tags_detected: List[str] = field(default_factory=list)
    context_keywords: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class HybridContextConfidenceSystem:
    """
    Unified hybrid system integrating:
    - Short@tag context metatagging
    - Chat context management
    - AI confidence scoring
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize the hybrid system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Load tag registry
        self.tag_registry: Dict[str, TagContext] = {}
        self._load_tag_registry()

        # Initialize confidence scorer if available
        if CONFIDENCE_SCORER_AVAILABLE:
            self.confidence_scorer = LLMConfidenceScorer(project_root)
        else:
            self.confidence_scorer = None
            self.logger.warning("Confidence scorer not available - confidence features limited")

        # Chat context management
        self.chat_contexts: Dict[str, ChatContext] = {}
        self.max_context_history = 50  # Maximum messages per conversation

        # Semantic analysis cache
        self.semantic_cache: Dict[str, List[str]] = {}

        self.logger.info("✅ Hybrid Context & Confidence System initialized")

    def _load_tag_registry(self):
        """Load and enhance tag registry from config"""
        registry_path = self.project_root / "config" / "shortag_registry.json"

        if not registry_path.exists():
            self.logger.warning(f"Tag registry not found at {registry_path}")
            return

        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)

            # Process each tag
            for tag_name, tag_data in registry_data.items():
                if tag_name.startswith("_"):  # Skip metadata
                    continue

                # Determine tag type
                if tag_name.startswith("@"):
                    tag_type = TagType.MENTION
                elif tag_name.startswith("#"):
                    tag_type = TagType.HASHTAG
                else:
                    continue

                # Extract semantic keywords from description
                description = tag_data.get("description", "")
                semantic_keywords = self._extract_semantic_keywords(description, tag_name)

                # Create enhanced tag context
                tag_context = TagContext(
                    tag=tag_name,
                    tag_type=tag_type,
                    category=tag_data.get("category", "unknown"),
                    description=description,
                    context_weight=tag_data.get("context_weight", 0.5),
                    ai_weight=tag_data.get("ai_weight", 0.5),
                    human_weight=tag_data.get("human_weight", 0.5),
                    semantic_keywords=semantic_keywords,
                    related_tags=self._find_related_tags(tag_name, registry_data),
                    confidence_boost=self._calculate_tag_confidence_boost(tag_data)
                )

                self.tag_registry[tag_name] = tag_context

            self.logger.info(f"✅ Loaded {len(self.tag_registry)} tags from registry")

        except Exception as e:
            self.logger.error(f"Failed to load tag registry: {e}")

    def _extract_semantic_keywords(self, text: str, tag: str) -> List[str]:
        """Extract semantic keywords from text"""
        # Remove common stop words and extract meaningful terms
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}

        # Extract words (3+ characters)
        words = re.findall(r'\b\w{3,}\b', text.lower())

        # Filter stop words and get unique keywords
        keywords = [w for w in words if w not in stop_words]

        # Add tag name (without @ or #)
        tag_clean = tag.lstrip("@#").lower()
        if tag_clean not in keywords:
            keywords.insert(0, tag_clean)

        return list(set(keywords))[:10]  # Limit to top 10

    def _find_related_tags(self, tag: str, registry_data: Dict) -> List[str]:
        """Find related tags based on category and semantic similarity"""
        related = []
        current_category = registry_data.get(tag, {}).get("category", "")
        current_desc = registry_data.get(tag, {}).get("description", "").lower()

        # Find tags in same category
        for other_tag, other_data in registry_data.items():
            if other_tag == tag or other_tag.startswith("_"):
                continue

            other_category = other_data.get("category", "")
            other_desc = other_data.get("description", "").lower()

            # Same category = related
            if other_category == current_category:
                related.append(other_tag)

            # Semantic similarity (simple word overlap)
            current_words = set(re.findall(r'\b\w{4,}\b', current_desc))
            other_words = set(re.findall(r'\b\w{4,}\b', other_desc))
            overlap = len(current_words.intersection(other_words))

            if overlap >= 2:  # At least 2 common words
                related.append(other_tag)

        return list(set(related))[:5]  # Limit to top 5

    def _calculate_tag_confidence_boost(self, tag_data: Dict) -> float:
        """Calculate confidence boost from tag metadata"""
        # Higher context_weight and ai_weight = higher confidence boost
        context_weight = tag_data.get("context_weight", 0.5)
        ai_weight = tag_data.get("ai_weight", 0.5)

        # Combined boost (weighted average)
        boost = (context_weight * 0.6 + ai_weight * 0.4)

        # Scale to 0.0-0.2 range (max 20% boost)
        return boost * 0.2

    def extract_tags_from_text(self, text: str) -> Dict[str, List[str]]:
        """
        Extract all tags from text with enhanced detection

        Returns:
            Dict with 'mentions' and 'hashtags' lists
        """
        mentions = re.findall(r'@\w+', text)
        hashtags = re.findall(r'#\w+', text)

        # Normalize (remove duplicates, preserve order)
        mentions = list(dict.fromkeys(mentions))
        hashtags = list(dict.fromkeys(hashtags))

        return {
            "mentions": mentions,
            "hashtags": hashtags,
            "all": mentions + hashtags
        }

    def analyze_tag_context(self, tags: List[str]) -> Dict[str, Any]:
        """
        Analyze context from detected tags

        Returns:
            Dict with context analysis including weights, keywords, and confidence boost
        """
        if not tags:
            return {
                "total_context_weight": 0.0,
                "total_ai_weight": 0.0,
                "total_human_weight": 0.0,
                "confidence_boost": 0.0,
                "semantic_keywords": [],
                "related_tags": [],
                "tag_details": {}
            }

        # Aggregate context from all tags
        total_context_weight = 0.0
        total_ai_weight = 0.0
        total_human_weight = 0.0
        total_confidence_boost = 0.0
        all_keywords = []
        all_related = []
        tag_details = {}

        for tag in tags:
            if tag in self.tag_registry:
                tag_ctx = self.tag_registry[tag]

                # Update usage
                tag_ctx.usage_frequency += 1
                tag_ctx.last_used = datetime.now().isoformat()

                # Aggregate weights
                total_context_weight += tag_ctx.context_weight
                total_ai_weight += tag_ctx.ai_weight
                total_human_weight += tag_ctx.human_weight
                total_confidence_boost += tag_ctx.confidence_boost

                # Aggregate keywords
                all_keywords.extend(tag_ctx.semantic_keywords)
                all_related.extend(tag_ctx.related_tags)

                # Store details
                tag_details[tag] = {
                    "category": tag_ctx.category,
                    "context_weight": tag_ctx.context_weight,
                    "ai_weight": tag_ctx.ai_weight,
                    "confidence_boost": tag_ctx.confidence_boost
                }

        # Normalize weights (average)
        tag_count = len([t for t in tags if t in self.tag_registry])
        if tag_count > 0:
            total_context_weight /= tag_count
            total_ai_weight /= tag_count
            total_human_weight /= tag_count
            total_confidence_boost = min(0.2, total_confidence_boost)  # Cap at 20%

        # Remove duplicate keywords
        all_keywords = list(set(all_keywords))
        all_related = list(set(all_related))

        return {
            "total_context_weight": total_context_weight,
            "total_ai_weight": total_ai_weight,
            "total_human_weight": total_human_weight,
            "confidence_boost": total_confidence_boost,
            "semantic_keywords": all_keywords,
            "related_tags": all_related,
            "tag_details": tag_details
        }

    def manage_chat_context(self, conversation_id: str, message: Dict[str, Any],
                           max_history: Optional[int] = None) -> ChatContext:
        """
        Manage chat context for a conversation

        Args:
            conversation_id: Unique conversation identifier
            message: Message dict with 'role' and 'content'
            max_history: Maximum messages to keep (default: self.max_context_history)

        Returns:
            Updated ChatContext
        """
        if max_history is None:
            max_history = self.max_context_history

        # Get or create context
        if conversation_id not in self.chat_contexts:
            self.chat_contexts[conversation_id] = ChatContext(conversation_id=conversation_id)

        context = self.chat_contexts[conversation_id]

        # Add message
        context.messages.append({
            "role": message.get("role", "user"),
            "content": message.get("content", ""),
            "timestamp": datetime.now().isoformat()
        })

        # Limit history
        if len(context.messages) > max_history:
            context.messages = context.messages[-max_history:]

        # Extract tags from message
        content = message.get("content", "")
        extracted_tags = self.extract_tags_from_text(content)
        context.extracted_tags.update(extracted_tags["all"])

        # Update conversation depth
        context.conversation_depth = len(context.messages)

        # Generate context summary (simplified - could use LLM)
        context.context_summary = self._generate_context_summary(context)

        # Extract topic keywords
        context.topic_keywords = self._extract_topic_keywords(context.messages)

        return context

    def _generate_context_summary(self, context: ChatContext) -> str:
        """Generate a summary of conversation context"""
        if not context.messages:
            return ""

        # Simple summary: extract key topics from recent messages
        recent_messages = context.messages[-5:]  # Last 5 messages
        topics = []

        for msg in recent_messages:
            content = msg.get("content", "")
            # Extract capitalized words and important terms
            important_terms = re.findall(r'\b[A-Z][a-z]+\b|\b\w{6,}\b', content)
            topics.extend(important_terms[:3])  # Top 3 per message

        # Get unique topics
        unique_topics = list(set(topics))[:10]

        return f"Topics: {', '.join(unique_topics)}"

    def _extract_topic_keywords(self, messages: List[Dict[str, Any]]) -> List[str]:
        """Extract topic keywords from conversation"""
        all_text = " ".join([msg.get("content", "") for msg in messages])

        # Extract meaningful words (4+ characters, not common words)
        words = re.findall(r'\b\w{4,}\b', all_text.lower())

        # Count frequency
        word_freq = defaultdict(int)
        for word in words:
            word_freq[word] += 1

        # Get top keywords by frequency
        top_keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:15]

        return [word for word, freq in top_keywords]

    def calculate_chat_context_score(self, conversation_id: str, current_text: str) -> float:
        """
        Calculate context score based on conversation history

        Returns:
            Context score 0.0-1.0
        """
        if conversation_id not in self.chat_contexts:
            return 0.5  # Neutral if no context

        context = self.chat_contexts[conversation_id]

        if not context.messages:
            return 0.5

        # Calculate score based on:
        # 1. Conversation depth (more messages = more context)
        depth_score = min(1.0, context.conversation_depth / 10.0)

        # 2. Topic relevance (how well current text matches conversation topics)
        current_words = set(re.findall(r'\b\w{4,}\b', current_text.lower()))
        topic_words = set(context.topic_keywords)
        relevance_score = len(current_words.intersection(topic_words)) / max(1, len(topic_words))

        # 3. Tag consistency (tags in current text match conversation tags)
        current_tags = set(self.extract_tags_from_text(current_text)["all"])
        conversation_tags = context.extracted_tags
        tag_score = len(current_tags.intersection(conversation_tags)) / max(1, len(conversation_tags))

        # Combined score (weighted)
        context_score = (
            depth_score * 0.3 +
            relevance_score * 0.4 +
            tag_score * 0.3
        )

        return min(1.0, context_score)

    def calculate_semantic_coherence(self, text: str, context_text: Optional[str] = None) -> float:
        """Calculate semantic coherence score"""
        if context_text is None:
            return 0.5  # Neutral if no context

        # Extract meaningful words from both texts
        text_words = set(re.findall(r'\b\w{4,}\b', text.lower()))
        context_words = set(re.findall(r'\b\w{4,}\b', context_text.lower()))

        if not context_words:
            return 0.5

        # Calculate overlap
        overlap = len(text_words.intersection(context_words))
        coherence = overlap / max(1, len(context_words))

        return min(1.0, coherence)

    def calculate_hybrid_confidence(self, prompt: str, response: str,
                                   conversation_id: Optional[str] = None,
                                   context: Optional[str] = None) -> HybridContextScore:
        """
        Calculate unified hybrid confidence score combining:
        - Tag context analysis
        - Chat context management
        - AI confidence scoring

        Returns:
            HybridContextScore with all components
        """
        # Extract tags from prompt and response
        prompt_tags = self.extract_tags_from_text(prompt)
        response_tags = self.extract_tags_from_text(response)
        all_tags = list(set(prompt_tags["all"] + response_tags["all"]))

        # Analyze tag context
        tag_analysis = self.analyze_tag_context(all_tags)
        tag_context_score = tag_analysis["total_context_weight"]
        tag_confidence_boost = tag_analysis["confidence_boost"]

        # Calculate chat context score
        if conversation_id:
            chat_context_score = self.calculate_chat_context_score(conversation_id, response)
        else:
            chat_context_score = 0.5  # Neutral if no conversation

        # Calculate semantic coherence
        context_text = context or (self.chat_contexts[conversation_id].context_summary if conversation_id else None)
        semantic_coherence = self.calculate_semantic_coherence(response, context_text)

        # Get AI confidence score (if scorer available)
        if self.confidence_scorer:
            ai_confidence_result = self.confidence_scorer.analyze_llm_output(
                prompt, response, context=context
            )
            ai_confidence = ai_confidence_result.overall_confidence
            confidence_level_str = ai_confidence_result.confidence_level.value
            recommendations = ai_confidence_result.recommendations
        else:
            # Fallback: simple confidence calculation
            ai_confidence = 0.7  # Default moderate confidence
            confidence_level_str = "medium"
            recommendations = []

        # Calculate context confidence (combination of tag and chat context)
        context_confidence = (
            tag_context_score * 0.4 +
            chat_context_score * 0.3 +
            semantic_coherence * 0.3
        )

        # Calculate hybrid confidence (combines AI confidence with context)
        hybrid_confidence = (
            ai_confidence * 0.5 +  # Base AI confidence
            context_confidence * 0.3 +  # Context quality
            tag_confidence_boost * 0.2  # Tag-based boost
        )

        # Determine confidence level
        if hybrid_confidence >= 0.8:
            confidence_level = "high"
        elif hybrid_confidence >= 0.5:
            confidence_level = "medium"
        else:
            confidence_level = "low"

        # Generate recommendations
        all_recommendations = list(recommendations)
        if hybrid_confidence < 0.5:
            all_recommendations.append("⚠️ Low hybrid confidence - consider adding more context tags")
        if tag_context_score < 0.5:
            all_recommendations.append("💡 Consider using relevant @tags or #hashtags for better context")
        if chat_context_score < 0.5 and conversation_id:
            all_recommendations.append("💡 Build conversation context with more relevant messages")

        return HybridContextScore(
            tag_context_score=tag_context_score,
            chat_context_score=chat_context_score,
            semantic_coherence=semantic_coherence,
            ai_confidence=ai_confidence,
            tag_confidence_boost=tag_confidence_boost,
            context_confidence=context_confidence,
            hybrid_confidence=hybrid_confidence,
            confidence_level=confidence_level,
            tags_detected=all_tags,
            context_keywords=tag_analysis["semantic_keywords"],
            recommendations=all_recommendations
        )

    def get_conversation_context(self, conversation_id: str) -> Optional[ChatContext]:
        """Get chat context for a conversation"""
        return self.chat_contexts.get(conversation_id)

    def clear_conversation_context(self, conversation_id: str):
        """Clear chat context for a conversation"""
        if conversation_id in self.chat_contexts:
            del self.chat_contexts[conversation_id]
            self.logger.info(f"Cleared context for conversation: {conversation_id}")

    def get_tag_statistics(self) -> Dict[str, Any]:
        """Get statistics about tag usage"""
        stats = {
            "total_tags": len(self.tag_registry),
            "tag_usage": {},
            "most_used_tags": [],
            "categories": defaultdict(int)
        }

        for tag, tag_ctx in self.tag_registry.items():
            stats["tag_usage"][tag] = {
                "frequency": tag_ctx.usage_frequency,
                "last_used": tag_ctx.last_used,
                "category": tag_ctx.category
            }
            stats["categories"][tag_ctx.category] += 1

        # Sort by usage frequency
        stats["most_used_tags"] = sorted(
            stats["tag_usage"].items(),
            key=lambda x: x[1]["frequency"],
            reverse=True
        )[:10]

        return stats


# Convenience functions
def create_hybrid_system(project_root: Optional[Path] = None) -> HybridContextConfidenceSystem:
    """Create and initialize hybrid system"""
    return HybridContextConfidenceSystem(project_root)


def calculate_hybrid_confidence(prompt: str, response: str, **kwargs) -> HybridContextScore:
    """Convenience function to calculate hybrid confidence"""
    system = HybridContextConfidenceSystem()
    return system.calculate_hybrid_confidence(prompt, response, **kwargs)


# Example usage
if __name__ == "__main__":
    print("🔗 Hybrid Context & Confidence System")
    print("=" * 60)

    # Initialize system
    system = create_hybrid_system()

    # Example conversation
    conversation_id = "test_conv_001"

    # Simulate conversation
    system.manage_chat_context(conversation_id, {
        "role": "user",
        "content": "I need help with @jarvis workflow automation using @v3 verification"
    })

    system.manage_chat_context(conversation_id, {
        "role": "assistant",
        "content": "I can help with @jarvis workflow automation. @v3 verification ensures quality."
    })

    # Test hybrid confidence calculation
    prompt = "Create a workflow using @jarvis with @v3 verification"
    response = "I've created a workflow using @jarvis automation system. @v3 verification has been integrated to ensure quality."

    score = system.calculate_hybrid_confidence(prompt, response, conversation_id=conversation_id)

    print(f"\n📊 Hybrid Confidence Analysis:")
    print(f"   Hybrid Confidence: {score.hybrid_confidence:.2f} ({score.confidence_level})")
    print(f"   Tag Context Score: {score.tag_context_score:.2f}")
    print(f"   Chat Context Score: {score.chat_context_score:.2f}")
    print(f"   Semantic Coherence: {score.semantic_coherence:.2f}")
    print(f"   AI Confidence: {score.ai_confidence:.2f}")
    print(f"   Tag Confidence Boost: {score.tag_confidence_boost:.2f}")
    print(f"   Context Confidence: {score.context_confidence:.2f}")

    print(f"\n🏷️  Tags Detected: {', '.join(score.tags_detected)}")
    print(f"🔑 Context Keywords: {', '.join(score.context_keywords[:10])}")

    if score.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in score.recommendations[:3]:
            print(f"   • {rec}")

    # Show tag statistics
    stats = system.get_tag_statistics()
    print(f"\n📈 Tag Statistics:")
    print(f"   Total Tags: {stats['total_tags']}")
    print(f"   Categories: {dict(stats['categories'])}")

    print("\n✅ Hybrid system ready for integration!")

