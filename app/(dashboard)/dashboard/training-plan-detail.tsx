'use client';

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useState } from "react";

interface TrainingPlanDetailProps {
  plan: any;
}

export function TrainingPlanDetail({ plan }: TrainingPlanDetailProps) {
  const [currentWeekIndex, setCurrentWeekIndex] = useState(0);
  
  if (!plan) return null;

  const weeks = plan.weeks || [];
  const week1 = weeks[currentWeekIndex] || null;
  const week2 = weeks[currentWeekIndex + 1] || null;
  const totalVolume = plan.total_volume_km || 0;

  const today = new Date();
  const planStart = plan.start_date ? new Date(plan.start_date) : today;
  const weeksSinceStart = Math.floor((today.getTime() - planStart.getTime()) / (7 * 24 * 60 * 60 * 1000));
  const suggestedWeekIndex = Math.max(0, Math.min(weeksSinceStart, weeks.length - 2));

  const renderDay = (day: any, dayIdx: number) => {
    let dayColor = 'slate';
    if (day.type?.toLowerCase().includes('easy')) dayColor = 'green';
    else if (day.type?.toLowerCase().includes('long')) dayColor = 'orange';
    else if (day.type?.toLowerCase().includes('speed') || day.type?.toLowerCase().includes('interval')) dayColor = 'red';
    else if (day.type?.toLowerCase().includes('recovery') || day.type?.toLowerCase().includes('rest')) dayColor = 'blue';
    else if (day.type?.toLowerCase().includes('strength')) dayColor = 'purple';
    
    const colorClass = {
      green: 'border-green-500 bg-green-900/20',
      orange: 'border-orange-500 bg-orange-900/20',
      red: 'border-red-500 bg-red-900/20',
      blue: 'border-blue-500 bg-blue-900/20',
      purple: 'border-purple-500 bg-purple-900/20',
      slate: 'border-slate-600 bg-slate-700/20'
    }[dayColor];

    return (
      <div key={dayIdx} className={`p-4 rounded-lg border-2 ${colorClass} space-y-2`}>
        <div>
          <h3 className="font-bold text-lg text-white">{day.day || `Día ${dayIdx + 1}`}</h3>
          <p className="text-sm font-semibold text-yellow-300">{day.type}</p>
        </div>
        {day.description && <p className="text-sm text-slate-300 italic">{day.description}</p>}
        <div className="grid grid-cols-2 gap-2 pt-2 border-t border-slate-600">
          {day.distance_km && <div className="bg-slate-900/50 p-2 rounded text-xs"><p className="text-slate-400">Distancia</p><p className="font-semibold text-white">{day.distance_km} km</p></div>}
          {day.pace_min_per_km && <div className="bg-slate-900/50 p-2 rounded text-xs"><p className="text-slate-400">Ritmo</p><p className="font-semibold text-white">{Math.floor(day.pace_min_per_km)}'{Math.round((day.pace_min_per_km % 1) * 60)}"</p></div>}
          {day.heart_rate_zone && <div className="bg-slate-900/50 p-2 rounded text-xs"><p className="text-slate-400">Zona HR</p><p className="font-semibold text-white">Z{day.heart_rate_zone}</p></div>}
          {day.duration_minutes && <div className="bg-slate-900/50 p-2 rounded text-xs"><p className="text-slate-400">Duración</p><p className="font-semibold text-white">{day.duration_minutes} min</p></div>}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <Card className="bg-gradient-to-r from-blue-900 to-slate-900 border-blue-600">
        <CardHeader>
          <CardTitle className="text-white text-3xl">{plan.name}</CardTitle>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div><p className="text-slate-400 text-xs">Objetivo</p><p className="text-white font-semibold text-sm">{plan.general_goal}</p></div>
            <div><p className="text-slate-400 text-xs">Duración</p><p className="text-white font-semibold text-sm">{plan.plan_duration_weeks || weeks.length} semanas</p></div>
            <div><p className="text-slate-400 text-xs">Volumen</p><p className="text-white font-semibold text-sm">{totalVolume.toFixed(0)} km</p></div>
            <div><p className="text-slate-400 text-xs">Viendo</p><p className="text-white font-semibold text-sm">S{currentWeekIndex + 1}-{Math.min(currentWeekIndex + 2, weeks.length)}</p></div>
          </div>
        </CardHeader>
      </Card>

      {weeks.length > 1 && (
        <Card className="bg-slate-800 border-slate-700">
          <CardHeader><CardTitle className="text-white">📍 Calendario Rolling (2 Semanas)</CardTitle></CardHeader>
          <CardContent className="space-y-3">
            <div className="flex gap-2 overflow-x-auto pb-2">
              {weeks.map((_, idx) => (
                <button key={idx} onClick={() => setCurrentWeekIndex(Math.min(idx, weeks.length - 2))} disabled={idx >= weeks.length - 1}
                  className={`px-3 py-1 rounded font-semibold text-xs whitespace-nowrap ${currentWeekIndex === idx ? 'bg-blue-600 text-white' : idx === suggestedWeekIndex ? 'bg-blue-900/50 text-blue-300 border border-blue-500' : 'bg-slate-700 text-slate-300'} disabled:opacity-30`}>
                  S{idx + 1}
                </button>
              ))}
            </div>
            <div className="flex gap-2">
              <Button onClick={() => setCurrentWeekIndex(Math.max(0, currentWeekIndex - 1))} disabled={currentWeekIndex === 0} className="flex-1 bg-slate-700 text-xs">← Ant</Button>
              <Button onClick={() => setCurrentWeekIndex(Math.min(currentWeekIndex + 1, weeks.length - 2))} disabled={currentWeekIndex >= weeks.length - 2} className="flex-1 bg-slate-700 text-xs">Sig →</Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="grid lg:grid-cols-2 gap-4">
        {week1 && (
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-lg">📅 Semana {week1.week_number}</CardTitle><p className="text-slate-400 text-xs">{week1.total_km?.toFixed(0)} km</p></CardHeader>
            <CardContent><div className="space-y-2">{week1.days?.map((day: any, i: number) => renderDay(day, i))}</div></CardContent>
          </Card>
        )}
        {week2 && (
          <Card className="bg-slate-800 border-slate-700">
            <CardHeader><CardTitle className="text-white text-lg">📅 Semana {week2.week_number}</CardTitle><p className="text-slate-400 text-xs">{week2.total_km?.toFixed(0)} km</p></CardHeader>
            <CardContent><div className="space-y-2">{week2.days?.map((day: any, i: number) => renderDay(day, i))}</div></CardContent>
          </Card>
        )}
      </div>

      <Card className="bg-blue-900/20 border-blue-600">
        <CardHeader><CardTitle className="text-blue-300">📱 Sincronizar con Dispositivo</CardTitle></CardHeader>
        <CardContent>
          <p className="text-sm text-blue-200 mb-3">Envía los entrenamientos de estas 2 semanas a tu Garmin</p>
          <Button className="w-full bg-blue-600 hover:bg-blue-700 text-sm">🔄 Enviar a Garmin</Button>
        </CardContent>
      </Card>
    </div>
  );
}
