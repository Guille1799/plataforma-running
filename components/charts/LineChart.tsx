'use client';

/**
 * LineChart.tsx - Simple line chart component
 * Sin dependencias externas, usando SVG puro
 */
import { useMemo } from 'react';

interface DataPoint {
  label: string;
  value: number;
}

interface LineChartProps {
  data: DataPoint[];
  height?: number;
  color?: string;
  showGrid?: boolean;
  showLabels?: boolean;
  className?: string;
}

export function LineChart({
  data,
  height = 200,
  color = '#3b82f6',
  showGrid = true,
  showLabels = true,
  className = '',
}: LineChartProps) {
  const { points, minValue, maxValue, yScale } = useMemo(() => {
    if (data.length === 0) return { points: '', minValue: 0, maxValue: 0, yScale: [] };

    const values = data.map(d => d.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    // Calculate points for polyline
    const width = 100; // Use percentage
    const spacing = width / (data.length - 1 || 1);
    
    const pointsStr = data
      .map((d, i) => {
        const x = i * spacing;
        const y = height - ((d.value - min) / range) * (height - 20);
        return `${x},${y}`;
      })
      .join(' ');

    // Y-axis scale
    const steps = 5;
    const scale = Array.from({ length: steps + 1 }, (_, i) => {
      const value = min + (range * i) / steps;
      return {
        y: height - ((value - min) / range) * (height - 20),
        value: value.toFixed(0),
      };
    });

    return { points: pointsStr, minValue: min, maxValue: max, yScale: scale };
  }, [data, height]);

  if (data.length === 0) {
    return (
      <div className={`flex items-center justify-center ${className}`} style={{ height }}>
        <p className="text-slate-400 text-sm">No hay datos disponibles</p>
      </div>
    );
  }

  return (
    <div className={`relative ${className}`}>
      <svg
        viewBox={`0 0 100 ${height}`}
        className="w-full"
        preserveAspectRatio="none"
      >
        {/* Grid lines */}
        {showGrid && yScale.map((tick, i) => (
          <line
            key={i}
            x1="0"
            y1={tick.y}
            x2="100"
            y2={tick.y}
            stroke="rgba(148, 163, 184, 0.1)"
            strokeWidth="0.5"
          />
        ))}

        {/* Area under the line */}
        <defs>
          <linearGradient id={`gradient-${color}`} x1="0" x2="0" y1="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.3" />
            <stop offset="100%" stopColor={color} stopOpacity="0" />
          </linearGradient>
        </defs>
        
        <polyline
          points={`0,${height} ${points} 100,${height}`}
          fill={`url(#gradient-${color})`}
        />

        {/* Line */}
        <polyline
          points={points}
          fill="none"
          stroke={color}
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Data points */}
        {data.map((d, i) => {
          const x = (i / (data.length - 1 || 1)) * 100;
          const y = height - ((d.value - minValue) / (maxValue - minValue || 1)) * (height - 20);
          return (
            <circle
              key={i}
              cx={x}
              cy={y}
              r="1.5"
              fill={color}
              className="hover:r-2 transition-all"
            />
          );
        })}
      </svg>

      {/* Labels */}
      {showLabels && (
        <div className="flex justify-between mt-2 px-1">
          {data.map((d, i) => {
            // Show only first, last, and middle labels to avoid crowding
            const shouldShow = i === 0 || i === data.length - 1 || i === Math.floor(data.length / 2);
            return (
              <div
                key={i}
                className={`text-xs text-slate-400 ${shouldShow ? 'opacity-100' : 'opacity-0'}`}
              >
                {d.label}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
