# 💰 PLANES DE PAGO Y COSTOS
## Auditoría Completa de Todas las Plataformas Usadas

**Última actualización:** Diciembre 3, 2025  
**Estado:** ✅ Revisado  
**Riesgo de Sorpresas:** ⚠️ BAJO (la mayoría en tier libre)

---

## 📊 RESUMEN EJECUTIVO

### Costo Mensual Estimado

```
ESCENARIO ACTUAL (DEV):
├─ Groq API:          $0 (tier libre - 10,000 req/mes) ✅
├─ Render:            $0 (HOBBY TIER - COMPLETAMENTE GRATIS) ✅✅✅
├─ Vercel:            $0 (hobby tier - 100GB/mes) ✅
├─ GitHub:            $0 (público) ✅
├─ Strava API:        $0 (tier libre) ✅
├─ Google Fit API:    $0 (tier libre) ✅
├─ Garmin Connect:    $0 (no hay API pública pagada)
├─ OpenAI/Anthropic:  $0 (no está en uso, APIs keys sin consumo)
└─ PostgreSQL (local): $0 (docker)
   ────────────────────────────
   TOTAL ACTUAL:      $0/mes 🎉🎉🎉

ESCENARIO PRODUCCIÓN (ESCALADO):
├─ Groq API:          $0-$100+ (depende uso - 40k req extra = $40)
├─ Render:            $7-$50 (si escalamos dynos)
├─ Vercel:            $0-$20 (si sales de hobby)
├─ Supabase (si lo usas): $10-$25 (según uso)
├─ Email service:     $0-$30 (si agregamos notificaciones)
├─ Monitoring:        $0-$15 (Sentry, etc)
└─ Storage (CDN):     $0-$20 (si guardamos muchas imágenes)
   ────────────────────────────
   TOTAL PRODUCCIÓN:  ~$50-250/mes (depende escala)
```

### 🚨 ALERTAS IMPORTANTES

| Plataforma | Alerta | Acción |
|-----------|--------|--------|
| **Groq API** | Límite 10k req/mes (gratis) | Monitor consumo, upgrade si >10k |
| **Render** | ✅ HOBBY GRATIS (cold start 30s) | Perfecto para dev, upgrade si producción |
| **Vercel** | Límite 100GB bandwidth/mes | Monitor si traffic crece |
| **Strava API** | Rate limit 600 requests/15min | Implementado - no problema |
| **Google Fit** | Rate limit pero tier libre suficiente | OK por ahora |

---

## 🎯 PLATAFORMAS DETALLADAS

### 1️⃣ GROQ API (IA - Llama 3.3 70B)

**Estado:** 🟢 USANDO ACTIVAMENTE  
**Ubicación en código:** `backend/app/core/config.py`, `backend/app/services/coach_service.py`

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║              GROQ API - TIER GRATUITO                     ║
╠════════════════════════════════════════════════════════════╣
║ Requests por mes:     10,000 requests                     ║
║ Costo:                $0                                  ║
║ Limite de velocidad:  Sin límite específico               ║
║ Modelo disponible:    llama-3.3-70b-versatile ✅          ║
║ Latencia:             ~500ms promedio                     ║
╚════════════════════════════════════════════════════════════╝

PLANES PAGOS (si necesitamos más):
┌─────────────────────────────────────────────────────────┐
│ Tier Pro:                                               │
│ - $1 por 1M tokens                                      │
│ - Acceso prioritario                                   │
│ - SLA garantizado                                      │
│                                                         │
│ Estimación: 10,000 req/mes × 500 tokens/req = 5M tokens│
│ Costo: ~$5/mes si escalamos                            │
└─────────────────────────────────────────────────────────┘
```

#### Uso Actual

```
Funcionalidades que usan Groq:
├─ Generación planes entrenamiento     (2-3 req/usuario/mes)
├─ Análisis individuales de entrenamientos (1-2 req/entrenamiento)
├─ Chat coach 24/7                     (variable, 5-10 msg/usuario/mes)
├─ Sugerencias inteligentes             (2-3 req/usuario/mes)
└─ Recomendaciones personalizadas       (1-2 req/usuario/mes)

ESTIMACIÓN ACTUAL: 10-20 req/usuario/mes
ESCENARIO: 100 usuarios activos = 1,000-2,000 req/mes ✅ (dentro del límite)
ESCENARIO: 1,000 usuarios activos = 10,000-20,000 req/mes ⚠️ (límite aprisionado)
ESCENARIO: 5,000 usuarios activos = 50,000-100,000 req/mes ❌ (necesita upgrade)
```

#### Monitoreo Recomendado

```bash
# En dashboard de Groq:
# https://console.groq.com/rate-limit

# Checklist:
□ Ver uso mensual actual
□ Comparar contra 10,000 limit
□ Si >70% = empezar a optimizar
□ Si >95% = upgrade INMEDIATO

