#!/usr/bin/env python3
"""
Extract Neo Browser Cookies for IDM Downloads
Extracts HuggingFace cookies from Neo browser and formats them for IDM
"""

import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from typing import Optional, Dict, List
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("extract_neo_cookies_for_idm")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def find_neo_cookies_db() -> Optional[Path]:
    try:
        """Find Neo browser cookies database"""
        neo_user_data_paths = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "User Data" / "Default" / "Cookies",
            Path(os.environ.get("APPDATA", "")) / "Neo" / "User Data" / "Default" / "Cookies",
            Path.home() / "AppData" / "Local" / "Neo" / "User Data" / "Default" / "Cookies",
        ]

        for path in neo_user_data_paths:
            if path.exists():
                return path

        return None

    except Exception as e:
        logger.error(f"Error in find_neo_cookies_db: {e}", exc_info=True)
        raise
def extract_huggingface_cookies(cookies_db: Path) -> str:
    """Extract HuggingFace cookies from Neo browser database"""
    try:
        # Copy database (Neo locks it)
        import shutil
        temp_db = cookies_db.parent / "Cookies_temp"
        shutil.copy2(cookies_db, temp_db)

        # Connect to cookies database
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        # Query HuggingFace cookies
        cursor.execute("""
            SELECT name, value, host_key, path, expires_utc, is_secure
            FROM cookies
            WHERE host_key LIKE '%huggingface.co%'
        """)

        cookies = cursor.fetchall()
        conn.close()

        # Cleanup temp file
        if temp_db.exists():
            temp_db.unlink()

        if not cookies:
            return ""

        # Format cookies for IDM (Netscape format or simple key=value)
        cookie_strings = []
        for name, value, host, path, expires, secure in cookies:
            cookie_strings.append(f"{name}={value}")

        return "; ".join(cookie_strings)

    except Exception as e:
        print(f"Error extracting cookies: {e}", file=sys.stderr)
        return ""

def main():
    """Main function"""
    cookies_db = find_neo_cookies_db()

    if not cookies_db:
        print("ERROR: Neo browser cookies database not found", file=sys.stderr)
        print("Please ensure Neo browser is installed and you're logged in to HuggingFace", file=sys.stderr)
        sys.exit(1)

    cookies = extract_huggingface_cookies(cookies_db)

    if cookies:
        print(cookies)
        sys.exit(0)
    else:
        print("ERROR: No HuggingFace cookies found", file=sys.stderr)
        print("Please log in to HuggingFace in Neo browser first", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":



    main()