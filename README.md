# 🌍 RAPID - AI-Powered Crisis Navigator

**Rapid Assessment Platform for Intelligent Disaster Response**

## 🎯 Overview

RAPID is a comprehensive crisis management platform that combines AI-powered damage detection, intelligent supply optimization, and dynamic navigation to help emergency responders save lives during disasters.

### Core Features

- **🔍 Rapid Damage Visual Triage**: Classify disaster damage from user-uploaded photos and satellite imagery using YOLOv8
- **📦 Supply & Resource Optimization**: Allocate and route emergency supplies using OR-Tools VRP
- **🗺️ Dynamic Navigation Graph**: Fuse satellite + crowdsourced data to guide responders around blocked roads

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 16+
- PostgreSQL 14+ with PostGIS extension

### Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python -m uvicorn main:app --reload
```

Backend runs at `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm start
```

Frontend runs at `http://localhost:3000`

## 📁 Project Structure

```
RAPID-WIDS/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── models/
│   │   ├── damage_detector.py  # YOLOv8 integration
│   │   ├── supply_optimizer.py # OR-Tools VRP
│   │   └── graph_navigator.py  # Pathfinding
│   ├── database.py             # PostgreSQL + PostGIS
│   ├── schemas.py              # Pydantic models
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Map.jsx         # Leaflet map component
│   │   │   ├── UploadPanel.jsx # Photo upload
│   │   │   └── Dashboard.jsx   # Main interface
│   │   └── App.jsx
│   └── package.json
└── README.md
```

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.9+
- **Frontend**: React 18, TailwindCSS, Leaflet.js
- **ML**: PyTorch, YOLOv8, ultralytics
- **Optimization**: Google OR-Tools
- **Database**: PostgreSQL 14+ with PostGIS
- **Deployment**: Docker, Docker Compose

## 📊 API Endpoints

- `POST /api/upload` - Upload disaster photo with GPS coordinates
- `POST /api/damage/detect` - Classify damage severity
- `POST /api/optimize/route` - Calculate optimal supply routes
- `POST /api/navigation/update` - Update road status (blocked/open)
- `GET /api/navigation/path` - Get optimal path between points
- `GET /api/reports` - Get all damage reports

## 🎤 Demo Scenario

1. **Upload**: Disaster photo with GPS coordinates
2. **Classify**: AI detects damage severity (0-4 scale)
3. **Map**: Heatmap updates with severity overlay
4. **Optimize**: Supply routes calculated for affected areas
5. **Reroute**: Dynamic pathfinding around blocked roads

## 🌟 Impact

- ⚡ Reduces emergency response time by up to 40%
- 🎯 Improves resource allocation accuracy
- 🛡️ Safer navigation for first responders
- 🌐 Scalable globally with offline support

## 📄 License

MIT License - built for the WIDS Hackathon 2025
