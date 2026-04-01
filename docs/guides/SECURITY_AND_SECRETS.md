# Security and Secrets

## Secrets Handling

- Never commit `.env` files with real values.
- Keep `.env.example` as the public template.
- Validate environment requirements in startup/config.

## Authentication Security

- JWT access/refresh token pattern
- Protected endpoints resolved via authenticated-user dependency
- Server-side token validation for all protected operations

## Integration Credentials

- Third-party integration credentials/tokens are stored server-side.
- Sensitive values are encrypted before persistence where applicable.

## Reporting Issues

If you find a vulnerability, follow [`../../SECURITY.md`](../../SECURITY.md).
