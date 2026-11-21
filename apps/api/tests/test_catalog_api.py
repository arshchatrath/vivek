import os
import sys
import io
from pathlib import Path

from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app


client = TestClient(app)


def test_catalog_has_four_sourced_brands():
    response = client.get("/api/v1/products", params={"limit": 100})
    assert response.status_code == 200
    assert response.json()["total"] >= 300
    for brand in ("Man Matters", "Be Bodywise", "Little Joys", "Root Labs"):
        result = client.get("/api/v1/products", params={"brand": brand, "limit": 1}).json()
        assert result["total"] > 0
        assert result["products"][0]["source_url"].startswith("https://")


def test_unknown_sensitive_fields_are_not_invented():
    product = client.get("/api/v1/products", params={"brand": "Little Joys", "limit": 1}).json()["products"][0]
    assert product["ingredients"] is None
    assert product["warnings"] is None
    assert product["age_restrictions"] is None


def test_missing_product_and_invalid_compare_return_404():
    assert client.get("/api/v1/products/not-real").status_code == 404
    assert client.post("/api/v1/products/compare", json={"product_ids": ["bad1", "bad2"]}).status_code == 404


def test_emergency_uses_safety_message_without_provider():
    response = client.post("/api/v1/chat", json={"question": "I have chest pain and can't breathe"})
    assert response.status_code == 200
    assert response.json()["status"] == "safety_escalation"
    assert response.json()["provider"] is None


def test_no_api_key_returns_source_cards(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_TEXT_MODEL", raising=False)
    response = client.post("/api/v1/chat", json={"question": "What does Man Matters DHT shampoo listing say?"})
    assert response.status_code == 200
    assert response.json()["status"] == "source_only"
    assert response.json()["sources"]


def test_label_requires_consent_and_does_not_call_provider_without_key(monkeypatch):
    monkeypatch.setenv("ENABLE_IMAGE_ANALYSIS", "true")
    image = Image.new("RGB", (8, 8), "white")
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    upload = {"image": ("label.png", buffer.getvalue(), "image/png")}
    assert client.post("/api/v1/vision/label", files=upload).status_code == 400
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    response = client.post("/api/v1/vision/label", files=upload, data={"consent": "true"})
    assert response.status_code == 200
    assert response.json()["status"] == "provider_unavailable"

