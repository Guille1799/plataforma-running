# 🏥 Health Metrics Strategy - Datos de Bienestar

## 🎯 Objetivo
Integrar métricas de salud y bienestar para que el Coach IA pueda dar recomendaciones personalizadas sobre:
- **Recuperación**: ¿Estás listo para entrenar duro hoy?
- **Carga de entrenamiento**: ¿Necesitas un día de descanso?
- **Prevención de sobreentrenamiento**: Detectar fatiga acumulada
- **Optimización del rendimiento**: Entrenar cuando tu cuerpo está preparado

---

## 📊 Métricas de Salud Críticas

### 1. **HRV (Heart Rate Variability)** 🫀
- **Por qué importa**: Indicador #1 de recuperación y estrés del sistema nervioso
- **Uso Coach IA**: 
  - HRV alta → Sistema recuperado, listo para entrenamiento intenso
  - HRV baja → Fatiga, recomendar día de recuperación activa
- **Rango normal**: 20-200ms (muy individual, importa la tendencia)

### 2. **Resting Heart Rate (FC Reposo)** 💤
- **Por qué importa**: Cambios indican fatiga o enfermedad
- **Uso Coach IA**:
  - FC reposo +5-10 bpm sobre baseline → Sobreentrenamiento o enfermedad
  - FC reposo bajando con tiempo → Mejorando fitness cardiovascular
- **Rango normal**: 40-70 bpm atletas, 60-100 bpm población general

### 3. **Sleep (Sueño)** 😴
- **Métricas clave**:
  - **Duración total**: 7-9 horas óptimo
  - **Sleep Score/Quality**: 0-100
  - **Deep Sleep**: Critical para recuperación muscular
  - **REM Sleep**: Critical para recuperación mental
- **Uso Coach IA**:
  - < 6 horas → Recomendar workout más suave o día off
  - Sleep score < 60 → Priorizar recuperación
  - Patrón de mal sueño 3+ días → Alerta de sobreentrenamiento

### 4. **Body Battery / Readiness Score** 🔋
- **Por qué importa**: Score compuesto de HRV + Sleep + Stress + Activity
- **Uso Coach IA**:
  - Score > 75 → Light verde para entrenamiento intenso
  - Score 50-75 → Entrenamiento moderado
  - Score < 50 → Recomendar recuperación activa o descanso
- **Disponibilidad**: Garmin (Body Battery), Whoop (Recovery Score), Oura (Readiness)

### 5. **Stress Level (Nivel de Estrés)** 🧘
- **Por qué importa**: Estrés crónico impacta recuperación
- **Uso Coach IA**: 
  - Stress alto consistente → Incorporar más días de recuperación
  - Spike de estrés → Evitar entrenamientos duros ese día

### 6. **Training Load / Strain** 📈
- **Por qué importa**: Balance entre carga y recuperación
- **Métricas**:
  - **Acute Load**: Carga última semana
  - **Chronic Load**: Carga últimas 4 semanas
  - **Training Stress Balance (TSB)**: Chronic - Acute
- **Uso Coach IA**:
  - TSB negativo → Fatigado, reducir carga
  - TSB positivo → Recuperado, puede intensificar
  - Acute/Chronic ratio > 1.5 → Alto riesgo lesión

---

## 🔌 Disponibilidad por Plataforma

### ✅ **GARMIN** (API Completa - Mejor Opción)
```
✅ HRV Status (nightly HRV)
✅ Resting Heart Rate (daily)
✅ Sleep (duration, stages, score)
✅ Body Battery (0-100 score)
✅ Stress Level (0-100)
✅ Respiration Rate
✅ Pulse Ox (SpO2)
✅ Steps, Intensity Minutes
✅ Daily Summary Endpoints
```

**Endpoints disponibles**:
- `GET /usersummary-service/usersummary/daily/{username}/{date}` → Todo en uno
- `GET /wellness-service/wellness/dailyHeartRate/{date}` → Resting HR + HRV
- `GET /wellness-service/wellness/dailySleep/{date}` → Sleep details
- `GET /wellness-service/wellness/dailyStress/{date}` → Stress timeline
- `GET /wellness-service/wellness/bodyBattery/{date}` → Body Battery timeline

### ⚠️ **STRAVA** (Solo Actividades - Sin Health Metrics)
```
❌ No HRV
❌ No Resting HR
❌ No Sleep
❌ No Body Battery
❌ No Stress
✅ Solo workout metrics (HR durante actividad, pace, distance)
```

