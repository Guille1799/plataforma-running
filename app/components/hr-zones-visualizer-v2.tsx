'use client';

import React, { useMemo } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';
import { useAuth } from '@/lib/auth-context';

interface HRZone {
    zone: string;
    name: string;
    intensityMin: number;
    intensityMax: number;
    color: string;
    colorClass: string;
    description: string;
    use: string;
}

interface HRZonesVisualizerV2Props {
    maxHR?: number;
    restingHR?: number;
    currentHR?: number;
}

export function HRZonesVisualizerV2({
    maxHR = 185,
    restingHR = 60,
    currentHR,
}: HRZonesVisualizerV2Props) {
    const { user } = useAuth();

    // Calcular zonas usando Karvonen formula
    const zones = useMemo(() => {
        const hrr = maxHR - restingHR;

        const HR_ZONES: HRZone[] = [
            {
                zone: 'Z1',
                name: 'Recovery',
                intensityMin: 0.50,
                intensityMax: 0.60,
                color: '#3b82f6',
                colorClass: 'bg-blue-200',
                description: 'Conversación normal, muy fácil',
                use: 'Recuperación activa entre entrenamientos duros',
            },
            {
                zone: 'Z2',
                name: 'Aerobic Base',
                intensityMin: 0.60,
                intensityMax: 0.70,
                color: '#10b981',
                colorClass: 'bg-green-200',
                description: 'Puedes hablar pero cuesta',
                use: 'Construcción de base aeróbica (80% entrenamientos)',
            },
            {
                zone: 'Z3',
                name: 'Sweet Spot',
                intensityMin: 0.70,
                intensityMax: 0.80,
                color: '#f59e0b',
                colorClass: 'bg-yellow-300',
                description: 'Esfuerzo moderado, conversación difícil',
                use: 'Entrenamientos de ritmo/tempo',
            },
            {
                zone: 'Z4',
                name: 'Threshold',
                intensityMin: 0.80,
                intensityMax: 0.90,
                color: '#ea580c',
                colorClass: 'bg-orange-400',
                description: 'Casi imposible hablar',
                use: 'Entrenamientos a ritmo máximo sostenible',
            },
            {
                zone: 'Z5',
                name: 'VO2 Max',
                intensityMin: 0.90,
                intensityMax: 1.0,
                color: '#ef4444',
                colorClass: 'bg-red-400',
                description: 'Esfuerzo máximo, anaeróbico',
                use: 'Series cortas, esfuerzo máximo',
            },
        ];

        // Convertir intensidades a bpm
        return HR_ZONES.map((zone) => ({
            ...zone,
            bpmMin: Math.round(zone.intensityMin * hrr + restingHR),
            bpmMax: Math.round(zone.intensityMax * hrr + restingHR),
        }));
    }, [maxHR, restingHR]);

    // Detectar zona actual
    const currentZone = useMemo(() => {
        if (!currentHR) return null;
        const hrr = maxHR - restingHR;
        const intensity = (currentHR - restingHR) / hrr;
        return zones.find((z) => intensity >= z.intensityMin && intensity < z.intensityMax);
    }, [currentHR, maxHR, restingHR, zones]);

    return (
        <div className="grid gap-4">
            {/* HR Zones Bar */}
            <Card>
                <CardHeader>
                    <CardTitle>Zonas de Frecuencia Cardíaca</CardTitle>
                    <CardDescription>
                        Max HR: {maxHR} bpm | Resting HR: {restingHR} bpm
                        {currentHR && ` | Current: ${currentHR} bpm`}
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <div className="space-y-6">
                        {/* Visual Bar */}
                        <div className="w-full h-12 rounded-lg overflow-hidden border-2 border-gray-300 flex">
                            {zones.map((zone) => (
                                <div
                                    key={zone.zone}
                                    className={`${zone.colorClass} flex-1 flex items-center justify-center text-xs font-bold text-gray-700 border-r border-gray-300 last:border-r-0 hover:opacity-80 transition-opacity`}
                                    title={`${zone.name}: ${zone.bpmMin}-${zone.bpmMax} bpm`}
                                >
                                    {zone.zone}
                                </div>
                            ))}
                        </div>

                        {/* Current HR Indicator */}
                        {currentHR && (
                            <div className="flex items-center justify-between p-4 bg-gradient-to-r from-gray-50 to-gray-100 rounded-lg border border-gray-200">
                                <div>
                                    <p className="text-sm text-gray-600">FC Actual</p>
                                    <p className="text-3xl font-bold text-red-500">{currentHR} bpm</p>
                                </div>
                                {currentZone && (
                                    <div className="text-right">
                                        <Badge className={`${currentZone.colorClass} text-gray-700 font-bold px-3 py-1`}>
                                            {currentZone.zone} - {currentZone.name}
                                        </Badge>
                                        <p className="text-xs text-gray-600 mt-2">{currentZone.description}</p>
                                    </div>
                                )}
                            </div>
                        )}

                        {/* Detailed Zone Information */}
                        <div className="grid gap-3">
                            {zones.map((zone) => (
                                <div
                                    key={zone.zone}
                                    className={`p-4 rounded-lg border-l-4 transition-all ${currentZone?.zone === zone.zone
                                            ? 'border-l-4 bg-opacity-20 ring-2 ring-offset-2'
                                            : 'border-opacity-50 hover:border-opacity-100'
                                        }`}
                                    style={{
                                        borderColor: zone.color,
                                        backgroundColor:
                                            currentZone?.zone === zone.zone
                                                ? `${zone.color}20`
                                                : undefined,
                                    }}
                                >
                                    <div className="flex items-start justify-between">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-2 mb-1">
                                                <Badge
                                                    className={`${zone.colorClass} text-gray-700 font-bold`}
                                                >
                                                    {zone.zone}
                                                </Badge>
                                                <h4 className="font-semibold text-lg">{zone.name}</h4>
                                                {currentZone?.zone === zone.zone && (
                                                    <Badge variant="secondary">En uso ahora</Badge>
                                                )}
                                            </div>
                                            <p className="text-sm text-gray-600 mb-2 font-mono">
                                                {zone.bpmMin} - {zone.bpmMax} bpm
                                            </p>
                                            <p className="text-sm mb-2">
                                                <span className="font-semibold">Sensación:</span> {zone.description}
                                            </p>
                                            <p className="text-sm">
                                                <span className="font-semibold">Uso:</span> {zone.use}
                                            </p>
                                        </div>
                                        <div className="text-right ml-4">
                                            <div className="text-xs text-gray-500 whitespace-nowrap">
                                                {Math.round(
                                                    ((zone.intensityMax - zone.intensityMin) * (maxHR - restingHR)) /
                                                    (maxHR - restingHR) *
                                                    100
                                                )}
                                                % del rango
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>

                        {/* Legend */}
                        <div className="p-4 bg-blue-50 rounded-lg text-sm text-gray-700 border border-blue-200">
                            <p className="font-semibold mb-2">📊 Información de las Zonas:</p>
                            <ul className="space-y-1 text-xs">
                                <li>
                                    <span className="font-semibold">Karvonen Formula:</span> Calcula zonas basadas en FC
                                    máxima y en reposo
                                </li>
                                <li>
                                    <span className="font-semibold">5 Zonas:</span> Diseñadas específicamente para running
                                    (no confundir con 7 zonas de potencia)
                                </li>
                                <li>
                                    <span className="font-semibold">⚠️ Nota:</span> Max HR: {maxHR} bpm | Resting HR:{' '}
                                    {restingHR} bpm (Actualiza en perfil si es incorrecto)
                                </li>
                            </ul>
                        </div>
                    </div>
                </CardContent>
            </Card>
        </div>
    );
}

export default HRZonesVisualizerV2;
