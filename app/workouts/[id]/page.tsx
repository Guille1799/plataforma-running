'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter, useParams } from 'next/navigation'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import {
  formatPace,
  formatDuration,
  formatDistance,
  formatDate,
} from '@/lib/formatters'
import { ArrowLeft, Heart, Zap, Clock, MapPin, Flame } from 'lucide-react'
import type { Workout } from '@/lib/types'

export default function WorkoutDetailPage() {
  const { user } = useAuth()
  const router = useRouter()
  const params = useParams()
  const workoutId = parseInt(params.id as string)

  const [workout, setWorkout] = useState<Workout | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadWorkout()
  }, [workoutId])

  const loadWorkout = async () => {
    try {
      setIsLoading(true)
      const allWorkouts = await apiClient.getWorkouts()
      const workoutsArray = Array.isArray(allWorkouts)
        ? allWorkouts
        : allWorkouts.workouts || []
      const found = workoutsArray.find((w) => w.id === workoutId)
      if (!found) {
        setError('Entrenamiento no encontrado')
      } else {
        setWorkout(found)
      }
    } catch (err: any) {
      console.error('Error loading workout:', err)
      setError('Error al cargar el entrenamiento')
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <div className="text-center py-12">
          <div className="animate-pulse">
            <p className="text-slate-400">Cargando entrenamiento...</p>
          </div>
        </div>
      </div>
    )
  }

  if (error || !workout) {
    return (
      <div className="min-h-screen bg-slate-950 p-6">
        <Button
          onClick={() => router.back()}
          variant="outline"
          className="mb-6 border-slate-700"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver
        </Button>
        <Card className="bg-slate-900 border-slate-800 p-6">
          <p className="text-red-400">{error || 'Entrenamiento no encontrado'}</p>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      {/* Header */}
      <div className="mb-6">
        <Button
          onClick={() => router.back()}
          variant="outline"
          className="mb-4 border-slate-700"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Volver
        </Button>

        <div>
          <h1 className="text-4xl font-bold text-white mb-2 capitalize">
            {workout.sport_type?.replace(/_/g, ' ')}
          </h1>
          <p className="text-slate-400">
            {formatDate(new Date(workout.start_time))}
          </p>
        </div>
      </div>

      {/* Main Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        {/* Distance */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <MapPin className="w-4 h-4" />
              Distancia
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-blue-400">
              {formatDistance(workout.distance_meters || 0)}
            </p>
          </CardContent>
        </Card>

        {/* Duration */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Clock className="w-4 h-4" />
              Duración
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-green-400">
              {formatDuration(workout.duration_seconds || 0)}
            </p>
          </CardContent>
        </Card>

        {/* Average Pace */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Zap className="w-4 h-4" />
              Ritmo Promedio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-purple-400">
              {formatPace(workout.avg_pace || 0)}
            </p>
          </CardContent>
        </Card>

        {/* Heart Rate */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Heart className="w-4 h-4" />
              FC Promedio
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-3xl font-bold text-red-400">
              {workout.avg_heart_rate ? `${Math.round(workout.avg_heart_rate)}` : '-'}
            </p>
            <p className="text-sm text-slate-500 mt-1">bpm</p>
          </CardContent>
        </Card>
      </div>

      {/* Secondary Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        {/* Max Speed */}
        {workout.max_speed && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Velocidad Máxima
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-white">
                {(workout.max_speed * 3.6).toFixed(2)} km/h
              </p>
            </CardContent>
          </Card>
        )}

        {/* Elevation */}
        {workout.elevation_gain && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Ganancia de Elevación
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-white">
                {Math.round(workout.elevation_gain)} m
              </p>
            </CardContent>
          </Card>
        )}

        {/* Calories */}
        {workout.calories && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Flame className="w-4 h-4" />
                Calorías
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-orange-400">
                {Math.round(workout.calories)}
              </p>
            </CardContent>
          </Card>
        )}

        {/* Cadence */}
        {workout.avg_cadence && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Cadencia Promedio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-white">
                {Math.round(workout.avg_cadence)} rpm
              </p>
            </CardContent>
          </Card>
        )}

        {/* Max HR */}
        {workout.max_heart_rate && (
          <Card className="bg-slate-900 border-slate-800">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                FC Máxima
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-bold text-red-400">
                {Math.round(workout.max_heart_rate)} bpm
              </p>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Details Card */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle>Detalles del Entrenamiento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <p className="text-sm text-slate-500 mb-2">Tipo de Deporte</p>
              <p className="text-lg font-semibold text-white capitalize">
                {workout.sport_type?.replace(/_/g, ' ')}
              </p>
            </div>

            <div>
              <p className="text-sm text-slate-500 mb-2">Hora de Inicio</p>
              <p className="text-lg font-semibold text-white">
                {new Date(workout.start_time).toLocaleTimeString('es-ES', {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </p>
            </div>

            {workout.avg_stance_time && (
              <div>
                <p className="text-sm text-slate-500 mb-2">Tiempo de Apoyo Promedio</p>
                <p className="text-lg font-semibold text-white">
                  {workout.avg_stance_time.toFixed(2)} ms
                </p>
              </div>
            )}

            {workout.avg_vertical_oscillation && (
              <div>
                <p className="text-sm text-slate-500 mb-2">Oscilación Vertical Promedio</p>
                <p className="text-lg font-semibold text-white">
                  {workout.avg_vertical_oscillation.toFixed(2)} cm
                </p>
              </div>
            )}

            {workout.left_right_balance && (
              <div>
                <p className="text-sm text-slate-500 mb-2">Balance Izq/Der</p>
                <p className="text-lg font-semibold text-white">
                  {workout.left_right_balance.toFixed(1)} %
                </p>
              </div>
            )}

            {workout.file_name && (
              <div>
                <p className="text-sm text-slate-500 mb-2">Archivo</p>
                <p className="text-lg font-semibold text-white break-all">
                  {workout.file_name}
                </p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Garmin Info */}
      {workout.garmin_activity_id && (
        <Card className="bg-slate-900 border-slate-800 mt-4">
          <CardHeader>
            <CardTitle className="text-sm">Información de Garmin</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-400">Activity ID: {workout.garmin_activity_id}</p>
          </CardContent>
        </Card>
      )}

      {/* Action Buttons */}
      <div className="mt-8 flex gap-4">
        <Button
          onClick={() => router.push(`/workouts/${workoutId}/analysis`)}
          className="bg-blue-600 hover:bg-blue-700"
        >
          Ver Análisis Detallado
        </Button>
        <Button variant="outline" className="border-slate-700">
          Compartir
        </Button>
      </div>
    </div>
  )
}
