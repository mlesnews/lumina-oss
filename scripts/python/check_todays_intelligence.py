#!/usr/bin/env python3
"""
Check Today's Intelligence Gathered

Checks for intelligence gathered today from:
- Email accounts
- SMS
- Social-news-education (white papers & thesis)
- All @sources

Tags: #INTELLIGENCE #EMAIL #SMS #SOURCES #CHECK @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, date
from typing import Dict, List, Any

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

logger = get_logger("CheckTodaysIntelligence")

# Import systems
try:
    from syphon_source_sweeps_scans import SyphonSourceSweepsScans
    SWEEPS_SCANS_AVAILABLE = True
except ImportError:
    SWEEPS_SCANS_AVAILABLE = False
    logger.warning("SYPHON Source Sweeps & Scans not available")

try:
    from unified_queue_adapter import UnifiedQueueAdapter
    UNIFIED_QUEUE_AVAILABLE = True
except ImportError:
    UNIFIED_QUEUE_AVAILABLE = False
    logger.warning("Unified Queue Adapter not available")


def check_todays_intelligence() -> Dict[str, Any]:
    """Check intelligence gathered today"""
    today = date.today()
    today_str = today.isoformat()

    result = {
        "date": today_str,
        "email_intelligence": [],
        "sms_intelligence": [],
        "social_news_education_intelligence": [],
        "all_sources_intelligence": [],
        "total_intelligence": 0,
        "sources_checked": []
    }

    # Check SYPHON Source Sweeps & Scans
    if SWEEPS_SCANS_AVAILABLE:
        try:
            sweeps_scans = SyphonSourceSweepsScans()

            # Get scans from today
            scans_today = [
                scan for scan in sweeps_scans.scan_history
                if scan.timestamp.date() == today
            ]

            for scan in scans_today:
                source_name = scan.source_name.lower()

                # Email intelligence
                if "email" in source_name:
                    result["email_intelligence"].append({
                        "source": scan.source_name,
                        "intelligence_extracted": scan.intelligence_extracted,
                        "items_found": scan.items_found,
                        "timestamp": scan.timestamp.isoformat(),
                        "duplicates_skipped": scan.metadata.get("duplicates_skipped", 0),
                        "updates_found": scan.metadata.get("updates_found", 0)
                    })

                # SMS intelligence
                elif "sms" in source_name:
                    result["sms_intelligence"].append({
                        "source": scan.source_name,
                        "intelligence_extracted": scan.intelligence_extracted,
                        "items_found": scan.items_found,
                        "timestamp": scan.timestamp.isoformat(),
                        "duplicates_skipped": scan.metadata.get("duplicates_skipped", 0),
                        "updates_found": scan.metadata.get("updates_found", 0)
                    })

                # Social-news-education intelligence
                elif any(term in source_name for term in ["social", "news", "education", "documentation", "holocron"]):
                    result["social_news_education_intelligence"].append({
                        "source": scan.source_name,
                        "intelligence_extracted": scan.intelligence_extracted,
                        "items_found": scan.items_found,
                        "timestamp": scan.timestamp.isoformat(),
                        "duplicates_skipped": scan.metadata.get("duplicates_skipped", 0),
                        "updates_found": scan.metadata.get("updates_found", 0)
                    })

                # All sources
                result["all_sources_intelligence"].append({
                    "source": scan.source_name,
                    "intelligence_extracted": scan.intelligence_extracted,
                    "items_found": scan.items_found,
                    "timestamp": scan.timestamp.isoformat()
                })

            result["total_intelligence"] = sum(scan.intelligence_extracted for scan in scans_today)
            result["sources_checked"] = [scan.source_name for scan in scans_today]

        except Exception as e:
            logger.error(f"Error checking sweeps/scans: {e}")

    # Check Unified Queue for today's items
    if UNIFIED_QUEUE_AVAILABLE:
        try:
            queue_adapter = UnifiedQueueAdapter(project_root)

            # Get items from today
            today_items = []
            for item in queue_adapter.queue_items.values():
                if item.created_at:
                    try:
                        item_date = datetime.fromisoformat(item.created_at.replace('Z', '+00:00')).date()
                        if item_date == today:
                            today_items.append({
                                "item_id": item.item_id,
                                "type": item.item_type.value,
                                "title": item.title,
                                "status": item.status.value,
                                "priority": item.priority,
                                "created_at": item.created_at
                            })
                    except:
                        pass

            result["queue_items_today"] = today_items
            result["queue_items_count"] = len(today_items)

        except Exception as e:
            logger.error(f"Error checking unified queue: {e}")

    # Check data directories for today's files
    data_dir = project_root / "data"

    # Email syphon data
    email_dir = data_dir / "email_syphon"
    if email_dir.exists():
        email_files_today = [
            f.name for f in email_dir.iterdir()
            if f.is_file() and today_str in f.name
        ]
        result["email_files_today"] = email_files_today

    # SMS syphon data
    sms_dir = data_dir / "sms_syphon"
    if sms_dir.exists():
        sms_files_today = [
            f.name for f in sms_dir.iterdir()
            if f.is_file() and today_str in f.name
        ]
        result["sms_files_today"] = sms_files_today

    # Holocron data (documentation/education)
    holocron_dir = data_dir / "holocron"
    if holocron_dir.exists():
        holocron_files_today = [
            f.name for f in holocron_dir.rglob("*")
            if f.is_file() and today_str in f.name
        ]
        result["holocron_files_today"] = holocron_files_today

    return result


def main():
    """Main execution"""
    logger.info("="*80)
    logger.info("📊 CHECKING TODAY'S INTELLIGENCE")
    logger.info("="*80)
    logger.info("")

    result = check_todays_intelligence()

    # Email Intelligence
    logger.info("📧 EMAIL INTELLIGENCE")
    logger.info("-"*80)
    if result["email_intelligence"]:
        total_email = sum(e["intelligence_extracted"] for e in result["email_intelligence"])
        logger.info(f"   Sources: {len(result['email_intelligence'])}")
        logger.info(f"   Total Intelligence: {total_email}")
        for email in result["email_intelligence"]:
            logger.info(f"   • {email['source']}: {email['intelligence_extracted']} intelligence")
            if email.get("duplicates_skipped", 0) > 0:
                logger.info(f"     ⏭️  Skipped {email['duplicates_skipped']} duplicates")
            if email.get("updates_found", 0) > 0:
                logger.info(f"     ✅ Found {email['updates_found']} updates")
    else:
        logger.info("   ⚠️  No email intelligence gathered today")
    logger.info("")

    # SMS Intelligence
    logger.info("📱 SMS INTELLIGENCE")
    logger.info("-"*80)
    if result["sms_intelligence"]:
        total_sms = sum(s["intelligence_extracted"] for s in result["sms_intelligence"])
        logger.info(f"   Sources: {len(result['sms_intelligence'])}")
        logger.info(f"   Total Intelligence: {total_sms}")
        for sms in result["sms_intelligence"]:
            logger.info(f"   • {sms['source']}: {sms['intelligence_extracted']} intelligence")
            if sms.get("duplicates_skipped", 0) > 0:
                logger.info(f"     ⏭️  Skipped {sms['duplicates_skipped']} duplicates")
            if sms.get("updates_found", 0) > 0:
                logger.info(f"     ✅ Found {sms['updates_found']} updates")
    else:
        logger.info("   ⚠️  No SMS intelligence gathered today")
    logger.info("")

    # Social-News-Education Intelligence
    logger.info("📚 SOCIAL-NEWS-EDUCATION INTELLIGENCE")
    logger.info("-"*80)
    if result["social_news_education_intelligence"]:
        total_social = sum(s["intelligence_extracted"] for s in result["social_news_education_intelligence"])
        logger.info(f"   Sources: {len(result['social_news_education_intelligence'])}")
        logger.info(f"   Total Intelligence: {total_social}")
        for social in result["social_news_education_intelligence"]:
            logger.info(f"   • {social['source']}: {social['intelligence_extracted']} intelligence")
            if social.get("duplicates_skipped", 0) > 0:
                logger.info(f"     ⏭️  Skipped {social['duplicates_skipped']} duplicates")
            if social.get("updates_found", 0) > 0:
                logger.info(f"     ✅ Found {social['updates_found']} updates")
    else:
        logger.info("   ⚠️  No social-news-education intelligence gathered today")
    logger.info("")

    # All Sources Summary
    logger.info("📊 ALL SOURCES SUMMARY")
    logger.info("-"*80)
    logger.info(f"   Total Intelligence Today: {result['total_intelligence']}")
    logger.info(f"   Sources Checked: {len(result['sources_checked'])}")
    if result.get("queue_items_count", 0) > 0:
        logger.info(f"   Queue Items Today: {result['queue_items_count']}")
    logger.info("")

    # Files Found
    if result.get("email_files_today"):
        logger.info(f"   📧 Email Files: {len(result['email_files_today'])}")
    if result.get("sms_files_today"):
        logger.info(f"   📱 SMS Files: {len(result['sms_files_today'])}")
    if result.get("holocron_files_today"):
        logger.info(f"   🗄️  Holocron Files: {len(result['holocron_files_today'])}")

    logger.info("")
    logger.info("="*80)
    logger.info("✅ TODAY'S INTELLIGENCE CHECK COMPLETE")
    logger.info("="*80)

    return result


if __name__ == "__main__":


    main()