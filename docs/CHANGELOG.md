# RunCoach AI - Change Log

## [0.3.0] - 2025-11-14

### 🏥 **HEALTH METRICS & READINESS SCORE - COMPLETE SYSTEM**

**Multi-Platform Health Integration:**
- ✅ **Garmin Connect** - Full health metrics (HRV, Body Battery, Sleep, Stress)
- ✅ **Google Fit** - Xiaomi/Amazfit support via Zepp automatic sync
- ✅ **Apple Health** - iPhone users via export.xml upload
- ✅ **Manual Entry** - Universal fallback for any device

**Health Metrics Tracked:**
- **Recovery**: HRV (ms), Resting HR (bpm), baselines
- **Sleep**: Duration, stages (deep/REM/light), sleep score
- **Readiness**: Body Battery, Readiness Score, Stress Level
- **Activity**: Steps, calories, intensity minutes
- **Subjective**: Energy, soreness, mood, motivation (manual)

**Readiness Score (0-100):**
- Weighted calculation: Body Battery (40%), Sleep (30%), HRV (20%), Resting HR (10%), Stress (10%)
- Confidence levels: high/medium/low based on data availability
- Automatic baseline calculation (7-day rolling average)
- Personalized recommendations: ✅ Ready / ⚠️ Moderate / 🛑 Rest Day

**AI Coach Integration:**
- Health-aware workout recommendations
- Automatic adaptation based on recovery state
- Prevents overtraining with alerts
- Personalized intensity guidance using readiness score

**New Endpoints:**
```
GET  /health/today - Today's health metrics
GET  /health/history?days=30 - Historical data
POST /health/manual - Manual entry (how you feel)
GET  /health/readiness - Current readiness score
GET  /health/recommendation - AI workout recommendation
POST /health/sync/garmin - Sync from Garmin
GET  /health/connect/google-fit - Google Fit OAuth
POST /health/sync/google-fit - Sync from Google Fit
POST /health/import/apple-health - Import Apple Health export
GET  /health/insights/trends - Health trends analysis
```

**Database Changes:**
- New `HealthMetric` model with 25+ fields
- User fields: Strava, Google Fit, Apple Health tokens
- Unique constraint: one health record per user per day
- Indexes for performance optimization

**Services Created:**
- `garmin_health_service.py` - Garmin Connect wellness API
- `google_fit_service.py` - Google Fit OAuth + data sync
- `apple_health_service.py` - Apple Health XML parser
- Enhanced `coach_service.py` - Readiness calculation + health-aware AI

**Migration:**
- Run `python migrate_health_metrics.py` to upgrade database
- Backward compatible with existing workouts
- Zero downtime migration

**Impact:**
- Garmin users: Premium experience with full metrics
- Xiaomi/Amazfit: Automatic via Zepp → Google Fit
- iPhone users: One-time export.xml import
- Others: Manual daily check-in

---

## [0.2.2] - 2025-11-14

### 🎯 Strava as Universal Hub Strategy

**Strava Integration Enhanced:**
- Positioned Strava as primary sync method for non-Garmin devices
- **Perfect solution for Xiaomi/Amazfit**: Zepp → Strava → RunCoach (fully automatic)
- Benefits 50+ device brands: Polar, Suunto, Wahoo, Coros, Apple Watch, Samsung
- Added `source_type` and `data_quality` fields to workouts table

**Source Tracking System:**
- `source_type`: garmin_oauth, garmin_fit, strava, gpx_upload, tcx_upload
- `data_quality`: high (FIT with form), medium (HR+GPS), basic (GPS only)
- Automatic quality detection based on available metrics
- Migration script for existing workouts

**Heart Rate Zones Calculator:**
- Auto-calculate from workout history (max HR observed)
- Fallback to age-based formula (220 - age)
- 5-zone model compatible with all devices
- Works perfectly with Xiaomi/Amazfit data via Strava

**Documentation Updates:**
- New `DATA_SOURCES_COMPARISON.md` - Complete device integration guide
- Updated `DEVICE_INTEGRATION_GUIDE.md` - Strava as recommended method
- Enhanced `README.md` - Universal device support highlighted

