"""
PUBLIC: WakaTime Badge Updater
Location: scripts/python/update_wakatime_badges.py
License: MIT

Automatically updates WakaTime badges in README and documentation files.
"""

import re
from pathlib import Path
from typing import Optional
import logging


# Initialize logger
logger = logging.getLogger(__name__)


def update_readme_badges(
    project_root: Path,
    user_id: Optional[str] = None,
    username: Optional[str] = None
) -> bool:
    """
    Update WakaTime badges in README.

    Args:
        project_root: Path to project root
        user_id: WakaTime user ID (optional, will use placeholder if not provided)
        username: WakaTime username (optional, will use placeholder if not provided)

    Returns:
        True if badges were added/updated, False otherwise
    """
    readme_path = project_root / "README_LUMINA.md"

    if not readme_path.exists():
        logger.warning(f"README not found at {readme_path}")
        return False

    # Read current README
    content = readme_path.read_text(encoding="utf-8")

    # Badge section template
    user_placeholder = user_id or "{user_id}"
    username_placeholder = username or "@username"

    badge_section = f"""
## 📊 Coding Statistics

Track coding activity with WakaTime:

[![WakaTime](https://wakatime.com/badge/user/{user_placeholder}/project/LUMINA.svg)](https://wakatime.com/{username_placeholder}/projects/LUMINA)

*Tracked with [WakaTime](https://wakatime.com) - Automatic time tracking for developers*

### Recent Activity

- View detailed stats: [WakaTime Dashboard](https://wakatime.com/dashboard)
- See all sharing options: [WakaTime Share](https://wakatime.com/share)
- Documentation: [WakaTime Sharing Setup](docs/WAKATIME_SHARING_SETUP.md)

"""

    # Check if badges section already exists
    if "WakaTime" in content and "badge" in content.lower():
        # Update existing badges
        pattern = r"## 📊 Coding Statistics.*?(?=\n## |\Z)"
        if re.search(pattern, content, re.DOTALL):
            content = re.sub(pattern, badge_section.strip(), content, flags=re.DOTALL)
            logger.info("Updated existing WakaTime badges section")
        else:
            logger.info("WakaTime badges found but section format may differ")
            return False
    else:
        # Add badges section after main title
        title_pattern = r"(# Lumina - Light Through Perfect Balance\n)"
        if re.search(title_pattern, content):
            content = re.sub(
                title_pattern,
                r"\1" + badge_section,
                content
            )
            logger.info("Added new WakaTime badges section")
        else:
            # Try adding after philosophy section
            philosophy_pattern = r"(## 🌟 The Name Says It All.*?\n\n)"
            if re.search(philosophy_pattern, content, re.DOTALL):
                content = re.sub(
                    philosophy_pattern,
                    r"\1" + badge_section,
                    content,
                    flags=re.DOTALL
                )
                logger.info("Added WakaTime badges section after philosophy")
            else:
                logger.warning("Could not find suitable location to add badges")
                return False

    # Write updated content
    readme_path.write_text(content, encoding="utf-8")
    logger.info(f"✅ Updated {readme_path} with WakaTime badges")
    return True


def update_contributing_badges(
    project_root: Path,
    user_id: Optional[str] = None,
    username: Optional[str] = None
) -> bool:
    """
    Add WakaTime badges to CONTRIBUTING.md if desired.

    Args:
        project_root: Path to project root
        user_id: WakaTime user ID
        username: WakaTime username

    Returns:
        True if updated, False otherwise
    """
    contributing_path = project_root / "CONTRIBUTING.md"

    if not contributing_path.exists():
        return False

    # Optional: Add badges to contributing guide
    # This is less common, so we'll skip for now
    return False


def main():
    try:
        """Main function to update WakaTime badges."""
        import sys
        import os

        # Get project root (3 levels up from this script)
        script_path = Path(__file__).resolve()
        project_root = script_path.parent.parent.parent

        # Get user ID and username from environment or args
        user_id = os.getenv("WAKATIME_USER_ID")
        username = os.getenv("WAKATIME_USERNAME")

        if len(sys.argv) > 1:
            user_id = sys.argv[1] if not user_id else user_id
        if len(sys.argv) > 2:
            username = sys.argv[2] if not username else username

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

        logger.info("🔄 Updating WakaTime badges...")

        if user_id and username:
            logger.info(f"Using WakaTime user: {username} (ID: {user_id})")
        else:
            logger.info("Using placeholder values - update with your WakaTime credentials")

        # Update README
        success = update_readme_badges(project_root, user_id, username)

        if success:
            print("✅ WakaTime badges updated successfully!")
            print(f"   Updated: {project_root / 'README_LUMINA.md'}")
            if not user_id or not username:
                print("\n⚠️  Note: Using placeholder values")
                print("   Set WAKATIME_USER_ID and WAKATIME_USERNAME environment variables")
                print("   or pass them as arguments to use real badges")
        else:
            print("⚠️  Could not update badges. Check logs for details.")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()