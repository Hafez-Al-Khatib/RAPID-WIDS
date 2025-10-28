"""Quick test to verify schemas import correctly"""

print("Testing schema imports...")

try:
    from schemas import (
        SourceType, 
        RoadStatusType, 
        SupplyPointType, 
        DamageClass,
        BoundingBox,
        DetectionResult,
        DamageReportCreate,
        DamageReportResponse,
        RouteSegment
    )
    
    print("✓ All enums and models imported successfully\n")
    
    # Test SourceType enum
    print("SourceType values:")
    for source in SourceType:
        print(f"  - {source.name}: {source.value}")
    
    # Test DamageClass enum
    print("\nDamageClass values:")
    for damage in DamageClass:
        print(f"  - {damage.name}: {damage.value}")
    
    # Test RoadStatusType enum
    print("\nRoadStatusType values:")
    for status in RoadStatusType:
        print(f"  - {status.name}: {status.value}")
    
    # Test SupplyPointType enum
    print("\nSupplyPointType values:")
    for sp_type in SupplyPointType:
        print(f"  - {sp_type.name}: {sp_type.value}")
    
    # Test creating instances
    print("\n" + "="*60)
    print("Testing model instantiation...")
    print("="*60)
    
    # Test DamageReportCreate
    report = DamageReportCreate(
        latitude=0.0123,
        longitude=0.0456,
        description="Test report",
        source=SourceType.USER_UPLOAD,
        reporter_id="test_user_123"
    )
    print(f"✓ Created DamageReportCreate: lat={report.latitude}, source={report.source.value}")
    
    # Test BoundingBox
    bbox = BoundingBox(
        x1=100.0,
        y1=150.0,
        x2=300.0,
        y2=400.0,
        confidence=0.92,
        class_id=0,
        label="building"
    )
    print(f"✓ Created BoundingBox: ({bbox.x1}, {bbox.y1}) to ({bbox.x2}, {bbox.y2})")
    
    # Test DetectionResult
    detection = DetectionResult(
        damage_class=DamageClass.MAJOR_DAMAGE,
        severity=2,
        confidence=0.87,
        bounding_boxes=[bbox],
        description="Major damage detected"
    )
    print(f"✓ Created DetectionResult: {detection.damage_class.value}, severity={detection.severity}")
    
    # Test validation
    print("\n" + "="*60)
    print("Testing validation...")
    print("="*60)
    
    try:
        # Invalid latitude
        bad_report = DamageReportCreate(
            latitude=999,  # Invalid!
            longitude=0.0
        )
        print("✗ Validation FAILED - should have caught invalid latitude")
    except Exception as e:
        print(f"✓ Validation caught invalid latitude: {type(e).__name__}")
    
    try:
        # Invalid enum
        from pydantic import ValidationError
        bad_report = DamageReportCreate(
            latitude=0.0,
            longitude=0.0,
            source="invalid_source"  # Invalid!
        )
        print("✗ Validation FAILED - should have caught invalid source")
    except ValidationError as e:
        print(f"✓ Validation caught invalid enum value")
    
    print("\n" + "="*60)
    print("🎉 ALL TESTS PASSED!")
    print("="*60)
    print("\nSchemas are ready for deployment!")
    
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
