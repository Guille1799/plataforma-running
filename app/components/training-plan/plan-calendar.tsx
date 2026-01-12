'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronLeft, 
  ChevronRight, 
  Calendar as CalendarIcon 
} from 'lucide-react';
import { 
  startOfWeek, 
  endOfWeek, 
  startOfMonth, 
  endOfMonth, 
  eachDayOfInterval,
  isSameDay,
  isSameMonth,
  format,
  addMonths,
  subMonths,
  addWeeks,
  subWeeks,
  getWeek,
  getYear,
} from 'date-fns';
import { es } from 'date-fns/locale';

interface Workout {
  day: number;
  date?: string;
  type: string;
  name: string;
  distance_km?: number;
  duration_minutes?: number;
  pace_target_min_per_km?: number;
  completed?: boolean;
  completed_date?: string;
}

interface Week {
  week: number;
  start_date: string;
  end_date: string;
  focus: string;
  total_km: number;
  intensity_score?: number;
  workouts: Workout[];
}

interface Plan {
  plan_id: string;
  plan_name: string;
  start_date: string;
  end_date: string;
  weeks: Week[];
}

interface PlanCalendarProps {
  plan: Plan;
  onDayClick?: (date: Date, workout: Workout | null) => void;
  view?: 'month' | 'week';
}

