# 📡 RunCoach AI - API Endpoints Reference

**Base URL**: `http://127.0.0.1:8000`

**Authentication**: All endpoints except `/auth/*` require `Authorization: Bearer {token}` header.

---

## 🔐 Authentication (`/api/v1/auth`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/register` | Create new user account | ❌ |
| `POST` | `/login` | Login and get JWT tokens | ❌ |
| `POST` | `/refresh` | Refresh access token | ✅ |
| `GET` | `/me` | Get current user profile | ✅ |

---

## 🏃 Workouts (`/api/v1/workouts`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | List workouts (paginated) | ✅ |
| `GET` | `/{workout_id}` | Get workout details | ✅ |
| `POST` | `/` | Create workout manually | ✅ |
| `PUT` | `/{workout_id}` | Update workout | ✅ |
| `DELETE` | `/{workout_id}` | Delete workout | ✅ |

**Query Parameters (GET /)**:
- `skip` (int): Pagination offset (default: 0)
- `limit` (int): Max results (default: 20, max: 100)
- `start_date` (ISO datetime): Filter from date
- `end_date` (ISO datetime): Filter to date

---

## 🌐 Garmin Integration (`/api/v1/garmin`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/connect` | Connect Garmin account | ✅ |
| `POST` | `/sync` | Sync Garmin activities | ✅ |
| `GET` | `/status` | Check connection status | ✅ |
| `DELETE` | `/disconnect` | Disconnect Garmin account | ✅ |

**POST /connect** Body:
```json
{
  "email": "garmin@email.com",
  "password": "password123"
}
```

**POST /sync** Query Parameters:
- `days` (int): Sync last N days (default: 7, max: 30)

---

## 🚴 Strava Integration (`/api/v1/strava`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/auth-url` | Get OAuth authorization URL | ✅ |
| `POST` | `/connect` | Connect with auth code | ✅ |
| `POST` | `/sync` | Sync Strava activities | ✅ |
| `GET` | `/status` | Check connection status | ✅ |
| `DELETE` | `/disconnect` | Disconnect Strava account | ✅ |

**OAuth Flow**:
1. `GET /auth-url` → Returns authorization URL
2. User authorizes on Strava → Redirected with `code`
3. `POST /connect` with code → Stores tokens

**POST /connect** Body:
```json
{
  "code": "authorization_code_from_strava"
}
```

---

## 📤 File Upload (`/api/v1/upload`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/workout` | Upload FIT/GPX/TCX file | ✅ |
| `GET` | `/supported-formats` | List supported formats | ✅ |

**POST /workout**:
- Content-Type: `multipart/form-data`
- Field: `file`
- Supported: `.fit`, `.gpx`, `.tcx`
- Max size: 10MB

**⚡ AUTO-CONVERSION:**
RunCoach detecta automáticamente archivos GPX (Xiaomi, Amazfit, Polar) y los convierte a FIT en memoria para extraer métricas avanzadas. La conversión es **transparente** - solo sube tu GPX y el sistema hace el resto.

**Métricas extraídas de GPX:**
- Distancia GPS (Haversine)
- Pace y velocidad
- Frecuencia cardíaca (si está en GPX)
- Elevación y desnivel
- Timestamps GPS

**Example (curl)**:
```bash
# Upload GPX from Xiaomi/Amazfit - auto-converts to FIT
curl -X POST "http://127.0.0.1:8000/api/v1/upload/workout" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@zepp_workout.gpx"

# Upload FIT from Garmin - direct parsing
curl -X POST "http://127.0.0.1:8000/api/v1/upload/workout" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@garmin_workout.fit"
```

---

## 👤 Athlete Profile (`/api/v1/profile`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `PUT` | `/goals` | Update goals | ✅ |
| `PUT` | `/preferences` | Update preferences | ✅ |
| `PUT` | `/physical` | Update physical stats | ✅ |

**PUT /goals** Body:
```json
{
  "goals": [
    {
      "type": "race",
      "target": "Sub-4:00 marathon",
      "deadline": "2026-04-15"
    }
  ]
}
```

**PUT /physical** Body:
```json
{
  "max_heart_rate": 185,
  "height_cm": 175.0,
  "weight_kg": 70.0
}
```

---

