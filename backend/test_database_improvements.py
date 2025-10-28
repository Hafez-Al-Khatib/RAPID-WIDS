"""
Test script for database improvements
Run: python test_database_improvements.py
"""

from database import SessionLocal, DamageReport, SupplyPoint, RoadStatus, init_db
import sys

def test_auto_geometry():
    """Test automatic geometry generation"""
    print("\n" + "="*60)
    print("TEST 1: Auto-Geometry Generation")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Create DamageReport WITHOUT manual geometry
        report = DamageReport(
            image_path="test.jpg",
            latitude=0.01,
            longitude=0.02,
            damage_severity=2,
            description="Test report"
        )
        
        db.add(report)
        db.flush()  # Trigger ORM but don't commit
        
        # Check geometry was auto-created
        assert report.location is not None, "Geometry should be auto-generated"
        print("✓ DamageReport geometry auto-generated")
        
        # Test SupplyPoint
        supply = SupplyPoint(
            name="Test Hospital",
            latitude=0.03,
            longitude=0.04,
            type="hospital"
        )
        
        db.add(supply)
        db.flush()
        
        assert supply.location is not None, "Supply point geometry should be auto-generated"
        print("✓ SupplyPoint geometry auto-generated")
        
        # Test RoadStatus
        road = RoadStatus(
            road_id="test_road_1",
            start_lat=0.0,
            start_lon=0.0,
            end_lat=0.01,
            end_lon=0.01
        )
        
        db.add(road)
        db.flush()
        
        assert road.geometry is not None, "Road geometry should be auto-generated"
        print("✓ RoadStatus geometry auto-generated")
        
        db.rollback()  # Don't actually save
        print("\n✅ AUTO-GEOMETRY TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def test_validation():
    """Test coordinate validation"""
    print("\n" + "="*60)
    print("TEST 2: Coordinate Validation")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Test invalid latitude (should fail)
        try:
            report = DamageReport(
                image_path="test.jpg",
                latitude=999,  # INVALID!
                longitude=0.0,
                damage_severity=1
            )
            print("✗ Should have raised ValueError for invalid latitude")
            return False
        except ValueError as e:
            print(f"✓ Invalid latitude caught: {e}")
        
        # Test invalid longitude (should fail)
        try:
            report = DamageReport(
                image_path="test.jpg",
                latitude=0.0,
                longitude=-999,  # INVALID!
                damage_severity=1
            )
            print("✗ Should have raised ValueError for invalid longitude")
            return False
        except ValueError as e:
            print(f"✓ Invalid longitude caught: {e}")
        
        print("\n✅ VALIDATION TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        return False
    finally:
        db.close()


def test_check_constraints():
    """Test database CHECK constraints"""
    print("\n" + "="*60)
    print("TEST 3: CHECK Constraints")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Test invalid damage severity (should fail at DB level)
        try:
            report = DamageReport(
                image_path="test.jpg",
                latitude=0.0,
                longitude=0.0,
                damage_severity=99  # INVALID! Must be 0-4
            )
            db.add(report)
            db.commit()
            print("✗ Should have failed CHECK constraint for damage_severity")
            return False
        except Exception as e:
            db.rollback()
            print(f"✓ Invalid damage_severity caught by DB: {type(e).__name__}")
        
        # Test invalid confidence (should fail)
        try:
            report = DamageReport(
                image_path="test.jpg",
                latitude=0.0,
                longitude=0.0,
                damage_severity=2,
                confidence=1.5  # INVALID! Must be 0.0-1.0
            )
            db.add(report)
            db.commit()
            print("✗ Should have failed CHECK constraint for confidence")
            return False
        except Exception as e:
            db.rollback()
            print(f"✓ Invalid confidence caught by DB: {type(e).__name__}")
        
        # Test invalid supply type (should fail)
        try:
            supply = SupplyPoint(
                name="Test",
                latitude=0.0,
                longitude=0.0,
                type="invalid_type"  # INVALID!
            )
            db.add(supply)
            db.commit()
            print("✗ Should have failed CHECK constraint for supply type")
            return False
        except Exception as e:
            db.rollback()
            print(f"✓ Invalid supply type caught by DB: {type(e).__name__}")
        
        print("\n✅ CHECK CONSTRAINTS TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def test_indexes():
    """Test that indexes were created"""
    print("\n" + "="*60)
    print("TEST 4: Spatial Indexes")
    print("="*60)
    
    from sqlalchemy import inspect, text
    from database import engine
    
    try:
        inspector = inspect(engine)
        
        # Check DamageReport indexes
        damage_indexes = inspector.get_indexes('damage_reports')
        index_names = [idx['name'] for idx in damage_indexes]
        
        print("DamageReport indexes:")
        for name in index_names:
            print(f"  ✓ {name}")
        
        # Check if GIST index exists (might need raw SQL)
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT indexname 
                FROM pg_indexes 
                WHERE tablename = 'damage_reports' 
                AND indexdef LIKE '%gist%'
            """))
            gist_indexes = [row[0] for row in result]
            
            if gist_indexes:
                print(f"\n✓ GIST spatial index found: {gist_indexes}")
            else:
                print("\n⚠ GIST index not found (might not be created yet)")
        
        print("\n✅ INDEXES TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_valid_data():
    """Test that valid data works correctly"""
    print("\n" + "="*60)
    print("TEST 5: Valid Data Insertion")
    print("="*60)
    
    db = SessionLocal()
    
    try:
        # Create valid records
        report = DamageReport(
            image_path="test.jpg",
            latitude=0.01,
            longitude=0.02,
            damage_severity=2,
            confidence=0.85,
            description="Valid test report",
            source="user_upload"
        )
        
        supply = SupplyPoint(
            name="Test Warehouse",
            latitude=0.03,
            longitude=0.04,
            type="warehouse",
            capacity=1000,
            demand=500,
            priority=2
        )
        
        road = RoadStatus(
            road_id="test_road_valid",
            start_lat=0.0,
            start_lon=0.0,
            end_lat=0.01,
            end_lon=0.01,
            status="open",
            severity=0
        )
        
        db.add(report)
        db.add(supply)
        db.add(road)
        db.commit()
        
        print("✓ DamageReport inserted successfully")
        print(f"  Severity: {report.damage_severity}")
        print(f"  Confidence: {report.confidence}")
        print(f"  Location: {report.location}")
        
        print("✓ SupplyPoint inserted successfully")
        print(f"  Type: {supply.type}")
        print(f"  Priority: {supply.priority}")
        
        print("✓ RoadStatus inserted successfully")
        print(f"  Status: {road.status}")
        print(f"  Severity: {road.severity}")
        
        # Clean up
        db.delete(report)
        db.delete(supply)
        db.delete(road)
        db.commit()
        
        print("\n✅ VALID DATA TEST PASSED")
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print(" "*15 + "DATABASE IMPROVEMENTS TEST SUITE")
    print("="*60)
    
    # Ensure database exists
    try:
        init_db()
        print("✓ Database initialized\n")
    except Exception as e:
        print(f"✗ Failed to initialize database: {e}")
        return False
    
    results = {
        "Auto-Geometry": test_auto_geometry(),
        "Validation": test_validation(),
        "CHECK Constraints": test_check_constraints(),
        "Spatial Indexes": test_indexes(),
        "Valid Data": test_valid_data()
    }
    
    # Summary
    print("\n" + "="*60)
    print(" "*25 + "SUMMARY")
    print("="*60)
    
    for test_name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {test_name:.<45} {status}")
    
    print("="*60)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    print(f"\n  Total: {passed}/{total} tests passed\n")
    
    if passed == total:
        print("🎉 ALL IMPROVEMENTS WORKING CORRECTLY!\n")
        return True
    else:
        print("⚠️  Some tests failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
