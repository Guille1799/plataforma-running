'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Activity, TrendingUp, Calendar, ArrowLeft, Target, Footprints } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useRouter } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

export default function ActivityDetailPage() {
    const router = useRouter()

    const { data: history } = useQuery({
        queryKey: ['health', 'history', 30],
        queryFn: async () => {
            const response = await apiClient.getHealthHistory(30)
            return response
        }
    })

    const activityData = history?.filter((m: any) => m.steps && m.steps > 100).map((m: any) => ({
        date: new Date(m.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
        steps: m.steps,
        km: m.steps ? +(m.steps * 0.00075).toFixed(1) : 0, // Aprox 750 steps = 1 km
        calories: m.steps ? Math.round(m.steps * 0.04) : 0 // Aprox 40 cal per 1000 steps
    })) || []

    // Revertir orden para mostrar más reciente a la derecha
    const chartData = [...activityData].reverse()

    const latest = activityData[activityData.length - 1]
    const avg7d = activityData.slice(-7).reduce((sum: number, d: any) => sum + d.steps, 0) / Math.min(7, activityData.length)
    const avg30d = activityData.reduce((sum: number, d: any) => sum + d.steps, 0) / activityData.length
    const maxSteps = Math.max(...activityData.map((d: any) => d.steps))
    const total30d = activityData.reduce((sum: number, d: any) => sum + d.steps, 0)

    const DAILY_GOAL = 10000

    const getActivityStatus = (steps: number) => {
        const percentage = (steps / DAILY_GOAL) * 100
        if (percentage >= 100) return { text: 'Meta Alcanzada', color: 'text-green-500', variant: 'default' as const, description: '¡Excelente!' }
        if (percentage >= 75) return { text: 'Casi Allí', color: 'text-blue-500', variant: 'default' as const, description: `${(100 - percentage).toFixed(0)}% restante` }
        if (percentage >= 50) return { text: 'En Progreso', color: 'text-yellow-500', variant: 'secondary' as const, description: 'Sigue así' }
        return { text: 'Bajo', color: 'text-red-500', variant: 'outline' as const, description: 'Más actividad necesaria' }
    }

    const status = latest ? getActivityStatus(latest.steps) : null

    // Distribution by achievement
    const distribution = [
        { range: '< 5k', count: activityData.filter((d: any) => d.steps < 5000).length },
        { range: '5k-10k', count: activityData.filter((d: any) => d.steps >= 5000 && d.steps < 10000).length },
        { range: '10k-15k', count: activityData.filter((d: any) => d.steps >= 10000 && d.steps < 15000).length },
        { range: '≥ 15k', count: activityData.filter((d: any) => d.steps >= 15000).length }
    ]

    const daysAboveGoal = activityData.filter((d: any) => d.steps >= DAILY_GOAL).length

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
                            <Footprints className="h-8 w-8 text-cyan-400" />
                            Actividad y Pasos
                        </h1>
                        <p className="text-slate-400">Seguimiento de tu actividad diaria</p>
                    </div>
                </div>
                {status && (
                    <Badge variant={status.variant} className="text-lg px-4 py-2">
                        {status.text}
                    </Badge>
                )}
            </div>

            {/* Summary Cards */}
            <div className="grid gap-4 md:grid-cols-5">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Hoy</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-3xl font-bold ${status?.color || 'text-white'}`}>
                            {latest?.steps ? (latest.steps >= 1000 ? `${(latest.steps / 1000).toFixed(1)}k` : latest.steps) : '--'}
                        </div>
                        <p className="text-xs text-slate-500">{status?.description}</p>
                        <div className="mt-2">
                            <div className="w-full bg-slate-700 rounded-full h-1.5">
                                <div
                                    className="bg-cyan-500 h-1.5 rounded-full transition-all"
                                    style={{ width: `${Math.min(100, (latest?.steps || 0) / DAILY_GOAL * 100)}%` }}
                                />
                            </div>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Media 7d</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {avg7d >= 1000 ? `${(avg7d / 1000).toFixed(1)}k` : avg7d.toFixed(0)}
                        </div>
                        <p className="text-xs text-slate-500">Promedio semanal</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Media 30d</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {avg30d >= 1000 ? `${(avg30d / 1000).toFixed(1)}k` : avg30d.toFixed(0)}
                        </div>
                        <p className="text-xs text-slate-500">Promedio mensual</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Récord</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-400">
                            {maxSteps >= 1000 ? `${(maxSteps / 1000).toFixed(1)}k` : maxSteps}
                        </div>
                        <p className="text-xs text-slate-500">Mejor día</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Meta Cumplida</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-cyan-400">
                            {daysAboveGoal}
                            <span className="text-sm text-slate-400 ml-1">días</span>
                        </div>
                        <p className="text-xs text-slate-500">Últimos 30 días</p>
                    </CardContent>
                </Card>
            </div>

            {/* Steps Trend Chart */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-cyan-400" />
                        Evolución de Pasos (30 días)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#e2e8f0' }}
                            />
                            <Bar
                                dataKey="steps"
                                fill="#22d3ee"
                                radius={[4, 4, 0, 0]}
                            />
                            {/* Goal line */}
                            <line
                                y1={DAILY_GOAL}
                                y2={DAILY_GOAL}
                                stroke="#10b981"
                                strokeWidth={2}
                                strokeDasharray="5 5"
                            />
                        </BarChart>
                    </ResponsiveContainer>
                    <div className="mt-2 text-center flex justify-center gap-6">
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-700 rounded-lg">
                            <Target className="h-3 w-3 text-green-400" />
                            <span className="text-xs text-slate-400">Meta diaria: </span>
                            <span className="text-sm font-semibold text-green-400">{(DAILY_GOAL / 1000).toFixed(0)}k pasos</span>
                        </div>
                        <div className="inline-flex items-center gap-2 px-3 py-1 bg-slate-700 rounded-lg">
                            <span className="text-xs text-slate-400">Total mes: </span>
                            <span className="text-sm font-semibold text-cyan-400">{(total30d / 1000).toFixed(0)}k pasos</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Distance Chart */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Activity className="h-5 w-5 text-blue-400" />
                        Distancia Estimada (km)
                    </CardTitle>
                    <p className="text-xs text-slate-400 mt-1">
                        Basado en ~750 pasos por kilómetro
                    </p>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="distanceGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#e2e8f0' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="km"
                                stroke="#3b82f6"
                                strokeWidth={2}
                                fill="url(#distanceGradient)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Distribution */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <Calendar className="h-5 w-5 text-indigo-400" />
                        Distribución de Actividad (30 días)
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
                            <Bar dataKey="count" fill="#06b6d4" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Educational Content */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">Beneficios de 10,000 Pasos</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300 space-y-2">
                        <p>
                            La meta de 10,000 pasos diarios (aproximadamente 7-8 km) es un objetivo
                            respaldado por estudios que muestra beneficios significativos para la salud.
                        </p>
                        <ul className="space-y-1 list-disc list-inside ml-2 text-xs mt-3">
                            <li>Mejora la salud cardiovascular</li>
                            <li>Ayuda a mantener un peso saludable</li>
                            <li>Reduce el riesgo de diabetes tipo 2</li>
                            <li>Fortalece huesos y músculos</li>
                            <li>Mejora el estado de ánimo y reduce estrés</li>
                            <li>Incrementa la energía durante el día</li>
                        </ul>
                        <div className="mt-4 p-3 bg-cyan-500/10 border border-cyan-500/20 rounded-lg">
                            <p className="text-cyan-400 font-medium flex items-center gap-2">
                                <Target className="h-4 w-4" />
                                Recomendación
                            </p>
                            <p className="text-xs mt-1">
                                Si no alcanzas 10k pasos, cualquier aumento en actividad es beneficioso. Empieza con metas más pequeñas.
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">Consejos para Más Pasos</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300">
                        <ul className="space-y-2 list-disc list-inside">
                            <li>Usa las escaleras en lugar del ascensor</li>
                            <li>Estaciona más lejos de tu destino</li>
                            <li>Haz pausas activas cada hora sentado</li>
                            <li>Camina mientras hablas por teléfono</li>
                            <li>Organiza reuniones caminando</li>
                            <li>Sal a caminar después de las comidas</li>
                            <li>Explora rutas nuevas en tu vecindario</li>
                            <li>Usa recordatorios para levantarte cada hora</li>
                        </ul>
                        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            <p className="text-xs text-blue-300">
                                <strong>Dato interesante:</strong> Caminar 10,000 pasos quema aproximadamente 400-500 calorías.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
