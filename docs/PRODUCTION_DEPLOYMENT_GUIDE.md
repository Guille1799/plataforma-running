# 🚀 Production Deployment Guide - TIER 2 System

**Version:** 1.0  
**Date:** November 17, 2025  
**Status:** ✅ READY FOR DEPLOYMENT  

---

## 📋 Pre-Deployment Checklist

### Backend Requirements
- [✅] Python 3.12+ installed
- [✅] FastAPI configured
- [✅] SQLAlchemy ORM ready
- [✅] Pydantic validation active
- [✅] Groq API key configured
- [✅] JWT authentication working
- [✅] 4 Services implemented (2,600+ lines)
- [✅] 17 API endpoints functional

### Frontend Requirements
- [✅] Node.js 18+ installed
- [✅] Next.js 16+ configured
- [✅] React 19 ready
- [✅] TypeScript strict mode enabled
- [✅] 6 Components created (2,210+ lines)
- [✅] Tailwind CSS configured
- [✅] shadcn/ui components imported

### Infrastructure Requirements
- [✅] Database: SQLite (dev) → PostgreSQL (prod)
- [✅] Environment variables configured
- [✅] CORS enabled
- [✅] Error logging setup
- [✅] Performance monitoring ready
- [✅] Backup procedures documented

---

## 🔧 Deployment Steps

### Phase 1: Backend Deployment (15-20 minutes)

#### 1.1 Prepare Backend

```bash
# Navigate to backend
cd backend

# Create production environment
cp .env.example .env.production

# Update .env.production with production values
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:password@host:5432/plataforma_running
export GROQ_API_KEY=your_production_key
export JWT_SECRET=your_production_secret
export ALLOWED_ORIGINS=https://yourdomain.com
```

#### 1.2 Build Backend

```bash
# Install dependencies in production
python -m venv venv_prod
source venv_prod/bin/activate  # or venv_prod\Scripts\activate.ps1 on Windows

# Install requirements
pip install -r requirements.txt

# Run migrations (if using Alembic)
alembic upgrade head

# Test before deployment
python -m pytest tests/
```

#### 1.3 Start Backend Service

**Option A: Using Uvicorn directly**
```bash
uvicorn app.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4 \
  --log-level info
```

**Option B: Using Gunicorn with Uvicorn workers**
```bash
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

**Option C: Using systemd service (Linux)**
```ini
# /etc/systemd/system/plataforma-running-backend.service
[Unit]
Description=Plataforma Running Backend
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/opt/plataforma-running/backend
ExecStart=/opt/plataforma-running/backend/venv/bin/gunicorn \
    app.main:app \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable plataforma-running-backend
sudo systemctl start plataforma-running-backend
```

#### 1.4 Verify Backend

```bash
# Test API endpoint
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://api.yourdomain.com/api/v1/health

# Check logs
tail -f /var/log/plataforma-running-backend.log

# Monitor performance
systemctl status plataforma-running-backend
```

---

### Phase 2: Frontend Deployment (10-15 minutes)

#### 2.1 Build Frontend

```bash
# Navigate to frontend
cd frontend

# Create production build
npm run build

# Test build locally
npm run start

# Verify build output
ls -la .next/
```

#### 2.2 Deploy Frontend

**Option A: Vercel (Recommended for Next.js)**
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy to Vercel
vercel --prod \
  --env DATABASE_URL=$DATABASE_URL \
  --env NEXT_PUBLIC_API_URL=https://api.yourdomain.com
```

**Option B: Self-hosted with Nginx**
```bash
# Copy build to server
scp -r .next/ root@server:/var/www/plataforma-running/.next/
scp -r public/ root@server:/var/www/plataforma-running/public/
scp package.json root@server:/var/www/plataforma-running/
scp next.config.js root@server:/var/www/plataforma-running/

# Install dependencies on server
npm install --production

# Create systemd service for Next.js
```

**Option C: Docker containerization**
```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

COPY package.json .
RUN npm install --production

COPY .next ./.next
COPY public ./public
COPY next.config.js .

EXPOSE 3000

CMD ["npm", "start"]
```

Build and push:
```bash
docker build -t plataforma-running-frontend:1.0 .
docker push your-registry/plataforma-running-frontend:1.0
docker run -p 3000:3000 \
  -e NEXT_PUBLIC_API_URL=https://api.yourdomain.com \
  plataforma-running-frontend:1.0
```

#### 2.3 Verify Frontend

```bash
# Test frontend load
curl -I https://yourdomain.com

# Check static assets
curl -I https://yourdomain.com/_next/static/...

# Verify API connectivity
curl -H "Authorization: Bearer $JWT_TOKEN" \
  https://yourdomain.com/api/v1/training/weekly-plan
```

---

### Phase 3: Database Migration (5-10 minutes)

#### 3.1 Backup Current Database

```bash
# SQLite backup
cp runcoach.db runcoach.db.backup.$(date +%Y%m%d_%H%M%S)

# PostgreSQL backup
pg_dump plataforma_running > backup_$(date +%Y%m%d_%H%M%S).sql
```

#### 3.2 Run Migrations

```bash
# If using Alembic
alembic upgrade head

# Or manually with SQLAlchemy
python -c "from app.database import Base, engine; Base.metadata.create_all(engine)"
```

#### 3.3 Verify Data

```bash
# Test database connection
python -c "from app.database import SessionLocal; db = SessionLocal(); print('✅ Database connected')"

# Check migrations
alembic current
```

---

### Phase 4: Nginx Configuration (10 minutes)

#### 4.1 Create Nginx Config

