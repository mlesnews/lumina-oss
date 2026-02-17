#!/usr/bin/env python3
"""
JARVIS Integration Test

Tests that all new systems are properly integrated and working together.

Tags: #JARVIS #INTEGRATION #TEST @JARVIS @LUMINA
"""

import sys
from pathlib import Path

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

logger = get_logger("JARVISIntegrationTest")


def test_all_systems():
    """Test all JARVIS systems are integrated"""
    logger.info("=" * 80)
    logger.info("🧪 JARVIS INTEGRATION TEST")
    logger.info("=" * 80)
    logger.info("")

    results = {
        "learning_pipeline": False,
        "interaction_recorder": False,
        "feedback_system": False,
        "context_analyzer": False,
        "intent_classifier": False,
        "action_predictor": False,
        "self_awareness": False,
    }

    # Test Learning Pipeline
    try:
        from jarvis_learning_pipeline import get_jarvis_learning_pipeline, LearningDataType
        pipeline = get_jarvis_learning_pipeline(project_root)
        pipeline.collect_learning_data(
            LearningDataType.INTERACTION,
            source="test",
            context={"test": True},
            data={"test": "integration_test"}
        )
        results["learning_pipeline"] = True
        logger.info("✅ Learning Pipeline: Working")
    except Exception as e:
        logger.error(f"❌ Learning Pipeline: Failed - {e}")

    # Test Interaction Recorder
    try:
        from jarvis_interaction_recorder import get_jarvis_interaction_recorder, InteractionType
        recorder = get_jarvis_interaction_recorder(project_root)
        recorder.record_interaction(
            InteractionType.TEXT_COMMAND,
            content="test command",
            context={"test": True},
            outcome={"success": True}
        )
        results["interaction_recorder"] = True
        logger.info("✅ Interaction Recorder: Working")
    except Exception as e:
        logger.error(f"❌ Interaction Recorder: Failed - {e}")

    # Test Feedback System
    try:
        from jarvis_feedback_system import get_jarvis_feedback_system, FeedbackType
        feedback = get_jarvis_feedback_system(project_root)
        feedback.record_feedback(
            FeedbackType.EXPLICIT_POSITIVE,
            target_action="test_action",
            feedback_value=0.8
        )
        results["feedback_system"] = True
        logger.info("✅ Feedback System: Working")
    except Exception as e:
        logger.error(f"❌ Feedback System: Failed - {e}")

    # Test Context Analyzer
    try:
        from jarvis_context_analyzer import get_jarvis_context_analyzer, ContextSource
        analyzer = get_jarvis_context_analyzer(project_root)
        analyzer.add_context_data(ContextSource.SYSTEM, {"test": True})
        context = analyzer.get_current_context()
        results["context_analyzer"] = True
        logger.info("✅ Context Analyzer: Working")
    except Exception as e:
        logger.error(f"❌ Context Analyzer: Failed - {e}")

    # Test Intent Classifier
    try:
        from jarvis_intent_classifier import get_jarvis_intent_classifier
        classifier = get_jarvis_intent_classifier(project_root)
        intent = classifier.classify_intent("test command")
        results["intent_classifier"] = True
        logger.info("✅ Intent Classifier: Working")
    except Exception as e:
        logger.error(f"❌ Intent Classifier: Failed - {e}")

    # Test Action Predictor
    try:
        from jarvis_action_predictor import get_jarvis_action_predictor
        predictor = get_jarvis_action_predictor(project_root)
        prediction = predictor.predict_next_action({"test": True})
        results["action_predictor"] = True
        logger.info("✅ Action Predictor: Working")
    except Exception as e:
        logger.error(f"❌ Action Predictor: Failed - {e}")

    # Test Self-Awareness
    try:
        from jarvis_self_awareness_system import get_jarvis_self_awareness
        awareness = get_jarvis_self_awareness(project_root)
        state = awareness.get_self_state()
        results["self_awareness"] = True
        logger.info("✅ Self-Awareness: Working")
    except Exception as e:
        logger.error(f"❌ Self-Awareness: Failed - {e}")

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("📊 INTEGRATION TEST RESULTS")
    logger.info("=" * 80)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for system, status in results.items():
        status_icon = "✅" if status else "❌"
        logger.info(f"{status_icon} {system.replace('_', ' ').title()}")

    logger.info("")
    logger.info(f"Total: {passed}/{total} systems working")

    if passed == total:
        logger.info("🎉 ALL SYSTEMS INTEGRATED AND WORKING!")
    else:
        logger.warning(f"⚠️  {total - passed} systems need attention")

    logger.info("=" * 80)
    logger.info("")

    return passed == total


if __name__ == "__main__":
    success = test_all_systems()
    sys.exit(0 if success else 1)
