"""Preset regions of interest for deforestation monitoring.

Each bbox is [min_lon, min_lat, max_lon, max_lat] in EPSG:4326.
Feel free to edit/add entries — the API doesn't require a preset,
you can also POST a raw bbox to /api/analyze.
"""

PRESETS = [
    {
        "id": "amazon-rondonia",
        "name": "Rondônia, Brazil (arc of deforestation)",
        "bbox": [-64.0, -11.5, -62.5, -10.0],
    },
    {
        "id": "amazon-para",
        "name": "Pará, Brazil",
        "bbox": [-54.5, -6.5, -53.0, -5.0],
    },
    {
        "id": "congo-basin",
        "name": "Congo Basin, DRC",
        "bbox": [23.0, -1.0, 24.5, 0.5],
    },
    {
        "id": "borneo-kalimantan",
        "name": "Kalimantan, Borneo",
        "bbox": [113.5, -1.5, 115.0, 0.0],
    },
    {
        "id": "sumatra-riau",
        "name": "Riau, Sumatra",
        "bbox": [101.0, 0.0, 102.5, 1.5],
    },
]


def get_preset(preset_id: str):
    for p in PRESETS:
        if p["id"] == preset_id:
            return p
    return None
