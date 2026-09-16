"""Centralized Model Training Data Management Service for DrinkBot.

Manages, versions, and tracks training datasets for:
1. SLM Fine-Tuning (Barista Dialogues in Gemma Chat Template format)
2. Domain RAG Embedding Retraining (Vietnamese F&B slang, nuances, and flavor pairs)

Supports Data Annotation, Trace-to-Dataset Curation, Dataset Versioning (v1.0, v1.1...),
and Data-to-Model Lineage tracking. Persisted in backend/data/datasets/training_datasets.json.
"""
from __future__ import annotations

import hashlib
import json
import logging
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "datasets"
DATASETS_FILE = DATA_DIR / "training_datasets.json"

DatasetType = Literal["slm_dialogues", "rag_slang_pairs"]


@dataclass
class SLMSample:
    id: str
    user_input: str
    model_output: str
    category: str = "general"
    verified: bool = True
    source_trace_id: str | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RAGPairSample:
    id: str
    query_slang: str
    target_drink_flavor: str
    label: float = 1.0  # 1.0 positive, -1.0 negative
    category: str = "general"
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


# Seed dialogues for SLM Gemma LoRA
INITIAL_SLM_SAMPLES: list[dict[str, Any]] = [
    {
        "id": "slm-001",
        "user_input": "Mình bị dị ứng sữa bò (lactose) nặng, quán có cà phê nào an toàn cho mình không?",
        "model_output": "Dạ em chào anh/chị! Quán em có món Oat Milk Mocha cực kỳ an toàn cho người không dung nạp lactose hay dị ứng sữa bò ạ. Món này sử dụng 100% sữa yến mạch tự nhiên, kết hợp ca cao nguyên chất và cà phê espresso thơm béo mà hoàn toàn không chứa sữa động vật ạ!",
        "category": "allergen_safety",
        "verified": True,
    },
    {
        "id": "slm-002",
        "user_input": "Trưa nay ăn đồ dầu mỡ ngấy quá, có thức uống nào thanh mát giải ngấy tức thì không?",
        "model_output": "Dạ để giải ngấy tức thì sau bữa trưa, em đặc biệt gợi ý cho mình một ly Iced Americano mát lạnh sảng khoái với vị đắng thanh sạch sẽ, hoặc món Green Detox Cold-Pressed ép từ táo xanh, dưa leo và cần tây tươi giúp thanh lọc cơ thể nhẹ nhàng ạ!",
        "category": "flavor_recommendation",
        "verified": True,
    },
    {
        "id": "slm-003",
        "user_input": "Em bị say cà phê tim đập nhanh, quán có trà nào thơm thanh không caffeine không?",
        "model_output": "Dạ nếu mình dễ bị say cà phê hoặc tim đập nhanh, em gợi ý Trà Hoa Cúc Mật Ong (Chamomile Honey) hoặc Hibiscus Berry Iced Tea ạ! Hai món này hoàn toàn không chứa caffeine (0%), vị ngọt thanh êm dịu giúp thư giãn tâm trí và ngủ rất ngon ạ.",
        "category": "caffeine_free",
        "verified": True,
    },
    {
        "id": "slm-004",
        "user_input": "Cho mình 2 ly Caramel Latte ít đường mang về nhé.",
        "model_output": "Dạ em đã ghi nhận đơn 2 ly Caramel Latte ít đường mang về của mình ạ! Em gửi món vào giỏ hàng ngay cho anh/chị nhé ạ.",
        "category": "ordering",
        "verified": True,
    },
    {
        "id": "slm-005",
        "user_input": "Mình muốn tìm thức uống làm đẹp da, ít calo để uống mỗi ngày.",
        "model_output": "Dạ món Green Detox Cold-Pressed và Hibiscus Berry Iced Tea là lựa chọn hoàn hảo ạ! Cả hai đều giàu chất chống oxy hóa, vitamin C tự nhiên, không đường hóa học giúp sáng da, giữ dáng và thanh nhiệt tuyệt vời ạ.",
        "category": "health_beauty",
        "verified": True,
    },
    {
        "id": "slm-006",
        "user_input": "Quán có bán matcha đá xay hay trà sữa trân châu không bạn?",
        "model_output": "Dạ hiện tại menu quán em tập trung vào các dòng Cà phê rang mộc chất lượng cao, Trà hoa thanh lọc và Nước ép nguyên chất nên chưa phục vụ matcha đá xay hay trà sữa trân châu ạ. Em có thể gợi ý cho mình món Caramel Latte ngọt béo hoặc Peach Oolong Tea thơm mát thanh ngọt tương tự nhé ạ!",
        "category": "menu_groundedness",
        "verified": True,
    },
    {
        "id": "slm-007",
        "user_input": "Giao cho anh Nam số 0912345678 đến 45 Lê Duẩn 1 ly Bạc xỉu nhé.",
        "model_output": "Dạ em chào anh Nam! Em đã lưu thông tin số điện thoại 0912345678 và địa chỉ nhận hàng tại 45 Lê Duẩn. Món Bạc xỉu (Caramel Latte béo ngọt dịu) của anh sẽ được pha chế và giao ngay ạ!",
        "category": "intent_ner",
        "verified": True,
    },
    {
        "id": "slm-008",
        "user_input": "Hôm nay trời se lạnh mưa phùn, uống gì cho ấm người vậy em?",
        "model_output": "Dạ tiết trời mưa lạnh thế này thì một ly Hazelnut Cappuccino nóng thơm nồng hương hạt phỉ bùi béo với lớp bọt sữa mềm mịn, hoặc một tách Trà Gừng Mật Ong ấm nồng cuống họng sẽ xua tan cái lạnh ngay tức thì ạ!",
        "category": "weather_mood",
        "verified": True,
    },
]

