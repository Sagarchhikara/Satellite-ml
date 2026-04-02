import os
import rasterio

def validate_tif(filepath: str) -> bool:
    if not os.path.exists(filepath):
        return False
    try:
        with rasterio.open(filepath) as src:
            # Optionally check if it's a valid raster with some shape/bands
            return src.count >= 0
    except Exception:
        return False

def get_band_count(filepath: str) -> int:
    with rasterio.open(filepath) as src:
        return src.count
