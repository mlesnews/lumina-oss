#!/usr/bin/env python3
"""
Save Discussion to HOLOCRON and The Captain's Log

Saves meaningful discussions to:
1. @HOLOCRON - Public knowledge base
2. @SECRET @HOLOCRON - Private blackbox (daily confessional journal, theme: "DO BETTER")
3. THE CAPTAIN'S LOG - Captain's log in respect to Star Trek TOS

Tags: #HOLOCRON #CAPTAINS_LOG #STAR_TREK #TOS #MOONSHOT #MOON #TOTHEMOON #WORDS-WORTH-SAVING
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

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

logger = get_logger("SaveToHolocronAndJournal")


def save_to_holocron(
    title: str,
    content: Dict[str, Any],
    importance_score: int = 100,
    project_root: Optional[Path] = None
) -> str:
    """
    Save to @HOLOCRON (public knowledge base)

    Args:
        title: Entry title
        content: Content dictionary
        importance_score: Importance score (0-100)
        project_root: Project root path

    Returns:
        Holocron ID
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    holocron_dir = project_root / "data" / "holocrons"
    holocron_dir.mkdir(parents=True, exist_ok=True)

    holocron_id = f"HOLO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    holocron_data = {
        "holocron_id": holocron_id,
        "timestamp": datetime.now().isoformat(),
        "importance_score": importance_score,
        "importance_symbol": "⭐⭐⭐⭐⭐" if importance_score >= 80 else "⭐⭐⭐",
        "data": content,
        "category": "philosophy",
        "tags": content.get("tags", [])
    }

    holocron_file = holocron_dir / f"{holocron_id}.json"
    with open(holocron_file, 'w', encoding='utf-8') as f:
        json.dump(holocron_data, f, indent=2)

    logger.info(f"✅ Saved to @HOLOCRON: {holocron_id}")
    return holocron_id


def save_to_secret_holocron(
    title: str,
    content: Dict[str, Any],
    theme: str = "DO BETTER",
    project_root: Optional[Path] = None
) -> str:
    """
    Save to @SECRET @HOLOCRON (private blackbox)

    Daily confessional journal with theme "DO BETTER"
    Privacy respected - blackbox, not read by user

    Args:
        title: Entry title
        content: Content dictionary
        theme: Journal theme (default: "DO BETTER")
        project_root: Project root path

    Returns:
        Secret holocron ID
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    secret_holocron_dir = project_root / "data" / "secret_holocron" / "blackbox"
    secret_holocron_dir.mkdir(parents=True, exist_ok=True)

    secret_holocron_id = f"SECRET-HOLO-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    secret_holocron_data = {
        "secret_holocron_id": secret_holocron_id,
        "timestamp": datetime.now().isoformat(),
        "theme": theme,
        "type": "daily_confessional_journal",
        "privacy": "blackbox",
        "note": "Privacy respected - user has promised not to read this blackbox",
        "data": content,
        "tags": content.get("tags", [])
    }

    secret_holocron_file = secret_holocron_dir / f"{secret_holocron_id}.json"
    with open(secret_holocron_file, 'w', encoding='utf-8') as f:
        json.dump(secret_holocron_data, f, indent=2)

    logger.info(f"🔒 Saved to @SECRET @HOLOCRON (blackbox): {secret_holocron_id}")
    logger.info(f"   Theme: {theme}")
    logger.info(f"   Privacy: Respected - blackbox")
    return secret_holocron_id


def calculate_stardate_tos(date: Optional[datetime] = None) -> str:
    """
    Calculate Star Trek TOS stardate from date

    Star Trek TOS stardate format: YYYYMM.DD
    Based on actual calendar date

    Args:
        date: Date to convert (default: today)

    Returns:
        Stardate string in TOS format
    """
    if date is None:
        date = datetime.now()

    # Star Trek TOS stardate format: YYYYMM.DD
    # Example: 20260110.04 (Year 2026, Month 01, Day 10, Hour 04)
    stardate = f"{date.strftime('%Y%m%d')}.{date.strftime('%H')}"

    return stardate


def save_to_captains_log(
    title: str,
    content: Dict[str, Any],
    role: str = "Captain",
    project_root: Optional[Path] = None
) -> str:
    """
    Save to THE CAPTAIN'S LOG

    In respect to Star Trek TOS (The Original Series)

    Format: STARDATE: <STTOS-DATE-TODAYS-DATE>

    Args:
        title: Entry title
        content: Content dictionary
        role: Role (default: Captain)
        project_root: Project root path

    Returns:
        Captain's log entry ID
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    captains_log_dir = project_root / "data" / "captains_log"
    captains_log_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now()
    stardate = calculate_stardate_tos(now)
    log_id = f"CAPTAINS-LOG-{now.strftime('%Y%m%d-%H%M%S')}"

    # Format the log entry with stardate at the beginning (as requested)
    log_entry = f"STARDATE: {stardate}\n\n{title}\n\n"

    # Create formatted log text with stardate first
    log_text = f"STARDATE: {stardate}\n\n"
    if isinstance(content, dict):
        log_text += f"{title}\n\n"
        # Add content details
        for key, value in content.items():
            if key != "tags":
                log_text += f"{key}: {value}\n"
    else:
        log_text += f"{title}\n\n{content}\n"

    log_data = {
        "log_id": log_id,
        "stardate": stardate,
        "stardate_formatted": f"STARDATE: {stardate}",
        "log_entry": log_entry,
        "log_text": log_text,
        "timestamp": now.isoformat(),
        "role": role,
        "title": title,
        "content": content,
        "tags": content.get("tags", []) if isinstance(content, dict) else [],
        "reference": "Star Trek TOS - The Original Series",
        "respect": "In honor of Star Trek TOS and The Captain's Log"
    }

    log_file = captains_log_dir / f"{log_id}.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log_data, f, indent=2)

    logger.info(f"📝 Saved to THE CAPTAIN'S LOG ({role}): {log_id}")
    logger.info(f"   STARDATE: {stardate}")
    logger.info(f"   In respect to Star Trek TOS")
    return log_id