# Seed pairs for Domain RAG Embeddings (32+ curated Vietnamese F&B slang, nuances, and flavor intent pairs)
INITIAL_RAG_PAIRS: list[dict[str, Any]] = [
    # Cà phê & Say caffeine
    {"id": "rag-001", "query_slang": "bạc xỉu sài gòn", "target_drink_flavor": "Caramel Latte ngọt béo nhiều sữa ít cà phê", "label": 1.0, "category": "coffee"},
    {"id": "rag-002", "query_slang": "say cà phê tim đập thình thịch", "target_drink_flavor": "Chamomile Honey Tea 0% caffeine hoa cúc dịu êm", "label": 1.0, "category": "caffeine_sensitivity"},
    {"id": "rag-003", "query_slang": "say cà phê cồn cào ruột", "target_drink_flavor": "Hibiscus Berry Iced Tea không caffeine mát ngọt", "label": 1.0, "category": "caffeine_sensitivity"},
    {"id": "rag-004", "query_slang": "cà phê đen đá không đường đậm đặc", "target_drink_flavor": "Classic Espresso và Iced Americano đắng mộc", "label": 1.0, "category": "coffee"},
    {"id": "rag-005", "query_slang": "cà phê béo ngậy bọt sữa dày", "target_drink_flavor": "Hazelnut Cappuccino bọt sữa bồng bềnh hạt phỉ", "label": 1.0, "category": "coffee"},
    {"id": "rag-006", "query_slang": "thức uống cho người mới tập uống cafe", "target_drink_flavor": "Caramel Latte sốt caramel ngọt thơm dễ uống", "label": 1.0, "category": "coffee"},
    # Ăn no, giải ngấy, tiêu thực
    {"id": "rag-007", "query_slang": "ăn đồ dầu mỡ ngấy quá giải ngấy", "target_drink_flavor": "Iced Americano thanh sạch hoặc Green Detox táo cần tây", "label": 1.0, "category": "digestive"},
    {"id": "rag-008", "query_slang": "no ứ hự đầy bụng khó tiêu", "target_drink_flavor": "Jasmine Green Tea hoặc Cold-Pressed Juice tiêu hóa tốt", "label": 1.0, "category": "digestive"},
    {"id": "rag-009", "query_slang": "uống sau bữa tiệc nhậu nhiều đạm", "target_drink_flavor": "Green Detox Cold-Pressed gừng tươi dưa leo thanh lọc", "label": 1.0, "category": "digestive"},
    # Thời tiết & Tâm trạng
    {"id": "rag-010", "query_slang": "trời mưa se lạnh cần ấm áp", "target_drink_flavor": "Hot Mocha sữa yến mạch ấm nồng và Hazelnut Cappuccino", "label": 1.0, "category": "weather"},
    {"id": "rag-011", "query_slang": "mùa hè oi bức 40 độ chảy mỡ", "target_drink_flavor": "Hibiscus Berry đá lạnh mát rượi sảng khoái", "label": 1.0, "category": "weather"},
    {"id": "rag-012", "query_slang": "ngồi đọc sách chill chill bên cửa sổ", "target_drink_flavor": "Jasmine Green Tea hoa nhài thoang thoảng tĩnh tâm", "label": 1.0, "category": "mood"},
    {"id": "rag-013", "query_slang": "stress căng thẳng muốn thư giãn đầu óc", "target_drink_flavor": "Chamomile Honey Tea hoa cúc mật ong xoa dịu thần kinh", "label": 1.0, "category": "mood"},
    {"id": "rag-014", "query_slang": "đang buồn muốn chút vị ngọt ủi an", "target_drink_flavor": "Caramel Latte ngọt ngào xua tan mệt mỏi", "label": 1.0, "category": "mood"},
    # Dị ứng, Sức khỏe & Ăn kiêng
    {"id": "rag-015", "query_slang": "dị ứng sữa bò đau bụng tiêu chảy", "target_drink_flavor": "Oat Milk Mocha sữa yến mạch thuần thực vật", "label": 1.0, "category": "health_allergy"},
    {"id": "rag-016", "query_slang": "ăn chay trường vegan không động vật", "target_drink_flavor": "Oat Milk Mocha hoặc các dòng Trà thảo mộc", "label": 1.0, "category": "health_diet"},
    {"id": "rag-017", "query_slang": "ăn kiêng keto low-carb không calo", "target_drink_flavor": "Iced Americano hoặc Jasmine Green Tea 0 đường", "label": 1.0, "category": "health_diet"},
    {"id": "rag-018", "query_slang": "làm đẹp da chống lão hóa", "target_drink_flavor": "Hibiscus Berry nhiều anthocyanin vitamin C sáng da", "label": 1.0, "category": "health_beauty"},
    {"id": "rag-019", "query_slang": "thanh lọc gan giải độc cơ thể detox", "target_drink_flavor": "Green Detox táo xanh cần tây dưa leo gừng tươi", "label": 1.0, "category": "health_detox"},
    {"id": "rag-020", "query_slang": "giữ dáng thon gọn giảm mỡ bụng", "target_drink_flavor": "Green Detox Cold-Pressed không đường giàu chất xơ", "label": 1.0, "category": "health_diet"},
    # Nhu cầu công việc & Thời gian
    {"id": "rag-021", "query_slang": "chạy deadline thức thâu đêm cần tỉnh ngủ", "target_drink_flavor": "Classic Espresso double shot tỉnh táo tập trung", "label": 1.0, "category": "work_focus"},
    {"id": "rag-022", "query_slang": "sáng sớm cần nạp năng lượng làm việc", "target_drink_flavor": "Classic Espresso hoặc Iced Americano sảng khoái", "label": 1.0, "category": "work_focus"},
    {"id": "rag-023", "query_slang": "chiều muộn 4h chiều không muốn mất ngủ tối", "target_drink_flavor": "Chamomile Honey Tea hoặc Peach Oolong Tea nhẹ dịu", "label": 1.0, "category": "time_sensitive"},
    {"id": "rag-024", "query_slang": "uống trước khi đi ngủ 30 phút", "target_drink_flavor": "Chamomile Honey Tea an thần ngủ sâu giấc", "label": 1.0, "category": "time_sensitive"},
    # Âm dương, Hương vị đối lập (Negative pairs)
    {"id": "rag-025", "query_slang": "món không đường không ngọt", "target_drink_flavor": "Caramel Latte nhiều syrup bơ ngọt ngào", "label": -0.8, "category": "negative_pair"},
    {"id": "rag-026", "query_slang": "người dị ứng sữa bò lactose", "target_drink_flavor": "Caramel Latte sữa tươi nguyên kem béo", "label": -0.9, "category": "negative_pair"},
    {"id": "rag-027", "query_slang": "say cà phê không uống được caffeine", "target_drink_flavor": "Classic Espresso đậm đặc 2 shot", "label": -1.0, "category": "negative_pair"},
    {"id": "rag-028", "query_slang": "trời mưa lạnh cần món ấm nóng", "target_drink_flavor": "Hibiscus Berry Iced Tea đá xay buốt răng", "label": -0.7, "category": "negative_pair"},
    {"id": "rag-029", "query_slang": "cần giảm cân ăn kiêng nghiêm ngặt", "target_drink_flavor": "Caramel Latte nhiều sốt bơ đường", "label": -0.8, "category": "negative_pair"},
    # Khẩu vị đặc trưng khác
    {"id": "rag-030", "query_slang": "vị chua ngọt thơm mùi quả mọng", "target_drink_flavor": "Hibiscus Berry đỏ rực chua thanh ngọt hậu", "label": 1.0, "category": "flavor_nuance"},
    {"id": "rag-031", "query_slang": "vị trà đậm chát nhẹ hậu ngọt sâu", "target_drink_flavor": "Peach Oolong Tea và Jasmine Green Tea búp non", "label": 1.0, "category": "flavor_nuance"},
    {"id": "rag-032", "query_slang": "thèm đồ uống ngọt thanh mát mẻ trưa hè", "target_drink_flavor": "Peach Oolong Tea mát lạnh đào miếng giòn", "label": 1.0, "category": "flavor_nuance"},
]


