'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-context';
import { apiClient } from '@/lib/api-client';
import type { Workout } from '@/lib/types';
import { formatDistance, formatDuration, formatPace } from '@/lib/formatters';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function DashboardPage() {
  const { user } = useAuth();
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadWorkouts = async () => {
      try {
        const data = await apiClient.getWorkouts(0, 1000);
        const workoutsArray = Array.isArray(data) ? data : (data.workouts || []);
        setWorkouts(workoutsArray);
      } catch (err) {
        console.error('Error loading workouts:', err);
        setWorkouts([]);
      } finally {
        setIsLoading(false);
      }
    };

    loadWorkouts();
  }, []);

  // Calculate metrics
  const totalDistance = workouts.reduce((sum, w) => sum + (w.distance_meters || 0), 0);
  const totalDuration = workouts.reduce((sum, w) => sum + (w.duration_seconds || 0), 0);
  const avgPace = workouts.length > 0
    ? (workouts.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / workouts.length) * 60
    : 0;

  // This week (últimos 7 días)
  const now = new Date();
  const weekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
  const thisWeekWorkouts = workouts.filter(w => new Date(w.start_time) > weekAgo);
  const thisWeekDistance = thisWeekWorkouts.reduce((sum, w) => sum + (w.distance_meters || 0), 0);
  const thisWeekCount = thisWeekWorkouts.length;

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Welcome Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            ¡Bienvenido de vuelta! 👟
          </h1>
          <p className="text-slate-400">
            {user?.email}
          </p>
        </div>

        {/* Stats Grid - This Week */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Entrenamientos
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">{thisWeekCount}</div>
              <p className="text-xs text-slate-500 mt-1">Esta semana</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Distancia Total
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">
                {formatDistance(thisWeekDistance)}
              </div>
              <p className="text-xs text-slate-500 mt-1">Esta semana</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Tiempo Total
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-400">
                {isLoading ? '--:--' : formatDuration(
                  thisWeekWorkouts.reduce((sum, w) => sum + (w.duration_seconds || 0), 0)
                )}
              </div>
              <p className="text-xs text-slate-500 mt-1">Esta semana</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400">
                Pace Promedio
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-400">
                {isLoading ? '--:--' : formatPace(avgPace)}
              </div>
              <p className="text-xs text-slate-500 mt-1">min/km</p>
            </CardContent>
          </Card>
        </div>

        {/* Lifetime Stats */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-white">Estadísticas Totales</CardTitle>
          </CardHeader>
          <CardContent className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-slate-400 text-sm mb-1">Total Entrenamientos</p>
              <p className="text-2xl font-bold text-blue-400">{workouts.length}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">Distancia Total</p>
              <p className="text-2xl font-bold text-green-400">{formatDistance(totalDistance)}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">Tiempo Total</p>
              <p className="text-2xl font-bold text-purple-400">{formatDuration(totalDuration)}</p>
            </div>
            <div>
              <p className="text-slate-400 text-sm mb-1">Pace Promedio (Histórico)</p>
              <p className="text-2xl font-bold text-orange-400">{formatPace(avgPace)}</p>
            </div>
          </CardContent>
        </Card>

        {/* Recent Workouts */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-white">Últimos Entrenamientos</CardTitle>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <p className="text-slate-400">Cargando...</p>
            ) : workouts.length === 0 ? (
              <p className="text-slate-400">No hay entrenamientos sincronizados aún. ¡Conecta tu Garmin!</p>
            ) : (
              <div className="space-y-3">
                {workouts.slice(0, 5).map(w => (
                  <div key={w.id} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                    <div>
                      <p className="text-white font-semibold">{w.sport_type}</p>
                      <p className="text-sm text-slate-400">{new Date(w.start_time).toLocaleDateString()}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-green-400 font-semibold">{formatDistance(w.distance_meters)}</p>
                      <p className="text-sm text-slate-400">{formatPace((w.avg_pace || 0) * 60)}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
