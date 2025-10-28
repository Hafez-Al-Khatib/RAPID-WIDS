"""
Pydantic schemas for RAPID API
Production-grade with enums, validation, and comprehensive documentation
"""

from pydantic import BaseModel, Field, validator, field_validator
from typing import Optional, List, Union
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMS - Type-safe field values
# ============================================================================

class SourceType(str, Enum):
    """Data source types with validation"""
    USER_UPLOAD = "user_upload"
    SATELLITE = "satellite"
    SIMULATION = "simulation"
    CROWDSOURCED = "crowdsourced"
    OFFICIAL = "official"
    SENSOR = "sensor"


class RoadStatusType(str, Enum):
    """Road status types"""
    OPEN = "open"
    BLOCKED = "blocked"
    DAMAGED = "damaged"
    UNDER_REPAIR = "under_repair"


class SupplyPointType(str, Enum):
    """Supply point types"""
    WAREHOUSE = "warehouse"
    HOSPITAL = "hospital"
    SHELTER = "shelter"
    AFFECTED_AREA = "affected_area"
    DISTRIBUTION_CENTER = "distribution_center"


class DamageClass(str, Enum):
    """Damage classification types"""
    NO_DAMAGE = "no-damage"
    MINOR_DAMAGE = "minor-damage"
    MAJOR_DAMAGE = "major-damage"
    DESTROYED = "destroyed"
    UNCLASSIFIED = "un-classified"


# ============================================================================
# SUB-MODELS - Reusable components
# ============================================================================

class BoundingBox(BaseModel):
    """Bounding box for detected objects/damage"""
    x1: float = Field(..., description="Top-left X coordinate (pixels)")
    y1: float = Field(..., description="Top-left Y coordinate (pixels)")
    x2: float = Field(..., description="Bottom-right X coordinate (pixels)")
    y2: float = Field(..., description="Bottom-right Y coordinate (pixels)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence (0-1)")
    class_id: int = Field(..., description="Object class ID")
    label: Optional[str] = Field(None, description="Human-readable label")
    
    @field_validator('x1', 'y1', 'x2', 'y2')
    @classmethod
    def validate_coordinates(cls, v):
        """Ensure coordinates are non-negative"""
        if v < 0:
            raise ValueError("Coordinates must be non-negative")
        return v


class Coordinate(BaseModel):
    """Geographic coordinate"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")


class RouteSegment(BaseModel):
    """Individual route segment for a vehicle"""
    vehicle_id: int = Field(..., description="Vehicle identifier (0-indexed)")
    stops: List[int] = Field(..., description="Ordered list of stop IDs")
    stop_coordinates: List[Coordinate] = Field(default_factory=list, description="Coordinates of each stop")
    distance: float = Field(..., ge=0, description="Total route distance in meters")
    duration: float = Field(..., ge=0, description="Estimated duration in minutes")
    load: int = Field(..., ge=0, description="Total load/demand served")
    
    class Config:
        json_schema_extra = {
            "example": {
                "vehicle_id": 0,
                "stops": [1, 3, 5],
                "distance": 5420.5,
                "duration": 18.2,
                "load": 450
            }
        }


class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(True, description="Whether the request succeeded")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages if failed")


# ============================================================================
# DAMAGE REPORT SCHEMAS
# ============================================================================

class DamageReportCreate(BaseModel):
    """Schema for creating damage report"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    description: Optional[str] = Field(None, max_length=1000, description="Report description")
    source: SourceType = Field(SourceType.USER_UPLOAD, description="Data source")
    reporter_id: Optional[str] = Field(None, max_length=100, description="Reporter identifier for provenance")
    
    class Config:
        json_schema_extra = {
            "example": {
                "latitude": 0.0123,
                "longitude": 0.0456,
                "description": "Collapsed building on Main St",
                "source": "user_upload",
                "reporter_id": "user_12345"
            }
        }


class DamageReportResponse(BaseModel):
    """Schema for damage report response"""
    id: int
    image_path: str
    latitude: float
    longitude: float
    location: Optional[str] = Field(None, description="WKT geometry (POINT)")
    damage_severity: int = Field(..., ge=0, le=4, description="Severity: 0=none, 1=minor, 2=major, 3=destroyed, 4=unclassified")
    damage_class: Optional[DamageClass] = Field(None, description="Human-readable damage class")
    confidence: float = Field(..., ge=0.0, le=1.0, description="ML model confidence (0-1)")
    verified: bool = Field(False, description="Whether report has been verified")
    description: Optional[str] = None
    timestamp: datetime = Field(..., description="Report creation time (UTC)")
    updated_at: Optional[datetime] = Field(None, description="Last update time (UTC)")
    source: SourceType
    reporter_id: Optional[str] = Field(None, description="Reporter identifier")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "image_path": "uploads/1234567890_0.0123_0.0456.jpg",
                "latitude": 0.0123,
                "longitude": 0.0456,
                "location": "POINT(0.0456 0.0123)",
                "damage_severity": 2,
                "damage_class": "major-damage",
                "confidence": 0.87,
                "verified": False,
                "timestamp": "2024-10-28T12:00:00Z",
                "source": "user_upload"
            }
        }


