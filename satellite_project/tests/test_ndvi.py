import os
import pytest
from httpx import AsyncClient, ASGITransport
from main import app
from utils import validate_tif

TEST_TILE_PATH = "test_tile.tif"

@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "satellite-ndvi"}

@pytest.mark.asyncio
async def test_analyze_rejects_non_tif():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        files = {"file": ("test.jpg", b"fake data", "image/jpeg")}
        response = await ac.post("/analyze", files=files)
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_analyze_with_valid_tile():
    assert os.path.exists(TEST_TILE_PATH), f"{TEST_TILE_PATH} not found"
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(TEST_TILE_PATH, "rb") as f:
            files = {"file": (TEST_TILE_PATH, f, "image/tiff")}
            response = await ac.post("/analyze", files=files)
            
    assert response.status_code == 200, response.text
    data = response.json()
    expected_keys = {"mean", "min", "max", "healthy_pct", "weak_pct", "stressed_pct", "pixel_count", "filename"}
    for key in expected_keys:
        assert key in data
    assert data["filename"] == TEST_TILE_PATH

@pytest.mark.asyncio
async def test_ndvi_values_in_valid_range():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(TEST_TILE_PATH, "rb") as f:
            files = {"file": (TEST_TILE_PATH, f, "image/tiff")}
            response = await ac.post("/analyze", files=files)
            
    assert response.status_code == 200
    data = response.json()
    assert -1.0 <= data["mean"] <= 1.0

@pytest.mark.asyncio
async def test_percentages_sum_to_100():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        with open(TEST_TILE_PATH, "rb") as f:
            files = {"file": (TEST_TILE_PATH, f, "image/tiff")}
            response = await ac.post("/analyze", files=files)
            
    assert response.status_code == 200
    data = response.json()
    total_pct = data["healthy_pct"] + data["weak_pct"] + data["stressed_pct"]
    assert abs(total_pct - 100.0) <= 0.1

def test_validate_tif_with_valid_file():
    assert validate_tif(TEST_TILE_PATH) is True

def test_validate_tif_with_fake_file():
    assert validate_tif("nonexistent_fake_file.tif") is False
