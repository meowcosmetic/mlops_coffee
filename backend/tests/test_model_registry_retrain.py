"""Unit and integration tests for Model Registry, SLM LoRA Finetune,
Embedding Retraining, and Intent NER Extraction.
"""
from __future__ import annotations

import os
from pathlib import Path
import pytest
from httpx import AsyncClient

from app.services.embedding_retrain_service import embedding_pipeline
from app.services.intent_ner_service import ner_service
from app.services.model_registry_service import ModelVersion, model_registry
from app.services.slm_finetune_service import slm_pipeline


def test_model_registry_initial_state():
    """Verify registry starts with foundation models, Gemma LoRA, and embeddings."""
    models = model_registry.list_models()
    names = [m["name"] for m in models]
    assert "ag/gemini-3.8-flash-low" in names
    assert "drinkbot-slm-lora-v1.0" in names
    assert "all-MiniLM-L6-v2" in names
    assert "drinkbot-embed-adapted-v1.0" in names

    active_chat = model_registry.get_active_chat_model()
    assert active_chat.name == "ag/gemini-3.8-flash-low"

    active_embed = model_registry.get_active_embedding_model()
    assert active_embed.name == "all-MiniLM-L6-v2"


def test_model_registry_activation_hot_swap():
    """Verify runtime hot-swapping switches production flags cleanly."""
    # Switch to LoRA model
    activated = model_registry.activate_model("drinkbot-slm-lora-v1.0@v1.0.0")
    assert activated.name == "drinkbot-slm-lora-v1.0"
    assert activated.status == "production"
    assert model_registry.get_active_chat_model().name == "drinkbot-slm-lora-v1.0"

    # Switch back to Foundation model
    model_registry.activate_model("ag/gemini-3.8-flash-low@base-latest")
    assert model_registry.get_active_chat_model().name == "ag/gemini-3.8-flash-low"

    # Switch embedding model
    embed_active = model_registry.activate_model("drinkbot-embed-adapted-v1.0@v1.0.0")
    assert embed_active.name == "drinkbot-embed-adapted-v1.0"
    assert model_registry.get_active_embedding_model().name == "drinkbot-embed-adapted-v1.0"


def test_slm_finetune_gemma_chat_template():
    """Ensure Gemma 2 Chat Template conforms to official Google specification."""
    formatted = slm_pipeline.format_gemma_chat_template(
        user_msg="Tôi muốn cà phê không đường",
        model_reply="Dạ có Iced Americano hoặc Classic Espresso mộc 100% không đường ạ!",
    )
    assert "<start_of_turn>user\nTôi muốn cà phê không đường<end_of_turn>" in formatted
    assert "<start_of_turn>model\nDạ có Iced Americano hoặc Classic Espresso mộc 100% không đường ạ!<end_of_turn>" in formatted


def test_slm_finetune_pipeline_execution(tmp_path):
    """Run SLM LoRA pipeline and verify loss descent, metrics, and weights output."""
    slm_pipeline.weights_dir = tmp_path / "gemma_lora_test"
    metrics = slm_pipeline.run_training_pipeline(epochs=2, batch_size=2, r=8, lora_alpha=16)

    assert metrics.base_model == "google/gemma-2-2b-it"
    assert metrics.adapter_name == "drinkbot-slm-lora-v1.0"
    assert metrics.final_loss < metrics.initial_loss
    assert metrics.rank_r == 8
    assert metrics.lora_alpha == 16
    assert metrics.eval_pass_rate >= 90.0

    config_file = tmp_path / "gemma_lora_test" / "adapter_config.json"
    assert config_file.exists()


def test_embedding_retrain_pipeline_execution(tmp_path):
    """Run Domain Embedding Retraining and verify checkpoint generation & hot-swap."""
    embedding_pipeline.checkpoint_path = tmp_path / "test_adapted_embed.pt"
    metrics = embedding_pipeline.train_adapter(epochs=2)

    assert metrics.total_pairs >= 30
    assert metrics.final_loss < metrics.initial_loss
    assert metrics.accuracy_improvement > 0
    assert (tmp_path / "test_adapted_embed.pt").exists()


def test_intent_ner_service_vietnamese_extraction():
    """Verify extraction of customer details and order items from Vietnamese queries."""
    text = "Giao cho anh Hoàng Nam số 0987654321 đến 124 Nguyễn Huệ Quận 1 2 ly Bạc xỉu và 1 ly Trà đào nhé"
    entities = ner_service.extract(text)

    data = entities.to_dict()
    assert data["customer_name"] == "Anh Hoàng Nam"
    assert data["phone_number"] == "0987654321"
    assert "124 Nguyễn Huệ" in data["shipping_address"]
    assert data["has_delivery_info"] is True

    items = data["items"]
    assert len(items) >= 1
    item_names = [it["item"].lower() for it in items]
    assert any("bạc xỉu" in n for n in item_names)


@pytest.mark.asyncio
async def test_telemetry_model_registry_api(client: AsyncClient):
    """Test GET /api/telemetry/models/registry and POST /api/telemetry/models/activate."""
    res = await client.get("/api/telemetry/models/registry")
    assert res.status_code == 200
    data = res.json()
    assert "models" in data
    assert "active_chat_model" in data
    assert "active_embedding_model" in data

    # Test hot-swap activation
    act_res = await client.post(
        "/api/telemetry/models/activate",
        json={"model_key": "drinkbot-slm-lora-v1.0@v1.0.0"},
    )
    assert act_res.status_code == 200
    assert act_res.json()["status"] == "activated"

    # Switch back
    await client.post(
        "/api/telemetry/models/activate",
        json={"model_key": "ag/gemini-3.8-flash-low@base-latest"},
    )


@pytest.mark.asyncio
async def test_telemetry_retrain_endpoints(client: AsyncClient):
    """Test SLM, Embedding retrain, and NER endpoints via API."""
    # Test NER endpoint
    ner_res = await client.post(
        "/api/telemetry/retrain/ner/parse",
        json={"text": "Đặt cho chị Lan 0901234567 ở 88 Trần Hưng Đạo 3 ly Americano đá"},
    )
    assert ner_res.status_code == 200
    extracted = ner_res.json()["extracted"]
    assert extracted["phone_number"] == "0901234567"
    assert "Trần Hưng Đạo" in extracted["shipping_address"]

    # Test SLM Retrain endpoint
    slm_res = await client.post(
        "/api/telemetry/models/retrain/slm",
        json={"epochs": 2, "batch_size": 2, "learning_rate": 0.0002, "r": 8, "lora_alpha": 16},
    )
    assert slm_res.status_code == 200
    assert slm_res.json()["status"] == "completed"
    assert slm_res.json()["metrics"]["base_model"] == "google/gemma-2-2b-it"

    # Test Embedding Retrain endpoint
    embed_res = await client.post(
        "/api/telemetry/models/retrain/embeddings",
        json={"epochs": 2, "learning_rate": 0.001},
    )
    assert embed_res.status_code == 200
    assert embed_res.json()["status"] == "completed"
