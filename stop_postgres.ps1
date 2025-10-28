# Stop local PostgreSQL to free port 5432

Write-Host "Stopping local PostgreSQL..." -ForegroundColor Yellow

# Common PostgreSQL service names
$services = @("postgresql-x64-14", "postgresql-x64-15", "postgresql-x64-16", "PostgreSQL")

foreach ($serviceName in $services) {
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($service) {
        Write-Host "Found: $serviceName - Status: $($service.Status)"
        if ($service.Status -eq "Running") {
            Stop-Service -Name $serviceName -Force
            Write-Host "  ✓ Stopped $serviceName" -ForegroundColor Green
        }
    }
}

Write-Host "`n✓ Done! Now restart Docker database:" -ForegroundColor Green
Write-Host "  docker-compose restart db" -ForegroundColor Cyan
