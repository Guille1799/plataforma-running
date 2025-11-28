# 📱 Guía de Integración de Health Metrics

## 🎯 ¿Para qué sirven las métricas de salud?

Las **health metrics** permiten que el Coach IA entienda tu estado de recuperación día a día y adapte tus entrenamientos para:

- ✅ **Prevenir sobreentrenamiento** - Detecta fatiga acumulada
- ✅ **Optimizar rendimiento** - Entrena duro cuando estás listo
- ✅ **Evitar lesiones** - Descansa cuando tu cuerpo lo necesita
- ✅ **Personalizar recomendaciones** - Basado en tu estado real

---

## 📊 ¿Qué métricas se rastrean?

### 🫀 Recuperación
- **HRV (Heart Rate Variability)**: Indicador #1 de recuperación
  - HRV alta → Sistema nervioso recuperado
  - HRV baja → Fatiga, necesitas descanso
- **Resting Heart Rate**: FC en reposo
  - Aumento de +5-10 bpm → Sobreentrenamiento o enfermedad
  - Bajando con el tiempo → Mejorando fitness

### 😴 Sueño
- **Duración total**: 7-9 horas óptimo
- **Sleep Score**: Calidad general (0-100)
- **Deep Sleep**: Recuperación muscular
- **REM Sleep**: Recuperación mental

### 🔋 Energía
- **Body Battery** (Garmin): Score 0-100
- **Readiness Score**: Normalizado entre plataformas
- **Stress Level**: 0-100 (menor = mejor)

### 🏃 Actividad
- **Steps**: Pasos diarios
- **Calories**: Calorías quemadas
- **Intensity Minutes**: Minutos de actividad moderada-vigorosa

---

## 🔌 Opciones de Integración

### 🥇 **OPCIÓN 1: Garmin (Recomendado para runners serios)**

**¿Por qué Garmin?**
- ✅ Métricas más completas (HRV, Body Battery, Sleep stages, Stress)
- ✅ Actualización automática 24/7
- ✅ Datos de mayor calidad
- ✅ Compatible con Garmin Forerunner, Fenix, Venu, etc.

**¿Cómo conectar?**

1. **Backend**: Conecta tu cuenta Garmin
```bash
POST /garmin/connect
{
  "email": "tu_email@garmin.com",
  "password": "tu_password"
}
```

2. **Sincronizar health metrics**:
```bash
POST /health/sync/garmin?days=7
```

3. **Ver tu readiness score**:
```bash
GET /health/readiness
```

**Frecuencia**: Sincroniza automáticamente cada día.

---

### 🥈 **OPCIÓN 2: Google Fit (Para Xiaomi/Amazfit/Android)**

**¿Por qué Google Fit?**
- ✅ Perfecto para usuarios de Xiaomi/Amazfit vía Zepp
- ✅ Sincronización automática: Zepp → Google Fit → RunCoach
- ✅ Funciona con 50+ marcas de dispositivos
- ✅ Free forever

**¿Cómo conectar?**

1. **Conecta tu reloj a Zepp**:
   - Abre Zepp app (Xiaomi/Amazfit)
   - Vincula tu reloj

2. **Conecta Zepp con Google Fit**:
   - Zepp app → Profile → Third-party access
   - Habilita Google Fit
   - Autoriza conexión

3. **Conecta Google Fit con RunCoach**:
```bash
GET /health/connect/google-fit
# Sigue el auth_url y autoriza
```

4. **Sincronizar datos**:
```bash
POST /health/sync/google-fit?days=7
```

**Qué datos obtienes**:
- ✅ Resting HR
- ✅ Sleep duration y stages
- ✅ Steps y calories
- ⚠️ NO HRV (Xiaomi no expone via Google Fit)
- ⚠️ NO Body Battery (métrica exclusiva de Garmin)

**Frecuencia**: Ejecuta sync diariamente o automatiza con cron job.

---

### 🥉 **OPCIÓN 3: Apple Health (Para iPhone)**

**¿Por qué Apple Health?**
- ✅ Ideal para usuarios de Apple Watch
- ✅ Métricas completas si usas Apple Watch
- ✅ Datos de salud integrados del iPhone
- ⚠️ Requiere export manual (no hay API pública)

**¿Cómo conectar?**

