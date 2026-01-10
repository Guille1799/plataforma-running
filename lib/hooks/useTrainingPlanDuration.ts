/**
 * useTrainingPlanDuration.ts - Hook for training plan duration calculation
 */
import { useState, useCallback } from 'react';
import { apiClient } from '@/lib/api-client';
import type { DurationCalculationResult, DurationOption } from '@/lib/types';

interface UseTrainingPlanDurationState {
  loading: boolean;
  error: string | null;
  data: DurationCalculationResult | null;
}

interface UseDurationOptionsState {
  loading: boolean;
  error: string | null;
  data: DurationOption[] | null;
}

/**
 * Hook to calculate training plan duration with race date
 */
export function useCalculateDurationWithRace() {
  const [state, setState] = useState<UseTrainingPlanDurationState>({
    loading: false,
    error: null,
    data: null,
  });

  const calculate = async (
    targetRaceDate: string,
    goalType: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance'
  ): Promise<DurationCalculationResult | null> => {
    setState({ loading: true, error: null, data: null });

    try {
      const result = await apiClient.calculatePlanDurationWithRace(targetRaceDate, goalType);
      setState({ loading: false, error: null, data: result });
      return result;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err.message || 'Error calculating duration';
      setState({ loading: false, error: errorMessage, data: null });
      console.error('❌ Error calculating plan duration:', err);
      return null;
    }
  };

  return { ...state, calculate };
}

/**
 * Hook to get available duration options for a goal type
 */
export function useDurationOptions() {
  const [state, setState] = useState<UseDurationOptionsState>({
    loading: false,
    error: null,
    data: null,
  });

  const getDurationOptions = useCallback(async (
    goalType: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance'
  ): Promise<DurationOption[] | null> => {
    // Prevent infinite loops - check if we already have data
    if (state.data && state.data.length > 0) {
      return state.data;
    }

    setState({ loading: true, error: null, data: null });

    try {
      const result = await apiClient.getPlanDurationOptions(goalType);
      setState({ loading: false, error: null, data: result });
      return result;
    } catch (err: any) {
      const errorMessage = err?.response?.data?.detail || err.message || 'Error fetching duration options';
      setState({ loading: false, error: errorMessage, data: null });
      console.error('❌ Error fetching duration options:', err);
      return null;
    }
  }, [state.data]);

  return { ...state, getDurationOptions };
}
