'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Moon, TrendingUp, Clock, Activity, ArrowLeft, Calendar } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useRouter } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

export default function SleepDetailPage() {
    const router = useRouter()

    const { data: history } = useQuery({
        queryKey: ['health', 'history', 30],
        queryFn: async () => {
            const response = await apiClient.getHealthHistory(30)
            return response
        }
    })

    const sleepData = history?.filter((m: any) => m.sleep_duration_minutes).map((m: any) => ({
        date: new Date(m.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
        duration: +(m.sleep_duration_minutes / 60).toFixed(1),
        score: m.sleep_score || 0,
        deep: m.deep_sleep_minutes ? +(m.deep_sleep_minutes / 60).toFixed(1) : 0,
        rem: m.rem_sleep_minutes ? +(m.rem_sleep_minutes / 60).toFixed(1) : 0,
        light: m.light_sleep_minutes ? +(m.light_sleep_minutes / 60).toFixed(1) : 0
    })) || []

    // Revertir orden para mostrar más reciente a la derecha
    const chartData = [...sleepData].reverse()

    const latest = sleepData[sleepData.length - 1]
    const avg7d = sleepData.slice(-7).reduce((sum: number, d: any) => sum + d.duration, 0) / Math.min(7, sleepData.length)
    const avg30d = sleepData.reduce((sum: number, d: any) => sum + d.duration, 0) / sleepData.length
    const maxSleep = Math.max(...sleepData.map((d: any) => d.duration))

    const getSleepStatus = (score: number) => {
        if (score >= 80) return { text: 'Excelente', color: 'text-green-500', variant: 'default' as const }
        if (score >= 60) return { text: 'Bueno', color: 'text-blue-500', variant: 'default' as const }
        if (score >= 40) return { text: 'Regular', color: 'text-yellow-500', variant: 'secondary' as const }
        return { text: 'Pobre', color: 'text-red-500', variant: 'outline' as const }
    }

    const status = latest ? getSleepStatus(latest.score) : null
    // Distribution by quality
    const distribution = [
        { range: 'Pobre (<40)', count: sleepData.filter((d: any) => d.score < 40).length },
        { range: 'Regular (40-60)', count: sleepData.filter((d: any) => d.score >= 40 && d.score < 60).length },
        { range: 'Bueno (60-80)', count: sleepData.filter((d: any) => d.score >= 60 && d.score < 80).length },
        { range: 'Excelente (≥80)', count: sleepData.filter((d: any) => d.score >= 80).length }
    ]

    return (
        <div className="container mx-auto p-6 space-y-6 max-w-7xl">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                    <Button variant="ghost" size="icon" onClick={() => router.back()}>
                        <ArrowLeft className="h-5 w-5" />
                    </Button>
                    <div>
                        <h1 className="text-3xl font-bold text-white flex items-center gap-2">
                            <Moon className="h-8 w-8 text-blue-400" />
                            Calidad de Sueño
                        </h1>
                        <p className="text-slate-400">Análisis detallado de tus patrones de sueño</p>
                    </div>
                </div>
                {status && (
                    <Badge variant={status.variant} className="text-lg px-4 py-2">
                        {status.text}
                    </Badge>
                )}
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-4">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Última Noche</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {latest?.duration.toFixed(1) || '--'}
                            <span className="text-sm text-slate-400 ml-1">hrs</span>
                        </div>
                        <p className="text-xs text-slate-500">Score: {latest?.score || '--'}/100</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Media 7 días</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {avg7d.toFixed(1)}
                            <span className="text-sm text-slate-400 ml-1">hrs</span>
                        </div>
                        <p className="text-xs text-slate-500">Promedio semanal</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Media 30 días</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {avg30d.toFixed(1)}
                            <span className="text-sm text-slate-400 ml-1">hrs</span>
                        </div>
                        <p className="text-xs text-slate-500">Promedio mensual</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Mejor Noche</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-400">
                            {maxSleep.toFixed(1)}
                            <span className="text-sm text-slate-400 ml-1">hrs</span>
                        </div>
                        <p className="text-xs text-slate-500">Máximo registrado</p>
                    </CardContent>
                </Card>
            </div>

            {/* Duration Trend Chart */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-blue-400" />
                        Duración del Sueño (30 días)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#e2e8f0' }}
                            />
                            <Line type="monotone" dataKey="duration" stroke="#60a5fa" strokeWidth={2} dot={{ fill: '#60a5fa', r: 4 }} />
                        </LineChart>
                    </ResponsiveContainer>
                    <div className="mt-2 text-center">
                        <div className="inline-block px-3 py-1 bg-slate-700 rounded-lg">
                            <span className="text-xs text-slate-400">Objetivo: </span>
                            <span className="text-sm font-semibold text-green-400">7-9 horas</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Sleep Score Trend */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Activity className="h-5 w-5 text-purple-400" />
                        Calidad del Sueño (Score)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} domain={[0, 100]} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#e2e8f0' }}
                            />
                            <Line type="monotone" dataKey="score" stroke="#c084fc" strokeWidth={2} dot={{ fill: '#c084fc', r: 4 }} />
                        </LineChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Sleep Phases */}
            {sleepData.some((d: any) => d.deep > 0 || d.rem > 0) && (
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Clock className="h-5 w-5 text-cyan-400" />
                            Fases del Sueño (Últimos 7 días)
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={sleepData.slice(-7)}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    labelStyle={{ color: '#e2e8f0' }}
                                />
                                <Bar dataKey="deep" stackId="a" fill="#10b981" name="Profundo" />
                                <Bar dataKey="rem" stackId="a" fill="#3b82f6" name="REM" />
                                <Bar dataKey="light" stackId="a" fill="#60a5fa" name="Ligero" />
                            </BarChart>
                        </ResponsiveContainer>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-500 rounded"></div>
                                <span className="text-xs text-slate-400">Profundo</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-600 rounded"></div>
                                <span className="text-xs text-slate-400">REM</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-400 rounded"></div>
                                <span className="text-xs text-slate-400">Ligero</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Distribution */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-indigo-400" />
                        Distribución de Calidad (30 días)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={distribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="range" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#e2e8f0' }}
                            />
                            <Bar dataKey="count" fill="#818cf8" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Educational Content */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">¿Qué es la Calidad del Sueño?</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300 space-y-2">
                        <p>
                            La calidad del sueño se mide por varios factores: duración total, eficiencia del sueño,
                            tiempo para conciliar el sueño, y distribución de las fases.
                        </p>
                        <p>
                            Un sueño de calidad incluye ciclos completos de sueño ligero, profundo y REM,
                            sin interrupciones frecuentes.
                        </p>
                        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            <p className="text-blue-400 font-medium">💤 Recomendación</p>
                            <p className="text-xs mt-1">
                                Adultos necesitan 7-9 horas de sueño por noche para una recuperación óptima.
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">Factores que Afectan el Sueño</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300">
                        <ul className="space-y-2 list-disc list-inside">
                            <li>Exposición a luz azul antes de dormir</li>
                            <li>Cafeína y alcohol en las horas previas</li>
                            <li>Temperatura de la habitación (ideal: 18-20°C)</li>
                            <li>Estrés y preocupaciones</li>
                            <li>Ejercicio intenso cerca de la hora de dormir</li>
                            <li>Horarios irregulares de sueño</li>
                            <li>Alimentación pesada antes de acostarse</li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