**Limitación crítica**: Strava NO expone datos de salud/bienestar via API. Solo actividades.

### 🔄 **XIAOMI/AMAZFIT via Zepp** (Workaround Necesario)
```
❌ No API oficial
⚠️ Zepp Health API (solo empresas)
🔄 Workarounds:
  1. Gadgetbridge (export manual)
  2. Zepp → Google Fit → Nuestra API
  3. Notify & Fitness app (export CSV)
```

**Métricas disponibles en Zepp**:
- ✅ HRV (PAI Score incluye HRV)
- ✅ Resting HR
- ✅ Sleep (duration, stages, REM)
- ✅ Stress (via HR analysis)
- ✅ Steps, calories
- ⚠️ NO Body Battery (equivalente: PAI Score)

### 🔄 **POLAR** (API Limitada pero Útil)
```
✅ HRV (orthostatic test)
✅ Resting HR
✅ Sleep (duration, score)
✅ Training Load Pro (cardio + muscle)
✅ Recovery Pro (test-based)
❌ No Body Battery equivalent
❌ No continuous stress
```

**Polar AccessLink API**:
- Requiere OAuth2
- Endpoints: `/v3/users/{user-id}/sleep`, `/v3/users/{user-id}/physical-information`

### 🔄 **WHOOP** (API Excelente - Enfocado en Recuperación)
```
✅ HRV (ms, baseline)
✅ Resting HR
✅ Sleep Performance (score, stages)
✅ Recovery Score (0-100, like Body Battery)
✅ Strain Score (training load)
✅ Respiratory Rate
```

**Whoop API v6**:
- Muy completa para recuperación
- Requiere Whoop membership ($30/month)

### 🔄 **OURA RING** (API Premium - Mejor para Sleep/Recovery)
```
✅ HRV (best-in-class)
✅ Resting HR
✅ Sleep Score (best-in-class)
✅ Readiness Score (like Body Battery)
✅ Activity Score
✅ Temperature deviation
```

**Oura API v2**:
- Excelente para salud/bienestar
- Precio accesible (~$300 one-time)

---

## 🎨 Arquitectura Propuesta

### **Opción A: Garmin-First (Implementación Inmediata)**
```
┌─────────────────────────────────────────────┐
│  GARMIN USERS (80% del mercado runner)      │
│  ✅ Health metrics via Garmin API           │
│  ✅ Ya implementado OAuth                   │
│  ✅ Endpoints health disponibles            │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│  COACH IA RECOMMENDATIONS                   │
│  • "Tu Body Battery está bajo (42/100)"    │
│  • "Considera workout suave hoy"            │
│  • "HRV 15% bajo → Necesitas recuperar"    │
└─────────────────────────────────────────────┘
```

**Timeline**: 2-3 días implementación

### **Opción B: Multi-Platform (Mediano Plazo)**
```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ GARMIN   │  │ STRAVA   │  │ XIAOMI   │  │ POLAR    │
│ (Health) │  │ (Workout)│  │ (Manual) │  │ (Health) │
└────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘
     │             │             │             │
     └──────────┬──┴─────────────┴─────────────┘
                │
                ▼
     ┌─────────────────────┐
     │  HEALTH AGGREGATOR  │
     │  • Normalize data   │
     │  • Fill gaps        │
     │  • Calculate trends │
     └──────────┬──────────┘
                │
                ▼
     ┌─────────────────────┐
     │  COACH IA ENGINE    │
     │  • Readiness calc   │
     │  • Load management  │
     │  • Recommendations  │
     └─────────────────────┘
```

**Timeline**: 2-3 semanas

### **Opción C: Xiaomi Workaround (Manual Entry)**
```
Para usuarios Xiaomi/Amazfit SIN Garmin:

1. USER INPUT MANUAL:
   ┌─────────────────────────────────┐
   │  "Cómo te sientes hoy?"         │
   │  😊 Excelente (Ready)           │
   │  😐 Normal (Moderate)           │
   │  😴 Cansado (Recovery)          │
   └─────────────────────────────────┘
                    │
                    ▼
   ┌─────────────────────────────────┐
   │  Optional: Enter metrics        │
   │  • Resting HR: 62 bpm           │
   │  • Sleep: 7.5h                  │
   │  • Stress: Medium               │
   └─────────────────────────────────┘

2. AUTOMATIC FROM WORKOUTS:
   - Analizar HR durante workouts → Estimar fitness
   - Track workout frequency → Detectar overtraining
   - Monitor performance trends → Fatigue indicators

3. GOOGLE FIT INTEGRATION (Medium term):
   - Zepp → Google Fit (automatic)
   - Google Fit API → RunCoach
   - Access: Sleep, HR, Steps
```

