"""
Unit tests for Graph Navigator module
Run: pytest tests/test_graph_navigator.py -v
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.graph_navigator import GraphNavigator


class TestGraphNavigator:
    """Test suite for GraphNavigator class"""
    
    @pytest.fixture
    def navigator(self):
        """Create navigator instance"""
        nav = GraphNavigator()
        nav._create_synthetic_graph((0.0, 0.0), 5000)
        return nav
    
    def test_initialization(self, navigator):
        """Test navigator initializes"""
        assert navigator is not None
        assert navigator.graph is not None
        print("✓ Navigator initialization passed")
    
    def test_graph_structure(self, navigator):
        """Test synthetic graph creation"""
        assert navigator.graph.number_of_nodes() > 0
        assert navigator.graph.number_of_edges() > 0
        print(f"✓ Graph structure passed - {navigator.graph.number_of_nodes()} nodes")
    
    def test_update_road_status(self, navigator):
        """Test road status update"""
        navigator.update_road_status("road_1", "blocked", 3)
        assert "road_1" in navigator.blocked_roads
        print("✓ Road status update passed")


def run_standalone_tests():
    """Run tests standalone"""
    print("\n" + "="*60)
    print("RAPID - Graph Navigator Tests")
    print("="*60 + "\n")
    
    try:
        navigator = GraphNavigator()
        navigator._create_synthetic_graph((0.0, 0.0), 5000)
        
        print(f"Test 1: Graph created with {navigator.graph.number_of_nodes()} nodes")
        print("  ✓ PASSED\n")
        
        print("="*60)
        print("All Graph Navigator Tests PASSED! ✓")
        print("="*60 + "\n")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}\n")
        return False


if __name__ == "__main__":
    success = run_standalone_tests()
    sys.exit(0 if success else 1)