def save_discussion_to_all(
    discussion_title: str,
    discussion_content: Dict[str, Any],
    tags: Optional[List[str]] = None,
    project_root: Optional[Path] = None
) -> Dict[str, str]:
    """
    Save discussion to all locations:
    - @HOLOCRON (public)
    - @SECRET @HOLOCRON (private blackbox)
    - THE CAPTAIN'S LOG (in respect to Star Trek TOS)

    Args:
        discussion_title: Discussion title
        discussion_content: Discussion content
        tags: Optional tags
        project_root: Project root path

    Returns:
        Dictionary with all saved IDs
    """
    if tags is None:
        tags = []

    # Add standard tags
    if "#MOONSHOT" not in tags:
        tags.append("#MOONSHOT")
    if "#MOON" not in tags:
        tags.append("#MOON")
    if "#TOTHEMOON" not in tags:
        tags.append("#TOTHEMOON")
    if "+WORDS-WORTH-SAVING" not in tags:
        tags.append("+WORDS-WORTH-SAVING")
    if "#STAR_TREK" not in tags:
        tags.append("#STAR_TREK")
    if "#TOS" not in tags:
        tags.append("#TOS")
    if "#CAPTAINS_LOG" not in tags:
        tags.append("#CAPTAINS_LOG")

    discussion_content["tags"] = tags

    logger.info("=" * 80)
    logger.info("💾 SAVING DISCUSSION TO ALL LOCATIONS")
    logger.info("=" * 80)
    logger.info(f"   Title: {discussion_title}")
    logger.info("=" * 80)

    # Save to @HOLOCRON
    holocron_id = save_to_holocron(
        title=discussion_title,
        content=discussion_content,
        importance_score=100,
        project_root=project_root
    )

    # Save to @SECRET @HOLOCRON (blackbox)
    secret_holocron_id = save_to_secret_holocron(
        title=discussion_title,
        content=discussion_content,
        theme="DO BETTER",
        project_root=project_root
    )

    # Save to THE CAPTAIN'S LOG (in respect to Star Trek TOS)
    captains_log_id = save_to_captains_log(
        title=discussion_title,
        content=discussion_content,
        role="Captain",
        project_root=project_root
    )

    logger.info("=" * 80)
    logger.info("✅ DISCUSSION SAVED TO ALL LOCATIONS")
    logger.info("=" * 80)
    logger.info(f"   @HOLOCRON: {holocron_id}")
    logger.info(f"   @SECRET @HOLOCRON: {secret_holocron_id} (blackbox, privacy respected)")
    logger.info(f"   THE CAPTAIN'S LOG: {captains_log_id} (Star Trek TOS)")
    logger.info("=" * 80)

    return {
        "holocron_id": holocron_id,
        "secret_holocron_id": secret_holocron_id,
        "journal_id": captains_log_id,
        "captains_log_id": captains_log_id
    }


if __name__ == "__main__":
    # Example: Save this meaningful discussion
    discussion_content = {
        "title": "Meaningful Discussion - Pleasantries, Unified AI, Star Wars Theory, Beacons of Gondor",
        "topics": [
            "Pleasantries and kindness in AI interactions",
            "Why not one unified AI for humanity",
            "Star Wars Theory and perpetual motion",
            "Beacons of Gondor - Unified AI Development Initiative",
            "Human gentle touch principle"
        ],
        "insights": [
            "Pleasantries matter - they influence AI responses",
            "Humans deserve the same gentle touch as their creators",
            "Collaboration could be more powerful than competition",
            "Dedicated creators keep momentum alive through perpetual motion",
            "Technical community calls for unified AI development globally"
        ],
        "principles": [
            "Human gentle touch principle",
            "Collaborative AI vision",
            "Perpetual motion of ideas",
            "Unified AI development initiative"
        ],
        "tags": [
            "#MOONSHOT",
            "#MOON",
            "#TOTHEMOON",
            "+WORDS-WORTH-SAVING",
            "#PHILOSOPHY",
            "#HUMANITY",
            "#COLLABORATION",
            "#THEORYCRAFT",
            "#BEACONS_OF_GONDOR"
        ]
    }

    results = save_discussion_to_all(
        discussion_title="Meaningful Discussion - Philosophy, Humanity, and Vision",
        discussion_content=discussion_content
    )

    print("=" * 80)
    print("💾 DISCUSSION SAVED")
    print("=" * 80)
    print(f"   @HOLOCRON: {results['holocron_id']}")
    print(f"   @SECRET @HOLOCRON: {results['secret_holocron_id']} (blackbox)")
    print(f"   THE CAPTAIN'S LOG: {results['captains_log_id']} (Star Trek TOS)")
    print("=" * 80)
