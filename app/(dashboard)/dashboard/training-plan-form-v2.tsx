'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { apiClient } from '@/lib/api-client';
import { useCalculateDurationWithRace, useDurationOptions } from '@/lib/hooks/useTrainingPlanDuration';

interface TrainingGoal {
  race_name: string;
  race_date: string;
  distance_km: number;
  target_time_minutes: number;
  target_pace_min_per_km?: number;
}

interface RaceSearchResult {
  id: string;
  name: string;
  date: string;
  distance_km: number;
  location?: string;
  region?: string;
  country?: string;
}

interface PlanFormData {
  has_target_race: boolean;
  target_race?: TrainingGoal;
  general_goal: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance' | null;
  priority: 'speed' | 'endurance' | 'recovery' | 'balanced' | null;
  training_days_per_week: number | null;
  preferred_long_run_day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday' | null;
  plan_duration_weeks: number | null;
  include_strength_training: boolean | null;
  strength_location: 'gym' | 'home' | 'none' | null;
  training_method: 'pace_based' | 'heart_rate_based' | 'automatic' | null;
  include_cross_training: boolean | null;
  cross_training_types: string[];
  recovery_focus: 'minimal' | 'moderate' | 'high' | null;
  injury_considerations?: string;
  duration_recommendation?: string;
}

