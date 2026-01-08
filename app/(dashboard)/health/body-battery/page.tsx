'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Battery, TrendingUp, Calendar, ArrowLeft, Zap, Moon, Activity } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useRouter } from 'next/navigation'
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart } from 'recharts'

export default function BodyBatteryDetailPage() {
    const router = useRouter()

    const { data: history } = useQuery({
        queryKey: ['health', 'history', 30],
        queryFn: async () => {
            const response = await apiClient.getHealthHistory(30)
            return response
        }
    })

    const batteryData = history?.filter((m: any) => m.body_battery !== null && m.body_battery !== undefined && m.body_battery > 5).map((m: any) => ({
        date: new Date(m.date).toLocaleDateString('es-ES', { day: 'numeric', month: 'short' }),
        battery: m.body_battery,
        sleep: m.sleep_score || 0,
        stress: m.stress_level || 0
    })) || []

    // Revertir orden para mostrar más reciente a la derecha
    const chartData = [...batteryData].reverse()

    const latest = batteryData[batteryData.length - 1]
    const avg7d = batteryData.slice(-7).reduce((sum: number, d: any) => sum + d.battery, 0) / Math.min(7, batteryData.length)
    const avg30d = batteryData.reduce((sum: number, d: any) => sum + d.battery, 0) / batteryData.length
    const maxBattery = Math.max(...batteryData.map((d: any) => d.battery))

    const getBatteryStatus = (battery: number) => {
        if (battery >= 75) return { text: 'Alta', color: 'text-green-500', variant: 'default' as const, description: 'Excelente nivel de energía' }
        if (battery >= 50) return { text: 'Media', color: 'text-blue-500', variant: 'default' as const, description: 'Energía moderada' }
        if (battery >= 25) return { text: 'Baja', color: 'text-yellow-500', variant: 'secondary' as const, description: 'Considera descanso' }
        return { text: 'Muy Baja', color: 'text-red-500', variant: 'outline' as const, description: 'Prioriza recuperación' }
    }

    const status = latest ? getBatteryStatus(latest.battery) : null
    // Distribution by level
    const distribution = [
        { range: 'Muy Baja (<25)', count: batteryData.filter((d: any) => d.battery < 25).length },
        { range: 'Baja (25-50)', count: batteryData.filter((d: any) => d.battery >= 25 && d.battery < 50).length },
        { range: 'Media (50-75)', count: batteryData.filter((d: any) => d.battery >= 50 && d.battery < 75).length },
        { range: 'Alta (≥75)', count: batteryData.filter((d: any) => d.battery >= 75).length }
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
                            <Battery className="h-8 w-8 text-green-400" />
                            Body Battery
                        </h1>
                        <p className="text-slate-400">Tu nivel de energía corporal y capacidad de rendimiento</p>
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
                            {latest?.battery || '--'}
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
                        <CardTitle className="text-sm text-slate-400">Máximo</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-green-400">
                            {maxBattery.toFixed(0)}
                            <span className="text-sm text-slate-400 ml-1">/100</span>
                        </div>
                        <p className="text-xs text-slate-500">Mejor recuperación</p>
                    </CardContent>
                </Card>
            </div>

            {/* Battery Trend Chart */}
            <Card className="border-slate-700 bg-slate-800/50">
                <CardHeader>
                    <CardTitle className="text-white flex items-center gap-2">
                        <TrendingUp className="h-5 w-5 text-green-400" />
                        Evolución de la Body Battery (30 días)
                    </CardTitle>
                </CardHeader>
                <CardContent>
                    <ResponsiveContainer width="100%" height={300}>
                        <AreaChart data={chartData}>
                            <defs>
                                <linearGradient id="batteryGradient" x1="0" y1="0" x2="0" y2="1">
                                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                                    <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
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
                                dataKey="battery"
                                stroke="#10b981"
                                strokeWidth={2}
                                fill="url(#batteryGradient)"
                            />
                        </AreaChart>
                    </ResponsiveContainer>
                    <div className="mt-2 text-center">
                        <div className="inline-block px-3 py-1 bg-slate-700 rounded-lg">
                            <span className="text-xs text-slate-400">Objetivo: </span>
                            <span className="text-sm font-semibold text-green-400">&gt; 75 (Alta energía)</span>
                        </div>
                    </div>
                </CardContent>
            </Card>

            {/* Battery vs Sleep Correlation */}
            {batteryData.some((d: any) => d.sleep > 0) && (
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Moon className="h-5 w-5 text-blue-400" />
                            Relación Body Battery - Sueño
                        </CardTitle>
                        <p className="text-xs text-slate-400 mt-1">
                            La calidad del sueño es el principal factor de recarga de tu Body Battery
                        </p>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={batteryData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="date" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <YAxis yAxisId="left" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <YAxis yAxisId="right" orientation="right" stroke="#94a3b8" style={{ fontSize: '12px' }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    labelStyle={{ color: '#e2e8f0' }}
                                />
                                <Line yAxisId="left" type="monotone" dataKey="battery" stroke="#10b981" strokeWidth={2} name="Body Battery" />
                                <Line yAxisId="right" type="monotone" dataKey="sleep" stroke="#60a5fa" strokeWidth={2} name="Sleep Score" />
                            </LineChart>
                        </ResponsiveContainer>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-500 rounded"></div>
                                <span className="text-xs text-slate-400">Body Battery</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-blue-400 rounded"></div>
                                <span className="text-xs text-slate-400">Sleep Score</span>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}

            {/* Battery vs Stress Correlation */}
            {batteryData.some((d: any) => d.stress > 0) && (
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white flex items-center gap-2">
                            <Activity className="h-5 w-5 text-orange-400" />
                            Relación Body Battery - Estrés
                        </CardTitle>
                        <p className="text-xs text-slate-400 mt-1">
                            El estrés alto consume tu Body Battery más rápidamente
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
                                <Line yAxisId="left" type="monotone" dataKey="battery" stroke="#10b981" strokeWidth={2} name="Body Battery" />
                                <Line yAxisId="right" type="monotone" dataKey="stress" stroke="#f97316" strokeWidth={2} name="Estrés" />
                            </LineChart>
                        </ResponsiveContainer>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-green-500 rounded"></div>
                                <span className="text-xs text-slate-400">Body Battery</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 bg-orange-500 rounded"></div>
                                <span className="text-xs text-slate-400">Estrés</span>
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
                            <Bar dataKey="count" fill="#22c55e" />
                        </BarChart>
                    </ResponsiveContainer>
                </CardContent>
            </Card>

            {/* Educational Content */}
            <div className="grid gap-4 md:grid-cols-2">
                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">¿Qué es Body Battery?</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300 space-y-2">
                        <p>
                            Body Battery es una medida propietaria de Garmin que estima tu nivel de energía
                            corporal en una escala de 0 a 100, basándose en HRV, estrés, sueño y actividad.
                        </p>
                        <p>
                            Tu Body Battery se recarga principalmente durante el sueño y el descanso,
                            y se consume durante el ejercicio, estrés mental y actividad física.
                        </p>
                        <div className="mt-4 p-3 bg-green-500/10 border border-green-500/20 rounded-lg">
                            <p className="text-green-400 font-medium flex items-center gap-2">
                                <Zap className="h-4 w-4" />
                                Optimización
                            </p>
                            <p className="text-xs mt-1">
                                Para maximizar tu Body Battery: duerme 7-9 horas, gestiona el estrés, y programa entrenamientos intensos cuando esté alta.
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <Card className="border-slate-700 bg-slate-800/50">
                    <CardHeader>
                        <CardTitle className="text-white text-lg">Factores que Afectan Body Battery</CardTitle>
                    </CardHeader>
                    <CardContent className="text-sm text-slate-300">
                        <div className="space-y-3">
                            <div>
                                <p className="font-medium text-green-400 mb-1">✓ Factores que la Recargan:</p>
                                <ul className="space-y-1 list-disc list-inside ml-2 text-xs">
                                    <li>Sueño de calidad</li>
                                    <li>Descanso y relajación</li>
                                    <li>Actividades tranquilas</li>
                                    <li>Niveles bajos de estrés</li>
                                </ul>
                            </div>
                            <div>
                                <p className="font-medium text-red-400 mb-1">✗ Factores que la Consumen:</p>
                                <ul className="space-y-1 list-disc list-inside ml-2 text-xs">
                                    <li>Ejercicio físico intenso</li>
                                    <li>Estrés mental y emocional</li>
                                    <li>Enfermedades o inflamación</li>
                                    <li>Falta de sueño</li>
                                    <li>Alcohol y cafeína</li>
                                </ul>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    )
}
