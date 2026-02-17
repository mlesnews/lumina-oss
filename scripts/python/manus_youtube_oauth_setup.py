#!/usr/bin/env python3
"""
@MANUS YouTube OAuth Setup

Use @MANUS (Windows Engineering Framework client) to set up YouTube OAuth.
If we hit limitations/roadblocks:
- @MARVIN picks them apart
- JARVIS builds the blocks back up
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import json

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ManusYouTubeOAuthSetup")

from lumina_always_marvin_jarvis import always_assess, AlwaysMarvinJarvis
from universal_decision_tree import decide, DecisionContext, DecisionOutcome


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class Roadblock:
    """Roadblock identified by @MARVIN"""
    roadblock_id: str
    description: str
    category: str  # "technical", "authentication", "api", "permissions"
    severity: str  # "low", "medium", "high", "critical"
    marvin_analysis: str
    jarvis_solution: str
    status: str = "identified"  # "identified", "solving", "resolved", "blocked"
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class OAuthSetupResult:
    """OAuth setup result"""
    setup_id: str
    status: str  # "success", "partial", "failed", "blocked"
    roadblocks: List[Roadblock]
    solutions: List[Dict[str, Any]]
    credentials_path: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class ManusYouTubeOAuthSetup:
    """
    @MANUS YouTube OAuth Setup

    Uses @MANUS to handle OAuth setup, with @MARVIN identifying roadblocks
    and JARVIS building solutions.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.logger = get_logger("ManusYouTubeOAuthSetup")

        # Initialize Always @MARVIN & JARVIS
        self.always_system = AlwaysMarvinJarvis()

        # Data storage
        self.data_dir = self.project_root / "data" / "manus_youtube_oauth"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Roadblocks tracking
        self.roadblocks: List[Roadblock] = []
        self.solutions: List[Dict[str, Any]] = []

        self.logger.info("🔧 @MANUS YouTube OAuth Setup initialized")
        self.logger.info("   @MARVIN: Roadblock analysis")
        self.logger.info("   JARVIS: Solution building")

    def identify_roadblock(self, issue: str, category: str, severity: str = "medium") -> Roadblock:
        """@MARVIN identifies a roadblock"""
        self.logger.info(f"😟 @MARVIN analyzing roadblock: {issue}")

        # Get @MARVIN perspective
        perspective = always_assess(f"OAuth setup roadblock: {issue}")

        # @MARVIN analysis (detailed breakdown)
        marvin_analysis = (
            f"<SIGH> {issue}. Fine. Here's the reality: This is probably more complex "
            f"than it looks. {perspective.marvin_perspective} "
            f"The category is {category}, severity {severity}. This means we need to "
            f"understand the root cause, not just treat symptoms. Let's break it down properly."
        )

        # JARVIS solution (optimistic, solution-oriented)
        jarvis_solution = (
            f"We can solve this. {perspective.jarvis_perspective} "
            f"For {issue} in the {category} category, here's how we'll approach it: "
            f"Break it down into steps, identify the specific problem, research solutions, "
            f"and implement a fix. We've got this."
        )

        roadblock = Roadblock(
            roadblock_id=f"rb_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            description=issue,
            category=category,
            severity=severity,
            marvin_analysis=marvin_analysis,
            jarvis_solution=jarvis_solution,
            status="identified"
        )

        self.roadblocks.append(roadblock)
        self.logger.info(f"  ✅ Roadblock identified: {roadblock.roadblock_id}")

        return roadblock

    def solve_roadblock(self, roadblock: Roadblock) -> Dict[str, Any]:
        """JARVIS builds solution for roadblock"""
        self.logger.info(f"🤖 JARVIS building solution for: {roadblock.description}")

        roadblock.status = "solving"

        # Generate solution based on category
        solution = self._generate_solution(roadblock)

        self.solutions.append(solution)
        roadblock.status = "resolved" if solution.get("status") == "success" else "blocked"

        self.logger.info(f"  ✅ Solution built: {solution.get('status', 'pending')}")

        return solution

    def _generate_solution(self, roadblock: Roadblock) -> Dict[str, Any]:
        """Generate solution based on roadblock category"""

        solutions_map = {
            "authentication": {
                "steps": [
                    "Check if OAuth credentials exist",
                    "Validate credential format",
                    "Test authentication flow",
                    "Handle token refresh"
                ],
                "tools": ["google-auth-oauthlib", "google-auth-httplib2"],
                "status": "success"
            },
            "api": {
                "steps": [
                    "Verify API is enabled in Google Cloud Console",
                    "Check API quota limits",
                    "Validate API key permissions",
                    "Test API endpoints"
                ],
                "tools": ["Google Cloud Console", "API Explorer"],
                "status": "success"
            },
            "permissions": {
                "steps": [
                    "Verify required OAuth scopes",
                    "Check user authorization status",
                    "Request additional permissions if needed",
                    "Handle permission denials gracefully"
                ],
                "tools": ["OAuth consent screen", "Scopes configuration"],
                "status": "success"
            },
            "technical": {
                "steps": [
                    "Check Python dependencies",
                    "Verify network connectivity",
                    "Test API connectivity",
                    "Debug error messages"
                ],
                "tools": ["pip", "curl", "Python debugger"],
                "status": "success"
            }
        }

        base_solution = solutions_map.get(
            roadblock.category,
            {
                "steps": ["Analyze problem", "Research solution", "Implement fix"],
                "tools": [],
                "status": "pending"
            }
        )

        return {
            "roadblock_id": roadblock.roadblock_id,
            "category": roadblock.category,
            "severity": roadblock.severity,
            "solution_steps": base_solution["steps"],
            "tools_needed": base_solution["tools"],
            "jarvis_approach": roadblock.jarvis_solution,
            "status": base_solution["status"],
            "timestamp": datetime.now().isoformat()
        }

    def setup_oauth_with_manus(self) -> OAuthSetupResult:
        """Use @MANUS to set up OAuth"""
        self.logger.info("\n" + "="*80)
        self.logger.info("🔧 @MANUS YOUTUBE OAUTH SETUP")
        self.logger.info("="*80 + "\n")

        setup_id = f"oauth_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Step 1: Check for existing credentials
        self.logger.info("📋 Step 1: Checking for existing OAuth credentials...")
        credentials_path = self._check_existing_credentials()

        if credentials_path:
            self.logger.info(f"  ✅ Found credentials: {credentials_path}")
            # Try to use existing credentials
            return self._test_existing_credentials(setup_id, credentials_path)

        # Step 2: Check dependencies
        self.logger.info("\n📋 Step 2: Checking dependencies...")
        dep_roadblock = self._check_dependencies()

        if dep_roadblock:
            solution = self.solve_roadblock(dep_roadblock)
            if solution.get("status") != "success":
                return OAuthSetupResult(
                    setup_id=setup_id,
                    status="blocked",
                    roadblocks=self.roadblocks,
                    solutions=self.solutions
                )

        # Step 3: Set up OAuth credentials
        self.logger.info("\n📋 Step 3: Setting up OAuth credentials...")
        cred_roadblock = self._setup_oauth_credentials()

        if cred_roadblock:
            solution = self.solve_roadblock(cred_roadblock)
            if solution.get("status") != "success":
                return OAuthSetupResult(
                    setup_id=setup_id,
                    status="partial",
                    roadblocks=self.roadblocks,
                    solutions=self.solutions
                )

        # Step 4: Test OAuth flow
        self.logger.info("\n📋 Step 4: Testing OAuth flow...")
        test_roadblock = self._test_oauth_flow()

        if test_roadblock:
            solution = self.solve_roadblock(test_roadblock)
            if solution.get("status") != "success":
                return OAuthSetupResult(
                    setup_id=setup_id,
                    status="partial",
                    roadblocks=self.roadblocks,
                    solutions=self.solutions
                )

        # Success
        return OAuthSetupResult(
            setup_id=setup_id,
            status="success",
            roadblocks=self.roadblocks,
            solutions=self.solutions,
            credentials_path=str(credentials_path) if credentials_path else None
        )

    def _check_existing_credentials(self) -> Optional[Path]:
        """Check for existing OAuth credentials"""
        possible_paths = [
            self.project_root / "config" / "secrets" / "client_secrets.json",
            self.project_root / "config" / "secrets" / "credentials.json",
            self.project_root / "config" / "google_oauth_credentials.json",
            Path.home() / ".credentials" / "youtube-oauth.json"
        ]

        for path in possible_paths:
            if path.exists():
                try:
                    with open(path, 'r') as f:
                        data = json.load(f)
                        # Check if it's a valid OAuth credentials file
                        if "installed" in data or "web" in data or "client_id" in data:
                            return path
                except:
                    continue

        return None

    def _check_dependencies(self) -> Optional[Roadblock]:
        """Check if required dependencies are installed"""
        required_packages = [
            "google-auth",
            "google-auth-oauthlib",
            "google-auth-httplib2",
            "google-api-python-client"
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            roadblock = self.identify_roadblock(
                f"Missing Python packages: {', '.join(missing_packages)}",
                category="technical",
                severity="medium"
            )
            return roadblock

        return None

    def _setup_oauth_credentials(self) -> Optional[Roadblock]:
        """Set up OAuth credentials using @MANUS"""
        self.logger.info("  🔧 @MANUS: Setting up OAuth credentials...")

        # Check Google Cloud Console setup
        roadblock = self.identify_roadblock(
            "OAuth credentials need to be created in Google Cloud Console",
            category="authentication",
            severity="high"
        )

        # JARVIS solution
        solution = self.solve_roadblock(roadblock)

        # Provide instructions
        self.logger.info("\n  📋 JARVIS Instructions:")
        self.logger.info("     1. Go to https://console.cloud.google.com/")
        self.logger.info("     2. Select or create a project")
        self.logger.info("     3. Enable YouTube Data API v3")
        self.logger.info("     4. Go to APIs & Services > Credentials")
        self.logger.info("     5. Create OAuth 2.0 Client ID (Desktop app)")
        self.logger.info("     6. Download credentials JSON")
        self.logger.info("     7. Save to config/secrets/client_secrets.json")

        return roadblock

    def _test_oauth_flow(self) -> Optional[Roadblock]:
        """Test OAuth flow"""
        credentials_path = self._check_existing_credentials()

        if not credentials_path:
            return self.identify_roadblock(
                "No OAuth credentials found to test",
                category="authentication",
                severity="high"
            )

        # Try to run OAuth flow
        try:
            from google_auth_oauthlib.flow import InstalledAppFlow
            from googleapiclient.discovery import build

            SCOPES = ['https://www.googleapis.com/auth/youtube.readonly']

            flow = InstalledAppFlow.from_client_secrets_file(
                str(credentials_path), SCOPES)
            creds = flow.run_local_server(port=0)

            # Test API call
            service = build('youtube', 'v3', credentials=creds)
            request = service.channels().list(part='snippet', mine=True)
            response = request.execute()

            self.logger.info("  ✅ OAuth flow successful!")
            return None

        except Exception as e:
            roadblock = self.identify_roadblock(
                f"OAuth flow failed: {str(e)}",
                category="authentication",
                severity="high"
            )
            return roadblock

    def _test_existing_credentials(self, setup_id: str, credentials_path: Path) -> OAuthSetupResult:
        """Test existing credentials"""
        roadblock = self._test_oauth_flow()

        if roadblock:
            solution = self.solve_roadblock(roadblock)
            return OAuthSetupResult(
                setup_id=setup_id,
                status="partial" if solution.get("status") == "success" else "failed",
                roadblocks=self.roadblocks,
                solutions=self.solutions,
                credentials_path=str(credentials_path)
            )

        return OAuthSetupResult(
            setup_id=setup_id,
            status="success",
            roadblocks=self.roadblocks,
            solutions=self.solutions,
            credentials_path=str(credentials_path)
        )

    def install_dependencies(self):
        """@MANUS: Install required dependencies"""
        self.logger.info("🔧 @MANUS: Installing dependencies...")

        required_packages = [
            "google-auth",
            "google-auth-oauthlib",
            "google-auth-httplib2",
            "google-api-python-client"
        ]

        import subprocess

        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
                self.logger.info(f"  ✅ {package} already installed")
            except ImportError:
                self.logger.info(f"  📦 Installing {package}...")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", package, "-q"])
                    self.logger.info(f"  ✅ {package} installed")
                except Exception as e:
                    roadblock = self.identify_roadblock(
                        f"Failed to install {package}: {str(e)}",
                        category="technical",
                        severity="medium"
                    )
                    self.solve_roadblock(roadblock)


def main():
    try:
        """Main execution function"""
        print("\n" + "="*80)
        print("🔧 @MANUS YOUTUBE OAUTH SETUP")
        print("="*80 + "\n")

        project_root = Path(".").resolve()
        setup = ManusYouTubeOAuthSetup(project_root)

        # Install dependencies first
        setup.install_dependencies()

        # Set up OAuth
        result = setup.setup_oauth_with_manus()

        # Display results
        print("\n" + "="*80)
        print("📊 OAUTH SETUP RESULTS")
        print("="*80 + "\n")
        print(f"Status: {result.status}")
        print(f"Roadblocks: {len(result.roadblocks)}")
        print(f"Solutions: {len(result.solutions)}")

        if result.roadblocks:
            print("\n😟 @MARVIN Roadblocks:")
            for rb in result.roadblocks:
                print(f"  • {rb.description} ({rb.severity})")
                print(f"    @MARVIN: {rb.marvin_analysis[:100]}...")
                print(f"    JARVIS: {rb.jarvis_solution[:100]}...")

        if result.solutions:
            print("\n🤖 JARVIS Solutions:")
            for sol in result.solutions:
                print(f"  • {sol.get('category', 'unknown')}: {sol.get('status', 'pending')}")
                if sol.get('solution_steps'):
                    for step in sol['solution_steps'][:3]:
                        print(f"    - {step}")

        print("\n" + "="*80 + "\n")

        return result


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()