export function TrainingPlanFormV2({ onPlanCreated }: { onPlanCreated: (plan: any) => void }) {
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [raceSearchQuery, setRaceSearchQuery] = useState('');
  const [raceSearchResults, setRaceSearchResults] = useState<RaceSearchResult[]>([]);
  const [showRaceSearch, setShowRaceSearch] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<any>(null);

  // Hooks for duration calculation
  const durationCalc = useCalculateDurationWithRace();
  const durationOpts = useDurationOptions();
  const [selectedDurationOption, setSelectedDurationOption] = useState<number | null>(null);

  const [formData, setFormData] = useState<PlanFormData>({
    has_target_race: false,
    general_goal: null,
    priority: null,
    training_days_per_week: null,
    preferred_long_run_day: null,
    plan_duration_weeks: null,
    include_strength_training: null,
    strength_location: null,
    training_method: null,
    include_cross_training: null,
    cross_training_types: [],
    recovery_focus: null,
  });

  // Búsqueda real de carreras via API
  useEffect(() => {
    if (raceSearchQuery.length < 2) {
      setRaceSearchResults([]);
      setIsSearching(false);
      return;
    }

    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);

    setIsSearching(true);
    searchTimeoutRef.current = setTimeout(async () => {
      try {
        console.log('🔍 Buscando carreras con query:', raceSearchQuery);
        const response = await apiClient.searchRaces(raceSearchQuery, undefined, undefined, undefined, undefined, undefined, 15);
        console.log('📍 Respuesta del API:', response);
        const races = response.races || [];
        console.log('🏃 Carreras encontradas:', races.length);
        setRaceSearchResults(races);
        setIsSearching(false);
      } catch (err) {
        console.error('❌ Error searching races:', err);
        setRaceSearchResults([]);
        setIsSearching(false);
      }
    }, 500);
  }, [raceSearchQuery]);

  const selectRace = async (race: RaceSearchResult) => {
    // Determinar objetivo basado en distancia
    let goal: any = 'improve_fitness';
    if (race.distance_km >= 42) goal = 'marathon';
    else if (race.distance_km >= 20) goal = 'half_marathon';
    else if (race.distance_km >= 9.5) goal = '10k';
    else if (race.distance_km >= 4.5) goal = '5k';

    // Update form data with race info
    setFormData({
      ...formData,
      has_target_race: true,
      target_race: {
        race_name: race.name,
        race_date: race.date,
        distance_km: race.distance_km,
        target_time_minutes: calculateDefaultTargetTime(race.distance_km),
        target_pace_min_per_km: calculateDefaultPace(race.distance_km),
      },
      general_goal: null, // No pre-select, leave for manual selection
    });

    // Calculate duration with race date
    try {
      const result = await durationCalc.calculate(race.date, goal);
      if (result) {
        setFormData(prev => ({
          ...prev,
          plan_duration_weeks: result.weeks,
          duration_recommendation: result.recommendation,
        }));
        console.log('✅ Duration calculated:', result);
      }
    } catch (err) {
      console.error('❌ Error calculating duration:', err);
      alert('Error al calcular la duración del plan. Usa valores por defecto.');
    }

    setShowRaceSearch(false);
    setRaceSearchQuery('');
  };

  const calculateDefaultTargetTime = (distanceKm: number): number => {
    // Asumir ritmo base de 6:00 min/km
    return distanceKm * 6;
  };

  const calculateDefaultPace = (distanceKm: number): number => {
    return 6.0;
  };

  const handleCreatePlan = async () => {
    // Determinar objetivo automático si hay carrera
    let finalGoal = formData.general_goal;
    if (formData.has_target_race && formData.target_race && !finalGoal) {
      const distance = formData.target_race.distance_km;
      if (distance >= 42) finalGoal = 'marathon';
      else if (distance >= 20) finalGoal = 'half_marathon';
      else if (distance >= 9.5) finalGoal = '10k';
      else if (distance >= 4.5) finalGoal = '5k';
      else finalGoal = 'improve_fitness';
    }

    // Validar que todos los campos estén rellenos
    if (!finalGoal) {
      alert('Por favor selecciona un objetivo general');
      return;
    }
    if (!formData.priority) {
      alert('Por favor selecciona una prioridad');
      return;
    }
    if (!formData.training_days_per_week) {
      alert('Por favor selecciona los días de entrenamiento');
      return;
    }
    if (!formData.preferred_long_run_day) {
      alert('Por favor selecciona un día para la tirada larga');
      return;
    }
    if (formData.include_strength_training === null) {
      alert('Por favor indica si incluir entrenamientos de fuerza');
      return;
    }
    if (formData.include_strength_training && !formData.strength_location) {
      alert('Por favor selecciona dónde harás los entrenamientos de fuerza');
      return;
    }
    if (formData.include_cross_training === null) {
      alert('Por favor indica si incluir cross-training');
      return;
    }
    if (!formData.training_method) {
      alert('Por favor selecciona un método de entrenamiento');
      return;
    }
    if (!formData.recovery_focus) {
      alert('Por favor selecciona un enfoque de recuperación');
      return;
    }
    if (!formData.plan_duration_weeks) {
      alert('Por favor selecciona una duración del plan');
      return;
    }

    setIsLoading(true);
    try {
      // Asegurar formato correcto para preferred_long_run_day (lowercase)
      const dayValue = formData.preferred_long_run_day?.toLowerCase() || 'saturday';

      const response = await apiClient.generateWeeklyPlan({
        general_goal: finalGoal,
        priority: formData.priority,
        has_target_race: formData.has_target_race,
        target_race: formData.target_race,
        training_days_per_week: formData.training_days_per_week,
        preferred_long_run_day: dayValue,
        plan_duration_weeks: formData.plan_duration_weeks || 12,
        include_strength_training: formData.include_strength_training,
        strength_location: formData.strength_location || 'gym',
        training_method: formData.training_method || 'automatic',
        include_cross_training: formData.include_cross_training || false,
        cross_training_types: formData.cross_training_types || [],
        recovery_focus: formData.recovery_focus || 'moderate',
        injury_considerations: formData.injury_considerations,
      } as any);

      onPlanCreated(response.plan);
    } catch (err) {
      console.error('Error creating plan:', err);
      alert('Error al crear el plan. Intenta nuevamente.');
    } finally {
      setIsLoading(false);
    }
  };

  // PASO 1: Carrera Objetivo (FIRST STEP)
  if (step === 1) {
    console.log('🎯 STEP 1 - showRaceSearch:', showRaceSearch, 'raceSearchQuery:', raceSearchQuery, 'results:', raceSearchResults.length);
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">1. ¿Tienes una carrera objetivo? 🏁</CardTitle>
          <p className="text-sm text-slate-400 mt-2">
            Esto nos ayuda a personalizar el plan perfectamente para tu meta
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-4">
            <button
              onClick={() => {
                setFormData({ ...formData, has_target_race: false });
                setStep(2);
              }}
              className="flex-1 p-4 rounded-lg border-2 border-slate-600 hover:border-slate-500 text-left"
            >
              <div className="font-semibold text-white">No</div>
              <div className="text-sm text-slate-400">Entrenar sin carrera específica</div>
            </button>
            <button
              onClick={() => {
                setFormData({ ...formData, has_target_race: true });
                setShowRaceSearch(true);
              }}
              className="flex-1 p-4 rounded-lg border-2 border-blue-500 bg-blue-900/30 text-left"
            >
              <div className="font-semibold text-blue-400">Sí</div>
              <div className="text-sm text-blue-300">Tengo una carrera en mente</div>
            </button>
          </div>

          {/* Búsqueda de Carreras */}
          {showRaceSearch && (
            <div className="space-y-4 p-4 bg-slate-700/50 rounded-lg">
              <div>
                <label className="block text-sm font-medium mb-2 text-white">Buscar Carrera</label>
                <input
                  type="text"
                  placeholder="Ej: Maratón de Madrid, 10K Barcelona..."
                  value={raceSearchQuery}
                  onChange={(e) => {
                    console.log('📝 Input changed:', e.target.value);
                    setRaceSearchQuery(e.target.value);
                  }}
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400"
                  autoFocus
                />
                {raceSearchQuery.length > 0 && raceSearchQuery.length < 2 && (
                  <p className="text-xs text-slate-400 mt-1">Escribe al menos 2 caracteres...</p>
                )}
              </div>

              {raceSearchResults.length > 0 && (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  <p className="text-xs text-slate-400">Se encontraron {raceSearchResults.length} carrera(s):</p>
                  {raceSearchResults.map(race => (
                    <button
                      key={race.id}
                      onClick={() => selectRace(race)}
                      className="w-full p-3 text-left bg-slate-600 hover:bg-slate-500 rounded transition"
                    >
                      <div className="font-semibold text-white">{race.name}</div>
                      <div className="text-xs text-slate-300">
                        {race.distance_km} km • {new Date(race.date).toLocaleDateString('es-ES')} • {race.location}
                      </div>
                    </button>
                  ))}
                </div>
              )}

              {raceSearchQuery && raceSearchQuery.length >= 2 && isSearching && (
                <div className="text-sm text-slate-400">
                  ⏳ Buscando carreras...
                </div>
              )}

              {raceSearchQuery && raceSearchQuery.length >= 2 && !isSearching && raceSearchResults.length === 0 && (
                <div className="text-sm text-slate-400">
                  ❌ No se encontraron carreras. Intenta con otro nombre o ubicación.
                </div>
              )}

              <div className="border-t border-slate-600 pt-3">
                <p className="text-xs text-slate-400 mb-3">¿No encuentras tu carrera? Puedes añadirla manualmente:</p>
                <button
                  onClick={() => {
                    setFormData({ ...formData, has_target_race: true });
                    setShowRaceSearch(false);
                    setStep(1.5); // New step for manual race entry
                  }}
                  className="w-full px-3 py-2 bg-slate-600 hover:bg-slate-500 rounded text-white text-sm"
                >
                  ✏️ Añadir Manualmente
                </button>
              </div>
            </div>
          )}

          {formData.has_target_race && formData.target_race && (
            <div className="p-4 bg-blue-900/20 border border-blue-600 rounded-lg space-y-3">
              <div className="font-semibold text-white mb-2">✅ Carrera seleccionada:</div>
              <div className="text-sm text-blue-300">
                <div>{formData.target_race.race_name}</div>
                <div>{formData.target_race.distance_km} km • {new Date(formData.target_race.race_date).toLocaleDateString('es-ES')}</div>
              </div>
              {formData.duration_recommendation && (
                <div className="p-3 bg-green-900/20 border border-green-600 rounded text-sm text-green-300">
                  💡 {formData.duration_recommendation}
                </div>
              )}
              {durationCalc.loading && (
                <div className="text-sm text-blue-300">⏳ Calculando duración recomendada...</div>
              )}
              {durationCalc.error && (
                <div className="text-sm text-red-300">❌ {durationCalc.error}</div>
              )}
            </div>
          )}

          <Button onClick={() => setStep(2)} className="w-full mt-6 bg-blue-600 hover:bg-blue-700">
            Siguiente
          </Button>
        </CardContent>
      </Card>
    );
  }

  // PASO 1.5: Añadir carrera manualmente
  if (step === 1.5) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Añadir Carrera Manualmente</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
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
            onChange={(e) => {
              const distance = parseFloat(e.target.value);
              setFormData({
                ...formData,
                target_race: {
                  ...formData.target_race,
                  distance_km: distance,
                  target_time_minutes: calculateDefaultTargetTime(distance),
                  target_pace_min_per_km: calculateDefaultPace(distance),
                } as any,
              });
            }}
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

          <div className="flex gap-3">
            <Button onClick={() => setStep(1)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button onClick={() => setStep(2)} className="flex-1 bg-blue-600 hover:bg-blue-700">
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 2: Objetivo General y Prioridad
  if (step === 2) {
    // Determinar objetivo automático si hay carrera
    const autoGoalFromRace = formData.has_target_race && formData.target_race ? (() => {
      const distance = formData.target_race.distance_km;
      if (distance >= 42) return 'marathon';
      if (distance >= 20) return 'half_marathon';
      if (distance >= 9.5) return '10k';
      if (distance >= 4.5) return '5k';
      return 'improve_fitness';
    })() : null;

    // Auto-establecer objetivo si viene de carrera
    if (autoGoalFromRace && !formData.general_goal) {
      setFormData(prev => ({ ...prev, general_goal: autoGoalFromRace as any }));
    }

    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">2. Objetivo y Prioridad</CardTitle>
          {formData.has_target_race && formData.target_race && (
            <p className="text-sm text-blue-400 mt-2">
              📌 Tu carrera ({formData.target_race.race_name}) sugiere el objetivo abajo
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.has_target_race && formData.target_race ? (
            <div className="p-4 bg-blue-900/20 border border-blue-500/50 rounded-lg">
              <label className="block text-sm font-medium mb-2 text-white">Objetivo (basado en tu carrera)</label>
              <div className="p-3 rounded-lg border-2 border-blue-500 bg-blue-900/30">
                {
                  {
                    'marathon': 'Maratón (42km)',
                    'half_marathon': 'Media Maratón (21km)',
                    '10k': '10 Kilómetros',
                    '5k': '5 Kilómetros',
                    'improve_fitness': 'Mejorar condición física',
                    'build_endurance': 'Aumentar resistencia',
                  }[autoGoalFromRace as string] || 'Objetivo personalizado'
                }
              </div>
              <p className="text-xs text-slate-400 mt-2">✓ Objetivo establecido automáticamente según tu carrera</p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium mb-3 text-white">Objetivo General</label>
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
                className={`w-full p-3 rounded-lg border-2 text-left mb-2 transition ${
                  formData.general_goal === goal.value
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                {goal.label}
              </button>
            ))}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium mb-3 text-white">Prioridad</label>
            {[
              { value: 'speed', label: 'Velocidad 🚀', desc: 'Mejorar pace' },
              { value: 'endurance', label: 'Resistencia 💪', desc: 'Distancias largas' },
              { value: 'recovery', label: 'Recuperación 😌', desc: 'Descanso y prevención' },
              { value: 'balanced', label: 'Equilibrado ⚖️', desc: 'Balance perfecto' },
            ].map(priority => (
              <button
                key={priority.value}
                onClick={() => setFormData({ ...formData, priority: priority.value as any })}
                className={`w-full p-3 rounded-lg border-2 text-left mb-2 transition ${
                  formData.priority === priority.value
                    ? 'border-blue-500 bg-blue-900/30'
                    : 'border-slate-600 hover:border-slate-500'
                }`}
              >
                <div className="font-semibold">{priority.label}</div>
                <div className="text-xs text-slate-400">{priority.desc}</div>
              </button>
            ))}
          </div>

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

  // PASO 3: Disponibilidad
  if (step === 3) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">3. Tu Disponibilidad</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-white">Días de entrenamiento por semana</label>
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
            <label className="block text-sm font-medium mb-2 text-white">Día para tirada larga</label>
            <select
              value={formData.preferred_long_run_day || ''}
              onChange={(e) =>
                setFormData({ ...formData, preferred_long_run_day: e.target.value as any })
              }
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white"
            >
              <option value="">-- Selecciona un día --</option>
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

  // PASO 4: Entrenamientos Adicionales
  if (step === 4) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">4. Entrenamientos Adicionales</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3 text-white">Entrenamientos de fuerza</label>
            <div className="flex gap-4">
              {['No', 'Sí'].map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => setFormData({ ...formData, include_strength_training: idx === 1 })}
                  className={`flex-1 p-3 rounded border-2 transition ${
                    formData.include_strength_training === (idx === 1)
                      ? 'border-blue-500 bg-blue-900/30'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>

          {formData.include_strength_training && (
            <div>
              <label className="block text-sm font-medium mb-2 text-white">¿Dónde?</label>
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
            <label className="block text-sm font-medium mb-3 text-white">Cross-training</label>
            <div className="flex gap-4">
              {['No', 'Sí'].map((option, idx) => (
                <button
                  key={idx}
                  onClick={() => setFormData({ ...formData, include_cross_training: idx === 1 })}
                  className={`flex-1 p-3 rounded border-2 transition ${
                    formData.include_cross_training === (idx === 1)
                      ? 'border-blue-500 bg-blue-900/30'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  {option}
                </button>
              ))}
            </div>
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

  // PASO 5: Método de Entrenamiento (CON OPCIÓN AUTOMÁTICO)
  if (step === 5) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">5. Método de Entrenamiento</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3 text-white">¿Cómo planificar?</label>
            <div className="space-y-2">
              {[
                { value: 'automatic', label: '🤖 Automático', desc: 'El coach elige el mejor método' },
                { value: 'pace_based', label: '⏱️ Por Ritmo (min/km)', desc: 'Control de velocidad' },
                { value: 'heart_rate_based', label: '❤️ Por Frecuencia Cardíaca', desc: 'Control por zonas HR' },
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
                  <div className="text-xs text-slate-400">{method.desc}</div>
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-3 text-white">Enfoque de Recuperación</label>
            <div className="space-y-2">
              {[
                { value: 'minimal', label: 'Mínima' },
                { value: 'moderate', label: 'Moderada' },
                { value: 'high', label: 'Alta' },
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
            <label className="block text-sm font-medium mb-2 text-white">Consideraciones especiales (lesiones, etc)</label>
            <textarea
              placeholder="Ej: Tengo tendinitis en el tobillo..."
              value={formData.injury_considerations || ''}
              onChange={(e) => setFormData({ ...formData, injury_considerations: e.target.value })}
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400 h-16"
            />
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

  // PASO 6: Duración del Plan
  if (step === 6) {
    const autoLoadDurationOptions = async () => {
      if (formData.general_goal && !formData.has_target_race && !durationOpts.data) {
        await durationOpts.getDurationOptions(formData.general_goal);
      }
    };

    useEffect(() => {
      autoLoadDurationOptions();
    }, [formData.general_goal]);

    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">6. Duración del Plan 📅</CardTitle>
          <p className="text-sm text-slate-400 mt-2">
            {formData.has_target_race 
              ? 'La duración se calculó automáticamente según tu carrera'
              : 'Elige la duración ideal para tu objetivo'}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.has_target_race && formData.plan_duration_weeks ? (
            <div className="p-4 bg-green-900/20 border border-green-600 rounded-lg space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-green-400">{formData.plan_duration_weeks}</span>
                <span className="text-lg text-green-300">semanas</span>
              </div>
              {formData.duration_recommendation && (
                <div className="text-sm text-green-300">
                  💡 {formData.duration_recommendation}
                </div>
              )}
              <p className="text-xs text-slate-400">✓ Duración automática para tu carrera objetivo</p>
            </div>
          ) : (
            <div className="space-y-3">
              {durationOpts.loading && (
                <div className="text-sm text-blue-300">⏳ Cargando opciones de duración...</div>
              )}
              {durationOpts.error && (
                <div className="text-sm text-red-300">❌ {durationOpts.error}</div>
              )}
              {durationOpts.data && durationOpts.data.length > 0 && (
                <div className="space-y-2">
                  {durationOpts.data.map((option) => (
                    <button
                      key={option.weeks}
                      onClick={() => {
                        setFormData({ ...formData, plan_duration_weeks: option.weeks });
                        setSelectedDurationOption(option.weeks);
                      }}
                      className={`w-full p-4 rounded-lg border-2 text-left transition ${
                        formData.plan_duration_weeks === option.weeks
                          ? 'border-blue-500 bg-blue-900/30'
                          : 'border-slate-600 hover:border-slate-500'
                      }`}
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <div className="font-bold text-white">{option.weeks} semanas</div>
                          <div className="text-sm text-slate-300">{option.label}</div>
                          <div className="text-xs text-slate-400 mt-1">{option.description}</div>
                        </div>
                        {option.recommended && (
                          <span className="bg-green-600 text-white text-xs px-2 py-1 rounded">
                            ⭐ Recomendado
                          </span>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              )}
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(5)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button
              onClick={handleCreatePlan}
              disabled={isLoading || !formData.plan_duration_weeks}
              className="flex-1 bg-green-600 hover:bg-green-700 disabled:bg-gray-600"
            >
              {isLoading ? 'Creando plan...' : '✨ Crear Plan de Entrenamiento'}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
}
