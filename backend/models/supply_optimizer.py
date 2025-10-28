from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import numpy as np
from typing import List, Dict, Tuple
import math


class SupplyOptimizer:
    """
    Google OR-Tools based Vehicle Routing Problem (VRP) solver
    for optimizing emergency supply distribution routes.
    """
    
    def __init__(self, num_vehicles: int = 5, vehicle_capacity: int = 1000):
        """
        Initialize supply optimizer.
        
        Args:
            num_vehicles: Number of available vehicles
            vehicle_capacity: Maximum capacity per vehicle
        """
        self.num_vehicles = num_vehicles
        self.vehicle_capacity = vehicle_capacity
    
    def optimize_routes(
        self,
        warehouse: Tuple[float, float],
        delivery_points: List[Dict],
        demands: List[int] = None
    ) -> Dict:
        """
        Optimize delivery routes from warehouse to affected areas.
        
        Args:
            warehouse: (lat, lon) of warehouse/depot
            delivery_points: List of dicts with 'latitude', 'longitude', 'demand'
            demands: List of demand values for each point (optional)
            
        Returns:
            Dictionary with optimized routes, distance, and duration
        """
        # Build location list (warehouse + delivery points)
        locations = [warehouse]
        for point in delivery_points:
            locations.append((point['latitude'], point['longitude']))
        
        # Extract demands
        if demands is None:
            demands = [point.get('demand', 100) for point in delivery_points]
        demands = [0] + demands  # Warehouse has 0 demand
        
        # Create distance matrix
        distance_matrix = self._create_distance_matrix(locations)
        
        # Create data model
        data = self._create_data_model(distance_matrix, demands)
        
        # Solve VRP
        solution = self._solve_vrp(data)
        
        return solution
    
    def _create_distance_matrix(self, locations: List[Tuple[float, float]]) -> List[List[int]]:
        """
        Create distance matrix using Haversine formula.
        Returns distances in meters (as integers for OR-Tools).
        """
        n = len(locations)
        matrix = [[0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                if i != j:
                    dist = self._haversine_distance(
                        locations[i][0], locations[i][1],
                        locations[j][0], locations[j][1]
                    )
                    matrix[i][j] = int(dist)  # Convert to integer meters
        
        return matrix
    
    def _haversine_distance(
        self,
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """
        Calculate Haversine distance between two coordinates in meters.
        """
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
    
    def _create_data_model(self, distance_matrix: List[List[int]], demands: List[int]) -> Dict:
        """Create data model for OR-Tools VRP solver"""
        data = {}
        data['distance_matrix'] = distance_matrix
        data['demands'] = demands
        data['vehicle_capacities'] = [self.vehicle_capacity] * self.num_vehicles
        data['num_vehicles'] = self.num_vehicles
        data['depot'] = 0  # Warehouse is at index 0
        return data
    
    def _solve_vrp(self, data: Dict) -> Dict:
        """
        Solve VRP using OR-Tools.
        
        Returns:
            Dictionary with routes and metrics
        """
        # Create routing model
        manager = pywrapcp.RoutingIndexManager(
            len(data['distance_matrix']),
            data['num_vehicles'],
            data['depot']
        )
        routing = pywrapcp.RoutingModel(manager)
        
        # Define cost callback
        def distance_callback(from_index, to_index):
            from_node = manager.IndexToNode(from_index)
            to_node = manager.IndexToNode(to_index)
            return data['distance_matrix'][from_node][to_node]
        
        transit_callback_index = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
        
        # Add capacity constraint
        def demand_callback(from_index):
            from_node = manager.IndexToNode(from_index)
            return data['demands'][from_node]
        
        demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
        routing.AddDimensionWithVehicleCapacity(
            demand_callback_index,
            0,  # null capacity slack
            data['vehicle_capacities'],
            True,  # start cumul to zero
            'Capacity'
        )
        
        # Set search parameters
        search_parameters = pywrapcp.DefaultRoutingSearchParameters()
        search_parameters.first_solution_strategy = (
            routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        )
        search_parameters.local_search_metaheuristic = (
            routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        )
        search_parameters.time_limit.FromSeconds(1)
        
        # Solve
        solution = routing.SolveWithParameters(search_parameters)
        
        if solution:
            return self._extract_solution(manager, routing, solution, data)
        else:
            return {
                "routes": [],
                "total_distance": 0,
                "total_duration": 0,
                "vehicles_used": 0,
                "error": "No solution found"
            }
    
    def _extract_solution(self, manager, routing, solution, data) -> Dict:
        """Extract routes from OR-Tools solution"""
        routes = []
        total_distance = 0
        vehicles_used = 0
        
        for vehicle_id in range(data['num_vehicles']):
            index = routing.Start(vehicle_id)
            route = {
                "vehicle_id": vehicle_id,
                "stops": [],
                "distance": 0,
                "load": 0
            }
            
            route_distance = 0
            route_load = 0
            
            while not routing.IsEnd(index):
                node_index = manager.IndexToNode(index)
                route["stops"].append(node_index)
                route_load += data['demands'][node_index]
                
                previous_index = index
                index = solution.Value(routing.NextVar(index))
                route_distance += routing.GetArcCostForVehicle(
                    previous_index, index, vehicle_id
                )
            
            # Add final depot
            route["stops"].append(manager.IndexToNode(index))
            route["distance"] = route_distance
            route["load"] = route_load
            
            # Calculate duration for this route (assuming 50 km/h average speed)
            route["duration"] = (route_distance / 1000) / 50 * 60  # minutes
            
            if len(route["stops"]) > 2:  # Has actual deliveries
                routes.append(route)
                total_distance += route_distance
                vehicles_used += 1
        
        # Estimate duration (assuming 50 km/h average speed)
        total_duration = (total_distance / 1000) / 50 * 60  # minutes
        
        return {
            "routes": routes,
            "total_distance": total_distance,
            "total_duration": total_duration,
            "vehicles_used": vehicles_used
        }


# Singleton instance
_optimizer_instance = None

def get_supply_optimizer() -> SupplyOptimizer:
    """Get singleton supply optimizer instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        import os
        num_vehicles = int(os.getenv("MAX_VEHICLES", "10"))
        capacity = int(os.getenv("VEHICLE_CAPACITY", "1000"))
        _optimizer_instance = SupplyOptimizer(num_vehicles, capacity)
    return _optimizer_instance
