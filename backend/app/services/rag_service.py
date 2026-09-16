"""Semantic RAG (Retrieval-Augmented Generation) Service for DrinkBot.

Provides local, free, zero-cost semantic search over rich drink flavor profiles,
tasting notes, mood/occasion contexts, and barista preparation knowledge.
Integrates with SentenceTransformer (all-MiniLM-L6-v2) on CPU with automatic
lightweight TF-IDF fallback if neural dependencies are unavailable.
"""
from __future__ import annotations

import logging
import math
import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models import MenuItem, UserPreference

logger = logging.getLogger(__name__)

# Rich semantic knowledge base for all 15 menu items
DRINK_KNOWLEDGE_BASE: list[dict] = [
    # --- Cafe (5) ---
    {
        "name": "Classic Espresso",
        "category": "cafe",
        "price": 2.50,
        "ingredients": ["espresso"],
        "caffeine": "high",
        "temperature": "hot",
        "tasting_notes": "Vị đắng đậm đà nguyên bản, lớp crema vàng óng sánh mịn, hậu vị khói thơm nồng mùi hạt rang mộc nguyên chất.",
        "mood_occasion": "Buổi sáng sớm cần tỉnh táo tức thì, kích thích sự tập trung cao độ khi làm việc, dân sành cà phê mộc đậm vị.",
        "best_for": "Người cần tỉnh ngủ cấp tốc, làm việc ban ngày, thích vị đắng mộc không đường không sữa.",
        "barista_notes": "Chiết xuất từ 100% hạt Robusta Đắk Lắk kết hợp Arabica Cầu Đất, áp suất 9 bar chuẩn Ý trong 25-30 giây.",
        "tags": ["đắng", "đậm đà", "tỉnh táo", "mạnh", "tập trung", "sáng sớm", "không đường", "không sữa", "espresso", "buồn ngủ"],
    },
    {
        "name": "Caramel Latte",
        "category": "cafe",
        "price": 4.50,
        "ingredients": ["espresso", "milk", "caramel syrup"],
        "caffeine": "medium",
        "temperature": "hot",
        "tasting_notes": "Vị béo ngậy ngọt ngào của sốt caramel bơ sữa, hòa quyện êm dịu cùng shot espresso và sữa tươi thanh trùng đánh bọt mềm mượt.",
        "mood_occasion": "Trời mưa se lạnh, buổi chiều mệt mỏi cần nạp năng lượng đường ngọt ngào, xoa dịu tâm trạng sau giờ làm việc căng thẳng.",
        "best_for": "Người hảo ngọt, thích vị béo kem sữa, người mới tập uống cà phê không chịu được vị đắng gắt.",
        "barista_notes": "Sốt caramel thủ công nấu chậm cùng bơ tươi, sữa tươi thanh trùng đánh bọt microfoam mịn màng tạo hình latte art.",
        "tags": ["ngọt", "béo ngậy", "caramel", "sữa", "trời lạnh", "trời mưa", "se lạnh", "ấm áp", "mệt mỏi", "năng lượng", "ngọt ngào"],
    },
    {
        "name": "Hazelnut Cappuccino",
        "category": "cafe",
        "price": 4.75,
        "ingredients": ["espresso", "milk", "hazelnut syrup"],
        "caffeine": "medium",
        "temperature": "hot",
        "tasting_notes": "Hương hạt phỉ (hazelnut) bùi béo nồng nàn, lớp bọt sữa dày xốp rắc bột quế nhẹ, vị cà phê đầm ấm sang trọng.",
        "mood_occasion": "Những ngày thời tiết mát mẻ hoặc se lạnh, trò chuyện thư giãn cùng bạn bè, đọc sách bên khung cửa sổ quán cafe.",
        "best_for": "Người yêu thích hương vị các loại hạt bùi béo, thích lớp bọt sữa bồng bềnh êm ái.",
        "barista_notes": "Tỷ lệ chuẩn 1/3 espresso, 1/3 sữa nóng và 1/3 bọt sữa bông xốp mềm mại, hòa quyện syrup hạt phỉ rang thơm.",
        "tags": ["hạt phỉ", "hazelnut", "bùi béo", "bọt sữa", "ấm", "thư giãn", "trò chuyện", "thơm béo", "cappuccino"],
    },
    {
        "name": "Iced Americano",
        "category": "cafe",
        "price": 3.00,
        "ingredients": ["espresso", "water", "ice"],
        "caffeine": "high",
        "temperature": "iced",
        "tasting_notes": "Thanh nhẹ, mát lạnh sảng khoái, vị đắng thanh sạch sẽ, không ngọt không béo, hậu vị thơm mát lâu dài.",
        "mood_occasion": "Ngày hè oi bức, sau bữa ăn trưa no nhiều dầu mỡ cần giải ngấy, người đang ăn kiêng giảm cân (keto, low-carb) cần tỉnh ngủ tức thì.",
        "best_for": "Dân văn phòng sau giờ trưa, người giảm cân, người thích cà phê đen lạnh sảng khoái.",
        "barista_notes": "Double shot espresso rót trực tiếp lên nước đá tinh khiết giúp giữ trọn vẹn lớp dầu hương thơm mà không bị khét.",
        "tags": ["mát lạnh", "giải nhiệt", "đắng thanh", "giảm cân", "ăn kiêng", "không calo", "giải ngấy", "mùa hè", "tỉnh táo", "sau bữa trưa"],
    },
    {
        "name": "Oat Milk Mocha",
        "category": "cafe",
        "price": 5.00,
        "ingredients": ["espresso", "oat milk", "cocoa", "sugar"],
        "caffeine": "medium",
        "temperature": "hot",
        "tasting_notes": "Đậm đà vị socola ca cao nguyên chất hòa cùng sữa yến mạch béo thơm tự nhiên, vị cà phê ngọt dịu không gây đầy bụng.",
        "mood_occasion": "Người ăn chay (vegan), người không dung nạp lactose, thích thức uống socola ấm áp dễ chịu cho ngày mưa gió.",
        "best_for": "Dị ứng sữa bò (dairy-free), thuần chay, thích socola ngọt béo mà không lo khó tiêu.",
        "barista_notes": "Bột ca cao nguyên chất 70% đánh tan cùng sữa yến mạch barista chuyên dụng, tạo độ sánh mịn màng không chứa sữa động vật.",
        "tags": ["sữa yến mạch", "oat milk", "thuần chay", "vegan", "dairy-free", "không sữa bò", "socola", "ca cao", "béo thơm", "ấm bụng"],
    },
    # --- Tea (5) ---
    {
        "name": "Jasmine Green Tea",
        "category": "tea",
        "price": 3.00,
        "ingredients": ["green tea", "jasmine"],
        "caffeine": "low",
        "temperature": "hot",
        "tasting_notes": "Thanh tao thanh khiết, thoang thoảng hương hoa nhài tự nhiên, vị chát nhẹ tinh tế đầu lưỡi và ngọt hậu lắng đọng cuống họng.",
        "mood_occasion": "Thư giãn tâm trí, giải tỏa stress sau giờ làm việc, thanh lọc cơ thể sau bữa ăn no, thích không gian yên tĩnh thiền tịnh.",
        "best_for": "Người thích trà truyền thống thanh nhẹ, người cần xoa dịu căng thẳng, thích mùi hương hoa tự nhiên.",
        "barista_notes": "Búp trà xanh non ướp hoa nhài tươi tự nhiên, ủ nước ở 80°C đúng 3 phút để giữ trọn chất chống oxy hóa EGCG.",
        "tags": ["hoa nhài", "thanh tao", "thanh lọc", "detox", "thư giãn", "stress", "chát nhẹ", "ngọt hậu", "thanh mát", "ít caffeine"],
    },
    {
        "name": "Classic Milk Tea",
        "category": "tea",
        "price": 3.75,
        "ingredients": ["black tea", "milk", "sugar"],
        "caffeine": "medium",
        "temperature": "iced",
        "tasting_notes": "Vị trà đen truyền thống đậm đà hòa quyện cùng sữa thơm béo ngọt ngào, cân bằng hoàn hảo chuẩn vị trà sữa tuổi thơ.",
        "mood_occasion": "Thèm đồ ngọt giải tỏa áp lực, tụ tập bạn bè trò chuyện, bữa xế chiều cần món ngon miệng vui vẻ sảng khoái.",
        "best_for": "Tín đồ trà sữa, thích vị ngọt thơm béo đậm đà, giải khát sau giờ học và làm việc.",
        "barista_notes": "Trà đen Ceylon thượng hạng ủ đậm đà chiết xuất trọn vị chát thơm, hòa cùng sữa đặc và sữa tươi tiệt trùng béo ngậy.",
        "tags": ["trà sữa", "ngọt ngào", "béo ngậy", "trà đen", "truyền thống", "vui vẻ", "bữa xế", "giải tỏa căng thẳng", "thèm ngọt"],
    },
    {
        "name": "Iced Peach Oolong",
        "category": "tea",
        "price": 4.25,
        "ingredients": ["oolong tea", "peach syrup", "ice"],
        "caffeine": "low",
        "temperature": "iced",
        "tasting_notes": "Hương trà ô long nướng thơm lừng quyện cùng vị đào giòn ngọt ngào tươi mát, uống vào giải nhiệt tức thì, mát tận tâm can.",
        "mood_occasion": "Buổi trưa hè nắng nóng, đi dạo phố, người thích trà trái cây thơm ngọt dễ uống, sảng khoái giải khát.",
        "best_for": "Người thích vị trái cây ngọt ngào thanh mát, muốn giải nhiệt mùa hè mà không quá ngọt gắt.",
        "barista_notes": "Trà ô long cao sơn nướng nhẹ ủ lạnh, kết hợp sốt đào tươi vàng ươm và lát đào giòn ngọt thơm phức.",
        "tags": ["đào", "ô long", "trà trái cây", "thơm lừng", "mát lạnh", "mùa hè", "giải nhiệt", "sảng khoái", "ngọt mát", "nắng nóng"],
    },
    {
        "name": "Chamomile Honey Tea",
        "category": "tea",
        "price": 3.25,
        "ingredients": ["chamomile", "honey"],
        "caffeine": "none",
        "temperature": "hot",
        "tasting_notes": "Hương hoa cúc La Mã dịu êm, mật ong hoa rừng ngọt thanh nhẹ nhàng, ấm áp dịu dàng, xua tan mọi mỏi mệt.",
        "mood_occasion": "Buổi tối trước khi đi ngủ, người mất ngủ khó vào giấc, người bị đau họng cảm lạnh, tuyệt đối không gây mất ngủ (0mg caffeine).",
        "best_for": "Người mất ngủ, đau họng, nhạy cảm với caffeine, người cần thư giãn tĩnh tâm ban đêm.",
        "barista_notes": "Hoa cúc La Mã sấy khô nguyên bông nhập khẩu, hòa cùng 1 thìa mật ong hoa nhãn nguyên chất khi nước đạt 75°C.",
        "tags": ["hoa cúc", "mật ong", "không caffeine", "ngủ ngon", "mất ngủ", "buổi tối", "đau họng", "ấm áp", "thư giãn", "dịu êm"],
    },
    {
        "name": "Matcha Latte",
        "category": "tea",
        "price": 4.95,
        "ingredients": ["matcha", "milk", "sugar"],
        "caffeine": "medium",
        "temperature": "hot",
        "tasting_notes": "Vị umami đặc trưng của trà xanh Nhật Bản, bùi bùi, béo ngậy mềm mại của sữa tươi, hậu vị thanh mát kéo dài.",
        "mood_occasion": "Cần tỉnh táo êm dịu kéo dài (không bị tim đập chân run như cà phê nhờ L-theanine), tốt cho sức khỏe và đẹp da.",
        "best_for": "Fan matcha, người muốn tỉnh táo nhẹ nhàng không say cafein, người quan tâm đến chất chống oxy hóa.",
        "barista_notes": "Bột matcha ceremonial grade từ Uji Kyoto, đánh tan bằng chổi tre Chasen truyền thống tạo lớp bọt xanh ngọc bích mịn mượt.",
        "tags": ["matcha", "trà xanh", "nhật bản", "béo ngậy", "umami", "tỉnh táo êm dịu", "không say cà phê", "chống oxy hóa", "đẹp da"],
    },
    # --- Fruit juice (5) ---
    {
        "name": "Fresh Orange Juice",
        "category": "fruit juice",
        "price": 4.00,
        "ingredients": ["orange"],
        "caffeine": "none",
        "temperature": "chilled",
        "tasting_notes": "Chua ngọt tự nhiên nguyên chất 100%, mọng nước ngập tràn tép cam tươi, thơm ngát tinh dầu cam tự nhiên giàu sức sống.",
        "mood_occasion": "Bữa sáng bổ sung vitamin C, giải cảm, tăng cường hệ miễn dịch, nạp lại năng lượng sau khi tập thể dục mệt mỏi.",
        "best_for": "Người cần bổ sung vitamin C, phục hồi sức khỏe, trẻ em, người thích nước ép tươi 100% tự nhiên.",
        "barista_notes": "Vắt trực tiếp từ cam sành tươi mọng nước vừa chín tới, không pha thêm nước, không thêm đường bảo quản.",
        "tags": ["cam", "vitamin c", "tươi mới", "chua ngọt", "nguyên chất", "giải cảm", "tăng đề kháng", "buổi sáng", "năng lượng"],
    },
    {
        "name": "Watermelon Cooler",
        "category": "fruit juice",
        "price": 4.50,
        "ingredients": ["watermelon", "lime", "ice"],
        "caffeine": "none",
        "temperature": "iced",
        "tasting_notes": "Vị ngọt thanh mát khiết của dưa hấu tươi mọng nước, điểm xuyết chút chua nhẹ sảng khoái của chanh tươi và đá tuyết mát rượi.",
        "mood_occasion": "Trưa hè nắng gắt oi bức, sau khi chơi thể thao ra nhiều mồ hôi, giải khát tức thì và cấp nước cấp tốc.",
        "best_for": "Người đang khát nước, nóng trong người, thích nước ép thanh mát ít calo.",
        "barista_notes": "Dưa hấu đỏ ngọt lịm ép lạnh, thêm vài giọt cốt chanh tươi để tôn lên vị ngọt thanh tự nhiên của trái cây.",
        "tags": ["dưa hấu", "mát rượi", "chanh", "giải nhiệt", "mùa hè", "khát nước", "thể thao", "ngọt mát", "cấp nước", "nắng gắt"],
    },
    {
        "name": "Mango Smoothie",
        "category": "fruit juice",
        "price": 5.50,
        "ingredients": ["mango", "yogurt", "honey", "ice"],
        "caffeine": "none",
        "temperature": "blended",
        "tasting_notes": "Chua ngọt đậm đà, sánh mịn như kem, thơm nức mũi hương xoài chín cây quyện vị chua dịu béo ngậy của sữa chua và mật ong.",
        "mood_occasion": "Bữa xế chiều đói bụng cần món ngọt no bụng, giải nhiệt ngày hè, hỗ trợ tiêu hóa với men vi sinh probiotic.",
        "best_for": "Người thích đồ uống sinh tố sánh đặc, ngọt ngào no lâu, tốt cho hệ tiêu hóa đường ruột.",
        "barista_notes": "Xoài cát Hòa Lộc chín mọng xay nhuyễn cùng sữa chua lên men tự nhiên và mật ong hoa rừng nguyên chất.",
        "tags": ["xoài", "sinh tố", "sữa chua", "sánh mịn", "no bụng", "bữa xế", "tiêu hóa", "chua ngọt", "mật ong", "mùa hè"],
    },
    {
        "name": "Berry Banana Blast",
        "category": "fruit juice",
        "price": 5.75,
        "ingredients": ["strawberry", "blueberry", "banana", "almond milk"],
        "caffeine": "none",
        "temperature": "blended",
        "tasting_notes": "Vị chua ngọt rực rỡ của dâu tây và việt quất hòa với độ ngọt bùi dẻo quánh của chuối chín và sữa hạnh nhân thơm lừng.",
        "mood_occasion": "Bữa sáng dinh dưỡng cho người tập gym/yoga, trước hoặc sau buổi workout, bổ sung kali và chất chống oxy hóa, thuần chay.",
        "best_for": "Dân tập thể thao (fitness/gym), người ăn thuần chay vegan, dị ứng sữa bò (dairy-free), nạp năng lượng lành mạnh.",
        "barista_notes": "Quả mọng đông lạnh cấp tốc giữ nguyên dưỡng chất, xay mịn cùng chuối già chín và sữa hạnh nhân không đường.",
        "tags": ["dâu tây", "việt quất", "chuối", "sữa hạnh nhân", "almond milk", "tập gym", "thể thao", "fitness", "thuần chay", "vegan", "không sữa bò"],
    },
    {
        "name": "Green Detox Juice",
        "category": "fruit juice",
        "price": 5.25,
        "ingredients": ["apple", "cucumber", "celery", "ginger"],
        "caffeine": "none",
        "temperature": "chilled",
        "tasting_notes": "Thanh mát tươi mới giòn tan, vị chua ngọt nhẹ của táo xanh, tươi mát của dưa leo cần tây và chút ấm áp the the của gừng tươi.",
        "mood_occasion": "Cần thanh lọc cơ thể (detox), sau những ngày tiệc tùng ăn nhiều dầu mỡ đồ ngọt, làm đẹp da và hỗ trợ giảm cân.",
        "best_for": "Người ăn kiêng giảm cân, eat clean, detox thanh lọc cơ thể, người thích nước ép xanh lành mạnh không đường.",
        "barista_notes": "Ép chậm lạnh (Cold-pressed) không sinh nhiệt giữ trọn 98% enzyme sống, vitamin và khoáng chất của rau củ tươi.",
        "tags": ["detox", "thanh lọc", "táo xanh", "cần tây", "dưa leo", "gừng", "giảm cân", "eat clean", "không đường", "đẹp da", "sau tiệc tùng"],
    },
]


