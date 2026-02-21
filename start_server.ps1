# Start LangChain1 Production Server
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "  🚀 Starting LangChain1 Production Server" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Check if activation worked
Write-Host "Checking dependencies..." -ForegroundColor Yellow
python -c "import fastapi, uvicorn; print('✅ FastAPI and uvicorn found!')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Dependencies not found. Please run: uv pip install -r langchain1/requirements.txt" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Starting server on http://localhost:8002..." -ForegroundColor Green
Write-Host ""
Write-Host "📖 API Docs:      http://localhost:8002/docs" -ForegroundColor Cyan
Write-Host "❤️  Health Check:  http://localhost:8002/health" -ForegroundColor Cyan
Write-Host "📊 Metrics:        http://localhost:8002/metrics" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Start the server
python -m uvicorn langchain1.production_server:app --reload --port 8002 --host 0.0.0.0
