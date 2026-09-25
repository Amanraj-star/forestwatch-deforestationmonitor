"""Forest Watch — Streamlit frontend.

Talks to the local FastAPI backend (app/main.py) over HTTP. Run the
backend first (uvicorn app.main:app --port 8000), then run this:

    streamlit run frontend/app.py
"""

import os

import folium
import requests
import streamlit as st
from streamlit_folium import st_folium

API_BASE = os.getenv("FOREST_WATCH_API", "http://localhost:8000")

st.set_page_config(page_title="Forest Watch", layout="wide")
st.title("🌳 Forest Watch — Deforestation Monitor")
st.caption(
    "Hansen Global Forest Change v1.13 (2000–2025), served by a local "
    "FastAPI + Google Earth Engine backend."
)


@st.cache_data(ttl=300)
def get_presets():
    r = requests.get(f"{API_BASE}/api/presets", timeout=10)
    r.raise_for_status()
    return r.json()


def health_check():
    try:
        r = requests.get(f"{API_BASE}/api/health", timeout=5)
        return r.json()
    except Exception:
        return None


health = health_check()
if health is None:
    st.error(
        f"Can't reach the backend at {API_BASE}. Make sure it's running: "
        "`uvicorn app.main:app --reload --port 8000`"
    )
    st.stop()
if not health.get("earth_engine_ready"):
    st.warning("Backend is up, but Earth Engine isn't initialized on the server yet.")

try:
    presets = get_presets()
except Exception as exc:
    st.error(f"Couldn't load presets: {exc}")
    st.stop()

preset_by_name = {p["name"]: p for p in presets}

with st.sidebar:
    st.header("Query")
    mode = st.radio("Area", ["Preset region", "Custom bounding box"])

    preset_id = None
    if mode == "Preset region":
        choice = st.selectbox("Region", list(preset_by_name.keys()))
        preset = preset_by_name[choice]
        bbox = preset["bbox"]
        preset_id = preset["id"]
    else:
        st.caption("Enter a bounding box in decimal degrees")
        col1, col2 = st.columns(2)
        min_lon = col1.number_input("Min Lon", value=-64.0, format="%.4f")
        min_lat = col2.number_input("Min Lat", value=-11.5, format="%.4f")
        max_lon = col1.number_input("Max Lon", value=-62.5, format="%.4f")
        max_lat = col2.number_input("Max Lat", value=-10.0, format="%.4f")
        bbox = [min_lon, min_lat, max_lon, max_lat]

    start_year, end_year = st.slider("Year range", 2001, 2025, (2015, 2024))
    include_sentinel = st.checkbox("Include Sentinel-2 imagery layer", value=False)
    run = st.button("Analyze selected area", type="primary")

if "result" not in st.session_state:
    st.session_state["result"] = None
    st.session_state["bbox"] = bbox

if run:
    payload = {
        "start_year": start_year,
        "end_year": end_year,
        "include_sentinel": include_sentinel,
    }
    if preset_id:
        payload["preset_id"] = preset_id
    else:
        payload["bbox"] = bbox

    with st.spinner("Querying Earth Engine — first run for a new area can take 10-30s..."):
        try:
            r = requests.post(f"{API_BASE}/api/analyze", json=payload, timeout=120)
            r.raise_for_status()
            st.session_state["result"] = r.json()
            st.session_state["bbox"] = bbox
        except requests.HTTPError as exc:
            st.error(f"Analysis failed: {exc.response.text}")
        except Exception as exc:
            st.error(f"Request failed: {exc}")

result = st.session_state["result"]

col_map, col_stats = st.columns([2, 1])

with col_map:
    center_bbox = st.session_state.get("bbox", bbox)
    center_lat = (center_bbox[1] + center_bbox[3]) / 2
    center_lon = (center_bbox[0] + center_bbox[2]) / 2
    m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles="CartoDB positron")

    if result:
        folium.TileLayer(
            tiles=result["tree_cover_tile_url"],
            attr="Google Earth Engine",
            name="Tree cover (2000)",
            overlay=True,
        ).add_to(m)
        folium.TileLayer(
            tiles=result["loss_tile_url"],
            attr="Google Earth Engine",
            name="Forest loss",
            overlay=True,
        ).add_to(m)
        if result.get("sentinel_tile_url"):
            folium.TileLayer(
                tiles=result["sentinel_tile_url"],
                attr="Copernicus Sentinel-2",
                name="Sentinel-2",
                overlay=True,
            ).add_to(m)
        folium.LayerControl().add_to(m)

    st_folium(m, height=560, use_container_width=True)

with col_stats:
    st.subheader("Results")
    if result:
        st.metric("Forest area (≥30% canopy, 2000)", f"{result['forest_area_ha']:,} ha")
        st.metric("Forest lost in range", f"{result['loss_area_ha']:,} ha")
        st.metric("Loss %", f"{result['loss_percent']}%")
        st.caption(f"Dataset: {result['dataset']}")
        st.caption(f"Years: {result['start_year']}–{result['end_year']}")
        st.caption(f"Cached result: {result['cached']}")
        st.caption(f"Computed at: {result['computed_at']}")
    else:
        st.info("Choose an area in the sidebar and click **Analyze selected area**.")
