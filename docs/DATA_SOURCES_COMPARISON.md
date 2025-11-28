# Comparativa Completa: Fuentes de Datos para RunCoach AI

## 📊 Tabla de Dispositivos y Métodos de Integración

| Dispositivo | Método Principal | Método Alternativo | Sync Automático | Métricas | Data Quality |
|-------------|------------------|-------------------|-----------------|----------|--------------|
| **Garmin** | OAuth Garmin Connect | Upload FIT manual | ✅ Sí | 18+ (form completa) | `high` |
| **Xiaomi/Amazfit** | **Strava (via Zepp)** | Upload GPX manual | ✅ Sí (via Strava) | 13 (sin form) | `medium` |
| **Polar** | Strava | Upload FIT/GPX | ✅ Sí (via Strava) | 15-18 | `high` (FIT) / `medium` (GPX) |
| **Suunto** | Strava | Upload FIT/GPX | ✅ Sí (via Strava) | 15-18 | `high` (FIT) / `medium` (GPX) |
| **Wahoo** | Strava | Upload FIT manual | ✅ Sí (via Strava) | 15-18 | `high` |
| **Coros** | Strava | Upload FIT manual | ✅ Sí (via Strava) | 15-18 | `high` |
| **Apple Watch** | Strava (via Health) | - | ✅ Sí (via Strava) | 12-15 | `medium` |
| **Samsung Galaxy Watch** | Strava (via Samsung Health) | - | ✅ Sí (via Strava) | 12-15 | `medium` |

---

## 🔄 Flujos de Sincronización

### **Opción 1: Garmin Directo (MEJOR para Garmin users)**
```
Garmin Watch → Garmin Connect → RunCoach (OAuth)
              (automático)        (automático)
```
**Ventajas:**
- ✅ Métricas running form completas (18+)
- ✅ Ground contact time, vertical oscillation, L/R balance
- ✅ Training Effect, Recovery Time
- ✅ Sincronización instantánea

**Desventajas:**
- ❌ Solo funciona con Garmin

---

### **Opción 2: Strava Universal (MEJOR para todos los demás)**
```
Any Device → Brand App → Strava → RunCoach (OAuth)
           (automático) (automático) (automático)
```

#### **Ejemplo: Xiaomi/Amazfit**
```
Mi Band 7 → Zepp App → Strava → RunCoach
         (auto)     (auto)    (auto)
```

#### **Ejemplo: Polar**
```
Polar Vantage → Polar Flow → Strava → RunCoach
              (auto)       (auto)    (auto)
```

**Ventajas:**
- ✅ Funciona con 50+ dispositivos
- ✅ Sincronización automática end-to-end
- ✅ Usuario solo conecta 2 veces (app → Strava, Strava → RunCoach)
- ✅ Todas las métricas básicas + HR + elevation
- ✅ Strava es gratis

**Desventajas:**
- ❌ Pierde métricas avanzadas de Garmin (form analysis)
- ❌ Cadencia en RPM (necesita conversión)

---

### **Opción 3: Upload Manual (Fallback)**
```
Any Device → Brand App → Export File → RunCoach (Upload)
                        (manual)      (manual)
```

**Ventajas:**
- ✅ Funciona siempre
- ✅ FIT files mantienen todas las métricas

**Desventajas:**
- ❌ Requiere acción manual cada vez
- ❌ Fricción alta
- ❌ Usuario puede olvidarse

---

## 📈 Métricas por Fuente de Datos

### **Garmin Direct (OAuth) - `data_quality: high`**
```json
{
  "distance_meters": 5000,
  "duration_seconds": 1800,
  "avg_heart_rate": 145,
  "max_heart_rate": 175,
  "avg_pace": 6.0,
  "avg_cadence": 170,
  "avg_stride_length": 1.18,
  "avg_vertical_oscillation": 8.5,
  "avg_ground_contact_time": 245,
  "left_right_balance": 49.5,
  "avg_leg_spring_stiffness": 7.8,
  "training_effect_aerobic": 3.2,
  "training_effect_anaerobic": 1.5,
  "vo2max_estimate": 52,
  "source_type": "garmin_oauth",
  "data_quality": "high"
}
```

### **Strava (OAuth) - `data_quality: medium`**
```json
{
  "distance_meters": 5000,
  "duration_seconds": 1800,
  "avg_heart_rate": 145,
  "max_heart_rate": 175,
  "avg_pace": 6.0,
  "avg_cadence": 85,  // RPM (steps/min * 2)
  "elevation_gain": 150,
  "calories": 350,
  "avg_speed": 2.78,
  "max_speed": 3.5,
  "source_type": "strava",
  "data_quality": "medium"
}
```

### **GPX Upload - `data_quality: medium/basic`**
```json
{
  "distance_meters": 5000,
  "duration_seconds": 1800,
  "avg_heart_rate": 145,  // Si está en extensiones
  "max_heart_rate": 175,
  "avg_pace": 6.0,
  "elevation_gain": 150,
  "calories": 350,  // Estimado
  "source_type": "gpx_upload",
  "data_quality": "medium"  // o "basic" si no hay HR
}
```

---

## 🎯 Estrategia de Onboarding

### **Paso 1: Detectar dispositivo del usuario**
```typescript
const devices = [
  { name: "Garmin", method: "direct", quality: "high" },
  { name: "Xiaomi/Amazfit", method: "strava", quality: "medium" },
  { name: "Polar", method: "strava", quality: "medium" },
  { name: "Suunto", method: "strava", quality: "medium" },
  { name: "Apple Watch", method: "strava", quality: "medium" },
  { name: "Otro", method: "upload", quality: "varies" }
]
```

### **Paso 2: Mostrar flujo recomendado**
```typescript
if (device === "Garmin") {
  return <ConnectGarmin />
} else if (device in ["Xiaomi", "Polar", "Suunto", "Apple"]) {
  return (
    <ConnectStrava 
      instructions={`
        1. Conecta ${device} con Strava (app nativa)
        2. Conecta Strava con RunCoach
        3. ¡Listo! Sync automático activado
      `}
    />
  )
} else {
  return <ManualUpload />
}
```

---

## 💡 Recomendaciones por Usuario

### **Runner con Garmin**
→ Conectar Garmin Connect directamente
→ Métricas completas, training effect, recovery

### **Runner con Xiaomi/Amazfit**
→ Conectar Zepp → Strava → RunCoach
→ Sync automático, métricas esenciales

### **Runner con múltiples dispositivos**
→ Conectar todos a Strava
→ Strava como hub central
→ Una sola conexión RunCoach ↔ Strava

### **Runner profesional con Garmin**
→ Garmin Connect + Strava
→ RunCoach lee de Garmin (más completo)
→ Strava como respaldo/social

---

## 🔮 Roadmap de Integraciones

### **Corto Plazo (MVP)**
- ✅ Garmin OAuth
- ✅ Strava OAuth
- ✅ Upload FIT/GPX/TCX
- ✅ Enhanced GPX parser

### **Medio Plazo**
- 📋 Wahoo API (si disponible)
- 📋 Coros API (si disponible)
- 📋 TrainingPeaks import
- 📋 Batch upload (múltiples archivos)

### **Largo Plazo**
- 📋 Zepp Health API (requiere partnership)
- 📋 Apple HealthKit
- 📋 Google Fit
- 📋 Webhook automático de Strava
