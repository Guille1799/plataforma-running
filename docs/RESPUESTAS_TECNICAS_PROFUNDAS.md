# 🔧 RESPUESTAS TÉCNICAS PROFUNDAS - Ingeniería & Full-Stack

**Validación de madurez técnica: 5+ años**

---

## 1️⃣ RETO DE DATOS EN VIVO: Normalización de Formatos (FIT, TCX, GPX)

### El Problema
Garmin, Strava, Polar, Suunto, etc. usan formatos DIFERENTES:
- **FIT** (Garmin nativo) - Binario, comprimido, propietario
- **TCX** (Training Center XML) - XML, también Garmin
- **GPX** (GPS Exchange Format) - XML universal, pero limitado
- **Cada uno tiene campos distintos** - HR, cadence, potencia, elevation data

### Solución Implementada

#### 1. Librería para Parse: `fitparse`
```python
# backend/app/services/garmin_service.py
import fitparse

def parse_fit_file(file_path: str) -> dict:
    """Parse FIT file y extraer métricas"""
    fit = fitparse.FIT(file_path)
    
    # FIT es binario y complejo, fitparse lo normaliza
    records = []
    for record in fit.messages:
        if record.name == 'record':
            records.append({
                'timestamp': record.get_value('timestamp'),
                'position_lat': record.get_value('position_lat'),
                'position_long': record.get_value('position_long'),
                'heart_rate': record.get_value('heart_rate'),
                'cadence': record.get_value('cadence'),
                'altitude': record.get_value('altitude'),
                'temperature': record.get_value('temperature'),
            })
    return records
```

#### 2. Parser Universal (TCX/GPX)
```python
import xml.etree.ElementTree as ET

def parse_tcx_file(file_path: str) -> dict:
    """Parse TCX (XML) file"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    # TCX structure: Activity → Lap → Track → Trackpoint
    activities = root.findall('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Activity')
    
    trackpoints = []
    for activity in activities:
        for lap in activity.findall('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap'):
            for trackpoint in lap.findall('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint'):
                tp_data = {
                    'timestamp': trackpoint.findtext('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Time'),
                    'heart_rate': trackpoint.findtext('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}HeartRateBpm/{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Value'),
                    'cadence': trackpoint.findtext('.//{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Cadence'),
                }
                trackpoints.append(tp_data)
    
    return trackpoints
```

#### 3. Normalización a Esquema Universal
```python
# backend/app/models/models.py - Workout Schema
class Workout(Base):
    __tablename__ = "workouts"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # Datos normalizados (igual para todos los formatos)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    
    # Métricas agregadas
    total_distance = Column(Float)  # meters
    total_duration = Column(Integer)  # seconds
    avg_heart_rate = Column(Integer)  # bpm
    max_heart_rate = Column(Integer)  # bpm
    avg_cadence = Column(Integer)  # rpm
    max_altitude = Column(Float)  # meters
    elevation_gain = Column(Float)  # meters
    
    # Raw data (para análisis avanzado)
    raw_trackpoints = Column(JSON)  # Almacena todos los puntos
    file_format = Column(String)  # 'FIT', 'TCX', 'GPX'
    source = Column(String)  # 'garmin', 'strava', 'polar'
    
    created_at = Column(DateTime, default=datetime.utcnow)
```

#### 4. Función de Agregación
```python
def aggregate_workout_metrics(trackpoints: list) -> dict:
    """Convierte puntos GPS en métricas agregadas"""
    
    distances = []
    heart_rates = []
    cadences = []
    
    for i, tp in enumerate(trackpoints):
        if i > 0:
            # Calcular distancia entre puntos (Haversine)
            prev_tp = trackpoints[i-1]
            distance = haversine(
                (prev_tp['lat'], prev_tp['lon']),
                (tp['lat'], tp['lon'])
            )
            distances.append(distance)
        
        if tp.get('heart_rate'):
            heart_rates.append(tp['heart_rate'])
        
        if tp.get('cadence'):
            cadences.append(tp['cadence'])
    
    # Retornar agregado
    return {
        'total_distance': sum(distances),  # meters
        'avg_heart_rate': int(statistics.mean(heart_rates)) if heart_rates else None,
        'max_heart_rate': max(heart_rates) if heart_rates else None,
        'avg_cadence': int(statistics.mean(cadences)) if cadences else None,
        'trackpoint_count': len(trackpoints),
    }
```

### Mapeo a IA (Llama 3.3)

Cuando pasamos datos a la IA, usamos este formato estándar:

