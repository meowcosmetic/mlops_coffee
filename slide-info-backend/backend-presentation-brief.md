# Backend Section — Presentation Outline Brief

Input for whoever builds the full deck. Content only, no slide styling/layout
prescribed — keep visual design consistent with the rest of the deck.

## Section goal

Show how the backend implements the workshop brief (chatbot that collects
name/phone/address, recommends detox/coffee/protein drinks, persists to a
DB) and where it stands against the MLOps asks (prompt/model versioning,
chat history logging for accuracy). Be honest about partial/not-started
items — this is a status update, not a victory lap.

## Suggested flow (slide-by-slide beats)

1. **Stack at a glance**
   - FastAPI + SQLAlchemy (async, asyncpg) + Alembic + Postgres
   - JWT auth, phone-only login (no password/OTP — note this is a
     deliberate simplification, flag as a discussion point if asked)
   - LangChain tool-calling agent on top of OpenAI
   - Dockerized (backend, frontend, root compose w/ postgres + adminer)
   - 560 lines of tests covering auth, chat flow, allergen safety, menu,
     phone validation, LLM telemetry

2. **Domain model / data collection**
   - `User` holds the entities the brief asks for: phone, name, address
   - `UserPreference` for taste profile (drink types, temperature,
     caffeine, allergies, dietary restrictions)
   - `MenuItem`, `ChatMessage`, `Favorite`, `Order`/`OrderItem`
   - Ties directly to brief requirement: "collect entities, push to DB" — done

3. **The chat agent**
   - Tool-calling loop, 3 tools: `update_profile`, `recommend_drink`, `order`
   - Key design point: business rules (allergen exclusion, price/name
     validation) enforced in Python, not trusted to the LLM
   - Human-in-the-loop: orders are created `pending` and require an
     explicit `/confirm` call before becoming `placed` — this is the
     project's one real approval gate, and it's for the one irreversible
     action (spending money)

4. **LLM plumbing & telemetry**
   - `ChatOpenAI` via langchain-openai, hitting OpenAI directly
   - Per-call structured JSON log: request id, provider, model,
     prompt name/version/hash, latency, success/error, tokens, cost
   - Token usage + model name also persisted per `ChatMessage` row —
     this is the "log chat history" + "track model usage" ask, done
   - Prompt versioning exists today via a manually-bumped version
     constant and a sha256 hash for drift detection — not yet a full
     store with history/diff/rollback (see scorecard below)

5. **Scorecard vs. the brief — be direct about gaps**
   | Ask | Status |
   |---|---|
   | Collect name/phone/address → DB | Done |
   | Recommend detox/coffee/protein drinks | Partial (category is free text; seed data not verified) |
   | Log chat history to track accuracy | Partial (tokens/cost stored, no accuracy/feedback signal) |
   | App → VPC endpoint → Bedrock | Not started (currently OpenAI direct — biggest gap) |
   | Docker for BE/FE | Done |
   | Model/token tracking per message | Done |
   | Prompt version control | Partial (version constant + hash for drift detection; system prompt is still a single hardcoded template, no store/history/diff/rollback) |
   | AI agent with human approval | Partial (order confirm exists; profile updates/recommendations apply immediately) |

6. **Closing / what's next (optional, for Q&A)**
   - Biggest gap: no Bedrock/VPC integration yet
   - Next likely priorities: real prompt store, accuracy/feedback capture,
     approval step for profile/recommendation actions if desired

## Notes for the deck builder

- Keep the scorecard table — it's the most useful artifact for the
  full presentation's "status" narrative.
- Don't oversell "Done" items; every "Done" above is backed by a
  specific file/model, verifiable in `backend-design.md`.
- No slide count / theme / color guidance given intentionally — leave
  that to whoever owns overall deck styling.