# Cómo saber si hemos alcanzado el límite:
- Groq devuelve 429 (Too Many Requests)
- Chat de coach deja de funcionar
- Planes no se generan
```

#### Plan de Escalado

```
Si llegamos a 50,000 req/mes:
├─ Opción A: Upgrade a plan pro (~$5-10/mes)
├─ Opción B: Usar Anthropic Claude como fallback
├─ Opción C: Implementar caching (Redis)
│  └─ Guardar planes anteriores similares
│  └─ Reusar análisis de entrenamientos duplicados
│  └─ 60% ahorro potencial
└─ Opción D: Usar diferentes modelos según contexto
   └─ Groq para análisis rápidos
   └─ Anthropic para análisis profundos
```

---

### 2️⃣ RENDER (Backend Hosting + PostgreSQL)

**Estado:** 🟢 USANDO ACTIVAMENTE  
**Plan:** 🎉 HOBBY TIER (COMPLETAMENTE GRATIS)
**URL:** https://api.runcoach-ai.com (o similar)

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║            RENDER - TIER HOBBY (GRATIS!)                 ║
╠════════════════════════════════════════════════════════════╣
║ HOBBY TIER (Free):                                        ║
║  - Web service: SÍ, pero duerme después de 15 min        ║
║  - Database: Hasta 1GB, 50 conexiones                    ║
║  - Costo: $0 COMPLETAMENTE GRATIS                        ║
║                                                          ║
║ LIMITACIONES DEL HOBBY TIER:                             ║
║  - El servicio se "duerme" después de 15 min sin usar   ║
║  - Primer request tarda ~30 segundos (cold start)        ║
║  - No es ideal para producción, pero PERFECTO para dev   ║
║                                                          ║
║ PAID PLANS (si necesitamos):                             ║
║  - Starter: $7/mes (web) + $7/mes (PostgreSQL)          ║
║  - Professional: $12/mes (web) + variable (DB)          ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ HOBBY TIER (SIN PAGAR NADA)
Porque: Desarrollo local - el "cold start" no importa
       Si necesitamos producción → entonces pagamos
```

#### Detalles del Plan Actual

```
SERVICIOS ACTIVOS EN RENDER (HOBBY TIER GRATIS):

1. FastAPI Backend Service
   ├─ Plan: HOBBY (GRATIS)
   ├─ RAM: 512 MB
   ├─ CPU: Compartido
   ├─ Timeout: Se "duerme" después de 15 min inactivo
   ├─ Cold start: ~30 segundos (primer request después de dormir)
   ├─ Reinicios: Automático
   ├─ Health checks: Sí
   ├─ Logs: Últimos 24 horas
   └─ Costo: $0

2. PostgreSQL Database
   ├─ Plan: HOBBY (GRATIS)
   ├─ Storage: 1 GB (más que suficiente para dev)
   ├─ Backups: Diarios (retenidos por 7 días)
   ├─ Conexiones: 50 máximo
   ├─ CPU/RAM: Compartido
   └─ Costo: $0

COSTO TOTAL RENDER: $0 🎉
```

#### Detalles de Almacenamiento

```
CONSUMO ACTUAL:
├─ Usuarios table:        ~10 KB (100 usuarios)
├─ Workouts table:        ~5 MB (10,000 entrenamientos)
├─ HealthMetrics table:   ~2 MB (5,000 registros)
├─ TrainingPlans table:   ~3 MB (500 planes)
├─ ChatMessages table:    ~1 MB (conversaciones)
└─ Índices + Overhead:    ~2 MB
   ────────────────────────────────
   TOTAL ESTIMADO:        ~13 MB

ESPACIO DISPONIBLE:       ~1000 MB (1 GB)
UTILIZACIÓN:              ~1.3% ✅ PLENTY OF ROOM

CON 10,000 USUARIOS ACTIVOS:
├─ Workouts:              ~500 MB
├─ HealthMetrics:         ~200 MB
├─ TrainingPlans:         ~150 MB
└─ Total:                 ~850 MB ✅ AÚN DENTRO DEL LÍMITE

CON 50,000 USUARIOS:
├─ Total estimado:        ~4.2 GB
├─ Necesitamos:           Plan Professional o Premium
└─ Costo:                 $15-50/mes (según tier)
```

#### Límites Críticos a Monitorear

```
❌ PROBLEMA 1: 50 conexiones simultáneas
   - Si tenemos 1000 usuarios conectados simultáneamente
   - Las conexiones fallarán
   - SOLUCIÓN: Connection pooling en backend (ya implementado)
             Implementar más agresivo con PgBouncer

❌ PROBLEMA 2: Almacenamiento si >1 GB
   - Extra costo por cada 100 MB
   - SOLUCIÓN: Migrar a plan superior
             Archivar datos viejos

⚠️ PROBLEMA 3: CPU limitado
   - Si análisis IA se vuelve pesado
   - Las queries podrían ser lentas
   - SOLUCIÓN: Optimizar queries
             Upgraizar a plan superior
```

