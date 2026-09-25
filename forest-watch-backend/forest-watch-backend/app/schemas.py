from typing import List, Optional

from pydantic import BaseModel, Field, model_validator


class AnalyzeRequest(BaseModel):
    preset_id: Optional[str] = Field(
        default=None, description="Id of a preset region (see GET /api/presets)"
    )
    bbox: Optional[List[float]] = Field(
        default=None,
        description="[min_lon, min_lat, max_lon, max_lat] — required if preset_id is omitted",
    )
    start_year: int = Field(default=2001, ge=2001, le=2025)
    end_year: int = Field(default=2024, ge=2001, le=2025)
    include_sentinel: bool = Field(
        default=False, description="Also fetch a Sentinel-2 median composite tile layer"
    )

    @model_validator(mode="after")
    def _check_area_and_years(self):
        if not self.preset_id and not self.bbox:
            raise ValueError("Provide either 'preset_id' or 'bbox'")
        if self.bbox is not None and len(self.bbox) != 4:
            raise ValueError("bbox must be exactly [min_lon, min_lat, max_lon, max_lat]")
        if self.start_year > self.end_year:
            raise ValueError("start_year must be <= end_year")
        return self


class PresetOut(BaseModel):
    id: str
    name: str
    bbox: List[float]


class AnalyzeResponse(BaseModel):
    forest_area_ha: float
    loss_area_ha: float
    loss_percent: float
    tree_cover_tile_url: str
    loss_tile_url: str
    sentinel_tile_url: Optional[str] = None
    dataset: str
    start_year: int
    end_year: int
    computed_at: str
    cached: bool
