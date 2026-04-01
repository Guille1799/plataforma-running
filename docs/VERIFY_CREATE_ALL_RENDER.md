# Verify `create_all` Is Not Used in Render

## Objective

Ensure production uses Alembic migrations instead of SQLAlchemy `create_all()`.

## What to verify

1. In Render service environment:
   - `ENVIRONMENT=production`
2. In Render logs at startup:
   - Confirm production migration messaging
   - Ensure no development-only schema auto-create path is triggered

## Recommended start command

If your deployment path does not run migrations automatically, use:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## Why this matters

- Prevents schema drift between environments
- Keeps DB evolution auditable through migration history
- Avoids accidental table creation behavior in production
