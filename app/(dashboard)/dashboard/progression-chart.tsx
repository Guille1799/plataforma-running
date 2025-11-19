'use client';

/**
 * Progression Chart Component
 * Shows HR progression over the last 8 weeks
 */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import type { Workout } from '@/lib/types';

interface ProgressionChartProps {
  workouts: Workout[];
}

export function ProgressionChart({ workouts }: ProgressionChartProps) {
  if (!workouts || workouts.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>📈</span> Progresión (Últimas 8 Semanas)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-center py-6">
            Sincroniza entrenamientos para ver tu progresión
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calcula promedio de FC por semana (últimas 8 semanas)
  const now = new Date();
  const eightWeeksAgo = new Date(now.getTime() - 8 * 7 * 24 * 60 * 60 * 1000);

  const recentWorkouts = workouts.filter(w => {
    const workoutDate = new Date(w.start_time);
    return workoutDate >= eightWeeksAgo;
  });

  // Agrupa por semana
  const weeklyAvg: Record<string, any> = {};
  
  recentWorkouts.forEach(workout => {
    const date = new Date(workout.start_time);
    const weekNumber = Math.floor((now.getTime() - date.getTime()) / (7 * 24 * 60 * 60 * 1000));
    const weekLabel = `W${8 - weekNumber}`;
    
    if (!weeklyAvg[weekLabel]) {
      weeklyAvg[weekLabel] = { week: weekLabel, hr: [], distance: 0, count: 0 };
    }
    
    if (workout.avg_heart_rate) {
      weeklyAvg[weekLabel].hr.push(workout.avg_heart_rate);
    }
    weeklyAvg[weekLabel].distance += workout.distance_meters || 0;
    weeklyAvg[weekLabel].count += 1;
  });

  // Calcula promedios
  const chartData = Object.entries(weeklyAvg).map(([key, data]) => ({
    week: data.week,
    avgHR: data.hr.length > 0 ? Math.round(data.hr.reduce((a: number, b: number) => a + b, 0) / data.hr.length) : 0,
    distance: Math.round(data.distance / 1000),
    workouts: data.count,
  })).sort((a, b) => a.week.localeCompare(b.week));

  if (chartData.length === 0 || chartData.every(d => d.avgHR === 0)) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>📈</span> Progresión (Últimas 8 Semanas)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-center py-6">
            No hay datos de FC en las últimas 8 semanas
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calcula estadísticas
  const validData = chartData.filter(d => d.avgHR > 0);
  const avgHROverall = Math.round(validData.reduce((a, d) => a + d.avgHR, 0) / validData.length);
  const minHR = Math.min(...validData.map(d => d.avgHR));
  const maxHR = Math.max(...validData.map(d => d.avgHR));
  const totalKm = chartData.reduce((a, d) => a + d.distance, 0);

  return (
    <Card className="bg-slate-800/50 border-slate-700 animate-fade-in hover:shadow-lg transition-shadow duration-300">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <span>📈</span> Progresión FC (Últimas 8 Semanas)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="week" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={['dataMin - 5', 'dataMax + 5']} />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#e2e8f0' }}
                formatter={(value) => [`${value} bpm`, 'FC Promedio']}
              />
              <Line
                type="monotone"
                dataKey="avgHR"
                stroke="#ef4444"
                dot={{ fill: '#ef4444', r: 4 }}
                activeDot={{ r: 6 }}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Stats Grid */}
        <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
          <div className="p-3 bg-slate-700/30 rounded-lg border border-slate-600">
            <p className="text-slate-400 text-xs font-medium">FC Promedio</p>
            <p className="text-red-400 text-lg font-bold">{avgHROverall} bpm</p>
          </div>
          <div className="p-3 bg-slate-700/30 rounded-lg border border-slate-600">
            <p className="text-slate-400 text-xs font-medium">FC Mínima</p>
            <p className="text-blue-400 text-lg font-bold">{minHR} bpm</p>
          </div>
          <div className="p-3 bg-slate-700/30 rounded-lg border border-slate-600">
            <p className="text-slate-400 text-xs font-medium">FC Máxima</p>
            <p className="text-orange-400 text-lg font-bold">{maxHR} bpm</p>
          </div>
          <div className="p-3 bg-slate-700/30 rounded-lg border border-slate-600">
            <p className="text-slate-400 text-xs font-medium">Total km</p>
            <p className="text-green-400 text-lg font-bold">{totalKm} km</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
