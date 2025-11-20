'use client';

/**
 * PersonalizedRecommendations Component
 * AI Coach recommendations based on recent workouts and performance
 */
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Lightbulb, Heart, Zap, AlertCircle, TrendingUp, MessageSquare } from 'lucide-react';

interface Recommendation {
  type: 'info' | 'warning' | 'success' | 'suggestion';
  title: string;
  description: string;
  icon: React.ReactNode;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function PersonalizedRecommendations() {
  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 'recent'],
    queryFn: () => apiClient.getWorkouts(0, 20),
    retry: 1,
  });

  const { data: healthData } = useQuery({
    queryKey: ['health', 'today'],
    queryFn: () => apiClient.getHealthToday?.(),
    retry: 1,
  });

  const { data: chatData } = useQuery({
    queryKey: ['coach', 'recommendations'],
    queryFn: () => apiClient.getChatHistory?.(5),
    retry: 1,
  });

  // Generate recommendations based on data
  const generateRecommendations = (): Recommendation[] => {
    const recs: Recommendation[] = [];
    const workouts = workoutsData?.workouts || [];
    const health = healthData || {};

    // Check recovery
    if (health.body_battery !== undefined && health.body_battery < 30) {
      recs.push({
        type: 'warning',
        title: 'Low Recovery Status',
        description: 'Your body battery is low. Consider a rest day or easy run to allow full recovery.',
        icon: <AlertCircle className="h-5 w-5 text-red-500" />,
      });
    }

    // Check HRV
    if (health.hrv_ms !== undefined && health.hrv_ms < 40) {
      recs.push({
        type: 'info',
        title: 'Monitor Stress Levels',
        description: 'Low HRV detected. Focus on sleep and stress management to improve readiness.',
        icon: <Heart className="h-5 w-5 text-orange-500" />,
      });
    }

    // Check training consistency
    const weekWorkouts = workouts.filter(w => {
      if (!w.date && !w.start_time) return false;
      const workoutDate = new Date(w.date || w.start_time);
      const weekAgo = new Date();
      weekAgo.setDate(weekAgo.getDate() - 7);
      return workoutDate >= weekAgo;
    }).length;

    if (weekWorkouts >= 4) {
      recs.push({
        type: 'success',
        title: 'Great Consistency!',
        description: `You've completed ${weekWorkouts} workouts this week. Keep up the excellent training discipline!`,
        icon: <TrendingUp className="h-5 w-5 text-green-500" />,
      });
    } else if (weekWorkouts >= 2) {
      recs.push({
        type: 'info',
        title: 'Pace Your Training',
        description: 'You have 2-3 workouts this week. Add one more session to optimize your training stimulus.',
        icon: <Zap className="h-5 w-5 text-yellow-500" />,
      });
    }

    // Check pace trends
    if (workouts.length > 5) {
      const recentPaces = workouts.slice(0, 5).map(w => w.avg_pace_min_km || 0);
      const olderPaces = workouts.slice(5, 10).map(w => w.avg_pace_min_km || 0);
      const recentAvg = recentPaces.reduce((a, b) => a + b, 0) / recentPaces.length;
      const olderAvg = olderPaces.reduce((a, b) => a + b, 0) / olderPaces.length;

      if (recentAvg < olderAvg - 0.15) {
        recs.push({
          type: 'success',
          title: 'Pace Improvement Detected',
          description: `Your recent average pace (${recentAvg.toFixed(2)} min/km) is faster than your average from 2 weeks ago. Great progress!`,
          icon: <TrendingUp className="h-5 w-5 text-green-500" />,
        });
      }
    }

    // Default recommendations
    if (recs.length === 0) {
      recs.push({
        type: 'suggestion',
        title: 'Get AI Coaching Advice',
        description: 'Chat with Coach AI to get personalized training recommendations based on your goals and performance.',
        icon: <MessageSquare className="h-5 w-5 text-blue-500" />,
        action: {
          label: 'Ask Coach',
          onClick: () => {
            // Navigate to chat
            window.location.href = '/dashboard/coach';
          },
        },
      });
    }

    return recs.slice(0, 4); // Show max 4 recommendations
  };

  const recommendations = generateRecommendations();

  const getCardStyles = (type: Recommendation['type']) => {
    const baseClasses = 'border-l-4 bg-slate-800/50 backdrop-blur';
    switch (type) {
      case 'warning':
        return `${baseClasses} border-l-red-500`;
      case 'success':
        return `${baseClasses} border-l-green-500`;
      case 'info':
        return `${baseClasses} border-l-yellow-500`;
      case 'suggestion':
      default:
        return `${baseClasses} border-l-blue-500`;
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-2 mb-6">
        <Lightbulb className="h-6 w-6 text-yellow-500" />
        <h2 className="text-xl font-bold text-white">AI Coach Recommendations</h2>
      </div>

      {recommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {recommendations.map((rec, idx) => (
            <Card key={idx} className={`${getCardStyles(rec.type)} border-slate-700 transition-all hover:border-slate-600`}>
              <CardHeader className="pb-3">
                <CardTitle className="text-sm font-medium text-white flex items-center gap-2">
                  {rec.icon}
                  {rec.title}
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <p className="text-sm text-slate-300">
                  {rec.description}
                </p>
                {rec.action && (
                  <button
                    onClick={rec.action.onClick}
                    className="text-sm font-medium text-blue-400 hover:text-blue-300 transition-colors"
                  >
                    {rec.action.label} →
                  </button>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      ) : (
        <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
          <CardContent className="p-6 text-center">
            <p className="text-slate-400">Loading personalized recommendations...</p>
          </CardContent>
        </Card>
      )}

      {/* Coach Chat Quick Access */}
      <Card className="bg-gradient-to-r from-blue-600/10 to-purple-600/10 border-slate-700 border-l-4 border-l-blue-500">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-white">
            <MessageSquare className="h-5 w-5" />
            Need More Guidance?
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-slate-300 mb-4">
            Chat with Coach AI for personalized training plans, injury prevention tips, or race-day strategies.
          </p>
          <a
            href="/dashboard/coach"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors font-medium"
          >
            <MessageSquare className="h-4 w-4" />
            Open Coach Chat
          </a>
        </CardContent>
      </Card>
    </div>
  );
}
