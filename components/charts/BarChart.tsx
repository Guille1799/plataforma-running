'use client';

/**
 * BarChart.tsx - Simple bar chart component
 */
import { useMemo } from 'react';

interface DataPoint {
  label: string;
  value: number;
  color?: string;
}

interface BarChartProps {
  data: DataPoint[];
  height?: number;
  defaultColor?: string;
  showValues?: boolean;
  className?: string;
}

export function BarChart({
  data,
  height = 200,
  defaultColor = '#3b82f6',
  showValues = true,
  className = '',
}: BarChartProps) {
  const maxValue = useMemo(() => {
    return Math.max(...data.map(d => d.value), 1);
  }, [data]);

  if (data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height }}>
        <p className="text-slate-400 text-sm">No hay datos disponibles</p>
      </div>
    );
  }

  return (
    <div className={className}>
      <div className="flex items-end justify-between gap-2" style={{ height }}>
        {data.map((item, i) => {
          const barHeight = (item.value / maxValue) * 100;
          const color = item.color || defaultColor;

          return (
            <div key={i} className="flex-1 flex flex-col items-center gap-2">
              {/* Value on top */}
              {showValues && (
                <div className="text-xs font-semibold text-slate-300">
                  {item.value.toFixed(0)}
                </div>
              )}

              {/* Bar */}
              <div className="w-full relative group">
                <div
                  className="w-full rounded-t-lg transition-all duration-300 hover:opacity-80"
                  style={{
                    height: `${barHeight}%`,
                    backgroundColor: color,
                    minHeight: '4px',
                  }}
                />
              </div>

              {/* Label */}
              <div className="text-xs text-slate-400 text-center truncate w-full">
                {item.label}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
