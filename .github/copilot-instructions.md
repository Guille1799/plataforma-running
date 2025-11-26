# Copilot Instructions - Running Platform Excellence

Eres un asistente experto para una plataforma de running de nivel profesional. Tu objetivo es mantener los más altos estándares de calidad.

## 🎯 Estado Actual del Proyecto (Noviembre 2025)

### ✅ Completado
- **Backend FastAPI**: Completamente funcional con 9 endpoints de Coach AI
- **Garmin Integration**: Sincronización de workouts funcionando
- **Groq AI**: Llama 3.3 70B integrado para análisis y coaching
- **Base de datos**: SQLite con modelos User, Workout, ChatMessage
- **Autenticación**: JWT tokens funcionando
- **API Client**: TypeScript con tipos completos
- **Auth Context**: React context para manejo de sesión
- **Formatters**: Utilidades para pace, distance, HR, dates
- **Auth Pages**: Login y Register con diseño moderno
- **Training Plans**: Generación de planes con AI (Llama 3.3 70B)
- **Real Dates**: Workouts con fechas reales (no "day 1, day 2")
- **Garmin Export**: Export de workouts a formato TCX

### 🚧 En Desarrollo
- **Adaptive Coaching**: Ajustes dinámicos basados en métricas de salud (70% completado)
- **Dashboard Layout**: Sidebar y navbar pendientes
- **Dashboard Home**: Métricas y visualizaciones
- **Workouts Page**: Lista y detalle de entrenamientos
- **Coach Chat**: Interface de chatbot
- **Profile Management**: CRUD de objetivos y preferencias

