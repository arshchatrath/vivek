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
    ("Hair  loss", "hair-loss"),
    ("hair‑loss", "hair-loss"),
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
    result = client.post("/api/v1/concerns", json={"concern": "How do I prevent cavities?"}).json()
    assert result["ingredients"][0]["name"] == "Fluoride"
    assert result["ingredients"][0]["products"] == []
