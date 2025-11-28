# RunCoach Backend - PostgreSQL + Docker Setup Guide

## 🚀 Quick Start

### 1. Install Docker & Docker Compose
- Download from: https://www.docker.com/products/docker-desktop
- Verify installation: `docker --version` && `docker-compose --version`

### 2. Update Environment Variables
```bash
cd backend
cp .env.example .env
# Edit .env with your values (especially ANTHROPIC_API_KEY)
```

### 3. Start Services
```bash
cd ..  # Go to project root
docker-compose up -d
```

**Services running:**
- PostgreSQL: localhost:5432
- Redis: localhost:6379

### 4. Update Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 5. Start FastAPI Server
```bash
cd backend
uvicorn app.main:app --reload
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

---

## 📦 Database Connection

### Current Setup
- **Engine**: PostgreSQL 16 (Alpine Linux - minimal)
- **Host**: localhost:5432
- **Database**: runcoach_db
- **User**: runcoach_user
- **Password**: your_secure_password_here (change in .env)

### Connection String
```
postgresql://runcoach_user:your_secure_password_here@localhost:5432/runcoach_db
```

### Health Check
```bash
docker-compose ps  # Check all services are running
docker logs runcoach_postgres  # View PostgreSQL logs
```

---

## 🗄️ Database Migrations (Future - Alembic)

Once ready to use Alembic:

```bash
# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migration
alembic upgrade head
```

For now, `models.Base.metadata.create_all(bind=engine)` handles table creation.

---

## 📝 Environment Variables

See `.env.example` for all available options:

| Variable | Purpose | Example |
|----------|---------|---------|
| DATABASE_URL | PostgreSQL connection | postgresql://user:pass@localhost:5432/db |
| ANTHROPIC_API_KEY | Claude API key | sk-ant-xxxxx |
| SECRET_KEY | JWT signing key | random-string-min-32-chars |
| ALLOWED_ORIGINS | CORS origins | http://localhost:3000,http://localhost:8000 |

---

## 🛑 Stop Services

```bash
docker-compose down  # Stop and remove containers
docker-compose down -v  # Also remove volumes (deletes data!)
```

---

## 🔧 Troubleshooting

### PostgreSQL won't start
```bash
docker-compose logs postgres
# Check if port 5432 is already in use
lsof -i :5432
```

### Connection refused
```bash
# Make sure services are running
docker-compose ps

# Try reconnecting after 10 seconds (services need time to start)
```

### Reset everything
```bash
docker-compose down -v
docker-compose up -d
# Services will reinitialize from scratch
```

---

## ✅ Next Steps

1. ✅ PostgreSQL configured
2. 🔲 Alembic migrations setup
3. 🔲 JWT authentication
4. 🔲 Tests with pytest
5. 🔲 FIT file upload
6. 🔲 Claude AI Coach integration
