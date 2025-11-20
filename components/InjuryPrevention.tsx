'use client';

/**
 * InjuryPrevention Component
 * AI-powered injury risk assessment based on training load and recovery
 */
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { AlertTriangle, Zap, TrendingUp, Heart, Activity } from 'lucide-react';

interface RiskFactor {
  factor: string;
  severity: 'low' | 'medium' | 'high';
  description: string;
  recommendation: string;
}

export function InjuryPrevention() {
  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 'recent'],
    queryFn: () => apiClient.getWorkouts(0, 50),
    retry: 1,
  });

  const { data: healthData } = useQuery({
    queryKey: ['health', 'today'],
    queryFn: () => apiClient.getHealthToday?.(),
    retry: 1,
  });

  const assessRisks = (): RiskFactor[] => {
    const risks: RiskFactor[] = [];
    const workouts = workoutsData?.workouts || [];
    const health = healthData || {};

    // Calculate training load (last 7 days)
    const weekWorkouts = workouts.filter(w => {
      if (!w.date && !w.start_time) return false;
      const workoutDate = new Date(w.date || w.start_time);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return workoutDate >= weekAgo;
    });

    const totalDistance = weekWorkouts.reduce((sum, w) => sum + (w.distance_km || 0), 0);
    const weeklyHours = weekWorkouts.reduce((sum, w) => sum + ((w.duration_seconds || 0) / 3600), 0);

    // Risk 1: High training load
    if (totalDistance > 60) {
      risks.push({
        factor: 'High Weekly Volume',
        severity: 'high',
        description: `You've run ${totalDistance.toFixed(0)} km this week (>60km threshold)`,
        recommendation: 'Consider adding a rest day or reducing intensity. Monitor for signs of overtraining.'
      });
    } else if (totalDistance > 45) {
      risks.push({
        factor: 'Elevated Training Load',
        severity: 'medium',
        description: `Weekly volume is ${totalDistance.toFixed(0)} km. Build gradually for adaptation.`,
        recommendation: 'Ensure adequate recovery between sessions. Include easy runs.'
      });
    }

    // Risk 2: Insufficient recovery
    if (health.body_battery !== undefined && health.body_battery < 20) {
      risks.push({
        factor: 'Poor Recovery Status',
        severity: 'high',
        description: 'Body battery critically low. Nervous system needs recovery.',
        recommendation: 'Take a rest day. Focus on sleep, nutrition, and stress management.'
      });
    } else if (health.body_battery !== undefined && health.body_battery < 40) {
      risks.push({
        factor: 'Inadequate Recovery',
        severity: 'medium',
        description: 'Recovery is below optimal levels.',
        recommendation: 'Reduce training intensity. Prioritize sleep and active recovery (yoga, walking).'
      });
    }

    // Risk 3: High heart rate variability
    if (health.hrv_ms !== undefined && health.hrv_ms < 30) {
      risks.push({
        factor: 'Elevated Stress Response',
        severity: 'high',
        description: 'Low HRV indicates nervous system stress.',
        recommendation: 'Implement stress reduction: meditation, breathing exercises, or light activity.'
      });
    }

    // Risk 4: Training frequency spike
    if (weekWorkouts.length >= 6) {
      risks.push({
        factor: 'High Training Frequency',
        severity: 'medium',
        description: `${weekWorkouts.length} sessions this week. Frequency is high.`,
        recommendation: 'Ensure varied intensities. Include 1-2 easy runs per week.'
      });
    }

    // Risk 5: Sudden intensity increase
    if (workouts.length >= 2) {
      const recentAvgPace = workouts.slice(0, 3).reduce((sum, w) => sum + (w.avg_pace_min_km || 0), 0) / 3;
      const previousAvgPace = workouts.slice(3, 6).reduce((sum, w) => sum + (w.avg_pace_min_km || 0), 0) / 3;
      
      if (recentAvgPace < previousAvgPace - 0.3) {
        risks.push({
          factor: 'Rapid Pace Increase',
          severity: 'medium',
          description: 'Recent runs are significantly faster than previous training.',
          recommendation: 'Build intensity gradually (10% increase per week max). Risk of injury increases with rapid changes.'
        });
      }
    }

    return risks;
  };

  const risks = assessRisks();

  const getIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <AlertTriangle className="h-5 w-5 text-red-500" />;
      case 'medium':
        return <Zap className="h-5 w-5 text-yellow-500" />;
      default:
        return <Activity className="h-5 w-5 text-green-500" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'border-l-red-500 bg-red-500/5';
      case 'medium':
        return 'border-l-yellow-500 bg-yellow-500/5';
      default:
        return 'border-l-green-500 bg-green-500/5';
    }
  };

  const overallRisk = risks.some(r => r.severity === 'high')
    ? 'high'
    : risks.some(r => r.severity === 'medium')
    ? 'medium'
    : 'low';

  return (
    <div className="space-y-6">
      {/* Overall Risk Badge */}
      <div className={`p-4 rounded-lg border-l-4 ${getSeverityColor(overallRisk)} backdrop-blur`}>
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-semibold text-white capitalize">
              Overall Injury Risk: <span className="ml-2 uppercase">{overallRisk}</span>
            </h3>
            <p className="text-sm text-slate-300 mt-1">
              {overallRisk === 'high'
                ? 'Multiple risk factors detected. Consider modifying training plan.'
                : overallRisk === 'medium'
                ? 'Some caution advised. Monitor these factors closely.'
                : 'Training load is healthy. Continue with smart recovery practices.'}
            </p>
          </div>
          {getIcon(overallRisk)}
        </div>
      </div>

      {/* Risk Factors */}
      {risks.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {risks.map((risk, idx) => (
            <Card key={idx} className={`border-l-4 bg-slate-800/50 backdrop-blur border-slate-700 ${getSeverityColor(risk.severity)}`}>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-white flex items-center gap-2">
                  {getIcon(risk.severity)}
                  {risk.factor}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <p className="text-sm text-slate-300">{risk.description}</p>
                <div className="p-2 bg-slate-700/50 rounded text-xs text-slate-200">
                  <span className="font-semibold text-blue-400">💡 Tip: </span>
                  {risk.recommendation}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-green-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-green-400">
              <Heart className="h-5 w-5" />
              All Clear!
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-slate-300">
              No significant injury risk factors detected. Your training load and recovery are balanced. Keep up the good work!
            </p>
          </CardContent>
        </Card>
      )}

      {/* Prevention Tips */}
      <Card className="bg-gradient-to-r from-blue-900/20 to-purple-900/20 border-slate-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-400">
            <Activity className="h-5 w-5" />
            Injury Prevention Tips
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="space-y-2 text-sm text-slate-300">
            <p>✓ Follow the 10% rule: Increase weekly volume by max 10%</p>
            <p>✓ Include 1-2 easy/recovery runs per week</p>
            <p>✓ Prioritize sleep: Aim for 7-9 hours nightly</p>
            <p>✓ Dynamic warm-up before runs, static stretching after</p>
            <p>✓ Strength training 2x per week (core, glutes, ankles)</p>
            <p>✓ Listen to your body: Rest when needed</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
