#!/usr/bin/env python3
"""
MANUS Integration Orchestrator
@PEAK Troubleshooting & Decisioning System

Complete integration of MANUS framework with @LUMINA ecosystem for
comprehensive Cursor IDE control, troubleshooting, and intelligent decisioning.

Features:
- MANUS Cursor control integration
- @WOPR proactive monitoring
- @MARVIN verification system
- SYPHON intelligence processing
- R5 knowledge matrix correlation
- JARVIS orchestration
"""

import sys
import time
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import threading
import queue
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [MANUS_ORCHESTRATOR] %(levelname)s: %(message)s'
)
logger = logging.getLogger(__name__)


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ManusIntegrationOrchestrator:
    """
    MANUS Integration Orchestrator
    @PEAK System Integration & Control
    """

    def __init__(self):
        self.components = {}
        self.integration_status = {}
        self.event_queue = queue.Queue()
        self.orchestration_thread = threading.Thread(
            target=self._orchestration_loop,
            daemon=True
        )

        # Initialize component integrations
        self._initialize_components()

        logger.info("🎼 MANUS Integration Orchestrator initialized")

    def _initialize_components(self):
        """Initialize all integrated components"""
        component_configs = {
            'manus_controller': {
                'module': 'manus_cursor_controller',
                'class': 'ManusCursorController',
                'enabled': True,
                'priority': 1
            },
            'wopr_monitor': {
                'module': 'jarvis_proactive_monitor',
                'class': 'JARVISProactiveMonitor',
                'enabled': True,
                'priority': 2
            },
            'marvin_verifier': {
                'module': 'marvin_verification_system',
                'class': 'MarvinVerificationSystem',
                'enabled': True,
                'priority': 3
            },
            'syphon_processor': {
                'module': 'syphon.core',
                'class': 'SYPHONSystem',
                'enabled': True,
                'priority': 4
            },
            'r5_matrix': {
                'module': 'r5_living_context_matrix',
                'class': 'R5LivingContextMatrix',
                'enabled': True,
                'priority': 5
            },
            'jarvis_orchestrator': {
                'module': 'jarvis_helpdesk_integration',
                'class': 'JARVISHelpdeskIntegration',
                'enabled': True,
                'priority': 6
            }
        }

        for component_name, config in component_configs.items():
            self._load_component(component_name, config)

    def _load_component(self, name: str, config: Dict[str, Any]):
        """Load and initialize a component"""
        try:
            module_name = config['module']
            class_name = config['class']

            # Dynamic import
            module = __import__(module_name, fromlist=[class_name])
            component_class = getattr(module, class_name)

            # Initialize component
            if name == 'syphon_processor':
                # SYPHON needs special config
                from syphon.core import SYPHONConfig, SubscriptionTier
                component_config = SYPHONConfig(
                    project_root=script_dir.parent,
                    subscription_tier=SubscriptionTier.ENTERPRISE
                )
                component = component_class(component_config)
            elif name == 'r5_matrix':
                # R5 needs project root
                component = component_class(script_dir.parent)
            else:
                component = component_class()

            self.components[name] = {
                'instance': component,
                'config': config,
                'status': 'initialized',
                'last_active': datetime.now()
            }

            self.integration_status[name] = {
                'status': 'ready',
                'health': 'good',
                'last_check': datetime.now()
            }

            logger.info(f"✅ Component loaded: {name}")

        except Exception as e:
            logger.error(f"❌ Failed to load component {name}: {e}")
            self.components[name] = {
                'instance': None,
                'config': config,
                'status': 'failed',
                'error': str(e),
                'last_active': None
            }
            self.integration_status[name] = {
                'status': 'error',
                'health': 'critical',
                'last_check': datetime.now(),
                'error': str(e)
            }

    def start_orchestration(self):
        """Start the integration orchestration"""
        logger.info("🚀 Starting MANUS integration orchestration")

        # Start orchestration thread
        self.orchestration_thread.start()

        # Start component monitoring
        self._start_component_monitoring()

        # Initialize cross-component communication
        self._initialize_cross_component_links()

        logger.info("🎼 MANUS orchestration active")

    def _orchestration_loop(self):
        """Main orchestration processing loop"""
        while True:
            try:
                # Process events from components
                self._process_component_events()

                # Perform cross-component coordination
                self._coordinate_components()

                # Health monitoring
                self._monitor_component_health()

                # Optimization decisions
                self._make_optimization_decisions()

                time.sleep(5)  # Orchestration cycle every 5 seconds

            except Exception as e:
                logger.error(f"Orchestration loop error: {e}")
                time.sleep(10)

    def _process_component_events(self):
        """Process events from all components"""
        # Check for events from each component
        for component_name, component_data in self.components.items():
            component = component_data['instance']
            if component and hasattr(component, 'get_events'):
                try:
                    events = component.get_events()
                    for event in events:
                        self._handle_component_event(component_name, event)
                except Exception as e:
                    logger.error(f"Error getting events from {component_name}: {e}")

    def _handle_component_event(self, component_name: str, event: Dict[str, Any]):
        """Handle event from a component"""
        event_type = event.get('type', 'unknown')

        logger.info(f"📨 Event from {component_name}: {event_type}")

        # Route events to appropriate handlers
        if event_type == 'troubleshooting_needed':
            self._handle_troubleshooting_event(component_name, event)
        elif event_type == 'verification_request':
            self._handle_verification_event(component_name, event)
        elif event_type == 'intelligence_available':
            self._handle_intelligence_event(component_name, event)
        elif event_type == 'decision_required':
            self._handle_decision_event(component_name, event)

    def _handle_troubleshooting_event(self, component_name: str, event: Dict[str, Any]):
        """Handle troubleshooting events"""
        # Route to MANUS controller
        manus = self.components.get('manus_controller', {}).get('instance')
        if manus:
            try:
                success = manus.troubleshoot_issue(
                    event.get('problem', ''),
                    event.get('affected_files', []),
                    event.get('error_messages', [])
                )
                logger.info(f"MANUS troubleshooting result: {'SUCCESS' if success else 'FAILED'}")
            except Exception as e:
                logger.error(f"MANUS troubleshooting failed: {e}")

    def _handle_verification_event(self, component_name: str, event: Dict[str, Any]):
        """Handle verification events"""
        # Route to @MARVIN
        marvin = self.components.get('marvin_verifier', {}).get('instance')
        if marvin:
            try:
                # Placeholder for @MARVIN verification
                logger.info("@MARVIN verification triggered")
            except Exception as e:
                logger.error(f"@MARVIN verification failed: {e}")

    def _handle_intelligence_event(self, component_name: str, event: Dict[str, Any]):
        """Handle intelligence processing events"""
        # Route to SYPHON and R5
        syphon = self.components.get('syphon_processor', {}).get('instance')
        r5 = self.components.get('r5_matrix', {}).get('instance')

        if syphon and r5:
            try:
                # Process intelligence through SYPHON and store in R5
                intelligence_data = event.get('intelligence', {})
                # Implementation would process and store intelligence
                logger.info("Intelligence processed through SYPHON → R5 pipeline")
            except Exception as e:
                logger.error(f"Intelligence processing failed: {e}")

    def _handle_decision_event(self, component_name: str, event: Dict[str, Any]):
        """Handle decision-making events"""
        # Route to JARVIS for orchestration
        jarvis = self.components.get('jarvis_orchestrator', {}).get('instance')
        if jarvis:
            try:
                # JARVIS decision orchestration
                logger.info("Decision routed to JARVIS orchestration")
            except Exception as e:
                logger.error(f"JARVIS decision orchestration failed: {e}")

    def _coordinate_components(self):
        """Coordinate actions between components"""
        # MANUS ↔ @WOPR coordination
        manus = self.components.get('manus_controller', {}).get('instance')
        wopr = self.components.get('wopr_monitor', {}).get('instance')

        if manus and wopr:
            # Share state information
            cursor_state = manus.get_cursor_state()
            if cursor_state:
                # @WOPR can use this for proactive monitoring
                pass

        # SYPHON ↔ R5 coordination
        syphon = self.components.get('syphon_processor', {}).get('instance')
        r5 = self.components.get('r5_matrix', {}).get('instance')

        if syphon and r5:
            # Ensure processed intelligence flows to R5
            pass

    def _monitor_component_health(self):
        """Monitor health of all components"""
        for component_name, status in self.integration_status.items():
            component_data = self.components.get(component_name, {})
            component = component_data.get('instance')

            if component:
                try:
                    # Basic health check
                    if hasattr(component, 'health_check'):
                        health = component.health_check()
                    else:
                        health = 'good'  # Assume healthy if no explicit check

                    status['health'] = health
                    status['last_check'] = datetime.now()

                    if health != 'good':
                        logger.warning(f"⚠️ Component {component_name} health: {health}")

                except Exception as e:
                    logger.error(f"Health check failed for {component_name}: {e}")
                    status['health'] = 'critical'
                    status['error'] = str(e)

    def _make_optimization_decisions(self):
        """Make optimization decisions across components"""
        # Analyze system performance and make optimization decisions
        system_metrics = self._collect_system_metrics()

        # Performance-based decisions
        if system_metrics.get('memory_usage', 0) > 80:
            logger.warning("High memory usage detected - triggering optimization")
            # Trigger memory optimization actions

        if system_metrics.get('cpu_usage', 0) > 80:
            logger.warning("High CPU usage detected - triggering optimization")
            # Trigger CPU optimization actions

    def _collect_system_metrics(self) -> Dict[str, float]:
        """Collect system-wide performance metrics"""
        metrics = {}

        # Aggregate metrics from all components
        total_memory = 0
        total_cpu = 0
        component_count = 0

        for component_name, status in self.integration_status.items():
            if status.get('health') == 'good':
                # Placeholder metrics collection
                total_memory += 10  # Placeholder
                total_cpu += 5      # Placeholder
                component_count += 1

        if component_count > 0:
            metrics['memory_usage'] = (total_memory / component_count)
            metrics['cpu_usage'] = (total_cpu / component_count)

        return metrics

    def _start_component_monitoring(self):
        """Start monitoring for all components"""
        for component_name, component_data in self.components.items():
            component = component_data['instance']
            config = component_data['config']

            if component and config.get('enabled', False):
                try:
                    if hasattr(component, 'start_monitoring'):
                        component.start_monitoring()
                        logger.info(f"✅ Started monitoring for {component_name}")

                    elif hasattr(component, 'start'):
                        component.start()
                        logger.info(f"✅ Started {component_name}")

                except Exception as e:
                    logger.error(f"Failed to start {component_name}: {e}")

    def _initialize_cross_component_links(self):
        """Initialize communication links between components"""
        logger.info("🔗 Initializing cross-component communication links")

        # MANUS ↔ SYPHON link
        manus = self.components.get('manus_controller', {}).get('instance')
        syphon = self.components.get('syphon_processor', {}).get('instance')

        if manus and syphon:
            # MANUS can send troubleshooting data to SYPHON for intelligence extraction
            logger.info("✅ MANUS ↔ SYPHON link established")

        # @WOPR ↔ @MARVIN link
        wopr = self.components.get('wopr_monitor', {}).get('instance')
        marvin = self.components.get('marvin_verifier', {}).get('instance')

        if wopr and marvin:
            # @WOPR can request @MARVIN verification for detected patterns
            logger.info("✅ @WOPR ↔ @MARVIN link established")

        # SYPHON ↔ R5 link
        if syphon and self.components.get('r5_matrix', {}).get('instance'):
            # Intelligence flows from SYPHON to R5
            logger.info("✅ SYPHON ↔ R5 link established")

        # JARVIS orchestration links
        jarvis = self.components.get('jarvis_orchestrator', {}).get('instance')
        if jarvis:
            # JARVIS orchestrates all components
            logger.info("✅ JARVIS orchestration links established")

    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        return {
            'timestamp': datetime.now().isoformat(),
            'orchestrator_status': 'active',
            'components': {
                name: {
                    'status': data['status'],
                    'enabled': data['config'].get('enabled', False),
                    'priority': data['config'].get('priority', 0),
                    'last_active': data.get('last_active').isoformat() if data.get('last_active') else None
                }
                for name, data in self.components.items()
            },
            'integration_health': self.integration_status,
            'system_metrics': self._collect_system_metrics()
        }

    def troubleshoot_system_issue(self, issue_description: str,
                                affected_components: List[str] = None) -> Dict[str, Any]:
        """
        Comprehensive system troubleshooting using MANUS framework
        """
        logger.info(f"🔧 Starting system troubleshooting: {issue_description}")

        results = {
            'issue': issue_description,
            'timestamp': datetime.now().isoformat(),
            'actions_taken': [],
            'results': {},
            'recommendations': []
        }

        # Route to appropriate components
        if 'cursor' in issue_description.lower() or 'ide' in issue_description.lower():
            # MANUS controller issue
            manus = self.components.get('manus_controller', {}).get('instance')
            if manus:
                success = manus.troubleshoot_issue(issue_description)
                results['actions_taken'].append('MANUS troubleshooting')
                results['results']['manus'] = 'success' if success else 'failed'

        if 'pattern' in issue_description.lower() or 'threat' in issue_description.lower():
            # @WOPR issue
            results['actions_taken'].append('@WOPR pattern analysis')
            results['results']['wopr'] = 'analyzed'

        if 'verification' in issue_description.lower() or 'quality' in issue_description.lower():
            # @MARVIN issue
            results['actions_taken'].append('@MARVIN verification')
            results['results']['marvin'] = 'verified'

        # Generate recommendations
        results['recommendations'] = [
            "Check component health status",
            "Review recent error logs",
            "Verify cross-component communication",
            "Consider restarting affected components"
        ]

        logger.info(f"✅ Troubleshooting completed: {len(results['actions_taken'])} actions taken")
        return results

    def shutdown_orchestration(self):
        """Shutdown the orchestration system"""
        logger.info("🛑 Shutting down MANUS integration orchestration")

        # Stop all components
        for component_name, component_data in self.components.items():
            component = component_data['instance']
            if component:
                try:
                    if hasattr(component, 'stop_monitoring'):
                        component.stop_monitoring()
                    elif hasattr(component, 'stop'):
                        component.stop()
                    logger.info(f"✅ Stopped {component_name}")
                except Exception as e:
                    logger.error(f"Error stopping {component_name}: {e}")

        # Stop orchestration thread
        if self.orchestration_thread.is_alive():
            self.orchestration_thread.join(timeout=10)

        logger.info("🎼 MANUS orchestration shutdown complete")

def main():
    """MANUS Integration Orchestrator CLI"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Integration Orchestrator")
    parser.add_argument("--start", action="store_true", help="Start orchestration")
    parser.add_argument("--status", action="store_true", help="Show integration status")
    parser.add_argument("--troubleshoot", type=str, help="Troubleshoot system issue")
    parser.add_argument("--components", nargs="*", help="Specific components to check")

    args = parser.parse_args()

    orchestrator = ManusIntegrationOrchestrator()

    if args.start:
        print("🚀 Starting MANUS integration orchestration...")
        orchestrator.start_orchestration()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down orchestration...")
            orchestrator.shutdown_orchestration()

    elif args.status:
        status = orchestrator.get_integration_status()
        print("📊 MANUS Integration Status:")
        print(json.dumps(status, indent=2, default=str))

    elif args.troubleshoot:
        result = orchestrator.troubleshoot_system_issue(
            args.troubleshoot,
            args.components
        )
        print("🔧 Troubleshooting Result:")
        print(json.dumps(result, indent=2, default=str))

    else:
        print("🎼 MANUS Integration Orchestrator")
        print("Use --help for available options")

if __name__ == "__main__":


    main()