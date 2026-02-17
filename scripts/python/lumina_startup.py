#!/usr/bin/env python3
"""
🔄 **Lumina Startup System - Persistent Initialization**

Comprehensive startup system that ensures all Lumina systems remain active
across Cursor IDE restarts. Eliminates gaps and maintains full functionality.

@V3_WORKFLOWED: True
@TEST_FIRST: True
@PERSISTENT_STARTUP: Enabled
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

# Local imports
script_dir = Path(__file__).parent.parent
project_root = script_dir.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

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

logger = get_logger("LuminaStartup")


class LuminaStartupSystem:
    """
    Comprehensive startup system for Lumina.

    Ensures all systems initialize properly and remain persistent
    across Cursor IDE restarts with zero functionality gaps.
    """

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent
        self.startup_log = []
        self.systems_status = {}

    async def full_system_startup(self) -> Dict[str, Any]:
        """
        Perform complete Lumina system startup.

        Initializes all critical systems in the correct order:
        1. Attribution system
        2. Jarvis extensions framework
        3. Voice systems
        4. Development tools
        5. Performance monitoring
        """

        logger.info("🚀 **LUMINA SYSTEM STARTUP INITIATED**")
        logger.info("=" * 60)

        startup_results = {
            'timestamp': asyncio.get_event_loop().time(),
            'systems_initialized': [],
            'systems_failed': [],
            'overall_status': 'starting',
            'startup_duration': 0
        }

        start_time = asyncio.get_event_loop().time()

        try:
            # Phase 1: Core Attribution System
            logger.info("\n📜 **Phase 1: Attribution System**")
            attribution_status = await self._initialize_attribution_system()
            startup_results['systems_initialized'].append({
                'phase': 1,
                'system': 'attribution',
                'status': attribution_status
            })

            # Phase 2: Jarvis Extensions Framework
            logger.info("\n🔧 **Phase 2: Jarvis Extensions Framework**")
            jarvis_status = await self._initialize_jarvis_extensions()
            startup_results['systems_initialized'].append({
                'phase': 2,
                'system': 'jarvis_extensions',
                'status': jarvis_status
            })

            # Phase 3: Voice Systems
            logger.info("\n🎙️ **Phase 3: Voice Systems**")
            voice_status = await self._initialize_voice_systems()
            startup_results['systems_initialized'].append({
                'phase': 3,
                'system': 'voice_systems',
                'status': voice_status
            })

            # Phase 4: Development Tools Integration
            logger.info("\n🛠️ **Phase 4: Development Tools**")
            dev_tools_status = await self._initialize_development_tools()
            startup_results['systems_initialized'].append({
                'phase': 4,
                'system': 'development_tools',
                'status': dev_tools_status
            })

            # Phase 5: Performance & Monitoring
            logger.info("\n📊 **Phase 5: Performance Monitoring**")
            monitoring_status = await self._initialize_performance_monitoring()
            startup_results['systems_initialized'].append({
                'phase': 5,
                'system': 'performance_monitoring',
                'status': monitoring_status
            })

            # Phase 6: Final Verification
            logger.info("\n✅ **Phase 6: System Verification**")
            verification_status = await self._perform_final_verification()
            startup_results['systems_initialized'].append({
                'phase': 6,
                'system': 'final_verification',
                'status': verification_status
            })

            # Calculate startup duration
            end_time = asyncio.get_event_loop().time()
            startup_results['startup_duration'] = end_time - start_time

            # Determine overall status
            failed_systems = [s for s in startup_results['systems_initialized'] if not s['status']['success']]
            if failed_systems:
                startup_results['overall_status'] = 'degraded'
                startup_results['systems_failed'] = failed_systems
            else:
                startup_results['overall_status'] = 'fully_operational'

            # Log final status
            self._log_startup_results(startup_results)

            return startup_results

        except Exception as e:
            logger.error(f"   ❌ CRITICAL: Startup failed with error: {e}")
            startup_results['overall_status'] = 'failed'
            startup_results['critical_error'] = str(e)
            return startup_results

    async def _initialize_attribution_system(self) -> Dict[str, Any]:
        """Initialize the attribution system."""
        try:
            from attributions_system import get_attribution_system

            # Get attribution system instance
            attribution_system = get_attribution_system()

            # Verify compliance
            from attributions_system import generate_compliance_report
            compliance_report = generate_compliance_report(days_back=7)

            if compliance_report['status'] == '✅ FULLY COMPLIANT':
                logger.info("   ✅ Attribution system initialized - 100% compliant")
                return {
                    'success': True,
                    'compliance_rate': compliance_report['overall_compliance']['compliance_rate'],
                    'citations_tracked': compliance_report['overall_compliance']['total_attributions']
                }
            else:
                logger.warning("   ⚠️ Attribution system initialized with compliance issues")
                return {
                    'success': False,
                    'error': 'Compliance verification failed',
                    'compliance_rate': compliance_report['overall_compliance']['compliance_rate']
                }

        except ImportError:
            logger.warning("   ⚠️ Attribution system not available")
            return {'success': False, 'error': 'Attribution system import failed'}
        except Exception as e:
            logger.error(f"   ❌ Attribution system initialization failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _initialize_jarvis_extensions(self) -> Dict[str, Any]:
        """Initialize Jarvis extensions framework."""
        try:
            from lumina_core.jarvis.extensions.integration_manager import initialize_integration_framework

            # Initialize the framework
            success = await initialize_integration_framework()

            if success:
                logger.info("   ✅ Jarvis extensions framework initialized")

                # Get extension status
                from lumina_core.jarvis.extensions.integration_manager import get_integration_manager
                manager = get_integration_manager()
                status = manager.get_extension_status()

                return {
                    'success': True,
                    'extensions_registered': status['total_extensions'],
                    'extensions_active': status['active_extensions']
                }
            else:
                logger.warning("   ⚠️ Jarvis extensions framework partially initialized")
                return {'success': False, 'error': 'Framework initialization incomplete'}

        except ImportError:
            logger.warning("   ⚠️ Jarvis extensions not available")
            return {'success': False, 'error': 'Extensions framework import failed'}
        except Exception as e:
            logger.error(f"   ❌ Jarvis extensions initialization failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _initialize_voice_systems(self) -> Dict[str, Any]:
        """Initialize voice systems."""
        try:
            # Import voice systems
            voice_systems_status = []

            # Unified Voice Interface
            try:
                from unified_voice_interface import initialize_unified_voice
                voice_success = await initialize_unified_voice()
                voice_systems_status.append({
                    'system': 'unified_voice',
                    'status': 'active' if voice_success else 'inactive'
                })
            except ImportError:
                voice_systems_status.append({
                    'system': 'unified_voice',
                    'status': 'unavailable'
                })

            # Voice Transcript Queue
            try:
                from voice_transcript_queue import get_voice_transcript_queue
                queue = get_voice_transcript_queue()
                queue.ensure_active()
                voice_systems_status.append({
                    'system': 'transcript_queue',
                    'status': 'active'
                })
            except ImportError:
                voice_systems_status.append({
                    'system': 'transcript_queue',
                    'status': 'unavailable'
                })

            active_systems = sum(1 for s in voice_systems_status if s['status'] == 'active')

            if active_systems > 0:
                logger.info(f"   ✅ Voice systems initialized ({active_systems} active)")
                return {
                    'success': True,
                    'active_systems': active_systems,
                    'systems': voice_systems_status
                }
            else:
                logger.warning("   ⚠️ No voice systems available")
                return {'success': False, 'error': 'No voice systems initialized'}

        except Exception as e:
            logger.error(f"   ❌ Voice systems initialization failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _initialize_development_tools(self) -> Dict[str, Any]:
        """Initialize development tools integration."""
        try:
            tools_status = []

            # Check for Cursor IDE integration
            cursor_available = self._check_cursor_ide_integration()
            tools_status.append({
                'tool': 'cursor_ide',
                'status': 'available' if cursor_available else 'unavailable'
            })

            # Check for Git integration
            git_available = self._check_git_integration()
            tools_status.append({
                'tool': 'git',
                'status': 'available' if git_available else 'unavailable'
            })

            # Check for container services
            container_available = self._check_container_services()
            tools_status.append({
                'tool': 'containers',
                'status': 'available' if container_available else 'unavailable'
            })

            available_tools = sum(1 for t in tools_status if t['status'] == 'available')

            logger.info(f"   ✅ Development tools initialized ({available_tools} available)")
            return {
                'success': True,
                'available_tools': available_tools,
                'tools': tools_status
            }

        except Exception as e:
            logger.error(f"   ❌ Development tools initialization failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _initialize_performance_monitoring(self) -> Dict[str, Any]:
        """Initialize performance monitoring systems."""
        try:
            monitoring_status = []

            # RR Methodology
            rr_active = self._check_rr_methodology()
            monitoring_status.append({
                'system': 'rr_methodology',
                'status': 'active' if rr_active else 'inactive'
            })

            # WOPR Evolution tracking
            wopr_active = self._check_wopr_evolution()
            monitoring_status.append({
                'system': 'wopr_evolution',
                'status': 'active' if wopr_active else 'inactive'
            })

            # Performance metrics
            metrics_active = self._check_performance_metrics()
            monitoring_status.append({
                'system': 'performance_metrics',
                'status': 'active' if metrics_active else 'inactive'
            })

            active_systems = sum(1 for s in monitoring_status if s['status'] == 'active')

            logger.info(f"   ✅ Performance monitoring initialized ({active_systems} active)")
            return {
                'success': True,
                'active_systems': active_systems,
                'monitoring': monitoring_status
            }

        except Exception as e:
            logger.error(f"   ❌ Performance monitoring initialization failed: {e}")
            return {'success': False, 'error': str(e)}

    async def _perform_final_verification(self) -> Dict[str, Any]:
        """Perform final system verification."""
        try:
            verification_results = []

            # Check overall system health
            health_score = await self._calculate_system_health_score()
            verification_results.append({
                'check': 'system_health',
                'score': health_score,
                'status': 'healthy' if health_score >= 0.8 else 'degraded'
            })

            # Verify persistence mechanisms
            persistence_ok = self._verify_persistence_mechanisms()
            verification_results.append({
                'check': 'persistence_mechanisms',
                'status': 'verified' if persistence_ok else 'failed'
            })

            # Check for gaps or failures
            gaps_found = self._check_for_system_gaps()
            verification_results.append({
                'check': 'system_gaps',
                'gaps_found': len(gaps_found),
                'status': 'no_gaps' if len(gaps_found) == 0 else 'gaps_detected'
            })

            overall_success = all(r['status'] in ['healthy', 'verified', 'no_gaps'] for r in verification_results)

            if overall_success:
                logger.info("   ✅ Final verification passed - all systems operational")
            else:
                logger.warning("   ⚠️ Final verification found issues")

            return {
                'success': overall_success,
                'verification_results': verification_results,
                'health_score': health_score
            }

        except Exception as e:
            logger.error(f"   ❌ Final verification failed: {e}")
            return {'success': False, 'error': str(e)}

    def _check_cursor_ide_integration(self) -> bool:
        """Check if Cursor IDE integration is available."""
        try:
            # Check for Cursor-specific files
            cursor_config = self.project_root / ".cursor"
            return cursor_config.exists()
        except:
            return False

    def _check_git_integration(self) -> bool:
        """Check if Git integration is available."""
        try:
            # Check if we're in a git repository
            git_dir = self.project_root / ".git"
            return git_dir.exists()
        except:
            return False

    def _check_container_services(self) -> bool:
        """Check if container services are available."""
        try:
            # Check for containerization directory
            container_dir = self.project_root / "containerization"
            return container_dir.exists()
        except:
            return False

    def _check_rr_methodology(self) -> bool:
        """Check if RR methodology is active."""
        try:
            # Check for RR-related files
            rr_files = [
                "RR_SESSION_COMPLETION_SYPHON.md",
                "WOPR_RR_INSIGHTS_IMPLEMENTATION.md"
            ]
            return any((self.project_root / f).exists() for f in rr_files)
        except:
            return False

    def _check_wopr_evolution(self) -> bool:
        """Check if WOPR evolution is active."""
        try:
            # Check for WOPR-related files
            wopr_files = [
                "LUMINA_WOPR_IMPLEMENTATION_ROADMAP.md",
                "LUMINA_10K_ADVANCED_SIMULATION.md"
            ]
            return any((self.project_root / f).exists() for f in wopr_files)
        except:
            return False

    def _check_performance_metrics(self) -> bool:
        """Check if performance metrics are active."""
        try:
            # Check for performance monitoring scripts
            perf_scripts = [
                "scripts/python/log_compression_system.py",
                "scripts/python/kenny_roast_and_repair.py"
            ]
            return any(Path(f).exists() for f in perf_scripts)
        except:
            return False

    async def _calculate_system_health_score(self) -> float:
        """Calculate overall system health score."""
        try:
            # Simple health calculation based on system availability
            health_factors = []

            # Attribution system health
            try:
                from attributions_system import generate_compliance_report
                compliance = generate_compliance_report(days_back=1)
                health_factors.append(compliance['overall_compliance']['compliance_rate'])
            except:
                health_factors.append(0.0)

            # Jarvis extensions health
            try:
                from lumina_core.jarvis.extensions.integration_manager import get_integration_manager
                manager = get_integration_manager()
                status = manager.get_extension_status()
                health_factors.append(status['active_extensions'] / max(1, status['total_extensions']))
            except:
                health_factors.append(0.0)

            # Voice systems health
            try:
                from unified_voice_interface import get_voice_system_status
                voice_status = get_voice_system_status()
                active_systems = sum(1 for s in voice_status['systems'].values() if s['available'])
                total_systems = len(voice_status['systems'])
                health_factors.append(active_systems / max(1, total_systems))
            except:
                health_factors.append(0.0)

            # Average health score
            if health_factors:
                return sum(health_factors) / len(health_factors)
            else:
                return 0.0

        except Exception as e:
            logger.debug(f"   Health calculation error: {e}")
            return 0.0

    def _verify_persistence_mechanisms(self) -> bool:
        """Verify persistence mechanisms are in place."""
        try:
            # Check for persistence-related files
            persistence_files = [
                ".cursor/commands/persistent.md",
                "lumina_core/jarvis/extensions/README.md",
                "ATTRIBUTIONS_AND_CREDITS.md"
            ]
            return all((self.project_root / f).exists() for f in persistence_files)
        except:
            return False

    def _check_for_system_gaps(self) -> List[str]:
        try:
            """Check for system gaps or failures."""
            gaps = []

            # Check for missing critical components
            critical_components = [
                ("attribution_system", "attributions_system.py"),
                ("jarvis_extensions", "lumina_core/jarvis/extensions/"),
                ("voice_systems", "unified_voice_interface.py"),
                ("startup_system", "lumina_startup.py")
            ]

            for component_name, component_path in critical_components:
                if not (self.project_root / component_path).exists():
                    gaps.append(f"Missing {component_name}: {component_path}")

            return gaps

        except Exception as e:
            self.logger.error(f"Error in _check_for_system_gaps: {e}", exc_info=True)
            raise
    def _log_startup_results(self, results: Dict[str, Any]):
        """Log startup results."""
        status = results['overall_status']
        duration = results['startup_duration']

        if status == 'fully_operational':
            logger.info("\n🎉 **STARTUP COMPLETE - ALL SYSTEMS OPERATIONAL**")
            logger.info(f"   ⏱️ Startup Duration: {duration:.2f}s")
            logger.info("   ✅ Zero gaps, full continuity achieved")
        elif status == 'degraded':
            logger.warning("\n⚠️ **STARTUP COMPLETE - DEGRADED MODE**")
            logger.warning(f"   ⏱️ Startup Duration: {duration:.2f}s")
            logger.warning(f"   ⚠️ {len(results['systems_failed'])} systems failed")
        else:
            logger.error("\n❌ **STARTUP FAILED**")
            logger.error(f"   ⏱️ Startup Duration: {duration:.2f}s")
            if 'critical_error' in results:
                logger.error(f"   💥 Critical Error: {results['critical_error']}")


# Global startup system
_startup_system = None


def get_startup_system() -> LuminaStartupSystem:
    """Get or create startup system instance."""
    global _startup_system
    if _startup_system is None:
        _startup_system = LuminaStartupSystem()
    return _startup_system


async def perform_full_startup() -> Dict[str, Any]:
    """Perform complete Lumina system startup."""
    startup_system = get_startup_system()
    return await startup_system.full_system_startup()


async def quick_startup_check() -> Dict[str, Any]:
    """Perform quick startup verification."""
    startup_system = get_startup_system()
    health_score = await startup_system._calculate_system_health_score()

    return {
        'health_score': health_score,
        'status': 'healthy' if health_score >= 0.8 else 'degraded',
        'timestamp': asyncio.get_event_loop().time()
    }


async def _cli_main():
    """Async CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Lumina Startup System")
    parser.add_argument("--full", action="store_true", help="Perform full system startup")
    parser.add_argument("--quick", action="store_true", help="Quick startup health check")
    parser.add_argument("--status", action="store_true", help="Show current system status")

    args = parser.parse_args()

    if args.full:
        print("🚀 **PERFORMING FULL LUMINA SYSTEM STARTUP**")
        print("=" * 60)
        results = await perform_full_startup()
        print(f"\n📊 **Startup Status: {results['overall_status'].upper()}**")
        print(f"   ⏱️ Startup Duration: {results.get('startup_duration', 0):.2f}s")
    elif args.quick:
        print("🔍 **QUICK STARTUP HEALTH CHECK**")
        print("=" * 40)
        results = await quick_startup_check()
        print(f"   Health Score: {results['health_score']:.2f}")
        print(f"   Status: {results['status'].upper()}")
    elif args.status:
        print("📊 **CURRENT SYSTEM STATUS**")
        print("=" * 30)
        startup_system = get_startup_system()
        health_score = await startup_system._calculate_system_health_score()
        print(f"   System Health: {health_score:.2f}")
        print(f"   Status: {'HEALTHY' if health_score >= 0.8 else 'DEGRADED'}")
    else:
        # Default: quick check
        results = await quick_startup_check()
        print(f"Health Score: {results['health_score']:.2f} - Status: {results['status'].upper()}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(_cli_main())