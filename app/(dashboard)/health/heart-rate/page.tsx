'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Heart, TrendingUp, Calendar, ArrowLeft, Activity, Moon } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useRouter } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

export default function HeartRateDetailPage() {
    const router = useRouter()

    const { data: history } = useQuery({
        queryKey: ['health', 'history', 30],
        queryFn: async () => {
            const response = await apiClient.getHealthHistory(30)
            return response
        }
    })

    const hrData = history?.filter((m: any) => m.resting_hr_bpm).map((m: any) => ({
        date: new Date(m.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
        rhr: m.resting_hr_bpm,
        baseline: m.resting_hr_baseline_bpm || m.resting_hr_bpm,
        vfc: m.hrv_ms || 0
    })) || []

    // Revertir orden para mostrar más reciente a la derecha
    const chartData = [...hrData].reverse()

    const latest = hrData[hrData.length - 1]
    const avg7d = hrData.slice(-7).reduce((sum: number, d: any) => sum + d.rhr, 0) / Math.min(7, hrData.length)
    const avg30d = hrData.reduce((sum: number, d: any) => sum + d.rhr, 0) / hrData.length
    const minHR = Math.min(...hrData.map((d: any) => d.rhr))

    const getHRStatus = (rhr: number, baseline: number) => {
        const diff = rhr - baseline
        if (diff <= -3) return { text: 'Excelente', color: 'text-green-500', variant: 'default' as const, description: 'Por debajo del baseline' }
        if (diff <= 2) return { text: 'Normal', color: 'text-blue-500', variant: 'default' as const, description: 'Dentro del rango esperado' }
        if (diff <= 5) return { text: 'Elevado', color: 'text-yellow-500', variant: 'secondary' as const, description: 'Ligeramente alto' }
        return { text: 'Muy Elevado', color: 'text-red-500', variant: 'outline' as const, description: 'Considera recuperación' }
    }

    const status = latest ? getHRStatus(latest.rhr, latest.baseline) : null

    // Distribution by zones
    const distribution = [
        { range: 'Muy Bajo (<50)', count: hrData.filter((d: any) => d.rhr < 50).length },
        { range: 'Bajo (50-60)', count: hrData.filter((d: any) => d.rhr >= 50 && d.rhr < 60).length },
        { range: 'Normal (60-70)', count: hrData.filter((d: any) => d.rhr >= 60 && d.rhr < 70).length },
        { range: 'Elevado (≥70)', count: hrData.filter((d: any) => d.rhr >= 70).length }
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
                            <Heart className="h-8 w-8 text-red-400" />
                            Frecuencia Cardíaca en Reposo
                        </h1>
                        <p className="text-slate-400">Monitoreo de tu salud cardiovascular</p>
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
                            {latest?.rhr || '--'}
                            <span className="text-sm text-slate-400 ml-1">bpm</span>
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
                            <span className="text-sm text-slate-400 ml-1">bpm</span>
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
                            <span className="text-sm text-slate-400 ml-1">bpm</span>
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
                            {minHR.toFixed(0)}
                            <span className="text-sm text-slate-400 ml-1">bpm</span>
                        </div>
                        <p className="text-xs text-slate-500">Mejor registro</p>
                    </CardContent>
                </Card>
            </div>

            {/* HR Trend vs Baseline */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-red-400" />
                        Evolución Frecuencia Cardíaca (30 días)
                    </CardTitle>
                    <p className="text-xs text-slate-400 mt-1">
                        Comparación con tu baseline personal
                    </p>
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
                            <Line type="monotone" dataKey="rhr" stroke="#ef4444" strokeWidth={2} name="RHR Actual" dot={{ fill: '#ef4444', r: 4 }} />
                            <Line type="monotone" dataKey="baseline" stroke="#94a3b8" strokeWidth={1} strokeDasharray="5 5" name="Baseline" />
                        </LineChart>
                    </ResponsiveContainer>
                    <div className="flex justify-center gap-6 mt-4">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-red-500 rounded"></div>
                            <span className="text-xs text-slate-400">RHR Actual</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 bg-slate-500 rounded"></div>
                            <span className="text-xs text-slate-400">Baseline</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* HR vs HRV Correlation */}
            {hrData.some((d: any) => d.hrv > 0) && (
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Activity className="h-5 w-5 text-purple-400" />
                            Relación Frecuencia Cardíaca - HRV
                        </CardTitle>
                        <p className="text-xs text-slate-400 mt-1">
                            Una FCR baja generalmente correlaciona con una VFC alta (mejor recuperación)
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
                                <Line yAxisId="left" type="monotone" dataKey="rhr" stroke="#ef4444" strokeWidth={2} name="FCR (bpm)" />
                                <Line yAxisId="right" type="monotone" dataKey="vfc" stroke="#a78bfa" strokeWidth={2} name="VFC (ms)" />
                            </LineChart>
                        </ResponsiveContainer>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-red-500 rounded"></div>
                                <span className="text-xs text-slate-400">RHR</span>
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
                        Distribución de Zonas (30 días)
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
                            <Bar dataKey="count" fill="#f87171" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Educational Content */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">¿Qué es la Frecuencia Cardíaca en Reposo?</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300 space-y-2">
                        <p>
                            La frecuencia cardíaca en reposo (RHR) es el número de latidos por minuto
                            cuando estás completamente en reposo. Es un indicador clave de tu salud cardiovascular.
                        </p>
                        <p>
                            Una RHR más baja generalmente indica mejor forma física. Los atletas de élite
                            pueden tener RHR de 40-50 bpm, mientras que la media es 60-100 bpm.
                        </p>
                        <div className="mt-4 p-3 bg-red-500/10 border border-red-500/20 rounded-lg">
                            <p className="text-red-400 font-medium flex items-center gap-2">
                                <Heart className="h-4 w-4" />
                                Indicador de Recuperación
                            </p>
                            <p className="text-xs mt-1">
                                Un aumento de 5+ bpm sobre tu baseline puede indicar falta de recuperación, estrés o enfermedad inminente.
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">Cómo Mejorar tu RHR</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300">
                        <ul className="space-y-2 list-disc list-inside">
                            <li>Entrenamiento cardiovascular regular (3-5x/semana)</li>
                            <li>Mantener un peso saludable</li>
                            <li>Dormir 7-9 horas de calidad</li>
                            <li>Reducir el estrés y la ansiedad</li>
                            <li>Evitar o limitar cafeína y alcohol</li>
                            <li>Mantenerse hidratado</li>
                            <li>Dejar de fumar</li>
                            <li>Incorporar ejercicios de respiración</li>
                        </ul>
                        <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg">
                            <p className="text-xs text-blue-300">
                                <strong>Rangos de referencia:</strong> &lt;60 bpm (excelente), 60-70 bpm (bueno), 70-80 bpm (promedio), &gt;80 bpm (considerar mejoras)
                            </p>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
