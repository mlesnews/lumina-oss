#!/usr/bin/env python3
"""
Voice Systems Testing Framework

Comprehensive testing for all voice system components:
- Voice Transcript Queue
- Voice Filter System
- Auto-Send Monitor
- Auto-Accept "Keep All" Button
- Full-Time Monitoring Service

Tags: #TESTING #VOICE_SYSTEMS #QUALITY_ASSURANCE #LUMINA_CORE
"""

import sys
import time
import unittest
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from unittest.mock import Mock, MagicMock, patch

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    def get_logger(name):
        return logging.getLogger(name)

logger = get_logger("VoiceSystemsTest")


class VoiceTranscriptQueueTest(unittest.TestCase):
    """Test Voice Transcript Queue System"""

    def setUp(self):
        """Set up test fixtures"""
        from voice_transcript_queue import VoiceTranscriptQueue
        self.queue = VoiceTranscriptQueue()

    def test_queue_initialization(self):
        """Test queue initializes correctly"""
        self.assertIsNotNone(self.queue)
        self.assertFalse(self.queue.processing)  # Not started yet

    def test_queue_request(self):
        """Test queuing a request"""
        request_id = self.queue.queue_request("Test request")
        self.assertIsNotNone(request_id)
        self.assertEqual(self.queue.stats["total_queued"], 1)

    def test_queue_voice_transcript(self):
        """Test queuing voice transcript"""
        request_id = self.queue.queue_voice_transcript("Test transcript")
        self.assertIsNotNone(request_id)
        self.assertEqual(self.queue.stats["voice_transcripts"], 1)

    def test_queue_processing(self):
        """Test queue processing starts"""
        self.queue.start_processing()
        self.assertTrue(self.queue.processing)
        time.sleep(0.5)  # Let it start
        self.queue.stop_processing()

    def test_queue_health_check(self):
        """Test queue health check and auto-restart"""
        stats = self.queue.get_stats()
        self.assertIn("processing", stats)
        # Health check should ensure processing is active
        if not stats["processing"]:
            self.queue.start_processing()
            stats = self.queue.get_stats()
            self.assertTrue(stats["processing"])


class VoiceFilterSystemTest(unittest.TestCase):
    """Test Voice Filter System"""

    def setUp(self):
        """Set up test fixtures"""
        from voice_filter_system import VoiceFilterSystem
        self.filter = VoiceFilterSystem(user_id="test_user")

    def test_filter_initialization(self):
        """Test filter initializes correctly"""
        self.assertIsNotNone(self.filter)
        self.assertTrue(self.filter.enabled or self.filter.profile_library is None)

    def test_tv_audio_detection(self):
        """Test TV audio detection (bleed-through prevention)"""
        # Test with TV-like audio features
        tv_features = {
            "mean_amplitude": 0.4,
            "std_amplitude": 0.1,  # Very consistent (TV-like)
            "duration": 6.0  # Long duration
        }

        # Test TV detection
        is_tv = self.filter._detect_tv_audio(tv_features, "reading from the holy gospel")
        self.assertTrue(is_tv, "Should detect TV audio with gospel text")

        # Test with TV keywords
        is_tv2 = self.filter._detect_tv_audio(tv_features, "tv show episode")
        self.assertTrue(is_tv2, "Should detect TV audio with TV keywords")

        # Test with consistent volume pattern
        tv_features2 = {"std_amplitude": 0.15}  # Consistent volume
        is_tv3 = self.filter._detect_tv_audio(tv_features2, None)
        self.assertTrue(is_tv3, "Should detect TV audio via volume pattern")

    def test_tv_audio_filtering(self):
        """Test TV audio is filtered immediately"""
        # Mock audio data
        mock_audio = Mock()
        tv_features = {
            "mean_amplitude": 0.4,
            "std_amplitude": 0.1,
            "duration": 6.0
        }

        # Should filter TV audio immediately
        result = self.filter.should_filter(
            mock_audio,
            audio_features=tv_features,
            transcription_text="reading from the holy gospel according to matthew"
        )

        # TV should be filtered
        self.assertTrue(result.should_filter, "TV audio should be filtered")
        self.assertIn("tv", result.reason.lower(), "Reason should mention TV")

    def test_tertiary_audio_learning(self):
        """Test tertiary audio (TV/wife) learning"""
        if not self.filter.profile_library:
            self.skipTest("Profile library not available")

        tv_features = {
            "mean_amplitude": 0.4,
            "std_amplitude": 0.1
        }

        # Learn TV audio
        self.filter._learn_tertiary_audio(
            tv_features,
            "test_tv_learning",
            "tv_audio",
            "tv"
        )

        # Check if TV profile was created/updated
        if "tv_audio" in self.filter.profile_library.voice_profiles:
            profile = self.filter.profile_library.voice_profiles["tv_audio"]
            self.assertGreater(profile.sample_count, 0, "TV profile should have samples")


class AutoSendMonitorTest(unittest.TestCase):
    """Test Auto-Send Monitor"""

    def setUp(self):
        """Set up test fixtures"""
        from cursor_auto_send_monitor import CursorAutoSendMonitor
        self.monitor = CursorAutoSendMonitor(enabled=True)

    def test_monitor_initialization(self):
        """Test monitor initializes correctly"""
        self.assertIsNotNone(self.monitor)
        self.assertTrue(self.monitor.enabled)

    def test_activity_tracking(self):
        """Test activity marking"""
        self.monitor.mark_activity()
        self.assertTrue(self.monitor.has_pending_message)
        self.assertIsNotNone(self.monitor.last_activity_time)

    def test_speech_end_tracking(self):
        """Test speech end marking"""
        self.monitor.mark_speech_end()
        self.assertIsNotNone(self.monitor.last_speech_end_time)

    def test_health_check(self):
        """Test monitor health check"""
        stats = self.monitor.get_stats()
        self.assertIn("running", stats)
        self.assertIn("enabled", stats)


