'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workout } from '@/lib/types';
import { formatDistance, formatPace } from '@/lib/formatters';

interface ChartsProps {
  workouts: Workout[];
}

export function WorkoutCharts({ workouts }: ChartsProps) {
  // Calcular workouts por semana
  const getWeekStats = () => {
    const weeks: Record<string, { distance: number; count: number; pace: number[] }> = {};
    
    const today = new Date();
    const last7Days = Array.from({ length: 7 }, (_, i) => {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      return date;
    }).reverse();

    last7Days.forEach(date => {
      const weekKey = date.toLocaleDateString('es-ES', { weekday: 'short' });
      weeks[weekKey] = { distance: 0, count: 0, pace: [] };
    });

    workouts.forEach(w => {
      const wDate = new Date(w.start_time);
      const dayKey = wDate.toLocaleDateString('es-ES', { weekday: 'short' });
      
      if (weeks[dayKey]) {
        weeks[dayKey].distance += (w.distance_meters || 0) / 1000;
        weeks[dayKey].count += 1;
        if (w.avg_pace) weeks[dayKey].pace.push(w.avg_pace);
      }
    });

    return Object.entries(weeks).map(([day, stats]) => ({
      day,
      distance: Number((stats.distance).toFixed(2)),
      count: stats.count,
      avgPace: stats.pace.length > 0 
        ? stats.pace.reduce((a, b) => a + b) / stats.pace.length 
        : 0,
    }));
  };

  // Calcular distribución de HR zones
  const getHRZones = () => {
    let z1 = 0; // <50%
    let z2 = 0; // 50-60%
    let z3 = 0; // 60-70%
    let z4 = 0; // 70-85%
    let z5 = 0; // >85%

    const avgMaxHR = 190; // Estimado
    const maxHR = 190;

    workouts.forEach(w => {
      if (!w.avg_heart_rate) return;
      const pct = (w.avg_heart_rate / maxHR) * 100;

      if (pct < 50) z1++;
      else if (pct < 60) z2++;
      else if (pct < 70) z3++;
      else if (pct < 85) z4++;
      else z5++;
    });

    const total = z1 + z2 + z3 + z4 + z5 || 1;
    return [
      { zone: 'Z1 <50%', count: z1, pct: ((z1 / total) * 100).toFixed(0) },
      { zone: 'Z2 50-60%', count: z2, pct: ((z2 / total) * 100).toFixed(0) },
      { zone: 'Z3 60-70%', count: z3, pct: ((z3 / total) * 100).toFixed(0) },
      { zone: 'Z4 70-85%', count: z4, pct: ((z4 / total) * 100).toFixed(0) },
      { zone: 'Z5 >85%', count: z5, pct: ((z5 / total) * 100).toFixed(0) },
    ];
  };

  // Calcular progresión de pace
  const getPaceProgression = () => {
    const sorted = [...workouts]
      .sort((a, b) => new Date(a.start_time).getTime() - new Date(b.start_time).getTime())
      .slice(-6);

    return sorted.map((w, i) => ({
      index: i + 1,
      pace: w.avg_pace || 0,
      date: new Date(w.start_time).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }),
    }));
  };

  const weekStats = getWeekStats();
  const hrZones = getHRZones();
  const paceProgression = getPaceProgression();

  const maxDistance = Math.max(...weekStats.map(w => w.distance), 1);
  const maxPace = Math.max(...paceProgression.map(p => p.pace), 500);

  const zoneColors = {
    'Z1 <50%': '#10b981',
    'Z2 50-60%': '#3b82f6',
    'Z3 60-70%': '#f59e0b',
    'Z4 70-85%': '#ef4444',
    'Z5 >85%': '#7c3aed',
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Weekly Distance Chart */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">📊 Distancia por Día</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {weekStats.map(w => (
            <div key={w.day} className="space-y-1">
              <div className="flex justify-between text-sm">
                <span className="text-slate-300">{w.day}</span>
                <span className="text-blue-400 font-medium">{w.distance}km</span>
              </div>
              <div className="w-full h-8 bg-slate-700 rounded-lg overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg transition-all"
                  style={{ width: `${(w.distance / maxDistance) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Pace Progression */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">⚡ Evolución de Pace</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-end justify-between gap-2 h-48">
              {paceProgression.map((p, i) => (
                <div key={i} className="flex-1 flex flex-col items-center">
                  <div className="w-full flex justify-center mb-2">
                    <div className="w-full max-w-12">
                      <div
                        className="bg-gradient-to-t from-purple-500 to-purple-400 rounded-t-lg transition-all"
                        style={{ height: `${(p.pace / maxPace) * 150}px` }}
                      />
                    </div>
                  </div>
                  <span className="text-xs text-slate-400 text-center">{p.date}</span>
                </div>
              ))}
            </div>
            <div className="text-center text-sm text-slate-400">
              {formatPace(paceProgression[paceProgression.length - 1]?.pace || 0)}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* HR Zones Distribution */}
      <Card className="bg-slate-800/50 border-slate-700 lg:col-span-2">
        <CardHeader>
          <CardTitle className="text-lg">💓 Distribución de Zonas HR</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
            {hrZones.map(zone => {
              const color = zoneColors[zone.zone as keyof typeof zoneColors];
              return (
                <div key={zone.zone} className="text-center">
                  <div
                    className="h-32 rounded-lg mb-3 flex items-center justify-center text-white font-bold text-lg transition-transform hover:scale-105"
                    style={{ backgroundColor: color }}
                  >
                    {zone.pct}%
                  </div>
                  <p className="text-sm text-slate-300 mb-1">{zone.zone}</p>
                  <p className="text-xs text-slate-500">{zone.count} entrenamientos</p>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Tipo de Deporte */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">🏃 Distribución por Tipo</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {Object.entries(
              workouts.reduce((acc, w) => {
                const type = w.sport_type || 'running';
                acc[type] = (acc[type] || 0) + 1;
                return acc;
              }, {} as Record<string, number>)
            ).map(([type, count]) => {
              const pct = ((count / workouts.length) * 100).toFixed(0);
              const icons = {
                running: '🏃',
                trail_running: '🥾',
                cycling: '🚴',
                walking: '🚶',
              };
              return (
                <div key={type} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-300">
                      {icons[type as keyof typeof icons] || '🏃'} {type}
                    </span>
                    <span className="text-green-400 font-medium">{pct}%</span>
                  </div>
                  <div className="w-full h-6 bg-slate-700 rounded-lg overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-500 to-green-600 rounded-lg"
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Personal Records */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">🏆 Personal Records</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {workouts.length > 0 && (
            <>
              <div>
                <p className="text-sm text-slate-400 mb-1">🏃 Distancia Máxima</p>
                <p className="text-2xl font-bold text-blue-400">
                  {formatDistance(Math.max(...workouts.map(w => w.distance_meters || 0)))}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">⚡ Pace Más Rápido</p>
                <p className="text-2xl font-bold text-purple-400">
                  {formatPace(Math.min(...workouts.filter(w => w.avg_pace).map(w => w.avg_pace || 999)))}
                </p>
              </div>
              <div>
                <p className="text-sm text-slate-400 mb-1">💓 HR Máximo</p>
                <p className="text-2xl font-bold text-red-400">
                  {Math.max(...workouts.filter(w => w.max_heart_rate).map(w => w.max_heart_rate || 0))}
                  <span className="text-sm text-slate-500 ml-1">bpm</span>
                </p>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
