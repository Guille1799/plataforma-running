'use client';

import { useState, useRef, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useRouter } from 'next/navigation';
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
  has_target_race: boolean | null;
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
  const router = useRouter();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [raceSearchQuery, setRaceSearchQuery] = useState('');
  const [raceSearchResults, setRaceSearchResults] = useState<RaceSearchResult[]>([]);
  const [showRaceSearch, setShowRaceSearch] = useState(false);
  const [isSearching, setIsSearching] = useState(false);
  const searchTimeoutRef = useRef<any>(null);

  // Hooks for duration calculation (MOVED TO TOP - outside conditionals)
  const durationCalc = useCalculateDurationWithRace();
  const durationOpts = useDurationOptions();
  const [selectedDurationOption, setSelectedDurationOption] = useState<number | null>(null);

  const [formData, setFormData] = useState<PlanFormData>({
    has_target_race: null,
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

  // FIXED: useEffect MUST be at top level, not inside conditionals
  useEffect(() => {
    if (step === 6 && formData.general_goal && !formData.has_target_race && !durationOpts.data) {
      durationOpts.getDurationOptions(formData.general_goal);
    }
  }, [step, formData.general_goal, formData.has_target_race, durationOpts]);

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
        const response = await apiClient.searchRaces(raceSearchQuery, undefined, undefined, undefined, undefined, undefined, 30);
        
        let races = response.races || [];
        
        // FILTER: Show only FUTURE races (from today onwards)
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        races = races.filter(race => {
          const raceDate = new Date(race.date);
          raceDate.setHours(0, 0, 0, 0);
          return raceDate >= today; // Only future races from today onwards
        });
        
        setRaceSearchResults(races);
        setIsSearching(false);
      } catch (err) {
        console.error('❌ SEARCH ERROR:', err);
        console.error('❌ SEARCH ERROR stack:', (err as any)?.stack);
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
      }
    } catch (err) {
      console.error('Error calculating duration:', err);
      // Don't alert - just skip duration calculation and let user proceed
      setFormData(prev => ({
        ...prev,
        plan_duration_weeks: 12,
        duration_recommendation: 'Plan estándar de 12 semanas',
      }));
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

  // Validar si todos los campos obligatorios del paso actual están rellenos
  const isStepValid = (): boolean => {
    switch (step) {
      case 1:
        // Paso 1: Debe seleccionar Sí o No explícitamente
        return formData.has_target_race !== null;
      case 2:
        // Paso 2: Objetivo general Y Prioridad (ambos son obligatorios)
        return formData.general_goal !== null && formData.priority !== null;
      case 3:
        // Paso 3: Prioridad y días de entrenamiento
        return formData.priority !== null && formData.training_days_per_week !== null;
      case 4:
        // Paso 4: Día tirada larga (SOLO validar que esté seleccionado)
        return formData.preferred_long_run_day !== null;
      case 5:
        // Paso 5: Entrenamientos Adicionales (Fuerza + Cross-training)
        // Strength training: must select if YES
        if (formData.include_strength_training === null) return false;
        if (formData.include_strength_training && !formData.strength_location) return false;
        // Cross training: must select if YES
        if (formData.include_cross_training === null) return false;
        if (formData.include_cross_training && formData.cross_training_types.length === 0) return false;
        return true;
      case 6:
        // Paso 6: Método de entrenamiento y recuperación
        return formData.training_method !== null && formData.recovery_focus !== null && formData.plan_duration_weeks !== null;
      default:
        return true;
    }
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
      alert('Por favor selecciona al menos 1 día para la tirada larga');
      return;
    }
    if (formData.include_strength_training === null) {
      alert('Por favor indica si incluir entrenamientos de fuerza');
      return;
    }
    if (formData.include_strength_training && !formData.strength_location) {
      alert('Por favor selecciona el tipo de entrenamiento de fuerza');
      return;
    }
    if (formData.include_cross_training === null) {
      alert('Por favor indica si incluir cross-training');
      return;
    }
    if (formData.include_cross_training && formData.cross_training_types.length === 0) {
      alert('Por favor selecciona al menos 1 deporte para cross-training');
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
      // Asegurar formato correcto para preferred_long_run_day (puede ser múltiples días separados por coma)
      const longRunDays = formData.preferred_long_run_day?.split(',').map(d => d.trim()).filter(Boolean) || [];
      const dayValue = longRunDays.length > 0 ? longRunDays[0].toLowerCase() : 'saturday';

      const response = await apiClient.generateWeeklyPlan({
        general_goal: finalGoal,
        priority: formData.priority,
        has_target_race: formData.has_target_race,
        target_race: formData.target_race,
        training_days_per_week: formData.training_days_per_week,
        preferred_long_run_day: dayValue,
        plan_duration_weeks: formData.plan_duration_weeks || 12,
        include_strength_training: formData.include_strength_training,
        strength_location: formData.strength_location || 'with_equipment',
        training_method: formData.training_method || 'automatic',
        include_cross_training: formData.include_cross_training || false,
        cross_training_types: formData.cross_training_types || [],
        recovery_focus: formData.recovery_focus || 'moderate',
        injury_considerations: formData.injury_considerations,
      } as any);

      onPlanCreated(response.plan);
    } catch (err) {
      console.error('Error creating plan:', err);
      const errorMsg = err instanceof Error ? err.message : 'Error desconocido';
      const errorDetail = err instanceof Response ? await err.json().catch(() => ({})) : {};
      console.error('Error details:', errorDetail);
      alert(`Error al crear el plan: ${errorMsg}\n\nMira la consola para más detalles.`);
    } finally {
      setIsLoading(false);
    }
  };

  // PASO 1: Carrera Objetivo (FIRST STEP)
  if (step === 1) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">1. ¿Tienes una carrera objetivo? 🏁</CardTitle>
          <p className="text-sm text-slate-400 mt-2">
            Esto nos ayuda a personalizar el plan perfectamente para tu meta
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.has_target_race === null && (
            <p className="text-sm text-orange-400 text-center mb-2">⚠️ Selecciona una opción para continuar</p>
          )}
          <div className="flex gap-4">
            <button
              onClick={() => {
                setFormData({ ...formData, has_target_race: false });
                setStep(2);
              }}
              className={`flex-1 p-4 rounded-lg border-2 text-left transition ${
                formData.has_target_race === false
                  ? 'border-green-500 bg-green-900/30'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              <div className={`font-semibold ${
                formData.has_target_race === false ? 'text-green-400' : 'text-white'
              }`}>
                No
              </div>
              <div className={`text-sm ${
                formData.has_target_race === false ? 'text-green-300' : 'text-slate-400'
              }`}>
                Entrenar sin carrera específica
              </div>
            </button>
            <button
              onClick={() => {
                setFormData({ ...formData, has_target_race: true });
                setShowRaceSearch(true);
              }}
              className={`flex-1 p-4 rounded-lg border-2 text-left transition ${
                formData.has_target_race === true
                  ? 'border-blue-500 bg-blue-900/30'
                  : 'border-slate-600 hover:border-slate-500'
              }`}
            >
              <div className={`font-semibold ${
                formData.has_target_race === true ? 'text-blue-400' : 'text-white'
              }`}>
                Sí
              </div>
              <div className={`text-sm ${
                formData.has_target_race === true ? 'text-blue-300' : 'text-slate-400'
              }`}>
                Tengo una carrera en mente
              </div>
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
                  {raceSearchResults.map(race => {
                    const raceDate = new Date(race.date);
                    const today = new Date();
                    const daysUntilRace = Math.floor((raceDate.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));
                    const isVeryClose = daysUntilRace < 14;

                    return (
                      <button
                        key={race.id}
                        onClick={() => selectRace(race)}
                        className={`w-full p-3 text-left rounded transition ${
                          isVeryClose
                            ? 'bg-orange-600/30 border border-orange-500 hover:bg-orange-600/50'
                            : 'bg-slate-600 hover:bg-slate-500 border border-transparent'
                        }`}
                      >
                        <div className="font-semibold text-white flex justify-between items-start">
                          <span>{race.name}</span>
                          {isVeryClose && <span className="text-xs bg-orange-600 px-2 py-1 rounded">⚠️ Próxima</span>}
                        </div>
                        <div className="text-xs text-slate-300">
                          {race.distance_km} km • {new Date(race.date).toLocaleDateString('es-ES')} • {race.location}
                        </div>
                        {isVeryClose && (
                          <div className="text-xs text-orange-300 mt-1">
                            ⏰ Solo {daysUntilRace} días - El coach te ayudará a planificar el tapering
                          </div>
                        )}
                      </button>
                    );
                  })}
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
            <Button 
              onClick={() => setStep(3)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 3: Disponibilidad
  if (step === 3) {
    const daysOfWeek = [
      { value: 'monday', label: 'Lunes' },
      { value: 'tuesday', label: 'Martes' },
      { value: 'wednesday', label: 'Miércoles' },
      { value: 'thursday', label: 'Jueves' },
      { value: 'friday', label: 'Viernes' },
      { value: 'saturday', label: 'Sábado' },
      { value: 'sunday', label: 'Domingo' },
    ];

    // FIX: preferred_long_run_day can be multiple days (1-2) as string array or comma-separated
    const selectedDays = formData.preferred_long_run_day 
      ? (typeof formData.preferred_long_run_day === 'string' 
          ? formData.preferred_long_run_day.split(',') 
          : [formData.preferred_long_run_day])
      : [];

    const toggleDay = (day: string) => {
      let newDays = selectedDays.includes(day)
        ? selectedDays.filter(d => d !== day)
        : [...selectedDays, day];
      
      // Max 2 days
      if (newDays.length > 2) {
        alert('Máximo 2 días para tirada larga');
        return;
      }
      
      setFormData({
        ...formData,
        preferred_long_run_day: newDays.join(',') as any,
      });
    };

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
            <label className="block text-sm font-medium mb-3 text-white">
              Días para tirada larga <span className="text-xs text-slate-400">(elige 1-2 días)</span>
            </label>
            <div className="grid grid-cols-2 gap-2">
              {daysOfWeek.map(day => (
                <label
                  key={day.value}
                  className={`p-3 rounded border-2 cursor-pointer transition ${
                    selectedDays.includes(day.value)
                      ? 'border-blue-500 bg-blue-900/30'
                      : 'border-slate-600 hover:border-slate-500'
                  }`}
                >
                  <input
                    type="checkbox"
                    checked={selectedDays.includes(day.value)}
                    onChange={() => toggleDay(day.value)}
                    className="mr-2"
                  />
                  <span className="text-white">{day.label}</span>
                </label>
              ))}
            </div>
            {selectedDays.length === 0 && (
              <p className="text-xs text-red-400 mt-2">⚠️ Selecciona al menos 1 día</p>
            )}
            {selectedDays.length > 0 && (
              <p className="text-xs text-blue-400 mt-2">✓ Seleccionados: {selectedDays.length} día(s)</p>
            )}
          </div>

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(2)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button 
              onClick={() => setStep(4)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
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
              <label className="block text-sm font-medium mb-2 text-white">Tipo de entrenamiento de fuerza</label>
              <div className="space-y-2">
                {[
                  { value: 'with_equipment', label: '🏋️ Con equipo', desc: 'Pesas, kettlebells, bandas...' },
                  { value: 'bodyweight', label: '💪 Sin equipo', desc: 'Peso corporal, sentadillas, flexiones...' },
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
                    <div className="font-semibold text-white">{option.label}</div>
                    <div className="text-xs text-slate-400">{option.desc}</div>
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
                  onClick={() => {
                    const newValue = idx === 1;
                    setFormData({ 
                      ...formData, 
                      include_cross_training: newValue,
                      cross_training_types: idx === 0 ? [] : formData.cross_training_types // Clear types if selecting "No"
                    });
                  }}
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

          {formData.include_cross_training && (
            <div>
              <label className="block text-sm font-medium mb-3 text-white">
                Selecciona deportes complementarios <span className="text-xs text-slate-400">(elige 1 o más)</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: 'swimming', label: '🏊 Natación' },
                  { value: 'cycling', label: '🚴 Ciclismo' },
                  { value: 'rowing', label: '🚣 Remo' },
                  { value: 'triathlon', label: '🏃‍♂️ Triatlón' },
                  { value: 'yoga', label: '🧘 Yoga' },
                  { value: 'pilates', label: '🤸 Pilates' },
                ].map(sport => (
                  <label
                    key={sport.value}
                    className={`p-3 rounded border-2 cursor-pointer transition ${
                      formData.cross_training_types.includes(sport.value)
                        ? 'border-green-500 bg-green-900/30'
                        : 'border-slate-600 hover:border-slate-500'
                    }`}
                  >
                    <input
                      type="checkbox"
                      checked={formData.cross_training_types.includes(sport.value)}
                      onChange={() => {
                        let newTypes = formData.cross_training_types.includes(sport.value)
                          ? formData.cross_training_types.filter(t => t !== sport.value)
                          : [...formData.cross_training_types, sport.value];
                        
                        // If selecting triathlon, remove swimming and cycling
                        if (sport.value === 'triathlon' && !formData.cross_training_types.includes('triathlon')) {
                          newTypes = newTypes.filter(t => t !== 'swimming' && t !== 'cycling');
                          newTypes.push('triathlon');
                        }
                        
                        // If triathlon is selected and we're removing it, don't auto-add swimming/cycling
                        if (sport.value === 'triathlon' && formData.cross_training_types.includes('triathlon')) {
                          newTypes = newTypes.filter(t => t !== 'triathlon');
                        }
                        
                        // Block selecting swimming or cycling if triathlon is selected
                        if ((sport.value === 'swimming' || sport.value === 'cycling') && 
                            formData.cross_training_types.includes('triathlon')) {
                          return; // Don't allow
                        }
                        
                        setFormData({ ...formData, cross_training_types: newTypes });
                      }}
                      disabled={
                        (sport.value === 'swimming' || sport.value === 'cycling') && 
                        formData.cross_training_types.includes('triathlon')
                      }
                      className="mr-2"
                    />
                    <span className={`text-sm ${
                      (sport.value === 'swimming' || sport.value === 'cycling') && 
                      formData.cross_training_types.includes('triathlon')
                        ? 'text-slate-500 line-through'
                        : 'text-white'
                    }`}>
                      {sport.label}
                    </span>
                  </label>
                ))}
              </div>
              <div className="mt-2 text-xs text-slate-400">
                ℹ️ Seleccionar Triatlón desactiva Natación y Ciclismo (ya incluidos)
              </div>
              {formData.cross_training_types.length === 0 && (
                <p className="text-xs text-orange-400 mt-2">⚠️ Selecciona al menos 1 deporte</p>
              )}
              {formData.cross_training_types.length > 0 && (
                <p className="text-xs text-green-400 mt-2">✓ Seleccionados: {formData.cross_training_types.length} deporte(s)</p>
              )}
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(3)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Atrás
            </Button>
            <Button 
              onClick={() => setStep(5)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
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
            <Button 
              onClick={() => setStep(6)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
              Siguiente
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 6: Duración del Plan
  if (step === 6) {
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
              disabled={isLoading || !isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 cursor-not-allowed opacity-50'}`}
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
