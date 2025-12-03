'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';

interface HRZone {
  zone: string;
  name: string;
  bpmMin: number;
  bpmMax: number;
  color: string;
  description: string;
  use: string;
}

const HR_ZONES: HRZone[] = [
  {
    zone: 'Z1',
    name: 'Recovery',
    bpmMin: 122,
    bpmMax: 135,
    color: 'bg-blue-200',
    description: 'Conversación normal, muy fácil',
    use: 'Recuperación activa entre entrenamientos duros',
  },
  {
    zone: 'Z2',
    name: 'Aerobic Base',
    bpmMin: 135,
    bpmMax: 147,
    color: 'bg-green-200',
    description: 'Puedes hablar pero cuesta',
    use: 'Construcción de base aeróbica (80% entrenamientos)',
  },
  {
    zone: 'Z3',
    name: 'Sweet Spot',
    bpmMin: 147,
    bpmMax: 160,
    color: 'bg-yellow-300',
    description: 'Esfuerzo moderado, conversación difícil',
    use: 'Entrenamientos de ritmo/tempo',
  },
  {
    zone: 'Z4',
    name: 'Threshold',
    bpmMin: 160,
    bpmMax: 172,
    color: 'bg-orange-300',
    description: 'Casi imposible hablar',
    use: 'Entrenamientos a ritmo máximo sostenible',
  },
  {
    zone: 'Z5',
    name: 'VO2 Max',
    bpmMin: 172,
    bpmMax: 185,
    color: 'bg-red-400',
    description: 'Esfuerzo máximo, anaeróbico',
    use: 'Series cortas, esfuerzo máximo',
  },
];

interface HRZonesVisualizerProps {
  maxHR?: number;
  restingHR?: number;
  currentHR?: number;
}

export function HRZonesVisualizer({ maxHR = 185, restingHR = 60, currentHR }: HRZonesVisualizerProps) {
  const hrRange = maxHR - restingHR;

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
              {HR_ZONES.map((zone) => (
                <div
                  key={zone.zone}
                  className={`${zone.color} flex-1 flex items-center justify-center text-xs font-bold text-gray-700 border-r border-gray-300 last:border-r-0`}
                  title={`${zone.name}: ${zone.bpmMin}-${zone.bpmMax} bpm`}
                >
                  {zone.zone}
                </div>
              ))}
            </div>

            {/* Current HR Indicator */}
            {currentHR && (
              <div className="flex items-center justify-between p-3 bg-gray-100 rounded-lg">
                <span className="font-semibold">FC Actual:</span>
                <div className="flex items-center gap-2">
                  <span className="text-2xl font-bold text-red-500">{currentHR} bpm</span>
                  <Badge variant="outline">
                    {HR_ZONES.find(z => currentHR >= z.bpmMin && currentHR <= z.bpmMax)?.zone || 'N/A'}
                  </Badge>
                </div>
              </div>
            )}

            {/* Detailed Zone Information */}
            <div className="grid gap-3">
              {HR_ZONES.map((zone) => (
                <div key={zone.zone} className={`p-4 rounded-lg border-l-4 ${zone.color.replace('bg-', 'border-')}`}>
                  <div className="flex items-start justify-between">
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <Badge className={`${zone.color} text-gray-700 font-bold`}>{zone.zone}</Badge>
                        <h4 className="font-semibold text-lg">{zone.name}</h4>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{zone.bpmMin}-{zone.bpmMax} bpm</p>
                      <p className="text-sm mb-2">
                        <span className="font-semibold">Sensación:</span> {zone.description}
                      </p>
                      <p className="text-sm">
                        <span className="font-semibold">Uso:</span> {zone.use}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xs text-gray-500">
                        {Math.round(((zone.bpmMax - zone.bpmMin) / hrRange) * 100)}% del rango
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Legend */}
            <div className="p-3 bg-blue-50 rounded-lg text-sm text-gray-700">
              <strong>💡 Nota:</strong> Estas son 5 zonas de frecuencia cardíaca para running usando la fórmula Karvonen.
              No confundir con las 7 zonas de potencia (en watts) para ciclismo.
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default HRZonesVisualizer;