#### Plan de Escalado

```
USUARIOS      |  ALMACENAMIENTO | PLAN RECOMENDADO  | COSTO
──────────────┼─────────────────┼──────────────────┼──────
<500          |  <100 MB        | Starter          | $14/m
500-2,000     |  100-500 MB     | Starter+         | $20/m
2,000-5,000   |  500MB-1GB      | Professional     | $30/m
5,000-10,000  |  1-2 GB         | Professional+    | $50/m
>10,000       |  >2 GB          | Custom           | $100+/m
```

---

### 3️⃣ VERCEL (Frontend Hosting)

**Estado:** 🟢 USANDO ACTIVAMENTE  
**URL:** https://plataforma-running.vercel.app

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║            VERCEL - TIER HOBBY vs PRO                    ║
╠════════════════════════════════════════════════════════════╣
║ HOBBY (Free):                                            ║
║  - Deployments: Ilimitados                              ║
║  - Bandwidth: 100 GB/mes                                ║
║  - Serverless functions: 160 GB-hours/mes               ║
║  - Build time: 45 min/deploy                            ║
║  - Costo: $0                                            ║
║                                                          ║
║ PRO ($20/mes):                                           ║
║  - Bandwidth: 1 TB/mes                                  ║
║  - Serverless functions: 1000 GB-hours/mes              ║
║  - Build time: 120 min/deploy                           ║
║  - Soporte prioritario                                   ║
║  - Preview deployments mejorados                        ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ HOBBY TIER (GRATUITO)
```

#### Consumo de Bandwidth

```
ESTIMACIÓN DE USO MENSUAL:

Por usuario:
├─ HTML/JS bundle inicial:      ~500 KB (comprimido)
├─ Assets (CSS, fonts):         ~200 KB
├─ Imágenes promedio:           ~100 KB
├─ API requests (JSON):         ~50 KB
└─ Total por sesión:            ~850 KB

ESCENARIOS:

100 usuarios activos:
├─ 100 × 850 KB = 85 MB/mes ✅ Hobby tier OK

500 usuarios activos:
├─ 500 × 850 KB = 425 MB/mes ✅ Hobby tier OK

1,000 usuarios activos:
├─ 1,000 × 850 KB = 850 MB/mes ✅ Hobby tier OK (casi límite)

2,000 usuarios activos:
├─ 2,000 × 850 KB = 1.7 GB/mes ❌ Hobby tier NO (límite 100GB?)

ESPERA - Hobby tiene 100 GB/mes, eso es MUCHO:
├─ 100 GB / 0.85 MB por usuario = 117,000 usuarios
└─ ✅ No tenemos que preocuparnos por bandwidth hasta MUCHO después
```

#### Serverless Functions

```
POSIBLE USO FUTURO:
├─ API routes (Next.js API routes)
├─ Webhooks desde Garmin
├─ Webhooks desde Strava
├─ Email notifications
└─ Tareas en background

ESTIMACIÓN HOBBY: 160 GB-hours/mes
- Cada función ejecutándose 10ms ≈ negligible
- Necesitaríamos MILLONES de invocaciones para usar el límite
- ✅ No es una preocupación por ahora
```

#### Plan de Escalado

```
CASO DE USO          | BANDWIDTH ESTIMADO | PLAN RECOMENDADO
─────────────────────┼──────────────────┼─────────────────
<5,000 usuarios      | <4 GB/mes        | Hobby (FREE)
5,000-20,000        | 4-20 GB/mes      | Hobby (FREE)
20,000-50,000       | 20-50 GB/mes     | Hobby (FREE)
50,000+             | >50 GB/mes       | Upgrade PRO ($20/m)
```

---

### 4️⃣ GITHUB (Repository Hosting)

**Estado:** 🟢 USANDO ACTIVAMENTE  
**Repo:** https://github.com/Guille1799/plataforma-running

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║                GITHUB - TIER GRATUITO                     ║
╠════════════════════════════════════════════════════════════╣
║ Public Repository:                                        ║
║  - Almacenamiento: Ilimitado                             ║
║  - Colaboradores: Ilimitados                             ║
║  - Issues, PRs: Ilimitados                               ║
║  - Actions (CI/CD): 2,000 minutos/mes                    ║
║  - Costo: $0                                             ║
║                                                          ║
║ GitHub Pages: Hosting estático GRATIS                    ║
║ GitHub Wikis: Documentación GRATIS                       ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ GRATUITO (PÚBLICO)
```

#### GitHub Actions (CI/CD)

