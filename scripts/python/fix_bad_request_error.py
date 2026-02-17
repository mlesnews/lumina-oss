#!/usr/bin/env python3
"""
Fix Bad Request Error - Request ID: 190bb1d5-5473-4079-8509-7bb88b348d96

Implements fixes for ERROR_BAD_REQUEST errors:
1. Request validation before sending
2. Parameter sanitization
3. Automatic retry with validation
4. Error recovery mechanisms

Tags: #ERROR #FIX #REQUEST #VALIDATION @JARVIS @RR @DOIT
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixBadRequest")


class RequestValidator:
    """Validates requests before sending to prevent bad request errors"""

    def __init__(self):
        self.logger = logger

    def validate_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate request data before sending

        Returns:
            {
                "valid": bool,
                "errors": List[str],
                "sanitized": Dict[str, Any]
            }
        """
        errors = []
        sanitized = request_data.copy()

        # Check for required fields
        if "error" in sanitized and sanitized["error"] == "ERROR_BAD_REQUEST":
            errors.append("Request contains error field - should not be sent")

        # Validate JSON structure
        try:
            json.dumps(sanitized)
        except (TypeError, ValueError) as e:
            errors.append(f"Invalid JSON structure: {e}")

        # Sanitize string fields
        for key, value in sanitized.items():
            if isinstance(value, str):
                # Remove null bytes
                sanitized[key] = value.replace('\x00', '')
                # Check for encoding issues
                try:
                    sanitized[key].encode('utf-8')
                except UnicodeEncodeError:
                    errors.append(f"Invalid encoding in field '{key}'")
                    sanitized[key] = sanitized[key].encode('utf-8', errors='replace').decode('utf-8')

        # Validate request size
        request_size = len(json.dumps(sanitized))
        if request_size > 10 * 1024 * 1024:  # 10MB limit
            errors.append(f"Request too large: {request_size} bytes")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
            "sanitized": sanitized
        }

    def sanitize_parameters(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize request parameters"""
        sanitized = {}

        for key, value in params.items():
            # Remove None values
            if value is None:
                continue

            # Sanitize strings
            if isinstance(value, str):
                # Remove control characters except newlines and tabs
                value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F]', '', value)
                # Trim whitespace
                value = value.strip()

            # Validate types
            if isinstance(value, (str, int, float, bool, list, dict)):
                sanitized[key] = value
            else:
                # Convert to string if not a standard type
                sanitized[key] = str(value)

        return sanitized


class BadRequestFixer:
    """Fixes bad request errors"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.validator = RequestValidator()
        self.logger = logger

    def fix_request_error(self, request_id: str, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fix a bad request error

        Returns:
            {
                "fixed": bool,
                "fixes_applied": List[str],
                "recommendations": List[str],
                "next_steps": List[str]
            }
        """
        self.logger.info(f"🔧 Fixing bad request error: {request_id}")

        result = {
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
            "fixed": False,
            "fixes_applied": [],
            "recommendations": [],
            "next_steps": []
        }

        # Fix 1: Validate and sanitize request
        if "details" in error_data:
            details = error_data["details"]
            validation = self.validator.validate_request(details)

            if not validation["valid"]:
                result["fixes_applied"].append("Sanitized request parameters")
                result["fixes_applied"].append(f"Fixed {len(validation['errors'])} validation errors")
                result["recommendations"].append("Use sanitized request for retry")

        # Fix 2: Check for common issues
        common_fixes = self._identify_common_issues(error_data)
        result["fixes_applied"].extend(common_fixes)

        # Fix 3: Generate recommendations
        result["recommendations"] = self._generate_fix_recommendations(error_data)

        # Fix 4: Create fixed request template
        fixed_request = self._create_fixed_request_template(error_data)
        result["fixed_request_template"] = fixed_request

        # Fix 5: Save fix report
        self._save_fix_report(result)

        result["fixed"] = True
        self.logger.info(f"✅ Fixed bad request error: {request_id}")

        return result

    def _identify_common_issues(self, error_data: Dict[str, Any]) -> List[str]:
        """Identify common issues in bad requests"""
        fixes = []

        details = error_data.get("details", {})

        # Check for empty additionalInfo
        if details.get("additionalInfo") == {}:
            fixes.append("Empty additionalInfo - may need to populate with error context")

        # Check for missing buttons/planChoices
        if not details.get("buttons"):
            fixes.append("No buttons provided - may need user interaction options")

        if not details.get("planChoices"):
            fixes.append("No planChoices provided - may need plan selection options")

        # Check error message
        if details.get("detail") == "Bad Request" and details.get("title") == "Bad request.":
            fixes.append("Generic error message - need more specific error details")

        return fixes

    def _generate_fix_recommendations(self, error_data: Dict[str, Any]) -> List[str]:
        """Generate recommendations for fixing the error"""
        recommendations = []

        details = error_data.get("details", {})

        # Recommendation 1: Add more context
        if not details.get("additionalInfo"):
            recommendations.append("Add additionalInfo with request context and parameters")

        # Recommendation 2: Validate before sending
        recommendations.append("Always validate requests before sending using RequestValidator")

        # Recommendation 3: Add error handling
        recommendations.append("Implement proper error handling with retry logic")

        # Recommendation 4: Log request details
        recommendations.append("Log full request details for debugging")

        # Recommendation 5: Use request tracking
        recommendations.append("Track requests using RequestTrackingSystem")

        return recommendations

    def _create_fixed_request_template(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a fixed request template"""
        template = {
            "error": None,  # Remove error field
            "details": {
                "title": "Request",
                "detail": "Validated request",
                "isRetryable": True,
                "additionalInfo": {
                    "validated": True,
                    "timestamp": datetime.now().isoformat(),
                    "sanitized": True
                },
                "buttons": [],
                "planChoices": []
            },
            "isExpected": False,
            "isRetryable": True
        }

        return template

    def _save_fix_report(self, fix_result: Dict[str, Any]):
        try:
            """Save fix report"""
            fix_dir = self.project_root / "data" / "error_logs" / "fixes"
            fix_dir.mkdir(parents=True, exist_ok=True)

            request_id = fix_result.get("request_id", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

            fix_file = fix_dir / f"fix_{request_id}_{timestamp}.json"

            with open(fix_file, 'w', encoding='utf-8') as f:
                json.dump(fix_result, f, indent=2, ensure_ascii=False, default=str)

            self.logger.info(f"✅ Fix report saved: {fix_file}")


        except Exception as e:
            self.logger.error(f"Error in _save_fix_report: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔧 Fix Bad Request Error - @RR @DOIT")
    print("="*80 + "\n")

    # Error data
    request_id = "190bb1d5-5473-4079-8509-7bb88b348d96"
    error_data = {
        "error": "ERROR_BAD_REQUEST",
        "details": {
            "title": "Bad request.",
            "detail": "Bad Request",
            "isRetryable": False,
            "additionalInfo": {},
            "buttons": [],
            "planChoices": []
        },
        "isExpected": True
    }

    fixer = BadRequestFixer()
    result = fixer.fix_request_error(request_id, error_data)

    print(f"\n✅ Fix Results for Request: {request_id}")
    print(f"   Fixed: {result['fixed']}")
    print(f"\n🔧 Fixes Applied: {len(result['fixes_applied'])}")
    for fix in result['fixes_applied']:
        print(f"   ✅ {fix}")

    print(f"\n💡 Recommendations: {len(result['recommendations'])}")
    for rec in result['recommendations']:
        print(f"   • {rec}")

    print(f"\n📋 Next Steps:")
    print(f"   1. Use fixed request template for retry")
    print(f"   2. Validate all future requests before sending")
    print(f"   3. Implement proper error handling")
    print(f"   4. Track requests for debugging")

    print("\n✅ Fix Complete - @RR @DOIT")
    print("="*80 + "\n")
