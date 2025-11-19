'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'
import { TrendingUp, TrendingDown, Activity, Heart, Moon, Battery } from 'lucide-react'
import { formatDate } from '@/lib/formatters'

export default function HealthHistoryPage() {
  const { data: history, isLoading } = useQuery({
    queryKey: ['health', 'history', 30],
    queryFn: () => apiClient.getHealthHistory(30),
  })

  const { data: trends } = useQuery({
    queryKey: ['health', 'trends', 30],
    queryFn: () => apiClient.getHealthTrends(30),
  })

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600" />
      </div>
    )
  }

  if (!history || history.length === 0) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div className="text-center py-12">
          <Activity className="h-16 w-16 mx-auto text-muted-foreground mb-4" />
          <h2 className="text-2xl font-bold mb-2">Sin datos de historial</h2>
          <p className="text-muted-foreground mb-6">
            Conecta un dispositivo o completa tu check-in diario para ver tendencias
          </p>
          <a href="/health/devices" className="text-blue-500 hover:underline">
            Conectar dispositivo →
          </a>
        </div>
      </div>
    )
  }

  // Prepare data for charts
  const chartData = history.map((metric: any) => ({
    date: new Date(metric.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
    fullDate: metric.date,
    hrv: metric.hrv_ms,
    hrvBaseline: metric.hrv_baseline_ms,
    restingHR: metric.resting_hr_bpm,
    restingHRBaseline: metric.resting_hr_baseline_bpm,
    sleep: metric.sleep_duration_minutes ? (metric.sleep_duration_minutes / 60).toFixed(1) : null,
    sleepScore: metric.sleep_score,
    bodyBattery: metric.body_battery,
    readiness: metric.readiness_score,
    stress: metric.stress_level,
    steps: metric.steps,
  })).reverse() // Most recent last

  // Calculate trends
  const calculateTrend = (data: any[], key: string) => {
    const values = data.filter(d => d[key] !== null && d[key] !== undefined).map(d => d[key])
    if (values.length < 2) return { direction: 'stable', change: 0 }
    const recent = values.slice(-7).reduce((a, b) => a + b, 0) / Math.min(7, values.length)
    const previous = values.slice(-14, -7).reduce((a, b) => a + b, 0) / Math.min(7, values.slice(-14, -7).length)
    const change = previous > 0 ? ((recent - previous) / previous * 100) : 0
    return {
      direction: change > 2 ? 'up' : change < -2 ? 'down' : 'stable',
      change: Math.abs(change).toFixed(1)
    }
  }

  const hrvTrend = calculateTrend(chartData, 'hrv')
  const sleepTrend = calculateTrend(chartData, 'sleep')
  const readinessTrend = calculateTrend(chartData, 'readiness')

  return (
    <div className="p-6 max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Health History</h1>
        <p className="text-muted-foreground">Últimos 30 días de métricas de salud</p>
      </div>

      {/* Trend Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Heart className="h-4 w-4" />
              HRV Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {hrvTrend.direction === 'up' ? (
                <TrendingUp className="h-5 w-5 text-green-500" />
              ) : hrvTrend.direction === 'down' ? (
                <TrendingDown className="h-5 w-5 text-red-500" />
              ) : (
                <Activity className="h-5 w-5 text-muted-foreground" />
              )}
              <span className={`text-lg font-bold ${
                hrvTrend.direction === 'up' ? 'text-green-500' : 
                hrvTrend.direction === 'down' ? 'text-red-500' : 
                'text-muted-foreground'
              }`}>
                {hrvTrend.change}%
              </span>
              <span className="text-sm text-muted-foreground">vs semana anterior</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Moon className="h-4 w-4" />
              Sleep Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {sleepTrend.direction === 'up' ? (
                <TrendingUp className="h-5 w-5 text-green-500" />
              ) : sleepTrend.direction === 'down' ? (
                <TrendingDown className="h-5 w-5 text-red-500" />
              ) : (
                <Activity className="h-5 w-5 text-muted-foreground" />
              )}
              <span className={`text-lg font-bold ${
                sleepTrend.direction === 'up' ? 'text-green-500' : 
                sleepTrend.direction === 'down' ? 'text-red-500' : 
                'text-muted-foreground'
              }`}>
                {sleepTrend.change}%
              </span>
              <span className="text-sm text-muted-foreground">vs semana anterior</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-sm flex items-center gap-2">
              <Battery className="h-4 w-4" />
              Readiness Trend
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {readinessTrend.direction === 'up' ? (
                <TrendingUp className="h-5 w-5 text-green-500" />
              ) : readinessTrend.direction === 'down' ? (
                <TrendingDown className="h-5 w-5 text-red-500" />
              ) : (
                <Activity className="h-5 w-5 text-muted-foreground" />
              )}
              <span className={`text-lg font-bold ${
                readinessTrend.direction === 'up' ? 'text-green-500' : 
                readinessTrend.direction === 'down' ? 'text-red-500' : 
                'text-muted-foreground'
              }`}>
                {readinessTrend.change}%
              </span>
              <span className="text-sm text-muted-foreground">vs semana anterior</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* HRV Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Heart Rate Variability (HRV)</CardTitle>
          <CardDescription>Mayor HRV indica mejor recuperación</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                labelStyle={{ color: 'hsl(var(--foreground))' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="hrv" 
                stroke="#3b82f6" 
                strokeWidth={2}
                name="HRV (ms)"
                dot={{ r: 3 }}
              />
              <Line 
                type="monotone" 
                dataKey="hrvBaseline" 
                stroke="#94a3b8" 
                strokeWidth={1}
                strokeDasharray="5 5"
                name="Baseline"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Sleep Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Sleep Duration & Quality</CardTitle>
          <CardDescription>Horas de sueño y score de calidad</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis yAxisId="left" className="text-xs" />
              <YAxis yAxisId="right" orientation="right" className="text-xs" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
              />
              <Legend />
              <Line 
                yAxisId="left"
                type="monotone" 
                dataKey="sleep" 
                stroke="#8b5cf6" 
                strokeWidth={2}
                name="Horas de sueño"
                dot={{ r: 3 }}
              />
              <Line 
                yAxisId="right"
                type="monotone" 
                dataKey="sleepScore" 
                stroke="#10b981" 
                strokeWidth={2}
                name="Sleep Score"
                dot={{ r: 3 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Readiness Score Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Readiness Score</CardTitle>
          <CardDescription>Tu nivel de preparación para entrenar (0-100)</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis domain={[0, 100]} className="text-xs" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
              />
              <Bar 
                dataKey="readiness" 
                fill="#3b82f6"
                name="Readiness"
                radius={[8, 8, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Resting HR Chart */}
      <Card>
        <CardHeader>
          <CardTitle>Resting Heart Rate</CardTitle>
          <CardDescription>Frecuencia cardíaca en reposo (menor es mejor)</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="date" className="text-xs" />
              <YAxis className="text-xs" />
              <Tooltip 
                contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="restingHR" 
                stroke="#ef4444" 
                strokeWidth={2}
                name="Resting HR (bpm)"
                dot={{ r: 3 }}
              />
              <Line 
                type="monotone" 
                dataKey="restingHRBaseline" 
                stroke="#94a3b8" 
                strokeWidth={1}
                strokeDasharray="5 5"
                name="Baseline"
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Body Battery & Stress */}
      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Body Battery</CardTitle>
            <CardDescription>Nivel de energía (0-100)</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis domain={[0, 100]} className="text-xs" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                />
                <Bar 
                  dataKey="bodyBattery" 
                  fill="#10b981"
                  name="Body Battery"
                  radius={[8, 8, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Stress Level</CardTitle>
            <CardDescription>Nivel de estrés (menor es mejor)</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="date" className="text-xs" />
                <YAxis domain={[0, 100]} className="text-xs" />
                <Tooltip 
                  contentStyle={{ backgroundColor: 'hsl(var(--card))', border: '1px solid hsl(var(--border))' }}
                />
                <Line 
                  type="monotone" 
                  dataKey="stress" 
                  stroke="#f59e0b" 
                  strokeWidth={2}
                  name="Stress"
                  dot={{ r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* AI Insights */}
      {trends && (
        <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
          <CardHeader>
            <CardTitle className="text-blue-900 dark:text-blue-100">
              🤖 AI Insights
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm text-blue-800 dark:text-blue-200">
            <p><strong>Análisis de tendencias:</strong></p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              {trends.insights?.map((insight: string, idx: number) => (
                <li key={idx}>{insight}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
