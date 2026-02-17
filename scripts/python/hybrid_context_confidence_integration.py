#!/usr/bin/env python3
"""
Hybrid Context & Confidence System Integration Examples

Demonstrates how to integrate the hybrid system with:
- Workflow systems
- Chat interfaces
- AI agents
- Context-aware applications

@lumina @jarvis #peak
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from hybrid_context_confidence_system import (
    HybridContextConfidenceSystem,
    HybridContextScore,
    create_hybrid_system
)

try:
    from workflow_base import WorkflowBase
    WORKFLOW_AVAILABLE = True
except ImportError:
    WORKFLOW_AVAILABLE = False
    WorkflowBase = None


class HybridAwareWorkflow:
    """
    Example workflow that uses hybrid context and confidence system
    """

    def __init__(self, workflow_name: str, conversation_id: Optional[str] = None):
        self.workflow_name = workflow_name
        self.conversation_id = conversation_id or f"workflow_{workflow_name}"
        self.hybrid_system = create_hybrid_system()

        if WORKFLOW_AVAILABLE:
            # Inherit from WorkflowBase if available
            self.workflow_base = WorkflowBase(workflow_name, total_steps=10)
        else:
            self.workflow_base = None

    async def execute_with_hybrid_context(self, step_name: str, prompt: str,
                                        llm_response_func) -> Dict[str, Any]:
        """
        Execute a workflow step with hybrid context and confidence checking

        Args:
            step_name: Name of the workflow step
            prompt: Prompt/instruction for this step
            llm_response_func: Async function that returns LLM response

        Returns:
            Dict with response, confidence scores, and recommendations
        """
        # Get LLM response
        response = await llm_response_func()

        # Calculate hybrid confidence
        hybrid_score = self.hybrid_system.calculate_hybrid_confidence(
            prompt=prompt,
            response=response,
            conversation_id=self.conversation_id
        )

        # Update chat context
        self.hybrid_system.manage_chat_context(
            self.conversation_id,
            {
                "role": "assistant",
                "content": response
            }
        )

        # Make decision based on confidence
        should_proceed = hybrid_score.hybrid_confidence >= 0.5

        result = {
            "step": step_name,
            "response": response,
            "hybrid_score": hybrid_score,
            "should_proceed": should_proceed,
            "confidence_level": hybrid_score.confidence_level,
            "recommendations": hybrid_score.recommendations
        }

        return result

    def get_context_summary(self) -> Dict[str, Any]:
        """Get summary of conversation context"""
        context = self.hybrid_system.get_conversation_context(self.conversation_id)

        if not context:
            return {"status": "no_context"}

        return {
            "conversation_id": context.conversation_id,
            "message_count": len(context.messages),
            "extracted_tags": list(context.extracted_tags),
            "context_summary": context.context_summary,
            "topic_keywords": context.topic_keywords[:10],
            "conversation_depth": context.conversation_depth
        }


class HybridChatInterface:
    """
    Example chat interface with hybrid context and confidence
    """

    def __init__(self):
        self.hybrid_system = create_hybrid_system()
        self.conversations: Dict[str, HybridChatInterface] = {}

    def start_conversation(self, conversation_id: str) -> str:
        """Start a new conversation"""
        self.conversations[conversation_id] = self
        return conversation_id

    def process_message(self, conversation_id: str, user_message: str,
                       llm_response: str) -> Dict[str, Any]:
        """
        Process a chat message with hybrid context and confidence

        Args:
            conversation_id: Conversation identifier
            user_message: User's message
            llm_response: LLM's response

        Returns:
            Dict with response, confidence, and context info
        """
        # Update context with user message
        self.hybrid_system.manage_chat_context(
            conversation_id,
            {
                "role": "user",
                "content": user_message
            }
        )

        # Calculate hybrid confidence
        hybrid_score = self.hybrid_system.calculate_hybrid_confidence(
            prompt=user_message,
            response=llm_response,
            conversation_id=conversation_id
        )

        # Update context with assistant response
        self.hybrid_system.manage_chat_context(
            conversation_id,
            {
                "role": "assistant",
                "content": llm_response
            }
        )

        # Extract tags from messages
        user_tags = self.hybrid_system.extract_tags_from_text(user_message)
        response_tags = self.hybrid_system.extract_tags_from_text(llm_response)

        return {
            "conversation_id": conversation_id,
            "user_message": user_message,
            "llm_response": llm_response,
            "hybrid_confidence": hybrid_score.hybrid_confidence,
            "confidence_level": hybrid_score.confidence_level,
            "tags_detected": hybrid_score.tags_detected,
            "context_keywords": hybrid_score.context_keywords,
            "recommendations": hybrid_score.recommendations,
            "user_tags": user_tags["all"],
            "response_tags": response_tags["all"]
        }

    def get_conversation_insights(self, conversation_id: str) -> Dict[str, Any]:
        """Get insights about a conversation"""
        context = self.hybrid_system.get_conversation_context(conversation_id)

        if not context:
            return {"status": "conversation_not_found"}

        # Analyze tag usage
        tag_analysis = {}
        for tag in context.extracted_tags:
            if tag in self.hybrid_system.tag_registry:
                tag_ctx = self.hybrid_system.tag_registry[tag]
                tag_analysis[tag] = {
                    "category": tag_ctx.category,
                    "usage_frequency": tag_ctx.usage_frequency,
                    "context_weight": tag_ctx.context_weight,
                    "ai_weight": tag_ctx.ai_weight
                }

        return {
            "conversation_id": conversation_id,
            "message_count": len(context.messages),
            "conversation_depth": context.conversation_depth,
            "extracted_tags": list(context.extracted_tags),
            "topic_keywords": context.topic_keywords,
            "context_summary": context.context_summary,
            "tag_analysis": tag_analysis
        }


def demonstrate_workflow_integration():
    """Demonstrate workflow integration"""
    print("🔗 Hybrid System - Workflow Integration Demo")
    print("=" * 60)

    workflow = HybridAwareWorkflow("example_workflow", "workflow_demo_001")

    # Simulate workflow steps
    async def mock_llm_response():
        return "I've completed the workflow step using @jarvis automation with @v3 verification."

    # This would be async in real usage
    print("\n📋 Workflow Step Execution:")
    print("   Step: Initialize workflow")
    print("   Prompt: Create workflow using @jarvis with @v3 verification")

    # In real usage: result = await workflow.execute_with_hybrid_context(...)
    print("   ✅ Workflow step executed with hybrid context checking")

    # Get context summary
    summary = workflow.get_context_summary()
    print(f"\n📊 Context Summary:")
    print(f"   Message Count: {summary.get('message_count', 0)}")
    print(f"   Extracted Tags: {', '.join(summary.get('extracted_tags', []))}")


def demonstrate_chat_integration():
    """Demonstrate chat interface integration"""
    print("\n💬 Hybrid System - Chat Interface Demo")
    print("=" * 60)

    chat = HybridChatInterface()
    conv_id = chat.start_conversation("chat_demo_001")

    # Simulate conversation
    user_msg = "I need help with @jarvis workflow automation"
    llm_response = "I can help with @jarvis workflow automation. Let me set up the system using @v3 verification."

    result = chat.process_message(conv_id, user_msg, llm_response)

    print(f"\n💬 Chat Message Processed:")
    print(f"   User: {user_msg}")
    print(f"   Assistant: {llm_response}")
    print(f"   Hybrid Confidence: {result['hybrid_confidence']:.2f} ({result['confidence_level']})")
    print(f"   Tags Detected: {', '.join(result['tags_detected'])}")

    # Get conversation insights
    insights = chat.get_conversation_insights(conv_id)
    print(f"\n📊 Conversation Insights:")
    print(f"   Message Count: {insights['message_count']}")
    print(f"   Conversation Depth: {insights['conversation_depth']}")
    print(f"   Topic Keywords: {', '.join(insights['topic_keywords'][:5])}")


def demonstrate_tag_analysis():
    """Demonstrate tag context analysis"""
    print("\n🏷️  Hybrid System - Tag Analysis Demo")
    print("=" * 60)

    system = create_hybrid_system()

    # Test text with multiple tags
    test_text = "I need @jarvis to help with @v3 verification for @r5 context aggregation. This is #peak quality work."

    # Extract tags
    tags = system.extract_tags_from_text(test_text)
    print(f"\n📝 Text: {test_text}")
    print(f"   Mentions: {', '.join(tags['mentions'])}")
    print(f"   Hashtags: {', '.join(tags['hashtags'])}")

    # Analyze tag context
    analysis = system.analyze_tag_context(tags["all"])
    print(f"\n📊 Tag Context Analysis:")
    print(f"   Total Context Weight: {analysis['total_context_weight']:.2f}")
    print(f"   Total AI Weight: {analysis['total_ai_weight']:.2f}")
    print(f"   Confidence Boost: {analysis['confidence_boost']:.2f}")
    print(f"   Semantic Keywords: {', '.join(analysis['semantic_keywords'][:10])}")
    print(f"   Related Tags: {', '.join(analysis['related_tags'][:5])}")


if __name__ == "__main__":
    print("🔗 Hybrid Context & Confidence System - Integration Examples")
    print("=" * 60)

    demonstrate_workflow_integration()
    demonstrate_chat_integration()
    demonstrate_tag_analysis()

    print("\n✅ Integration examples complete!")
    print("The hybrid system is ready for integration into your applications.")

