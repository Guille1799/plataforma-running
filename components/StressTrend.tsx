// Stress Trend Component
'use client'

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { TrendingDown, TrendingUp } from 'lucide-react'
import type { HealthMetric } from '@/lib/types'

interface StressTrendProps {
    metrics: HealthMetric[]
    days?: number
}

export function StressTrend({ metrics, days = 7 }: StressTrendProps) {
    // Filter and sort metrics
    const sortedMetrics = [...metrics]
        .filter(m => m.stress_level !== null && m.stress_level !== undefined)
        .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
        .slice(-days)

    if (sortedMetrics.length === 0) {
        return null
    }

    const avgStress = sortedMetrics.reduce((sum, m) => sum + (m.stress_level || 0), 0) / sortedMetrics.length
    const latestStress = sortedMetrics[sortedMetrics.length - 1]?.stress_level || 0
    const trend = sortedMetrics.length >= 2
        ? latestStress - (sortedMetrics[0]?.stress_level || 0)
        : 0

    // Calculate SVG points for sparkline
    const maxStress = Math.max(...sortedMetrics.map(m => m.stress_level || 0), 100)
    const width = 300
    const height = 80
    const padding = 10

    const points = sortedMetrics.map((m, i) => {
        const x = padding + (i / (sortedMetrics.length - 1)) * (width - 2 * padding)
        const y = height - padding - ((m.stress_level || 0) / maxStress) * (height - 2 * padding)
        return `${x},${y}`
    }).join(' ')

    const getStressColor = (stress: number) => {
        if (stress >= 70) return 'text-red-500'
        if (stress >= 40) return 'text-yellow-500'
        return 'text-green-500'
    }

    const getStressLevel = (stress: number) => {
        if (stress >= 70) return 'Alto'
        if (stress >= 40) return 'Moderado'
        return 'Bajo'
    }

    return (
        <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader className="pb-2">
                <CardTitle className="text-sm text-white flex items-center justify-between">
                    <span>Estrés</span>
                    <span className={`text-xs font-normal ${getStressColor(latestStress)}`}>
                        {getStressLevel(latestStress)}
                    </span>
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {/* Main Value */}
                <div className="flex items-baseline gap-2">
                    <span className={`text-3xl font-bold ${getStressColor(latestStress)}`}>
                        {latestStress}
                    </span>
                    <span className="text-xs text-slate-400">/100</span>
                    {trend !== 0 && (
                        <div className={`flex items-center text-xs ${trend < 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {trend < 0 ? <TrendingDown className="h-3 w-3" /> : <TrendingUp className="h-3 w-3" />}
                            <span>{Math.abs(trend).toFixed(0)}</span>
                        </div>
                    )}
                </div>

                {/* Sparkline Chart */}
                <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-16">
                    {/* Grid lines */}
                    <line x1={padding} y1={padding} x2={padding} y2={height - padding} stroke="#475569" strokeWidth="1" />
                    <line x1={padding} y1={height - padding} x2={width - padding} y2={height - padding} stroke="#475569" strokeWidth="1" />

                    {/* Average line */}
                    <line
                        x1={padding}
                        y1={height - padding - (avgStress / maxStress) * (height - 2 * padding)}
                        x2={width - padding}
                        y2={height - padding - (avgStress / maxStress) * (height - 2 * padding)}
                        stroke="#64748b"
                        strokeWidth="1"
                        strokeDasharray="4"
                    />

                    {/* Stress line */}
                    <polyline
                        points={points}
                        fill="none"
                        stroke="#f59e0b"
                        strokeWidth="2"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />

                    {/* Data points */}
                    {sortedMetrics.map((m, i) => {
                        const x = padding + (i / (sortedMetrics.length - 1)) * (width - 2 * padding)
                        const y = height - padding - ((m.stress_level || 0) / maxStress) * (height - 2 * padding)
                        return (
                            <circle
                                key={i}
                                cx={x}
                                cy={y}
                                r="3"
                                fill="#f59e0b"
                                stroke="#1e293b"
                                strokeWidth="2"
                            />
                        )
                    })}
                </svg>

                {/* Stats */}
                <div className="flex justify-between text-xs text-slate-400">
                    <span>Promedio: {avgStress.toFixed(0)}</span>
                    <span>{days}d</span>
                </div>
            </CardContent>
        </Card>
    )
}