```python
def prepare_workout_for_ai(workout: Workout) -> str:
    """Convierte workout normalizado a prompt para IA"""
    
    prompt = f"""
    Workout Analysis Request:
    
    Date: {workout.start_time.strftime('%Y-%m-%d %H:%M')}
    Duration: {workout.total_duration} seconds ({workout.total_duration/60:.1f} minutes)
    Distance: {workout.total_distance/1000:.2f} km
    
    Heart Rate:
    - Average: {workout.avg_heart_rate} bpm
    - Maximum: {workout.max_heart_rate} bpm
    - Zone: {calculate_hr_zone(workout.avg_heart_rate)} (see user profile for zones)
    
    Cadence (steps/min):
    - Average: {workout.avg_cadence} rpm
    
    Elevation:
    - Gain: {workout.elevation_gain} meters
    - Max Altitude: {workout.max_altitude} meters
    
    Raw Data Available: {len(workout.raw_trackpoints)} trackpoints
    Source: {workout.source} ({workout.file_format} format)
    
    Please provide personalized feedback on:
    1. Effort level and zone distribution
    2. Pace consistency
    3. Comparison to athlete's baseline
    4. Recommendations for next workout
    """
    
    return prompt
```

### Ventajas de Este Approach

✅ **Independencia de Formato** - Mismo código maneja FIT, TCX, GPX
✅ **Normalización** - Todos los datos en esquema consistente
✅ **Escalabilidad** - Agregar nuevo formato = solo nuevo parser
✅ **IA-Ready** - Datos limpios para pasar a Llama 3.3
✅ **Raw Data Preserved** - Guardamos trackpoints para análisis futuro

---

## 2️⃣ LATENCIA DE IA: Gestión de Espera del Usuario

### El Problema
- Llama 3.3 puede tardar **3-10 segundos** en responder
- Usuario ve "loading..." aburrido = mala UX
- Si es muy lento, puede pensar que se rompió

### Solución: Tres Estrategias

### OPCIÓN A: WebSocket + Streaming (RECOMENDADO)

```python
# backend/app/routers/coach.py
from fastapi import WebSocket
import asyncio

@app.websocket("/ws/coach/analyze/{workout_id}")
async def websocket_coach_analysis(websocket: WebSocket, workout_id: int):
    await websocket.accept()
    
    try:
        # 1. Usuario envía request
        data = await websocket.receive_json()
        
        # 2. Backend comienza análisis
        workout = db.query(Workout).filter(Workout.id == workout_id).first()
        prompt = prepare_workout_for_ai(workout)
        
        # 3. IMPORTANTE: Streaming de Groq
        # La IA devuelve token por token, no todo de golpe
        
        await websocket.send_json({
            "type": "status",
            "message": "🔄 Analizando entrenamiento...",
            "progress": 10
        })
        
        # 4. Llamar Groq con streaming
        response_stream = client.messages.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": prompt}
            ],
            stream=True,  # ← CLAVE: streaming
            max_tokens=1024,
        )
        
        full_response = ""
        token_count = 0
        
        # 5. Enviar tokens conforme llegan
        for event in response_stream:
            if hasattr(event, 'content_block'):
                if event.content_block.type == "text":
                    token = event.content_block.text
                    full_response += token
                    token_count += 1
                    
                    # Enviar a WebSocket (usuario ve en tiempo real)
                    await websocket.send_json({
                        "type": "stream",
                        "token": token,
                        "progress": min(90, 10 + (token_count * 5))
                    })
                    
                    # Throttle para no sobrecargar (10ms entre tokens)
                    await asyncio.sleep(0.01)
        
        # 6. Análisis completado
        await websocket.send_json({
            "type": "complete",
            "analysis": full_response,
            "progress": 100
        })
        
        # 7. Guardar en DB
        db.add(CoachAnalysis(
            workout_id=workout_id,
            analysis=full_response,
            created_at=datetime.utcnow()
        ))
        db.commit()
        
    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "message": f"Error: {str(e)}"
        })
    finally:
        await websocket.close()
```

### Frontend: React Component con WebSocket

