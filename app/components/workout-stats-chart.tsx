'use client';

import React from 'react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';

// Mock data - en producción vendrá de la API
const workoutData = [
  { week: 'Sem 1', distance: 32, duration: 240, workouts: 4 },
  { week: 'Sem 2', distance: 35, duration: 250, workouts: 4 },
  { week: 'Sem 3', distance: 38, duration: 265, workouts: 5 },
  { week: 'Sem 4', distance: 40, duration: 280, workouts: 5 },
  { week: 'Sem 5', distance: 42, duration: 290, workouts: 5 },
];

const intensityData = [
  { name: 'Z1 Recovery', value: 15, color: '#3b82f6' },
  { name: 'Z2 Aerobic', value: 55, color: '#10b981' },
  { name: 'Z3 Tempo', value: 20, color: '#f59e0b' },
  { name: 'Z4-Z5 Hard', value: 10, color: '#ef4444' },
];

export function WorkoutStatsChart() {
  return (
    <div className="grid gap-4 grid-cols-1 lg:grid-cols-2">
      {/* Distancia y Duración por Semana */}
      <Card>
        <CardHeader>
          <CardTitle>Entrenamientos Semanales</CardTitle>
          <CardDescription>Distancia total y duración</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={workoutData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="week" />
              <YAxis yAxisId="left" label={{ value: 'Distancia (km)', angle: -90, position: 'insideLeft' }} />
              <YAxis yAxisId="right" orientation="right" label={{ value: 'Duración (min)', angle: 90, position: 'insideRight' }} />
              <Tooltip />
              <Legend />
              <Bar yAxisId="left" dataKey="distance" fill="#3b82f6" name="Distancia (km)" />
              <Bar yAxisId="right" dataKey="duration" fill="#10b981" name="Duración (min)" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Distribución por Zona de Intensidad */}
      <Card>
        <CardHeader>
          <CardTitle>Distribución de Intensidad</CardTitle>
          <CardDescription>% de tiempo en cada zona HR</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={intensityData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, value }) => `${name}: ${value}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {intensityData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Progresión de Ritmo */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>Progresión de Ritmo Promedio</CardTitle>
          <CardDescription>Evolución del ritmo en los últimos entrenamientos</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart
              data={[
                { date: 'Hace 5d', pace: 6.2 },
                { date: 'Hace 4d', pace: 6.15 },
                { date: 'Hace 3d', pace: 6.1 },
                { date: 'Hace 2d', pace: 6.05 },
                { date: 'Ayer', pace: 6.0 },
                { date: 'Hoy', pace: 5.95 },
              ]}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis label={{ value: 'Ritmo (min/km)', angle: -90, position: 'insideLeft' }} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="pace"
                stroke="#3b82f6"
                dot={{ fill: '#3b82f6' }}
                name="Ritmo (min/km)"
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}

export default WorkoutStatsChart;
