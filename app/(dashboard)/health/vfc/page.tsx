'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Activity, TrendingUp, Calendar, ArrowLeft, Heart } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useRouter } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

export default function VFCDetailPage() {
    const router = useRouter()

    const { data: history } = useQuery({
        queryKey: ['health', 'history', 30],
        queryFn: async () => {
            const response = await apiClient.getHealthHistory(30)
            return response
        }
    })

    const vfcData = history?.filter((m: any) => m.hrv_ms).map((m: any) => ({
        date: new Date(m.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
        vfc: m.hrv_ms,
        baseline: m.hrv_baseline_ms || 60,
        stress: m.stress_level || 0
    })) || []

    // Revertir orden para mostrar más reciente a la derecha
    const chartData = [...vfcData].reverse()

    const latest = vfcData[vfcData.length - 1]
    const avg7d = vfcData.slice(-7).reduce((sum: number, d: any) => sum + d.vfc, 0) / Math.min(7, vfcData.length)
    const avg30d = vfcData.reduce((sum: number, d: any) => sum + d.vfc, 0) / vfcData.length
    const maxVFC = Math.max(...vfcData.map((d: any) => d.vfc))

    const getVFCStatus = (vfc: number) => {
        if (vfc >= 60) return { text: 'Excelente', color: 'text-green-500', variant: 'default' as const, description: 'Muy buena recuperación' }
        if (vfc >= 40) return { text: 'Bueno', color: 'text-blue-500', variant: 'default' as const, description: 'Recuperación adecuada' }
        if (vfc >= 20) return { text: 'Regular', color: 'text-yellow-500', variant: 'secondary' as const, description: 'Necesitas más descanso' }
        return { text: 'Bajo', color: 'text-red-500', variant: 'outline' as const, description: 'Prioriza la recuperación' }
    }

    const status = latest ? getVFCStatus(latest.vfc) : null

    // Distribution by ranges
    const distribution = [
        { range: 'Bajo (<20)', count: vfcData.filter((d: any) => d.vfc < 20).length, color: '#ef4444' },
        { range: 'Regular (20-40)', count: vfcData.filter((d: any) => d.vfc >= 20 && d.vfc < 40).length, color: '#eab308' },
        { range: 'Bueno (40-60)', count: vfcData.filter((d: any) => d.vfc >= 40 && d.vfc < 60).length, color: '#3b82f6' },
        { range: 'Excelente (≥60)', count: vfcData.filter((d: any) => d.vfc >= 60).length, color: '#22c55e' }
    ]

    return (
        <div className="container mx-auto p-6 space-y-6 max-w-6xl">
            {/* Header */}
            <div className="flex items-center gap-4">
                <Button variant="ghost" size="icon" onClick={() => router.back()}>
                    <ArrowLeft className="h-5 w-5" />
                </Button>
                <div>
                    <h1 className="text-3xl font-bold text-white">Variabilidad de Frecuencia Cardíaca (VFC)</h1>
                    <p className="text-slate-400">Análisis detallado de tu VFC y recuperación</p>
                </div>
            </div>

            {/* Current Status */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                        <Activity className="h-5 w-5 text-purple-400" />
                        Estado Actual
                    </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div>
                            <div className="text-sm text-slate-400">VFC Actual</div>
                            <div className={`text-3xl font-bold ${status?.color || 'text-white'}`}>
                                {latest?.vfc || 0}
                                <span className="text-lg ml-1">ms</span>
                            </div>
                            {status && <Badge variant={status.variant} className="mt-1">{status.text}</Badge>}
                        </div>
                        <div>
                            <div className="text-sm text-slate-400">Promedio 7 días</div>
                            <div className="text-2xl font-bold text-white">
                                {avg7d.toFixed(0)}
                                <span className="text-sm ml-1">ms</span>
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-slate-400">Promedio 30 días</div>
                            <div className="text-2xl font-bold text-white">
                                {avg30d.toFixed(0)}
                                <span className="text-sm ml-1">ms</span>
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-slate-400">Máximo Histórico</div>
                            <div className="text-2xl font-bold text-green-400">
                                {maxVFC}
                                <span className="text-sm ml-1">ms</span>
                            </div>
                        </div>
                    </div>
                    {status && (
                        <div className="p-3 bg-slate-700/50 rounded-lg">
                            <div className="text-sm text-slate-300">{status.description}</div>
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* VFC Trend Chart */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                        <TrendingUp className="h-5 w-5 text-blue-400" />
                        Tendencia de VFC (Últimos 30 días)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="colorVFC" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0} />
                                </linearGradient>
                            </defs>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" />
                            <YAxis stroke="#94a3b8" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                                labelStyle={{ color: '#f1f5f9' }}
                            />
                            <Area type="monotone" dataKey="vfc" stroke="#8b5cf6" fillOpacity={1} fill="url(#colorVFC)" name="VFC (ms)" />
                            <Line type="monotone" dataKey="baseline" stroke="#60a5fa" strokeDasharray="5 5" name="Baseline" />
                        </AreaChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Distribution */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                        <Calendar className="h-5 w-5 text-purple-400" />
                        Distribución por Rangos
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={250}>
                        <BarChart data={distribution}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="range" stroke="#94a3b8" angle={-15} textAnchor="end" height={80} />
                            <YAxis stroke="#94a3b8" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                                labelStyle={{ color: '#f1f5f9' }}
                            />
                            <Bar dataKey="count" fill="#8b5cf6" name="Días" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* VFC vs Stress Correlation */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-white">
                        <Heart className="h-5 w-5 text-red-400" />
                        VFC vs Estrés
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <LineChart data={chartData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                            <XAxis dataKey="date" stroke="#94a3b8" />
                            <YAxis yAxisId="left" stroke="#8b5cf6" />
                            <YAxis yAxisId="right" orientation="right" stroke="#f59e0b" />
                            <Tooltip
                                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155' }}
                                labelStyle={{ color: '#f1f5f9' }}
                            />
                            <Line yAxisId="left" type="monotone" dataKey="vfc" stroke="#8b5cf6" name="VFC (ms)" strokeWidth={2} />
                            <Line yAxisId="right" type="monotone" dataKey="stress" stroke="#f59e0b" name="Estrés" strokeWidth={2} />
                        </LineChart>
                    </ResponsiveContainer>
                    <div className="mt-4 text-sm text-slate-400">
                        Una VFC más alta generalmente se correlaciona con niveles de estrés más bajos, indicando mejor recuperación.
                    </div>
                </CardContent>
            </Card>

            {/* Educational Content */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white">¿Qué es la VFC?</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4 text-slate-300">
                    <p>
                        La <strong>Variabilidad de Frecuencia Cardíaca (VFC)</strong> mide la variación en el tiempo entre latidos consecutivos.
                        Una VFC más alta indica mejor recuperación y adaptabilidad del sistema nervioso autónomo.
                    </p>

                    <div className="space-y-2">
                        <h3 className="font-semibold text-white">Factores que afectan la VFC:</h3>
                        <ul className="list-disc list-inside space-y-1 ml-2">
                            <li>Calidad del sueño</li>
                            <li>Nivel de estrés y ansiedad</li>
                            <li>Entrenamiento y fatiga</li>
                            <li>Hidratación y nutrición</li>
                            <li>Estado de salud general</li>
                        </ul>
                    </div>

                    <div className="space-y-2">
                        <h3 className="font-semibold text-white">Cómo mejorar tu VFC:</h3>
                        <ul className="list-disc list-inside space-y-1 ml-2">
                            <li>Prioriza un sueño de calidad (7-9 horas)</li>
                            <li>Practica técnicas de relajación (meditación, respiración profunda)</li>
                            <li>Mantén un equilibrio entre entrenamiento y recuperación</li>
                            <li>Hidrátate adecuadamente</li>
                            <li>Evita el sobreentrenamiento</li>
                        </ul>
                    </div>

                    <div className="p-4 bg-blue-900/20 border border-blue-800/30 rounded-lg">
                        <p className="text-sm">
                            <strong>💡 Tip:</strong> La VFC es más precisa cuando se mide en reposo, preferiblemente al despertar antes de levantarte de la cama.
                        </p>
                    </div>
                </CardContent>
            </Card>
        </div>
    )
}
