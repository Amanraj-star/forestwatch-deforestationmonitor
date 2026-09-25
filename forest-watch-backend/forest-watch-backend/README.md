# Forest Watch — Backend API

A FastAPI backend for deforestation monitoring. It queries **Google Earth
Engine** live: forest loss detection comes from the **Hansen Global Forest
Change v1.13** dataset (`UMD/hansen/global_forest_change_2025_v1_13`,
coverage 2000–2025), with an optional **Sentinel-2** median-composite layer
for visual context. Results are cached to disk so repeat queries for the
same area/year-range don't re-hit Earth Engine.

This is a real API connection, not mock data — you need your own free
Google Earth Engine account to run it.

## 1. One-time account setup (do this first, in a browser)

1. Sign up for Earth Engine (free) if you haven't: https://earthengine.google.com/signup/
2. Register a Google Cloud project for Earth Engine use:
   https://code.earthengine.google.com/register
   (Note the **project id** — you'll need it below.)

## 2. Install & run

**Windows (PowerShell):**
```powershell
cd forest-watch-backend
.\run_local.ps1
```

**macOS / Linux:**
```bash
cd forest-watch-backend
chmod +x run_local.sh   # if needed
./run_local.sh
```

The script will:
- create a virtualenv (`.venv`) and install `requirements.txt`
- copy `.env.example` to `.env` (edit it and set `EE_PROJECT` to your project id)
- run `earthengine authenticate` (opens a browser once, then remembers you)
- start the API at **http://localhost:8000**

If you'd rather run the steps by hand:
```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env             # then edit EE_PROJECT inside it
earthengine authenticate
uvicorn app.main:app --reload --port 8000
```

## 3. Try it

Interactive docs (Swagger UI): **http://localhost:8000/docs**

```bash
# Health check
curl http://localhost:8000/api/health

# List preset regions
curl http://localhost:8000/api/presets

# Analyze a preset region
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"preset_id": "amazon-rondonia", "start_year": 2015, "end_year": 2024, "include_sentinel": true}'

# Or analyze a custom bounding box [min_lon, min_lat, max_lon, max_lat]
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"bbox": [-64.0, -11.5, -62.5, -10.0], "start_year": 2020, "end_year": 2024}'
```

`/api/analyze` returns forest area, area lost, loss %, and XYZ **tile URL
templates** you can drop straight into a Leaflet/Mapbox/folium map
(`{z}/{x}/{y}` placeholders included) — one for tree cover, one for loss,
and optionally one for the Sentinel-2 composite.

## Project layout

```
forest-watch-backend/
├── app/
│   ├── main.py         # FastAPI app + routes
│   ├── ee_service.py   # Earth Engine connection + analysis logic
│   ├── presets.py       # Preset regions of interest
│   ├── schemas.py       # Request/response models
│   └── cache.py          # Local JSON result cache
├── cache/                # Auto-created; cached results live here
├── requirements.txt
├── .env.example
├── run_local.sh / run_local.ps1
└── README.md
```

## Endpoints

| Method | Path            | Description                                   |
|--------|-----------------|------------------------------------------------|
| GET    | `/api/health`   | Server + Earth Engine connection status       |
| GET    | `/api/presets`  | List of preset regions                        |
| POST   | `/api/analyze`  | Run/fetch a deforestation analysis            |

`POST /api/analyze` body:
```json
{
  "preset_id": "amazon-rondonia",   // OR "bbox": [minLon, minLat, maxLon, maxLat]
  "start_year": 2001,               // 2001-2025
  "end_year": 2024,                 // 2001-2025
  "include_sentinel": false
}
```

## Connecting a frontend

CORS is wide open (`*`) for local development. Point any frontend (the
Streamlit app you already have, a React app, etc.) at
`http://localhost:8000/api/...`. If you want, I can also wire up a
Streamlit or React frontend that calls this API directly — just ask.

## Troubleshooting

- **"Earth Engine could not be initialized"** — you haven't run
  `earthengine authenticate` yet, or `EE_PROJECT` in `.env` is wrong/unset,
  or that Google Cloud project doesn't have the Earth Engine API enabled.
- **`reduceRegion` is slow for large areas** — Hansen data is 30 m
  resolution; very large bboxes at `scale=30` can take a while. Shrink the
  bbox or raise `scale` in `ee_service.py` for faster (coarser) stats.
- **Want fresh results** — delete everything in `cache/` to force
  recomputation.
