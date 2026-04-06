# Supabase Circuit Breaker Fix

## Error

`Circuit breaker open: Too many authentication errors`

## What it means

Supabase is temporarily blocking connections due to repeated auth failures.

## Common causes

- Invalid `DATABASE_URL` credentials
- Using direct DB connection instead of Session Pooler
- Reset password not propagated to Render
- Supabase project paused

## Recovery checklist

1. Confirm Supabase project is active.
2. Copy Session Pooler connection string from Supabase dashboard.
3. Update `DATABASE_URL` in Render exactly.
4. Ensure `ENVIRONMENT=production` in Render.
5. Wait 5-15 minutes for breaker reset.
6. Redeploy and verify `/health`.

## Correct connection style

Use Session Pooler URL format:

```text
postgresql://postgres.[PROJECT_REF]:[PASSWORD]@aws-[REGION].pooler.supabase.com:5432/postgres
```

Do not use direct host connection for this setup.
