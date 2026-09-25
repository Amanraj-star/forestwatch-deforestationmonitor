"""Preset regions of interest for deforestation monitoring.

Each bbox is [min_lon, min_lat, max_lon, max_lat] in EPSG:4326.
The API doesn't require a preset — you can also POST a raw bbox to
/api/analyze (or use "Custom bounding box" in the Streamlit frontend).
"""

PRESETS = [
    # --- Amazon basin ---
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
        "id": "amazon-acre",
        "name": "Acre, Brazil",
        "bbox": [-70.0, -9.5, -68.5, -8.0],
    },
    {
        "id": "peru-madre-de-dios",
        "name": "Madre de Dios, Peru",
        "bbox": [-70.5, -12.5, -69.0, -11.0],
    },
    # --- Congo basin ---
    {
        "id": "congo-basin",
        "name": "Congo Basin, DRC",
        "bbox": [23.0, -1.0, 24.5, 0.5],
    },
    {
        "id": "congo-ituri",
        "name": "Ituri, DRC",
        "bbox": [28.0, 1.0, 29.5, 2.5],
    },
    # --- Southeast Asia ---
    {
        "id": "borneo-kalimantan",
        "name": "Kalimantan, Borneo (Indonesia)",
        "bbox": [113.5, -1.5, 115.0, 0.0],
    },
    {
        "id": "borneo-sarawak",
        "name": "Sarawak, Borneo (Malaysia)",
        "bbox": [111.0, 1.0, 112.5, 2.5],
    },
    {
        "id": "sumatra-riau",
        "name": "Riau, Sumatra",
        "bbox": [101.0, 0.0, 102.5, 1.5],
    },
    {
        "id": "sumatra-aceh",
        "name": "Aceh, Sumatra",
        "bbox": [96.0, 3.5, 97.5, 5.0],
    },
    {
        "id": "myanmar-bago",
        "name": "Bago Yoma, Myanmar",
        "bbox": [96.0, 18.0, 97.5, 19.5],
    },
    # --- Madagascar ---
    {
        "id": "madagascar-east",
        "name": "Eastern rainforest corridor, Madagascar",
        "bbox": [49.0, -18.5, 50.5, -17.0],
    },
]


def get_preset(preset_id: str):
    for p in PRESETS:
        if p["id"] == preset_id:
            return p
    return None
