import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import cache, ee_service, presets
from .schemas import AnalyzeRequest, AnalyzeResponse, PresetOut

load_dotenv()

app = FastAPI(
    title="Forest Watch API",
    description="Deforestation monitoring backend — Hansen Global Forest Change "
    "via Google Earth Engine, with optional Sentinel-2 context.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this once you have a real frontend origin
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    project = os.getenv("EE_PROJECT")
    try:
        ee_service.init_earth_engine(project)
        print(f"[startup] Earth Engine initialized (project={project or 'default'})")
    except RuntimeError as exc:
        # Don't crash the server on boot — surface the error on first /api/analyze call
        # instead, so /api/health and /api/presets still work without EE credentials.
        print(f"[startup warning] {exc}")


@app.get("/api/health")
def health():
    return {"status": "ok", "earth_engine_ready": ee_service.is_initialized()}


@app.get("/api/presets", response_model=List[PresetOut])
def list_presets():
    return presets.PRESETS


@app.post("/api/analyze", response_model=AnalyzeResponse)
def analyze(req: AnalyzeRequest):
    if not ee_service.is_initialized():
        try:
            ee_service.init_earth_engine(os.getenv("EE_PROJECT"))
        except RuntimeError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc

    if req.preset_id:
        preset = presets.get_preset(req.preset_id)
        if not preset:
            raise HTTPException(status_code=404, detail=f"Unknown preset_id '{req.preset_id}'")
        bbox = preset["bbox"]
    else:
        bbox = req.bbox

    cache_kwargs = dict(
        bbox=bbox,
        start_year=req.start_year,
        end_year=req.end_year,
        include_sentinel=req.include_sentinel,
    )

    cached_result = cache.get_cached(**cache_kwargs)
    if cached_result is not None:
        cached_result["cached"] = True
        return cached_result

    try:
        result = ee_service.analyze_region(
            bbox, req.start_year, req.end_year, req.include_sentinel
        )
    except Exception as exc:  # noqa: BLE001 - turn EE errors into a clean HTTP error
        raise HTTPException(status_code=502, detail=f"Earth Engine query failed: {exc}") from exc

    result["cached"] = False
    cache.set_cached(result, **cache_kwargs)
    return result
