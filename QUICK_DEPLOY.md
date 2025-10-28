# ⚡ Quick Deployment Guide

## Option 1: Docker Compose (Recommended - Easiest)

### Start Everything
```powershell
# From project root
docker-compose up -d

# Wait for database to be ready (30 seconds)
timeout /t 30

# Initialize database schema
docker-compose exec backend python database.py

# Load sample data
docker-compose exec backend python seed_data.py
```

### Access Application
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Option 2: Local Development (Requires PostgreSQL)

### Prerequisites
- PostgreSQL 14+ with PostGIS installed locally
- Python 3.9+ virtual environment

### Setup PostgreSQL Password
If you get password authentication errors:

1. **Find `pg_hba.conf`** (usually in `C:\Program Files\PostgreSQL\14\data\`)

2. **Change authentication method:**
   ```
   # IPv4 local connections:
   host    all             all             127.0.0.1/32            trust
   # IPv6 local connections:
   host    all             all             ::1/128                 trust
   ```

3. **Restart PostgreSQL service:**
   ```powershell
   Restart-Service postgresql-x64-14
   ```

4. **Set postgres password:**
   ```powershell
   psql -U postgres
   ALTER USER postgres PASSWORD 'password';
   ```

### Initialize Database
```powershell
# Activate virtualenv
.\rapidenv\Scripts\Activate.ps1

cd backend

# Create database and tables
python init_db.py

# Load sample data
python seed_data.py

# Start server
python main.py
```

---

## Quick Test Which Option Works

### Test Docker
```powershell
docker --version
docker-compose --version
```

If both work → **Use Option 1** (Docker Compose)

### Test Local PostgreSQL
```powershell
psql -U postgres -c "SELECT version();"
```

If works → **Use Option 2** (Local)

---

## Current Status

Based on the error, you have two choices:

### Choice A: Use Docker (No PostgreSQL setup needed!)
```powershell
docker-compose up -d
docker-compose exec backend python database.py
docker-compose exec backend python seed_data.py
```

### Choice B: Fix Local PostgreSQL
1. Set PostgreSQL password to `password`
2. OR update `.env` with your PostgreSQL password
3. Run `python init_db.py`

**Recommendation: Use Docker Compose (Option A)** - It's faster and already configured!
