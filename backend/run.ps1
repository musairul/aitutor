# Run this script to start the backend
# First activate the virtual environment, then run the app

Write-Host "Starting AI Tutor Backend..." -ForegroundColor Green
Write-Host "Make sure you're in the backend directory and virtual environment is activated" -ForegroundColor Yellow
Write-Host ""

# Check if we're in the right directory
if (Test-Path "app.py") {
    python app.py
} else {
    Write-Host "Error: app.py not found. Please run this from the backend directory." -ForegroundColor Red
    Write-Host "cd backend" -ForegroundColor Yellow
}