class AutoAcceptTest(unittest.TestCase):
    """Test Auto-Accept 'Keep All' Button"""

    def setUp(self):
        """Set up test fixtures"""
        from cursor_ide_auto_accept import CursorIDEAutoAccept
        self.auto_accept = CursorIDEAutoAccept()

    def test_auto_accept_initialization(self):
        """Test auto-accept initializes correctly"""
        self.assertIsNotNone(self.auto_accept)
        self.assertEqual(self.auto_accept.acceptance_cooldown, 3.0)
        self.assertEqual(self.auto_accept.max_acceptances_per_minute, 10)

    def test_should_accept_cooldown(self):
        """Test cooldown prevents infinite loops"""
        from datetime import datetime
        self.auto_accept.last_acceptance_time = datetime.now()

        # Should not accept immediately (cooldown active)
        should_accept = self.auto_accept._should_accept()
        self.assertFalse(should_accept, "Should respect cooldown period")

    def test_acceptance_rate_limiting(self):
        """Test rate limiting prevents excessive acceptances"""
        self.auto_accept.acceptance_count = 10  # At limit
        should_accept = self.auto_accept._should_accept()
        self.assertFalse(should_accept, "Should respect rate limit")

    def test_cursor_running_detection(self):
        """Test Cursor IDE running detection"""
        is_running = self.auto_accept._is_cursor_running()
        # Should return True or False (not raise exception)
        self.assertIsInstance(is_running, bool)

    def test_acceptance_recording(self):
        """Test acceptance is recorded properly"""
        initial_count = self.auto_accept.acceptance_count
        self.auto_accept._record_acceptance()
        self.assertEqual(self.auto_accept.acceptance_count, initial_count + 1)
        self.assertIsNotNone(self.auto_accept.last_acceptance_time)


class FullTimeMonitoringTest(unittest.TestCase):
    """Test Full-Time Monitoring Service"""

    def setUp(self):
        """Set up test fixtures"""
        from full_time_monitoring_service import FullTimeMonitoringService
        self.monitoring = FullTimeMonitoringService(check_interval=1.0)

    def test_monitoring_initialization(self):
        """Test monitoring service initializes correctly"""
        self.assertIsNotNone(self.monitoring)
        self.assertFalse(self.monitoring.running)

    def test_system_health_checks(self):
        """Test all systems are checked"""
        # Start monitoring briefly
        self.monitoring.start()
        time.sleep(2.0)  # Let it check systems

        stats = self.monitoring.get_stats()
        self.assertIn("systems", stats)
        self.assertIn("queue", stats["systems"])
        self.assertIn("filter", stats["systems"])
        self.assertIn("monitor", stats["systems"])
        self.assertIn("auto_accept", stats["systems"])

        self.monitoring.stop()

    def test_problem_queue_monitoring(self):
        """Test problem queue is monitored"""
        stats = self.monitoring.get_stats()
        self.assertIn("problem_queue", stats["systems"])
        self.assertIn("problems_detected", stats["systems"]["problem_queue"])


class IntegrationTest(unittest.TestCase):
    """Integration tests for all systems working together"""

    def test_full_system_integration(self):
        """Test all systems work together"""
        from full_time_monitoring_service import get_full_time_monitoring_service

        # Get monitoring service (should auto-start)
        service = get_full_time_monitoring_service()
        self.assertIsNotNone(service)

        # Wait a moment for systems to initialize
        time.sleep(2.0)

        # Check all systems are active
        stats = service.get_stats()
        systems = stats.get("systems", {})

        # At least some systems should be active
        active_count = sum(
            1 for sys_name, sys_data in systems.items()
            if isinstance(sys_data, dict) and sys_data.get("active", False)
        )
        self.assertGreater(active_count, 0, "At least one system should be active")


def run_all_tests():
    """Run all test suites"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(VoiceTranscriptQueueTest))
    suite.addTests(loader.loadTestsFromTestCase(VoiceFilterSystemTest))
    suite.addTests(loader.loadTestsFromTestCase(AutoSendMonitorTest))
    suite.addTests(loader.loadTestsFromTestCase(AutoAcceptTest))
    suite.addTests(loader.loadTestsFromTestCase(FullTimeMonitoringTest))
    suite.addTests(loader.loadTestsFromTestCase(IntegrationTest))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Voice Systems Testing Framework")
    parser.add_argument("--test", help="Run specific test class")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--tv-filter", action="store_true", help="Test TV filtering specifically")
    parser.add_argument("--auto-accept", action="store_true", help="Test auto-accept 'Keep All' functionality")

    args = parser.parse_args()

    if args.tv_filter:
        # Specific TV filter test
        print("\n🧪 Testing TV Audio Filtering (Bleed-Through Prevention)...")
        suite = unittest.TestLoader().loadTestsFromTestCase(VoiceFilterSystemTest)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1

    if args.auto_accept:
        # Specific auto-accept test
        print("\n🧪 Testing Auto-Accept 'Keep All' Button Functionality...")
        suite = unittest.TestLoader().loadTestsFromTestCase(AutoAcceptTest)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        return 0 if result.wasSuccessful() else 1

    if args.test:
        # Run specific test class
        test_class = globals().get(args.test)
        if test_class:
            suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            return 0 if result.wasSuccessful() else 1
        else:
            print(f"❌ Test class '{args.test}' not found")
            return 1

    # Run all tests by default
    print("\n🧪 Running All Voice Systems Tests...")
    success = run_all_tests()
    return 0 if success else 1


if __name__ == "__main__":


    sys.exit(main())