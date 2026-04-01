# Copilot Instructions - RunCoach AI

These instructions keep implementation and documentation aligned with current project reality.

## Reference state

- Frontend: Next.js 16 + React 19 + TypeScript
- Backend: FastAPI + PostgreSQL + SQLAlchemy
- Async: Celery + Redis
- AI: Groq (Llama 3.3)
- Local startup: `start-dev.ps1` / `stop-dev.ps1`

## Development rules

1. Prefer small, verifiable, high-impact changes.
2. Keep code and docs consistent after each change.
3. Never commit secrets or credentials.
4. Prefer explicit typing and clear validation.
5. If a critical flow changes, update checks/tests and docs.

## Minimum quality baseline

Frontend:
- `npm run lint`
- `npm run typecheck`
- `npm run build`

Backend:
- `pytest` from `backend/`

## Collaboration conventions

- Commit message prefixes:
  - `feat:`
  - `fix:`
  - `docs:`
  - `chore:`
- Prefer focused PRs with short impact-driven descriptions.
