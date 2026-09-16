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
async def get_prompts():
    """Get all prompt versions from registry with active status and hashes."""
    prompts = prompt_service.get_all_prompts()
    active = prompt_service.get_active_prompt()
    return {
        "active_version": active.version,
        "prompts": prompts,
    }


@router.post("/prompts/activate")
async def activate_prompt(payload: PromptActivateRequest):
    """Activate or rollback to a prompt version dynamically without redeploying code."""
    try:
        updated = prompt_service.activate_prompt_version(payload.version)
        return {
            "status": "activated",
            "active_version": updated.version,
            "prompt": updated,
        }
    except ValueError as err:
        raise HTTPException(status_code=404, detail=str(err))


@router.post("/prompts")
async def create_prompt(payload: PromptCreateRequest):
    """Register a new prompt version for A/B testing or experimentation."""
    item = prompt_service.register_new_prompt(
        version=payload.version,
        template=payload.template,
        description=payload.description,
        label=payload.label,
        activate=payload.activate,
    )
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


@router.get("/evals/latest")
async def get_latest_eval():
    """Get the most recent benchmark run summary."""
    latest = eval_service.get_latest_benchmark()
    return {"benchmark": latest}




