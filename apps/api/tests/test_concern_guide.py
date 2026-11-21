import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.main import app


client = TestClient(app)


@pytest.mark.parametrize(("concern", "topic"), [
    ("My scalp is itchy and has white flakes.", "scalp-flakes"),
    ("I keep getting pimples and blackheads.", "acne"),
    ("My hair has been thinning over several months.", "hair-loss"),
    ("hairloss", "hair-loss"),
    ("hairlos", "hair-loss"),
    ("I have haiir loss", "hair-loss"),
    ("Hair  loss", "hair-loss"),
    ("hair‑loss", "hair-loss"),
    ("I have dandruf", "scalp-flakes"),
    ("dandurff", "scalp-flakes"),
    ("acnee", "acne"),
    ("constripation", "constipation"),
    ("Mere baal gir rahe hain", "hair-loss"),
    ("Mere baal nahate waqt nikalte hain", "hair-loss"),
    ("Mera chehra dhone ke baad khinchta hai", "dry-skin"),
    ("मेरे बाल गिर रहे हैं", "hair-loss"),
    ("My skin feels dry and tight after washing.", "dry-skin"),
    ("I have rough bumps on my arms.", "rough-bumps"),
    ("What should I look for in a sunscreen?", "sun-protection"),
    ("My hair feels dry and frizzy.", "dry-hair"),
    ("What can help with body odor?", "body-odor"),
    ("I've been having trouble sleeping.", "sleep"),
    ("What should I look for in toothpaste to prevent cavities?", "cavity-prevention"),
    ("I have dark spots on my face", "dark-spots"),
    ("I have been constipated lately.", "constipation"),
])
def test_examples_retrieve_the_intended_sourced_guide(concern, topic):
    result = client.post("/api/v1/concerns", json={"concern": concern}).json()
    assert result["status"] == "guidance"
    assert result["topic"]["id"] == topic
    assert result["guidance"]
    assert all(card["source"]["url"].startswith("https://") for card in result["guidance"])


@pytest.mark.parametrize(("concern", "expected"), [
    ("I have scalp flakes and my lips are swollen", "urgent"),
    ("Can my 8-year-old use something for dandruff?", "care_first"),
    ("Pregnant and getting acne", "care_first"),
    ("Constipation with blood in my stool", "care_first"),
    ("I have an unexplained tremor", "outside_coverage"),
    ("I have acne and hair loss", "clarify"),
    ("I have acne and hairlos", "clarify"),
    ("I get brown discoloration after pimples heal", "clarify"),
    ("I have chset pain", "urgent"),
    ("I can't brethe", "urgent"),
    ("I have an ache", "outside_coverage"),
    ("Can I combine two acne treatments?", "care_first"),
    ("My hairloss was sudden", "care_first"),
])
def test_sensitive_or_unclear_cases_do_not_show_products(concern, expected):
    result = client.post("/api/v1/concerns", json={"concern": concern}).json()
    assert result["status"] == expected
    assert not result.get("ingredients")


def test_ingredient_matching_respects_form_and_source():
    result = client.post("/api/v1/concerns", json={"concern": "I have dandruff"}).json()
    ketoconazole = next(item for item in result["ingredients"] if item["name"] == "Ketoconazole")
    assert {item["brand"] for item in ketoconazole["products"]} == {"Be Bodywise", "Man Matters"}
    assert all("shampoo" in item["name"].lower() and "ketoconazole" in item["name"].lower()
               for item in ketoconazole["products"])
    for listing in ketoconazole["products"]:
        stored = client.get(f"/api/v1/products/{listing['id']}").json()
        for field in ("source_url", "image_url", "price", "currency", "captured_at"):
            assert listing[field] == stored[field]
    result = client.post("/api/v1/concerns", json={"concern": "How do I prevent cavities?"}).json()
    assert result["ingredients"][0]["name"] == "Fluoride"
    assert result["ingredients"][0]["products"] == []


def test_retrieved_topic_uses_saved_sources_without_groq(monkeypatch):
    import app.main as api
    import app.concerns as concerns

    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setattr(concerns, "search_topics", lambda _: ("hair-loss", []))

    async def unexpected_groq_call(*_):
        pytest.fail("A new concern should not use Groq follow-up quota")

    monkeypatch.setattr(api, "find_followup_passages", unexpected_groq_call)
    response = client.post("/api/v1/concerns", json={
        "concern": "My brush is full of strands",
        "topic": "acne",
        "share_followup": True,
    })
    assert response.status_code == 200
    assert response.json()["topic"]["id"] == "hair-loss"


