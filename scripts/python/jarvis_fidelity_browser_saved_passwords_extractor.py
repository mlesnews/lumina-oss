#!/usr/bin/env python3
"""
JARVIS Fidelity Browser Saved Passwords Extractor
Extracts Fidelity credentials from browser's saved passwords

Since ProtonPass CLI is broken and GUI extraction is complex,
we can extract credentials directly from the browser's saved password manager.

Tags: #FIDELITY #BROWSER #PASSWORDS #AUTOMATION #JARVIS
"""

import sys
import os
import sqlite3
import json
import base64
from pathlib import Path
from typing import Dict, Any, Optional

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFidelityBrowserSavedPasswordsExtractor")


class JARVISFidelityBrowserSavedPasswordsExtractor:
    """
    Extract Fidelity credentials from browser's saved passwords

    Uses browser password databases (Chrome/Edge/Neo use same format)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize extractor"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Browser password database locations
        self.browser_paths = {
            "Neo": Path(os.environ.get("LOCALAPPDATA", "")) / "Neo" / "User Data" / "Default" / "Login Data",
            "Chrome": Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "User Data" / "Default" / "Login Data",
            "Edge": Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "Edge" / "User Data" / "Default" / "Login Data"
        }

        logger.info("=" * 70)
        logger.info("🤖 JARVIS FIDELITY BROWSER SAVED PASSWORDS EXTRACTOR")
        logger.info("=" * 70)
        logger.info("   Extracting from browser's saved password database")
        logger.info("   Fully automated - NO MANUAL STEPS")
        logger.info("")

    def extract_from_browser_db(self, db_path: Path, browser_name: str) -> Dict[str, Optional[str]]:
        """Extract credentials from browser password database"""
        logger.info(f"🔍 Extracting from {browser_name} password database...")
        logger.info(f"   Path: {db_path}")

        if not db_path.exists():
            logger.warning(f"   ⚠️  Database not found at: {db_path}")
            return {"username": None, "password": None, "source": None}

        try:
            # Copy database (browser may have it locked)
            import shutil
            import tempfile

            temp_db = Path(tempfile.gettempdir()) / f"login_data_{browser_name}.db"
            if temp_db.exists():
                temp_db.unlink()

            shutil.copy2(db_path, temp_db)
            logger.info("   ✅ Database copied to temp location")

            # Connect to database
            conn = sqlite3.connect(str(temp_db))
            cursor = conn.cursor()

            # Query for Fidelity credentials
            query = """
            SELECT origin_url, username_value, password_value 
            FROM logins 
            WHERE origin_url LIKE '%fidelity%' 
               OR origin_url LIKE '%fidelityinvestments%'
               OR origin_url LIKE '%fidelity.com%'
            """

            cursor.execute(query)
            results = cursor.fetchall()

            conn.close()
            temp_db.unlink()  # Clean up

            if results:
                logger.info(f"   ✅ Found {len(results)} Fidelity credential(s)")

                # Use the first result (most recent)
                origin_url, username, encrypted_password = results[0]

                # Decrypt password (Windows uses DPAPI)
                try:
                    import win32crypt
                    password = win32crypt.CryptUnprotectData(encrypted_password, None, None, None, 0)[1].decode('utf-8')

                    logger.info(f"   Username: ✅")
                    logger.info(f"   Password: ✅")

                    return {
                        "username": username,
                        "password": password,
                        "source": f"{browser_name}_saved_passwords",
                        "url": origin_url
                    }
                except ImportError:
                    logger.warning("   ⚠️  win32crypt not available - cannot decrypt password")
                    logger.info("   💡 Install pywin32: pip install pywin32")
                    return {"username": username, "password": None, "source": f"{browser_name}_saved_passwords"}
                except Exception as e:
                    logger.error(f"   ❌ Decryption failed: {e}")
                    return {"username": username, "password": None, "source": f"{browser_name}_saved_passwords"}
            else:
                logger.info("   ⚠️  No Fidelity credentials found in database")
                return {"username": None, "password": None, "source": None}

        except Exception as e:
            logger.error(f"   ❌ Extraction failed: {e}")
            return {"username": None, "password": None, "source": None, "error": str(e)}

    def extract_credentials(self) -> Dict[str, Any]:
        """Extract credentials from all available browsers"""
        logger.info("=" * 70)
        logger.info("🚀 EXTRACTING FROM BROWSER SAVED PASSWORDS")
        logger.info("=" * 70)
        logger.info("")

        # Try each browser
        for browser_name, db_path in self.browser_paths.items():
            result = self.extract_from_browser_db(db_path, browser_name)
            if result.get("username") and result.get("password"):
                logger.info("")
                logger.info("=" * 70)
                logger.info(f"✅ CREDENTIALS EXTRACTED: {browser_name}")
                logger.info("=" * 70)
                return {
                    "success": True,
                    "username": result["username"],
                    "password": result["password"],
                    "source": result["source"],
                    "url": result.get("url")
                }

        logger.info("")
        logger.info("=" * 70)
        logger.info("⚠️  NO CREDENTIALS FOUND IN BROWSER SAVED PASSWORDS")
        logger.info("=" * 70)

        return {
            "success": False,
            "username": None,
            "password": None,
            "source": None
        }


def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(description="JARVIS Fidelity Browser Saved Passwords Extractor")
    parser.add_argument("--extract", "-e", action="store_true", help="Extract credentials")

    args = parser.parse_args()

    extractor = JARVISFidelityBrowserSavedPasswordsExtractor()

    if args.extract:
        result = extractor.extract_credentials()
        if result.get("success"):
            print(f"\n✅ Credentials extracted successfully!")
            print(f"   Username: {result['username']}")
            print(f"   Password: {'***' if result['password'] else 'Not found'}")
            print(f"   Source: {result['source']}")
        else:
            print(f"\n⚠️  No credentials found in browser saved passwords")
    else:
        parser.print_help()


if __name__ == "__main__":


    main()