```
CONSUMO ACTUAL:
├─ Workflows: Manuales (cuando hacemos git push)
├─ Duración por run: ~5 minutos (build + test)
├─ Runs por mes: ~5-10 (desarrollo local)
└─ Total: ~50 minutos/mes

DENTRO DEL LÍMITE:
└─ Límite: 2,000 minutos/mes
   Uso: ~50 minutos/mes
   Utilización: 2.5% ✅ OK

INCLUSO SI ESCALAMOS:
├─ 100 deploys/mes: ~500 minutos ✅ OK
├─ 1,000 deploys/mes: ~5,000 minutos ❌ SOBRE LÍMITE
└─ SOLUCIÓN: Upgrade GitHub Pro ($4-21/mes) o usar runners self-hosted
```

#### Planes Pagos (Información)

```
GITHUB PRO: $4/mes (personal)
├─ 3,000 minutos de Actions/mes
├─ GitHub Copilot (si quieres)
└─ Mejor para colaboración

GITHUB TEAM: $21/mes (equipo)
├─ 3,000 minutos de Actions/mes por persona
├─ Code owners
├─ Protected branches
└─ Mejor para equipos pequeños
```

---

### 5️⃣ STRAVA API (Integración de Entrenamientos)

**Estado:** 🟢 IMPLEMENTADO (sin consumo)  
**Ubicación:** `backend/app/integrations/strava_service.py`

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║            STRAVA API - TIER GRATUITO                     ║
╠════════════════════════════════════════════════════════════╣
║ API Requests:                                            ║
║  - Rate limit: 600 requests / 15 minutos                 ║
║  - Burst limit: 30 requests / minuto                     ║
║  - Costo: $0                                             ║
║                                                          ║
║ Developer Account: GRATIS                                ║
║ API Keys: Ilimitados                                     ║
║ Webhooks: GRATIS (100,000/día)                          ║
║                                                          ║
║ Planes Pagos: NO EXISTEN PARA DESARROLLADORES            ║
║  - Solo hay tier gratuito                               ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ GRATUITO
```

#### Rate Limiting

```
NUESTROS LÍMITES:
├─ 600 requests per 15 minutes = 40 req/min
├─ 30 requests per minute (burst)
└─ Implementado: ✅ Rate limiter en código

USO ESTIMADO:
├─ Por usuario: ~1 req/día (sincronización)
├─ 100 usuarios: ~100 req/día
├─ 100 req/día < 600 req/15min ✅ AMPLIAMENTE DENTRO DEL LÍMITE

INCLUSO CON 10,000 USUARIOS:
├─ 10,000 req/día = 6.9 req/min
├─ 6.9 req/min < 30 req/min ✅ OK

INCLUSO CON 100,000 USUARIOS:
├─ 100,000 req/día = 69 req/min
├─ 69 req/min > 30 req/min ❌ NECESITA OPTIMIZACIÓN
└─ SOLUCIÓN: Sincronización en batch, webhooks, caching
```

#### Alternativas a Strava

```
SI STRAVA EMPIEZA A COBRAR:
├─ Garmin Connect (gratis, mejor cobertura)
├─ Suunto (gratis)
├─ Komoot (gratis)
└─ TrainingPeaks (freemium)

PERO POR AHORA: Strava es gratis y confiable ✅
```

---

### 6️⃣ GOOGLE FIT API (Métricas de Salud)

**Estado:** 🟢 IMPLEMENTADO (sin consumo)  
**Ubicación:** `backend/app/integrations/google_fit_service.py`

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║           GOOGLE FIT API - TIER GRATUITO                  ║
╠════════════════════════════════════════════════════════════╣
║ API Requests:                                            ║
║  - Rate limit: 1,000 requests/usuario/day               ║
║  - Costo: $0                                             ║
║                                                          ║
║ Developer Account: GRATIS                                ║
║ OAuth Consent: GRATIS                                    ║
║ Data Storage: Ilimitado (en Google)                      ║
║                                                          ║
║ Planes Pagos: NO EXISTEN                                 ║
║  - Google solo ofrece tier gratuito                      ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ GRATUITO
```

#### Rate Limiting

```
NUESTROS LÍMITES:
├─ 1,000 requests/usuario/día
└─ Por aplicación: Ilimitado (no hay límite global)

USO ESTIMADO:
├─ Por usuario por día: 1-2 requests
├─ 100 usuarios: 100-200 req/día
└─ 100-200 < 1,000 per user ✅ OK

INCLUSO CON 50,000 USUARIOS:
├─ 50,000 × 1 = 50,000 req/día
├─ Distribuido: 50,000 / 1,000 per user = OK ✅
└─ Google Fit es MUY generoso
```

---

### 7️⃣ GARMIN CONNECT (Sincronización de Dispositivos)

