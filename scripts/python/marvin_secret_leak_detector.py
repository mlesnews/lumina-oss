#!/usr/bin/env python3
"""
MARVIN Secret Leak Detector
Real-time monitoring for secrets exposed in logs, outputs, and commands

MARVIN's job: Catch secrets BEFORE they're exposed

Tags: #MARVIN #SECURITY #SECRETS #LEAK_DETECTION @MARVIN @SECURITY
"""

import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from secret_masker import mask_secret, mask_api_key
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    # Fallback masker
    def mask_secret(text: str) -> str:
        return re.sub(r'sk_[a-zA-Z0-9]{20,}', lambda m: f"sk_{'*' * (len(m.group()) - 3)}", text)
    def mask_api_key(key: str) -> str:
        return f"{key[:3]}***...***{key[-4:]}" if len(key) > 7 else "***REDACTED***"

logger = get_logger("MARVINSecretLeakDetector")

# Secret patterns (expanded)
SECRET_PATTERNS = [
    (r'sk_[a-zA-Z0-9]{20,}', 'ElevenLabs/Stripe API Key'),
    (r'[a-f0-9]{40,}', 'SHA256/Hex Key'),
    (r'eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+', 'JWT Token'),
    (r'[A-Za-z0-9]{32,}', 'Generic Long Token'),
    (r'-----BEGIN.*PRIVATE KEY-----', 'Private Key'),
    (r'password\s*[:=]\s*[^\s]+', 'Password in Clear'),
    (r'api[_-]?key\s*[:=]\s*["\']?[a-zA-Z0-9]{20,}', 'API Key Pattern'),
]


class MARVINSecretLeakDetector:
    """
    MARVIN: Security Specialist - Secret Leak Detection

    Real-time monitoring to catch secrets BEFORE they're exposed
    """

    def __init__(self):
        self.logger = logger
        self.violations: List[Dict[str, Any]] = []
        self.enabled = True

        self.logger.info("🔒 MARVIN Secret Leak Detector initialized")
        self.logger.info("   ⚠️  CRITICAL SECURITY MONITORING ACTIVE")

    def scan_text(self, text: str, source: str = "unknown") -> List[Dict[str, Any]]:
        """
        Scan text for exposed secrets

        Returns:
            List of violations found
        """
        if not self.enabled or not text:
            return []

        violations = []

        for pattern, secret_type in SECRET_PATTERNS:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                secret_value = match.group()
                violation = {
                    "type": secret_type,
                    "pattern": pattern,
                    "value_preview": mask_api_key(secret_value),
                    "full_value": secret_value,  # Keep for masking
                    "position": match.span(),
                    "source": source,
                    "severity": "CRITICAL"
                }
                violations.append(violation)

                # Immediate alert
                self.logger.error("=" * 80)
                self.logger.error("🚨 MARVIN SECURITY ALERT: SECRET LEAK DETECTED!")
                self.logger.error("=" * 80)
                self.logger.error(f"   Type: {secret_type}")
                self.logger.error(f"   Source: {source}")
                self.logger.error(f"   Value: {mask_api_key(secret_value)}")
                self.logger.error(f"   Position: {match.span()}")
                self.logger.error("")
                self.logger.error("   ⚠️  SECRET EXPOSED IN THE CLEAR!")
                self.logger.error("   🔒 IMMEDIATE MASKING REQUIRED")
                self.logger.error("=" * 80)

        self.violations.extend(violations)
        return violations

    def scan_command_output(self, command: str, output: str) -> List[Dict[str, Any]]:
        """Scan command output for secrets"""
        return self.scan_text(output, source=f"command: {command}")

    def should_block(self, text: str) -> Tuple[bool, str]:
        """
        Determine if text should be blocked from output

        Returns:
            (should_block, reason)
        """
        violations = self.scan_text(text)
        if violations:
            return True, f"Contains {len(violations)} exposed secret(s)"
        return False, ""

    def mask_and_report(self, text: str, source: str = "unknown") -> str:
        """
        Mask secrets in text and report violations

        Returns:
            Masked text
        """
        violations = self.scan_text(text, source)

        if violations:
            masked_text = mask_secret(text)
            self.logger.error(f"🔒 MARVIN: Masked {len(violations)} secret(s) in {source}")
            return masked_text

        return text

    def get_violation_report(self) -> Dict[str, Any]:
        """Get report of all violations detected"""
        return {
            "total_violations": len(self.violations),
            "violations": [
                {
                    "type": v["type"],
                    "source": v["source"],
                    "severity": v["severity"],
                    "preview": v["value_preview"]
                }
                for v in self.violations
            ],
            "enabled": self.enabled
        }

    def reset_violations(self):
        """Reset violation tracking"""
        self.violations.clear()
        self.logger.info("🔒 MARVIN: Violation tracking reset")


# Global instance
_marvin_detector: Optional[MARVINSecretLeakDetector] = None


def get_marvin_detector() -> MARVINSecretLeakDetector:
    """Get global MARVIN detector instance"""
    global _marvin_detector
    if _marvin_detector is None:
        _marvin_detector = MARVINSecretLeakDetector()
    return _marvin_detector


def marvin_scan_text(text: str, source: str = "unknown") -> str:
    """
    MARVIN wrapper: Scan and mask text

    Returns:
        Masked text if secrets found, original otherwise
    """
    detector = get_marvin_detector()
    return detector.mask_and_report(text, source)


def marvin_should_block(text: str) -> Tuple[bool, str]:
    """MARVIN wrapper: Check if text should be blocked"""
    detector = get_marvin_detector()
    return detector.should_block(text)


if __name__ == "__main__":
    # Test
    detector = MARVINSecretLeakDetector()

    # Test case
    test_output = "API key: sk_191353bd872b59ef42db77c7c593e181c2d91dad7003a603"
    print("Testing MARVIN Secret Leak Detector...")
    print(f"Input: {test_output}")

    masked = detector.mask_and_report(test_output, "test")
    print(f"Output: {masked}")

    report = detector.get_violation_report()
    print(f"\nViolations: {report['total_violations']}")
