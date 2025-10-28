"""
Graph Neural Network-based damage detector for disaster imagery.
Uses spatial relationships and building context for accurate damage assessment.

Implementation options:
1. Pre-trained model from xBD challenge
2. PyTorch Geometric GCN with quick training
3. Hybrid CNN-GNN approach
"""

import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Dict, List, Tuple, Optional
import numpy as np
from PIL import Image
import cv2

try:
    import torch_geometric
    from torch_geometric.nn import GCNConv, global_mean_pool
    from torch_geometric.data import Data, Batch
    TORCH_GEOMETRIC_AVAILABLE = True
except ImportError:
    TORCH_GEOMETRIC_AVAILABLE = False
    print("⚠️  PyTorch Geometric not installed. Using fallback CNN approach.")

from ultralytics import YOLO


class BuildingGraphGNN(nn.Module):
    """
    Graph Convolutional Network for building damage assessment.
    Models spatial relationships between damaged structures.
    """
    
    def __init__(self, node_features: int = 128, hidden_dim: int = 256, num_classes: int = 5):
        super(BuildingGraphGNN, self).__init__()
        
        # GCN layers
        self.conv1 = GCNConv(node_features, hidden_dim)
        self.conv2 = GCNConv(hidden_dim, hidden_dim)
        self.conv3 = GCNConv(hidden_dim, hidden_dim // 2)
        
        # Classification head
        self.fc1 = nn.Linear(hidden_dim // 2, 64)
        self.fc2 = nn.Linear(64, num_classes)
        
        self.dropout = nn.Dropout(0.3)
    
    def forward(self, data):
        x, edge_index, batch = data.x, data.edge_index, data.batch
        
        # GCN layers with ReLU and dropout
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = self.dropout(x)
        
        x = self.conv3(x, edge_index)
        x = F.relu(x)
        
        # Global pooling
        x = global_mean_pool(x, batch)
        
        # Classification
        x = self.fc1(x)
        x = F.relu(x)
        x = self.dropout(x)
        x = self.fc2(x)
        
        return F.log_softmax(x, dim=1)


class GNNDamageDetector:
    """
    Advanced damage detector using Graph Neural Networks.
    Combines YOLO for detection with GNN for damage classification.
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
        1: "Minor damage: Superficial damage, broken windows",
        2: "Major damage: Partial roof collapse, major structural issues",
        3: "Destroyed: Complete structural collapse",
        4: "Unable to classify damage level"
    }
    
    def __init__(
        self,
        detector_model_path: str = "yolov8n.pt",
        gnn_model_path: Optional[str] = None,
        confidence_threshold: float = 0.5,
        use_gnn: bool = True
    ):
        """
        Initialize GNN-based damage detector.
        
        Args:
            detector_model_path: Path to YOLO detection model
            gnn_model_path: Path to pre-trained GNN model (optional)
            confidence_threshold: Detection confidence threshold
            use_gnn: Whether to use GNN (falls back to heuristics if False)
        """
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.confidence_threshold = confidence_threshold
        self.use_gnn = use_gnn and TORCH_GEOMETRIC_AVAILABLE
        
        # Load YOLO for object detection
        self.detector = YOLO(detector_model_path)
        
        # Load or initialize GNN
        if self.use_gnn:
            self.gnn = BuildingGraphGNN().to(self.device)
            
            if gnn_model_path:
                try:
                    self.gnn.load_state_dict(torch.load(gnn_model_path, map_location=self.device))
                    self.gnn.eval()
                    print(f"✅ Loaded pre-trained GNN from {gnn_model_path}")
                except Exception as e:
                    print(f"⚠️  Could not load GNN model: {e}")
                    print("   Using randomly initialized GNN (demo mode)")
            else:
                print("ℹ️  Using randomly initialized GNN (demo mode)")
                print("   For production, train on xBD dataset or load pre-trained weights")
        else:
            self.gnn = None
            print("⚠️  GNN disabled, using heuristic approach")
    
    def detect_damage(self, image_path: str) -> Dict:
        """
        Detect and classify damage using GNN-based approach.
        
        Args:
            image_path: Path to disaster image
            
        Returns:
            Dictionary with damage assessment results
        """
        # Step 1: Detect objects/buildings with YOLO
        detections = self.detector(image_path, conf=self.confidence_threshold)
        
        if not self.use_gnn or len(detections) == 0 or len(detections[0].boxes) == 0:
            # Fallback to heuristic method
            return self._heuristic_assessment(detections)
        
        # Step 2: Build graph from detections
        graph_data = self._build_spatial_graph(detections[0], image_path)
        
        if graph_data is None:
            return self._heuristic_assessment(detections)
        
        # Step 3: Run GNN inference
        with torch.no_grad():
            self.gnn.eval()
            output = self.gnn(graph_data)
            severity = output.argmax(dim=1).item()
            confidence = torch.exp(output).max().item()
        
        return {
            "damage_class": self.DAMAGE_CLASSES.get(severity, "un-classified"),
            "severity": severity,
            "confidence": confidence,
            "bounding_boxes": self._extract_boxes(detections[0]),
            "description": self.SEVERITY_DESCRIPTIONS.get(severity, "Unknown"),
            "method": "GNN"
        }
    
    def _build_spatial_graph(self, detection_result, image_path: str) -> Optional[Data]:
        """
        Build graph representation from detected objects.
        Nodes = detected objects, Edges = spatial proximity
        """
        boxes = detection_result.boxes
        if len(boxes) == 0:
            return None
        
        num_nodes = len(boxes)
        
        # Extract bounding box features
        node_features = []
        positions = []
        
        for box in boxes:
            # Bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
            
            # Node features: [x_center, y_center, width, height, confidence, class]
            x_center = (x1 + x2) / 2
            y_center = (y1 + y2) / 2
            width = x2 - x1
            height = y2 - y1
            conf = box.conf[0].cpu().item()
            cls = box.cls[0].cpu().item() if len(box.cls) > 0 else 0
            
            # Create feature vector (pad to 128 dimensions)
            features = np.zeros(128)
            features[0] = x_center
            features[1] = y_center
            features[2] = width
            features[3] = height
            features[4] = conf
            features[5] = cls
            
            node_features.append(features)
            positions.append([x_center, y_center])
        
        node_features = torch.tensor(node_features, dtype=torch.float32)
        positions = np.array(positions)
        
        # Build edges based on spatial proximity
        edge_index = self._build_knn_edges(positions, k=min(5, num_nodes - 1))
        
        # Create PyG Data object
        data = Data(
            x=node_features,
            edge_index=edge_index,
            batch=torch.zeros(num_nodes, dtype=torch.long)
        ).to(self.device)
        
        return data
    
    def _build_knn_edges(self, positions: np.ndarray, k: int = 5) -> torch.Tensor:
        """
        Build k-nearest neighbor edges based on spatial distance.
        """
        from scipy.spatial.distance import cdist
        
        num_nodes = len(positions)
        if num_nodes <= 1:
            return torch.empty((2, 0), dtype=torch.long)
        
        # Compute pairwise distances
        distances = cdist(positions, positions)
        
        # Find k nearest neighbors for each node
        edge_list = []
        for i in range(num_nodes):
            # Get k nearest neighbors (excluding self)
            neighbors = np.argsort(distances[i])[1:k+1]
            for j in neighbors:
                edge_list.append([i, j])
        
        edge_index = torch.tensor(edge_list, dtype=torch.long).t().contiguous()
        return edge_index
    
    def _heuristic_assessment(self, detections) -> Dict:
        """
        Fallback heuristic method (same as original).
        """
        if len(detections) == 0 or len(detections[0].boxes) == 0:
            return {
                "damage_class": "no-damage",
                "severity": 0,
                "confidence": 0.0,
                "bounding_boxes": [],
                "description": "No damage detected",
                "method": "heuristic"
            }
        
        boxes = detections[0].boxes
        num_detections = len(boxes)
        avg_confidence = float(boxes.conf.mean()) if len(boxes.conf) > 0 else 0.0
        
        # Heuristic severity calculation
        if num_detections > 10 and avg_confidence > 0.7:
            severity = 3
        elif num_detections > 5 and avg_confidence > 0.6:
            severity = 2
        elif num_detections > 2 and avg_confidence > 0.5:
            severity = 1
        elif num_detections > 0:
            severity = 1
        else:
            severity = 0
        
        return {
            "damage_class": self.DAMAGE_CLASSES.get(severity, "un-classified"),
            "severity": severity,
            "confidence": avg_confidence,
            "bounding_boxes": self._extract_boxes(detections[0]),
            "description": self.SEVERITY_DESCRIPTIONS.get(severity, "Unknown"),
            "method": "heuristic"
        }
    
    def _extract_boxes(self, result) -> List[Dict]:
        """Extract bounding boxes from YOLO results"""
        bounding_boxes = []
        
        if len(result.boxes) == 0:
            return bounding_boxes
        
        for box in result.boxes:
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
        """Detect damage from image bytes"""
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Save temporarily for YOLO
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            cv2.imwrite(tmp.name, img)
            result = self.detect_damage(tmp.name)
        
        import os
        os.unlink(tmp.name)
        
        return result


# Singleton instance
_gnn_detector_instance = None

def get_gnn_damage_detector() -> GNNDamageDetector:
    """Get singleton GNN damage detector instance"""
    global _gnn_detector_instance
    if _gnn_detector_instance is None:
        import os
        detector_path = os.getenv("YOLO_MODEL_PATH", "yolov8n.pt")
        gnn_path = os.getenv("GNN_MODEL_PATH", None)
        confidence = float(os.getenv("CONFIDENCE_THRESHOLD", "0.5"))
        use_gnn = os.getenv("USE_GNN", "true").lower() == "true"
        
        _gnn_detector_instance = GNNDamageDetector(
            detector_model_path=detector_path,
            gnn_model_path=gnn_path,
            confidence_threshold=confidence,
            use_gnn=use_gnn
        )
    return _gnn_detector_instance


if __name__ == "__main__":
    # Demo and testing
    print("GNN Damage Detector - Demo Mode")
    print("="*60)
    
    detector = GNNDamageDetector(use_gnn=TORCH_GEOMETRIC_AVAILABLE)
    
    print(f"Using GNN: {detector.use_gnn}")
    print(f"Device: {detector.device}")
    print(f"PyTorch Geometric Available: {TORCH_GEOMETRIC_AVAILABLE}")
