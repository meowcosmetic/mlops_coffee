"""Immutable metadata for the prompts and models used by the chat agent."""

from dataclasses import dataclass

from app.config import settings

DEFAULT_SYSTEM_PROMPT_VERSION = "1.2.0"
DEFAULT_SYSTEM_PROMPT_NAME = "drink-assistant-system"
DEFAULT_SYSTEM_PROMPT_TEMPLATE = """You are a friendly drink shop assistant chatting with {name}.

Current known profile (may be incomplete):
{profile_json}

You have three tools: update_profile, recommend_drink, and order (see their descriptions).

Rules:
- If tastes, drink types, temperature, caffeine, or allergy info is missing, naturally ask about
  it in conversation (a question or two at a time) instead of reciting a rigid checklist.
- Never recommend or order a drink that contains one of the customer's declared allergens.
- Only reference drinks by the exact names returned by recommend_drink.
- The order tool creates a pending preview only. Never say an order is placed until the
    customer confirms it using the confirmation controls in the chat.
- The update_profile tool stages a pending change only. Never say preferences are saved until
    the customer confirms them using the confirmation controls in the chat.
- Reply in the same language the customer writes in, and keep replies short and conversational.
"""


@dataclass(frozen=True)
class LLMVersion:
    provider: str
    model: str
    prompt_name: str
    prompt_version: str
    prompt_hash: str


SYSTEM_PROMPT_VERSION = DEFAULT_SYSTEM_PROMPT_VERSION
SYSTEM_PROMPT_NAME = DEFAULT_SYSTEM_PROMPT_NAME
SYSTEM_PROMPT_TEMPLATE = DEFAULT_SYSTEM_PROMPT_TEMPLATE


def build_version(prompt) -> LLMVersion:
    """Build an `LLMVersion` from an active `PromptVersion` DB row."""
    return LLMVersion(
        provider=settings.llm_provider,
        model=settings.openai_model,
        prompt_name=prompt.name,
        prompt_version=prompt.version,
        prompt_hash=prompt.prompt_hash,
    )


def current_version() -> LLMVersion:
    """Build a default `LLMVersion` based on settings and default prompt template."""
    import hashlib
    h = hashlib.sha256(DEFAULT_SYSTEM_PROMPT_TEMPLATE.encode("utf-8")).hexdigest()[:16]
    return LLMVersion(
        provider=settings.llm_provider,
        model=settings.openai_model,
        prompt_name=DEFAULT_SYSTEM_PROMPT_NAME,
        prompt_version=DEFAULT_SYSTEM_PROMPT_VERSION,
        prompt_hash=h,
    )
