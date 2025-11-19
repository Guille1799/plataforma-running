/**
 * api-client.ts - Centralized API client for backend communication
 */
import axios, { AxiosInstance, AxiosError } from 'axios';
import { enrichWorkouts } from './formatters';
import type {
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User,
  Workout,
  WorkoutListResponse,
  SyncResponse,
  GarminConnectRequest,
  GarminConnectResponse,
  AthleteProfile,
  Goal,
  HRZonesResponse,
  WorkoutAnalysisRequest,
  WorkoutAnalysisResponse,
  WeeklyPlanRequest,
  WeeklyPlanResponse,
  FormAnalysisRequest,
  FormAnalysisResponse,
  ChatRequest,
  ChatResponse,
  ChatHistoryResponse,
  APIError,
  DurationCalculationResult,
  DurationOption,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';

class APIClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor to add auth token
    this.client.interceptors.request.use(
      (config) => {
        const token = this.getToken();
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError<APIError>) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear token and redirect to login
          this.clearToken();
          if (typeof window !== 'undefined') {
            window.location.href = '/login';
          }
        }
        return Promise.reject(error);
      }
    );
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  getToken(): string | null {
    // Always try to load from localStorage on client side if this.token is null
    if (this.token === null && typeof window !== 'undefined') {
      const savedToken = localStorage.getItem('auth_token');
      if (savedToken) {
        this.token = savedToken;
      }
    }
    return this.token;
  }

  // ============================================================================
  // AUTH
  // ============================================================================

  async login(credentials: LoginRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/v1/auth/login', credentials);
    this.setToken(response.data.access_token);
    return response.data;
  }

  async register(data: RegisterRequest): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/api/v1/auth/register', data);
    this.setToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/api/v1/auth/me');
    return response.data;
  }

  logout() {
    this.clearToken();
  }

  // ============================================================================
  // WORKOUTS
  // ============================================================================

  async getWorkouts(skip: number = 0, limit: number = 50): Promise<WorkoutListResponse> {
    const response = await this.client.get<any>('/api/v1/workouts', {
      params: { skip, limit },
    });
    
    // Backend puede retornar array directo o { workouts: [...], total: ... }
    const workoutsArray = Array.isArray(response.data) ? response.data : (response.data.workouts || []);
    const total = response.data.total || workoutsArray.length;
    
    // Enrich workouts with computed properties for dashboard compatibility
    const enrichedWorkouts = enrichWorkouts(workoutsArray);
    
    // Debug logging
    if (typeof window !== 'undefined' && enrichedWorkouts.length > 0) {
      console.log('🔍 API Client - First workout (raw):', workoutsArray[0]);
      console.log('✅ API Client - First workout (enriched):', enrichedWorkouts[0]);
    }
    
    return { workouts: enrichedWorkouts, total };
  }

  async createWorkout(data: any): Promise<Workout> {
    const response = await this.client.post<Workout>('/api/v1/workouts/create', data);
    return response.data;
  }

  async getWorkout(id: number): Promise<Workout> {
    const response = await this.client.get<Workout>(`/api/v1/workouts/${id}`);
    return response.data;
  }

  async deleteWorkout(id: number): Promise<{ message: string }> {
    const response = await this.client.delete(`/api/v1/workouts/${id}`);
    return response.data;
  }

  // ============================================================================
  // GARMIN
  // ============================================================================

  async connectGarmin(credentials: GarminConnectRequest): Promise<GarminConnectResponse> {
    const response = await this.client.post<GarminConnectResponse>(
      '/api/v1/garmin/connect',
      credentials
    );
    return response.data;
  }

  async syncGarmin(days: number = 30): Promise<SyncResponse> {
    // Backend automatically detects first sync vs subsequent syncs
    // Send GarminSyncRequest with null values to use defaults
    const response = await this.client.post<SyncResponse>('/api/v1/garmin/sync', {
      start_date: null,
      end_date: null
    });
    return response.data;
  }

  // ============================================================================
  // PROFILE
  // ============================================================================

  async getProfile(): Promise<AthleteProfile> {
    const response = await this.client.get<AthleteProfile>('/api/v1/profile/');
    return response.data;
  }

  async updateProfile(profile: Partial<AthleteProfile>): Promise<AthleteProfile> {
    const response = await this.client.patch<AthleteProfile>('/api/v1/profile/', profile);
    return response.data;
  }

  async getGoals(): Promise<Goal[]> {
    const response = await this.client.get<Goal[]>('/api/v1/profile/goals');
    return response.data;
  }

  async createGoal(goal: Omit<Goal, 'id'>): Promise<Goal> {
    const response = await this.client.post<Goal>('/api/v1/profile/goals', goal);
    return response.data;
  }

  async updateGoal(index: number, goal: Goal): Promise<Goal> {
    const response = await this.client.put<Goal>(`/api/v1/profile/goals/${index}`, goal);
    return response.data;
  }

  async deleteGoal(index: number): Promise<{ message: string }> {
    const response = await this.client.delete(`/api/v1/profile/goals/${index}`);
    return response.data;
  }

  // ============================================================================
  // COACH AI
  // ============================================================================

  async getHRZones(): Promise<HRZonesResponse> {
    const response = await this.client.get<HRZonesResponse>('/api/v1/coach/hr-zones');
    return response.data;
  }

  async analyzeWorkout(
    workoutId: number,
    request?: WorkoutAnalysisRequest
  ): Promise<WorkoutAnalysisResponse> {
    const response = await this.client.post<WorkoutAnalysisResponse>(
      `/api/v1/coach/analyze/${workoutId}`,
      request || {}
    );
    return response.data;
  }

  async generateWeeklyPlan(request?: WeeklyPlanRequest): Promise<WeeklyPlanResponse> {
    const response = await this.client.post<WeeklyPlanResponse>(
      '/api/v1/coach/plan',
      request || {}
    );
    return response.data;
  }

  async analyzeForm(workoutId: number, request?: FormAnalysisRequest): Promise<FormAnalysisResponse> {
    const response = await this.client.post<FormAnalysisResponse>(
      `/api/v1/coach/analyze-form/${workoutId}`,
      request || {}
    );
    return response.data;
  }

  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/api/v1/coach/chat', request);
    return response.data;
  }

  async getChatHistory(limit: number = 50): Promise<ChatHistoryResponse> {
    const response = await this.client.get<ChatHistoryResponse>('/api/v1/coach/chat/history', {
      params: { limit },
    });
    return response.data;
  }

  async clearChatHistory(): Promise<{ message: string }> {
    const response = await this.client.delete('/api/v1/coach/chat/history');
    return response.data;
  }

  async analyzeWorkoutDeep(workoutId: number): Promise<FormAnalysisResponse> {
    const response = await this.client.post<FormAnalysisResponse>(
      `/api/v1/coach/analyze-deep/${workoutId}`
    );
    return response.data;
  }

  // ============================================================================
  // HEALTH METRICS
  // ============================================================================

  async getHealthToday(): Promise<any> {
    const response = await this.client.get('/api/v1/health/today');
    return response.data;
  }

  async getHealthHistory(days: number = 30): Promise<any[]> {
    const response = await this.client.get('/api/v1/health/history', {
      params: { days },
    });
    return response.data;
  }

  async createManualHealthMetric(data: {
    date: string;
    energy_level?: number;
    soreness_level?: number;
    mood?: number;
    motivation?: number;
    sleep_duration_minutes?: number;
    resting_hr_bpm?: number;
    notes?: string;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/health/manual', data);
    return response.data;
  }

  async getReadinessScore(): Promise<any> {
    const response = await this.client.get('/api/v1/health/readiness');
    return response.data;
  }

  async getWorkoutRecommendation(): Promise<any> {
    const response = await this.client.get('/api/v1/health/recommendation');
    return response.data;
  }

  async syncGarminHealth(days: number = 7): Promise<any> {
    const response = await this.client.post('/api/v1/health/sync/garmin', null, {
      params: { days },
    });
    return response.data;
  }

  async connectGoogleFit(): Promise<{ auth_url: string; state: string }> {
    const response = await this.client.get('/api/v1/health/connect/google-fit');
    return response.data;
  }

  async googleFitCallback(code: string, state: string): Promise<any> {
    const response = await this.client.post('/api/v1/health/callback/google-fit', null, {
      params: { code, state },
    });
    return response.data;
  }

  async syncGoogleFitHealth(days: number = 7): Promise<any> {
    const response = await this.client.post('/api/v1/health/sync/google-fit', null, {
      params: { days },
    });
    return response.data;
  }

  async importAppleHealth(file: File, maxDays: number = 30): Promise<any> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await this.client.post('/api/v1/health/import/apple-health', formData, {
      params: { max_days: maxDays },
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  async getHealthTrends(days: number = 30): Promise<any> {
    const response = await this.client.get('/api/v1/health/insights/trends', {
      params: { days },
    });
    return response.data;
  }

  // ============================================================================
  // ONBOARDING
  // ============================================================================

  async getOnboardingStatus(): Promise<any> {
    const response = await this.client.get('/api/v1/onboarding/status');
    return response.data;
  }

  async completeOnboarding(data: {
    primary_device: string;
    use_case: string;
    coach_style_preference?: string;
    language?: string;
    enable_notifications?: boolean;
    integration_sources?: string[];
  }): Promise<any> {
    const response = await this.client.post('/api/v1/onboarding/complete', data);
    return response.data;
  }

  // ============================================================================
  // COACH (PERSONALIZATION)
  // ============================================================================

  async getPersonalizedRecommendation(): Promise<any> {
    const response = await this.client.get('/api/v1/coach/personalized-recommendation');
    return response.data;
  }

  // ============================================================================
  // DEVICE INTEGRATIONS
  // ============================================================================

  /**
   * Get all device integrations for current user
   */
  async getDeviceIntegrations(): Promise<any> {
    const response = await this.client.get('/api/v1/profile/integrations');
    return response.data;
  }

  /**
   * Add a new device integration
   */
  async addDeviceIntegration(data: {
    device_type: string;
    device_name: string;
    sync_interval_hours?: number;
    auto_sync_enabled?: boolean;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/profile/integrations', data);
    return response.data;
  }

  /**
   * Update device integration settings
   */
  async updateDeviceIntegration(
    deviceId: string,
    data: {
      device_name?: string;
      sync_interval_hours?: number;
      auto_sync_enabled?: boolean;
    }
  ): Promise<any> {
    const response = await this.client.put(`/api/v1/profile/integrations/${deviceId}`, data);
    return response.data;
  }

  /**
   * Remove a device integration
   */
  async removeDeviceIntegration(deviceId: string): Promise<void> {
    await this.client.delete(`/api/v1/profile/integrations/${deviceId}`);
  }

  /**
   * Get sync status for a specific device
   */
  async getDeviceSyncStatus(deviceId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/profile/integrations/${deviceId}/sync-status`);
    return response.data;
  }

  /**
   * Set a device as primary for personalization
   */
  async setPrimaryDevice(deviceId: string): Promise<any> {
    const response = await this.client.post(`/api/v1/profile/integrations/${deviceId}/set-primary`);
    return response.data;
  }

  /**
   * Trigger manual sync for all devices
   */
  async syncAllDevices(): Promise<any> {
    const response = await this.client.post('/api/v1/profile/integrations/sync-all');
    return response.data;
  }

  // ============================================================================
  // TRAINING PLANS
  // ============================================================================

  /**
   * Generate a training plan with AI
   */
  async generateTrainingPlan(data: {
    goal_type: string;
    goal_distance: number;
    goal_time?: string | null;
    race_date: string;
    current_weekly_distance: number;
    available_training_days: number;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/training-plans/generate', data);
    return response.data;
  }

  /**
   * Get all user training plans
   */
  async getTrainingPlans(): Promise<any[]> {
    const response = await this.client.get('/api/v1/training-plans/');
    return response.data;
  }

  /**
   * Delete a training plan
   */
  async deleteTrainingPlan(planId: number): Promise<void> {
    await this.client.delete(`/api/v1/training-plans/${planId}`);
  }

  // ============================================================================
  // PREDICTIONS
  // ============================================================================

  /**
   * Predict race times based on current performance
   */
  async predictRaceTimes(data: {
    distance: number;
    time_seconds: number;
    age?: number;
    gender?: string;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/predictions/race-times', data);
    return response.data;
  }

  /**
   * Get VDOT score
   */
  async getVDOT(data: {
    distance: number;
    time_seconds: number;
  }): Promise<any> {
    const response = await this.client.post('/api/v1/predictions/vdot', data);
    return response.data;
  }

  /**
   * Get training paces based on VDOT
   */
  async getTrainingPaces(vdot: number): Promise<any> {
    const response = await this.client.get(`/api/v1/predictions/training-paces/${vdot}`);
    return response.data;
  }

  // ============================================================================
  // STRAVA INTEGRATION
  // ============================================================================

  /**
   * Initialize Strava OAuth flow
   */
  async initStravaAuth(): Promise<{ authorization_url: string }> {
    const response = await this.client.get('/api/v1/integrations/strava/auth');
    return response.data;
  }

  /**
   * Disconnect Strava
   */
  async disconnectStrava(): Promise<void> {
    await this.client.post('/api/v1/integrations/strava/disconnect');
  }

  // ============================================================================
  // TRAINING PLAN DURATION
  // ============================================================================

  async calculatePlanDurationWithRace(
    targetRaceDate: string,
    goalType: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance'
  ): Promise<DurationCalculationResult> {
    const response = await this.client.post<DurationCalculationResult>(
      '/api/v1/training-plans/duration/with-target-race',
      {
        target_race_date: targetRaceDate,
        goal_type: goalType,
      }
    );
    return response.data;
  }

  async getPlanDurationOptions(
    goalType: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance'
  ): Promise<DurationOption[]> {
    const response = await this.client.get<{ duration_options: DurationOption[] }>(
      `/api/v1/training-plans/duration-options/${goalType}`
    );
    return response.data.duration_options || [];
  }

  // ============================================================================
  // EVENTS & RACES
  // ============================================================================

  async searchRaces(
    query?: string,
    location?: string,
    dateFrom?: string,
    dateTo?: string,
    minDistance?: number,
    maxDistance?: number,
    limit: number = 20
  ): Promise<any> {
    const response = await this.client.get('/api/v1/events/races/search', {
      params: {
        q: query,
        location,
        date_from: dateFrom,
        date_to: dateTo,
        min_distance: minDistance,
        max_distance: maxDistance,
        limit,
      },
    });
    return response.data;
  }

  async getUpcomingRaces(weeks: number = 12, limit: number = 10): Promise<any> {
    const response = await this.client.get('/api/v1/events/races/upcoming', {
      params: { weeks, limit },
    });
    return response.data;
  }

  async getRaceById(raceId: string): Promise<any> {
    const response = await this.client.get(`/api/v1/events/races/${raceId}`);
    return response.data;
  }

  async getRacesByDistance(distanceKm: number, tolerance: number = 2.0): Promise<any> {
    const response = await this.client.get(`/api/v1/events/races/by-distance/${distanceKm}`, {
      params: { tolerance },
    });
    return response.data;
  }
}

// Export singleton instance
export const apiClient = new APIClient();