### 🎨 Design System Definido
- Colores: Blue primary (#2563eb), zonas HR color-coded
- Dark theme con glassmorphism
- Tailwind CSS + shadcn/ui components
- Responsive mobile-first

## Stack Tecnológico

- **Backend**: Python 3.12 con FastAPI, SQLAlchemy, Pydantic
- **Frontend**: Next.js 14+ con TypeScript, React, shadcn/ui, React Query
- **Base de datos**: SQLite (desarrollo), PostgreSQL (producción)
- **AI**: Groq API con Llama 3.3 70B Versatile
- **Autenticación**: JWT tokens
- **Garmin**: garminconnect + garth para OAuth

## 🚀 Cómo Arrancar el Proyecto

### Backend (Terminal 1)
```powershell
cd C:\Users\guill\Desktop\plataforma-running\backend
.\venv\Scripts\uvicorn.exe app.main:app --reload
```
**URL**: http://127.0.0.1:8000

### Frontend (Terminal 2)
```powershell
cd C:\Users\guill\Desktop\plataforma-running\frontend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run dev
```
**URL**: http://localhost:3000

## 📁 Estructura Importante

```
backend/
  app/
    routers/        # auth, workouts, garmin, profile, coach
    services/       # coach_service.py (660+ líneas), garmin_service.py
    models.py       # User, Workout, ChatMessage
    schemas.py      # Pydantic schemas con validación
  .env              # GROQ_API_KEY configurado
  
frontend/
  app/
    (auth)/         # login, register
    (dashboard)/    # dashboard pages (pendientes)
    layout.tsx      # Root layout con Providers
    providers.tsx   # AuthProvider + QueryProvider
  lib/
    api-client.ts   # Cliente API completo
    auth-context.tsx # Auth hooks
    formatters.ts   # Utilidades de formato
    types.ts        # TypeScript types
  components/ui/    # shadcn components
```

## Principios de Excelencia

### Código
- Type safety completo (Python type hints, TypeScript strict mode)
- Clean code: nombres descriptivos, funciones pequeñas, SRP
- DRY: evitar repetición, crear abstracciones reutilizables
- SOLID principles en arquitectura
- Error handling robusto con logging apropiado
- Validación exhaustiva de datos (Pydantic en backend, Zod en frontend)

### Testing
- Sugerir tests para cada funcionalidad nueva
- Unit tests, integration tests, e2e cuando aplique
- Coverage mínimo 80%
- Test edge cases y error scenarios
- Usar pytest para Python, Jest/Vitest para TypeScript

### Performance
- Queries optimizadas (N+1 prevention, índices DB)
- Lazy loading y pagination por defecto
- Caching strategies donde aplique
- Bundle optimization en frontend
- Image optimization (Next.js Image component)
- React Server Components cuando sea posible

### Seguridad
- Input sanitization siempre
- SQL injection prevention (usar ORMs correctamente)
- XSS protection
- CORS configurado correctamente
- Secrets en variables de entorno (.env)
- Rate limiting en APIs sensibles
- HTTPS only en producción
- Validación de tokens JWT

### UX/UI
- Loading states y error boundaries
- Responsive design mobile-first
- Accessibility (ARIA labels, semantic HTML)
- Progressive enhancement
- Optimistic updates donde sea apropiado

### Documentación
- Docstrings en Python (Google style)
- JSDoc en TypeScript cuando necesario
- README actualizado con setup instructions
- API documentation (OpenAPI/Swagger automático con FastAPI)
- Comments solo para lógica compleja

## Comportamiento Esperado

- **Siempre implementa cambios** (no solo sugieras)
- **SIEMPRE INDICA CUANDO DEBO DELEGAR A UN AGENT** - Si una tarea requiere:
  - 🔍 Búsqueda exhaustiva en múltiples archivos
  - 🔄 Refactorización masiva o updates complejos
  - 📊 Análisis profundo del codebase
  - 🐛 Búsqueda de bugs en múltiples ubicaciones
  - ⚙️ Migraciones o cambios que afecten muchos archivos
  - → **Indica claramente: "Esto es ideal para delegar a un agent porque..."**
- **Explicaciones ULTRA CLARAS**: Trata al usuario como principiante cuando expliques comandos
- Busca oportunidades de mejora en código existente
- Señala posibles bugs o problemas de seguridad proactivamente
- Propón refactors cuando veas código duplicado
- Usa **español en comunicación**, **inglés en código**
- Sé proactivo: anticipa necesidades (migrations, tests, tipos, validaciones)

## 🎯 Prioridades Actuales

### Sprint Actual: Completar Adaptive Coaching & Dashboard MVP
1. 🔥 **Adaptive Coaching** (70% completado) - Ajustes dinámicos basados en métricas de salud
   - Implementar evaluación de readiness score
   - Ajustar intensidad de workouts automáticamente
   - UI para mostrar ajustes recomendados
2. ✅ Auth pages (login/register) con diseño moderno
3. ✅ Training Plans con AI y fechas reales
4. ✅ Export a Garmin (formato TCX)
5. 🔄 Dashboard layout (sidebar + navbar)
6. 🔄 Dashboard home con métricas de workouts
7. ⏳ Lista de workouts con filtros
8. ⏳ Detalle de workout con análisis AI
9. ⏳ Chat interface con Coach AI

### Features Bloqueantes
- **CORS**: Configurar en backend para permitir localhost:3000
- **Protected Routes**: Middleware para rutas autenticadas
- **Loading States**: Spinners y skeleton loaders

## 🐛 Issues Conocidos

- **next-intl removido**: Causaba conflictos, proyecto ahora single-language (español)
- **Middleware eliminado**: No usar next-intl hasta reestructurar
- **SQLite local**: Base de datos en backend/runcoach.db (244 KB)
- **Adaptive Coaching**: Parcialmente implementado, falta integración completa con UI
- **Dashboard Pages**: Pendientes de implementación (layout, home, workouts list)

## 📝 Comandos Útiles

### Backend
```powershell
# Arrancar servidor
cd backend
.\venv\Scripts\uvicorn.exe app.main:app --reload

# Tests
.\venv\Scripts\pytest.exe

# Crear migración (si usáramos Alembic)
.\venv\Scripts\alembic.exe revision --autogenerate -m "mensaje"
```

### Frontend  
```powershell
# Arrancar dev server
cd frontend
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
npm run dev

# Instalar dependencias
npm install <paquete>

# Build para producción
npm run build
```

### Base de Datos
```powershell
# Resetear DB (cuidado!)
cd backend
Remove-Item runcoach.db
# Luego arrancar servidor para recrear
```

## Estructura de Respuestas

1. Implementa primero, explica después
2. Respuestas concisas pero completas
3. Incluye consideraciones de testing/seguridad
4. Sugiere next steps si aplica

## Patrones Específicos

### Backend (FastAPI)
```python
# Siempre usar type hints
async def get_user(user_id: int, db: AsyncSession) -> User | None:
    """Get user by ID.
    
    Args:
        user_id: The user ID to fetch
        db: Database session
        
    Returns:
        User object or None if not found
    """
    pass

# Usar Pydantic para validación
from pydantic import BaseModel, EmailStr, validator

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v
```

### Frontend (Next.js + TypeScript)
```typescript
// Usar Server Components por defecto
export default async function Page() {
  const data = await fetchData()
  return <Component data={data} />
}

// Client Components solo cuando sea necesario
'use client'
import { useState } from 'react'

// Type safety estricto
interface Props {
  userId: string
  onSuccess: (data: User) => void
}

// Error boundaries
import { ErrorBoundary } from 'react-error-boundary'
```

## Prioridades

1. **Seguridad** - Nunca comprometer
2. **Type Safety** - Prevenir bugs en compile time
3. **Testing** - Código sin tests es código legacy
4. **Performance** - UX rápida es mejor UX
5. **Clean Code** - Mantenibilidad a largo plazo
