# Chatbot Fix & Run Script
# Run this in a NEW PowerShell window after closing ALL Python processes

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "  🔧 Fixing Chatbot Environment" -ForegroundColor Yellow
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""

# Check if any Python processes are running
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue
if ($pythonProcesses) {
    Write-Host "⚠️  Warning: Python processes are still running!" -ForegroundColor Red
    Write-Host "Please close all Python processes, VSCode, and terminals, then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Running processes:" -ForegroundColor Yellow
    $pythonProcesses | Format-Table Name, Id, Path -AutoSize
    Write-Host ""
    $response = Read-Host "Do you want to force-kill these processes? (y/N)"
    if ($response -eq "y" -or $response -eq "Y") {
        $pythonProcesses | Stop-Process -Force
        Write-Host "✅ Killed Python processes" -ForegroundColor Green
        Start-Sleep -Seconds 2
    } else {
        exit 1
    }
}

Write-Host "1. Removing old virtual environment..." -ForegroundColor Yellow
if (Test-Path .venv) {
    try {
        Remove-Item -Recurse -Force .venv -ErrorAction Stop
        Write-Host "   ✅ Removed .venv" -ForegroundColor Green
    } catch {
        Write-Host "   ⚠️  Could not remove .venv automatically" -ForegroundColor Red
        Write-Host "   Please manually delete the .venv folder and run this script again" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host "   ✅ No existing .venv" -ForegroundColor Green
}

Write-Host ""
Write-Host "2. Creating fresh virtual environment..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Failed to create venv" -ForegroundColor Red
    exit 1
}
Write-Host "   ✅ Created .venv" -ForegroundColor Green

Write-Host ""
Write-Host "3. Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1
Write-Host "   ✅ Activated" -ForegroundColor Green

Write-Host ""
Write-Host "4. Installing dependencies (this may take a few minutes)..." -ForegroundColor Yellow
uv sync
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Installation failed" -ForegroundColor Red
    Write-Host "   Try: pip install -e ." -ForegroundColor Yellow
    exit 1
}
Write-Host "   ✅ Dependencies installed" -ForegroundColor Green

Write-Host ""
Write-Host "5. Testing chatbot import..." -ForegroundColor Yellow
python -c "from chatbot.api import app; print('   ✅ Chatbot ready!')"
if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Import test failed" -ForegroundColor Red
    Write-Host "   Check SETUP_CHATBOT.md for manual troubleshooting" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host "  ✅ SUCCESS! Chatbot is ready to run" -ForegroundColor Green
Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host ("=" * 79) -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the chatbot:" -ForegroundColor Cyan
Write-Host "  uvicorn chatbot.api:app --reload --port 8001" -ForegroundColor White
Write-Host ""
Write-Host "Then visit: http://localhost:8001" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press any key to start the server now, or Ctrl+C to exit..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "Starting server..." -ForegroundColor Green
uvicorn chatbot.api:app --reload --port 8001
