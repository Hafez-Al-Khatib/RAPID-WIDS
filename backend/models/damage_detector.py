import torch
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple
import os


class DamageDetector:
    """
    YOLOv8-based damage detection model for disaster imagery.
    Classifies damage severity on 0-4 scale based on xBD dataset standards.
    """
    
    DAMAGE_CLASSES = {
        0: "no-damage",
        1: "minor-damage",
        2: "major-damage",
        3: "destroyed",
        4: "un-classified"
    }
    
    SEVERITY_DESCRIPTIONS = {
        0: "No visible damage detected",
        1: "Minor damage: Superficial damage, windows broken",
        2: "Major damage: Partial roof collapse, major structural issues",
        3: "Destroyed: Complete structural collapse",
        4: "Unable to classify damage level"
    }
    
    def __init__(self, model_path: str = None, confidence_threshold: float = 0.5):
        """
        Initialize damage detector with YOLOv8 model.
        
        Args:
            model_path: Path to trained model weights (defaults to YOLOv8n)
            confidence_threshold: Minimum confidence for detections
        """
        self.confidence_threshold = confidence_threshold
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        # Use pretrained YOLOv8 or custom weights
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            # Use YOLOv8n as base model for demo
            self.model = YOLO('yolov8n.pt')
        
        print(f"✅ DamageDetector initialized on {self.device}")
    
    def detect_damage(self, image_path: str) -> Dict:
        """
        Detect and classify damage in an image.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with damage classification results
        """
        # Run inference
        results = self.model(image_path, conf=self.confidence_threshold)
        
        # Parse results
        damage_severity = self._calculate_severity(results)
        confidence = self._calculate_confidence(results)
        bounding_boxes = self._extract_boxes(results)
        
        return {
            "damage_class": self.DAMAGE_CLASSES.get(damage_severity, "un-classified"),
            "severity": damage_severity,
            "confidence": confidence,
            "bounding_boxes": bounding_boxes,
            "description": self.SEVERITY_DESCRIPTIONS.get(damage_severity, "Unknown")
        }
    
    def _calculate_severity(self, results) -> int:
        """
        Calculate overall damage severity from detection results.
        Uses heuristics based on detection count and confidence.
        """
        if len(results) == 0 or len(results[0].boxes) == 0:
            return 0  # No damage detected
        
        boxes = results[0].boxes
        num_detections = len(boxes)
        avg_confidence = float(boxes.conf.mean()) if len(boxes.conf) > 0 else 0.0
        
        # Heuristic damage classification
        # In production, this would use trained classification head
        if num_detections > 10 and avg_confidence > 0.7:
            return 3  # Destroyed
        elif num_detections > 5 and avg_confidence > 0.6:
            return 2  # Major damage
        elif num_detections > 2 and avg_confidence > 0.5:
            return 1  # Minor damage
        elif num_detections > 0:
            return 1  # Minor damage
        else:
            return 0  # No damage
    
    def _calculate_confidence(self, results) -> float:
        """Calculate average confidence across all detections"""
        if len(results) == 0 or len(results[0].boxes) == 0:
            return 0.0
        
        boxes = results[0].boxes
        return float(boxes.conf.mean()) if len(boxes.conf) > 0 else 0.0
    
    def _extract_boxes(self, results) -> List[Dict]:
        """Extract bounding boxes with class and confidence"""
        bounding_boxes = []
        
        if len(results) == 0:
            return bounding_boxes
        
        boxes = results[0].boxes
        
        for box in boxes:
            bounding_boxes.append({
                "x1": float(box.xyxy[0][0]),
                "y1": float(box.xyxy[0][1]),
                "x2": float(box.xyxy[0][2]),
                "y2": float(box.xyxy[0][3]),
                "confidence": float(box.conf[0]),
                "class": int(box.cls[0]) if len(box.cls) > 0 else 0
            })
        
        return bounding_boxes
    
    def detect_from_bytes(self, image_bytes: bytes) -> Dict:
        """
        Detect damage from image bytes (for API uploads).
        
        Args:
            image_bytes: Raw image bytes
            
        Returns:
            Dictionary with damage classification results
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Run inference
        results = self.model(img, conf=self.confidence_threshold)
        
        # Parse results
        damage_severity = self._calculate_severity(results)
        confidence = self._calculate_confidence(results)
        bounding_boxes = self._extract_boxes(results)
        
        return {
            "damage_class": self.DAMAGE_CLASSES.get(damage_severity, "un-classified"),
            "severity": damage_severity,
            "confidence": confidence,
            "bounding_boxes": bounding_boxes,
            "description": self.SEVERITY_DESCRIPTIONS.get(damage_severity, "Unknown")
        }


# Singleton instance
_detector_instance = None

def get_damage_detector() -> DamageDetector:
    """Get singleton damage detector instance"""
    global _detector_instance
    if _detector_instance is None:
        model_path = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
        confidence = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
        _detector_instance = DamageDetector(model_path, confidence)
    return _detector_instance
