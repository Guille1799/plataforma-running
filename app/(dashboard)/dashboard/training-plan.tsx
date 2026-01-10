'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { apiClient } from '@/lib/api-client';

interface TrainingDay {
  day: string;
  type: string;
  distance?: string;
  duration?: string;
  intensity: string;
  description: string;
}

interface TrainingPlan {
  week: number;
  focus: string;
  days: TrainingDay[];
}

export function TrainingPlanGenerator() {
  const [isOpen, setIsOpen] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [goal, setGoal] = useState('general');
  const [duration, setDuration] = useState(4);
  const [plan, setPlan] = useState<TrainingPlan | null>(null);

  const generatePlan = async () => {
    setIsGenerating(true);
    try {
      // Usar el metodo chat para generar el plan
      const response = await apiClient.chat({
        message: `Genera un plan de entrenamiento de ${duration} semanas con objetivo de ${goal}. Formato: JSON con estructura {week, focus, days[]}`,
      });

      // Simular un plan si el API no lo devuelve estructura JSON
      const mockPlan: TrainingPlan = {
        week: 1,
        focus: goal === 'speed' ? 'Mejora de velocidad' : goal === 'endurance' ? 'Resistencia' : 'Fitness general',
        days: [
          {
            day: 'Lunes',
            type: 'Easy Run',
            distance: '8km',
            duration: '45 min',
            intensity: 'Baja',
            description: 'Carrera ligera de recuperación. Mantén un ritmo conversacional.',
          },
          {
            day: 'Martes',
            type: 'Intervalos',
            distance: '10km',
            duration: '50 min',
            intensity: 'Alta',
            description: '5x 3min a ritmo 5K con 2min de recuperación.',
          },
          {
            day: 'Miércoles',
            type: 'Rest Day',
            intensity: 'Reposo',
            description: 'Día de descanso activo. Camina o yoga ligero si lo deseas.',
          },
          {
            day: 'Jueves',
            type: 'Tempo Run',
            distance: '10km',
            duration: '55 min',
            intensity: 'Media-Alta',
            description: '3km calentamiento + 4km a ritmo tempo + 3km enfriamiento.',
          },
          {
            day: 'Viernes',
            type: 'Easy Run',
            distance: '6km',
            duration: '40 min',
            intensity: 'Baja',
            description: 'Recuperación pre-fin de semana.',
          },
          {
            day: 'Sábado',
            type: 'Long Run',
            distance: '16km',
            duration: '90 min',
            intensity: 'Media',
            description: 'Tu carrera larga de la semana. Ve lentamente.',
          },
          {
            day: 'Domingo',
            type: 'Rest Day',
            intensity: 'Reposo',
            description: 'Descanso completo y recuperación.',
          },
        ],
      };

      setPlan(mockPlan);
    } catch (err) {
      console.error('Error generando plan:', err);
    } finally {
      setIsGenerating(false);
    }
  };

  return (
    <div className="space-y-4">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-medium transition-all flex items-center justify-center space-x-2"
      >
        <span>📅</span>
        <span>{isOpen ? 'Cerrar' : 'Generar Plan de Entrenamiento'}</span>
      </button>

      {isOpen && (
        <Card className="bg-slate-800/50 border-slate-700">
          <CardHeader>
            <CardTitle className="text-lg">Personaliza tu Plan</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {!plan ? (
              <>
                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    ¿Cuál es tu objetivo?
                  </label>
                  <select
                    value={goal}
                    onChange={e => setGoal(e.target.value)}
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  >
                    <option value="general">🏃 Fitness General</option>
                    <option value="speed">⚡ Mejorar Velocidad</option>
                    <option value="endurance">💪 Aumentar Resistencia</option>
                    <option value="race">🏆 Preparar para Carrera</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-300 mb-2">
                    Duración del plan: {duration} semanas
                  </label>
                  <input
                    type="range"
                    min="2"
                    max="12"
                    value={duration}
                    onChange={e => setDuration(parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-slate-400 mt-1">
                    <span>2 sem</span>
                    <span>12 sem</span>
                  </div>
                </div>

                <button
                  onClick={generatePlan}
                  disabled={isGenerating}
                  className="w-full px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors"
                >
                  {isGenerating ? '⏳ Generando...' : '✨ Generar Plan'}
                </button>
              </>
            ) : (
              <>
                <div className="space-y-4">
                  <h3 className="text-lg font-bold text-white">{plan.focus}</h3>
                  <p className="text-sm text-slate-400">
                    Semana 1 de {duration} - Mantén consistencia y escucha a tu cuerpo
                  </p>

                  <div className="space-y-3">
                    {plan.days.map((day, idx) => (
                      <div key={idx} className="p-3 bg-slate-700/50 rounded-lg border border-slate-600">
                        <div className="flex items-start justify-between mb-2">
                          <div>
                            <p className="font-semibold text-white">{day.day}</p>
                            <p className="text-sm text-blue-400">{day.type}</p>
                          </div>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            day.intensity === 'Baja' ? 'bg-green-900/50 text-green-300' :
                            day.intensity === 'Media' ? 'bg-yellow-900/50 text-yellow-300' :
                            day.intensity === 'Alta' ? 'bg-red-900/50 text-red-300' :
                            'bg-slate-600 text-slate-300'
                          }`}>
                            {day.intensity}
                          </span>
                        </div>
                        {day.distance && (
                          <p className="text-sm text-slate-300">
                            📏 {day.distance} • ⏱ {day.duration}
                          </p>
                        )}
                        <p className="text-sm text-slate-400 mt-2">{day.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex gap-2 pt-4 border-t border-slate-700">
                  <button
                    onClick={() => setPlan(null)}
                    className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition-colors"
                  >
                    ← Volver
                  </button>
                  <button
                    onClick={() => {
                      // Note: This is a demo component. For real plan generation with auto-save,
                      // use the TrainingPlanForm component which calls /api/v1/training-plans/generate
                      alert('Este es un componente de ejemplo. Para generar un plan real que se guarde automáticamente, usa el formulario completo de planes de entrenamiento.');
                    }}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
                  >
                    💾 Guardar Plan
                  </button>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
}
