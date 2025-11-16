# 🚀 DEPLOY GUIDE - Plataforma de Running

Guía paso-a-paso para desplegar la plataforma en producción.

---

## 📋 PREREQUISITOS

### Software Requerido
- Python 3.12+ (`python --version`)
- Node.js 18+ (`node --version`)
- Docker Desktop (opcional pero recomendado)
- Git (`git --version`)

### Cuentas Necesarias
- [ ] Groq API Key (https://console.groq.com) - `GROQ_API_KEY`
- [ ] Garmin Developer Account (para OAuth)
- [ ] PostgreSQL Database (producción) - alternativa a SQLite

### Archivos de Configuración
```
backend/.env          (Variables de entorno)
frontend/.env.local   (Variables de entorno frontend)
docker-compose.yml    (Si usas Docker)
```

---

## 📊 STEP 1: VALIDACIÓN PRE-DEPLOY

Ejecuta el script de validación:

```powershell
# En Windows PowerShell
python validate_platform.py

# O en Linux/Mac
python3 validate_platform.py
```

**Resultado esperado**:
```
🎯 RESUMEN
✅ Pasados: 25
❌ Críticos: 0
⚠️ Advertencias: 0

🚀 Estado: LISTA PARA DEPLOY
```

Si hay ❌ críticos, FIX antes de continuar.

---

## 🔧 STEP 2: CONFIGURACIÓN DE VARIABLES

### Backend (.env)

```bash
# Database
DATABASE_URL=sqlite:///runcoach.db  # Desarrollo
# DATABASE_URL=postgresql://user:pass@host:5432/runcoach  # Producción

# Groq AI
GROQ_API_KEY=gsk_...  # Obtener en https://console.groq.com

# Garmin (opcional)
GARMIN_CONSUMER_KEY=...
GARMIN_CONSUMER_SECRET=...

# Security
JWT_SECRET_KEY=tu_secret_super_largo_aleatorio_aqui
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS (Producción)
ALLOWED_ORIGINS=https://tudominio.com,https://www.tudominio.com

# Logging
LOG_LEVEL=INFO
DEBUG=False
```

### Frontend (.env.local)

```bash
# API
NEXT_PUBLIC_API_URL=https://api.tudominio.com

# Groq (si usas en frontend)
NEXT_PUBLIC_GROQ_API_KEY=gsk_...  # NO recomendado, usa backend
```

---

## 🐳 STEP 3: DEPLOYMENT OPCIONES

### OPCIÓN A: Docker (Recomendado)

#### a) Build Images

```bash
cd plataforma-running

# Backend image
docker build -f backend/Dockerfile -t runcoach-backend:latest ./backend

# Frontend image  
docker build -f frontend/Dockerfile -t runcoach-frontend:latest ./frontend
```

#### b) Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    image: runcoach-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://runcoach:password@db:5432/runcoach
      - GROQ_API_KEY=${GROQ_API_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
    depends_on:
      - db
    volumes:
      - ./backend:/app  # Development only

  frontend:
    image: runcoach-frontend:latest
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=runcoach
      - POSTGRES_USER=runcoach
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### c) Deploy con Docker Compose

```bash
# Desarrollo
docker-compose up

# Producción (background)
docker-compose up -d

# Ver logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop
docker-compose down

# Update images
docker-compose pull && docker-compose up -d
```

---

### OPCIÓN B: Heroku

#### a) Preparar Heroku

```bash
# Login
heroku login

# Crear apps
heroku create runcoach-backend --buildpack heroku/python
heroku create runcoach-frontend --buildpack heroku/nodejs
```

#### b) Backend Deploy

```bash
cd backend

# Config vars
heroku config:set GROQ_API_KEY=gsk_... -a runcoach-backend
heroku config:set DATABASE_URL=postgresql://... -a runcoach-backend
heroku config:set JWT_SECRET_KEY=... -a runcoach-backend

# Deploy
git push heroku main

# Ver logs
heroku logs --tail -a runcoach-backend
```

#### c) Frontend Deploy

```bash
cd frontend

# Config vars
heroku config:set NEXT_PUBLIC_API_URL=https://runcoach-backend.herokuapp.com -a runcoach-frontend

# Deploy
git push heroku main

# Ver logs
heroku logs --tail -a runcoach-frontend
```

---

### OPCIÓN C: AWS (EC2 + ALB)

#### a) EC2 Setup

```bash
# SSH a instancia
ssh -i key.pem ubuntu@instance-ip

# Update OS
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com | sudo bash

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone repo
git clone https://github.com/tu-usuario/plataforma-running.git
cd plataforma-running

# Variables de entorno
sudo nano backend/.env
# Agrega variables aquí

# Start services
docker-compose up -d
```

#### b) SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx

sudo certbot certonly --standalone -d tudominio.com

# Auto-renewal
sudo systemctl enable certbot.timer
```

#### c) Nginx Reverse Proxy

```nginx
server {
    listen 443 ssl http2;
    server_name tudominio.com;

    ssl_certificate /etc/letsencrypt/live/tudominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tudominio.com/privkey.pem;

    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
    }
}

server {
    listen 80;
    server_name tudominio.com;
    return 301 https://$server_name$request_uri;
}
```

---

## 🗄️ STEP 4: DATABASE MIGRATION

### SQLite → PostgreSQL

```bash
# 1. Dump SQLite
sqlite3 backend/runcoach.db .dump > backup.sql

# 2. Create PostgreSQL DB
createdb runcoach

# 3. Migrate with SQLAlchemy
cd backend
python3 -c "
from app.models import Base
from app.database import engine
Base.metadata.create_all(bind=engine)
"

# 4. Import data (si es necesario)
psql runcoach < backup.sql
```

### Health Check

```bash
# Verifica que DB está OK
curl http://localhost:8000/api/v1/health

# Expected:
# {"status": "ok", "database": "connected"}
```

---

## 🔐 STEP 5: SECURITY CHECKLIST

- [ ] JWT_SECRET_KEY: ≥ 32 caracteres aleatorios
- [ ] CORS: Solo dominio(s) permitidos
- [ ] HTTPS: Certificado válido
- [ ] Rate limiting: Habilitado (slowapi)
- [ ] CSRF protection: Activo
- [ ] SQL injection: Prevenido (ORM SQLAlchemy)
- [ ] XSS protection: Headers de seguridad
- [ ] Secrets: NO en código, solo .env
- [ ] API Keys: Rotadas regularmente
- [ ] Backups: Automáticos, tested

### Headers de Seguridad (Nginx)

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Content-Security-Policy "default-src 'self'" always;
```

---

## 📊 STEP 6: MONITORING & LOGGING

### Backend Logs

```bash
# En Docker
docker-compose logs -f backend

# En Heroku
heroku logs -f -a runcoach-backend

# En EC2
tail -f /var/log/runcoach/backend.log
```

### Metrics a Monitorear

- [ ] CPU usage < 70%
- [ ] Memory < 1GB
- [ ] Response time < 500ms
- [ ] Error rate < 0.1%
- [ ] Database connections < 50

### Alertas (Recomendado)

```python
# Con Sentry para errores
import sentry_sdk

sentry_sdk.init(
    dsn="https://key@sentry.io/project-id",
    environment="production"
)

# Con Datadog para metrics
from datadog import initialize, api

options = {
    'api_key': 'DATADOG_API_KEY',
    'app_key': 'DATADOG_APP_KEY'
}
initialize(**options)
```

---

## 🚦 STEP 7: SMOKE TESTS

Después de deploy, verifica:

```bash
# Health check
curl https://api.tudominio.com/api/v1/health

# Auth endpoint
curl -X POST https://api.tudominio.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'

# Frontend loads
curl https://tudominio.com | grep -q "RunCoach" && echo "✅ Frontend OK"

# Swagger docs
curl https://api.tudominio.com/docs | grep -q "openapi" && echo "✅ Docs OK"
```

---

## 🔄 STEP 8: CONTINUOUS DEPLOYMENT

### GitHub Actions (CI/CD)

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Tests
        run: |
          cd backend && python -m pytest
          cd ../frontend && npm test
      
      - name: Deploy Backend
        run: docker push runcoach-backend:latest
        env:
          DOCKER_USERNAME: ${{ secrets.DOCKER_USERNAME }}
          DOCKER_PASSWORD: ${{ secrets.DOCKER_PASSWORD }}
      
      - name: Deploy Frontend
        run: |
          cd frontend
          npm run build
          npm run deploy
        env:
          NEXT_PUBLIC_API_URL: ${{ secrets.API_URL }}
```

---

## 📈 STEP 9: PERFORMANCE OPTIMIZATION

### Backend Caching

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def search_races(query: str):
    # Cached para 1 hora
    return db.search(query)
```

### Frontend Optimization

```bash
# Build optimizado
cd frontend
npm run build

# Resultado esperado
# ✅ Built in XX seconds
# ✅ Bundle size: < 500KB (gzipped)
```

### Database Optimization

```sql
-- Índices críticos
CREATE INDEX idx_user_id ON workouts(user_id);
CREATE INDEX idx_start_time ON workouts(start_time);
CREATE INDEX idx_email ON users(email);

-- Query plan
EXPLAIN ANALYZE SELECT * FROM workouts WHERE user_id = 1;
```

---

## 🆘 TROUBLESHOOTING

### Backend no arranca

```bash
# Revisar logs
docker-compose logs backend

# Reiniciar
docker-compose restart backend

# Revisar config
cat backend/.env | grep -E "DATABASE|GROQ"

# Test connection
python3 -c "from app.database import engine; print(engine.execute('SELECT 1'))"
```

### Frontend 404 en /api

```bash
# Revisar NEXT_PUBLIC_API_URL
echo $NEXT_PUBLIC_API_URL

# Rebuildar
npm run build

# Clear cache
rm -rf .next
npm run dev
```

### Database connection error

```bash
# Test connection
psql postgresql://user:pass@host:5432/runcoach -c "SELECT 1"

# Si falla, revisar:
# 1. Host correcto
# 2. Credenciales
# 3. Firewall abierto (5432)
# 4. DB creada
```

### Rate limiting bloqueando requests

```python
# Ajusta en main.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["1000/day", "100/hour"]  # Aumenta si es necesario
)
```

---

## 🎯 ROLLBACK PLAN

Si algo falla:

```bash
# 1. Identifica versión anterior
docker image ls | head -2

# 2. Rollback
docker-compose down
docker tag runcoach-backend:v1-previous runcoach-backend:latest
docker-compose up -d

# 3. Restaura DB si es necesario
psql runcoach < backup_previous.sql

# 4. Verifica
curl https://api.tudominio.com/health
```

---

## 📋 CHECKLIST FINAL

- [ ] Variables .env configuradas ✅
- [ ] Tests pasando 100% ✅
- [ ] Security checklist completo ✅
- [ ] Database migrada/pronta ✅
- [ ] Certificados SSL ✅
- [ ] DNS apuntando ✅
- [ ] CDN configurado (si aplica) ✅
- [ ] Backups automatizados ✅
- [ ] Monitoring habilitado ✅
- [ ] Smoke tests pasados ✅
- [ ] Rollback plan documentado ✅

---

## 🎉 DEPLOY EXITOSO

Si todo está ✅, la plataforma está **EN PRODUCCIÓN**!

```
🚀 plataforma-running is LIVE
📍 https://tudominio.com
🎯 Status: Excellent
📊 Metrics: Optimal
🔐 Security: Excellent
```

**Próximos pasos**:
1. Monitorea primeras 24 horas
2. Recopila feedback de usuarios
3. Bug fixes rápidos si hay issues
4. Plan de mejora continua

---

**¡ÉXITO!** 🏆
