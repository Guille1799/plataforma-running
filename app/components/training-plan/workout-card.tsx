'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  ChevronDown, 
  ChevronUp, 
  CheckCircle2, 
  Circle,
  Target,
  Clock,
  Route,
  Heart,
  Activity
} from 'lucide-react';

interface Workout {
  day?: number;
  date?: string;
  type: string;
  name: string;
  distance_km?: number;
  duration_minutes?: number;
  pace_target_min_per_km?: number;
  pace_range?: { min: number; max: number };
  heart_rate_zones?: number[];
  heart_rate_percentage?: { min: number; max: number };
  rpe_target?: number;
  intervals?: Array<{
    duration: string;
    pace_target: string;
    recovery: string;
    repetitions: number;
  }>;
  notes?: string;
  completed?: boolean;
  completed_date?: string;
  actual_distance_km?: number;
  actual_pace?: number;
  actual_hr_avg?: number;
}

interface WorkoutCardProps {
  workout: Workout;
  weekNum?: number;
  onComplete?: (workout: Workout) => void;
  expandable?: boolean;
}

export function WorkoutCard({ 
  workout, 
  weekNum,
  onComplete,
  expandable = true 
}: WorkoutCardProps) {
  const [expanded, setExpanded] = useState(false);

  const getWorkoutColor = (type: string) => {
    const colors: Record<string, { border: string; bg: string; text: string }> = {
      'easy_run': {
        border: 'border-green-500',
        bg: 'bg-green-900/20',
        text: 'text-green-400'
      },
      'tempo_run': {
        border: 'border-yellow-500',
        bg: 'bg-yellow-900/20',
        text: 'text-yellow-400'
      },
      'interval_run': {
        border: 'border-red-500',
        bg: 'bg-red-900/20',
        text: 'text-red-400'
      },
      'long_run': {
        border: 'border-blue-500',
        bg: 'bg-blue-900/20',
        text: 'text-blue-400'
      },
      'recovery': {
        border: 'border-purple-500',
        bg: 'bg-purple-900/20',
        text: 'text-purple-400'
      },
      'cross_training': {
        border: 'border-orange-500',
        bg: 'bg-orange-900/20',
        text: 'text-orange-400'
      },
      'strength': {
        border: 'border-pink-500',
        bg: 'bg-pink-900/20',
        text: 'text-pink-400'
      },
    };
    return colors[type] || {
      border: 'border-slate-600',
      bg: 'bg-slate-700/20',
      text: 'text-slate-300'
    };
  };

  const getWorkoutTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      'easy_run': 'Rodaje Suave',
      'tempo_run': 'Tempo',
      'interval_run': 'Series/Intervalos',
      'long_run': 'Rodaje Largo',
      'recovery': 'Recuperación',
      'cross_training': 'Cross Training',
      'strength': 'Fuerza',
    };
    return labels[type] || type;
  };

  const formatPace = (pace: number) => {
    const minutes = Math.floor(pace);
    const seconds = Math.round((pace % 1) * 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}/km`;
  };

  const colors = getWorkoutColor(workout.type);
  const hasActualData = workout.completed && (
    workout.actual_distance_km || workout.actual_pace || workout.actual_hr_avg
  );

  return (
    <Card className={`${colors.border} ${colors.bg} border-2`}>
      <CardHeader>
        <div
          className={`flex items-start justify-between ${expandable ? 'cursor-pointer' : ''}`}
          onClick={() => expandable && setExpanded(!expanded)}
        >
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-1">
              <CardTitle className="text-white text-lg">
                {workout.name || getWorkoutTypeLabel(workout.type)}
              </CardTitle>
              {workout.completed ? (
                <CheckCircle2 className="h-5 w-5 text-green-400" />
              ) : (
                <Circle className="h-5 w-5 text-slate-500" />
              )}
            </div>
            <Badge className={`${colors.border} ${colors.text} border`}>
              {getWorkoutTypeLabel(workout.type)}
            </Badge>
          </div>
          {expandable && (
            <Button variant="ghost" size="sm" className="ml-2">
              {expanded ? (
                <ChevronUp className="h-4 w-4" />
              ) : (
                <ChevronDown className="h-4 w-4" />
              )}
            </Button>
          )}
        </div>
      </CardHeader>

      {/* Main Stats (always visible) */}
      <CardContent>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-3">
          {workout.distance_km && (
            <div className="flex items-center gap-2">
              <Route className="h-4 w-4 text-slate-400" />
              <div>
                <div className="text-xs text-slate-400">Distancia</div>
                <div className="font-semibold text-white">
                  {workout.distance_km.toFixed(1)} km
                </div>
                {hasActualData && workout.actual_distance_km && (
                  <div className="text-xs text-green-400">
                    ✓ {workout.actual_distance_km.toFixed(1)} km
                  </div>
                )}
              </div>
            </div>
          )}
          
          {workout.pace_target_min_per_km && (
            <div className="flex items-center gap-2">
              <Target className="h-4 w-4 text-slate-400" />
              <div>
                <div className="text-xs text-slate-400">Ritmo Obj.</div>
                <div className="font-semibold text-white">
                  {formatPace(workout.pace_target_min_per_km)}
                </div>
                {hasActualData && workout.actual_pace && (
                  <div className="text-xs text-green-400">
                    ✓ {formatPace(workout.actual_pace)}
                  </div>
                )}
              </div>
            </div>
          )}
          
          {workout.duration_minutes && (
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4 text-slate-400" />
              <div>
                <div className="text-xs text-slate-400">Duración</div>
                <div className="font-semibold text-white">
                  {workout.duration_minutes} min
                </div>
              </div>
            </div>
          )}
          
          {workout.heart_rate_zones && workout.heart_rate_zones.length > 0 && (
            <div className="flex items-center gap-2">
              <Heart className="h-4 w-4 text-slate-400" />
              <div>
                <div className="text-xs text-slate-400">Zonas HR</div>
                <div className="font-semibold text-white">
                  {workout.heart_rate_zones.map(z => `Z${z}`).join(', ')}
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Comparison (if completed) */}
        {hasActualData && (
          <Card className="bg-green-900/20 border-green-500/50 mb-3">
            <CardContent className="pt-4">
              <div className="text-sm font-semibold text-green-400 mb-2">
                Comparación: Planificado vs Realizado
              </div>
              <div className="grid grid-cols-3 gap-2 text-xs">
                {workout.distance_km && workout.actual_distance_km && (
                  <div>
                    <div className="text-slate-400">Distancia</div>
                    <div className="text-white">
                      {workout.actual_distance_km.toFixed(1)} / {workout.distance_km.toFixed(1)} km
                    </div>
                  </div>
                )}
                {workout.pace_target_min_per_km && workout.actual_pace && (
                  <div>
                    <div className="text-slate-400">Ritmo</div>
                    <div className="text-white">
                      {formatPace(workout.actual_pace)} / {formatPace(workout.pace_target_min_per_km)}
                    </div>
                  </div>
                )}
                {workout.actual_hr_avg && (
                  <div>
                    <div className="text-slate-400">FC Promedio</div>
                    <div className="text-white">
                      {workout.actual_hr_avg} bpm
                    </div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Expanded Details */}
        {expanded && (
          <div className="space-y-3 pt-3 border-t border-slate-700">
            {/* Pace Range */}
            {workout.pace_range && (
              <div>
                <div className="text-xs text-slate-400 mb-1">Rango de Ritmo:</div>
                <div className="text-sm text-white">
                  {formatPace(workout.pace_range.min)} - {formatPace(workout.pace_range.max)}
                </div>
              </div>
            )}

            {/* Heart Rate Percentage */}
            {workout.heart_rate_percentage && (
              <div>
                <div className="text-xs text-slate-400 mb-1">FC (% máximo):</div>
                <div className="text-sm text-white">
                  {workout.heart_rate_percentage.min}% - {workout.heart_rate_percentage.max}%
                </div>
              </div>
            )}

            {/* RPE Target */}
            {workout.rpe_target && (
              <div>
                <div className="text-xs text-slate-400 mb-1">RPE Objetivo:</div>
                <div className="text-sm text-white">
                  {workout.rpe_target}/10
                </div>
              </div>
            )}

            {/* Intervals */}
            {workout.intervals && workout.intervals.length > 0 && (
              <div>
                <div className="text-xs text-slate-400 mb-2">Intervalos:</div>
                <div className="space-y-2">
                  {workout.intervals.map((interval, idx) => (
                    <Card key={idx} className="bg-slate-900/50 border-slate-700">
                      <CardContent className="pt-3">
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs">
                          <div>
                            <div className="text-slate-400">Duración</div>
                            <div className="text-white font-semibold">{interval.duration}</div>
                          </div>
                          <div>
                            <div className="text-slate-400">Ritmo</div>
                            <div className="text-white font-semibold">{interval.pace_target}</div>
                          </div>
                          <div>
                            <div className="text-slate-400">Recuperación</div>
                            <div className="text-white font-semibold">{interval.recovery}</div>
                          </div>
                          <div>
                            <div className="text-slate-400">Repeticiones</div>
                            <div className="text-white font-semibold">{interval.repetitions}x</div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            )}

            {/* Notes */}
            {workout.notes && (
              <div>
                <div className="text-xs text-slate-400 mb-1">Notas:</div>
                <div className="text-sm text-slate-300 italic">{workout.notes}</div>
              </div>
            )}

            {/* Complete Button */}
            {!workout.completed && onComplete && (
              <Button
                onClick={() => onComplete(workout)}
                className="w-full bg-green-600 hover:bg-green-700"
              >
                <CheckCircle2 className="h-4 w-4 mr-2" />
                Marcar como Completado
              </Button>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
