'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workout } from '@/lib/types';
import { formatDistance, formatPace, formatDuration, formatDate } from '@/lib/formatters';

interface ComparisonProps {
  workouts: Workout[];
}

export function WorkoutComparison({ workouts }: ComparisonProps) {
  const [selectedWorkouts, setSelectedWorkouts] = useState<number[]>([]);
  const [showComparison, setShowComparison] = useState(false);

  const toggleWorkoutSelection = (id: number) => {
    setSelectedWorkouts(prev => {
      if (prev.includes(id)) {
        return prev.filter(wid => wid !== id);
      } else if (prev.length < 3) {
        return [...prev, id];
      }
      return prev;
    });
  };

  const compareSelectedWorkouts = () => {
    if (selectedWorkouts.length < 2) {
      alert('Selecciona al menos 2 entrenamientos para comparar');
      return;
    }
    setShowComparison(true);
  };

  const comparingWorkouts = workouts.filter(w => selectedWorkouts.includes(w.id));

  // Calculate statistics
  const calculateStats = (workoutList: Workout[]) => {
    return {
      avgDistance: (workoutList.reduce((sum, w) => sum + (w.distance_meters || 0), 0) / workoutList.length) / 1000,
      avgPace: workoutList.reduce((sum, w) => sum + (w.avg_pace || 0), 0) / workoutList.length,
      avgHR: Math.round(workoutList.reduce((sum, w) => sum + (w.avg_heart_rate || 0), 0) / workoutList.length),
      avgDuration: Math.round(workoutList.reduce((sum, w) => sum + (w.duration_seconds || 0), 0) / workoutList.length),
      totalDistance: (workoutList.reduce((sum, w) => sum + (w.distance_meters || 0), 0)) / 1000,
      totalDuration: workoutList.reduce((sum, w) => sum + (w.duration_seconds || 0), 0),
    };
  };

  const sortedWorkouts = [...workouts].sort((a, b) => 
    new Date(b.start_time).getTime() - new Date(a.start_time).getTime()
  );

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">🔄 Comparar Entrenamientos</h2>

      {!showComparison ? (
        <>
          {/* Selection Mode */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-lg">
                Selecciona entrenamientos ({selectedWorkouts.length}/3)
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="max-h-96 overflow-y-auto space-y-2">
                {sortedWorkouts.map(workout => (
                  <button
                    key={workout.id}
                    onClick={() => toggleWorkoutSelection(workout.id)}
                    className={`w-full p-4 rounded-lg text-left transition-all border-2 ${
                      selectedWorkouts.includes(workout.id)
                        ? 'bg-blue-900/50 border-blue-500 shadow-lg'
                        : 'bg-slate-700/50 border-slate-600 hover:border-slate-500'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="font-semibold text-white">
                          {selectedWorkouts.includes(workout.id) ? '✓ ' : ''}
                          {workout.sport_type || 'Running'}
                        </p>
                        <p className="text-sm text-slate-400">
                          {formatDate(workout.start_time)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="text-blue-400 font-medium">
                          {formatDistance(workout.distance_meters)}
                        </p>
                        <p className="text-sm text-slate-400">
                          {formatPace(workout.avg_pace)}
                        </p>
                      </div>
                    </div>
                  </button>
                ))}
              </div>

              <div className="flex gap-3 pt-4 border-t border-slate-700">
                <button
                  onClick={compareSelectedWorkouts}
                  disabled={selectedWorkouts.length < 2}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
                >
                  🔄 Comparar ({selectedWorkouts.length})
                </button>
                <button
                  onClick={() => setSelectedWorkouts([])}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                >
                  Limpiar
                </button>
              </div>
            </CardContent>
          </Card>
        </>
      ) : (
        <>
          {/* Comparison View */}
          <div className="space-y-6">
            {/* Individual Workout Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {comparingWorkouts.map((workout, idx) => (
                <Card key={workout.id} className="bg-slate-800/50 border-slate-700">
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">
                        Entrenamiento {idx + 1}
                      </CardTitle>
                      <span className="text-xs bg-slate-700 px-2 py-1 rounded">
                        {new Date(workout.start_time).toLocaleDateString('es-ES')}
                      </span>
                    </div>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Tipo</p>
                      <p className="text-lg font-bold text-blue-400">
                        {workout.sport_type || 'Running'}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Distancia</p>
                      <p className="text-lg font-bold text-green-400">
                        {formatDistance(workout.distance_meters)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Tiempo</p>
                      <p className="text-lg font-bold text-yellow-400">
                        {formatDuration(workout.duration_seconds)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">Pace</p>
                      <p className="text-lg font-bold text-purple-400">
                        {formatPace(workout.avg_pace)}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-slate-400 mb-1">HR Promedio</p>
                      <p className="text-lg font-bold text-red-400">
                        {Math.round(workout.avg_heart_rate || 0)} bpm
                      </p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>

            {/* Comparison Summary */}
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-lg">📊 Análisis Comparativo</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Metrics Table */}
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-700">
                        <th className="text-left py-3 px-4 text-slate-400">Métrica</th>
                        {comparingWorkouts.map((w, idx) => (
                          <th key={w.id} className="text-center py-3 px-4 text-slate-300">
                            E{idx + 1}
                          </th>
                        ))}
                        <th className="text-center py-3 px-4 text-slate-300">Promedio</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-slate-700 hover:bg-slate-700/30">
                        <td className="py-3 px-4 text-slate-300">Distancia</td>
                        {comparingWorkouts.map(w => (
                          <td key={w.id} className="text-center py-3 px-4 text-blue-400 font-medium">
                            {formatDistance(w.distance_meters)}
                          </td>
                        ))}
                        <td className="text-center py-3 px-4 text-blue-300 font-bold">
                          {((calculateStats(comparingWorkouts).avgDistance).toFixed(2))} km
                        </td>
                      </tr>
                      <tr className="border-b border-slate-700 hover:bg-slate-700/30">
                        <td className="py-3 px-4 text-slate-300">Tiempo</td>
                        {comparingWorkouts.map(w => (
                          <td key={w.id} className="text-center py-3 px-4 text-green-400 font-medium">
                            {formatDuration(w.duration_seconds)}
                          </td>
                        ))}
                        <td className="text-center py-3 px-4 text-green-300 font-bold">
                          {formatDuration(calculateStats(comparingWorkouts).avgDuration)}
                        </td>
                      </tr>
                      <tr className="border-b border-slate-700 hover:bg-slate-700/30">
                        <td className="py-3 px-4 text-slate-300">Pace</td>
                        {comparingWorkouts.map(w => (
                          <td key={w.id} className="text-center py-3 px-4 text-purple-400 font-medium">
                            {formatPace(w.avg_pace)}
                          </td>
                        ))}
                        <td className="text-center py-3 px-4 text-purple-300 font-bold">
                          {formatPace(calculateStats(comparingWorkouts).avgPace)}
                        </td>
                      </tr>
                      <tr className="hover:bg-slate-700/30">
                        <td className="py-3 px-4 text-slate-300">HR Promedio</td>
                        {comparingWorkouts.map(w => (
                          <td key={w.id} className="text-center py-3 px-4 text-red-400 font-medium">
                            {Math.round(w.avg_heart_rate || 0)}
                          </td>
                        ))}
                        <td className="text-center py-3 px-4 text-red-300 font-bold">
                          {calculateStats(comparingWorkouts).avgHR}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>

                {/* Insights */}
                <div className="p-4 bg-slate-700/50 rounded-lg border border-slate-600 space-y-2">
                  <p className="font-semibold text-white mb-3">💡 Insights</p>
                  {comparingWorkouts.length >= 2 && (
                    <>
                      <p className="text-sm text-slate-300">
                        ✓ Distancia Máxima: <span className="text-blue-400 font-medium">
                          {formatDistance(Math.max(...comparingWorkouts.map(w => w.distance_meters || 0)))}
                        </span>
                      </p>
                      <p className="text-sm text-slate-300">
                        ✓ Pace Más Rápido: <span className="text-purple-400 font-medium">
                          {formatPace(Math.min(...comparingWorkouts.map(w => w.avg_pace || 999)))}
                        </span>
                      </p>
                      <p className="text-sm text-slate-300">
                        ✓ HR Máximo: <span className="text-red-400 font-medium">
                          {Math.max(...comparingWorkouts.map(w => w.max_heart_rate || 0))} bpm
                        </span>
                      </p>
                    </>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Button to go back */}
            <button
              onClick={() => {
                setShowComparison(false);
                setSelectedWorkouts([]);
              }}
              className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
            >
              ← Seleccionar Otros
            </button>
          </div>
        </>
      )}
    </div>
  );
}
