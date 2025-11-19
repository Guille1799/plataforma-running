'use client';

/**
 * HR Zones Visualization Component
 * Shows 5 HR training zones with colors and ranges
 */
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

interface HRZone {
  name: string;
  min_bpm: number;
  max_bpm: number;
  percentage: string;
  purpose: string;
  intensity: string;
}

interface HRZonesVizProps {
  user: any;
}

const zoneColors = {
  'Z1': { bg: 'bg-blue-500/20', border: 'border-blue-500', text: 'text-blue-400', label: 'bg-blue-600' },
  'Z2': { bg: 'bg-green-500/20', border: 'border-green-500', text: 'text-green-400', label: 'bg-green-600' },
  'Z3': { bg: 'bg-yellow-500/20', border: 'border-yellow-500', text: 'text-yellow-400', label: 'bg-yellow-600' },
  'Z4': { bg: 'bg-orange-500/20', border: 'border-orange-500', text: 'text-orange-400', label: 'bg-orange-600' },
  'Z5': { bg: 'bg-red-500/20', border: 'border-red-500', text: 'text-red-400', label: 'bg-red-600' },
};

export function HRZonesVisualization({ user }: HRZonesVizProps) {
  if (!user?.hr_zones || user.hr_zones.length === 0) {
    return (
      <Card className="bg-slate-800/50 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white flex items-center gap-2">
            <span>❤️</span> Zonas de Frecuencia Cardíaca
          </CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-slate-400 text-center py-6">
            Completa tu perfil con FC máxima para ver tus zonas personalizadas
          </p>
        </CardContent>
      </Card>
    );
  }

  // Parse HR zones
  const zones = user.hr_zones;
  const zoneKeys = ['zone_1', 'zone_2', 'zone_3', 'zone_4', 'zone_5'];
  const zoneNames = ['Z1', 'Z2', 'Z3', 'Z4', 'Z5'];

  return (
    <Card className="bg-slate-800/50 border-slate-700 animate-fade-in hover:shadow-lg transition-shadow duration-300">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <span>❤️</span> Zonas de Frecuencia Cardíaca (Fórmula Karvonen)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {zoneKeys.map((zoneKey, idx) => {
            const zone = zones[zoneKey];
            if (!zone || !zone.hr) return null;
            
            const zoneName = zoneNames[idx];
            const colors = zoneColors[zoneName as keyof typeof zoneColors];
            
            return (
              <div
                key={zoneKey}
                className={`p-4 rounded-lg border ${colors.border} ${colors.bg} transition-all hover:shadow-lg`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`px-3 py-1 rounded text-white font-bold text-sm ${colors.label}`}>
                      {zoneName}
                    </div>
                    <div className="flex-1">
                      <p className={`font-semibold ${colors.text}`}>
                        {zone.hr.min_bpm} - {zone.hr.max_bpm} bpm
                      </p>
                      <p className="text-slate-400 text-sm">{zone.description}</p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-slate-300 text-sm font-medium">{zone.intensity}</p>
                    <p className="text-slate-400 text-xs">{zone.purpose}</p>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
        
        {/* Quick Info */}
        <div className="mt-6 p-4 bg-slate-700/30 rounded-lg border border-slate-600">
          <p className="text-slate-300 text-xs">
            💡 <span className="font-semibold">Karvonen Formula:</span> Calcula zonas basadas en tu FC máxima y FC en reposo para mayor precisión que simples porcentajes
          </p>
        </div>
      </CardContent>
    </Card>
  );
}
