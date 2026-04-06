# Required Environment Variables (Render and Vercel)

## Render (backend)

Required:
- `ENVIRONMENT=production`
- `DATABASE_URL=postgresql://...`
- `SECRET_KEY=<32+ chars>`
- `ALGORITHM=HS256`

Recommended:
- `GROQ_API_KEY=<key>`
- `ALLOWED_ORIGINS=https://plataforma-running.vercel.app`

## Vercel (frontend)

Required:
- `NEXT_PUBLIC_API_URL=https://plataforma-running.onrender.com`

## Verification checklist

1. Confirm variables in platform dashboards.
2. Redeploy both services after env updates.
3. Verify API health endpoint and frontend runtime calls.
4. Check latest monitoring workflow run for status.
