# 🚀 Getting Started with RAPID

Welcome to RAPID - AI-Powered Crisis Navigator! This guide will get you up and running in minutes.

## 📋 Prerequisites

Choose one of the following setup options:

### Option A: Docker (Recommended - Easiest)
- ✅ Docker Desktop installed ([Download](https://www.docker.com/products/docker-desktop))
- ✅ 8GB RAM available
- ✅ 20GB free disk space

### Option B: Manual Setup
- ✅ Python 3.9+ ([Download](https://www.python.org/downloads/))
- ✅ Node.js 16+ ([Download](https://nodejs.org/))
- ✅ PostgreSQL 14+ with PostGIS ([Download](https://www.postgresql.org/download/))
- ✅ Git ([Download](https://git-scm.com/downloads))

---

## ⚡ Quick Start (Docker - 5 Minutes)

### Step 1: Setup Environment
```powershell
# Navigate to project directory
cd c:\Users\Hafez\Documents\GitHub\RAPID-WIDS

# Create environment file from template
copy .env.example .env
```

### Step 2: Start Services
```powershell
# Start all services with Docker Compose
docker-compose up -d

# Wait for services to start (about 30 seconds)
# Watch the logs
docker-compose logs -f
```

### Step 3: Initialize Database
```powershell
# Initialize database schema
docker-compose exec backend python database.py

# Load sample data (optional but recommended for demo)
docker-compose exec backend python seed_data.py
```

### Step 4: Access Application
Open your browser:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Step 5: Verify Everything Works
```powershell
# Check all services are running
docker-compose ps

# Test backend API
curl http://localhost:8000/

# Test database connection
docker-compose exec backend python -c "from database import SessionLocal; db = SessionLocal(); print('DB Connected!')"
```

**✅ You're ready!** Skip to [First Steps](#first-steps)

---

## 🔧 Manual Setup (Advanced)

### Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy ..\.env.example .env

# Edit .env and update DATABASE_URL
# DATABASE_URL=postgresql://postgres:password@localhost:5432/rapid_db

# Initialize database
python database.py

# Load sample data (optional)
python seed_data.py

# Start backend server
python main.py
```

Backend runs at http://localhost:8000

### Frontend Setup

```powershell
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
echo REACT_APP_API_URL=http://localhost:8000 > .env.local

# Start development server
npm start
```

Frontend runs at http://localhost:3000

### PostgreSQL Setup (if not using Docker)

```powershell
# Using Docker for PostgreSQL only
docker run -d `
  --name rapid_db `
  -e POSTGRES_PASSWORD=password `
  -e POSTGRES_DB=rapid_db `
  -p 5432:5432 `
  postgis/postgis:14-3.3

# Or install PostgreSQL locally and enable PostGIS extension
# CREATE EXTENSION postgis;
```

---

## 🎯 First Steps

### 1. Explore the Interface

Navigate to http://localhost:3000 and familiarize yourself with:
- **Upload Tab**: Upload disaster photos for AI analysis
- **Optimize Tab**: Calculate optimal supply routes
- **Stats Tab**: View system statistics and metrics
- **Map**: Interactive visualization of all data

### 2. Upload Your First Disaster Photo

1. Click the **Upload** tab
2. Choose any image (disaster photo, building, etc.)
3. Enter GPS coordinates:
   - Click "Use Current Location" (if browser supports)
   - Or manually enter: Lat: `0.01`, Lon: `0.01`
4. Add description: "Test upload"
5. Click "Upload & Analyze"
6. Watch the AI classify damage in real-time!
7. View the result on the map

### 3. Optimize Supply Routes

1. Click the **Optimize** tab
2. Select warehouse: "Central Supply Depot"
3. Check 3-4 delivery points (shelters or affected areas)
4. Set vehicles: `3`, capacity: `1000`
5. Click "Optimize Routes"
6. View optimized routes on the map (different colors per vehicle)

### 4. View Statistics

1. Click the **Stats** tab
2. Review damage severity distribution
3. Check road network status
4. Monitor system health

---

## 🧪 Testing the Demo Scenario

Run the complete hackathon demo:

### Scenario: Hurricane Aftermath Response

1. **Initial Assessment**
   - Upload disaster photo showing building damage
   - AI classifies as "Major Damage - Level 2"
   - Map shows severity heatmap

2. **Resource Planning**
   - Navigate to Optimize tab
   - Select Central Warehouse
   - Select 5 affected areas needing supplies
   - Optimize routes for 3 vehicles
   - View optimized delivery routes on map

3. **Real-time Updates**
   - Check blocked roads on map (red dashed lines)
   - Use Stats tab to see road status breakdown
   - Navigate to API docs to explore update endpoints

4. **Impact Analysis**
   - Stats tab shows total reports, critical areas
   - Dashboard shows recent reports timeline
   - Map provides full situational awareness

---

## 🔍 Exploring the API

### Interactive API Documentation
Visit http://localhost:8000/docs for Swagger UI

### Common API Endpoints

**Health Check:**
```bash
curl http://localhost:8000/
```

**Get Damage Reports:**
```bash
curl http://localhost:8000/api/reports
```

**Get Statistics:**
```bash
curl http://localhost:8000/api/stats
```

**Upload Photo (using curl):**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "file=@path/to/image.jpg" \
  -F "latitude=0.01" \
  -F "longitude=0.01" \
  -F "description=Test upload"
```

**Initialize Navigation Graph:**
```bash
curl -X POST "http://localhost:8000/api/navigation/initialize?center_lat=0.0&center_lon=0.0&radius=5000"
```

---

## 🎤 Preparing for Demo Presentation

### Before the Presentation

1. **Ensure all services are running:**
   ```powershell
   docker-compose ps
   # All should show "Up"
   ```

2. **Load fresh sample data:**
   ```powershell
   docker-compose exec backend python seed_data.py
   ```

3. **Prepare a disaster photo:**
   - Download sample disaster images from [xBD dataset](https://xview2.org/)
   - Or use any building/infrastructure photo

4. **Test the full workflow:**
   - Upload → Classify → Optimize → View Stats
   - Time it (should be under 2 minutes)

5. **Review pitch materials:**
   - Read `DEMO_SCRIPT.md` for presentation flow
   - Review `HACKATHON_PITCH.md` for talking points
   - Practice the 5-minute demo

### During the Demo

Follow the script in `DEMO_SCRIPT.md`:
1. **Hook** (30s): State the problem
2. **Damage Detection** (1.5min): Live upload and classification
3. **Route Optimization** (1.5min): Live optimization demo
4. **Dynamic Navigation** (1min): Show blocked roads and rerouting
5. **Impact** (30s): Stats and big picture

### After the Demo

**Answer common questions:**
- "How accurate is the AI?" → "YOLOv8 trained on xBD, customizable confidence threshold"
- "Does it work offline?" → "Yes, with cached maps and local ML models"
- "Can it scale?" → "Yes, from neighborhoods to regions, cloud-ready"
- "What's the cost?" → "Open-source core, cloud hosting ~$500-2000/month"

---

## 🛠️ Customization & Configuration

### Change Map Center
Edit `backend/.env`:
```ini
DEFAULT_MAP_CENTER_LAT=40.7128
DEFAULT_MAP_CENTER_LON=-74.0060
```

### Adjust ML Confidence Threshold
Edit `backend/.env`:
```ini
CONFIDENCE_THRESHOLD=0.6
```

### Configure Vehicle Fleet
Edit `backend/.env`:
```ini
MAX_VEHICLES=10
VEHICLE_CAPACITY=2000
```

### Use Custom YOLO Model
1. Place your trained model in `backend/models/`
2. Edit `backend/.env`:
   ```ini
   YOLO_MODEL_PATH=models/custom_yolov8.pt
   ```

### Add Real Location Data

Initialize navigation graph for your area:
```bash
curl -X POST "http://localhost:8000/api/navigation/initialize?center_lat=YOUR_LAT&center_lon=YOUR_LON&radius=10000"
```

---

## 🐛 Troubleshooting

### Services won't start
```powershell
# Check Docker is running
docker --version

# Check ports aren't in use
netstat -ano | findstr ":8000"
netstat -ano | findstr ":3000"

# Restart services
docker-compose down
docker-compose up -d
```

### Database connection errors
```powershell
# Check database is running
docker-compose ps db

# View database logs
docker-compose logs db

# Recreate database
docker-compose down -v
docker-compose up -d
```

### Frontend can't connect to backend
Check `frontend/.env.local`:
```ini
REACT_APP_API_URL=http://localhost:8000
```

### YOLO model download issues
```powershell
# Manually download model
docker-compose exec backend python -c "from ultralytics import YOLO; YOLO('yolov8n.pt')"
```

### Out of memory
Increase Docker memory:
1. Docker Desktop → Settings → Resources
2. Set Memory to at least 8GB
3. Click Apply & Restart

---

## 📚 Additional Resources

- **Quick Start**: `QUICKSTART.md` - Fast setup guide
- **Demo Script**: `DEMO_SCRIPT.md` - Hackathon presentation flow
- **Pitch Deck**: `HACKATHON_PITCH.md` - Full pitch materials
- **Deployment**: `DEPLOYMENT.md` - Production deployment guide
- **API Docs**: http://localhost:8000/docs (when running)

---

## 🤝 Getting Help

### Check Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs db
```

### Common Commands
```powershell
# Restart everything
docker-compose restart

# Stop everything
docker-compose down

# Rebuild and restart
docker-compose up -d --build

# View running containers
docker-compose ps

# Execute commands in backend
docker-compose exec backend python database.py
```

---

## 🎉 You're All Set!

Your RAPID platform is now ready for:
- ✅ Hackathon demo
- ✅ Development and testing
- ✅ Showing to stakeholders
- ✅ Further customization

**Next Steps:**
1. Practice your demo presentation
2. Customize for your specific use case
3. Add real disaster imagery
4. Deploy to the cloud (see `DEPLOYMENT.md`)

**Good luck with your hackathon! 🚀**

---

**Questions?** Review the documentation or check the logs for specific errors.
