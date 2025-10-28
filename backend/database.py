from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text, CheckConstraint, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates, relationship
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_SetSRID, ST_MakePoint
from geoalchemy2.elements import WKTElement
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DamageReport(Base):
    """Damage reports from uploaded photos"""
    __tablename__ = "damage_reports"
    __table_args__ = (
        Index('idx_damage_location', 'location', postgresql_using='gist'),
        Index('idx_damage_severity', 'damage_severity'),
        Index('idx_damage_timestamp', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String(500), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    damage_severity = Column(
        Integer,
        CheckConstraint('damage_severity >= 0 AND damage_severity <= 4', name='valid_damage_severity'),
        default=0,
        nullable=False
    )  # 0-4 scale: 0=no damage, 1=minor, 2=major, 3=destroyed, 4=unclassified
    confidence = Column(
        Float,
        CheckConstraint('confidence >= 0.0 AND confidence <= 1.0', name='valid_confidence'),
        default=0.0
    )
    verified = Column(Boolean, default=False)
    description = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(
        String(50),
        CheckConstraint("source IN ('user_upload', 'satellite', 'simulation', 'crowdsourced')", name='valid_source'),
        default="user_upload"
    )
    
    @validates('latitude', 'longitude')
    def validate_coordinates(self, key, value):
        """Validate and sync coordinates with geometry"""
        if key == 'latitude' and not (-90 <= value <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {value}")
        if key == 'longitude' and not (-180 <= value <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {value}")
        return value
    
    def __init__(self, **kwargs):
        """Auto-generate geometry from lat/lon"""
        super().__init__(**kwargs)
        if 'latitude' in kwargs and 'longitude' in kwargs and 'location' not in kwargs:
            self.location = WKTElement(f'POINT({kwargs["longitude"]} {kwargs["latitude"]})', srid=4326)


class RoadStatus(Base):
    """Dynamic road network status"""
    __tablename__ = "road_status"
    __table_args__ = (
        Index('idx_road_geometry', 'geometry', postgresql_using='gist'),
        Index('idx_road_status', 'status'),
    )

    id = Column(Integer, primary_key=True, index=True)
    road_id = Column(String(100), unique=True, index=True, nullable=False)
    start_lat = Column(Float, nullable=False)
    start_lon = Column(Float, nullable=False)
    end_lat = Column(Float, nullable=False)
    end_lon = Column(Float, nullable=False)
    geometry = Column(Geometry('LINESTRING', srid=4326), nullable=False)
    status = Column(
        String(20),
        CheckConstraint("status IN ('open', 'blocked', 'damaged', 'under_repair')", name='valid_road_status'),
        default="open"
    )
    severity = Column(
        Integer,
        CheckConstraint('severity >= 0 AND severity <= 5', name='valid_road_severity'),
        default=0
    )
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    source = Column(
        String(50),
        CheckConstraint("source IN ('crowdsourced', 'official', 'satellite', 'sensor')", name='valid_road_source'),
        default="crowdsourced"
    )
    
    @validates('start_lat', 'start_lon', 'end_lat', 'end_lon')
    def validate_coordinates(self, key, value):
        """Validate coordinates"""
        if 'lat' in key and not (-90 <= value <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {value}")
        if 'lon' in key and not (-180 <= value <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {value}")
        return value
    
    def __init__(self, **kwargs):
        """Auto-generate geometry from start/end coordinates"""
        super().__init__(**kwargs)
        if all(k in kwargs for k in ['start_lon', 'start_lat', 'end_lon', 'end_lat']) and 'geometry' not in kwargs:
            self.geometry = WKTElement(
                f'LINESTRING({kwargs["start_lon"]} {kwargs["start_lat"]}, {kwargs["end_lon"]} {kwargs["end_lat"]})',
                srid=4326
            )


class SupplyPoint(Base):
    """Supply distribution points (hospitals, shelters, warehouses)"""
    __tablename__ = "supply_points"
    __table_args__ = (
        Index('idx_supply_location', 'location', postgresql_using='gist'),
        Index('idx_supply_type', 'type'),
        Index('idx_supply_priority', 'priority'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    type = Column(
        String(50),
        CheckConstraint("type IN ('warehouse', 'hospital', 'shelter', 'affected_area', 'distribution_center')", name='valid_supply_type'),
        nullable=False
    )
    demand = Column(
        Integer,
        CheckConstraint('demand >= 0', name='valid_demand'),
        default=0
    )  # required supplies
    capacity = Column(
        Integer,
        CheckConstraint('capacity >= 0', name='valid_capacity'),
        default=0
    )  # available supplies
    priority = Column(
        Integer,
        CheckConstraint('priority >= 1 AND priority <= 5', name='valid_priority'),
        default=1
    )  # 1-5 priority (1=highest)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    @validates('latitude', 'longitude')
    def validate_coordinates(self, key, value):
        """Validate and sync coordinates with geometry"""
        if key == 'latitude' and not (-90 <= value <= 90):
            raise ValueError(f"Latitude must be between -90 and 90, got {value}")
        if key == 'longitude' and not (-180 <= value <= 180):
            raise ValueError(f"Longitude must be between -180 and 180, got {value}")
        return value
    
    def __init__(self, **kwargs):
        """Auto-generate geometry from lat/lon"""
        super().__init__(**kwargs)
        if 'latitude' in kwargs and 'longitude' in kwargs and 'location' not in kwargs:
            self.location = WKTElement(f'POINT({kwargs["longitude"]} {kwargs["latitude"]})', srid=4326)


def get_db():
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")


if __name__ == "__main__":
    init_db()
