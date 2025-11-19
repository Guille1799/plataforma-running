'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import type { Workout } from '@/lib/types';
import { formatPace, formatDuration, formatDistance, formatDate } from '@/lib/formatters';

interface ExportProps {
  workouts: Workout[];
}

export function ExportWorkouts({ workouts }: ExportProps) {
  const [isExporting, setIsExporting] = useState(false);

  const exportToCSV = () => {
    setIsExporting(true);
    
    // Headers
    const headers = ['Fecha', 'Tipo', 'Distancia (km)', 'Tiempo', 'Pace', 'HR Promedio', 'Calorías'];
    
    // Rows
    const rows = workouts.map(w => [
      new Date(w.start_time).toLocaleDateString('es-ES'),
      w.sport_type || 'Running',
      ((w.distance_meters || 0) / 1000).toFixed(2),
      formatDuration(w.duration_seconds),
      formatPace(w.avg_pace),
      Math.round(w.avg_heart_rate || 0),
      w.elevation_gain || '-',
    ]);

    // Create CSV content
    const csvContent = [
      headers.join(','),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(',')),
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    
    link.setAttribute('href', url);
    link.setAttribute('download', `entrenamientos_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setIsExporting(false);
  };

  const exportToJSON = () => {
    setIsExporting(true);

    const data = {
      exportDate: new Date().toISOString(),
      totalWorkouts: workouts.length,
      totalDistance: ((workouts.reduce((sum, w) => sum + (w.distance_meters || 0), 0)) / 1000).toFixed(2),
      workouts: workouts.map(w => ({
        id: w.id,
        date: w.start_time,
        type: w.sport_type,
        distance: ((w.distance_meters || 0) / 1000).toFixed(2),
        duration: w.duration_seconds,
        pace: w.avg_pace,
        hrAvg: Math.round(w.avg_heart_rate || 0),
        hrMax: w.max_heart_rate,
        elevation: w.elevation_gain,
      })),
    };

    const jsonContent = JSON.stringify(data, null, 2);
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `entrenamientos_${new Date().toISOString().split('T')[0]}.json`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    setIsExporting(false);
  };

  return (
    <Card className="bg-slate-800/50 border-slate-700">
      <CardHeader>
        <CardTitle className="text-lg">📥 Exportar Datos</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm text-slate-300">
          Descarga tus datos de entrenamiento en diferentes formatos
        </p>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          <button
            onClick={exportToCSV}
            disabled={isExporting || workouts.length === 0}
            className="px-4 py-3 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
          >
            <span>📊</span>
            <span>{isExporting ? 'Exportando...' : 'Descargar CSV'}</span>
          </button>
          
          <button
            onClick={exportToJSON}
            disabled={isExporting || workouts.length === 0}
            className="px-4 py-3 bg-purple-600 hover:bg-purple-700 disabled:opacity-50 text-white rounded-lg font-medium transition-colors flex items-center justify-center space-x-2"
          >
            <span>📄</span>
            <span>{isExporting ? 'Exportando...' : 'Descargar JSON'}</span>
          </button>
        </div>

        <div className="mt-4 p-3 bg-slate-700/50 rounded-lg text-sm text-slate-300">
          <p>📈 <strong>{workouts.length}</strong> entrenamientos disponibles para exportar</p>
          <p>📏 Total: <strong>{formatDistance(workouts.reduce((sum, w) => sum + (w.distance_meters || 0), 0))}</strong></p>
        </div>
      </CardContent>
    </Card>
  );
}
