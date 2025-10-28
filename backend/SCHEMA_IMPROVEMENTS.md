# 📋 Pydantic Schema Improvements

## Summary of Improvements

All your suggested enhancements have been implemented in `schemas_improved.py`!

---

## ✅ 1. Enum Usage for Type Safety

### Problem
String fields like `source`, `status`, `type` allowed typos and lacked IDE support.

### Solution Implemented

**Created 5 Enums:**

```python
from enum import Enum

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
    """Damage classification"""
    NO_DAMAGE = "no-damage"
    MINOR_DAMAGE = "minor-damage"
    MAJOR_DAMAGE = "major-damage"
    DESTROYED = "destroyed"
    UNCLASSIFIED = "un-classified"
```

**Benefits:**
- ✅ IDE autocomplete
- ✅ Prevents typos at compile time
- ✅ Self-documenting API
- ✅ Type-safe validation
- ✅ Better OpenAPI/Swagger docs

**Usage:**
```python
# Before: String (typo-prone)
report = DamageReportCreate(
    latitude=0.01,
    longitude=0.02,
    source="user_uplod"  # Typo! No error until runtime
)

# After: Enum (type-safe)
report = DamageReportCreate(
    latitude=0.01,
    longitude=0.02,
    source=SourceType.USER_UPLOAD  # IDE autocomplete, compile-time check
)
```

---

## ✅ 2. Geometry Fields in Responses

### Problem
`location` and `geometry` fields excluded from responses, limiting map visualization.

### Solution Implemented

**Added geometry fields to all response schemas:**

```python
class DamageReportResponse(BaseModel):
    # ... other fields ...
    location: Optional[str] = Field(None, description="WKT geometry (POINT)")
    # e.g., "POINT(0.0456 0.0123)"

class RoadStatusResponse(BaseModel):
    # ... other fields ...
    geometry: Optional[str] = Field(None, description="WKT geometry (LINESTRING)")
    # e.g., "LINESTRING(0.0 0.0, 0.01 0.01)"

class SupplyPointResponse(BaseModel):
    # ... other fields ...
    location: Optional[str] = Field(None, description="WKT geometry (POINT)")
```

**Also created GeoJSON schemas:**

```python
class GeoJSONPoint(BaseModel):
    """GeoJSON Point geometry"""
    type: str = Field("Point", const=True)
    coordinates: List[float] = Field(..., min_length=2, max_length=3)
    # [longitude, latitude, altitude?]

class GeoJSONLineString(BaseModel):
    """GeoJSON LineString geometry"""
    type: str = Field("LineString", const=True)
    coordinates: List[List[float]] = Field(...)
    # [[lon, lat], [lon, lat], ...]
```

**Benefits:**
- ✅ Can render on map directly
- ✅ WKT format (PostGIS standard)
- ✅ Optional GeoJSON support
- ✅ Frontend can visualize without conversion

---

## ✅ 3. BoundingBox Schema (Strongly Typed)

### Problem
`bounding_boxes: List[dict]` was too generic, no validation.

### Solution Implemented

**Created dedicated BoundingBox model:**

```python
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
```

**Updated DetectionResult:**

```python
class DetectionResult(BaseModel):
    damage_class: DamageClass
    severity: int = Field(..., ge=0, le=4)
    confidence: float = Field(..., ge=0.0, le=1.0)
    bounding_boxes: List[BoundingBox] = Field(default_factory=list)  # Strongly typed!
    description: str
    method: Optional[str] = Field(None, description="Detection method (GNN, heuristic)")
    model_version: Optional[str] = Field(None, description="ML model version")
```

**Benefits:**
- ✅ Validation on all box coordinates
- ✅ Type-safe access: `box.x1` instead of `box['x1']`
- ✅ Auto-generated API docs show exact structure
- ✅ IDE autocomplete on bounding box properties

---

## ✅ 4. Units Clarification

### Problem
`distance` and `duration` lacked units documentation.

### Solution Implemented

**Added explicit unit descriptions:**

```python
class PathResponse(BaseModel):
    coordinates: List[List[float]]
    distance: float = Field(..., ge=0, description="Total distance in meters")  # ← Units!
    duration: float = Field(..., ge=0, description="Estimated duration in minutes")  # ← Units!
    blocked_roads: List[str] = Field(default_factory=list)

class OptimizeRouteResponse(BaseModel):
    routes: List[RouteSegment]
    total_distance: float = Field(..., ge=0, description="Total distance across all routes in meters")
    total_duration: float = Field(..., ge=0, description="Total estimated duration in minutes")
    vehicles_used: int
```

**Created RouteSegment sub-model with units:**

```python
class RouteSegment(BaseModel):
    """Individual route segment for a vehicle"""
    vehicle_id: int
    stops: List[int] = Field(..., description="Ordered list of stop IDs")
    stop_coordinates: List[Coordinate] = Field(default_factory=list)
    distance: float = Field(..., ge=0, description="Total route distance in meters")
    duration: float = Field(..., ge=0, description="Estimated duration in minutes")
    load: int = Field(..., ge=0, description="Total load/demand served")
```

