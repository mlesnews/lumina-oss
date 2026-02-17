#!/usr/bin/env python3
"""
JARVIS Docker Hardware Testing Framework

JARVIS orchestrates testing AIOS on all hardware devices using Docker as VM.
5W1H analysis with R5 aggregation.

Tags: #JARVIS #DOCKER #HARDWARE_TESTING #5W1H #R5 @JARVIS @LUMINA
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISDockerHardwareTest")


class JARVISDockerHardwareTest:
    """
    JARVIS Docker Hardware Testing Framework

    Tests AIOS installation on all hardware devices using Docker as VM.
    """

    def __init__(self):
        """Initialize JARVIS Docker Hardware Test"""
        logger.info("🤖 JARVIS Docker Hardware Testing Framework initializing...")

        # Hardware profiles to test
        self.hardware_profiles = [
            'desktop_pc',
            'laptop',
            'raspberry_pi',
            'mobile_android',
            'server'
        ]

        # Docker compose file
        self.docker_compose = project_root / "docker" / "aios_kernel" / "docker-compose.yml"

        # Test results
        self.test_results = []

        # R5 integration
        self.r5 = None
        self._initialize_r5()

        logger.info("✅ JARVIS Docker Hardware Testing Framework ready")

    def _initialize_r5(self):
        """Initialize R5 for knowledge aggregation"""
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.r5 = R5LivingContextMatrix(project_root=project_root)
            logger.info("✅ R5 initialized for knowledge aggregation")
        except Exception as e:
            logger.warning(f"⚠️ R5 not available: {e}")
            self.r5 = None

    def _5w1h_analysis(self, profile: str) -> Dict[str, Any]:
        """
        5W1H Analysis for hardware testing

        What, Who, When, Where, Why, How
        """
        return {
            'what': f'Test AIOS installation on {profile}',
            'who': 'JARVIS (autonomous)',
            'when': datetime.now().isoformat(),
            'where': f'Docker container: aios-{profile}',
            'why': 'Verify AIOS works on all hardware devices',
            'how': 'Docker VM framework with hardware simulation'
        }

    def start_docker_services(self) -> bool:
        """Start Docker services for all hardware profiles"""
        logger.info("🐳 Starting Docker services...")

        try:
            # Change to docker directory
            docker_dir = self.docker_compose.parent

            # Start services
            result = subprocess.run(
                ['docker-compose', '-f', str(self.docker_compose), 'up', '-d'],
                cwd=str(docker_dir),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Docker services started")
                return True
            else:
                logger.error(f"❌ Docker services failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Docker error: {e}")
            return False

    def stop_docker_services(self) -> bool:
        """Stop Docker services"""
        logger.info("🐳 Stopping Docker services...")

        try:
            docker_dir = self.docker_compose.parent
            result = subprocess.run(
                ['docker-compose', '-f', str(self.docker_compose), 'down'],
                cwd=str(docker_dir),
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                logger.info("✅ Docker services stopped")
                return True
            else:
                logger.error(f"❌ Docker stop failed: {result.stderr}")
                return False
        except Exception as e:
            logger.error(f"❌ Docker error: {e}")
            return False

    def test_hardware_profile(self, profile: str) -> Dict[str, Any]:
        """
        Test AIOS on a specific hardware profile

        Args:
            profile: Hardware profile name

        Returns:
            Test result
        """
        logger.info(f"🧪 Testing hardware profile: {profile}")

        # 5W1H analysis
        analysis = self._5w1h_analysis(profile)

        # Test in Docker container
        container_name = f"aios-{profile.replace('_', '-')}"

        try:
            # Execute test in container
            result = subprocess.run(
                ['docker', 'exec', container_name, 'python', 
                 'scripts/python/aios/kernel/hardware_simulator.py'],
                capture_output=True,
                text=True,
                timeout=60
            )

            test_result = {
                'profile': profile,
                'container': container_name,
                '5w1h': analysis,
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None,
                'timestamp': datetime.now().isoformat()
            }

            # Aggregate with R5
            if self.r5:
                try:
                    self.r5.add_session({
                        'type': 'hardware_test',
                        'profile': profile,
                        'result': test_result,
                        '5w1h': analysis
                    })
                except Exception as e:
                    logger.warning(f"⚠️ R5 aggregation error: {e}")

            logger.info(f"✅ Test completed for {profile}: {'success' if test_result['success'] else 'failed'}")

            return test_result

        except subprocess.TimeoutExpired:
            logger.error(f"❌ Test timeout for {profile}")
            return {
                'profile': profile,
                'container': container_name,
                '5w1h': analysis,
                'success': False,
                'error': 'Timeout',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"❌ Test error for {profile}: {e}")
            return {
                'profile': profile,
                'container': container_name,
                '5w1h': analysis,
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def test_all_hardware(self) -> Dict[str, Any]:
        """Test AIOS on all hardware profiles"""
        logger.info("🧪 Testing AIOS on all hardware profiles...")

        # Start Docker services
        if not self.start_docker_services():
            return {
                'success': False,
                'error': 'Failed to start Docker services'
            }

        # Test each profile
        results = []
        for profile in self.hardware_profiles:
            result = self.test_hardware_profile(profile)
            results.append(result)
            self.test_results.append(result)

        # Summary
        success_count = sum(1 for r in results if r.get('success', False))
        total_count = len(results)

        summary = {
            'success': success_count == total_count,
            'total_tests': total_count,
            'successful_tests': success_count,
            'failed_tests': total_count - success_count,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }

        logger.info(f"✅ Testing complete: {success_count}/{total_count} successful")

        return summary

    def get_test_report(self) -> Dict[str, Any]:
        """Get comprehensive test report"""
        return {
            'test_results': self.test_results,
            'summary': {
                'total': len(self.test_results),
                'successful': sum(1 for r in self.test_results if r.get('success', False)),
                'failed': sum(1 for r in self.test_results if not r.get('success', False))
            },
            'hardware_profiles': self.hardware_profiles,
            'docker_vm': True
        }


def main():
    """JARVIS autonomous hardware testing"""
    print("=" * 80)
    print("🤖 JARVIS DOCKER HARDWARE TESTING FRAMEWORK")
    print("   Testing AIOS on all hardware devices using Docker VM")
    print("=" * 80)
    print()

    jarvis = JARVISDockerHardwareTest()

    # Test all hardware
    print("TESTING ALL HARDWARE PROFILES:")
    print("-" * 80)
    results = jarvis.test_all_hardware()

    print(f"\nResults: {results['successful_tests']}/{results['total_tests']} successful")
    print()

    for result in results['results']:
        status = "✅" if result.get('success') else "❌"
        print(f"{status} {result['profile']}: {result.get('error', 'Success')}")

    print()

    # Report
    print("TEST REPORT:")
    print("-" * 80)
    report = jarvis.get_test_report()
    print(f"Total Tests: {report['summary']['total']}")
    print(f"Successful: {report['summary']['successful']}")
    print(f"Failed: {report['summary']['failed']}")
    print()

    print("=" * 80)
    print("✅ JARVIS Docker Hardware Testing - Complete")
    print("=" * 80)


if __name__ == "__main__":


    main()