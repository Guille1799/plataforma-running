'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiClient } from '@/lib/api-client';

interface TrainingGoal {
  race_name: string;
  race_date: string;
  distance_km: number;
  target_time_minutes: number;
  target_pace_min_per_km: number;
}

interface PlanFormData {
  general_goal: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance';
  priority: 'speed' | 'endurance' | 'recovery' | 'balanced';
  has_target_race: boolean;
  target_race?: TrainingGoal;
  training_days_per_week: number;
  preferred_long_run_day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  plan_duration_weeks: number;
  include_strength_training: boolean;
  strength_location: 'gym' | 'home' | 'none';
  training_method: 'pace_based' | 'heart_rate_based';
  include_cross_training: boolean;
  cross_training_types: string[];
  recovery_focus: 'minimal' | 'moderate' | 'high';
  injury_considerations?: string;
}

interface TrainingPlan {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  weeks: TrainingWeek[];
}

interface TrainingWeek {
  week_number: number;
  days: TrainingDay[];
  total_km: number;
}

interface TrainingDay {
  day: string;
  type: string;
  description: string;
  distance_km?: number;
  pace_min_per_km?: number;
  heart_rate_zone?: number;
  duration_minutes?: number;
}

export function TrainingPlanForm({ onPlanCreated }: { onPlanCreated: (plan: TrainingPlan) => void }) {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState<PlanFormData>({
    general_goal: 'improve_fitness',
    priority: 'balanced',
    has_target_race: false,
    training_days_per_week: 4,
    preferred_long_run_day: 'saturday',
    plan_duration_weeks: 8,
    include_strength_training: true,
    strength_location: 'gym',
    training_method: 'pace_based',
    include_cross_training: false,
    cross_training_types: [],
    recovery_focus: 'moderate',
  });

  const handleCreatePlan = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.generateWeeklyPlan({
        general_goal: formData.general_goal,
        priority: formData.priority,
        has_target_race: formData.has_target_race,
        target_race: formData.target_race,
        training_days_per_week: formData.training_days_per_week,
        preferred_long_run_day: formData.preferred_long_run_day,
        plan_duration_weeks: formData.plan_duration_weeks,
        include_strength_training: formData.include_strength_training,
        strength_location: formData.strength_location,
        training_method: formData.training_method,
        include_cross_training: formData.include_cross_training,
        cross_training_types: formData.cross_training_types,
        recovery_focus: formData.recovery_focus,
        injury_considerations: formData.injury_considerations,
      });

      onPlanCreated(response.plan as TrainingPlan);
    } catch (err) {
      console.error('Error creating plan:', err);
      alert('Error al crear el plan. Intenta nuevamente.');
    } finally {
      setIsLoading(false);
    }
  };

  // PASO 1: Objetivo General
  if (step === 1) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">1. ¿Cuál es tu objetivo general?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { value: 'marathon', label: 'Maratón (42km)' },
            { value: 'half_marathon', label: 'Media Maratón (21km)' },
            { value: '10k', label: '10 Kilómetros' },
            { value: '5k', label: '5 Kilómetros' },
            { value: 'improve_fitness', label: 'Mejorar condición física' },
            { value: 'build_endurance', label: 'Aumentar resistencia' },
          ].map(goal => (
            <button
              key={goal.value}
              onClick={() => setFormData({ ...formData, general_goal: goal.value as any })}
              className={`w-full p-4 rounded-lg border-2 text-left transition ${
                formData.general_goal === goal.value
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              {goal.label}
            </button>
          ))}
          <Button onClick={() => setStep(2)} className="w-full mt-6 bg-blue-600 hover:bg-blue-700">
            Siguiente
          </Button>
        </CardContent>
      </Card>
    );
  }

  // PASO 2: Prioridad
  if (step === 2) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">2. ¿Cuál es tu prioridad?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {[
            { value: 'speed', label: 'Velocidad 🚀', desc: 'Mejorar pace y velocidad' },
            { value: 'endurance', label: 'Resistencia 💪', desc: 'Aumentar distancias largas' },
            { value: 'recovery', label: 'Recuperación 😌', desc: 'Enfoque en descanso y prevención' },
            { value: 'balanced', label: 'Equilibrado ⚖️', desc: 'Balance entre velocidad y resistencia' },
          ].map(priority => (
            <button
              key={priority.value}
              onClick={() => setFormData({ ...formData, priority: priority.value as any })}
              className={`w-full p-4 rounded-lg border-2 text-left transition ${
                formData.priority === priority.value
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              <div className="font-semibold">{priority.label}</div>
              <div className="text-sm text-slate-400">{priority.desc}</div>
            </button>
          ))}
          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(1)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button onClick={() => setStep(3)} className="flex-1 bg-blue-600 hover:bg-blue-700">
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 3: Carrera Objetivo
  if (step === 3) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">3. ¿Tienes una carrera objetivo?</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <button
              onClick={() => setFormData({ ...formData, has_target_race: false })}
              className={`flex-1 p-4 rounded-lg border-2 transition ${
                !formData.has_target_race
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              No
            </button>
            <button
              onClick={() => setFormData({ ...formData, has_target_race: true })}
              className={`flex-1 p-4 rounded-lg border-2 transition ${
                formData.has_target_race
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              Sí
            </button>
          </div>

          {formData.has_target_race && (
            <div className="space-y-4 mt-6 p-4 bg-slate-700/50 rounded-lg">
              <input
                type="text"
                placeholder="Nombre de la carrera"
                value={formData.target_race?.race_name || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    target_race: { ...formData.target_race, race_name: e.target.value } as any,
                  })
                }
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400"
              />
              <input
                type="date"
                value={formData.target_race?.race_date || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    target_race: { ...formData.target_race, race_date: e.target.value } as any,
                  })
                }
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white"
              />
              <input
                type="number"
                placeholder="Distancia (km)"
                value={formData.target_race?.distance_km || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    target_race: { ...formData.target_race, distance_km: parseFloat(e.target.value) } as any,
                  })
                }
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400"
              />
              <input
                type="number"
                placeholder="Tiempo objetivo (minutos)"
                value={formData.target_race?.target_time_minutes || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    target_race: { ...formData.target_race, target_time_minutes: parseFloat(e.target.value) } as any,
                  })
                }
                className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400"
              />
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(2)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button onClick={() => setStep(4)} className="flex-1 bg-blue-600 hover:bg-blue-700">
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 4: Disponibilidad de Entrenamientos
  if (step === 4) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">4. Tu disponibilidad de entrenamientos</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2">¿Cuántos días a la semana puedes entrenar?</label>
            <div className="flex gap-2">
              {[3, 4, 5, 6, 7].map(days => (
                <button
                  key={days}
                  onClick={() => setFormData({ ...formData, training_days_per_week: days })}
                  className={`flex-1 p-3 rounded border-2 transition ${
                    formData.training_days_per_week === days
                      ? 'border-blue-500 bg-blue-900/30'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  {days}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">¿Qué día prefieres para la tirada larga?</label>
            <select
              value={formData.preferred_long_run_day}
              onChange={(e) =>
                setFormData({ ...formData, preferred_long_run_day: e.target.value as any })
              }
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white"
            >
              {['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'].map(day => (
                <option key={day} value={day}>
                  {day === 'monday' && 'Lunes'}
                  {day === 'tuesday' && 'Martes'}
                  {day === 'wednesday' && 'Miércoles'}
                  {day === 'thursday' && 'Jueves'}
                  {day === 'friday' && 'Viernes'}
                  {day === 'saturday' && 'Sábado'}
                  {day === 'sunday' && 'Domingo'}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">¿Cuántas semanas debe durar el plan?</label>
            <input
              type="number"
              min="2"
              max="52"
              value={formData.plan_duration_weeks}
              onChange={(e) => setFormData({ ...formData, plan_duration_weeks: parseInt(e.target.value) })}
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white"
            />
          </div>

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(3)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button onClick={() => setStep(5)} className="flex-1 bg-blue-600 hover:bg-blue-700">
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 5: Entrenamientos Adicionales
  if (step === 5) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">5. Entrenamientos adicionales</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3">¿Quieres incluir entrenamientos de fuerza?</label>
            <div className="flex gap-4">
              <button
                onClick={() => setFormData({ ...formData, include_strength_training: false })}
                className={`flex-1 p-3 rounded border-2 transition ${
                  !formData.include_strength_training
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                No
              </button>
              <button
                onClick={() => setFormData({ ...formData, include_strength_training: true })}
                className={`flex-1 p-3 rounded border-2 transition ${
                  formData.include_strength_training
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                Sí
              </button>
            </div>
          </div>

          {formData.include_strength_training && (
            <div>
              <label className="block text-sm font-medium mb-3">¿Dónde harás los entrenamientos de fuerza?</label>
              <div className="space-y-2">
                {[
                  { value: 'gym', label: '🏋️ Gimnasio' },
                  { value: 'home', label: '🏠 Casa' },
                ].map(option => (
                  <button
                    key={option.value}
                    onClick={() => setFormData({ ...formData, strength_location: option.value as any })}
                    className={`w-full p-3 rounded border-2 transition text-left ${
                      formData.strength_location === option.value
                        ? 'border-blue-500 bg-blue-900/30'
                        : 'border-slate-600 hover:border-slate-500'
                    }`}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-3">¿Quieres entrenamientos cruzados (cross-training)?</label>
            <div className="flex gap-4">
              <button
                onClick={() => setFormData({ ...formData, include_cross_training: false })}
                className={`flex-1 p-3 rounded border-2 transition ${
                  !formData.include_cross_training
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                No
              </button>
              <button
                onClick={() => setFormData({ ...formData, include_cross_training: true })}
                className={`flex-1 p-3 rounded border-2 transition ${
                  formData.include_cross_training
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                Sí
              </button>
            </div>
          </div>

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(4)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button onClick={() => setStep(6)} className="flex-1 bg-blue-600 hover:bg-blue-700">
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 6: Método de Entrenamiento
  if (step === 6) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">6. Método de entrenamiento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3">¿Planificación por ritmo o por BPM?</label>
            <div className="space-y-2">
              {[
                { value: 'pace_based', label: '⏱️ Basado en Ritmo (min/km)', desc: 'Control de velocidad' },
                { value: 'heart_rate_based', label: '❤️ Basado en Frecuencia Cardíaca', desc: 'Control por zonas HR' },
              ].map(method => (
                <button
                  key={method.value}
                  onClick={() => setFormData({ ...formData, training_method: method.value as any })}
                  className={`w-full p-4 rounded border-2 transition text-left ${
                    formData.training_method === method.value
                      ? 'border-blue-500 bg-blue-900/30'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <div className="font-semibold">{method.label}</div>
                  <div className="text-sm text-slate-400">{method.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3">¿Cuál es tu enfoque de recuperación?</label>
            <div className="space-y-2">
              {[
                { value: 'minimal', label: 'Mínima - Poco enfoque en descanso' },
                { value: 'moderate', label: 'Moderada - Balance entre esfuerzo y descanso' },
                { value: 'high', label: 'Alta - Mucho énfasis en recuperación' },
              ].map(recovery => (
                <button
                  key={recovery.value}
                  onClick={() => setFormData({ ...formData, recovery_focus: recovery.value as any })}
                  className={`w-full p-3 rounded border-2 transition text-left ${
                    formData.recovery_focus === recovery.value
                      ? 'border-blue-500 bg-blue-900/30'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  {recovery.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">¿Tienes lesiones o consideraciones especiales?</label>
            <textarea
              placeholder="Ej: Tengo tendinitis en el tobillo, evitar cambios bruscos..."
              value={formData.injury_considerations || ''}
              onChange={(e) => setFormData({ ...formData, injury_considerations: e.target.value })}
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400 h-20"
            />
          </div>

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(5)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button
              onClick={handleCreatePlan}
              disabled={isLoading}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              {isLoading ? 'Creando plan...' : 'Crear Plan de Entrenamiento'}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
}
