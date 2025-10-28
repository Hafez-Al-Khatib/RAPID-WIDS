# Stop local PostgreSQL service to free port 5432 for Docker

Write-Host "Checking PostgreSQL services..." -ForegroundColor Yellow

Get-Service | Where-Object {$_.Name -like "postgresql*"} | ForEach-Object {
    Write-Host "`nFound service: $($_.Name)" -ForegroundColor Cyan
    Write-Host "  Status: $($_.Status)" -ForegroundColor Cyan
    
    if ($_.Status -eq "Running") {
        Write-Host "  Stopping service..." -ForegroundColor Yellow
        Stop-Service $_.Name -Force
        Write-Host "  ✓ Service stopped" -ForegroundColor Green
    } else {
        Write-Host "  Service already stopped" -ForegroundColor Gray
    }
}

Write-Host "`n✓ Local PostgreSQL stopped. Port 5432 is now free for Docker!" -ForegroundColor Green
Write-Host "`nRestart Docker database:" -ForegroundColor Yellow
Write-Host "  docker-compose restart db" -ForegroundColor White