# ============================================================================
# ROAD STATUS SCHEMAS
# ============================================================================

class RoadStatusUpdate(BaseModel):
    """Schema for updating road status"""
    road_id: str = Field(..., max_length=100, description="Unique road identifier")
    start_lat: float = Field(..., ge=-90, le=90, description="Start latitude")
    start_lon: float = Field(..., ge=-180, le=180, description="Start longitude")
    end_lat: float = Field(..., ge=-90, le=90, description="End latitude")
    end_lon: float = Field(..., ge=-180, le=180, description="End longitude")
    status: RoadStatusType = Field(..., description="Road status")
    severity: int = Field(default=0, ge=0, le=5, description="Damage severity (0-5)")
    source: SourceType = Field(SourceType.CROWDSOURCED, description="Data source")
    verified: Optional[bool] = Field(False, description="Whether status has been verified")
    reporter_id: Optional[str] = Field(None, max_length=100, description="Reporter identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "road_id": "main_st_bridge_1",
                "start_lat": 0.01,
                "start_lon": 0.01,
                "end_lat": 0.02,
                "end_lon": 0.02,
                "status": "blocked",
                "severity": 4,
                "source": "crowdsourced",
                "verified": False
            }
        }


class RoadStatusResponse(BaseModel):
    """Schema for road status response"""
    id: int
    road_id: str
    start_lat: float
    start_lon: float
    end_lat: float
    end_lon: float
    geometry: Optional[str] = Field(None, description="WKT geometry (LINESTRING)")
    status: RoadStatusType
    severity: int = Field(..., ge=0, le=5)
    timestamp: datetime = Field(..., description="Status update time (UTC)")
    updated_at: Optional[datetime] = Field(None, description="Last update time (UTC)")
    source: SourceType
    verified: bool = Field(False, description="Verification status")
    reporter_id: Optional[str] = None
    
    class Config:
        from_attributes = True


# ============================================================================
# SUPPLY POINT SCHEMAS
# ============================================================================

class SupplyPointCreate(BaseModel):
    """Schema for creating supply point"""
    name: str = Field(..., max_length=200, description="Supply point name")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    type: SupplyPointType = Field(..., description="Supply point type")
    demand: int = Field(default=0, ge=0, description="Required supplies (units)")
    capacity: int = Field(default=0, ge=0, description="Available supplies (units)")
    priority: int = Field(default=1, ge=1, le=5, description="Priority level (1=highest, 5=lowest)")
    verified: Optional[bool] = Field(False, description="Verification status")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "Central Hospital",
                "latitude": 0.0123,
                "longitude": 0.0456,
                "type": "hospital",
                "demand": 500,
                "capacity": 100,
                "priority": 1
            }
        }


class SupplyPointResponse(BaseModel):
    """Schema for supply point response"""
    id: int
    name: str
    latitude: float
    longitude: float
    location: Optional[str] = Field(None, description="WKT geometry (POINT)")
    type: SupplyPointType
    demand: int = Field(..., ge=0, description="Required supplies (units)")
    capacity: int = Field(..., ge=0, description="Available supplies (units)")
    priority: int = Field(..., ge=1, le=5, description="Priority (1=highest)")
    timestamp: datetime = Field(..., description="Creation time (UTC)")
    updated_at: Optional[datetime] = Field(None, description="Last update time (UTC)")
    verified: bool = Field(False, description="Verification status")
    
    class Config:
        from_attributes = True


# ============================================================================
# NAVIGATION & OPTIMIZATION SCHEMAS
# ============================================================================

class PathRequest(BaseModel):
    """Schema for pathfinding request"""
    start_lat: float = Field(..., ge=-90, le=90, description="Start latitude")
    start_lon: float = Field(..., ge=-180, le=180, description="Start longitude")
    end_lat: float = Field(..., ge=-90, le=90, description="End latitude")
    end_lon: float = Field(..., ge=-180, le=180, description="End longitude")
    avoid_blocked: bool = Field(True, description="Avoid blocked roads")
    avoid_damaged: bool = Field(False, description="Avoid damaged roads")
    
    class Config:
        json_schema_extra = {
            "example": {
                "start_lat": 0.0,
                "start_lon": 0.0,
                "end_lat": 0.01,
                "end_lon": 0.01,
                "avoid_blocked": True
            }
        }


class PathResponse(BaseModel):
    """Schema for path response"""
    coordinates: List[List[float]] = Field(..., description="Path coordinates [[lon, lat], ...]")
    distance: float = Field(..., ge=0, description="Total distance in meters")
    duration: float = Field(..., ge=0, description="Estimated duration in minutes")
    blocked_roads: List[str] = Field(default_factory=list, description="List of blocked road IDs encountered")
    avoided_roads: List[str] = Field(default_factory=list, description="List of roads avoided")
    
    class Config:
        json_schema_extra = {
            "example": {
                "coordinates": [[0.0, 0.0], [0.005, 0.005], [0.01, 0.01]],
                "distance": 1570.5,
                "duration": 5.2,
                "blocked_roads": ["road_1", "road_3"]
            }
        }


