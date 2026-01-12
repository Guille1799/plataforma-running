# 📋 TODO Futuro y Mejoras Pendientes

**Fecha de creación:** 2026-01-10  
**Propósito:** Documentar todas las mejoras, features y trabajos pendientes que detectamos pero que NO haremos ahora. Este documento se irá actualizando conforme encontremos más cosas.

---

## 🎯 Enfoque Actual: Garmin

**Decisión:** Nos enfocamos en hacer Garmin perfecto primero, luego expandiremos a otros dispositivos.

---

## 📱 Dispositivos Pendientes (No Garmin)

### Xiaomi / Amazfit
- [ ] Dashboard específico (`XiaomiDashboard`) - **Estado:** Existe pero necesita mejoras
- [ ] Integración completa de sincronización automática
- [ ] Soporte para métricas específicas de Xiaomi/Amazfit
- [ ] Optimización de widgets para métricas básicas (sueño, pasos, rachas)

### Apple Health
- [ ] Dashboard específico (actualmente usa `ManualDashboard`)
- [ ] Sincronización automática en tiempo real (actualmente solo importación manual)
- [ ] Integración con HealthKit API (si es posible)
- [ ] Mejora del flujo de importación de archivos XML

### Strava
- [ ] Dashboard específico (actualmente usa `ManualDashboard`)
- [ ] Widgets para segmentos y PRs
- [ ] Integración con features sociales de Strava
- [ ] Visualización de rutas GPS mejorada

### Manual Entry
- [ ] Mejoras en `ManualDashboard` para mejor UX
- [ ] Templates de entrada rápida
- [ ] Validación mejorada de datos manuales

---

## 🔧 Mejoras Técnicas Generales

### Sincronización
- [ ] Sistema de retry automático para sincronizaciones fallidas
- [ ] Notificaciones cuando la sincronización falla
- [ ] Logs detallados de sincronización para debugging
- [ ] Dashboard de estado de sincronización por dispositivo

### Performance
- [ ] Optimización de queries para dashboards
- [ ] Caché de datos de salud para reducir llamadas al backend
- [ ] Lazy loading de componentes pesados

### UX/UI
- [ ] Mejoras en responsive design para móviles
- [ ] Modo claro/oscuro (actualmente solo oscuro)
- [ ] Accesibilidad (ARIA labels, keyboard navigation)
- [ ] Animaciones y transiciones más suaves

---

## 📊 Features Pendientes

### Analytics
- [ ] Comparación de rendimiento entre períodos
- [ ] Predicciones de rendimiento basadas en tendencias
- [ ] Exportación de reportes en PDF/Excel

### Social
- [ ] Compartir logros en redes sociales
- [ ] Comparación con otros usuarios (anónima)
- [ ] Retos y competencias

### Notificaciones
- [ ] Notificaciones push para recordatorios de entrenamiento
- [ ] Alertas de sobreentrenamiento
- [ ] Recordatorios de sincronización

---

## 🌐 Internacionalización (i18n)

### Estado Actual
- ❌ **No está implementado** - Aunque `next-intl` está instalado, no está configurado
- ❌ **Todo está en inglés** - Textos hardcodeados en inglés
- ✅ **Backend soporta idioma** - Se guarda `user.language` en BD
- ⚠️ **Onboarding pregunta idioma al final** - Debería ser el primer paso

### Trabajo Pendiente
- [ ] Configurar `next-intl` en Next.js
- [ ] Mover selección de idioma al primer paso del onboarding
- [ ] Traducir todo el onboarding a español e inglés
- [ ] Limitar idiomas a ES y EN (eliminar FR y DE por ahora)
- [ ] Traducir resto de la aplicación (dashboard, componentes, etc.)
- [ ] Sistema de traducciones mantenible

**Ver:** `docs/ONBOARDING_PROBLEMAS_Y_MEJORAS.md` para detalles completos

---

## 🐛 Bugs Conocidos (No Críticos)

### Onboarding
- [ ] "Balanced" aparece preseleccionado visualmente sin que el usuario lo elija
- [ ] No hay UI para configurar "Custom" coach prompt (aunque el backend lo soporta)
- [ ] Onboarding está en inglés pero pregunta por idioma al final (debería ser primero)

**Ver:** `docs/ONBOARDING_PROBLEMAS_Y_MEJORAS.md` para detalles completos

---

## 📝 Notas

- Este documento se actualiza conforme encontramos cosas que necesitan trabajo
- Las prioridades pueden cambiar según feedback de usuarios
- Algunos items pueden moverse a otros documentos si se vuelven críticos
