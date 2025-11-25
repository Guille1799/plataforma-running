# 🚀 QUICK START VERIFICATION

## Pre-Requisitos
- ✅ Backend running: `127.0.0.1:8000`
- ✅ Frontend running: `localhost:3000`
- ✅ Logged in: `test@example.com` / `password123`

---

## 🧪 Test 1: Race Search Fix (Bug #1)

**What**: Buscador mostraba solo Málaga aunque backend devuelve 30+ resultados

**How to Verify**:
1. Go: http://localhost:3000/dashboard/training-plans
2. Click: "Nueva Plan de Entrenamiento"
3. In Paso 1, type in search box: `marat`
4. **EXPECTED**: See list like:
   - Marató de Barcelona (Mar 2025)
   - Maratón de Madrid (Apr 2025)
   - Maratón de Málaga (Nov 2025)
   - Maratón de Valencia (Nov 2025)
   - Media Maratón de... (multiple)
   - Half Marathon... (multiple)
   - **TOTAL: 30+ results**

5. **VERIFY IN DEVTOOLS**:
   - Press F12
   - Go to Network tab
   - Search "marat" again
   - Find request: `search?q=marat&_t=12345...`
   - Check Response: `{success: true, count: 30, races: [...]}`

**If works**: ✅ Click in Málaga to select

---

## 🧪 Test 2: Paso 6 Duration Loading (Bug #2)

**What**: Duration options didn't load in Paso 6

**How to Verify**:
1. From Paso 1, select: "No, I want to train in general"
2. Paso 2: Select `Marathon` + `Speed`
3. Paso 3: Select `4-5 days per week`
4. Paso 4: Select `Saturday` for long run
5. Paso 5: Select `Yes, gym` + `3 sports`
6. **Paso 6**: Should see 4 duration options:
   - 4 semanas
   - 8 semanas
   - 12 semanas (⭐ Recommended)
   - 16 semanas

7. **VERIFY IN CONSOLE**:
   - Press F12 → Console
   - Should see: `📋 Loading duration options for goal: marathon`

**If works**: ✅ Select 12 semanas

---

## 🧪 Test 3: Paso 2 Validation (Bug #3)

**What**: Could advance without selecting priority

**How to Verify**:
1. Paso 2 screen
2. **Step A**: Don't select anything
   - Button should be **GRAY** ← Can't click
3. **Step B**: Select only "Marathon"
   - Button should still be **GRAY** ← Can't click (missing priority)
4. **Step C**: Deselect "Marathon", select only "Speed" 
   - Button should still be **GRAY** ← Can't click (missing goal)
5. **Step D**: Select BOTH "Marathon" + "Speed"
   - Button should turn **BLUE** ← Now clickeable! ✅

**Expected visual**: 
- Gray button with text like "Siguiente →" (unclickable)
- Blue button when valid (clickable)

---

## ✅ Quick Validation Checklist

### Race Search
- [ ] Search "marat" returns 30+ results
- [ ] Results include Barcelona, Madrid, Málaga, Valencia
- [ ] DevTools shows unique `_t` parameter per search
- [ ] No caching (each search gets fresh results)

### Duration Loading
- [ ] Paso 6 without race shows duration options
- [ ] 4 options visible: 4, 8, 12, 16 semanas
- [ ] Console shows "📋 Loading duration options..."
- [ ] Can select duration
- [ ] Button enables when selected

### Validation
- [ ] Paso 2 button GRAY until both selected
- [ ] All "Siguiente" buttons respect validation
- [ ] "Crear Plan" button only enabled when ready
- [ ] Can't advance with incomplete selections

### Full Flow
- [ ] Create plan with race: Works ✅
- [ ] Create plan without race: Works ✅
- [ ] Form saves successfully
- [ ] Plan appears in dashboard

---

## 🎯 Visual Indicators

### ✅ Green/Blue States
- Race: 30 results showing
- Duration: 4 options visible
- Button: Blue = ENABLED (clickable)

### 🔴 Gray/Disabled States
- Button: Gray = DISABLED (can't click)
- Cannot advance without valid selections
- User gets visual feedback

---

## 🐛 If Something is Wrong

1. **Hard refresh**: `Ctrl+Shift+R`
2. **Check backend**: `http://127.0.0.1:8000/docs`
3. **Check console**: `F12 → Console tab`
4. **Check network**: `F12 → Network tab`
5. **Verify login**: Logged in as `test@example.com`
6. **Check file**: `frontend/app/(dashboard)/dashboard/training-plan-form-v2.tsx`
   - Should have `isStepValid()` function
   - Should have cache-busting in `api-client.ts`

---

## 📝 What Changed

### File 1: `lib/api-client.ts`
- Added `_t: Date.now()` to searchRaces params
- Added Cache-Control headers
- Result: Fresh results every search

### File 2: `training-plan-form-v2.tsx`
- Added `isStepValid()` function
- Moved useEffect to top level
- Added `disabled={!isStepValid()}` to all buttons
- Result: Proper validation & duration loading

---

## 🚀 Go Test!

1. Open browser to http://localhost:3000/dashboard/training-plans
2. Click "Nueva Plan de Entrenamiento"
3. Run through Test 1, 2, 3 above
4. Report results!
