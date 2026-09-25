# Run once to set up, then any time to start the server.
# Usage: .\run_local.ps1

$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    py -m venv .venv
}

.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "Created .env from .env.example — edit EE_PROJECT before continuing." -ForegroundColor Yellow
}

# One-time browser login for Earth Engine (skips automatically if already authenticated)
earthengine authenticate

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
