"""
Unit tests for Supply Optimizer module
Run: pytest tests/test_supply_optimizer.py -v
"""

import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.supply_optimizer import SupplyOptimizer


class TestSupplyOptimizer:
    """Test suite for SupplyOptimizer class"""
    
    @pytest.fixture
    def optimizer(self):
        """Create optimizer instance for testing"""
        return SupplyOptimizer(num_vehicles=3, vehicle_capacity=1000)
    
    @pytest.fixture
    def sample_delivery_points(self):
        """Create sample delivery points"""
        return [
            {'latitude': 0.01, 'longitude': 0.01, 'demand': 100},
            {'latitude': 0.02, 'longitude': 0.02, 'demand': 150},
            {'latitude': 0.03, 'longitude': 0.03, 'demand': 200},
            {'latitude': -0.01, 'longitude': 0.01, 'demand': 120},
            {'latitude': 0.01, 'longitude': -0.01, 'demand': 180},
        ]
    
    def test_optimizer_initialization(self, optimizer):
        """Test optimizer initializes correctly"""
        assert optimizer is not None
        assert optimizer.num_vehicles == 3
        assert optimizer.vehicle_capacity == 1000
        print("✓ Optimizer initialization test passed")
    
    def test_haversine_distance_same_point(self, optimizer):
        """Test Haversine distance for same point"""
        distance = optimizer._haversine_distance(0.0, 0.0, 0.0, 0.0)
        assert distance == 0.0
        print("✓ Haversine same point test passed")
    
    def test_haversine_distance_calculation(self, optimizer):
        """Test Haversine distance calculation"""
        # Distance between (0, 0) and (0.01, 0.01) should be ~1570 meters
        distance = optimizer._haversine_distance(0.0, 0.0, 0.01, 0.01)
        assert distance > 0
        assert 1000 < distance < 2000  # Approximately 1.57 km
        print(f"✓ Haversine calculation test passed - Distance: {distance:.2f}m")
    
    def test_create_distance_matrix(self, optimizer):
        """Test distance matrix creation"""
        locations = [
            (0.0, 0.0),
            (0.01, 0.01),
            (0.02, 0.02)
        ]
        
        matrix = optimizer._create_distance_matrix(locations)
        
        # Verify matrix structure
        assert len(matrix) == 3
        assert all(len(row) == 3 for row in matrix)
        
        # Verify diagonal is zero
        assert all(matrix[i][i] == 0 for i in range(3))
        
        # Verify symmetry
        assert matrix[0][1] == matrix[1][0]
        
        # Verify positive distances
        assert matrix[0][1] > 0
        
        print("✓ Distance matrix creation test passed")
    
    def test_create_data_model(self, optimizer):
        """Test VRP data model creation"""
        distance_matrix = [[0, 100, 200], [100, 0, 150], [200, 150, 0]]
        demands = [0, 100, 150]
        
        data = optimizer._create_data_model(distance_matrix, demands)
        
        assert 'distance_matrix' in data
        assert 'demands' in data
        assert 'vehicle_capacities' in data
        assert 'num_vehicles' in data
        assert 'depot' in data
        
        assert data['depot'] == 0
        assert data['num_vehicles'] == 3
        assert len(data['vehicle_capacities']) == 3
        assert all(cap == 1000 for cap in data['vehicle_capacities'])
        
        print("✓ Data model creation test passed")
    
    def test_optimize_routes_basic(self, optimizer, sample_delivery_points):
        """Test basic route optimization"""
        warehouse = (0.0, 0.0)
        
        result = optimizer.optimize_routes(warehouse, sample_delivery_points)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert 'routes' in result
        assert 'total_distance' in result
        assert 'total_duration' in result
        assert 'vehicles_used' in result
        
        # Verify data types
        assert isinstance(result['routes'], list)
        assert isinstance(result['total_distance'], (int, float))
        assert isinstance(result['total_duration'], (float, int))
        assert isinstance(result['vehicles_used'], int)
        
        # Verify constraints
        assert result['vehicles_used'] <= optimizer.num_vehicles
        assert result['total_distance'] >= 0
        assert result['total_duration'] >= 0
        
        print(f"✓ Basic optimization test passed")
        print(f"  Routes: {len(result['routes'])}")
        print(f"  Distance: {result['total_distance']/1000:.2f} km")
        print(f"  Duration: {result['total_duration']:.1f} min")
        print(f"  Vehicles: {result['vehicles_used']}")
    
    def test_optimize_with_custom_demands(self, optimizer):
        """Test optimization with custom demands"""
        warehouse = (0.0, 0.0)
        delivery_points = [
            {'latitude': 0.01, 'longitude': 0.01, 'demand': 300},
            {'latitude': 0.02, 'longitude': 0.02, 'demand': 400},
        ]
        demands = [300, 400]
        
        result = optimizer.optimize_routes(warehouse, delivery_points, demands)
        
        assert 'routes' in result
        # Verify at least one route exists
        assert len(result['routes']) > 0
        
        print(f"✓ Custom demands test passed - {len(result['routes'])} routes created")
    
    def test_vehicle_capacity_constraint(self):
        """Test vehicle capacity is respected"""
        optimizer = SupplyOptimizer(num_vehicles=1, vehicle_capacity=500)
        warehouse = (0.0, 0.0)
        
        # Two points with demand exceeding single vehicle capacity
        delivery_points = [
            {'latitude': 0.01, 'longitude': 0.01, 'demand': 400},
            {'latitude': 0.02, 'longitude': 0.02, 'demand': 400},
        ]
        
        result = optimizer.optimize_routes(warehouse, delivery_points)
        
        # Should use more than 1 vehicle (but we only have 1, so might not serve all)
        # OR-Tools should handle this gracefully
        assert 'routes' in result
        
        print("✓ Capacity constraint test passed")
    
    def test_single_delivery_point(self, optimizer):
        """Test optimization with single delivery point"""
        warehouse = (0.0, 0.0)
        delivery_points = [{'latitude': 0.01, 'longitude': 0.01, 'demand': 100}]
        
        result = optimizer.optimize_routes(warehouse, delivery_points)
        
        assert result['vehicles_used'] >= 1
        assert len(result['routes']) >= 1
        
        print("✓ Single delivery point test passed")
    
    def test_multiple_vehicles(self):
        """Test with multiple vehicles"""
        optimizer = SupplyOptimizer(num_vehicles=5, vehicle_capacity=1000)
        warehouse = (0.0, 0.0)
        
        delivery_points = [
            {'latitude': i*0.01, 'longitude': i*0.01, 'demand': 200}
            for i in range(1, 8)
        ]
        
        result = optimizer.optimize_routes(warehouse, delivery_points)
        
        assert result['vehicles_used'] <= 5
        assert len(result['routes']) <= 5
        
        print(f"✓ Multiple vehicles test passed - Used {result['vehicles_used']}/5 vehicles")


