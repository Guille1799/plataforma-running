'use client';

import { useAuth } from '@/lib/auth-context';
import { useRouter } from 'next/navigation';
import { useState, useEffect, useMemo } from 'react';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { formatPace, formatDuration, formatDistance } from '@/lib/formatters';
import {
  Activity,
  TrendingUp,
  Heart,
  Zap,
  Target,
  Clock,
  ArrowRight,
} from 'lucide-react';
import Link from 'next/link';
import { format, subDays, parseISO } from 'date-fns';
import { es } from 'date-fns/locale';
import type { Workout } from '@/lib/types';
import { WorkoutStatsChart } from '@/app/components/workout-stats-chart';
import { HRZonesVisualizer } from '@/app/components/hr-zones-visualizer';
import { HRZonesVisualizerV2 } from '@/app/components/hr-zones-visualizer-v2';
import { DateRangeFilter } from '@/app/components/date-range-filter';
import { AlertCircle, Loader2 } from 'lucide-react';
export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [dateRange, setDateRange] = useState({
    from: subDays(new Date(), 30),
    to: new Date(),
  });

  useEffect(() => {
    loadWorkouts();
  }, []);

  // Filtrar workouts por rango de fechas
  const filteredWorkouts = useMemo(() => {
    return workouts.filter((w) => {
      const workoutDate = parseISO(w.start_time);
      return workoutDate >= dateRange.from && workoutDate <= dateRange.to;
    });
  }, [workouts, dateRange]);

  const loadWorkouts = async () => {
    try {
      const data = await apiClient.getWorkouts(0, 100);
      const workoutsArray = Array.isArray(data) ? data : (data.workouts || []);
      setWorkouts(workoutsArray);
    } catch (err) {
      console.error('Error loading workouts:', err);
      setWorkouts([]);
    } finally {
      setIsLoading(false);
    }
  };

  const totalDistance = filteredWorkouts.reduce((sum, w) => sum + (w.distance_meters || 0), 0);
  const totalTime = filteredWorkouts.reduce((sum, w) => sum + (w.duration_seconds || 0), 0);
  const avgPace = filteredWorkouts.length > 0
    ? filteredWorkouts.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / filteredWorkouts.length
    : 0;
  const avgHR = filteredWorkouts.length > 0
    ? Math.round(filteredWorkouts.reduce((sum, w) => sum + (w.avg_heart_rate || 0), 0) / filteredWorkouts.length)
    : 0;
  const streakDays = calculateStreak(filteredWorkouts);

  function calculateStreak(workouts: Workout[]): number {
    if (workouts.length === 0) return 0;
    const dates = workouts
      .map((w) => new Date(w.start_time).toDateString())
      .filter((date, index, array) => array.indexOf(date) === index)
      .sort((a, b) => new Date(b).getTime() - new Date(a).getTime());

    let streak = 1;
    for (let i = 0; i < dates.length - 1; i++) {
      const diff =
        (new Date(dates[i]).getTime() - new Date(dates[i + 1]).getTime()) /
        (1000 * 60 * 60 * 24);
      if (diff === 1) {
        streak++;
      } else {
        break;
      }
    }
    return streak;
  }

  return (
    <div>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">Dashboard</h1>
        <p className="text-slate-400">Bienvenido {user?.email?.split('@')[0]}</p>
      </div>

      {/* Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-8">
        {/* Total Workouts */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              Entrenamientos
            </CardTitle>
            <Activity className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-8 w-16 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <div className="text-2xl font-bold text-white">
                  {workouts.length}
                </div>
                <p className="text-xs text-slate-500 mt-1">Total completados</p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Total Distance */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              Distancia
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-cyan-500" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-8 w-24 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <div className="text-2xl font-bold text-white">
                  {formatDistance(totalDistance)}
                </div>
                <p className="text-xs text-slate-500 mt-1">Total recorrida</p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Average Heart Rate */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              FC Promedio
            </CardTitle>
            <Heart className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-8 w-16 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <div className="text-2xl font-bold text-white">
                  {avgHR || 0}
                </div>
                <p className="text-xs text-slate-500 mt-1">bpm</p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Average Pace */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              Ritmo Promedio
            </CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-8 w-20 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <div className="text-2xl font-bold text-white">
                  {avgPace > 0 ? formatPace(avgPace) : '--:--'}
                </div>
                <p className="text-xs text-slate-500 mt-1">min/km</p>
              </>
            )}
          </CardContent>
        </Card>

        {/* Streak */}
        <Card className="bg-slate-900 border-slate-800">
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-slate-300">
              Racha
            </CardTitle>
            <Target className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="h-8 w-12 bg-slate-800 rounded animate-pulse" />
            ) : (
              <>
                <div className="text-2xl font-bold text-white">
                  {streakDays}
                </div>
                <p className="text-xs text-slate-500 mt-1">días</p>
              </>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Link href="/workouts">
          <Card className="bg-slate-900 border-slate-800 hover:border-blue-600 cursor-pointer transition-colors">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Entrenamientos</p>
                  <p className="text-lg font-semibold text-white">Ver todos</p>
                </div>
                <ArrowRight className="w-5 h-5 text-blue-500" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/coach">
          <Card className="bg-slate-900 border-slate-800 hover:border-purple-600 cursor-pointer transition-colors">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Coach AI</p>
                  <p className="text-lg font-semibold text-white">Consultar</p>
                </div>
                <ArrowRight className="w-5 h-5 text-purple-500" />
              </div>
            </CardContent>
          </Card>
        </Link>

        <Link href="/training">
          <Card className="bg-slate-900 border-slate-800 hover:border-green-600 cursor-pointer transition-colors">
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-slate-400">Plan de Entrenamiento</p>
                  <p className="text-lg font-semibold text-white">Ver plan</p>
                </div>
                <ArrowRight className="w-5 h-5 text-green-500" />
              </div>
            </CardContent>
          </Card>
        </Link>
      </div>

      {/* Recent Workouts */}
      <Card className="bg-slate-900 border-slate-800">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Entrenamientos Recientes</span>
            <Link href="/workouts">
              <Button variant="outline" size="sm" className="border-slate-700">
                Ver todos
              </Button>
            </Link>
          </CardTitle>
          <CardDescription>Tus últimos 5 entrenamientos</CardDescription>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="space-y-4">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-12 bg-slate-800 rounded animate-pulse" />
              ))}
            </div>
          ) : workouts.length === 0 ? (
            <div className="text-center py-12 text-slate-400">
              <Activity className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg">No hay entrenamientos registrados</p>
              <p className="text-sm">Sincroniza tu Garmin o carga un archivo para comenzar</p>
            </div>
          ) : (
            <div className="space-y-3">
              {workouts.slice(0, 5).map((workout) => (
                <Link
                  key={workout.id}
                  href={`/workouts/${workout.id}`}
                >
                  <div className="p-4 rounded-lg bg-slate-800/50 hover:bg-slate-800 transition-colors">
                    <div className="flex items-center justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="font-medium text-white">
                            {formatDistance(workout.distance_meters)}
                          </span>
                          <span className="text-xs bg-blue-500/20 text-blue-400 px-2 py-1 rounded">
                            {workout.sport_type || 'Run'}
                          </span>
                        </div>
                        <p className="text-sm text-slate-400">
                          {format(new Date(workout.start_time), 'd MMM yyyy', {
                            locale: es,
                          })}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="flex gap-4 text-sm">
                          <div>
                            <p className="text-slate-400 text-xs">Ritmo</p>
                            <p className="font-medium text-white">
                              {formatPace(workout.avg_pace)}
                            </p>
                          </div>
                          <div>
                            <p className="text-slate-400 text-xs">FC</p>
                            <p className="font-medium text-white">
                              {workout.avg_heart_rate} bpm
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Charts Section */}
      <div className="mt-12">
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-white mb-2">Análisis Detallado</h2>
          <p className="text-slate-400">Progresión y estadísticas de entrenamientos</p>
        </div>

        {/* Date Range Filter */}
        <div className="mb-6">
          <DateRangeFilter dateRange={dateRange} onDateRangeChange={setDateRange} />
        </div>

        {/* Workout Stats Charts */}
        {isLoading ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="flex items-center justify-center py-12">
              <div className="flex flex-col items-center gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-blue-500" />
                <p className="text-slate-400">Cargando análisis de entrenamientos...</p>
              </div>
            </CardContent>
          </Card>
        ) : workouts.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="flex items-center justify-center py-12">
              <div className="flex flex-col items-center gap-3 text-center">
                <AlertCircle className="h-8 w-8 text-yellow-500" />
                <div>
                  <p className="text-slate-300 font-semibold">No hay entrenamientos sincronizados</p>
                  <p className="text-slate-400 text-sm">
                    Conecta tu dispositivo Garmin para comenzar a analizar tus entrenamientos
                  </p>
                </div>
                <Link href="/garmin">
                  <Button className="mt-4">Conectar Garmin</Button>
                </Link>
              </div>
            </CardContent>
          </Card>
        ) : filteredWorkouts.length === 0 ? (
          <Card className="bg-slate-900 border-slate-800">
            <CardContent className="flex items-center justify-center py-12">
              <div className="flex flex-col items-center gap-3 text-center">
                <AlertCircle className="h-8 w-8 text-yellow-500" />
                <div>
                  <p className="text-slate-300 font-semibold">No hay entrenamientos en este período</p>
                  <p className="text-slate-400 text-sm">
                    Selecciona otro rango de fechas o ajusta los filtros
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-8">
            <WorkoutStatsChart workouts={filteredWorkouts} weeksToShow={5} />

            {/* HR Zones Info */}
            <HRZonesVisualizerV2 maxHR={185} restingHR={60} currentHR={avgHR || undefined} />
          </div>
        )}
      </div>
    </div>
  );

}
