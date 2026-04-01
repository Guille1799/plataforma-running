# Architecture

## System Overview

RunCoach AI is a full-stack platform with:
- Next.js frontend (`app/`, `components/`, `lib/`)
- FastAPI backend (`backend/app/routers`, `backend/app/services`)
- PostgreSQL for persistent domain data
- Celery + Redis for async and scheduled execution
- Groq-backed AI services for plan/recommendation generation

## Core Runtime Flow

1. Frontend sends authenticated requests to FastAPI.
2. Routers validate input and delegate to domain services.
3. Services persist/read domain data via SQLAlchemy models.
4. Background or scheduled tasks run through Celery workers.
5. Results are surfaced back to UI as dashboards, plans, and insights.

## Main Domains

- **Authentication**: JWT-based login, refresh, and user identity.
- **Workouts**: activity ingestion and analysis.
- **Health**: metrics ingestion and trend usage.
- **Training Plans**: AI generation, persistence, adaptation, progress tracking.
- **Events**: race catalog discovery and filtering.

## Why This Architecture

- Clear separation between API handlers and business logic.
- Async processing for heavy sync and periodic jobs.
- Relational model for user-centric history and plan tracking.
- Explicit modular routing enables incremental feature growth.
