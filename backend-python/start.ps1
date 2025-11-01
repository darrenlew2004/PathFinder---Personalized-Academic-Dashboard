# Start the FastAPI server in development mode
Write-Host "Starting PathFinder Python Backend..." -ForegroundColor Green
Write-Host "API will be available at: http://localhost:9000" -ForegroundColor Cyan
Write-Host "Swagger Docs at: http://localhost:9000/docs" -ForegroundColor Cyan
Write-Host ""

# Check if virtual environment exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment not found. Please run setup.ps1 first." -ForegroundColor Red
    exit 1
}

# Set environment variable for Cassandra driver to use asyncio
$env:CASSANDRA_DRIVER_EVENT_LOOP = 'asyncio'

# Start using the run.py wrapper script (handles asyncio reactor initialization)
python run.py
