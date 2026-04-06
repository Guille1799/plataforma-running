# How It Works (End-to-End)

A quick-read document to understand the product logic in a few minutes.

## 1) Authentication Flow

```mermaid
flowchart TD
  userClient["User (Frontend)"] -->|"POST /api/v1/auth/login"| authRouter["AuthRouter"]
  authRouter --> crudLayer["CRUD User Lookup"]
  crudLayer --> userDb[(PostgreSQL users)]
  authRouter --> jwtService["JWT Service"]
  jwtService --> accessToken["AccessToken"]
  jwtService --> refreshToken["RefreshToken"]
  accessToken --> userClient
  refreshToken --> userClient
  userClient -->|"GET /api/v1/auth/me (Bearer token)"| protectedEndpoint["Protected Endpoints"]
```

Key points:
- The system issues `access_token` and `refresh_token`.
- `refresh_token` supports session renewal without forcing a new login.
- Protected routes rely on the authenticated-user dependency.

## 2) Garmin Sync Flow

```mermaid
flowchart TD
  userClient["User (Frontend)"] -->|"POST /api/v1/garmin/connect"| garminRouter["GarminRouter"]
  garminRouter --> garminService["GarminService"]
  garminService --> garminOAuth["Garmin OAuth (garth/garminconnect)"]
  garminOAuth --> tokenStore["Encrypted token/session storage"]
  tokenStore --> userDb[(PostgreSQL users)]

  userClient -->|"POST /api/v1/garmin/sync"| garminRouter
  garminRouter --> garminService
  garminService --> garminApi["Garmin Activities API"]
  garminApi --> fitParser["FIT/Activity parser"]
  fitParser --> workoutsCrud["Workout CRUD"]
  workoutsCrud --> workoutsDb[(PostgreSQL workouts)]
  workoutsDb --> dashboardUi["Dashboard / Workouts UI"]
```

Key points:
- Connect and sync are two different steps.
- Sync persists user workouts (personal training history).
- Connection/sync status is available via `GET /api/v1/garmin/status`.

## 3) Training Plan Flow

```mermaid
flowchart TD
  userClient["User (Frontend Wizard)"] -->|"POST /api/v1/training-plans/generate"| plansRouter["TrainingPlansRouter"]
  plansRouter --> validationLayer["Goal date + volume validation"]
  validationLayer --> planService["TrainingPlanService"]
  planService --> aiProvider["Groq LLM"]
  aiProvider --> planDraft["Plan draft (weeks/sessions)"]
  planDraft --> userPreferences["Persist in user preferences"]
  userPreferences --> userDb[(PostgreSQL users)]
  userDb --> plansRouter
  plansRouter --> userClient
  userClient -->|"GET /api/v1/training-plans/*"| planTracking["Progress/Adherence endpoints"]
```

Key points:
- Plans are generated from goal + target date + current weekly volume.
- Target date is validated before generation.
- Users can list, adapt, and track adherence/progress.

## 4) Data Model Distinction (Important)

```mermaid
flowchart LR
  eventsSeed["Events seed catalog (e.g. 52 races)"] --> eventsDb[(PostgreSQL events)]
  garminSync["User Garmin sync"] --> workoutsDb[(PostgreSQL workouts)]
  uploads["GPX/FIT uploads"] --> workoutsDb
  eventsDb --> planningUi["Race search / planning UI"]
  workoutsDb --> analyticsUi["Performance analytics UI"]
```

- **Events/Races**: catalog used to explore and select goals.
- **Workouts**: real athlete training history.
- If both counts happen to be 52 at some point, that is coincidence, not a data relation.
