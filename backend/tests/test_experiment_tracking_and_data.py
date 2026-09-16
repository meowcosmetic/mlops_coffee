"""Unit and API tests for Model Hyperparameters Experiment Tracking
and Centralized Training Data Management.
"""
from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.services.experiment_tracker_service import DATA_DIR as EXP_DATA_DIR, RUNS_FILE as EXP_RUNS_FILE, ExperimentRun, experiment_tracker
from app.services.slm_finetune_service import slm_pipeline
from app.services.training_data_service import DATA_DIR as DS_DATA_DIR, DATASETS_FILE as DS_DATASETS_FILE, training_data_service


@pytest.fixture(autouse=True)
def isolate_test_data(tmp_path):
    """Isolate datasets and experiment storage during test execution."""
    test_ds_dir = tmp_path / "datasets"
    test_ds_dir.mkdir(parents=True, exist_ok=True)
    training_data_service.data_dir = test_ds_dir
    training_data_service.datasets_file = test_ds_dir / "training_datasets.json"
    training_data_service.reset_to_defaults()

    test_exp_dir = tmp_path / "experiments"
    test_exp_dir.mkdir(parents=True, exist_ok=True)
    experiment_tracker.data_dir = test_exp_dir
    experiment_tracker.runs_file = test_exp_dir / "experiment_runs.json"
    experiment_tracker._load_or_initialize()

    yield

    # Restore default paths and state
    training_data_service.data_dir = DS_DATA_DIR
    training_data_service.datasets_file = DS_DATASETS_FILE
    training_data_service.reset_to_defaults()
    experiment_tracker.data_dir = EXP_DATA_DIR
    experiment_tracker.runs_file = EXP_RUNS_FILE
    experiment_tracker._load_or_initialize()



def test_training_data_service_initialization():
    """Verify default datasets exist with versions and samples."""
    datasets = training_data_service.list_datasets()
    names = [d["name"] for d in datasets]
    assert "drinkbot-slm-finetune-dataset" in names
    assert "drinkbot-fnb-slang-dataset" in names

    slm_data = training_data_service.get_dataset("drinkbot-slm-finetune-dataset")
    assert slm_data is not None
    assert slm_data["sample_count"] >= 8
    assert len(slm_data["samples"]) >= 8
    assert slm_data["version"] == "v1.0.0"


def test_training_data_service_add_sample_and_versioning(tmp_path):
    """Test adding new curated sample and snapshotting a new version."""
    # Add new sample
    new_sample = {
        "user_input": "Cho 1 ly Trà đào cam sả ít ngọt nha quán",
        "model_output": "Dạ quán em có Trà đào cam sả thanh mát ít ngọt thơm nồng vị sả tươi cho mình ạ!",
        "category": "tea",
    }
    added = training_data_service.add_sample("drinkbot-slm-finetune-dataset", new_sample)
    assert "id" in added

    # Create new version snapshot v1.1.0
    v11 = training_data_service.create_new_version(
        "drinkbot-slm-finetune-dataset",
        "v1.1.0-test",
        description="Test snapshot with new peach tea sample",
    )
    assert v11["version"] == "v1.1.0-test"
    assert v11["sample_count"] >= 9


def test_experiment_tracker_logging_and_comparison():
    """Verify logging an experiment run and side-by-side run comparison."""
    run = ExperimentRun(
        run_id="test-run-compare-01",
        experiment_name="test-exp",
        pipeline_type="slm_lora_finetune",
        model_name="drinkbot-slm-lora-v1.0",
        base_model="google/gemma-2-2b-it",
        hyperparameters={"r": 16, "lora_alpha": 32, "epochs": 4, "learning_rate": 0.0001},
        dataset_lineage={"dataset_name": "drinkbot-slm-finetune-dataset", "version": "v1.0.0", "sample_count": 8},
        loss_history=[{"epoch": 1, "loss": 2.2}, {"epoch": 4, "loss": 0.35}],
        initial_loss=2.2,
        final_loss=0.35,
        eval_metrics={"overall_pass_rate": 97.5},
        hardware={"device_name": "NVIDIA RTX 3060", "vram_total_gb": 12.0},
        duration_seconds=15.2,
    )
    logged_id = experiment_tracker.log_run(run)
    assert logged_id == "test-run-compare-01"

    # Compare against baseline seed run
    comp = experiment_tracker.compare_runs(["run-slm-lora-001", "test-run-compare-01"])
    assert comp["total_compared"] >= 1
    assert len(comp["comparison"]) >= 1


def test_slm_pipeline_logs_experiment_with_lineage(tmp_path):
    """Run SLM pipeline and verify experiment run is automatically logged with dataset lineage."""
    slm_pipeline.weights_dir = tmp_path / "test_exp_weights"
    metrics = slm_pipeline.run_training_pipeline(epochs=2, batch_size=2, r=8, lora_alpha=16)

    assert metrics.status == "completed"

    runs = experiment_tracker.list_runs(pipeline_type="slm_lora_finetune")
    assert len(runs) >= 1
    latest_run = runs[0]
    assert latest_run["model_name"] == "drinkbot-slm-lora-v1.0"
    assert "dataset_lineage" in latest_run
    assert latest_run["dataset_lineage"]["dataset_name"] == "drinkbot-slm-finetune-dataset"


@pytest.mark.asyncio
async def test_telemetry_experiment_and_dataset_apis(client: AsyncClient):
    """Test REST API endpoints for experiments and training datasets."""
    # 1. Get runs
    res_runs = await client.get("/api/telemetry/experiments/runs")
    assert res_runs.status_code == 200
    runs_data = res_runs.json()
    assert "runs" in runs_data

    # 2. Compare runs
    res_comp = await client.get("/api/telemetry/experiments/compare?run_ids=run-slm-lora-001,run-rag-embed-001")
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert "comparison" in comp_data

    # 3. Get datasets list
    res_ds = await client.get("/api/telemetry/datasets")
    assert res_ds.status_code == 200
    assert len(res_ds.json()["datasets"]) >= 2

    # 4. Get dataset details
    res_detail = await client.get("/api/telemetry/datasets/drinkbot-slm-finetune-dataset")
    assert res_detail.status_code == 200
    assert "samples" in res_detail.json()["dataset"]

    # 5. Add sample to dataset via API
    add_res = await client.post(
        "/api/telemetry/datasets/drinkbot-slm-finetune-dataset/samples",
        json={"sample": {"user_input": "Trà gừng nóng", "model_output": "Dạ có Trà gừng mật ong ạ"}},
    )
    assert add_res.status_code == 200
    assert add_res.json()["status"] == "created"

    # 6. Create new version snapshot via API
    ver_res = await client.post(
        "/api/telemetry/datasets/drinkbot-slm-finetune-dataset/versions",
        json={"version": "v1.2.0-api-test", "description": "API snapshot"},
    )
    assert ver_res.status_code == 200
    assert ver_res.json()["version"]["version"] == "v1.2.0-api-test"
