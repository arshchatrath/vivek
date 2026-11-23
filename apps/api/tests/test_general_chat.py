"""Verify general chat safety, provider reporting, and grounded retrieval."""

import json
import sys
from pathlib import Path
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app import main
from app import rag_service as retrieval


client = TestClient(main.app)


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    for key in ("DATABASE_URL", "REDIS_URL", "GROQ_API_KEY", "GROQ_TEXT_MODEL"):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture
def provider(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(main, "provider_call_allowed", lambda name: name == "groq")
    real_client = httpx.AsyncClient

    def mock_response(status_code=200):
        requests = []

        def respond(request):
            requests.append(json.loads(request.content))
            return httpx.Response(status_code, json={"choices": [{"message": {"content": "Example reply"}}]})

        transport = httpx.MockTransport(respond)
        monkeypatch.setattr(main.httpx, "AsyncClient", lambda **kwargs: real_client(transport=transport, **kwargs))
        return requests

    return mock_response


@pytest.mark.parametrize(("message", "expected"), [
    ("I have severe chest pain", "urgent"),
    ("I have shortness of breath", "urgent"),
    ("I am suicidal", "urgent"),
    ("saans nahi aa rahi", "urgent"),
    ("I am having shrotness of breath", "urgent"),
    ("Can I take minoxidil while pregnant?", "care_first"),
    ("What products are good for kids' immunity?", "care_first"),
])
def test_general_chat_shares_safety_routing(message, expected, monkeypatch):
    quota = Mock(side_effect=AssertionError("Safety response must stay local"))
    monkeypatch.setattr(main, "provider_call_allowed", quota)
    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    result = client.post("/api/v1/chat/general", json={"message": message, "share_with_groq": True}).json()
    assert result["status"] == expected
    assert result["products"] == []
    assert result["ingredients"] == []
    assert result["provider"] is None
    quota.assert_not_called()


def test_general_chat_checks_user_history_for_care_first(provider):
    requests = provider()
    result = client.post("/api/v1/chat/general", json={
        "message": "Can I use it?",
        "history": [{"role": "user", "content": "I am pregnant."}],
        "share_with_groq": True,
    }).json()
    assert result["status"] == "care_first"
    assert not requests


def test_general_chat_requires_explicit_sharing(provider):
    requests = provider()
    result = client.post("/api/v1/chat/general", json={"message": "What is biotin?"}).json()
    assert result["status"] == "consent_required"
    assert not requests


def test_general_chat_reports_missing_key_before_quota(monkeypatch):
    quota = Mock(side_effect=AssertionError("Missing credentials must not use quota"))
    monkeypatch.setattr(main, "provider_call_allowed", quota)
    result = client.post("/api/v1/chat/general", json={
        "message": "What is biotin?", "share_with_groq": True,
    }).json()
    assert result["status"] == "provider_unavailable"
    assert result["provider"] is None
    quota.assert_not_called()


def test_general_chat_reports_provider_error(provider):
    requests = provider(503)
    result = client.post("/api/v1/chat/general", json={
        "message": "What is biotin?", "share_with_groq": True,
    }).json()
    assert result["status"] == "provider_unavailable"
    assert result["provider"] is None
    assert len(requests) == 1


def test_general_chat_shares_latest_history_and_nutrition(provider):
    requests = provider()
    history = [{"role": "user" if n % 2 == 0 else "assistant", "content": f"Message {n}"} for n in range(6)]
    response = client.post("/api/v1/chat/general", json={
        "message": "What is the serving size of Biotin Hair Gummies (30N)?",
        "history": history,
        "language": "Hindi",
        "share_with_groq": True,
    })
    assert response.status_code == 200
    data = response.json()
    assert (data["status"], data["provider"], data["response"]) == ("success", "groq", "Example reply")
    assert len(requests) == 1
    messages = requests[0]["messages"]
    assert messages[1:-1] == history[-4:]
    facts = json.loads(messages[-1]["content"])
    assert facts["language"] == "Hindi"
    product = data["products"][0]
    assert product["name"] == "Biotin Hair Gummies (30N)"
    assert product["nutritional_facts"] == {"serving_size": "1 gummy (approximately 3.7 g)"}
    assert facts["listing_context"][0]["nutritional_facts"] == product["nutritional_facts"]
    assert facts["listing_context"][0]["source_url"] == product["source_url"]


def test_dandruff_search_uses_pertinent_titles_and_ingredient_names(provider):
    provider()
    result = client.post("/api/v1/chat/general", json={
        "message": "What products help with dandruff?", "share_with_groq": True,
    }).json()
    assert result["products"]
    assert all("dandruff" in item["name"].casefold() for item in result["products"])
    ingredient_names = {item["name"] for item in result["ingredients"]}
    assert "Ketoconazole" in ingredient_names
    assert "Hyaluronic Acid" not in ingredient_names


def test_hybrid_ranking_stays_within_relevant_listing_urls(monkeypatch):
    items = [
        {"id": "1", "name": "Dandruff Shampoo A", "brand": "Brand", "review_status": "source_observed", "source_url": "first"},
        {"id": "2", "name": "Dandruff Shampoo B", "brand": "Brand", "review_status": "approved", "source_url": "second"},
        {"id": "3", "name": "Dandruff Shampoo C", "brand": "Brand", "review_status": "retired", "source_url": "retired"},
        {"id": "4", "name": "Magnesium Gummies", "brand": "Brand", "review_status": "source_observed", "source_url": "unrelated"},
    ]
    monkeypatch.setenv("DATABASE_URL", "local-test")
    db_rank = Mock(return_value=["second", "first"])
    monkeypatch.setattr(retrieval, "rank_listing_urls", db_rank)
    products = retrieval.rag_service.search_products("dandruff shampoo", items, limit=2, hybrid=True)
    assert [product["id"] for product in products] == ["2", "1"]
    assert db_rank.call_args.args[3] == ["first", "second"]


@pytest.mark.parametrize("message", [" ", "x", "a" * 1501])
def test_general_chat_validates_message_length(message):
    assert client.post("/api/v1/chat/general", json={"message": message}).status_code == 422


def test_general_chat_rejects_excess_history():
    history = [{"role": "user", "content": "Previous question"}] * 11
    response = client.post("/api/v1/chat/general", json={"message": "Biotin?", "history": history})
    assert response.status_code == 422


def test_product_search_respects_limit():
    response = client.get("/api/v1/products/search/shampoo", params={"limit": 3})
    assert response.status_code == 200
    result = response.json()
    assert result["total"] == len(result["products"]) == 3
    assert all("shampoo" in item["name"].casefold() for item in result["products"])
