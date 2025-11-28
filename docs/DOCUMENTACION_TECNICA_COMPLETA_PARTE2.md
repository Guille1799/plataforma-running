# 📘 DOCUMENTACIÓN TÉCNICA COMPLETA - PLATAFORMA RUNNING TIER 2
## PARTE 2: RACE PREDICTION & TRAINING RECOMMENDATIONS

**Continuación de documentación exhaustiva**  
**Fecha:** 17 de Noviembre, 2025

---

## ÍNDICE PARTE 2

1. [Service 3: Race Prediction Enhanced](#service-3-race-prediction-enhanced)
2. [Service 4: Training Recommendations](#service-4-training-recommendations)
3. [Integración con Groq/Llama AI](#integración-con-groqllama-ai)

---

## SERVICE 3: RACE PREDICTION ENHANCED

### Propósito General
Predecir tiempo de carrera con precisión utilizando 3 capas:
1. Modelo estadístico (algoritmos clásicos)
2. Factores ambientales (clima, altitud, terreno)
3. IA Generativa (Groq Llama 3.3 70B) para análisis contextual

### Capa 1: Modelo Estadístico Base

#### Predicción VDOT (VO2 Max Index)

```python
def calculate_vdot(user):
    """
    VDOT = VO2 Max Index
    Métrica estándar de running que correlaciona con performance
    
    Basada en mejor tiempo reciente en carrera
    """
    
    # Obtener carrera más rápida reciente (5K, 10K, Half, Full)
    best_recent_race = get_best_race_last_90_days(user)
    
    if best_recent_race is None:
        # Si no hay carreras, calcular del último VO2 max test
        return user.vo2_max or estimate_from_max_hr(user)
    
    # Fórmula de Jack Daniels VDOT
    if best_recent_race.distance == 5:  # 5K
        # VDOT = (-4.6 + 0.182258 × pace_seg + 0.000104 × pace_seg²) / 0.8
        pace_sec = best_recent_race.time_seconds
        vdot = (-4.6 + 0.182258 * pace_sec + 0.000104 * (pace_sec ** 2)) / 0.8
    
    elif best_recent_race.distance == 10:  # 10K
        pace_sec = best_recent_race.time_seconds
        vdot = (-4.6 + 0.182258 * pace_sec + 0.000104 * (pace_sec ** 2)) / 0.834
    
    elif best_recent_race.distance == 21.1:  # Half Marathon
        pace_sec = best_recent_race.time_seconds
        vdot = (-4.6 + 0.182258 * pace_sec + 0.000104 * (pace_sec ** 2)) / 0.923
    
    elif best_recent_race.distance == 42.2:  # Marathon
        pace_sec = best_recent_race.time_seconds
        vdot = (-4.6 + 0.182258 * pace_sec + 0.000104 * (pace_sec ** 2)) / 1.08
    
    return vdot  # Número entre 40-80
```

#### Predicción de Tiempo por Distancia

```python
def predict_race_time(user, target_distance_km):
    """
    Usa fórmula Riegel para predecir tiempo en diferente distancia
    
    FÓRMULA: T2 = T1 × (D2/D1) ^ 1.06
    Donde 1.06 es el exponente que refleja fatiga en distancias largas
    """
    
    # PASO 1: Obtener VDOT base
    base_vdot = calculate_vdot(user)  # e.g., 55
    
    # PASO 2: Convertir VDOT a tiempo para distancia estándar (10K)
    # Usando tabla de Jack Daniels
    base_10k_pace = vdot_to_pace_10k(base_vdot)  # e.g., 5:00 min/km
    base_10k_time = base_10k_pace * 10  # 50 minutos
    
    # PASO 3: Aplicar fórmula Riegel
    riegel_exponent = 1.06  # Factor de fatiga (mayor = fatiga acumulada)
    predicted_time = base_10k_time * ((target_distance_km / 10) ** riegel_exponent)
    
    # PASO 4: Aplicar factor de forma actual
    # Si el usuario ha estado entrenando poco, multiplicar por 1.1 (10% más lento)
    # Si ha estado en forma máxima, multiplicar por 0.95 (5% más rápido)
    fitness_factor = get_current_fitness_factor(user)  # 0.95 a 1.1
    predicted_time *= fitness_factor
    
    # PASO 5: Convertir a formato legible
    hours = int(predicted_time // 60)
    minutes = int(predicted_time % 60)
    seconds = int((predicted_time % 1) * 60)
    
    return {
        "distance_km": target_distance_km,
        "predicted_time_minutes": predicted_time,
        "formatted": f"{hours}:{minutes:02d}:{seconds:02d}",
        "pace_min_km": predicted_time / target_distance_km,
        "confidence": 0.75
    }
```

#### Ejemplo Práctico

```
Usuario: Juan García
- Mejor 10K reciente: 50 minutos (5:00 min/km)
- VO2 Max estimado: 55

PREDICCIÓN PARA CARRERA DE 21.1 KM (HALF MARATHON):
1. VDOT base = 55
2. Tiempo 10K base = 50 minutos
3. Fórmula Riegel: 50 × (21.1/10)^1.06 = 50 × 2.15 = 107.5 min
4. Factor forma actual = 0.98 (entrenando bien)
5. Tiempo predicho = 107.5 × 0.98 = 105.4 minutos
6. Resultado: 1:45:24 ± 2 minutos
```

---

### Capa 2: Factores Ambientales

#### Factor 1: Temperatura

```python
def calculate_temperature_impact(current_temp_c, optimal_temp_c=15):
    """
    Temperatura óptima para running: 10-15°C
    
    Impacto en performance (pérdida de velocidad):
    - < 0°C: 15% más lento (frío extremo)
    - 0-5°C: 8% más lento
    - 5-10°C: 3% más lento
    - 10-15°C: 0% (óptimo)
    - 15-20°C: 2% más lento (calor moderado)
    - 20-25°C: 5% más lento
    - 25-30°C: 10% más lento (calor fuerte)
    - > 30°C: 15-20% más lento
    """
    
    temp_diff = abs(current_temp_c - optimal_temp_c)
    
    if current_temp_c < 0:
        impact_percent = -15
    elif current_temp_c < 5:
        impact_percent = -8
    elif current_temp_c < 10:
        impact_percent = -3
    elif current_temp_c <= 15:
        impact_percent = 0  # Óptimo
    elif current_temp_c < 20:
        impact_percent = -2
    elif current_temp_c < 25:
        impact_percent = -5
    elif current_temp_c < 30:
        impact_percent = -10
    else:
        impact_percent = -15
    
    # Convertir a multiplicador
    time_multiplier = 1 + (impact_percent / 100)  # 1.0 = sin cambio
    
    return {
        "temperature": current_temp_c,
        "impact_percent": impact_percent,
        "time_multiplier": time_multiplier,
        "interpretation": f"Carrera será ~{abs(impact_percent)}% " + 
                         ("más rápida" if impact_percent > 0 else "más lenta")
    }
```

#### Factor 2: Humedad

```python
def calculate_humidity_impact(temp_c, humidity_percent):
    """
    La humedad COMBINADA con temperatura crea riesgo térmico
    
    Índice de calor = cómo se SIENTE la temperatura
    """
    
    # Fórmula de Heat Index
    if temp_c >= 26.7:  # Solo relevante con calor
        c1 = -42.379
        c2 = 2.04901523
        c3 = 10.14333127
        c4 = -0.22475541
        c5 = -0.00683783
        c6 = -0.05481717
        c7 = 0.00122874
        c8 = 0.00085282
        c9 = -0.00000199
        
        t = (temp_c * 9/5) + 32  # Convertir a Fahrenheit
        rh = humidity_percent
        
        heat_index_f = (c1 + c2*t + c3*rh + c4*t*rh + c5*t**2 + 
                       c6*rh**2 + c7*t**2*rh + c8*t*rh**2 + c9*t**2*rh**2)
        
        heat_index_c = (heat_index_f - 32) * 5/9
        
        if heat_index_c > 41:
            impact_percent = -20  # Extremamente lento
        elif heat_index_c > 38:
            impact_percent = -15
        elif heat_index_c > 35:
            impact_percent = -10
        else:
            impact_percent = -5
    else:
        # Con temperaturas moderadas, la humedad tiene poco impacto
        impact_percent = -1 if humidity_percent > 80 else 0
    
    return {
        "humidity": humidity_percent,
        "effective_temp": heat_index_c if temp_c >= 26.7 else temp_c,
        "impact_percent": impact_percent,
        "caution": "Alto riesgo de deshidratación" if heat_index_c > 38 else None
    }
```

#### Factor 3: Viento

```python
def calculate_wind_impact(wind_speed_kmh, direction_percent):
    """
    direction_percent = % del recorrido contra el viento
    
    Impacto del viento es MUY significativo
    Correr contra viento de 10 kmh = cuesta de 3-4%
    """
    
    # Viento a favor es beneficio, contra es costo
    effective_wind = wind_speed_kmh * ((direction_percent / 100) - 0.5) * 2
    
    # Fórmula empírica: 1 kmh viento = 1% pérdida de velocidad
    wind_impact_percent = effective_wind * 1
    
    time_multiplier = 1 + (wind_impact_percent / 100)
    
    return {
        "wind_speed": wind_speed_kmh,
        "wind_direction_against_percent": direction_percent,
        "effective_wind_impact": effective_wind,
        "time_multiplier": time_multiplier,
        "interpretation": f"Viento causará {wind_impact_percent:+.1f}% cambio en tiempo"
    }
```

#### Factor 4: Altitud

```python
def calculate_altitude_impact(elevation_m, acclimatization_days=0):
    """
    Altitud > 1500m causa hipoxia (menos oxígeno)
    
    Pérdida de VO2 Max:
    - 1500m: 2% pérdida
    - 2000m: 8% pérdida
    - 2500m: 15% pérdida
    - 3000m+: 25%+ pérdida
    """
    
    if elevation_m <= 1500:
        vo2_loss_percent = 0
        return {"altitude_m": elevation_m, "vo2_loss": vo2_loss_percent, "impact": "NONE"}
    
    # Fórmula exponencial para altitud
    vo2_loss_percent = 100 * (1 - math.exp(-0.00001 * (elevation_m - 1500)))
    
    # Acclimatization mejora las cosas
    # Cada 3 días de acclimatización recupera ~20% del VO2 perdido
    acclimatization_recovery = min(vo2_loss_percent * 0.2 * (acclimatization_days / 3), 
                                   vo2_loss_percent * 0.8)  # Max 80% recovery
    
    net_vo2_loss = vo2_loss_percent - acclimatization_recovery
    
    # VO2 loss = time loss (linealmente)
    time_multiplier = 1 + (net_vo2_loss / 100)
    
    return {
        "altitude_m": elevation_m,
        "vo2_loss_percent": vo2_loss_percent,
        "acclimatization_recovery": acclimatization_recovery,
        "net_time_multiplier": time_multiplier,
        "recommendation": f"Necesitas {int(acclimatization_days)} días más para " +
                         "aclimatarte completamente"
    }
```

#### Factor 5: Terreno

```python
def calculate_terrain_impact(terrain_type, elevation_gain_m, elevation_loss_m, distance_km):
    """
    Terreno cambio dramáticamente la dificultad
    """
    
    # Base: 0% (carretera plana)
    impact_percent = 0
    
    if terrain_type == "flat_road":
        impact_percent = 0
    
    elif terrain_type == "hilly_road":
        impact_percent = 2  # Muy poco pendiente
    
    elif terrain_type == "rolling_hills":
        impact_percent = 5
    
    elif terrain_type == "mountain":
        impact_percent = 8
    
    elif terrain_type == "trail":
        impact_percent = 12  # Trail es mucho más difícil
    
    elif terrain_type == "technical_trail":
        impact_percent = 15  # Rocas, raíces, requiere concentración
    
    # Factor adicional por ganancia de elevación
    # Regla empírica: 100m ganancia = cuesta de 1km
    elevation_km_equivalent = elevation_gain_m / 100
    additional_distance = distance_km + elevation_km_equivalent
    distance_multiplier = additional_distance / distance_km
    
    # Elevación de descenso: más fácil pero strés muscular
    # -30m descenso = -0.3km, pero causa muscle damage
    downhill_stress = elevation_loss_m / 100 * 0.5  # Mitad del beneficio del descent
    
    time_multiplier = 1 + (impact_percent / 100) * distance_multiplier * (1 + downhill_stress/100)
    
    return {
        "terrain": terrain_type,
        "elevation_gain": elevation_gain_m,
        "elevation_loss": elevation_loss_m,
        "base_impact_percent": impact_percent,
        "distance_multiplier": distance_multiplier,
        "final_time_multiplier": time_multiplier,
        "interpretation": f"Por terreno y elevación, carrera será " +
                         f"{(time_multiplier-1)*100:.1f}% más lenta"
    }
```

---

### Capa 3: Integración IA (Groq/Llama)

#### Solicitud a Groq para Contexto

```python
async def get_ai_prediction_context(user, race_params):
    """
    Usa IA para analizar contexto completo del atleta
    """
    
    prompt = f"""
    Analiza este atleta de running y proporciona insights sobre su carrera predicha:
    
    PERFIL DEL ATLETA:
    - Edad: {user.age}
    - Años de experiencia: {user.running_experience_years}
    - VO2 Max: {user.vo2_max}
    - Mejores tiempos recientes:
      * 5K: {user.best_5k_time}
      * 10K: {user.best_10k_time}
      * Half: {user.best_half_marathon_time}
    - Estatus actual: {user.current_fitness_status}
    - HRV promedio: {user.avg_hrv}
    - Estrés reportado: {user.stress_level}/10
    
    CARRERA PREDICHA:
    - Distancia: {race_params['distance']}km
    - Tiempo predicho: {race_params['predicted_time']}
    - Objetivo personal: {race_params['goal_time']}
    - Ubicación: {race_params['location']}
    - Temperatura esperada: {race_params['temperature']}°C
    - Elevación: {race_params['elevation_gain']}m ascenso
    - Terreno: {race_params['terrain']}
    - Dias para prepararse: {race_params['days_to_race']}
    
    PROPORCIONA:
    1. Análisis de viabilidad del objetivo
    2. Puntos fuertes y débiles del atleta para esta carrera
    3. Estrategia de carrera recomendada (ritmo, pacing)
    4. Riesgos potenciales (lesiones, deshidratación, etc.)
    5. Táctica de nutrición durante la carrera
    6. Recomendaciones para próximas 2 semanas de entrenamiento
    
    Sé específico y práctico.
    """
    
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        
        message = client.messages.create(
            model="mixtral-8x7b-32768",  # O "llama-3.3-70b-versatile"
            max_tokens=2048,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        analysis = message.content[0].text
        
        return {
            "ai_analysis": analysis,
            "model": message.model,
            "usage": {
                "input_tokens": message.usage.input_tokens,
                "output_tokens": message.usage.output_tokens
            }
        }
    
    except Exception as e:
        return {
            "error": str(e),
            "fallback": "No AI analysis available"
        }
```

#### Ejemplo de Respuesta IA

```
ANÁLISIS IA - Carrera de 21.1 km (Half Marathon)

Análisis de Viabilidad:
Tu objetivo de 1:42:00 es REALISTA pero AMBICIOSO
- Tiempo predicho: 1:45:24 (±2 min)
- Gap con objetivo: -3 minutos (1.8%)
- Recomendación: Posible si todo va perfecto

Tus Puntos Fuertes:
✅ Excelente VO2 Max (55) - top 20% de tu edad
✅ HRV estable (45ms) - buena recuperación
✅ Experiencia en media maratón (3 previas)
✅ Entrenamiento consistente últimas 8 semanas

Tus Puntos Débiles:
❌ Poco trabajo en umbrales lactato (Z4)
❌ Volumen semanal ligeramente bajo (40km vs 50km ideal)
❌ Estrés personal reportado (7/10) - afecta recovery

Estrategia de Carrera:
1. KM 0-5: Corre a 5:05 min/km (conservador, warm-up)
2. KM 5-16: 4:50 min/km (pace objetivo, 80% del esfuerzo)
3. KM 16-21: 4:45 min/km (push final si te sientes bien)

Riesgos:
⚠️ CALOR: 22°C con 65% humedad = +2% más lento
⚠️ VIENTO: Pronóstico muestra vientos de 15 kmh
⚠️ DESHIDRATACIÓN: Con temperatura, necesitas +500ml fluidos

Nutrición:
- Desayuna 2-3 horas antes (carbos + proteína)
- Toma 150-200 caloría cada 5 km (gels + agua)
- Electrolitos cada 10 km
- POST-carrera: proteína + carbos en 30 min

Plan Próximas 2 Semanas:
Semana 1 (11 días para carrera):
- Lun: 10km fácil
- Mié: 8km con 4 × 3min al Z4 (threshold)
- Viér: 12km progresivo (primeros 5 fácil, últimos 7 carrera)
- Dom: 15km muy fácil
- Total: 45km

Semana 2 (días finales):
- Lun: 8km muy fácil
- Mié: 6km con 6 × 1min al Z5 (velocidad) 
- Viér: 5km DESCANSO ACTIVO
- Dom: 21.1km CARRERA

Confidence: 82% (factores: forma buena, tiempo ajustado, riesgos manejables)
```

---

## SERVICE 4: TRAINING RECOMMENDATIONS

### Sistema de 5 Fases

```python
class TrainingPhase(Enum):
    PHASE_1_BASE = {
        "name": "Base Building",
        "weeks": 4,
        "focus": "Aerobic foundation, building weekly volume",
        "weekly_structure": [
            "Monday: REST",
            "Tuesday: Easy run 8-10km",
            "Wednesday: Easy run 8-10km + strength training",
            "Thursday: Tempo run 2km warmup + 6km at Z3 + 1km cooldown",
            "Friday: Easy run 6-8km",
            "Saturday: Long run - increase 1km per week (12,13,14,15km)",
            "Sunday: Rest or easy yoga"
        ],
        "intensity_distribution": {
            "Z1": "10%",    # Easy
            "Z2": "60%",    # Conversational
            "Z3": "20%",    # Tempo
            "Z4": "8%",     # Threshold
            "Z5": "2%"      # VO2 Max
        },
        "volume_increase": "10% per week",
        "goals": [
            "Build aerobic base (650+ weekly km)",
            "Establish consistent training habit",
            "Avoid injury through gradual progression",
            "Improve fat adaptation"
        ]
    }
    
    PHASE_2_BUILD = {
        "name": "Build & Strength",
        "weeks": 4,
        "focus": "Increase threshold capacity, specific aerobic power",
        "weekly_structure": [
            "Monday: Strength training (hills or weights)",
            "Tuesday: Easy run 10km + core",
            "Wednesday: Hard session - 8km easy + 4-6×3min Z4 + 3km easy",
            "Thursday: Easy run 8km",
            "Friday: Tempo run - 3km easy + 8km Z3 + 2km easy",
            "Saturday: Long run 16-18km (Z2)",
            "Sunday: Rest"
        ],
        "intensity_distribution": {
            "Z1": "5%",
            "Z2": "50%",
            "Z3": "25%",
            "Z4": "15%",
            "Z5": "5%"
        },
        "volume_increase": "5% per week (slower than phase 1)",
        "goals": [
            "Increase threshold pace (VDOT +3-5 points)",
            "Build muscular strength for injury prevention",
            "Improve VO2 Max",
            "Mental toughness through hard sessions"
        ]
    }
    
    PHASE_3_PEAK = {
        "name": "Peak Performance",
        "weeks": 3,
        "focus": "Race-specific fitness, speed work",
        "weekly_structure": [
            "Monday: Easy run 8km + mobility",
            "Tuesday: VO2 Max session - 10km easy + 6-8×3min Z5 + 5km easy",
            "Wednesday: Easy run 8km",
            "Thursday: Race-pace run - 10km easy + 5km at RACE PACE + 3km easy",
            "Friday: Easy recovery 6km",
            "Saturday: Long run at comfortable pace 18-20km",
            "Sunday: Rest"
        ],
        "intensity_distribution": {
            "Z1": "5%",
            "Z2": "45%",
            "Z3": "20%",
            "Z4": "15%",
            "Z5": "15%"
        },
        "volume_increase": "0% (maintain, no increase)",
        "goals": [
            "Peak VO2 Max and threshold capacity",
            "Train body for race distance",
            "Mental confidence through race-pace runs",
            "Perfect race strategy"
        ]
    }
    
    PHASE_4_TAPER = {
        "name": "Taper & Race Prep",
        "weeks": 2,
        "focus": "Recovery while maintaining fitness",
        "weekly_structure": [
            "Monday: Easy 6km",
            "Tuesday: 6km easy + 3×2min race pace (short, sharp)",
            "Wednesday: Easy 5km",
            "Thursday: 5km easy + 2×1min Z5 (very short)",
            "Friday: EASY 4km",
            "Saturday: VERY EASY 3km (loose-up)",
            "Sunday: RACE DAY!"
        ],
        "volume_increase": "-30% to -40% (sharp reduction)",
        "intensity_distribution": {
            "Z1": "10%",
            "Z2": "70%",
            "Z3": "10%",
            "Z4": "5%",
            "Z5": "5%"  # Only short strides
        },
        "goals": [
            "Fully recover from training stress",
            "Maintain fitness (don't decondition)",
            "Mental readiness for race",
            "Arrive fresh and ready to race"
        ]
    }
    
    PHASE_5_RECOVERY = {
        "name": "Post-Race Recovery",
        "weeks": 2-3,
        "focus": "Active recovery, rebuild base",
        "weekly_structure": [
            "Days 1-3: Walk only (20-30 min easy)",
            "Days 4-7: Very easy running 4-6km or cross-training",
            "Week 2: Easy running 6-8km, no intensity",
            "Week 3+: Return to base building"
        ],
        "volume": "70% of peak",
        "intensity_distribution": {
            "Z1": "5%",
            "Z2": "95%"  # Almost all easy
        },
        "goals": [
            "Physical and mental recovery",
            "Prevent post-race injury",
            "Rebuild aerobic base",
            "Reflect and plan next cycle"
        ]
    }
```

---

### Sistema de Adaptación Dinámico

```python
def calculate_adaptive_load_multiplier(user):
    """
    Ajusta el plan automáticamente basado en estado actual
    
    Factores:
    - HRV: ¿Cómo está la recuperación?
    - Sleep: ¿Descansó bien?
    - Fatigue rating: ¿Cómo se siente?
    - Recent volume: ¿Ha entrenado demasiado?
    - Stress level: ¿Estrés personal alto?
    """
    
    # FACTOR 1: HRV (Heart Rate Variability)
    # Normal HRV para este atleta: 45ms
    hrv_current = user.get_hrv_today()  # e.g., 35ms
    hrv_baseline = 45
    
    if hrv_current >= hrv_baseline * 1.15:
        hrv_multiplier = 1.2  # +20% intensidad, super recuperado
    elif hrv_current >= hrv_baseline:
        hrv_multiplier = 1.1  # +10%
    elif hrv_current >= hrv_baseline * 0.95:
        hrv_multiplier = 1.0  # 100% plan
    elif hrv_current >= hrv_baseline * 0.85:
        hrv_multiplier = 0.85  # -15% cansancio
    elif hrv_current >= hrv_baseline * 0.75:
        hrv_multiplier = 0.7  # -30% fatiga acumulada
    else:
        hrv_multiplier = 0.5  # -50% descansa
    
    # FACTOR 2: Dormir
    hours_slept = user.get_last_night_sleep()  # e.g., 5.5 horas
    
    if hours_slept >= 8.5:
        sleep_multiplier = 1.15  # +15% bien descansado
    elif hours_slept >= 8:
        sleep_multiplier = 1.0  # Óptimo
    elif hours_slept >= 7:
        sleep_multiplier = 0.9  # -10%
    elif hours_slept >= 6:
        sleep_multiplier = 0.75  # -25%
    else:
        sleep_multiplier = 0.5  # -50% sin dormir
    
    # FACTOR 3: Percepción de cansancio (escala 1-10)
    fatigue_rating = user.get_fatigue_rating()  # e.g., 7/10
    
    if fatigue_rating <= 3:
        fatigue_multiplier = 1.2  # Fresco
    elif fatigue_rating <= 5:
        fatigue_multiplier = 1.0
    elif fatigue_rating <= 7:
        fatigue_multiplier = 0.75
    else:
        fatigue_multiplier = 0.5  # Muy cansado
    
    # FACTOR 4: Volumen reciente
    # Si has corrido demasiado en últimas 2 semanas, necesitas descanso
    two_week_volume = sum(w.distance_km for w in get_workouts(user, days=14))
    target_two_week_volume = 80  # km objetivo cada 2 semanas
    
    if two_week_volume <= target_two_week_volume * 0.8:
        volume_multiplier = 1.1  # Bajo volumen, puedes hacer más
    elif two_week_volume <= target_two_week_volume:
        volume_multiplier = 1.0
    elif two_week_volume <= target_two_week_volume * 1.2:
        volume_multiplier = 0.85  # Un poco alto
    else:
        volume_multiplier = 0.7  # Demasiado volumen, reduce
    
    # FACTOR 5: Estrés personal
    stress_level = user.get_reported_stress()  # 1-10
    
    if stress_level <= 3:
        stress_multiplier = 1.0
    elif stress_level <= 6:
        stress_multiplier = 0.9  # -10% cuando hay estrés
    elif stress_level <= 8:
        stress_multiplier = 0.75  # -25%
    else:
        stress_multiplier = 0.6  # -40% estrés alto
    
    # CÁLCULO FINAL: Media geométrica
    final_multiplier = (
        hrv_multiplier ** 0.25 *
        sleep_multiplier ** 0.25 *
        fatigue_multiplier ** 0.25 *
        volume_multiplier ** 0.15 *
        stress_multiplier ** 0.1
    )
    
    return {
        "hrv_factor": hrv_multiplier,
        "sleep_factor": sleep_multiplier,
        "fatigue_factor": fatigue_multiplier,
        "volume_factor": volume_multiplier,
        "stress_factor": stress_multiplier,
        "final_multiplier": final_multiplier,
        "action": {
            "< 0.6": "🔴 DESCANSA - Tu cuerpo necesita recovery",
            "0.6-0.8": "🟠 REDUCE - Entrena fácil hoy",
            "0.8-1.0": "🟡 MODERADO - Sigue plan, no es día de push",
            "1.0-1.1": "🟢 NORMAL - Entrena como programado",
            "> 1.1": "🟢🟢 INTENSO - ¡Día ideal para hard workout!"
        }[categorize_multiplier(final_multiplier)]
    }
```

---

### Plan Semanal Dinámico

```python
async def generate_adaptive_weekly_plan(user, current_phase):
    """
    Crea el plan de la semana ajustándose a estado actual
    """
    
    plan = get_base_plan_for_phase(current_phase)  # Plan base
    
    for day, workout in enumerate(plan['workouts']):
        # Calcular multiplicador para ese día
        load_multiplier = calculate_adaptive_load_multiplier(user)
        
        # Aplicar multiplicador
        adjusted_workout = {
            "date": today() + timedelta(days=day),
            "type": workout['type'],
            "distance_km": workout['distance_km'] * load_multiplier,
            "intensity": adjust_intensity(workout['intensity'], load_multiplier),
            "duration": workout['duration_minutes'] * load_multiplier,
            "notes": generate_specific_notes(user, load_multiplier)
        }
        
        # Solicitar IA para contexto
        if load_multiplier < 0.7:
            ai_suggestion = await get_ai_recovery_advice(user)
            adjusted_workout['ai_advice'] = ai_suggestion
        
        plan['workouts'][day] = adjusted_workout
    
    return plan
```

---

**[CONTINÚA EN PARTE 3]**

*Documento de 3,000+ líneas. Parte 2 completada.*
*Contiene: Race Prediction (4 capas), Training Recommendations (5 fases), Adapatación Dinámica.*
