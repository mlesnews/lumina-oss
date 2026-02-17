#!/usr/bin/env python3
"""
Content Creation Status Report

Status of *.txt-md-json + @HOLOCRON + YouTube/Social Media Video Creator Content

NOT to be confused with "holo/holovid/video" etc.

Tags: #content_creation #holocron #youtube #social_media #video_creator #status
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("ContentCreationStatus")


class ContentType(Enum):
    """Content types"""
    TEXT = "txt"
    MARKDOWN = "md"
    JSON = "json"
    HOLOCRON = "holocron"
    YOUTUBE = "youtube"
    SOCIAL_MEDIA = "social_media"
    VIDEO = "video"


class ComponentStatus(Enum):
    """Component status"""
    OPERATIONAL = "operational"
    PARTIAL = "partial"
    NOT_IMPLEMENTED = "not_implemented"
    BLOCKED = "blocked"
    UNKNOWN = "unknown"


@dataclass
class ContentComponent:
    """Content creation component"""
    name: str
    content_type: ContentType
    status: ComponentStatus
    file_path: Optional[str] = None
    description: str = ""
    dependencies: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result['content_type'] = self.content_type.value
        result['status'] = self.status.value
        return result


class ContentCreationStatusReport:
    """
    Status report for content creation system

    *.txt-md-json + @HOLOCRON + YouTube/Social Media Video Creator
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.scripts_dir = self.project_root / "scripts" / "python"

        logger.info("=" * 80)
        logger.info("📊 CONTENT CREATION STATUS REPORT")
        logger.info("=" * 80)
        logger.info("   Scope: *.txt-md-json + @HOLOCRON + YouTube/Social Media")
        logger.info("   Note: NOT holo/holovid/video (different system)")
        logger.info("=" * 80)
        logger.info("")

    def check_holocron_system(self) -> List[ContentComponent]:
        """Check @HOLOCRON system"""
        components = []

        holocron_files = [
            "holocron_compound_logging_system.py",
            "lumina_holocron_video_generator.py"
        ]

        for file_name in holocron_files:
            file_path = self.scripts_dir / file_name
            exists = file_path.exists()

            if exists:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "FFmpeg" in content or "video" in content.lower():
                            status = ComponentStatus.PARTIAL if "not available" in content.lower() else ComponentStatus.OPERATIONAL
                        else:
                            status = ComponentStatus.OPERATIONAL
                except:
                    status = ComponentStatus.UNKNOWN
            else:
                status = ComponentStatus.NOT_IMPLEMENTED

            components.append(ContentComponent(
                name=file_name.replace('.py', ''),
                content_type=ContentType.HOLOCRON,
                status=status,
                file_path=str(file_path) if exists else None,
                description=f"Holocron system component: {file_name}"
            ))

        return components

    def check_youtube_system(self) -> List[ContentComponent]:
        """Check YouTube content creation"""
        components = []

        youtube_files = [
            "jarvis_syphon_youtube_financial_creators.py"
        ]

        for file_name in youtube_files:
            file_path = self.scripts_dir / file_name
            exists = file_path.exists()

            if exists:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "youtube_api_key" in content or "YouTube" in content:
                            status = ComponentStatus.PARTIAL if "not found" in content.lower() else ComponentStatus.OPERATIONAL
                        else:
                            status = ComponentStatus.OPERATIONAL
                except:
                    status = ComponentStatus.UNKNOWN
            else:
                status = ComponentStatus.NOT_IMPLEMENTED

            components.append(ContentComponent(
                name=file_name.replace('.py', ''),
                content_type=ContentType.YOUTUBE,
                status=status,
                file_path=str(file_path) if exists else None,
                description=f"YouTube content creation: {file_name}"
            ))

        return components

    def check_text_md_json_systems(self) -> List[ContentComponent]:
        try:
            """Check text/markdown/JSON content systems"""
            components = []

            # Check for text/markdown/JSON processing
            text_files = [
                "standardized_timestamp_logging.py",  # Text logging
                "trace_ask_stack_to_inception.py",  # JSON/Text output
            ]

            for file_name in text_files:
                file_path = self.scripts_dir / file_name
                exists = file_path.exists()

                components.append(ContentComponent(
                    name=file_name.replace('.py', ''),
                    content_type=ContentType.TEXT,
                    status=ComponentStatus.OPERATIONAL if exists else ComponentStatus.NOT_IMPLEMENTED,
                    file_path=str(file_path) if exists else None,
                    description=f"Text/Markdown/JSON processing: {file_name}"
                ))

            return components

        except Exception as e:
            self.logger.error(f"Error in check_text_md_json_systems: {e}", exc_info=True)
            raise
    def check_video_generation(self) -> List[ContentComponent]:
        """Check video generation system"""
        components = []

        video_files = [
            "lumina_holocron_video_generator.py"
        ]

        for file_name in video_files:
            file_path = self.scripts_dir / file_name
            exists = file_path.exists()

            if exists:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        if "FFmpeg" in content:
                            status = ComponentStatus.PARTIAL if "not available" in content.lower() else ComponentStatus.OPERATIONAL
                        else:
                            status = ComponentStatus.OPERATIONAL
                except:
                    status = ComponentStatus.UNKNOWN
            else:
                status = ComponentStatus.NOT_IMPLEMENTED

            components.append(ContentComponent(
                name=file_name.replace('.py', ''),
                content_type=ContentType.VIDEO,
                status=status,
                file_path=str(file_path) if exists else None,
                description=f"Video generation: {file_name}"
            ))

        return components

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive status report"""
        holocron_components = self.check_holocron_system()
        youtube_components = self.check_youtube_system()
        text_components = self.check_text_md_json_systems()
        video_components = self.check_video_generation()

        all_components = holocron_components + youtube_components + text_components + video_components

        operational_count = sum(1 for c in all_components if c.status == ComponentStatus.OPERATIONAL)
        partial_count = sum(1 for c in all_components if c.status == ComponentStatus.PARTIAL)
        not_impl_count = sum(1 for c in all_components if c.status == ComponentStatus.NOT_IMPLEMENTED)

        overall_status = "PARTIAL"
        if operational_count == len(all_components):
            overall_status = "OPERATIONAL"
        elif not_impl_count > operational_count:
            overall_status = "NOT_READY"

        report = {
            "report_date": datetime.now().isoformat(),
            "overall_status": overall_status,
            "summary": {
                "holocron_components": len(holocron_components),
                "youtube_components": len(youtube_components),
                "text_components": len(text_components),
                "video_components": len(video_components),
                "total_components": len(all_components),
                "operational": operational_count,
                "partial": partial_count,
                "not_implemented": not_impl_count
            },
            "holocron_system": [c.to_dict() for c in holocron_components],
            "youtube_system": [c.to_dict() for c in youtube_components],
            "text_md_json_systems": [c.to_dict() for c in text_components],
            "video_generation": [c.to_dict() for c in video_components],
            "note": "NOT to be confused with 'holo/holovid/video' - this is the content creation system for *.txt-md-json + @HOLOCRON + YouTube/Social Media"
        }

        return report

    def print_report(self):
        """Print formatted status report"""
        report = self.generate_report()

        print("\n" + "=" * 80)
        print("📊 CONTENT CREATION STATUS REPORT")
        print("=" * 80)
        print(f"Report Date: {report['report_date']}")
        print(f"Overall Status: {report['overall_status']}")
        print("")
        print("📋 SCOPE")
        print("-" * 80)
        print("   *.txt-md-json + @HOLOCRON + YouTube/Social Media Video Creator")
        print("   NOTE: NOT holo/holovid/video (different system)")
        print("")

        print("📈 SUMMARY")
        print("-" * 80)
        print(f"Holocron Components: {report['summary']['holocron_components']}")
        print(f"YouTube Components: {report['summary']['youtube_components']}")
        print(f"Text/MD/JSON Components: {report['summary']['text_components']}")
        print(f"Video Components: {report['summary']['video_components']}")
        print(f"Total: {report['summary']['total_components']}")
        print(f"Operational: {report['summary']['operational']}")
        print(f"Partial: {report['summary']['partial']}")
        print(f"Not Implemented: {report['summary']['not_implemented']}")
        print("")

        print("📚 @HOLOCRON SYSTEM")
        print("-" * 80)
        for comp in report['holocron_system']:
            status_icon = "✅" if comp['status'] == "operational" else "⚠️" if comp['status'] == "partial" else "❌"
            print(f"{status_icon} {comp['name']}: {comp['status']}")
        print("")

        print("📺 YOUTUBE SYSTEM")
        print("-" * 80)
        for comp in report['youtube_system']:
            status_icon = "✅" if comp['status'] == "operational" else "⚠️" if comp['status'] == "partial" else "❌"
            print(f"{status_icon} {comp['name']}: {comp['status']}")
        print("")

        print("📝 TEXT/MD/JSON SYSTEMS")
        print("-" * 80)
        for comp in report['text_md_json_systems']:
            status_icon = "✅" if comp['status'] == "operational" else "⚠️" if comp['status'] == "partial" else "❌"
            print(f"{status_icon} {comp['name']}: {comp['status']}")
        print("")

        print("🎬 VIDEO GENERATION")
        print("-" * 80)
        for comp in report['video_generation']:
            status_icon = "✅" if comp['status'] == "operational" else "⚠️" if comp['status'] == "partial" else "❌"
            print(f"{status_icon} {comp['name']}: {comp['status']}")
        print("")

        print("=" * 80)
        print("")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Content Creation Status Report")
        parser.add_argument('--json', action='store_true', help='Output as JSON')
        parser.add_argument('--save', type=str, metavar='FILE', help='Save report to file')

        args = parser.parse_args()

        reporter = ContentCreationStatusReport()

        if args.json:
            report = reporter.generate_report()
            print(json.dumps(report, indent=2))
        else:
            reporter.print_report()

        if args.save:
            report = reporter.generate_report()
            output_file = Path(args.save)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, default=str)
            logger.info(f"💾 Report saved to: {output_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()