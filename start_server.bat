@echo off
echo ================================================================================
echo   Starting LangChain1 Production Server
echo ================================================================================
echo.

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Checking dependencies...
python -c "import fastapi, uvicorn; print('FastAPI and uvicorn found!')"

if errorlevel 1 (
    echo Dependencies not found. Please run: uv pip install -r langchain1/requirements.txt
    exit /b 1
)

echo.
echo Starting server on http://localhost:8002...
echo.
echo API Docs:      http://localhost:8002/docs
echo Health Check:  http://localhost:8002/health
echo Metrics:       http://localhost:8002/metrics
echo.
echo Press Ctrl+C to stop the server
echo ================================================================================
echo.

python -m uvicorn langchain1.production_server:app --reload --port 8002 --host 0.0.0.0