## 🤖 AI Coach (`/api/v1/coach`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/chat` | Chat with AI coach | ✅ |
| `GET` | `/chat/history` | Get conversation history | ✅ |
| `DELETE` | `/chat/history` | Clear conversation | ✅ |
| `POST` | `/analyze/{workout_id}` | Quick workout analysis | ✅ |
| `POST` | `/analyze-deep/{workout_id}` | Deep 5-section analysis | ✅ |
| `POST` | `/analyze-form/{workout_id}` | Running form analysis | ✅ |
| `POST` | `/plan` | Generate weekly plan | ✅ |
| `GET` | `/hr-zones` | Calculate HR zones | ✅ |

**POST /chat** Body:
```json
{
  "message": "How should I prepare for my marathon?"
}
```

**POST /plan** Body:
```json
{
  "start_date": "2025-11-18",
  "goal_type": "half_marathon",
  "target_volume_km": 40
}
```

**GET /hr-zones** Query Parameters:
- `max_hr` (int): Maximum heart rate

---

## 📋 Training Plans (`/api/v1/training-plans`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/generate` | Generate training plan | ✅ |
| `GET` | `/` | List all plans | ✅ |
| `GET` | `/{plan_id}` | Get plan details | ✅ |
| `POST` | `/{plan_id}/adapt` | Adapt plan to progress | ✅ |
| `PUT` | `/{plan_id}/status` | Update plan status | ✅ |
| `DELETE` | `/{plan_id}` | Delete plan | ✅ |

**POST /generate** Body:
```json
{
  "goal_type": "half_marathon",
  "goal_date": "2026-04-15T09:00:00Z",
  "current_weekly_km": 30.0,
  "weeks": 12,
  "notes": "Previous knee injury, prefer flat terrain"
}
```

**Goal Types**:
- `5k`, `10k`, `15k`, `half_marathon`, `marathon`
- `fitness`, `base_building`

**POST /{plan_id}/adapt** Body:
```json
{
  "plan_id": "plan_abc123",
  "feedback": "Feeling fatigued, need more recovery"
}
```

**PUT /{plan_id}/status** Query Parameters:
- `status`: `active`, `completed`, `paused`

---

## 🏁 Race Predictions (`/api/v1/predictions`)

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/race-times` | Predict all race times | ✅ |
| `GET` | `/vdot` | Calculate VDOT score | ✅ |
| `GET` | `/training-paces` | Get pace zones | ✅ |
| `GET` | `/distances` | List supported distances | ✅ |

**POST /race-times** Body (optional):
```json
{
  "base_distance_km": 10.0,
  "base_time_minutes": 48.5
}
```

If no body provided, uses best recent performance (auto-detect).

**Response**:
```json
{
  "success": true,
  "predictions": {
    "5K": {
      "predicted_time_minutes": 22.5,
      "predicted_time_formatted": "22:30",
      "predicted_pace": "4:30/km",
      "confidence": "high"
    },
    "Marathon": {
      "predicted_time_minutes": 225.6,
      "predicted_time_formatted": "3:45:36",
      "predicted_pace": "5:21/km",
      "confidence": "low"
    }
  },
  "vdot": 52.3,
  "training_paces": {
    "easy": "6:00-6:30/km",
    "marathon": "5:21/km",
    "threshold": "4:50/km",
    "interval": "4:30/km",
    "repetition": "4:15/km"
  }
}
```

**GET /vdot** Query Parameters:
- `distance_km` (float): Race distance
- `time_minutes` (float): Race time

**GET /training-paces** Query Parameters:
- `vdot` (float): VDOT score (20-90)

---

## 📊 Health & Docs

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/` | API status | ❌ |
| `GET` | `/health` | Health check | ❌ |
| `GET` | `/docs` | Swagger UI (interactive) | ❌ |
| `GET` | `/redoc` | ReDoc (alternative docs) | ❌ |

---

## 🔑 Authentication Examples

### Login
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "password123"
  }'
```

**Response**:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Using Token
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/workouts/" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 📝 Notes

- **Pagination**: Default `limit=20`, max `limit=100`
- **Dates**: ISO 8601 format (`2025-11-18T10:30:00Z`)
- **Errors**: Standard HTTP codes (400, 401, 404, 500)
- **Rate Limiting**: Not implemented yet (TODO)
- **Versioning**: API v1 (future: v2 with breaking changes)

---

## 🧪 Testing Endpoints

**Interactive Docs**: http://127.0.0.1:8000/docs

Try endpoints directly in the Swagger UI:
1. Click **Authorize** button
2. Paste your access token
3. Click any endpoint → **Try it out** → **Execute**

---

**Last Updated**: Nov 13, 2025 (v0.2.0)  
**Total Endpoints**: 42