**Technical Implementation:**
- Strava parser sets `source_type='strava'` and `data_quality='medium'`
- GPX parser determines quality based on HR/cadence availability
- Garmin OAuth maintains `data_quality='high'` with full form metrics
- Migration script updates existing workouts retroactively

---

## [0.2.1] - 2025-11-14

### ⚡ Xiaomi/Amazfit Auto-Conversion

**GPX → FIT Transparent Conversion**
- Automatic detection and conversion of GPX files to FIT format
- Zero user friction: upload GPX, get FIT-quality metrics
- Advanced metric extraction:
  - Haversine GPS distance (±10m accuracy)
  - Pace and speed calculations
  - Heart rate from GPX extensions
  - Elevation and elevation gain
  - Session summary (total time, avg/max HR)
  - Lap data from waypoints
- FIT protocol compliant (Garmin-compatible)
- In-memory processing (no temp files)
- Backward compatible (GPX parsing still available)
- Benefits ALL GPX uploads, not just Xiaomi/Amazfit

**New Service:**
- `GPXToFITConverter` - Complete conversion pipeline (220+ lines)
  - FIT header generation
  - File ID message (Garmin format)
  - Session/lap/record messages
  - CRC checksum validation

**Modified:**
- `file_upload_service.py` - Auto-converts GPX before parsing
- `DEVICE_INTEGRATION_GUIDE.md` - Xiaomi/Amazfit section updated
- `README.md` - Multi-device integration highlighted
- `API_REFERENCE.md` - Auto-conversion documented

**Dependencies:**
- Added `gpxpy==1.6.2` - Advanced GPX parsing
- Added `python-fitparse==2.0.4` - FIT file generation

---

## [0.2.0] - 2025-11-13

### 🚀 Major Feature Expansion

#### ✅ Multi-Platform Integration

**Strava Integration**
- OAuth2 authentication flow
- Automatic activity synchronization
- Token refresh mechanism
- Activity parsing to workout format
- Deduplication by start time
- 5 new endpoints:
  - `GET /api/v1/strava/auth-url` - Get OAuth URL
  - `POST /api/v1/strava/connect` - Connect with authorization code
  - `POST /api/v1/strava/sync` - Sync activities
  - `GET /api/v1/strava/status` - Check connection status
  - `DELETE /api/v1/strava/disconnect` - Remove connection

**Universal File Upload**
- Support for 3 file formats:
  - **FIT** (Garmin, Wahoo, Polar) - 18 metrics including advanced form
  - **GPX** (Xiaomi, Amazfit, Suunto) - GPS tracks + elevation
  - **TCX** (Garmin Training Center) - Lap data + metrics
- Drag & drop UI in frontend
- Haversine formula for GPX distance calculation
- Automatic format detection
- File size validation (10MB limit)
- 2 new endpoints:
  - `POST /api/v1/upload/workout` - Upload workout file
  - `GET /api/v1/upload/supported-formats` - List formats

**Device Compatibility**
- Garmin: OAuth + Manual upload
- Strava: OAuth sync
- Xiaomi/Amazfit: Manual GPX export
- Polar: Manual upload
- Wahoo: Manual upload
- Suunto: Manual upload
- Coros: Manual upload

#### 🤖 Advanced AI Services

**AI Training Plan Generator**
- Multi-week personalized plans (4-24 weeks)
- Goal-specific adaptation:
  - 5K, 10K, 15K, Half Marathon, Marathon
  - General fitness
  - Base building
- JSON-structured weekly breakdown:
  - Daily workouts with distances
  - Pace targets and HR zones
  - Workout types (easy/interval/tempo/long)
  - Intensity distribution (easy/moderate/hard %)
- Plan adaptation based on:
  - Adherence percentage
  - Performance vs targets
  - Fatigue indicators
  - User feedback