---

## 🚀 Implementación Fase 1: Garmin Health Metrics

### 1. Database Schema
```python
# models.py - Add HealthMetric model

class HealthMetric(Base):
    """Daily health and wellness metrics"""
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    date = Column(DateTime, nullable=False, index=True)
    
    # Recovery Metrics
    hrv_ms = Column(Float, nullable=True)  # HRV in milliseconds
    resting_hr_bpm = Column(Integer, nullable=True)  # Resting heart rate
    
    # Sleep Metrics
    sleep_duration_minutes = Column(Integer, nullable=True)
    sleep_score = Column(Integer, nullable=True)  # 0-100
    deep_sleep_minutes = Column(Integer, nullable=True)
    rem_sleep_minutes = Column(Integer, nullable=True)
    light_sleep_minutes = Column(Integer, nullable=True)
    awake_minutes = Column(Integer, nullable=True)
    
    # Readiness Metrics
    body_battery = Column(Integer, nullable=True)  # 0-100 (Garmin)
    readiness_score = Column(Integer, nullable=True)  # 0-100 (normalized)
    stress_level = Column(Integer, nullable=True)  # 0-100
    
    # Activity Metrics
    steps = Column(Integer, nullable=True)
    calories_burned = Column(Integer, nullable=True)
    intensity_minutes = Column(Integer, nullable=True)
    
    # Respiratory
    respiration_rate = Column(Float, nullable=True)  # breaths/min
    spo2_percentage = Column(Float, nullable=True)  # Oxygen saturation
    
    # Metadata
    source = Column(String, nullable=False)  # garmin, polar, manual, google_fit
    data_quality = Column(String, default="high")  # high, medium, basic
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        # One record per user per day
        UniqueConstraint('user_id', 'date', name='uix_user_date'),
    )
```

### 2. Garmin Health Service
```python
# services/garmin_health_service.py

class GarminHealthService:
    """Fetch health metrics from Garmin Connect"""
    
    async def fetch_daily_summary(
        self, 
        api: GarminConnectAPI, 
        date: datetime
    ) -> Dict:
        """Get all health metrics for a specific date"""
        date_str = date.strftime("%Y-%m-%d")
        
        # Garmin API calls
        heart_rate = api.get_heart_rates(date_str)  # HRV + Resting HR
        sleep = api.get_sleep_data(date_str)
        stress = api.get_stress_data(date_str)
        body_battery = api.get_body_battery(date_str)
        steps = api.get_steps_data(date_str)
        
        return {
            "hrv_ms": heart_rate.get("heartRateVariability"),
            "resting_hr_bpm": heart_rate.get("restingHeartRate"),
            "sleep_duration_minutes": sleep.get("sleepTimeSeconds", 0) // 60,
            "sleep_score": sleep.get("sleepScore"),
            "deep_sleep_minutes": sleep.get("deepSleepSeconds", 0) // 60,
            "rem_sleep_minutes": sleep.get("remSleepSeconds", 0) // 60,
            "body_battery": body_battery[-1].get("charged") if body_battery else None,
            "stress_level": self._calculate_avg_stress(stress),
            "steps": steps.get("totalSteps")
        }
    
    async def sync_health_metrics(
        self,
        db: Session,
        user_id: int,
        days: int = 7
    ) -> List[HealthMetric]:
        """Sync last N days of health metrics"""
        # Get user's Garmin connection
        user = crud.get_user(db, user_id)
        api = self._restore_garmin_session(user)
        
        metrics = []
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            
            # Check if already exists
            existing = db.query(HealthMetric).filter(
                HealthMetric.user_id == user_id,
                HealthMetric.date == date.date()
            ).first()
            
            if existing:
                continue
            
            # Fetch and save
            data = await self.fetch_daily_summary(api, date)
            metric = HealthMetric(
                user_id=user_id,
                date=date,
                source="garmin",
                **data
            )
            db.add(metric)
            metrics.append(metric)
        
        db.commit()
        return metrics
```

