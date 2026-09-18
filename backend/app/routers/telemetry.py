"""Router providing operational and trace telemetry for Langfuse and frontend inspector."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.services import eval_service, langfuse_service, prompt_service

router = APIRouter(prefix="/telemetry", tags=["telemetry"])


class PromptActivateRequest(BaseModel):
    version: str


class PromptCreateRequest(BaseModel):
    version: str
    template: str
    description: str = ""
    label: str = "staging"
    activate: bool = False


@router.get("/traces")
async def get_traces(limit: int = 20):
    """Return recent LLM execution traces with Langfuse metadata for the frontend inspector."""
    traces = langfuse_service.get_recent_traces(limit=limit)
    return {
        "langfuse_enabled": settings.langfuse_enabled,
        "langfuse_host": settings.langfuse_host,
        "total_traces": len(traces),
        "traces": traces,
    }


@router.post("/traces/clear")
async def clear_traces():
    """Clear local memory traces."""
    langfuse_service.clear_traces()
    return {"status": "cleared"}


@router.get("/prompts")
async def get_prompts(db: AsyncSession = Depends(get_db)):
    """Get all prompt versions from registry and database with active status and hashes."""
    from app.models import PromptVersion
    from sqlalchemy import select

    try:
        db_rows = list(await db.scalars(select(PromptVersion).order_by(PromptVersion.id)))
        for r in db_rows:
            if r.version not in prompt_service._REGISTRY:
                prompt_service.register_new_prompt(
                    version=r.version,
                    template=r.template,
                    description=f"Database prompt v{r.version}",
                    label="production" if r.is_active else "staged",
                    activate=r.is_active,
                )
            elif r.is_active:
                prompt_service.activate_prompt_version(r.version)
    except Exception:
        pass

    prompts = prompt_service.get_all_prompts()
    active = prompt_service.get_active_prompt()
    return {
        "active_version": active.version,
        "prompts": prompts,
    }


@router.post("/prompts/activate")
async def activate_prompt(payload: PromptActivateRequest, db: AsyncSession = Depends(get_db)):
    """Activate or rollback to a prompt version dynamically without redeploying code."""
    try:
        updated = prompt_service.activate_prompt_version(payload.version)

        # Synchronize immediately into PostgreSQL PromptVersion table
        from app.models import PromptVersion
        from sqlalchemy import select, update as sa_update

        # Deactivate all active rows in DB for this prompt name
        await db.execute(
            sa_update(PromptVersion).where(PromptVersion.name == updated.name).values(is_active=False)
        )

        row = await db.scalar(
            select(PromptVersion).where(PromptVersion.name == updated.name, PromptVersion.version == updated.version)
        )
        if row:
            row.is_active = True
            row.template = updated.template
            row.prompt_hash = updated.prompt_hash
        else:
            db.add(PromptVersion(
                name=updated.name,
                version=updated.version,
                template=updated.template,
                prompt_hash=updated.prompt_hash,
                is_active=True,
            ))
        await db.commit()

        return {
            "status": "activated",
            "active_version": updated.version,
            "prompt": updated,
        }
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/prompts")
async def create_prompt(payload: PromptCreateRequest, db: AsyncSession = Depends(get_db)):
    """Register a new prompt version for A/B testing or experimentation."""
    item = prompt_service.register_new_prompt(
        version=payload.version,
        template=payload.template,
        description=payload.description,
        label=payload.label,
        activate=payload.activate,
    )

    # Sync into DB table PromptVersion
    try:
        from app.models import PromptVersion
        from sqlalchemy import select, update as sa_update

        if payload.activate:
            await db.execute(
                sa_update(PromptVersion).where(PromptVersion.name == item.name).values(is_active=False)
            )
        row = await db.scalar(
            select(PromptVersion).where(PromptVersion.name == item.name, PromptVersion.version == item.version)
        )
        if row:
            row.template = item.template
            row.prompt_hash = item.prompt_hash
            if payload.activate:
                row.is_active = True
        else:
            db.add(PromptVersion(
                name=item.name,
                version=item.version,
                template=item.template,
                prompt_hash=item.prompt_hash,
                is_active=payload.activate,
            ))
        await db.commit()
    except Exception:
        pass

    return {"status": "registered", "prompt": item}


# --- CENTRALIZED EVALS & BENCHMARK SUITE ---

class EvalItemCreateRequest(BaseModel):
    category: str = "allergen_safety"
    name: str = ""
    input_text: str
    expected: dict = {}
    description: str = ""


class BenchmarkRunRequest(BaseModel):
    prompt_version: str | None = None
    model_name: str | None = None


@router.get("/models")
async def get_available_models():
    """Return available LLM models that can be selected for benchmarking and chat."""
    models = [
        {"id": "ag/gemini-3.8-flash-low", "name": "Gemini 3.8 Flash (Low Latency - Mặc định)"},
        {"id": "ag/gemini-3.8-flash-medium", "name": "Gemini 3.8 Flash (Medium)"},
        {"id": "ag/gemini-3.8-flash-high", "name": "Gemini 3.8 Flash (High Reasoning)"},
        {"id": "ag/gemini-3.7-flash-medium", "name": "Gemini 3.7 Flash"},
        {"id": "cx/gpt-5.4-mini", "name": "GPT 5.4 Mini"},
        {"id": "ag/claude-sonnet-4-6", "name": "Claude Sonnet 4.6"},
    ]
    return {
        "current_model": settings.openai_model,
        "models": models,
    }


@router.get("/evals/dataset")
async def get_eval_dataset():
    """Retrieve all test cases in the centralized Langfuse dataset."""
    items = eval_service.get_dataset_items()
    return {
        "total": len(items),
        "dataset_name": "drinkbot-centralized-benchmark",
        "items": items,
    }


@router.post("/evals/dataset/items")
async def create_eval_item(payload: EvalItemCreateRequest):
    """Add a test case to the centralized dataset (supports Trace-to-Dataset curation)."""
    item = eval_service.add_dataset_item(
        category=payload.category,
        name=payload.name,
        input_text=payload.input_text,
        expected=payload.expected,
        description=payload.description,
    )
    return {"status": "created", "item": item}


@router.delete("/evals/dataset/items/{item_id}")
async def remove_eval_item(item_id: str):
    """Delete a test case from the centralized dataset."""
    deleted = eval_service.delete_dataset_item(item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Test case not found")
    return {"status": "deleted"}


@router.post("/evals/run")
async def run_eval_benchmark(payload: BenchmarkRunRequest, db: AsyncSession = Depends(get_db)):
    """Execute automated benchmark against all dataset items and calculate scores."""
    from dataclasses import asdict
    summary = await eval_service.run_benchmark(
        db=db,
        prompt_version=payload.prompt_version,
        model_name=payload.model_name,
    )
    return {"status": "completed", "benchmark": asdict(summary)}


# --- MODEL REGISTRY & RETRAINING PIPELINE ---

class ModelActivateRequest(BaseModel):
    model_key: str


class SLMFinetuneRequest(BaseModel):
    epochs: int = 3
    batch_size: int = 4
    learning_rate: float = 0.0002
    r: int = 8
    lora_alpha: int = 16


class EmbeddingRetrainRequest(BaseModel):
    epochs: int = 5
    learning_rate: float = 0.001


class NERParseRequest(BaseModel):
    text: str


@router.get("/models/registry")
async def get_model_registry(model_type: str | None = None):
    """List all registered models, checkpoints, and active runtime states."""
    from app.services.model_registry_service import model_registry
    models = model_registry.list_models(model_type=model_type)  # type: ignore
    active_chat = model_registry.get_active_chat_model()
    active_embed = model_registry.get_active_embedding_model()
    return {
        "models": models,
        "active_chat_model": f"{active_chat.name}@{active_chat.version}",
        "active_embedding_model": f"{active_embed.name}@{active_embed.version}",
    }


@router.post("/models/activate")
async def activate_model(payload: ModelActivateRequest):
    """Hot-swap the active chat model or embedding model at runtime without downtime."""
    from app.services.model_registry_service import model_registry
    try:
        updated = model_registry.activate_model(payload.model_key)
        return {"status": "activated", "model": updated}
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/models/retrain/slm")
async def trigger_slm_finetune(payload: SLMFinetuneRequest):
    """Trigger LoRA Fine-Tuning pipeline for google/gemma-2-2b-it -> drinkbot-slm-lora-v1.0."""
    from dataclasses import asdict
    from app.services.slm_finetune_service import slm_pipeline
    metrics = slm_pipeline.run_training_pipeline(
        epochs=payload.epochs,
        batch_size=payload.batch_size,
        learning_rate=payload.learning_rate,
        r=payload.r,
        lora_alpha=payload.lora_alpha,
    )
    return {"status": "completed", "metrics": asdict(metrics)}


@router.post("/models/retrain/embeddings")
async def trigger_embedding_retrain(payload: EmbeddingRetrainRequest):
    """Trigger Domain Adaptation Retraining for MiniLM-L6-v2 RAG embeddings."""
    from dataclasses import asdict
    from app.services.embedding_retrain_service import embedding_pipeline
    metrics = embedding_pipeline.train_adapter(
        epochs=payload.epochs,
        learning_rate=payload.learning_rate,
    )
    return {"status": "completed", "metrics": asdict(metrics)}


@router.post("/retrain/ner/parse")
async def parse_customer_intent_ner(payload: NERParseRequest):
    """Extract Customer Name, Phone Number, Delivery Address, and Items from chat."""
    from app.services.intent_ner_service import ner_service
    entities = ner_service.extract(payload.text)
    return {"status": "success", "extracted": entities.to_dict()}


@router.get("/evals/latest")
async def get_latest_eval():
    """Get the most recent benchmark run summary."""
    latest = eval_service.get_latest_benchmark()
    return {"benchmark": latest}


# --- EXPERIMENT TRACKING & RUN HISTORY ---

@router.get("/experiments/runs")
async def get_experiment_runs(pipeline_type: str | None = None):
    """Retrieve historical model training runs with hyperparameters, loss curves, and hardware stats."""
    from app.services.experiment_tracker_service import experiment_tracker
    runs = experiment_tracker.list_runs(pipeline_type=pipeline_type)
    return {"total": len(runs), "runs": runs}


@router.get("/experiments/compare")
async def compare_experiment_runs(run_ids: str):
    """Compare hyperparameters and metrics across multiple experiment runs (comma-separated run_ids)."""
    from app.services.experiment_tracker_service import experiment_tracker
    ids = [i.strip() for i in run_ids.split(",") if i.strip()]
    comparison = experiment_tracker.compare_runs(ids)
    return comparison


# --- CENTRALIZED TRAINING DATA MANAGEMENT & LINEAGE ---

class DatasetSampleCreateRequest(BaseModel):
    sample: dict


class DatasetVersionCreateRequest(BaseModel):
    version: str
    description: str = ""


@router.get("/datasets")
async def get_training_datasets(dataset_type: str | None = None):
    """List centralized training datasets (SLM Dialogues & RAG Slang Pairs) with version metadata."""
    from app.services.training_data_service import training_data_service
    datasets = training_data_service.list_datasets(dataset_type=dataset_type)
    return {"datasets": datasets}


@router.get("/datasets/{name}")
async def get_training_dataset_details(name: str, version: str | None = None):
    """Get detailed samples and metadata for a specific dataset version."""
    from app.services.training_data_service import training_data_service
    data = training_data_service.get_dataset(name, version=version)
    if not data:
        raise HTTPException(status_code=404, detail=f"Dataset '{name}' not found")
    return {"dataset": data}


@router.post("/datasets/{name}/samples")
async def add_sample_to_dataset(name: str, payload: DatasetSampleCreateRequest):
    """Add a new training dialogue or slang pair to the dataset (Data Annotation / Curation)."""
    from app.services.training_data_service import training_data_service
    try:
        created = training_data_service.add_sample(name, payload.sample)
        return {"status": "created", "sample": created}
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/datasets/{name}/versions")
async def create_dataset_version(name: str, payload: DatasetVersionCreateRequest):
    """Snapshot a new immutable version of the dataset (Data Versioning)."""
    from app.services.training_data_service import training_data_service
    try:
        new_ver = training_data_service.create_new_version(
            dataset_name=name,
            new_version=payload.version,
            description=payload.description,
        )
        return {"status": "created", "version": new_ver}
    except ValueError as err:
        raise HTTPException(status_code=400, detail=str(err))

