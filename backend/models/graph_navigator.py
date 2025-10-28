import networkx as nx
import numpy as np
from typing import List, Dict, Tuple, Optional
import math
from sqlalchemy.orm import Session
from database import RoadStatus


class GraphNavigator:
    """
    Dynamic graph-based navigation system that combines OpenStreetMap data
    with real-time crowdsourced road status updates.
    """
    
    def __init__(self):
        """Initialize graph navigator"""
        self.graph = nx.Graph()
        self.blocked_roads = set()
        self.damaged_roads = {}
        print("✅ GraphNavigator initialized")
    
    def build_graph_from_osm(self, center: Tuple[float, float], radius: float = 5000):
        """
        Build road network graph from OpenStreetMap data.
        
        Args:
            center: (lat, lon) center point
            radius: Radius in meters
        """
        try:
            import osmnx as ox
            
            # Download road network
            G = ox.graph_from_point(
                center,
                dist=radius,
                network_type='drive',
                simplify=True
            )
            
            # Convert to undirected graph with custom attributes
            self.graph = nx.Graph()
            
            for u, v, data in G.edges(data=True):
                # Get node coordinates
                u_lat, u_lon = G.nodes[u]['y'], G.nodes[u]['x']
                v_lat, v_lon = G.nodes[v]['y'], G.nodes[v]['x']
                
                # Calculate edge weight (distance)
                distance = self._haversine_distance(u_lat, u_lon, v_lat, v_lon)
                
                # Add edge with attributes
                self.graph.add_edge(
                    u, v,
                    weight=distance,
                    length=data.get('length', distance),
                    highway=data.get('highway', 'road'),
                    status='open',
                    u_lat=u_lat,
                    u_lon=u_lon,
                    v_lat=v_lat,
                    v_lon=v_lon
                )
            
            print(f"✅ Built graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
            
        except ImportError:
            print("⚠️ osmnx not available, creating synthetic graph")
            self._create_synthetic_graph(center, radius)
        except Exception as e:
            print(f"⚠️ Error loading OSM data: {e}, creating synthetic graph")
            self._create_synthetic_graph(center, radius)
    
    def _create_synthetic_graph(self, center: Tuple[float, float], radius: float):
        """
        Create synthetic road network for demo purposes.
        Creates a grid-like network around the center point.
        """
        lat_center, lon_center = center
        
        # Create grid (e.g., 10x10)
        grid_size = 10
        step_lat = (radius / 111000) / grid_size  # Convert meters to lat degrees
        step_lon = (radius / (111000 * math.cos(math.radians(lat_center)))) / grid_size
        
        node_id = 0
        node_map = {}
        
        # Create nodes
        for i in range(grid_size):
            for j in range(grid_size):
                lat = lat_center + (i - grid_size/2) * step_lat
                lon = lon_center + (j - grid_size/2) * step_lon
                
                self.graph.add_node(
                    node_id,
                    lat=lat,
                    lon=lon
                )
                node_map[(i, j)] = node_id
                node_id += 1
        
        # Create edges (grid connections)
        for i in range(grid_size):
            for j in range(grid_size):
                current = node_map[(i, j)]
                
                # Connect to right neighbor
                if j < grid_size - 1:
                    neighbor = node_map[(i, j + 1)]
                    self._add_synthetic_edge(current, neighbor)
                
                # Connect to bottom neighbor
                if i < grid_size - 1:
                    neighbor = node_map[(i + 1, j)]
                    self._add_synthetic_edge(current, neighbor)
        
        print(f"✅ Created synthetic graph with {self.graph.number_of_nodes()} nodes and {self.graph.number_of_edges()} edges")
    
    def _add_synthetic_edge(self, u: int, v: int):
        """Add edge with distance calculation"""
        u_lat, u_lon = self.graph.nodes[u]['lat'], self.graph.nodes[u]['lon']
        v_lat, v_lon = self.graph.nodes[v]['lat'], self.graph.nodes[v]['lon']
        
        distance = self._haversine_distance(u_lat, u_lon, v_lat, v_lon)
        
        self.graph.add_edge(
            u, v,
            weight=distance,
            length=distance,
            status='open',
            u_lat=u_lat,
            u_lon=u_lon,
            v_lat=v_lat,
            v_lon=v_lon
        )
    
    def update_road_status(self, road_id: str, status: str, severity: int = 0):
        """
        Update road status based on crowdsourced reports.
        
        Args:
            road_id: Identifier for road segment
            status: 'open', 'blocked', or 'damaged'
            severity: Damage severity (0-4)
        """
        if status == 'blocked':
            self.blocked_roads.add(road_id)
        elif road_id in self.blocked_roads:
            self.blocked_roads.remove(road_id)
        
        if severity > 0:
            self.damaged_roads[road_id] = severity
        
        # Update graph edge weights
        for u, v, data in self.graph.edges(data=True):
            edge_id = f"{u}-{v}"
            if edge_id == road_id or f"{v}-{u}" == road_id:
                data['status'] = status
                
                # Increase weight for damaged roads
                if status == 'blocked':
                    data['weight'] = float('inf')
                elif status == 'damaged' and severity > 0:
                    data['weight'] = data['length'] * (1 + severity * 0.5)
                else:
                    data['weight'] = data['length']
    
    def find_path(
        self,
        start: Tuple[float, float],
        end: Tuple[float, float],
        avoid_blocked: bool = True
    ) -> Optional[Dict]:
        """
        Find optimal path using A* algorithm.
        
        Args:
            start: (lat, lon) start coordinate
            end: (lat, lon) end coordinate
            avoid_blocked: Whether to avoid blocked roads
            
        Returns:
            Dictionary with path coordinates, distance, and duration
        """
        # Find nearest nodes
        start_node = self._find_nearest_node(start)
        end_node = self._find_nearest_node(end)
        
        if start_node is None or end_node is None:
            return None
        
        try:
            # Create weight function
            def weight_func(u, v, data):
                if avoid_blocked and data.get('status') == 'blocked':
                    return float('inf')
                return data.get('weight', data.get('length', 1))
            
            # Find shortest path using A*
            path = nx.astar_path(
                self.graph,
                start_node,
                end_node,
                heuristic=lambda u, v: self._heuristic(u, v),
                weight=weight_func
            )
            
            # Extract coordinates and calculate metrics
            coordinates = []
            total_distance = 0
            blocked_roads = []
            
            for i in range(len(path)):
                node = path[i]
                node_data = self.graph.nodes[node]
                coordinates.append([
                    node_data.get('lon', node_data.get('x', 0)),
                    node_data.get('lat', node_data.get('y', 0))
                ])
                
                if i < len(path) - 1:
                    edge_data = self.graph[path[i]][path[i+1]]
                    total_distance += edge_data.get('length', 0)
                    
                    if edge_data.get('status') == 'blocked':
                        blocked_roads.append(f"{path[i]}-{path[i+1]}")
            
            # Estimate duration (assuming 50 km/h average)
            duration = (total_distance / 1000) / 50 * 60  # minutes
            
            return {
                "coordinates": coordinates,
                "distance": total_distance,
                "duration": duration,
                "blocked_roads": blocked_roads
            }
            
        except nx.NetworkXNoPath:
            return None
        except Exception as e:
            print(f"Error finding path: {e}")
            return None
    
    def _find_nearest_node(self, coord: Tuple[float, float]) -> Optional[int]:
        """Find nearest graph node to given coordinate"""
        lat, lon = coord
        min_dist = float('inf')
        nearest = None
        
        for node, data in self.graph.nodes(data=True):
            node_lat = data.get('lat', data.get('y', 0))
            node_lon = data.get('lon', data.get('x', 0))
            
            dist = self._haversine_distance(lat, lon, node_lat, node_lon)
            
            if dist < min_dist:
                min_dist = dist
                nearest = node
        
        return nearest
    
    def _heuristic(self, u: int, v: int) -> float:
        """A* heuristic: Haversine distance between nodes"""
        u_data = self.graph.nodes[u]
        v_data = self.graph.nodes[v]
        
        u_lat = u_data.get('lat', u_data.get('y', 0))
        u_lon = u_data.get('lon', u_data.get('x', 0))
        v_lat = v_data.get('lat', v_data.get('y', 0))
        v_lon = v_data.get('lon', v_data.get('x', 0))
        
        return self._haversine_distance(u_lat, u_lon, v_lat, v_lon)
    
    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calculate Haversine distance in meters"""
        R = 6371000  # Earth radius in meters
        
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = (math.sin(delta_phi / 2) ** 2 +
             math.cos(phi1) * math.cos(phi2) *
             math.sin(delta_lambda / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def load_road_status_from_db(self, db: Session):
        """Load road status updates from database"""
        road_statuses = db.query(RoadStatus).all()
        
        for road in road_statuses:
            self.update_road_status(road.road_id, road.status, road.severity)
        
        print(f"✅ Loaded {len(road_statuses)} road status updates")


# Singleton instance
_navigator_instance = None

def get_graph_navigator() -> GraphNavigator:
    """Get singleton graph navigator instance"""
    global _navigator_instance
    if _navigator_instance is None:
        _navigator_instance = GraphNavigator()
    return _navigator_instance
