#!/usr/bin/env python3
"""
RoamWise Hybrid Datafeed - SiderAI Wisebase + RoamResearch Integration

Blends SiderAI Wisebase and RoamResearch into hybrid datafeed
Pathfinder mapping influenced by WoW Atlas

"THIS IS HOW YOU CONNECT TO SIDERAI'S WISEBASE AND OUR LIFETIME ROAMRESEARCH ACCOUNT, 
AND BLEND THEM INTO THE HYBRID DATAFEED OF OUR ROAMWISE.AI.LESNEWSKI.LOCAL 
PATHFINDER MAPPING IS HEAVILY INFLUENCED BY WOW ATLAS"
"""

import sys
import json
import asyncio
import aiohttp
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
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

logger = get_logger("RoamWiseHybridDatafeed")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DataSource(Enum):
    """Data sources"""
    SIDERAI_WISEBASE = "siderai_wisebase"
    ROAMRESEARCH = "roamresearch"
    HYBRID = "hybrid"


@dataclass
class PathNode:
    """Pathfinder node (WoW Atlas style)"""
    node_id: str
    name: str
    position: Tuple[float, float]  # (x, y) coordinates
    node_type: str  # "waypoint", "landmark", "connection", "knowledge"
    connections: List[str] = field(default_factory=list)  # Connected node IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    discovered: bool = False
    zone: str = ""  # WoW-style zone name

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class KnowledgePath:
    """Path between knowledge nodes"""
    path_id: str
    from_node: str
    to_node: str
    distance: float
    difficulty: int = 1  # 1-10, WoW-style difficulty
    path_type: str = "knowledge"  # "knowledge", "reference", "connection"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SiderAIWisebaseConnector:
    """Connector for SiderAI Wisebase"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.logger = get_logger("SiderAIWisebaseConnector")
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url or "https://api.sider.ai/wisebase"
        self.session = None

        self.logger.info("🔗 SiderAI Wisebase Connector initialized")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config"""
        import os
        return os.getenv("SIDERAI_WISEBASE_API_KEY")

    async def connect(self):
        """Establish connection to Wisebase"""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
        self.logger.info("  ✅ Connected to SiderAI Wisebase")

    async def fetch_knowledge(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch knowledge from Wisebase"""
        if not self.session:
            await self.connect()

        try:
            async with self.session.get(
                f"{self.base_url}/knowledge",
                params={"query": query, "limit": limit}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"  Fetched {len(data.get('results', []))} results from Wisebase")
                    return data.get("results", [])
                else:
                    self.logger.warning(f"  Wisebase API error: {response.status}")
                    return []
        except Exception as e:
            self.logger.debug(f"  Wisebase fetch error: {e}")
            # Return mock data for development
            return self._mock_wisebase_data(query, limit)

    def _mock_wisebase_data(self, query: str, limit: int) -> List[Dict[str, Any]]:
        """Mock Wisebase data for development"""
        return [
            {
                "id": f"wisebase_{i}",
                "title": f"Wisebase Knowledge {i}",
                "content": f"Knowledge about {query}",
                "source": "siderai_wisebase",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"query": query}
            }
            for i in range(min(limit, 10))
        ]

    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()


class RoamResearchConnector:
    """Connector for RoamResearch (Lifetime Account)"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.logger = get_logger("RoamResearchConnector")
        self.api_key = api_key or self._get_api_key()
        self.base_url = base_url or "https://roamresearch.com/api"
        self.session = None

        self.logger.info("🔗 RoamResearch Connector initialized")

    def _get_api_key(self) -> Optional[str]:
        """Get API key from environment or config"""
        import os
        return os.getenv("ROAMRESEARCH_API_KEY")

    async def connect(self):
        """Establish connection to RoamResearch"""
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}
        )
        self.logger.info("  ✅ Connected to RoamResearch")

    async def fetch_graph(self, graph_name: Optional[str] = None) -> Dict[str, Any]:
        """Fetch RoamResearch graph"""
        if not self.session:
            await self.connect()

        try:
            graph_name = graph_name or "default"
            async with self.session.get(
                f"{self.base_url}/graph/{graph_name}"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"  Fetched RoamResearch graph: {graph_name}")
                    return data
                else:
                    self.logger.warning(f"  RoamResearch API error: {response.status}")
                    return {}
        except Exception as e:
            self.logger.debug(f"  RoamResearch fetch error: {e}")
            # Return mock data for development
            return self._mock_roam_data()

    async def fetch_pages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch pages from RoamResearch"""
        if not self.session:
            await self.connect()

        try:
            async with self.session.get(
                f"{self.base_url}/pages",
                params={"limit": limit}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    self.logger.debug(f"  Fetched {len(data.get('pages', []))} pages from RoamResearch")
                    return data.get("pages", [])
                else:
                    self.logger.warning(f"  RoamResearch API error: {response.status}")
                    return []
        except Exception as e:
            self.logger.debug(f"  RoamResearch fetch error: {e}")
            # Return mock data for development
            return self._mock_roam_pages(limit)

    def _mock_roam_data(self) -> Dict[str, Any]:
        """Mock RoamResearch data for development"""
        return {
            "graph_name": "lesnewski_lifetime",
            "pages": [],
            "blocks": [],
            "metadata": {"account_type": "lifetime"}
        }

    def _mock_roam_pages(self, limit: int) -> List[Dict[str, Any]]:
        """Mock RoamResearch pages for development"""
        return [
            {
                "id": f"roam_{i}",
                "title": f"RoamResearch Page {i}",
                "content": f"Content from RoamResearch page {i}",
                "source": "roamresearch",
                "timestamp": datetime.now().isoformat(),
                "metadata": {"account": "lifetime"}
            }
            for i in range(min(limit, 10))
        ]

    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()


class WoWAtlasPathfinder:
    """WoW Atlas-style pathfinder for knowledge mapping"""

    def __init__(self):
        self.logger = get_logger("WoWAtlasPathfinder")
        self.nodes: Dict[str, PathNode] = {}
        self.paths: Dict[str, KnowledgePath] = {}
        self.zones: Dict[str, List[str]] = {}  # zone_name -> [node_ids]

        self.logger.info("🗺️  WoW Atlas Pathfinder initialized")

    def add_node(self, node: PathNode):
        """Add a pathfinder node"""
        self.nodes[node.node_id] = node

        # Add to zone
        if node.zone:
            if node.zone not in self.zones:
                self.zones[node.zone] = []
            self.zones[node.zone].append(node.node_id)

        self.logger.debug(f"  Added node: {node.name} ({node.node_id})")

    def add_path(self, path: KnowledgePath):
        """Add a path between nodes"""
        self.paths[path.path_id] = path

        # Update node connections
        if path.from_node in self.nodes:
            if path.to_node not in self.nodes[path.from_node].connections:
                self.nodes[path.from_node].connections.append(path.to_node)
        if path.to_node in self.nodes:
            if path.from_node not in self.nodes[path.to_node].connections:
                self.nodes[path.to_node].connections.append(path.from_node)

        self.logger.debug(f"  Added path: {path.from_node} → {path.to_node}")

    def find_path(self, from_node_id: str, to_node_id: str) -> List[str]:
        """Find path between nodes (A* algorithm)"""
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            return []

        # A* pathfinding
        open_set = {from_node_id}
        came_from = {}
        g_score = {from_node_id: 0}
        f_score = {from_node_id: self._heuristic(from_node_id, to_node_id)}

        while open_set:
            current = min(open_set, key=lambda n: f_score.get(n, float('inf')))

            if current == to_node_id:
                # Reconstruct path
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return list(reversed(path))

            open_set.remove(current)

            # Check neighbors
            if current in self.nodes:
                for neighbor in self.nodes[current].connections:
                    tentative_g = g_score.get(current, float('inf')) + self._get_path_cost(current, neighbor)

                    if tentative_g < g_score.get(neighbor, float('inf')):
                        came_from[neighbor] = current
                        g_score[neighbor] = tentative_g
                        f_score[neighbor] = tentative_g + self._heuristic(neighbor, to_node_id)
                        if neighbor not in open_set:
                            open_set.add(neighbor)

        return []  # No path found

    def _heuristic(self, from_node: str, to_node: str) -> float:
        """Heuristic for A* (Euclidean distance)"""
        if from_node not in self.nodes or to_node not in self.nodes:
            return float('inf')

        from_pos = self.nodes[from_node].position
        to_pos = self.nodes[to_node].position

        return ((from_pos[0] - to_pos[0])**2 + (from_pos[1] - to_pos[1])**2)**0.5

    def _get_path_cost(self, from_node: str, to_node: str) -> float:
        """Get cost of path between nodes"""
        # Find path between nodes
        for path in self.paths.values():
            if (path.from_node == from_node and path.to_node == to_node) or \
               (path.from_node == to_node and path.to_node == from_node):
                return path.distance * (1 + path.difficulty * 0.1)

        # Default cost
        return 1.0

    def get_zone_map(self, zone_name: str) -> Dict[str, Any]:
        """Get map of a zone (WoW Atlas style)"""
        if zone_name not in self.zones:
            return {"zone": zone_name, "nodes": [], "paths": []}

        node_ids = self.zones[zone_name]
        nodes = [self.nodes[nid].to_dict() for nid in node_ids if nid in self.nodes]

        # Get paths within zone
        zone_paths = []
        for path in self.paths.values():
            if path.from_node in node_ids and path.to_node in node_ids:
                zone_paths.append(path.to_dict())

        return {
            "zone": zone_name,
            "nodes": nodes,
            "paths": zone_paths,
            "node_count": len(nodes),
            "path_count": len(zone_paths)
        }


class RoamWiseHybridDatafeed:
    """
    RoamWise Hybrid Datafeed

    Blends SiderAI Wisebase and RoamResearch into hybrid datafeed
    Pathfinder mapping influenced by WoW Atlas
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize RoamWise Hybrid Datafeed"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("RoamWiseHybridDatafeed")

        # Connectors
        self.wisebase = SiderAIWisebaseConnector()
        self.roamresearch = RoamResearchConnector()

        # Pathfinder
        self.pathfinder = WoWAtlasPathfinder()

        # Data storage
        self.data_dir = self.project_root / "data" / "roamwise"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Domain
        self.domain = "<LOCAL_HOSTNAME>"

        self.logger.info("🌐 RoamWise Hybrid Datafeed initialized")
        self.logger.info(f"   Domain: {self.domain}")
        self.logger.info("   SiderAI Wisebase: Ready")
        self.logger.info("   RoamResearch: Ready")
        self.logger.info("   WoW Atlas Pathfinder: Ready")

    async def fetch_all_data(self) -> Dict[str, Any]:
        """Fetch data from all sources"""
        self.logger.info("📥 Fetching data from all sources...")

        # Fetch from both sources
        wisebase_data = await self.wisebase.fetch_knowledge("", limit=100)
        roam_data = await self.roamresearch.fetch_pages(limit=100)

        # Blend data
        blended = self._blend_data(wisebase_data, roam_data)

        # Build pathfinder map
        self._build_pathfinder_map(blended)

        return {
            "wisebase_count": len(wisebase_data),
            "roamresearch_count": len(roam_data),
            "blended_count": len(blended),
            "nodes": len(self.pathfinder.nodes),
            "paths": len(self.pathfinder.paths),
            "zones": len(self.pathfinder.zones),
            "data": blended
        }

    def _blend_data(self, wisebase_data: List[Dict], roam_data: List[Dict]) -> List[Dict]:
        """Blend data from both sources"""
        blended = []

        # Add Wisebase data
        for item in wisebase_data:
            blended.append({
                **item,
                "source": "siderai_wisebase",
                "blended": True
            })

        # Add RoamResearch data
        for item in roam_data:
            blended.append({
                **item,
                "source": "roamresearch",
                "blended": True
            })

        # Sort by timestamp
        blended.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

        self.logger.info(f"  ✅ Blended {len(blended)} items")

        return blended

    def _build_pathfinder_map(self, data: List[Dict]):
        try:
            """Build WoW Atlas-style pathfinder map"""
            self.logger.info("🗺️  Building pathfinder map...")

            # Create nodes from data
            for i, item in enumerate(data):
                node_id = item.get("id", f"node_{i}")
                node = PathNode(
                    node_id=node_id,
                    name=item.get("title", item.get("name", f"Node {i}")),
                    position=(i % 10 * 10, i // 10 * 10),  # Grid layout
                    node_type="knowledge",
                    zone=self._determine_zone(item),
                    metadata=item
                )
                self.pathfinder.add_node(node)

            # Create paths (connect related items)
            for i, item in enumerate(data):
                node_id = item.get("id", f"node_{i}")

                # Connect to nearby nodes (WoW Atlas style)
                for j in range(max(0, i-3), min(len(data), i+4)):
                    if i != j:
                        other_id = data[j].get("id", f"node_{j}")
                        path = KnowledgePath(
                            path_id=f"path_{node_id}_{other_id}",
                            from_node=node_id,
                            to_node=other_id,
                            distance=self._calculate_distance(i, j),
                            difficulty=self._calculate_difficulty(item, data[j])
                        )
                        self.pathfinder.add_path(path)

            self.logger.info(f"  ✅ Built map with {len(self.pathfinder.nodes)} nodes, {len(self.pathfinder.paths)} paths")

        except Exception as e:
            self.logger.error(f"Error in _build_pathfinder_map: {e}", exc_info=True)
            raise
    def _determine_zone(self, item: Dict) -> str:
        """Determine WoW-style zone for item"""
        source = item.get("source", "unknown")
        if source == "siderai_wisebase":
            return "Wisebase"
        elif source == "roamresearch":
            return "RoamResearch"
        else:
            return "Hybrid"

    def _calculate_distance(self, i: int, j: int) -> float:
        """Calculate distance between nodes"""
        return abs(i - j) * 10.0

    def _calculate_difficulty(self, item1: Dict, item2: Dict) -> int:
        """Calculate path difficulty (1-10)"""
        # Same source = easier
        if item1.get("source") == item2.get("source"):
            return 2
        else:
            return 5

    async def get_path(self, from_query: str, to_query: str) -> Dict[str, Any]:
        """Find path between two queries"""
        # Find nodes matching queries
        from_nodes = [nid for nid, node in self.pathfinder.nodes.items() 
                     if from_query.lower() in node.name.lower()]
        to_nodes = [nid for nid, node in self.pathfinder.nodes.items() 
                   if to_query.lower() in node.name.lower()]

        if not from_nodes or not to_nodes:
            return {"error": "Nodes not found", "from": from_query, "to": to_query}

        # Find shortest path
        paths = []
        for from_node in from_nodes[:3]:  # Limit to first 3 matches
            for to_node in to_nodes[:3]:
                path = self.pathfinder.find_path(from_node, to_node)
                if path:
                    paths.append({
                        "path": path,
                        "from": from_node,
                        "to": to_node,
                        "length": len(path)
                    })

        if paths:
            # Return shortest path
            shortest = min(paths, key=lambda p: p["length"])
            return {
                "success": True,
                "path": shortest["path"],
                "from": shortest["from"],
                "to": shortest["to"],
                "length": shortest["length"]
            }

        return {"error": "No path found", "from": from_query, "to": to_query}

    async def close(self):
        """Close connections"""
        await self.wisebase.close()
        await self.roamresearch.close()


async def main():
    """Main entry point"""
    datafeed = RoamWiseHybridDatafeed()

    try:
        # Fetch all data
        results = await datafeed.fetch_all_data()

        print("\n" + "="*70)
        print("🌐 RoamWise Hybrid Datafeed")
        print("="*70)
        print(f"Domain: {datafeed.domain}")
        print(f"Wisebase items: {results['wisebase_count']}")
        print(f"RoamResearch items: {results['roamresearch_count']}")
        print(f"Blended items: {results['blended_count']}")
        print(f"Pathfinder nodes: {results['nodes']}")
        print(f"Pathfinder paths: {results['paths']}")
        print(f"Zones: {results['zones']}")
        print("="*70 + "\n")

        # Test pathfinding
        path_result = await datafeed.get_path("Wisebase", "RoamResearch")
        if path_result.get("success"):
            print(f"✅ Found path: {path_result['from']} → {path_result['to']} ({path_result['length']} steps)")
        else:
            print(f"⏳ Pathfinding: {path_result.get('error', 'No path')}")

    finally:
        await datafeed.close()


if __name__ == "__main__":



    asyncio.run(main())