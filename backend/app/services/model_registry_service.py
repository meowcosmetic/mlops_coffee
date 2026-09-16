"""Model Registry Service for DrinkBot.

Tracks, versions, and manages LLM Foundation models, Fine-Tuned SLM LoRA checkpoints
(specifically trained from google/gemma-2-2b-it), and Domain RAG Embedding Adapters.
Enables runtime hot-swapping and rollback with full Langfuse metadata tracking.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import hashlib
import json
import logging
from typing import Literal

logger = logging.getLogger(__name__)

ModelType = Literal["foundation", "fine-tuned-slm", "rag-embedding"]
ModelStatus = Literal["production", "staging", "archived", "evaluating"]


@dataclass
class ModelVersion:
    name: str
    version: str
    model_type: ModelType
    base_model: str
    description: str
    status: ModelStatus
    checkpoint_uri: str | None = None
    lora_params: dict | None = None
    eval_pass_rate: float | None = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    sha256_hash: str = ""

    def __post_init__(self):
        if not self.sha256_hash:
            raw = f"{self.name}:{self.version}:{self.base_model}:{self.model_type}"
            self.sha256_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]


# Initial default Model Registry state
INITIAL_MODELS: list[ModelVersion] = [
    # 1. Foundation Models
    ModelVersion(
        name="ag/gemini-3.8-flash-low",
        version="base-latest",
        model_type="foundation",
        base_model="Google Gemini 3.8 Flash",
        description="Mô hình Cloud mặc định, xử lý hội thoại và tool-calling nhanh.",
        status="production",
        eval_pass_rate=93.8,
    ),
    ModelVersion(
        name="gpt-4o-mini",
        version="base-latest",
        model_type="foundation",
        base_model="OpenAI GPT-4o-mini",
        description="Mô hình Cloud dự phòng của OpenAI.",
        status="staging",
        eval_pass_rate=91.5,
    ),
    # 2. Fine-Tuned SLMs & Local Ollama Models (0đ Cost)
    ModelVersion(
        name="drinkbot-slm-lora-v1.0",
        version="v1.0.0",
        model_type="fine-tuned-slm",
        base_model="google/gemma-2-2b-it (Ollama Local)",
        description="Mô hình SLM fine-tuned bằng LoRA, phục vụ cục bộ qua Ollama (RTX 3060) - 0đ chi phí, không cần Cloud API Key.",
        status="staging",
        checkpoint_uri="weights/drinkbot-slm-lora-v1.0",
        lora_params={
            "r": 8,
            "lora_alpha": 16,
            "target_modules": ["q_proj", "v_proj"],
            "epochs": 3,
            "learning_rate": 0.0002,
        },
        eval_pass_rate=96.2,
    ),
    ModelVersion(
        name="gemma4:e4b",
        version="local-latest",
        model_type="fine-tuned-slm",
        base_model="Ollama Local (NVIDIA GeForce RTX 3060 12GB)",
        description="Mô hình Gemma 4 local trên Ollama - 0đ chi phí, 100% offline không cần API key.",
        status="staging",
        eval_pass_rate=96.0,
    ),
    # 3. RAG Embedding Models
    ModelVersion(
        name="all-MiniLM-L6-v2",
        version="base-384d",
        model_type="rag-embedding",
        base_model="sentence-transformers/all-MiniLM-L6-v2",
        description="Mô hình embedding gốc 384 chiều chạy trên CPU.",
        status="production",
        eval_pass_rate=100.0,
    ),
    ModelVersion(
        name="drinkbot-embed-adapted-v1.0",
        version="v1.0.0",
        model_type="rag-embedding",
        base_model="sentence-transformers/all-MiniLM-L6-v2 + Linear Adapter",
        description="Embedding Adapter đã được tái huấn luyện (Contrastive Learning) với từ lóng và khẩu vị F&B Việt Nam.",
        status="staging",
        checkpoint_uri="weights/drinkbot-embed-adapted-v1.0.pt",
        eval_pass_rate=100.0,
    ),
]


class ModelRegistryService:
    """Singleton service for managing model versions, promotions, and active serving states."""

    def __init__(self) -> None:
        self._models: dict[str, ModelVersion] = {
            f"{m.name}@{m.version}": m for m in INITIAL_MODELS
        }
        self._active_chat_model = "ag/gemini-3.8-flash-low@base-latest"
        self._active_embedding_model = "all-MiniLM-L6-v2@base-384d"

    def list_models(self, model_type: ModelType | None = None) -> list[dict]:
        """List all models in the registry, optionally filtered by type."""
        models = list(self._models.values())
        if model_type:
            models = [m for m in models if m.model_type == model_type]
        
        result = []
        for m in models:
            data = asdict(m)
            data["is_active_chat"] = (f"{m.name}@{m.version}" == self._active_chat_model)
            data["is_active_embedding"] = (f"{m.name}@{m.version}" == self._active_embedding_model)
            result.append(data)
        return result

    def get_model(self, key: str) -> ModelVersion | None:
        """Get model by 'name@version' or just 'name'."""
        if key in self._models:
            return self._models[key]
        for k, m in self._models.items():
            if m.name == key:
                return m
        return None

    def register_model(self, model: ModelVersion) -> ModelVersion:
        """Register or update a model checkpoint in the registry."""
        key = f"{model.name}@{model.version}"
        self._models[key] = model
        logger.info("Registered model version: %s (status: %s)", key, model.status)
        return model

    def activate_model(self, key: str) -> ModelVersion:
        """Promote and activate a model for runtime serving without restarting."""
        model = self.get_model(key)
        if not model:
            raise ValueError(f"Model '{key}' not found in registry.")

        if model.model_type in ("foundation", "fine-tuned-slm"):
            # Deactivate previous active chat model from production
            prev = self.get_model(self._active_chat_model)
            if prev and prev.status == "production":
                prev.status = "staging"
            model.status = "production"
            self._active_chat_model = f"{model.name}@{model.version}"
            logger.info("Active Chat Model switched to: %s", self._active_chat_model)
        elif model.model_type == "rag-embedding":
            prev = self.get_model(self._active_embedding_model)
            if prev and prev.status == "production":
                prev.status = "staging"
            model.status = "production"
            self._active_embedding_model = f"{model.name}@{model.version}"
            logger.info("Active Embedding Model switched to: %s", self._active_embedding_model)

        return model

    def get_active_chat_model(self) -> ModelVersion:
        """Returns the current active model version used for customer chats."""
        return self._models.get(
            self._active_chat_model, INITIAL_MODELS[0]
        )

    def get_active_embedding_model(self) -> ModelVersion:
        """Returns the current active embedding model version used for RAG."""
        return self._models.get(
            self._active_embedding_model, INITIAL_MODELS[3]
        )


# Global singleton
model_registry = ModelRegistryService()
