'use client';

/**
 * ExportAnalytics Component
 * Export training data and analytics in multiple formats (PDF, CSV, JSON)
 */
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Download, FileJson, FileText, Table, Calendar, Trophy } from 'lucide-react';
import { formatPace, formatDistance, formatDate } from '@/lib/formatters';

type ExportFormat = 'csv' | 'json' | 'pdf';

interface ExportOption {
  format: ExportFormat;
  label: string;
  icon: React.ReactNode;
  description: string;
  mimeType: string;
}

export function ExportAnalytics() {
  const [isExporting, setIsExporting] = useState(false);
  const [selectedPeriod, setSelectedPeriod] = useState<'week' | 'month' | 'all'>('month');

  const { data: workoutsData } = useQuery({
    queryKey: ['workouts', 'export'],
    queryFn: () => apiClient.getWorkouts(0, 1000),
    retry: 1,
  });

  const workouts = workoutsData?.workouts || [];

  // Filter by period
  const getFilteredWorkouts = () => {
    const now = new Date();
    let startDate = new Date();

    if (selectedPeriod === 'week') {
      startDate.setDate(now.getDate() - 7);
    } else if (selectedPeriod === 'month') {
      startDate.setMonth(now.getMonth() - 1);
    } else {
      startDate = new Date(0); // all time
    }

    return workouts.filter(w => {
      if (!w.date && !w.start_time) return false;
      const workoutDate = new Date(w.date || w.start_time);
      return workoutDate >= startDate;
    });
  };

  const filteredWorkouts = getFilteredWorkouts();

  // Calculate stats
  const stats = {
    totalDistance: filteredWorkouts.reduce((sum, w) => sum + (w.distance_km || 0), 0),
    totalTime: filteredWorkouts.reduce((sum, w) => sum + ((w.duration_seconds || 0) / 60), 0),
    avgPace: filteredWorkouts.length
      ? filteredWorkouts.reduce((sum, w) => sum + (w.avg_pace_min_km || 0), 0) / filteredWorkouts.length
      : 0,
    workoutCount: filteredWorkouts.length,
    fastestPace: filteredWorkouts.length
      ? Math.min(...filteredWorkouts.map(w => w.avg_pace_min_km || 999).filter(p => p < 999))
      : 0,
  };

  const generateCSV = () => {
    const headers = ['Date', 'Type', 'Distance (km)', 'Time (min)', 'Avg Pace', 'Max HR', 'Calories', 'Notes'];
    const rows = filteredWorkouts.map(w => [
      formatDate(w.date || w.start_time || ''),
      w.workout_type || 'Run',
      (w.distance_km || 0).toFixed(2),
      Math.round((w.duration_seconds || 0) / 60),
      formatPace(w.avg_pace_min_km),
      w.max_heart_rate || 'N/A',
      w.calories_burned || 0,
      w.notes || ''
    ]);

    const csv = [headers, ...rows].map(row => 
      row.map(cell => `"${cell}"`).join(',')
    ).join('\n');

    return csv;
  };

  const generateJSON = () => {
    return JSON.stringify(
      {
        exportDate: new Date().toISOString(),
        period: selectedPeriod,
        stats,
        workouts: filteredWorkouts
      },
      null,
      2
    );
  };

  const generatePDF = () => {
    // Simple PDF generation via HTML
    const content = `
    <html>
    <head>
      <title>Training Analytics Report</title>
      <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1 { color: #2563eb; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
        th { background-color: #f0f0f0; font-weight: bold; }
        .stats { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 20px 0; }
        .stat-card { padding: 15px; border: 1px solid #ccc; border-radius: 8px; }
        .stat-value { font-size: 24px; font-weight: bold; color: #2563eb; }
        .stat-label { font-size: 12px; color: #666; }
      </style>
    </head>
    <body>
      <h1>Training Analytics Report</h1>
      <p>Report generated on: ${new Date().toLocaleDateString()}</p>
      <p>Period: ${selectedPeriod.toUpperCase()}</p>
      
      <div class="stats">
        <div class="stat-card">
          <div class="stat-label">Total Distance</div>
          <div class="stat-value">${stats.totalDistance.toFixed(1)} km</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Total Time</div>
          <div class="stat-value">${(stats.totalTime / 60).toFixed(1)} hrs</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Workouts</div>
          <div class="stat-value">${stats.workoutCount}</div>
        </div>
      </div>
      
      <table>
        <tr>
          <th>Date</th><th>Type</th><th>Distance</th><th>Time</th><th>Pace</th><th>HR Max</th><th>Calories</th>
        </tr>
        ${filteredWorkouts.map(w => `
          <tr>
            <td>${formatDate(w.date || w.start_time || '')}</td>
            <td>${w.workout_type || 'Run'}</td>
            <td>${(w.distance_km || 0).toFixed(2)} km</td>
            <td>${Math.round((w.duration_seconds || 0) / 60)} min</td>
            <td>${formatPace(w.avg_pace_min_km)}</td>
            <td>${w.max_heart_rate || 'N/A'} bpm</td>
            <td>${w.calories_burned || 0}</td>
          </tr>
        `).join('')}
      </table>
    </body>
    </html>
    `;
    return content;
  };

  const handleExport = (format: ExportFormat) => {
    setIsExporting(true);

    try {
      let content = '';
      let filename = `training-analytics-${selectedPeriod}-${new Date().toISOString().split('T')[0]}`;
      let mimeType = 'text/plain';

      if (format === 'csv') {
        content = generateCSV();
        filename += '.csv';
        mimeType = 'text/csv';
      } else if (format === 'json') {
        content = generateJSON();
        filename += '.json';
        mimeType = 'application/json';
      } else if (format === 'pdf') {
        content = generatePDF();
        filename += '.html'; // Note: In production, use jspdf library
        mimeType = 'text/html';
      }

      // Create and trigger download
      const blob = new Blob([content], { type: mimeType });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);

      setTimeout(() => setIsExporting(false), 500);
    } catch (error) {
      console.error('Export error:', error);
      setIsExporting(false);
    }
  };

  const exportOptions: ExportOption[] = [
    {
      format: 'csv',
      label: 'CSV',
      icon: <Table className="h-5 w-5" />,
      description: 'Spreadsheet format - Import to Excel or Sheets',
      mimeType: 'text/csv'
    },
    {
      format: 'json',
      label: 'JSON',
      icon: <FileJson className="h-5 w-5" />,
      description: 'Complete data with metadata',
      mimeType: 'application/json'
    },
    {
      format: 'pdf',
      label: 'Report',
      icon: <FileText className="h-5 w-5" />,
      description: 'Formatted report for sharing',
      mimeType: 'application/pdf'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Period Selection */}
      <Card className="bg-slate-800/50 backdrop-blur border-slate-700">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Select Time Period
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-3">
            {(['week', 'month', 'all'] as const).map(period => (
              <button
                key={period}
                onClick={() => setSelectedPeriod(period)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  selectedPeriod === period
                    ? 'bg-blue-600 text-white'
                    : 'bg-slate-700 text-slate-300 hover:bg-slate-600'
                }`}
              >
                {period === 'week' ? 'Last Week' : period === 'month' ? 'Last Month' : 'All Time'}
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-blue-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-400">Total Distance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-400">{stats.totalDistance.toFixed(1)}</div>
            <p className="text-xs text-slate-500">km</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-purple-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-400">Total Time</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-400">{(stats.totalTime / 60).toFixed(1)}</div>
            <p className="text-xs text-slate-500">hours</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-green-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-400">Avg Pace</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-400">{formatPace(stats.avgPace)}</div>
            <p className="text-xs text-slate-500">min/km</p>
          </CardContent>
        </Card>

        <Card className="bg-slate-800/50 backdrop-blur border-slate-700 border-l-4 border-l-yellow-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-xs text-slate-400">Workouts</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{stats.workoutCount}</div>
            <p className="text-xs text-slate-500">sessions</p>
          </CardContent>
        </Card>
      </div>

      {/* Export Options */}
      <div className="space-y-3">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Download className="h-5 w-5" />
          Export Format
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {exportOptions.map(option => (
            <button
              key={option.format}
              onClick={() => handleExport(option.format)}
              disabled={isExporting || filteredWorkouts.length === 0}
              className="p-4 rounded-lg border-2 border-slate-700 hover:border-blue-600 transition-all text-left disabled:opacity-50 disabled:cursor-not-allowed hover:bg-slate-800/50"
            >
              <div className="flex items-center gap-3 mb-2">
                <div className="text-blue-400">{option.icon}</div>
                <span className="font-semibold text-white">{option.label}</span>
              </div>
              <p className="text-sm text-slate-400">{option.description}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Info */}
      {filteredWorkouts.length > 0 ? (
        <Card className="bg-blue-900/20 border-blue-700">
          <CardContent className="p-4 text-sm text-blue-200">
            📊 {filteredWorkouts.length} workouts ready to export • {stats.totalDistance.toFixed(0)} km total distance
          </CardContent>
        </Card>
      ) : (
        <Card className="bg-yellow-900/20 border-yellow-700">
          <CardContent className="p-4 text-sm text-yellow-200">
            ⚠️ No workouts found for the selected period
          </CardContent>
        </Card>
      )}
    </div>
  );
}
