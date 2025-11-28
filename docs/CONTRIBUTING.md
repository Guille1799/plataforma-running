# Contributing to RunCoach AI

¡Gracias por tu interés en contribuir a RunCoach AI! 🏃‍♂️

## 🚀 Cómo Contribuir

### 1. Fork y Clone

```bash
# Fork el repositorio en GitHub
# Luego clona tu fork
git clone https://github.com/TU-USUARIO/plataforma-running.git
cd plataforma-running
```

### 2. Setup de Desarrollo

```bash
# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias de desarrollo
cd backend
pip install -r requirements.txt
pip install -r requirements-test.txt

# Configurar .env
cp .env.example .env
# Edita .env con tus credenciales
```

### 3. Crear Branch

```bash
# Crear branch para tu feature
git checkout -b feature/mi-nueva-feature

# O para bug fix
git checkout -b fix/mi-fix
```

### 4. Desarrollo

#### Estándares de Código

**Python (Backend)**
- Seguir PEP 8
- Type hints obligatorios
- Docstrings para funciones públicas (Google style)
- Máximo 100 caracteres por línea

```python
def analyze_workout(
    workout: models.Workout,
    user: models.User
) -> Dict[str, Any]:
    """Analyze workout and provide feedback.
    
    Args:
        workout: Workout to analyze
        user: User who performed workout
        
    Returns:
        Dict with analysis and recommendations
    """
    pass
```

**TypeScript (Frontend - Futuro)**
- Seguir estilo Airbnb
- Strict mode habilitado
- Props interfaces claramente definidas

#### Testing

```bash
# Ejecutar tests antes de commit
pytest

# Con coverage
pytest --cov=app tests/

# Tests específicos
pytest tests/test_auth.py -v
```

**Reglas de Testing:**
- Mínimo 80% de coverage
- Tests para happy path y edge cases
- Tests para manejo de errores

### 5. Commit

```bash
# Commits descriptivos con prefijos
git commit -m "feat: Add weekly plan generation"
git commit -m "fix: Resolve Garmin sync timeout issue"
git commit -m "docs: Update API documentation"
git commit -m "test: Add tests for coach service"
```

**Prefijos de Commit:**
- `feat:` Nueva feature
- `fix:` Bug fix
- `docs:` Cambios en documentación
- `test:` Añadir o modificar tests
- `refactor:` Refactorización sin cambios funcionales
- `perf:` Mejoras de performance
- `style:` Cambios de formato (espacios, etc)
- `chore:` Mantenimiento (deps, config, etc)

### 6. Push y Pull Request

```bash
# Push tu branch
git push origin feature/mi-nueva-feature
```

Luego crea un Pull Request en GitHub con:
- Descripción clara de los cambios
- Referencias a issues relacionados
- Screenshots si aplica (UI changes)
- Lista de tests añadidos

## 📋 Checklist antes de PR

- [ ] Código sigue las guías de estilo
- [ ] Type hints completos (Python)
- [ ] Docstrings añadidos
- [ ] Tests escritos y pasando
- [ ] Coverage >= 80%
- [ ] Documentación actualizada (si aplica)
- [ ] CHANGELOG.md actualizado
- [ ] No hay secrets hardcodeados
- [ ] .gitignore actualizado (si añadiste archivos)

## 🏗️ Arquitectura

### Backend Structure
```
app/
├── main.py           # FastAPI app, routers
├── models.py         # SQLAlchemy models
├── schemas.py        # Pydantic schemas
├── crud.py           # DB operations
├── security.py       # Auth logic
├── core/
│   └── config.py     # Settings
├── routers/          # API endpoints
└── services/         # Business logic
```

### Principios
- **Separation of Concerns**: Routers → Services → CRUD
- **Dependency Injection**: Use FastAPI `Depends()`
- **Type Safety**: Pydantic para validación
- **Error Handling**: HTTPException con status codes apropiados
- **Security**: Nunca hardcodear secrets

## 🎯 Áreas de Contribución

### High Priority
- [ ] Frontend (Next.js)
- [ ] Alembic migrations
- [ ] Advanced FIT parsing
- [ ] Redis caching
- [ ] Rate limiting

### Medium Priority
- [ ] Strava integration
- [ ] Weather API
- [ ] Voice coaching
- [ ] Race predictor
- [ ] Nutrition tracking

### Low Priority
- [ ] Social features
- [ ] Sleep integration
- [ ] Injury prevention ML

### Always Welcome
- 🐛 Bug fixes
- 📝 Documentation improvements
- 🧪 More tests
- 🌐 Translations
- ♿ Accessibility improvements

## 💡 Ideas y Sugerencias

¿Tienes una idea? ¡Abre un issue primero!

Etiquetas para issues:
- `feature` - Nueva funcionalidad
- `bug` - Algo no funciona
- `documentation` - Mejoras en docs
- `enhancement` - Mejora a feature existente
- `good first issue` - Bueno para principiantes
- `help wanted` - Necesitamos ayuda

## 🔒 Seguridad

Si encuentras una vulnerabilidad de seguridad, **NO abras un issue público**.

En su lugar, envía un email a: security@runcoach.ai

## 📞 Contacto

- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions
- **Email:** guillermomartindeoliva@gmail.com

## 📜 Código de Conducta

### Nuestros Valores

- **Respeto:** Trata a todos con respeto
- **Inclusión:** Todos son bienvenidos
- **Colaboración:** Trabajamos juntos
- **Calidad:** Nos esforzamos por la excelencia
- **Aprendizaje:** Compartimos conocimiento

### Comportamiento Esperado

✅ Ser amigable y paciente
✅ Ser considerado con diferentes perspectivas
✅ Dar y recibir feedback constructivo
✅ Aceptar responsabilidad por errores
✅ Enfocarse en lo mejor para la comunidad

### Comportamiento Inaceptable

❌ Lenguaje o imágenes sexuales
❌ Trolling o comentarios insultantes
❌ Acoso público o privado
❌ Publicar información privada sin permiso
❌ Comportamiento no profesional

## 🙏 Reconocimientos

Los contribuidores serán reconocidos en:
- README.md (sección Contributors)
- CHANGELOG.md (en releases)
- Hall of Fame (website futuro)

## 📝 Licencia

Al contribuir, aceptas que tus contribuciones se licencien bajo la licencia MIT del proyecto.

---

**¡Gracias por hacer RunCoach AI mejor! 🚀🏃‍♂️**