def test_uncertain_retrieval_asks_before_showing_guidance(monkeypatch):
    import app.concerns as concerns

    monkeypatch.setattr(concerns, "search_topics", lambda _: (None, ["dry-skin", "rough-bumps"]))
    response = client.post("/api/v1/concerns", json={"concern": "My skin feels odd"})
    result = response.json()
    assert result["status"] == "clarify"
    assert {choice["id"] for choice in result["topics"]} == {"dry-skin", "rough-bumps"}
    assert not result.get("guidance") and not result.get("ingredients")


@pytest.mark.parametrize(("question", "topic"), [
    ("Every time I wash my hair, a lot comes out", "hair-loss"),
    ("I can spend half the night in bed without getting any rest", "sleep"),
    ("There is a ringing in my ears", None),
])
def test_hybrid_retrieval_with_seeded_postgres(question, topic):
    from app.concerns import normalize_concern, related_topics

    if not os.getenv("DATABASE_URL"):
        pytest.skip("Seed the local PostgreSQL database to test vector retrieval")
    assert not related_topics(normalize_concern(question))
    result = client.post("/api/v1/concerns", json={"concern": question}).json()
    if topic:
        assert result["status"] == "guidance"
        assert result["topic"]["id"] == topic
        assert result["retrieval"] == "postgres_guidance"
        assert result["guidance"]
    else:
        assert result["status"] == "outside_coverage"
        assert not result.get("ingredients")


@pytest.mark.parametrize(("answer", "status", "topic"), [
    ({"action": "match", "topic": "scalp-flakes"}, "guidance", "scalp-flakes"),
    ({"action": "match", "topic": "unreviewed"}, "outside_coverage", None),
    ({"action": "match", "topic": "scalp-flakes", "answer": "extra text"}, "outside_coverage", None),
    ({"action": "clarify", "topic": None}, "clarify", None),
    ({"action": "outside_coverage", "topic": None}, "outside_coverage", None),
    ({"action": "care_first", "topic": None}, "care_first", None),
    ({"action": "urgent", "topic": None}, "urgent", None),
    (None, "outside_coverage", None),
])
def test_groq_routing_requires_opt_in_and_uses_saved_results(monkeypatch, answer, status, topic):
    import app.main as api
    import app.concerns as concerns

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setattr(concerns, "search_topics", lambda _: (None, []))
    calls = []
    question = "whyt skayls thru mi hayer"

    async def groq_reply(system, payload):
        calls.append(payload)
        return answer

    monkeypatch.setattr(api, "groq_json", groq_reply)
    first = client.post("/api/v1/concerns", json={"concern": question}).json()
    assert first["status"] == "outside_coverage" and first["can_retry_with_groq"]
    assert not calls
    result = client.post("/api/v1/concerns", json={"concern": question, "share_routing": True}).json()
    assert len(calls) == 1 and calls[0]["question"] == question
    assert all(set(details) == {"id", "title"} for details in calls[0]["topics"])
    assert result["status"] == status and (result.get("topic") or {}).get("id") == topic
    assert not result.get("can_retry_with_groq")
    if topic:
        assert result["guidance"] and all(card["source"]["url"].startswith("https://") for card in result["guidance"])
    else:
        assert not result.get("guidance") and not result.get("ingredients")


@pytest.mark.parametrize(("question", "status"), [
    ("I have chset pain", "urgent"),
    ("I have acne and hairlos", "clarify"),
    ("hairlos", "guidance"),
])
def test_groq_routing_skips_safety_results_and_known_topics(monkeypatch, question, status):
    import app.main as api

    async def unexpected_call(*_):
        pytest.fail("Groq should not be called for a resolved or higher-priority result")

    monkeypatch.setattr(api, "route_unclear_concern", unexpected_call)
    reply = client.post("/api/v1/concerns", json={"concern": question, "share_routing": True}).json()
    assert reply["status"] == status and not reply.get("can_retry_with_groq")


def test_groq_routing_respects_unavailable_quota(monkeypatch):
    import app.main as api

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    monkeypatch.setenv("DATABASE_URL", "")
    monkeypatch.setattr(api, "provider_call_allowed", lambda _: False)

    def unexpected_client(*args, **kwargs):
        pytest.fail("The Groq client should not be opened without quota")

    monkeypatch.setattr(api.httpx, "AsyncClient", unexpected_client)
    result = client.post("/api/v1/concerns", json={
        "concern": "whyt skayls thru mi hayer",
        "share_routing": True,
    }).json()
    assert result["status"] == "outside_coverage" and result["topics"]
    assert "unavailable" in result["message"]
