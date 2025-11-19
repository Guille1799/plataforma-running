/**
 * types.ts - TypeScript types matching backend schemas
 */

// ============================================================================
// AUTH & USER
// ============================================================================

export interface User {
  id: number;
  email: string;
  running_level?: string;
  max_heart_rate?: number;
  coaching_style?: string;
  height_cm?: number;
  weight_kg?: number;
  hr_zones?: HRZone[];
  power_zones?: PowerZone[];
  goals?: Goal[];
  injuries?: Injury[];
  preferences?: AthletePreferences;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// ============================================================================
// ATHLETE PROFILE
// ============================================================================

export type RunningLevel = 'beginner' | 'intermediate' | 'advanced' | 'elite';
export type CoachingStyle = 'motivational' | 'analytical' | 'balanced';
export type GoalType = 'race' | 'distance' | 'time' | 'consistency';

export interface Goal {
  type: GoalType;
  target: string;
  deadline?: string;
  description?: string;
}

export interface Injury {
  type: string;
  severity: 'mild' | 'moderate' | 'severe';
  date: string;
  status: 'active' | 'recovering' | 'healed';
  notes?: string;
}

export interface AthletePreferences {
  preferred_training_days?: string[];
  available_hours_per_week?: number;
  preferred_workout_time?: 'morning' | 'afternoon' | 'evening';
  equipment?: string[];
}

export interface AthleteProfile {
  running_level?: RunningLevel;
  max_heart_rate?: number;
  coaching_style?: CoachingStyle;
  goals?: Goal[];
  injuries?: Injury[];
  preferences?: AthletePreferences;
}

// ============================================================================
// WORKOUTS
// ============================================================================

export interface Workout {
  id: number;
  user_id: number;
  garmin_activity_id?: string;
  sport_type: string;
  start_time: string;
  duration_seconds: number;
  distance_meters: number;
  avg_heart_rate?: number;
  max_heart_rate?: number;
  avg_pace?: number;
  max_speed?: number;
  calories?: number;
  elevation_gain?: number;
  avg_cadence?: number;
  max_cadence?: number;
  avg_stance_time?: number;
  avg_vertical_oscillation?: number;
  avg_leg_spring_stiffness?: number;
  left_right_balance?: number;
  file_name?: string;
  created_at: string;
  // Computed properties (helpers)
  distance_km?: number;       // distance_meters / 1000
  avg_pace_min_km?: number;   // avg_pace converted to min/km
  date?: string;              // start_time as date
}

export interface WorkoutListResponse {
  workouts: Workout[];
  total: number;
}

export interface SyncResponse {
  synced_count: number;
  workout_ids: number[];
}

// ============================================================================
// HEALTH METRICS
// ============================================================================

export interface HealthMetric {
  id: number;
  user_id: number;
  date: string;
  
  // Recovery Metrics
  hrv_ms?: number;
  resting_hr_bpm?: number;
  hrv_baseline_ms?: number;
  resting_hr_baseline_bpm?: number;
  
  // Sleep Metrics
  sleep_duration_minutes?: number;
  sleep_score?: number;
  deep_sleep_minutes?: number;
  rem_sleep_minutes?: number;
  light_sleep_minutes?: number;
  awake_minutes?: number;
  
  // Readiness Metrics
  body_battery?: number;
  readiness_score?: number;
  stress_level?: number;
  recovery_score?: number;
  
  // Activity Metrics
  steps?: number;
  calories_burned?: number;
  active_calories?: number;
  intensity_minutes?: number;
  
  // Respiratory Metrics
  respiration_rate?: number;
  spo2_percentage?: number;
  
  // Subjective Metrics
  energy_level?: number;  // 1-5
  soreness_level?: number;  // 1-5
  mood?: number;  // 1-5
  motivation?: number;  // 1-5
  notes?: string;
  
