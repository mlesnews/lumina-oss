#!/usr/bin/env python3
"""
Lumina YouTube Channel Setup & Configuration

Setup and configuration for Lumina YouTube channel docuseries uploads.
Includes channel creation guidance and upload automation.
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaYouTubeChannel")


class LuminaYouTubeChannel:
    """
    Lumina YouTube Channel Configuration and Management

    Manages the Lumina YouTube channel for docuseries content
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Lumina YouTube channel manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config" / "youtube"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_file = self.config_dir / "lumina_channel_config.json"
        self.credentials_file = self.config_dir / "credentials.json"
        self.client_secrets_file = self.config_dir / "client_secrets.json"

        # Load or create config
        self.config = self._load_or_create_config()

        logger.info("📺 Lumina YouTube Channel manager initialized")

    def _load_or_create_config(self) -> Dict[str, Any]:
        """Load existing config or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load config: {e}")

        # Default config
        default_config = {
            "channel": {
                "name": "Lumina",
                "handle": "@lumina",  # To be created
                "description": "Lumina - AI-Powered Knowledge Docuseries\n\nTransforming YouTube content into structured knowledge through Holocrons and intelligent docuseries.",
                "keywords": [
                    "AI", "Artificial Intelligence", "Knowledge Management",
                    "Holocron", "Docuseries", "Technology", "Learning",
                    "ULTRON", "SYPHON", "JARVIS"
                ],
                "category": "Education",
                "language": "en",
                "country": "US"
            },
            "upload": {
                "privacy": "public",  # or "unlisted", "private"
                "default_tags": ["#lumina", "#holocron", "#docuseries", "#ai"],
                "default_category": "Education",
                "default_language": "en"
            },
            "docuseries": {
                "playlist_name": "Lumina Docuseries - ULTRON Channel Analysis",
                "description": "Docuseries chapters created from ULTRON channel videos, transformed into Holocrons and knowledge artifacts.",
                "episode_prefix": "Chapter"
            },
            "youtube_api": {
                "enabled": False,
                "api_key": None,
                "oauth_required": True,
                "scopes": [
                    "https://www.googleapis.com/auth/youtube.upload",
                    "https://www.googleapis.com/auth/youtube.force-ssl"
                ]
            },
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Save default config
        with open(self.config_file, 'w') as f:
            json.dump(default_config, f, indent=2)

        return default_config

    def save_config(self):
        try:
            """Save current configuration"""
            self.config["updated_at"] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            logger.info("✅ Configuration saved")

        except Exception as e:
            self.logger.error(f"Error in save_config: {e}", exc_info=True)
            raise
    def setup_channel_guidance(self) -> Dict[str, Any]:
        """
        Provide guidance for creating Lumina YouTube channel

        Returns:
            Step-by-step setup instructions
        """
        guidance = {
            "steps": [
                {
                    "step": 1,
                    "title": "Create YouTube Channel",
                    "description": "Go to YouTube and create a new channel named 'Lumina'",
                    "url": "https://www.youtube.com/create_channel",
                    "notes": "Choose a name that represents the knowledge docuseries concept"
                },
                {
                    "step": 2,
                    "title": "Channel Branding",
                    "description": "Set up channel branding:",
                    "checklist": [
                        "Upload channel banner (recommended: 2560x1440px)",
                        "Upload channel icon/profile picture",
                        "Write channel description with keywords",
                        "Add channel links and social media"
                    ]
                },
                {
                    "step": 3,
                    "title": "Enable YouTube Data API",
                    "description": "Enable YouTube Data API v3 in Google Cloud Console",
                    "url": "https://console.cloud.google.com/apis/library/youtube.googleapis.com",
                    "checklist": [
                        "Create Google Cloud Project (if needed)",
                        "Enable YouTube Data API v3",
                        "Create OAuth 2.0 credentials",
                        "Download client_secrets.json"
                    ]
                },
                {
                    "step": 4,
                    "title": "Configure Credentials",
                    "description": "Set up authentication credentials",
                    "instructions": [
                        f"Place client_secrets.json in: {self.client_secrets_file}",
                        "Run OAuth flow to get access token",
                        "Credentials will be stored securely"
                    ]
                },
                {
                    "step": 5,
                    "title": "Create First Playlist",
                    "description": "Create playlist for docuseries",
                    "playlist_name": self.config["docuseries"]["playlist_name"],
                    "notes": "This playlist will contain all ULTRON docuseries chapters"
                },
                {
                    "step": 6,
                    "title": "Test Upload",
                    "description": "Test upload with a sample video",
                    "notes": "Verify upload process works before processing all videos"
                }
            ],
            "config_location": str(self.config_file),
            "credentials_location": str(self.credentials_file),
            "status": "ready_for_setup"
        }

        return guidance

    def generate_channel_description(self) -> str:
        """Generate optimized channel description"""
        description = f"""Lumina - AI-Powered Knowledge Docuseries

