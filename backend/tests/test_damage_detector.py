"""
Unit tests for Damage Detector module
Run: pytest tests/test_damage_detector.py -v
"""

import pytest
import numpy as np
from PIL import Image
import io
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.damage_detector import DamageDetector


class TestDamageDetector:
    """Test suite for DamageDetector class"""
    
    @pytest.fixture
    def detector(self):
        """Create detector instance for testing"""
        return DamageDetector(confidence_threshold=0.5)
    
    @pytest.fixture
    def sample_image_path(self, tmp_path):
        """Create a sample test image"""
        # Create a simple test image
        img = Image.new('RGB', (640, 480), color='red')
        image_path = tmp_path / "test_image.jpg"
        img.save(image_path)
        return str(image_path)
    
    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes"""
        img = Image.new('RGB', (640, 480), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        return img_bytes.getvalue()
    
    def test_detector_initialization(self, detector):
        """Test detector initializes correctly"""
        assert detector is not None
        assert detector.confidence_threshold == 0.5
        assert detector.model is not None
        assert detector.device in ['cuda', 'cpu']
        print("✓ Detector initialization test passed")
    
    def test_damage_classes(self, detector):
        """Test damage class definitions"""
        assert len(detector.DAMAGE_CLASSES) == 5
        assert detector.DAMAGE_CLASSES[0] == "no-damage"
        assert detector.DAMAGE_CLASSES[1] == "minor-damage"
        assert detector.DAMAGE_CLASSES[2] == "major-damage"
        assert detector.DAMAGE_CLASSES[3] == "destroyed"
        assert detector.DAMAGE_CLASSES[4] == "un-classified"
        print("✓ Damage classes test passed")
    
    def test_severity_descriptions(self, detector):
        """Test severity descriptions exist"""
        assert len(detector.SEVERITY_DESCRIPTIONS) == 5
        assert "No visible damage" in detector.SEVERITY_DESCRIPTIONS[0]
        assert "destroyed" in detector.SEVERITY_DESCRIPTIONS[3].lower()
        print("✓ Severity descriptions test passed")
    
    def test_detect_damage_from_file(self, detector, sample_image_path):
        """Test damage detection from file path"""
        result = detector.detect_damage(sample_image_path)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "damage_class" in result
        assert "severity" in result
        assert "confidence" in result
        assert "bounding_boxes" in result
        assert "description" in result
        
        # Verify data types
        assert isinstance(result["damage_class"], str)
        assert isinstance(result["severity"], int)
        assert isinstance(result["confidence"], float)
        assert isinstance(result["bounding_boxes"], list)
        assert isinstance(result["description"], str)
        
        # Verify ranges
        assert 0 <= result["severity"] <= 4
        assert 0.0 <= result["confidence"] <= 1.0
        
        print(f"✓ Detection from file test passed - Severity: {result['severity']}, Confidence: {result['confidence']:.2f}")
    
    def test_detect_damage_from_bytes(self, detector, sample_image_bytes):
        """Test damage detection from image bytes"""
        result = detector.detect_from_bytes(sample_image_bytes)
        
        # Verify result structure
        assert isinstance(result, dict)
        assert "damage_class" in result
        assert "severity" in result
        assert "confidence" in result
        
        # Verify ranges
        assert 0 <= result["severity"] <= 4
        assert 0.0 <= result["confidence"] <= 1.0
        
        print(f"✓ Detection from bytes test passed - Severity: {result['severity']}")
    
    def test_calculate_severity_no_detections(self, detector):
        """Test severity calculation with no detections"""
        # Mock empty results
        class MockResults:
            def __init__(self):
                self.boxes = []
        
        results = [MockResults()]
        severity = detector._calculate_severity(results)
        
        assert severity == 0  # No damage when no detections
        print("✓ No detections test passed")
    
    def test_calculate_confidence_no_detections(self, detector):
        """Test confidence calculation with no detections"""
        class MockResults:
            def __init__(self):
                self.boxes = []
        
        results = [MockResults()]
        confidence = detector._calculate_confidence(results)
        
        assert confidence == 0.0
        print("✓ No confidence test passed")
    
    def test_extract_boxes_empty(self, detector):
        """Test box extraction with no detections"""
        class MockResults:
            def __init__(self):
                self.boxes = []
        
        results = [MockResults()]
        boxes = detector._extract_boxes(results)
        
        assert isinstance(boxes, list)
        assert len(boxes) == 0
        print("✓ Empty boxes extraction test passed")
    
    def test_confidence_threshold(self):
        """Test custom confidence threshold"""
        detector = DamageDetector(confidence_threshold=0.7)
        assert detector.confidence_threshold == 0.7
        print("✓ Custom confidence threshold test passed")
    
    def test_damage_class_mapping(self, detector):
        """Test damage class mapping for all severities"""
        for severity in range(5):
            damage_class = detector.DAMAGE_CLASSES.get(severity)
            assert damage_class is not None
            assert isinstance(damage_class, str)
        print("✓ Damage class mapping test passed")


def run_standalone_tests():
    """Run tests standalone without pytest"""
    print("\n" + "="*60)
    print("RAPID - Damage Detector Standalone Tests")
    print("="*60 + "\n")
    
    try:
        detector = DamageDetector(confidence_threshold=0.5)
        
        # Test 1: Initialization
        print("Test 1: Detector Initialization")
        assert detector is not None
        print(f"  Device: {detector.device}")
        print(f"  Confidence threshold: {detector.confidence_threshold}")
        print("  ✓ PASSED\n")
        
        # Test 2: Damage Classes
        print("Test 2: Damage Classes")
        for severity, class_name in detector.DAMAGE_CLASSES.items():
            print(f"  Severity {severity}: {class_name}")
        print("  ✓ PASSED\n")
        
        # Test 3: Create test image and detect
        print("Test 3: Damage Detection")
        img = Image.new('RGB', (640, 480), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        
        result = detector.detect_from_bytes(img_bytes.getvalue())
        print(f"  Damage Class: {result['damage_class']}")
        print(f"  Severity: {result['severity']}")
        print(f"  Confidence: {result['confidence']:.2%}")
        print(f"  Description: {result['description']}")
        print(f"  Bounding Boxes: {len(result['bounding_boxes'])}")
        print("  ✓ PASSED\n")
        
        print("="*60)
        print("All Damage Detector Tests PASSED! ✓")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n✗ FAILED: {str(e)}\n")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    # Run standalone tests if executed directly
    success = run_standalone_tests()
    sys.exit(0 if success else 1)
