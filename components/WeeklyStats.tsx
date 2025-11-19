'use client';

/**
 * WeeklyStats.tsx - Visual weekly statistics component
 */
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { BarChart } from '@/components/charts';
import type { Workout } from '@/lib/types';

interface WeeklyStatsProps {
  workouts: Workout[];
  className?: string;
}

export function WeeklyStats({ workouts, className = '' }: WeeklyStatsProps) {
  const weeklyData = useMemo(() => {
    const days = ['Dom', 'Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb'];
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay()); // Start of week (Sunday)

    // Initialize data for each day of the week
    const dataByDay = days.map((day, index) => {
      const date = new Date(weekStart);
      date.setDate(weekStart.getDate() + index);
      
      // Find workouts for this day
      const dayWorkouts = workouts.filter(w => {
        const workoutDate = new Date(w.start_time);
        return workoutDate.toDateString() === date.toDateString();
      });

      // Calculate total distance in km for the day
      const totalDistance = dayWorkouts.reduce((sum, w) => {
        return sum + (w.distance_meters || 0) / 1000;
      }, 0);

      return {
        label: day,
        value: totalDistance,
        color: index === today.getDay() ? '#3b82f6' : '#64748b',
      };
    });

    return dataByDay;
  }, [workouts]);

  const totalDistance = useMemo(() => {
    return weeklyData.reduce((sum, d) => sum + d.value, 0);
  }, [weeklyData]);

  const totalWorkouts = useMemo(() => {
    return weeklyData.filter(d => d.value > 0).length;
  }, [weeklyData]);

  const avgDistance = totalWorkouts > 0 ? totalDistance / totalWorkouts : 0;

  return (
    <Card className={`bg-slate-800/50 border-slate-700 ${className}`}>
      <CardHeader>
        <CardTitle className="text-white flex items-center justify-between">
          <span>Esta Semana 📅</span>
          <div className="flex items-center gap-4 text-sm font-normal">
            <span className="text-slate-400">
              {totalWorkouts} entrenamientos
            </span>
            <span className="text-blue-400 font-semibold">
              {totalDistance.toFixed(1)} km
            </span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <BarChart
          data={weeklyData}
          height={150}
          showValues={false}
        />

        {/* Summary Stats */}
        <div className="mt-4 grid grid-cols-3 gap-4">
          <div className="text-center">
            <p className="text-2xl font-bold text-white">
              {totalDistance.toFixed(1)}
            </p>
            <p className="text-xs text-slate-400">km totales</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-white">
              {totalWorkouts}
            </p>
            <p className="text-xs text-slate-400">entrenamientos</p>
          </div>
          <div className="text-center">
            <p className="text-2xl font-bold text-white">
              {avgDistance.toFixed(1)}
            </p>
            <p className="text-xs text-slate-400">km promedio</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
