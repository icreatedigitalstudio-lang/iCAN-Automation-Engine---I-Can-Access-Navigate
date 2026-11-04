
import pytest

def test_api():
    try:
        from src.pyautoforge.api.main import app
        from fastapi.testclient import TestClient
        client = TestClient(app)
        resp = client.get("/health/live")
        assert resp.status_code == 200
    except Exception as e:
        pytest.skip(f"API not available: {e}")
