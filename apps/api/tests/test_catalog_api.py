import base64
import json
import os
import sys
import io
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import main


client = TestClient(main.app)


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
    sources = response.json()["sources"]
    assert sources
    for source in sources:
        listing = client.get(f"/api/v1/products/{source['id']}").json()
        assert source["url"] == listing["source_url"]
        for field in ("image_url", "price", "currency", "captured_at"):
            assert source[field] == listing[field]


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


@pytest.mark.parametrize("retry_allowed", [True, False], ids=["fallback-succeeds", "fallback-is-budgeted"])
def test_label_checks_quota_before_falling_back_from_gemini_503(monkeypatch, retry_allowed):
    monkeypatch.setenv("ENABLE_IMAGE_ANALYSIS", "true")
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setenv("GEMINI_VISION_MODEL", "test-primary-model")
    events = []
    requests = []
    allowed = iter((True, retry_allowed))
    observation = {"product_name": "Sample Wash", "visible_ingredients": ["Water"]}

    def check_budget(provider):
        assert provider == "gemini"
        events.append("quota")
        return next(allowed)

    def respond(request):
        events.append("request")
        requests.append(request)
        if len(requests) == 1:
            return httpx.Response(503)
        return httpx.Response(200, json={
            "candidates": [{"content": {"parts": [{"text": json.dumps(observation)}]}}],
        })

    transport = httpx.MockTransport(respond)
    async_client = httpx.AsyncClient
    monkeypatch.setattr(main, "provider_call_allowed", check_budget)
    monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: async_client(transport=transport, **kwargs))
    buffer = io.BytesIO()
    Image.new("RGB", (8, 8), "white").save(buffer, format="PNG")

    response = client.post("/api/v1/vision/label", data={"consent": "true"}, files={
        "image": ("label.png", buffer.getvalue(), "image/png"),
    })

    assert response.status_code == 200
    assert requests[0].url.path.endswith("/test-primary-model:generateContent")
    if retry_allowed:
        assert events == ["quota", "request", "quota", "request"]
        assert requests[0].url != requests[1].url
        primary_photo, photo = [
            json.loads(request.content)["contents"][0]["parts"][1]["inline_data"] for request in requests
        ]
        assert primary_photo == photo
        assert photo["mime_type"] == "image/jpeg"
        with Image.open(io.BytesIO(base64.b64decode(photo["data"]))) as cleaned:
            assert cleaned.format == "JPEG"
        assert response.json()["status"] == "observed_unverified"
        assert response.json()["observation"] == observation
    else:
        assert events == ["quota", "request", "quota"]
        assert response.json()["status"] == "provider_unavailable"
        assert response.json()["observation"] is None