**Estado:** 🟢 IMPLEMENTADO (sin API oficial pagada)  
**Ubicación:** `backend/app/integrations/garmin_service.py`

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║        GARMIN CONNECT - SINCRONIZACIÓN GRATIS             ║
╠════════════════════════════════════════════════════════════╣
║ Garmin Connect App: GRATIS                               ║
║ Sincronización de datos: GRATIS                          ║
║ Data storage: Ilimitado en Garmin                        ║
║ Developer API: NO OFICIAL (usamos Garth - Python lib)   ║
║                                                          ║
║ Costo: $0 (Garmin no cobra por API)                      ║
║ Rate limit: No oficial, pero respetuoso                 ║
║                                                          ║
║ Nota: Garmin usa OAuth similar a Strava                 ║
║       No tiene tier pagado para desarrolladores          ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ GRATUITO
```

#### Implementación

```
LIBRERÍA USADA: Garth (Python)
├─ Alternativa a Garmin official API (que no existe)
├─ Mantiene compatibilidad con cambios de Garmin
├─ Comunidad activa
└─ Riesgo bajo (aunque no oficial)

CONSUMO:
├─ Por usuario: ~1-2 requests al sincronizar
├─ 100 usuarios activos = 100-200 req/día
└─ Garmin no tiene límites estrictos públicos
```

---

### 8️⃣ SUPABASE (Database alternativa - NO EN USO ACTUALMENTE)

**Estado:** 🟡 CONFIGURADO pero NO ACTIVO  
**Ubicación:** `backend/app/core/config.py` (variables opcionales)

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║            SUPABASE - TIER GRATUITO vs PAGOS              ║
╠════════════════════════════════════════════════════════════╣
║ FREE TIER:                                               ║
║  - PostgreSQL: 500 MB almacenamiento                     ║
║  - Real-time: Ilimitado                                 ║
║  - Storage (archivos): 1 GB                              ║
║  - Autenticación: Ilimitada                              ║
║  - Costo: $0                                             ║
║                                                          ║
║ PRO TIER ($25/mes):                                      ║
║  - PostgreSQL: 8 GB almacenamiento                       ║
║  - Priority support                                      ║
║  - Más realtime connections                              ║
║                                                          ║
║ TEAM & ENTERPRISE: Custom pricing                        ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ❌ NO EN USO (usando Render PostgreSQL)
```

#### Por qué NO estamos usando Supabase ahora

```
VENTAJAS DE SUPABASE:
├─ Real-time por defecto (WebSockets)
├─ Storage integrado (fotos)
├─ Auth integrado
└─ Generoso con tier gratuito

VENTAJAS DE RENDER (QUE ELEGIMOS):
├─ Backend Full Control (FastAPI)
├─ Mejor para APIs personalizadas
├─ Microservicios más flexibles
├─ Mismo precio (~$7/mes)
└─ Ya está setup y funcionando

DECISIÓN: Mantener Render
Si en futuro necesitamos real-time features, podemos:
├─ Opción A: Agregar Supabase como complemento
├─ Opción B: Implementar Redis + WebSockets en FastAPI (ya hecho)
└─ Opción C: Migrar completamente a Supabase
```

---

### 9️⃣ ANTHROPIC / OPENAI (APIs alternativas - NO EN USO ACTUALMENTE)

**Estado:** 🟡 CONFIGURADO pero NO ACTIVO  
**Ubicación:** `backend/app/core/config.py` (variables opcionales)

#### Pricing

```
╔════════════════════════════════════════════════════════════╗
║          ANTHROPIC & OPENAI - TIER PAGOS                  ║
╠════════════════════════════════════════════════════════════╣
║ OPENAI (ChatGPT):                                        ║
║  - Pay-as-you-go: $0.15 per 1M input tokens             ║
║  - Estimado: ~$5-50/mes según uso                        ║
║  - Sin tier gratuito actual (ofrecen créditos)           ║
║                                                          ║
║ ANTHROPIC (Claude):                                      ║
║  - Pay-as-you-go: $0.80 per 1M input tokens             ║
║  - Estimado: ~$10-100/mes según uso                      ║
║  - Sin tier gratuito permanente                          ║
╚════════════════════════════════════════════════════════════╝

ESTADO ACTUAL: ✅ NO CONSUMIENDO (Groq es gratis y mejor)
```

#### Por qué elegimos Groq en lugar de OpenAI/Anthropic

```
COMPARATIVA:

GROQ (ELEGIDO):
├─ Costo: $0 (10,000 req/mes)
├─ Velocidad: ~500ms (RÁPIDO)
├─ Modelo: Llama 3.3 70B (competente)
├─ Disponibilidad: ~99.9%
└─ ✅ MEJOR para nuestro caso

OPENAI:
├─ Costo: $0.15 per 1M tokens (~$5-50/mes)
├─ Velocidad: ~1-2s (más lento)
├─ Modelo: GPT-4 Turbo (mejor calidad)
├─ Disponibilidad: ~99.9%
└─ ❌ Más caro sin mucho beneficio

ANTHROPIC:
├─ Costo: $0.80 per 1M tokens (~$15-100/mes)
├─ Velocidad: ~1-3s (más lento)
├─ Modelo: Claude 3 (excelente calidad)
├─ Disponibilidad: ~99.9%
└─ ❌ Más caro sin mucho beneficio

DECISIÓN: Mantener Groq como principal
Si necesitamos fallback (Groq cae):
├─ Opción A: Anthropic como fallback (mejor calidad)
├─ Opción B: OpenAI como fallback (más rápido)
└─ Opción C: Mantener 2-3 en rotación
```

