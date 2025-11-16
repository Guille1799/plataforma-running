# 🏃‍♂️ RunCoach AI - Technical Documentation

## 🏗️ Arquitectura del Proyecto

### Backend Stack
- **Framework:** FastAPI 0.104+
- **Database:** SQLite (dev) / PostgreSQL (prod)
- **ORM:** SQLAlchemy 2.0+
- **Auth:** JWT (PyJWT)
- **AI:** Groq API (Llama 3.3 70B Versatile)
- **Integrations:** 
  - Garmin Connect (garminconnect + garth)
  - Strava API v3 (OAuth2)
- **File Parsing:** 
  - FIT files (fitparse)
  - GPX files (xml.etree)
  - TCX files (xml.etree)
- **Encryption:** Fernet (cryptography)

### Project Structure
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app + routers
│   ├── database.py             # SQLAlchemy setup
│   ├── models.py               # DB models (User, Workout, ChatMessage)
│   ├── schemas.py              # Pydantic schemas (validation)
│   ├── crud.py                 # Database operations
│   ├── security.py             # JWT, password hashing
│   │
│   ├── core/
│   │   ├── config.py           # Settings (env vars)
│   │
│   ├── routers/
│   │   ├── auth.py             # Register, login, refresh
│   │   ├── workouts.py         # Workout CRUD
│   │   ├── garmin.py           # Garmin integration (4 endpoints)
│   │   ├── strava.py           # Strava OAuth + sync (5 endpoints)
│   │   ├── upload.py           # File upload FIT/GPX/TCX (2 endpoints)
│   │   ├── profile.py          # Athlete profile + goals CRUD
│   │   └── coach.py            # AI Coach (9 endpoints)
│   │
│   └── services/
│       ├── garmin_service.py   # Garmin API wrapper + FIT parsing
│       ├── strava_service.py   # Strava OAuth + activity sync (400+ lines)
│       ├── file_upload_service.py  # Universal file parser (FIT/GPX/TCX, 400+ lines)
│       ├── training_plan_service.py  # AI training plans (300+ lines)
│       ├── race_predictor_service.py  # VDOT + race predictions (300+ lines)
│       └── coach_service.py    # AI Coach logic (660+ lines)
│
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_auth.py            # Auth tests
│   └── test_utils.py
│
├── .env                        # Environment variables
├── requirements.txt            # Production dependencies
├── requirements-test.txt       # Test dependencies
└── pytest.ini                  # Pytest configuration
```

---

## 🗄️ Database Schema

### User Model
```python
users
├── id (PK)
├── name
├── email (unique)
├── hashed_password
├── is_active
├── created_at
│
# Garmin Integration
├── garmin_email
├── garmin_token (encrypted)
├── garmin_connected_at
├── last_garmin_sync
│
# Athlete Profile
├── running_level (enum: beginner/intermediate/advanced/elite)
├── max_heart_rate
├── height_cm
├── weight_kg
├── hr_zones (JSON array)
├── power_zones (JSON array)
├── goals (JSON array)
├── coaching_style (enum: motivational/analytical/balanced/custom)
├── injuries (JSON array)
└── preferences (JSON object, stores: Strava tokens, training plans)
```

### Workout Model
```python
workouts
├── id (PK)
├── user_id (FK -> users)
├── sport_type
├── start_time
├── duration_seconds
├── distance_meters
├── avg_heart_rate
├── max_heart_rate
├── avg_pace
├── max_speed
├── calories
├── elevation_gain
│
# Running Form Metrics (NEW)
├── avg_cadence (steps/min)
├── max_cadence
├── avg_stance_time (ms)
├── avg_vertical_oscillation (cm)
├── avg_leg_spring_stiffness
├── left_right_balance (% left leg)
│
├── file_name
└── created_at
```

### ChatMessage Model
```python
chat_messages
├── id (PK)
├── user_id (FK -> users)
├── role (user/assistant)
├── content
├── tokens_used
└── created_at
```

---

## 🔐 Authentication Flow

### Registration
1. User sends: `name`, `email`, `password`
2. Password hashed with `bcrypt`
3. User created in DB
4. Returns: `access_token` + `refresh_token`

### Login
1. User sends: `email`, `password`
2. Password verified with `bcrypt`
3. Tokens generated (JWT)
4. Returns: `access_token` (30m) + `refresh_token` (7d)

### Token Structure
```python
{
  "sub": "user_id",
  "exp": timestamp
}
```

### Protected Endpoints
All `/api/v1/*` endpoints (except auth) require:
```
Authorization: Bearer {access_token}
```

---

## 📡 Multi-Platform Integration

### 1. Garmin Integration

#### Authentication Flow
```python
# 1. User provides Garmin credentials
email, password = request

# 2. Create Garmin API instance
api = Garmin(email, password)
api.login()  # CRITICAL: Must call explicitly

# 3. Encrypt and store credentials
encrypted = encrypt_token(json.dumps({"email": email, "password": password}))
user.garmin_token = encrypted

# 4. For subsequent requests
credentials = json.loads(decrypt_token(user.garmin_token))
api = Garmin(credentials['email'], credentials['password'])
api.login()  # Re-authenticate each time
```

#### Why Re-authenticate?
- `garth.client` is global singleton
- OAuth tokens don't persist across HTTP requests
- Solution: `Garmin().login()` on each request

### 2. Strava Integration (NEW)

#### OAuth2 Flow
```python
# Step 1: Get authorization URL
GET /api/v1/strava/auth-url
Response: {
  "authorization_url": "https://www.strava.com/oauth/authorize?..."
}

# Step 2: User authorizes → Redirected to callback with code
# http://localhost:3000/auth/strava/callback?code=xxx&scope=...

# Step 3: Exchange code for tokens
POST /api/v1/strava/connect
Body: { "code": "xxx" }
Response: {
  "status": "connected",
  "athlete": {
    "id": 12345,
    "name": "John Doe",
    "profile": "https://..."
  }
}
```

#### Token Storage
```python
# Stored in user.preferences as JSON
{
  "strava_access_token": "xxx",
  "strava_refresh_token": "yyy",
  "strava_expires_at": 1234567890,
  "strava_athlete_id": 12345
}
```

#### Activity Sync
```python
POST /api/v1/strava/sync
Response: {
  "synced": 15,
  "skipped": 2,  # Already exist
  "total": 17
}

# Converts Strava activity → Workout model
# Metrics: distance, time, avg_speed, elevation, calories, HR
```

### 3. Manual File Upload (NEW)

#### Supported Formats
- **FIT** (Flexible and Interoperable Data Transfer)
  - Native format: Garmin, Wahoo, Polar
  - Full metrics: HR, cadence, power, form
  - Parser: `fitparse` library

- **GPX** (GPS Exchange Format)
  - Native format: Xiaomi, Amazfit, Suunto
  - GPS tracks + elevation
  - Parser: XML parsing + Haversine distance

- **TCX** (Training Center XML)
  - Native format: Garmin Training Center
  - Lap data + metrics
  - Parser: XML parsing

#### Upload Flow
```python
POST /api/v1/upload/workout
Content-Type: multipart/form-data
Body: file=@workout.fit

# Backend flow:
1. Save file to temp location
2. Detect format (extension)
3. Call appropriate parser:
   - parse_fit_file()
   - parse_gpx_file()
   - parse_tcx_file()
4. Extract metrics (11-18 depending on format)
5. Create Workout in DB
6. Delete temp file
7. Return workout_id
```

#### FIT Parser Metrics (18 total)
```python
{
  "sport_type": "running",
  "start_time": datetime,
  "duration_seconds": 3600,
  "distance_meters": 10000,
  "avg_heart_rate": 145,
  "max_heart_rate": 175,
  "avg_pace": 6.0,  # min/km
  "max_speed": 4.5,  # m/s
  "calories": 650,
  "elevation_gain": 120,
  "avg_cadence": 175,
  "max_cadence": 190,
  "avg_stance_time": 240,  # ms
  "avg_vertical_oscillation": 8.5,  # cm
  "avg_leg_spring_stiffness": 12.5,
  "left_right_balance": 50.5,  # % left
  "avg_power": 280,  # watts
  "normalized_power": 295
}
```

#### GPX Parser (Basic)
```python
{
  "sport_type": "running",
  "start_time": datetime,
  "distance_meters": 10000,  # Calculated via Haversine
  "duration_seconds": 3600,  # Last - first timestamp
  "elevation_gain": 120,  # Sum positive elevation deltas
  "avg_heart_rate": 145,  # If HR extension present
  "max_heart_rate": 175
}
```

#### Device Compatibility Matrix
| Device       | FIT | GPX | TCX | Auto-Sync | Manual Upload |
|--------------|-----|-----|-----|-----------|---------------|
| Garmin       | ✅  | ✅  | ✅  | ✅ OAuth  | ✅            |
| Strava       | -   | -   | -   | ✅ OAuth  | ✅            |
| Xiaomi       | ❌  | ✅  | ❌  | ❌        | ✅            |
| Amazfit      | ❌  | ✅  | ❌  | ❌        | ✅            |
| Polar        | ✅  | ✅  | ❌  | ❌        | ✅            |
| Wahoo        | ✅  | ✅  | ❌  | ❌        | ✅            |
| Suunto       | ✅  | ✅  | ❌  | ❌        | ✅            |
| Coros        | ✅  | ✅  | ❌  | ❌        | ✅            |

---

## 📡 Garmin Integration (Legacy)

### Authentication Flow
```python
# 1. User provides Garmin credentials
email, password = request

# 2. Create Garmin API instance
api = Garmin(email, password)
api.login()  # CRITICAL: Must call explicitly

# 3. Encrypt and store credentials
encrypted = encrypt_token(json.dumps({"email": email, "password": password}))
user.garmin_token = encrypted

# 4. For subsequent requests
credentials = json.loads(decrypt_token(user.garmin_token))
api = Garmin(credentials['email'], credentials['password'])
api.login()  # Re-authenticate each time
```

### Why Re-authenticate?
- `garth.client` is global singleton
- OAuth tokens don't persist across HTTP requests
- Solution: `Garmin().login()` on each request

### FIT File Parsing
```python
# 1. Download activity
fit_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)

# 2. Parse with fitparse
fitfile = FitFile(BytesIO(fit_data))

# 3. Extract metrics
for record in fitfile.get_messages('record'):
    timestamp = record.get_value('timestamp')
    heart_rate = record.get_value('heart_rate')
    cadence = record.get_value('cadence')
    # ... 11 metrics total
```

---

## 🤖 AI Coach Architecture

### CoachService Class Structure

#### 1. HR Zones Calculation
```python
calculate_hr_zones(max_hr: int) -> Dict
# Returns 5 zones based on % of max HR
```

#### 2. Athlete Context Builder
```python
build_athlete_context(user, workouts, goals) -> str
# Compiles:
# - User profile (level, FCM)
# - Recent training history
# - Active goals
# - Injuries
# - Preferences
```

#### 3. Coaching Style Prompts
```python
get_coaching_style_prompt(style: str) -> str
# Returns system prompt for:
# - motivational: Energético, positivo
# - analytical: Analítico, científico
# - balanced: Mix equilibrado
# - custom: User-defined prompt
```

#### 4. Post-Workout Analysis
```python
analyze_workout(workout, user, recent_workouts, db) -> Dict
# 1. Build athlete context
# 2. Format workout details
# 3. Call Groq API with prompt
# 4. Return analysis + metrics
```

#### 5. Weekly Plan Generation
```python
generate_weekly_plan(user, workouts, start_date) -> Dict
# 1. Calculate current weekly volume
# 2. Build context with goals
# 3. Generate 7-day plan with Groq
# 4. Includes: distances, paces, zones
```

#### 6. Form Analysis
```python
analyze_running_form(workout, user) -> Dict
# Analyzes:
# - Pace consistency
# - HR variability
# - Elevation efficiency
# - Running economy
```

#### 7. Chatbot with Memory
```python
chat_with_coach(user, message, history, workouts, db) -> Dict
# 1. Load last 10 messages (context)
# 2. Build athlete context
# 3. Send to Groq with full history
# 4. Save messages to DB
# 5. Return response
```

---

## 🎯 Advanced AI Services (NEW)

### TrainingPlanService

**Purpose**: Generate personalized multi-week training plans using AI

**File**: `app/services/training_plan_service.py` (300+ lines)

#### Key Methods

##### 1. Generate Plan
```python
async def generate_plan(
    user: User,
    goal_type: str,  # "5k", "10k", "half_marathon", "marathon", "fitness"
    goal_date: datetime,
    current_weekly_km: float,
    weeks: int = 12,
    db: AsyncSession
) -> Dict
```

**Process:**
1. Query recent 20 workouts for fitness assessment
2. Calculate current volume, avg pace, frequency
3. Build rich context (profile + history + goal)
4. Call Groq API with structured prompt
5. Parse JSON response
6. Validate plan structure
7. Store in user.preferences["training_plan"]

**Output JSON Structure:**
```json
{
  "plan_id": "plan_uuid",
  "plan_name": "Preparación Media Maratón",
  "goal_type": "half_marathon",
  "goal_date": "2026-04-15",
  "total_weeks": 12,
  "target_weekly_km": 50,
  
  "weeks": [
    {
      "week": 1,
      "focus": "Base aeróbica",
      "total_km": 30,
      "intensity_distribution": {
        "easy": 80,
        "moderate": 15,
        "hard": 5
      },
      "workouts": [
        {
          "day": 1,
          "type": "easy_run",
          "name": "Rodaje suave",
          "distance_km": 8,
          "pace_target": "5:30-6:00 min/km",
          "hr_zone": "Zone 2",
          "notes": "Mantén conversación cómoda"
        },
        {
          "day": 3,
          "type": "interval",
          "name": "Series 1km",
          "distance_km": 10,
          "structure": "2km calentamiento + 5x1km (R:2min) + 2km vuelta calma",
          "pace_target": "4:30-4:45 min/km (series)",
          "hr_zone": "Zone 4",
          "notes": "Primera sesión de calidad"
        }
      ]
    }
  ],
  
  "nutrition_tips": [
    "Hidratación: 2-3L agua diarios",
    "Carbohidratos pre-entreno: 1-2h antes"
  ],
  
  "recovery_tips": [
    "Dormir 7-9 horas",
    "Estiramientos post-entreno"
  ]
}
```

##### 2. Adapt Plan
```python
async def adapt_plan(
    user: User,
    plan_id: str,
    actual_workouts: List[Workout],
    db: AsyncSession
) -> Dict
```

**Process:**
1. Load original plan from preferences
2. Calculate adherence % (completed/planned)
3. Analyze performance vs targets
4. Adjust upcoming weeks based on:
   - Fatigue indicators
   - Consistency
   - Performance trends
5. Return adapted plan

**Adaptation Logic:**
- **High adherence (>90%)**: Progress normally
- **Medium adherence (70-89%)**: Maintain current load
- **Low adherence (<70%)**: Reduce volume 10-20%
- **Overperformance**: Increase intensity slightly
- **Underperformance**: Focus on base building

---

### RacePredictorService

**Purpose**: Predict race times using VDOT and Riegel formulas

**File**: `app/services/race_predictor_service.py` (300+ lines)

#### Key Methods

##### 1. Predict Race Times
```python
async def predict_race_times(
    user_id: int,
    base_distance_km: Optional[float] = None,
    base_time_minutes: Optional[float] = None,
    db: AsyncSession
) -> Dict
```

**Process:**
1. If no base provided: Find best recent performance (last 60 days)
2. Calculate VDOT from base performance
3. Apply Riegel formula for 5 distances
4. Calculate confidence score
5. Get training pace zones

**Output:**
```json
{
  "predictions": {
    "5K": {
      "predicted_time_minutes": 22.5,
      "predicted_time_formatted": "22:30",
      "predicted_pace": "4:30/km",
      "confidence": "high"
    },
    "10K": {
      "predicted_time_minutes": 47.8,
      "predicted_time_formatted": "47:48",
      "predicted_pace": "4:47/km",
      "confidence": "high"
    },
    "15K": {
      "predicted_time_minutes": 74.2,
      "predicted_time_formatted": "1:14:12",
      "predicted_pace": "4:57/km",
      "confidence": "medium"
    },
    "Half_Marathon": {
      "predicted_time_minutes": 105.3,
      "predicted_time_formatted": "1:45:18",
      "predicted_pace": "5:00/km",
      "confidence": "medium"
    },
    "Marathon": {
      "predicted_time_minutes": 225.6,
      "predicted_time_formatted": "3:45:36",
      "predicted_pace": "5:21/km",
      "confidence": "low"
    }
  },
  
  "vdot": 52.3,
  
  "base_performance": {
    "distance_km": 10.0,
    "time_minutes": 47.8,
    "pace": "4:47/km",
    "date": "2025-11-01"
  },
  
  "training_paces": {
    "easy": "6:00-6:30 min/km",
    "marathon": "5:21 min/km",
    "threshold": "4:50 min/km",
    "interval": "4:30 min/km",
    "repetition": "4:15 min/km"
  }
}
```

##### 2. VDOT Calculation
```python
def _calculate_vdot(distance_meters: float, time_seconds: float) -> float
```

**Jack Daniels Formula:**
```python
velocity = distance_meters / time_seconds  # m/s
vo2 = -4.6 + 0.182258 * (velocity * 3.6) + 0.000104 * (velocity * 3.6)^2
vdot = vo2 / (1 - math.exp(-0.012 * time_seconds))
return vdot
```

**VDOT Scale:**
- 30-40: Beginner
- 40-50: Intermediate
- 50-60: Advanced
- 60-70: Competitive
- 70+: Elite

##### 3. Riegel Prediction
```python
def _riegel_prediction(base_time: float, base_dist: float, target_dist: float) -> float
```

**Riegel Formula:**
```python
T2 = T1 * (D2 / D1) ^ 1.06

# Where:
# T1 = base time (minutes)
# D1 = base distance (km)
# T2 = predicted time (minutes)
# D2 = target distance (km)
# 1.06 = fatigue factor (endurance decay)
```

**Example:**
- Base: 10K in 48 minutes
- Predict Marathon: 48 * (42.195 / 10) ^ 1.06 = 227 minutes (3:47)

##### 4. Training Pace Zones
```python
def get_training_paces(vdot: float) -> Dict
```

**Jack Daniels Training Zones:**
- **Easy**: 65-79% effort, conversational
- **Marathon**: 80-89% effort, goal race pace
- **Threshold**: 90-92% effort, comfortably hard
- **Interval**: 95-100% effort, VO2max
- **Repetition**: 105-110% effort, speed work

**Calculation:**
Uses VDOT tables to determine optimal paces for each zone.

##### 5. Confidence Scoring
```python
def _calculate_confidence(base_distance: float, target_distance: float) -> str
```

**Logic:**
```python
ratio = target_distance / base_distance

if ratio <= 2.0:
    return "high"     # Interpolating nearby distances
elif ratio <= 4.0:
    return "medium"   # Moderate extrapolation
else:
    return "low"      # Large extrapolation (e.g., 10K → Marathon)
```

---

## 🤖 AI Coach Architecture (Legacy)

---

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DATABASE_URL=sqlite:///./runcoach.db

# Security
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# AI
GROQ_API_KEY=gsk_...

# Strava OAuth (NEW)
STRAVA_CLIENT_ID=your-strava-client-id
STRAVA_CLIENT_SECRET=your-strava-client-secret
STRAVA_REDIRECT_URI=http://localhost:3000/auth/strava/callback

# Application
DEBUG=False
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Settings Class (Pydantic)
```python
class Settings(BaseSettings):
    database_url: str
    secret_key: str
    algorithm: str
    groq_api_key: Optional[str]
    # ...
    
    class Config:
        env_file = ".env"
```

---

## 🧪 Testing

### Run Tests
```bash
pytest
pytest --cov=app tests/
pytest -v tests/test_auth.py
```

### Test Structure
```python
# conftest.py - Fixtures
@pytest.fixture
def client():
    # Returns TestClient with in-memory DB

@pytest.fixture
def auth_headers(client):
    # Returns auth headers with valid token

# test_auth.py
def test_register(client):
    response = client.post("/api/v1/auth/register", json={...})
    assert response.status_code == 201
    assert "access_token" in response.json()
```

---

## 🚀 Deployment

### Local Development
```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### Production (Docker)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY app/ ./app/
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment-Specific Settings
```python
# Development
DEBUG=True
DATABASE_URL=sqlite:///./runcoach.db

# Production
DEBUG=False
DATABASE_URL=postgresql://user:pass@host:5432/runcoach
SECRET_KEY=<strong-random-key>
```

---

## 📊 Performance Optimization

### Database
- Indexes on: `user_id`, `email`, `start_time`
- Pagination: Default 20, max 100
- Eager loading: Use `joinedload()` for relationships

### Caching
- Consider Redis for:
  - Garmin auth tokens
  - Frequently accessed user profiles
  - Chat history

### AI Calls
- Current: ~500-800 tokens per request
- Cost: $0.59/1M tokens (Groq)
- Optimize: Reduce context length for simple queries

---

## 🔒 Security Best Practices

### Implemented
✅ Password hashing (bcrypt)
✅ JWT tokens with expiration
✅ Encrypted Garmin credentials (Fernet)
✅ CORS configuration
✅ Input validation (Pydantic)
✅ SQL injection prevention (SQLAlchemy ORM)

### TODO for Production
- [ ] Rate limiting (slowapi)
- [ ] HTTPS only
- [ ] Environment-based secrets
- [ ] API key rotation
- [ ] Audit logging
- [ ] GDPR compliance (data export/deletion)

---

## 📈 Monitoring & Logging

### Add Structured Logging
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
logger.info("User registered", extra={"user_id": user.id})
```

### Metrics to Track
- API response times
- Groq API token usage
- Garmin sync success rate
- Active users
- Workout sync volume

---

## 🐛 Known Issues & Limitations

### Garmin Integration
- Must re-authenticate on each request (garth limitation)
- No support for multi-sport activities yet
- FIT parsing limited to available metrics in file

### Strava Integration (NEW)
- Tokens stored in JSON (TODO: encrypt like Garmin)
- No webhook support yet (manual sync only)
- Activity deduplication by start_time (not Strava ID)

### File Upload
- Max file size: 10MB (configurable)
- GPX/TCX: Limited metrics vs FIT files
- No batch upload yet (one file at a time)

### AI Coach
- Context window: 10 previous messages
- No streaming responses yet
- English/Spanish only
- Training plans: JSON parsing can fail on malformed AI output

### Race Predictor
- VDOT accuracy depends on recent race-effort workouts
- Riegel formula best for <4x distance extrapolation
- No adjustment for terrain, weather, or training age

### Database
- SQLite for dev (not concurrent-safe)
- No migrations system (use Alembic for prod)
- Large FIT files (>50MB) can cause timeouts

---

## 🔮 Future Improvements

### Completed in Latest Update ✅
- ✅ **Strava Integration** - OAuth2 + activity sync
- ✅ **Multi-Format File Upload** - FIT, GPX, TCX parsers
- ✅ **Training Plan Generator** - AI-powered 12-week plans
- ✅ **Race Time Predictor** - VDOT + Riegel formulas
- ✅ **Running Form Metrics** - 6 advanced biomechanics
- ✅ **Device Integration Guide** - 6+ brands documented

### High Priority (Next Sprint)
1. **API Endpoints for New Services**
   - POST /api/v1/training-plans/generate
   - GET /api/v1/training-plans/{plan_id}
   - POST /api/v1/training-plans/{plan_id}/adapt
   - GET /api/v1/predictions/race-times
   - GET /api/v1/predictions/training-paces

2. **Frontend UI for New Features**
   - Training plans page (/dashboard/plans)
   - Race predictor calculator (/dashboard/predictions)
   - Strava connection flow (/dashboard/strava)
   - File upload page (DONE ✅)

3. **Alembic Migrations** - Proper DB versioning
4. **Advanced FIT Parsing** - Power metrics, running dynamics

### Medium Priority
5. **Apple Health Integration** - HealthKit API
6. **Google Fit Integration** - REST API
7. **Advanced Charts** - Recharts/Chart.js visualizations
8. **Weather API** - Adapt training to conditions
9. **Caching Layer** - Redis for performance
10. **Injury Prevention** - Fatigue analysis + alerts

### Low Priority
11. **Social Features** - Leaderboards, challenges, community feed
12. **Nutrition Tracking** - Pre/post workout meals, macros
13. **Sleep Integration** - Oura Ring, Apple Health
14. **Voice Coach** - Audio feedback during runs
15. **Live Activity Tracking** - Real-time GPS + coaching

---

## 📚 Additional Resources

### Documentation
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [SQLAlchemy ORM](https://docs.sqlalchemy.org/en/20/)
- [Garmin Connect Python](https://github.com/cyberjunky/python-garminconnect)
- [Strava API v3](https://developers.strava.com/docs/reference/)
- [Groq API](https://console.groq.com/docs)
- [fitparse](https://github.com/dtcooper/python-fitparse)
- [Jack Daniels VDOT](https://runsmartproject.com/calculator/)

### Project Documentation
- [README.md](README.md) - Setup & Getting Started
- [DEVICE_INTEGRATION_GUIDE.md](DEVICE_INTEGRATION_GUIDE.md) - Export workouts from all devices
- [SETUP.md](SETUP.md) - Detailed installation
- [CONTRIBUTING.md](CONTRIBUTING.md) - How to contribute
- [TECHNICAL_DOCS.md](TECHNICAL_DOCS.md) - This file

### Learning Resources
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [REST API Design](https://restfulapi.net/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [OAuth 2.0 Flow](https://www.oauth.com/oauth2-servers/server-side-apps/authorization-code/)
- [FIT File Format](https://developer.garmin.com/fit/protocol/)
- [GPX Schema](https://www.topografix.com/GPX/1/1/)

---

**Maintainer:** Guillermo Martín de Oliva  
**Version:** 0.2.0  
**Last Updated:** 13 Nov 2025

**Major Updates in v0.2.0:**
- Multi-platform support (Garmin, Strava, Manual Upload)
- AI training plan generator (12-week personalized)
- Race time predictor (VDOT + Riegel)
- FIT/GPX/TCX file parsers
- Running form metrics (6 advanced)
- Device integration guide (6+ brands)
