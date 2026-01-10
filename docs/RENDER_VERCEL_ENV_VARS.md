# 🔧 Variables de Entorno Requeridas - Render y Vercel

**Última actualización:** 2026-01-10  
**Estado:** ⚠️ Configuración incompleta detectada

---

## 🎯 Problema Identificado

### ❌ Render: Falta `ENVIRONMENT=production`

**Problema:** Sin esta variable, el backend no sabe que está en producción y:
- ❌ No valida `SECRET_KEY` correctamente
- ❌ Usa configuraciones de desarrollo
- ❌ Puede generar keys temporales que cambian en cada reinicio
- ❌ No filtra correctamente los CORS origins

**Solución:** Agregar `ENVIRONMENT=production` en Render

---

## ✅ Variables Requeridas en Render

### **OBLIGATORIAS:**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `ENVIRONMENT` | `production` | **⚠️ FALTA - CRÍTICO** - Indica que está en producción |
| `DATABASE_URL` | `postgresql://...` | ✅ Ya configurado - URL de Supabase Session Pooler |
| `SECRET_KEY` | `[32+ caracteres]` | ✅ Ya configurado - Key para JWT (debe ser ≥32 chars) |
| `ALGORITHM` | `HS256` | ✅ Ya configurado - Algoritmo de JWT |

### **OPCIONALES (pero recomendadas):**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `GROQ_API_KEY` | `gsk_...` | ✅ Ya configurado - Para funcionalidades de AI |
| `ALLOWED_ORIGINS` | `https://plataforma-running.vercel.app` | Para CORS personalizado (si no está, usa defaults) |

---

## ✅ Variables Requeridas en Vercel

### **OBLIGATORIAS:**

| Variable | Valor | Descripción |
|----------|-------|-------------|
| `NEXT_PUBLIC_API_URL` | `https://plataforma-running.onrender.com` | **⚠️ VERIFICAR** - URL del backend API |

### **CÓMO VERIFICAR EN VERCEL:**

1. Ve a: https://vercel.com/dashboard → Tu proyecto → Settings → Environment Variables
2. Busca: `NEXT_PUBLIC_API_URL`
3. Debe tener el valor: `https://plataforma-running.onrender.com`
4. Si no existe, **AGREGARLO**:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://plataforma-running.onrender.com`
   - Environment: Production, Preview, Development (todos)

---

## 🔍 Por Qué Render tiene Timeout

**Posibles causas:**

1. **Cold Start (MÁS PROBABLE)**
   - Render Free Tier tiene cold starts de 30-60 segundos
   - El timeout del health check es de 15 segundos
   - **Solución:** Esperar el cold start o usar un plan pago

2. **Falta ENVIRONMENT=production**
   - Sin esta variable, el código puede generar errores al validar SECRET_KEY
   - Puede intentar usar SQLite en lugar de PostgreSQL
   - **Solución:** Agregar `ENVIRONMENT=production`

3. **Error al iniciar**
   - Si falta `ENVIRONMENT=production`, puede fallar la validación
   - Si la base de datos no está accesible, puede fallar
   - **Solución:** Verificar logs de Render para ver el error exacto

---

## 📋 Checklist de Configuración

### Render:
- [x] `DATABASE_URL` - ✅ Configurado
- [x] `SECRET_KEY` - ✅ Configurado
- [x] `ALGORITHM` - ✅ Configurado
- [x] `GROQ_API_KEY` - ✅ Configurado (opcional)
- [ ] `ENVIRONMENT` - ❌ **FALTA - AGREGAR `production`**

### Vercel:
- [ ] `NEXT_PUBLIC_API_URL` - ⚠️ **VERIFICAR** - Debe ser `https://plataforma-running.onrender.com`

---

## 🚀 Pasos para Arreglar

### Paso 1: Agregar ENVIRONMENT en Render

1. Ve a: https://dashboard.render.com → Tu servicio Backend → Environment
2. Click en "Add Environment Variable"
3. Key: `ENVIRONMENT`
4. Value: `production`
5. Click "Save Changes"
6. Render reiniciará automáticamente el servicio

### Paso 2: Verificar NEXT_PUBLIC_API_URL en Vercel

1. Ve a: https://vercel.com/dashboard → Tu proyecto → Settings → Environment Variables
2. Busca `NEXT_PUBLIC_API_URL`
3. Si no existe, agregar:
   - Key: `NEXT_PUBLIC_API_URL`
   - Value: `https://plataforma-running.onrender.com`
   - Environments: Production, Preview, Development (todos)
4. Click "Save"
5. Hacer un nuevo deployment (o esperar al siguiente push)

### Paso 3: Verificar Logs de Render

Después de agregar `ENVIRONMENT=production`:
1. Ve a: Render Dashboard → Tu servicio → Logs
2. Busca errores de validación de SECRET_KEY
3. Verifica que dice "Production mode: Using Alembic migrations"
4. Verifica que conecta correctamente a la base de datos

---

## 🔍 Cómo Verificar que Funciona

### Render:
```bash
# Después de agregar ENVIRONMENT=production, los logs deberían mostrar:
"Production mode: Using Alembic migrations for database schema management"
"INFO:     Application startup complete."
```

### Vercel:
- El frontend debería poder hacer requests al backend
- Verifica en la consola del navegador que no haya errores de CORS
- Verifica que `NEXT_PUBLIC_API_URL` apunte al backend correcto

---

**Última actualización:** 2026-01-10  
**Mantenido por:** Sistema de Monitoreo RunCoach AI