1. **Exporta datos desde iPhone**:
   - Abre app **Salud** (Health)
   - Tap tu foto de perfil (arriba derecha)
   - **Exportar todos los datos de salud**
   - Espera a que se genere export.zip
   - Extrae el archivo `export.xml`

2. **Importa a RunCoach**:
```bash
POST /health/import/apple-health
Content-Type: multipart/form-data

file: export.xml
max_days: 30
```

**Qué datos obtienes**:
- ✅ HRV (si usas Apple Watch)
- ✅ Resting HR
- ✅ Sleep duration
- ✅ Steps y active calories

**Frecuencia**: Re-exporta cada semana o mes para actualizar datos.

---

### 🆘 **OPCIÓN 4: Manual Entry (Universal Fallback)**

**¿Por qué manual?**
- ✅ Funciona con CUALQUIER dispositivo
- ✅ No requiere conexiones técnicas
- ✅ Captura tu percepción subjetiva
- ⚠️ Requiere disciplina diaria

**¿Cómo usar?**

Cada mañana, registra cómo te sientes:

```bash
POST /health/manual
{
  "date": "2025-11-14",
  "energy_level": 4,        // 1=Muy bajo, 5=Excelente
  "soreness_level": 2,      // 1=Sin molestias, 5=Muy dolorido
  "mood": 4,                // 1=Mal, 5=Excelente
  "motivation": 5,          // 1=Ninguna, 5=Muy motivado
  "sleep_duration_minutes": 450,  // 7.5 horas
  "resting_hr_bpm": 52,
  "notes": "Me siento genial, listo para entrenar duro"
}
```

**Qué datos obtienes**:
- ✅ Tu percepción de energía y recuperación
- ✅ Sleep duration (manual)
- ✅ Resting HR (si lo mides)
- ✅ Notas personalizadas

**Frecuencia**: Diaria, toma 30 segundos.

---

## 🤖 ¿Cómo usa el Coach IA estas métricas?

### Readiness Score (0-100)

El Coach calcula un **Readiness Score** que combina:

```
Readiness = 40% Body Battery/Readiness
          + 30% Sleep Quality
          + 20% HRV vs Baseline
          + 10% Resting HR vs Baseline
          + Bonus: Stress Level
```

### Interpretación:

| Score | Estado | Recomendación |
|-------|--------|---------------|
| 75-100 | ✅ **Excelente** | Perfecto para entrenamientos intensos (intervals, tempo runs) |
| 60-74 | ⚠️ **Moderado** | Entrenamientos ligeros o moderados (aerobic base, easy runs) |
| 0-59 | 🛑 **Bajo** | Día de descanso o recuperación activa (caminar, stretching) |

### Ejemplo Real:

```json
{
  "readiness_score": 82,
  "confidence": "high",
  "factors": [
    {"name": "Body Battery", "score": 85, "status": "good"},
    {"name": "Sleep Quality", "score": 75, "status": "good"},
    {"name": "HRV", "score": 95, "status": "good", "detail": "65ms (baseline: 62ms)"},
    {"name": "Resting HR", "score": 90, "status": "good", "detail": "52 bpm (baseline: 54 bpm)"}
  ],
  "recommendation": "✅ Excelente estado de recuperación. Perfecto para entrenamientos intensos.",
  "should_train_hard": true
}
```

### AI Recommendation:

```
Con tu Readiness Score de 82/100, estás en un estado óptimo de recuperación.

WORKOUT RECOMENDADO HOY:
🏃 Intervalos 5x1000m

Intensidad: Zona 4 (Threshold)
- Pace objetivo: 4:15-4:25 min/km
- FC objetivo: 165-175 bpm
- Recuperación: 2min trote suave entre reps

Duración total: 45-50 minutos (incluye calentamiento y enfriamiento)

TU CUERPO ESTÁ LISTO:
✅ Body Battery 85/100 - Energía excelente
✅ HRV 5% por encima de tu baseline - Sistema nervioso recuperado
✅ Dormiste 7.5h con buen sueño profundo

PRECAUCIONES:
- Calienta bien 15min antes de intervalos
- Si sientes fatiga inesperada en rep 3, acorta la sesión
- Hidrátate bien post-workout
```

---

## 🔄 Automatización

### Sync Diario Automático (Backend)

Puedes crear un cron job para sincronizar datos automáticamente:

```python
# sync_health_daily.py
import requests

def sync_all_users_health():
    users = get_all_users_with_connections()
    
    for user in users:
        token = user.access_token
        
        # Garmin
        if user.garmin_token:
            requests.post(
                f"{API_URL}/health/sync/garmin",
                headers={"Authorization": f"Bearer {token}"},
                params={"days": 1}
            )
        
        # Google Fit
        if user.google_fit_token:
            requests.post(
                f"{API_URL}/health/sync/google-fit",
                headers={"Authorization": f"Bearer {token}"},
                params={"days": 1}
            )

# Run daily at 6 AM
```

### Frontend: Daily Check-in Widget

```tsx
// components/DailyCheckIn.tsx
export function DailyCheckIn() {
  const [energy, setEnergy] = useState(3)
  
  async function submitCheckIn() {
    await apiClient.post('/health/manual', {
      date: new Date().toISOString().split('T')[0],
      energy_level: energy,
      soreness_level: soreness,
      mood: mood,
      motivation: motivation
    })
  }
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>¿Cómo te sientes hoy?</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div>
            <Label>Nivel de energía</Label>
            <Slider value={[energy]} onValueChange={([v]) => setEnergy(v)} min={1} max={5} />
            <p className="text-sm">{energyLabels[energy]}</p>
          </div>
          {/* ... otros campos ... */}
          <Button onClick={submitCheckIn}>Guardar</Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

---

## 📈 Endpoints Disponibles

### Consultar Datos
```bash
GET /health/today                    # Métricas de hoy
GET /health/history?days=30          # Historial
GET /health/readiness                # Readiness score
GET /health/recommendation           # Recomendación AI completa
GET /health/insights/trends          # Tendencias (HRV, sleep, etc.)
```

### Sincronización Automática
```bash
POST /health/sync/garmin?days=7      # Garmin
POST /health/sync/google-fit?days=7  # Google Fit
```

### OAuth Setup
```bash
GET  /health/connect/google-fit      # Obtener auth URL
POST /health/callback/google-fit     # Callback OAuth
```

### Import/Manual
```bash
POST /health/import/apple-health     # Upload export.xml
POST /health/manual                  # Manual entry
```

---

## 🎯 Resumen: ¿Qué opción elegir?

| Dispositivo | Método Recomendado | Calidad | Automatización |
|-------------|-------------------|---------|----------------|
| **Garmin Forerunner/Fenix** | Garmin API | ⭐⭐⭐⭐⭐ | Automático |
| **Xiaomi Mi Band/Amazfit** | Google Fit | ⭐⭐⭐⭐ | Automático |
| **Apple Watch** | Apple Health | ⭐⭐⭐⭐ | Manual export |
| **Polar/Suunto/Coros** | Strava (workouts) + Manual (health) | ⭐⭐⭐ | Semi-auto |
| **Sin reloj inteligente** | Manual Entry | ⭐⭐ | Manual |

---

## ❓ FAQ

**P: ¿Puedo usar múltiples fuentes?**
R: Sí, pero solo se guardará un registro por día. Prioridad: Garmin > Google Fit > Apple Health > Manual

**P: ¿Qué pasa si no tengo datos hoy?**
R: El Coach usará tu última entrada y dará recomendaciones genéricas. Readiness Score = 50 (neutral).

**P: ¿Mis datos son privados?**
R: Sí, solo tú y el Coach IA tienen acceso. No se comparten con terceros.

**P: ¿Puedo editar entradas pasadas?**
R: Sí, con POST /health/manual puedes actualizar cualquier día.

**P: ¿Google Fit funciona con Zepp?**
R: Sí, pero Zepp → Google Fit solo sincroniza sleep y steps. No HRV ni stress.

**P: ¿Apple Health requiere Apple Watch?**
R: No, pero sin Apple Watch solo tendrás steps y sleep duration (del iPhone). HRV requiere Apple Watch.

---

## 🚀 Próximos Pasos

1. **Elige tu método** de integración
2. **Conecta tu dispositivo** siguiendo las instrucciones arriba
3. **Sincroniza tus datos** (automático o manual)
4. **Consulta tu Readiness Score** cada mañana
5. **Sigue las recomendaciones del Coach IA**

¡Tu entrenamiento ahora está personalizado 24/7 basado en tu estado real de recuperación! 🎉