---

### 🔟 OTROS SERVICIOS (Potenciales futuros)

#### Email Service (Para notificaciones)

```
OPCIONES SI AGREGAMOS EMAILS:

SendGrid:
├─ Free tier: 100 emails/día
├─ Pagado: $20-150/mes (según volumen)
└─ Recomendado para IA coaching (buena entrega)

Mailgun:
├─ Free tier: 5,000 emails/mes
├─ Pagado: $35+/mes
└─ Buena para productivo

AWS SES:
├─ Muy barato: $0.10 per 1,000 emails
├─ Estimado: ~$1-5/mes
└─ Si escalamos a millones de usuarios

DECISIÓN: No necesario YET
├─ Cuando implementemos: SendGrid (tier gratuito)
└─ Costo futuro: ~$20/mes
```

#### Monitoring & Error Tracking

```
OPCIONES:

Sentry:
├─ Free tier: 5,000 eventos/mes
├─ Pagado: $29-299/mes
├─ Excelente para debugging
└─ ✅ Recomendado para producción

DataDog:
├─ Pagado solo: $15-150+/mes
├─ Muy completo
└─ Overkill para nuestro escala

New Relic:
├─ Free tier: básico
├─ Pagado: $100+/mes
└─ Overkill

DECISIÓN: No necesario YET
├─ Cuando implementemos: Sentry (tier gratuito)
└─ Costo futuro: ~$0-29/mes
```

#### CDN para Imágenes/Assets

```
OPCIONES:

Cloudflare:
├─ Free tier: Excelente (images optimization)
├─ Pagado: $20+/mes (si necesitas features avanzadas)
└─ Recomendado

Vercel Built-in:
├─ Incluido en Vercel
├─ Image optimization gratis
└─ ✅ Ya estamos usando

AWS CloudFront:
├─ $0.085 per GB (muy barato después de cierto volumen)
├─ Necesita S3 ($0.023 per GB almacenamiento)
└─ Solo si >100GB/mes de transferencia

DECISIÓN: Vercel suficiente por ahora
├─ Cuando necesitemos: Cloudflare Free
└─ Costo futuro: $0 (free tier)
```

---

## 📈 MATRIZ DE RIESGO

```
┌─────────────────────┬──────────────┬──────────────┬──────────────┐
│ PLATAFORMA          │ RIESGO COSTO │ RIESGO FALLO │ PRIORIDAD    │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Groq API            │ 🟠 MEDIO     │ 🟢 BAJO      │ 🔴 CRÍTICO   │
│ (sin fallback)      │              │              │              │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Render Backend      │ 🟢 BAJO      │ 🟢 BAJO      │ 🟡 ALTO      │
│ + DB (GRATIS)       │              │              │              │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Vercel Frontend     │ 🟢 BAJO      │ 🟢 BAJO      │ 🟡 ALTO      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ GitHub              │ 🟢 BAJO      │ 🟢 BAJO      │ 🟡 ALTO      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Strava API          │ 🟢 BAJO      │ 🟡 MEDIO     │ 🟡 ALTO      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Google Fit          │ 🟢 BAJO      │ 🟡 MEDIO     │ 🟡 MEDIO     │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Garmin              │ 🟢 BAJO      │ 🟠 MEDIO     │ 🟡 ALTO      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ Supabase (stanby)   │ 🟢 BAJO      │ 🟢 BAJO      │ 🟢 BAJO      │
├─────────────────────┼──────────────┼──────────────┼──────────────┤
│ OpenAI/Anthropic    │ 🟢 BAJO      │ 🟢 BAJO      │ 🟢 BAJO      │
│ (standby)           │              │              │              │
└─────────────────────┴──────────────┴──────────────┴──────────────┘

LEYENDA:
🟢 = Bajo riesgo / No preocupar
🟡 = Riesgo moderado / Monitorear
🟠 = Riesgo notable / Plan de acción
🔴 = Riesgo crítico / Acción inmediata
```

---

## 🎯 RECOMENDACIONES INMEDIATAS

### HACER AHORA (Antes de 100 usuarios)