class OptimizeRouteRequest(BaseModel):
    """Schema for supply route optimization"""
    warehouse_id: int = Field(..., description="Warehouse/depot supply point ID")
    delivery_points: List[int] = Field(..., min_length=1, description="List of delivery point IDs")
    num_vehicles: int = Field(default=1, ge=1, le=20, description="Number of vehicles available")
    vehicle_capacity: int = Field(default=1000, ge=1, description="Vehicle capacity in units")
    
    @field_validator('delivery_points')
    @classmethod
    def validate_delivery_points(cls, v):
        """Ensure delivery points list is not empty"""
        if not v:
            raise ValueError("At least one delivery point is required")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "warehouse_id": 1,
                "delivery_points": [3, 5, 7, 9],
                "num_vehicles": 2,
                "vehicle_capacity": 1000
            }
        }


class OptimizeRouteResponse(BaseModel):
    """Schema for optimized route response"""
    routes: List[RouteSegment] = Field(..., description="Optimized routes for each vehicle")
    total_distance: float = Field(..., ge=0, description="Total distance across all routes in meters")
    total_duration: float = Field(..., ge=0, description="Total estimated duration in minutes")
    vehicles_used: int = Field(..., ge=0, description="Number of vehicles utilized")
    unserved_points: List[int] = Field(default_factory=list, description="Delivery points that couldn't be served")
    
    class Config:
        json_schema_extra = {
            "example": {
                "routes": [
                    {
                        "vehicle_id": 0,
                        "stops": [1, 3, 5],
                        "distance": 5420.5,
                        "duration": 18.2,
                        "load": 450
                    }
                ],
                "total_distance": 10500.0,
                "total_duration": 35.5,
                "vehicles_used": 2,
                "unserved_points": []
            }
        }


# ============================================================================
# ML DETECTION SCHEMAS
# ============================================================================

class DetectionResult(BaseModel):
    """Schema for damage detection result"""
    damage_class: DamageClass = Field(..., description="Damage classification")
    severity: int = Field(..., ge=0, le=4, description="Severity level (0-4)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence (0-1)")
    bounding_boxes: List[BoundingBox] = Field(default_factory=list, description="Detected object bounding boxes")
    description: str = Field(..., description="Human-readable description")
    method: Optional[str] = Field(None, description="Detection method used (e.g., 'GNN', 'heuristic')")
    model_version: Optional[str] = Field(None, description="ML model version")
    
    class Config:
        json_schema_extra = {
            "example": {
                "damage_class": "major-damage",
                "severity": 2,
                "confidence": 0.87,
                "bounding_boxes": [
                    {
                        "x1": 100.5,
                        "y1": 150.2,
                        "x2": 300.8,
                        "y2": 400.5,
                        "confidence": 0.92,
                        "class_id": 0,
                        "label": "building"
                    }
                ],
                "description": "Major damage: Partial roof collapse, major structural issues",
                "method": "GNN"
            }
        }


# ============================================================================
# STATISTICS & ANALYTICS SCHEMAS
# ============================================================================

class SystemStatistics(BaseModel):
    """System-wide statistics"""
    total_reports: int = Field(..., ge=0, description="Total damage reports")
    severe_damage: int = Field(..., ge=0, description="Reports with severity >= 3")
    verified_reports: int = Field(..., ge=0, description="Verified damage reports")
    blocked_roads: int = Field(..., ge=0, description="Number of blocked roads")
    damaged_roads: int = Field(..., ge=0, description="Number of damaged roads")
    open_roads: int = Field(..., ge=0, description="Number of open roads")
    supply_points: int = Field(..., ge=0, description="Total supply points")
    warehouses: int = Field(..., ge=0, description="Number of warehouses")
    hospitals: int = Field(..., ge=0, description="Number of hospitals")
    shelters: int = Field(..., ge=0, description="Number of shelters")
    affected_areas: int = Field(..., ge=0, description="Number of affected areas")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Statistics generation time (UTC)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_reports": 127,
                "severe_damage": 34,
                "verified_reports": 89,
                "blocked_roads": 12,
                "supply_points": 45,
                "timestamp": "2024-10-28T12:00:00Z"
            }
        }


# ============================================================================
# UTILITY SCHEMAS
# ============================================================================

class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field("healthy", description="Service status")
    version: str = Field("1.0.0", description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Check time (UTC)")
    database_connected: bool = Field(True, description="Database connection status")
    ml_models_loaded: bool = Field(True, description="ML models loaded status")


class GeoJSONPoint(BaseModel):
    """GeoJSON Point geometry"""
    type: str = Field("Point", const=True)
    coordinates: List[float] = Field(..., min_length=2, max_length=3, description="[longitude, latitude, altitude?]")


class GeoJSONLineString(BaseModel):
    """GeoJSON LineString geometry"""
    type: str = Field("LineString", const=True)
    coordinates: List[List[float]] = Field(..., description="Array of [longitude, latitude] pairs")