### 3. Coach IA Integration
```python
# services/coach_service.py - Add health-aware recommendations

async def generate_workout_recommendation(
    self,
    user_id: int,
    db: Session
) -> Dict:
    """Generate workout rec based on health metrics"""
    
    # Get today's health metrics
    today_health = db.query(HealthMetric).filter(
        HealthMetric.user_id == user_id,
        HealthMetric.date == date.today()
    ).first()
    
    # Calculate readiness
    readiness = self._calculate_readiness(today_health)
    
    # Get recent workouts for context
    recent_workouts = self._get_recent_workouts(db, user_id, days=7)
    
    # Build prompt for Groq
    prompt = f"""
    Athlete readiness assessment:
    - Body Battery: {today_health.body_battery}/100
    - HRV: {today_health.hrv_ms}ms (baseline: {self._get_hrv_baseline(user_id)})
    - Resting HR: {today_health.resting_hr_bpm} bpm
    - Sleep: {today_health.sleep_duration_minutes/60:.1f}h (score: {today_health.sleep_score}/100)
    - Stress: {today_health.stress_level}/100
    - Readiness Score: {readiness}/100
    
    Recent training:
    {self._format_recent_workouts(recent_workouts)}
    
    Based on these metrics, recommend today's training:
    - Should they train hard, moderate, or rest?
    - What type of workout?
    - What intensity (pace/HR zones)?
    - Any precautions?
    """
    
    response = await self.groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": COACH_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    
    return {
        "readiness_score": readiness,
        "recommendation": response.choices[0].message.content,
        "should_train_hard": readiness >= 75,
        "health_alerts": self._generate_health_alerts(today_health)
    }

def _calculate_readiness(self, health: HealthMetric) -> int:
    """Calculate 0-100 readiness score"""
    if not health:
        return 50  # Neutral
    
    factors = []
    
    # Body Battery (40% weight)
    if health.body_battery:
        factors.append((health.body_battery, 0.4))
    
    # Sleep Score (30% weight)
    if health.sleep_score:
        factors.append((health.sleep_score, 0.3))
    
    # HRV vs Baseline (20% weight)
    if health.hrv_ms:
        baseline = self._get_hrv_baseline(health.user_id)
        hrv_score = min(100, (health.hrv_ms / baseline) * 100)
        factors.append((hrv_score, 0.2))
    
    # Resting HR vs Baseline (10% weight)
    if health.resting_hr_bpm:
        baseline = self._get_resting_hr_baseline(health.user_id)
        # Lower is better
        rhr_score = max(0, 100 - ((health.resting_hr_bpm - baseline) * 10))
        factors.append((rhr_score, 0.1))
    
    if not factors:
        return 50
    
    # Weighted average
    total_weight = sum(w for _, w in factors)
    weighted_sum = sum(score * weight for score, weight in factors)
    
    return int(weighted_sum / total_weight)
```

### 4. API Endpoints
```python
# routers/health.py - NEW

@router.get("/health/today")
async def get_today_health(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's health metrics"""
    health = db.query(models.HealthMetric).filter(
        models.HealthMetric.user_id == current_user.id,
        models.HealthMetric.date == date.today()
    ).first()
    
    if not health:
        return {"message": "No health data for today"}
    
    return health

@router.post("/health/sync")
async def sync_health_metrics(
    days: int = 7,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync health metrics from Garmin"""
    if not current_user.garmin_token:
        raise HTTPException(400, "Garmin not connected")
    
    service = GarminHealthService()
    metrics = await service.sync_health_metrics(db, current_user.id, days)
    
    return {
        "synced": len(metrics),
        "latest": metrics[0] if metrics else None
    }

@router.get("/health/readiness")
async def get_readiness_score(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get today's readiness score"""
    coach_service = CoachService()
    recommendation = await coach_service.generate_workout_recommendation(
        current_user.id, 
        db
    )
    
    return recommendation
```

---

## 📱 Frontend Components

