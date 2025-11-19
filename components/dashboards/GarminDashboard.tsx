'use client';

/**
 * GarminDashboard.tsx - Dashboard optimizado para Garmin
 * Enfoque: Body Battery, HRV, Readiness Score, Training Load
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
import { Activity, TrendingUp, Calendar, Zap, Heart, BarChart3, Lightbulb } from 'lucide-react';
import { formatPace, formatDistance } from '@/lib/formatters';

export function GarminDashboard() {
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
  const thisWeekWorkouts = workouts.filter((w) => {
    if (!w.date && !w.start_time) return false;
    const workoutDate = new Date(w.date || w.start_time);
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    return workoutDate >= weekAgo;
  }).length;

  const thisMonthDistance = workouts.reduce((sum, w) => {
    if (!w.date && !w.start_time) return sum;
    const workoutDate = new Date(w.date || w.start_time);
    const monthAgo = new Date();
    monthAgo.setDate(monthAgo.getDate() - 30);
    if (workoutDate >= monthAgo && w.distance_km) {
      return sum + w.distance_km;
    }
    return sum;
  }, 0);

  const avgPace = workouts.length
    ? workouts.reduce((sum, w) => sum + (w.avg_pace_min_km || 0), 0) / workouts.length
    : 0;

  // Garmin specific metrics
  const bodyBattery = healthData?.body_battery || 0;
  const hrv = healthData?.hrv_ms || 0;
  const readinessScore = healthData?.readiness_score || 0;
  const stressLevel = healthData?.stress_level || 0;

  const getBatteryColor = (battery: number) => {
    if (battery >= 70) return 'text-green-400 bg-green-500/10';
    if (battery >= 50) return 'text-yellow-400 bg-yellow-500/10';
    return 'text-red-400 bg-red-500/10';
  };

  const getHRVColor = (hrv: number) => {
    if (hrv >= 60) return 'text-green-400';
    if (hrv >= 40) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Training Status</h1>
          <p className="text-slate-400">Garmin Advanced Metrics</p>
        </div>

        {/* Readiness Badge */}
        <ReadinessBadge />

        {/* Garmin Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Body Battery */}
          <Card className={`border-l-4 border-l-blue-500 bg-slate-800/50 backdrop-blur ${getBatteryColor(bodyBattery)}`}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Body Battery
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{bodyBattery}%</div>
              <p className="text-xs text-slate-500 mt-1">
                {bodyBattery >= 70 ? 'Excellent' : bodyBattery >= 50 ? 'Good' : 'Low'}
              </p>
            </CardContent>
          </Card>

          {/* HRV */}
          <Card className={`border-l-4 border-l-purple-500 bg-slate-800/50 backdrop-blur`}>
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Heart className="h-4 w-4" />
                HRV
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className={`text-3xl font-bold ${getHRVColor(hrv)}`}>{hrv.toFixed(1)}ms</div>
              <p className="text-xs text-slate-500 mt-1">Heart Rate Variability</p>
            </CardContent>
          </Card>

          {/* Readiness */}
          <Card className="border-l-4 border-l-cyan-500 bg-slate-800/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Readiness
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-cyan-400">{readinessScore}</div>
              <p className="text-xs text-slate-500 mt-1">/100 Score</p>
            </CardContent>
          </Card>

          {/* Stress Level */}
          <Card className="border-l-4 border-l-red-500 bg-slate-800/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <BarChart3 className="h-4 w-4" />
                Stress
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-400">{stressLevel}</div>
              <p className="text-xs text-slate-500 mt-1">Stress Level</p>
            </CardContent>
          </Card>
        </div>

        {/* Training Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Calendar className="h-4 w-4" />
                This Week
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">{thisWeekWorkouts}</div>
              <p className="text-xs text-slate-500 mt-1">workouts</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                This Month
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">{formatDistance(thisMonthDistance)}</div>
              <p className="text-xs text-slate-500 mt-1">total distance</p>
            </CardContent>
          </Card>

          <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Activity className="h-4 w-4" />
                Avg Pace
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-400">{formatPace(avgPace)}</div>
              <p className="text-xs text-slate-500 mt-1">min/km</p>
            </CardContent>
          </Card>
        </div>

        {/* AI Coach Tips */}
        {personalizationData && personalizationData.device_customization && (
          <Card className="bg-gradient-to-r from-blue-900/30 to-purple-900/30 border-blue-600/30 backdrop-blur">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-blue-300">
                <Lightbulb className="h-5 w-5" />
                {personalizationData.device_customization.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-300">{personalizationData.device_customization.focus}</p>
              <div className="space-y-2">
                {personalizationData.device_customization.tips.map((tip: string, idx: number) => (
                  <div key={idx} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-blue-400 font-semibold">•</span>
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

