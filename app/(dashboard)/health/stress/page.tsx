'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { TrendingUp, Activity, Calendar, ArrowLeft, AlertTriangle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useRouter } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

export default function StressDetailPage() {
    const router = useRouter()

    const { data: history } = useQuery({
        queryKey: ['health', 'history', 30],
        queryFn: async () => {
            const response = await apiClient.getHealthHistory(30)
            return response
        }
    })

    const stressData = history?.filter((m: any) => m.stress_level !== null && m.stress_level !== undefined).map((m: any) => ({
        date: new Date(m.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
        stress: m.stress_level,
        vfc: m.hrv_ms || 0
    })) || []

    // Revertir orden para mostrar más reciente a la derecha
    const chartData = [...stressData].reverse()

    const latest = stressData[stressData.length - 1]
    const avg7d = stressData.slice(-7).reduce((sum: number, d: any) => sum + d.stress, 0) / Math.min(7, stressData.length)
    const avg30d = stressData.reduce((sum: number, d: any) => sum + d.stress, 0) / stressData.length
    const minStress = Math.min(...stressData.map((d: any) => d.stress))

    const getStressStatus = (stress: number) => {
        if (stress < 25) return { text: 'Bajo', color: 'text-green-500', variant: 'default' as const, description: 'Nivel óptimo de estrés' }
        if (stress < 50) return { text: 'Moderado', color: 'text-blue-500', variant: 'default' as const, description: 'Nivel normal' }
        if (stress < 75) return { text: 'Alto', color: 'text-yellow-500', variant: 'secondary' as const, description: 'Considera técnicas de relajación' }
        return { text: 'Muy Alto', color: 'text-red-500', variant: 'outline' as const, description: 'Prioriza recuperación' }
    }

    const status = latest ? getStressStatus(latest.stress) : null
    // Distribution by level
    const distribution = [
        { range: 'Bajo (<25)', count: stressData.filter((d: any) => d.stress < 25).length },
        { range: 'Moderado (25-50)', count: stressData.filter((d: any) => d.stress >= 25 && d.stress < 50).length },
        { range: 'Alto (50-75)', count: stressData.filter((d: any) => d.stress >= 50 && d.stress < 75).length },
        { range: 'Muy Alto (≥75)', count: stressData.filter((d: any) => d.stress >= 75).length }
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
                            <Activity className="h-8 w-8 text-orange-400" />
                            Nivel de Estrés
                        </h1>
                        <p className="text-slate-400">Monitoreo y análisis de tu respuesta al estrés</p>
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
                        <CardTitle className="text-sm text-slate-400">Actual</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-3xl font-bold ${status?.color || 'text-white'}`}>
                            {latest?.stress || '--'}
                            <span className="text-sm text-slate-400 ml-1">/100</span>
                        </div>
                        <p className="text-xs text-slate-500">{status?.description}</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Media 7 días</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {avg7d.toFixed(0)}
                            <span className="text-sm text-slate-400 ml-1">/100</span>
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
                            {avg30d.toFixed(0)}
                            <span className="text-sm text-slate-400 ml-1">/100</span>
                        </div>
                        <p className="text-xs text-slate-500">Promedio mensual</p>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader className="pb-2">
                        <CardTitle className="text-sm text-slate-400">Mínimo</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-400">
                            {minStress.toFixed(0)}
                            <span className="text-sm text-slate-400 ml-1">/100</span>
                        </div>
                        <p className="text-xs text-slate-500">Tu mejor momento</p>
                    </CardContent>
                </Card>
            </div>

            {/* Stress Trend Chart */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-orange-400" />
                        Evolución del Estrés (30 días)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="stressGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#f97316" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#f97316" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                            <YAxis stroke="#94a3b8" style={{ fontSize: '12px' }} domain={[0, 100]} />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                labelStyle={{ color: '#e2e8f0' }}
                            />
                            <Area
                                type="monotone"
                                dataKey="stress"
                                stroke="#f97316"
                                strokeWidth={2}
                                fill="url(#stressGradient)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                    <div className="mt-2 text-center">
                        <div className="inline-block px-3 py-1 bg-slate-700 rounded-lg">
                            <span className="text-xs text-slate-400">Objetivo: </span>
                            <span className="text-sm font-semibold text-green-400">&lt; 50 (Moderado o Bajo)</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Stress vs HRV Correlation */}
            {stressData.some((d: any) => d.hrv > 0) && (
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Activity className="h-5 w-5 text-purple-400" />
                            Correlación Estrés - HRV
                        </CardTitle>
                        <p className="text-xs text-slate-400 mt-1">
                            El HRV alto generalmente indica estrés bajo y buena recuperación
                        </p>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <YAxis yAxisId="left" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    labelStyle={{ color: '#e2e8f0' }}
                                />
                                <Line yAxisId="left" type="monotone" dataKey="stress" stroke="#f97316" strokeWidth={2} name="Estrés" />
                                <Line yAxisId="right" type="monotone" dataKey="hrv" stroke="#a78bfa" strokeWidth={2} name="HRV (ms)" />
                            </LineChart>
                        </ResponsiveContainer>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-orange-500 rounded"></div>
                                <span className="text-xs text-slate-400">Estrés</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-purple-400 rounded"></div>
                                <span className="text-xs text-slate-400">HRV</span>
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
                        Distribución de Niveles (30 días)
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
                            <Bar dataKey="count" fill="#fb923c" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Educational Content */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">¿Qué es el Nivel de Estrés?</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300 space-y-2">
                        <p>
                            El nivel de estrés se calcula a partir de la variabilidad de la frecuencia cardíaca (HRV)
                            y otros indicadores fisiológicos. Un valor alto indica que tu cuerpo está bajo estrés.
                        </p>
                        <p>
                            El estrés crónico puede afectar negativamente tu recuperación, sistema inmune,
                            y rendimiento deportivo.
                        </p>
                        <div className="mt-4 p-3 bg-orange-500/10 border border-orange-500/20 rounded-lg">
                            <p className="text-orange-400 font-medium flex items-center gap-2">
                                <AlertTriangle className="h-4 w-4" />
                                Importante
                            </p>
                            <p className="text-xs mt-1">
                                Si tu estrés es constantemente alto (&gt;75), considera hablar con un profesional de la salud.
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">Técnicas de Reducción</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300">
                        <ul className="space-y-2 list-disc list-inside">
                            <li>Respiración profunda y meditación (10-15 min/día)</li>
                            <li>Ejercicio regular moderado</li>
                            <li>Sueño de calidad (7-9 horas)</li>
                            <li>Tiempo en la naturaleza</li>
                            <li>Actividades sociales y de ocio</li>
                            <li>Limitar cafeína y alcohol</li>
                            <li>Yoga o estiramientos suaves</li>
                            <li>Gestión del tiempo y prioridades</li>
                        </ul>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
