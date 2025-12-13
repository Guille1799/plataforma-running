# 🎯 PHASE 3 & 4 ROADMAP

**Project**: RunCoach AI  
**Date**: December 13, 2025  
**Status**: Planning Phase 3 Implementation

---

## ⚡ PHASE 3: ADVANCED FEATURES (2-3 Weeks)

### FASE 3a: Email Notifications System (3-4 days)

**Goal**: Notify users about important events (new plans, coaching insights, overtraining warnings)

**Backend Tasks**:
1. Setup email service (SendGrid or similar)
2. Create notification models in DB:
   - `notifications` table (id, user_id, type, content, read, created_at)
   - `notification_templates` table (template_name, subject, body)
3. Implement notification triggers:
   - New training plan created
   - Coaching analysis ready
   - Overtraining detected
   - Weekly summary report
4. Create email template system with HTML rendering
5. API endpoints:
   - POST `/api/v1/notifications/preferences` - user preferences
   - GET `/api/v1/notifications` - get user notifications
   - PATCH `/api/v1/notifications/{id}/read` - mark as read
   - DELETE `/api/v1/notifications/{id}`

**Frontend Tasks**:
1. Notification center page (`/dashboard/notifications`)
2. Bell icon in navbar with unread count
3. Notification settings in profile
4. Email preference toggles:
   - Daily summary
   - Weekly analysis
   - Alerts only (critical)
   - Disabled

**Features**:
- ✅ Real-time notification badge on bell icon
- ✅ Notification history with filtering
- ✅ Email scheduling (choose time of day)
- ✅ Do-not-disturb hours
- ✅ Notification grouping by type

---

### FASE 3b: Redis Caching Implementation (3-4 days)

**Goal**: Improve performance by caching expensive computations

**Backend Setup**:
```bash
# Add Redis to docker-compose
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
  volumes:
    - redis_data:/data

# Add to requirements.txt
redis>=5.0.0
```

**Cache Strategy**:
1. **User Computations** (30 min TTL):
   - Training plan generation (IA takes 2-5 seconds)
   - HR zone calculations
   - Overtraining risk assessment
   - Readiness score

2. **Aggregations** (1 hour TTL):
   - Weekly/monthly statistics
   - Trend calculations
   - Leader board rankings

3. **API Responses** (5 min TTL):
   - GET `/api/v1/workouts` (list)
   - GET `/api/v1/health-metrics`
   - GET `/api/v1/dashboard/summary`

4. **Device Sync** (2 hour TTL):
   - Garmin availability status
   - Last sync timestamp

**Implementation**:
```python
# backend/app/services/cache_service.py
from redis import Redis
from typing import Any

class CacheService:
    def __init__(self, redis_client: Redis):
        self.client = redis_client
    
    def get(self, key: str) -> Any:
        """Get value from cache"""
        value = self.client.get(key)
        return json.loads(value) if value else None
    
    def set(self, key: str, value: Any, ttl_seconds: int = 3600):
        """Set value in cache with TTL"""
        self.client.setex(key, ttl_seconds, json.dumps(value))
    
    def invalidate(self, key: str):
        """Invalidate cache key"""
        self.client.delete(key)
    
    def invalidate_pattern(self, pattern: str):
        """Invalidate all keys matching pattern"""
        keys = self.client.keys(pattern)
        if keys:
            self.client.delete(*keys)
```

**Benefits**:
- ✅ 90% faster API responses for cached data
- ✅ Reduced database load
- ✅ Lower Groq API calls (plan generation cached)
- ✅ Better user experience

---

### FASE 3c: WebSocket Streaming (4-5 days)

**Goal**: Real-time coaching responses (instead of waiting for full response)

**Current State** (Using HTTP Polling):
```
User: "¿Cómo mejorar mi ritmo?"
  ↓
Frontend: Wait 2-5 seconds for full response
  ↓
Backend: Call Groq API, wait for response
  ↓
Frontend: Display entire response at once
```

**Target State** (Using WebSocket Streaming):
```
User: "¿Cómo mejorar mi ritmo?"
  ↓
Frontend: Connect WebSocket, start streaming
  ↓
Backend: Call Groq API with streaming
  ↓
Frontend: Display response word-by-word in real-time
User sees: "Para mejorar... tu ritmo... debes..." (live typing effect)
```

**WebSocket Implementation**:
```python
# backend/app/routers/coach_ws.py
from fastapi import WebSocket

@router.websocket("/ws/coach/{user_id}")
async def websocket_coach(websocket: WebSocket, user_id: int):
    await websocket.accept()
    
    try:
        while True:
            # Receive user message
            data = await websocket.receive_json()
            user_message = data.get("message")
            
            # Stream IA response
            async for chunk in stream_groq_response(user_message):
                await websocket.send_text(chunk)
            
            # Send completion signal
            await websocket.send_json({"type": "complete"})
    
    except Exception as e:
        await websocket.close(code=1000)
```

