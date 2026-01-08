# 🚀 Guía de Inicio Rápido

Hemos simplificado el proceso de arranque para usar **Docker** (backend) y **Next.js** (frontend) de forma robusta.

## 1. Iniciar la Plataforma (`start-dev.bat`)

Simplemente haz doble clic en el archivo `start-dev.bat` en la carpeta del proyecto.

Este script:
1. Levanta el Backend, Base de Datos y Redis usando Docker.
2. Espera 10 segundos a que todo esté listo.
3. Abre una nueva ventana negra para el Frontend.

**URLs Importantes:**
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/docs

## 2. Detener la Plataforma (`stop-dev.bat`)

Para apagar todo correctamente:
1. Cierra la ventana negra del Frontend.
2. Haz doble clic en `stop-dev.bat`.

Esto detendrá los contenedores de Docker para liberar memoria.

---

### Solución de Problemas

**Si el backend falla:**
- Asegúrate de que Docker Desktop esté abierto y el icono de la ballena esté visible.
- Ejecuta `docker ps` en una terminal para ver si los contenedores `runcoach_backend`, `runcoach_db` y `runcoach_redis` están corriendo.

**Si el frontend falla:**
- Verifica que no tengas otra cosa corriendo en el puerto 3000.
- En la ventana del frontend, busca errores de compilación.
