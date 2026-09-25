# Run from the project root (forest-watch-backend), with the backend
# already running in another terminal on port 8000.
# Usage: .\run_frontend.ps1

$ErrorActionPreference = "Stop"

.\.venv\Scripts\Activate.ps1
pip install -r frontend\requirements.txt
streamlit run frontend\app.py
