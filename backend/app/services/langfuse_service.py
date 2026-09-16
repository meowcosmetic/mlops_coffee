"""Langfuse observability client, callback handlers, and runtime log inspector."""
import logging
import os
import time
from collections import deque
from dataclasses import asdict, dataclass, field
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)

# Lưu vết 50 log trace gần nhất trong memory để cấp cho Dashboard/Sidebar trên Frontend
_RECENT_LOGS: deque = deque(maxlen=50)

_langfuse_client = None
_langfuse_handler = None


@dataclass
class LangfuseTraceRecord:
    trace_id: str
    user_id: int | str
    timestamp: str
    model: str
    prompt_name: str
    prompt_version: str
    prompt_hash: str
    system_prompt: str
    input_text: str
    output_text: str
    latency_ms: float
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cost_usd: float
    tools_called: list[str]
    tool_calls_detail: list[dict] = field(default_factory=list)
    success: bool = True
    status: str = "success"
    error: str | None = None
    langfuse_url: str | None = None


def get_langfuse():
    """Lazy initialization of Langfuse client."""
    global _langfuse_client
    if _langfuse_client is not None:
        return _langfuse_client

    if not settings.langfuse_enabled:
        return None

    try:
        from langfuse import Langfuse
        _langfuse_client = Langfuse(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
        )
        logger.info("Langfuse client initialized successfully (%s)", settings.langfuse_host)
        return _langfuse_client
    except Exception as exc:
        logger.warning("Could not initialize Langfuse SDK: %s", exc)
        return None


def get_langfuse_callback(trace_name: str = "drink-chat", user_id: str | None = None, session_id: str | None = None):
    """Return a Langfuse CallbackHandler for LangChain if configured and valid."""
    if not settings.langfuse_enabled:
        return None

    try:
        from langfuse.callback import CallbackHandler
        handler = CallbackHandler(
            public_key=settings.langfuse_public_key,
            secret_key=settings.langfuse_secret_key,
            host=settings.langfuse_host,
            user_id=str(user_id) if user_id else None,
            session_id=str(session_id) if session_id else None,
        )
        return handler
    except Exception as exc:
        logger.debug("Langfuse CallbackHandler not attached: %s", exc)
        return None


def record_trace(
    trace_id: str,
    user_id: int | str,
    model: str,
    prompt_version: str,
    input_text: str,
    output_text: str,
    latency_ms: float,
    input_tokens: int,
    output_tokens: int,
    total_tokens: int,
    cost_usd: float,
    tools_called: list[str],
    prompt_name: str = "drink-assistant-system",
    prompt_hash: str = "",
    system_prompt: str = "",
    tool_calls_detail: list[dict] | None = None,
    success: bool = True,
    error: str | None = None,
):
    """Save trace to local memory queue for immediate UI sidebar inspection and push to Langfuse."""
    now_str = time.strftime("%Y-%m-%d %H:%M:%S")
    langfuse_url = f"{settings.langfuse_host.rstrip('/')}/project/traces/{trace_id}" if settings.langfuse_enabled else None

    record = LangfuseTraceRecord(
        trace_id=trace_id,
        user_id=user_id,
        timestamp=now_str,
        model=model,
        prompt_name=prompt_name,
        prompt_version=prompt_version,
        prompt_hash=prompt_hash,
        system_prompt=system_prompt,
        input_text=input_text,
        output_text=output_text,
        latency_ms=round(latency_ms, 2),
        input_tokens=input_tokens or 0,
        output_tokens=output_tokens or 0,
        total_tokens=total_tokens or 0,
        cost_usd=round(cost_usd or 0.0, 8),
        tools_called=tools_called,
        tool_calls_detail=tool_calls_detail or [],
        success=success,
        status="success" if success else "error",
        error=error,
        langfuse_url=langfuse_url,
    )
    _RECENT_LOGS.appendleft(asdict(record))

    # Async push to remote Langfuse if available
    client = get_langfuse()
    if client:
        try:
            client.trace(
                id=trace_id,
                name="drink-bot-turn",
                user_id=str(user_id),
                metadata={
                    "model": model,
                    "prompt_version": prompt_version,
                    "latency_ms": latency_ms,
                    "tools": tools_called,
                    "environment": "docker-compose",
                },
                input=input_text,
                output=output_text,
            )
        except Exception as err:
            logger.debug("Background Langfuse dispatch warning: %s", err)


def get_recent_traces(limit: int = 20) -> list[dict]:
    """Retrieve recent traces for the frontend inspector sidebar."""
    return list(_RECENT_LOGS)[:limit]


def clear_traces():
    """Clear in-memory traces."""
    _RECENT_LOGS.clear()
