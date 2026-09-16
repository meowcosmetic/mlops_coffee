from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import PromptVersion
from app.routers.menu import require_admin
from app.schemas import PromptVersionCreate, PromptVersionOut
from app.services import prompts

router = APIRouter(prefix="/prompts", tags=["prompts"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[PromptVersionOut])
async def list_versions(name: str, db: AsyncSession = Depends(get_db)):
    rows = await db.scalars(
        select(PromptVersion).where(PromptVersion.name == name).order_by(PromptVersion.id)
    )
    return list(rows)


@router.post("", response_model=PromptVersionOut, status_code=status.HTTP_201_CREATED)
async def create_version(payload: PromptVersionCreate, db: AsyncSession = Depends(get_db)):
    row = await prompts.create_version(
        db, name=payload.name, template=payload.template, version=payload.version, activate=payload.activate
    )
    await db.commit()
    await db.refresh(row)
    return row


@router.post("/{version_id}/activate", response_model=PromptVersionOut)
async def activate_version(version_id: int, db: AsyncSession = Depends(get_db)):
    try:
        row = await prompts.activate_version(db, version_id)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    await db.commit()
    await db.refresh(row)
    return row
