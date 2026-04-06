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
      alert('Please select a general goal');
      return;
    }
    if (!formData.priority) {
      alert('Please select a priority');
      return;
    }
    if (!formData.training_days_per_week) {
      alert('Please select your training days per week');
      return;
    }
    if (!formData.preferred_long_run_day) {
      alert('Please select at least 1 day for your long run');
      return;
    }
    if (formData.include_strength_training === null) {
      alert('Please indicate whether to include strength training');
      return;
    }
    if (formData.include_strength_training && !formData.strength_location) {
      alert('Please select a strength training type');
      return;
    }
    if (formData.include_cross_training === null) {
      alert('Please indicate whether to include cross-training');
      return;
    }
    if (formData.include_cross_training && formData.cross_training_types.length === 0) {
      alert('Please select at least 1 cross-training sport');
      return;
    }
    if (!formData.training_method) {
      alert('Please select a training method');
      return;
    }
    if (!formData.recovery_focus) {
      alert('Please select a recovery focus');
      return;
    }
    if (!formData.plan_duration_weeks) {
      alert('Please select a plan duration');
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
      const errorMsg = err instanceof Error ? err.message : 'Unknown error';
      const errorDetail = err instanceof Response ? await err.json().catch(() => ({})) : {};
      console.error('Error details:', errorDetail);
      alert(`Error creating plan: ${errorMsg}\n\nCheck the console for details.`);
    } finally {
      setIsLoading(false);
    }
  };

  // PASO 1: Carrera Objetivo (FIRST STEP)
  if (step === 1) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">1. Do you have a target race? 🏁</CardTitle>
          <p className="text-sm text-slate-400 mt-2">
            This helps us personalise the plan perfectly for your goal
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.has_target_race === null && (
            <p className="text-sm text-orange-400 text-center mb-2">⚠️ Select an option to continue</p>
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
                Train without a specific race
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
                Yes
              </div>
              <div className={`text-sm ${
                formData.has_target_race === true ? 'text-blue-300' : 'text-slate-400'
              }`}>
                I have a race in mind
              </div>
            </button>
          </div>

          {/* Race Search */}
          {showRaceSearch && (
            <div className="space-y-4 p-4 bg-slate-700/50 rounded-lg">
              <div>
                <label className="block text-sm font-medium mb-2 text-white">Search Race</label>
                <input
                  type="text"
                  placeholder="e.g. Madrid Marathon, 10K Barcelona..."
                  value={raceSearchQuery}
                  onChange={(e) => {
                    setRaceSearchQuery(e.target.value);
                  }}
                  className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400"
                  autoFocus
                />
                {raceSearchQuery.length > 0 && raceSearchQuery.length < 2 && (
                  <p className="text-xs text-slate-400 mt-1">Type at least 2 characters...</p>
                )}
              </div>

              {raceSearchResults.length > 0 && (
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  <p className="text-xs text-slate-400">Found {raceSearchResults.length} race(s):</p>
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
                          {isVeryClose && <span className="text-xs bg-orange-600 px-2 py-1 rounded">⚠️ Soon</span>}
                        </div>
                        <div className="text-xs text-slate-300">
                          {race.distance_km} km • {new Date(race.date).toLocaleDateString('en-GB')} • {race.location}
                        </div>
                        {isVeryClose && (
                          <div className="text-xs text-orange-300 mt-1">
                            ⏰ Only {daysUntilRace} days — the coach will help you plan your taper
                          </div>
                        )}
                      </button>
                    );
                  })}
                </div>
              )}

              {raceSearchQuery && raceSearchQuery.length >= 2 && isSearching && (
                <div className="text-sm text-slate-400">
                  ⏳ Searching races...
                </div>
              )}

              {raceSearchQuery && raceSearchQuery.length >= 2 && !isSearching && raceSearchResults.length === 0 && (
                <div className="text-sm text-slate-400">
                  ❌ No races found. Try a different name or location.
                </div>
              )}

              <div className="border-t border-slate-600 pt-3">
                <p className="text-xs text-slate-400 mb-3">Can&apos;t find your race? Add it manually:</p>
                <button
                  onClick={() => {
                    setFormData({ ...formData, has_target_race: true });
                    setShowRaceSearch(false);
                    setStep(1.5);
                  }}
                  className="w-full px-3 py-2 bg-slate-600 hover:bg-slate-500 rounded text-white text-sm"
                >
                  ✏️ Add Manually
                </button>
              </div>
            </div>
          )}

          {formData.has_target_race && formData.target_race && (
            <div className="p-4 bg-blue-900/20 border border-blue-600 rounded-lg space-y-3">
              <div className="font-semibold text-white mb-2">✅ Selected race:</div>
              <div className="text-sm text-blue-300">
                <div>{formData.target_race.race_name}</div>
                <div>{formData.target_race.distance_km} km • {new Date(formData.target_race.race_date).toLocaleDateString('en-GB')}</div>
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
            Next
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
          <CardTitle className="text-white">Add Race Manually</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <input
            type="text"
            placeholder="Race name"
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
            placeholder="Distance (km)"
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
            placeholder="Target time (minutes)"
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
              Back
            </Button>
            <Button onClick={() => setStep(2)} className="flex-1 bg-blue-600 hover:bg-blue-700">
              Next
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
          <CardTitle className="text-white">2. Goal &amp; Priority</CardTitle>
          {formData.has_target_race && formData.target_race && (
            <p className="text-sm text-blue-400 mt-2">
              📌 Your race ({formData.target_race.race_name}) suggests the goal below
            </p>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.has_target_race && formData.target_race ? (
            <div className="p-4 bg-blue-900/20 border border-blue-500/50 rounded-lg">
              <label className="block text-sm font-medium mb-2 text-white">Goal (based on your race)</label>
              <div className="p-3 rounded-lg border-2 border-blue-500 bg-blue-900/30">
                {
                  {
                    'marathon': 'Marathon (42km)',
                    'half_marathon': 'Half Marathon (21km)',
                    '10k': '10 Kilometres',
                    '5k': '5 Kilometres',
                    'improve_fitness': 'Improve fitness',
                    'build_endurance': 'Build endurance',
                  }[autoGoalFromRace as string] || 'Custom goal'
                }
              </div>
              <p className="text-xs text-slate-400 mt-2">✓ Goal automatically set based on your race</p>
            </div>
          ) : (
            <div>
              <label className="block text-sm font-medium mb-3 text-white">General Goal</label>
              {[
                { value: 'marathon', label: 'Marathon (42km)' },
                { value: 'half_marathon', label: 'Half Marathon (21km)' },
                { value: '10k', label: '10 Kilometres' },
                { value: '5k', label: '5 Kilometres' },
                { value: 'improve_fitness', label: 'Improve fitness' },
                { value: 'build_endurance', label: 'Build endurance' },
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
            <label className="block text-sm font-medium mb-3 text-white">Priority</label>
            {[
              { value: 'speed', label: 'Speed 🚀', desc: 'Improve pace' },
              { value: 'endurance', label: 'Endurance 💪', desc: 'Long distances' },
              { value: 'recovery', label: 'Recovery 😌', desc: 'Rest and injury prevention' },
              { value: 'balanced', label: 'Balanced ⚖️', desc: 'Perfect balance' },
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
              Back
            </Button>
            <Button 
              onClick={() => setStep(3)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
              Next
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  // PASO 3: Disponibilidad
  if (step === 3) {
    const daysOfWeek = [
      { value: 'monday', label: 'Monday' },
      { value: 'tuesday', label: 'Tuesday' },
      { value: 'wednesday', label: 'Wednesday' },
      { value: 'thursday', label: 'Thursday' },
      { value: 'friday', label: 'Friday' },
      { value: 'saturday', label: 'Saturday' },
      { value: 'sunday', label: 'Sunday' },
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
        alert('Maximum 2 days for long run');
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
          <CardTitle className="text-white">3. Your Availability</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-2 text-white">Training days per week</label>
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
              Long run days <span className="text-xs text-slate-400">(choose 1-2 days)</span>
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
              <p className="text-xs text-red-400 mt-2">⚠️ Select at least 1 day</p>
            )}
            {selectedDays.length > 0 && (
              <p className="text-xs text-blue-400 mt-2">✓ Selected: {selectedDays.length} day(s)</p>
            )}
          </div>

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(2)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Back
            </Button>
            <Button 
              onClick={() => setStep(4)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
              Next
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
          <CardTitle className="text-white">4. Additional Training</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3 text-white">Strength training</label>
            <div className="flex gap-4">
              {['No', 'Yes'].map((option, idx) => (
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
              <label className="block text-sm font-medium mb-2 text-white">Strength training type</label>
              <div className="space-y-2">
                {[
                  { value: 'with_equipment', label: '🏋️ With equipment', desc: 'Weights, kettlebells, bands...' },
                  { value: 'bodyweight', label: '💪 Bodyweight', desc: 'Squats, push-ups, no equipment...' },
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
              {['No', 'Yes'].map((option, idx) => (
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
                Select complementary sports <span className="text-xs text-slate-400">(choose 1 or more)</span>
              </label>
              <div className="grid grid-cols-2 gap-2">
                {[
                  { value: 'swimming', label: '🏊 Swimming' },
                  { value: 'cycling', label: '🚴 Cycling' },
                  { value: 'rowing', label: '🚣 Rowing' },
                  { value: 'triathlon', label: '🏃‍♂️ Triathlon' },
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
                ℹ️ Selecting Triathlon disables Swimming and Cycling (already included)
              </div>
              {formData.cross_training_types.length === 0 && (
                <p className="text-xs text-orange-400 mt-2">⚠️ Select at least 1 sport</p>
              )}
              {formData.cross_training_types.length > 0 && (
                <p className="text-xs text-green-400 mt-2">✓ Selected: {formData.cross_training_types.length} sport(s)</p>
              )}
            </div>
          )}

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(3)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Back
            </Button>
            <Button 
              onClick={() => setStep(5)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
              Next
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
          <CardTitle className="text-white">5. Training Method</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-3 text-white">How to plan?</label>
            <div className="space-y-2">
              {[
                { value: 'automatic', label: '🤖 Automatic', desc: 'The coach picks the best method' },
                { value: 'pace_based', label: '⏱️ By Pace (min/km)', desc: 'Speed-based control' },
                { value: 'heart_rate_based', label: '❤️ By Heart Rate', desc: 'HR zone-based control' },
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
            <label className="block text-sm font-medium mb-3 text-white">Recovery Focus</label>
            <div className="space-y-2">
              {[
                { value: 'minimal', label: 'Minimal' },
                { value: 'moderate', label: 'Moderate' },
                { value: 'high', label: 'High' },
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
            <label className="block text-sm font-medium mb-2 text-white">Special considerations (injuries, etc.)</label>
            <textarea
              placeholder="e.g. I have ankle tendinitis..."
              value={formData.injury_considerations || ''}
              onChange={(e) => setFormData({ ...formData, injury_considerations: e.target.value })}
              className="w-full px-3 py-2 bg-slate-600 border border-slate-500 rounded text-white placeholder-slate-400 h-16"
            />
          </div>

          <div className="flex gap-3 mt-6">
            <Button onClick={() => setStep(4)} className="flex-1 bg-slate-700 hover:bg-slate-600">
              Back
            </Button>
            <Button 
              onClick={() => setStep(6)} 
              disabled={!isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-blue-600 hover:bg-blue-700' : 'bg-slate-500 cursor-not-allowed opacity-50'}`}
            >
              Next
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
          <CardTitle className="text-white">6. Plan Duration 📅</CardTitle>
          <p className="text-sm text-slate-400 mt-2">
            {formData.has_target_race 
              ? 'Duration calculated automatically based on your race'
              : 'Choose the ideal duration for your goal'}
          </p>
        </CardHeader>
        <CardContent className="space-y-4">
          {formData.has_target_race && formData.plan_duration_weeks ? (
            <div className="p-4 bg-green-900/20 border border-green-600 rounded-lg space-y-3">
              <div className="flex items-center gap-2">
                <span className="text-2xl font-bold text-green-400">{formData.plan_duration_weeks}</span>
                <span className="text-lg text-green-300">weeks</span>
              </div>
              {formData.duration_recommendation && (
                <div className="text-sm text-green-300">
                  💡 {formData.duration_recommendation}
                </div>
              )}
              <p className="text-xs text-slate-400">✓ Automatic duration for your target race</p>
            </div>
          ) : (
            <div className="space-y-3">
              {durationOpts.loading && (
                <div className="text-sm text-blue-300">⏳ Loading duration options...</div>
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
                          <div className="font-bold text-white">{option.weeks} weeks</div>
                          <div className="text-sm text-slate-300">{option.label}</div>
                          <div className="text-xs text-slate-400 mt-1">{option.description}</div>
                        </div>
                        {option.recommended && (
                          <span className="bg-green-600 text-white text-xs px-2 py-1 rounded">
                            ⭐ Recommended
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
              Back
            </Button>
            <Button
              onClick={handleCreatePlan}
              disabled={isLoading || !isStepValid()}
              className={`flex-1 ${isStepValid() ? 'bg-green-600 hover:bg-green-700' : 'bg-gray-600 cursor-not-allowed opacity-50'}`}
            >
              {isLoading ? 'Creating plan...' : '✨ Create Training Plan'}
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return null;
}