### Health Dashboard
```tsx
// app/(dashboard)/health/page.tsx

export default function HealthPage() {
  const { data: health } = useQuery({
    queryKey: ['health', 'today'],
    queryFn: () => apiClient.getHealthToday()
  })
  
  const { data: readiness } = useQuery({
    queryKey: ['readiness'],
    queryFn: () => apiClient.getReadinessScore()
  })
  
  return (
    <div className="space-y-6">
      {/* Readiness Score Card */}
      <Card>
        <CardHeader>
          <CardTitle>Readiness Score</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <div className="text-6xl font-bold">
              {readiness?.readiness_score}/100
            </div>
            <div className="flex-1">
              <Progress value={readiness?.readiness_score} />
              <p className="mt-2 text-sm text-muted-foreground">
                {readiness?.should_train_hard ? 
                  "✅ Ready for hard training" : 
                  "⚠️ Consider light training"}
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
      
      {/* Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          icon="🫀"
          label="HRV"
          value={health?.hrv_ms}
          unit="ms"
        />
        <MetricCard
          icon="💤"
          label="Sleep"
          value={(health?.sleep_duration_minutes / 60).toFixed(1)}
          unit="h"
        />
        <MetricCard
          icon="🔋"
          label="Body Battery"
          value={health?.body_battery}
          unit="/100"
        />
        <MetricCard
          icon="❤️"
          label="Resting HR"
          value={health?.resting_hr_bpm}
          unit="bpm"
        />
      </div>
      
      {/* Coach Recommendation */}
      <Card>
        <CardHeader>
          <CardTitle>Coach Recommendation</CardTitle>
        </CardHeader>
        <CardContent>
          <p>{readiness?.recommendation}</p>
        </CardContent>
      </Card>
    </div>
  )
}
```

---

## 🎯 Roadmap

### **FASE 1: Garmin Health (Semana 1-2)** ✅ PRIORITY
- [ ] Database migration: Add `HealthMetric` model
- [ ] `GarminHealthService`: Fetch health endpoints
- [ ] API endpoints: `/health/today`, `/health/sync`
- [ ] Coach IA: Integrate readiness score into recommendations
- [ ] Frontend: Health dashboard with readiness score
- [ ] Testing: End-to-end health sync flow

### **FASE 2: Manual Entry (Semana 3)** ⏳
- [ ] Frontend: "How do you feel today?" widget
- [ ] Allow manual entry: Sleep hours, energy level, soreness
- [ ] Calculate readiness from manual inputs
- [ ] Fallback for non-Garmin users

### **FASE 3: Strava Enhancement (Semana 4)** ⏳
- [ ] Analyze workout HR patterns → Estimate fitness
- [ ] Track workout frequency → Detect overtraining
- [ ] Performance trends → Fatigue indicators
- [ ] No direct health metrics but infer from training

### **FASE 4: Multi-Platform (Mes 2-3)** 🔮
- [ ] Google Fit integration (for Xiaomi/Zepp)
- [ ] Polar AccessLink API
- [ ] Whoop API (premium users)
- [ ] Oura API (premium users)
- [ ] Normalize data across platforms

---

## 💡 Recomendación Final

### **Para MVP (Próximas 2 semanas)**:

1. **IMPLEMENTAR Garmin Health** (80% de runners serios usan Garmin)
   - Full health metrics via API
   - Ya tenemos OAuth implementado
   - 2-3 días desarrollo

2. **MANUAL ENTRY Widget** para usuarios sin Garmin
   - Simple "Cómo te sientes: 😊😐😴"
   - Optional: Sleep hours, resting HR
   - 1 día desarrollo

3. **Coach IA Integration**
   - Readiness score calculation
   - Health-aware recommendations
   - Alerts sobre overtraining
   - 2 días desarrollo

### **Total: ~1 semana** para tener sistema completo de health metrics con Garmin + fallback manual.

---

## 🔥 Impacto en Coach IA

Con health metrics, el Coach puede:

✅ **Prevenir lesiones**: "Tu HRV está 20% bajo, evita entrenamientos duros hoy"  
✅ **Optimizar rendimiento**: "Body Battery 85/100, perfecto para intervalos"  
✅ **Personalizar recomendaciones**: "Dormiste solo 5h, cambiamos workout duro por recuperación activa"  
✅ **Detectar sobreentrenamiento**: "3 días consecutivos de fatiga + aumento resting HR → Día de descanso obligatorio"  
✅ **Educar al atleta**: "Tu HRV ha mejorado 15% este mes, tu adaptación cardiovascular está funcionando"

**Sin health metrics**, el Coach solo ve workouts → Puede recomendar training plans pero no puede adaptar día a día según el estado del atleta.

**Con health metrics**, el Coach se vuelve un **verdadero entrenador personal** que monitorea tu bienestar 24/7.
