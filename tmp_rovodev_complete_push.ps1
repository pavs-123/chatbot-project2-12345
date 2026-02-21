# Complete GitHub Push Script
Write-Host "=" * 60 -ForegroundColor Cyan
Write-Host "GitHub Upload Script for chatbot-project2" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Cyan

# Step 1: Check current status
Write-Host "`n[1/6] Checking current Git status..." -ForegroundColor Yellow
git status

# Step 2: Remove old remote if exists
Write-Host "`n[2/6] Removing old remote (if exists)..." -ForegroundColor Yellow
git remote remove origin 2>$null

# Step 3: Add remote
Write-Host "`n[3/6] Adding GitHub remote..." -ForegroundColor Yellow
git remote add origin https://github.com/pavs-123/chatbot-project2.git
git remote -v

# Step 4: Rename branch to main
Write-Host "`n[4/6] Renaming branch to main..." -ForegroundColor Yellow
git branch -M main
git branch

# Step 5: Test connection
Write-Host "`n[5/6] Testing GitHub connection..." -ForegroundColor Yellow
Write-Host "Checking remote repository..." -ForegroundColor Gray
git ls-remote --heads origin

# Step 6: Push to GitHub
Write-Host "`n[6/6] Pushing all files to GitHub..." -ForegroundColor Yellow
Write-Host "You will be prompted for credentials:" -ForegroundColor Gray
Write-Host "  Username: pavs-123" -ForegroundColor Gray
Write-Host "  Password: [Your GitHub Token]" -ForegroundColor Gray
Write-Host ""
git push -u origin main --verbose

Write-Host "`n" + "=" * 60 -ForegroundColor Green
Write-Host "Push complete! Visit: https://github.com/pavs-123/chatbot-project2" -ForegroundColor Green
Write-Host "=" * 60 -ForegroundColor Green
