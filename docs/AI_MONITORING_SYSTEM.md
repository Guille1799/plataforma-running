# AI Monitoring Context

## Goal

Provide machine-readable production status so assistants can reason about uptime and failures without manual log sharing.

## Mechanism

1. `monitor-production.yml` checks production endpoints.
2. Workflow writes `docs/PRODUCTION_STATUS.md`.
3. Assistants read this file as context for support/debugging conversations.

## Data produced

`docs/PRODUCTION_STATUS.md` includes:
- timestamp
- commit SHA
- workflow run URL
- per-service status, latency, and errors

## Caveat

The file is a snapshot, not a live health feed. Always verify latest Actions run for real-time state.
