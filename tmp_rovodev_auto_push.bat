@echo off
echo ============================================
echo Auto Push to GitHub
echo ============================================
echo.

REM Remove old remote if exists
git remote remove origin 2>nul

REM Add GitHub remote (UPDATE THE USERNAME IF NEEDED)
echo Adding remote...
git remote add origin https://github.com/pavs-123/chatbot-project2.git

REM Rename branch to main
echo Renaming branch to main...
git branch -M main

REM Push to GitHub
echo.
echo Pushing to GitHub...
echo You will be prompted for:
echo   Username: pavs-123 (or pavs_123)
echo   Password: Your GitHub Token
echo.
git push -u origin main

echo.
echo ============================================
echo Done! Check: https://github.com/pavs-123/chatbot-project2
echo ============================================
pause
