"""Router providing operational and trace telemetry for Langfuse and frontend inspector."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.config import settings
from app.services import langfuse_service, prompt_service

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