- Nutrition and recovery tips
- 6 new endpoints:
  - `POST /api/v1/training-plans/generate` - Generate plan
  - `GET /api/v1/training-plans/` - List all plans
  - `GET /api/v1/training-plans/{id}` - Get plan details
  - `POST /api/v1/training-plans/{id}/adapt` - Adapt plan
  - `PUT /api/v1/training-plans/{id}/status` - Update status
  - `DELETE /api/v1/training-plans/{id}` - Delete plan

**Race Time Predictor**
- VDOT calculation (Jack Daniels method)
- Riegel formula for 5 distances:
  - 5K, 10K, 15K, Half Marathon, Marathon
- Confidence scoring:
  - High: ≤2x base distance
  - Medium: 2-4x base distance
  - Low: >4x base distance
- Training pace zones:
  - Easy (65-79% effort)
  - Marathon (80-89% effort)
  - Threshold (90-92% effort)
  - Interval (95-100% effort)
  - Repetition (105-110% effort)
- Automatic best performance detection (60 days)
- Manual base performance input
- 3 new endpoints:
  - `POST /api/v1/predictions/race-times` - Predict all distances
  - `GET /api/v1/predictions/vdot` - Calculate VDOT
  - `GET /api/v1/predictions/training-paces` - Get pace zones

#### 🏃 Enhanced Workout Metrics

**Running Form Analysis (6 new fields)**
- `avg_cadence` - Steps per minute
- `max_cadence` - Peak cadence
- `avg_stance_time` - Ground contact time (ms)
- `avg_vertical_oscillation` - Bounce (cm)
- `avg_leg_spring_stiffness` - Power efficiency
- `left_right_balance` - Symmetry (% left leg)

**Database Migrations**
- Added 6 form metric columns to `workouts` table
- Added 4 new user profile fields:
  - `height_cm`, `weight_kg`
  - `hr_zones`, `power_zones` (JSON)
  - `last_garmin_sync`

#### 📚 Documentation

**New Guides**
- `DEVICE_INTEGRATION_GUIDE.md` (200+ lines)
  - Export instructions for 6+ device brands
  - File format explanations
  - Troubleshooting tips
  - FAQ section
- `TECHNICAL_DOCS.md` updated (500+ lines)
  - Complete API reference
  - Multi-platform architecture
  - AI service algorithms (VDOT, Riegel)
  - Training plan JSON structure
  - Database schema with new fields

#### 🎨 Frontend Updates

**New Pages**
- File Upload (`/dashboard/upload`)
  - Drag & drop interface
  - File validation (.fit/.gpx/.tcx)
  - Device compatibility grid
  - Upload progress indicator

**UI Components**
- Sidebar updated with "Subir Archivo" option
- Loading states for async operations
- Error handling with user-friendly messages

#### 🔧 Backend Services

**New Services (1,400+ lines total)**
- `strava_service.py` (400+ lines)
- `file_upload_service.py` (400+ lines)
- `training_plan_service.py` (300+ lines)
- `race_predictor_service.py` (300+ lines)

**Configuration Updates**
- Added Strava OAuth credentials to config
- Environment variable validation
- CORS updated for new endpoints

#### 📊 API Statistics

**Total Endpoints: 40+**
- Authentication: 4 endpoints
- Workouts: 5 endpoints
- Garmin: 4 endpoints
- Strava: 5 endpoints (NEW)
- File Upload: 2 endpoints (NEW)
- Profile: 3 endpoints
- AI Coach: 9 endpoints
- Training Plans: 6 endpoints (NEW)
- Predictions: 4 endpoints (NEW)

---

## [0.1.0] - 2025-11-13

### 🎉 Initial Release

#### ✅ Features Implemented

**Authentication & Security**
- JWT-based authentication (access + refresh tokens)
- Bcrypt password hashing
- Protected API endpoints
- Token expiration management

**Garmin Connect Integration**
- Full Garmin account connection
- Automatic workout sync from Garmin Connect
- FIT file parsing (11 metrics extracted)
- Encrypted credential storage (Fernet)
- Real-time activity downloads

