# 🏃 RunCoach AI - Guía Completa de Integración

## Dispositivos Compatibles

RunCoach AI soporta múltiples plataformas y dispositivos deportivos:

### ✅ Integración Directa (API)
- **Garmin Connect** - Sync automático OAuth
- **Strava** - Import desde Strava (próximamente)
- **Upload Manual** - FIT, GPX, TCX files

### 📱 Dispositivos Soportados via Upload

### ✅ Integración Directa (API)
- **Garmin Connect** - Sync automático OAuth
- **Strava** - Sync automático OAuth (RECOMENDADO para Xiaomi/Amazfit)
- **Upload Manual** - FIT, GPX, TCX files

### 📱 Dispositivos Soportados via Upload

#### Garmin (⌚ Sync Automático)
- Forerunner series
- Fenix series
- Vivoactive series
- Export automático via OAuth

#### Xiaomi / Amazfit / Zepp 🔥 SYNC VIA STRAVA (RECOMENDADO)
- Mi Band series (5, 6, 7, 8)
- Amazfit GTR (2, 3, 4), GTS (2, 3, 4)
- Amazfit Bip (U Pro, 3, 5)
- Amazfit Stratos, T-Rex

**🚀 OPCIÓN 1: Sync Automático via Strava (MEJOR)**

La forma MÁS FÁCIL de sincronizar Xiaomi/Amazfit sin subir archivos:

1. **Conecta Zepp con Strava** (una sola vez):
   - Zepp app → Perfil → Configuración
   - Conectar con aplicaciones de terceros → Strava
   - Autorizar conexión ✅
   - Todos tus workouts se sincronizan automáticamente a Strava

2. **Conecta RunCoach con Strava** (una sola vez):
   - RunCoach → Conectar dispositivos → Strava
   - Autorizar acceso ✅
   - Sincronización automática activada

3. **¡Listo!** Flujo completamente automático:
   ```
   Xiaomi Watch → Zepp App → Strava → RunCoach
   (automático)    (automático)  (automático)
   ```

**Métricas disponibles via Strava:**
- ✅ Distancia GPS precisa
- ✅ Ritmo y velocidad
- ✅ Frecuencia cardíaca (avg/max)
- ✅ Elevación y desnivel
- ✅ Cadencia
- ✅ Calorías
- ✅ Timestamps completos

**🔧 OPCIÓN 2: Upload Manual GPX (Alternativa)**

Si no quieres usar Strava, puedes subir archivos manualmente:

1. Abre Zepp app
2. Ve a Perfil → Ajustes → Exportar datos
3. Selecciona entrenamientos → Exportar como GPX
4. Sube archivos GPX en RunCoach
5. Sistema extrae todas las métricas disponibles

**Métricas extraídas de GPX:**
- ✅ Distancia (Haversine GPS)
- ✅ Ritmo y velocidad
- ✅ Frecuencia cardíaca (si disponible en extensiones)
- ✅ Elevación y desnivel
- ✅ Cadencia (si disponible)
- ✅ Timestamp GPS preciso

#### Polar
- Vantage, Grit, Pacer, Ignite series
- Export desde Polar Flow

**Cómo exportar:**
1. Polar Flow web → Diario
2. Click en entrenamiento → ⋮ → Exportar
3. Selecciona GPX o TCX
4. Sube a RunCoach

#### Wahoo
- ELEMNT, RIVAL series
- Export FIT files

**Cómo exportar:**
1. Wahoo app → Entrenamiento
2. Share → Exportar FIT
3. Sube a RunCoach

#### Suunto
- Suunto 9, 7, 5 series
- Export desde Suunto app

**Cómo exportar:**
1. Suunto app → Entrenamiento
2. Share → Exportar GPX/FIT
3. Sube a RunCoach

#### Coros
- PACE, APEX, VERTIX series
- Export FIT files

**Cómo exportar:**
1. Coros app → Entrenamiento
2. Export → FIT/GPX
3. Sube a RunCoach

---

## 📤 Formatos de Archivo Soportados

### FIT (Flexible and Interoperable Data Transfer)
**Mejor para:** Garmin, Wahoo, Coros, Polar
**Incluye:** Todas las métricas (FC, cadencia, potencia, form metrics)
**Tamaño:** Compacto (~50-200KB)

