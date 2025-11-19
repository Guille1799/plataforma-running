'use client';

/**
 * XiaomiDashboard.tsx - Dashboard optimizado para Xiaomi/Amazfit
 * Enfoque: Simple, Accessible, Activity Rings, Sleep Quality
 */
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { ReadinessBadge } from '@/components/ReadinessBadge';
import { PerformanceAnalytics } from '@/components/PerformanceAnalytics';
import { WeeklyGoalsTracker } from '@/components/WeeklyGoalsTracker';
import { PersonalizedRecommendations } from '@/components/PersonalizedRecommendations';
import { InjuryPrevention } from '@/components/InjuryPrevention';
import { ExportAnalytics } from '@/components/ExportAnalytics';
import { Activity, Moon, Heart, Flame, TrendingUp, Calendar, Lightbulb, BarChart3 } from 'lucide-react';
import { formatDistance } from '@/lib/formatters';

export function XiaomiDashboard() {
  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 'recent'],
    queryFn: () => apiClient.getWorkouts(0, 30),
    retry: 1,
  });

  const { data: healthData } = useQuery({
    queryKey: ['health', 'today'],
    queryFn: () => apiClient.getHealthToday?.(),
    retry: 1,
  });

  const { data: personalizationData } = useQuery({
    queryKey: ['coach', 'personalized'],
    queryFn: () => apiClient.getPersonalizedRecommendation?.(),
    retry: 1,
  });

  const workouts = workoutsData?.workouts || [];

  // Calculate stats
  const todayWorkouts = workouts.filter((w) => {
    if (!w.date && !w.start_time) return false;
    const workoutDate = new Date(w.date || w.start_time);
    const today = new Date();
    return workoutDate.toDateString() === today.toDateString();
  }).length;

  const thisWeekWorkouts = workouts.filter((w) => {
    if (!w.date && !w.start_time) return false;
    const workoutDate = new Date(w.date || w.start_time);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return workoutDate >= weekAgo;
  }).length;

  // Health metrics
  const heartRate = healthData?.resting_hr_bpm || 0;
  const sleepDuration = healthData?.sleep_duration_minutes || 0;
  const sleepScore = healthData?.sleep_score || 0;
  const steps = healthData?.steps || 0;
  const calories = healthData?.calories || 0;

  const sleepHours = sleepDuration / 60;
  const getSleepColor = (hours: number) => {
    if (hours >= 7) return 'text-green-400';
    if (hours >= 6) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">My Activity</h1>
          <p className="text-slate-400">Xiaomi / Amazfit Daily Overview</p>
        </div>

        {/* Readiness Badge */}
        <ReadinessBadge />

        {/* Daily Activity Ring */}
        <Card className="bg-gradient-to-r from-slate-800/50 to-slate-900/50 border-slate-700 backdrop-blur">
          <CardHeader>
            <CardTitle className="text-lg">Today's Activity</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {/* Steps */}
              <div className="text-center p-4 bg-slate-900/30 rounded-lg border border-slate-600">
                <Activity className="h-6 w-6 text-blue-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-blue-400">{(steps / 1000).toFixed(1)}k</div>
                <p className="text-xs text-slate-400 mt-1">Steps</p>
              </div>

              {/* Heart Rate */}
              <div className="text-center p-4 bg-slate-900/30 rounded-lg border border-slate-600">
                <Heart className="h-6 w-6 text-red-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-red-400">{heartRate}</div>
                <p className="text-xs text-slate-400 mt-1">Resting HR</p>
              </div>

              {/* Calories */}
              <div className="text-center p-4 bg-slate-900/30 rounded-lg border border-slate-600">
                <Flame className="h-6 w-6 text-orange-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-orange-400">{(calories / 100).toFixed(0)}00</div>
                <p className="text-xs text-slate-400 mt-1">Calories</p>
              </div>

              {/* Workouts Today */}
              <div className="text-center p-4 bg-slate-900/30 rounded-lg border border-slate-600">
                <Activity className="h-6 w-6 text-cyan-400 mx-auto mb-2" />
                <div className="text-2xl font-bold text-cyan-400">{todayWorkouts}</div>
                <p className="text-xs text-slate-400 mt-1">Workouts</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Sleep & Rest */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Sleep */}
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Moon className="h-4 w-4" />
                Last Night's Sleep
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getSleepColor(sleepHours)}`}>
                {sleepHours.toFixed(1)}h
              </div>
              <div className="flex items-center gap-2 mt-3">
                <div className="flex-1 h-2 bg-slate-600 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500"
                    style={{ width: `${Math.min((sleepHours / 9) * 100, 100)}%` }}
                  />
                </div>
                <span className="text-xs text-slate-400">Score: {sleepScore}/100</span>
              </div>
            </CardContent>
          </Card>

          {/* Weekly Summary */}
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                This Week
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">{thisWeekWorkouts}</div>
              <p className="text-xs text-slate-500 mt-1">completed workouts</p>
              <div className="flex gap-1 mt-3">
                {[7, 6, 5, 4, 3, 2, 1].map((day) => (
                  <div
                    key={day}
                    className={`h-8 w-full rounded ${
                      day <= thisWeekWorkouts
                        ? 'bg-gradient-to-t from-green-600 to-green-500'
                        : 'bg-slate-700'
                    }`}
                    title={`Day ${8 - day}`}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Activity */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
          <CardHeader>
            <CardTitle>Recent Workouts</CardTitle>
          </CardHeader>
          <CardContent>
            {workouts.slice(0, 5).length > 0 ? (
              <div className="space-y-3">
                {workouts.slice(0, 5).map((workout, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-slate-900/30 rounded-lg border border-slate-600"
                  >
                    <div className="flex-1">
                      <p className="font-semibold text-white capitalize">{workout.sport_type}</p>
                      <p className="text-xs text-slate-400">
                        {new Date(workout.start_time).toLocaleDateString()}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-blue-400">{formatDistance(workout.distance_km)}</p>
                      <p className="text-xs text-slate-400">
                        {Math.floor(workout.duration_seconds / 60)}m
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 text-center py-8">No workouts yet</p>
            )}
          </CardContent>
        </Card>

        {/* AI Coach Tips */}
        {personalizationData && personalizationData.device_customization && (
          <Card className="bg-gradient-to-r from-orange-900/30 to-pink-900/30 border-orange-600/30 backdrop-blur">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-300">
                <Lightbulb className="h-5 w-5" />
                {personalizationData.device_customization.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-300">{personalizationData.device_customization.focus}</p>
              <div className="space-y-2">
                {personalizationData.device_customization.tips.map((tip: string, idx: number) => (
                  <div key={idx} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-orange-400 font-semibold">•</span>
                    <span>{tip}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Performance Analytics Section */}
        <div className="pt-8 border-t border-slate-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-blue-400" />
            Performance Trends
          </h2>
          <PerformanceAnalytics />
        </div>

        {/* Weekly Goals Section */}
        <div className="pt-8 border-t border-slate-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Calendar className="h-6 w-6 text-purple-400" />
            This Week's Goals
          </h2>
          <WeeklyGoalsTracker />
        </div>

        {/* AI Recommendations Section */}
        <div className="pt-8 border-t border-slate-700">
          <PersonalizedRecommendations />
        </div>

        {/* Injury Prevention Section */}
        <div className="pt-8 border-t border-slate-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <Heart className="h-6 w-6 text-red-400" />
            Injury Prevention
          </h2>
          <InjuryPrevention />
        </div>

        {/* Export Analytics Section */}
        <div className="pt-8 border-t border-slate-700">
          <h2 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-green-400" />
            Export & Analytics
          </h2>
          <ExportAnalytics />
        </div>
      </div>
    </div>
  );
}

