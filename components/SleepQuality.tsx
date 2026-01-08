'use client';

/**
 * SleepQuality.tsx - Sleep quality visualization and analysis
 */
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { ProgressRing } from '@/components/charts';
import type { HealthMetric } from '@/lib/types';

interface SleepQualityProps {
  metrics: HealthMetric[];
  days?: number;
  className?: string;
  compact?: boolean;
}

export function SleepQuality({ metrics, days = 7, className = '', compact = false }: SleepQualityProps) {
  const sleepData = useMemo(() => {
    const sorted = [...metrics]
      .filter(m => m.sleep_duration_minutes != null)
      .sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime())
      .slice(0, days);

    if (sorted.length === 0) return null;

    const latest = sorted[0];
    const avgDuration = sorted.reduce((sum, m) => sum + (m.sleep_duration_minutes || 0), 0) / sorted.length;
    const avgScore = sorted.reduce((sum, m) => sum + (m.sleep_score || 0), 0) / sorted.length;

    return {
      latest: {
        duration: latest.sleep_duration_minutes || 0,
        score: latest.sleep_score || 0,
        deep: latest.deep_sleep_minutes || 0,
        rem: latest.rem_sleep_minutes || 0,
        light: latest.light_sleep_minutes || 0,
        date: latest.date,
      },
      average: {
        duration: avgDuration,
        score: avgScore,
      },
    };
  }, [metrics, days]);

  if (!sleepData) {
    return (
      <Card className={`bg-slate-800/50 border-slate-700 ${className}`}>
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>🌙</span>
            <span>Calidad del Sueño</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <p className="text-slate-400">No hay datos de sueño disponibles</p>
            <p className="text-sm text-slate-500 mt-1">
              Conecta un dispositivo compatible para trackear tu sueño
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const { latest, average } = sleepData;
  const hoursLatest = latest.duration / 60;
  const hoursAverage = average.duration / 60;

  const getSleepQuality = (score: number) => {
    if (score >= 80) return { text: 'Excelente', color: '#10b981' };
    if (score >= 70) return { text: 'Bueno', color: '#3b82f6' };
    if (score >= 60) return { text: 'Regular', color: '#f59e0b' };
    return { text: 'Pobre', color: '#ef4444' };
  };

  const quality = getSleepQuality(latest.score);

  return (
    <Card className={`bg-slate-800/50 border-slate-700 ${className}`}>
      <CardHeader className={compact ? "pb-2" : ""}>
        <CardTitle className={`text-white flex items-center justify-between ${compact ? "text-sm" : ""}`}>
          <span className="flex items-center gap-2">
            <span>🌙</span>
            <span>Calidad del Sueño</span>
          </span>
          <span className={`${compact ? "text-xs" : "text-sm"} font-normal`} style={{ color: quality.color }}>
            {quality.text}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className={compact ? "space-y-2" : "space-y-6"}>
        {/* Main Score */}
        {compact ? (
          <div className="flex items-center justify-between">
            <div>
              <div className="text-3xl font-bold text-white">
                {hoursLatest.toFixed(1)}<span className="text-sm text-slate-400 ml-1">hrs</span>
              </div>
              <div className="text-xs text-slate-400 mt-1">
                Score: <span className="font-medium text-white">{latest.score}</span>/100
              </div>
            </div>
            <ProgressRing
              progress={latest.score}
              size={80}
              strokeWidth={8}
              color={quality.color}
            />
          </div>
        ) : (
          <div className="flex items-center justify-center">
            <ProgressRing
              progress={latest.score}
              size={140}
              strokeWidth={12}
              color={quality.color}
            />
          </div>
        )}

        {/* Duration Stats */}
        {!compact && (
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center p-3 bg-slate-700/30 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Anoche</p>
              <p className="text-2xl font-bold text-white">
                {hoursLatest.toFixed(1)}
                <span className="text-sm text-slate-400 ml-1">hrs</span>
              </p>
            </div>
            <div className="text-center p-3 bg-slate-700/30 rounded-lg">
              <p className="text-xs text-slate-400 mb-1">Promedio {days}d</p>
              <p className="text-2xl font-bold text-white">
                {hoursAverage.toFixed(1)}
                <span className="text-sm text-slate-400 ml-1">hrs</span>
              </p>
            </div>
          </div>
        )}

        {/* Compact stats */}
        {compact && (
          <div className="flex justify-between text-xs text-slate-400">
            <span>Promedio: <strong className="text-white">{hoursAverage.toFixed(1)}h</strong></span>
            <span>{days} días</span>
          </div>
        )}

        {/* Sleep Stages - Only in non-compact */}
        {!compact && (latest.deep > 0 || latest.rem > 0 || latest.light > 0) && (
          <div className="space-y-2">
            <p className="text-xs font-semibold text-slate-400 uppercase">Fases del Sueño</p>

            <div className="space-y-2">
              {/* Deep Sleep */}
              {latest.deep > 0 && (
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300">Profundo</span>
                    <span className="text-slate-400">{latest.deep} min</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-purple-500"
                      style={{ width: `${(latest.deep / latest.duration) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* REM Sleep */}
              {latest.rem > 0 && (
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300">REM</span>
                    <span className="text-slate-400">{latest.rem} min</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-blue-500"
                      style={{ width: `${(latest.rem / latest.duration) * 100}%` }}
                    />
                  </div>
                </div>
              )}

              {/* Light Sleep */}
              {latest.light > 0 && (
                <div>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="text-slate-300">Ligero</span>
                    <span className="text-slate-400">{latest.light} min</span>
                  </div>
                  <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-cyan-500"
                      style={{ width: `${(latest.light / latest.duration) * 100}%` }}
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Recommendation - Only in non-compact */}
        {!compact && hoursLatest < 7 && (
          <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
            <p className="text-xs text-yellow-300">
              ⚠️ <strong>Dormir menos de 7 horas</strong> puede afectar tu recuperación y rendimiento.
            </p>
          </div>
        )}

        {!compact && hoursLatest >= 7 && hoursLatest <= 9 && (
          <div className="p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
            <p className="text-xs text-green-300">
              ✅ <strong>Excelente duración de sueño</strong> para optimizar tu recuperación.
            </p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