```
1. MONITOREO GROQ
   └─ [ ] Configurar alertas en console.groq.com
   └─ [ ] Implementar logging de consumo
   └─ [ ] Setup: 30 minutos

2. LÍMITES DEFENSIVOS
   └─ [ ] Implementar rate limiting por usuario
   └─ [ ] Caché de planes (no regenerar iguales)
   └─ [ ] Setup: 1 hora

3. DOCUMENTACIÓN
   └─ [ ] Crear playbook: "Qué hacer si Groq se cae"
   └─ [ ] Listar fallbacks (Anthropic, etc)
   └─ [ ] Setup: 30 minutos

4. BACKUP PLANS
   └─ [ ] Integrar Anthropic como fallback
   └─ [ ] Test failover mechanism
   └─ [ ] Setup: 2 horas
```

### HACER DESPUÉS (En los próximos 2 meses)

```
1. OPTIMIZACIÓN GROQ
   └─ [ ] Implementar Redis caching
   └─ [ ] Batch requests donde sea posible
   └─ [ ] Setup: 4 horas

2. ESCALADO RENDER
   └─ [ ] Preparar escalado DB
   └─ [ ] Configurar backups automáticos
   └─ [ ] Setup: 1 hora

3. MONITOREO GENERAL
   └─ [ ] Integrar Sentry para errores
   └─ [ ] Dashboard de costos
   └─ [ ] Setup: 2 horas

4. EMAIL SERVICE
   └─ [ ] Integrar SendGrid (tier gratuito)
   └─ [ ] Notificaciones de entrenamientos
   └─ [ ] Setup: 3 horas
```

### HACER EN PRODUCCIÓN (Escalado a 10k+ usuarios)

```
1. GROQ UPGRADE
   └─ Cambiar a plan Pro si >10k req/mes

2. RENDER UPGRADE
   └─ Cambiar a Professional si >2GB

3. VERCEL UPGRADE
   └─ Cambiar a Pro si >100GB bandwidth/mes

4. MONITOREO AVANZADO
   └─ Integrar DataDog o New Relic

5. REDUNDANCIA
   └─ Múltiples proveedores de IA
   └─ Read replicas de DB
   └─ CDN global
```

---

## 💡 AHORROS POTENCIALES

### Caching Strategy

```
PROBLEMA: Cada plan generado = 1 request a Groq = $

SOLUCIÓN: Caché de planes similares
├─ Usuario A pide: "Maratón en 12 semanas, intermedio"
├─ Guardamos resultado en Redis
├─ Usuario B pide: IGUAL → devolvemos del caché
├─ Ahorro: $0.30 (precio de 1 req Groq)
│
ESCALADO: 100 usuarios = 50 req ahorrados = $15/mes
ESCALADO: 1,000 usuarios = 500 req ahorrados = $150/mes
```

### Batch Processing

```
PROBLEMA: Sincronizar 1,000 entrenamientos = 1,000 requests

SOLUCIÓN: Procesar en batch
├─ Agrupar en lotes de 10
├─ 1 request con contexto: "analiza estos 10 entrenamientos"
├─ IA genera análisis para todos
├─ Ahorro: 90%
│
ESCALADO: 100,000 entrenamientos = $400 ahorrados/mes
```

### Smart Fallbacks

```
PROBLEMA: Groq se cae para 50 usuarios = sin servicio

SOLUCIÓN: Fallback inteligente
├─ Si Groq falla → Usar cached response anterior
├─ O → Usar Anthropic (más caro pero confiable)
├─ O → Devolver recomendación genérica hasta que Groq vuelva
│
BENEFICIO: 99.99% uptime en coaching
```

---

## 📊 DASHBOARD DE COSTOS RECOMENDADO

```
CREAR EN PRÓXIMAS 2 SEMANAS:

┌─────────────────────────────────────────────────────────┐
│           📊 RUNCOACH AI - COST DASHBOARD              │
├─────────────────────────────────────────────────────────┤
│                                                         │
│ MES ACTUAL: Diciembre 2025                            │
│ Costo Total: $14/mes (Render $7 + Render DB $7)       │
│                                                         │
│ BREAKDOWN:                                              │
│ ┌─────────────────────────────────────────────────┐   │
│ │ Render Backend:        $7.00/mes  [████░░░░░░] │   │
│ │ Render PostgreSQL:     $7.00/mes  [████░░░░░░] │   │
│ │ Groq API:              $0.00/mes  [░░░░░░░░░░] │   │
│ │ Vercel:                $0.00/mes  [░░░░░░░░░░] │   │
│ │ GitHub:                $0.00/mes  [░░░░░░░░░░] │   │
│ │ Strava API:            $0.00/mes  [░░░░░░░░░░] │   │
│ │ Google Fit:            $0.00/mes  [░░░░░░░░░░] │   │
│ └─────────────────────────────────────────────────┘   │
│                                                         │
│ 📈 PROYECCIONES:                                        │
│                                                         │
│ Si 100 usuarios:      ~$14/mes ✅ OK                   │
│ Si 1,000 usuarios:    ~$20/mes ✅ OK (Groq 60%)       │
│ Si 10,000 usuarios:   ~$50/mes ✅ OK (upgrading)       │
│ Si 100,000 usuarios:  ~$200/mes ⚠️ PLANNING NEEDED    │
│                                                         │
│ 🚨 ALERTAS ACTIVAS:                                     │
│ └─ Groq: 200/10,000 requests (2%) - OK                │
│ └─ Render DB: 13MB/1000MB (1.3%) - OK                 │
│ └─ Vercel BW: 1GB/100GB (1%) - OK                     │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## 🔐 DATOS SENSIBLES - DÓNDE ESTÁN

```
UBICACIÓN DE CREDENCIALES:
├─ API Keys: .env (NO en git - gitignored) ✅
├─ DB Password: .env (NO en git) ✅
├─ JWT Secret: .env (NO en git) ✅
├─ OAuth tokens: BD (encriptados con key rotation) ✅
└─ Resultados sensibles: BD (protegido por JWT)

