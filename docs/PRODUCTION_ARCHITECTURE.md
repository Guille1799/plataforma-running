# 🏗️ Production Architecture - Plataforma Running

**Version:** 1.0  
**Status:** Ready for Deployment  
**Last Updated:** November 17, 2025

---

## 📐 System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                        🌐 USERS                                  │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
        ┌───────────▼────────┐    ┌────────▼──────────┐
        │   FRONTEND (SPA)   │    │   MOBILE APP     │
        │   Next.js 16       │    │   React Native   │
        │   React 19         │    │   (Future)       │
        └────────┬───────────┘    └──────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
    │      ┌─────▼─────┐      │
    │      │  Nginx    │      │
    │      │ (SSL/TLS) │      │
    │      │  Reverse  │      │
    │      │  Proxy    │      │
    │      └─────┬─────┘      │
    │            │            │
    │  ┌─────────▼────────┐   │
    │  │   Load Balancer  │   │
    │  │   (Nginx/HAProxy)│   │
    │  └─────────┬────────┘   │
    │            │            │
    ├────────────┼────────────┤
    │            │            │
┌───▼──────┐ ┌──▼──────┐ ┌───▼──────┐
│ Backend  │ │ Backend │ │ Backend  │
│  API 1   │ │ API 2   │ │ API 3    │
│ Instance │ │Instance │ │Instance  │
│ Uvicorn  │ │Uvicorn  │ │Uvicorn   │
└───┬──────┘ └──┬──────┘ └───┬──────┘
    │           │            │
    └───────────┼────────────┘
                │
        ┌───────▼──────────┐
        │   Database       │
        │  PostgreSQL      │
        │  (Primary)       │
        │  Replication     │
        └────────┬─────────┘
                 │
        ┌────────▼──────────┐
        │   Backup DB       │
        │  PostgreSQL       │
        │  (Replica/Standby)│
        └───────────────────┘

        External Services:
        ┌──────────────┐
        │  Groq API    │
        │  (AI Coach)  │
        └──────────────┘
        
        ┌──────────────┐
        │  Garmin API  │
        │  (Workouts)  │
        └──────────────┘
