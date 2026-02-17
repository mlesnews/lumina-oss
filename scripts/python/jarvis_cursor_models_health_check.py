#!/usr/bin/env python3
"""
JARVIS Cursor IDE Models Health Check

Integrates Cursor IDE model testing into JARVIS unified health system.
Tests all models (cloud and local) using the same mechanics Cursor IDE uses.

Tags: #CURSOR_IDE #MODEL_HEALTH #HEALTH_CHECK #LLM_MODELS @JARVIS @LUMINA @DOIT
"""

import json
import os
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
project_root = script_dir.parent.parent
from lumina_core.paths import setup_paths
setup_paths()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger, setup_logging
except ImportError:
    from lumina_core.logging import get_logger
    setup_logging = lambda: None

logger = get_logger("JARVISCursorModelsHealthCheck")

# Import the model tester
try:
    from test_cursor_models import CursorModelTester, ModelTestResult
    MODEL_TESTER_AVAILABLE = True
except ImportError:
    MODEL_TESTER_AVAILABLE = False
    logger.warning("Model tester not available - install required dependencies")


@dataclass
class ModelHealthStatus:
    """Health status for a single model"""
    name: str
    title: str
    provider: str
    status: str  # "healthy", "degraded", "unhealthy", "unknown"
    response_time: float
    last_check: str
    error: Optional[str] = None
    local_only: bool = False


