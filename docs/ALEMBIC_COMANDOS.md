# Alembic Commands (Quick Reference)

## Docker mode (recommended)

```powershell
# Current migration state
docker exec runcoach_backend python -m alembic current

# Mark migrations as applied without executing SQL
docker exec runcoach_backend python -m alembic stamp head

# Apply pending migrations
docker exec runcoach_backend python -m alembic upgrade head

# Migration history
docker exec runcoach_backend python -m alembic history

# Create migration
docker exec -w /app runcoach_backend python -m alembic revision --autogenerate -m "Describe change"
```

## Local mode (without Docker)

```powershell
cd backend
python -m alembic current
python -m alembic stamp head
python -m alembic upgrade head
```

## Practical notes

- Compose startup does not auto-apply migrations.
- Run `upgrade head` explicitly when schema changes are introduced.
- Use `stamp head` only when DB schema is already aligned manually.
