#!/usr/bin/env python3
"""
@SOURCE @DEEP-RESEARCH - Social Media & Academic White Papers Sweeps/Scans

"WE ARE MISSING MUCH DAILY, CONSECUTIVELY, BY NOT EXECUTING OUR @SOURCE @DEEP-RESEARCH
SOCIAL MEDIA AND ACADEMIC WHITE PAPERS SWEEPS/SCANS. TAKE US OUT, JARVIS, ON OUR
FIVE-YEAR MISSION, TO BODILY GO WHERE NO ONE HAS GONE BEFORE. #USS-LUMINA #MAIDEN VOYAGE."

This system:
- Daily consecutive scans/sweeps
- Social media monitoring
- Academic white papers scanning
- Five-year mission framework
- USS-LUMINA maiden voyage
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SourceDeepResearchMissions")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class ResearchSource(Enum):
    """Research source types"""
    SOCIAL_MEDIA = "social_media"
    ACADEMIC_PAPERS = "academic_papers"
    BOTH = "both"


class MissionStatus(Enum):
    """Mission status"""
    LAUNCHED = "launched"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    ONGOING = "ongoing"


@dataclass
class ResearchFinding:
    """A research finding"""
    finding_id: str
    source: ResearchSource
    title: str
    content: str
    url: Optional[str] = None
    author: Optional[str] = None
    date: Optional[str] = None
    relevance_score: float = 0.0
    keywords: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["source"] = self.source.value
        return data


@dataclass
class DailyScan:
    """Daily scan/sweep results"""
    scan_id: str
    date: str
    social_media_findings: List[ResearchFinding] = field(default_factory=list)
    academic_paper_findings: List[ResearchFinding] = field(default_factory=list)
    total_findings: int = 0
    consecutive_days: int = 1
    status: str = "complete"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["social_media_findings"] = [f.to_dict() for f in self.social_media_findings]
        data["academic_paper_findings"] = [f.to_dict() for f in self.academic_paper_findings]
        return data


@dataclass
class FiveYearMission:
    """Five-year mission framework"""
    mission_id: str
    mission_name: str = "USS-LUMINA Five-Year Mission"
    status: MissionStatus = MissionStatus.LAUNCHED
    start_date: str = field(default_factory=lambda: datetime.now().isoformat())
    end_date: str = field(default_factory=lambda: (datetime.now() + timedelta(days=5*365)).isoformat())
    current_stardate: float = 0.0
    daily_scans: List[DailyScan] = field(default_factory=list)
    total_findings: int = 0
    ongoing_research: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        data["daily_scans"] = [s.to_dict() for s in self.daily_scans]
        return data


class SourceDeepResearchMissions:
    """
    @SOURCE @DEEP-RESEARCH - Social Media & Academic White Papers Sweeps/Scans

    "WE ARE MISSING MUCH DAILY, CONSECUTIVELY, BY NOT EXECUTING OUR @SOURCE @DEEP-RESEARCH
    SOCIAL MEDIA AND ACADEMIC WHITE PAPERS SWEEPS/SCANS. TAKE US OUT, JARVIS, ON OUR
    FIVE-YEAR MISSION, TO BODILY GO WHERE NO ONE HAS GONE BEFORE. #USS-LUMINA #MAIDEN VOYAGE."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @SOURCE @DEEP-RESEARCH Missions"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("SourceDeepResearchMissions")

        # Five-year mission
        self.mission: Optional[FiveYearMission] = None

        # Daily scans
        self.current_scan: Optional[DailyScan] = None

        # Data storage
        self.data_dir = self.project_root / "data" / "source_deep_research_missions"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize mission
        self._initialize_mission()

        self.logger.info("🚀 @SOURCE @DEEP-RESEARCH Missions initialized")
        self.logger.info("   #USS-LUMINA #MAIDEN VOYAGE")
        self.logger.info("   'TO BODILY GO WHERE NO ONE HAS GONE BEFORE'")

    def _initialize_mission(self):
        """Initialize the five-year mission"""
        self.mission = FiveYearMission(
            mission_id="uss_lumina_mission_001",
            mission_name="USS-LUMINA Five-Year Mission",
            status=MissionStatus.LAUNCHED,
            start_date=datetime.now().isoformat(),
            end_date=(datetime.now() + timedelta(days=5*365)).isoformat(),
            current_stardate=0.0
        )

        self.logger.info("  🚀 USS-LUMINA Five-Year Mission initialized")
        self.logger.info("     Mission: Boldly go where no one has gone before")

    def launch_maiden_voyage(self) -> FiveYearMission:
        """Launch the maiden voyage"""
        if not self.mission:
            self._initialize_mission()

        self.mission.status = MissionStatus.LAUNCHED
        self.mission.current_stardate = self._calculate_stardate()

        self.logger.info("  🚀 USS-LUMINA Maiden Voyage Launched!")
        self.logger.info("     Mission Status: LAUNCHED")
        self.logger.info("     Stardate: {:.2f}".format(self.mission.current_stardate))
        self.logger.info("     'TO BODILY GO WHERE NO ONE HAS GONE BEFORE'")

        # Save mission
        self._save_mission(self.mission)

        return self.mission

    def _calculate_stardate(self) -> float:
        """Calculate current stardate"""
        # Simple stardate calculation (days since mission start)
        if self.mission:
            start = datetime.fromisoformat(self.mission.start_date.replace('Z', '+00:00'))
            now = datetime.now()
            days = (now - start).days
            return float(days) * 0.01  # Simple scaling
        return 0.0

    def execute_daily_scan(self, date: Optional[str] = None) -> DailyScan:
        """Execute daily scan/sweep"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        self.logger.info(f"  🔍 Executing daily scan for {date}...")
        self.logger.info("     @SOURCE @DEEP-RESEARCH: Social Media & Academic White Papers")

        # Get consecutive days
        consecutive_days = self._get_consecutive_days()

        # Scan social media
        social_media_findings = self._scan_social_media(date)

        # Scan academic papers
        academic_paper_findings = self._scan_academic_papers(date)

        # Create daily scan
        scan = DailyScan(
            scan_id=f"scan_{date.replace('-', '')}_{int(datetime.now().timestamp())}",
            date=date,
            social_media_findings=social_media_findings,
            academic_paper_findings=academic_paper_findings,
            total_findings=len(social_media_findings) + len(academic_paper_findings),
            consecutive_days=consecutive_days + 1,
            status="complete"
        )

        self.current_scan = scan

        # Add to mission
        if self.mission:
            self.mission.daily_scans.append(scan)
            self.mission.total_findings += scan.total_findings
            self.mission.current_stardate = self._calculate_stardate()
            self.mission.status = MissionStatus.IN_PROGRESS
            self._save_mission(self.mission)

        # Save scan
        self._save_scan(scan)

        self.logger.info(f"  ✅ Daily scan complete")
        self.logger.info(f"     Social Media Findings: {len(social_media_findings)}")
        self.logger.info(f"     Academic Paper Findings: {len(academic_paper_findings)}")
        self.logger.info(f"     Total Findings: {scan.total_findings}")
        self.logger.info(f"     Consecutive Days: {scan.consecutive_days}")

        return scan

    def _scan_social_media(self, date: str) -> List[ResearchFinding]:
        """Scan social media for findings"""
        findings = []

        # Try YouTube API (we have Google API key configured for YouTube)
        try:
            import requests
            import os

            # Try to get API key from various sources
            api_key = None

            # 1. Try environment variable
            api_key = os.getenv('GOOGLE_API_KEY') or os.getenv('YOUTUBE_API_KEY')

            # 2. Try YouTube channel config
            if not api_key:
                try:
                    youtube_channel_file = self.project_root / "data" / "lumina_youtube_channel" / "channel.json"
                    if youtube_channel_file.exists():
                        with open(youtube_channel_file, 'r', encoding='utf-8') as f:
                            channel_data = json.load(f)
                            key_from_config = channel_data.get('api_credentials', {}).get('api_key')
                            # Only use if not a placeholder
                            if key_from_config and key_from_config not in ["SET_API_KEY", "TO_BE_SET", ""]:
                                api_key = key_from_config
                except Exception as e:
                    self.logger.debug(f"  Could not load API key from channel config: {e}")

            # 3. Try config/secrets directory
            if not api_key:
                try:
                    secrets_file = self.project_root / "config" / "secrets" / "google_api_key.json"
                    if secrets_file.exists():
                        with open(secrets_file, 'r', encoding='utf-8') as f:
                            secrets_data = json.load(f)
                            key_from_file = secrets_data.get('api_key') or secrets_data.get('GOOGLE_API_KEY')
                            # Only use if not a placeholder
                            if key_from_file and key_from_file not in ["SET_API_KEY", "TO_BE_SET", ""]:
                                api_key = key_from_file
                except Exception as e:
                    self.logger.debug(f"  Could not load API key from secrets: {e}")

            # 4. Try Azure Key Vault (ALL secrets stored here - @MARVIN: "It's already there!")
            if not api_key:
                try:
                    import importlib.util
                    azure_module_path = self.project_root / "scripts" / "python" / "azure_service_bus_integration.py"
                    if azure_module_path.exists():
                        spec = importlib.util.spec_from_file_location("azure_service_bus_integration", azure_module_path)
                        azure_module = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(azure_module)
                        AzureKeyVaultClient = azure_module.AzureKeyVaultClient

                        # Azure Key Vault URL
                        vault_url = "https://jarvis-lumina.vault.azure.net/"

                        try:
                            key_vault = AzureKeyVaultClient(vault_url)

                            # @MARVIN: "LIST ALL SECRETS FIRST to find the actual name!"
                            try:
                                all_secrets = key_vault.list_secrets()
                                self.logger.debug(f"  📋 Available secrets in vault: {len(all_secrets)} found")

                                # Look for YouTube/Google related secrets
                                youtube_secrets = [s for s in all_secrets if any(term in s.lower() for term in ['youtube', 'google', 'api'])]
                                if youtube_secrets:
                                    self.logger.info(f"  ✅ Found potential YouTube/Google secrets: {youtube_secrets}")
                            except Exception as e:
                                self.logger.debug(f"  Could not list secrets: {e}")

                            # Try common secret names for YouTube/Google API key
                            secret_names = [
                                "youtube-api-key",
                                "google-api-key",
                                "google-youtube-api-key",
                                "youtube-google-api-key",
                                "youtube_api_key",  # snake_case variant
                                "google_api_key",   # snake_case variant
                                "YOUTUBE_API_KEY",  # uppercase variant
                                "GOOGLE_API_KEY"    # uppercase variant
                            ]

                            # Also try any secrets that contain 'youtube' or 'google' from the list
                            try:
                                all_secrets = key_vault.list_secrets()
                                for secret_name in all_secrets:
                                    if any(term in secret_name.lower() for term in ['youtube', 'google']) and 'api' in secret_name.lower():
                                        secret_names.append(secret_name)  # Add actual secret names found
                            except Exception:
                                pass  # If listing fails, continue with hardcoded names

                            for secret_name in secret_names:
                                try:
                                    api_key = key_vault.get_secret(secret_name)
                                    if api_key and api_key not in ["SET_API_KEY", "TO_BE_SET", ""]:
                                        self.logger.info(f"  ✅ Retrieved API key from Azure Key Vault: {secret_name}")
                                        break
                                except Exception as e:
                                    # Log first attempt failure, but continue trying
                                    if secret_name == secret_names[0]:
                                        self.logger.debug(f"  Trying secret name: {secret_name} (not found, continuing...)")
                                    continue  # Try next secret name

                        except Exception as e:
                            self.logger.warning(f"  ⚠️  Could not access Azure Key Vault: {e}")
                            self.logger.info(f"     @MARVIN: API key is there - check authentication/permissions")
                    else:
                        self.logger.debug(f"  azure_service_bus_integration.py not found")
                except Exception as e:
                    self.logger.debug(f"  Could not check Azure Key Vault: {e}")

            # 5. Try n8n integration (if n8n has YouTube API configured)
            # Note: n8n stores credentials internally, but we can call n8n workflows
            if not api_key:
                try:
                    # Check if we can use n8n workflow to access YouTube
                    # This would require n8n to have YouTube API credentials configured
                    n8n_config_file = self.project_root / "config" / "n8n" / "unified_communications_config.json"
                    if n8n_config_file.exists():
                        with open(n8n_config_file, 'r', encoding='utf-8') as f:
                            n8n_config = json.load(f)
                            n8n_url = n8n_config.get('n8n_config', {}).get('n8n_webhook_base', 'http://localhost:5678/webhook')
                            # Note: We could call n8n webhook here, but credentials are in n8n
                            # For now, log that n8n integration is available
                            self.logger.debug(f"  n8n webhook available at {n8n_url}")
                except Exception as e:
                    self.logger.debug(f"  Could not check n8n config: {e}")

            # Skip if API key is placeholder
            if api_key and api_key not in ["SET_API_KEY", "TO_BE_SET", ""]:
                # Use YouTube Data API v3 to search for videos
                search_query = "AI technology OR artificial intelligence OR machine learning"
                youtube_url = "https://www.googleapis.com/youtube/v3/search"
                params = {
                    'part': 'snippet',
                    'q': search_query,
                    'type': 'video',
                    'maxResults': 5,
                    'order': 'date',
                    'key': api_key
                }

                try:
                    response = requests.get(youtube_url, params=params, timeout=10)
                    if response.status_code == 200:
                        data = response.json()
                        items = data.get('items', [])

                        for item in items:
                            snippet = item.get('snippet', {})
                            video_id = item.get('id', {}).get('videoId')

                            if snippet and video_id:
                                title = snippet.get('title', '')
                                description = snippet.get('description', '')
                                channel_title = snippet.get('channelTitle', '')
                                published_at = snippet.get('publishedAt', '')
                                video_url = f"https://www.youtube.com/watch?v={video_id}"

                                finding = ResearchFinding(
                                    finding_id=f"youtube_{date}_{video_id}",
                                    source=ResearchSource.SOCIAL_MEDIA,
                                    title=f"YouTube: {title}",
                                    content=description[:500] + "..." if len(description) > 500 else description,
                                    url=video_url,
                                    author=channel_title,
                                    date=published_at[:10] if published_at else date,
                                    relevance_score=0.80,  # Can be improved with better scoring
                                    keywords=["YouTube", "AI", "video"] + title.split()[:3]
                                )
                                findings.append(finding)
                                self.logger.info(f"  ✅ Extracted YouTube video: {title[:50]}...")

                        if findings:
                            self.logger.info(f"  ✅ Connected to YouTube API - {len(findings)} videos retrieved")
                    elif response.status_code == 400:
                        error_data = response.json() if response.text else {}
                        error_msg = error_data.get('error', {}).get('message', 'Bad Request')
                        self.logger.warning(f"  ⚠️  YouTube API bad request (400): {error_msg}")
                        self.logger.info(f"     API key found but request format may be incorrect")
                    elif response.status_code == 403:
                        self.logger.warning(f"  ⚠️  YouTube API access denied (403) - check API key permissions")
                    elif response.status_code == 401:
                        self.logger.warning(f"  ⚠️  YouTube API unauthorized (401) - API key may be invalid")
                    else:
                        error_text = response.text[:200] if response.text else ""
                        self.logger.warning(f"  ⚠️  YouTube API returned status {response.status_code}: {error_text}")
                except requests.exceptions.RequestException as e:
                    self.logger.warning(f"  ⚠️  YouTube API request failed: {e}")
            else:
                if not api_key:
                    self.logger.info(f"  ℹ️  YouTube API key not found in config files or environment")
                elif api_key in ["SET_API_KEY", "TO_BE_SET", ""]:
                    self.logger.info(f"  ℹ️  YouTube API key is placeholder - needs to be configured")
                self.logger.info(f"     Set GOOGLE_API_KEY or YOUTUBE_API_KEY environment variable")
                self.logger.info(f"     Or update data/lumina_youtube_channel/channel.json with actual API key")

        except ImportError:
            self.logger.warning(f"  ⚠️  requests library not available")
        except Exception as e:
            self.logger.warning(f"  ⚠️  YouTube API connection failed: {e}")

        # Note: Other social media APIs (Twitter/X, Reddit, LinkedIn) still require credentials
        # We don't have those yet, so we return what we have: YouTube findings (if any)
        # This is honest - we use what we have, don't simulate what we don't have

        if findings:
            self.logger.info(f"  ✅ Social media scan: {len(findings)} YouTube videos found")
        else:
            self.logger.info(f"  ℹ️  No social media findings (YouTube API key not configured or no results)")

        return findings

    def _scan_academic_papers(self, date: str) -> List[ResearchFinding]:
        """Scan academic white papers for findings"""
        findings = []

        # Try arXiv API (public, no authentication required for basic queries)
        try:
            import requests
            import xml.etree.ElementTree as ET

            # Search for AI-related papers from recent submissions
            search_query = "cat:cs.AI OR cat:cs.LG OR all:artificial+intelligence"
            arxiv_url = f"http://export.arxiv.org/api/query?search_query={search_query}&start=0&max_results=5&sortBy=submittedDate&sortOrder=descending"

            response = requests.get(arxiv_url, timeout=10)
            if response.status_code == 200:
                # Parse XML response properly
                try:
                    root = ET.fromstring(response.content)
                    # arXiv uses Atom feed format
                    namespace = {'atom': 'http://www.w3.org/2005/Atom'}
                    entries = root.findall('atom:entry', namespace)

                    for entry in entries:
                        # Extract paper information
                        title_elem = entry.find('atom:title', namespace)
                        summary_elem = entry.find('atom:summary', namespace)
                        id_elem = entry.find('atom:id', namespace)
                        published_elem = entry.find('atom:published', namespace)
                        authors = entry.findall('atom:author/atom:name', namespace)

                        if title_elem is not None and title_elem.text:
                            title = title_elem.text.strip().replace('\n', ' ')
                            paper_id = id_elem.text if id_elem is not None and id_elem.text else ""
                            summary = summary_elem.text.strip() if summary_elem is not None and summary_elem.text else ""
                            published = published_elem.text if published_elem is not None and published_elem.text else date
                            author_list = [author.text for author in authors if author.text]
                            author_str = ", ".join(author_list) if author_list else "Unknown"

                            # Extract paper ID from URL (format: http://arxiv.org/abs/1234.5678)
                            paper_url = paper_id
                            if "abs/" in paper_id:
                                paper_id_short = paper_id.split("abs/")[-1]
                            else:
                                paper_id_short = paper_id.split("/")[-1] if "/" in paper_id else paper_id

                            # Create finding from real paper data
                            finding = ResearchFinding(
                                finding_id=f"academic_{date}_{paper_id_short.replace('.', '_').replace('/', '_')}",
                                source=ResearchSource.ACADEMIC_PAPERS,
                                title=title,
                                content=summary[:500] + "..." if len(summary) > 500 else summary,  # Limit content length
                                url=paper_url,
                                author=author_str,
                                date=published[:10] if published else date,  # Use published date or current date
                                relevance_score=0.85,  # Can be improved with better scoring
                                keywords=["arXiv", "AI", "academic paper"] + title.split()[:3]  # Basic keywords
                            )
                            findings.append(finding)
                            self.logger.info(f"  ✅ Extracted real paper: {title[:50]}...")

                    if findings:
                        self.logger.info(f"  ✅ Connected to arXiv API - {len(findings)} real papers retrieved")
                    else:
                        self.logger.info(f"  ℹ️  arXiv API connected but no papers found in response")

                except ET.ParseError as e:
                    self.logger.warning(f"  ⚠️  Failed to parse arXiv XML response: {e}")
                except Exception as e:
                    self.logger.warning(f"  ⚠️  Error parsing arXiv response: {e}")
        except ImportError:
            self.logger.warning(f"  ⚠️  xml.etree.ElementTree not available for parsing")
        except Exception as e:
            self.logger.warning(f"  ⚠️  arXiv API connection failed: {e}")

        # GUARDRAIL 001: NO SIMULATION
        # Do not return example_findings - only return real findings
        # If we have real findings, return them
        # If not, return empty list (be honest about what we have)
        if findings:
            return findings
        else:
            # No real findings yet - return empty (not fake data)
            self.logger.info(f"  ℹ️  No real academic findings yet - returning empty list (NO SIMULATION)")
            return []

    def _get_consecutive_days(self) -> int:
        """Get consecutive days of scanning"""
        if not self.mission or not self.mission.daily_scans:
            return 0

        # Count consecutive days
        scans = sorted(self.mission.daily_scans, key=lambda s: s.date, reverse=True)
        consecutive = 0
        last_date = datetime.now().date()

        for scan in scans:
            scan_date = datetime.strptime(scan.date, "%Y-%m-%d").date()
            if scan_date == last_date - timedelta(days=consecutive):
                consecutive += 1
                last_date = scan_date
            else:
                break

        return consecutive

    def get_mission_status(self) -> Dict[str, Any]:
        """Get mission status"""
        if not self.mission:
            self._initialize_mission()

        return {
            "mission_id": self.mission.mission_id,
            "mission_name": self.mission.mission_name,
            "status": self.mission.status.value,
            "start_date": self.mission.start_date,
            "end_date": self.mission.end_date,
            "current_stardate": self.mission.current_stardate,
            "total_daily_scans": len(self.mission.daily_scans),
            "total_findings": self.mission.total_findings,
            "consecutive_days": self._get_consecutive_days(),
            "hashtags": ["#USS-LUMINA", "#MAIDEN VOYAGE"]
        }

    def _save_mission(self, mission: FiveYearMission) -> None:
        try:
            """Save mission"""
            mission_file = self.data_dir / "mission.json"
            with open(mission_file, 'w', encoding='utf-8') as f:
                json.dump(mission.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_mission: {e}", exc_info=True)
            raise
    def _save_scan(self, scan: DailyScan) -> None:
        try:
            """Save daily scan"""
            scan_file = self.data_dir / "scans" / f"{scan.scan_id}.json"
            scan_file.parent.mkdir(parents=True, exist_ok=True)
            with open(scan_file, 'w', encoding='utf-8') as f:
                json.dump(scan.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_scan: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="@SOURCE @DEEP-RESEARCH Missions")
    parser.add_argument("--launch", action="store_true", help="Launch maiden voyage")
    parser.add_argument("--scan", action="store_true", help="Execute daily scan")
    parser.add_argument("--date", type=str, help="Date for scan (YYYY-MM-DD)")
    parser.add_argument("--status", action="store_true", help="Get mission status")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    missions = SourceDeepResearchMissions()

    if args.launch:
        mission = missions.launch_maiden_voyage()
        if args.json:
            print(json.dumps(mission.to_dict(), indent=2))
        else:
            print(f"\n🚀 USS-LUMINA Maiden Voyage Launched!")
            print(f"   Mission: {mission.mission_name}")
            print(f"   Status: {mission.status.value}")
            print(f"   Stardate: {mission.current_stardate:.2f}")
            print(f"   'TO BODILY GO WHERE NO ONE HAS GONE BEFORE'")
            print(f"   #USS-LUMINA #MAIDEN VOYAGE")

    elif args.scan:
        scan = missions.execute_daily_scan(args.date)
        if args.json:
            print(json.dumps(scan.to_dict(), indent=2))
        else:
            print(f"\n🔍 Daily Scan Complete")
            print(f"   Date: {scan.date}")
            print(f"   Social Media Findings: {len(scan.social_media_findings)}")
            print(f"   Academic Paper Findings: {len(scan.academic_paper_findings)}")
            print(f"   Total Findings: {scan.total_findings}")
            print(f"   Consecutive Days: {scan.consecutive_days}")

    elif args.status:
        status = missions.get_mission_status()
        if args.json:
            print(json.dumps(status, indent=2))
        else:
            print(f"\n🚀 USS-LUMINA Mission Status")
            print(f"   Mission: {status['mission_name']}")
            print(f"   Status: {status['status']}")
            print(f"   Stardate: {status['current_stardate']:.2f}")
            print(f"   Total Daily Scans: {status['total_daily_scans']}")
            print(f"   Total Findings: {status['total_findings']}")
            print(f"   Consecutive Days: {status['consecutive_days']}")
            print(f"   {', '.join(status['hashtags'])}")

    else:
        parser.print_help()
        print("\n🚀 @SOURCE @DEEP-RESEARCH Missions")
        print("   #USS-LUMINA #MAIDEN VOYAGE")
        print("   'TO BODILY GO WHERE NO ONE HAS GONE BEFORE'")