{self.config['channel']['description']}

🔮 About Lumina:
Lumina transforms YouTube content into structured knowledge through:
• Holocron Notebooks - Jupyter notebooks containing video intelligence
• Docuseries Chapters - Organized knowledge presentations
• SYPHON Intelligence - Actionable insights extraction
• ULTRON Cluster - Unified knowledge processing

📚 Content:
• Docuseries chapters from ULTRON channel analysis
• Knowledge transformation workflows
• AI-powered content structuring
• Educational technology insights

#Lumina #Holocron #Docuseries #AI #KnowledgeManagement #ULTRON #SYPHON
"""
        return description

    def create_upload_metadata(self, video_title: str, description: str,
                               chapter_number: int, tags: List[str] = None) -> Dict[str, Any]:
        """
        Create YouTube upload metadata for a docuseries chapter

        Args:
            video_title: Video title
            description: Video description
            chapter_number: Chapter number in docuseries
            tags: Additional tags

        Returns:
            YouTube API upload metadata
        """
        docuseries_config = self.config["docuseries"]
        upload_config = self.config["upload"]

        full_title = f"{docuseries_config['episode_prefix']} {chapter_number}: {video_title}"

        full_description = f"""{description}

---

📚 Lumina Docuseries - ULTRON Channel Analysis
Chapter {chapter_number} of our knowledge transformation journey.

🔮 Holocron Notebooks Available:
These videos are created from Holocron notebooks (Jupyter notebooks)
containing structured intelligence from source YouTube content.

#Lumina #Holocron #Docuseries #Chapter{chapter_number} #{docuseries_config['episode_prefix'].lower()}

---

About Lumina:
Lumina transforms YouTube content into structured knowledge through
Holocron notebooks, docuseries chapters, and SYPHON intelligence extraction.
"""

        all_tags = upload_config["default_tags"] + (tags or [])
        all_tags.append(f"chapter{chapter_number}")

        metadata = {
            "snippet": {
                "title": full_title,
                "description": full_description,
                "tags": all_tags,
                "categoryId": "27",  # Education (YouTube category ID)
                "defaultLanguage": upload_config["default_language"],
                "defaultAudioLanguage": upload_config["default_language"]
            },
            "status": {
                "privacyStatus": upload_config["privacy"],
                "selfDeclaredMadeForKids": False
            }
        }

        return metadata


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Lumina YouTube Channel Setup & Configuration"
        )
        parser.add_argument("--setup-guide", action="store_true",
                           help="Show channel setup guidance")
        parser.add_argument("--generate-description", action="store_true",
                           help="Generate channel description")
        parser.add_argument("--create-metadata", nargs=3,
                           metavar=("TITLE", "DESCRIPTION", "CHAPTER"),
                           help="Create upload metadata for a video")

        args = parser.parse_args()

        channel = LuminaYouTubeChannel()

        if args.setup_guide:
            guidance = channel.setup_channel_guidance()
            print("\n" + "="*60)
            print("LUMINA YOUTUBE CHANNEL SETUP GUIDE")
            print("="*60)
            for step in guidance["steps"]:
                print(f"\nStep {step['step']}: {step['title']}")
                print(f"  {step['description']}")
                if "checklist" in step:
                    for item in step["checklist"]:
                        print(f"    • {item}")
                if "url" in step:
                    print(f"  URL: {step['url']}")
            print("\n" + "="*60)
            print(f"Config file: {guidance['config_location']}")
            print("="*60)

        elif args.generate_description:
            description = channel.generate_channel_description()
            print("\n" + "="*60)
            print("LUMINA YOUTUBE CHANNEL DESCRIPTION")
            print("="*60)
            print(description)
            print("="*60)

        elif args.create_metadata:
            title, desc, chapter = args.create_metadata
            metadata = channel.create_upload_metadata(
                title, desc, int(chapter)
            )
            print("\n" + "="*60)
            print("YOUTUBE UPLOAD METADATA")
            print("="*60)
            print(json.dumps(metadata, indent=2))
            print("="*60)

        else:
            parser.print_help()
            print("\n📺 Lumina YouTube Channel Setup")
            print("   Run with --setup-guide to see setup instructions")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()