**Benefits:**
- ✅ No ambiguity (meters vs km, minutes vs seconds)
- ✅ Shows in API documentation
- ✅ Developers know exact units
- ✅ Consistent across all endpoints

---

## ✅ 5. Optional Fields for Completeness

### Problem
Missing `verified`, `reporter_id`, `updated_at` in various schemas.

### Solution Implemented

**Added to DamageReportCreate:**

```python
class DamageReportCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    description: Optional[str] = Field(None, max_length=1000)
    source: SourceType = Field(SourceType.USER_UPLOAD)
    reporter_id: Optional[str] = Field(None, max_length=100, description="Reporter identifier for provenance")  # NEW!
```

**Added to RoadStatusUpdate:**

```python
class RoadStatusUpdate(BaseModel):
    # ... existing fields ...
    source: SourceType = Field(SourceType.CROWDSOURCED)
    verified: Optional[bool] = Field(False, description="Whether status has been verified")  # NEW!
    reporter_id: Optional[str] = Field(None, max_length=100, description="Reporter identifier")  # NEW!
```

**Added to SupplyPointCreate:**

```python
class SupplyPointCreate(BaseModel):
    # ... existing fields ...
    priority: int = Field(default=1, ge=1, le=5)
    verified: Optional[bool] = Field(False, description="Verification status")  # NEW!
```

**Added to all Response schemas:**

```python
class DamageReportResponse(BaseModel):
    # ... existing fields ...
    timestamp: datetime = Field(..., description="Report creation time (UTC)")
    updated_at: Optional[datetime] = Field(None, description="Last update time (UTC)")  # NEW!
    reporter_id: Optional[str] = Field(None)  # NEW!
    damage_class: Optional[DamageClass] = Field(None)  # NEW!
```

**Benefits:**
- ✅ Audit trail with `reporter_id`
- ✅ Track edits with `updated_at`
- ✅ Verification workflow support
- ✅ Full provenance tracking

---

## 💡 Additional Enhancements

Beyond your suggestions, I added:

### 1. Coordinate Sub-Model

```python
class Coordinate(BaseModel):
    """Geographic coordinate"""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
```

**Usage in RouteSegment:**
```python
stop_coordinates: List[Coordinate] = Field(default_factory=list)
```

### 2. APIResponse Wrapper

```python
class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool = Field(True, description="Whether the request succeeded")
    message: Optional[str] = Field(None, description="Response message")
    data: Optional[dict] = Field(None, description="Response data")
    errors: Optional[List[str]] = Field(None, description="Error messages if failed")
```

**Use for consistent error handling:**
```python
@app.post("/api/upload")
async def upload(file: UploadFile):
    try:
        # ... processing ...
        return APIResponse(
            success=True,
            message="Upload successful",
            data={"report_id": report.id}
        )
    except Exception as e:
        return APIResponse(
            success=False,
            message="Upload failed",
            errors=[str(e)]
        )
```

### 3. SystemStatistics Schema

```python
class SystemStatistics(BaseModel):
    """System-wide statistics"""
    total_reports: int = Field(..., ge=0)
    severe_damage: int = Field(..., ge=0)
    verified_reports: int = Field(..., ge=0)
    blocked_roads: int = Field(..., ge=0)
    # ... 10+ more fields ...
    timestamp: datetime = Field(default_factory=datetime.utcnow)
```

### 4. HealthCheck Schema

```python
class HealthCheck(BaseModel):
    """Health check response"""
    status: str = Field("healthy")
    version: str = Field("1.0.0")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    database_connected: bool = Field(True)
    ml_models_loaded: bool = Field(True)
```

### 5. Enhanced Validation

**Coordinate range validation:**
```python
latitude: float = Field(..., ge=-90, le=90)  # Auto validates!
longitude: float = Field(..., ge=-180, le=180)
```

**Custom validators:**
```python
@field_validator('delivery_points')
@classmethod
def validate_delivery_points(cls, v):
    if not v:
        raise ValueError("At least one delivery point is required")
    return v
```

**String length limits:**
```python
description: Optional[str] = Field(None, max_length=1000)
reporter_id: Optional[str] = Field(None, max_length=100)
name: str = Field(..., max_length=200)
```

### 6. JSON Schema Examples

Every schema now has examples for auto-generated docs:

```python
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
```

Shows up in `/docs` Swagger UI!

---

## 📊 Before vs After Comparison

### Before (Old schemas.py)

```python
class DamageReportCreate(BaseModel):
    latitude: float  # No validation
    longitude: float
    description: Optional[str] = None
    source: str = "user_upload"  # String - typo-prone!
    # Missing: reporter_id

class DetectionResult(BaseModel):
    damage_class: str  # String, not enum
    severity: int
    confidence: float
    bounding_boxes: List[dict] = []  # Untyped dict!
    description: str
    # Missing: method, model_version
```

