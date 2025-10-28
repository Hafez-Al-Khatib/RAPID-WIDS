# RAPID Setup Script for Windows PowerShell
# This script sets up the complete RAPID environment

Write-Host "🌍 RAPID Crisis Navigator - Setup Script" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

# Check for Docker
Write-Host "Checking prerequisites..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "✓ Docker found" -ForegroundColor Green
    $useDocker = Read-Host "Would you like to use Docker? (y/n)"
} else {
    Write-Host "✗ Docker not found" -ForegroundColor Red
    $useDocker = "n"
}

if ($useDocker -eq "y") {
    # Docker setup
    Write-Host ""
    Write-Host "Setting up with Docker..." -ForegroundColor Yellow
    
    # Create .env file
    if (!(Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host "✓ Created .env file" -ForegroundColor Green
    }
    
    # Start services
    Write-Host "Starting Docker services..." -ForegroundColor Yellow
    docker-compose up -d
    
    # Wait for database
    Write-Host "Waiting for database to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    # Initialize database
    Write-Host "Initializing database..." -ForegroundColor Yellow
    docker-compose exec -T backend python database.py
    
    # Seed sample data
    $seedData = Read-Host "Would you like to load sample data? (y/n)"
    if ($seedData -eq "y") {
        docker-compose exec -T backend python seed_data.py
    }
    
    Write-Host ""
    Write-Host "✅ Setup complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Access your application:" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor White
    Write-Host "  API Docs: http://localhost:8000/docs" -ForegroundColor White
    
} else {
    # Manual setup
    Write-Host ""
    Write-Host "Setting up manually..." -ForegroundColor Yellow
    
    # Create .env file
    if (!(Test-Path .env)) {
        Copy-Item .env.example .env
        Write-Host "✓ Created .env file" -ForegroundColor Green
    }
    
    # Backend setup
    Write-Host ""
    Write-Host "Setting up backend..." -ForegroundColor Yellow
    Set-Location backend
    
    # Create virtual environment
    if (!(Test-Path venv)) {
        python -m venv venv
        Write-Host "✓ Created virtual environment" -ForegroundColor Green
    }
    
    # Activate and install dependencies
    & .\venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Write-Host "✓ Installed Python dependencies" -ForegroundColor Green
    
    Set-Location ..
    
    # Frontend setup
    Write-Host ""
    Write-Host "Setting up frontend..." -ForegroundColor Yellow
    Set-Location frontend
    
    if (Get-Command npm -ErrorAction SilentlyContinue) {
        npm install
        Write-Host "✓ Installed Node dependencies" -ForegroundColor Green
    } else {
        Write-Host "✗ npm not found. Please install Node.js" -ForegroundColor Red
    }
    
    Set-Location ..
    
    Write-Host ""
    Write-Host "⚠ Manual setup complete!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Ensure PostgreSQL with PostGIS is running" -ForegroundColor White
    Write-Host "2. Update DATABASE_URL in .env file" -ForegroundColor White
    Write-Host "3. Initialize database: cd backend && python database.py" -ForegroundColor White
    Write-Host "4. Start backend: cd backend && python main.py" -ForegroundColor White
    Write-Host "5. Start frontend: cd frontend && npm start" -ForegroundColor White
}

Write-Host ""
Write-Host "📚 For more information, see QUICKSTART.md" -ForegroundColor Cyan
