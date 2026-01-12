# 🔕 Desactivar Notificaciones de GitHub Actions

## Método 1: Desactivar desde GitHub (Recomendado)

1. Ve a: **https://github.com/settings/notifications**
2. Busca la sección **"Actions"**
3. Desmarca:
   - ✅ **"Workflow runs"** (ejecuciones de workflows)
   - ✅ **"Workflow run failures"** (fallos de workflows)
4. Guarda los cambios

## Método 2: Desactivar solo para este repositorio

1. Ve a: **https://github.com/Guille1799/plataforma-running**
2. Click en **"Settings"** (parte superior del repo)
3. Ve a: **"Notifications"** (menú lateral izquierdo)
4. Desmarca las notificaciones de Actions que quieras desactivar

## Método 3: Desactivar el workflow completamente

Si no necesitas el monitoreo automático, puedes:
1. Eliminar el archivo `.github/workflows/monitor-production.yml`
2. O comentar el schedule (línea 8-10) para que solo se ejecute manualmente

## Método 4: Cambiar frecuencia del schedule

Puedes cambiar el cron de cada hora a cada 6 horas o una vez al día:

```yaml
schedule:
  # Cada 6 horas en lugar de cada hora
  - cron: '0 */6 * * *'
  
  # O una vez al día a las 9 AM UTC
  - cron: '0 9 * * *'
```
