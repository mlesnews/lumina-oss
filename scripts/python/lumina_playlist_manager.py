#!/usr/bin/env python3
"""
LUMINA Playlist Manager

Manages YouTube playlists for multimedia storytelling.
Creates, updates, and organizes playlists.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINAPlaylistManager")


class LUMINAPlaylistManager:
    """
    Manages YouTube playlists

    Creates and organizes playlists for multimedia storytelling
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        self.playlists_dir = project_root / "data" / "multimedia" / "playlists"
        self.playlists_dir.mkdir(parents=True, exist_ok=True)

    def create_playlist(self, title: str, description: str,
                       privacy: str = "private") -> Dict[str, Any]:
        """
        Create a new playlist

        Args:
            title: Playlist title
            description: Playlist description
            privacy: Privacy setting (private, unlisted, public)

        Returns:
            Playlist data
        """
        playlist = {
            'playlist_id': f"playlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'title': title,
            'description': description,
            'privacy': privacy,
            'videos': [],
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        }

        # Save playlist
        playlist_file = self.playlists_dir / f"{playlist['playlist_id']}.json"
        try:
            with open(playlist_file, 'w') as f:
                json.dump(playlist, f, indent=2)
            self.logger.info(f"✅ Created playlist: {playlist['playlist_id']}")
        except Exception as e:
            self.logger.error(f"Failed to save playlist: {e}")
            return {
                'success': False,
                'error': str(e)
            }

        return {
            'success': True,
            'playlist': playlist
        }

    def add_video_to_playlist(self, playlist_id: str, video_id: str,
                             position: Optional[int] = None) -> Dict[str, Any]:
        """
        Add a video to a playlist

        Args:
            playlist_id: Playlist ID
            video_id: YouTube video ID
            position: Optional position in playlist
        """
        playlist_file = self.playlists_dir / f"{playlist_id}.json"

        if not playlist_file.exists():
            return {
                'success': False,
                'error': f'Playlist not found: {playlist_id}'
            }

        try:
            with open(playlist_file, 'r') as f:
                playlist = json.load(f)

            video_entry = {
                'video_id': video_id,
                'added_at': datetime.now().isoformat(),
                'position': position or len(playlist.get('videos', []))
            }

            if 'videos' not in playlist:
                playlist['videos'] = []

            playlist['videos'].append(video_entry)
            playlist['updated_at'] = datetime.now().isoformat()

            with open(playlist_file, 'w') as f:
                json.dump(playlist, f, indent=2)

            self.logger.info(f"✅ Added video {video_id} to playlist {playlist_id}")

            return {
                'success': True,
                'playlist': playlist
            }

        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to add video: {e}'
            }

    def get_playlist(self, playlist_id: str) -> Dict[str, Any]:
        """Get playlist data"""
        playlist_file = self.playlists_dir / f"{playlist_id}.json"

        if not playlist_file.exists():
            return {
                'success': False,
                'error': f'Playlist not found: {playlist_id}'
            }

        try:
            with open(playlist_file, 'r') as f:
                playlist = json.load(f)

            return {
                'success': True,
                'playlist': playlist
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to load playlist: {e}'
            }

    def list_playlists(self) -> List[Dict[str, Any]]:
        """List all playlists"""
        playlists = []

        for playlist_file in self.playlists_dir.glob("playlist_*.json"):
            try:
                with open(playlist_file, 'r') as f:
                    playlists.append(json.load(f))
            except Exception as e:
                self.logger.error(f"Failed to load {playlist_file}: {e}")

        return playlists


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Playlist Manager")
        parser.add_argument("--create", action="store_true", help="Create a playlist")
        parser.add_argument("--title", type=str, help="Playlist title")
        parser.add_argument("--description", type=str, help="Playlist description")
        parser.add_argument("--add-video", action="store_true", help="Add video to playlist")
        parser.add_argument("--playlist-id", type=str, help="Playlist ID")
        parser.add_argument("--video-id", type=str, help="Video ID")
        parser.add_argument("--list", action="store_true", help="List all playlists")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = LUMINAPlaylistManager(project_root)

        if args.create:
            if not args.title:
                print("❌ Please provide --title")
                return

            result = manager.create_playlist(
                title=args.title,
                description=args.description or ""
            )

            if result.get('success'):
                print(f"\n✅ Created playlist: {result['playlist']['playlist_id']}")
                print(f"   Title: {result['playlist']['title']}")
            else:
                print(f"❌ Error: {result.get('error')}")

        elif args.add_video:
            if not args.playlist_id or not args.video_id:
                print("❌ Please provide --playlist-id and --video-id")
                return

            result = manager.add_video_to_playlist(args.playlist_id, args.video_id)

            if result.get('success'):
                print(f"\n✅ Added video to playlist")
            else:
                print(f"❌ Error: {result.get('error')}")

        elif args.list:
            playlists = manager.list_playlists()
            print(f"\n📋 Playlists: {len(playlists)}")
            for playlist in playlists:
                print(f"\n  {playlist['title']}")
                print(f"    ID: {playlist['playlist_id']}")
                print(f"    Videos: {len(playlist.get('videos', []))}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()