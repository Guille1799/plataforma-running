# Contributing

Gracias por tu interes en mejorar RunCoach AI.

## Flujo recomendado

1. Crea una rama por cambio: `feature/...`, `fix/...`, `docs/...`, `chore/...`.
2. Mantiene cada PR enfocada en un solo objetivo.
3. Antes de abrir PR ejecuta:

```powershell
npm run check
cd backend
pytest tests/ -v --tb=short
```

## Convencion de commits

Usa mensajes cortos y orientados a impacto:

- `feat: add Garmin sync retry guard`
- `fix: avoid token refresh loop on expired session`
- `docs: align quickstart with powershell scripts`
- `chore: add frontend typecheck to CI`

## Pull Requests

Incluye en la descripcion:

- Contexto del problema
- Cambio aplicado
- Como validarlo localmente
- Riesgos o limitaciones conocidas

## Seguridad

No subas secretos (`.env`, claves API, tokens).  
Si detectas una vulnerabilidad, sigue [`SECURITY.md`](SECURITY.md).
