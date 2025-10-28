# 🚀 Start Database - Step by Step

## Quick Start

### 1. Start Docker Desktop
- Open **Docker Desktop** from Start Menu
- Wait for it to say "Docker Desktop is running"
- Look for green icon in system tray

### 2. Start PostgreSQL Database
```powershell
cd C:\Users\Hafez\Documents\GitHub\RAPID-WIDS

# Start just the database
docker-compose up -d db

# Wait for it to be ready (20 seconds)
Start-Sleep -Seconds 20
```

### 3. Update .env File
Change this line in `.env`:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/rapid_db
```

**Note:** Use `password` not `root` for Docker!

### 4. Initialize Database Schema
```powershell
.\rapidenv\Scripts\Activate.ps1
cd backend

# Create tables
python database.py

# Load sample data
python seed_data.py
```

### 5. Start Backend Server
```powershell
# In backend folder, virtualenv activated
python main.py
```

### 6. Access Application
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- Test: http://localhost:8000/api/stats

---

## Troubleshooting

### Docker Desktop Not Starting?
1. Restart computer
2. Open Docker Desktop
3. Wait for "Docker Desktop is running"

### Database Connection Error?
Check `.env` has:
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/rapid_db
```

### Port 5432 Already in Use?
Your local PostgreSQL is running. Either:
- **Option A:** Stop local PostgreSQL service
  ```powershell
  Stop-Service postgresql-x64-14
  ```
  
- **Option B:** Use different port in docker-compose.yml:
  ```yaml
  ports:
    - "5433:5432"  # Changed to 5433
  ```
  Then update .env:
  ```
  DATABASE_URL=postgresql://postgres:password@localhost:5433/rapid_db
  ```

---

## Verify Everything Works

```powershell
# Check database is running
docker ps

# Should see:
# rapid_db   postgis/postgis:14-3.3   Up X seconds   0.0.0.0:5432->5432/tcp

# Test connection
docker-compose exec db psql -U postgres -d rapid_db -c "SELECT PostGIS_Version();"
```

---

## Complete Fresh Start

If anything goes wrong:

```powershell
# Stop everything
docker-compose down -v

# Remove database volume
docker volume rm rapid-wids_postgres_data

# Start fresh
docker-compose up -d db
Start-Sleep -Seconds 20

# Initialize
.\rapidenv\Scripts\Activate.ps1
cd backend
python database.py
python seed_data.py
python main.py
```
