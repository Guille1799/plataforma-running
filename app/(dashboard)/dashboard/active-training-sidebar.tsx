'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

interface TrainingDay {
  day: string;
  type: string;
  description: string;
  distance_km?: number;
  pace_min_per_km?: number;
  heart_rate_zone?: number;
  duration_minutes?: number;
}

interface TrainingWeek {
  week_number: number;
  days: TrainingDay[];
  total_km: number;
}

interface TrainingPlan {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  weeks: TrainingWeek[];
}

export function ActiveTrainingPlanSidebar({ plan }: { plan: TrainingPlan | null }) {
  const [currentWeek, setCurrentWeek] = useState(1);
  const [todayWorkout, setTodayWorkout] = useState<TrainingDay | null>(null);

  useEffect(() => {
    if (!plan) return;
    
    // Find today's day of week (0 = Sunday, 1 = Monday, etc.)
    const today = new Date().getDay();
    const dayName = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'][today];
    
    const currentWeekData = plan.weeks.find(w => w.week_number === currentWeek);
    if (currentWeekData) {
      const today_workout = currentWeekData.days.find(d => d.day.includes(dayName));
      setTodayWorkout(today_workout || null);
    }
  }, [plan, currentWeek]);

  if (!plan) {
    return (
      <Card className="bg-slate-800 border-slate-700 h-full">
        <CardHeader>
          <CardTitle className="text-white">Plan de Entrenamiento</CardTitle>
        </CardHeader>
        <CardContent className="text-center text-slate-400">
          No hay plan activo. ¡Crea uno para comenzar!
        </CardContent>
      </Card>
    );
  }

  // Validar que el plan tenga la estructura correcta
  if (!plan.weeks || !Array.isArray(plan.weeks) || plan.weeks.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Plan de Entrenamiento</CardTitle>
        </CardHeader>
        <CardContent className="text-center text-slate-400">
          <p>Plan en generación...</p>
          <p className="text-xs mt-2">Recarga la página en unos momentos</p>
        </CardContent>
      </Card>
    );
  }

  const currentWeekData = plan.weeks.find(w => w.week_number === currentWeek);

  return (
    <div className="space-y-4">
      {/* Entrenamiento de Hoy */}
      {todayWorkout && (
        <Card className="bg-gradient-to-br from-blue-900/50 to-slate-800 border-blue-600">
          <CardHeader>
            <CardTitle className="text-white text-sm">Hoy: {todayWorkout.day}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div>
              <div className="text-2xl font-bold text-blue-400">{todayWorkout.type}</div>
              <p className="text-xs text-slate-400">{todayWorkout.description}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-2">
              {todayWorkout.distance_km && (
                <div className="p-2 bg-slate-700/50 rounded">
                  <div className="text-xs text-slate-400">Distancia</div>
                  <div className="font-semibold text-white">{todayWorkout.distance_km} km</div>
                </div>
              )}
              {todayWorkout.pace_min_per_km && (
                <div className="p-2 bg-slate-700/50 rounded">
                  <div className="text-xs text-slate-400">Ritmo</div>
                  <div className="font-semibold text-white">{todayWorkout.pace_min_per_km.toFixed(1)}'</div>
                </div>
              )}
              {todayWorkout.duration_minutes && (
                <div className="p-2 bg-slate-700/50 rounded">
                  <div className="text-xs text-slate-400">Duración</div>
                  <div className="font-semibold text-white">{todayWorkout.duration_minutes} min</div>
                </div>
              )}
              {todayWorkout.heart_rate_zone && (
                <div className="p-2 bg-slate-700/50 rounded">
                  <div className="text-xs text-slate-400">Zona HR</div>
                  <div className="font-semibold text-white">Z{todayWorkout.heart_rate_zone}</div>
                </div>
              )}
            </div>

            <Button className="w-full bg-blue-600 hover:bg-blue-700 text-sm">
              ▶️ Empezar Entrenamiento
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Vista General de la Semana Actual */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader className="pb-3">
          <div className="flex justify-between items-center">
            <CardTitle className="text-white text-sm">Semana {currentWeek}</CardTitle>
            <div className="text-xs text-slate-400">
              {currentWeekData?.total_km.toFixed(1)} km
            </div>
          </div>
        </CardHeader>
        <CardContent className="space-y-2">
          {currentWeekData?.days.map((day, idx) => (
            <div key={idx} className="flex items-center justify-between p-2 bg-slate-700/40 rounded">
              <div>
                <div className="text-sm font-medium text-white">{day.day}</div>
                <div className="text-xs text-blue-400">{day.type}</div>
              </div>
              {day.distance_km && (
                <div className="text-xs text-slate-300 font-semibold">{day.distance_km} km</div>
              )}
            </div>
          ))}
        </CardContent>
      </Card>

      {/* Navegación entre Semanas */}
      <div className="flex gap-2">
        <Button
          onClick={() => setCurrentWeek(Math.max(1, currentWeek - 1))}
          disabled={currentWeek === 1}
          className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-50"
          size="sm"
        >
          ← Semana Anterior
        </Button>
        <Button
          onClick={() => setCurrentWeek(Math.min(plan.weeks.length, currentWeek + 1))}
          disabled={currentWeek === plan.weeks.length}
          className="flex-1 bg-slate-700 hover:bg-slate-600 disabled:opacity-50"
          size="sm"
        >
          Siguiente Semana →
        </Button>
      </div>

      {/* Info del Plan */}
      <Card className="bg-slate-800/50 border-slate-700">
        <CardContent className="pt-4 space-y-2 text-xs text-slate-400">
          <div>📅 Inicio: {new Date(plan.start_date).toLocaleDateString('es-ES')}</div>
          <div>🏁 Fin: {new Date(plan.end_date).toLocaleDateString('es-ES')}</div>
          <div>⏳ Duración: {plan.weeks.length} semanas</div>
        </CardContent>
      </Card>
    </div>
  );
}
