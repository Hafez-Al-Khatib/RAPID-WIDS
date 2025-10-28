from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from geoalchemy2.elements import WKTElement
from geoalchemy2.shape import to_shape
from typing import List, Optional
import os
import shutil
from datetime import datetime
from dotenv import load_dotenv

from database import get_db, init_db, DamageReport, RoadStatus, SupplyPoint
from schemas import (
    DamageReportCreate, DamageReportResponse,
    RoadStatusUpdate, RoadStatusResponse,
    SupplyPointCreate, SupplyPointResponse,
    PathRequest, PathResponse,
    OptimizeRouteRequest, OptimizeRouteResponse,
    DetectionResult,
    # Enums for type safety
    SourceType, RoadStatusType, SupplyPointType, DamageClass
)
from models import get_damage_detector, get_supply_optimizer, get_graph_navigator

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAPID - Crisis Navigator API",
    description="AI-Powered Crisis Management Platform",
    version="1.0.0"
)

# CORS configuration
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create upload directory
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Initialize database
@app.on_event("startup")
async def startup_event():
    """Initialize database and ML models on startup"""
    init_db()
    
    # Initialize graph navigator with default location
    navigator = get_graph_navigator()
    # Default to a common location (can be updated via API)
    navigator.build_graph_from_osm((0.0, 0.0), radius=5000)
    
    print("🚀 RAPID API Server started successfully!")


# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "service": "RAPID Crisis Navigator",
        "version": "1.0.0"
    }


# Damage Detection Endpoints
@app.post("/api/upload", response_model=DamageReportResponse)
async def upload_disaster_photo(
    file: UploadFile = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    description: Optional[str] = Form(None),
    source: str = Form("user_upload"),
    db: Session = Depends(get_db)
):
    """
    Upload disaster photo and detect damage automatically.
    
    - **file**: Image file (JPEG, PNG)
    - **latitude**: GPS latitude
    - **longitude**: GPS longitude
    - **description**: Optional description
    - **source**: Data source (user_upload, satellite, simulation)
    """
    # Save uploaded file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_ext = os.path.splitext(file.filename)[1]
    filename = f"{timestamp}_{latitude}_{longitude}{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Run damage detection
    detector = get_damage_detector()
    detection_result = detector.detect_damage(file_path)
    
    # Create damage report in database (geometry auto-generated from lat/lon)
    report = DamageReport(
        image_path=file_path,
        latitude=latitude,
        longitude=longitude,
        damage_severity=detection_result['severity'],
        confidence=detection_result['confidence'],
        verified=False,
        description=description or detection_result['description'],
        source=source
    )
    
    db.add(report)
    db.commit()
    db.refresh(report)
    
    # Convert geometry to WKT string for response
    if report.location:
        geom = to_shape(report.location)
        report.location = geom.wkt
    
    return report


@app.post("/api/damage/detect", response_model=DetectionResult)
async def detect_damage(file: UploadFile = File(...)):
    """
    Detect damage in uploaded image (without saving to database).
    Useful for quick classification.
    """
    # Read file bytes
    image_bytes = await file.read()
    
    # Run detection
    detector = get_damage_detector()
    result = detector.detect_from_bytes(image_bytes)
    
    return result


