import pytest
from sqlalchemy import select

from app.models import PromptVersion
from app.services import prompts


async def test_create_version_computes_hash_and_defaults_inactive(db_session):
    row = await prompts.create_version(db_session, name="drink-assistant-system",
                                        template="Hello {name}", version="1.0.0")
    await db_session.commit()

    assert row.prompt_hash == prompts.compute_hash("Hello {name}")
    assert row.is_active is False


async def test_activate_version_deactivates_previous_active_row(db_session):
    first = await prompts.create_version(db_session, name="drink-assistant-system",
                                          template="v1", version="2.0.0", activate=True)
    second = await prompts.create_version(db_session, name="drink-assistant-system",
                                           template="v2", version="2.1.0")
    await db_session.commit()

    await prompts.activate_version(db_session, second.id)
    await db_session.commit()

    refreshed_first = await db_session.get(PromptVersion, first.id)
    refreshed_second = await db_session.get(PromptVersion, second.id)
    assert refreshed_first.is_active is False
    assert refreshed_second.is_active is True


async def test_get_active_prompt_returns_the_active_row(db_session):
    await prompts.create_version(db_session, name="drink-assistant-system",
                                  template="inactive", version="2.0.0")
    active = await prompts.create_version(db_session, name="drink-assistant-system",
                                           template="active", version="2.1.0", activate=True)
    await db_session.commit()

    result = await prompts.get_active_prompt(db_session, name="drink-assistant-system")
    assert result.id == active.id
    assert result.template == "active"


async def test_get_active_prompt_raises_when_none_active(db_session):
    with pytest.raises(LookupError):
        await prompts.get_active_prompt(db_session, name="nonexistent")


async def test_create_version_rejects_malformed_template(db_session):
    with pytest.raises(ValueError):
        await prompts.create_version(db_session, name="drink-assistant-system",
                                      template="Hello {unknown_field}", version="9.0.0")
    await db_session.commit()

    row = await db_session.scalar(
        select(PromptVersion).where(PromptVersion.version == "9.0.0")
    )
    assert row is None


async def test_activate_version_rejects_malformed_template(db_session, monkeypatch):
    # Bypass validation to persist a malformed template directly, simulating a
    # pre-existing bad row (e.g. inserted before validation existed).
    monkeypatch.setattr(prompts, "_validate_template", lambda template: None)
    bad = await prompts.create_version(db_session, name="drink-assistant-system",
                                        template="Hello {unknown_field}", version="9.1.0")
    await db_session.commit()
    monkeypatch.undo()

    with pytest.raises(ValueError):
        await prompts.activate_version(db_session, bad.id)
    await db_session.commit()

    refreshed = await db_session.get(PromptVersion, bad.id)
    assert refreshed.is_active is False
