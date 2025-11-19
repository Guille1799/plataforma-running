'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api-client'
import { Battery, TrendingUp, TrendingDown, Minus } from 'lucide-react'
import Link from 'next/link'

export function ReadinessBadge() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['readiness'],
    queryFn: () => apiClient.getReadinessScore(),
    retry: 1,
    refetchInterval: 5 * 60 * 1000, // Refresh every 5 minutes
  })

  if (isLoading) {
    return (
      <Card className="hover:bg-accent/50 transition-colors">
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-muted animate-pulse" />
            <div className="space-y-2 flex-1">
              <div className="h-4 bg-muted rounded w-24 animate-pulse" />
              <div className="h-3 bg-muted rounded w-32 animate-pulse" />
            </div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (error || !data) {
    return (
      <Card className="hover:bg-accent/50 transition-colors border-dashed">
        <CardContent className="p-4">
          <Link href="/health/devices" className="flex items-center gap-3">
            <div className="h-12 w-12 rounded-full bg-muted flex items-center justify-center">
              <Battery className="h-6 w-6 text-muted-foreground" />
            </div>
            <div>
              <p className="font-semibold text-sm">Sin datos de salud</p>
              <p className="text-xs text-muted-foreground">Conecta un dispositivo →</p>
            </div>
          </Link>
        </CardContent>
      </Card>
    )
  }

  const { score, confidence, trend } = data
  const scoreColor = score >= 75 ? 'text-green-500' : score >= 60 ? 'text-yellow-500' : 'text-red-500'
  const bgColor = score >= 75 ? 'bg-green-500/10' : score >= 60 ? 'bg-yellow-500/10' : 'bg-red-500/10'
  const borderColor = score >= 75 ? 'border-green-500/20' : score >= 60 ? 'border-yellow-500/20' : 'border-red-500/20'

  const confidenceBadgeMap: Record<string, { label: string; variant: 'default' | 'secondary' | 'outline' }> = {
    high: { label: 'Alta precisión', variant: 'default' as const },
    medium: { label: 'Precisión media', variant: 'secondary' as const },
    low: { label: 'Datos limitados', variant: 'outline' as const },
  }
  
  const confidenceBadge = confidenceBadgeMap[confidence] || confidenceBadgeMap.low

  const trendIcon = trend === 'improving' ? (
    <TrendingUp className="h-3 w-3 text-green-500" />
  ) : trend === 'declining' ? (
    <TrendingDown className="h-3 w-3 text-red-500" />
  ) : (
    <Minus className="h-3 w-3 text-muted-foreground" />
  )

  return (
    <Link href="/health">
      <Card className={`hover:bg-accent/50 transition-colors ${borderColor} border`}>
        <CardContent className="p-4">
          <div className="flex items-center gap-3">
            {/* Circular Score */}
            <div className="relative h-12 w-12">
              <svg className="transform -rotate-90 h-12 w-12">
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                  className="text-muted"
                />
                <circle
                  cx="24"
                  cy="24"
                  r="20"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                  strokeDasharray={`${(score / 100) * 125.6} 125.6`}
                  className={scoreColor}
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className={`text-sm font-bold ${scoreColor}`}>{score}</span>
              </div>
            </div>

            {/* Info */}
            <div className="flex-1 space-y-1">
              <div className="flex items-center gap-2">
                <p className="font-semibold text-sm">Readiness</p>
                {trendIcon}
              </div>
              <Badge variant={confidenceBadge.variant} className="text-xs">
                {confidenceBadge.label}
              </Badge>
            </div>

            {/* Status Indicator */}
            <div className={`h-2 w-2 rounded-full ${bgColor} ${scoreColor.replace('text-', 'bg-')}`} />
          </div>
        </CardContent>
      </Card>
    </Link>
  )
}