@app.get("/api/reports", response_model=List[DamageReportResponse])
async def get_damage_reports(
    skip: int = 0,
    limit: int = 100,
    min_severity: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get all damage reports with optional filtering.
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    - **min_severity**: Minimum damage severity (0-4)
    """
    query = db.query(DamageReport)
    
    if min_severity > 0:
        query = query.filter(DamageReport.damage_severity >= min_severity)
    
    reports = query.order_by(DamageReport.timestamp.desc()).offset(skip).limit(limit).all()
    
    # Convert geometries to WKT strings for response
    for report in reports:
        if report.location:
            geom = to_shape(report.location)
            report.location = geom.wkt
    
    return reports


# Supply Optimization Endpoints
@app.post("/api/supply/point", response_model=SupplyPointResponse)
async def create_supply_point(
    point: SupplyPointCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new supply point (warehouse, hospital, shelter, or affected area).
    """
    supply_point = SupplyPoint(
        name=point.name,
        latitude=point.latitude,
        longitude=point.longitude,
        location=WKTElement(f'POINT({point.longitude} {point.latitude})', srid=4326),
        type=point.type,
        demand=point.demand,
        capacity=point.capacity,
        priority=point.priority
    )
    
    db.add(supply_point)
    db.commit()
    db.refresh(supply_point)
    
    return supply_point


@app.get("/api/supply/points", response_model=List[SupplyPointResponse])
async def get_supply_points(
    type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all supply points, optionally filtered by type.
    
    - **type**: Filter by type (warehouse, hospital, shelter, affected_area)
    """
    query = db.query(SupplyPoint)
    
    if type:
        query = query.filter(SupplyPoint.type == type)
    
    points = query.all()
    
    # Convert geometries to WKT strings for response
    for point in points:
        if point.location:
            geom = to_shape(point.location)
            point.location = geom.wkt
    
    return points


@app.post("/api/optimize/route", response_model=OptimizeRouteResponse)
async def optimize_supply_route(
    request: OptimizeRouteRequest,
    db: Session = Depends(get_db)
):
    """
    Optimize supply delivery routes using Vehicle Routing Problem (VRP) solver.
    
    - **warehouse_id**: ID of warehouse/depot
    - **delivery_points**: List of delivery point IDs
    - **num_vehicles**: Number of available vehicles
    - **vehicle_capacity**: Capacity per vehicle
    """
    # Get warehouse
    warehouse = db.query(SupplyPoint).filter(SupplyPoint.id == request.warehouse_id).first()
    if not warehouse:
        raise HTTPException(status_code=404, detail="Warehouse not found")
    
    # Get delivery points
    delivery_points = db.query(SupplyPoint).filter(
        SupplyPoint.id.in_(request.delivery_points)
    ).all()
    
    if not delivery_points:
        raise HTTPException(status_code=404, detail="No delivery points found")
    
    # Prepare data for optimizer
    warehouse_coords = (warehouse.latitude, warehouse.longitude)
    delivery_data = [
        {
            'latitude': p.latitude,
            'longitude': p.longitude,
            'demand': p.demand
        }
        for p in delivery_points
    ]
    
    # Run optimization
    optimizer = get_supply_optimizer()
    optimizer.num_vehicles = request.num_vehicles
    optimizer.vehicle_capacity = request.vehicle_capacity
    
    result = optimizer.optimize_routes(warehouse_coords, delivery_data)
    
    return result


# Navigation & Routing Endpoints
@app.post("/api/navigation/update", response_model=RoadStatusResponse)
async def update_road_status(
    update: RoadStatusUpdate,
    db: Session = Depends(get_db)
):
    """
    Update road status based on crowdsourced reports.
    
    - **road_id**: Unique road segment identifier
    - **status**: open, blocked, or damaged
    - **severity**: Damage severity (0-4)
    """
    # Create road status record
    road_status = RoadStatus(
        road_id=update.road_id,
        start_lat=update.start_lat,
        start_lon=update.start_lon,
        end_lat=update.end_lat,
        end_lon=update.end_lon,
        geometry=WKTElement(
            f'LINESTRING({update.start_lon} {update.start_lat}, {update.end_lon} {update.end_lat})',
            srid=4326
        ),
        status=update.status,
        severity=update.severity,
        source=update.source
    )
    
    db.add(road_status)
    db.commit()
    db.refresh(road_status)
    
    # Update navigation graph
    navigator = get_graph_navigator()
    navigator.update_road_status(update.road_id, update.status, update.severity)
    
    return road_status


@app.get("/api/navigation/roads", response_model=List[RoadStatusResponse])
async def get_road_statuses(
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get all road status updates.
    
    - **status**: Filter by status (open, blocked, damaged)
    """
    query = db.query(RoadStatus)
    
    if status:
        query = query.filter(RoadStatus.status == status)
    
    roads = query.order_by(RoadStatus.timestamp.desc()).all()
    return roads


@app.post("/api/navigation/path", response_model=PathResponse)
async def find_optimal_path(request: PathRequest):
    """
    Find optimal path between two points using A* algorithm.
    Avoids blocked roads if requested.
    
    - **start_lat**: Start latitude
    - **start_lon**: Start longitude
    - **end_lat**: End latitude
    - **end_lon**: End longitude
    - **avoid_blocked**: Whether to avoid blocked roads
    """
    navigator = get_graph_navigator()
    
    result = navigator.find_path(
        (request.start_lat, request.start_lon),
        (request.end_lat, request.end_lon),
        avoid_blocked=request.avoid_blocked
    )
    
    if result is None:
        raise HTTPException(status_code=404, detail="No path found")
    
    return result


@app.post("/api/navigation/initialize")
async def initialize_navigation_graph(
    center_lat: float,
    center_lon: float,
    radius: float = 5000
):
    """
    Initialize navigation graph for a specific area.
    Downloads OpenStreetMap data and builds the road network.
    
    - **center_lat**: Center latitude
    - **center_lon**: Center longitude
    - **radius**: Radius in meters (default 5000)
    """
    navigator = get_graph_navigator()
    navigator.build_graph_from_osm((center_lat, center_lon), radius)
    
    return {
        "status": "success",
        "message": f"Graph initialized with {navigator.graph.number_of_nodes()} nodes",
        "nodes": navigator.graph.number_of_nodes(),
        "edges": navigator.graph.number_of_edges()
    }


# Statistics Endpoint
@app.get("/api/stats")
async def get_statistics(db: Session = Depends(get_db)):
    """Get overall system statistics"""
    total_reports = db.query(DamageReport).count()
    severe_damage = db.query(DamageReport).filter(DamageReport.damage_severity >= 3).count()
    blocked_roads = db.query(RoadStatus).filter(RoadStatus.status == 'blocked').count()
    supply_points = db.query(SupplyPoint).count()
    
    return {
        "total_damage_reports": total_reports,
        "severe_damage_reports": severe_damage,
        "blocked_roads": blocked_roads,
        "supply_points": supply_points
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", 8000)),
        reload=True
    )
