"""
@v3 Verification Logic
Workflow validation and verification system for astromech droids (R2-D2, R5-D4)

Always part of global workflow - runs before main workflow execution
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

try:
    from lumina_core.logging import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("V3Verification")
else:
    logger = get_logger("V3Verification")


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class VerificationResult:
    """Result of a verification step"""
    step_name: str
    passed: bool
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class V3VerificationConfig:
    """V3 verification configuration"""
    enabled: bool = True
    auto_verify: bool = True
    verification_required: bool = True
    fail_on_error: bool = True
    log_verification: bool = True
    verification_log_path: Optional[Path] = None


class V3Verification:
    """
    @v3 Verification Logic

    Always part of global workflow - runs before main workflow execution.
    Provides verification and validation for astromech droid operations.
    """

    def __init__(self, config: Optional[V3VerificationConfig] = None):
        """
        Initialize V3 verification system

        Args:
            config: Optional V3VerificationConfig instance
        """
        self.config = config or V3VerificationConfig()
        self.verification_results: List[VerificationResult] = []

        if self.config.verification_log_path:
            self.config.verification_log_path.parent.mkdir(parents=True, exist_ok=True)

        logger.info("@v3 Verification Logic initialized")
        logger.info(f"Auto-verify: {self.config.auto_verify}")
        logger.info(f"Verification required: {self.config.verification_required}")

    def verify_workflow_preconditions(self, workflow_data: Dict[str, Any]) -> VerificationResult:
        """
        Verify workflow preconditions before execution

        Args:
            workflow_data: Workflow data to verify

        Returns:
            VerificationResult
        """
        step_name = "pre_workflow_verification"
        details = {}
        issues = []

        # Check required fields
        required_fields = ["workflow_id", "workflow_name"]
        for field in required_fields:
            if field not in workflow_data:
                issues.append(f"Missing required field: {field}")
            else:
                details[field] = workflow_data[field]

        # Verify workflow structure
        if "steps" in workflow_data:
            if not isinstance(workflow_data["steps"], list):
                issues.append("Workflow steps must be a list")
            else:
                details["step_count"] = len(workflow_data["steps"])

        # Check for valid configuration
        if "config" in workflow_data:
            details["has_config"] = True

        passed = len(issues) == 0
        message = "Pre-workflow verification passed" if passed else f"Pre-workflow verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def verify_data_integrity(self, data: Any, data_type: str = "generic") -> VerificationResult:
        """
        Verify data integrity

        Args:
            data: Data to verify
            data_type: Type of data being verified

        Returns:
            VerificationResult
        """
        step_name = f"data_integrity_verification_{data_type}"
        details = {"data_type": data_type}
        issues = []

        # Check if data exists
        if data is None:
            issues.append("Data is None")
        else:
            details["data_exists"] = True

            # Check data type
            if isinstance(data, dict):
                details["data_structure"] = "dict"
                details["key_count"] = len(data)
            elif isinstance(data, list):
                details["data_structure"] = "list"
                details["item_count"] = len(data)
            elif isinstance(data, str):
                details["data_structure"] = "string"
                details["length"] = len(data)
            else:
                details["data_structure"] = type(data).__name__

        passed = len(issues) == 0
        message = f"Data integrity verification passed for {data_type}" if passed else f"Data integrity verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def verify_aggregation_preconditions(self, session_data: List[Dict[str, Any]]) -> VerificationResult:
        """
        Verify preconditions before aggregation (R5 specific)

        Args:
            session_data: List of session data to verify

        Returns:
            VerificationResult
        """
        step_name = "pre_aggregation_verification"
        details = {}
        issues = []

        # Verify session data is a list
        if not isinstance(session_data, list):
            issues.append("Session data must be a list")
        else:
            details["session_count"] = len(session_data)

            # Verify each session has required fields
            required_session_fields = ["session_id", "timestamp", "messages"]
            valid_sessions = 0

            for i, session in enumerate(session_data):
                session_valid = True
                for field in required_session_fields:
                    if field not in session:
                        issues.append(f"Session {i} missing field: {field}")
                        session_valid = False

                if session_valid:
                    valid_sessions += 1
                    # Verify messages is a list
                    if not isinstance(session.get("messages"), list):
                        issues.append(f"Session {i} messages must be a list")
                    else:
                        details[f"session_{i}_message_count"] = len(session["messages"])

            details["valid_sessions"] = valid_sessions
            details["invalid_sessions"] = len(session_data) - valid_sessions

        passed = len(issues) == 0
        message = f"Pre-aggregation verification passed ({details.get('valid_sessions', 0)} valid sessions)" if passed else f"Pre-aggregation verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def verify_aggregation_results(self, aggregated_data: Dict[str, Any]) -> VerificationResult:
        """
        Verify aggregation results completeness (R5 specific)

        Args:
            aggregated_data: Aggregated data to verify

        Returns:
            VerificationResult
        """
        step_name = "post_aggregation_verification"
        details = {}
        issues = []

        # Verify required fields in aggregated data
        required_fields = ["total_sessions", "total_messages", "last_updated"]
        for field in required_fields:
            if field not in aggregated_data:
                issues.append(f"Missing aggregated field: {field}")
            else:
                details[field] = aggregated_data[field]

        # Verify data consistency
        if "sessions" in aggregated_data:
            session_count = len(aggregated_data["sessions"])
            if "total_sessions" in aggregated_data:
                if session_count > aggregated_data["total_sessions"]:
                    issues.append(f"Session count mismatch: {session_count} > {aggregated_data['total_sessions']}")
                else:
                    details["session_count_consistent"] = True

        # Verify patterns if present
        if "peak_patterns" in aggregated_data:
            patterns = aggregated_data["peak_patterns"]
            if isinstance(patterns, list):
                details["pattern_count"] = len(patterns)
            else:
                issues.append("peak_patterns must be a list")

        passed = len(issues) == 0
        message = "Post-aggregation verification passed" if passed else f"Post-aggregation verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def verify_pattern_extraction(self, patterns: List[str]) -> VerificationResult:
        """
        Verify @PEAK patterns are valid and extractable (R5 specific)

        Args:
            patterns: List of patterns to verify

        Returns:
            VerificationResult
        """
        step_name = "pattern_extraction_verification"
        details = {}
        issues = []

        # Verify patterns is a list
        if not isinstance(patterns, list):
            issues.append("Patterns must be a list")
        else:
            details["pattern_count"] = len(patterns)

            # Verify each pattern
            valid_patterns = 0
            for i, pattern in enumerate(patterns):
                if not isinstance(pattern, str):
                    issues.append(f"Pattern {i} must be a string")
                elif len(pattern.strip()) == 0:
                    issues.append(f"Pattern {i} is empty")
                else:
                    valid_patterns += 1
                    # Check for @PEAK indicator
                    if "@PEAK" in pattern.upper() or "@peak" in pattern:
                        details[f"pattern_{i}_has_peak_indicator"] = True

            details["valid_patterns"] = valid_patterns
            details["invalid_patterns"] = len(patterns) - valid_patterns

        passed = len(issues) == 0
        message = f"Pattern extraction verification passed ({details.get('valid_patterns', 0)} valid patterns)" if passed else f"Pattern extraction verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def verify_matrix_generation(self, matrix_file: Path) -> VerificationResult:
        """
        Verify living context matrix is generated correctly (R5 specific)

        Args:
            matrix_file: Path to generated matrix file

        Returns:
            VerificationResult
        """
        step_name = "matrix_generation_verification"
        details = {}
        issues = []

        # Verify file exists
        if not matrix_file.exists():
            issues.append(f"Matrix file does not exist: {matrix_file}")
        else:
            details["file_exists"] = True
            details["file_size"] = matrix_file.stat().st_size

            # Verify file is readable
            try:
                with open(matrix_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    details["content_length"] = len(content)

                    # Verify content has expected sections
                    expected_sections = ["R5 Living Context Matrix", "@PEAK Patterns"]
                    for section in expected_sections:
                        if section in content:
                            details[f"has_{section.lower().replace(' ', '_')}"] = True
                        else:
                            issues.append(f"Missing expected section: {section}")
            except Exception as e:
                issues.append(f"Error reading matrix file: {e}")

        passed = len(issues) == 0
        message = "Matrix generation verification passed" if passed else f"Matrix generation verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def verify_technical_operation(self, operation_data: Dict[str, Any]) -> VerificationResult:
        """
        Verify technical operation (R2-D2 specific)

        Args:
            operation_data: Technical operation data to verify

        Returns:
            VerificationResult
        """
        step_name = "technical_operation_verification"
        details = {}
        issues = []

        # Verify operation type
        if "operation_type" not in operation_data:
            issues.append("Missing operation_type")
        else:
            details["operation_type"] = operation_data["operation_type"]

        # Verify operation parameters
        if "parameters" in operation_data:
            if not isinstance(operation_data["parameters"], dict):
                issues.append("Parameters must be a dictionary")
            else:
                details["parameter_count"] = len(operation_data["parameters"])

        # Verify system access if required
        if operation_data.get("requires_system_access", False):
            details["system_access_required"] = True
            # Additional verification for system access operations

        passed = len(issues) == 0
        message = "Technical operation verification passed" if passed else f"Technical operation verification failed: {', '.join(issues)}"

        result = VerificationResult(
            step_name=step_name,
            passed=passed,
            message=message,
            details=details
        )

        self.verification_results.append(result)
        return result

    def run_full_verification(self, workflow_data: Dict[str, Any]) -> Tuple[bool, List[VerificationResult]]:
        """
        Run full verification suite

        Args:
            workflow_data: Workflow data to verify

        Returns:
            Tuple of (all_passed, results)
        """
        logger.info("Running @v3 full verification suite...")

        # Pre-workflow verification
        pre_result = self.verify_workflow_preconditions(workflow_data)

        # Data integrity verification
        data_result = self.verify_data_integrity(workflow_data, "workflow")

        # Check if all passed
        all_passed = pre_result.passed and data_result.passed

        if self.config.log_verification:
            self._log_verification_results()

        logger.info(f"@v3 verification complete: {'PASSED' if all_passed else 'FAILED'}")

        return all_passed, self.verification_results

    def _log_verification_results(self) -> None:
        """Log verification results to file"""
        if not self.config.verification_log_path:
            return

        log_data = {
            "verification_run": datetime.now().isoformat(),
            "results": [
                {
                    "step": r.step_name,
                    "passed": r.passed,
                    "message": r.message,
                    "details": r.details,
                    "timestamp": r.timestamp.isoformat()
                }
                for r in self.verification_results
            ],
            "summary": {
                "total_steps": len(self.verification_results),
                "passed": sum(1 for r in self.verification_results if r.passed),
                "failed": sum(1 for r in self.verification_results if not r.passed)
            }
        }

        try:
            with open(self.config.verification_log_path, 'a') as f:
                json.dump(log_data, f, indent=2)
                f.write("\n")
        except Exception as e:
            logger.warning(f"Failed to log verification results: {e}")

    def get_verification_summary(self) -> Dict[str, Any]:
        """Get summary of verification results"""
        return {
            "total_verifications": len(self.verification_results),
            "passed": sum(1 for r in self.verification_results if r.passed),
            "failed": sum(1 for r in self.verification_results if not r.passed),
            "results": [
                {
                    "step": r.step_name,
                    "passed": r.passed,
                    "message": r.message
                }
                for r in self.verification_results
            ]
        }


def verify_workflow(workflow_data: Dict[str, Any], config: Optional[V3VerificationConfig] = None) -> Tuple[bool, List[VerificationResult]]:
    """
    Convenience function to verify a workflow

    Args:
        workflow_data: Workflow data to verify
        config: Optional V3VerificationConfig

    Returns:
        Tuple of (all_passed, results)
    """
    verifier = V3Verification(config)
    return verifier.run_full_verification(workflow_data)


def verify_workflow_with_droid_actor(workflow_data: Dict[str, Any], project_root: Optional[Path] = None) -> Tuple[bool, Dict[str, Any]]:
    """
    Verify workflow using smart droid actor selection (recommended)

    Args:
        workflow_data: Workflow data to verify
        project_root: Optional project root path

    Returns:
        Tuple of (verification_passed, verification_results with droid assignment)
    """
    try:
        from droid_actor_system import verify_workflow_with_droid_actor as droid_verify
        return droid_verify(workflow_data, project_root)
    except ImportError:
        logger.warning("droid_actor_system not available, using standard verification")
        verifier = V3Verification()
        passed, results = verifier.run_full_verification(workflow_data)
        return passed, {"verification_results": results}


if __name__ == "__main__":
    # Example usage
    test_workflow = {
        "workflow_id": "test_workflow",
        "workflow_name": "Test Workflow",
        "steps": [
            {"step": 1, "action": "test"}
        ],
        "config": {}
    }

    verifier = V3Verification()
    passed, results = verifier.run_full_verification(test_workflow)

    print(f"Verification {'PASSED' if passed else 'FAILED'}")
    for result in results:
        print(f"  {result.step_name}: {result.message}")

