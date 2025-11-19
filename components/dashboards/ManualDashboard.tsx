'use client';

/**
 * ManualDashboard.tsx - Dashboard optimizado para Manual Entry/General Users
 * Enfoque: Goals, Manual Logging, Trends, Personal Records
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
import { Trophy, Target, TrendingUp, Calendar, Plus, LogIn, Lightbulb, BarChart3, Heart } from 'lucide-react';
import { formatPace, formatDistance } from '@/lib/formatters';
import Link from 'next/link';

export function ManualDashboard() {
  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 'recent'],
    queryFn: () => apiClient.getWorkouts(0, 30),
    retry: 1,
  });

  const { data: personalizationData } = useQuery({
    queryKey: ['coach', 'personalized'],
    queryFn: () => apiClient.getPersonalizedRecommendation?.(),
    retry: 1,
  });

  const workouts = workoutsData?.workouts || [];

  // Calculate PRs and stats
  const fastestPace = workouts.length
    ? Math.min(...workouts.map(w => w.avg_pace_min_km || 999).filter(p => p < 999))
    : 0;

  const longestRun = workouts.length
    ? Math.max(...workouts.map(w => w.distance_km || 0))
    : 0;

  const totalDistance = workouts.reduce((sum, w) => sum + (w.distance_km || 0), 0);
  const totalWorkouts = workouts.length;
  const avgPace = workouts.length
    ? workouts.reduce((sum, w) => sum + (w.avg_pace_min_km || 0), 0) / workouts.length
    : 0;

  // Weekly breakdown
  const weeklyData = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    const dayWorkouts = workouts.filter((w) => {
      const wDate = new Date(w.date || w.start_time);
      return wDate.toDateString() === date.toDateString();
    });
    const distance = dayWorkouts.reduce((sum, w) => sum + (w.distance_km || 0), 0);
    return { date: date.toLocaleDateString('es-ES', { weekday: 'short' }), distance };
  });

  return (
    <div className="p-8">
      <div className="max-w-6xl mx-auto space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">Training Log</h1>
          <p className="text-slate-400">Personal Training Tracker</p>
        </div>

        {/* Readiness Badge */}
        <ReadinessBadge />

        {/* Quick Stats - Personal Records */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Workouts */}
          <Card className="border-l-4 border-l-blue-500 bg-slate-800/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <LogIn className="h-4 w-4" />
                Total Logged
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-blue-400">{totalWorkouts}</div>
              <p className="text-xs text-slate-500 mt-1">workouts</p>
            </CardContent>
          </Card>

          {/* Total Distance */}
          <Card className="border-l-4 border-l-green-500 bg-slate-800/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Total Distance
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-green-400">{formatDistance(totalDistance)}</div>
              <p className="text-xs text-slate-500 mt-1">all time</p>
            </CardContent>
          </Card>

          {/* Fastest Pace */}
          <Card className="border-l-4 border-l-purple-500 bg-slate-800/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Trophy className="h-4 w-4" />
                Fastest Pace
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-purple-400">{formatPace(fastestPace)}</div>
              <p className="text-xs text-slate-500 mt-1">Personal Record</p>
            </CardContent>
          </Card>

          {/* Longest Run */}
          <Card className="border-l-4 border-l-cyan-500 bg-slate-800/50 backdrop-blur">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
                <Target className="h-4 w-4" />
                Longest Run
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-cyan-400">{formatDistance(longestRun)}</div>
              <p className="text-xs text-slate-500 mt-1">max distance</p>
            </CardContent>
          </Card>
        </div>

        {/* Weekly Breakdown */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="h-5 w-5" />
              This Week Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-end gap-2 h-32">
              {weeklyData.map((day, idx) => (
                <div key={idx} className="flex-1 flex flex-col items-center gap-2">
                  <div
                    className="w-full bg-gradient-to-t from-blue-600 to-blue-500 rounded-t hover:from-blue-700 hover:to-blue-600 transition-colors"
                    style={{
                      height: `${Math.max((day.distance / Math.max(...weeklyData.map(d => d.distance), 1)) * 100, 5)}%`,
                    }}
                    title={`${day.distance.toFixed(1)} km`}
                  />
                  <span className="text-xs text-slate-400">{day.date}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Actions & Recent */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          {/* Quick Actions */}
          <Card className="bg-gradient-to-br from-blue-900/30 to-slate-800/50 border-blue-600/30 backdrop-blur">
            <CardHeader>
              <CardTitle className="text-lg">Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Link href="/upload">
                <button className="w-full px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium transition-colors flex items-center justify-center gap-2">
                  <Plus className="h-4 w-4" />
                  Log Workout
                </button>
              </Link>
              <Link href="/health">
                <button className="w-full px-4 py-2 rounded-lg border border-slate-600 hover:border-slate-500 text-white font-medium transition-colors">
                  Daily Check-In
                </button>
              </Link>
              <Link href="/coach">
                <button className="w-full px-4 py-2 rounded-lg border border-slate-600 hover:border-slate-500 text-white font-medium transition-colors">
                  Ask Coach
                </button>
              </Link>
            </CardContent>
          </Card>

          {/* Stats Summary - span 2 cols */}
          <div className="lg:col-span-2 grid grid-cols-2 gap-4">
            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-slate-400">Average Pace</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">{formatPace(avgPace)}</div>
              </CardContent>
            </Card>

            <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-medium text-slate-400">Workouts/Week</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-white">
                  {(totalWorkouts / Math.max((new Date().getTime() - new Date(workouts[workouts.length - 1]?.start_time || Date.now()).getTime()) / (1000 * 60 * 60 * 24 * 7), 1)).toFixed(1)}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>

        {/* Recent Workouts */}
        <Card className="bg-slate-800/50 border-slate-700 backdrop-blur">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
          </CardHeader>
          <CardContent>
            {workouts.slice(0, 8).length > 0 ? (
              <div className="space-y-2">
                {workouts.slice(0, 8).map((workout, idx) => (
                  <div
                    key={idx}
                    className="flex items-center justify-between p-3 bg-slate-900/30 rounded-lg border border-slate-600 hover:border-slate-500 transition-colors"
                  >
                    <div className="flex-1 min-w-0">
                      <p className="font-semibold text-white capitalize">{workout.sport_type}</p>
                      <p className="text-xs text-slate-400">
                        {new Date(workout.start_time).toLocaleDateString('es-ES')}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="font-semibold text-blue-400">{formatDistance(workout.distance_km)}</p>
                      <p className="text-xs text-slate-400">@ {formatPace(workout.avg_pace_min_km)}</p>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-slate-400 text-center py-8">No workouts logged yet. Start tracking!</p>
            )}
          </CardContent>
        </Card>

        {/* AI Coach Tips */}
        {personalizationData && personalizationData.device_customization && (
          <Card className="bg-gradient-to-r from-green-900/30 to-emerald-900/30 border-green-600/30 backdrop-blur">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-300">
                <Lightbulb className="h-5 w-5" />
                {personalizationData.device_customization.title}
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <p className="text-sm text-slate-300">{personalizationData.device_customization.focus}</p>
              <div className="space-y-2">
                {personalizationData.device_customization.tips.map((tip: string, idx: number) => (
                  <div key={idx} className="flex gap-2 text-sm text-slate-300">
                    <span className="text-green-400 font-semibold">•</span>
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