```

---

## 🔐 Security Layers

### Layer 1: Network Security
```
┌─────────────────────────────────────┐
│  🔒 WAF (Web Application Firewall)  │
│     (Cloudflare/AWS WAF)            │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│  🔒 DDoS Protection & Rate Limiting │
│     (Cloudflare/AWS Shield)         │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│  🔒 TLS/SSL Encryption              │
│     (Let's Encrypt - Auto-Renewal)  │
└──────────────────┬──────────────────┘
                   │
┌──────────────────▼──────────────────┐
│  🔒 Nginx Reverse Proxy             │
│     (HTTPS → HTTP internal)         │
└─────────────────────────────────────┘
```

### Layer 2: Application Security
```
┌────────────────────────────────────────┐
│  🔒 Input Validation (Pydantic)        │
│     ├─ Schema validation               │
│     ├─ Type checking                   │
│     └─ Constraint validation           │
└──────────────────┬─────────────────────┘
                   │
┌──────────────────▼─────────────────────┐
│  🔒 Authentication (JWT)               │
│     ├─ Token generation                │
│     ├─ Token validation                │
│     └─ Token expiration                │
└──────────────────┬─────────────────────┘
                   │
┌──────────────────▼─────────────────────┐
│  🔒 Authorization (RBAC)               │
│     ├─ User roles                      │
│     ├─ Permission checking             │
│     └─ Resource access control         │
└──────────────────┬─────────────────────┘
                   │
┌──────────────────▼─────────────────────┐
│  🔒 SQL Injection Prevention           │
│     ├─ Parameterized queries           │
│     ├─ ORM usage (SQLAlchemy)          │
│     └─ Input escaping                  │
└──────────────────┬─────────────────────┘
                   │
┌──────────────────▼─────────────────────┐
│  🔒 XSS Protection                     │
│     ├─ Content-Security-Policy         │
│     ├─ HTML escaping                   │
│     └─ React auto-escaping             │
└─────────────────────────────────────────┘
```

### Layer 3: Data Security
```
┌──────────────────────────────────────┐
│  🔒 Database Encryption               │
│     ├─ TLS connections                │
│     ├─ Encrypted storage              │
│     └─ Password hashing (bcrypt)      │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│  🔒 Access Control                    │
│     ├─ Database user limits           │
│     ├─ Connection pooling             │
│     └─ Row-level security             │
└──────────────────┬───────────────────┘
                   │
┌──────────────────▼───────────────────┐
│  🔒 Backup & Recovery                 │
│     ├─ Daily encrypted backups        │
│     ├─ Point-in-time recovery         │
│     └─ Disaster recovery plan         │
└──────────────────────────────────────┘
```

---

## 📊 Infrastructure Components

### Frontend Infrastructure
| Component | Technology | Purpose | HA Strategy |
|-----------|-----------|---------|------------|
| CDN | CloudFlare/CloudFront | Content delivery, caching | Multi-region |
| Static hosting | Vercel/S3 | HTML, CSS, JS assets | Geo-redundant |
| Load balancer | Nginx | Request distribution | Active-active |

### Backend Infrastructure
| Component | Technology | Purpose | HA Strategy |
|-----------|-----------|---------|------------|
| API Servers | Uvicorn × N | Request processing | Load-balanced |
| Message Queue | Redis | Async jobs, caching | Sentinel HA |
| Cache Layer | Redis | Performance boost | Cluster mode |
| Database | PostgreSQL | Data persistence | Replication + Backup |

### Monitoring & Observability
| Component | Technology | Purpose |
|-----------|-----------|---------|
| Metrics | Prometheus | System metrics collection |
| Logs | ELK Stack | Centralized logging |
| Traces | Jaeger | Distributed tracing |
| Alerts | AlertManager | Incident notification |

---

## 🔄 Deployment Pipeline

### CI/CD Flow
```
┌──────────┐
│  Push    │  Developer commits code to git
│  Code    │
└────┬─────┘
     │
     ▼
┌──────────────┐
│  Webhook     │  GitHub/GitLab trigger
│  Trigger     │
└────┬─────────┘
     │
     ▼
┌──────────────────────┐
│  🔄 CI Pipeline      │
├──────────────────────┤
│  ✓ Checkout code     │
│  ✓ Run tests         │  (Backend + Frontend)
│  ✓ Lint code         │  (Python + TypeScript)
│  ✓ Build artifact    │  (Docker images)
│  ✓ Security scan     │  (SAST/Dependency check)
└────┬─────────────────┘
     │
     ├─ On failure ──────────▶ Notify developers
     │                        (Slack/Email)
     │
     ▼
┌──────────────────────┐
│  🔄 CD Pipeline      │
├──────────────────────┤
│  → Staging Deploy    │
│    ✓ Deploy to staging
│    ✓ Run e2e tests   │
│    ✓ Performance check
│    ✓ Manual approval │
└────┬─────────────────┘
     │
     ├─ On approval ────────▶ Auto-deploy
     │
     ▼
┌──────────────────────┐
│  🚀 Production Deploy│
├──────────────────────┤
│  → Blue-Green Deploy │
│    ✓ Health checks   │
│    ✓ Smoke tests     │
│    ✓ Traffic switch  │
│    ✓ Rollback ready  │
└──────────────────────┘
```

---

## 📈 Scaling Strategy

### Horizontal Scaling
```
Requests/sec Growth  →  Add Backend Instances
                          │
                    ┌─────┴─────┐
                    │           │
              ┌─────▼─────┐  ┌──▼──────┐
              │ Instance 1│  │Instance 2│
              │ Uvicorn   │  │ Uvicorn  │
              └───────────┘  └──────────┘
              
Load distribution via Nginx round-robin
Connection pooling via PgBouncer
```

### Vertical Scaling
```
High resource usage  →  Increase server capacity
                           │
                      ┌────┴─────┐
                      │           │
                   CPU ×2     Memory ×2
                   
Result: Better single-instance performance
```

### Database Scaling
```
Write-heavy workload  →  Read replicas + Sharding
                             │
                      ┌──────┴──────┐
                      │             │
                  Primary DB    Read-only Replicas
                  (Write)       (Read queries)
```

---

## 🎯 Performance Targets

### Backend Performance
```
Endpoint                    Target Response Time
─────────────────────────────────────────────
GET /api/v1/health          < 100ms
POST /api/v1/auth/login     < 300ms
POST /api/v1/race/predict   < 500ms (AI)
POST /api/v1/training/plan  < 800ms (AI)
GET /api/v1/workouts        < 200ms
```

### Frontend Performance
```
Metric                      Target Value
─────────────────────────────────────────
Page Load Time              < 2s
Time to Interactive (TTI)   < 3s
First Contentful Paint      < 1.5s
Largest Contentful Paint    < 2.5s
Cumulative Layout Shift     < 0.1
```

### Infrastructure Performance
```
Metric                      Target Value
─────────────────────────────────────────
API Availability            99.9% (SLA)
Database Availability       99.95%
DNS Resolution              < 50ms
SSL Handshake               < 100ms
Request Processing          < 200ms
```

---

## 🔄 High Availability Strategy

### Database HA
```
┌──────────────────────────────┐
│   Primary Database           │
│   (Read/Write)               │
│   PostgreSQL 15              │
└──────────────────────────────┘
           │ Streaming Replication
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐   ┌───▼────┐
│Replica1│   │Replica2│
│(Standby)   │(Standby)
│(Read)      │(Read)
└─────────┘   └─────────┘

Failover: Via pg_ctl promote
Recovery Time Objective (RTO): 5 minutes
Recovery Point Objective (RPO): < 1 minute
```

### Application Server HA
```
┌─────────────────────────┐
│   Health Checker        │
│   (Monitors instances)  │
└──────────────┬──────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐ ┌────▼───┐ ┌────▼───┐
│ App1 │ │  App2  │ │  App3  │
│ OK ✓ │ │ OK ✓   │ │ OK ✓   │
└──────┘ └────────┘ └────────┘

If App2 fails: Automatic removal from load balancer
If App2 recovers: Auto-readmission
```

### Cache Layer HA
```
┌─────────────────────────────┐
│   Redis Cluster             │
│   Master-Slave + Sentinel   │
└──────────────────────────────┘
           │ Automatic failover
           │
    ┌──────┴──────┐
    │             │
┌───▼────┐   ┌───▼────┐
│Master  │   │ Slave  │
│(Write) │   │ (Read) │
└────────┘   └────────┘
```

---

## 📊 Monitoring & Alerting

### Key Metrics to Monitor
```
Category              Metric                  Alert Threshold
────────────────────────────────────────────────────────────
Performance           API Response Time       > 1000ms
                      Error Rate              > 1%
                      Request/sec             > Capacity × 80%

Infrastructure        CPU Usage               > 80%
                      Memory Usage            > 85%
                      Disk Usage              > 90%
                      Network I/O             > 80% capacity

Database              Query Time              > 5s
                      Connection Pool         > 80% used
                      Replication Lag         > 1s
                      Database Size           Growth > 10%/day

Business              User Signups            < Expected × 50%
                      Failed Authentications  > 10/min
                      API Errors              > Expected × 2x
```

### Alert Channels
```
Severity    Channel              Escalation Path
────────────────────────────────────────────────
Critical    PagerDuty           → On-call → Manager
            SMS                 → Page team immediately
            
High        Slack #alerts       → Team notified
            Email notifications → Check within 15 min
            
Medium      Slack #monitoring   → Monitor
            Dashboard alert      → Review daily
            
Low         Log aggregation     → Review during standup
```

---

## 🔒 Disaster Recovery Plan

### RPO & RTO Targets
```
Scenario                    RPO          RTO
──────────────────────────────────────────────
Database Failure            5 minutes    15 minutes
Single Server Down          N/A          < 30 seconds
Entire Datacenter Down      1 hour       2 hours
Corrupted Data              N/A          4 hours
```

### Backup Strategy
```
Frequency       Type            Retention      Storage
──────────────────────────────────────────────────────
Hourly          Incremental     7 days         Local + S3
Daily           Full            30 days        S3
Weekly          Full            12 weeks       S3 Glacier
Monthly         Full            12 months      S3 Glacier
```

### Failover Procedures
```
1. Detect failure (monitoring alert)
   ↓
2. Automatic response:
   ├─ Remove failed node from load balancer
   ├─ Promote standby database
   ├─ Notify ops team
   └─ Start health checks
   ↓
3. Manual verification:
   ├─ Check services responding
   ├─ Monitor error rates
   ├─ Verify data consistency
   └─ Document incident
   ↓
4. Recovery (when original node ready):
   ├─ Re-sync data
   ├─ Health check pass
   ├─ Re-add to load balancer
   └─ Resume normal operation
```

---

## 📋 Compliance & Security Checklist

### Data Protection
- [✅] Encryption at rest (AES-256)
- [✅] Encryption in transit (TLS 1.3)
- [✅] Password hashing (bcrypt)
- [✅] Secure key management (AWS KMS/Vault)
- [✅] Data retention policies
- [✅] GDPR compliance mechanisms

### Access Control
- [✅] Multi-factor authentication (future)
- [✅] Role-based access control (RBAC)
- [✅] Audit logging for all access
- [✅] VPN access to infrastructure
- [✅] API key rotation policy
- [✅] Principle of least privilege

### Incident Management
- [✅] Incident response plan
- [✅] Change management process
- [✅] Rollback procedures
- [✅] Disaster recovery testing (quarterly)
- [✅] Post-incident reviews
- [✅] Metrics tracking

---

## 🚀 Deployment Checklist

Before going live:

- [ ] All services healthy
- [ ] Database replicas in sync
- [ ] SSL certificates valid
- [ ] DNS properly configured
- [ ] Load balancer tested
- [ ] Backup verified
- [ ] Monitoring active
- [ ] Alerting configured
- [ ] Runbooks created
- [ ] Team trained
- [ ] Rollback plan ready
- [ ] Documentation current
- [ ] Stakeholders notified

---

## 📞 Architecture Support

**Infrastructure Lead:** [Name]  
**Database Admin:** [Name]  
**DevOps Engineer:** [Name]  
**On-Call Schedule:** [Link to PagerDuty]

---

*Production Architecture v1.0 - Ready for Deployment 🚀*
