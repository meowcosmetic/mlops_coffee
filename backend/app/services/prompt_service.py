"""Dynamic Prompt Registry & Version Management.

Supports:
- Dynamic prompt fetching without redeploying code.
- Version management (SemVer, SHA256 hashes, release notes).
- Instant Rollback & A/B testing switching on runtime.
- Langfuse Prompt Registry synchronization when Langfuse is connected.
"""
import logging
import time
from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import Any


from app.config import settings

logger = logging.getLogger(__name__)

V1_0_0_TEMPLATE = """You are a polite drink assistant chatting with {name}.
Known preferences: {profile_json}
Recommend drinks from the menu and help the customer place orders.
Always check for allergies and never recommend items containing allergens.
"""

V1_1_0_TEMPLATE = """You are a friendly drink shop assistant chatting with {name}.

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
- Reply in the same language the customer writes in, and keep replies short and conversational.
"""

V1_2_0_AB_TEST_TEMPLATE = """You are a lively, enthusiastic drink barista assisting {name}!

Customer profile:
{profile_json}

Tools available: update_profile, recommend_drink, order.

Special Guidelines (A/B Test Variant - Fast & Dynamic Upsell):
- Be energetic, warm, and concise (under 3 sentences per response).
- Prioritize seasonal drinks (iced, refreshing fruit teas and cold brew).
- STRICT SAFETY: Never recommend any drink with declared allergens.
- Create an order preview whenever the customer shows interest in an item.
- Answer in Vietnamese naturally like a modern youthful coffee shop.
"""


@dataclass
class PromptVersionItem:
    name: str
    version: str
    label: str  # production | staging | ab_test
    template: str
    description: str
    prompt_hash: str
    is_active: bool
    source: str = "local_registry"  # local_registry | langfuse_cloud


# In-memory dynamic prompt registry
_REGISTRY: dict[str, PromptVersionItem] = {}


def _hash_template(tpl: str) -> str:
    return sha256(tpl.strip().encode("utf-8")).hexdigest()[:12]


def _init_default_prompts():
    global _REGISTRY
    if _REGISTRY:
        return

    _REGISTRY["1.0.0"] = PromptVersionItem(
        name="drink-assistant-system",
        version="1.0.0",
        label="deprecated",
        template=V1_0_0_TEMPLATE,
        description="Prompt gốc ban đầu - Tư vấn cơ bản theo kịch bản",
        prompt_hash=_hash_template(V1_0_0_TEMPLATE),
        is_active=False,
    )

    _REGISTRY["1.1.0"] = PromptVersionItem(
        name="drink-assistant-system",
        version="1.1.0",
        label="production",
        template=V1_1_0_TEMPLATE,
        description="Phiên bản chuẩn Production - Hỗ trợ đầy đủ 3 tools & kiểm tra dị ứng nghiêm ngặt",
        prompt_hash=_hash_template(V1_1_0_TEMPLATE),
        is_active=True,
    )

    _REGISTRY["1.2.0-ab-test"] = PromptVersionItem(
        name="drink-assistant-system",
        version="1.2.0-ab-test",
        label="ab_test",
        template=V1_2_0_AB_TEST_TEMPLATE,
        description="Biến thể thử nghiệm A/B - Phong cách Barista năng động, tư vấn siêu ngắn gọn",
        prompt_hash=_hash_template(V1_2_0_AB_TEST_TEMPLATE),
        is_active=False,
    )


_init_default_prompts()


def get_all_prompts() -> list[dict]:
    """Return all prompt versions in registry."""
    _init_default_prompts()
    return [asdict(item) for item in _REGISTRY.values()]


_LF_LAST_CHECK: float = 0.0
_LF_CACHED_REMOTE_PROMPT: PromptVersionItem | None = None


def get_active_prompt() -> PromptVersionItem:
    """Return currently active prompt. Attempts to check Langfuse Prompt Registry if online."""
    global _LF_LAST_CHECK, _LF_CACHED_REMOTE_PROMPT
    _init_default_prompts()

    # Try sync with Langfuse Prompt Registry if configured (check at most once every 5 mins)
    now = time.time()
    if settings.langfuse_enabled and (now - _LF_LAST_CHECK > 300):
        _LF_LAST_CHECK = now
        try:
            from app.services.langfuse_service import get_langfuse
            client = get_langfuse()
            if client:
                lf_prompt = client.get_prompt("drink-assistant-system", label="production")
                if lf_prompt and hasattr(lf_prompt, "prompt"):
                    h = _hash_template(lf_prompt.prompt)
                    _LF_CACHED_REMOTE_PROMPT = PromptVersionItem(
                        name="drink-assistant-system",
                        version=getattr(lf_prompt, "version", "langfuse-cloud"),
                        label="production",
                        template=lf_prompt.prompt,
                        description="Fetched dynamically from Langfuse Prompt Registry",
                        prompt_hash=h,
                        is_active=True,
                        source="langfuse_cloud",
                    )
        except Exception as exc:
            logger.debug("Langfuse Prompt Registry fetch skipped (using local registry): %s", exc)
            _LF_CACHED_REMOTE_PROMPT = None

    if _LF_CACHED_REMOTE_PROMPT:
        return _LF_CACHED_REMOTE_PROMPT

    for item in _REGISTRY.values():
        if item.is_active:
            return item


    # Fallback default
    return _REGISTRY.get("1.1.0", list(_REGISTRY.values())[0])


def get_prompt_by_version(version: str | None) -> PromptVersionItem | None:
    """Return a prompt version item by version string, or None if not found."""
    if not version:
        return None
    _init_default_prompts()
    return _REGISTRY.get(version)



def activate_prompt_version(version: str) -> PromptVersionItem:
    """Set a specific prompt version as active (instant rollback / A/B switch)."""
    _init_default_prompts()
    if version not in _REGISTRY:
        raise ValueError(f"Prompt version '{version}' not found in registry.")

    for k, item in _REGISTRY.items():
        item.is_active = (k == version)
        if item.is_active:
            item.label = "production"
        elif item.label == "production":
            item.label = "staged"

    logger.info("Prompt version switched to '%s'", version)
    return _REGISTRY[version]


def register_new_prompt(version: str, template: str, description: str, label: str = "staging", activate: bool = False) -> PromptVersionItem:
    """Add a new prompt version to registry for testing or rollout."""
    _init_default_prompts()
    h = _hash_template(template)
    item = PromptVersionItem(
        name="drink-assistant-system",
        version=version.strip(),
        label=label.strip(),
        template=template.strip(),
        description=description.strip(),
        prompt_hash=h,
        is_active=activate,
    )
    if activate:
        for it in _REGISTRY.values():
            it.is_active = False
    _REGISTRY[version] = item
    return item
