'use client';

/**
 * HRVTrend.tsx - Heart Rate Variability trend visualization
 */
import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { LineChart } from '@/components/charts';
import type { HealthMetric } from '@/lib/types';

interface HRVTrendProps {
  metrics: HealthMetric[];
  days?: number;
  className?: string;
}

export function HRVTrend({ metrics, days = 7, className = '' }: HRVTrendProps) {
  const trendData = useMemo(() => {
    // Sort by date (most recent last)
    const sorted = [...metrics]
      .filter(m => m.hrv_ms != null)
      .sort((a, b) => new Date(a.date).getTime() - new Date(b.date).getTime())
      .slice(-days);

    return sorted.map(m => ({
      label: new Date(m.date).toLocaleDateString('es-ES', { 
        month: 'short', 
        day: 'numeric' 
      }),
      value: m.hrv_ms || 0,
    }));
  }, [metrics, days]);

  const latestHRV = trendData.length > 0 ? trendData[trendData.length - 1].value : 0;
  const avgHRV = trendData.length > 0 
    ? trendData.reduce((sum, d) => sum + d.value, 0) / trendData.length 
    : 0;

  const getHRVStatus = (hrv: number) => {
    if (hrv >= 60) return { text: 'Excelente', color: 'text-green-400' };
    if (hrv >= 40) return { text: 'Bueno', color: 'text-blue-400' };
    if (hrv >= 20) return { text: 'Moderado', color: 'text-yellow-400' };
    return { text: 'Bajo', color: 'text-red-400' };
  };

  const status = getHRVStatus(latestHRV);

  return (
    <Card className={`bg-slate-800/50 border-slate-700 ${className}`}>
      <CardHeader>
        <CardTitle className="text-white flex items-center justify-between">
          <span className="flex items-center gap-2">
            <span>❤️</span>
            <span>HRV Trend</span>
          </span>
          <span className={`text-sm font-normal ${status.color}`}>
            {status.text}
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {trendData.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-400">No hay datos de HRV disponibles</p>
            <p className="text-sm text-slate-500 mt-1">
              Conecta un dispositivo compatible para ver tu HRV
            </p>
          </div>
        ) : (
          <>
            <LineChart
              data={trendData}
              height={150}
              color="#3b82f6"
              showGrid={true}
              showLabels={true}
            />

            {/* Stats */}
            <div className="grid grid-cols-2 gap-4 pt-2 border-t border-slate-700">
              <div>
                <p className="text-xs text-slate-400 mb-1">Último</p>
                <p className="text-2xl font-bold text-white">
                  {latestHRV.toFixed(0)}
                  <span className="text-sm text-slate-400 ml-1">ms</span>
                </p>
              </div>
              <div>
                <p className="text-xs text-slate-400 mb-1">Promedio {days}d</p>
                <p className="text-2xl font-bold text-white">
                  {avgHRV.toFixed(0)}
                  <span className="text-sm text-slate-400 ml-1">ms</span>
                </p>
              </div>
            </div>

            {/* Info */}
            <div className="p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
              <p className="text-xs text-blue-300">
                💡 <strong>HRV más alto</strong> indica mejor recuperación y adaptación al entrenamiento.
              </p>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
