"""
Seed database with sample data for demo/testing purposes.
Run this script to populate the database with realistic crisis scenario data.
"""

from database import SessionLocal, init_db, SupplyPoint, RoadStatus, DamageReport
from geoalchemy2.elements import WKTElement
import random
from datetime import datetime, timedelta

def seed_database():
    """Populate database with sample data"""
    
    print("🌱 Seeding database with sample data...")
    
    # Initialize database (tables already created, skip this)
    # init_db()
    db = SessionLocal()
    
    try:
        # Clear existing data (optional)
        print("Clearing existing data...")
        db.query(DamageReport).delete()
        db.query(RoadStatus).delete()
        db.query(SupplyPoint).delete()
        db.commit()
        
        # Center coordinates (example: use your target location)
        center_lat, center_lon = 0.0, 0.0
        
        # 1. Create Supply Points
        print("Creating supply points...")
        
        # Warehouses
        warehouses = [
            {
                "name": "Central Supply Depot",
                "lat": center_lat,
                "lon": center_lon,
                "type": "warehouse",
                "capacity": 10000,
                "demand": 0,
                "priority": 5
            },
            {
                "name": "North Distribution Center",
                "lat": center_lat + 0.05,
                "lon": center_lon + 0.02,
                "type": "warehouse",
                "capacity": 5000,
                "demand": 0,
                "priority": 4
            }
        ]
        
        for w in warehouses:
            supply_point = SupplyPoint(
                name=w["name"],
                latitude=w["lat"],
                longitude=w["lon"],
                type=w["type"],
                capacity=w["capacity"],
                demand=w["demand"],
                priority=w["priority"]
            )
            db.add(supply_point)
        
        # Hospitals
        hospitals = [
            {
                "name": "City General Hospital",
                "lat": center_lat + 0.01,
                "lon": center_lon + 0.01,
                "capacity": 200,
                "demand": 300,
                "priority": 5
            },
            {
                "name": "Emergency Medical Center",
                "lat": center_lat - 0.02,
                "lon": center_lon + 0.03,
                "capacity": 100,
                "demand": 150,
                "priority": 4
            }
        ]
        
        for h in hospitals:
            supply_point = SupplyPoint(
                name=h["name"],
                latitude=h["lat"],
                longitude=h["lon"],
                type="hospital",
                capacity=h["capacity"],
                demand=h["demand"],
                priority=h["priority"]
            )
            db.add(supply_point)
        
        # Shelters
        shelters = [
            {
                "name": "Community Shelter A",
                "lat": center_lat + 0.02,
                "lon": center_lon - 0.01,
                "demand": 200,
                "priority": 3
            },
            {
                "name": "School Evacuation Center",
                "lat": center_lat - 0.01,
                "lon": center_lon - 0.02,
                "demand": 250,
                "priority": 3
            },
            {
                "name": "Sports Complex Shelter",
                "lat": center_lat + 0.03,
                "lon": center_lon + 0.03,
                "demand": 300,
                "priority": 3
            }
        ]
        
        for s in shelters:
            supply_point = SupplyPoint(
                name=s["name"],
                latitude=s["lat"],
                longitude=s["lon"],
                type="shelter",
                capacity=0,
                demand=s["demand"],
                priority=s["priority"]
            )
            db.add(supply_point)
        
        # Affected Areas
        affected_areas = [
            {
                "name": "Downtown District",
                "lat": center_lat + 0.015,
                "lon": center_lon + 0.015,
                "demand": 500,
                "priority": 5
            },
            {
                "name": "Riverside Community",
                "lat": center_lat - 0.025,
                "lon": center_lon + 0.01,
                "demand": 350,
                "priority": 4
            },
            {
                "name": "Industrial Zone",
                "lat": center_lat + 0.03,
                "lon": center_lon - 0.02,
                "demand": 200,
                "priority": 3
            }
        ]
        
        for a in affected_areas:
            supply_point = SupplyPoint(
                name=a["name"],
                latitude=a["lat"],
                longitude=a["lon"],
                type="affected_area",
                capacity=0,
                demand=a["demand"],
                priority=a["priority"]
            )
            db.add(supply_point)
        
        # 2. Create Simulated Damage Reports
        print("Creating damage reports...")
        
        damage_scenarios = [
            {"lat": center_lat + 0.012, "lon": center_lon + 0.018, "severity": 3, "conf": 0.89, "desc": "Building collapsed, multiple casualties reported"},
            {"lat": center_lat + 0.016, "lon": center_lon + 0.012, "severity": 2, "conf": 0.76, "desc": "Major structural damage to commercial buildings"},
            {"lat": center_lat - 0.022, "lon": center_lon + 0.015, "severity": 3, "conf": 0.92, "desc": "Complete destruction of residential area"},
            {"lat": center_lat + 0.025, "lon": center_lon - 0.018, "severity": 1, "conf": 0.68, "desc": "Minor damage, broken windows and debris"},
            {"lat": center_lat - 0.015, "lon": center_lon - 0.022, "severity": 2, "conf": 0.81, "desc": "Partial roof collapse, flooding observed"},
            {"lat": center_lat + 0.008, "lon": center_lon + 0.005, "severity": 1, "conf": 0.72, "desc": "Superficial damage to infrastructure"},
            {"lat": center_lat - 0.008, "lon": center_lon + 0.025, "severity": 2, "conf": 0.78, "desc": "Major cracks in building foundations"},
            {"lat": center_lat + 0.035, "lon": center_lon + 0.028, "severity": 1, "conf": 0.65, "desc": "Minor structural issues, safe to enter"},
        ]
        
        for i, scenario in enumerate(damage_scenarios):
            # Vary timestamps
            timestamp = datetime.utcnow() - timedelta(hours=random.randint(0, 24))
            
            report = DamageReport(
                image_path=f"uploads/simulation_{i}.jpg",
                latitude=scenario["lat"],
                longitude=scenario["lon"],
                damage_severity=scenario["severity"],
                confidence=scenario["conf"],
                verified=random.choice([True, False]),
                description=scenario["desc"],
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(1, 48)),
                source="simulation"
            )
            db.add(report)
        
        # 3. Create Road Status Updates
        print("Creating road status updates...")
        
        road_scenarios = [
            {
                "road_id": "road_main_st_1",
                "start_lat": center_lat + 0.01,
                "start_lon": center_lon + 0.01,
                "end_lat": center_lat + 0.02,
                "end_lon": center_lon + 0.015,
                "status": "blocked",
                "severity": 4
            },
            {
                "road_id": "road_bridge_2",
                "start_lat": center_lat - 0.02,
                "start_lon": center_lon + 0.01,
                "end_lat": center_lat - 0.02,
                "end_lon": center_lon + 0.02,
                "status": "blocked",
                "severity": 3
            },
            {
                "road_id": "road_highway_3",
                "start_lat": center_lat + 0.03,
                "start_lon": center_lon - 0.01,
                "end_lat": center_lat + 0.03,
                "end_lon": center_lon + 0.01,
                "status": "damaged",
                "severity": 2
            },
            {
                "road_id": "road_access_4",
                "start_lat": center_lat - 0.01,
                "start_lon": center_lon - 0.02,
                "end_lat": center_lat + 0.01,
                "end_lon": center_lon - 0.02,
                "status": "open",
                "severity": 0
            }
        ]
        
        for road in road_scenarios:
            road_status = RoadStatus(
                road_id=road["road_id"],
                start_lat=road["start_lat"],
                start_lon=road["start_lon"],
                end_lat=road["end_lat"],
                end_lon=road["end_lon"],
                status=road["status"],
                severity=road["severity"],
                timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 12)),
                source="crowdsourced"
            )
            db.add(road_status)
        
        # Commit all changes
        db.commit()
        
        # Print summary
        print("\n✅ Database seeded successfully!")
        print(f"   - Supply Points: {db.query(SupplyPoint).count()}")
        print(f"   - Damage Reports: {db.query(DamageReport).count()}")
        print(f"   - Road Statuses: {db.query(RoadStatus).count()}")
        print("\n🎉 Ready for demo!")
        
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
