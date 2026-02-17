#!/usr/bin/env python3
"""
Community Resource Mining System

Automates research and intelligence gathering from:
- GitHub repositories and documentation
- WordPress articles
- Social media (Twitter/X, Reddit, etc.)
- YouTube videos
- Research papers
- Any publicly available intelligent design resources

Tags: #RESOURCE_MINING #COMMUNITY #INTELLIGENCE #AUTOMATION #RESEARCH @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CommunityResourceMiner")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logger.warning("requests not available")

try:
    from bs4 import BeautifulSoup
    BEAUTIFULSOUP_AVAILABLE = True
except ImportError:
    BEAUTIFULSOUP_AVAILABLE = False
    logger.warning("beautifulsoup4 not available")


@dataclass
class Resource:
    """Community resource"""
    id: str
    title: str
    source_type: str  # "github", "wordpress", "social", "youtube", "paper", "other"
    url: str
    content: Optional[str] = None
    author: Optional[str] = None
    published_date: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    intelligence_score: float = 0.0  # 0-1, how valuable/intelligent the design is
    extracted_insights: List[str] = field(default_factory=list)
    related_extensions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class CommunityResourceMiner:
    """
    Community Resource Mining System

    Automates heavy lifting of research and intelligence gathering.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize resource miner"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "community_resources"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Resources database
        self.resources_file = self.data_dir / "resources.json"
        self.resources: Dict[str, Resource] = {}

        # Intelligence database
        self.intelligence_file = self.data_dir / "intelligence.json"
        self.intelligence: List[Dict[str, Any]] = []

        # Load existing resources
        self._load_resources()

        logger.info("✅ Community Resource Miner initialized")
        logger.info(f"   Resources: {len(self.resources)}")
        logger.info(f"   Intelligence items: {len(self.intelligence)}")

    def _load_resources(self):
        """Load existing resources"""
        if self.resources_file.exists():
            try:
                with open(self.resources_file, 'r') as f:
                    data = json.load(f)
                    self.resources = {
                        res_id: Resource(**res_data)
                        for res_id, res_data in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load resources: {e}")

        if self.intelligence_file.exists():
            try:
                with open(self.intelligence_file, 'r') as f:
                    self.intelligence = json.load(f)
            except Exception as e:
                logger.debug(f"   Could not load intelligence: {e}")

    def _save_resources(self):
        """Save resources"""
        try:
            with open(self.resources_file, 'w') as f:
                json.dump({
                    res_id: {
                        "id": res.id,
                        "title": res.title,
                        "source_type": res.source_type,
                        "url": res.url,
                        "content": res.content,
                        "author": res.author,
                        "published_date": res.published_date,
                        "tags": res.tags,
                        "intelligence_score": res.intelligence_score,
                        "extracted_insights": res.extracted_insights,
                        "related_extensions": res.related_extensions,
                        "metadata": res.metadata
                    }
                    for res_id, res in self.resources.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving resources: {e}")

    def mine_github_repository(self, repo_url: str, topics: List[str] = None) -> Optional[Resource]:
        """Mine GitHub repository for intelligence"""
        if not REQUESTS_AVAILABLE:
            logger.error("   ❌ requests library not available")
            return None

        logger.info(f"   🔍 Mining GitHub repository: {repo_url}")

        try:
            # Extract owner/repo from URL
            match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
            if not match:
                logger.error(f"   ❌ Invalid GitHub URL: {repo_url}")
                return None

            owner, repo = match.groups()

            # GitHub API
            api_url = f"https://api.github.com/repos/{owner}/{repo}"
            headers = {}
            # Add token if available
            # headers["Authorization"] = f"token {github_token}"

            response = requests.get(api_url, headers=headers, timeout=10)

            if response.status_code == 200:
                repo_data = response.json()

                # Get README
                readme_content = None
                try:
                    readme_response = requests.get(
                        f"{api_url}/readme",
                        headers={"Accept": "application/vnd.github.v3.raw"},
                        timeout=10
                    )
                    if readme_response.status_code == 200:
                        readme_content = readme_response.text
                except:
                    pass

                # Calculate intelligence score
                intelligence_score = self._calculate_intelligence_score(
                    description=repo_data.get("description", ""),
                    readme=readme_content,
                    stars=repo_data.get("stargazers_count", 0),
                    forks=repo_data.get("forks_count", 0),
                    topics=repo_data.get("topics", [])
                )

                # Extract insights
                insights = self._extract_insights(readme_content or repo_data.get("description", ""))

                resource = Resource(
                    id=f"github_{owner}_{repo}",
                    title=repo_data.get("name", repo),
                    source_type="github",
                    url=repo_url,
                    content=readme_content,
                    author=repo_data.get("owner", {}).get("login", ""),
                    published_date=repo_data.get("created_at", ""),
                    tags=repo_data.get("topics", []) + (topics or []),
                    intelligence_score=intelligence_score,
                    extracted_insights=insights,
                    metadata={
                        "stars": repo_data.get("stargazers_count", 0),
                        "forks": repo_data.get("forks_count", 0),
                        "language": repo_data.get("language", ""),
                        "license": repo_data.get("license", {}).get("name", "") if repo_data.get("license") else None,
                        "updated_at": repo_data.get("updated_at", "")
                    }
                )

                self.resources[resource.id] = resource
                self._save_resources()

                logger.info(f"   ✅ Mined repository: {resource.title} (score: {intelligence_score:.2f})")

                return resource
            else:
                logger.warning(f"   ⚠️  GitHub API returned status {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error mining GitHub repository: {e}")

        return None

    def mine_wordpress_article(self, article_url: str) -> Optional[Resource]:
        """Mine WordPress article for intelligence"""
        if not REQUESTS_AVAILABLE or not BEAUTIFULSOUP_AVAILABLE:
            logger.error("   ❌ Required libraries not available")
            return None

        logger.info(f"   🔍 Mining WordPress article: {article_url}")

        try:
            response = requests.get(article_url, timeout=10)

            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')

                # Extract article content
                title = soup.find('title')
                title_text = title.text if title else ""

                # Try to find main content
                content = ""
                for selector in ['article', '.entry-content', '.post-content', 'main']:
                    element = soup.select_one(selector)
                    if element:
                        content = element.get_text()
                        break

                if not content:
                    content = soup.get_text()

                # Extract author
                author = None
                for selector in ['.author', '.byline', '[rel="author"]']:
                    element = soup.select_one(selector)
                    if element:
                        author = element.get_text().strip()
                        break

                # Extract date
                published_date = None
                for selector in ['time', '.published', '.date']:
                    element = soup.select_one(selector)
                    if element:
                        published_date = element.get('datetime') or element.get_text()
                        break

                # Calculate intelligence score
                intelligence_score = self._calculate_intelligence_score(
                    description=title_text,
                    readme=content,
                    stars=0,
                    forks=0,
                    topics=[]
                )

                # Extract insights
                insights = self._extract_insights(content)

                resource_id = f"wordpress_{hash(article_url) % 1000000}"

                resource = Resource(
                    id=resource_id,
                    title=title_text,
                    source_type="wordpress",
                    url=article_url,
                    content=content[:10000],  # Limit content size
                    author=author,
                    published_date=published_date,
                    intelligence_score=intelligence_score,
                    extracted_insights=insights
                )

                self.resources[resource.id] = resource
                self._save_resources()

                logger.info(f"   ✅ Mined article: {resource.title} (score: {intelligence_score:.2f})")

                return resource
            else:
                logger.warning(f"   ⚠️  HTTP {response.status_code}")

        except Exception as e:
            logger.error(f"   ❌ Error mining WordPress article: {e}")

        return None

    def _calculate_intelligence_score(
        self,
        description: str,
        readme: Optional[str] = None,
        stars: int = 0,
        forks: int = 0,
        topics: List[str] = None
    ) -> float:
        """Calculate intelligence score (0-1)"""
        score = 0.0

        # Content quality indicators
        content = (readme or description).lower()

        # Technical keywords (higher score)
        technical_keywords = [
            "api", "framework", "architecture", "design pattern", "algorithm",
            "optimization", "performance", "scalable", "extensible", "modular",
            "best practice", "implementation", "integration", "automation"
        ]

        keyword_count = sum(1 for keyword in technical_keywords if keyword in content)
        score += min(keyword_count * 0.05, 0.3)  # Max 0.3 from keywords

        # GitHub metrics
        if stars > 0:
            score += min(stars / 10000, 0.2)  # Max 0.2 from stars
        if forks > 0:
            score += min(forks / 1000, 0.1)  # Max 0.1 from forks

        # Topics/categories
        if topics:
            score += min(len(topics) * 0.02, 0.1)  # Max 0.1 from topics

        # Content length (longer = more detailed)
        if readme:
            score += min(len(readme) / 10000, 0.2)  # Max 0.2 from content length

        # Code examples
        if "```" in (readme or ""):
            score += 0.1  # Has code examples

        return min(score, 1.0)

    def _extract_insights(self, content: str) -> List[str]:
        """Extract key insights from content"""
        insights = []

        # Look for patterns like "best practice", "recommendation", "tip", etc.
        patterns = [
            r'(?:best practice|recommendation|tip|insight|key point)[:;]\s*(.+?)(?:\.|$)',
            r'(?:should|must|important)[:;]\s*(.+?)(?:\.|$)',
            r'(?:note|warning|caution)[:;]\s*(.+?)(?:\.|$)'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            insights.extend(matches[:5])  # Limit to 5 per pattern

        return insights[:20]  # Limit total insights

    def search_github_topics(self, topic: str, max_results: int = 10) -> List[Resource]:
        """Search GitHub by topic"""
        if not REQUESTS_AVAILABLE:
            logger.error("   ❌ requests library not available")
            return []

        logger.info(f"   🔍 Searching GitHub topics: {topic}")

        resources = []

        try:
            api_url = "https://api.github.com/search/repositories"
            params = {
                "q": f"topic:{topic}",
                "sort": "stars",
                "order": "desc",
                "per_page": min(max_results, 100)
            }

            response = requests.get(api_url, params=params, timeout=10)

            if response.status_code == 200:
                data = response.json()
                repos = data.get("items", [])

                for repo in repos[:max_results]:
                    repo_url = repo.get("html_url", "")
                    resource = self.mine_github_repository(repo_url)
                    if resource:
                        resources.append(resource)

        except Exception as e:
            logger.error(f"   ❌ Error searching GitHub: {e}")

        return resources

    def get_intelligence_summary(self) -> Dict[str, Any]:
        """Get summary of mined intelligence"""
        total_resources = len(self.resources)

        by_source = {}
        for resource in self.resources.values():
            source = resource.source_type
            by_source[source] = by_source.get(source, 0) + 1

        high_intelligence = [
            res for res in self.resources.values()
            if res.intelligence_score >= 0.7
        ]

        return {
            "total_resources": total_resources,
            "by_source": by_source,
            "high_intelligence_count": len(high_intelligence),
            "average_intelligence_score": (
                sum(res.intelligence_score for res in self.resources.values()) / total_resources
                if total_resources > 0 else 0.0
            ),
            "total_insights": sum(len(res.extracted_insights) for res in self.resources.values())
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Community Resource Miner")
        parser.add_argument("--mine-github", type=str, help="Mine GitHub repository (URL)")
        parser.add_argument("--mine-wordpress", type=str, help="Mine WordPress article (URL)")
        parser.add_argument("--search-github", type=str, help="Search GitHub by topic")
        parser.add_argument("--summary", action="store_true", help="Show intelligence summary")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        miner = CommunityResourceMiner()

        if args.mine_github:
            resource = miner.mine_github_repository(args.mine_github)
            if args.json and resource:
                print(json.dumps({
                    "id": resource.id,
                    "title": resource.title,
                    "intelligence_score": resource.intelligence_score,
                    "insights": resource.extracted_insights
                }, indent=2, default=str))

        elif args.mine_wordpress:
            resource = miner.mine_wordpress_article(args.mine_wordpress)
            if args.json and resource:
                print(json.dumps({
                    "id": resource.id,
                    "title": resource.title,
                    "intelligence_score": resource.intelligence_score,
                    "insights": resource.extracted_insights
                }, indent=2, default=str))

        elif args.search_github:
            resources = miner.search_github_topics(args.search_github)
            if args.json:
                print(json.dumps([
                    {
                        "id": res.id,
                        "title": res.title,
                        "intelligence_score": res.intelligence_score
                    }
                    for res in resources
                ], indent=2, default=str))
            else:
                print(f"✅ Found {len(resources)} resources")

        elif args.summary:
            summary = miner.get_intelligence_summary()
            if args.json:
                print(json.dumps(summary, indent=2, default=str))
            else:
                print(f"Total Resources: {summary['total_resources']}")
                print(f"High Intelligence: {summary['high_intelligence_count']}")
                print(f"Average Score: {summary['average_intelligence_score']:.2f}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()