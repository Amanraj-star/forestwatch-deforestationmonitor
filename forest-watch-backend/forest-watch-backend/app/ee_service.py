"""Google Earth Engine connection + deforestation analysis.

Detection source: UMD/hansen/global_forest_change_2025_v1_13
  - 'treecover2000'  : % canopy cover in year 2000
  - 'loss'           : binary forest-loss mask, 2001-2025
  - 'lossyear'       : year of loss, encoded 1-25 (=> 2001-2025)
Optional context layer: Sentinel-2 surface reflectance (COPERNICUS/S2_SR_HARMONIZED),
median composite for the end_year, cloud-filtered.
"""

from datetime import datetime, timezone

import ee

DATASET_ID = "UMD/hansen/global_forest_change_2025_v1_13"
FOREST_CANOPY_THRESHOLD = 30  # % canopy cover in 2000 to count a pixel as "forest"

_initialized = False


def init_earth_engine(project: str | None = None) -> None:
    """Initialize the Earth Engine connection.

    Requires that `earthengine authenticate` has already been run once on
    this machine (stores a local OAuth credential), and that `project` is
    a Google Cloud project with the Earth Engine API enabled.
    """
    global _initialized
    if _initialized:
        return
    try:
        if project:
            ee.Initialize(project=project)
        else:
            ee.Initialize()
        _initialized = True
    except Exception as exc:  # noqa: BLE001 - surface a clear setup message
        raise RuntimeError(
            "Earth Engine could not be initialized. Run 'earthengine authenticate' "
            "once, set EE_PROJECT in your .env to a Google Cloud project that has "
            "the Earth Engine API enabled (register at "
            "https://code.earthengine.google.com/register), then restart the server."
        ) from exc


def is_initialized() -> bool:
    return _initialized


def _region_from_bbox(bbox: list[float]) -> "ee.Geometry":
    min_lon, min_lat, max_lon, max_lat = bbox
    return ee.Geometry.Rectangle([min_lon, min_lat, max_lon, max_lat])


def analyze_region(
    bbox: list[float],
    start_year: int,
    end_year: int,
    include_sentinel: bool,
) -> dict:
    if not _initialized:
        raise RuntimeError("Earth Engine not initialized")

    region = _region_from_bbox(bbox)

    hansen = ee.Image(DATASET_ID)
    tree_cover = hansen.select("treecover2000")
    loss_year = hansen.select("lossyear")

    start_offset = max(start_year - 2000, 1)
    end_offset = min(end_year - 2000, 25)
    loss_in_range = hansen.select("loss").updateMask(
        loss_year.gte(start_offset).And(loss_year.lte(end_offset))
    )

    forest_mask = tree_cover.gte(FOREST_CANOPY_THRESHOLD)
    pixel_area = ee.Image.pixelArea()

    forest_area_img = pixel_area.updateMask(forest_mask)
    loss_area_img = pixel_area.updateMask(loss_in_range)

    stats = ee.Dictionary(
        {
            "forest_area_m2": forest_area_img.reduceRegion(
                reducer=ee.Reducer.sum(), geometry=region, scale=30, maxPixels=1e10
            ).get("area"),
            "loss_area_m2": loss_area_img.reduceRegion(
                reducer=ee.Reducer.sum(), geometry=region, scale=30, maxPixels=1e10
            ).get("area"),
        }
    ).getInfo()

    forest_area_ha = (stats.get("forest_area_m2") or 0) / 10000
    loss_area_ha = (stats.get("loss_area_m2") or 0) / 10000
    loss_percent = (loss_area_ha / forest_area_ha * 100) if forest_area_ha else 0.0

    tree_cover_map = (
        tree_cover.updateMask(tree_cover.gt(0))
        .visualize(min=0, max=100, palette=["black", "green"])
        .getMapId()
    )
    loss_map = loss_in_range.visualize(palette=["red"]).getMapId()

    sentinel_tile_url = None
    if include_sentinel:
        sentinel = (
            ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
            .filterBounds(region)
            .filterDate(f"{end_year}-01-01", f"{end_year}-12-31")
            .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
            .median()
        )
        sentinel_map = sentinel.visualize(bands=["B4", "B3", "B2"], min=0, max=3000).getMapId()
        sentinel_tile_url = sentinel_map["tile_fetcher"].url_format

    return {
        "forest_area_ha": round(forest_area_ha, 2),
        "loss_area_ha": round(loss_area_ha, 2),
        "loss_percent": round(loss_percent, 3),
        "tree_cover_tile_url": tree_cover_map["tile_fetcher"].url_format,
        "loss_tile_url": loss_map["tile_fetcher"].url_format,
        "sentinel_tile_url": sentinel_tile_url,
        "dataset": DATASET_ID,
        "start_year": start_year,
        "end_year": end_year,
        "computed_at": datetime.now(timezone.utc).isoformat(),
    }
