"""Very small local cache so repeated queries don't re-hit Earth Engine.

Results are keyed by a hash of the query parameters and stored as JSON
files under ../cache. Hansen forest-loss stats for a fixed area/year
range don't change between runs, so there's no TTL/eviction — delete
the cache/ folder if you ever want to force a recompute.
"""

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

CACHE_DIR = Path(__file__).resolve().parent.parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


def _cache_key(**kwargs) -> str:
    raw = json.dumps(kwargs, sort_keys=True, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:24]


def get_cached(**kwargs) -> Optional[Dict[str, Any]]:
    path = CACHE_DIR / f"{_cache_key(**kwargs)}.json"
    if path.exists():
        return json.loads(path.read_text())
    return None


def set_cached(result: Dict[str, Any], **kwargs) -> None:
    path = CACHE_DIR / f"{_cache_key(**kwargs)}.json"
    path.write_text(json.dumps(result, indent=2))