class CursorModelsHealthChecker:
    """Health checker for Cursor IDE models integrated with JARVIS"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_path = project_root / "data" / "cursor_models" / "cursor_models_config.json"
        self.health_data_dir = project_root / "data" / "cursor_models_health"
        self.health_data_dir.mkdir(parents=True, exist_ok=True)

        if not MODEL_TESTER_AVAILABLE:
            logger.error("Model tester not available")
            return

        self.tester = CursorModelTester(str(self.config_path))
        self.last_check_time = None
        self.last_results: List[ModelTestResult] = []
        self.health_status: Dict[str, Any] = {
            "timestamp": datetime.now().isoformat(),
            "overall_health": "UNKNOWN",
            "local_models": {},
            "cloud_models": {},
            "summary": {}
        }

    def check_models_health(self, quick_check: bool = False) -> Dict[str, Any]:
        """
        Check health of all Cursor IDE models

        Args:
            quick_check: If True, only check local models (faster)

        Returns:
            Health status dictionary
        """
        if not MODEL_TESTER_AVAILABLE:
            return {
                "status": "UNKNOWN",
                "error": "Model tester not available",
                "timestamp": datetime.now().isoformat()
            }

        start_time = time.time()
        logger.info("🔍 Starting Cursor IDE models health check...")

        try:
            # Load API keys from environment (optional)
            api_keys = {
                'openai': os.getenv('OPENAI_API_KEY', ''),
                'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY', ''),
                'anthropic': os.getenv('ANTHROPIC_API_KEY', ''),
                'ANTHROPIC_API_KEY': os.getenv('ANTHROPIC_API_KEY', ''),
            }

            # Run tests
            if quick_check:
                # Only test local models for quick check
                config = self.tester.load_config()
                local_models = [
                    m for m in config.get('cursor.chat.customModels', [])
                    if m.get('localOnly', False)
                ]
                # Temporarily replace models list for quick check
                original_models = config.get('cursor.chat.customModels', [])
                config['cursor.chat.customModels'] = local_models
                # Save temp config, test, restore
                temp_config_path = self.config_path.with_suffix('.json.tmp')
                with open(temp_config_path, 'w') as f:
                    json.dump(config, f, indent=2)
                self.tester.config_path = str(temp_config_path)
                results = self.tester.run_tests(api_keys)
                self.tester.config_path = str(self.config_path)
                temp_config_path.unlink()
            else:
                results = self.tester.run_tests(api_keys)

            self.last_results = results
            self.last_check_time = datetime.now()

            # Process results into health status
            health_status = self._process_results_to_health(results)

            # Calculate overall health
            health_status['overall_health'] = self._determine_overall_health(health_status)
            health_status['check_duration'] = time.time() - start_time
            health_status['timestamp'] = datetime.now().isoformat()

            self.health_status = health_status

            # Save health status
            self._save_health_status(health_status)

            logger.info(f"✅ Models health check complete: {health_status['overall_health']}")

            return health_status

        except Exception as e:
            logger.error(f"❌ Error during models health check: {str(e)}")
            return {
                "status": "UNHEALTHY",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def _process_results_to_health(self, results: List[ModelTestResult]) -> Dict[str, Any]:
        """Convert test results to health status format"""
        local_models = {}
        cloud_models = {}

        local_healthy = 0
        local_total = 0
        cloud_healthy = 0
        cloud_total = 0

        for result in results:
            # Determine health status from test result
            if result.status == "success":
                health_status = "healthy"
                if result.local_only:
                    local_healthy += 1
                else:
                    cloud_healthy += 1
            elif result.status == "failed":
                health_status = "unhealthy"
            elif result.status == "skipped":
                health_status = "unknown"
            else:
                health_status = "unknown"

            model_health = {
                "name": result.name,
                "title": result.title,
                "provider": result.provider,
                "status": health_status,
                "response_time": result.response_time,
                "last_check": datetime.now().isoformat(),
                "local_only": result.local_only,
                "requires_api_key": result.requires_api_key
            }

            if result.error:
                model_health["error"] = result.error[:200]  # Truncate long errors

            if result.local_only:
                local_models[result.name] = model_health
                local_total += 1
            else:
                cloud_models[result.name] = model_health
                cloud_total += 1

        return {
            "local_models": local_models,
            "cloud_models": cloud_models,
            "summary": {
                "local": {
                    "total": local_total,
                    "healthy": local_healthy,
                    "unhealthy": local_total - local_healthy,
                    "success_rate": f"{(local_healthy/local_total*100):.1f}%" if local_total > 0 else "0%"
                },
                "cloud": {
                    "total": cloud_total,
                    "healthy": cloud_healthy,
                    "unhealthy": cloud_total - cloud_healthy,
                    "success_rate": f"{(cloud_healthy/cloud_total*100):.1f}%" if cloud_total > 0 else "N/A"
                }
            }
        }

    def _determine_overall_health(self, health_status: Dict[str, Any]) -> str:
        """Determine overall health from individual model statuses"""
        local_summary = health_status.get('summary', {}).get('local', {})
        cloud_summary = health_status.get('summary', {}).get('cloud', {})

        local_unhealthy = local_summary.get('unhealthy', 0)
        local_total = local_summary.get('total', 0)

        # Local models are critical - if any are unhealthy, overall is unhealthy
        if local_total > 0 and local_unhealthy > 0:
            # Check if all local models are unhealthy
            if local_unhealthy == local_total:
                return "UNHEALTHY"
            else:
                return "DEGRADED"

        # If all local models are healthy
        if local_total > 0 and local_unhealthy == 0:
            return "HEALTHY"

        # If no local models tested
        return "UNKNOWN"

    def _save_health_status(self, health_status: Dict[str, Any]):
        try:
            """Save health status to file"""
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            health_file = self.health_data_dir / f"health_status_{timestamp}.json"

            with open(health_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, default=str)

            # Also save latest
            latest_file = self.health_data_dir / "health_status_latest.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(health_status, f, indent=2, default=str)

        except Exception as e:
            self.logger.error(f"Error in _save_health_status: {e}", exc_info=True)
            raise
    def get_health_status(self) -> Dict[str, Any]:
        """Get current health status"""
        return self.health_status

    def get_health_summary(self) -> Dict[str, Any]:
        """Get health summary for display"""
        summary = self.health_status.get('summary', {})
        local = summary.get('local', {})
        cloud = summary.get('cloud', {})

        return {
            "overall_health": self.health_status.get('overall_health', 'UNKNOWN'),
            "local_models": {
                "healthy": local.get('healthy', 0),
                "total": local.get('total', 0),
                "success_rate": local.get('success_rate', '0%')
            },
            "cloud_models": {
                "healthy": cloud.get('healthy', 0),
                "total": cloud.get('total', 0),
                "success_rate": cloud.get('success_rate', 'N/A')
            },
            "last_check": self.last_check_time.isoformat() if self.last_check_time else None
        }


def create_models_health_check_function(project_root: Path) -> callable:
    """
    Create a health check function for JARVIS unified health system

    Returns:
        Function that returns health status dict
    """
    checker = CursorModelsHealthChecker(project_root)

    def check_cursor_models_health() -> Dict[str, Any]:
        """Health check function for unified system"""
        try:
            # Quick check (local models only) for regular monitoring
            health_status = checker.check_models_health(quick_check=True)

            # Convert to unified health system format
            overall = health_status.get('overall_health', 'UNKNOWN')

            if overall == "HEALTHY":
                return {
                    "status": "HEALTHY",
                    "local_models": health_status.get('summary', {}).get('local', {}),
                    "message": "All local models operational"
                }
            elif overall == "DEGRADED":
                return {
                    "status": "DEGRADED",
                    "local_models": health_status.get('summary', {}).get('local', {}),
                    "message": "Some local models have issues"
                }
            elif overall == "UNHEALTHY":
                return {
                    "status": "UNHEALTHY",
                    "local_models": health_status.get('summary', {}).get('local', {}),
                    "message": "Local models are not functioning"
                }
            else:
                return {
                    "status": "UNKNOWN",
                    "message": "Model health check status unknown"
                }
        except Exception as e:
            logger.error(f"Error in models health check: {str(e)}")
            return {
                "status": "UNKNOWN",
                "error": str(e)
            }

    return check_cursor_models_health


def main():
    """Main entry point for standalone execution"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Cursor Models Health Check")
    parser.add_argument("--quick", action="store_true", help="Quick check (local models only)")
    parser.add_argument("--full", action="store_true", help="Full check (all models)")
    parser.add_argument("--status", action="store_true", help="Show current status")

    args = parser.parse_args()

    if not MODEL_TESTER_AVAILABLE:
        logger.error("Model tester not available")
        return

    from lumina_core.paths import get_project_root
    project_root = get_project_root()
    checker = CursorModelsHealthChecker(project_root)

    if args.status:
        status = checker.get_health_status()
        print(json.dumps(status, indent=2, default=str))
    elif args.full:
        health = checker.check_models_health(quick_check=False)
        print(json.dumps(health, indent=2, default=str))
    else:
        # Default: quick check
        health = checker.check_models_health(quick_check=True)
        summary = checker.get_health_summary()

        print("\n" + "=" * 80)
        print("🏥 CURSOR IDE MODELS HEALTH CHECK")
        print("=" * 80)
        print(f"Overall Health: {summary['overall_health']}")
        print(f"Local Models: {summary['local_models']['healthy']}/{summary['local_models']['total']} healthy ({summary['local_models']['success_rate']})")
        print(f"Cloud Models: {summary['cloud_models']['healthy']}/{summary['cloud_models']['total']} healthy ({summary['cloud_models']['success_rate']})")
        if summary['last_check']:
            print(f"Last Check: {summary['last_check']}")
        print("=" * 80 + "\n")


if __name__ == "__main__":


    main()