  // Metadata
  source?: string;
  data_quality?: string;
  created_at?: string;
}

// ============================================================================
// COACH AI
// ============================================================================

export interface HRZone {
  zone: number;
  min_hr?: number;
  max_hr?: number;
  min?: number;
  max?: number;
  name?: string;
  percentage_max?: string;
  training_effect?: string;
}

export interface PowerZone {
  zone: number;
  min?: number;
  max?: number;
  name?: string;
}

export interface HRZonesResponse {
  max_heart_rate: number;
  zones: HRZone[];
}

export interface WorkoutAnalysisRequest {
  focus_areas?: string[];
}

export interface WorkoutAnalysisResponse {
  analysis: string;
  detected_zone: string;
  recommendations: string[];
  tokens_used: number;
}

export interface TrainingGoal {
  race_name: string;
  race_date: string;
  distance_km: number;
  target_time_minutes: number;
  target_pace_min_per_km?: number;
}

export interface WeeklyPlanRequest {
  general_goal: 'marathon' | 'half_marathon' | '10k' | '5k' | 'improve_fitness' | 'build_endurance';
  priority: 'speed' | 'endurance' | 'recovery' | 'balanced';
  has_target_race: boolean;
  target_race?: TrainingGoal;
  training_days_per_week: number;
  preferred_long_run_day: 'monday' | 'tuesday' | 'wednesday' | 'thursday' | 'friday' | 'saturday' | 'sunday';
  plan_duration_weeks: number;
  include_strength_training: boolean;
  strength_location: 'gym' | 'home' | 'none';
  training_method: 'pace_based' | 'heart_rate_based' | 'automatic';
  include_cross_training: boolean;
  cross_training_types: string[];
  recovery_focus: 'minimal' | 'moderate' | 'high';
  injury_considerations?: string;
}

export interface TrainingDay {
  day: string;
  type: string;
  description: string;
  distance_km?: number;
  pace_min_per_km?: number;
  heart_rate_zone?: number;
  duration_minutes?: number;
}

export interface TrainingWeek {
  week_number: number;
  days: TrainingDay[];
  total_km: number;
}

export interface TrainingPlan {
  id: string;
  name: string;
  start_date: string;
  end_date: string;
  weeks: TrainingWeek[];
  general_goal: string;
  priority: string;
  training_days_per_week: number;
  plan_duration_weeks: number;
  total_volume_km: number;
  max_weekly_distance_km: number;
}

export interface WorkoutPlan {
  day: string;
  type: string;
  duration: string;
  description: string;
  intensity: string;
}

export interface WeeklyPlanResponse {
  plan: TrainingPlan;
  workouts?: WorkoutPlan[];
  weekly_volume?: number;
  tokens_used?: number;
}

export interface FormAnalysisRequest {
  focus_areas?: string[];
}

export interface FormAnalysisResponse {
  analysis: string;
  efficiency_rating: string;
  recommendations: string[];
  tokens_used: number;
}

export interface ChatRequest {
  message: string;
  include_workout_context?: boolean;
}

export interface ChatMessage {
  id: number;
  user_id: number;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

export interface ChatMessageOut {
  id: number;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ChatResponse {
  user_message: ChatMessageOut;
  assistant_message: ChatMessageOut;
  conversation_length: number;
  tokens_used: number;
}

export interface ChatHistoryResponse {
  messages: ChatMessage[];
  total: number;
}

export interface DeepAnalysisResponse {
  analysis: string;
  workout_id: number;
  similar_workouts_count: number;
  tokens_used: number;
  analyzed_at: string;
}

// ============================================================================
// GARMIN
// ============================================================================

export interface GarminConnectRequest {
  email: string;
  password: string;
}

export interface GarminConnectResponse {
  message: string;
  credentials_encrypted: boolean;
}

// ============================================================================
// TRAINING PLAN DURATION
// ============================================================================

export interface DurationCalculationResult {
  weeks: number;
  taper_start_date: string;
  recommendation: string;
  feasible: boolean;
}

export interface DurationOption {
  weeks: number;
  label: string;
  description: string;
  recommended: boolean;
}

// ============================================================================
// API ERROR
// ============================================================================

export interface APIError {
  detail: string;
}