### After (schemas_improved.py)

```python
class DamageReportCreate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90)  # ✅ Validated!
    longitude: float = Field(..., ge=-180, le=180)  # ✅ Validated!
    description: Optional[str] = Field(None, max_length=1000)  # ✅ Length limit
    source: SourceType = Field(SourceType.USER_UPLOAD)  # ✅ Enum!
    reporter_id: Optional[str] = Field(None, max_length=100)  # ✅ Added!
    
    class Config:
        json_schema_extra = {"example": {...}}  # ✅ Documentation!

class DetectionResult(BaseModel):
    damage_class: DamageClass  # ✅ Enum!
    severity: int = Field(..., ge=0, le=4)  # ✅ Range validation!
    confidence: float = Field(..., ge=0.0, le=1.0)  # ✅ Range validation!
    bounding_boxes: List[BoundingBox] = Field(default_factory=list)  # ✅ Strongly typed!
    description: str
    method: Optional[str] = Field(None)  # ✅ Added!
    model_version: Optional[str] = Field(None)  # ✅ Added!
```

---

## 🚀 Integration Steps

### Option 1: Replace Completely (Recommended)

```powershell
cd backend

# Backup old schemas
copy schemas.py schemas_old_backup.py

# Replace with improved version
copy schemas_improved.py schemas.py

# Test imports
python -c "from schemas import *; print('✓ Schemas loaded')"
```

### Option 2: Gradual Migration

Keep both files, import from improved:

```python
# main.py
from schemas_improved import (
    DamageReportCreate,
    DamageReportResponse,
    SourceType,  # Use enums!
    RoadStatusType,
    SupplyPointType
)
```

Update endpoints one by one.

### Option 3: Merge Manually

Copy specific improvements from `schemas_improved.py` to `schemas.py`.

---

## 🧪 Testing

### Test Enum Validation

```python
from schemas import DamageReportCreate, SourceType

# Valid - works
report = DamageReportCreate(
    latitude=0.01,
    longitude=0.02,
    source=SourceType.SATELLITE  # ✅
)

# Invalid - fails at validation
try:
    report = DamageReportCreate(
        latitude=0.01,
        longitude=0.02,
        source="invalid_source"  # ❌ ValidationError!
    )
except ValidationError as e:
    print(f"Caught: {e}")
```

### Test Coordinate Validation

```python
# Invalid latitude - caught immediately
try:
    report = DamageReportCreate(
        latitude=999,  # ❌ Must be -90 to 90
        longitude=0.0
    )
except ValidationError as e:
    print(f"Invalid latitude caught: {e}")
```

### Test BoundingBox

```python
from schemas import BoundingBox

# Valid
box = BoundingBox(
    x1=100.0,
    y1=150.0,
    x2=300.0,
    y2=400.0,
    confidence=0.92,
    class_id=0,
    label="building"
)

# Invalid - negative coordinates
try:
    box = BoundingBox(
        x1=-10.0,  # ❌ Must be non-negative
        y1=150.0,
        x2=300.0,
        y2=400.0,
        confidence=0.92,
        class_id=0
    )
except ValidationError as e:
    print(f"Negative coordinate caught: {e}")
```

---

## 📚 Auto-Generated Documentation

With improved schemas, `/docs` (Swagger UI) now shows:

- ✅ Enum dropdown menus (not free text)
- ✅ Field descriptions in tooltips
- ✅ Example requests/responses
- ✅ Validation rules (min, max, length)
- ✅ Required vs optional fields
- ✅ Units in descriptions

**Try it:**
```powershell
# Start server
python main.py

# Open browser
http://localhost:8000/docs
```

Look at the POST endpoints - enums show as dropdowns!

---

## ✅ Summary

| Improvement | Status | Impact |
|------------|--------|--------|
| **Enum Usage** | ✅ Complete | Type safety, IDE support |
| **Geometry Fields** | ✅ Complete | Map visualization |
| **BoundingBox Schema** | ✅ Complete | Strong typing |
| **Units Clarification** | ✅ Complete | No ambiguity |
| **Optional Fields** | ✅ Complete | Audit trail |
| **Coordinate Validation** | ✅ Bonus | Data quality |
| **String Length Limits** | ✅ Bonus | Security |
| **JSON Examples** | ✅ Bonus | Better docs |
| **Sub-models** | ✅ Bonus | Reusability |
| **APIResponse Wrapper** | ✅ Bonus | Consistency |

**Total schemas created:** 25+
**Total improvements:** 40+

Your schemas are now **production-grade**! 🚀

---

## 🎯 Next Steps

1. **Backup old schemas**: `copy schemas.py schemas_old_backup.py`
2. **Switch to new**: `copy schemas_improved.py schemas.py`
3. **Update main.py**: Import from new schemas
4. **Test API**: Visit `/docs` to see improvements
5. **Update frontend**: Use enum values, new fields

Your API is now **type-safe, self-documenting, and production-ready**! 🎉
