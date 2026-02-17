#!/usr/bin/env python3
"""
Agent Reporting Integration
<COMPANY_NAME> LLC

Ensures all agents report status and operational data to the command center.
Provides standardized reporting interface for all agent types.
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from cfs_command_center_supervisor import CFSCommandCenterSupervisor
    COMMAND_CENTER_AVAILABLE = True
except ImportError:
    COMMAND_CENTER_AVAILABLE = False
    CFSCommandCenterSupervisor = None

logger = get_logger("AgentReportingIntegration")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class AgentReporter:
    """
    Standardized agent reporting interface

    All agents should use this to report status to the command center.
    """

    def __init__(self, agent_id: str, agent_name: str, command_center: Optional[CFSCommandCenterSupervisor] = None):
        """Initialize agent reporter"""
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.command_center = command_center
        self.logger = get_logger(f"AgentReporter.{agent_id}")

        if not self.command_center and COMMAND_CENTER_AVAILABLE:
            try:
                project_root = Path(__file__).parent.parent.parent
                self.command_center = CFSCommandCenterSupervisor(project_root)
            except Exception as e:
                self.logger.warning(f"Could not initialize command center: {e}")

    def report_status(self, status_data: Dict[str, Any]) -> bool:
        """
        Report agent status to command center

        Args:
            status_data: Dictionary containing:
                - status: Agent status (active, idle, busy, degraded, failed)
                - health_score: Health score (0-100)
                - success_rate: Success rate (0-100)
                - error_count: Number of errors
                - request_count: Number of requests
                - cpu_usage: CPU usage percentage
                - memory_usage_mb: Memory usage in MB
                - active_tasks: Number of active tasks
                - operational_data: Any operational data
        """
        if not self.command_center:
            self.logger.warning("Command center not available - status not reported")
            return False

        # Add agent identification
        status_data['agent_id'] = self.agent_id
        status_data['agent_name'] = self.agent_name
        status_data['timestamp'] = datetime.now().isoformat()

        try:
            success = self.command_center.update_agent_status(self.agent_id, status_data)
            if success:
                self.logger.debug(f"Status reported to command center")
            return success
        except Exception as e:
            self.logger.error(f"Failed to report status: {e}")
            return False

    def report_heartbeat(self) -> bool:
        """Report heartbeat to command center"""
        return self.report_status({
            'status': 'active',
            'heartbeat': True
        })

    def report_alert(self, alert_type: str, message: str, severity: str = "medium") -> bool:
        """Report alert to command center"""
        return self.report_status({
            'status': 'active',
            'alert': {
                'type': alert_type,
                'message': message,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
        })

    def report_operational_data(self, data: Dict[str, Any]) -> bool:
        """Report operational data to command center"""
        return self.report_status({
            'status': 'active',
            'operational_data': data
        })


def get_agent_reporter(agent_id: str, agent_name: str) -> AgentReporter:
    """Get agent reporter instance for an agent"""
    return AgentReporter(agent_id, agent_name)


# Example usage for agents
if __name__ == "__main__":
    # Example: Agent reporting its status
    reporter = get_agent_reporter("test_agent", "Test Agent")

    # Report status
    reporter.report_status({
        'status': 'active',
        'health_score': 95.0,
        'success_rate': 98.5,
        'error_count': 2,
        'request_count': 150,
        'cpu_usage': 25.0,
        'memory_usage_mb': 512.0,
        'active_tasks': 3
    })

    # Report heartbeat
    reporter.report_heartbeat()

    # Report alert
    reporter.report_alert("performance", "High CPU usage detected", "high")

    # Report operational data
    reporter.report_operational_data({
        'tasks_completed': 100,
        'current_operation': 'processing_data'
    })

    print("✅ Agent reporting examples completed")

