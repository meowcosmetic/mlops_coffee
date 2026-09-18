import json
import logging
import os
import time
import uuid
from dataclasses import dataclass
from functools import lru_cache

from langchain_openai import ChatOpenAI

from app.config import settings

logger = logging.getLogger(__name__)

OLLAMA_BASE_URL = os.environ.get(
    "OLLAMA_BASE_URL",
    "http://host.docker.internal:11434/v1" if os.path.exists("/.dockerenv") else "http://127.0.0.1:11434/v1",
)


@dataclass(frozen=True)
class LLMUsage:
    input_tokens: int | None = None
    output_tokens: int | None = None
    total_tokens: int | None = None
    estimated_cost_usd: float | None = None


@dataclass(frozen=True)
class LLMInvocation:
    response: object
    usage: LLMUsage

    def __getattr__(self, name: str):
        return getattr(self.response, name)

@lru_cache
def get_chat_model(model_name: str | None = None) -> ChatOpenAI:
    req_model = model_name or settings.openai_model

    # 1. Local SLM & Ollama Models (0đ cost, 100% offline, NO cloud API key needed)
    if (
        req_model.startswith("drinkbot-slm-")
        or "lora" in req_model.lower()
        or req_model.startswith("gemma")
        or req_model.startswith("qwen")
    ):
        ollama_model = "gemma4:e4b"
        if req_model in ("gemma4:12b", "gemma4:e4b", "qwen3:8b"):
            ollama_model = req_model

        logger.info(
            "Routing to Local Ollama Inference (0đ cost): model=%s via %s",
            ollama_model,
            OLLAMA_BASE_URL,
        )
        return ChatOpenAI(
            model=ollama_model,
            api_key="ollama",
            base_url=OLLAMA_BASE_URL,
            temperature=0.7,
        )

    # 2. Cloud Foundation Models (Gemini / OpenAI)
    return ChatOpenAI(
        model=req_model,
        api_key=settings.openai_api_key or "no-key-provided",
        base_url=settings.openai_base_url,
        temperature=1,
    )


def invoke(model, messages, version=None):
    """Invoke a model and emit redacted operational metadata as one JSON log event.

    `version` is an `app.llm_versions.LLMVersion` describing the active prompt/model,
    fetched by the caller (the DB is the source of truth, not a hardcoded constant).
    """
    if version is None:
        from app.llm_versions import current_version
        version = current_version()
    request_id = str(uuid.uuid4())
    started = time.perf_counter()
    try:
        response = model.invoke(messages)
    except Exception as exc:
        logger.warning("Primary model invocation failed (%s). Attempting intelligent fallback...", exc)
        # Fallback 1: If cloud model failed (no API key, 404, rate limit), fallback to Local Ollama!
        try:
            from app.services.agent import TOOL_SCHEMAS
            fallback_ollama = ChatOpenAI(
                model="gemma4:e4b",
                api_key="ollama",
                base_url=OLLAMA_BASE_URL,
                temperature=0.7,
            ).bind_tools(TOOL_SCHEMAS)
            response = fallback_ollama.invoke(messages)
            logger.info("Successfully recovered using Local Ollama (gemma4:e4b)!")
        except Exception:
            # Fallback 2: If Ollama failed and cloud key is present, fallback to cloud
            if settings.openai_api_key:
                try:
                    fallback_cloud = ChatOpenAI(
                        model=settings.openai_model,
                        api_key=settings.openai_api_key,
                        base_url=settings.openai_base_url,
                        temperature=1,
                    ).bind_tools(TOOL_SCHEMAS)
                    response = fallback_cloud.invoke(messages)
                    logger.info("Successfully recovered using Cloud Model (%s)!", settings.openai_model)
                except Exception:
                    logger.exception(json.dumps({
                        "event": "llm_invocation",
                        "request_id": request_id,
                        "provider": version.provider,
                        "model": version.model,
                        "prompt_name": version.prompt_name,
                        "prompt_version": version.prompt_version,
                        "prompt_hash": version.prompt_hash,
                        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                        "success": False,
                        "error_type": type(exc).__name__,
                    }))
                    raise exc
            else:
                logger.exception(json.dumps({
                    "event": "llm_invocation",
                    "request_id": request_id,
                    "provider": version.provider,
                    "model": version.model,
                    "prompt_name": version.prompt_name,
                    "prompt_version": version.prompt_version,
                    "prompt_hash": version.prompt_hash,
                    "latency_ms": round((time.perf_counter() - started) * 1000, 2),
                    "success": False,
                    "error_type": type(exc).__name__,
                }))
                raise exc

    usage = getattr(response, "response_metadata", {}).get("token_usage", {})
    input_tokens = usage.get("prompt_tokens")
    output_tokens = usage.get("completion_tokens")
    estimated_cost = None
    if isinstance(input_tokens, int) and isinstance(output_tokens, int):
        estimated_cost = round(
            (input_tokens / 1_000_000) * settings.llm_input_cost_per_million
            + (output_tokens / 1_000_000) * settings.llm_output_cost_per_million,
            8,
        )
    logger.info(json.dumps({
        "event": "llm_invocation",
        "request_id": request_id,
        "provider": version.provider,
        "model": version.model,
        "prompt_name": version.prompt_name,
        "prompt_version": version.prompt_version,
        "prompt_hash": version.prompt_hash,
        "latency_ms": round((time.perf_counter() - started) * 1000, 2),
        "success": True,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": usage.get("total_tokens"),
        "estimated_cost_usd": estimated_cost,
    }))
    return LLMInvocation(
        response=response,
        usage=LLMUsage(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=usage.get("total_tokens"),
            estimated_cost_usd=estimated_cost,
        ),
    )