**Workout Management**
- Complete workout CRUD operations
- Pagination support
- Filtering by date range
- Detailed metrics storage

**Athlete Profile System**
- Running level tracking (beginner/intermediate/advanced/elite)
- Max heart rate configuration
- Custom goals with deadlines
- Injury history tracking
- Training preferences
- Configurable coaching style

**AI Coach - Post-Workout Analysis**
- Intelligent workout analysis using Llama 3.3 70B
- Personalized feedback based on profile
- HR zone identification
- Effort assessment
- Technical recommendations
- Next workout suggestions

**AI Coach - Training Plans**
- Weekly 7-day plan generation
- Progressive volume management
- Varied workout types (base/tempo/intervals)
- Goal-oriented planning
- Terrain and preference consideration

**AI Coach - Chatbot**
- Natural conversation with memory
- Context-aware responses
- Full access to user profile and history
- Conversation history persistence
- Adaptive coaching style

**AI Coach - Form Analysis**
- Running technique evaluation
- Pace consistency analysis
- HR variability assessment
- Elevation efficiency
- Drill and exercise recommendations

**HR Zones System**
- 5-zone heart rate calculator
- Personalized zone ranges
- Zone-based workout classification
- Performance tracking by zone

#### 📊 API Endpoints (25 total)

**Auth (3)**
- POST /api/v1/auth/register
- POST /api/v1/auth/login
- POST /api/v1/auth/refresh

**Workouts (2)**
- GET /api/v1/workouts
- GET /api/v1/workouts/{id}

**Garmin (4)**
- POST /api/v1/garmin/connect
- POST /api/v1/garmin/sync
- GET /api/v1/garmin/status
- DELETE /api/v1/garmin/disconnect

**Profile (6)**
- GET /api/v1/profile
- PATCH /api/v1/profile
- GET /api/v1/profile/goals
- POST /api/v1/profile/goals
- PATCH /api/v1/profile/goals/{index}
- DELETE /api/v1/profile/goals/{index}

**Coach AI (10)**
- POST /api/v1/coach/analyze/{workout_id}
- POST /api/v1/coach/analyze-form/{workout_id}
- POST /api/v1/coach/plan
- POST /api/v1/coach/chat
- GET /api/v1/coach/chat/history
- DELETE /api/v1/coach/chat/history
- GET /api/v1/coach/hr-zones

#### 🛠️ Technical Stack

**Backend**
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.0+
- Python 3.11+

**AI & Integrations**
- Groq API (Llama 3.3 70B)
- garminconnect 0.2.30
- garth 0.5.17
- fitparse 1.2.0

**Security**
- PyJWT for tokens
- bcrypt for passwords
- cryptography (Fernet) for credentials

**Testing**
- pytest
- pytest-cov
- 18/18 tests passing

#### 📝 Documentation

- Complete API documentation (Swagger/OpenAPI)
- User guide (GUIA_COMPLETA.md)
- Technical documentation (TECHNICAL_DOCS.md)
- Setup automation script (setup_everything.ps1)

#### 🎯 Known Limitations

- SQLite database (dev only, not production-ready)
- No database migrations (Alembic needed)
- Limited FIT metrics (cadence/vertical oscillation not yet parsed)
- Chatbot context limited to last 10 messages
- No streaming AI responses
- Manual Garmin re-authentication per request

### 🔮 Coming Soon

**High Priority**
- [ ] Frontend (Next.js dashboard)
- [ ] Alembic migrations
- [ ] Advanced FIT parsing
- [ ] PostgreSQL production setup
- [ ] Redis caching layer

**Medium Priority**
- [ ] Strava integration
- [ ] Weather API integration
- [ ] Voice coaching
- [ ] Race time predictor

**Low Priority**
- [ ] Social features
- [ ] Nutrition tracking
- [ ] Sleep integration

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- MAJOR: Breaking changes
- MINOR: New features (backwards compatible)
- PATCH: Bug fixes

---

**Maintainer:** Guillermo Martín de Oliva  
**Release Date:** 13 November 2025  
**Status:** ✅ Production Ready (Backend)
