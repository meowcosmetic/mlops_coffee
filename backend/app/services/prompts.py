"""DB-backed prompt version store: create, activate, and look up active prompt templates."""
from hashlib import sha256

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import PromptVersion


def compute_hash(template: str) -> str:
    return sha256(template.encode("utf-8")).hexdigest()[:12]


def _validate_template(template: str) -> None:
    try:
        template.format(name="", profile_json="{}")
    except Exception as exc:
        raise ValueError(f"template failed to render: {exc}") from exc


async def create_version(
    db: AsyncSession, *, name: str, template: str, version: str, activate: bool = False
) -> PromptVersion:
    _validate_template(template)
    if activate:
        await db.execute(
            update(PromptVersion).where(PromptVersion.name == name).values(is_active=False)
        )
    row = PromptVersion(
        name=name,
        version=version,
        template=template,
        prompt_hash=compute_hash(template),
        is_active=activate,
    )
    db.add(row)
    await db.flush()
    return row


async def activate_version(db: AsyncSession, version_id: int) -> PromptVersion:
    row = await db.get(PromptVersion, version_id)
    if row is None:
        raise LookupError(f"No prompt version with id {version_id}")
    _validate_template(row.template)
    await db.execute(
        update(PromptVersion).where(PromptVersion.name == row.name).values(is_active=False)
    )
    row.is_active = True
    await db.flush()

    try:
        from app.services import prompt_service
        prompt_service.activate_prompt_version(row.version)
    except Exception:
        pass

    return row


async def get_active_prompt(db: AsyncSession, name: str = "drink-assistant-system") -> PromptVersion:
    row = await db.scalar(
        select(PromptVersion).where(PromptVersion.name == name, PromptVersion.is_active.is_(True))
    )
    if row is None:
        raise LookupError(f"No active prompt version for '{name}'")
    return row
