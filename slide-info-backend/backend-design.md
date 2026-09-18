# Backend design findings (as of 2026-09-17, `backend` branch)

## Stack
FastAPI + SQLAlchemy async (asyncpg) + Alembic + Postgres, JWT auth (phone-only,
no password/OTP — login just checks phone exists), LangChain (`langchain-openai`)
tool-calling agent. Dockerfiles exist for both `backend/` and `frontend/`, plus a
root `docker-compose.yml` wiring postgres + backend + frontend + adminer.
Tests: 560 lines across auth, chat flow, allergen safety, menu, phone validation,
LLM telemetry (all in `backend/tests/`).

## Domain model (app/models.py)
`User` (phone/name/address — the collected entities from the topic), `UserPreference`
(tastes, drink_types, temperature, caffeine, allergies, dietary_restrictions),
`MenuItem`, `ChatMessage` (role, content, **model_name, input/output/total_tokens,
estimated_cost_usd**), `Favorite`, `Order`/`OrderItem` (status: pending → placed/cancelled).
New on `backend` branch: `PromptVersion` (id, name, version, template, prompt_hash,
is_active, created_at — unique on name+version) and `PendingPreferenceChange`
(id, user_id, changes JSON, status: pending → confirmed/cancelled, created_at).

## Chat agent (app/services/agent.py)
Tool-calling loop (max 4 iterations) with three tools: `update_profile`,
`recommend_drink`, `order`. Business rules (allergen exclusion, exact-name/price
validation) are enforced in Python tool executors, never trusted to the model.
`order` only ever creates a **pending** order; a separate `/chat/orders/{id}/confirm`
endpoint requires explicit user confirmation before it becomes `placed`.
`update_profile` now follows the same pattern (added on `backend` branch): it stages
a `PendingPreferenceChange` row instead of writing `UserPreference` directly, and
`POST /api/chat/preferences/{id}/confirm` (`GET /api/chat/preferences/pending` to list)
applies or discards it. So both irreversible/user-facing writes — orders and profile
changes — now go through human-in-the-loop approval; only `recommend_drink` is immediate
(read-only, so no gate needed).

## LLM plumbing (app/services/llm.py, app/llm_versions.py, app/services/prompts.py)
- Model client: `ChatOpenAI` from `langchain-openai`, hitting OpenAI's API directly
  (`openai_base_url` config, default `api.openai.com`). **No AWS Bedrock / VPC
  endpoint integration exists today.**
- Per-invocation telemetry unchanged: request id, provider, model, prompt_name/version/hash,
  latency, success/error, token usage, estimated cost — one structured JSON log line
  per call, token usage + model name also persisted per-`ChatMessage` row.
- **Prompt versioning is now DB-backed** (was the biggest labeling-vs-control gap,
  now closed). `app/services/prompts.py` provides `create_version`, `activate_version`
  (deactivates all other rows for that `name`), `get_active_prompt`, `compute_hash`.
  `agent.py`/`main.py` fetch the active `PromptVersion` per turn/health-check instead
  of importing a constant. `llm_versions.py` keeps only `DEFAULT_SYSTEM_PROMPT_*`
  (used to seed the first row) and `build_version()` to turn a `PromptVersion` row
  into the `LLMVersion` passed into `llm.invoke(model, messages, version)` (version
  is now an explicit required arg, not fetched internally).
  Admin surface: `POST /api/prompts` (create version), `GET /api/prompts?name=...`
  (list/history), `POST /api/prompts/{id}/activate` (roll forward/back) — all behind
  `require_admin` (same dependency `menu.py` uses). This gives real history + rollback,
  not just a hash label.

## Coverage vs. the workshop topic + team comments

| Ask | Status |
|---|---|
| Collect name/phone/address, push to DB | Done (`RegisterRequest` → `User` row) |
| Recommend detox/coffee/protein drinks | Done — seed data now includes a `"protein"` category (3 shakes) and a second `"detox"`-tagged item, alongside existing cafe/tea/fruit-juice items |
| Log chat history to track accuracy | Partial — messages + token/cost stored; no accuracy/feedback signal captured (no thumbs up/down, no eval harness) |
| app → VPC endpoint → Bedrock | **Not started** — currently OpenAI direct. This is the biggest remaining gap vs. comment #1 |
| Docker for BE/FE | **Already done** (comment #2 appears satisfied) |
| Model tracking: model + tokens per message | **Already done** (`ChatMessage` columns + JSON logs) |
| Prompt version control | **Done** — DB-backed `PromptVersion` store with real history + activate/rollback via admin endpoints (comment #4 now satisfied) |
| AI agent with human approval | **Done** — order confirmation and profile-preference confirmation both require explicit user approval before applying |