```nginx
# /etc/nginx/sites-available/plataforma-running
upstream backend {
    server 127.0.0.1:8000;
}

upstream frontend {
    server 127.0.0.1:3000;
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# Backend API
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # CORS headers
    add_header Access-Control-Allow-Origin "https://yourdomain.com" always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
    add_header Access-Control-Allow-Headers "Content-Type, Authorization" always;

    if ($request_method = 'OPTIONS') {
        return 204;
    }
}

# Frontend
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static assets caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 4.2 Enable Nginx Config

```bash
# Test Nginx config
sudo nginx -t

# Enable site
sudo ln -s /etc/nginx/sites-available/plataforma-running /etc/nginx/sites-enabled/

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx
```

---

### Phase 5: SSL/TLS Setup (10-15 minutes)

#### 5.1 Get SSL Certificate

```bash
# Using Let's Encrypt with Certbot
sudo certbot certonly --nginx \
  -d yourdomain.com \
  -d api.yourdomain.com \
  -d www.yourdomain.com

# Auto-renew certificate
sudo certbot renew --dry-run
```

#### 5.2 Enable Auto-Renewal

```bash
# Enable certbot timer
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

# Check renewal status
sudo certbot renew --dry-run
```

---

### Phase 6: Monitoring & Logging (10 minutes)

#### 6.1 Configure Logging

```bash
# Backend logs
mkdir -p /var/log/plataforma-running
touch /var/log/plataforma-running/backend.log
touch /var/log/plataforma-running/access.log

# Logrotate config
# /etc/logrotate.d/plataforma-running
/var/log/plataforma-running/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        systemctl reload plataforma-running-backend > /dev/null 2>&1 || true
    endscript
}
```

#### 6.2 Setup Monitoring

```bash
# Install monitoring tools
apt-get install prometheus grafana-server

# Configure alerts for:
# - API response time > 1s
# - Error rate > 1%
# - CPU usage > 80%
# - Memory usage > 85%
# - Database connections > 80% of max
```

---

### Phase 7: Health Checks & Smoke Tests (5-10 minutes)

#### 7.1 Smoke Tests

```bash
#!/bin/bash
# smoke_tests.sh

echo "🧪 Running Smoke Tests..."

# Test backend health
echo -n "Backend health... "
if curl -s https://api.yourdomain.com/api/v1/health | grep -q "ok"; then
    echo "✅"
else
    echo "❌ FAILED"
    exit 1
fi

# Test frontend load
echo -n "Frontend load... "
if curl -s https://yourdomain.com | grep -q "html"; then
    echo "✅"
else
    echo "❌ FAILED"
    exit 1
fi

# Test API endpoints
echo -n "API race prediction... "
if curl -s -H "Authorization: Bearer $JWT_TOKEN" \
    "https://api.yourdomain.com/api/v1/race/predict-with-conditions?base_distance=10&base_time=45&target_distance=21.1" | grep -q "prediction"; then
    echo "✅"
else
    echo "❌ FAILED"
    exit 1
fi

echo "🎉 All smoke tests passed!"
```

#### 7.2 Production Verification

```bash
# Check service status
systemctl status plataforma-running-backend
systemctl status nginx

# Check logs for errors
tail -f /var/log/plataforma-running/backend.log

# Monitor resource usage
watch -n 1 'free -h && echo "---" && ps aux | grep uvicorn'
```

---

## 📊 Post-Deployment Checklist

### Day 1 (Launch)
- [ ] All services running
- [ ] Smoke tests passing
- [ ] No critical errors in logs
- [ ] API response times normal
- [ ] Frontend loads quickly
- [ ] Users can login
- [ ] All features accessible

### Day 3 (Monitoring)
- [ ] No escalating errors
- [ ] Performance stable
- [ ] User feedback positive
- [ ] Security logs clean
- [ ] Database performing well

### Week 1 (Stabilization)
- [ ] Load testing completed
- [ ] Backup tested
- [ ] Disaster recovery verified
- [ ] Team trained
- [ ] Documentation updated

---

## 🚨 Rollback Plan

### If Critical Issues Found

```bash
# Immediate rollback (within 30 minutes)

# Backend rollback
cd backend
git checkout previous-version
systemctl restart plataforma-running-backend

# Frontend rollback
cd frontend
npm run build  # Build previous version
systemctl restart plataforma-running-frontend

# Database rollback (if needed)
pg_restore backup_YYYYMMDD_HHMMSS.sql

# Notify team
echo "🚨 ROLLBACK IN PROGRESS - Check slack for updates"
```

---

## 📈 Performance Baselines

| Metric | Target | Monitor |
|--------|--------|---------|
| API Response Time | < 500ms | Every request |
| Page Load Time | < 2s | Every page view |
| CPU Usage | < 70% | Every 5 min |
| Memory Usage | < 80% | Every 5 min |
| Error Rate | < 0.1% | Continuous |
| Uptime | > 99.9% | Continuous |

---

## 🔐 Security Checklist

- [✅] HTTPS enabled
- [✅] SSL certificate valid
- [✅] CORS properly configured
- [✅] JWT validation working
- [✅] Rate limiting configured
- [✅] Security headers set
- [✅] Input validation enforced
- [✅] SQL injection prevented
- [✅] XSS protection enabled
- [✅] Regular backups scheduled

---

## 📞 Support Contacts

**On-Call:** [Contact info]  
**Escalation:** [Manager info]  
**Emergency:** [Emergency number]

---

## ✅ Deployment Completed

**Backend Status:** ✅ Running  
**Frontend Status:** ✅ Running  
**Database Status:** ✅ Connected  
**Monitoring Status:** ✅ Active  
**All Systems:** ✅ OPERATIONAL  

**Production Launch Time:** ____________  
**Deployment Lead Sign-off:** ____________  

---

*Deployment Guide v1.0 - November 2025*  
*Ready for Production 🚀*
