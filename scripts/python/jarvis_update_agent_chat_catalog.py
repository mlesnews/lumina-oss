#!/usr/bin/env python3
"""
JARVIS Update Agent Chat Catalog
Uses existing Dewey Decimal Chat Catalog to keep agent chat session titles updated

@JARVIS @DEWEY @CATALOG @AGENT_CHAT_SESSIONS @EXISTING_INFRASTRUCTURE
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Use existing infrastructure - no new code generation
from scripts.python.dewey_decimal_chat_catalog import DeweyDecimalChatCatalog

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISUpdateCatalog")


def update_agent_chat_catalog():
    """Update agent chat session catalog using existing Dewey Decimal system"""
    logger.info("=" * 70)
    logger.info("📚 UPDATING AGENT CHAT SESSION CATALOG")
    logger.info("   Using existing Dewey Decimal Chat Catalog")
    logger.info("=" * 70)
    logger.info("")

    # Use existing infrastructure
    catalog = DeweyDecimalChatCatalog()

    # Scan and catalog all sessions
    logger.info("🔍 Scanning and cataloging agent chat sessions...")
    result = catalog.scan_and_catalog_sessions()

    logger.info("")
    logger.info("=" * 70)
    logger.info("✅ CATALOG UPDATE COMPLETE")
    logger.info("=" * 70)
    logger.info(f"Sessions found: {result['sessions_found']}")
    logger.info(f"Sessions cataloged: {result['sessions_cataloged']}")
    logger.info(f"Total catalog entries: {result['total_catalog_entries']}")
    logger.info("")

    # Generate report
    report = catalog.generate_catalog_report()
    logger.info("📊 CATALOG SUMMARY:")
    logger.info(f"   Total entries: {report['total_entries']}")
    logger.info(f"   Categories: {len(report['categories'])}")
    logger.info("")
    logger.info("   Top categories:")
    for category, count in sorted(report['categories'].items(), key=lambda x: x[1], reverse=True)[:10]:
        logger.info(f"      {category}: {count}")
    logger.info("")

    logger.info("=" * 70)
    logger.info("✅ WORKING TITLES UPDATED IN CARD CATALOG")
    logger.info("=" * 70)

    return {
        "success": True,
        "result": result,
        "report": report
    }


if __name__ == "__main__":
    print("=" * 70)
    print("📚 UPDATE AGENT CHAT SESSION CATALOG")
    print("   Using existing Dewey Decimal Chat Catalog")
    print("=" * 70)
    print()

    result = update_agent_chat_catalog()

    print()
    print("=" * 70)
    print("✅ CATALOG UPDATED")
    print("=" * 70)
    print(f"Sessions cataloged: {result['result']['sessions_cataloged']}")
    print(f"Total entries: {result['report']['total_entries']}")
    print("=" * 70)