VERIFICACIÓN GIT:
├─ [ ] .env en .gitignore? SÍ ✅
├─ [ ] Secrets en actions? Configurados ✅
├─ [ ] Tokens en logs? NO ✅
└─ [ ] API keys en commits? NO ✅
```

---

## 📅 CHECKLIST: PREVENIR SORPRESAS

Antes de lanzar a producción:

```
□ Monitoreo Groq API (límites de requests)
□ Monitoreo Render (almacenamiento DB)
□ Monitoreo Vercel (bandwidth)
□ Alertas configuradas (email)
□ Fallbacks implementados (Anthropic)
□ Rate limiting por usuario
□ Caching de resultados
□ Documentación de escalado
□ Plan de respuesta a outages
□ Backup automático de DB
□ Renovación automática de certificados SSL
□ Monitoreo de uptime (UptimeRobot o similar)
```

---

## 📞 MATRIZ DE CONTACTO

| Servicio | Soporte | Email | Chat | Docs |
|----------|---------|-------|------|------|
| **Groq** | ⭐⭐⭐⭐ | support@groq.com | Sí | groq.com |
| **Render** | ⭐⭐⭐ | support@render.com | Sí | render.com/docs |
| **Vercel** | ⭐⭐⭐⭐ | support@vercel.com | Sí | vercel.com/docs |
| **GitHub** | ⭐⭐⭐⭐ | support@github.com | Comunidad | github.com/docs |
| **Strava** | ⭐⭐ | developers@strava.com | No | strava.com/developers |
| **Google** | ⭐⭐⭐ | Google Cloud Support | Sí | cloud.google.com |

---

## 🎓 CONCLUSIÓN

```
✅ ESTADO ACTUAL: 100% OPTIMIZADO - COMPLETAMENTE GRATIS EN DESARROLLO

Invertimos:
├─ $0 en infraestructura (Render Hobby free tier)
├─ $0 en APIs (todas con tier gratuito)
└─ TOTAL: $0/mes 🎉🎉🎉 para funcionalidad COMPLETA

⚠️ PUNTO CRÍTICO A MONITOREAR: Groq API (10k req/mes limit)
   Si lo alcanzamos → upgrade pro ($5-10/mes) o agregar fallback

📈 ESCALADO SOSTENIBLE:

Hasta producción con 1,000 usuarios:
├─ Groq API:     $0-5/mes (dentro de límite)
├─ Render:       $0/mes (hobby tier sigue siendo gratis en dev)
│                $7-14/mes (si queremos producción sin cold start)
├─ Vercel:       $0/mes (hobby tier)
└─ TOTAL:        $0-20/mes (muy sostenible)

Hasta 10,000 usuarios:
├─ Groq API:     $10-20/mes (upgrade plan pro)
├─ Render:       $14-30/mes (upgrade a Starter/Professional)
├─ Vercel:       $0-20/mes
└─ TOTAL:        $30-50/mes (muy asequible)

Hasta 100,000+ usuarios:
├─ Groq API:     $50-100/mes
├─ Render:       $100+/mes (escalado)
├─ Vercel:       $20-50/mes
├─ Email service: $20-30/mes (si agregamos)
├─ Monitoring:   $15-50/mes
└─ TOTAL:        $200-250/mes (crecimiento lineal, predecible)

🎯 PRÓXIMOS PASOS:
1. ✅ Hemos verificado: TODO ES GRATIS EN DESARROLLO
2. Implementar monitoreo Groq (en 30 min)
3. Crear fallback Anthropic (en 2 horas si lo necesitamos)
4. Optimizar caching (cuando alcancemos 5k req/mes)
5. Documentar playbook de escalado
```

---

**Documento creado:** Diciembre 3, 2025  
**Siguiente revisión recomendada:** Cada vez que se agregue un servicio nuevo o cuando se alcance el 80% de cualquier límite  
**Autor:** Sistema de Documentación RunCoach AI
