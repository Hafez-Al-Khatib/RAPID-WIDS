import torch
from ultralytics import YOLO
import cv2
import numpy as np
from PIL import Image
from typing import Dict, List, Tuple, Optional
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
        0: "No damaged vehicles detected",
        1: "Minor damage: Few damaged/displaced vehicles",
        2: "Major damage: Multiple damaged/overturned vehicles",
        3: "Severe destruction: Many destroyed vehicles, debris field",
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
        
        # COCO class IDs for vehicles
        self.VEHICLE_CLASSES = {
            2: 'car',
            3: 'motorcycle', 
            5: 'bus',
            7: 'truck'
        }
        
        # Focus on cars primarily (class 2)
        self.TARGET_CLASS = 2  # Car
        
        # Use pretrained YOLOv8 or custom weights
        if model_path and os.path.exists(model_path):
            self.model = YOLO(model_path)
        else:
            # Use YOLOv8n as base model for demo
            self.model = YOLO('yolov8n.pt')
        
        # Initialize Gemini analyzer (optional)
        try:
            from models.gemini_analyzer import get_gemini_analyzer
            self.gemini = get_gemini_analyzer()
        except ImportError:
            self.gemini = None
            print("⚠️  Gemini analyzer not available")
        
        print(f"✅ DamageDetector initialized on {self.device}")
        print(f"🚗 Focusing on vehicle detection (cars)")
        if self.gemini and self.gemini.model:
            print(f"🤖 Gemini VLM analysis enabled")
    
    def detect_damage(self, image_path: str) -> Dict:
        """
        Detect and classify damage in an image using YOLO + optional Gemini VLM.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Dictionary with damage classification results
        """
        # Run YOLO inference for car counting
        results = self.model(image_path, conf=self.confidence_threshold)
        
        # Parse YOLO results
        yolo_severity = self._calculate_severity(results)
        yolo_confidence = self._calculate_confidence(results)
        bounding_boxes = self._extract_boxes(results)
        
        # Try Gemini VLM analysis if available
        gemini_result = None
        if self.gemini and self.gemini.model:
            gemini_result = self.gemini.analyze_disaster_image(image_path)
        
        # Combine results (prefer Gemini if available, otherwise use YOLO)
        if gemini_result and gemini_result.get('available'):
            # Use Gemini's analysis as primary
            final_severity = gemini_result.get('severity', yolo_severity)
            final_confidence = gemini_result.get('confidence', yolo_confidence)
            description = gemini_result.get('description', self.SEVERITY_DESCRIPTIONS.get(final_severity, "Unknown"))
            
            return {
                "damage_class": self.DAMAGE_CLASSES.get(final_severity, "un-classified"),
                "severity": final_severity,
                "confidence": final_confidence,
                "bounding_boxes": bounding_boxes,
                "description": description,
                "gemini_analysis": {
                    "indicators": gemini_result.get('indicators', []),
                    "recommendations": gemini_result.get('recommendations', ''),
                    "raw_response": gemini_result.get('raw_response', '')
                },
                "yolo_analysis": {
                    "severity": yolo_severity,
                    "confidence": yolo_confidence,
                    "car_count": len(bounding_boxes)
                },
                "analysis_method": "gemini_vlm"
            }
        else:
            # Fallback to YOLO-only analysis
            return {
                "damage_class": self.DAMAGE_CLASSES.get(yolo_severity, "un-classified"),
                "severity": yolo_severity,
                "confidence": yolo_confidence,
                "bounding_boxes": bounding_boxes,
                "description": self.SEVERITY_DESCRIPTIONS.get(yolo_severity, "Unknown"),
                "yolo_analysis": {
                    "car_count": len(bounding_boxes)
                },
                "analysis_method": "yolo_only"
            }
    
    def _calculate_severity(self, results) -> int:
        """
        Calculate damage severity based on vehicle detections.
        
        Logic:
        - No detections at all (including cars) = No damage (clean scene)
        - Few cars detected normally = No damage (normal traffic)
        - Many cars detected = Higher severity (more people affected)
        
        NOTE: This uses COCO-trained YOLO to detect cars as damage proxy.
        For production, use xBD-trained model.
        """
        if len(results) == 0 or len(results[0].boxes) == 0:
            # Nothing detected at all - clean scene
            return 0  # No damage
        
        boxes = results[0].boxes
        classes = boxes.cls.cpu().numpy() if len(boxes.cls) > 0 else []
        
        # Filter for cars only (class 2)
        car_detections = sum(1 for cls in classes if int(cls) == self.TARGET_CLASS)
        
        # Calculate severity based on car count
        # For disaster imagery, many cars = many people affected
        if car_detections == 0:
            # Detections exist but no cars - unclear scene
            return 0  # No damage
        elif car_detections >= 10:
            # Very many cars - major disaster impact
            return 3  # Severe destruction (many people affected)
        elif car_detections >= 6:
            # Many cars - significant impact
            return 2  # Major damage
        elif car_detections >= 3:
            # Several cars - moderate impact
            return 1  # Minor damage
        else:
            # 1-2 cars - normal/minimal
            return 0  # No damage
    
    def _calculate_confidence(self, results) -> float:
        """Calculate average confidence across all detections"""
        if len(results) == 0 or len(results[0].boxes) == 0:
            return 0.0
        
        boxes = results[0].boxes
        return float(boxes.conf.mean()) if len(boxes.conf) > 0 else 0.0
    
    def _extract_boxes(self, results) -> List[Dict]:
        """Extract bounding box information from YOLO results (cars only)"""
        boxes_list = []
        
        if len(results) == 0 or len(results[0].boxes) == 0:
            return boxes_list
        
        boxes = results[0].boxes
        for box in boxes:
            cls = int(box.cls)
            # Only include cars (class 2)
            if cls == self.TARGET_CLASS:
                boxes_list.append({
                    "x1": float(box.xyxy[0][0]),
                    "y1": float(box.xyxy[0][1]),
                    "x2": float(box.xyxy[0][2]),
                    "y2": float(box.xyxy[0][3]),
                    "confidence": float(box.conf),
                    "class": cls,
                    "class_name": "car"
                })
        
        return boxes_list
    
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