export function PlanCalendar({ plan, onDayClick, view: initialView = 'month' }: PlanCalendarProps) {
  const [currentDate, setCurrentDate] = useState(new Date(plan.start_date));
  const [view, setView] = useState<'month' | 'week'>(initialView);

  // Build workout map by date
  const workoutMap = useMemo(() => {
    const map = new Map<string, Workout[]>();
    
    plan.weeks.forEach(week => {
      week.workouts.forEach(workout => {
        if (workout.date) {
          const dateKey = format(new Date(workout.date), 'yyyy-MM-dd');
          if (!map.has(dateKey)) {
            map.set(dateKey, []);
          }
          map.get(dateKey)!.push(workout);
        } else if (workout.day) {
          // Calculate date from week start and day (1-7, Monday-Sunday)
          const weekStart = new Date(week.start_date);
          const dayOffset = (workout.day - 1) % 7; // Convert 1-7 to 0-6
          const workoutDate = new Date(weekStart);
          workoutDate.setDate(weekStart.getDate() + dayOffset);
          const dateKey = format(workoutDate, 'yyyy-MM-dd');
          if (!map.has(dateKey)) {
            map.set(dateKey, []);
          }
          map.get(dateKey)!.push(workout);
        }
      });
    });
    
    return map;
  }, [plan]);

  const getWorkoutColor = (type: string) => {
    const colors: Record<string, string> = {
      'easy_run': 'bg-green-500/20 text-green-400 border-green-500/50',
      'tempo_run': 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
      'interval_run': 'bg-red-500/20 text-red-400 border-red-500/50',
      'long_run': 'bg-blue-500/20 text-blue-400 border-blue-500/50',
      'recovery': 'bg-purple-500/20 text-purple-400 border-purple-500/50',
      'cross_training': 'bg-orange-500/20 text-orange-400 border-orange-500/50',
      'strength': 'bg-pink-500/20 text-pink-400 border-pink-500/50',
    };
    return colors[type] || 'bg-slate-700 text-slate-300 border-slate-600';
  };

  const getWorkoutTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'easy_run': 'Rodaje',
      'tempo_run': 'Tempo',
      'interval_run': 'Series',
      'long_run': 'Largo',
      'recovery': 'Recuperación',
      'cross_training': 'Cross',
      'strength': 'Fuerza',
    };
    return labels[type] || type;
  };

  // Month view
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(currentDate);
  const calendarStart = startOfWeek(monthStart, { weekStartsOn: 1 }); // Monday
  const calendarEnd = endOfWeek(monthEnd, { weekStartsOn: 1 });
  const monthDays = eachDayOfInterval({ start: calendarStart, end: calendarEnd });

  // Week view
  const weekStart = startOfWeek(currentDate, { weekStartsOn: 1 });
  const weekEnd = endOfWeek(currentDate, { weekStartsOn: 1 });
  const weekDays = eachDayOfInterval({ start: weekStart, end: weekEnd });

  const navigateMonth = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => direction === 'next' ? addMonths(prev, 1) : subMonths(prev, 1));
  };

  const navigateWeek = (direction: 'prev' | 'next') => {
    setCurrentDate(prev => direction === 'next' ? addWeeks(prev, 1) : subWeeks(prev, 1));
  };

  const handleDayClick = (date: Date) => {
    const dateKey = format(date, 'yyyy-MM-dd');
    const workouts = workoutMap.get(dateKey) || [];
    onDayClick?.(date, workouts[0] || null);
  };

  const renderDay = (date: Date, isCurrentMonth: boolean) => {
    const dateKey = format(date, 'yyyy-MM-dd');
    const workouts = workoutMap.get(dateKey) || [];
    const isToday = isSameDay(date, new Date());
    const isPlanDate = date >= new Date(plan.start_date) && date <= new Date(plan.end_date);

    return (
      <div
        key={dateKey}
        className={`
          min-h-[100px] p-2 border border-slate-700 bg-slate-800/30
          ${!isCurrentMonth ? 'opacity-40' : ''}
          ${isToday ? 'ring-2 ring-blue-500' : ''}
          ${isPlanDate ? 'cursor-pointer hover:bg-slate-700/50' : 'cursor-not-allowed'}
          transition-colors
        `}
        onClick={() => isPlanDate && handleDayClick(date)}
      >
        <div className="flex items-center justify-between mb-1">
          <span className={`text-sm font-medium ${isToday ? 'text-blue-400' : 'text-slate-300'}`}>
            {format(date, 'd')}
          </span>
        </div>
        
        <div className="space-y-1">
          {workouts.map((workout, idx) => (
            <Badge
              key={idx}
              className={`${getWorkoutColor(workout.type)} text-xs px-2 py-0.5 w-full justify-start`}
            >
              <span className="truncate">
                {workout.completed ? '✓ ' : ''}
                {getWorkoutTypeLabel(workout.type)}
              </span>
            </Badge>
          ))}
        </div>
      </div>
    );
  };

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle className="text-white flex items-center gap-2">
            <CalendarIcon className="h-5 w-5" />
            Calendario del Plan
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setView(view === 'month' ? 'week' : 'month')}
              className="border-slate-700"
            >
              {view === 'month' ? 'Vista Semanal' : 'Vista Mensual'}
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent>
        {view === 'month' ? (
          <>
            {/* Month Navigation */}
            <div className="flex items-center justify-between mb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateMonth('prev')}
                className="border-slate-700"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-xl font-semibold text-white">
                {format(currentDate, 'MMMM yyyy', { locale: es })}
              </h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateMonth('next')}
                className="border-slate-700"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Month Calendar Grid */}
            <div className="grid grid-cols-7 gap-1">
              {/* Day headers */}
              {['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'].map(day => (
                <div key={day} className="text-center text-sm font-semibold text-slate-400 p-2">
                  {day}
                </div>
              ))}
              
              {/* Calendar days */}
              {monthDays.map(day => renderDay(day, isSameMonth(day, currentDate)))}
            </div>
          </>
        ) : (
          <>
            {/* Week Navigation */}
            <div className="flex items-center justify-between mb-4">
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateWeek('prev')}
                className="border-slate-700"
              >
                <ChevronLeft className="h-4 w-4" />
              </Button>
              <h2 className="text-xl font-semibold text-white">
                Semana {format(weekStart, 'd')} - {format(weekEnd, 'd MMM yyyy', { locale: es })}
              </h2>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigateWeek('next')}
                className="border-slate-700"
              >
                <ChevronRight className="h-4 w-4" />
              </Button>
            </div>

            {/* Week View */}
            <div className="grid grid-cols-7 gap-4">
              {weekDays.map((day, idx) => {
                const dateKey = format(day, 'yyyy-MM-dd');
                const workouts = workoutMap.get(dateKey) || [];
                const isToday = isSameDay(day, new Date());

                return (
                  <div
                    key={dateKey}
                    className={`
                      p-4 border rounded-lg
                      ${isToday ? 'ring-2 ring-blue-500 border-blue-500' : 'border-slate-700 bg-slate-800/30'}
                      cursor-pointer hover:bg-slate-700/50 transition-colors
                    `}
                    onClick={() => handleDayClick(day)}
                  >
                    <div className="mb-3">
                      <div className="text-sm font-medium text-slate-400 mb-1">
                        {format(day, 'EEEE', { locale: es })}
                      </div>
                      <div className={`text-2xl font-bold ${isToday ? 'text-blue-400' : 'text-white'}`}>
                        {format(day, 'd')}
                      </div>
                    </div>
                    
                    <div className="space-y-2">
                      {workouts.length === 0 ? (
                        <div className="text-xs text-slate-500">Descanso</div>
                      ) : (
                        workouts.map((workout, workoutIdx) => (
                          <div
                            key={workoutIdx}
                            className={`p-2 rounded ${getWorkoutColor(workout.type)}`}
                          >
                            <div className="font-semibold text-sm mb-1">
                              {workout.completed ? '✓ ' : ''}
                              {getWorkoutTypeLabel(workout.type)}
                            </div>
                            {workout.name && (
                              <div className="text-xs opacity-90 mb-1">{workout.name}</div>
                            )}
                            {workout.distance_km && (
                              <div className="text-xs opacity-75">
                                {workout.distance_km.toFixed(1)} km
                              </div>
                            )}
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}

        {/* Legend */}
        <div className="mt-6 pt-4 border-t border-slate-700">
          <div className="text-sm font-semibold text-slate-400 mb-2">Leyenda:</div>
          <div className="flex flex-wrap gap-2">
            {['easy_run', 'tempo_run', 'interval_run', 'long_run', 'recovery'].map(type => (
              <Badge key={type} className={getWorkoutColor(type)}>
                {getWorkoutTypeLabel(type)}
              </Badge>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
