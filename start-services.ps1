# Simple Windows PowerShell script to start Docker services
# Run this script from the project root directory

Write-Host "Starting Nexxora Promotional Engine Services..." -ForegroundColor Green
Write-Host ""

# Check if Docker is running
Write-Host "Checking Docker..." -ForegroundColor Yellow
try {
    $dockerCheck = docker ps 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker is not running!" -ForegroundColor Red
        Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Docker is running" -ForegroundColor Green
} catch {
    Write-Host "Docker is not running!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Starting essential services (PostgreSQL, MongoDB, Redis)..." -ForegroundColor Yellow
Write-Host "This may take a few minutes on first run..." -ForegroundColor Yellow
Write-Host ""

# Start essential services first
docker-compose up -d postgres mongodb redis

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Essential services started!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Waiting 10 seconds for services to initialize..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
    
    Write-Host ""
    Write-Host "Starting optional services (Kafka, Zookeeper, MinIO)..." -ForegroundColor Yellow
    docker-compose up -d zookeeper kafka minio
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "All services started successfully!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Checking service status..." -ForegroundColor Yellow
        docker-compose ps
        
        Write-Host ""
        Write-Host "Next Steps:" -ForegroundColor Cyan
        Write-Host "1. Initialize database: cd backend ; python scripts/init_database.py" -ForegroundColor White
        Write-Host "2. Start backend: uvicorn app.main:app --reload" -ForegroundColor White
        Write-Host "3. Access API docs: http://localhost:8000/api/docs" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "Essential services are running, but optional services failed." -ForegroundColor Yellow
        Write-Host "The application should still work with PostgreSQL, MongoDB, and Redis." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Failed to start services. Check Docker Desktop is running." -ForegroundColor Red
    exit 1
}
