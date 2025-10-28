# 🚀 RAPID Quick Start Guide

Get RAPID up and running in 5 minutes!

## Option 1: Docker Compose (Recommended)

**Prerequisites**: Docker Desktop installed

```bash
# 1. Clone and navigate
cd RAPID-WIDS

# 2. Create environment file
copy .env.example .env

# 3. Start all services
docker-compose up -d

# 4. Initialize database
docker-compose exec backend python database.py

# 5. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## Option 2: Manual Setup

### Backend Setup

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy ..\.env.example .env

# Initialize database (requires PostgreSQL with PostGIS)
python database.py

# Start server
python main.py
# Or: uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
echo REACT_APP_API_URL=http://localhost:8000 > .env.local

# Start development server
npm start
```

Frontend runs at `http://localhost:3000`

## Database Setup (PostgreSQL with PostGIS)

### Windows (using Docker)
```bash
docker run -d \
  --name rapid_db \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=rapid_db \
  -p 5432:5432 \
  postgis/postgis:14-3.3
```

### Verify Database
```bash
# Check connection
docker exec -it rapid_db psql -U postgres -d rapid_db -c "SELECT version();"
```

## Initial Data Setup

### Create Sample Supply Points

```bash
# Access backend container or local environment
cd backend

# Create sample data using Python
python
```

```python
from database import SessionLocal, SupplyPoint, init_db
from geoalchemy2.elements import WKTElement

init_db()
db = SessionLocal()

# Add sample warehouse
warehouse = SupplyPoint(
    name="Central Warehouse",
    latitude=0.0,
    longitude=0.0,
    location=WKTElement('POINT(0.0 0.0)', srid=4326),
    type="warehouse",
    capacity=10000,
    demand=0,
    priority=5
)
db.add(warehouse)

# Add sample affected area
affected = SupplyPoint(
    name="Affected Area 1",
    latitude=0.01,
    longitude=0.01,
    location=WKTElement('POINT(0.01 0.01)', srid=4326),
    type="affected_area",
    capacity=0,
    demand=500,
    priority=4
)
db.add(affected)

db.commit()
print("Sample data created!")
```

## Testing the System

### 1. Upload Test Photo
- Go to http://localhost:3000
- Click "Upload" tab
- Upload any disaster photo
- Use coordinates: Lat: 0.0, Lon: 0.0
- Click "Upload & Analyze"

### 2. Optimize Routes
- Click "Optimize" tab
- Select "Central Warehouse"
- Select delivery points
- Set vehicles: 3
- Click "Optimize Routes"

### 3. View Stats
- Click "Stats" tab to see system statistics

## API Testing

### Using Swagger UI
Visit http://localhost:8000/docs for interactive API documentation

### Using curl

```bash
# Health check
curl http://localhost:8000/

# Get damage reports
curl http://localhost:8000/api/reports

# Get statistics
curl http://localhost:8000/api/stats
```

## Common Issues

### Port already in use
```bash
# Change ports in docker-compose.yml or .env
# Backend: API_PORT=8001
# Frontend: Change port in package.json
```

### Database connection error
```bash
# Verify PostgreSQL is running
docker ps | grep rapid_db

# Check DATABASE_URL in .env
DATABASE_URL=postgresql://postgres:password@localhost:5432/rapid_db
```

### YOLO model download issues
The system will auto-download YOLOv8n on first run. Ensure internet connection.

## Next Steps

1. **Initialize Navigation Graph**: Use the API to set your area
   ```bash
   curl -X POST "http://localhost:8000/api/navigation/initialize?center_lat=YOUR_LAT&center_lon=YOUR_LON&radius=5000"
   ```

2. **Add Supply Points**: Create warehouses, hospitals, and shelters via the API

3. **Upload Real Data**: Use the web interface to upload disaster photos

4. **Customize**: Modify coordinates, add your dataset, fine-tune models

## Demo Scenario

Run the complete demo workflow:

1. Upload disaster photo with GPS
2. AI classifies damage (0-4 scale)
3. Map updates with severity heatmap
4. Create supply points in affected areas
5. Optimize delivery routes
6. Mark roads as blocked
7. See automatic rerouting

## Support

- Check logs: `docker-compose logs -f`
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`

🎉 You're ready to save lives with RAPID!
