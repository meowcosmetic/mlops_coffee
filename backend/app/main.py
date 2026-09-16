from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.llm_versions import build_version
from app.routers import auth, chat, menu, users
from app.services import prompts

app = FastAPI(
    title="chatBotDrinkRecommendation",
    description="Personalized drink recommendations powered by Langchain + OpenAI.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# All routes live under /api so the frontend can proxy a single path prefix
app.include_router(auth.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(menu.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.get("/api/health", tags=["health"])
async def health(db: AsyncSession = Depends(get_db)):
    prompt_row = await prompts.get_active_prompt(db)
    version = build_version(prompt_row)
    return {
        "status": "ok",
        "llm_provider": version.provider,
        "llm_model": version.model,
        "prompt_name": version.prompt_name,
        "prompt_version": version.prompt_version,
        "prompt_hash": version.prompt_hash,
    }
