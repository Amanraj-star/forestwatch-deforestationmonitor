#!/usr/bin/env bash
# Run from the project root (forest-watch-backend), with the backend
# already running in another terminal on port 8000.
# Usage: ./run_frontend.sh
set -euo pipefail

source .venv/bin/activate
pip install -r frontend/requirements.txt
streamlit run frontend/app.py