### GPX (GPS Exchange Format)
**Mejor para:** Xiaomi/Amazfit, Suunto, Polar
**Incluye:** Ruta GPS, FC, elevación, tiempo
**Tamaño:** Grande (~500KB-2MB)
**Compatible:** Universal, todos los dispositivos

### TCX (Training Center XML)
**Mejor para:** Garmin legacy
**Incluye:** Métricas básicas + GPS
**Tamaño:** Medio (~200KB-1MB)

---

## 🚀 Guía Rápida de Upload

### Paso 1: Exportar desde tu dispositivo
- Sigue las instrucciones específicas arriba

### Paso 2: Subir a RunCoach
1. Ve a **Dashboard → Subir Archivo**
2. Arrastra el archivo o click para seleccionar
3. Click **Subir Entrenamiento**

### Paso 3: ¡Listo!
- El entrenamiento aparecerá en tu lista
- Análisis AI disponible inmediatamente
- Métricas avanzadas procesadas

---

## 🔮 Próximamente

### Integraciones Planificadas
- [ ] **Strava** - Sync bidireccional
- [ ] **Apple Health** - Import workouts
- [ ] **Google Fit** - Android sync
- [ ] **TrainingPeaks** - Pro athletes
- [ ] **Final Surge** - Coaching platforms

### Features Avanzadas
- [ ] **Auto-import** via email (forward@runcoach.ai)
- [ ] **Webhook sync** para actualizaciones automáticas
- [ ] **Bulk upload** múltiples archivos
- [ ] **Cloud storage** integración (Dropbox, Drive)

---

## ❓ FAQ

### ¿Puedo importar entrenamientos antiguos?
Sí, puedes subir archivos de cualquier fecha. El sistema detectará automáticamente la fecha del entrenamiento.

### ¿Qué métricas se extraen?
Dependiendo del archivo:
- **Básico:** Distancia, tiempo, pace
- **Intermedio:** FC promedio/máx, calorías, elevación
- **Avanzado:** Cadencia, TCS, oscilación vertical, balance, potencia

### ¿Los archivos se guardan?
No guardamos los archivos originales, solo extraemos las métricas. Tus datos están seguros.

### ¿Límite de tamaño?
Máximo 10MB por archivo (suficiente para maratones completos con GPS).

### ¿Puedo editar entrenamientos después?
Próximamente tendremos edición manual de métricas.

---

## 🛠️ Troubleshooting

### Error: "Formato no soportado"
- Verifica que el archivo sea .fit, .gpx o .tcx
- Algunos dispositivos generan formatos propietarios - intenta exportar como GPX

### Error: "No se pudo parsear el archivo"
- El archivo puede estar corrupto
- Intenta exportar de nuevo desde la app original

---

## ⚙️ Características Técnicas

### Conversión Automática GPX → FIT

**¿Qué es?**
RunCoach detecta automáticamente archivos GPX (Xiaomi, Amazfit, Polar, etc.) y los convierte a formato FIT en memoria antes de procesarlos. Esto permite extraer métricas avanzadas que no están disponibles en el formato GPX estándar.

**¿Por qué FIT es mejor que GPX?**
- **FIT**: Formato binario de Garmin con soporte nativo para HR, cadencia, power, zonas
- **GPX**: Formato XML genérico solo con lat/lon/elevación básica
- **Conversión**: Crea estructura FIT compatible con parsers Garmin

**Proceso transparente:**
1. Usuario sube GPX desde Zepp/Polar/etc.
2. Backend detecta formato GPX
3. Convierte a FIT con métricas calculadas (Haversine distance, pace, speed)
4. Parsea FIT para extraer todos los datos
5. Crea workout con métricas FIT-quality
6. Usuario no nota diferencia - todo automático

**Métricas generadas:**
- Distancia GPS con algoritmo Haversine (precisión ±10m)
- Pace/Speed calculados de timestamps
- Frecuencia cardíaca desde GPX heart rate extensions
- Elevación y desnivel acumulado
- Session summary (total time, avg HR, max HR)
- Lap data si hay waypoints
- Contacta soporte si persiste

### Faltan métricas
- No todos los dispositivos registran todas las métricas
- FIT files suelen tener más datos que GPX
- Algunos relojes básicos solo registran GPS y tiempo

---

## 📧 Soporte

¿Problemas? Contacta: support@runcoach.ai
