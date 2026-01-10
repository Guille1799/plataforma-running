# 📚 Guías y Explicaciones - RunCoach AI

Esta carpeta contiene la **documentación completa y actualizada** del proyecto RunCoach AI.

---

## 📖 Documentos Disponibles

### 🔐 [00_SECURITY_AND_SECRETS.md](00_SECURITY_AND_SECRETS.md)
**Gestión de Datos Sensibles y Seguridad**

Aprende cómo se gestionan los secrets en el proyecto:
- ✅ Sistema de `.env` vs `.env.example`
- ✅ Autenticación JWT (access + refresh tokens)
- ✅ OAuth con Garmin Connect
- ✅ Protección en 4 capas
- ✅ Qué hacer si se filtra un secret
- ✅ Checklist de seguridad

**Ideal para:** Entender cómo protegemos las credenciales y datos sensibles.

---

### 🏗️ [01_ARCHITECTURE.md](01_ARCHITECTURE.md)
**Arquitectura del Sistema Completa**

Todo sobre la estructura técnica del proyecto:
- ✅ Diagrama de arquitectura completo
- ✅ Stack tecnológico (Next.js, FastAPI, PostgreSQL, Celery, Redis)
- ✅ Esquema de base de datos con todas las tablas
- ✅ Sistema de autenticación
- ✅ Integraciones (Groq IA, Garmin Connect)
- ✅ Tareas asíncronas con Celery Beat
- ✅ API REST completa
- ✅ Frontend con React Query + Zustand
- ✅ Despliegue en Docker + Render

**Ideal para:** Entender cómo funciona el sistema técnicamente.

---

### 👨‍💻 [02_DEVELOPMENT_GUIDE.md](02_DEVELOPMENT_GUIDE.md)
**Guía Completa de Desarrollo**

Guía práctica para desarrolladores:
- ✅ Setup inicial paso a paso
- ✅ Estructura del proyecto
- ✅ Flujo de trabajo con Git
- ✅ Comandos útiles (Docker, backend, frontend, DB, Celery)
- ✅ Base de datos: migraciones, queries, índices
- ✅ Testing (manual y automatizado)
- ✅ Debugging (logs, breakpoints, DevTools)
- ✅ Convenciones de código
- ✅ Cómo añadir nuevas features
- ✅ Troubleshooting de problemas comunes

**Ideal para:** Desarrollar nuevas features o resolver problemas.

---

### 🏃 [03_FEATURES_AND_WORKFLOWS.md](03_FEATURES_AND_WORKFLOWS.md)
**Features y Flujos de Usuario**

Todo sobre las funcionalidades del proyecto:
- ✅ Dashboard con métricas en tiempo real
- ✅ Análisis de entrenamientos (GPX/FIT + IA)
- ✅ Métricas de salud (Garmin sync, HRV, alertas)
- ✅ Planes de entrenamiento (wizard, generación IA, adaptación)
- ✅ Base de datos de 52 carreras
- ✅ Flujos completos de usuario (nuevo usuario, usuario avanzado)
- ✅ Arquitectura de datos con diagramas

**Ideal para:** Entender qué hace la aplicación y cómo se usan las features.

---

## 🚀 ¿Por Dónde Empezar?

### Si eres nuevo en el proyecto:
1. 📖 Lee [02_DEVELOPMENT_GUIDE.md](02_DEVELOPMENT_GUIDE.md) → Setup inicial
2. 🏗️ Lee [01_ARCHITECTURE.md](01_ARCHITECTURE.md) → Entiende la arquitectura
3. 🏃 Lee [03_FEATURES_AND_WORKFLOWS.md](03_FEATURES_AND_WORKFLOWS.md) → Conoce las features

### Si vas a trabajar con seguridad/secrets:
- 🔐 Lee [00_SECURITY_AND_SECRETS.md](00_SECURITY_AND_SECRETS.md)

### Si vas a añadir una nueva feature:
1. 🏗️ [01_ARCHITECTURE.md](01_ARCHITECTURE.md) → Entiende dónde encaja
2. 👨‍💻 [02_DEVELOPMENT_GUIDE.md](02_DEVELOPMENT_GUIDE.md) → Sección "Añadir Nuevas Features"
3. 🏃 [03_FEATURES_AND_WORKFLOWS.md](03_FEATURES_AND_WORKFLOWS.md) → Ve cómo funcionan las features existentes

---

## 📊 Estadísticas

- **Total de líneas de documentación:** ~3.000
- **Diagramas:** 5+
- **Ejemplos de código:** 50+
- **Comandos útiles:** 100+

---

## 🔄 Última Actualización

**Fecha:** 8 de enero de 2026  
**Versión:** 3.0  
**Estado:** ✅ Documentación completa y actualizada

---

## 📝 Notas

- Todos los archivos están en Markdown para fácil navegación
- Los diagramas usan caracteres ASCII para verse en cualquier editor
- Los ejemplos de código están listos para copiar y pegar
- La documentación está sincronizada con el código actual

---

**¿Tienes preguntas?** Revisa la sección de troubleshooting en [02_DEVELOPMENT_GUIDE.md](02_DEVELOPMENT_GUIDE.md)
