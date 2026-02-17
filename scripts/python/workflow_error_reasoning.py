"""
Workflow Error Reasoning Mixin
Provides comprehensive error reasoning and validation for workflows.
"""

from typing import Dict, Any, List
from datetime import datetime
import traceback
import logging


class WorkflowErrorReasoningMixin:
    """Mixin class providing error reasoning capabilities"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not hasattr(self, 'logger'):
            self.logger = logging.getLogger(self.__class__.__name__)

    def execute_with_error_reasoning(self, operation_func, context: str = "") -> Dict[str, Any]:
        """
        Execute operation with comprehensive error handling and reasoning.

        Unlike silent failures, this provides detailed reasoning for any issues.

        Args:
            operation_func: Function to execute
            context: Context information for error reporting

        Returns:
            Dict with result, success status, and detailed reasoning
        """
        operation_name = getattr(operation_func, '__name__', 'unknown_operation')

        try:
            self.logger.info(f"🔄 Executing {operation_name} with error reasoning...")

            # Pre-execution validation
            validation_result = self._validate_operation_prerequisites(operation_func, context)
            if not validation_result['can_proceed']:
                return {
                    'success': False,
                    'reasoning': f"Pre-execution validation failed: {validation_result['reason']}",
                    'validation_details': validation_result,
                    'error_category': 'validation_failure',
                    'context': context,
                    'timestamp': datetime.now().isoformat()
                }

            # Execute operation
            result = operation_func()

            # Post-execution validation
            post_validation = self._validate_operation_result(result, context)
            if not post_validation['is_valid']:
                return {
                    'success': False,
                    'reasoning': f"Post-execution validation failed: {post_validation['reason']}",
                    'result': result,
                    'validation_details': post_validation,
                    'error_category': 'post_validation_failure',
                    'context': context,
                    'timestamp': datetime.now().isoformat()
                }

            # Success
            return {
                'success': True,
                'result': result,
                'reasoning': f"Operation {operation_name} completed successfully with all validations passed",
                'validation_details': post_validation,
                'context': context,
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            error_details = {
                'exception_type': type(e).__name__,
                'exception_message': str(e),
                'stack_trace': traceback.format_exc(),
                'context': context,
                'operation_name': operation_name,
                'timestamp': datetime.now().isoformat()
            }

            self.logger.error(f"❌ Operation {operation_name} failed with reasoning", extra=error_details)

            return {
                'success': False,
                'reasoning': self._generate_error_reasoning(error_details),
                'error_details': error_details,
                'error_category': 'execution_failure',
                'recovery_suggestions': self._generate_recovery_suggestions(error_details),
                'context': context,
                'timestamp': datetime.now().isoformat()
            }

    def _validate_operation_prerequisites(self, operation_func, context: str) -> Dict[str, Any]:
        """Validate prerequisites before operation execution"""
        operation_name = getattr(operation_func, '__name__', 'unknown')

        validations = []

        # Check if required dependencies are available
        if operation_name == 'analyze_llm_output_safety':
            if not hasattr(self, 'confidence_scorer') or self.confidence_scorer is None:
                validations.append({
                    'check': 'confidence_scorer_available',
                    'passed': False,
                    'reason': 'Confidence scorer not initialized'
                })

        # Check workflow state
        if hasattr(self, 'step_tracker') and self.step_tracker:
            current_step = getattr(self.step_tracker, 'current_step', 0)
            total_steps = getattr(self, 'total_steps', 0)
            if current_step >= total_steps:
                validations.append({
                    'check': 'workflow_not_complete',
                    'passed': False,
                    'reason': f'Workflow already completed ({current_step}/{total_steps})'
                })

        can_proceed = all(v.get('passed', True) for v in validations)
        reason = "; ".join([v['reason'] for v in validations if not v.get('passed', True)]) if not can_proceed else "All prerequisites met"

        return {
            'can_proceed': can_proceed,
            'reason': reason,
            'validations': validations
        }

    def _validate_operation_result(self, result, context: str) -> Dict[str, Any]:
        """Validate operation result after execution"""
        validations = []

        # Check result structure
        if not isinstance(result, dict):
            validations.append({
                'check': 'result_structure',
                'passed': False,
                'reason': f'Result should be dict, got {type(result).__name__}'
            })

        # Check for required result fields
        if isinstance(result, dict):
            if 'success' not in result:
                validations.append({
                    'check': 'result_has_success',
                    'passed': False,
                    'reason': 'Result missing required "success" field'
                })

            if 'reasoning' not in result:
                validations.append({
                    'check': 'result_has_reasoning',
                    'passed': False,
                    'reason': 'Result missing required "reasoning" field'
                })

        # Context-specific validations
        if context and isinstance(result, dict):
            if 'llm_response' in result and len(str(result.get('llm_response', ''))) == 0:
                validations.append({
                    'check': 'llm_response_not_empty',
                    'passed': False,
                    'reason': 'LLM response is empty'
                })

        is_valid = all(v.get('passed', True) for v in validations)
        reason = "; ".join([v['reason'] for v in validations if not v.get('passed', True)]) if not is_valid else "All validations passed"

        return {
            'is_valid': is_valid,
            'reason': reason,
            'validations': validations
        }

    def _generate_error_reasoning(self, error_details: Dict[str, Any]) -> str:
        """Generate human-readable reasoning for errors"""
        exception_type = error_details.get('exception_type', 'Unknown')
        exception_message = error_details.get('exception_message', 'No message')
        operation_name = error_details.get('operation_name', 'unknown operation')
        context = error_details.get('context', '')

        reasoning = f"Operation '{operation_name}' failed with {exception_type}: {exception_message}"

        if context:
            reasoning += f" (Context: {context})"

        # Add specific guidance based on error type
        if 'ImportError' in exception_type:
            reasoning += ". This suggests a missing dependency or module not installed."
        elif 'KeyError' in exception_type:
            reasoning += ". This suggests code is trying to access a dictionary key that doesn't exist."
        elif 'AttributeError' in exception_type:
            reasoning += ". This suggests code is trying to access an attribute or method that doesn't exist."
        elif 'TypeError' in exception_type:
            reasoning += ". This suggests a type mismatch or incorrect function call."
        elif 'ValueError' in exception_type:
            reasoning += ". This suggests invalid data or parameter values."

        return reasoning

    def _generate_recovery_suggestions(self, error_details: Dict[str, Any]) -> List[str]:
        """Generate recovery suggestions based on error details"""
        suggestions = []

        exception_type = error_details.get('exception_type', '')
        exception_message = error_details.get('exception_message', '')
        operation_name = error_details.get('operation_name', '')

        # General suggestions
        suggestions.append("Check system logs for additional error details")
        suggestions.append("Verify all required dependencies are installed")
        suggestions.append("Ensure configuration files are properly formatted")

        # Specific suggestions based on error type
        if 'ImportError' in exception_type:
            suggestions.insert(0, f"Install missing module mentioned in error: pip install {exception_message.split()[-1] if 'No module named' in exception_message else 'unknown'}")
        elif 'KeyError' in exception_type:
            suggestions.insert(0, f"Check that required data keys are present in input data")
        elif 'confidence' in operation_name.lower():
            suggestions.insert(0, f"Verify confidence scorer is properly initialized")
        elif 'llm' in operation_name.lower():
            suggestions.insert(0, f"Check LLM service availability and API keys")

        return suggestions
