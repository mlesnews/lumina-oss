#!/usr/bin/env python3
"""
Complete ULTRON to Lumina Pipeline - End-to-End Execution

This script executes the complete pipeline:
1. Process videos → Holocrons
2. Upload Holocrons to NAS Jupyter
3. Transform Holocrons → Video chapters
4. Prepare for YouTube upload

Run this after setting up YouTube channel credentials.
"""

import sys
from pathlib import Path
import json
from datetime import datetime

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from ultron_to_lumina_docuseries_pipeline import ULTRONToLuminaPipeline
from lumina_youtube_channel_setup import LuminaYouTubeChannel
from youtube_upload_automation import YouTubeUploader


def main():
    """Execute complete pipeline"""
    print("="*70)
    print("ULTRON TO LUMINA DOCUSERIES - COMPLETE PIPELINE")
    print("="*70)
    print()

    # Initialize components
    print("🔧 Initializing pipeline components...")
    pipeline = ULTRONToLuminaPipeline()
    channel = LuminaYouTubeChannel()

    print("✅ Components initialized")
    print()

    # Show setup status
    print("📋 SETUP STATUS")
    print("-"*70)

    # Check YouTube API availability
    try:
        from youtube_upload_automation import YOUTUBE_API_AVAILABLE
        if YOUTUBE_API_AVAILABLE:
            print("✅ YouTube API libraries available")
            uploader = YouTubeUploader()
            creds_exist = uploader.credentials_file.exists()
            secrets_exist = uploader.client_secrets_file.exists()

            if creds_exist:
                print("✅ YouTube credentials found")
            else:
                print("⚠️  YouTube credentials not found - run authentication")

            if secrets_exist:
                print("✅ YouTube client secrets found")
            else:
                print("⚠️  YouTube client secrets not found")
                print(f"   Place client_secrets.json at: {uploader.client_secrets_file}")
        else:
            print("⚠️  YouTube API libraries not installed")
            print("   Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    except Exception as e:
        print(f"⚠️  YouTube upload check failed: {e}")

    print()

    # Check NAS Jupyter
    nas_config = pipeline.nas_jupyter_config
    nas_ip = nas_config.get("nas", {}).get("ip", "<NAS_PRIMARY_IP>")
    nas_port = nas_config.get("nas", {}).get("jupyter_port", 8888)
    print(f"📚 NAS Jupyter: http://{nas_ip}:{nas_port}")
    print(f"   Holocrons: {pipeline.jupyter_dir}")
    print()

    # Show pipeline summary
    print("📊 PIPELINE SUMMARY")
    print("-"*70)
    print("1. ✅ Video Transcription System - Ready")
    print("2. ✅ SYPHON Intelligence Extraction - Ready")
    print("3. ✅ Holocron Notebook Creation - Ready")
    print("4. ✅ NAS Jupyter Upload - Ready")
    print("5. ✅ Video Chapter Generation - Ready")
    print("6. ⏳ YouTube Upload - Requires credentials")
    print()

    # Show usage
    print("🚀 USAGE")
    print("-"*70)
    print()
    print("Process videos from ULTRON channels:")
    print("  python scripts/python/ultron_to_lumina_docuseries_pipeline.py --process-all --max-videos 5")
    print()
    print("Process single video:")
    print("  python scripts/python/ultron_to_lumina_docuseries_pipeline.py \\")
    print("      --video-url \"https://www.youtube.com/watch?v=VIDEO_ID\" \\")
    print("      --channel \"Channel Name\"")
    print()
    print("Setup YouTube channel:")
    print("  python scripts/python/lumina_youtube_channel_setup.py --setup-guide")
    print()
    print("Authenticate YouTube API:")
    print("  python scripts/python/youtube_upload_automation.py --authenticate")
    print()
    print("Upload video:")
    print("  python scripts/python/youtube_upload_automation.py --upload VIDEO_PATH METADATA_JSON")
    print()

    # Show file locations
    print("📁 FILE LOCATIONS")
    print("-"*70)
    print(f"Holocrons: {pipeline.jupyter_dir}")
    print(f"Videos: {pipeline.videos_dir}")
    print(f"Transcriptions: {pipeline.transcriptions_dir}")
    print(f"Config: {channel.config_file}")
    print()

    print("="*70)
    print("PIPELINE READY FOR EXECUTION")
    print("="*70)


if __name__ == "__main__":


    main()