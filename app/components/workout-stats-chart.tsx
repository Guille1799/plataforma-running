'use client';

import React, { useMemo, useState } from 'react';
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
import { Workout } from '@/lib/types';
import { format, parseISO, subWeeks, startOfWeek, endOfWeek, isWithinInterval } from 'date-fns';
import { es } from 'date-fns/locale';
import { Button } from '@/app/components/ui/button';

interface WorkoutStatsChartProps {
    workouts: Workout[];
    weeksToShow?: number;
}

// HR Zone mappings (Karvonen formula)
const HR_ZONES = {
    Z1: { min: 0.50, max: 0.60, name: 'Z1 Recovery', color: '#3b82f6' },
    Z2: { min: 0.60, max: 0.70, name: 'Z2 Aerobic', color: '#10b981' },
    Z3: { min: 0.70, max: 0.80, name: 'Z3 Tempo', color: '#f59e0b' },
    Z4: { min: 0.80, max: 0.90, name: 'Z4 Threshold', color: '#ef4444' },
    Z5: { min: 0.90, max: 1.00, name: 'Z5 VO2 Max', color: '#d32f2f' },
};

function getHRZone(avgHR: number | undefined, maxHR: number = 185, restingHR: number = 60): string {
    if (!avgHR) return 'Unknown';
    const hrr = maxHR - restingHR;
    const intensity = (avgHR - restingHR) / hrr;

    for (const [key, zone] of Object.entries(HR_ZONES)) {
        if (intensity >= zone.min && intensity < zone.max) return key;
    }
    return 'Z5';
}

export function WorkoutStatsChart({ workouts, weeksToShow = 5 }: WorkoutStatsChartProps) {
    const [selectedZone, setSelectedZone] = useState<string | null>(null);

    // Procesar datos por semana
    const weeklyData = useMemo(() => {
        if (!workouts || workouts.length === 0) {
            return Array(weeksToShow)
                .fill(null)
                .map((_, i) => ({
                    week: `Sem ${i + 1}`,
                    distance: 0,
                    duration: 0,
                    workouts: 0,
                }));
        }

        const weeks = Array(weeksToShow)
            .fill(null)
            .map((_, i) => {
                const endDate = new Date();
                endDate.setDate(endDate.getDate() - i * 7);
                const startDate = new Date(endDate);
                startDate.setDate(startDate.getDate() - 7);

                const weekWorkouts = workouts.filter((w) => {
                    const workoutDate = parseISO(w.start_time);
                    return (
                        workoutDate >= startDate &&
                        workoutDate <= endDate
                    );
                });

                const distance = weekWorkouts.reduce(
                    (sum, w) => sum + (w.distance_meters / 1000),
                    0
                );
                const duration = weekWorkouts.reduce(
                    (sum, w) => sum + w.duration_seconds / 60,
                    0
                );

                return {
                    week: format(endDate, 'MMM dd', { locale: es }),
                    distance: Math.round(distance * 10) / 10,
                    duration: Math.round(duration),
                    workouts: weekWorkouts.length,
                };
            })
            .reverse();

        return weeks;
    }, [workouts, weeksToShow]);

    // Calcular distribución de zonas HR
    const intensityData = useMemo(() => {
        if (!workouts || workouts.length === 0) {
            return [
                { name: 'Z1 Recovery', value: 20, color: '#3b82f6' },
                { name: 'Z2 Aerobic', value: 50, color: '#10b981' },
                { name: 'Z3 Tempo', value: 20, color: '#f59e0b' },
                { name: 'Z4-Z5 Hard', value: 10, color: '#ef4444' },
            ];
        }

        const zoneCounts: { [key: string]: number } = {
            Z1: 0,
            Z2: 0,
            Z3: 0,
            Z4: 0,
            Z5: 0,
        };

        workouts.forEach((w) => {
            if (w.avg_heart_rate) {
                const zone = getHRZone(w.avg_heart_rate);
                zoneCounts[zone]++;
            }
        });

        const total = Object.values(zoneCounts).reduce((a, b) => a + b, 0) || 1;

        const zoneMapping: { [key: string]: { name: string; color: string } } = {
            Z1: { name: 'Z1 Recovery', color: '#3b82f6' },
            Z2: { name: 'Z2 Aerobic', color: '#10b981' },
            Z3: { name: 'Z3 Tempo', color: '#f59e0b' },
            Z4: { name: 'Z4 Threshold', color: '#ea580c' },
            Z5: { name: 'Z5 VO2 Max', color: '#ef4444' },
        };

        return Object.entries(zoneCounts).map(([zone, count]) => ({
            name: zoneMapping[zone].name,
            value: Math.round((count / total) * 100),
            color: zoneMapping[zone].color,
        }));
    }, [workouts]);

    // Datos de progresión de ritmo (últimos 10 entrenamientos)
    const paceData = useMemo(() => {
        if (!workouts || workouts.length === 0) {
            return [];
        }

        return workouts
            .slice(-10)
            .map((w, idx) => ({
                date: format(parseISO(w.start_time), 'MMM dd', { locale: es }),
                pace: w.avg_pace ? Math.round(w.avg_pace * 100) / 100 : 0,
                distance: Math.round((w.distance_meters / 1000) * 10) / 10,
            }))
            .reverse();
    }, [workouts]);

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
                        <BarChart data={weeklyData}>
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
                    {paceData.length > 0 ? (
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={paceData}>
                                <CartesianGrid strokeDasharray="3 3" />
                                <XAxis dataKey="date" />
                                <YAxis label={{ value: 'Ritmo (min/km)', angle: -90, position: 'insideLeft' }} />
                                <Tooltip formatter={(value: number) => `${value.toFixed(2)} min/km`} />
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
                    ) : (
                        <div className="h-[300px] flex items-center justify-center text-gray-500">
                            No hay datos de ritmo disponibles
                        </div>
                    )}
                </CardContent>
            </Card>

            {/* Resumen de Estadísticas */}
            <Card className="lg:col-span-2">
                <CardHeader>
                    <CardTitle>Resumen de Estadísticas</CardTitle>
                    <CardDescription>Últimas {weeksToShow} semanas</CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="p-3 bg-blue-50 rounded-lg">
                            <p className="text-xs text-gray-600">Total Distancia</p>
                            <p className="text-2xl font-bold text-blue-600">
                                {Math.round(weeklyData.reduce((sum, w) => sum + w.distance, 0) * 10) / 10} km
                            </p>
                        </div>
                        <div className="p-3 bg-green-50 rounded-lg">
                            <p className="text-xs text-gray-600">Total Entrenamientos</p>
                            <p className="text-2xl font-bold text-green-600">
                                {weeklyData.reduce((sum, w) => sum + w.workouts, 0)}
                            </p>
                        </div>
                        <div className="p-3 bg-orange-50 rounded-lg">
                            <p className="text-xs text-gray-600">Total Tiempo</p>
                            <p className="text-2xl font-bold text-orange-600">
                                {Math.round(weeklyData.reduce((sum, w) => sum + w.duration, 0))} min
                            </p>
                        </div>
                        <div className="p-3 bg-purple-50 rounded-lg">
                            <p className="text-xs text-gray-600">Ritmo Promedio</p>
                            <p className="text-2xl font-bold text-purple-600">
                                {paceData.length > 0
                                    ? (paceData.reduce((sum, p) => sum + p.pace, 0) / paceData.length).toFixed(2)
                                    : '0.00'}{' '}
                                min/km
                            </p>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

export default WorkoutStatsChart;