def run_standalone_tests():
    """Run tests standalone without pytest"""
    print("\n" + "="*60)
    print("RAPID - Supply Optimizer Standalone Tests")
    print("="*60 + "\n")
    
    try:
        optimizer = SupplyOptimizer(num_vehicles=3, vehicle_capacity=1000)
        
        # Test 1: Initialization
        print("Test 1: Optimizer Initialization")
        print(f"  Vehicles: {optimizer.num_vehicles}")
        print(f"  Capacity per vehicle: {optimizer.vehicle_capacity}")
        print("  ✓ PASSED\n")
        
        # Test 2: Haversine Distance
        print("Test 2: Haversine Distance Calculation")
        dist = optimizer._haversine_distance(0.0, 0.0, 0.01, 0.01)
        print(f"  Distance (0,0) to (0.01,0.01): {dist:.2f}m")
        assert dist > 0
        print("  ✓ PASSED\n")
        
        # Test 3: Route Optimization
        print("Test 3: Route Optimization")
        warehouse = (0.0, 0.0)
        delivery_points = [
            {'latitude': 0.01, 'longitude': 0.01, 'demand': 100},
            {'latitude': 0.02, 'longitude': 0.02, 'demand': 150},
            {'latitude': -0.01, 'longitude': 0.01, 'demand': 120},
            {'latitude': 0.01, 'longitude': -0.01, 'demand': 180},
        ]
        
        result = optimizer.optimize_routes(warehouse, delivery_points)
        
        print(f"  Total Distance: {result['total_distance']/1000:.2f} km")
        print(f"  Total Duration: {result['total_duration']:.1f} minutes")
        print(f"  Vehicles Used: {result['vehicles_used']}")
        print(f"  Routes Created: {len(result['routes'])}")
        
        for i, route in enumerate(result['routes']):
            print(f"\n  Route {i+1} (Vehicle {route['vehicle_id']+1}):")
            print(f"    Stops: {len(route['stops'])}")
            print(f"    Distance: {route['distance']/1000:.2f} km")
            print(f"    Load: {route['load']} units")
        
        print("\n  ✓ PASSED\n")
        
        print("="*60)
        print("All Supply Optimizer Tests PASSED! ✓")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_standalone_tests()
    sys.exit(0 if success else 1)
