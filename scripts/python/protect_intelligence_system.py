#!/usr/bin/env python3
"""
Protect Intelligence System from Bad Actors

Prevents bad actors from injecting false information into intelligence gathering.
Similar to protecting against compromised news media sources.

Tags: #INTELLIGENCE #SECURITY #BAD_ACTORS #PROTECTION @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from email_intelligence_filter import EmailIntelligenceFilter

logger = get_logger("ProtectIntelligenceSystem")


class IntelligenceSystemProtection:
    """
    Protect Intelligence System from Bad Actors

    Prevents compromised sources from injecting false information into
    intelligence gathering system (like protecting against compromised news media).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize intelligence system protection"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.filter_system = EmailIntelligenceFilter(project_root)

        logger.info("✅ Intelligence System Protection initialized")
        logger.info("   🛡️  Protecting against bad actors and compromised sources")

    def protect_intelligence_gathering(self) -> Dict[str, Any]:
        """
        Protect intelligence gathering system by filtering bad data sources

        Returns:
            Protection results
        """
        logger.info("=" * 80)
        logger.info("🛡️  PROTECTING INTELLIGENCE GATHERING SYSTEM")
        logger.info("=" * 80)
        logger.info("")
        logger.info("   Filtering out:")
        logger.info("   • Advertising emails")
        logger.info("   • Junk mail")
        logger.info("   • Spam")
        logger.info("   • Phishing emails")
        logger.info("   • Compromised sources (bad actors)")
        logger.info("   • False information injection attempts")
        logger.info("")

        # Walk email hub and filter
        results = self.filter_system.walk_email_hub()

        # Protection summary
        protection_summary = {
            "total_emails_scanned": results.total_emails,
            "legitimate_emails": results.wheat_emails,
            "filtered_emails": results.chaff_emails,
            "phishing_blocked": results.phishing,
            "compromised_sources_blocked": sum(
                1 for c in results.classifications if c.is_compromised
            ),
            "protection_status": "active"
        }

        logger.info("")
        logger.info("=" * 80)
        logger.info("🛡️  PROTECTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"✅ Legitimate emails: {protection_summary['legitimate_emails']}")
        logger.info(f"❌ Filtered emails: {protection_summary['filtered_emails']}")
        logger.info(f"🎣 Phishing blocked: {protection_summary['phishing_blocked']}")
        logger.info(f"🚫 Compromised sources blocked: {protection_summary['compromised_sources_blocked']}")
        logger.info("")
        logger.info("✅ Intelligence system protected from bad actors")
        logger.info("=" * 80)

        return protection_summary


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Protect Intelligence System from Bad Actors")

    args = parser.parse_args()

    protection = IntelligenceSystemProtection()
    results = protection.protect_intelligence_gathering()

    logger.info("")
    logger.info("✅ Intelligence system protection complete")
    logger.info("   🛡️  System protected from false information injection")


if __name__ == "__main__":


    main()