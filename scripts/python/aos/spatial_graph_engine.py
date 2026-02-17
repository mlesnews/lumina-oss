#!/usr/bin/env python3
"""
AOS Spatial Graph Engine

Mathematical graph representation of all systems in multi-dimensional space.
Maps systems using spatial coordinates and graph algorithms.

Tags: #AOS #SPATIAL #GRAPH #MATHEMATICAL @JARVIS @LUMINA
"""

import networkx as nx
import math
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from enum import Enum

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AOSSpatialGraphEngine")


class Dimension(Enum):
    """Multi-dimensional coordinate system"""
    X = 'x'  # Spatial X
    Y = 'y'  # Spatial Y
    Z = 'z'  # Spatial Z
    T = 't'  # Time
    P = 'p'  # Platform (Windows=0, Linux=1, macOS=2, ...)
    F = 'f'  # Framework (Python=0, Rust=1, Go=2, ...)
    I = 'i'  # Infrastructure (Docker=0, K8s=1, Bare=2, ...)
    R = 'r'  # Reality (Physical=0, Virtual=1, Quantum=2, ...)


@dataclass
class ComponentCoordinates:
    """Multi-dimensional coordinates for a component"""
    x: float = 0.0  # Spatial X
    y: float = 0.0  # Spatial Y
    z: float = 0.0  # Spatial Z
    t: float = 0.0  # Time
    p: int = 0       # Platform (Windows=0, Linux=1, macOS=2, ...)
    f: int = 0       # Framework (Python=0, Rust=1, Go=2, ...)
    i: int = 0       # Infrastructure (Docker=0, K8s=1, Bare=2, ...)
    r: int = 0       # Reality (Physical=0, Virtual=1, Quantum=2, ...)

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary"""
        return {
            'x': self.x, 'y': self.y, 'z': self.z,
            't': self.t, 'p': self.p, 'f': self.f,
            'i': self.i, 'r': self.r
        }

    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'ComponentCoordinates':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in ['x', 'y', 'z', 't', 'p', 'f', 'i', 'r']})


class SpatialGraphEngine:
    """
    Mathematical graph representation of all systems in multi-dimensional space.

    Maps systems using:
    - Spatial coordinates (x, y, z)
    - Time dimension (t)
    - Platform dimension (p)
    - Framework dimension (f)
    - Infrastructure dimension (i)
    - Reality dimension (r)
    """

    def __init__(self):
        """Initialize spatial graph engine"""
        self.graph = nx.MultiDiGraph()
        self.dimensions = [dim.value for dim in Dimension]
        self.platform_map = {
            'windows': 0, 'linux': 1, 'macos': 2,
            'ios': 3, 'android': 4, 'web': 5
        }
        self.framework_map = {
            'python': 0, 'rust': 1, 'go': 2,
            'javascript': 3, 'java': 4, 'cpp': 5
        }
        self.infrastructure_map = {
            'docker': 0, 'kubernetes': 1, 'bare': 2,
            'vm': 3, 'cloud': 4
        }
        self.reality_map = {
            'physical': 0, 'virtual': 1, 'quantum': 2,
            'docker': 3, 'kubernetes': 4
        }
        logger.info("🌐 AOS Spatial Graph Engine initialized")

    def add_component(
        self,
        component_id: str,
        coordinates: ComponentCoordinates,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add component to spatial graph.

        Args:
            component_id: Unique identifier for component
            coordinates: Multi-dimensional coordinates
            properties: Additional properties (type, status, etc.)
        """
        if properties is None:
            properties = {}

        self.graph.add_node(
            component_id,
            coordinates=coordinates.to_dict(),
            **properties
        )

        logger.debug(f"Added component: {component_id} at {coordinates}")

    def add_connection(
        self,
        source: str,
        target: str,
        weight: Optional[float] = None,
        properties: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add connection between components.

        Args:
            source: Source component ID
            target: Target component ID
            weight: Connection weight (distance if None)
            properties: Additional connection properties
        """
        if weight is None:
            weight = self.calculate_distance(source, target)

        if properties is None:
            properties = {}

        self.graph.add_edge(
            source,
            target,
            weight=weight,
            **properties
        )

        logger.debug(f"Added connection: {source} -> {target} (weight={weight:.2f})")

    def calculate_distance(
        self,
        node_a: str,
        node_b: str
    ) -> float:
        """
        Calculate multi-dimensional distance between two nodes.

        Uses Euclidean distance across all dimensions.

        Args:
            node_a: First node ID
            node_b: Second node ID

        Returns:
            Multi-dimensional distance
        """
        if node_a not in self.graph or node_b not in self.graph:
            return float('inf')

        coords_a = self.graph.nodes[node_a]['coordinates']
        coords_b = self.graph.nodes[node_b]['coordinates']

        # Calculate Euclidean distance across all dimensions
        distance = math.sqrt(
            sum((coords_a[dim] - coords_b[dim])**2 
                for dim in self.dimensions)
        )

        return distance

    def find_optimal_path(
        self,
        source: str,
        target: str,
        algorithm: str = 'dijkstra'
    ) -> List[str]:
        """
        Find optimal path between two nodes using spatial algorithms.

        Args:
            source: Source node ID
            target: Target node ID
            algorithm: Algorithm to use ('dijkstra', 'astar', 'bellman-ford')

        Returns:
            List of node IDs representing the path
        """
        if source not in self.graph or target not in self.graph:
            logger.warning(f"Nodes not found: {source} or {target}")
            return []

        try:
            if algorithm == 'dijkstra':
                path = nx.shortest_path(
                    self.graph,
                    source,
                    target,
                    weight='weight'
                )
            elif algorithm == 'astar':
                # A* with multi-dimensional heuristic
                def heuristic(u, v):
                    return self.calculate_distance(u, v)
                path = nx.astar_path(
                    self.graph,
                    source,
                    target,
                    heuristic=heuristic,
                    weight='weight'
                )
            elif algorithm == 'bellman-ford':
                path = nx.bellman_ford_path(
                    self.graph,
                    source,
                    target,
                    weight='weight'
                )
            else:
                logger.warning(f"Unknown algorithm: {algorithm}, using dijkstra")
                path = nx.shortest_path(
                    self.graph,
                    source,
                    target,
                    weight='weight'
                )

            logger.info(f"Found path from {source} to {target}: {len(path)} nodes")
            return path

        except nx.NetworkXNoPath:
            logger.warning(f"No path found from {source} to {target}")
            return []

    def find_closest_components(
        self,
        component_id: str,
        max_distance: float = 10.0,
        max_results: int = 10
    ) -> List[Tuple[str, float]]:
        """
        Find closest components within distance threshold.

        Args:
            component_id: Reference component ID
            max_distance: Maximum distance threshold
            max_results: Maximum number of results

        Returns:
            List of (component_id, distance) tuples
        """
        if component_id not in self.graph:
            return []

        distances = []
        for node in self.graph.nodes():
            if node == component_id:
                continue

            distance = self.calculate_distance(component_id, node)
            if distance <= max_distance:
                distances.append((node, distance))

        # Sort by distance and return top results
        distances.sort(key=lambda x: x[1])
        return distances[:max_results]

    def get_component_coordinates(self, component_id: str) -> Optional[ComponentCoordinates]:
        """Get coordinates for a component"""
        if component_id not in self.graph:
            return None

        coords_dict = self.graph.nodes[component_id]['coordinates']
        return ComponentCoordinates.from_dict(coords_dict)

    def update_coordinates(
        self,
        component_id: str,
        coordinates: ComponentCoordinates
    ) -> None:
        """Update coordinates for a component"""
        if component_id not in self.graph:
            logger.warning(f"Component not found: {component_id}")
            return

        self.graph.nodes[component_id]['coordinates'] = coordinates.to_dict()
        logger.debug(f"Updated coordinates for {component_id}")

    def get_graph_stats(self) -> Dict[str, Any]:
        """Get statistics about the graph"""
        return {
            'nodes': self.graph.number_of_nodes(),
            'edges': self.graph.number_of_edges(),
            'density': nx.density(self.graph),
            'is_connected': nx.is_strongly_connected(self.graph) if self.graph.number_of_nodes() > 0 else False,
            'dimensions': len(self.dimensions)
        }


def main():
    """Example usage"""
    engine = SpatialGraphEngine()

    # Add components
    jarvis_coords = ComponentCoordinates(x=0, y=0, z=0, p=0, f=0, i=0, r=0)
    r5_coords = ComponentCoordinates(x=1, y=1, z=0, p=0, f=0, i=0, r=0)
    marvin_coords = ComponentCoordinates(x=2, y=0, z=0, p=0, f=0, i=0, r=0)

    engine.add_component('jarvis', jarvis_coords, {'type': 'service', 'status': 'active'})
    engine.add_component('r5', r5_coords, {'type': 'service', 'status': 'active'})
    engine.add_component('marvin', marvin_coords, {'type': 'service', 'status': 'active'})

    # Add connections
    engine.add_connection('jarvis', 'r5')
    engine.add_connection('jarvis', 'marvin')
    engine.add_connection('r5', 'marvin')

    # Find optimal path
    path = engine.find_optimal_path('jarvis', 'marvin')
    print(f"Optimal path: {path}")

    # Find closest components
    closest = engine.find_closest_components('jarvis', max_distance=5.0)
    print(f"Closest to jarvis: {closest}")

    # Get stats
    stats = engine.get_graph_stats()
    print(f"Graph stats: {stats}")


if __name__ == "__main__":


    main()