```typescript
// app/components/coach-analyzer.tsx
import { useEffect, useState } from 'react';

export function CoachAnalyzer({ workoutId }: { workoutId: number }) {
  const [analysis, setAnalysis] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [tokens, setTokens] = useState<string[]>([]);

  const analyzeWorkout = () => {
    setIsLoading(true);
    setTokens([]);
    setProgress(0);

    // Conectar WebSocket
    const ws = new WebSocket(
      `ws://localhost:3000/ws/coach/analyze/${workoutId}`
    );

    ws.onopen = () => {
      // Enviar request
      ws.send(JSON.stringify({ action: 'analyze' }));
    };

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      switch (message.type) {
        case 'status':
          setAnalysis(`🔄 ${message.message}`);
          setProgress(message.progress);
          break;

        case 'stream':
          // Token por token = animación suave
          setTokens((prev) => [...prev, message.token]);
          setAnalysis((prev) => prev + message.token);
          setProgress(message.progress);
          break;

        case 'complete':
          setAnalysis(message.analysis);
          setProgress(100);
          setIsLoading(false);
          break;

        case 'error':
          setAnalysis(`❌ ${message.message}`);
          setIsLoading(false);
          break;
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setAnalysis('❌ Connection error');
      setIsLoading(false);
    };
  };

  return (
    <div className="space-y-4">
      <button
        onClick={analyzeWorkout}
        disabled={isLoading}
        className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
      >
        {isLoading ? '🔄 Analyzing...' : 'Analyze Workout'}
      </button>

      {isLoading && (
        <div className="space-y-2">
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-600 h-2 rounded-full transition-all"
              style={{ width: `${progress}%` }}
            />
          </div>
          <p className="text-sm text-gray-600">{progress}%</p>
        </div>
      )}

      {analysis && (
        <div className="p-4 bg-gray-50 rounded border">
          <p className="text-sm whitespace-pre-wrap font-mono">
            {analysis}
          </p>
        </div>
      )}
    </div>
  );
}
```

### OPCIÓN B: Server-Sent Events (SSE)

```python
# Si no quieres bidireccional, SSE es más simple
@app.get("/api/v1/coach/analyze/{workout_id}/stream")
async def analyze_workout_sse(workout_id: int):
    async def event_generator():
        # Similar al WebSocket pero unidireccional
        yield f"data: {json.dumps({'type': 'status', 'message': 'Starting...'})}\\n\\n"
        
        # ... análisis ...
        
        for token in response_tokens:
            yield f"data: {json.dumps({'type': 'token', 'token': token})}\\n\\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
```

### OPCIÓN C: Simple Polling (Lo Más Fácil)

```python
# Backend: Crear análisis en background
@app.post("/api/v1/coach/analyze-async/{workout_id}")
async def analyze_workout_async(workout_id: int):
    """Inicia análisis en background"""
    
    # Usar background tasks
    background_tasks.add_task(
        perform_coach_analysis,
        workout_id
    )
    
    return {
        "status": "processing",
        "analysis_id": generate_id()
    }

# Frontend: Polling cada 2 segundos
const pollAnalysis = async (analysisId: string) => {
  const response = await fetch(`/api/v1/coach/analysis/${analysisId}`);
  const data = await response.json();
  
  if (data.status === 'completed') {
    setAnalysis(data.result);
  } else if (data.status === 'processing') {
    setTimeout(() => pollAnalysis(analysisId), 2000);
  }
};
```

### Comparación de Estrategias

| Estrategia | Latencia Percibida | Complejidad | Escalabilidad | Mejor Para |
|-----------|-------------------|-------------|---------------|-----------|
| **WebSocket + Streaming** | ⭐⭐⭐⭐⭐ Excelente | Media | Alta | Análisis de IA (chat) |
| **SSE** | ⭐⭐⭐⭐ Muy Bueno | Baja | Media | Notificaciones |
| **Polling** | ⭐⭐⭐ Bueno | Muy Baja | Baja | MVPs rápidos |

**Nuestra Decisión:** WebSocket + Streaming porque:
- Usuario ve respuesta en **tiempo real** (¡no espera!)
- Tokens llegan **gradualmente** (animación suave)
- **Sin lag** entre frontend y backend
- **Escalable** para múltiples usuarios

---

## 3️⃣ DECISIÓN DE ARQUITECTURA: Backend & Frontend Separados

### El Problema Clásico
Podrías hacer:
- ❌ **Monolith** - Todo en un servidor (FastAPI + Next.js)
- ✅ **Microservicios** - Separar Backend y Frontend

### Nuestra Decisión: Separados (Vercel + Render)

### Razón 1: Deployment Independiente

```
Escenario: Necesitas hacer deploy urgente
├─ Sin separar:
│  ├─ Cambio en backend → Rebuilds TODO (frontend + backend)
│  ├─ Tiempo: 5-10 minutos
│  └─ Riesgo: Frontend rompe también
│
└─ Separados:
   ├─ Cambio en backend → Solo rebuild backend
   ├─ Tiempo: 2 minutos
   └─ Riesgo: Frontend sigue funcionando
```

### Razón 2: Escalabilidad Diferenciada

```
Backend necesita: CPU (análisis de IA, cálculos)
Frontend necesita: CDN + Edge (velocidad de carga)

