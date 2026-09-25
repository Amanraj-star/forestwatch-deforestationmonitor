# 🌳 Forest Watch

Forest Watch is a deforestation monitoring app. A **FastAPI** backend queries
**Google Earth Engine** live — forest loss comes from the **Hansen Global
Forest Change v1.13** dataset (2000–2025), with an optional **Sentinel-2**
composite layer for visual context — and a **Streamlit** frontend lets you
pick a region (or draw a custom bounding box), run the analysis, and view
results on an interactive map.

This is a real Earth Engine connection, not mock data — you'll need your own
free Google Earth Engine account to run it (steps below).

## Project structure

```
forest-watch/
├── forest-watch-backend/   # FastAPI + Earth Engine API
│   └── README.md           # detailed backend docs
└── frontend/                # Streamlit app
    └── app.py
```

## Quick start

### 1. One-time Earth Engine account setup

1. Sign up for Earth Engine (free): https://earthengine.google.com/signup/
2. Register a Google Cloud project for Earth Engine use:
   https://code.earthengine.google.com/register
   (note the **project id**, you'll need it below)

### 2. Run the backend

**macOS / Linux**
```bash
cd forest-watch-backend
chmod +x run_local.sh   # if needed
./run_local.sh
```

**Windows (PowerShell)**
```powershell
cd forest-watch-backend
.\run_local.ps1
```

This creates a virtualenv, installs dependencies, copies `.env.example` to
`.env` (edit it and set `EE_PROJECT` to your project id), runs
`earthengine authenticate` once, and starts the API at
**http://localhost:8000** (docs at `/docs`).

See [`forest-watch-backend/README.md`](forest-watch-backend/README.md) for
full endpoint docs, request/response formats, and troubleshooting.

### 3. Run the frontend

With the backend running in one terminal, in another:

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

By default the frontend talks to `http://localhost:8000`. To point it at a
different backend, set the `FOREST_WATCH_API` environment variable before
running Streamlit.

## Using the app

1. In the sidebar, pick a **preset region** or enter a **custom bounding
   box** (decimal degrees).
2. Choose a **year range** (2001–2025) and optionally include the
   Sentinel-2 imagery layer.
3. Click **Analyze selected area**.
4. View forest area, area lost, and loss % alongside a map with tree cover,
   loss, and (optionally) Sentinel-2 tile layers.

## Tech stack

- **Backend:** FastAPI, Google Earth Engine Python API, Pydantic, local JSON
  result caching
- **Frontend:** Streamlit, Folium / streamlit-folium, Requests

## License

Add your preferred license here (e.g. MIT) before publishing.
