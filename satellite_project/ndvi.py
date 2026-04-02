import numpy as np
import rasterio

def compute_ndvi(filepath: str) -> dict:
    with rasterio.open(filepath) as src:
        if src.count < 2:
            raise ValueError(f"File has fewer than 2 bands: {src.count}")
        
        red = src.read(1).astype(np.float64)
        nir = src.read(2).astype(np.float64)

    # Suppress divide-by-zero warnings
    old_settings = np.seterr(divide='ignore', invalid='ignore')
    try:
        ndvi = (nir - red) / (nir + red)
    finally:
        np.seterr(**old_settings)

    # Mask valid pixels
    valid_mask = np.isfinite(ndvi)
    valid_ndvi = ndvi[valid_mask]
    
    pixel_count = valid_ndvi.size
    
    if pixel_count == 0:
        return {
            "mean": 0.0,
            "min": 0.0,
            "max": 0.0,
            "healthy_pct": 0.0,
            "weak_pct": 0.0,
            "stressed_pct": 0.0,
            "pixel_count": 0
        }
        
    mean_val = float(np.mean(valid_ndvi))
    min_val = float(np.min(valid_ndvi))
    max_val = float(np.max(valid_ndvi))
    
    healthy = np.sum(valid_ndvi > 0.4)
    weak = np.sum((valid_ndvi >= 0.2) & (valid_ndvi <= 0.4))
    stressed = np.sum(valid_ndvi < 0.2)
    
    healthy_pct = (int(healthy) / pixel_count) * 100.0
    weak_pct = (int(weak) / pixel_count) * 100.0
    stressed_pct = (int(stressed) / pixel_count) * 100.0
    
    return {
        "mean": round(mean_val, 4),
        "min": round(min_val, 4),
        "max": round(max_val, 4),
        "healthy_pct": round(healthy_pct, 2),
        "weak_pct": round(weak_pct, 2),
        "stressed_pct": round(stressed_pct, 2),
        "pixel_count": int(pixel_count)
    }
