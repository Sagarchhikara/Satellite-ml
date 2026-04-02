import numpy as np
import rasterio
from rasterio.transform import from_origin

def create_test_tif(filepath="/home/sagarchhikara/Satellite-ml/satellite_project/test_tile.tif"):
    np.random.seed(42)
    red = np.random.uniform(0.05, 0.15, (10, 10)).astype(np.float32)
    nir = np.random.uniform(0.2, 0.6, (10, 10)).astype(np.float32)
    
    red[0:4, :] = 0.05
    nir[0:4, :] = 0.5   # NDVI = 0.81 (healthy)
    
    red[4:7, :] = 0.2
    nir[4:7, :] = 0.35  # NDVI = 0.27 (weak)
    
    red[7:10, :] = 0.3
    nir[7:10, :] = 0.35 # NDVI = 0.07 (stressed)
    
    transform = from_origin(0, 0, 10, 10)
    
    with rasterio.open(
        filepath,
        'w',
        driver='GTiff',
        height=10,
        width=10,
        count=2,
        dtype=str(red.dtype),
        crs='+proj=latlong',
        transform=transform,
    ) as dst:
        dst.write(red, 1)
        dst.write(nir, 2)

if __name__ == '__main__':
    create_test_tif()
