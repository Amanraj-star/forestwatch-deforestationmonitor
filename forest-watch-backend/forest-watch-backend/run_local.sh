#!/usr/bin/env bash
# Run once to set up, then any time to start the server.
# Usage: ./run_local.sh
set -euo pipefail

if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "Created .env from .env.example — edit EE_PROJECT before continuing."
fi

# One-time browser login for Earth Engine (skips automatically if already authenticated)
earthengine authenticate

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
