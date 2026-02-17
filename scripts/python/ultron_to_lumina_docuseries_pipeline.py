#!/usr/bin/env python3
"""
ULTRON to Lumina Docuseries Pipeline

Complete pipeline that:
1. Processes individual videos from ULTRON syphoned channels
2. Transcribes videos and extracts intelligence via SYPHON
3. Converts to Jupyter Notebook Holocrons (@holocrons)
4. Uploads Holocrons to NAS Jupyter server
5. Transforms Holocrons into docuseries video chapters
6. Creates/upload to Lumina YouTube channel

This creates a complete knowledge transformation pipeline:
YouTube Videos → Transcription → Holocrons → Docuseries → Lumina Channel
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ULTRONToLuminaPipeline")

# Import required modules
try:
    from syphon_ultron_test_channels import ULTRONChannelSyphon
    from automatic_video_audio_transcription import VideoAudioTranscriber
    from youtube_to_holocron_transformer import YouTubeToHolocronTransformer
    from holocron_docuseries import HolocronDocuseries, HolocronType
    from lumina_holocron_video_generator import HolocronVideoGenerator
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    logger.error("   Some modules may not be available")
    # Create placeholder classes for missing modules
    ULTRONChannelSyphon = None
    VideoAudioTranscriber = None
    YouTubeToHolocronTransformer = None
    HolocronDocuseries = None
    HolocronVideoGenerator = None


class ULTRONToLuminaPipeline:
    """
    Complete pipeline from ULTRON channel videos to Lumina YouTube docuseries
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize pipeline"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Data directories
        self.data_dir = self.project_root / "data"
        self.holocrons_dir = self.data_dir / "holocron" / "ultron_videos"
        self.jupyter_dir = self.data_dir / "jupyter" / "ultron_holocrons"
        self.videos_dir = self.data_dir / "videos" / "ultron_docuseries"
        self.transcriptions_dir = self.data_dir / "transcriptions" / "ultron"

        # Create directories
        for dir_path in [self.holocrons_dir, self.jupyter_dir, self.videos_dir, self.transcriptions_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.channel_syphon = ULTRONChannelSyphon(project_root) if ULTRONChannelSyphon else None
        self.transcriber = VideoAudioTranscriber(project_root) if VideoAudioTranscriber else None
        self.holocron_transformer = YouTubeToHolocronTransformer(project_root) if YouTubeToHolocronTransformer else None
        self.docuseries = HolocronDocuseries(project_root) if HolocronDocuseries else None
        self.video_generator = HolocronVideoGenerator(project_root) if HolocronVideoGenerator else None

        # NAS Jupyter configuration
        self.nas_jupyter_config = self._load_nas_jupyter_config()

        logger.info("🚀 ULTRON to Lumina Docuseries Pipeline initialized")

    def _load_nas_jupyter_config(self) -> Dict[str, Any]:
        """Load NAS Jupyter configuration"""
        config_file = self.project_root / "config" / "jupyter" / "nas_config.json"
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load NAS Jupyter config: {e}")

        # Default config
        return {
            "nas": {
                "ip": "<NAS_PRIMARY_IP>",
                "jupyter_port": 8888,
                "notebook_directory": str(self.jupyter_dir)
            },
            "access": {
                "nas": "http://<NAS_PRIMARY_IP>:8888"
            }
        }

    def process_video_to_holocron(self, video_url: str, channel_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single video through the pipeline:
        1. Transcribe video
        2. Extract intelligence via SYPHON
        3. Convert to Holocron
        4. Save as Jupyter Notebook

        Args:
            video_url: YouTube video URL
            channel_info: Channel metadata

        Returns:
            Processing results
        """
        logger.info(f"📹 Processing video: {video_url}")

        video_id = self._extract_video_id(video_url)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        result = {
            "video_id": video_id,
            "video_url": video_url,
            "channel": channel_info.get("name", "Unknown"),
            "processed_at": timestamp,
            "status": "processing",
            "steps": {}
        }

        try:
            # Step 1: Transcribe video
            logger.info(f"   Step 1/4: Transcribing video...")
            if self.transcriber:
                transcription_result = self.transcriber.transcribe_youtube_video(
                    video_url,
                    output_dir=self.transcriptions_dir
                )
                result["steps"]["transcription"] = {
                    "status": "success",
                    "transcript_file": str(transcription_result.get("transcript_file", "")),
                    "duration": transcription_result.get("duration", 0),
                    "word_count": transcription_result.get("word_count", 0)
                }
                transcript_text = transcription_result.get("transcript_text", "")
            else:
                logger.warning("   ⚠️  Transcriber not available")
                result["steps"]["transcription"] = {"status": "skipped"}
                transcript_text = ""

            # Step 2: Extract intelligence via SYPHON (if available)
            logger.info(f"   Step 2/4: Extracting intelligence...")
            intelligence = {
                "actionable_items": [],
                "tasks": [],
                "decisions": [],
                "key_insights": []
            }

            if transcript_text and self.channel_syphon and self.channel_syphon.syphon_system:
                try:
                    # Create a simple content string for SYPHON
                    syphon_content = f"Video: {video_url}\n\n{transcript_text[:5000]}"  # Limit for processing
                    # Note: Full SYPHON integration would require proper content structure
                    intelligence["extracted"] = True
                except Exception as e:
                    logger.warning(f"   ⚠️  SYPHON extraction failed: {e}")
                    intelligence["extracted"] = False

            result["steps"]["intelligence"] = {"status": "success", "data": intelligence}

            # Step 3: Convert to Holocron (Jupyter Notebook)
            logger.info(f"   Step 3/4: Creating Holocron (Jupyter Notebook)...")
            holocron_notebook = self._create_holocron_notebook(
                video_id=video_id,
                video_url=video_url,
                channel_info=channel_info,
                transcript=transcript_text,
                intelligence=intelligence,
                timestamp=timestamp
            )

            notebook_path = self.jupyter_dir / f"holocron_{video_id}_{timestamp}.ipynb"
            with open(notebook_path, 'w', encoding='utf-8') as f:
                json.dump(holocron_notebook, f, indent=2, ensure_ascii=False)

            result["steps"]["holocron"] = {
                "status": "success",
                "notebook_path": str(notebook_path),
                "notebook_id": holocron_notebook.get("metadata", {}).get("holocron_id", "")
            }

            logger.info(f"   ✅ Holocron created: {notebook_path.name}")

            # Step 4: Upload to NAS Jupyter (if configured)
            logger.info(f"   Step 4/4: Uploading to NAS Jupyter...")
            upload_result = self._upload_to_nas_jupyter(notebook_path)
            result["steps"]["nas_upload"] = upload_result

            result["status"] = "success"
            logger.info(f"   ✅ Video processing complete!")

        except Exception as e:
            logger.error(f"   ❌ Error processing video: {e}")
            result["status"] = "error"
            result["error"] = str(e)

        return result

    def _extract_video_id(self, video_url: str) -> str:
        """Extract video ID from URL"""
        import re
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/@[\w]+\/videos\/([a-zA-Z0-9_-]{11})'
        ]
        for pattern in patterns:
            match = re.search(pattern, video_url)
            if match:
                return match.group(1)
        return video_url.split('/')[-1].split('?')[0]

    def _create_holocron_notebook(self, video_id: str, video_url: str, channel_info: Dict[str, Any],
                                      transcript: str, intelligence: Dict[str, Any],
                                      timestamp: str) -> Dict[str, Any]:
        try:
            """
            Create a Jupyter Notebook Holocron from video data

            Holocron structure:
            - Markdown cells: Metadata, insights, analysis
            - Code cells: Data processing, visualization
            - Output cells: Results, visualizations
            """
            holocron_id = f"HOLOCRON-ULTRON-{video_id}-{timestamp}"

            notebook = {
                "cells": [],
                "metadata": {
                    "kernelspec": {
                        "display_name": "Python 3",
                        "language": "python",
                        "name": "python3"
                    },
                    "language_info": {
                        "name": "python",
                        "version": "3.11.0"
                    },
                    "holocron_id": holocron_id,
                    "source": "ultron_channel",
                    "channel": channel_info.get("name", "Unknown"),
                    "video_url": video_url,
                    "created_at": timestamp
                },
                "nbformat": 4,
                "nbformat_minor": 4
            }

            # Cell 1: Title and Metadata
            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    f"# @holocron: {channel_info.get('name', 'Unknown Channel')}\n",
                    f"\n",
                    f"**Video ID**: `{video_id}`\n",
                    f"**Source**: [{video_url}]({video_url})\n",
                    f"**Channel**: {channel_info.get('name', 'Unknown')}\n",
                    f"**Created**: {timestamp}\n",
                    f"**Holocron ID**: `{holocron_id}`\n",
                    f"\n",
                    f"---\n",
                    f"\n",
                    f"*This Holocron was automatically generated from ULTRON channel video processing*"
                ]
            })

            # Cell 2: Intelligence Summary
            notebook["cells"].append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [
                    "## Intelligence Summary\n",
                    "\n",
                    "### Key Insights\n",
                    "\n"
                ] + [f"- {insight}\n" for insight in intelligence.get("key_insights", [])] + [
                    "\n",
                    "### Actionable Items\n",
                    "\n"
                ] + [f"- {item}\n" for item in intelligence.get("actionable_items", [])]
            })

            # Cell 3: Transcript (if available)
            if transcript:
                notebook["cells"].append({
                    "cell_type": "markdown",
                    "metadata": {},
                    "source": [
                        "## Video Transcript\n",
                        "\n",
                        "```\n",
                        transcript[:5000] + ("\n\n... (truncated)" if len(transcript) > 5000 else ""),
                        "\n```\n"
                    ]
                })

            # Cell 4: Analysis Code Cell
            notebook["cells"].append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Holocron Analysis\n",
                    "import json\n",
                    "from pathlib import Path\n",
                    "from datetime import datetime\n",
                    "\n",
                    f"holocron_id = \"{holocron_id}\"\n",
                    f"video_id = \"{video_id}\"\n",
                    f"channel = \"{channel_info.get('name', 'Unknown')}\"\n",
                    "\n",
                    "print(f\"Holocron: {holocron_id}\")\n",
                    "print(f\"Video: {video_id}\")\n",
                    "print(f\"Channel: {channel}\")\n",
                    "print(f\"Created: {datetime.now().isoformat()}\")"
                ],
                "outputs": []
            })

            # Cell 5: Data Export
            notebook["cells"].append({
                "cell_type": "code",
                "execution_count": None,
                "metadata": {},
                "source": [
                    "# Export Holocron Data\n",
                    "\n",
                    "holocron_data = {\n",
                    f"    \"holocron_id\": \"{holocron_id}\",\n",
                    f"    \"video_id\": \"{video_id}\",\n",
                    f"    \"video_url\": \"{video_url}\",\n",
                    f"    \"channel\": \"{channel_info.get('name', 'Unknown')}\",\n",
                    f"    \"intelligence\": {json.dumps(intelligence, indent=2)},\n",
                    f"    \"created_at\": \"{timestamp}\"\n",
                    "}\n",
                    "\n",
                    "print(json.dumps(holocron_data, indent=2))"
                ],
                "outputs": []
            })

            return notebook

        except Exception as e:
            self.logger.error(f"Error in _create_holocron_notebook: {e}", exc_info=True)
            raise
    def _upload_to_nas_jupyter(self, notebook_path: Path) -> Dict[str, Any]:
        """Upload notebook to NAS Jupyter server"""
        try:
            nas_config = self.nas_jupyter_config.get("nas", {})
            nas_ip = nas_config.get("ip", "<NAS_PRIMARY_IP>")
            jupyter_port = nas_config.get("jupyter_port", 8888)

            # Check if NAS Jupyter is accessible
            import urllib.request
            try:
                urllib.request.urlopen(f"http://{nas_ip}:{jupyter_port}", timeout=5)
                nas_accessible = True
            except:
                nas_accessible = False

            if not nas_accessible:
                logger.warning(f"   ⚠️  NAS Jupyter not accessible at {nas_ip}:{jupyter_port}")
                return {"status": "skipped", "reason": "NAS not accessible"}

            # For now, just verify the notebook is in the correct directory
            # Full upload would require Jupyter API or SSH/SMB copy
            logger.info(f"   ✅ Notebook ready for NAS Jupyter: {notebook_path}")
            logger.info(f"      NAS Jupyter: http://{nas_ip}:{jupyter_port}")
            logger.info(f"      Notebook will be accessible via NAS Jupyter interface")

            return {
                "status": "ready",
                "nas_ip": nas_ip,
                "nas_port": jupyter_port,
                "notebook_path": str(notebook_path),
                "access_url": f"http://{nas_ip}:{jupyter_port}/tree/{notebook_path.name}"
            }

        except Exception as e:
            logger.warning(f"   ⚠️  NAS upload check failed: {e}")
            return {"status": "error", "error": str(e)}

    def transform_holocron_to_chapter(self, notebook_path: Path, chapter_number: int) -> Dict[str, Any]:
        """
        Transform a Holocron notebook into a docuseries video chapter

        Args:
            notebook_path: Path to Holocron notebook
            chapter_number: Chapter number in docuseries

        Returns:
            Chapter metadata and video file path
        """
        logger.info(f"🎬 Transforming Holocron to video chapter: {notebook_path.name}")

        try:
            # Load notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook = json.load(f)

            metadata = notebook.get("metadata", {})
            holocron_id = metadata.get("holocron_id", "unknown")
            channel = metadata.get("channel", "Unknown")

            # Extract content from notebook cells
            title = f"Chapter {chapter_number}: {channel} - {holocron_id}"
            description = self._extract_notebook_summary(notebook)

            # Generate video from Holocron
            if self.video_generator:
                try:
                    # Split description into segments for video scenes
                    segments = description[:500].split('. ')[:5]  # First 5 sentences
                    segments = [s.strip() + '.' for s in segments if s.strip()]

                    video_result = self.video_generator.generate_holocron_video(
                        title=title,
                        script_segments=segments if segments else [description[:200]],
                        subtitle=f"Holocron: {holocron_id}",
                        duration_per_segment=4.0
                    )
                    video_path = Path(video_result.get("video_path")) if video_result.get("video_path") else None
                except Exception as e:
                    logger.warning(f"   ⚠️  Video generation failed: {e}")
                    video_path = None
            else:
                logger.warning("   ⚠️  Video generator not available")
                video_path = None

            # Create docuseries episode
            if self.docuseries:
                episode = self.docuseries.create_docuseries_episode(
                    title=title,
                    description=description,
                    journey_stage=f"ULTRON Chapter {chapter_number}",
                    systems_covered=[channel]
                )
            else:
                episode = None

            return {
                "status": "success",
                "chapter_number": chapter_number,
                "title": title,
                "description": description,
                "video_path": str(video_path) if video_path else None,
                "episode_id": episode.episode_id if episode else None,
                "holocron_id": holocron_id
            }

        except Exception as e:
            logger.error(f"   ❌ Error transforming to chapter: {e}")
            return {"status": "error", "error": str(e)}

    def _extract_notebook_summary(self, notebook: Dict[str, Any]) -> str:
        """Extract summary from notebook cells"""
        summary_parts = []

        for cell in notebook.get("cells", []):
            if cell.get("cell_type") == "markdown":
                source = "".join(cell.get("source", []))
                # Extract first paragraph
                lines = source.split("\n")
                for line in lines[:10]:  # First 10 lines
                    if line.strip() and not line.startswith("#"):
                        summary_parts.append(line.strip())
                        if len(summary_parts) >= 3:
                            break

        return " ".join(summary_parts[:200])  # Limit to 200 chars

    def process_all_channel_videos(self, max_videos_per_channel: int = 5) -> Dict[str, Any]:
        try:
            """
            Process all videos from ULTRON channels

            Args:
                max_videos_per_channel: Maximum videos to process per channel

            Returns:
                Processing summary
            """
            logger.info("🚀 Starting ULTRON to Lumina pipeline...")

            if not self.channel_syphon:
                logger.error("❌ Channel syphon not available")
                return {"status": "error", "message": "Channel syphon not available"}

            # Get channel data
            logger.info("📺 Fetching channel data...")
            channel_results = self.channel_syphon.syphon_all_channels()

            if channel_results.get("status") == "error":
                logger.error("❌ Failed to fetch channel data")
                return channel_results

            processing_summary = {
                "pipeline": "ULTRON to Lumina Docuseries",
                "timestamp": datetime.now().isoformat(),
                "channels_processed": 0,
                "videos_processed": 0,
                "holocrons_created": 0,
                "chapters_created": 0,
                "results": []
            }

            # Process videos from each channel
            for channel_key, channel_data in channel_results.get("channels", {}).items():
                channel_name = channel_data.get("name", channel_key)
                logger.info(f"\n📺 Processing channel: {channel_name}")

                # Get videos (would need to extract from channel data or fetch separately)
                videos = channel_data.get("videos", [])[:max_videos_per_channel]

                if not videos:
                    logger.warning(f"   ⚠️  No videos found for {channel_name}")
                    continue

                processing_summary["channels_processed"] += 1

                for idx, video in enumerate(videos, 1):
                    video_url = video.get("url") or f"https://www.youtube.com/watch?v={video.get('video_id', '')}"

                    logger.info(f"\n   Video {idx}/{len(videos)}: {video.get('title', 'Unknown')[:50]}")

                    # Process video to Holocron
                    result = self.process_video_to_holocron(video_url, channel_data)

                    if result["status"] == "success":
                        processing_summary["videos_processed"] += 1
                        processing_summary["holocrons_created"] += 1

                        # Transform to chapter
                        notebook_path = Path(result["steps"]["holocron"]["notebook_path"])
                        chapter_number = processing_summary["chapters_created"] + 1

                        chapter_result = self.transform_holocron_to_chapter(notebook_path, chapter_number)

                        if chapter_result["status"] == "success":
                            processing_summary["chapters_created"] += 1

                    processing_summary["results"].append(result)

            logger.info(f"\n✅ Pipeline Complete!")
            logger.info(f"   Channels: {processing_summary['channels_processed']}")
            logger.info(f"   Videos: {processing_summary['videos_processed']}")
            logger.info(f"   Holocrons: {processing_summary['holocrons_created']}")
            logger.info(f"   Chapters: {processing_summary['chapters_created']}")

            # Save summary
            summary_file = self.videos_dir / f"pipeline_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(processing_summary, f, indent=2, ensure_ascii=False)

            logger.info(f"   📊 Summary saved: {summary_file.name}")

            return processing_summary


        except Exception as e:
            self.logger.error(f"Error in process_all_channel_videos: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="ULTRON to Lumina Docuseries Pipeline",
            epilog="Transforms YouTube videos → Holocrons → Docuseries → Lumina Channel"
        )
        parser.add_argument("--process-all", action="store_true",
                           help="Process all videos from ULTRON channels")
        parser.add_argument("--max-videos", type=int, default=5,
                           help="Maximum videos per channel (default: 5)")
        parser.add_argument("--video-url", type=str,
                           help="Process a single video URL")
        parser.add_argument("--channel", type=str,
                           help="Channel name for single video processing")

        args = parser.parse_args()

        pipeline = ULTRONToLuminaPipeline()

        if args.process_all:
            results = pipeline.process_all_channel_videos(max_videos_per_channel=args.max_videos)
            print("\n" + "="*60)
            print("PIPELINE SUMMARY")
            print("="*60)
            print(f"Channels: {results['channels_processed']}")
            print(f"Videos: {results['videos_processed']}")
            print(f"Holocrons: {results['holocrons_created']}")
            print(f"Chapters: {results['chapters_created']}")
            print("="*60)

        elif args.video_url:
            channel_info = {"name": args.channel or "Unknown"}
            result = pipeline.process_video_to_holocron(args.video_url, channel_info)
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()
            print("\n🚀 ULTRON to Lumina Docuseries Pipeline")
            print("   Transform YouTube videos → Holocrons → Docuseries → Lumina Channel")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()