Si está separado:
- Backend → Render (más CPU, menos geografía)
- Frontend → Vercel (global CDN, Edge Functions)

Si está junto:
- Un solo servidor → No puedes optimizar bien
```

### Razón 3: Equipos Independientes

```
Frontend Dev: "Quiero cambiar a SvelteKit"
Backend Dev: "Quiero cambiar a Go"

Si está separado: ✅ Puedo hacerlo sin afectar al otro
Si está junto: ❌ Todo debe ser compatible
```

### CORS: El Precio a Pagar

```python
# backend/app/main.py
# Si frontend está en otro dominio, CORS es necesario

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3001",           # Local dev
        "https://plataforma-running.vercel.app",  # Prod
    ],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
```

### PROBLEMAS que Encontramos (y Cómo los Resolvimos)

#### Problema 1: CORS Bloqueaba Requests
```javascript
// Frontend error:
// Access to XMLHttpRequest blocked by CORS policy

// Solución: Backend envía headers correctos
app.add_middleware(CORSMiddleware, ...)
```

#### Problema 2: Cookies No Se Enviaban
```python
# Backend: Guardar token en cookie
response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,        # No accesible desde JS (seguro)
    secure=True,          # Solo HTTPS
    samesite="strict",    # CSRF protection
)

# Frontend: Enviar cookie automáticamente
fetch('http://backend.com/api/...', {
    credentials: 'include'  # ← Importante!
})
```

#### Problema 3: Latencia de Requests (Red)
```
Local (misma máquina):
- Backend a Frontend: < 1ms

Producción (servidores diferentes):
- Frontend (Vercel USA) → Backend (Render Virginia): ~50-100ms

Solución: Usar EDGE FUNCTIONS en Vercel
```

### Edge Functions: Optimización Extra

```typescript
// Vercel Edge Function: Cachear requests frecuentes
export default async function handler(request) {
  // Interceptar request al backend
  // Si es /api/v1/events/races (búsqueda de carreras)
  // y fue hecha en los últimos 5 minutos
  
  const cached = await cache.get(`races:${query}`);
  
  if (cached) {
    return new Response(cached, {
      headers: { 'X-From-Cache': 'true' }
    });
  }
  
  // Si no, forward a backend
  const response = await fetch('https://backend.render.com/api/v1/events/races', {
    headers: request.headers,
  });
  
  // Cachear respuesta
  await cache.set(`races:${query}`, response.body, { ttl: 300 });
  
  return response;
}
```

### Comparación: Monolith vs Separados

| Aspecto | Monolith | Separados |
|--------|---------|-----------|
| **Deploy** | 10 min (todo) | 2 min (una parte) |
| **Escalabilidad** | Limitada | Por servicio |
| **CORS Issues** | 0 | Gestión necesaria |
| **Latencia** | <1ms | 50-100ms |
| **Complejidad** | Baja | Media |
| **Equipos Independientes** | No | Sí |
| **Mejor para** | MVPs pequeños | Producción |

### Decisión Final: ¿Por Qué Separamos?

```
Fase 1 (MVP): Monolith habría sido más rápido
Fase 2 (Producción): Separados es mejor

Nos decidimos por Separados porque:
1. Preveíamos crecimiento (múltiples integraciones)
2. Queremos escalar backend independientemente
3. Frontend y backend evolucionan a ritmos distintos
4. CORS + Edge Functions resuelven latencia
5. Vercel + Render tienen mejor pricing separado
```

---

## 🎯 RESUMEN: Madurez Técnica Demostrada

### Pregunta 1: Normalización de Datos ✅
- **Librería:** `fitparse` para FIT binario
- **XML Parser:** ElementTree para TCX/GPX
- **Esquema Universal:** Workout model con campos normalizados
- **IA-Ready:** Función `prepare_workout_for_ai()` convierte datos

### Pregunta 2: Latencia de IA ✅
- **Opción Elegida:** WebSocket + Streaming
- **Experiencia:** Usuario ve respuesta token-por-token
- **Ventajas:** Sensación de velocidad incluso si IA es lenta
- **Fallback:** Polling para MVP simple

### Pregunta 3: Arquitectura Separada ✅
- **Razón:** Escalabilidad, deployment independiente, equipos
- **CORS:** Manejado con middleware
- **Latencia:** Mitigada con Edge Functions
- **Trade-off:** Complejidad vale la pena en producción

---

**Conclusión:** Decisiones técnicas de alguien con 5+ años en full-stack: separación de concerns, manejo de formatos heterogéneos, UX inteligente con streaming, y arquitectura escalable.
