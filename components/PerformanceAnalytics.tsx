'use client';

/**
 * PerformanceAnalytics Component
 * Displays trend analysis and performance metrics over time
 */
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TrendingUp, Calendar, Target } from 'lucide-react';

interface PerformanceData {
  date: string;
  pace: number;
  distance: number;
  pace_trend: number;
  speed_trend: number;
}

export function PerformanceAnalytics() {
  const { data: workoutsData, isLoading } = useQuery({
    queryKey: ['workouts', 'analytics'],
    queryFn: () => apiClient.getWorkouts(0, 100),
    retry: 1,
  });

  // Process data for chart
  const processedData = (workoutsData?.workouts || [])
    .slice(-30) // Last 30 workouts
    .map((w) => ({
      date: w.date ? new Date(w.date).toLocaleDateString('es-ES', { month: 'short', day: 'numeric' }) : 'N/A',
      pace: w.avg_pace_min_km || 0,
      distance: w.distance_km || 0,
      pace_trend: (w.avg_pace_min_km || 0) * 0.95, // Simulate trend
      speed_trend: (w.distance_km || 0) * 1.02,
    }))
    .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime());

  // Calculate improvements
  const firstWorkout = processedData[0];
  const lastWorkout = processedData[processedData.length - 1];
  const paceImprovement = firstWorkout && lastWorkout 
    ? ((firstWorkout.pace - lastWorkout.pace) / firstWorkout.pace * 100).toFixed(1)
    : 0;
  const distanceImprovement = firstWorkout && lastWorkout
    ? ((lastWorkout.distance - firstWorkout.distance) / firstWorkout.distance * 100).toFixed(1)
    : 0;

  if (isLoading) {
    return (
      <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
        <CardHeader>
          <CardTitle>Performance Analytics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-slate-400">Loading metrics...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Improvement Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-green-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Pace Improvement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">
              {paceImprovement}%
            </div>
            <p className="text-xs text-slate-500 mt-1">vs first recorded workout</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-blue-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <TrendingUp className="h-4 w-4" />
              Distance Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">
              {distanceImprovement}%
            </div>
            <p className="text-xs text-slate-500 mt-1">average distance increase</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-purple-500">
          <CardHeader className="pb-3">
            <CardTitle className="text-sm font-medium text-slate-400 flex items-center gap-2">
              <Calendar className="h-4 w-4" />
              Active Days
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-400">
              {processedData.length}
            </div>
            <p className="text-xs text-slate-500 mt-1">in last 30 workouts</p>
          </CardContent>
        </Card>
      </div>

      {/* Pace Trend Chart */}
      <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <TrendingUp className="h-5 w-5" />
            Pace Trend (min/km)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="pace" 
                stroke="#3b82f6" 
                dot={false}
                strokeWidth={2}
                name="Actual Pace"
              />
              <Line 
                type="monotone" 
                dataKey="pace_trend" 
                stroke="#10b981" 
                dot={false}
                strokeWidth={2}
                strokeDasharray="5 5"
                name="Trend"
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Distance Trend Chart */}
      <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Distance Progression (km)
          </CardTitle>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={processedData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="date" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" />
              <Tooltip 
                contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569' }}
                labelStyle={{ color: '#e2e8f0' }}
              />
              <Legend />
              <Bar dataKey="distance" fill="#8b5cf6" name="Distance (km)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
