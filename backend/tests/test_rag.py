"""Unit tests for the Semantic RAG service and its integration with Allergen Safety."""
import pytest
from app.models import MenuItem, UserPreference
from app.services.rag_service import rag_service, DRINK_KNOWLEDGE_BASE
from app.services import recommendation


@pytest.fixture
def sample_menu() -> list[MenuItem]:
    items = []
    for idx, d in enumerate(DRINK_KNOWLEDGE_BASE):
        item = MenuItem(
            id=idx + 1,
            name=d["name"],
            category=d["category"],
            price=d["price"],
            description=d.get("tasting_notes", ""),
            ingredients=d["ingredients"],
            available=True,
        )
        items.append(item)
    return items


def test_knowledge_base_covers_all_15_drinks():
    assert len(DRINK_KNOWLEDGE_BASE) == 15
    names = {d["name"] for d in DRINK_KNOWLEDGE_BASE}
    expected_categories = {"cafe", "tea", "fruit juice"}
    categories = {d["category"] for d in DRINK_KNOWLEDGE_BASE}
    assert categories == expected_categories
    assert "Classic Espresso" in names
    assert "Caramel Latte" in names
    assert "Chamomile Honey Tea" in names
    assert "Berry Banana Blast" in names


def test_semantic_search_cold_rainy_mood(sample_menu):
    query = "Hôm nay trời mưa se lạnh, tôi mệt mỏi thèm món gì béo ngậy ngọt ngào làm tỉnh táo"
    results = rag_service.search_drinks(query=query, safe_candidates=sample_menu, limit=3)
    assert len(results) == 3
    top_names = [r["name"] for r in results]
    # Caramel Latte or Hazelnut Cappuccino or Matcha Latte should be recommended
    assert any(name in top_names for name in ["Caramel Latte", "Hazelnut Cappuccino", "Matcha Latte"])
    for r in results:
        assert "match_score" in r
        assert "reason" in r
        assert "tasting_notes" in r
        assert r["match_score"] > 0


def test_semantic_search_with_strict_allergy_guardrail(sample_menu):
    # Customer asks for rich creamy drink, but is severely allergic to DAIRY / MILK
    allergies = ["dairy", "milk"]
    safe_candidates = recommendation.filter_candidates(sample_menu, allergies)

    # Verify Caramel Latte, Hazelnut Cappuccino, Classic Milk Tea, Mango Smoothie are removed
    safe_names = {item.name for item in safe_candidates}
    assert "Caramel Latte" not in safe_names
    assert "Hazelnut Cappuccino" not in safe_names
    assert "Classic Milk Tea" not in safe_names

    # Run RAG semantic search on safe candidates only
    query = "món ngọt ngào béo thơm sảng khoái"
    results = rag_service.search_drinks(query=query, safe_candidates=safe_candidates, limit=3)

    result_names = [r["name"] for r in results]
    # Absolutely NO dairy drink should appear
    assert "Caramel Latte" not in result_names
    assert "Classic Milk Tea" not in result_names
    # Oat Milk Mocha (oat milk is dairy free) or Berry Banana Blast (almond milk) are safe
    assert any(name in result_names for name in ["Oat Milk Mocha", "Berry Banana Blast", "Iced Peach Oolong"])


def test_semantic_search_gym_workout(sample_menu):
    query = "vừa tập gym xong cần món bổ sung năng lượng hoa quả chất chống oxy hóa"
    results = rag_service.search_drinks(query=query, safe_candidates=sample_menu, limit=2)
    top_names = [r["name"] for r in results]
    assert any(name in top_names for name in ["Berry Banana Blast", "Fresh Orange Juice", "Green Detox Juice"])


def test_barista_knowledge_retrieval():
    info = rag_service.get_barista_knowledge("Cold Brew hoặc cách pha Espresso hạt Arabica")
    assert info is not None
    assert "Espresso" in info or "Arabica" in info
