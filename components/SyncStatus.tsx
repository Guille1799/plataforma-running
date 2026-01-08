'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { RefreshCw, CheckCircle, AlertCircle, Clock } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { formatDistanceToNow } from 'date-fns'
import { es } from 'date-fns/locale'

export function SyncStatus() {
    const { data: profile } = useQuery({
        queryKey: ['profile'],
        queryFn: () => apiClient.getProfile()
    })

    const { data: healthToday } = useQuery({
        queryKey: ['health', 'today'],
        queryFn: () => apiClient.getHealthToday()
    })

    if (!profile) return null

    const lastSync = profile.last_garmin_sync
    const hasHealthData = healthToday && Object.keys(healthToday).length > 1 // more than just 'date'

    return (
        <Card className="border-slate-700 bg-slate-800/50">
            <CardHeader className="pb-3">
                <CardTitle className="text-sm text-white flex items-center justify-between">
                    <span className="flex items-center gap-2">
                        <Clock className="h-4 w-4 text-blue-400" />
                        Estado de Sincronización
                    </span>
                    {hasHealthData ? (
                        <Badge variant="default" className="text-xs">
                            <CheckCircle className="h-3 w-3 mr-1" />
                            Activo
                        </Badge>
                    ) : (
                        <Badge variant="outline" className="text-xs">
                            <AlertCircle className="h-3 w-3 mr-1" />
                            Sin datos
                        </Badge>
                    )}
                </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
                {lastSync ? (
                    <>
                        <div className="text-xs text-slate-400">
                            Última sincronización Garmin:
                        </div>
                        <div className="text-sm font-medium text-white">
                            {formatDistanceToNow(new Date(lastSync), { addSuffix: true, locale: es })}
                        </div>
                    </>
                ) : (
                    <div className="text-xs text-slate-500">
                        No se ha sincronizado aún
                    </div>
                )}

                {healthToday?.date && (
                    <div className="text-xs text-slate-500 pt-2 border-t border-slate-700">
                        Datos de salud: {new Date(healthToday.date).toLocaleDateString('es-ES')}
                    </div>
                )}
            </CardContent>
        </Card>
    )
}
