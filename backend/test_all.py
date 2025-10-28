"""
Run all RAPID component tests
Usage: python test_all.py
"""

import sys
import os

# Add tests directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tests'))

def main():
    print("\n" + "="*70)
    print(" "*15 + "RAPID - COMPREHENSIVE UNIT TESTS")
    print("="*70 + "\n")
    
    results = {}
    
    # Test 1: Damage Detector
    print("="*70)
    print("TEST SUITE 1: DAMAGE DETECTOR")
    print("="*70)
    try:
        from tests.test_damage_detector import run_standalone_tests as test_detector
        results['Damage Detector'] = test_detector()
    except Exception as e:
        print(f"✗ Damage Detector tests failed: {e}")
        results['Damage Detector'] = False
    
    # Test 2: Supply Optimizer
    print("\n" + "="*70)
    print("TEST SUITE 2: SUPPLY OPTIMIZER")
    print("="*70)
    try:
        from tests.test_supply_optimizer import run_standalone_tests as test_optimizer
        results['Supply Optimizer'] = test_optimizer()
    except Exception as e:
        print(f"✗ Supply Optimizer tests failed: {e}")
        results['Supply Optimizer'] = False
    
    # Test 3: Graph Navigator
    print("\n" + "="*70)
    print("TEST SUITE 3: GRAPH NAVIGATOR")
    print("="*70)
    try:
        from tests.test_graph_navigator import run_standalone_tests as test_navigator
        results['Graph Navigator'] = test_navigator()
    except Exception as e:
        print(f"✗ Graph Navigator tests failed: {e}")
        results['Graph Navigator'] = False
    
    # Summary
    print("\n" + "="*70)
    print(" "*25 + "TEST SUMMARY")
    print("="*70)
    for component, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {component:.<50} {status}")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\n  Total: {passed}/{total} test suites passed\n")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
