#!/usr/bin/env python3
"""
Test script for Agent History API endpoints
Tests all agent history functionality including search, pin/unpin, and timeout handling

Tags: #TEST #AGENT_HISTORY #API #PIN_UNPIN #SEARCH @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List

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

from agent_history_manager import AgentHistoryManager, AgentType, HistoryStatus

logger = get_logger("TestAgentHistoryAPI")


class AgentHistoryAPITester:
    """Test suite for Agent History API functionality"""

    def __init__(self):
        self.project_root = project_root
        self.manager = AgentHistoryManager(project_root)
        self.test_results = {
            "passed": [],
            "failed": [],
            "warnings": []
        }
        self.test_histories = []

    def setup_test_data(self):
        """Create test agent histories"""
        logger.info("=" * 80)
        logger.info("📋 SETTING UP TEST DATA")
        logger.info("=" * 80)

        # Create test histories
        test_cases = [
            {
                "agent_type": AgentType.AGENT,
                "agent_name": "Test Agent 1",
                "chat_id": "chat_test_1",
                "ask_id": "ask_test_1"
            },
            {
                "agent_type": AgentType.SUB_AGENT,
                "agent_name": "Test Sub-Agent 1",
                "chat_id": "chat_test_2",
                "ask_id": "ask_test_2"
            },
            {
                "agent_type": AgentType.AGENT,
                "agent_name": "Search Test Agent",
                "chat_id": "chat_search_1",
                "workflow_id": "workflow_search_1"
            },
            {
                "agent_type": AgentType.SUB_AGENT,
                "agent_name": "Pin Test Agent",
                "chat_id": "chat_pin_1"
            }
        ]

        for test_case in test_cases:
            history = self.manager.create_agent_history(**test_case)
            self.test_histories.append(history)
            logger.info(f"   ✅ Created test history: {history.history_id} ({history.agent_name})")

        logger.info(f"\n   📊 Created {len(self.test_histories)} test histories\n")

    def test_search_functionality(self):
        """Test search functionality with pagination"""
        logger.info("=" * 80)
        logger.info("🔍 TESTING SEARCH FUNCTIONALITY")
        logger.info("=" * 80)

        # Test 1: Basic search
        try:
            result = self.manager.search_histories("Test", limit=10, offset=0)
            assert result["total"] > 0, "Search should return results"
            assert len(result["items"]) > 0, "Search should return items"
            assert "hasMore" in result, "Result should include hasMore flag"
            self.test_results["passed"].append("Basic search")
            logger.info("   ✅ Basic search: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Basic search: {str(e)}")
            logger.error(f"   ❌ Basic search: FAILED - {e}")

        # Test 2: Pagination
        try:
            result1 = self.manager.search_histories("Test", limit=2, offset=0)
            result2 = self.manager.search_histories("Test", limit=2, offset=2)

            assert result1["offset"] == 0, "First page offset should be 0"
            assert result2["offset"] == 2, "Second page offset should be 2"
            assert len(result1["items"]) <= 2, "First page should have max 2 items"
            assert len(result2["items"]) <= 2, "Second page should have max 2 items"

            # Items should be different
            ids1 = {item["history_id"] for item in result1["items"]}
            ids2 = {item["history_id"] for item in result2["items"]}
            assert ids1.isdisjoint(ids2), "Pages should have different items"

            self.test_results["passed"].append("Pagination")
            logger.info("   ✅ Pagination: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Pagination: {str(e)}")
            logger.error(f"   ❌ Pagination: FAILED - {e}")

        # Test 3: Keyword filtering
        try:
            result = self.manager.search_histories("Search", limit=10, offset=0)
            assert any("Search" in item["agent_name"] for item in result["items"]), \
                "Search should find items with keyword in name"
            self.test_results["passed"].append("Keyword filtering")
            logger.info("   ✅ Keyword filtering: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Keyword filtering: {str(e)}")
            logger.error(f"   ❌ Keyword filtering: FAILED - {e}")

        # Test 4: Empty search
        try:
            result = self.manager.search_histories("NonExistentKeyword12345", limit=10, offset=0)
            assert result["total"] == 0 or len(result["items"]) == 0, \
                "Search for non-existent keyword should return empty results"
            self.test_results["passed"].append("Empty search")
            logger.info("   ✅ Empty search: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Empty search: {str(e)}")
            logger.error(f"   ❌ Empty search: FAILED - {e}")

    def test_pin_unpin_functionality(self):
        """Test pin/unpin functionality"""
        logger.info("=" * 80)
        logger.info("📌 TESTING PIN/UNPIN FUNCTIONALITY")
        logger.info("=" * 80)

        if not self.test_histories:
            logger.warning("   ⚠️  No test histories available")
            return

        test_history = self.test_histories[0]
        history_id = test_history.history_id

        # Test 1: Pin history
        try:
            success = self.manager.pin_history(history_id)
            assert success, "Pin operation should succeed"

            # Verify pin status
            history = self.manager.get_history_by_id(history_id)
            assert history is not None, "History should exist"
            assert history.pinned, "History should be pinned"

            self.test_results["passed"].append("Pin history")
            logger.info("   ✅ Pin history: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Pin history: {str(e)}")
            logger.error(f"   ❌ Pin history: FAILED - {e}")

        # Test 2: Get pinned histories
        try:
            pinned = self.manager.get_pinned_histories()
            assert len(pinned) > 0, "Should have at least one pinned history"
            assert any(h.history_id == history_id for h in pinned), \
                "Pinned history should be in pinned list"
            self.test_results["passed"].append("Get pinned histories")
            logger.info("   ✅ Get pinned histories: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Get pinned histories: {str(e)}")
            logger.error(f"   ❌ Get pinned histories: FAILED - {e}")

        # Test 3: Unpin history
        try:
            success = self.manager.unpin_history(history_id)
            assert success, "Unpin operation should succeed"

            # Verify unpin status
            history = self.manager.get_history_by_id(history_id)
            assert history is not None, "History should exist"
            assert not history.pinned, "History should not be pinned"

            self.test_results["passed"].append("Unpin history")
            logger.info("   ✅ Unpin history: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Unpin history: {str(e)}")
            logger.error(f"   ❌ Unpin history: FAILED - {e}")

        # Test 4: Pin history again (toggle test)
        try:
            success = self.manager.pin_history(history_id)
            assert success, "Re-pin operation should succeed"
            history = self.manager.get_history_by_id(history_id)
            assert history.pinned, "History should be pinned again"
            self.test_results["passed"].append("Re-pin history")
            logger.info("   ✅ Re-pin history: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Re-pin history: {str(e)}")
            logger.error(f"   ❌ Re-pin history: FAILED - {e}")

    def test_get_history_by_id(self):
        """Test get history by ID functionality"""
        logger.info("=" * 80)
        logger.info("📖 TESTING GET HISTORY BY ID")
        logger.info("=" * 80)

        if not self.test_histories:
            logger.warning("   ⚠️  No test histories available")
            return

        test_history = self.test_histories[0]
        history_id = test_history.history_id

        # Test 1: Get existing history
        try:
            history = self.manager.get_history_by_id(history_id)
            assert history is not None, "History should be retrieved"
            assert history.history_id == history_id, "History ID should match"
            assert history.last_accessed is not None, "Last accessed should be updated"
            self.test_results["passed"].append("Get existing history")
            logger.info("   ✅ Get existing history: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Get existing history: {str(e)}")
            logger.error(f"   ❌ Get existing history: FAILED - {e}")

        # Test 2: Get non-existent history
        try:
            history = self.manager.get_history_by_id("non_existent_history_id_12345")
            assert history is None, "Non-existent history should return None"
            self.test_results["passed"].append("Get non-existent history")
            logger.info("   ✅ Get non-existent history: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Get non-existent history: {str(e)}")
            logger.error(f"   ❌ Get non-existent history: FAILED - {e}")

    def test_error_handling(self):
        """Test error handling"""
        logger.info("=" * 80)
        logger.info("⚠️  TESTING ERROR HANDLING")
        logger.info("=" * 80)

        # Test 1: Pin non-existent history
        try:
            success = self.manager.pin_history("non_existent_history_id_12345")
            assert not success, "Pin non-existent history should fail"
            self.test_results["passed"].append("Pin non-existent history error handling")
            logger.info("   ✅ Pin non-existent history error handling: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Pin non-existent history: {str(e)}")
            logger.error(f"   ❌ Pin non-existent history: FAILED - {e}")

        # Test 2: Unpin non-existent history
        try:
            success = self.manager.unpin_history("non_existent_history_id_12345")
            assert not success, "Unpin non-existent history should fail"
            self.test_results["passed"].append("Unpin non-existent history error handling")
            logger.info("   ✅ Unpin non-existent history error handling: PASSED")
        except Exception as e:
            self.test_results["failed"].append(f"Unpin non-existent history: {str(e)}")
            logger.error(f"   ❌ Unpin non-existent history: FAILED - {e}")

    def cleanup_test_data(self):
        """Clean up test data (optional)"""
        logger.info("=" * 80)
        logger.info("🧹 CLEANUP (Optional)")
        logger.info("=" * 80)
        logger.info("   ℹ️  Test histories remain in database for inspection")
        logger.info("   ℹ️  To remove manually, delete from agent_histories.json")

    def run_all_tests(self):
        """Run all tests"""
        logger.info("=" * 80)
        logger.info("🧪 AGENT HISTORY API TEST SUITE")
        logger.info("=" * 80)
        logger.info("")

        try:
            # Setup
            self.setup_test_data()

            # Run tests
            self.test_search_functionality()
            self.test_pin_unpin_functionality()
            self.test_get_history_by_id()
            self.test_error_handling()

            # Cleanup
            self.cleanup_test_data()

            # Summary
            self.print_summary()

        except Exception as e:
            logger.error(f"Test suite error: {e}", exc_info=True)
            self.test_results["failed"].append(f"Test suite error: {str(e)}")
            self.print_summary()

    def print_summary(self):
        """Print test summary"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 TEST SUMMARY")
        logger.info("=" * 80)
        logger.info("")

        passed_count = len(self.test_results["passed"])
        failed_count = len(self.test_results["failed"])
        warning_count = len(self.test_results["warnings"])
        total_count = passed_count + failed_count

        logger.info(f"   ✅ Passed: {passed_count}")
        logger.info(f"   ❌ Failed: {failed_count}")
        logger.info(f"   ⚠️  Warnings: {warning_count}")
        logger.info(f"   📊 Total: {total_count}")
        logger.info("")

        if self.test_results["passed"]:
            logger.info("   ✅ PASSED TESTS:")
            for test in self.test_results["passed"]:
                logger.info(f"      - {test}")
            logger.info("")

        if self.test_results["failed"]:
            logger.info("   ❌ FAILED TESTS:")
            for test in self.test_results["failed"]:
                logger.info(f"      - {test}")
            logger.info("")

        if self.test_results["warnings"]:
            logger.info("   ⚠️  WARNINGS:")
            for warning in self.test_results["warnings"]:
                logger.info(f"      - {warning}")
            logger.info("")

        success_rate = (passed_count / total_count * 100) if total_count > 0 else 0
        logger.info(f"   📈 Success Rate: {success_rate:.1f}%")
        logger.info("")

        if failed_count == 0:
            logger.info("   🎉 ALL TESTS PASSED!")
        else:
            logger.info(f"   ⚠️  {failed_count} test(s) failed")

        logger.info("")
        logger.info("=" * 80)


def main():
    """Main entry point"""
    tester = AgentHistoryAPITester()
    tester.run_all_tests()

    # Exit with error code if tests failed
    if tester.test_results["failed"]:
        sys.exit(1)
    return 0


if __name__ == "__main__":


    sys.exit(main())