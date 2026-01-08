'use client'

import { useState, useEffect } from 'react'
import { useAuth } from '@/lib/auth-context'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { apiClient } from '@/lib/api-client'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import {
  formatPace,
  formatDuration,
  formatDistance,
  formatDate,
} from '@/lib/formatters'
import { Activity } from 'lucide-react'
import type { Workout } from '@/lib/types'

export default function WorkoutsPage() {
  const { user } = useAuth()
  const router = useRouter()
  const [workouts, setWorkouts] = useState<Workout[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  // Filter states
  const [searchQuery, setSearchQuery] = useState('')
  const [sportFilter, setSportFilter] = useState('all')
  const [dateFrom, setDateFrom] = useState('')
  const [dateTo, setDateTo] = useState('')
  const [sortBy, setSortBy] = useState('date-desc')
  const [currentPage, setCurrentPage] = useState(1)
  const itemsPerPage = 100

  // Pagination
  const filteredWorkouts = workouts
    .filter((w) => {
      if (sportFilter !== 'all' && w.sport_type !== sportFilter) return false
      if (searchQuery && !w.sport_type?.toLowerCase().includes(searchQuery.toLowerCase()))
        return false
      if (dateFrom && new Date(w.start_time) < new Date(dateFrom)) return false
      if (dateTo && new Date(w.start_time) > new Date(dateTo)) return false
      return true
    })
    .sort((a, b) => {
      switch (sortBy) {
        case 'date-asc':
          return new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
        case 'date-desc':
          return new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
        case 'distance-desc':
          return (b.distance_meters || 0) - (a.distance_meters || 0)
        case 'distance-asc':
          return (a.distance_meters || 0) - (b.distance_meters || 0)
        case 'pace-asc':
          return (a.avg_pace || 0) - (b.avg_pace || 0)
        case 'pace-desc':
          return (b.avg_pace || 0) - (a.avg_pace || 0)
        default:
          return 0
      }
    })

  const totalPages = Math.ceil(filteredWorkouts.length / itemsPerPage)
  const paginatedWorkouts = filteredWorkouts.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  useEffect(() => {
    loadWorkouts()
  }, [])

  const loadWorkouts = async () => {
    try {
      setIsLoading(true)
      const data = await apiClient.getWorkouts()
      const workoutsArray = Array.isArray(data) ? data : data.workouts || []
      setWorkouts(workoutsArray)
    } catch (err: any) {
      console.error('Error loading workouts:', err)
      setError('Error al cargar entrenamientos')
    } finally {
      setIsLoading(false)
    }
  }

  const getSportTypes = () => {
    return Array.from(new Set(workouts.map((w) => w.sport_type).filter(Boolean)))
  }

  const stats = {
    total: filteredWorkouts.length,
    distance: filteredWorkouts.reduce((sum, w) => sum + (w.distance_meters || 0), 0) / 1000,
    time: filteredWorkouts.reduce((sum, w) => sum + (w.duration_seconds || 0), 0),
    avgPace: filteredWorkouts.length > 0
      ? filteredWorkouts.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / filteredWorkouts.length
      : 0,
  }

  return (
    <div className="min-h-screen bg-slate-950 p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">Mis Entrenamientos</h1>
        <p className="text-slate-400">
          {filteredWorkouts.length} entrenamientos ({stats.distance.toFixed(1)} km)
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400">Entrenamientos</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{stats.total}</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400">Distancia Total</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{stats.distance.toFixed(1)} km</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400">Tiempo Total</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{formatDuration(stats.time)}</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400">Ritmo Promedio</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-2xl font-bold text-white">{formatPace(stats.avgPace)}</p>
          </CardContent>
        </Card>
      </div>

      {/* Filters */}
      <Card className="bg-slate-900 border-slate-800 mb-8 p-6">
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <div>
            <label className="text-sm text-slate-400 mb-2 block">Buscar</label>
            <Input
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value)
                setCurrentPage(1)
              }}
              placeholder="Tipo de deporte..."
              className="bg-slate-800 border-slate-700"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-2 block">Tipo</label>
            <select
              value={sportFilter}
              onChange={(e) => {
                setSportFilter(e.target.value)
                setCurrentPage(1)
              }}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-slate-200 text-sm"
            >
              <option value="all">Todos</option>
              {getSportTypes().map((type) => (
                <option key={type} value={type}>
                  {type}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-2 block">Desde</label>
            <Input
              type="date"
              value={dateFrom}
              onChange={(e) => {
                setDateFrom(e.target.value)
                setCurrentPage(1)
              }}
              className="bg-slate-800 border-slate-700"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-2 block">Hasta</label>
            <Input
              type="date"
              value={dateTo}
              onChange={(e) => {
                setDateTo(e.target.value)
                setCurrentPage(1)
              }}
              className="bg-slate-800 border-slate-700"
            />
          </div>

          <div>
            <label className="text-sm text-slate-400 mb-2 block">Ordenar por</label>
            <select
              value={sortBy}
              onChange={(e) => {
                setSortBy(e.target.value)
                setCurrentPage(1)
              }}
              className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-md text-slate-200 text-sm"
            >
              <option value="date-desc">Más reciente</option>
              <option value="date-asc">Más antiguo</option>
              <option value="distance-desc">Mayor distancia</option>
              <option value="distance-asc">Menor distancia</option>
              <option value="pace-asc">Ritmo más rápido</option>
              <option value="pace-desc">Ritmo más lento</option>
            </select>
          </div>
        </div>
      </Card>

      {/* Workouts List */}
      {isLoading ? (
        <div className="text-center py-12">
          <div className="animate-pulse">
            <p className="text-slate-400">Cargando entrenamientos...</p>
          </div>
        </div>
      ) : error ? (
        <Card className="bg-slate-900 border-slate-800 p-6">
          <p className="text-red-400">{error}</p>
          <Button onClick={loadWorkouts} className="mt-4 bg-blue-600">
            Reintentar
          </Button>
        </Card>
      ) : filteredWorkouts.length === 0 ? (
        <Card className="bg-slate-900 border-slate-800 p-12 text-center">
          <Activity className="w-12 h-12 mx-auto mb-4 opacity-50 text-slate-600" />
          <p className="text-slate-400 mb-4">No hay entrenamientos para mostrar</p>
          <Button className="bg-blue-600">Sincronizar Garmin</Button>
        </Card>
      ) : (
        <>
          <div className="space-y-4 mb-8">
            {paginatedWorkouts.map((workout) => (
              <Link key={workout.id} href={`/workouts/${workout.id}`}>
                <Card className="bg-slate-900 border-slate-800 hover:border-blue-600 cursor-pointer transition-colors">
                  <CardContent className="p-6">
                    <div className="flex items-center justify-between">
                      {/* Left */}
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <span className="text-2xl">{getWorkoutIcon(workout.sport_type)}</span>
                          <div>
                            <h3 className="text-lg font-semibold text-white capitalize">
                              {workout.sport_type?.replace(/_/g, ' ')}
                            </h3>
                            <p className="text-sm text-slate-400">
                              {formatDate(new Date(workout.start_time))}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Right */}
                      <div className="grid grid-cols-4 gap-8 text-right">
                        <div>
                          <p className="text-xs text-slate-500 mb-1">Distancia</p>
                          <p className="text-lg font-semibold text-white">
                            {formatDistance(workout.distance_meters || 0)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 mb-1">Ritmo</p>
                          <p className="text-lg font-semibold text-white">
                            {formatPace(workout.avg_pace || 0)}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 mb-1">FC Promedio</p>
                          <p className="text-lg font-semibold text-white">
                            {workout.avg_heart_rate ? `${Math.round(workout.avg_heart_rate)} bpm` : '-'}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-slate-500 mb-1">Duración</p>
                          <p className="text-lg font-semibold text-white">
                            {formatDuration(workout.duration_seconds || 0)}
                          </p>
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </Link>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex justify-center items-center gap-4">
              <Button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                variant="outline"
                className="border-slate-700"
              >
                Anterior
              </Button>
              <span className="text-slate-400">
                Página {currentPage} de {totalPages}
              </span>
              <Button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                variant="outline"
                className="border-slate-700"
              >
                Siguiente
              </Button>
            </div>
          )}
        </>
      )}
    </div>
  )
}

function getWorkoutIcon(type?: string): string {
  const icons: Record<string, string> = {
    running: '🏃',
    trail_running: '🥾',
    cycling: '🚴',
    swimming: '🏊',
    walking: '🚶',
    gym: '🏋️',
    yoga: '🧘',
    pilates: '🤸',
  }
  return icons[type || 'running'] || '🏃'
}