def _build_searchable_doc(item: dict) -> str:
    """Combines all semantic facets of a drink into a rich document for embedding."""
    ingredients_str = ", ".join(item.get("ingredients", []))
    tags_str = ", ".join(item.get("tags", []))
    return (
        f"Tên món: {item['name']}. "
        f"Phân loại: {item['category']}. "
        f"Giá: {item['price']:.2f}$. "
        f"Nguyên liệu: {ingredients_str}. "
        f"Hương vị: {item.get('tasting_notes', '')} "
        f"Tâm trạng & Ngữ cảnh phù hợp: {item.get('mood_occasion', '')} "
        f"Phù hợp cho: {item.get('best_for', '')} "
        f"Bí quyết pha chế Barista: {item.get('barista_notes', '')} "
        f"Từ khóa: {tags_str}."
    )


class LocalSemanticEngine:
    """Local, offline, zero-cost semantic embedding & search engine.
    Uses SentenceTransformer (all-MiniLM-L6-v2) when available, with
    an automatic TF-IDF/n-gram cosine similarity fallback.
    """

    def __init__(self) -> None:
        self._model = None
        self._embeddings: list[list[float]] | None = None
        self._docs = [_build_searchable_doc(d) for d in DRINK_KNOWLEDGE_BASE]
        self._init_engine()

    def _init_engine(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer  # type: ignore

            logger.info("Initializing Local SentenceTransformer (all-MiniLM-L6-v2)...")
            self._model = SentenceTransformer("all-MiniLM-L6-v2")
            raw_embeds = self._model.encode(self._docs, normalize_embeddings=True)
            self._embeddings = [list(vec) for vec in raw_embeds]
            logger.info("Successfully encoded %d menu drinks using SentenceTransformer.", len(self._docs))
        except Exception as err:
            logger.info(
                "SentenceTransformer not loaded (%s). Using built-in TF-IDF Vectorizer.", err
            )
            self._model = None
            self._embeddings = None

    def _tokenize(self, text: str) -> list[str]:
        words = re.findall(r"[\w\u00C0-\u1EF9]+", text.lower())
        tokens: list[str] = []
        for w in words:
            if len(w) > 1:
                tokens.append(w)
        # Add bigrams for context (e.g. 'se lạnh', 'béo ngậy', 'không sữa')
        for i in range(len(words) - 1):
            tokens.append(f"{words[i]} {words[i+1]}")
        return tokens

    def _tfidf_similarity(self, query: str, doc: str) -> float:
        q_tokens = set(self._tokenize(query))
        d_tokens = self._tokenize(doc)
        if not q_tokens or not d_tokens:
            return 0.0

        d_counts: dict[str, int] = {}
        for t in d_tokens:
            d_counts[t] = d_counts.get(t, 0) + 1

        # Term overlap with sub-linear TF
        overlap_score = 0.0
        for token in q_tokens:
            if token in d_counts:
                # Bigrams give more weight than unigrams
                weight = 2.0 if " " in token else 1.0
                overlap_score += weight * (1.0 + math.log(d_counts[token]))

        # Normalization factor
        doc_len_factor = math.sqrt(len(d_tokens)) or 1.0
        query_len_factor = math.sqrt(len(q_tokens)) or 1.0
        normalized = overlap_score / (doc_len_factor * query_len_factor)
        return min(max(normalized * 1.5, 0.0), 1.0)

    def compute_similarity(self, query: str, drink_idx: int) -> float:
        """Calculate semantic similarity between a customer query and a drink profile."""
        if self._model is not None and self._embeddings is not None:
            try:
                import numpy as np  # type: ignore

                q_vec = self._model.encode([query], normalize_embeddings=True)[0]
                doc_vec = np.array(self._embeddings[drink_idx])
                sim = float(np.dot(q_vec, doc_vec))
                return max(0.0, min(1.0, sim))
            except Exception:
                pass
        # Fallback to TF-IDF semantic matching
        return self._tfidf_similarity(query, self._docs[drink_idx])


# Global singleton engine instance
_engine = LocalSemanticEngine()


class RAGService:
    """High-level RAG Service providing semantic search, recommendation ranking,
    and Barista knowledge retrieval for DrinkBot."""

    def __init__(self) -> None:
        self.knowledge_base = DRINK_KNOWLEDGE_BASE
        self.by_name = {d["name"].lower(): (idx, d) for idx, d in enumerate(self.knowledge_base)}

    def search_drinks(
        self,
        query: str,
        safe_candidates: list[MenuItem],
        prefs: UserPreference | None = None,
        limit: int = 3,
    ) -> list[dict]:
        """Rank safe candidate drinks by semantic similarity to customer's mood/taste query.
        
        CRITICAL: Only drinks present in `safe_candidates` (already filtered by Allergen
        Safety Guardrail in code) are evaluated. This preserves 100% allergen safety!
        """
        if not safe_candidates:
            return []

        safe_names = {item.name.lower(): item for item in safe_candidates}
        scored: list[tuple[float, MenuItem, dict]] = []

        for name_lower, item in safe_names.items():
            kb_entry = self.by_name.get(name_lower)
            if kb_entry is None:
                # Basic fallback if a new item is in DB but not yet in KB
                score = 0.3
                meta = {
                    "name": item.name,
                    "tasting_notes": item.description or "",
                    "mood_occasion": "Đồ uống thơm ngon phù hợp thưởng thức mỗi ngày.",
                    "barista_notes": "Pha chế theo công thức chuẩn quán.",
                }
            else:
                idx, meta = kb_entry
                if query and query.strip():
                    sim_score = _engine.compute_similarity(query, idx)
                else:
                    sim_score = 0.5

                # Preference booster bonus (+0.1 if user drink_type matches, +0.05 temperature match)
                bonus = 0.0
                if prefs:
                    if prefs.drink_types and item.category in prefs.drink_types:
                        bonus += 0.10
                    if prefs.temperature and prefs.temperature in meta.get("temperature", ""):
                        bonus += 0.05
                    if prefs.caffeine == "none" and meta.get("caffeine") == "none":
                        bonus += 0.05

                score = min(1.0, sim_score + bonus)

            scored.append((score, item, meta))

        # Sort descending by semantic score
        scored.sort(key=lambda x: x[0], reverse=True)
        top_picks = scored[:limit]

        results: list[dict] = []
        for score, item, meta in top_picks:
            results.append({
                "name": item.name,
                "price": float(item.price),
                "description": item.description,
                "category": item.category,
                "tasting_notes": meta.get("tasting_notes", ""),
                "mood_occasion": meta.get("mood_occasion", ""),
                "barista_notes": meta.get("barista_notes", ""),
                "match_score": round(score * 100, 1),
                "reason": (
                    f"Khớp {round(score * 100)}% với mong muốn của bạn: "
                    f"{meta.get('tasting_notes', '')} Phù hợp: {meta.get('mood_occasion', '')}"
                ),
            })

        return results

    def get_barista_knowledge(self, query: str) -> str | None:
        """Retrieve relevant preparation knowledge or store policy for FAQ queries."""
        q_lower = query.lower()
        for d in self.knowledge_base:
            if d["name"].lower() in q_lower or any(t in q_lower for t in d.get("tags", [])):
                return (
                    f"Ghi chú Barista về món {d['name']}: {d.get('barista_notes', '')} "
                    f"Hương vị chuẩn: {d.get('tasting_notes', '')}"
                )
        return None


# Global singleton instance
rag_service = RAGService()
