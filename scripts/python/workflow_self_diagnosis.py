"""
Workflow Self-Diagnosis Mixin
Provides self-diagnosis capabilities for workflows.
"""

from typing import Dict, Any, List
from datetime import datetime
import logging


class WorkflowSelfDiagnosisMixin:
    """Mixin class providing workflow self-diagnosis capabilities"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(self.__class__.__name__)
        self._last_failure = None

    def diagnose_workflow_health(self) -> Dict[str, Any]:
        """
        Perform comprehensive self-diagnosis of workflow health.

        Unlike silent failures, this tells you exactly what's wrong and why.
        """
        diagnosis = {
            'timestamp': datetime.now().isoformat(),
            'workflow_name': getattr(self, 'workflow_name', 'unknown'),
            'overall_health': 'unknown',
            'critical_issues': [],
            'warnings': [],
            'recommendations': [],
            'system_status': {},
            'next_steps': []
        }

        # Check basic workflow state
        if hasattr(self, 'step_tracker') and self.step_tracker:
            diagnosis['system_status']['step_tracker'] = 'available'
            current_step = getattr(self.step_tracker, 'current_step', 0)
            total_steps = getattr(self, 'total_steps', 0)
            diagnosis['system_status']['progress'] = f"{current_step}/{total_steps}"

            if current_step == 0:
                diagnosis['critical_issues'].append("Workflow has not started any steps")
                diagnosis['recommendations'].append("Initialize workflow and begin execution")
        else:
            diagnosis['critical_issues'].append("Step tracker not available")
            diagnosis['recommendations'].append("Initialize workflow with proper step tracking")

        # Check confidence scorer
        if hasattr(self, 'confidence_scorer') and self.confidence_scorer:
            diagnosis['system_status']['confidence_scorer'] = 'available'
        else:
            diagnosis['warnings'].append("Confidence scorer not available - reduced hallucination protection")
            diagnosis['recommendations'].append("Initialize confidence scorer for full functionality")

        # Check expected deliverables
        if hasattr(self, 'expected_deliverables') and self.expected_deliverables:
            diagnosis['system_status']['deliverables'] = f"{len(self.expected_deliverables)} expected"
        else:
            diagnosis['warnings'].append("No expected deliverables defined")
            diagnosis['recommendations'].append("Define expected deliverables for completion verification")

        # Determine overall health
        if diagnosis['critical_issues']:
            diagnosis['overall_health'] = 'critical'
            diagnosis['next_steps'].append("Address critical issues immediately")
        elif diagnosis['warnings']:
            diagnosis['overall_health'] = 'warning'
            diagnosis['next_steps'].append("Review and address warnings")
        else:
            diagnosis['overall_health'] = 'healthy'
            diagnosis['next_steps'].append("Workflow is ready for execution")

        return diagnosis

    def explain_last_failure(self) -> Dict[str, Any]:
        """
        Explain the last workflow failure with detailed reasoning.

        No more silent failures - workflows now explain themselves.
        """
        if not hasattr(self, '_last_failure') or not self._last_failure:
            return {
                'has_failure': False,
                'explanation': 'No recent failures recorded',
                'timestamp': datetime.now().isoformat()
            }

        failure = self._last_failure

        explanation = {
            'has_failure': True,
            'timestamp': failure.get('timestamp', 'unknown'),
            'step': failure.get('step', 'unknown'),
            'operation': failure.get('operation', 'unknown'),
            'error_type': failure.get('error_type', 'unknown'),
            'error_message': failure.get('error_message', 'unknown'),
            'reasoning': self._analyze_failure_cause(failure),
            'root_cause': self._identify_root_cause(failure),
            'preventive_actions': self._suggest_prevention(failure),
            'recovery_steps': self._suggest_recovery(failure)
        }

        return explanation

    def _analyze_failure_cause(self, failure: Dict[str, Any]) -> str:
        """Analyze the root cause of a failure"""
        error_type = failure.get('error_type', '')
        operation = failure.get('operation', '')

        if 'ImportError' in error_type:
            return f"Missing dependency required for {operation}. The system tried to import a module that isn't installed."
        elif 'confidence' in operation.lower():
            return f"Confidence scoring failed during {operation}. This suggests either the input data was malformed or the confidence model encountered an unexpected condition."
        elif 'validation' in operation.lower():
            return f"Data validation failed during {operation}. The input data didn't meet the required criteria or format."
        elif 'network' in str(failure).lower():
            return f"Network connectivity issue during {operation}. The system couldn't reach required external services."
        else:
            return f"Unexpected error during {operation}. The specific cause needs further investigation of the error details."

    def _identify_root_cause(self, failure: Dict[str, Any]) -> str:
        """Identify the root cause category"""
        error_type = failure.get('error_type', '')
        operation = failure.get('operation', '')

        if 'ImportError' in error_type:
            return "dependency_missing"
        elif 'KeyError' in error_type or 'AttributeError' in error_type:
            return "data_structure_issue"
        elif 'confidence' in operation.lower():
            return "ai_model_failure"
        elif 'validation' in operation.lower():
            return "input_validation_failure"
        elif 'network' in str(failure).lower():
            return "connectivity_issue"
        else:
            return "unknown_cause"

    def _suggest_prevention(self, failure: Dict[str, Any]) -> List[str]:
        """Suggest preventive actions"""
        root_cause = self._identify_root_cause(failure)
        suggestions = []

        if root_cause == "dependency_missing":
            suggestions.extend([
                "Add missing dependencies to requirements.txt",
                "Implement dependency checking at startup",
                "Use try/except blocks for optional imports"
            ])
        elif root_cause == "data_structure_issue":
            suggestions.extend([
                "Add input validation before processing",
                "Implement data structure checks",
                "Use type hints and runtime type checking"
            ])
        elif root_cause == "ai_model_failure":
            suggestions.extend([
                "Add confidence model health checks",
                "Implement fallback confidence scoring",
                "Add input sanitization for AI models"
            ])
        elif root_cause == "connectivity_issue":
            suggestions.extend([
                "Add retry logic for network operations",
                "Implement connection health monitoring",
                "Use local caching for offline operation"
            ])

        return suggestions

    def _suggest_recovery(self, failure: Dict[str, Any]) -> List[str]:
        """Suggest recovery steps"""
        root_cause = self._identify_root_cause(failure)
        recovery = []

        if root_cause == "dependency_missing":
            recovery.extend([
                "Install missing dependencies",
                "Restart the workflow after installation",
                "Check system compatibility"
            ])
        elif root_cause == "data_structure_issue":
            recovery.extend([
                "Fix input data format",
                "Re-run validation checks",
                "Use corrected data for retry"
            ])
        elif root_cause == "ai_model_failure":
            recovery.extend([
                "Reset confidence model state",
                "Use simplified confidence scoring",
                "Skip confidence check for this operation"
            ])
        elif root_cause == "connectivity_issue":
            recovery.extend([
                "Check network connectivity",
                "Wait and retry operation",
                "Use cached or local alternatives"
            ])

        return recovery
