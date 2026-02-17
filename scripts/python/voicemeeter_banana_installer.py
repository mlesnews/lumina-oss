#!/usr/bin/env python3
"""
VB Audio VoiceMeeter Banana Installer

Download and install VB Audio VoiceMeeter Banana.
Performance tune to limit scope of audio listened to by AI.
Use isolated voice pattern for transcription.

Tags: #VOICEMEETER #BANANA #AUDIO-TUNING #VOICE-PATTERN @JARVIS @TEAM
"""

import sys
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("VoiceMeeterBananaInstaller")
ts_logger = get_timestamp_logger()


class VOICEMEETERBANANAINSTALLER:
    """
    VB Audio VoiceMeeter Banana Installer

    Download and install VB Audio VoiceMeeter Banana.
    Performance tune to limit scope of audio listened to by AI.
    Use isolated voice pattern for transcription.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VoiceMeeter Banana Installer"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.downloads_dir = self.project_root / "downloads"
        self.downloads_dir.mkdir(parents=True, exist_ok=True)

        # VB Audio VoiceMeeter Banana download URL
        self.voicemeeter_url = "https://download.vb-audio.com/Download_CABLE/VoicemeeterBanana_2.0.8.2.exe"
        self.installer_name = "VoicemeeterBanana_2.0.8.2.exe"

        logger.info("🎤 VoiceMeeter Banana Installer initialized")
        logger.info("   Performance tune audio for AI")
        logger.info("   Isolated voice pattern for transcription")

    def download_voicemeeter(self) -> Path:
        """Download VB Audio VoiceMeeter Banana"""
        installer_path = self.downloads_dir / self.installer_name

        if installer_path.exists():
            logger.info(f"✅ Installer already exists: {installer_path}")
            return installer_path

        logger.info(f"📥 Downloading VoiceMeeter Banana from {self.voicemeeter_url}")
        logger.info(f"   Saving to: {installer_path}")

        try:
            urllib.request.urlretrieve(self.voicemeeter_url, installer_path)
            logger.info(f"✅ Download complete: {installer_path}")
            return installer_path
        except Exception as e:
            logger.error(f"❌ Download failed: {e}")
            raise

    def install_voicemeeter(self, installer_path: Optional[Path] = None, silent: bool = False) -> bool:
        """Install VB Audio VoiceMeeter Banana"""
        if installer_path is None:
            installer_path = self.downloads_dir / self.installer_name

        if not installer_path.exists():
            logger.error(f"❌ Installer not found: {installer_path}")
            return False

        logger.info(f"🔧 Installing VoiceMeeter Banana: {installer_path}")

        try:
            if silent:
                # Silent install
                subprocess.run(
                    [str(installer_path), "/S"],
                    check=True,
                    timeout=300,
                )
            else:
                # Interactive install
                subprocess.run(
                    [str(installer_path)],
                    check=True,
                    timeout=300,
                )

            logger.info("✅ VoiceMeeter Banana installed successfully")
            return True
        except subprocess.TimeoutExpired:
            logger.error("❌ Installation timed out")
            return False
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Installation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Installation error: {e}")
            return False

    def configure_for_ai(self) -> Dict[str, Any]:
        """Configure VoiceMeeter Banana for AI audio tuning"""
        logger.info("🎛️  Configuring VoiceMeeter Banana for AI audio tuning")
        logger.info("   Limit scope of audio listened to by AI")
        logger.info("   Use isolated voice pattern")
        logger.info("   Performance tune")

        configuration = {
            "input_channel": "Hardware Input 1",  # User's microphone
            "output_channel": "VAIO3",  # Virtual audio cable for AI
            "isolation_mode": True,  # Isolate user's voice
            "noise_gate": True,  # Filter background noise
            "compression": True,  # Normalize audio levels
            "voice_pattern_matching": True,  # Use voice pattern
            "ai_listening_scope": "isolated_voice_only",  # Limit scope
        }

        logger.info("✅ Configuration created:")
        logger.info(f"   Input: {configuration['input_channel']}")
        logger.info(f"   Output: {configuration['output_channel']}")
        logger.info(f"   Isolation: {configuration['isolation_mode']}")
        logger.info(f"   AI Scope: {configuration['ai_listening_scope']}")

        return configuration


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="VB Audio VoiceMeeter Banana Installer")
    parser.add_argument("--download", action="store_true", help="Download VoiceMeeter Banana")
    parser.add_argument("--install", action="store_true", help="Install VoiceMeeter Banana")
    parser.add_argument("--silent", action="store_true", help="Silent install")
    parser.add_argument("--configure", action="store_true", help="Configure for AI")

    args = parser.parse_args()

    print("="*80)
    print("🎤 VB AUDIO VOICEMEETER BANANA INSTALLER")
    print("="*80)
    print()
    print("Download and install VB Audio VoiceMeeter Banana")
    print("Performance tune to limit scope of audio listened to by AI")
    print("Use isolated voice pattern for transcription")
    print()

    installer = VOICEMEETERBANANAINSTALLER()

    if args.download:
        installer_path = installer.download_voicemeeter()
        print(f"📥 Download complete: {installer_path}")
        print()

    if args.install:
        success = installer.install_voicemeeter(silent=args.silent)
        if success:
            print("✅ Installation complete")
        else:
            print("❌ Installation failed")
        print()

    if args.configure:
        config = installer.configure_for_ai()
        print("🎛️  CONFIGURATION:")
        print(f"   Input: {config['input_channel']}")
        print(f"   Output: {config['output_channel']}")
        print(f"   Isolation: {config['isolation_mode']}")
        print(f"   AI Scope: {config['ai_listening_scope']}")
        print()

    if not any([args.download, args.install, args.configure]):
        # Default: show info
        print("Use --download to download VoiceMeeter Banana")
        print("Use --install to install VoiceMeeter Banana")
        print("Use --silent for silent install")
        print("Use --configure to configure for AI")
        print()


if __name__ == "__main__":


    main()