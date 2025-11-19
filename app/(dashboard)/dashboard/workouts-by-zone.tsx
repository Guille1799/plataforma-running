'use client';

/**
 * Workouts by Zone Chart Component
 * Shows distribution of workouts across HR zones (last 4 weeks)
 * Zones calculated based on % of max HR
 */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import type { Workout } from '@/lib/types';

interface WorkoutsByZoneProps {
  workouts: Workout[];
  maxHR?: number;
}

function getZoneFromHR(hr: number, maxHR: number): string {
  const pct = (hr / maxHR) * 100;
  if (pct < 50) return 'Z1';
  if (pct < 70) return 'Z2';
  if (pct < 80) return 'Z3';
  if (pct < 90) return 'Z4';
  return 'Z5';
}

export function WorkoutsByZoneChart({ workouts, maxHR = 200 }: WorkoutsByZoneProps) {
  if (!workouts || workouts.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>📊</span> Entrenamientos por Zona
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-center py-6">
            Sincroniza entrenamientos para ver la distribución por zonas
          </p>
        </CardContent>
      </Card>
    );
  }

  // Agrupa workouts por semana (últimas 4 semanas) y por zona
  const now = new Date();
  const fourWeeksAgo = new Date(now.getTime() - 4 * 7 * 24 * 60 * 60 * 1000);

  const recentWorkouts = workouts.filter(w => {
    const workoutDate = new Date(w.start_time);
    return workoutDate >= fourWeeksAgo && (w.avg_heart_rate || 0) > 0;
  });

  // Crea estructura de datos por semana
  const weeklyData: Record<string, any> = {};
  
  recentWorkouts.forEach(workout => {
    const date = new Date(workout.start_time);
    const weekNumber = Math.floor((now.getTime() - date.getTime()) / (7 * 24 * 60 * 60 * 1000));
    const weekLabel = `Semana ${4 - weekNumber}`;
    
    if (!weeklyData[weekLabel]) {
      weeklyData[weekLabel] = { week: weekLabel, Z1: 0, Z2: 0, Z3: 0, Z4: 0, Z5: 0 };
    }
    
    const zone = getZoneFromHR(workout.avg_heart_rate || 0, maxHR);
    if (zone in weeklyData[weekLabel]) {
      weeklyData[weekLabel][zone] += 1;
    }
  });

  const chartData = Object.values(weeklyData).sort((a, b) => 
    a.week.localeCompare(b.week)
  );

  if (chartData.length === 0 || recentWorkouts.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>📊</span> Entrenamientos por Zona
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-center py-6">
            No hay datos de FC disponibles en las últimas 4 semanas
          </p>
        </CardContent>
      </Card>
    );
  }

  // Calcula totales por zona
  const totals = { Z1: 0, Z2: 0, Z3: 0, Z4: 0, Z5: 0 };
  recentWorkouts.forEach(w => {
    const zone = getZoneFromHR(w.avg_heart_rate || 0, maxHR);
    totals[zone as keyof typeof totals] += 1;
  });

  return (
    <Card className="bg-slate-800/50 border-slate-700 animate-fade-in hover:shadow-lg transition-shadow duration-300">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <span>📊</span> Entrenamientos por Zona (Últimas 4 Semanas)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="w-full h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 20 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#475569" />
              <XAxis dataKey="week" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              <Bar dataKey="Z1" stackId="a" fill="#3b82f6" />
              <Bar dataKey="Z2" stackId="a" fill="#10b981" />
              <Bar dataKey="Z3" stackId="a" fill="#eab308" />
              <Bar dataKey="Z4" stackId="a" fill="#f97316" />
              <Bar dataKey="Z5" stackId="a" fill="#ef4444" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        {/* Summary */}
        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          <div className="p-2 bg-blue-500/10 rounded border border-blue-500/30">
            <p className="text-blue-400">Z1: {totals.Z1}</p>
          </div>
          <div className="p-2 bg-green-500/10 rounded border border-green-500/30">
            <p className="text-green-400">Z2: {totals.Z2}</p>
          </div>
          <div className="p-2 bg-yellow-500/10 rounded border border-yellow-500/30">
            <p className="text-yellow-400">Z3: {totals.Z3}</p>
          </div>
          <div className="p-2 bg-orange-500/10 rounded border border-orange-500/30">
            <p className="text-orange-400">Z4+: {totals.Z4 + totals.Z5}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
