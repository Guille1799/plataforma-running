'use client'

import { useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from 'sonner'
import { apiClient } from '@/lib/api-client'
import { Watch, Smartphone, Apple, RefreshCw, Upload, Link as LinkIcon, CheckCircle2, XCircle } from 'lucide-react'

export default function DevicesPage() {
  const [appleHealthFile, setAppleHealthFile] = useState<File | null>(null)
  const queryClient = useQueryClient()

  // Query user's connected devices status (from health metrics)
  const { data: healthData } = useQuery({
    queryKey: ['health', 'today'],
    queryFn: () => apiClient.getHealthToday(),
  })

  // Garmin Sync
  const garminSyncMutation = useMutation({
    mutationFn: () => apiClient.syncGarminHealth(7),
    onSuccess: () => {
      toast.success('✅ Datos de Garmin sincronizados')
      queryClient.invalidateQueries({ queryKey: ['health'] })
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.detail || 'Garmin no conectado'}`)
    },
  })

  // Google Fit Connect
  const googleFitConnectMutation = useMutation({
    mutationFn: async () => {
      const response = await apiClient.connectGoogleFit()
      window.location.href = response.auth_url
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  // Google Fit Sync
  const googleFitSyncMutation = useMutation({
    mutationFn: () => apiClient.syncGoogleFitHealth(7),
    onSuccess: () => {
      toast.success('✅ Datos de Google Fit sincronizados')
      queryClient.invalidateQueries({ queryKey: ['health'] })
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.detail || 'Google Fit no conectado'}`)
    },
  })

  // Apple Health Import
  const appleHealthImportMutation = useMutation({
    mutationFn: () => {
      if (!appleHealthFile) throw new Error('No file selected')
      return apiClient.importAppleHealth(appleHealthFile, 30)
    },
    onSuccess: (data) => {
      toast.success(`✅ Importados ${data.metrics_imported} días de datos de Apple Health`)
      queryClient.invalidateQueries({ queryKey: ['health'] })
      setAppleHealthFile(null)
    },
    onError: (error: any) => {
      toast.error(`Error: ${error.response?.data?.detail || error.message}`)
    },
  })

  const isGarminConnected = healthData?.source === 'garmin'
  const isGoogleFitConnected = healthData?.source === 'google_fit'
  const isAppleHealthConnected = healthData?.source === 'apple_health'

  return (
    <div className="space-y-6 p-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-3xl font-bold mb-2">Dispositivos Conectados</h1>
        <p className="text-muted-foreground">
          Conecta tu reloj o app de salud para sincronizar métricas automáticamente
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        {/* Garmin */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Watch className="h-5 w-5" />
              Garmin
            </CardTitle>
            <CardDescription>
              Garmin Forerunner, Fenix, etc.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Estado:</span>
              {isGarminConnected ? (
                <Badge variant="default" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  Conectado
                </Badge>
              ) : (
                <Badge variant="secondary" className="gap-1">
                  <XCircle className="h-3 w-3" />
                  Desconectado
                </Badge>
              )}
            </div>

            <div className="space-y-2 text-xs text-muted-foreground">
              <p>✓ HRV y Frecuencia Cardíaca</p>
              <p>✓ Body Battery</p>
              <p>✓ Sueño (duración + fases)</p>
              <p>✓ Estrés</p>
              <p>✓ Pasos y calorías</p>
            </div>

            {isGarminConnected ? (
              <Button
                onClick={() => garminSyncMutation.mutate()}
                disabled={garminSyncMutation.isPending}
                variant="outline"
                className="w-full"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${garminSyncMutation.isPending ? 'animate-spin' : ''}`} />
                {garminSyncMutation.isPending ? 'Sincronizando...' : 'Sincronizar Ahora'}
              </Button>
            ) : (
              <Button variant="default" className="w-full" asChild>
                <a href="http://127.0.0.1:8000/garmin/connect" target="_blank">
                  <LinkIcon className="h-4 w-4 mr-2" />
                  Conectar Garmin
                </a>
              </Button>
            )}
          </CardContent>
        </Card>

        {/* Google Fit */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Smartphone className="h-5 w-5" />
              Google Fit
            </CardTitle>
            <CardDescription>
              Xiaomi Mi Band, Amazfit (via Zepp)
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Estado:</span>
              {isGoogleFitConnected ? (
                <Badge variant="default" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  Conectado
                </Badge>
              ) : (
                <Badge variant="secondary" className="gap-1">
                  <XCircle className="h-3 w-3" />
                  Desconectado
                </Badge>
              )}
            </div>

            <div className="space-y-2 text-xs text-muted-foreground">
              <p>✓ Frecuencia Cardíaca en reposo</p>
              <p>✓ Sueño (duración + fases)</p>
              <p>✓ Pasos y calorías</p>
              <p>✓ Minutos activos</p>
              <p className="text-yellow-500">⚠ No soporta HRV ni Body Battery</p>
            </div>

            {isGoogleFitConnected ? (
              <Button
                onClick={() => googleFitSyncMutation.mutate()}
                disabled={googleFitSyncMutation.isPending}
                variant="outline"
                className="w-full"
              >
                <RefreshCw className={`h-4 w-4 mr-2 ${googleFitSyncMutation.isPending ? 'animate-spin' : ''}`} />
                {googleFitSyncMutation.isPending ? 'Sincronizando...' : 'Sincronizar Ahora'}
              </Button>
            ) : (
              <Button
                onClick={() => googleFitConnectMutation.mutate()}
                disabled={googleFitConnectMutation.isPending}
                variant="default"
                className="w-full"
              >
                <LinkIcon className="h-4 w-4 mr-2" />
                {googleFitConnectMutation.isPending ? 'Conectando...' : 'Conectar Google Fit'}
              </Button>
            )}

            <div className="text-xs text-muted-foreground border-t pt-2">
              <p className="font-semibold">Setup Xiaomi/Amazfit:</p>
              <ol className="list-decimal list-inside space-y-1 mt-1">
                <li>Instala app Zepp Life</li>
                <li>Conecta tu band</li>
                <li>Sincroniza con Google Fit en ajustes</li>
                <li>Conecta aquí</li>
              </ol>
            </div>
          </CardContent>
        </Card>

        {/* Apple Health */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Apple className="h-5 w-5" />
              Apple Health
            </CardTitle>
            <CardDescription>
              iPhone + Apple Watch
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Estado:</span>
              {isAppleHealthConnected ? (
                <Badge variant="default" className="gap-1">
                  <CheckCircle2 className="h-3 w-3" />
                  Datos importados
                </Badge>
              ) : (
                <Badge variant="secondary" className="gap-1">
                  <XCircle className="h-3 w-3" />
                  Sin datos
                </Badge>
              )}
            </div>

            <div className="space-y-2 text-xs text-muted-foreground">
              <p>✓ HRV y Frecuencia Cardíaca</p>
              <p>✓ Sueño (duración)</p>
              <p>✓ Pasos y calorías</p>
              <p className="text-yellow-500">⚠ Importación manual (no automática)</p>
            </div>

            <div className="space-y-2">
              <Label htmlFor="apple-file" className="text-sm">
                Exportar desde app Salud de iPhone
              </Label>
              <Input
                id="apple-file"
                type="file"
                accept=".xml,.zip"
                onChange={(e) => setAppleHealthFile(e.target.files?.[0] || null)}
              />
            </div>

            <Button
              onClick={() => appleHealthImportMutation.mutate()}
              disabled={!appleHealthFile || appleHealthImportMutation.isPending}
              variant="default"
              className="w-full"
            >
              <Upload className="h-4 w-4 mr-2" />
              {appleHealthImportMutation.isPending ? 'Importando...' : 'Importar Datos'}
            </Button>

            <div className="text-xs text-muted-foreground border-t pt-2">
              <p className="font-semibold">Cómo exportar:</p>
              <ol className="list-decimal list-inside space-y-1 mt-1">
                <li>Abre app Salud</li>
                <li>Toca tu foto de perfil</li>
                <li>Exportar todos los datos</li>
                <li>Sube export.xml aquí</li>
              </ol>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Card */}
      <Card className="bg-blue-50 dark:bg-blue-950 border-blue-200 dark:border-blue-800">
        <CardHeader>
          <CardTitle className="text-blue-900 dark:text-blue-100">
            💡 Recomendaciones
          </CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2 text-blue-800 dark:text-blue-200">
          <p>
            <strong>Mejor opción:</strong> Garmin (métricas más completas, sincronización automática)
          </p>
          <p>
            <strong>Budget-friendly:</strong> Xiaomi Mi Band + Google Fit (buena relación calidad-precio)
          </p>
          <p>
            <strong>Ya tienes iPhone?</strong> Apple Watch con importación manual
          </p>
          <p className="text-xs text-muted-foreground mt-4">
            Los datos se sincronizan automáticamente cada noche. También puedes sincronizar manualmente cuando quieras.
          </p>
        </CardContent>
      </Card>
    </div>
  )
}
