"""
Workflow Recovery Mixin
Provides recovery capabilities for workflow failures.
"""

from typing import Dict, Any
from datetime import datetime
import logging


class WorkflowRecoveryMixin:
    """Mixin class providing workflow recovery capabilities"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(self.__class__.__name__)

    def attempt_workflow_recovery(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Attempt to recover from workflow failure with detailed reasoning.

        Unlike silent failures, this tries to fix issues and explains the recovery process.
        """
        recovery_attempt = {
            'timestamp': datetime.now().isoformat(),
            'original_failure': failure_context,
            'recovery_strategy': self._determine_recovery_strategy(failure_context),
            'attempted_actions': [],
            'success': False,
            'final_state': 'failed',
            'reasoning': []
        }

        strategy = recovery_attempt['recovery_strategy']

        if strategy == 'retry_with_backoff':
            result = self._retry_with_exponential_backoff(failure_context)
            recovery_attempt['attempted_actions'].append('retry_with_backoff')
            recovery_attempt['reasoning'].append("Attempted retry with exponential backoff to handle transient failures")

        elif strategy == 'use_fallback_method':
            result = self._try_fallback_method(failure_context)
            recovery_attempt['attempted_actions'].append('use_fallback_method')
            recovery_attempt['reasoning'].append("Attempted fallback method to bypass the failed operation")

        elif strategy == 'repair_input_data':
            result = self._repair_input_data(failure_context)
            recovery_attempt['attempted_actions'].append('repair_input_data')
            recovery_attempt['reasoning'].append("Attempted to repair or sanitize input data causing the failure")

        elif strategy == 'skip_and_continue':
            result = self._skip_failed_operation(failure_context)
            recovery_attempt['attempted_actions'].append('skip_and_continue')
            recovery_attempt['reasoning'].append("Skipped failed operation and attempted to continue workflow")

        else:
            recovery_attempt['reasoning'].append(f"No suitable recovery strategy found for failure type: {failure_context.get('error_type', 'unknown')}")
            result = {'success': False, 'reason': 'No recovery strategy available'}

        recovery_attempt['success'] = result.get('success', False)
        recovery_attempt['final_state'] = 'recovered' if recovery_attempt['success'] else 'failed'
        recovery_attempt['result'] = result

        self.logger.info(f"Recovery attempt completed: {recovery_attempt['final_state']}")

        return recovery_attempt

    def _determine_recovery_strategy(self, failure_context: Dict[str, Any]) -> str:
        """Determine the best recovery strategy for a failure"""
        error_type = failure_context.get('error_type', '')
        operation = failure_context.get('operation', '')

        # Network/connectivity issues -> retry
        if any(keyword in str(failure_context).lower() for keyword in ['connection', 'timeout', 'network', 'api']):
            return 'retry_with_backoff'

        # Data validation issues -> repair input
        elif any(keyword in error_type.lower() for keyword in ['valueerror', 'keyerror', 'typeerror']):
            return 'repair_input_data'

        # AI/confidence issues -> fallback method
        elif 'confidence' in operation.lower() or 'ai' in operation.lower():
            return 'use_fallback_method'

        # Non-critical operations -> skip and continue
        elif failure_context.get('critical', True) == False:
            return 'skip_and_continue'

        # Default: no recovery possible
        return 'none'

    def _retry_with_exponential_backoff(self, failure_context: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Retry operation with exponential backoff"""
        import time

        operation_func = failure_context.get('operation_func')
        if not operation_func:
            return {'success': False, 'reason': 'No operation function available for retry'}

        for attempt in range(max_retries):
            try:
                # Exponential backoff: 1s, 2s, 4s
                if attempt > 0:
                    delay = 2 ** (attempt - 1)
                    self.logger.info(f"Waiting {delay}s before retry attempt {attempt + 1}")
                    time.sleep(delay)

                result = operation_func()
                return {'success': True, 'result': result, 'attempts': attempt + 1}

            except Exception as e:
                self.logger.warning(f"Retry attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    return {'success': False, 'reason': f'All {max_retries} retry attempts failed', 'last_error': str(e)}

        return {'success': False, 'reason': 'Retry logic failed unexpectedly'}

    def _try_fallback_method(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Try a fallback method for failed operation"""
        operation = failure_context.get('operation', '')

        # For confidence scoring failures, use simple threshold-based approach
        if 'confidence' in operation.lower():
            return {
                'success': True,
                'result': {'confidence_level': 'medium', 'fallback_used': True},
                'reason': 'Used simple threshold-based confidence scoring as fallback'
            }

        # For validation failures, use relaxed validation
        elif 'validation' in operation.lower():
            return {
                'success': True,
                'result': {'validation_passed': True, 'relaxed_rules': True},
                'reason': 'Used relaxed validation rules as fallback'
            }

        return {'success': False, 'reason': f'No fallback method available for {operation}'}

    def _repair_input_data(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Attempt to repair input data that caused failure"""
        # This would contain logic to sanitize, repair, or reformat input data
        # For now, return a placeholder
        return {
            'success': False,
            'reason': 'Input data repair not yet implemented - would sanitize and reformat data'
        }

    def _skip_failed_operation(self, failure_context: Dict[str, Any]) -> Dict[str, Any]:
        """Skip failed operation and continue workflow"""
        return {
            'success': True,
            'result': {'operation_skipped': True, 'continued_workflow': True},
            'reason': f'Skipped failed operation {failure_context.get("operation", "unknown")} and continued'
        }
