// Health Dashboard Page
'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Badge } from '@/components/ui/badge'
import { Activity, Heart, Moon, Battery, TrendingUp, Calendar } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { formatDate } from '@/lib/formatters'
import { DailyCheckIn } from '@/components/DailyCheckIn'
import { HRVTrend } from '@/components/HRVTrend'
import { SleepQuality } from '@/components/SleepQuality'
import type { HealthMetric } from '@/lib/types'

export default function HealthPage() {
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

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Health Metrics</h1>
        <p className="text-muted-foreground">
          Tu estado de recuperación y recomendaciones personalizadas
        </p>
      </div>

      {/* Two Column Layout: Readiness + Daily Check-In */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Readiness Score Card - Hero */}
        <Card className="border-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">Readiness Score</CardTitle>
                <CardDescription>
                  {todayHealth?.date ? formatDate(new Date(todayHealth.date)) : 'Hoy'}
                </CardDescription>
              </div>
              <Badge variant={getReadinessStatus(readiness?.readiness_score || 50).variant}>
                {getReadinessStatus(readiness?.readiness_score || 50).text}
              </Badge>
            </div>
          </CardHeader>
        <CardContent>
          <div className="flex items-center gap-8">
            {/* Circular Progress */}
            <div className="relative w-32 h-32">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle
                  className="text-gray-200 stroke-current"
                  strokeWidth="10"
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                />
                <circle
                  className={`${getReadinessColor(readiness?.readiness_score || 50)} stroke-current`}
                  strokeWidth="10"
                  strokeLinecap="round"
                  cx="50"
                  cy="50"
                  r="40"
                  fill="transparent"
                  strokeDasharray={`${((readiness?.readiness_score || 0) / 100) * 251.2} 251.2`}
                  transform="rotate(-90 50 50)"
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-3xl font-bold ${getReadinessColor(readiness?.readiness_score || 50)}`}>
                  {readiness?.readiness_score || '--'}
                </span>
              </div>
            </div>

            {/* Factors Breakdown */}
            <div className="flex-1 space-y-3">
              <div className="flex items-center justify-between text-sm">
                <span className="text-muted-foreground">Confianza</span>
                <span className="font-medium capitalize">{readiness?.confidence || 'low'}</span>
              </div>

              {readiness?.factors?.map((factor: any, idx: number) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span>{factor.name}</span>
                    <span className="font-medium">{factor.score}/100</span>
                  </div>
                  <Progress value={factor.score} className="h-2" />
                  {factor.detail && (
                    <p className="text-xs text-muted-foreground">{factor.detail}</p>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Recommendation */}
          {readiness?.recommendation && (
            <div className="mt-6 p-4 bg-muted rounded-lg">
              <p className="text-sm font-medium">{readiness.recommendation}</p>
            </div>
          )}
        </CardContent>
      </Card>

        {/* Daily Check-In Card */}
        <DailyCheckIn />
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* HRV */}
        <MetricCard
          icon={<Heart className="h-5 w-5" />}
          label="HRV"
          value={todayHealth?.hrv_ms}
          unit="ms"
          baseline={todayHealth?.hrv_baseline_ms}
          description="Heart Rate Variability"
        />

        {/* Resting HR */}
        <MetricCard
          icon={<Activity className="h-5 w-5" />}
          label="Resting HR"
          value={todayHealth?.resting_hr_bpm}
          unit="bpm"
          baseline={todayHealth?.resting_hr_baseline_bpm}
          description="Frecuencia cardíaca en reposo"
        />

        {/* Sleep */}
        <MetricCard
          icon={<Moon className="h-5 w-5" />}
          label="Sleep"
          value={todayHealth?.sleep_duration_minutes ? +(todayHealth.sleep_duration_minutes / 60).toFixed(1) : null}
          unit="h"
          score={todayHealth?.sleep_score}
          description="Duración y calidad del sueño"
        />

        {/* Body Battery */}
        <MetricCard
          icon={<Battery className="h-5 w-5" />}
          label="Body Battery"
          value={todayHealth?.body_battery}
          unit="/100"
          description="Nivel de energía corporal"
        />
      </div>

      {/* AI Recommendation Card */}
      {!loadingRec && recommendation && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="h-5 w-5" />
              Recomendación del Coach IA
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none">
              <pre className="whitespace-pre-wrap font-sans text-sm">
                {recommendation.ai_recommendation}
              </pre>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Activity Metrics */}
      {(todayHealth?.steps || todayHealth?.calories_burned) && (
        <Card>
          <CardHeader>
            <CardTitle>Actividad del Día</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {todayHealth.steps && (
                <div>
                  <p className="text-sm text-muted-foreground">Pasos</p>
                  <p className="text-2xl font-bold">{todayHealth.steps.toLocaleString()}</p>
                </div>
              )}
              {todayHealth.calories_burned && (
                <div>
                  <p className="text-sm text-muted-foreground">Calorías</p>
                  <p className="text-2xl font-bold">{todayHealth.calories_burned}</p>
                </div>
              )}
              {todayHealth.intensity_minutes && (
                <div>
                  <p className="text-sm text-muted-foreground">Minutos Intensos</p>
                  <p className="text-2xl font-bold">{todayHealth.intensity_minutes}</p>
                </div>
              )}
              {todayHealth.stress_level !== null && (
                <div>
                  <p className="text-sm text-muted-foreground">Estrés</p>
                  <p className="text-2xl font-bold">{todayHealth.stress_level}/100</p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Trends: HRV + Sleep Quality */}
      {history?.metrics && history.metrics.length > 0 && (
        <div className="grid gap-6 lg:grid-cols-2">
          <HRVTrend metrics={history.metrics} days={7} />
          <SleepQuality metrics={history.metrics} days={7} />
        </div>
      )}

      {/* Data Source Badge */}
      {todayHealth && (
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Calendar className="h-4 w-4" />
          <span>Fuente de datos:</span>
          <Badge variant="outline" className="capitalize">
            {todayHealth.source === 'garmin' ? 'Garmin Connect' :
             todayHealth.source === 'google_fit' ? 'Google Fit' :
             todayHealth.source === 'apple_health' ? 'Apple Health' :
             'Manual Entry'}
          </Badge>
          <Badge variant="outline" className="capitalize">
            {todayHealth.data_quality === 'high' ? 'Alta Calidad' :
             todayHealth.data_quality === 'medium' ? 'Calidad Media' :
             'Calidad Básica'}
          </Badge>
        </div>
      )}
    </div>
  )
}

// Metric Card Component
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
