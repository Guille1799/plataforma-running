// Health Dashboard Page
'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Activity, Heart, Moon, Battery, TrendingUp, TrendingDown, Calendar, ArrowRight } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { formatDate } from '@/lib/formatters'
import { useRouter } from 'next/navigation'
import { DailyCheckIn } from '@/components/DailyCheckIn'
import { HRVTrend } from '@/components/HRVTrend'
import { SleepQuality } from '@/components/SleepQuality'
import { StressTrend } from '@/components/StressTrend'
import { SyncStatus } from '@/components/SyncStatus'
import type { HealthMetric } from '@/lib/types'

export default function HealthPage() {
  const router = useRouter()

  // Fetch today's health metrics
  const { data: todayHealth, isLoading: loadingToday } = useQuery({
    queryKey: ['health', 'today'],
    queryFn: () => apiClient.getHealthToday()
  })

  // Fetch readiness score
  const { data: readiness, isLoading: loadingReadiness } = useQuery({
    queryKey: ['health', 'readiness'],
    queryFn: () => apiClient.getReadinessScore()
  })

  // Calculate readiness from health metrics if API doesn't return it
  const calculatedReadiness = todayHealth ? {
    readiness_score: calculateReadinessFromMetrics(todayHealth),
    confidence: 'medium',
    factors: getReadinessFactors(todayHealth),
    recommendation: getReadinessRecommendation(calculateReadinessFromMetrics(todayHealth))
  } : null

  const effectiveReadiness = readiness?.readiness_score ? readiness : calculatedReadiness

  // Fetch AI recommendation
  const { data: recommendation, isLoading: loadingRec } = useQuery({
    queryKey: ['health', 'recommendation'],
    queryFn: () => apiClient.getWorkoutRecommendation()
  })

  // Fetch history for trends
  const { data: history } = useQuery({
    queryKey: ['health', 'history'],
    queryFn: async () => {
      const response = await apiClient.getHealthHistory(7);
      return { metrics: response as HealthMetric[] };
    }
  })

  if (loadingToday || loadingReadiness) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    )
  }

  const getReadinessColor = (score: number) => {
    if (score >= 75) return 'text-green-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  const getReadinessStatus = (score: number) => {
    if (score >= 75) return { text: 'Excelente', variant: 'default' as const }
    if (score >= 60) return { text: 'Moderado', variant: 'secondary' as const }
    return { text: 'Recuperación', variant: 'outline' as const }
  }

  // Helper functions for readiness calculation
  function calculateReadinessFromMetrics(health: any): number {
    let score = 0
    let totalWeight = 0

    // Body battery - only use if > 5 (filter invalid values)
    if (health.body_battery !== null && health.body_battery !== undefined && health.body_battery > 5) {
      score += health.body_battery * 0.4
      totalWeight += 0.4
    }

    // Sleep score or duration
    if (health.sleep_score !== null && health.sleep_score !== undefined) {
      score += health.sleep_score * 0.35
      totalWeight += 0.35
    } else if (health.sleep_duration_minutes) {
      const sleepHours = health.sleep_duration_minutes / 60
      const sleepScore = sleepHours >= 7 ? Math.min(100, sleepHours * 12) : sleepHours * 10
      score += sleepScore * 0.35
      totalWeight += 0.35
    }

    // HRV - with or without baseline
    if (health.hrv_ms) {
      let hrvScore = 50 // default
      if (health.hrv_baseline_ms) {
        const hrvRatio = health.hrv_ms / health.hrv_baseline_ms
        hrvScore = Math.min(100, Math.max(0, 50 + (hrvRatio - 1) * 50))
      } else {
        // Without baseline, use general ranges: 20-80ms
        // <20=poor, 20-40=low, 40-60=good, >60=excellent
        if (health.hrv_ms < 20) hrvScore = 30
        else if (health.hrv_ms < 40) hrvScore = 60
        else if (health.hrv_ms < 60) hrvScore = 80
        else hrvScore = 95
      }
      score += hrvScore * 0.15
      totalWeight += 0.15
    }

    // Stress level (inverse - lower is better)
    if (health.stress_level !== null && health.stress_level !== undefined) {
      const stressScore = 100 - health.stress_level
      score += stressScore * 0.1
      totalWeight += 0.1
    }

    // If we have no factors at all, return 0
    if (totalWeight === 0) return 0

    // Normalize by total weight
    return Math.round(score / totalWeight)
  }

  function getReadinessFactors(health: any) {
    const factors = []

    if (health.body_battery !== null && health.body_battery !== undefined && health.body_battery > 5) {
      factors.push({ name: 'Body Battery', score: health.body_battery })
    }

    if (health.sleep_score) {
      factors.push({ name: 'Sleep Quality', score: health.sleep_score })
    } else if (health.sleep_duration_minutes) {
      const sleepHours = health.sleep_duration_minutes / 60
      const sleepScore = Math.min(100, sleepHours >= 7 ? sleepHours * 12 : sleepHours * 10)
      factors.push({ name: 'Sleep', score: Math.round(sleepScore) })
    }

    if (health.hrv_ms) {
      let hrvScore = 50
      if (health.hrv_baseline_ms) {
        const ratio = health.hrv_ms / health.hrv_baseline_ms
        hrvScore = Math.min(100, 50 + (ratio - 1) * 50)
      } else {
        // Without baseline, use general ranges
        if (health.hrv_ms < 20) hrvScore = 30
        else if (health.hrv_ms < 40) hrvScore = 60
        else if (health.hrv_ms < 60) hrvScore = 80
        else hrvScore = 95
      }
      factors.push({ name: 'HRV', score: Math.round(hrvScore) })
    }

    if (health.stress_level !== null && health.stress_level !== undefined) {
      const stressScore = 100 - health.stress_level
      factors.push({ name: 'Estrés', score: Math.round(stressScore) })
    }

    return factors
  }

  function getReadinessRecommendation(score: number): string {
    if (score >= 75) return '¡Listo para entrenar duro! Tu cuerpo está recuperado.'
    if (score >= 60) return 'Entrenamiento moderado recomendado. Escucha a tu cuerpo.'
    return 'Prioriza recuperación. Entrenamiento suave o descanso.'
  }

  function formatSleepDate(dateStr: string): string {
    const date = new Date(dateStr)
    const prevDate = new Date(date)
    prevDate.setDate(prevDate.getDate() - 1)
    const prevDay = prevDate.getDate()
    const currDay = date.getDate()
    const prevMonth = prevDate.toLocaleDateString('es-ES', { month: 'short' })
    const currMonth = date.toLocaleDateString('es-ES', { month: 'short' })

    if (prevMonth === currMonth) {
      return `${prevDay}-${currDay} ${currMonth}`
    }
    return `${prevDay} ${prevMonth} - ${currDay} ${currMonth}`
  }

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-7xl">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-white">Health Metrics</h1>
          <p className="text-slate-400">
            Tu estado de recuperación y recomendaciones personalizadas
          </p>
        </div>
        <div className="w-64">
          <SyncStatus />
        </div>
      </div>

      {/* Main Grid: Compact 4-column layout */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {/* Readiness Score - Compact Card */}
        <Card className="border-slate-700 bg-slate-800/50">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm text-white flex items-center justify-between">
              <span>Readiness</span>
              {effectiveReadiness?.readiness_score && (
                <Badge
                  variant={getReadinessStatus(effectiveReadiness.readiness_score).variant}
                  className="text-xs h-5"
                >
                  {getReadinessStatus(effectiveReadiness.readiness_score).text}
                </Badge>
              )}
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            {/* Compact Circular Progress */}
            <div className="flex justify-center">
              <div className="relative w-20 h-20">
                <svg className="w-full h-full" viewBox="0 0 100 100">
                  <circle
                    className="text-slate-700 stroke-current"
                    strokeWidth="10"
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                  />
                  <circle
                    className={`${getReadinessColor(effectiveReadiness?.readiness_score || 0)} stroke-current`}
                    strokeWidth="10"
                    strokeLinecap="round"
                    cx="50"
                    cy="50"
                    r="40"
                    fill="transparent"
                    strokeDasharray={`${((effectiveReadiness?.readiness_score || 0) / 100) * 251.2} 251.2`}
                    transform="rotate(-90 50 50)"
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className={`text-xl font-bold ${getReadinessColor(effectiveReadiness?.readiness_score || 0)}`}>
                    {effectiveReadiness?.readiness_score || 0}
                  </span>
                </div>
              </div>
            </div>

            {/* Mini Factors */}
            {effectiveReadiness?.factors && effectiveReadiness.factors.length > 0 && (
              <div className="space-y-1.5">
                {effectiveReadiness.factors.slice(0, 3).map((factor: any, idx: number) => (
                  <div key={idx} className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">{factor.name}</span>
                    <span className="font-medium text-white">{factor.score}</span>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Compact Health Metrics - Remaining 3 columns in first row */}
        {todayHealth?.hrv_ms && (
          <div onClick={() => router.push('/health/vfc')} className="cursor-pointer hover:scale-105 transition-transform">
            <CompactMetricCard
              icon={<Heart className="h-4 w-4" />}
              label="VFC"
              value={todayHealth.hrv_ms}
              unit="ms"
              baseline={todayHealth.hrv_baseline_ms}
              clickable={true}
            />
          </div>
        )}

        {todayHealth?.resting_hr_bpm && (
          <div onClick={() => router.push('/health/heart-rate')} className="cursor-pointer hover:scale-105 transition-transform">
            <CompactMetricCard
              icon={<Activity className="h-4 w-4" />}
              label="Resting HR"
              value={todayHealth.resting_hr_bpm}
              unit="bpm"
              baseline={todayHealth.resting_hr_baseline_bpm}
              clickable={true}
            />
          </div>
        )}

        {todayHealth?.sleep_duration_minutes && (
          <div onClick={() => router.push('/health/sleep')} className="cursor-pointer hover:scale-105 transition-transform">
            <CompactMetricCard
              icon={<Moon className="h-4 w-4" />}
              label={todayHealth?.date ? formatSleepDate(todayHealth.date) : "Sleep"}
              value={+(todayHealth.sleep_duration_minutes / 60).toFixed(1)}
              unit="hrs"
              score={todayHealth.sleep_score}
              clickable={true}
            />
          </div>
        )}

        {/* Second row if needed */}
        {todayHealth?.body_battery !== null && todayHealth?.body_battery !== undefined && todayHealth.body_battery > 5 && (
          <div onClick={() => router.push('/health/body-battery')} className="cursor-pointer hover:scale-105 transition-transform">
            <CompactMetricCard
              icon={<Battery className="h-4 w-4" />}
              label="Body Battery"
              value={todayHealth.body_battery}
              unit="/100"
              clickable={true}
            />
          </div>
        )}

        {todayHealth?.steps && todayHealth.steps > 100 && (
          <div onClick={() => router.push('/health/activity')} className="cursor-pointer hover:scale-105 transition-transform">
            <CompactMetricCard
              icon={<Activity className="h-4 w-4" />}
              label="Steps"
              value={todayHealth.steps > 1000 ? +(todayHealth.steps / 1000).toFixed(1) + 'k' : todayHealth.steps}
              unit=""
              clickable={true}
            />
          </div>
        )}

        {todayHealth?.stress_level !== null && todayHealth?.stress_level !== undefined && (
          <div onClick={() => router.push('/health/stress')} className="cursor-pointer hover:scale-105 transition-transform">
            <CompactMetricCard
              icon={<TrendingUp className="h-4 w-4" />}
              label="Stress"
              value={todayHealth.stress_level}
              unit="/100"
              isStress={true}
              clickable={true}
            />
          </div>
        )}

        {/* Row 2: Additional metrics always visible */}
        {todayHealth?.vo2_max && todayHealth.vo2_max > 0 && (
          <CompactMetricCard
            icon={<Activity className="h-4 w-4 text-purple-400" />}
            label="VO₂ Max"
            value={todayHealth.vo2_max}
            unit=""
          />
        )}

        {todayHealth?.max_hr_bpm && todayHealth.max_hr_bpm > 0 && (
          <CompactMetricCard
            icon={<Heart className="h-4 w-4 text-red-400" />}
            label="Max HR"
            value={todayHealth.max_hr_bpm}
            unit="bpm"
          />
        )}

        {todayHealth?.avg_hr_bpm && todayHealth.avg_hr_bpm > 0 && (
          <CompactMetricCard
            icon={<Heart className="h-4 w-4 text-pink-400" />}
            label="Avg HR"
            value={todayHealth.avg_hr_bpm}
            unit="bpm"
          />
        )}

        {todayHealth?.calories_burned && todayHealth.calories_burned > 100 && (
          <CompactMetricCard
            icon={<Activity className="h-4 w-4 text-orange-400" />}
            label="Calories"
            value={todayHealth.calories_burned >= 1000 ? `${(todayHealth.calories_burned / 1000).toFixed(1)}k` : todayHealth.calories_burned}
            unit="kcal"
          />
        )}

        {todayHealth?.active_minutes && todayHealth.active_minutes > 0 && (
          <CompactMetricCard
            icon={<Activity className="h-4 w-4 text-green-400" />}
            label="Active"
            value={todayHealth.active_minutes}
            unit="min"
          />
        )}

        {todayHealth?.floors_climbed && todayHealth.floors_climbed > 0 && (
          <CompactMetricCard
            icon={<TrendingUp className="h-4 w-4 text-cyan-400" />}
            label="Floors"
            value={todayHealth.floors_climbed}
            unit="pisos"
          />
        )}

        {todayHealth?.respiratory_rate && todayHealth.respiratory_rate > 0 && (
          <CompactMetricCard
            icon={<Activity className="h-4 w-4 text-blue-400" />}
            label="Resp Rate"
            value={todayHealth.respiratory_rate}
            unit="br/min"
          />
        )}

        {todayHealth?.spo2_percent && todayHealth.spo2_percent > 90 && (
          <CompactMetricCard
            icon={<Activity className="h-4 w-4 text-indigo-400" />}
            label="SpO₂"
            value={todayHealth.spo2_percent}
            unit="%"
          />
        )}

        {todayHealth?.deep_sleep_minutes && todayHealth.deep_sleep_minutes > 0 && (
          <CompactMetricCard
            icon={<Moon className="h-4 w-4 text-purple-400" />}
            label="Deep Sleep"
            value={+(todayHealth.deep_sleep_minutes / 60).toFixed(1)}
            unit="hrs"
          />
        )}

        {todayHealth?.rem_sleep_minutes && todayHealth.rem_sleep_minutes > 0 && (
          <CompactMetricCard
            icon={<Moon className="h-4 w-4 text-blue-400" />}
            label="REM Sleep"
            value={+(todayHealth.rem_sleep_minutes / 60).toFixed(1)}
            unit="hrs"
          />
        )}

        {todayHealth?.floors_climbed && todayHealth.floors_climbed > 0 && (
          <CompactMetricCard
            icon={<TrendingUp className="h-4 w-4 text-cyan-400" />}
            label="Floors"
            value={todayHealth.floors_climbed}
            unit="pisos"
          />
        )}
      </div>

      <SleepQuality metrics={history.metrics} days={7} compact={true} />
      <StressTrend metrics={history.metrics} days={7} />

      {/* AI Recommendation - Full width if exists */}
      {!loadingRec && recommendation?.ai_recommendation && (
        <Card className="border-slate-700 bg-slate-800/50">
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center gap-2 text-lg text-white">
              <TrendingUp className="h-5 w-5 text-blue-400" />
              Recomendación del Coach IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-sm text-slate-300 whitespace-pre-wrap leading-relaxed">
              {recommendation.ai_recommendation}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Daily Check-In - Moved to bottom, more compact */}
      <DailyCheckIn />

      {/* Data Source - Compact */}
      {todayHealth && (
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <Calendar className="h-3 w-3" />
          <span>Fuente:</span>
          <Badge variant="outline" className="text-xs py-0">
            {todayHealth.source === 'garmin' ? 'Garmin' : todayHealth.source}
          </Badge>
        </div>
      )}
    </div>
  )
}

// ============================================================
// COMPACT METRIC CARD (NEW - Efficient Space Usage)
// ============================================================
function CompactMetricCard({ icon, label, value, unit, baseline, score, isStress, clickable }: {
  icon: React.ReactNode
  label: string
  value: number | string
  unit: string
  baseline?: number | null
  score?: number | null
  isStress?: boolean
  clickable?: boolean
}) {
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  const delta = baseline && numValue ? numValue - baseline : null
  const deltaPercent = baseline && numValue ? ((numValue - baseline) / baseline * 100).toFixed(0) : null

  // For stress, reverse the color logic (lower is better)
  const getDeltaColor = () => {
    if (delta === null) return ''
    if (isStress) {
      return delta < 0 ? 'text-green-400' : 'text-red-400'
    }
    return delta > 0 ? 'text-green-400' : 'text-red-400'
  }

  const getTrendIcon = () => {
    if (delta === null) return null
    if (isStress) {
      return delta < 0 ? <TrendingDown className="h-3 w-3 text-green-400" /> : <TrendingUp className="h-3 w-3 text-red-400" />
    }
    return delta > 0 ? <TrendingUp className="h-3 w-3 text-green-400" /> : <TrendingDown className="h-3 w-3 text-red-400" />
  }

  return (
    <Card className={`border-slate-700 bg-slate-800/50 ${clickable ? 'hover:border-blue-500 hover:shadow-lg hover:shadow-blue-500/20 transition-all' : ''}`}>
      <CardContent className="p-4">
        <div className="space-y-2">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div className="text-slate-400">{icon}</div>
            <div className="flex items-center gap-1">
              {score && (
                <Badge
                  variant={score >= 70 ? 'default' : score >= 40 ? 'secondary' : 'outline'}
                  className="text-xs h-5"
                >
                  {score}
                </Badge>
              )}
              {clickable && <ArrowRight className="h-3 w-3 text-slate-500" />}
            </div>
          </div>

          {/* Value */}
          <div>
            <div className="text-2xl font-bold text-white">
              {value}{unit && <span className="text-sm text-slate-400 ml-1">{unit}</span>}
            </div>
            <div className="text-xs text-slate-500">{label}</div>
          </div>

          {/* Delta vs baseline */}
          {delta !== null && baseline && (
            <div className={`flex items-center gap-1 text-xs ${getDeltaColor()}`}>
              {getTrendIcon()}
              <span>
                {delta > 0 ? '+' : ''}{Math.abs(delta).toFixed(0)} ({deltaPercent}%)
              </span>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

// ============================================================
// METRIC CARD (Original)
// ============================================================
function MetricCard({ icon, label, value, unit, baseline, score, description }: {
  icon: React.ReactNode
  label: string
  value: number | null | undefined
  unit?: string
  baseline?: number | null
  score?: number | null
  description?: string
}) {
  const getDelta = () => {
    if (!value || !baseline) return null
    const delta = value - baseline
    const percentage = ((delta / baseline) * 100).toFixed(0)
    return { delta, percentage }
  }

  const delta = getDelta()

  return (
    <Card>
      <CardHeader className="pb-2">
        <div className="flex items-center gap-2">
          <div className="p-2 bg-primary/10 rounded-lg text-primary">
            {icon}
          </div>
          <CardTitle className="text-sm font-medium">{label}</CardTitle>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-1">
          {value !== null && value !== undefined ? (
            <>
              <div className="flex items-baseline gap-1">
                <span className="text-2xl font-bold">{value}</span>
                {unit && <span className="text-sm text-muted-foreground">{unit}</span>}
              </div>

              {delta && (
                <p className={`text-xs ${delta.delta > 0 ? 'text-green-600' : 'text-red-600'}`}>
                  {delta.delta > 0 ? '↑' : '↓'} {Math.abs(Number(delta.percentage))}% vs baseline
                </p>
              )}

              {score !== null && score !== undefined && (
                <p className="text-xs text-muted-foreground">Score: {score}/100</p>
              )}

              {description && (
                <p className="text-xs text-muted-foreground">{description}</p>
              )}
            </>
          ) : (
            <p className="text-sm text-muted-foreground">No data</p>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