class TrainingDataService:
    """Singleton service for managing centralized training datasets, versions, and lineage."""

    def __init__(self) -> None:
        self.data_dir = DATA_DIR
        self.datasets_file = DATASETS_FILE
        self._datasets: dict[str, dict[str, Any]] = {}
        self._load_or_initialize()

    def _calculate_hash(self, samples: list[dict]) -> str:
        serialized = json.dumps(samples, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:12]

    def _load_or_initialize(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        if self.datasets_file.exists():
            try:
                with open(self.datasets_file, "r", encoding="utf-8") as f:
                    self._datasets = json.load(f)
                    return
            except Exception as e:
                logger.warning("Error loading training datasets (%s). Re-initializing.", e)

        # Initialize default datasets
        slm_hash = self._calculate_hash(INITIAL_SLM_SAMPLES)
        rag_hash = self._calculate_hash(INITIAL_RAG_PAIRS)

        self._datasets = {
            "drinkbot-slm-finetune-dataset": {
                "name": "drinkbot-slm-finetune-dataset",
                "dataset_type": "slm_dialogues",
                "description": "Tập dữ liệu mẫu hội thoại Barista chuẩn hóa phong cách phục vụ, an toàn dị ứng cho Gemma 2 2B LoRA.",
                "current_version": "v1.0.0",
                "versions": {
                    "v1.0.0": {
                        "version": "v1.0.0",
                        "description": "Phiên bản khởi tạo từ các traces chuẩn của quán",
                        "sample_count": len(INITIAL_SLM_SAMPLES),
                        "sha256_hash": slm_hash,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "samples": INITIAL_SLM_SAMPLES,
                    }
                },
            },
            "drinkbot-fnb-slang-dataset": {
                "name": "drinkbot-fnb-slang-dataset",
                "dataset_type": "rag_slang_pairs",
                "description": "Tập 35+ cặp từ lóng, tiếng lóng và khẩu vị F&B Việt Nam để huấn luyện RAG Embedding Adapter.",
                "current_version": "v1.0.0",
                "versions": {
                    "v1.0.0": {
                        "version": "v1.0.0",
                        "description": "Phiên bản khởi tạo từ điển từ lóng F&B",
                        "sample_count": len(INITIAL_RAG_PAIRS),
                        "sha256_hash": rag_hash,
                        "created_at": datetime.now(timezone.utc).isoformat(),
                        "samples": INITIAL_RAG_PAIRS,
                    }
                },
            },
        }
        self._save_to_disk()

    def _save_to_disk(self) -> None:
        try:
            with open(self.datasets_file, "w", encoding="utf-8") as f:
                json.dump(self._datasets, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error("Failed to save training datasets to disk: %s", e)

    def reset_to_defaults(self) -> None:
        """Reset datasets to initial clean seed state."""
        if self.datasets_file.exists():
            try:
                self.datasets_file.unlink()
            except Exception:
                pass
        self._load_or_initialize()


    def list_datasets(self, dataset_type: str | None = None) -> list[dict[str, Any]]:
        """List all datasets with metadata and current active version."""
        results = []
        for name, ds in self._datasets.items():
            if dataset_type and ds.get("dataset_type") != dataset_type:
                continue
            cur_ver_key = ds.get("current_version", "v1.0.0")
            ver_info = ds.get("versions", {}).get(cur_ver_key, {})
            results.append({
                "name": ds["name"],
                "dataset_type": ds["dataset_type"],
                "description": ds["description"],
                "current_version": cur_ver_key,
                "sample_count": ver_info.get("sample_count", 0),
                "sha256_hash": ver_info.get("sha256_hash", ""),
                "versions_available": list(ds.get("versions", {}).keys()),
                "created_at": ver_info.get("created_at", ""),
            })
        return results

    def get_dataset(self, name: str, version: str | None = None) -> dict[str, Any] | None:
        """Get dataset details along with its samples for a specific version."""
        ds = self._datasets.get(name)
        if not ds:
            return None
        target_ver = version or ds.get("current_version", "v1.0.0")
        ver_data = ds.get("versions", {}).get(target_ver)
        if not ver_data:
            return None
        return {
            "name": ds["name"],
            "dataset_type": ds["dataset_type"],
            "description": ds["description"],
            "version": target_ver,
            "sample_count": ver_data["sample_count"],
            "sha256_hash": ver_data["sha256_hash"],
            "created_at": ver_data["created_at"],
            "samples": ver_data["samples"],
        }

    def add_sample(self, dataset_name: str, sample_payload: dict[str, Any]) -> dict[str, Any]:
        """Add a new training sample into current version (Data Annotation & Curation)."""
        ds = self._datasets.get(dataset_name)
        if not ds:
            raise ValueError(f"Dataset '{dataset_name}' not found.")

        cur_ver = ds.get("current_version", "v1.0.0")
        ver_data = ds["versions"][cur_ver]

        sample_id = sample_payload.get("id") or f"sample-{uuid.uuid4().hex[:6]}"
        sample_payload["id"] = sample_id
        sample_payload["created_at"] = datetime.now(timezone.utc).isoformat()

        ver_data["samples"].append(sample_payload)
        ver_data["sample_count"] = len(ver_data["samples"])
        ver_data["sha256_hash"] = self._calculate_hash(ver_data["samples"])
        self._save_to_disk()

        logger.info("Added sample %s to dataset %s@%s", sample_id, dataset_name, cur_ver)
        return sample_payload

    def create_new_version(
        self, dataset_name: str, new_version: str, description: str = ""
    ) -> dict[str, Any]:
        """Create a new version snapshot of the dataset (Data Versioning)."""
        ds = self._datasets.get(dataset_name)
        if not ds:
            raise ValueError(f"Dataset '{dataset_name}' not found.")
        if new_version in ds["versions"]:
            raise ValueError(f"Version '{new_version}' already exists for dataset '{dataset_name}'.")

        cur_ver = ds.get("current_version", "v1.0.0")
        cur_samples = list(ds["versions"][cur_ver]["samples"])

        ds["versions"][new_version] = {
            "version": new_version,
            "description": description or f"Snapshot from {cur_ver}",
            "sample_count": len(cur_samples),
            "sha256_hash": self._calculate_hash(cur_samples),
            "created_at": datetime.now(timezone.utc).isoformat(),
            "samples": cur_samples,
        }
        ds["current_version"] = new_version
        self._save_to_disk()

        logger.info("Created new dataset version: %s@%s", dataset_name, new_version)
        return ds["versions"][new_version]

    def export_training_samples(self, dataset_name: str, version: str | None = None) -> list[dict[str, Any]]:
        """Export samples for pipeline consumption."""
        data = self.get_dataset(dataset_name, version)
        if not data:
            return []
        return data.get("samples", [])


training_data_service = TrainingDataService()