**Frontend Integration**:
```typescript
// app/components/coach-chat-v2.tsx (with streaming)

const handleStreamingMessage = async (message: string) => {
  const ws = new WebSocket(`ws://localhost:3000/ws/coach/${user.id}`);
  
  ws.onopen = () => {
    ws.send(JSON.stringify({ message }));
  };
  
  ws.onmessage = (event) => {
    if (event.data === '{"type":"complete"}') {
      ws.close();
    } else {
      // Append to message in real-time
      setStreamingResponse(prev => prev + event.data);
    }
  };
};
```

**Benefits**:
- ✅ Perceived performance improvement (response appears instantly)
- ✅ Better UX with live typing effect
- ✅ Lower latency perception
- ✅ More engaging experience

---

## 📱 PHASE 4: MOBILE & MONETIZATION (2-4 Weeks)

### FASE 4a: React Native Mobile App (10-15 days)

**Setup**:
```bash
npx create-expo-app runcoach-mobile
cd runcoach-mobile
npm install @react-navigation/native @react-navigation/stack
npm install axios date-fns
```

**Core Features**:
1. **Auth Flow**:
   - Login/Register
   - Token storage (SecureStore)
   - Auto-login if token valid

2. **Dashboard Screen**:
   - Recent workouts list
   - Summary stats cards
   - Quick plan view
   - Sync button for Garmin

3. **Workouts List Screen**:
   - Infinite scroll
   - Filter by sport type
   - Quick details modal
   - Share functionality

4. **Training Plan Screen**:
   - Weekly breakdown
   - Day details modal
   - Mark completed
   - Coaching tips per workout

5. **Coach Chat Screen**:
   - Chat interface
   - WebSocket for streaming
   - Voice input (optional)
   - Message history

6. **Settings Screen**:
   - Profile editing
   - Device management
   - Notification preferences
   - Logout

**Push Notifications**:
- Expo Push Notifications
- Daily coaching reminders
- New plan ready alerts
- Overtraining warnings

**Native Features**:
- Bluetooth for wearable data
- Background sync on app open
- Offline mode (cache recent data)
- App icon + splash screen

---

### FASE 4b: Monetization Model (3-5 days)

**Tier Structure**:
```
FREE TIER (Current):
  ✅ 5 AI coach messages/month
  ✅ View workouts (max 100)
  ✅ Basic analytics
  ✅ 1 training plan/month
  ✅ Ads on dashboard

PRO TIER ($4.99/month):
  ✅ Unlimited AI coach messages
  ✅ Unlimited training plans
  ✅ Advanced analytics (heatmaps, trends)
  ✅ Export to PDF/CSV
  ✅ No ads
  ✅ Email summaries

ELITE TIER ($9.99/month):
  ✅ Everything in Pro
  ✅ Personal coaching (group video calls, monthly)
  ✅ Nutrition recommendations (AI-based)
  ✅ Recovery protocols (AI-generated)
  ✅ Priority support
  ✅ Custom training periodization

ENTERPRISE ($99/month):
  ✅ Everything in Elite
  ✅ Team management (coach + 10 athletes)
  ✅ API access
  ✅ Custom integrations
  ✅ Dedicated support
```

**Implementation**:
1. **Payment Processing**:
   - Stripe integration
   - In-app purchases (mobile)
   - Subscription management
   - Invoice generation

2. **Feature Gating**:
   ```python
   @require_subscription_tier("pro")
   def export_workout(workout_id: int):
       # Only Pro+ users
   
   @rate_limit(messages=5, period="month", tier="free")
   def coach_message(user_id: int):
       # Free: 5/month, Pro: unlimited
   ```

3. **Analytics**:
   - Conversion tracking
   - Churn analysis
   - LTV by tier
   - Feature usage by tier

---

## 🚀 Implementation Priority

```
IMMEDIATE (Next 2 weeks):
  1. FASE 3a - Email notifications (high impact, medium effort)
  2. FASE 3b - Redis caching (high impact, medium effort)

NEXT (2-4 weeks):
  3. FASE 3c - WebSocket streaming (medium impact, high effort)
  4. FASE 4a - Mobile app (high impact, high effort)

LATER (4-8 weeks):
  5. FASE 4b - Monetization (high impact, medium effort)
  6. FASE 4c - Marketing & growth (lower priority)
```

---

## 📊 Success Metrics

**By end of Phase 3**:
- ✅ Email notifications working (test with own email)
- ✅ API response times < 100ms (cached)
- ✅ WebSocket connection stable (no disconnects)
- ✅ Coach chat streaming live

**By end of Phase 4**:
- ✅ Mobile app working on iOS + Android
- ✅ Push notifications delivered
- ✅ Subscription tiers working
- ✅ Payment processing tested

---

## 💰 Estimated Costs

**Additional Services**:
- SendGrid (emails): $20/month (5k emails/month)
- Stripe (payments): 2.9% + $0.30 per transaction
- Redis (caching): Included in Render free tier OR $12/month for managed
- Firebase (push notifications): FREE

**Total Additional**: ~$30-40/month (still <$100 total)

---

## 🎯 Which Phase First?

**RECOMMENDATION**: Start with **FASE 3a (Notifications)** because:
1. ✅ Highest ROI (improves user engagement immediately)
2. ✅ Moderate complexity (good learning opportunity)
3. ✅ Foundation for Phase 4 monetization
4. ✅ 3-4 days to complete
5. ✅ Visible user-facing feature

**Then FASE 3b (Caching)** because:
1. ✅ Backend performance boost
2. ✅ Reduces Groq API usage costs
3. ✅ Better user experience
4. ✅ Foundation for Phase 4 scale

---

**Ready to start? Let me know which Phase to begin!**
