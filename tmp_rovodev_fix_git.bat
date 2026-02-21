@echo off
echo ============================================
echo Fixing Git Lock and Pushing to GitHub
echo ============================================
echo.

echo [1/4] Removing Git lock file...
del /F /Q ".git\index.lock" 2>nul
del /F /Q ".git\ORIG_HEAD.lock" 2>nul
del /F /Q ".git\refs\heads\main.lock" 2>nul

echo [2/4] Aborting rebase...
git rebase --abort

echo [3/4] Resetting to clean state...
git reset --hard HEAD

echo [4/4] Checking what's on GitHub...
git fetch origin
git log origin/main --oneline -10

echo.
echo ============================================
echo Check: https://github.com/pavs-123/chatbot-project2-12345
echo ============================================
echo.
echo If files are already there, you're done!
echo If not, run: git push -u origin main --force
echo.
pause
