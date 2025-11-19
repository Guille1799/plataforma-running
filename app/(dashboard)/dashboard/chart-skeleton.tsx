'use client';

/**
 * Chart Skeleton Component
 * Displays a skeleton loader for chart components
 */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface ChartSkeletonProps {
  title?: string;
  height?: string;
}

export function ChartSkeleton({ title = "Cargando datos...", height = "h-64" }: ChartSkeletonProps) {
  return (
    <Card className="bg-slate-800/50 border-slate-700 animate-fade-in">
      <CardHeader>
        <CardTitle className="text-white h-6 bg-slate-700/50 rounded w-32 animate-pulse-soft" />
      </CardHeader>
      <CardContent>
        <div className={`w-full ${height} bg-slate-700/30 rounded-lg animate-pulse-soft`} />
      </CardContent>
    </Card>
  );
}

export function StatsSkeleton() {
  return (
    <div className="grid grid-cols-2 gap-2 md:grid-cols-4 animate-fade-in">
      {[...Array(4)].map((_, i) => (
        <div
          key={i}
          className="p-3 bg-slate-700/30 rounded-lg h-20 animate-pulse-soft"
        />
      ))}
    </div>
  );
}
