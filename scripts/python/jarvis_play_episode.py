#!/usr/bin/env python3
"""
JARVIS Episode Player - Full Screen Playback

Plays the 40-minute Quantum Anime episode in full screen mode.

Tags: #JARVIS #PLAYBACK #FULLSCREEN @JARVIS @LUMINA
"""

import sys
import subprocess
from pathlib import Path
from typing import Optional

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


class JARVISEpisodePlayer:
    """JARVIS Episode Player - Full Screen Playback"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS player"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("JARVISEpisodePlayer")

        self.episodes_dir = self.project_root / "data" / "quantum_anime" / "episodes_40min"

    def play_episode(self, episode_id: str = "S01E01", fullscreen: bool = True):
        """Play episode in full screen"""
        # Try multiple locations
        possible_paths = [
            self.episodes_dir / f"{episode_id}_40MIN_FINAL.mp4",
            self.project_root / "data" / "quantum_anime" / "videos" / f"{episode_id}_40MIN_ANIMATED_FINAL.mp4",
            self.project_root / "data" / "quantum_anime" / "videos_animated" / f"{episode_id}_ANIMATED_COMPLETE.mp4",
            self.project_root / "data" / "quantum_anime" / "videos" / f"{episode_id}_40MIN_FINAL.mp4",
        ]

        episode_file = None
        for path in possible_paths:
            if path.exists():
                episode_file = path
                break

        if not episode_file or not episode_file.exists():
            self.logger.error(f"❌ Episode not found. Checked:")
            for path in possible_paths:
                self.logger.error(f"   - {path} ({'✅' if path.exists() else '❌'})")
            return False

        self.logger.info(f"🎬 JARVIS: Playing episode {episode_id} in full screen...")
        self.logger.info(f"   📁 File: {episode_file.name}")

        # Try different players in order of preference
        players = [
            # VLC (best for full screen)
            {
                "name": "VLC",
                "command": ["vlc", "--fullscreen", "--no-video-title-show", str(episode_file)],
                "check": ["vlc", "--version"]
            },
            # Windows Media Player
            {
                "name": "Windows Media Player",
                "command": ["wmplayer", "/fullscreen", str(episode_file)],
                "check": ["wmplayer", "/?"]
            },
            # Default Windows video player
            {
                "name": "Default Player",
                "command": ["start", "/max", str(episode_file)],
                "check": None
            },
            # Fallback: open with default application
            {
                "name": "System Default",
                "command": ["cmd", "/c", "start", "", str(episode_file)],
                "check": None
            }
        ]

        for player in players:
            try:
                # Check if player is available
                if player["check"]:
                    check_result = subprocess.run(
                        player["check"],
                        capture_output=True,
                        timeout=2
                    )
                    if check_result.returncode != 0:
                        continue

                # Launch player
                self.logger.info(f"   🎥 Using {player['name']}...")

                if player["name"] == "System Default":
                    # Use os.startfile for Windows
                    import os
                    os.startfile(str(episode_file))
                else:
                    subprocess.Popen(
                        player["command"],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                    )

                self.logger.info(f"   ✅ Episode playing in {player['name']}")
                return True

            except FileNotFoundError:
                continue
            except Exception as e:
                self.logger.warning(f"   ⚠️  {player['name']} failed: {e}")
                continue

        # Last resort: open with default application
        try:
            import os
            import webbrowser
            os.startfile(str(episode_file))
            self.logger.info("   ✅ Opened with system default player")
            return True
        except Exception as e:
            self.logger.error(f"   ❌ Failed to open episode: {e}")
            return False

    def play_with_vlc_fullscreen(self, episode_id: str = "S01E01"):
        """Play episode with VLC in full screen (preferred method)"""
        episode_file = self.episodes_dir / f"{episode_id}_40MIN_FINAL.mp4"

        if not episode_file.exists():
            self.logger.error(f"❌ Episode not found: {episode_file}")
            return False

        # VLC full screen command
        cmd = [
            "vlc",
            "--fullscreen",
            "--no-video-title-show",
            "--intf", "dummy",  # No interface
            "--play-and-exit",  # Exit when done
            str(episode_file)
        ]

        try:
            self.logger.info(f"🎬 JARVIS: Launching VLC in full screen mode...")
            subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            self.logger.info("   ✅ VLC launched in full screen")
            return True
        except FileNotFoundError:
            self.logger.warning("   ⚠️  VLC not found, trying alternative player...")
            return self.play_episode(episode_id, fullscreen=True)
        except Exception as e:
            self.logger.error(f"   ❌ VLC launch failed: {e}")
            return self.play_episode(episode_id, fullscreen=True)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Episode Player")
    parser.add_argument("--episode", "-e", default="S01E01", help="Episode ID (default: S01E01)")
    parser.add_argument("--vlc", action="store_true", help="Force VLC player")

    args = parser.parse_args()

    print("="*80)
    print("JARVIS EPISODE PLAYER - FULL SCREEN")
    print("="*80)

    player = JARVISEpisodePlayer()

    if args.vlc:
        success = player.play_with_vlc_fullscreen(args.episode)
    else:
        success = player.play_episode(args.episode, fullscreen=True)

    if success:
        print(f"\n✅ Episode {args.episode} is now playing in full screen!")
        print("   Press ESC or close the player window to exit.")
    else:
        print(f"\n❌ Failed to launch episode player")
        print("   Please ensure a media player (VLC, Windows Media Player) is installed.")

    print("="*80)


if __name__ == "__main__":


    main()