'use client';

/**
 * Predictions Page - Race time predictions and VDOT calculator
 */
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/lib/api-client';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";

export default function PredictionsPage() {
  const [formData, setFormData] = useState({
    distance_km: '',
    time_seconds: '',
    age: '',
    gender: 'male',
  });

  const [predictions, setPredictions] = useState<any>(null);
  const [vdotData, setVdotData] = useState<any>(null);
  const [trainingPaces, setTrainingPaces] = useState<any>(null);

  // Predict race times
  const predictMutation = useMutation({
    mutationFn: (data: any) => apiClient.predictRaceTimes?.(data) || Promise.reject('Not implemented'),
    onSuccess: (data) => {
      setPredictions(data);
    },
  });

  // Calculate VDOT
  const vdotMutation = useMutation({
    mutationFn: (data: any) => apiClient.getVDOT?.(data) || Promise.reject('Not implemented'),
    onSuccess: (data) => {
      setVdotData(data);
    },
  });

  // Get training paces
  const pacesMutation = useMutation({
    mutationFn: (vdot: number) => apiClient.getTrainingPaces?.(vdot) || Promise.reject('Not implemented'),
    onSuccess: (data) => {
      setTrainingPaces(data);
    },
  });

  const handlePredict = () => {
    if (!formData.distance_km || !formData.time_seconds) {
      alert('Por favor completa distancia y tiempo');
      return;
    }

    const data = {
      distance_km: parseFloat(formData.distance_km),
      time_seconds: parseInt(formData.time_seconds),
      age: formData.age ? parseInt(formData.age) : undefined,
      gender: formData.gender as 'male' | 'female',
    };

    predictMutation.mutate(data);
    vdotMutation.mutate(data);
  };

  const handleCalculatePaces = () => {
    if (vdotData?.vdot) {
      pacesMutation.mutate(vdotData.vdot);
    }
  };

  const formatTime = (seconds: number) => {
    const hours = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
      return `${hours}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    }
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const formatPace = (secondsPerKm: number) => {
    const mins = Math.floor(secondsPerKm / 60);
    const secs = Math.round(secondsPerKm % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}/km`;
  };

  const distanceOptions = [
    { km: 1, label: '1 km' },
    { km: 3, label: '3 km' },
    { km: 5, label: '5K' },
    { km: 10, label: '10K' },
    { km: 15, label: '15K' },
    { km: 21.097, label: 'Media Maratón' },
    { km: 42.195, label: 'Maratón' },
  ];

  return (
    <div className="p-8">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold text-white mb-2">
            Predicciones y VDOT 🎯
          </h1>
          <p className="text-slate-400">
            Predice tus tiempos de carrera y calcula ritmos de entrenamiento
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          {/* Input Card */}
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Ingresa tu Mejor Tiempo</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label className="text-slate-300">Distancia (km)</Label>
                <select
                  value={formData.distance_km}
                  onChange={(e) => setFormData({ ...formData, distance_km: e.target.value })}
                  className="w-full mt-1 px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white"
                >
                  <option value="">Selecciona distancia</option>
                  {distanceOptions.map(opt => (
                    <option key={opt.km} value={opt.km}>{opt.label}</option>
                  ))}
                </select>
              </div>

              <div>
                <Label className="text-slate-300">Tiempo (segundos)</Label>
                <Input
                  type="number"
                  placeholder="ej: 2400 (40 minutos)"
                  value={formData.time_seconds}
                  onChange={(e) => setFormData({ ...formData, time_seconds: e.target.value })}
                  className="bg-slate-900 border-slate-600 text-white"
                />
                <p className="text-xs text-slate-500 mt-1">
                  Tip: 40 min = 2400 segundos
                </p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label className="text-slate-300">Edad (opcional)</Label>
                  <Input
                    type="number"
                    placeholder="ej: 30"
                    value={formData.age}
                    onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                    className="bg-slate-900 border-slate-600 text-white"
                  />
                </div>

                <div>
                  <Label className="text-slate-300">Género</Label>
                  <select
                    value={formData.gender}
                    onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                    className="w-full mt-1 px-3 py-2 bg-slate-900 border border-slate-600 rounded-lg text-white"
                  >
                    <option value="male">Masculino</option>
                    <option value="female">Femenino</option>
                  </select>
                </div>
              </div>

              <Button
                onClick={handlePredict}
                disabled={predictMutation.isPending}
                className="w-full bg-blue-600 hover:bg-blue-700"
              >
                {predictMutation.isPending ? 'Calculando...' : 'Calcular Predicciones'}
              </Button>
            </CardContent>
          </Card>

          {/* VDOT Card */}
          {vdotData && (
            <Card className="bg-slate-800/50 border-slate-700">
              <CardHeader>
                <CardTitle className="text-white">Tu VDOT</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="text-center py-6">
                  <div className="text-6xl font-bold text-blue-400 mb-2">
                    {vdotData.vdot.toFixed(1)}
                  </div>
                  <p className="text-slate-400 mb-4">
                    {vdotData.fitness_level}
                  </p>
                  <Badge className="bg-blue-500/20 text-blue-300 border-blue-500/30">
                    {vdotData.percentile}º percentil
                  </Badge>
                </div>

                {vdotData.interpretation && (
                  <div className="p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                    <p className="text-sm text-slate-300">{vdotData.interpretation}</p>
                  </div>
                )}

                <Button
                  onClick={handleCalculatePaces}
                  disabled={pacesMutation.isPending}
                  className="w-full bg-green-600 hover:bg-green-700"
                >
                  {pacesMutation.isPending ? 'Calculando...' : 'Ver Ritmos de Entrenamiento'}
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Race Predictions */}
        {predictions && (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Predicciones de Tiempos de Carrera</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(predictions.predictions).map(([distance, time]: [string, any]) => (
                  <div key={distance} className="p-4 bg-slate-700/30 rounded-lg border border-slate-600">
                    <p className="text-sm text-slate-400 mb-1">{distance}</p>
                    <p className="text-2xl font-bold text-white">{formatTime(time)}</p>
                  </div>
                ))}
              </div>

              {predictions.ai_insights && (
                <div className="mt-4 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <p className="text-sm text-blue-300 whitespace-pre-wrap">
                    {predictions.ai_insights}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Training Paces */}
        {trainingPaces && (
          <Card className="bg-slate-800/50 border-slate-700">
            <CardHeader>
              <CardTitle className="text-white">Ritmos de Entrenamiento Recomendados</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid gap-3">
                {Object.entries(trainingPaces.paces).map(([type, pace]: [string, any]) => (
                  <div key={type} className="flex items-center justify-between p-3 bg-slate-700/30 rounded-lg border border-slate-600">
                    <div>
                      <p className="font-semibold text-white capitalize">{type.replace('_', ' ')}</p>
                      <p className="text-xs text-slate-400">{getPaceDescription(type)}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xl font-bold text-blue-400">{formatPace(pace)}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Box */}
        <Card className="bg-slate-800/50 border-slate-700">
          <CardContent className="p-6">
            <h3 className="text-lg font-semibold text-white mb-2">💡 ¿Qué es VDOT?</h3>
            <p className="text-sm text-slate-400">
              <strong>VDOT</strong> es una medida de tu capacidad aeróbica desarrollada por Jack Daniels. 
              Representa tu VO2max ajustado por eficiencia de carrera. Un VDOT más alto indica mejor forma física.
              Usamos este valor para calcular ritmos de entrenamiento personalizados y predecir tus tiempos en diferentes distancias.
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

function getPaceDescription(type: string): string {
  const descriptions: Record<string, string> = {
    easy: 'Rodajes suaves, recuperación',
    marathon: 'Ritmo objetivo de maratón',
    threshold: 'Umbral anaeróbico, tempo runs',
    interval: 'Intervalos cortos, 5K pace',
    repetition: 'Series cortas máxima intensidad',
  };
  return descriptions[type] || '';
}
