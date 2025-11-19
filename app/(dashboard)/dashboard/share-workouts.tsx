'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workout } from '@/lib/types';
import { formatDate, formatPace, formatDistance, formatDuration } from '@/lib/formatters';

interface ShareProps {
  workouts: Workout[];
}

export function ShareWorkouts({ workouts }: ShareProps) {
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [shareMessage, setShareMessage] = useState('');
  const [copied, setCopied] = useState(false);

  const generateShareMessage = (workout: Workout) => {
    const message = `🏃 Acabo de completar un entrenamiento:
    
📍 ${workout.sport_type || 'Running'}
📏 Distancia: ${formatDistance(workout.distance_meters)}
⏱ Tiempo: ${formatDuration(workout.duration_seconds)}
⚡ Pace: ${formatPace(workout.avg_pace)}
💓 HR: ${Math.round(workout.avg_heart_rate || 0)} bpm
📅 ${formatDate(workout.start_time)}

¡Únete a mi comunidad de corredores! 🏅
#RunCoachAI #Running #TrainingGoals`;
    return message;
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const generateShareLinks = (workout: Workout) => {
    const message = encodeURIComponent(generateShareMessage(workout));
    return {
      twitter: `https://twitter.com/intent/tweet?text=${message}`,
      whatsapp: `https://wa.me/?text=${message}`,
      facebook: `https://www.facebook.com/sharer/sharer.php?quote=${message}`,
    };
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">📤 Compartir Entrenamientos</h2>

      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-lg">Selecciona un entrenamiento para compartir</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="max-h-64 overflow-y-auto space-y-2">
            {workouts.length > 0 ? (
              workouts.map(workout => (
                <button
                  key={workout.id}
                  onClick={() => {
                    setSelectedWorkout(workout);
                    setShareMessage(generateShareMessage(workout));
                  }}
                  className={`w-full p-4 rounded-lg text-left transition-all border-2 ${
                    selectedWorkout?.id === workout.id
                      ? 'bg-blue-900/50 border-blue-500'
                      : 'bg-slate-700/50 border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-semibold text-white">{workout.sport_type || 'Running'}</p>
                      <p className="text-sm text-slate-400">{formatDate(workout.start_time)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-blue-400 font-medium">{formatDistance(workout.distance_meters)}</p>
                      <p className="text-sm text-slate-400">{formatPace(workout.avg_pace)}</p>
                    </div>
                  </div>
                </button>
              ))
            ) : (
              <p className="text-slate-400 text-center py-8">No hay entrenamientos para compartir</p>
            )}
          </div>

          {selectedWorkout && (
            <div className="space-y-4 pt-4 border-t border-slate-700">
              {/* Preview */}
              <div className="p-4 bg-slate-700/50 rounded-lg text-sm text-slate-100 whitespace-pre-wrap font-mono text-xs border border-slate-600">
                {shareMessage}
              </div>

              {/* Copy Button */}
              <button
                onClick={() => copyToClipboard(shareMessage)}
                className="w-full px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
              >
                <span>{copied ? '✓ Copiado' : '📋 Copiar Texto'}</span>
              </button>

              {/* Social Share Buttons */}
              <div className="space-y-2">
                <p className="text-xs text-slate-400 mb-2">Compartir en redes sociales:</p>
                <div className="grid grid-cols-3 gap-2">
                  <a
                    href={generateShareLinks(selectedWorkout).twitter}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg font-medium transition-colors text-center text-sm"
                  >
                    𝕏 Tweet
                  </a>
                  <a
                    href={generateShareLinks(selectedWorkout).whatsapp}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors text-center text-sm"
                  >
                    💬 WhatsApp
                  </a>
                  <a
                    href={generateShareLinks(selectedWorkout).facebook}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="px-3 py-2 bg-blue-700 hover:bg-blue-800 text-white rounded-lg font-medium transition-colors text-center text-sm"
                  >
                    f Facebook
                  </a>
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
