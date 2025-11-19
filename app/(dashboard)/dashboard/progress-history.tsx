'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workout } from '@/lib/types';
import { formatDistance, formatPace, formatDuration } from '@/lib/formatters';

interface ProgressProps {
  workouts: Workout[];
}

export function ProgressHistory({ workouts }: ProgressProps) {
  const sortedWorkouts = [...workouts].sort((a, b) => 
    new Date(a.start_time).getTime() - new Date(b.start_time).getTime()
  );

  // Calcular progreso semanal
  const getWeeklyProgress = () => {
    const weeks: Record<string, {
      distance: number;
      count: number;
      avgPace: number;
      avgHR: number;
    }> = {};

    sortedWorkouts.forEach(w => {
      const date = new Date(w.start_time);
      const weekStart = new Date(date);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay());
      const weekKey = weekStart.toISOString().split('T')[0];

      if (!weeks[weekKey]) {
        weeks[weekKey] = { distance: 0, count: 0, avgPace: 0, avgHR: 0 };
      }

      weeks[weekKey].distance += (w.distance_meters || 0) / 1000;
      weeks[weekKey].count += 1;
      weeks[weekKey].avgPace += w.avg_pace || 0;
      weeks[weekKey].avgHR += w.avg_heart_rate || 0;
    });

    return Object.entries(weeks)
      .map(([week, data]) => ({
        week,
        distance: Number(data.distance.toFixed(2)),
        count: data.count,
        avgPace: data.avgPace / data.count,
        avgHR: Math.round(data.avgHR / data.count),
        weekDisplay: new Date(week + 'T00:00:00Z').toLocaleDateString('es-ES', {
          month: 'short',
          day: 'numeric',
        }),
      }))
      .slice(-12); // Últimas 12 semanas
  };

  // Calcular mejora de pace
  const getPaceImprovement = () => {
    if (sortedWorkouts.length < 2) return null;

    const first10 = sortedWorkouts.slice(0, Math.min(10, sortedWorkouts.length));
    const last10 = sortedWorkouts.slice(Math.max(0, sortedWorkouts.length - 10));

    const avgFirstPace = first10.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / first10.length;
    const avgLastPace = last10.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / last10.length;

    const improvement = avgFirstPace - avgLastPace;
    const improvementPct = ((improvement / avgFirstPace) * 100).toFixed(1);

    return {
      before: avgFirstPace,
      after: avgLastPace,
      improvement: improvement,
      improvementPct: improvementPct,
    };
  };

  // Calcular milestone badges
  const getMilestones = () => {
    const totalDistance = sortedWorkouts.reduce((sum, w) => sum + ((w.distance_meters || 0) / 1000), 0);
    const totalWorkouts = sortedWorkouts.length;
    const avgPace = sortedWorkouts.length > 0
      ? sortedWorkouts.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / sortedWorkouts.length
      : 0;

    const milestones = [];

    if (totalWorkouts >= 10) milestones.push({ icon: '🏃', label: '10 Entrenamientos', value: totalWorkouts });
    if (totalWorkouts >= 50) milestones.push({ icon: '💪', label: '50 Entrenamientos', value: totalWorkouts });
    if (totalWorkouts >= 100) milestones.push({ icon: '🔥', label: '100 Entrenamientos', value: totalWorkouts });

    if (totalDistance >= 50) milestones.push({ icon: '📏', label: '50 km', value: Math.round(totalDistance) });
    if (totalDistance >= 100) milestones.push({ icon: '🚀', label: '100 km', value: Math.round(totalDistance) });
    if (totalDistance >= 500) milestones.push({ icon: '🏆', label: '500 km', value: Math.round(totalDistance) });

    if (avgPace > 0 && avgPace < 360) milestones.push({ icon: '⚡', label: 'Sub 6 min/km', value: formatPace(avgPace) });
    if (avgPace > 0 && avgPace < 300) milestones.push({ icon: '🔥', label: 'Sub 5 min/km', value: formatPace(avgPace) });

    return milestones;
  };

  const weeklyProgress = getWeeklyProgress();
  const paceImprovement = getPaceImprovement();
  const milestones = getMilestones();

  const maxDistance = Math.max(...weeklyProgress.map(w => w.distance), 1);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">📈 Tu Progreso</h2>

      {/* Improvement Summary */}
      {paceImprovement && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-gradient-to-br from-green-900/50 to-green-800/30 border-green-700">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-green-300 mb-2">Mejora de Pace</p>
                <p className="text-3xl font-bold text-green-400 mb-1">
                  {formatPace(paceImprovement.improvement)}
                </p>
                <p className="text-xs text-green-200">
                  {paceImprovement.improvementPct}% más rápido
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-blue-900/50 to-blue-800/30 border-blue-700">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-blue-300 mb-2">Pace Inicial</p>
                <p className="text-3xl font-bold text-blue-400">
                  {formatPace(paceImprovement.before)}
                </p>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gradient-to-br from-purple-900/50 to-purple-800/30 border-purple-700">
            <CardContent className="pt-6">
              <div className="text-center">
                <p className="text-sm text-purple-300 mb-2">Pace Actual</p>
                <p className="text-3xl font-bold text-purple-400">
                  {formatPace(paceImprovement.after)}
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Milestones */}
      {milestones.length > 0 && (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-lg">🎯 Logros Desbloqueados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-3">
              {milestones.map((milestone, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-700/50 rounded-lg border border-slate-600 text-center hover:border-yellow-500 transition-colors"
                >
                  <div className="text-2xl mb-1">{milestone.icon}</div>
                  <p className="text-xs text-slate-300">{milestone.label}</p>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Weekly Trend */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">📊 Tendencia Semanal</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {weeklyProgress.length > 0 ? (
            <>
              <div className="overflow-x-auto pb-4">
                <div className="flex gap-3 min-w-min">
                  {weeklyProgress.map((week, idx) => (
                    <div key={idx} className="flex flex-col items-center">
                      <div className="w-20">
                        <div className="h-32 bg-slate-700 rounded-t-lg flex items-end justify-center p-1 mb-2">
                          <div
                            className="w-full bg-gradient-to-t from-blue-500 to-blue-400 rounded-sm transition-all"
                            style={{ height: `${(week.distance / maxDistance) * 100}%` }}
                          />
                        </div>
                        <p className="text-xs text-slate-300 text-center font-medium mb-1">
                          {week.weekDisplay}
                        </p>
                        <div className="text-center">
                          <p className="text-sm font-bold text-blue-400">{week.distance}km</p>
                          <p className="text-xs text-slate-500">{week.count} entrenamientos</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-700">
                <div>
                  <p className="text-sm text-slate-400 mb-1">Semana Más Activa</p>
                  <p className="text-2xl font-bold text-green-400">
                    {Math.max(...weeklyProgress.map(w => w.distance))}km
                  </p>
                </div>
                <div>
                  <p className="text-sm text-slate-400 mb-1">Semana Promedio</p>
                  <p className="text-2xl font-bold text-blue-400">
                    {(weeklyProgress.reduce((sum, w) => sum + w.distance, 0) / weeklyProgress.length).toFixed(1)}km
                  </p>
                </div>
              </div>
            </>
          ) : (
            <p className="text-slate-400 text-center py-8">No hay datos suficientes aún</p>
          )}
        </CardContent>
      </Card>

      {/* Monthly Summary */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">📅 Resumen por Mes</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {Object.entries(
              sortedWorkouts.reduce((acc, w) => {
                const date = new Date(w.start_time);
                const month = date.toLocaleDateString('es-ES', { month: 'long', year: 'numeric' });
                if (!acc[month]) {
                  acc[month] = { workouts: 0, distance: 0, time: 0 };
                }
                acc[month].workouts += 1;
                acc[month].distance += (w.distance_meters || 0) / 1000;
                acc[month].time += w.duration_seconds || 0;
                return acc;
              }, {} as Record<string, any>)
            )
              .reverse()
              .map(([month, data]) => (
                <div key={month} className="p-4 bg-slate-700/50 rounded-lg border border-slate-600">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="text-sm font-semibold text-white capitalize">{month}</h4>
                    <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                      {data.workouts} entrenamientos
                    </span>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Distancia</p>
                      <p className="text-lg font-bold text-blue-400">
                        {data.distance.toFixed(1)}km
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Tiempo</p>
                      <p className="text-lg font-bold text-green-400">
                        {formatDuration(data.time)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Pace Prom</p>
                      <p className="text-lg font-bold text-purple-400">
                        {formatPace(
                          sortedWorkouts
                            .filter(w => 
                              new Date(w.start_time).toLocaleDateString('es-ES', { month: 'long', year: 'numeric' }) === month
                            )
                            .reduce((sum, w) => sum + (w.avg_pace || 0), 0) /
                          data.workouts
                        )}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
